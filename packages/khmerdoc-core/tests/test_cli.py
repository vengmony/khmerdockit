"""Tests for the CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from khmerdoc.cli import main


RECEIPT = """\
Example Mart
RECEIPT
No: INV-001
Date: 2026-06-02
Tel: 012345678
------------------------
Classic Clog        1 x 12.50   12.50
------------------------
TOTAL       $12.50
"""


def test_cli_parse_writes_json(tmp_path: Path) -> None:
    doc = tmp_path / "receipt.txt"
    doc.write_text(RECEIPT, encoding="utf-8")
    out = tmp_path / "result.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["parse", str(doc), "--type", "receipt", "--ocr-backend", "mock", "-o", str(out)],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["document_type"] == "receipt"
    assert payload["total"] == 12.5


def test_cli_ocr_prints_text(tmp_path: Path) -> None:
    doc = tmp_path / "receipt.txt"
    doc.write_text(RECEIPT, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["ocr", str(doc), "--ocr-backend", "mock"])
    assert result.exit_code == 0, result.output
    assert "Example Mart" in result.output


def test_cli_list_schemas() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list-schemas"])
    assert result.exit_code == 0, result.output
    assert "Receipt" in result.output
