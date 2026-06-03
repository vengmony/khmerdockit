# KhmerDocKit

> **Open-source AI toolkit for Cambodia-focused business document understanding.**

KhmerDocKit extracts structured data from Khmer and English business documents —
receipts, invoices, quotations, delivery notes, bank transfer slips, payment
proof screenshots, and supplier purchase documents. It is designed for
**Cambodian developers, SMEs, POS vendors, accountants, fintech teams, and
govtech builders**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status: v0.1.0 MVP](https://img.shields.io/badge/status-v0.1.0%20MVP-blue)](./CHANGELOG.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

---

## Why this exists

Cambodia's POS, retail, and fintech ecosystem runs on a paper / phone-photo
substrate — receipts, invoices, and bank slips in mixed Khmer / English, USD
and KHR, with local phone formats and reference numbers. Most off-the-shelf
document-AI tools are trained on US/EU data and quietly misread the
Cambodian parts.

KhmerDocKit is **open infrastructure** for that gap:

* **Reusable** — Python library, REST API, web demo, CLI, JSON schemas.
* **Local-first** — works offline with the mock OCR backend; the default
  rule-based extractor does not require an API key.
* **Honest** — no fake benchmarks, no fake users, no private data in the
  repo. Everything shipped is **synthetic**.
* **Generic enough** for other low-resource-language document-AI work
  (just add your own OCR/extractor adapters).

## Project status & maintainers

KhmerDocKit is **founder-led and community-driven**. The current
maintainers are listed in [`MAINTAINERS.md`](./MAINTAINERS.md). The
project is actively open for contributions — see
[`CONTRIBUTING.md`](./CONTRIBUTING.md) and the
[`good first issue`](https://github.com/khmerdoc/khmerdockit/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
list. If you maintain a Cambodia-focused POS, fintech, or govtech
product and want to shape the roadmap, please reach out via a GitHub
discussion.

## What you get in v0.1.0

| Surface              | Status |
| -------------------- | ------ |
| Python library       | ✅ `khmerdoc-core` (Pydantic v2) |
| FastAPI server       | ✅ `khmerdoc-api` (`/health`, `/v1/parse`, `/v1/ocr`, `/v1/schemas`) |
| Gradio demo (single command) | ✅ `khmerdoc-demo` (drop file → JSON in 5s) |
| Next.js web demo     | ✅ `khmerdoc-web` (upload, preview, JSON viewer) |
| CLI                  | ✅ `khmerdoc parse|ocr|benchmark|list-schemas` |
| OCR backends         | ✅ `mock` (default), `paddle` (optional), `tesseract` (optional) |
| Extractor backends   | ✅ `rules` (regex + heuristics). LLM adapter planned for v0.3. |
| Cambodia validators  | ✅ Phone, currency, date, line-item totals |
| Synthetic dataset    | ✅ 20 samples (5 receipts, 5 invoices, 5 quotations, 5 bank slips) |
| Docker               | ✅ `docker compose up --build` |
| CI                   | ✅ GitHub Actions: lint + test + Docker build |
| Docs                 | ✅ See `/docs` |
| **LLM extraction**   | ⏳ planned v0.3 |
| **Khmer docs**       | ⏳ planned v0.4 |

## Quickstart

### 1. Install (Python 3.11+)

```bash
git clone https://github.com/khmerdoc/khmerdockit
cd khmerdockit
make install           # installs khmerdoc-core and khmerdoc-api in editable mode
```

### 2. Try the CLI on a synthetic sample

```bash
khmerdoc parse datasets/synthetic/receipts/receipt-001/document.txt --type receipt
```

### 3. Run the API

```bash
make api               # uvicorn on http://localhost:8000
```

```bash
curl -X POST http://localhost:8000/v1/parse \
  -F "file=@datasets/synthetic/invoices/invoice-001/document.txt" \
  -F "document_type=invoice"
```

The OpenAPI / Swagger UI is at <http://localhost:8000/docs>.

### 4. Run the web demo

```bash
make install-web
make web               # Next.js on http://localhost:3000
```

The web demo expects the API at `http://localhost:8000`. To change that, set
`NEXT_PUBLIC_API_BASE_URL` before starting the dev server.

### 5. Or run everything in Docker

```bash
make docker            # docker compose up --build
```

## Example output

```json
{
  "document_type": "receipt",
  "merchant_name": "Example Mart",
  "date": "2026-06-02",
  "currency": "USD",
  "subtotal": 12.5,
  "discount": 0,
  "tax": 0,
  "total": 12.5,
  "phone_numbers": ["012345678"],
  "invoice_number": "INV-001",
  "line_items": [
    { "name": "Classic Clog", "quantity": 1, "unit_price": 12.5, "total": 12.5 }
  ],
  "confidence": 0.82,
  "raw_ocr_text": "...",
  "warnings": []
}
```

## Repository layout

```
khmer-dockit/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── ROADMAP.md
├── CHANGELOG.md
├── Makefile
├── docker-compose.yml
├── .env.example
├── packages/
│   ├── khmerdoc-core/      ← Python library
│   ├── khmerdoc-api/       ← FastAPI server
│   ├── khmerdoc-demo/      ← Gradio demo (single command, public URL via --share)
│   └── khmerdoc-web/       ← Next.js demo
├── datasets/synthetic/     ← 20 synthetic samples + labels
├── examples/               ← Python + curl usage
├── docs/                   ← Architecture, schemas, OCR, etc.
└── .github/                ← CI + issue / PR templates
```

## Architecture (one paragraph)

A document is uploaded to the API, which passes it to an **OCR adapter**
(`mock` by default, with optional `paddle` / `tesseract` backends). The OCR
output goes to an **extractor** (currently a regex + heuristics
`RuleBasedExtractor`; an OpenAI-compatible LLM adapter lands in v0.3). The
extractor fills a typed Pydantic model (`Receipt` / `Invoice` / `Quotation`
/ `BankSlip`) and a **Cambodia validator** layer adds structured `Warning`s
for things like unusual phone numbers or unrealistic dates. The result is
serialised to JSON for the API / web demo / CLI.

See [`docs/architecture.md`](./docs/architecture.md) for diagrams and
extension points.

## Cambodia validation rules (highlights)

* Phone numbers in `0XXXXXXXX`, `+855XXXXXXXX`, or `0XXX XXX XXX` form.
* Currency is normalised from `$`, `USD`, `៛`, `KHR`, and `RIEL`.
* Dates are parsed from `YYYY-MM-DD`, `DD/MM/YYYY`, and `02 Jun 2026` shapes.
* Line-item totals are checked against `quantity × unit_price`.
* Dates more than 10 years in the past / 1 year in the future are flagged.

See [`docs/cambodia_validation_rules.md`](./docs/cambodia_validation_rules.md).

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md). TL;DR: v0.2 = better Khmer dates + line
items, v0.3 = LLM extraction adapter, v0.4 = plugin system + Khmer docs,
v1.0 = stable schemas + production deployment.

## Contributing

We welcome PRs. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) and the
[`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) first. **Do not commit real
receipts or private data** — only synthetic samples go in `datasets/synthetic/`.

If you're new, start with a `good first issue` or a
[document template request](./.github/ISSUE_TEMPLATE/document_template_request.yml) — both are
self-contained and don't require touching the core extraction logic.

## License

[MIT](./LICENSE). © 2026 KhmerDocKit contributors.

## Acknowledgements

* The OCR integration design borrows ideas from
  [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR),
  [Tesseract](https://github.com/tesseract-ocr/tesseract), and the wider
  document-AI community.
* The synthetic generators use a small set of plausible but **entirely
  fictional** merchant and bank names; any resemblance to a real
  Cambodian business is coincidental.
