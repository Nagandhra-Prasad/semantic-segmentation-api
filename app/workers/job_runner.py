from datetime import UTC, datetime
from uuid import UUID

from app.core.config import settings
from app.core.uuid import parse_uuid
from app.db.models.processing_job import JobStatus, ProcessingJob
from app.db.models.upload import MediaType, Upload
from app.ml.frame_extractor import extract_video_frames
from app.ml.inference import run_inference_on_image
from app.ml.video_stitcher import frames_to_mp4
from app.services.activity_service import log_activity
from app.services.model_manager import ModelManager


async def run_job(job_id: str | UUID) -> None:
    job_uuid = job_id if isinstance(job_id, UUID) else parse_uuid(job_id)
    job = await ProcessingJob.get(job_uuid)
    if not job:
        return

    upload = await Upload.get(job.upload_id)
    if not upload:
        job.status = JobStatus.FAILED
        job.error_message = "Upload missing"
        await job.save()
        return

    result_root = settings.result_path / str(job.id)
    result_root.mkdir(parents=True, exist_ok=True)

    try:
        ModelManager.warm_up()
        total_ms = 0.0
        seg_paths: list[str] = []
        overlay_paths: list[str] = []
        merged_counts: dict[str, int] = {}
        frames = 0

        if upload.media_type == MediaType.IMAGE:
            result = run_inference_on_image(upload.file_path, result_root, stem="image")
            seg_paths.append(result.segmented_path)
            overlay_paths.append(result.overlay_path)
            merged_counts = result.class_counts
            total_ms = result.inference_time_ms
            frames = 1
        elif upload.media_type == MediaType.DATASET:
            image_paths = upload.dataset_image_paths or []
            for idx, image_path in enumerate(image_paths):
                result = run_inference_on_image(image_path, result_root, stem=f"frame_{idx:04d}")
                seg_paths.append(result.segmented_path)
                overlay_paths.append(result.overlay_path)
                total_ms += result.inference_time_ms
                for key, val in result.class_counts.items():
                    merged_counts[key] = merged_counts.get(key, 0) + val
                frames += 1
        else:
            frames_dir = result_root / "frames"
            frame_paths = extract_video_frames(
                upload.file_path,
                frames_dir,
                frame_interval=settings.VIDEO_FRAME_INTERVAL,
                max_frames=settings.VIDEO_MAX_FRAMES,
            )
            for idx, frame_path in enumerate(frame_paths):
                result = run_inference_on_image(frame_path, result_root, stem=f"frame_{idx:04d}")
                seg_paths.append(result.segmented_path)
                overlay_paths.append(result.overlay_path)
                total_ms += result.inference_time_ms
                for key, val in result.class_counts.items():
                    merged_counts[key] = merged_counts.get(key, 0) + val
                frames += 1

        job.segmented_paths = seg_paths
        job.overlay_paths = overlay_paths
        job.overlay_video_path = None
        job.segmented_video_path = None
        if upload.media_type in (MediaType.VIDEO, MediaType.DATASET) and len(overlay_paths) > 1:
            job.overlay_video_path = frames_to_mp4(
                overlay_paths,
                result_root / "overlay_preview.mp4",
                fps=settings.RESULT_VIDEO_FPS,
            )
            job.segmented_video_path = frames_to_mp4(
                seg_paths,
                result_root / "segmented_preview.mp4",
                fps=settings.RESULT_VIDEO_FPS,
            )

        job.class_counts = merged_counts
        job.detected_class_count = len(merged_counts)
        job.inference_time_ms = total_ms
        job.frames_processed = frames
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        await job.save()
        await log_activity(job.user_id, "processing_completed", "job", job.id)
    except Exception as exc:  # noqa: BLE001
        job.status = JobStatus.FAILED
        job.error_message = str(exc)
        await job.save()
        await log_activity(
            job.user_id,
            "processing_failed",
            "job",
            job.id,
            {"error": str(exc)},
        )


def run_sync_processing(job_id: str) -> None:
    from app.workers.async_loop import run_async

    run_async(run_job(job_id))
