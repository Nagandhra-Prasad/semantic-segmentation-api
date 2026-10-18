from datetime import UTC, datetime
from enum import Enum

from pydantic import EmailStr, Field

from app.db.base import UUIDDocument


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(UUIDDocument):
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"
