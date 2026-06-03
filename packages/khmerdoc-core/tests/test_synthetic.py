"""Test for the synthetic dataset generator + benchmark runner."""

from __future__ import annotations

from pathlib import Path

from khmerdoc.benchmark import BenchmarkRunner
from khmerdoc.synthetic import generate


def test_synthetic_generator(tmp_path: Path) -> None:
    samples = generate(tmp_path, seed=1, per_type=3)
    # 3 samples * 4 kinds = 12
    assert len(samples) == 12
    for kind in ("receipts", "invoices", "quotations", "bank_slips"):
        assert (tmp_path / kind).exists()
        # at least one sample
        sample_dirs = list((tmp_path / kind).iterdir())
        assert sample_dirs, f"no samples generated for {kind}"
        first = sample_dirs[0]
        assert (first / "document.txt").exists()
        assert (first / "expected.json").exists()


def test_benchmark_runner_runs(tmp_path: Path) -> None:
    generate(tmp_path, seed=2, per_type=2)
    runner = BenchmarkRunner(tmp_path)
    report = runner.run()
    assert report["n_samples"] == 8  # 4 kinds × 2 each
    assert "fields" in report
    assert "merchant_name" in report["fields"]
    # All four kinds should be present somewhere in the per-doc list.
    types = {d["document_type"] for d in report["per_doc"]}
    assert {"receipt", "invoice", "quotation", "bank_slip"} <= types
