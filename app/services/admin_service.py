from uuid import UUID

from fastapi import HTTPException, status

from app.db.models.processing_job import ProcessingJob
from app.db.models.upload import Upload
from app.db.models.user import User, UserRole
from app.schemas.admin import AdminUploadItem, AdminUserItem
from app.schemas.user import UserPublic


async def list_all_users() -> list[AdminUserItem]:
    users = await User.find_all().sort(-User.created_at).to_list()
    return [
        AdminUserItem(
            user=UserPublic.from_document(u),
            upload_count=await Upload.find(Upload.user_id == u.id).count(),
        )
        for u in users
    ]


async def set_user_active(admin: User, user_id: UUID, is_active: bool) -> UserPublic:
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot deactivate their own account",
        )
    target = await User.get(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.role == UserRole.ADMIN and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate an admin account",
        )
    target.is_active = is_active
    await target.save()
    return UserPublic.from_document(target)


async def list_all_uploads() -> list[AdminUploadItem]:
    uploads = await Upload.find_all().sort(-Upload.created_at).to_list()
    items: list[AdminUploadItem] = []
    for upload in uploads:
        owner = await User.get(upload.user_id)
        latest_job = (
            await ProcessingJob.find(ProcessingJob.upload_id == upload.id)
            .sort(-ProcessingJob.created_at)
            .first_or_none()
        )
        items.append(
            AdminUploadItem(
                id=upload.id,
                original_filename=upload.original_filename,
                media_type=upload.media_type,
                category=upload.category,
                size_bytes=upload.size_bytes,
                is_validated=upload.is_validated,
                created_at=upload.created_at,
                user_id=upload.user_id,
                user_email=owner.email if owner else None,
                user_full_name=owner.full_name if owner else None,
                latest_job_id=latest_job.id if latest_job else None,
                latest_job_status=latest_job.status.value if latest_job else None,
            )
        )
    return items
