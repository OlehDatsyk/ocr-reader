"""
test_ocr_service.py
=====================
Unit tests for ``image_service`` (validation) and ``ocr_service`` (prompt
construction / configuration errors). Real network calls to OpenAI are never
made in these tests.
"""

from __future__ import annotations

import asyncio
import io

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from config import settings
from exceptions import FileTooLargeError, InvalidImageError, OpenAIConfigurationError
from image_service import ValidatedImage, validate_upload
from ocr_service import OCRService, _build_input
from schemas import OCRLanguage


def _make_upload_file(data: bytes, filename: str = "scan.png") -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(data), headers=Headers({}))


def test_validate_upload_accepts_valid_png(tiny_png_bytes):
    upload = _make_upload_file(tiny_png_bytes)
    image = asyncio.run(validate_upload(upload))
    assert isinstance(image, ValidatedImage)
    assert image.mime_type == "image/png"
    assert image.size_bytes == len(tiny_png_bytes)


def test_validate_upload_rejects_empty_file():
    upload = _make_upload_file(b"")
    with pytest.raises(InvalidImageError):
        asyncio.run(validate_upload(upload))


def test_validate_upload_rejects_non_image_bytes():
    upload = _make_upload_file(b"this is definitely not an image")
    with pytest.raises(InvalidImageError):
        asyncio.run(validate_upload(upload))


def test_validate_upload_rejects_oversized_file(tiny_png_bytes, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_size_mb", 0.0000001)
    upload = _make_upload_file(tiny_png_bytes)
    with pytest.raises(FileTooLargeError):
        asyncio.run(validate_upload(upload))


def test_data_url_is_well_formed(tiny_png_bytes):
    image = ValidatedImage(filename="scan.png", mime_type="image/png", data=tiny_png_bytes)
    assert image.data_url.startswith("data:image/png;base64,")


def test_build_input_includes_language_hint(tiny_png_bytes):
    image = ValidatedImage(filename="scan.png", mime_type="image/png", data=tiny_png_bytes)
    payload = _build_input(image, OCRLanguage.FRENCH)
    prompt_text = payload[0]["content"][0]["text"]
    assert "French" in prompt_text
    assert payload[0]["content"][1]["type"] == "input_image"


def test_build_input_auto_language_mentions_detection(tiny_png_bytes):
    image = ValidatedImage(filename="scan.png", mime_type="image/png", data=tiny_png_bytes)
    payload = _build_input(image, OCRLanguage.AUTO)
    assert "automatically" in payload[0]["content"][0]["text"]


def test_extract_raises_when_api_key_missing(tiny_png_bytes, monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "")
    service = OCRService()
    image = ValidatedImage(filename="scan.png", mime_type="image/png", data=tiny_png_bytes)
    with pytest.raises(OpenAIConfigurationError):
        asyncio.run(service.extract(image, OCRLanguage.AUTO))
