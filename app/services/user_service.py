from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.db.models.user import User, UserRole
from app.schemas.user import UserProfileUpdate
from app.services.activity_service import log_activity


async def update_profile(user: User, data: UserProfileUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    user.updated_at = datetime.now(UTC)
    await user.save()
    await log_activity(user.id, "profile_updated", "user", user.id)
    return user


async def set_user_role(admin: User, user_id: UUID, role: UserRole) -> User:
    target = await User.get(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    target.role = role
    target.updated_at = datetime.now(UTC)
    await target.save()
    await log_activity(
        admin.id,
        "role_updated",
        "user",
        target.id,
        {"new_role": role.value},
    )
    return target
