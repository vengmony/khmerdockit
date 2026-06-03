"""`khmerdoc` command-line entry point."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from .extractors import ExtractorRegistry
from .ocr import OcrAdapterRegistry
from .schemas import DocumentType
from .validators import validate_extraction

console = Console()


def _coerce_document_type(value: str | None) -> DocumentType:
    if not value or value == "auto":
        return DocumentType.UNKNOWN  # type: ignore[return-value]
    try:
        return DocumentType(value)
    except ValueError:
        raise click.BadParameter(f"Unknown document type '{value}'.")


def _resolve_ocr(backend: str):
    try:
        return OcrAdapterRegistry.create(backend)
    except KeyError as e:
        raise click.ClickException(str(e)) from e


def _resolve_extractor(name: str):
    try:
        return ExtractorRegistry.create(name)
    except KeyError as e:
        raise click.ClickException(str(e)) from e


@click.group()
@click.version_option(package_name="khmerdoc-core")
def main() -> None:
    """KhmerDocKit CLI."""


@main.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--type", "document_type", default="auto", show_default=True, help="Document type hint.")
@click.option("--ocr-backend", default="mock", show_default=True, help="OCR backend to use.")
@click.option(
    "--extractor",
    default="rules",
    show_default=True,
    help="Extractor backend to use (rules for the v0.1 MVP).",
)
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=Path), default=None)
def parse(
    file_path: Path,
    document_type: str,
    ocr_backend: str,
    extractor: str,
    output: Path | None,
) -> None:
    """Parse a single document file and print structured JSON."""
    ocr = _resolve_ocr(ocr_backend)
    text_result = ocr.extract_text(file_path)
    # If the adapter returned no text (e.g. the mock backend when no lines
    # were injected), fall back to reading the file as plain text — useful for
    # the synthetic ``.txt`` files.
    if not text_result.text and file_path.suffix.lower() == ".txt":
        text_result.text = file_path.read_text(encoding="utf-8")

    ext = _resolve_extractor(extractor)
    dt = _coerce_document_type(document_type)
    result = ext.extract(text_result, document_type=dt)
    validate_extraction(result)

    payload = result.to_jsonable()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    else:
        console.print(rendered)


@main.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--ocr-backend", default="mock", show_default=True)
def ocr(file_path: Path, ocr_backend: str) -> None:
    """Run OCR on a single file and print the raw text."""
    ocr = _resolve_ocr(ocr_backend)
    result = ocr.extract_text(file_path)
    if not result.text and file_path.suffix.lower() == ".txt":
        result.text = file_path.read_text(encoding="utf-8")
    console.print(result.text)


@main.command()
@click.argument("dataset_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--extractor", default="rules", show_default=True)
def benchmark(dataset_dir: Path, extractor: str) -> None:
    """Run the benchmark over a directory of synthetic documents."""
    from .benchmark import BenchmarkRunner

    runner = BenchmarkRunner(dataset_dir)
    report = runner.run()
    console.print(f"[bold]Benchmark[/bold] over {report['root']} — {report['n_samples']} samples")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Field")
    table.add_column("P", justify="right")
    table.add_column("R", justify="right")
    table.add_column("F1", justify="right")
    table.add_column("OK", justify="right")
    table.add_column("Miss", justify="right")
    table.add_column("Wrong", justify="right")
    for f, d in report["fields"].items():
        table.add_row(
            f,
            f"{d['precision']:.2f}",
            f"{d['recall']:.2f}",
            f"{d['f1']:.2f}",
            str(d["correct"]),
            str(d["missing"]),
            str(d["wrong"]),
        )
    console.print(table)


@main.command("list-schemas")
def list_schemas() -> None:
    """Print the public JSON schema for every public model."""
    from .schemas import BankSlip, ExtractionResult, Invoice, LineItem, Quotation, Receipt

    for name, model in {
        "Receipt": Receipt,
        "Invoice": Invoice,
        "Quotation": Quotation,
        "BankSlip": BankSlip,
        "LineItem": LineItem,
        "ExtractionResult": ExtractionResult,
    }.items():
        console.rule(name)
        console.print_json(json.dumps(model.model_json_schema(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
