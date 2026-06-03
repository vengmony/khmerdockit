"""Tests for the Gradio demo app — focused on the helper logic, not the UI."""

from __future__ import annotations

from pathlib import Path

from khmerdoc_demo.app import SAMPLES, _read_uploaded, run_extraction


def test_samples_have_text_and_type() -> None:
    assert len(SAMPLES) >= 4
    for name, info in SAMPLES.items():
        assert "text" in info and info["text"].strip(), f"empty sample: {name}"
        assert info["document_type"] in {"receipt", "invoice", "quotation", "bank_slip"}


def test_run_extraction_returns_payload() -> None:
    text = SAMPLES["Receipt — English, USD"]["text"]
    payload, md, raw, err = run_extraction(text, "auto")
    assert payload["document_type"] == "receipt"
    assert payload["total"] == 18.5
    assert "012345678" in payload["phone_numbers"]
    assert err == ""
    assert "Document type" in md
    assert payload == __import__("json").loads(raw)


def test_run_extraction_unknown_type() -> None:
    _, md, _, _ = run_extraction("hello", "menu")
    assert "Unknown document type" in md


def test_run_extraction_empty_input() -> None:
    _, md, _, err = run_extraction("", "auto")
    assert "_No text to extract._" in md
    assert err != ""


def test_read_uploaded_txt(tmp_path: Path) -> None:
    p = tmp_path / "demo.txt"
    p.write_text("hello\nworld", encoding="utf-8")
    assert _read_uploaded(p) == "hello\nworld"


def test_read_uploaded_missing_path() -> None:
    assert _read_uploaded("/nonexistent.txt") == ""


def test_read_uploaded_binary(tmp_path: Path) -> None:
    p = tmp_path / "pic.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n")
    out = _read_uploaded(p)
    assert "binary file" in out
    assert "OCR for" in out
