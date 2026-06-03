# Quickstart

This guide gets you from a clean checkout to a running demo in under five
minutes.

## 0. Prerequisites

* **Python 3.11+** (3.12 recommended). Verify with `python --version`.
* **Node.js 20+** (only for the web demo). Verify with `node --version`.
* **Docker** (only for the `make docker` path).

## 1. Clone & install

```bash
git clone https://github.com/khmerdoc/khmerdockit
cd khmerdockit
make install            # installs khmerdoc-core + khmerdoc-api
```

## 2. Try the CLI

The repo ships with 20 synthetic documents under `datasets/synthetic/`.

```bash
khmerdoc parse datasets/synthetic/receipts/receipt-001/document.txt --type receipt
khmerdoc ocr    datasets/synthetic/invoices/invoice-001/document.txt
khmerdoc benchmark datasets/synthetic
```

Expected: the parse command prints a JSON object with `document_type`,
`merchant_name`, `total`, `line_items`, etc.

## 3. Start the API

```bash
make api
```

* API root: <http://localhost:8000/>
* Health:   <http://localhost:8000/health>
* Docs:     <http://localhost:8000/docs>

In another terminal:

```bash
curl -s http://localhost:8000/health | jq
curl -s -X POST http://localhost:8000/v1/parse \
  -F "file=@datasets/synthetic/receipts/receipt-001/document.txt" \
  -F "document_type=receipt" | jq
```

## 4. Start the web demo

```bash
make install-web
make web
```

Open <http://localhost:3000>.

The demo lets you:

* Drop a file (image, PDF, or text).
* Click any of the four built-in sample documents.
* See the extracted JSON, warnings, confidence, and a preview.

## 5. (Optional) Run via Docker

```bash
make docker
```

This starts the API on `:8000` and the web demo on `:3000`, with a shared
volume for the synthetic dataset.

## 6. Switching OCR backends

By default the API uses the **mock** OCR backend, which returns nothing (so
uploads must be `.txt`). To use a real OCR engine:

```bash
# Tesseract (requires the system binary + pip extra)
pip install -e "packages/khmerdoc-core[tesseract]"
KHMERDOC_OCR_BACKEND=tesseract KHMERDOC_OCR_LANG=eng+khm make api

# PaddleOCR (heavier, Khmer-capable)
pip install -e "packages/khmerdoc-core[paddle]"
KHMERDOC_OCR_BACKEND=paddle KHMERDOC_OCR_LANG=km make api
```

See [`docs/ocr_adapters.md`](./ocr_adapters.md) for details and how to add
your own backend.

## 7. Where to go next

* `docs/architecture.md` — overall design.
* `docs/schemas.md` — the public JSON schemas.
* `docs/cambodia_validation_rules.md` — the validator reference.
* `ROADMAP.md` — what's planned after v0.1.
* `CONTRIBUTING.md` — how to send a PR.
