from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User, UserRole
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate
from app.services.activity_service import log_activity


async def register_user(data: UserCreate) -> User:
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.USER,
    )
    await user.insert()
    await log_activity(user.id, "user_registered", "user", user.id)
    return user


async def authenticate_user(email: str, password: str) -> TokenResponse:
    user = await User.find_one(User.email == email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact an administrator.",
        )
    token = create_access_token(str(user.id), {"role": user.role.value})
    await log_activity(user.id, "user_login", "user", user.id)
    return TokenResponse(access_token=token, token_type="bearer")
