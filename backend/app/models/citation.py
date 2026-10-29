from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Citation(Base):
    __tablename__ = "citations"

    __table_args__ = (
        UniqueConstraint(
            "chat_message_id",
            "citation_order",
            name="uq_citations_message_order",
        ),
        CheckConstraint(
            "citation_order > 0",
            name="ck_citations_order",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4
    )
    chat_message_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("chat_messages.id"), nullable=False
    )
    document_chunk_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("document_chunks.id"), nullable=False
    )
    citation_order: Mapped[int] = mapped_column(
        Integer, nullable=False
    )