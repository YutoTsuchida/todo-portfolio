"""Create users, todos, and sessions.

Revision ID: 20261011_01
Revises:
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261011_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

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


def upgrade() -> None:
    """REQ-D-001 through REQ-D-008, REQ-SEC-004, REQ-SEC-008."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "username ~ '^[a-z0-9_-]{3,30}$'",
            name=op.f("ck_users_username_format"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "todos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column(
            "description", sa.String(length=1000), server_default="", nullable=False
        ),
        sa.Column("status", sa.Text(), server_default="incomplete", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "char_length(title) BETWEEN 1 AND 100",
            name=op.f("ck_todos_title_length"),
        ),
        sa.CheckConstraint(
            f"substring(title FROM 1 FOR 1) NOT IN ({UNICODE_WHITE_SPACE_SQL}) "
            f"AND substring(title FROM char_length(title) FOR 1) "
            f"NOT IN ({UNICODE_WHITE_SPACE_SQL})",
            name=op.f("ck_todos_title_no_surrounding_whitespace"),
        ),
        sa.CheckConstraint(
            TITLE_NEWLINE_CHECK_SQL,
            name=op.f("ck_todos_title_no_newlines"),
        ),
        sa.CheckConstraint(
            "char_length(description) BETWEEN 0 AND 1000",
            name=op.f("ck_todos_description_length"),
        ),
        sa.CheckConstraint(
            "status IN ('incomplete', 'completed')",
            name=op.f("ck_todos_status_values"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_todos_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_todos")),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("csrf_token", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "octet_length(token_hash) = 32",
            name=op.f("ck_sessions_token_hash_length"),
        ),
        sa.CheckConstraint(
            "expires_at = created_at + INTERVAL '8 hours'",
            name=op.f("ck_sessions_fixed_duration"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_sessions_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_sessions")),
    )
    op.create_index(
        op.f("ix_todos_user_id_created_at_id"),
        "todos",
        ["user_id", sa.text("created_at DESC"), sa.text("id DESC")],
        unique=False,
    )
    op.create_index(
        op.f("ix_sessions_expires_at"), "sessions", ["expires_at"], unique=False
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("todos")
    op.drop_table("users")
