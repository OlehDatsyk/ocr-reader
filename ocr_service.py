"""
ocr_service.py
===============
The AI core of OCR Reader: turns an image into text using the OpenAI
Responses API's vision (image input) capability.

Three capabilities are exposed, matching the three ways the frontend can
ask for text:

1. :meth:`OCRService.extract` - plain extraction, returns raw text.
2. :meth:`OCRService.extract_structured` - same call, but constrained to
   the :class:`schemas.OCRStructuredExtraction` Pydantic schema using the
   Responses API structured-output ("parse") helper.
3. :meth:`OCRService.stream_extract` - streams text deltas back as they
   are generated, for a live "typing" effect in the UI.

The service is intentionally the *only* place in the codebase that talks
to the OpenAI SDK, so the rest of the application never needs to know
which model or API shape is in use.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from openai import APIError, AsyncOpenAI, AuthenticationError

from config import settings
from exceptions import OCRProcessingError, OpenAIConfigurationError
from image_service import ValidatedImage
from schemas import OCRLanguage, OCRStructuredExtraction

logger = logging.getLogger(__name__)

_BASE_INSTRUCTIONS = (
    "You are an expert OCR (optical character recognition) engine embedded in "
    "an enterprise document-processing application. Carefully read every piece "
    "of visible text in the supplied image and transcribe it verbatim, "
    "preserving the original reading order, line breaks and punctuation as "
    "closely as possible. Do not translate the text. Do not summarise, censor, "
    "invent, or omit any text you can see, including small print, stamps, "
    "handwriting and watermarks. If the image contains no legible text, say so "
    "clearly instead of inventing content."
)


def _language_instruction(language: OCRLanguage) -> str:
    if language is OCRLanguage.AUTO:
        return "Detect the language(s) present automatically."
    return f"The dominant language of the document is expected to be {language.value.title()}."


def _build_input(
    image: ValidatedImage, language: OCRLanguage, extra: str = ""
) -> list[dict]:
    prompt = f"{_BASE_INSTRUCTIONS} {_language_instruction(language)} {extra}".strip()
    return [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": image.data_url},
            ],
        }
    ]


class OCRService:
    """Thin, typed wrapper around the OpenAI Responses API vision endpoint."""

    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if not settings.has_valid_api_key:
            raise OpenAIConfigurationError(
                "OPENAI_API_KEY is not configured. Add it to your .env file and restart the server."
            )
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout_seconds,
            )
        return self._client

    async def extract(self, image: ValidatedImage, language: OCRLanguage) -> str:
        """Extract plain text from ``image``. Returns the raw transcription."""
        client = self._get_client()
        try:
            response = await client.responses.create(
                model=settings.openai_model,
                input=_build_input(image, language),
                max_output_tokens=settings.openai_max_output_tokens,
            )
        except AuthenticationError as exc:
            logger.error("OpenAI authentication failed: %s", exc)
            raise OpenAIConfigurationError(
                "OpenAI rejected the configured API key. Verify OPENAI_API_KEY in your .env file."
            ) from exc
        except APIError as exc:
            logger.error("OpenAI API error during extraction: %s", exc)
            raise OCRProcessingError(f"The vision model request failed: {exc}") from exc

        text = (response.output_text or "").strip()
        if not text:
            raise OCRProcessingError(
                "The model returned an empty response for this image."
            )
        return text

    async def extract_structured(
        self, image: ValidatedImage, language: OCRLanguage
    ) -> OCRStructuredExtraction:
        """Extract text constrained to the structured ``OCRStructuredExtraction`` schema."""
        client = self._get_client()
        extra = (
            "Additionally, break the text into ordered semantic blocks "
            "(heading, paragraph, list_item, table, caption, other)."
        )
        try:
            response = await client.responses.parse(
                model=settings.openai_model,
                input=_build_input(image, language, extra=extra),
                text_format=OCRStructuredExtraction,
                max_output_tokens=settings.openai_max_output_tokens,
            )
        except AuthenticationError as exc:
            logger.error("OpenAI authentication failed: %s", exc)
            raise OpenAIConfigurationError(
                "OpenAI rejected the configured API key. Verify OPENAI_API_KEY in your .env file."
            ) from exc
        except APIError as exc:
            logger.error("OpenAI API error during structured extraction: %s", exc)
            raise OCRProcessingError(f"The vision model request failed: {exc}") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise OCRProcessingError(
                "The model did not return a valid structured response."
            )
        return parsed

    async def stream_extract(
        self, image: ValidatedImage, language: OCRLanguage
    ) -> AsyncIterator[str]:
        """Yield text deltas as the model generates the transcription.

        Yields
        ------
        str
            Successive chunks of generated text. Concatenating every yielded
            chunk reproduces the full transcription.
        """
        client = self._get_client()
        try:
            async with client.responses.stream(
                model=settings.openai_model,
                input=_build_input(image, language),
                max_output_tokens=settings.openai_max_output_tokens,
            ) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta
                    elif event.type == "response.error":
                        raise OCRProcessingError(
                            f"Streaming error from OpenAI: {event.error}"
                        )
                await stream.get_final_response()
        except AuthenticationError as exc:
            logger.error("OpenAI authentication failed during streaming: %s", exc)
            raise OpenAIConfigurationError(
                "OpenAI rejected the configured API key. Verify OPENAI_API_KEY in your .env file."
            ) from exc
        except APIError as exc:
            logger.error("OpenAI API error during streaming extraction: %s", exc)
            raise OCRProcessingError(
                f"The vision model streaming request failed: {exc}"
            ) from exc


# Module-level singleton - the service holds no per-request state, only a
# lazily created HTTP client, so sharing one instance across requests is safe.
ocr_service = OCRService()
