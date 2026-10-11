from collections.abc import Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse


def health_router(check_database: Callable[[], bool]) -> APIRouter:
    router = APIRouter(prefix="/health", tags=["health"])

    @router.get("/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/ready")
    def ready() -> JSONResponse:
        available = check_database()
        return JSONResponse(
            status_code=200 if available else 503,
            content={"status": "ok" if available else "unavailable"},
            headers={"Cache-Control": "no-store"},
        )

    return router
