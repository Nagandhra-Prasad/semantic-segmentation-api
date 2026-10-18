from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.db.base import UUIDDocument


class UploadCategory(str, Enum):
    ROAD_IMAGE = "road_image"
    DASHCAM_VIDEO = "dashcam_video"
    TRAFFIC_SCENE = "traffic_scene"
    DATASET = "dataset"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DATASET = "dataset"


class Upload(UUIDDocument):
    user_id: UUID
    original_filename: str
    stored_filename: str
    file_path: str
    media_type: MediaType
    category: UploadCategory
    content_type: str
    size_bytes: int
    is_validated: bool = False
    validation_message: str | None = None
    dataset_image_paths: list[str] = Field(default_factory=list)
    dataset_image_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "uploads"
