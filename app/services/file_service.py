import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.db.models.upload import MediaType, Upload, UploadCategory
from app.db.models.user import User
from app.services.activity_service import log_activity
from app.utils.dataset_zip import extract_dataset_zip


def _media_type_for_extension(ext: str, category: UploadCategory) -> MediaType:
    if category == UploadCategory.DATASET:
        if ext != ".zip":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset uploads must be a .zip file of images",
            )
        return MediaType.DATASET
    if ext in settings.allowed_image_exts:
        return MediaType.IMAGE
    if ext in settings.allowed_video_exts:
        return MediaType.VIDEO
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")


def _validate_category_media(category: UploadCategory, media_type: MediaType) -> None:
    if category == UploadCategory.DASHCAM_VIDEO and media_type != MediaType.VIDEO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dashcam category requires a video file",
        )
    if category in (UploadCategory.ROAD_IMAGE, UploadCategory.TRAFFIC_SCENE) and media_type != MediaType.IMAGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Road/traffic scene categories require an image file",
        )
    if category == UploadCategory.DATASET and media_type != MediaType.DATASET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset category requires a .zip archive of images",
        )


async def save_upload(
    user: User,
    file: UploadFile,
    category: UploadCategory,
) -> Upload:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    ext = Path(file.filename).suffix.lower()
    media_type = _media_type_for_extension(ext, category)
    _validate_category_media(category, media_type)

    settings.upload_path.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest = settings.upload_path / stored_name

    size = 0
    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                await out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
                )
            await out.write(chunk)

    dataset_paths: list[str] = []
    dataset_count = 0
    validation_message = "File type and size validated"
    if media_type == MediaType.DATASET:
        extract_root = settings.upload_path / "datasets" / stored_name.replace(ext, "")
        dataset_paths = extract_dataset_zip(dest, extract_root)
        dataset_count = len(dataset_paths)
        total_in_zip = sum(
            1
            for p in extract_root.rglob("*")
            if p.is_file() and p.suffix.lower() in settings.allowed_image_exts
        )
        if total_in_zip > dataset_count:
            validation_message = (
                f"Extracted {dataset_count} of {total_in_zip} images "
                f"(limit {settings.DATASET_MAX_IMAGES} per job)"
            )
        else:
            validation_message = f"Dataset ready: {dataset_count} image(s)"

    upload = Upload(
        user_id=user.id,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=str(dest),
        media_type=media_type,
        category=category,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        is_validated=True,
        validation_message=validation_message,
        dataset_image_paths=dataset_paths,
        dataset_image_count=dataset_count,
    )
    await upload.insert()
    await log_activity(
        user.id,
        "file_uploaded",
        "upload",
        upload.id,
        {"category": category.value, "media_type": media_type.value},
    )
    return upload
