from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    __table_args__ = (
        CheckConstraint(
            "scope IN ('SHARED', 'PRIVATE')",
            name="ck_company_profiles_scope",
        ),
        CheckConstraint(
            "(scope = 'SHARED' AND owner_user_id IS NULL) "
            "OR (scope = 'PRIVATE' AND owner_user_id IS NOT NULL)",
            name="ck_company_profiles_scope_owner",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    ticker_symbol: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    scope: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    owner_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    owner: Mapped["User | None"] = relationship(
        back_populates="company_profiles",
    )