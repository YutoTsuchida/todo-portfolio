import os

from sqlalchemy import URL


def database_url() -> URL:
    """Read required settings without embedding credentials in source code."""
    return URL.create(
        "postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["POSTGRES_DB"],
    )
