from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.schemas.segmentation import ProcessingJobResponse
from app.services.processing_service import create_processing_job, get_job_for_user

router = APIRouter(prefix="/processing")


@router.post("/uploads/{upload_id}/run", response_model=ProcessingJobResponse)
async def run_processing(
    upload_id: UUID,
    user: User = Depends(get_current_active_user),
) -> ProcessingJobResponse:
    job = await create_processing_job(user, upload_id)
    return ProcessingJobResponse.from_document(job)


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_job(
    job_id: UUID,
    user: User = Depends(get_current_active_user),
) -> ProcessingJobResponse:
    job = await get_job_for_user(user, job_id)
    return ProcessingJobResponse.from_document(job)
