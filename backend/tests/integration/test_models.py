from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session as OrmSession

from app.db.models import Session, Todo, User

pytestmark = pytest.mark.integration


def make_user(username: str = "alice") -> User:
    return User(username=username, password_hash="argon2id-placeholder")


def make_todo(user: User, title: str = "Todo") -> Todo:
    return Todo(user=user, title=title)


def make_session(user: User, marker: int = 1) -> Session:
    created_at = datetime(2026, 10, 11, marker, tzinfo=UTC)
    return Session(
        token_hash=bytes([marker]) * 32,
        user=user,
        csrf_token=f"csrf-{marker}",
        created_at=created_at,
        expires_at=created_at + timedelta(hours=8),
    )


def test_user_defaults_and_relationships(db_session: OrmSession) -> None:
    """REQ-D-001, REQ-D-003: User owns zero or more Todos and Sessions."""
    user = make_user()
    todo = make_todo(user)
    login_session = make_session(user)
    db_session.add(user)
    db_session.flush()

    assert isinstance(user.id, uuid.UUID)
    assert user.created_at.tzinfo is not None
    assert todo.user is user and todo in user.todos
    assert login_session.user is user and login_session in user.sessions


@pytest.mark.parametrize("column", ["id", "username", "password_hash", "created_at"])
def test_user_required_columns_reject_null(db_session: OrmSession, column: str) -> None:
    """REQ-D-001, REQ-D-005: required User data cannot be NULL."""
    values = {
        "id": uuid.uuid4(),
        "username": "alice",
        "password_hash": "hash",
        "created_at": datetime.now(UTC),
    }
    values[column] = None
    with pytest.raises(IntegrityError):
        db_session.execute(insert(User).values(**values))


@pytest.mark.parametrize(
    "username",
    ["ab", "a" * 31, "Alice", "ali ce", "alice!", "アリス"],
)
def test_user_username_check_rejects_invalid_values(
    db_session: OrmSession, username: str
) -> None:
    """REQ-D-001, REQ-T-002: DB enforces normalized username boundaries."""
    db_session.add(make_user(username))
    with pytest.raises(DatabaseError):
        db_session.flush()


@pytest.mark.parametrize("username", ["abc", "a" * 30, "alice_1", "alice-1"])
def test_user_username_check_accepts_valid_values(
    db_session: OrmSession, username: str
) -> None:
    """REQ-D-001, REQ-T-002: valid normalized usernames are accepted."""
    db_session.add(make_user(username))
    db_session.flush()


def test_user_username_is_unique(db_session: OrmSession) -> None:
    """REQ-F-001, REQ-D-001: normalized username is unique."""
    db_session.add_all([make_user("alice"), make_user("alice")])
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_todo_defaults_same_title_and_completed(db_session: OrmSession) -> None:
    """REQ-D-002, REQ-D-008: Todo defaults and duplicate titles."""
    user = make_user()
    first = make_todo(user, "same")
    second = make_todo(user, "same")
    third = Todo(user=user, title="done", status="completed")
    db_session.add_all([first, second, third])
    db_session.flush()

    assert first.description == ""
    assert first.status == "incomplete"
    assert first.created_at.tzinfo is not None
    assert first.updated_at.tzinfo is not None
    assert third.status == "completed"


@pytest.mark.parametrize(
    "column",
    [
        "id",
        "user_id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    ],
)
def test_todo_required_columns_reject_null(db_session: OrmSession, column: str) -> None:
    """REQ-D-002, REQ-D-003, REQ-D-005: required Todo data cannot be NULL."""
    user = make_user()
    db_session.add(user)
    db_session.flush()
    values = {
        "id": uuid.uuid4(),
        "user_id": user.id,
        "title": "Todo",
        "description": "",
        "status": "incomplete",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    values[column] = None
    with pytest.raises(IntegrityError):
        db_session.execute(insert(Todo).values(**values))


def test_todo_rejects_unknown_user(db_session: OrmSession) -> None:
    """REQ-D-003: an ownerless Todo cannot be saved."""
    db_session.add(Todo(user_id=uuid.uuid4(), title="orphan"))
    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize("title", ["x", "x" * 100])
def test_todo_title_accepts_boundaries(db_session: OrmSession, title: str) -> None:
    """REQ-D-002, REQ-T-002: title accepts 1 and 100 code points."""
    db_session.add(make_todo(make_user(), title))
    db_session.flush()


@pytest.mark.parametrize(
    "title",
    [
        "",
        "x" * 101,
        " ",
        " leading",
        "trailing ",
        "line\nfeed",
        "carriage\rreturn",
        "next\x85line",
        "line\u2028separator",
        "paragraph\u2029separator",
    ],
)
def test_todo_title_rejects_invalid_values(db_session: OrmSession, title: str) -> None:
    """REQ-D-002, REQ-T-002: title DB checks reject invalid input."""
    db_session.add(make_todo(make_user(), title))
    with pytest.raises(DatabaseError):
        db_session.flush()


@pytest.mark.parametrize(
    "whitespace",
    [
        *(chr(value) for value in range(0x0009, 0x000E)),
        "\u0020",
        "\u0085",
        "\u00a0",
        "\u1680",
        *(chr(value) for value in range(0x2000, 0x200B)),
        "\u2028",
        "\u2029",
        "\u202f",
        "\u205f",
        "\u3000",
    ],
)
@pytest.mark.parametrize("side", ["leading", "trailing"])
def test_todo_title_rejects_each_surrounding_unicode_whitespace(
    db_session: OrmSession, whitespace: str, side: str
) -> None:
    """REQ-D-002, REQ-T-002: exact DESIGN.md White_Space set is enforced."""
    title = f"{whitespace}title" if side == "leading" else f"title{whitespace}"
    db_session.add(make_todo(make_user(), title))
    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize("length", [0, 1000])
def test_todo_description_accepts_boundaries(
    db_session: OrmSession, length: int
) -> None:
    """REQ-D-002, REQ-T-002: description accepts 0 and 1000 code points."""
    db_session.add(Todo(user=make_user(), title="Todo", description="x" * length))
    db_session.flush()


def test_todo_description_rejects_1001_characters(db_session: OrmSession) -> None:
    """REQ-D-002, REQ-T-002: description rejects 1001 code points."""
    db_session.add(Todo(user=make_user(), title="Todo", description="x" * 1001))
    with pytest.raises(DatabaseError):
        db_session.flush()


def test_todo_rejects_invalid_status(db_session: OrmSession) -> None:
    """REQ-D-008, REQ-T-002: only incomplete/completed are valid."""
    db_session.add(Todo(user=make_user(), title="Todo", status="invalid"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_user_delete_is_restricted_by_todo(db_session: OrmSession) -> None:
    """REQ-D-003, REQ-D-006: Todo prevents owner deletion."""
    user = make_user()
    db_session.add(make_todo(user))
    db_session.flush()
    with pytest.raises(IntegrityError):
        db_session.execute(delete(User).where(User.id == user.id))


def test_todo_delete_keeps_user(db_session: OrmSession) -> None:
    """REQ-D-009: physical Todo deletion does not delete its owner."""
    user = make_user()
    todo = make_todo(user)
    db_session.add(todo)
    db_session.flush()
    db_session.delete(todo)
    db_session.flush()
    assert db_session.get(User, user.id) is user


def test_session_valid_constraints_and_multiple_per_user(
    db_session: OrmSession,
) -> None:
    """REQ-F-003, REQ-SEC-008: a User can own independent Sessions."""
    user = make_user()
    first = make_session(user, 1)
    second = make_session(user, 2)
    db_session.add_all([first, second])
    db_session.flush()
    assert first.user is user and second.user is user
    assert len(user.sessions) == 2


@pytest.mark.parametrize("length", [31, 33])
def test_session_token_hash_requires_32_bytes(
    db_session: OrmSession, length: int
) -> None:
    """REQ-SEC-008: token hash has SHA-256 output length."""
    login_session = make_session(make_user())
    login_session.token_hash = b"x" * length
    db_session.add(login_session)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_session_token_hash_is_unique(db_session: OrmSession) -> None:
    """REQ-SEC-008: token hash primary key cannot be duplicated."""
    user = make_user()
    db_session.add_all([make_session(user), make_session(user)])
    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize(
    "column", ["token_hash", "user_id", "csrf_token", "created_at", "expires_at"]
)
def test_session_required_columns_reject_null(
    db_session: OrmSession, column: str
) -> None:
    """REQ-SEC-008: required Session data cannot be NULL."""
    user = make_user()
    db_session.add(user)
    db_session.flush()
    created_at = datetime.now(UTC)
    values = {
        "token_hash": b"x" * 32,
        "user_id": user.id,
        "csrf_token": "csrf",
        "created_at": created_at,
        "expires_at": created_at + timedelta(hours=8),
    }
    values[column] = None
    with pytest.raises(IntegrityError):
        db_session.execute(insert(Session).values(**values))


def test_session_rejects_unknown_user(db_session: OrmSession) -> None:
    """REQ-SEC-008: an ownerless Session cannot be saved."""
    created_at = datetime.now(UTC)
    db_session.add(
        Session(
            token_hash=b"x" * 32,
            user_id=uuid.uuid4(),
            csrf_token="csrf",
            created_at=created_at,
            expires_at=created_at + timedelta(hours=8),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_session_rejects_non_eight_hour_duration(db_session: OrmSession) -> None:
    """REQ-SEC-008, REQ-T-004: Session duration is exactly eight hours."""
    login_session = make_session(make_user())
    login_session.expires_at += timedelta(seconds=1)
    db_session.add(login_session)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_user_delete_is_restricted_by_session(db_session: OrmSession) -> None:
    """REQ-SEC-008: Session prevents owner deletion."""
    user = make_user()
    db_session.add(make_session(user))
    db_session.flush()
    with pytest.raises(IntegrityError):
        db_session.execute(delete(User).where(User.id == user.id))


def test_deleting_one_session_keeps_user_todo_and_other_session(
    db_session: OrmSession,
) -> None:
    """REQ-F-003: logout deletes only the selected Session row."""
    user = make_user()
    todo = make_todo(user)
    first = make_session(user, 1)
    second = make_session(user, 2)
    db_session.add_all([todo, first, second])
    db_session.flush()
    db_session.delete(first)
    db_session.flush()

    assert db_session.get(User, user.id) is user
    assert db_session.get(Todo, todo.id) is todo
    assert (
        db_session.scalar(
            select(Session).where(Session.token_hash == second.token_hash)
        )
        is second
    )
