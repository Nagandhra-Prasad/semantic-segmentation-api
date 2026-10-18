from datetime import UTC, datetime
from uuid import UUID

from pydantic import Field

from app.db.base import UUIDDocument


class Report(UUIDDocument):
    user_id: UUID
    job_id: UUID
    pdf_path: str | None = None
    excel_path: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "reports"
