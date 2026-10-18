from fastapi import APIRouter

from app.api.v1.routes import (
    admin,
    analytics,
    auth,
    dataset,
    files,
    health,
    history,
    processing,
    reports,
    segmentation,
    uploads,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(uploads.router, tags=["uploads"])
api_router.include_router(processing.router, tags=["processing"])
api_router.include_router(segmentation.router, tags=["segmentation"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(history.router, tags=["history"])
api_router.include_router(dataset.router, tags=["dataset"])
api_router.include_router(files.router, tags=["files"])
