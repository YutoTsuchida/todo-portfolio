from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from app.main import create_app


def test_live_does_not_connect_to_database() -> None:
    """REQ-OPS-007: liveness must not depend on PostgreSQL."""
    engine = Mock(spec=Engine)
    with TestClient(create_app(engine)) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    engine.connect.assert_not_called()
    engine.dispose.assert_called_once()


def test_ready_hides_database_failure() -> None:
    """REQ-SEC-010: database exceptions must never enter the response."""
    engine = Mock(spec=Engine)
    engine.connect.side_effect = OperationalError(
        "SELECT 1", {}, Exception("private database connection details")
    )
    with TestClient(create_app(engine)) as client:
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert response.headers["cache-control"] == "no-store"
