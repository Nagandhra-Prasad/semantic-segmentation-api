from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.db.base import UUIDDocument


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(UUIDDocument):
    user_id: UUID
    upload_id: UUID
    status: JobStatus = JobStatus.PENDING
    celery_task_id: str | None = None
    original_media_path: str | None = None
    segmented_paths: list[str] = Field(default_factory=list)
    overlay_paths: list[str] = Field(default_factory=list)
    overlay_video_path: str | None = None
    segmented_video_path: str | None = None
    class_counts: dict[str, int] = Field(default_factory=dict)
    detected_class_count: int = 0
    inference_time_ms: float | None = None
    model_accuracy_reference: float | None = None
    error_message: str | None = None
    frames_processed: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    class Settings:
        name = "processing_jobs"
