# KhmerDocKit v0.1.0 — milestone summary

> Quick orientation for the first tag. **v0.1.0 is an early MVP.** Numbers
> will be soft; APIs may shift; please file issues for anything that hurts.

## What's in the box

* `packages/khmerdoc-core` — Pydantic v2 schemas, OCR adapter interface
  (`mock` / `paddle` / `tesseract`), rule-based extractor, Cambodia
  validators, CLI, synthetic generator, benchmark.
* `packages/khmerdoc-api` — FastAPI server with `/health`, `/v1/parse`,
  `/v1/ocr`, `/v1/schemas`. File-size + MIME allow-list enforced.
* `packages/khmerdoc-web` — Next.js 14 (TypeScript + Tailwind) demo with
  upload, preview, JSON viewer, and four built-in sample documents.
* `datasets/synthetic/` — 20 deterministic samples (5 receipts, 5
  invoices, 5 quotations, 5 bank slips) with expected JSON labels.
* `docs/` — quickstart, architecture, schemas, OCR adapters, LLM
  extractors, benchmark, Cambodia validation rules, Khmer landing
  page, and a draft Codex-for-OSS application.
* `examples/` — Python + curl usage.
* `.github/` — CI (lint + test + Docker build) and issue / PR templates.

## What works (verified locally)

* `make install && make test` — **48 pytest tests pass.**
* `khmerdoc parse datasets/synthetic/receipts/receipt-001/document.txt`
  returns the expected JSON (total 22.31, phone 0120433218, etc.).
* `khmerdoc benchmark datasets/synthetic` — core fields (date, total,
  currency, document_type, merchant_name, invoice_number, quotation_number,
  reference, amount) score **F1 = 1.00** on the v0.1 dataset.
* `POST /v1/parse` end-to-end smoke test returns 200 with the expected
  payload and zero warnings on the sample.
* `GET /v1/schemas` lists all six public models.

## What's known to be missing (v0.2 / v0.3 backlog)

* Bank-slip fields `bank_name`, `sender_name`, `receiver_account` are
  not yet extracted by the rule-based extractor.
* The benchmark's `line_items` score is artificially low because the
  list-comparison scorer uses a string-based norm; a v0.2 fix is
  tracked in `docs/suggested-github-issues.md`.
* The LLM extraction adapter is **not implemented**; see
  `docs/llm_extractors.md` for the v0.3 design.
* Khmer-language documentation is a placeholder (`docs/khmer.md`).

## Try it

```bash
make install
make test
make api               # then open http://localhost:8000/docs
# in another terminal
make install-web && make web   # then open http://localhost:3000
```

## License

MIT — see `LICENSE`.
