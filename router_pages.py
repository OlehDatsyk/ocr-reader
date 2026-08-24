"""
router_pages.py
=================
Serves the server-rendered HTML shell for the dashboard. All dynamic data
(history, extraction results) is fetched client-side from the ``/api/*``
JSON endpoints defined in ``router_ocr.py`` and ``router_history.py`` - these
routes only render the static page scaffolding via Jinja2.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import settings
from schemas import OCRLanguage
from utils import LANGUAGE_LABELS

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent / "templates")
)

_LANGUAGE_OPTIONS = [(lang.value, label) for lang, label in LANGUAGE_LABELS.items()]


def _base_context(active: str) -> dict:
    return {
        "active": active,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "languages": _LANGUAGE_OPTIONS,
        "openai_configured": settings.has_valid_api_key,
    }


@router.get("/", response_class=HTMLResponse)
async def page_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "index.html", _base_context(active="upload")
    )


@router.get("/history", response_class=HTMLResponse)
async def page_history(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "history.html", _base_context(active="history")
    )


@router.get("/settings", response_class=HTMLResponse)
async def page_settings(request: Request) -> HTMLResponse:
    context = _base_context(active="settings")
    context.update(
        {
            "openai_model": settings.openai_model,
            "max_upload_size_mb": settings.max_upload_size_mb,
            "environment": settings.environment,
            "app_version": settings.app_version,
        }
    )
    return templates.TemplateResponse(request, "settings.html", context)
