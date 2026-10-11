from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine

from app.core.config import database_url
from app.db.connection import build_engine, is_database_ready
from app.routers.health import health_router


def create_app(engine: Engine | None = None) -> FastAPI:
    database = engine if engine is not None else build_engine(database_url())

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            database.dispose()

    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router(lambda: is_database_ready(database)))
    return app
