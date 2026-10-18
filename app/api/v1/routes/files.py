from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.access import user_owns_resource
from app.core.dependencies import get_current_active_user
from app.db.models.upload import Upload
from app.db.models.user import User
from app.utils.filenames import result_download_filename

router = APIRouter(prefix="/files")


def _safe_path(relative: str) -> Path:
    base = settings.result_path.resolve()
    target = (base / relative).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return target


def _media_type_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "application/pdf"
    if ext in (".mp4", ".mov"):
        return "video/mp4"
    if ext in (".png",):
        return "image/png"
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    return "application/octet-stream"


@router.get("/uploads/{upload_id}")
async def get_upload_file(
    upload_id: UUID,
    user: User = Depends(get_current_active_user),
) -> FileResponse:
    upload = await Upload.get(upload_id)
    if not upload or not user_owns_resource(user, upload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    path = Path(upload.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(
        path,
        filename=upload.original_filename,
        media_type=_media_type_for(path),
    )


@router.get("/results/{job_id}/{filename}")
async def get_result_file(
    job_id: UUID,
    filename: str,
    user: User = Depends(get_current_active_user),
) -> FileResponse:
    from app.db.models.processing_job import ProcessingJob

    job = await ProcessingJob.get(job_id)
    if not job or not user_owns_resource(user, job.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    path = _safe_path(f"{job_id}/{filename}")
    upload = await Upload.get(job.upload_id)
    download_name = result_download_filename(
        upload.original_filename if upload else None,
        filename,
    )
    return FileResponse(path, filename=download_name, media_type=_media_type_for(path))
