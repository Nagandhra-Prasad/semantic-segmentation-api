from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.services.dataset_service import list_cityscapes_samples

router = APIRouter(prefix="/dataset")


@router.get("/cityscapes/samples")
async def cityscapes_samples(
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
) -> dict:
    samples = list_cityscapes_samples(limit=limit)
    return {"count": len(samples), "samples": samples}
