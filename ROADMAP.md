# KhmerDocKit — Roadmap

This roadmap is **public, transparent, and open to contribution**. Items may shift in priority based on community feedback. If you want to pick up a milestone item, open an issue or a draft PR.

Status legend: `[done]` `[in-progress]` `[planned]`

## v0.1.0 — MVP `[done]`

- `khmerdoc-core` Python package (Pydantic v2, OCR adapter, rule-based extractor, Cambodia validators, CLI)
- `khmerdoc-api` FastAPI server (`/health`, `/v1/parse`, `/v1/ocr`, `/v1/schemas`)
- `khmerdoc-web` Next.js 14 demo (upload, preview, JSON viewer, sample docs)
- 20 synthetic sample documents with expected JSON labels
- Docker / docker-compose, GitHub Actions CI
- Public docs and contributor guide

## v0.2 — Better extraction `[planned]`

- Stronger Khmer-script date parsing (Buddhist Era, ថ្ងៃទី…)
- Better line-item extraction (multi-line items, qty × unit price reconciliation)
- PDF text + image support (text layer first, OCR fallback)
- More synthetic templates (handwritten-style, low-light)
- Benchmark scoring (field-level precision/recall, JSON Diff)

## v0.3 — LLM-assisted extraction `[planned]`

- OpenAI-compatible LLM extraction adapter (optional, off by default)
- Confidence scoring that blends rules + LLM agreement
- Human-correction UI in the web demo (edit + re-export)
- Pluggable prompt templates per document type

## v0.4 — Ecosystem `[planned]`

- Plugin / template registry for community document templates
- Khmer-language documentation (README.kh.md, docs/khmer.md)
- Public benchmark leaderboard (no real user docs, synthetic only)
- CI workflow to evaluate PRs against the benchmark

## v1.0 — Stable `[planned]`

- Stable schemas (semver-locked)
- Stable API (v1 contract, deprecation policy)
- Production Docker images (signed, multi-arch)
- Eval suite with reproducible numbers
- Contributor ecosystem: regular releases, triage rotation, governance

---

## How to influence this roadmap

- File an issue with the `enhancement` or `document-template-request` template.
- Comment on existing issues.
- Open a PR — even small improvements matter.

This project is **early-stage**. Numbers and timelines will be updated as we go.
