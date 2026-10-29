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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint(
            "report_id",
            "chunk_index",
            name="uq_document_chunks_report_index",
        ),
        CheckConstraint(
            "page_start IS NULL OR page_end IS NULL "
            "OR page_start <= page_end",
            name="ck_document_chunks_pages",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("financial_reports.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    page_start: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    page_end: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    section_title: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )