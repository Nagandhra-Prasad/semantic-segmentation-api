import re
from datetime import datetime
from pathlib import Path
from uuid import UUID


def sanitize_filename(name: str, max_length: int = 120) -> str:
    cleaned = re.sub(r"[^\w.\- ]+", "_", name, flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._ ")
    if not cleaned:
        return "segmentation"
    return cleaned[:max_length]


def source_stem(original_filename: str | None, fallback: str = "segmentation") -> str:
    if not original_filename:
        return fallback
    return sanitize_filename(Path(original_filename).stem) or fallback


def report_pdf_filename(stem: str, created_at: datetime | None = None) -> str:
    ts = (created_at or datetime.now()).strftime("%Y%m%d_%H%M")
    return f"{stem}_segmentation_report_{ts}.pdf"


def report_excel_filename(stem: str, created_at: datetime | None = None) -> str:
    ts = (created_at or datetime.now()).strftime("%Y%m%d_%H%M")
    return f"{stem}_segmentation_report_{ts}.xlsx"


def result_download_filename(
    original_filename: str | None,
    result_basename: str,
) -> str:
    stem = source_stem(original_filename)
    name = result_basename.lower()
    if name.endswith(".mp4"):
        if "overlay" in name:
            return f"{stem}_segmented_overlay.mp4"
        if "segmented" in name:
            return f"{stem}_segmented_mask.mp4"
        return f"{stem}_segmented_preview.mp4"
    if "overlay" in name:
        return f"{stem}_segmented_overlay.png"
    if "segmented" in name:
        return f"{stem}_segmented_mask.png"
    return sanitize_filename(result_basename)


def unique_report_path(directory: Path, filename: str, job_id: UUID) -> Path:
    path = directory / filename
    if path.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        return directory / f"{stem}_{str(job_id)[:8]}{suffix}"
    return path
