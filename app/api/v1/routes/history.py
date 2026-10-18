from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.schemas.report import ReportResponse
from app.db.models.upload import Upload
from app.schemas.segmentation import ProcessingJobResponse
from app.schemas.upload import UploadResponse
from app.services.history_service import (
    list_job_history,
    list_report_history,
    list_upload_history,
    list_user_activity,
)
from app.services.report_service import build_report_response

router = APIRouter(prefix="/history")


@router.get("/uploads", response_model=list[UploadResponse])
async def uploads_history(user: User = Depends(get_current_active_user)) -> list[UploadResponse]:
    uploads = await list_upload_history(user)
    return [UploadResponse.from_document(u) for u in uploads]


@router.get("/jobs", response_model=list[ProcessingJobResponse])
async def jobs_history(user: User = Depends(get_current_active_user)) -> list[ProcessingJobResponse]:
    jobs = await list_job_history(user)
    result: list[ProcessingJobResponse] = []
    for job in jobs:
        upload = await Upload.get(job.upload_id)
        name = upload.original_filename if upload else None
        result.append(ProcessingJobResponse.from_document(job, source_filename=name))
    return result


@router.get("/reports", response_model=list[ReportResponse])
async def reports_history(user: User = Depends(get_current_active_user)) -> list[ReportResponse]:
    reports = await list_report_history(user)
    return [await build_report_response(r) for r in reports]


@router.get("/activity")
async def activity_history(user: User = Depends(get_current_active_user)) -> list[dict]:
    activities = await list_user_activity(user)
    return [
        {
            "id": a.id,
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "details": a.details,
            "created_at": a.created_at,
        }
        for a in activities
    ]
