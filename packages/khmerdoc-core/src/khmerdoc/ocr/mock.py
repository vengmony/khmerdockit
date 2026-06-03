"""A deterministic OCR adapter for tests and offline demos.

The mock adapter does not look at the file at all. It returns a configurable
list of lines, which lets tests build predictable extraction cases without
shipping real receipts or installing a heavyweight OCR engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..schemas import OCRResult, OCRToken


class MockOCRAdapter:
    """Returns a fixed text block, ignoring the input file."""

    name = "mock"

    def __init__(self, lines: Sequence[str] | str | None = None) -> None:
        if lines is None:
            lines = []
        if isinstance(lines, str):
            self._lines: list[str] = [ln for ln in lines.splitlines() if ln.strip()]
        else:
            self._lines = [str(ln) for ln in lines]

    def extract_text(self, file_path: str | Path) -> OCRResult:
        # We deliberately do not open the file: this adapter is deterministic.
        del file_path
        text = "\n".join(self._lines)
        tokens = [
            OCRToken(text=line, confidence=0.95) for line in self._lines if line.strip()
        ]
        return OCRResult(
            text=text,
            tokens=tokens,
            language="en",
            confidence=0.95,
            engine=self.name,
            raw={"source": "mock"},
        )


def mock_ocr_from_text(text: str) -> MockOCRAdapter:
    """Helper: build a :class:`MockOCRAdapter` from a raw text block."""
    return MockOCRAdapter(lines=text.splitlines())
