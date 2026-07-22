"""
router_history.py
===================
HTTP endpoints for the extraction history: listing, retrieving, deleting
and downloading (TXT / Markdown) past results.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from history_service import clear_history, delete_history_item, get_history_detail, list_history
from schemas import HistoryDetail, HistoryListResponse
from utils import slugify_filename, to_markdown

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
async def get_history(
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> HistoryListResponse:
    """Return a page of past extractions, newest first."""
    return list_history(limit=limit, offset=offset)


@router.get("/{record_id}", response_model=HistoryDetail)
async def get_history_item(record_id: int) -> HistoryDetail:
    """Return the full detail (including complete text) of one record."""
    return get_history_detail(record_id)


@router.delete("/{record_id}")
async def remove_history_item(record_id: int) -> dict[str, str]:
    """Delete a single history record."""
    delete_history_item(record_id)
    return {"status": "deleted"}


@router.delete("")
async def remove_all_history() -> dict[str, int]:
    """Delete every history record. Used by the 'Clear history' button."""
    deleted = clear_history()
    return {"deleted": deleted}


@router.get("/{record_id}/download")
async def download_history_item(
    record_id: int, fmt: Literal["txt", "md"] = Query(default="txt")
) -> PlainTextResponse:
    """Download a single extraction as a plain-text or Markdown file."""
    item = get_history_detail(record_id)
    base_name = slugify_filename(item.filename)

    if fmt == "md":
        body = to_markdown(
            filename=item.filename,
            language=item.language,
            model=item.model,
            created_at=item.created_at,
            text=item.text,
        )
        media_type = "text/markdown"
        download_name = f"{base_name}.md"
    else:
        body = item.text
        media_type = "text/plain"
        download_name = f"{base_name}.txt"

    return PlainTextResponse(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
