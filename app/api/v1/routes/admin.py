from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import require_roles
from app.db.models.user import User, UserRole
from app.schemas.admin import AdminUploadItem, AdminUserItem, UserActiveUpdate
from app.schemas.user import UserPublic
from app.services.admin_service import list_all_uploads, list_all_users, set_user_active

router = APIRouter(prefix="/admin")


@router.get("/users", response_model=list[AdminUserItem])
async def get_all_users(_admin: User = Depends(require_roles(UserRole.ADMIN))) -> list[AdminUserItem]:
    return await list_all_users()


@router.patch("/users/{user_id}/active", response_model=UserPublic)
async def update_user_active(
    user_id: UUID,
    payload: UserActiveUpdate,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserPublic:
    return await set_user_active(admin, user_id, payload.is_active)


@router.get("/uploads", response_model=list[AdminUploadItem])
async def get_all_uploads(_admin: User = Depends(require_roles(UserRole.ADMIN))) -> list[AdminUploadItem]:
    return await list_all_uploads()
