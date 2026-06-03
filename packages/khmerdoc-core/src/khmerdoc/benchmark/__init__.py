"""Benchmark utilities: run an extractor over a labelled dataset and score it."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .scoring import BenchmarkReport, field_scores, score_extraction
from .runner import BenchmarkRunner

__all__ = [
    "BenchmarkReport",
    "BenchmarkRunner",
    "field_scores",
    "score_extraction",
]
