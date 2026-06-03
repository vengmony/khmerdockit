"""Run an extractor over a directory of synthetic documents and score it."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ..extractors import RuleBasedExtractor
from ..ocr import MockOCRAdapter
from .scoring import BenchmarkReport, score_extraction


class BenchmarkRunner:
    """Walk a directory of synthetic docs, run extraction, and report scores.

    Expected layout::

        datasets/synthetic/
            receipts/
                r-001.json     # expected labels
                r-001.txt      # OCR text
            invoices/...
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"Synthetic dataset not found: {self.root}")
        self.extractor = RuleBasedExtractor()
        self.ocr = MockOCRAdapter()

    def _load(self, doc_dir: Path) -> tuple[str, dict] | None:
        text_files = sorted(doc_dir.glob("*.txt"))
        if not text_files:
            return None
        text = text_files[0].read_text(encoding="utf-8")
        label_path = doc_dir / "expected.json"
        if not label_path.exists():
            return None
        return text, json.loads(label_path.read_text(encoding="utf-8"))

    def run(self) -> dict:
        """Return a dict with overall + per-field BenchmarkReports."""
        overall: dict[str, BenchmarkReport] = {}
        per_doc: list[dict] = []
        for doc_dir in sorted(p for p in self.root.iterdir() if p.is_dir()):
            for sample in sorted(p for p in doc_dir.iterdir() if p.is_dir()):
                loaded = self._load(sample)
                if loaded is None:
                    continue
                text, expected = loaded
                ocr_result = self.ocr.extract_text(sample)
                result = self.extractor.extract(ocr_result)
                # The mock adapter returns empty text by default — replace it
                # with the real text from the file.
                result.raw_ocr_text = text
                from khmerdoc.extractors.rules import RuleBasedExtractor as _R  # noqa: F401
                # Re-run the extractor with the loaded text to keep things simple.
                result = self.extractor.extract(text)
                per_field = score_extraction(expected, result)
                per_doc.append(
                    {
                        "sample": str(sample.relative_to(self.root)),
                        "document_type": result.document_type.value,
                        "confidence": result.confidence,
                        "warnings": [w.model_dump() for w in result.warnings],
                        "fields": {k: v.to_dict() for k, v in per_field.items()},
                    }
                )
                for k, rep in per_field.items():
                    if k not in overall:
                        overall[k] = BenchmarkReport()
                    overall[k].total += rep.total
                    overall[k].correct += rep.correct
                    overall[k].partial += rep.partial
                    overall[k].missing += rep.missing
                    overall[k].wrong += rep.wrong
        return {
            "root": str(self.root),
            "n_samples": len(per_doc),
            "per_doc": per_doc,
            "fields": {k: v.to_dict() for k, v in overall.items()},
        }
