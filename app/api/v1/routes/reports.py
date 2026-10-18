from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.core.dependencies import get_current_active_user
from app.db.models.report import Report
from app.db.models.user import User
from app.schemas.report import ReportResponse
from app.services.report_service import build_report_response, generate_report, get_report_download_name

router = APIRouter(prefix="/reports")


@router.post("/jobs/{job_id}", response_model=ReportResponse)
async def create_report(
    job_id: UUID,
    user: User = Depends(get_current_active_user),
) -> ReportResponse:
    report = await generate_report(user, job_id)
    return await build_report_response(report)


@router.get("/{report_id}/pdf")
async def download_pdf(
    report_id: UUID,
    user: User = Depends(get_current_active_user),
) -> FileResponse:
    report = await Report.get(report_id)
    if not report or report.user_id != user.id or not report.pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    filename = await get_report_download_name(report, "pdf")
    return FileResponse(
        path=report.pdf_path,
        filename=filename,
        media_type="application/pdf",
    )


@router.get("/{report_id}/excel")
async def download_excel(
    report_id: UUID,
    user: User = Depends(get_current_active_user),
) -> FileResponse:
    report = await Report.get(report_id)
    if not report or report.user_id != user.id or not report.excel_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    filename = await get_report_download_name(report, "excel")
    return FileResponse(
        path=report.excel_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
