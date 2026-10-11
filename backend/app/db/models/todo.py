from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.db.models.user import User


UNICODE_WHITE_SPACE_SQL = ", ".join(
    f"chr({code_point})"
    for code_point in (
        *range(0x0009, 0x000E),
        0x0020,
        0x0085,
        0x00A0,
        0x1680,
        *range(0x2000, 0x200B),
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    )
)
TITLE_NEWLINE_CHECK_SQL = " AND ".join(
    f"position(chr({code_point}) in title) = 0"
    for code_point in (0x000A, 0x000D, 0x0085, 0x2028, 0x2029)
)


class Todo(Base):
    """REQ-D-002, REQ-D-003, REQ-D-005, REQ-D-008: owned Todo data."""

    __tablename__ = "todos"
    __table_args__ = (
        CheckConstraint(
            "char_length(title) BETWEEN 1 AND 100",
            name="title_length",
        ),
        CheckConstraint(
            f"substring(title FROM 1 FOR 1) NOT IN ({UNICODE_WHITE_SPACE_SQL}) "
            f"AND substring(title FROM char_length(title) FOR 1) "
            f"NOT IN ({UNICODE_WHITE_SPACE_SQL})",
            name="title_no_surrounding_whitespace",
        ),
        CheckConstraint(TITLE_NEWLINE_CHECK_SQL, name="title_no_newlines"),
        CheckConstraint(
            "char_length(description) BETWEEN 0 AND 1000",
            name="description_length",
        ),
        CheckConstraint(
            "status IN ('incomplete', 'completed')",
            name="status_values",
        ),
        Index(
            "ix_todos_user_id_created_at_id",
            "user_id",
            text("created_at DESC"),
            text("id DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", name="fk_todos_user_id_users"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(
        String(1000), nullable=False, server_default=text("''")
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'incomplete'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    user: Mapped[User] = relationship(back_populates="todos")
