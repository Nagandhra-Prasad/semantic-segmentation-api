from uuid import UUID

from app.core.access import user_owns_resource
from app.db.models.processing_job import JobStatus, ProcessingJob
from app.db.models.user import User


async def user_analytics_summary(user: User) -> dict:
    jobs = await ProcessingJob.find(ProcessingJob.user_id == user.id).to_list()
    completed = [j for j in jobs if j.status == JobStatus.COMPLETED]
    total_inference = sum(j.inference_time_ms or 0 for j in completed)
    avg_inference = total_inference / len(completed) if completed else 0.0
    all_classes: set[str] = set()
    for job in completed:
        all_classes.update(job.class_counts.keys())

    return {
        "total_jobs": len(jobs),
        "completed_jobs": len(completed),
        "failed_jobs": len([j for j in jobs if j.status == JobStatus.FAILED]),
        "total_detected_classes_across_jobs": len(all_classes),
        "average_inference_time_ms": round(avg_inference, 2),
        "reference_model_miou": completed[0].model_accuracy_reference if completed else None,
    }


async def job_analytics(user: User, job_id: UUID) -> dict:
    job = await ProcessingJob.get(job_id)
    if not job or not user_owns_resource(user, job.user_id):
        return {}
    return {
        "job_id": job.id,
        "status": job.status.value,
        "detected_class_count": job.detected_class_count,
        "class_counts": job.class_counts,
        "inference_time_ms": job.inference_time_ms,
        "frames_processed": job.frames_processed,
        "model_accuracy_reference": job.model_accuracy_reference,
        "segmentation_performance": {
            "pixel_class_distribution": job.class_counts,
        },
    }
