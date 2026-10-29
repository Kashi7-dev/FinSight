from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MetricInput(Base):
    __tablename__ = "metric_inputs"

    __table_args__ = (
        UniqueConstraint(
            "metric_result_id",
            "input_role",
            "statement_item_id",
            name="uq_metric_inputs_result_role_item",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    metric_result_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("metric_results.id"), nullable=False
    )
    statement_item_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("statement_items.id"), nullable=False
    )
    input_role: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )