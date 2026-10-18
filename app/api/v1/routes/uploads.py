from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies import get_current_active_user
from app.db.models.upload import UploadCategory
from app.db.models.user import User
from app.schemas.upload import UploadResponse
from app.services.file_service import save_upload

router = APIRouter(prefix="/uploads")


@router.post("", response_model=UploadResponse)
async def upload_media(
    category: UploadCategory = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_active_user),
) -> UploadResponse:
    upload = await save_upload(user, file, category)
    return UploadResponse.from_document(upload)
