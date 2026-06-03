# Changelog

All notable changes to **KhmerDocKit** are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- LLM extraction adapter (OpenAI-compatible) (v0.3)
- Plugin / document-template system (v0.4)
- Khmer-language documentation (v0.4)
- Public benchmark leaderboard (v0.4)

## [0.1.0] - 2026-06-03

### Added
- Initial public release of **KhmerDocKit**.
- `khmerdoc-core` Python package:
  - Pydantic v2 schemas (`Receipt`, `Invoice`, `Quotation`, `BankSlip`, `LineItem`, `ExtractionResult`, `Warning`, `DocumentType`).
  - OCR adapter interface with `mock`, `paddle`, and `tesseract` adapters.
  - Rule-based local extractor (total, currency, phone, date, invoice number, merchant, line items).
  - Cambodia validators (phone formats, USD/KHR, date normalization).
  - CLI: `khmerdoc parse ...`, `khmerdoc ocr ...`, `khmerdoc benchmark ...`.
- `khmerdoc-api` FastAPI server:
  - `GET /health`
  - `POST /v1/parse` (multipart upload)
  - `POST /v1/ocr`
  - `GET /v1/schemas`
  - CORS for the local web demo, OpenAPI docs at `/docs`.
- `khmerdoc-demo` **Gradio** web UI (`khmerdoc-demo` command):
  - Single-command run, no API server, no Node.js.
  - File upload + paste-OCR-text + four built-in sample buttons.
  - Formatted markdown view + raw JSON view + warnings.
  - `--share` flag for a free 72-hour public URL.
- `khmerdoc-web` Next.js 14 demo (TypeScript + Tailwind):
  - Upload page with drag-and-drop.
  - Document preview.
  - Extracted JSON viewer.
  - Confidence and warnings display.
  - Sample documents.
- Synthetic dataset generator + 20 labelled samples (5 receipts, 5 invoices, 5 quotations, 5 bank slips).
- Docker / docker-compose setup.
- GitHub Actions CI (lint + test).
- Documentation: `README`, `quickstart`, `architecture`, `schemas`, `ocr_adapters`, `llm_extractors`, `benchmark`, `cambodia_validation_rules`, `khmer` (placeholder), `codex-for-oss-application`.
- Issue / PR templates, contributing guide, security policy, code of conduct, roadmap.
