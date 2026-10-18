from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.db.models.processing_job import JobStatus, ProcessingJob
from app.db.models.report import Report
from app.db.models.upload import Upload
from app.db.models.user import User
from app.ml.cityscapes_labels import DISPLAY_CATEGORIES
from app.schemas.report import ReportResponse
from app.services.activity_service import log_activity
from app.utils.filenames import (
    report_excel_filename,
    report_pdf_filename,
    source_stem,
    unique_report_path,
)


async def build_report_response(report: Report) -> ReportResponse:
    job = await ProcessingJob.get(report.job_id)
    upload = await Upload.get(job.upload_id) if job else None
    stem = source_stem(upload.original_filename if upload else None)
    pdf_name = report_pdf_filename(stem, report.created_at)
    excel_name = report_excel_filename(stem, report.created_at)
    title = f"{stem} — segmentation report"
    return ReportResponse(
        id=report.id,
        job_id=report.job_id,
        pdf_path=report.pdf_path,
        excel_path=report.excel_path,
        created_at=report.created_at,
        source_filename=upload.original_filename if upload else None,
        display_title=title,
        pdf_download_name=pdf_name,
        excel_download_name=excel_name,
    )


async def get_report_download_name(report: Report, file_type: str) -> str:
    meta = await build_report_response(report)
    if file_type == "pdf":
        return meta.pdf_download_name or "segmentation_report.pdf"
    return meta.excel_download_name or "segmentation_report.xlsx"


async def generate_report(user: User, job_id: UUID) -> Report:
    job = await ProcessingJob.get(job_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job not completed")

    upload = await Upload.get(job.upload_id)
    stem = source_stem(upload.original_filename if upload else None)

    settings.report_path.mkdir(parents=True, exist_ok=True)
    pdf_path = unique_report_path(
        settings.report_path,
        report_pdf_filename(stem),
        job.id,
    )
    excel_path = unique_report_path(
        settings.report_path,
        report_excel_filename(stem),
        job.id,
    )

    _write_pdf(job, pdf_path, stem)
    _write_excel(job, excel_path, stem)

    report = Report(
        user_id=user.id,
        job_id=job.id,
        pdf_path=str(pdf_path),
        excel_path=str(excel_path),
    )
    await report.insert()
    await log_activity(user.id, "report_generated", "report", report.id)
    return report


def _write_pdf(job: ProcessingJob, path: Path, title_stem: str) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Semantic Segmentation Report — {title_stem}")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Job ID: {job.id}")
    y -= 15
    c.drawString(50, y, f"Inference time (ms): {job.inference_time_ms}")
    y -= 15
    c.drawString(50, y, f"Detected classes: {job.detected_class_count}")
    y -= 25

    if job.overlay_paths:
        img = ImageReader(job.overlay_paths[0])
        c.drawImage(img, 50, y - 200, width=250, height=200, preserveAspectRatio=True)
        y -= 220

    c.drawString(50, y, "Object summary:")
    y -= 15
    for key, count in job.class_counts.items():
        label = next((cat.label for cat in DISPLAY_CATEGORIES if cat.key == key), key)
        c.drawString(60, y, f"- {label}: {count} pixels")
        y -= 12
        if y < 80:
            c.showPage()
            y = height - 50

    c.save()


def _write_excel(job: ProcessingJob, path: Path, title_stem: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Metric", "Value"])
    ws.append(["Source", title_stem])
    ws.append(["Job ID", str(job.id)])
    ws.append(["Inference time (ms)", job.inference_time_ms])
    ws.append(["Detected class count", job.detected_class_count])
    ws.append(["Model mIoU (reference)", job.model_accuracy_reference])
    ws.append([])
    ws.append(["Class", "Pixel count"])
    for key, count in job.class_counts.items():
        label = next((c.label for c in DISPLAY_CATEGORIES if c.key == key), key)
        ws.append([label, count])
    wb.save(path)
