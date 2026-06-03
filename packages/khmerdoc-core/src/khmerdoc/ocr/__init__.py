"""OCR adapter interface and built-in implementations.

Adapters follow a small, explicit contract so they can be swapped in tests
or production without changing downstream code:

    ocr = OcrAdapterRegistry.create("mock")
    result = ocr.extract_text("path/to/receipt.jpg")
    assert isinstance(result, OCRResult)
"""

from __future__ import annotations

from .base import OCRAdapter, OcrAdapterRegistry, OcrBackend
from .easyocr import EasyOCRAdapter
from .mock import MockOCRAdapter
from .paddle import PaddleOCRAdapter
from .tesseract import TesseractOCRAdapter

__all__ = [
    "OCRAdapter",
    "EasyOCRAdapter",
    "OcrAdapterRegistry",
    "OcrBackend",
    "MockOCRAdapter",
    "PaddleOCRAdapter",
    "TesseractOCRAdapter",
]
