"""
utils.py
========
Small, dependency-free helper functions shared across the codebase.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from schemas import OCRLanguage

# Human-readable labels for the language dropdown in the UI. Kept here (not
# in the frontend) so the backend remains the single source of truth for
# what "language" strings mean.
LANGUAGE_LABELS: dict[OCRLanguage, str] = {
    OCRLanguage.AUTO: "Auto-detect",
    OCRLanguage.ENGLISH: "English",
    OCRLanguage.SPANISH: "Spanish",
    OCRLanguage.FRENCH: "French",
    OCRLanguage.GERMAN: "German",
    OCRLanguage.PORTUGUESE: "Portuguese",
    OCRLanguage.ITALIAN: "Italian",
    OCRLanguage.DUTCH: "Dutch",
    OCRLanguage.RUSSIAN: "Russian",
    OCRLanguage.ARABIC: "Arabic",
    OCRLanguage.HINDI: "Hindi",
    OCRLanguage.CHINESE: "Chinese",
    OCRLanguage.JAPANESE: "Japanese",
    OCRLanguage.KOREAN: "Korean",
}


def word_count(text: str) -> int:
    """Count whitespace-separated words in ``text``."""
    return len(text.split())


def char_count(text: str) -> int:
    """Count characters in ``text``."""
    return len(text)


def make_preview(text: str, max_chars: int = 160) -> str:
    """Collapse whitespace and truncate ``text`` for list-view previews."""
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= max_chars:
        return collapsed
    return collapsed[: max_chars - 1].rstrip() + "…"


def utc_now_iso() -> str:
    """Current UTC time as an ISO-8601 string (second precision)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def to_markdown(filename: str, language: str, model: str, created_at: str, text: str) -> str:
    """Render an extraction result as a small, self-contained Markdown document."""
    lines = [
        f"# OCR Result — {filename}",
        "",
        f"- **Detected language:** {language}",
        f"- **Model:** {model}",
        f"- **Extracted at (UTC):** {created_at}",
        "",
        "---",
        "",
        text.strip(),
        "",
    ]
    return "\n".join(lines)


def slugify_filename(name: str) -> str:
    """Produce a filesystem/URL-safe base name (without extension)."""
    base = re.sub(r"\.[^.]+$", "", name)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("_")
    return base or "ocr-result"
