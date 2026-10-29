from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
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


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED', 'UNAVAILABLE')",
            name="ck_forecast_runs_status",
        ),
        CheckConstraint(
            "horizon_periods > 0",
            name="ck_forecast_runs_horizon",
        ),
        CheckConstraint(
            "frequency IN ('ANNUAL', 'QUARTERLY')",
            name="ck_forecast_runs_frequency",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    company_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("company_profiles.id"), nullable=False
    )
    target_metric_code: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    algorithm_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    model_version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    frequency: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    horizon_periods: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    training_period_end: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="RUNNING"
    )
    warning: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )