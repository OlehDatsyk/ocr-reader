"""
database.py
============
Lightweight SQLite persistence layer.

The project deliberately avoids an ORM: the schema is tiny (a single
``history`` table) and the stdlib ``sqlite3`` module is more than enough,
keeps the dependency footprint minimal, and is trivial to reason about.

Design notes
------------
* Every function opens a short-lived connection and closes it again. SQLite
  handles this pattern well and it avoids any cross-request connection
  state or threading foot-guns under Uvicorn's worker model.
* ``sqlite3.Row`` is used as the row factory so callers can access columns
  by name and convert rows to dicts trivially.
* WAL mode is enabled for better concurrent read/write behaviour.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import settings

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT NOT NULL,
    extracted_text  TEXT NOT NULL,
    language        TEXT NOT NULL,
    model           TEXT NOT NULL,
    char_count      INTEGER NOT NULL,
    word_count      INTEGER NOT NULL,
    structured      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_history_created_at ON history (created_at DESC);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with sane pragmas, closing it afterwards."""
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the database schema if it does not already exist."""
    with get_connection() as conn:
        conn.executescript(_SCHEMA)
    logger.info("Database initialised at %s", settings.database_path)
