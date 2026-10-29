from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    __table_args__ = (
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH')",
            name="ck_data_quality_issues_severity",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'APPROVED', 'REJECTED', 'RESOLVED')",
            name="ck_data_quality_issues_status",
        ),
        CheckConstraint(
            "report_id IS NOT NULL OR sync_run_id IS NOT NULL",
            name="ck_data_quality_issues_reference",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    report_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("financial_reports.id"), nullable=True
    )
    sync_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("sync_runs.id"), nullable=True
    )
    reviewed_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )

    issue_code: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    severity: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OPEN"
    )
    resolution_note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )