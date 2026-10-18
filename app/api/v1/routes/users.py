from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user, require_roles
from app.db.models.user import User, UserRole
from app.schemas.user import RoleUpdateRequest, UserProfileUpdate, UserPublic
from app.services.user_service import set_user_role, update_profile

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserPublic)
async def get_profile(user: User = Depends(get_current_active_user)) -> UserPublic:
    return UserPublic.from_document(user)


@router.patch("/me", response_model=UserPublic)
async def patch_profile(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_active_user),
) -> UserPublic:
    updated = await update_profile(user, payload)
    return UserPublic.from_document(updated)


@router.patch("/{user_id}/role", response_model=UserPublic)
async def update_role(
    user_id: UUID,
    payload: RoleUpdateRequest,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserPublic:
    target = await set_user_role(admin, user_id, payload.role)
    return UserPublic.from_document(target)
