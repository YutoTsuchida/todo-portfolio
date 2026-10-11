from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.db.models.user import User


class Session(Base):
    """REQ-F-003, REQ-SEC-008: revocable fixed-duration database session."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("octet_length(token_hash) = 32", name="token_hash_length"),
        CheckConstraint(
            "expires_at = created_at + INTERVAL '8 hours'",
            name="fixed_duration",
        ),
        Index("ix_sessions_expires_at", "expires_at"),
        Index("ix_sessions_user_id", "user_id"),
    )

    token_hash: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", name="fk_sessions_user_id_users"),
        nullable=False,
    )
    csrf_token: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="sessions")
