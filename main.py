"""
main.py
========
Application entrypoint for OCR Reader.

Run locally with:

    uvicorn main:app --reload

or simply:

    python main.py

which starts Uvicorn programmatically using the host/port from ``.env``.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from exceptions import register_exception_handlers
from logging_config import configure_logging
from router_history import router as history_router
from router_ocr import router as ocr_router
from router_pages import router as pages_router
from schemas import HealthResponse

configure_logging()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s (environment=%s)", settings.app_name, settings.app_version, settings.environment)
    init_db()
    if not settings.has_valid_api_key:
        logger.warning(
            "OPENAI_API_KEY is not set. OCR requests will fail until it is configured in .env."
        )
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-grade OCR extraction powered by the OpenAI Responses API vision models.",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(pages_router)
app.include_router(ocr_router)
app.include_router(history_router)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Lightweight liveness/readiness probe."""
    return HealthResponse(
        status="ok" if settings.has_valid_api_key else "degraded",
        app_name=settings.app_name,
        app_version=settings.app_version,
        openai_configured=settings.has_valid_api_key,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # we manage logging ourselves via logging_config.py
    )
