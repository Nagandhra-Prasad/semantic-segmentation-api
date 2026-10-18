from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserPublic
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserPublic)
async def register(payload: UserCreate) -> UserPublic:
    user = await register_user(payload)
    return UserPublic.from_document(user)


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    return await authenticate_user(form.username, form.password)
