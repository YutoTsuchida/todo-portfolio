from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session as OrmSession


def require_test_database_url() -> str:
    """Reject destructive integration work outside the dedicated local test DB."""
    raw_url = os.environ.get("TEST_DATABASE_URL")
    if not raw_url:
        pytest.fail("TEST_DATABASE_URL is required; use the dedicated test database")
    url = make_url(raw_url)
    if (
        url.drivername != "postgresql+psycopg"
        or url.database != "todo_test"
        or url.username != "todo_test"
        or url.host not in {"127.0.0.1", "localhost", "db-test"}
    ):
        pytest.fail("Only the dedicated local todo_test PostgreSQL is allowed")
    return raw_url


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    require_test_database_url()
    backend_dir = Path(__file__).resolve().parents[2]
    return Config(backend_dir / "alembic.ini")


@pytest.fixture(scope="session")
def migrated_engine(alembic_config: Config) -> Iterator[Engine]:
    command.upgrade(alembic_config, "head")
    engine = create_engine(require_test_database_url())
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(migrated_engine: Engine) -> Iterator[OrmSession]:
    connection = migrated_engine.connect()
    transaction = connection.begin()
    session = OrmSession(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
