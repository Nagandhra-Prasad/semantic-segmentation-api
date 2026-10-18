from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models.upload import MediaType, UploadCategory


class UploadResponse(BaseModel):
    id: UUID
    original_filename: str
    media_type: MediaType
    category: UploadCategory
    size_bytes: int
    is_validated: bool
    validation_message: str | None
    dataset_image_count: int = 0
    created_at: datetime

    @classmethod
    def from_document(cls, upload) -> "UploadResponse":
        return cls(
            id=upload.id,
            original_filename=upload.original_filename,
            media_type=upload.media_type,
            category=upload.category,
            size_bytes=upload.size_bytes,
            is_validated=upload.is_validated,
            validation_message=upload.validation_message,
            dataset_image_count=upload.dataset_image_count,
            created_at=upload.created_at,
        )
