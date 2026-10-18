from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.services.analytics_service import job_analytics, user_analytics_summary

router = APIRouter(prefix="/analytics")


@router.get("/summary")
async def analytics_summary(user: User = Depends(get_current_active_user)) -> dict:
    return await user_analytics_summary(user)


@router.get("/jobs/{job_id}")
async def job_metrics(
    job_id: UUID,
    user: User = Depends(get_current_active_user),
) -> dict:
    return await job_analytics(user, job_id)
