from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: UUID
    job_id: UUID
    pdf_path: str | None
    excel_path: str | None
    created_at: datetime
    source_filename: str | None = None
    display_title: str | None = None
    pdf_download_name: str | None = None
    excel_download_name: str | None = None
