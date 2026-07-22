"""
history_service.py
====================
Persistence-facing service for the extraction ``history`` table.

Kept separate from ``database.py`` (which only knows about raw SQL/
connections) so that callers work with typed dictionaries and never see a
``sqlite3.Row`` or a raw cursor.
"""

from __future__ import annotations

import logging

from database import get_connection
from exceptions import HistoryNotFoundError
from schemas import HistoryDetail, HistoryItem, HistoryListResponse
from utils import make_preview

logger = logging.getLogger(__name__)


def save_result(
    *,
    filename: str,
    text: str,
    language: str,
    model: str,
    char_count: int,
    word_count: int,
    structured: bool,
) -> int:
    """Insert a new extraction result and return its generated id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO history (filename, extracted_text, language, model,
                                  char_count, word_count, structured)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, text, language, model, char_count, word_count, int(structured)),
        )
        new_id = cursor.lastrowid
    logger.info("Saved history record id=%s filename=%s", new_id, filename)
    return int(new_id)


def get_created_at(record_id: int) -> str:
    """Fetch just the ``created_at`` timestamp for a freshly inserted row."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT created_at FROM history WHERE id = ?", (record_id,)
        ).fetchone()
    if row is None:
        raise HistoryNotFoundError(f"History record {record_id} not found.")
    return row["created_at"]


def list_history(limit: int = 25, offset: int = 0) -> HistoryListResponse:
    """Return a page of history items, newest first, plus the total count."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, filename, extracted_text, language, model,
                   char_count, word_count, structured, created_at
            FROM history
            ORDER BY created_at DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) AS n FROM history").fetchone()["n"]

    items = [
        HistoryItem(
            id=row["id"],
            filename=row["filename"],
            preview=make_preview(row["extracted_text"]),
            language=row["language"],
            model=row["model"],
            char_count=row["char_count"],
            word_count=row["word_count"],
            structured=bool(row["structured"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]
    return HistoryListResponse(items=items, total=total, limit=limit, offset=offset)


def get_history_detail(record_id: int) -> HistoryDetail:
    """Fetch a single history record with the full extracted text."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, filename, extracted_text, language, model,
                   char_count, word_count, structured, created_at
            FROM history WHERE id = ?
            """,
            (record_id,),
        ).fetchone()

    if row is None:
        raise HistoryNotFoundError(f"History record {record_id} not found.")

    return HistoryDetail(
        id=row["id"],
        filename=row["filename"],
        preview=make_preview(row["extracted_text"]),
        text=row["extracted_text"],
        language=row["language"],
        model=row["model"],
        char_count=row["char_count"],
        word_count=row["word_count"],
        structured=bool(row["structured"]),
        created_at=row["created_at"],
    )


def delete_history_item(record_id: int) -> None:
    """Delete a single history record. Raises if it does not exist."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
        if cursor.rowcount == 0:
            raise HistoryNotFoundError(f"History record {record_id} not found.")
    logger.info("Deleted history record id=%s", record_id)


def clear_history() -> int:
    """Delete every history record and return how many rows were removed."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM history")
        deleted = cursor.rowcount
    logger.info("Cleared history (%d records removed)", deleted)
    return deleted
