"""
schemas.py
==========
Pydantic v2 data-transfer objects used across the API boundary and by the
OpenAI structured-output call.

Keeping every schema in one module makes it trivial to see the full public
"shape" of the OCR Reader API at a glance, which matters more than strict
per-layer separation for a project this size.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OCRLanguage(str, Enum):
    """Languages the user can hint to the vision model.

    ``AUTO`` lets the model detect the language(s) present in the image,
    which also correctly handles multi-language documents.
    """

    AUTO = "auto"
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    GERMAN = "german"
    PORTUGUESE = "portuguese"
    ITALIAN = "italian"
    DUTCH = "dutch"
    RUSSIAN = "russian"
    ARABIC = "arabic"
    HINDI = "hindi"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    KOREAN = "korean"


class BlockType(str, Enum):
    """Semantic classification of a detected block of text."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    CAPTION = "caption"
    OTHER = "other"


class OCRTextBlock(BaseModel):
    """A single semantic block of text detected inside the image.

    This is also the schema handed to the OpenAI Responses API structured
    output feature (``text_format``), so the model is constrained to return
    exactly this shape.
    """

    model_config = ConfigDict(extra="forbid")

    type: BlockType = Field(description="Semantic role of this block of text.")
    text: str = Field(description="The verbatim text content of the block.")
    order: int = Field(description="Reading order of this block, starting at 0.")


class OCRStructuredExtraction(BaseModel):
    """Top level structured output requested from the vision model."""

    model_config = ConfigDict(extra="forbid")

    detected_language: str = Field(
        description="Best-guess primary language of the text in the image, e.g. 'English'."
    )
    summary: str = Field(
        description="One sentence describing what kind of document/image this is."
    )
    blocks: list[OCRTextBlock] = Field(
        default_factory=list, description="Ordered semantic blocks of extracted text."
    )
    full_text: str = Field(
        description="The complete extracted text, in natural reading order, "
        "with original line breaks preserved where meaningful."
    )


class OCRExtractRequest(BaseModel):
    """Form-encoded options accompanying an image upload."""

    model_config = ConfigDict(extra="forbid")

    language: OCRLanguage = OCRLanguage.AUTO
    structured: bool = False


class OCRResult(BaseModel):
    """Response returned by the non-streaming extraction endpoint."""

    id: int
    filename: str
    text: str
    detected_language: str
    language_requested: OCRLanguage
    model: str
    structured: bool
    blocks: list[OCRTextBlock] = Field(default_factory=list)
    char_count: int
    word_count: int
    created_at: str


class HistoryItem(BaseModel):
    """Summary row shown in the history list view."""

    id: int
    filename: str
    preview: str
    language: str
    model: str
    char_count: int
    word_count: int
    structured: bool
    created_at: str


class HistoryDetail(HistoryItem):
    """Full history record, including the complete extracted text."""

    text: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    app_version: str
    openai_configured: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str


class StreamEvent(BaseModel):
    """Shape of each Server-Sent-Event payload emitted during streaming OCR."""

    type: Literal["delta", "done", "error"]
    text: str | None = None
    result: OCRResult | None = None
    message: str | None = None
