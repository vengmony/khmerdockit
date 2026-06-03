"""API tests using FastAPI's TestClient.

These tests don't require any external services — they use the mock OCR
backend and exercise the HTTP surface end-to-end.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from khmerdoc_api.main import create_app

RECEIPT = """\
Example Mart
RECEIPT
No: INV-001
Date: 2026-06-02
Tel: 012345678
------------------------
Classic Clog        1 x 12.50   12.50
------------------------
TOTAL       $12.50
"""


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "khmerdoc-api"


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "khmerdoc-api"


def test_schemas_list(client: TestClient) -> None:
    r = client.get("/v1/schemas")
    assert r.status_code == 200
    body = r.json()
    names = {s["name"] for s in body["schemas"]}
    assert {"Receipt", "Invoice", "Quotation", "BankSlip", "LineItem", "ExtractionResult"} <= names


def test_schemas_single(client: TestClient) -> None:
    r = client.get("/v1/schemas/Receipt")
    assert r.status_code == 200
    assert r.json()["name"] == "Receipt"


def test_schemas_404(client: TestClient) -> None:
    r = client.get("/v1/schemas/NotAThing")
    assert r.status_code == 404


def test_parse_text_file_as_receipt(client: TestClient) -> None:
    files = {"file": ("receipt.txt", io.BytesIO(RECEIPT.encode("utf-8")), "text/plain")}
    data = {"document_type": "receipt"}
    r = client.post("/v1/parse", files=files, data=data)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["document_type"] == "receipt"
    assert body["total"] == 12.5
    assert "012345678" in body["phone_numbers"]


def test_parse_with_auto_type(client: TestClient) -> None:
    files = {"file": ("invoice.txt", io.BytesIO(b"INVOICE\nTOTAL $10.00\n"), "text/plain")}
    r = client.post("/v1/parse", files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    # Auto-detection should classify as invoice (or at least produce something sane).
    assert body["document_type"] in {"invoice", "receipt"}


def test_parse_invalid_type(client: TestClient) -> None:
    files = {"file": ("x.txt", io.BytesIO(b"x"), "text/plain")}
    data = {"document_type": "menu"}
    r = client.post("/v1/parse", files=files, data=data)
    assert r.status_code == 400


def test_ocr_endpoint(client: TestClient) -> None:
    files = {"file": ("r.txt", io.BytesIO(RECEIPT.encode("utf-8")), "text/plain")}
    r = client.post("/v1/ocr", files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "Example Mart" in body["text"]
    assert body["engine"] in {"mock", "passthrough", "paddle", "tesseract"}


def test_parse_rejects_unsupported_mime(client: TestClient) -> None:
    files = {"file": ("x.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")}
    r = client.post("/v1/parse", files=files)
    assert r.status_code == 400
    assert "Unsupported content type" in r.text or "Unsupported" in r.text


def test_openapi_docs_available(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()
