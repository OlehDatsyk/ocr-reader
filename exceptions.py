"""
exceptions.py
=============
Application-specific exceptions and their FastAPI exception handlers.

Raising a specific exception type (instead of a bare ``HTTPException``) at
the service layer keeps services free of any HTTP/framework concerns while
still allowing ``main.py`` to translate them into clean, consistent JSON
error responses via ``schemas.ErrorResponse``.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from schemas import ErrorResponse

logger = logging.getLogger(__name__)


class OCRReaderError(Exception):
    """Base class for all application-raised errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidImageError(OCRReaderError):
    """Raised when an uploaded file is not a supported/valid image."""

    status_code = status.HTTP_400_BAD_REQUEST


class FileTooLargeError(OCRReaderError):
    """Raised when an uploaded file exceeds the configured size limit."""

    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class OpenAIConfigurationError(OCRReaderError):
    """Raised when the OpenAI API key is missing or invalid."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class OCRProcessingError(OCRReaderError):
    """Raised when the OpenAI vision call fails or returns unusable output."""

    status_code = status.HTTP_502_BAD_GATEWAY


class HistoryNotFoundError(OCRReaderError):
    """Raised when a requested history record does not exist."""

    status_code = status.HTTP_404_NOT_FOUND


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that turn ``OCRReaderError`` subclasses into JSON."""

    @app.exception_handler(OCRReaderError)
    async def handle_ocr_reader_error(request: Request, exc: OCRReaderError) -> JSONResponse:
        logger.warning("%s on %s: %s", type(exc).__name__, request.url.path, exc.message)
        payload = ErrorResponse(error=type(exc).__name__, detail=exc.message)
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s", request.url.path)
        payload = ErrorResponse(
            error="InternalServerError",
            detail="An unexpected error occurred. Check the server logs for details.",
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())
