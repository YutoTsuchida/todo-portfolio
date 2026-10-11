from sqlalchemy import URL, Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def build_engine(url: URL) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_timeout=3,
        connect_args={"connect_timeout": 3, "options": "-c statement_timeout=3000"},
        hide_parameters=True,
    )


def is_database_ready(engine: Engine) -> bool:
    """REQ-OPS-007, REQ-SEC-010: probe without exposing database errors."""
    try:
        with engine.connect() as connection:
            return bool(connection.execute(text("SELECT 1")).scalar_one() == 1)
    except SQLAlchemyError:
        return False
