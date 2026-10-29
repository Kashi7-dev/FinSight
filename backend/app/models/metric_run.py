from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MetricRun(Base):
    __tablename__ = "metric_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_metric_runs_status",
        ),
        CheckConstraint(
            "period_start IS NULL OR period_end IS NULL "
            "OR period_start <= period_end",
            name="ck_metric_runs_period",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    company_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("company_profiles.id"), nullable=False
    )
    period_start: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    period_end: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    formula_set_version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="RUNNING"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )