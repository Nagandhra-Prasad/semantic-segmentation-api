from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.ml.cityscapes_labels import legend_payload
from app.schemas.segmentation import DashboardViewResponse, ProcessingJobResponse
from app.db.models.upload import MediaType, Upload
from app.services.processing_service import get_job_for_user

router = APIRouter(prefix="/segmentation")


@router.get("/legend")
def get_legend() -> list[dict]:
    return legend_payload()


@router.get("/dashboard/{job_id}", response_model=DashboardViewResponse)
async def dashboard_view(
    job_id: UUID,
    user: User = Depends(get_current_active_user),
) -> DashboardViewResponse:
    job = await get_job_for_user(user, job_id)
    upload = await Upload.get(job.upload_id)
    return DashboardViewResponse(
        job=ProcessingJobResponse.from_document(job),
        legend=legend_payload(),
        original_media_path=job.original_media_path,
        media_type=upload.media_type if upload else MediaType.IMAGE,
    )
