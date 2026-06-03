"""Gradio demo app for KhmerDocKit.

Run with:

    pip install -e packages/khmerdoc-demo
    khmerdoc-demo                # opens http://localhost:7860

Or, with a free temporary public URL (great for community testing):

    khmerdoc-demo --share

The app talks directly to the khmerdoc-core library (no API server needed).
It supports:

* File upload (image / PDF / plain text).
* Four built-in synthetic samples that work offline.
* Auto-detect or pinned document type.
* Formatted result view + raw JSON + warnings.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import gradio as gr

from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.ocr import MockOCRAdapter
from khmerdoc.schemas import DocumentType
from khmerdoc.synthetic import generate
from khmerdoc.validators import validate_extraction

__version__ = "0.1.0"

# ---- Sample data ----------------------------------------------------------

# Inline synthetic samples — small, deterministic, work offline.
# Mirrors the four samples embedded in the Next.js web demo.
SAMPLES: dict[str, dict[str, str]] = {
    "Receipt — English, USD": {
        "document_type": "receipt",
        "text": (
            "Example Mart\n"
            "RECEIPT\n"
            "No: INV-001\n"
            "Date: 2026-06-02\n"
            "Tel: 012345678\n"
            "------------------------\n"
            "Classic Clog        1 x 12.50   12.50\n"
            "USB-C Cable 1m      2 x  3.00    6.00\n"
            "------------------------\n"
            "SUBTOTAL    $18.50\n"
            "TOTAL       $18.50\n"
            "Thank you!\n"
        ),
    },
    "Invoice — English, USD": {
        "document_type": "invoice",
        "text": (
            "Mekong Minimart\n"
            "INVOICE\n"
            "Invoice No: INV-123\n"
            "Date: 02/06/2026\n"
            "Due Date: 16/06/2026\n"
            "Bill To: Sokha Construction\n"
            "Tel: +85512345678\n"
            "--------------------------------\n"
            "Rice 5kg            2 x 25.00  =  50.00\n"
            "Soap Bar            5 x  1.50  =   7.50\n"
            "--------------------------------\n"
            "SUBTOTAL    $57.50\n"
            "TOTAL       $57.50\n"
        ),
    },
    "Quotation — KHR": {
        "document_type": "quotation",
        "text": (
            "Riverside Restaurant\n"
            "QUOTATION\n"
            "Quote No: QUOT-007\n"
            "Date: 2026-06-01\n"
            "Valid Until: 2026-06-15\n"
            "Attn: Mey Mom Cosmetics\n"
            "Tel: 093 222 333\n"
            "--------------------------------\n"
            "Set Lunch A          20 x 12,000  =  240,000 ៛\n"
            "Set Lunch B          10 x 18,000  =  180,000 ៛\n"
            "--------------------------------\n"
            "SUBTOTAL    420,000 ៛\n"
            "TOTAL       420,000 ៛\n"
        ),
    },
    "Bank slip — USD transfer": {
        "document_type": "bank_slip",
        "text": (
            "ACLEDA Bank\n"
            "BANK TRANSFER CONFIRMATION\n"
            "Reference: TRF123456\n"
            "Date: 2026-05-30\n"
            "From: Sokha Construction  Acc: 12345678\n"
            "To:   Mekong Minimart     Acc: 87654321\n"
            "Amount: $250.00\n"
            "Status: SUCCESS\n"
        ),
    },
}

# ---- Core logic -----------------------------------------------------------


def _extractor() -> RuleBasedExtractor:
    return RuleBasedExtractor()


def _read_uploaded(file_path: str | Path | None) -> str:
    """Read an uploaded file and return its text.

    Gradio passes a path-like object. For images and PDFs, the mock OCR
    backend is used (so it returns nothing); we fall back to reading the
    file directly, which works for plain text uploads.
    """
    if file_path is None:
        return ""
    p = Path(file_path)
    if not p.exists():
        return ""
    suffix = p.suffix.lower()
    if suffix in {".txt", ".csv", ".json"}:
        return p.read_text(encoding="utf-8", errors="replace")
    # For images / PDFs the user would need a real OCR backend. We
    # surface a friendly message in the UI.
    return (
        f"[Uploaded binary file: {p.name} ({p.stat().st_size} bytes). "
        f"OCR for {suffix or 'this format'} requires the paddle / tesseract "
        f"backend. Install one with `pip install khmerdoc-core[paddle]` or "
        f"`[tesseract]`, then restart with KHMERDOC_OCR_BACKEND set.]"
    )


def run_extraction(
    text: str,
    document_type: str,
) -> tuple[dict[str, Any], str, str, str]:
    """Run extraction on the given text. Returns (json_dict, formatted_md, raw_json, error)."""
    if not text or not text.strip():
        return (
            {},
            "_No text to extract._",
            "{}",
            "Paste some text, upload a `.txt`, or click a sample button.",
        )
    try:
        dt = DocumentType(document_type) if document_type != "auto" else DocumentType.UNKNOWN  # type: ignore[arg-type]
    except ValueError:
        return ({}, f"_Unknown document type: {document_type}_", "{}", "")

    extractor = _extractor()
    ocr = MockOCRAdapter(lines=text.splitlines())
    ocr_result = ocr.extract_text("ignored-in-mock")
    # If the mock adapter produced no text, fall back to the raw text we
    # were given — this lets the demo work when the user supplies plain
    # text without configuring a real OCR backend.
    if not ocr_result.text:
        ocr_result.text = text
    result = extractor.extract(ocr_result, document_type=dt)
    validate_extraction(result)
    payload = result.to_jsonable()

    # Pretty markdown view
    md_lines = [
        f"**Document type:** `{payload.get('document_type', 'unknown')}`",
        f"**Engine:** `{payload.get('engine', 'rules')}`  |  "
        f"**Confidence:** `{int((payload.get('confidence', 0) or 0) * 100)}%`",
    ]
    warnings = payload.get("warnings") or []
    if warnings:
        md_lines.append("**Warnings:**")
        for w in warnings:
            md_lines.append(f"- `{w.get('code', '')}` — {w.get('message', '')}")
    else:
        md_lines.append("**Warnings:** _none_")

    # Skip the fields we already display
    skip = {"document_type", "engine", "confidence", "warnings", "raw_ocr_text"}
    fields = {k: v for k, v in payload.items() if k not in skip and v not in (None, [], "")}
    if fields:
        md_lines.append("\n**Extracted fields:**\n")
        for k, v in fields.items():
            md_lines.append(f"- **{k}**: `{json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}`")

    if payload.get("line_items"):
        md_lines.append("\n**Line items:**\n")
        md_lines.append("| name | quantity | unit_price | total |")
        md_lines.append("| --- | ---: | ---: | ---: |")
        for it in payload["line_items"]:
            md_lines.append(
                f"| {it.get('name', '')} | {it.get('quantity', '')} | "
                f"{it.get('unit_price', '')} | {it.get('total', '')} |"
            )

    return (payload, "\n".join(md_lines), json.dumps(payload, indent=2, ensure_ascii=False), "")


# ---- Gradio UI -------------------------------------------------------------


def _build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="KhmerDocKit — Cambodia Document AI",
    ) as demo:
        gr.Markdown(
            """
            # KhmerDocKit — Cambodia Document AI

            Open-source AI toolkit for extracting structured data from
            Khmer / English business documents. **v0.1.0 MVP.**

            - **Upload** a `.txt` file, or
            - **Paste** OCR text in the box, or
            - **Click a sample** below to try a synthetic document.

            The app runs entirely in this process — no API server, no
            network calls. Tip: set `--share` (or `share=True` in
            `launch()`) to get a temporary public URL.
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                file_input = gr.File(
                    label="Upload a document (text only in mock mode)",
                    file_types=[".txt", ".csv", ".json"],
                    type="filepath",
                )
                text_input = gr.Textbox(
                    label="…or paste OCR text here",
                    placeholder=(
                        "Example Mart\nRECEIPT\nNo: INV-001\nDate: 2026-06-02\n"
                        "Tel: 012345678\nTOTAL       $12.50"
                    ),
                    lines=12,
                )
                with gr.Row():
                    doc_type = gr.Dropdown(
                        choices=["auto", "receipt", "invoice", "quotation", "bank_slip"],
                        value="auto",
                        label="Document type",
                        scale=2,
                    )
                    run_btn = gr.Button("Extract", variant="primary", scale=1)

            with gr.Column(scale=2):
                gr.Markdown("### Sample documents\nClick to load a synthetic example.")
                for name, info in SAMPLES.items():
                    btn = gr.Button(name, size="sm")
                    btn.click(
                        fn=lambda txt=info["text"], dt=info["document_type"]: (txt, dt),
                        inputs=None,
                        outputs=[text_input, doc_type],
                    )

        gr.Markdown("---")
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Result")
                formatted = gr.Markdown(value="_Click **Extract** to see results._")
            with gr.Column():
                gr.Markdown("### Raw JSON")
                raw_json = gr.Code(language="json", label="")

        error_box = gr.Markdown(value="")

        # Wire up the run button
        def _on_run(file_path: str | None, text: str, dt: str) -> tuple[str, str, str]:
            effective = text or ""
            if file_path:
                effective = _read_uploaded(file_path) or effective
            payload, md, raw, err = run_extraction(effective, dt)
            return md, raw, err

        run_btn.click(
            fn=_on_run,
            inputs=[file_input, text_input, doc_type],
            outputs=[formatted, raw_json, error_box],
        )

        gr.Markdown(
            """
            ---
            **Heads up:** v0.1.0 ships with the **mock** OCR backend, so
            image and PDF uploads will show a placeholder message. To run
            OCR on real images, install a real backend:
            ```
            pip install -e packages/khmerdoc-core[paddle]
            KHMERDOC_OCR_BACKEND=paddle khmerdoc-demo
            ```
            Or:
            ```
            pip install -e packages/khmerdoc-core[tesseract]
            KHMERDOC_OCR_BACKEND=tesseract khmerdoc-demo
            ```
            """
        )

    return demo


# ---- Entry point ----------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="khmerdoc-demo",
        description="Run the KhmerDocKit Gradio demo (no API server required).",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind to (default: 7860).")
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a temporary public Gradio URL (valid 72h).",
    )
    args = parser.parse_args(argv)

    print(
        f"[khmerdoc-demo] v{__version__} — starting Gradio UI on "
        f"http://{args.host}:{args.port}",
        file=sys.stderr,
    )

    demo = _build_ui()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        theme=gr.themes.Soft(primary_hue="indigo"),
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
