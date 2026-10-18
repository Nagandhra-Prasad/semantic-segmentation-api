from uuid import UUID

from app.db.models.user import User, UserRole


def user_owns_resource(user: User, owner_id: UUID) -> bool:
    if user.role == UserRole.ADMIN:
        return True
    return user.id == owner_id
