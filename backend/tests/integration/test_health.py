import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app.db.connection import build_engine
from app.main import create_app


@pytest.mark.integration
def test_ready_connects_to_postgresql() -> None:
    """REQ-NF-001, REQ-OPS-007: verify readiness against real test PostgreSQL."""
    raw_url = os.environ.get("TEST_DATABASE_URL")
    if not raw_url:
        pytest.fail("TEST_DATABASE_URL is required; use the dedicated test database")
    url = make_url(raw_url)
    # Fail closed: never fall back to the development or production connection.
    if (
        url.drivername != "postgresql+psycopg"
        or url.database != "todo_test"
        or url.username != "todo_test"
        or url.host not in {"127.0.0.1", "localhost", "db-test"}
    ):
        pytest.fail("Only the dedicated local todo_test PostgreSQL is allowed")
    with TestClient(create_app(build_engine(url))) as client:
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
