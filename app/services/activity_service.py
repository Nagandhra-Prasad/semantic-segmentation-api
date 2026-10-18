from uuid import UUID

from app.db.models.activity import UserActivity


async def log_activity(
    user_id: UUID,
    action: str,
    resource_type: str | None = None,
    resource_id: UUID | None = None,
    details: dict | None = None,
) -> UserActivity:
    activity = UserActivity(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    await activity.insert()
    return activity
