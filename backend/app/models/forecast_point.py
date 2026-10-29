from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ForecastPoint(Base):
    __tablename__ = "forecast_points"

    __table_args__ = (
        UniqueConstraint(
            "forecast_run_id",
            "step_number",
            name="uq_forecast_points_run_step",
        ),
        CheckConstraint(
            "step_number > 0",
            name="ck_forecast_points_step",
        ),
        CheckConstraint(
            "lower_bound IS NULL OR upper_bound IS NULL "
            "OR lower_bound <= upper_bound",
            name="ck_forecast_points_interval",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    forecast_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("forecast_runs.id"), nullable=False
    )
    step_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    forecast_period_end: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    predicted_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 6), nullable=False
    )
    lower_bound: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 6), nullable=True
    )
    upper_bound: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 6), nullable=True
    )