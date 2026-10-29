from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MetricResult(Base):
    __tablename__ = "metric_results"

    __table_args__ = (
        UniqueConstraint(
            "metric_run_id",
            "metric_code",
            "period_end",
            name="uq_metric_results_run_code_period",
        ),
        CheckConstraint(
            "result_status IN "
            "('CALCULATED', 'INSUFFICIENT_DATA', "
            "'NOT_APPLICABLE', 'ERROR')",
            name="ck_metric_results_status",
        ),
        CheckConstraint(
            "(result_status = 'CALCULATED' AND value IS NOT NULL) "
            "OR (result_status <> 'CALCULATED' AND value IS NULL)",
            name="ck_metric_results_value_presence",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    metric_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("metric_runs.id"), nullable=False
    )
    metric_code: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 6), nullable=True
    )
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    result_status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    formula_version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    explanation: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )