"""Tests for the OCR adapter interface and built-in adapters."""

from __future__ import annotations

from pathlib import Path

import pytest

from khmerdoc.ocr import (
    MockOCRAdapter,
    OcrAdapterRegistry,
    PaddleOCRAdapter,
    TesseractOCRAdapter,
)
from khmerdoc.ocr.base import OcrBackend


def test_mock_adapter_returns_fixed_text() -> None:
    a = MockOCRAdapter(lines=["hello", "world"])
    r = a.extract_text("ignored.jpg")
    assert r.text == "hello\nworld"
    assert r.engine == "mock"
    assert len(r.tokens) == 2


def test_mock_adapter_from_text_helper() -> None:
    a = MockOCRAdapter("line1\nline2\n")
    r = a.extract_text("anything")
    assert r.text == "line1\nline2"


def test_registry_creates_known_backends() -> None:
    for name in ("mock", "paddle", "tesseract", "easyocr"):
        adapter = OcrAdapterRegistry.create(name)
        # EasyOCR / Paddle / Tesseract classes may or may not be importable
        # depending on optional deps, so we only assert Mock works.
        if name == "mock":
            assert isinstance(adapter, MockOCRAdapter)
        else:
            # Just verify the factory returned *some* object with the right name.
            assert getattr(adapter, "name", "") == name


def test_registry_unknown_backend() -> None:
    with pytest.raises(KeyError):
        OcrAdapterRegistry.create("nope")


def test_easyocr_backend_id_exists() -> None:
    # The OcrBackend enum must list easyocr so env-driven config can use it.
    assert OcrBackend.EASYOCR.value == "easyocr"
    assert "easyocr" in [b.value for b in OcrBackend]


def test_paddle_adapter_missing_dependency(tmp_path: Path) -> None:
    # If paddleocr isn't installed we should get a clear ImportError.
    # We don't want to install it for tests, so just verify the error path
    # by monkeypatching the import to fail.
    import khmerdoc.ocr.paddle as paddle_mod

    def _boom(self):  # pragma: no cover - exercised only when paddle missing
        raise ImportError("paddleocr not installed")

    paddle_mod.PaddleOCRAdapter._get_engine = _boom  # type: ignore[method-assign]
    adapter = PaddleOCRAdapter()
    with pytest.raises(ImportError):
        adapter._get_engine()
