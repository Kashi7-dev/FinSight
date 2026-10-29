from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    __table_args__ = (
        CheckConstraint(
            "origin IN ('USER_UPLOAD', 'EXTERNAL')",
            name="ck_financial_reports_origin",
        ),
        CheckConstraint(
            "report_type IN ('ANNUAL', 'QUARTERLY', 'INTERIM')",
            name="ck_financial_reports_type",
        ),
        CheckConstraint(
            "statement_scope IN ('CONSOLIDATED', 'SEPARATE')",
            name="ck_financial_reports_scope",
        ),
        CheckConstraint(
            "(origin = 'USER_UPLOAD' "
            "AND uploaded_by_user_id IS NOT NULL "
            "AND data_source_id IS NULL) "
            "OR "
            "(origin = 'EXTERNAL' "
            "AND uploaded_by_user_id IS NULL "
            "AND data_source_id IS NOT NULL)",
            name="ck_financial_reports_origin_owner",
        ),
        CheckConstraint(
            "fiscal_quarter IS NULL OR fiscal_quarter BETWEEN 1 AND 4",
            name="ck_financial_reports_quarter",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    company_profile_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("company_profiles.id"), nullable=False
    )
    uploaded_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    data_source_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("data_sources.id"), nullable=True
    )

    origin: Mapped[str] = mapped_column(String(20), nullable=False)
    report_type: Mapped[str] = mapped_column(String(20), nullable=False)
    statement_scope: Mapped[str] = mapped_column(String(20), nullable=False)

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    fiscal_quarter: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    period_start: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    period_end: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    original_filename: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    storage_key: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    source_url: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="UPLOADED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )