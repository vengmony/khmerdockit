"""Field-level precision/recall scoring for extraction results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ..schemas import ExtractionResult


@dataclass
class BenchmarkReport:
    """A per-field report produced by :func:`score_extraction`."""

    total: int = 0
    correct: int = 0
    partial: int = 0
    missing: int = 0
    wrong: int = 0

    @property
    def precision(self) -> float:
        if self.correct + self.partial + self.wrong == 0:
            return 0.0
        return (self.correct + 0.5 * self.partial) / (self.correct + self.partial + self.wrong)

    @property
    def recall(self) -> float:
        if self.correct + self.partial + self.missing == 0:
            return 0.0
        return (self.correct + 0.5 * self.partial) / (self.correct + self.partial + self.missing)

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)

    def to_dict(self) -> dict[str, float | int]:
        return {
            "total": self.total,
            "correct": self.correct,
            "partial": self.partial,
            "missing": self.missing,
            "wrong": self.wrong,
            "precision": round(self.precision, 3),
            "recall": round(self.recall, 3),
            "f1": round(self.f1, 3),
        }


def _norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, list):
        return ",".join(sorted(_norm(v) for v in value))
    return str(value).strip().lower()


def _compare(expected: Any, got: Any) -> str:
    if expected is None or expected == "" or expected == []:
        if got is None or got == "" or got == []:
            return "missing"  # nothing expected, nothing got — counted as missing
        return "wrong"  # expected empty, got something
    if got is None or got == "" or got == []:
        return "missing"
    if _norm(expected) == _norm(got):
        return "correct"
    return "wrong"


def field_scores(
    expected: dict[str, Any],
    got: dict[str, Any],
    *,
    fields: Iterable[str] | None = None,
) -> dict[str, BenchmarkReport]:
    """Score a single extraction against the expected labels."""
    fields = list(fields) if fields is not None else sorted(set(expected) | set(got))
    reports: dict[str, BenchmarkReport] = {}
    for f in fields:
        r = BenchmarkReport(total=1)
        outcome = _compare(expected.get(f), got.get(f))
        setattr(r, outcome, 1)
        reports[f] = r
    return reports


def score_extraction(
    expected: ExtractionResult | dict[str, Any],
    got: ExtractionResult,
) -> dict[str, BenchmarkReport]:
    """Score a single :class:`ExtractionResult` against the expected JSON."""
    if isinstance(expected, ExtractionResult):
        exp_dict = expected.to_jsonable()
    else:
        exp_dict = expected
    got_dict = got.to_jsonable()
    return field_scores(exp_dict, got_dict)


__all__ = ["BenchmarkReport", "field_scores", "score_extraction"]
