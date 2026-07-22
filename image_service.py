"""
image_service.py
=================
Validates uploaded image bytes and prepares them for the OpenAI Vision
input format.

Images are never written to disk: everything happens in memory and the
raw bytes are discarded as soon as the request finishes, which keeps the
application stateless with respect to user content (only the *extracted
text* is persisted, in ``database.py``).

Validation deliberately checks the binary "magic number" signature of the
file rather than trusting the client-supplied ``Content-Type`` header or
file extension, since both are trivially spoofable.
"""

from __future__ import annotations

import base64
import logging

from fastapi import UploadFile

from config import settings
from exceptions import FileTooLargeError, InvalidImageError

logger = logging.getLogger(__name__)

# Magic-byte signatures -> MIME type. Order matters only for readability.
_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"BM", "image/bmp"),
    (b"RIFF", "image/webp"),  # WEBP is RIFF + "WEBP" at offset 8, checked below
]


def _sniff_mime_type(data: bytes) -> str | None:
    """Return the MIME type implied by the file's binary signature, or None."""
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    for signature, mime in _SIGNATURES:
        if signature == b"RIFF":
            continue  # handled above
        if data.startswith(signature):
            return mime
    return None


class ValidatedImage:
    """A validated image ready to be sent to the OpenAI Responses API."""

    __slots__ = ("filename", "mime_type", "data", "size_bytes")

    def __init__(self, filename: str, mime_type: str, data: bytes) -> None:
        self.filename = filename
        self.mime_type = mime_type
        self.data = data
        self.size_bytes = len(data)

    @property
    def data_url(self) -> str:
        """The image encoded as a base64 data URL for the vision API."""
        encoded = base64.b64encode(self.data).decode("ascii")
        return f"data:{self.mime_type};base64,{encoded}"


async def validate_upload(file: UploadFile) -> ValidatedImage:
    """Read, size-check and content-sniff an uploaded file.

    Raises
    ------
    FileTooLargeError
        If the file exceeds ``settings.max_upload_size_mb``.
    InvalidImageError
        If the file is empty or is not a recognised image format.
    """
    data = await file.read()

    if not data:
        raise InvalidImageError("The uploaded file is empty.")

    if len(data) > settings.max_upload_size_bytes:
        raise FileTooLargeError(
            f"File exceeds the {settings.max_upload_size_mb:.1f} MB upload limit."
        )

    mime_type = _sniff_mime_type(data)
    if mime_type is None or mime_type not in settings.allowed_mime_types:
        raise InvalidImageError(
            "Unsupported or unrecognised image format. "
            "Supported formats: JPEG, PNG, WEBP, GIF, BMP."
        )

    filename = file.filename or "upload"
    logger.info("Validated upload '%s' (%s, %d bytes)", filename, mime_type, len(data))
    return ValidatedImage(filename=filename, mime_type=mime_type, data=data)
