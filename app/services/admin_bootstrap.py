from datetime import UTC, datetime

from app.core.config import settings
from app.core.security import hash_password
from app.db.models.user import User, UserRole


async def ensure_default_admin() -> None:
    """Create or refresh the configured admin account (credentials from .env)."""
    admin = await User.find_one(User.email == settings.ADMIN_EMAIL)
    if admin is None:
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_FULL_NAME,
            role=UserRole.ADMIN,
            is_active=True,
        )
        await admin.insert()
        return

    admin.role = UserRole.ADMIN
    admin.is_active = True
    admin.full_name = settings.ADMIN_FULL_NAME
    admin.hashed_password = hash_password(settings.ADMIN_PASSWORD)
    admin.updated_at = datetime.now(UTC)
    await admin.save()
