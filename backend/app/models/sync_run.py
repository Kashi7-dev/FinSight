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
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'PARTIAL', 'FAILED')",
            name="ck_sync_runs_status",
        ),
        CheckConstraint(
            "records_fetched >= 0 "
            "AND records_accepted >= 0 "
            "AND records_rejected >= 0",
            name="ck_sync_runs_record_counts",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    data_source_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("data_sources.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="RUNNING"
    )
    records_fetched: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    records_accepted: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    records_rejected: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
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