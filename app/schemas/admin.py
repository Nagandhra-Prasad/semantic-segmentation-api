from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.db.models.upload import MediaType, UploadCategory
from app.schemas.user import UserPublic


class UserActiveUpdate(BaseModel):
    is_active: bool


class AdminUserItem(BaseModel):
    user: UserPublic
    upload_count: int


class AdminUploadItem(BaseModel):
    id: UUID
    original_filename: str
    media_type: MediaType
    category: UploadCategory
    size_bytes: int
    is_validated: bool
    created_at: datetime
    user_id: UUID
    user_email: EmailStr | None
    user_full_name: str | None
    latest_job_id: UUID | None = None
    latest_job_status: str | None = None
