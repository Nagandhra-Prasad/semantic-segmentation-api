from datetime import UTC, datetime
from uuid import UUID

from pydantic import Field

from app.db.base import UUIDDocument


class UserActivity(UUIDDocument):
    user_id: UUID
    action: str
    resource_type: str | None = None
    resource_id: UUID | None = None
    details: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "user_activities"
