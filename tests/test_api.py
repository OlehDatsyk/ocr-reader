"""
test_api.py
============
End-to-end tests against the FastAPI app using ``TestClient``. The OpenAI
call itself is monkeypatched so the test suite never needs network access
or a real API key.
"""

from __future__ import annotations

import router_ocr
from schemas import OCRStructuredExtraction, OCRTextBlock


def _patch_extract(monkeypatch, text: str = "Hello from the test double."):
    async def fake_extract(self, image, language):
        return text

    monkeypatch.setattr(router_ocr.ocr_service, "extract", fake_extract.__get__(router_ocr.ocr_service))


def _patch_extract_structured(monkeypatch):
    async def fake_extract_structured(self, image, language):
        return OCRStructuredExtraction(
            detected_language="English",
            summary="A short test document.",
            blocks=[OCRTextBlock(type="paragraph", text="Hello from structured mode.", order=0)],
            full_text="Hello from structured mode.",
        )

    monkeypatch.setattr(
        router_ocr.ocr_service,
        "extract_structured",
        fake_extract_structured.__get__(router_ocr.ocr_service),
    )


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["openai_configured"] is True


def test_dashboard_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Extract text from an image" in response.text


def test_history_page_renders(client):
    response = client.get("/history")
    assert response.status_code == 200


def test_settings_page_renders(client):
    response = client.get("/settings")
    assert response.status_code == 200


def test_extract_plain_text(client, monkeypatch, tiny_png_bytes):
    _patch_extract(monkeypatch, text="Invoice #1234 — Total: $42.00")
    response = client.post(
        "/api/ocr/extract",
        files={"file": ("invoice.png", tiny_png_bytes, "image/png")},
        data={"language": "auto", "structured": "false"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Invoice #1234 — Total: $42.00"
    assert body["char_count"] == len(body["text"])
    assert body["id"] > 0


def test_extract_structured(client, monkeypatch, tiny_png_bytes):
    _patch_extract_structured(monkeypatch)
    response = client.post(
        "/api/ocr/extract",
        files={"file": ("doc.png", tiny_png_bytes, "image/png")},
        data={"language": "english", "structured": "true"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["structured"] is True
    assert len(body["blocks"]) == 1
    assert body["blocks"][0]["type"] == "paragraph"


def test_extract_rejects_invalid_file(client, tiny_png_bytes):
    response = client.post(
        "/api/ocr/extract",
        files={"file": ("not-an-image.txt", b"plain text content", "text/plain")},
        data={"language": "auto", "structured": "false"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "InvalidImageError"


def test_history_lifecycle(client, monkeypatch, tiny_png_bytes):
    _patch_extract(monkeypatch, text="Some extracted text for history.")
    create = client.post(
        "/api/ocr/extract",
        files={"file": ("note.png", tiny_png_bytes, "image/png")},
        data={"language": "auto", "structured": "false"},
    )
    record_id = create.json()["id"]

    listing = client.get("/api/history")
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    detail = client.get(f"/api/history/{record_id}")
    assert detail.status_code == 200
    assert detail.json()["text"] == "Some extracted text for history."

    download = client.get(f"/api/history/{record_id}/download?fmt=txt")
    assert download.status_code == 200
    assert download.text == "Some extracted text for history."

    delete = client.delete(f"/api/history/{record_id}")
    assert delete.status_code == 200

    missing = client.get(f"/api/history/{record_id}")
    assert missing.status_code == 404


def test_history_not_found(client):
    response = client.get("/api/history/999999")
    assert response.status_code == 404
    assert response.json()["error"] == "HistoryNotFoundError"
