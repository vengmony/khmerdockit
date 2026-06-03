"""Extraction engines: turn raw OCR text into typed documents.

Currently ships with a :class:`RuleBasedExtractor` and a registry. An LLM
extractor will plug in here in v0.3.
"""

from __future__ import annotations

from .base import Extractor, ExtractorRegistry
from .rules import RuleBasedExtractor

__all__ = [
    "Extractor",
    "ExtractorRegistry",
    "RuleBasedExtractor",
]
