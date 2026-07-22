"""
conftest.py
============
Test environment bootstrap. Environment variables must be set *before* any
application module is imported, since ``config.py`` reads them at import
time via ``get_settings()``.
"""

from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.gettempdir())
TEST_DB_PATH = _TMP / "ocr_reader_test.db"
TEST_LOG_DIR = _TMP / "ocr_reader_test_logs"

os.environ["OPENAI_API_KEY"] = "sk-test-key-not-real"
os.environ["DATABASE_PATH"] = str(TEST_DB_PATH)
os.environ["LOG_DIR"] = str(TEST_LOG_DIR)
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from database import init_db  # noqa: E402
from main import app  # noqa: E402

# A minimal valid 1x1 transparent PNG, used so tests never need a real image file.
_TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


@pytest.fixture()
def tiny_png_bytes() -> bytes:
    return base64.b64decode(_TINY_PNG_B64)


@pytest.fixture()
def client():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    init_db()
    with TestClient(app) as test_client:
        yield test_client
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
