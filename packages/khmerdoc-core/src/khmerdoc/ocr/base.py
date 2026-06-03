"""OCR adapter base class and a tiny registry.

Adapters convert a file on disk (image or PDF) into an :class:`OCRResult`.
The default registry knows about three backends: ``mock``, ``paddle``, and
``tesseract``. New backends can be added by calling
:func:`OcrAdapterRegistry.register` with a string key and a factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Callable

from ..schemas import OCRResult


class OcrBackend(str, Enum):
    """Known OCR backend identifiers."""

    MOCK = "mock"
    PADDLE = "paddle"
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"


class OCRAdapter(ABC):
    """Abstract base for OCR adapters."""

    #: Short identifier — matches a key in :class:`OcrAdapterRegistry`.
    name: str = "abstract"

    @abstractmethod
    def extract_text(self, file_path: str | Path) -> OCRResult:
        """Run OCR on ``file_path`` and return an :class:`OCRResult`.

        Implementations must not raise on recoverable errors — they should
        return a low-confidence :class:`OCRResult` with an explanatory
        warning. Fatal errors (missing file, unsupported type) should raise.
        """

    # Optional hooks for adapters that need configuration.
    def configure(self, **kwargs: object) -> None:  # pragma: no cover - default no-op
        return None


class OcrAdapterRegistry:
    """In-process registry of OCR adapter factories.

    Usage::

        OcrAdapterRegistry.register("mock", lambda: MockOCRAdapter())
        adapter = OcrAdapterRegistry.create("mock")
    """

    _factories: dict[str, Callable[[], OCRAdapter]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], OCRAdapter]) -> None:
        cls._factories[name] = factory

    @classmethod
    def create(cls, name: str | OcrBackend) -> OCRAdapter:
        key = name.value if isinstance(name, OcrBackend) else str(name)
        if key not in cls._factories:
            raise KeyError(
                f"Unknown OCR backend '{key}'. Known: {sorted(cls._factories)}. "
                "Did you forget to install the optional extra (e.g. pip install khmerdoc-core[paddle])?"
            )
        return cls._factories[key]()

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._factories)


# Built-in adapters are registered lazily to keep ``import khmerdoc.ocr`` cheap.
def _register_defaults() -> None:
    from .easyocr import EasyOCRAdapter
    from .mock import MockOCRAdapter
    from .paddle import PaddleOCRAdapter
    from .tesseract import TesseractOCRAdapter

    OcrAdapterRegistry.register(OcrBackend.MOCK.value, MockOCRAdapter)
    OcrAdapterRegistry.register(OcrBackend.PADDLE.value, PaddleOCRAdapter)
    OcrAdapterRegistry.register(OcrBackend.TESSERACT.value, TesseractOCRAdapter)
    OcrAdapterRegistry.register(OcrBackend.EASYOCR.value, EasyOCRAdapter)


_register_defaults()
