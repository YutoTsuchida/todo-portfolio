import os

from sqlalchemy import URL, make_url


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


def migration_database_url() -> URL:
    """Use the dedicated test URL when supplied, otherwise the development URL."""
    test_url = os.environ.get("TEST_DATABASE_URL")
    return make_url(test_url) if test_url else database_url()
