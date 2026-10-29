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
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StatementItem(Base):
    __tablename__ = "statement_items"

    __table_args__ = (
        CheckConstraint(
            "statement_type IN "
            "('BALANCE_SHEET', 'INCOME_STATEMENT', 'CASH_FLOW')",
            name="ck_statement_items_type",
        ),
        CheckConstraint(
            "value_status IN "
            "('PRESENT', 'MISSING', 'NOT_APPLICABLE', "
            "'NOT_DISCLOSED', 'EXTRACTION_FAILED')",
            name="ck_statement_items_value_status",
        ),
        CheckConstraint(
            "(value_status = 'PRESENT' AND value IS NOT NULL) "
            "OR (value_status <> 'PRESENT' AND value IS NULL)",
            name="ck_statement_items_value_presence",
        ),
        CheckConstraint(
            "extraction_confidence IS NULL "
            "OR extraction_confidence BETWEEN 0 AND 1",
            name="ck_statement_items_confidence",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("financial_reports.id"), nullable=False
    )

    statement_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    item_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    normalized_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    raw_label: Mapped[str] = mapped_column(Text, nullable=False)
    raw_value_text: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    value: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 6), nullable=True
    )
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    value_status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    source_page: Mapped[int | None] = mapped_column(
        # Dùng Integer nếu thêm import tương ứng ở phần đầu.
        # Ví dụ đầy đủ ở dưới.
        Integer,
        nullable=True,
    )
    extraction_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )