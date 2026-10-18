from app.core.celery_app import celery_app
from app.workers import celery_signals  # noqa: F401 — register worker_ready hook
from app.workers.job_runner import run_sync_processing


@celery_app.task(name="process_upload", bind=True)
def process_upload_task(self, job_id: str) -> str:
    run_sync_processing(job_id)
    return job_id
