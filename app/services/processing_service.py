from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.db.models.processing_job import JobStatus, ProcessingJob
from app.db.models.upload import Upload
from app.core.access import user_owns_resource
from app.db.models.user import User
from app.services.activity_service import log_activity


async def create_processing_job(user: User, upload_id: UUID) -> ProcessingJob:
    from app.workers.tasks import process_upload_task

    upload = await Upload.get(upload_id)
    if not upload or not user_owns_resource(user, upload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    job = ProcessingJob(
        user_id=user.id,
        upload_id=upload.id,
        status=JobStatus.PENDING,
        original_media_path=upload.file_path,
        model_accuracy_reference=settings.REFERENCE_MODEL_MIOU,
    )
    await job.insert()

    task = process_upload_task.delay(str(job.id))
    job.celery_task_id = task.id
    job.status = JobStatus.PROCESSING
    await job.save()

    await log_activity(user.id, "processing_started", "job", job.id)
    return job


async def get_job_for_user(user: User, job_id: UUID) -> ProcessingJob:
    job = await ProcessingJob.get(job_id)
    if not job or not user_owns_resource(user, job.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
