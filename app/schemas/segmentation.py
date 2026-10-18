from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models.processing_job import JobStatus
from app.db.models.upload import MediaType


class ProcessingJobResponse(BaseModel):
    id: UUID
    upload_id: UUID
    status: JobStatus
    celery_task_id: str | None
    segmented_paths: list[str]
    overlay_paths: list[str]
    class_counts: dict[str, int]
    detected_class_count: int
    inference_time_ms: float | None
    model_accuracy_reference: float | None
    frames_processed: int
    overlay_video_path: str | None = None
    segmented_video_path: str | None = None
    source_filename: str | None = None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    @classmethod
    def from_document(cls, job, source_filename: str | None = None) -> "ProcessingJobResponse":
        return cls(
            id=job.id,
            upload_id=job.upload_id,
            status=job.status,
            celery_task_id=job.celery_task_id,
            segmented_paths=job.segmented_paths,
            overlay_paths=job.overlay_paths,
            overlay_video_path=job.overlay_video_path,
            segmented_video_path=job.segmented_video_path,
            class_counts=job.class_counts,
            detected_class_count=job.detected_class_count,
            inference_time_ms=job.inference_time_ms,
            model_accuracy_reference=job.model_accuracy_reference,
            frames_processed=job.frames_processed,
            source_filename=source_filename,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at,
        )


class DashboardViewResponse(BaseModel):
    job: ProcessingJobResponse
    legend: list[dict]
    original_media_path: str | None
    media_type: MediaType
