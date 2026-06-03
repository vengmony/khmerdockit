"""Extractor base class and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from ..schemas import DocumentType, ExtractionResult, OCRResult


class Extractor(ABC):
    """Convert :class:`OCRResult` into an :class:`ExtractionResult`."""

    name: str = "abstract"

    @abstractmethod
    def extract(
        self,
        ocr: OCRResult | str,
        document_type: DocumentType | str | None = None,
    ) -> ExtractionResult:
        """Run extraction.

        Parameters
        ----------
        ocr:
            Either an :class:`OCRResult` or the raw OCR text.
        document_type:
            Optional hint. If ``None`` or ``"auto"``, the extractor will try
            to infer the type from the text.
        """


class ExtractorRegistry:
    _factories: dict[str, Callable[[], Extractor]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], Extractor]) -> None:
        cls._factories[name] = factory

    @classmethod
    def create(cls, name: str) -> Extractor:
        if name not in cls._factories:
            raise KeyError(f"Unknown extractor '{name}'. Known: {sorted(cls._factories)}.")
        return cls._factories[name]()

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._factories)


def _register_defaults() -> None:
    from .rules import RuleBasedExtractor  # local import to avoid cycles

    ExtractorRegistry.register("rules", RuleBasedExtractor)


_register_defaults()
