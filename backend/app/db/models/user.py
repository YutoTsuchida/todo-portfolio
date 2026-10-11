from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.db.models.session import Session
    from app.db.models.todo import Todo


class User(Base):
    """REQ-D-001, REQ-D-005, REQ-SEC-004: normalized account data."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "username ~ '^[a-z0-9_-]{3,30}$'",
            name="username_format",
        ),
        UniqueConstraint("username", name="uq_users_username"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    todos: Mapped[list[Todo]] = relationship(
        back_populates="user", passive_deletes="all"
    )
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user", passive_deletes="all"
    )
