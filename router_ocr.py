"""
router_ocr.py
==============
HTTP endpoints for turning an uploaded image into text.

Three endpoints, mirroring ``OCRService``:

* ``POST /api/ocr/extract``        - plain or structured extraction (JSON body back).
* ``POST /api/ocr/stream``         - Server-Sent-Events stream of text deltas.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import StreamingResponse

from config import settings
from history_service import get_created_at, save_result
from image_service import validate_upload
from ocr_service import ocr_service
from schemas import OCRLanguage, OCRResult, StreamEvent
from utils import char_count, word_count

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


@router.post("/extract", response_model=OCRResult)
async def extract_text(
    file: UploadFile,
    language: OCRLanguage = Form(default=OCRLanguage.AUTO),
    structured: bool = Form(default=False),
) -> OCRResult:
    """Extract text from an uploaded image and persist it to history."""
    image = await validate_upload(file)

    if structured:
        parsed = await ocr_service.extract_structured(image, language)
        text = parsed.full_text
        detected_language = parsed.detected_language
        blocks = parsed.blocks
    else:
        text = await ocr_service.extract(image, language)
        detected_language = (
            language.value if language != OCRLanguage.AUTO else "auto-detected"
        )
        blocks = []

    record_id = save_result(
        filename=image.filename,
        text=text,
        language=detected_language,
        model=settings.openai_model,
        char_count=char_count(text),
        word_count=word_count(text),
        structured=structured,
    )
    created_at = get_created_at(record_id)

    return OCRResult(
        id=record_id,
        filename=image.filename,
        text=text,
        detected_language=detected_language,
        language_requested=language,
        model=settings.openai_model,
        structured=structured,
        blocks=blocks,
        char_count=char_count(text),
        word_count=word_count(text),
        created_at=created_at,
    )


@router.post("/stream")
async def stream_extract(
    file: UploadFile,
    language: OCRLanguage = Form(default=OCRLanguage.AUTO),
) -> StreamingResponse:
    """Stream extracted text back as Server-Sent Events.

    Each event is a JSON-encoded :class:`schemas.StreamEvent`. The final
    ``done`` event carries the persisted :class:`schemas.OCRResult`.
    """
    image = await validate_upload(file)

    async def event_generator():
        collected: list[str] = []
        try:
            async for delta in ocr_service.stream_extract(image, language):
                collected.append(delta)
                event = StreamEvent(type="delta", text=delta)
                yield f"data: {event.model_dump_json()}\n\n"

            full_text = "".join(collected).strip()
            if not full_text:
                raise ValueError("The model returned no text for this image.")

            detected_language = (
                language.value if language != OCRLanguage.AUTO else "auto-detected"
            )
            record_id = save_result(
                filename=image.filename,
                text=full_text,
                language=detected_language,
                model=settings.openai_model,
                char_count=char_count(full_text),
                word_count=word_count(full_text),
                structured=False,
            )
            created_at = get_created_at(record_id)
            result = OCRResult(
                id=record_id,
                filename=image.filename,
                text=full_text,
                detected_language=detected_language,
                language_requested=language,
                model=settings.openai_model,
                structured=False,
                blocks=[],
                char_count=char_count(full_text),
                word_count=word_count(full_text),
                created_at=created_at,
            )
            done_event = StreamEvent(type="done", result=result)
            yield f"data: {done_event.model_dump_json()}\n\n"
        except Exception as exc:  # noqa: BLE001 - streamed to the client as an SSE error event
            logger.exception("Streaming OCR failed")
            error_event = StreamEvent(type="error", message=str(exc))
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
