from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('QUEUED', 'PROCESSING', 'REVIEW_REQUIRED', "
            "'COMPLETED', 'FAILED')",
            name="ck_extraction_jobs_status",
        ),
        CheckConstraint(
            "attempt_number >= 1",
            name="ck_extraction_jobs_attempt",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("financial_reports.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="QUEUED"
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )