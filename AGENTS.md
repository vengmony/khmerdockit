# AGENTS.md — Project context for AI coding agents

> This file is the primary context source for AI coding agents (Codex CLI,
> Claude Code, OpenCode, Cline, etc.) working on the **KhmerDocKit**
> repository. It follows the convention described at
> <https://developers.openai.com/codex/guides/agents-md>. If you are a
> human contributor, the same rules apply — read the relevant sections
> before opening a PR.

## Project summary

**KhmerDocKit** is an open-source, MIT-licensed toolkit for extracting
structured data from Khmer / English business documents (receipts,
invoices, quotations, bank transfer slips). It targets the Cambodia
POS / fintech / govtech stack. Monorepo with three packages:

* `packages/khmerdoc-core/` — Pydantic v2 library, OCR adapters, rule-based
  extractor, Cambodia validators, CLI, synthetic data generator, benchmark.
* `packages/khmerdoc-api/` — FastAPI server (`/v1/parse`, `/v1/ocr`,
  `/v1/schemas`, `/health`).
* `packages/khmerdoc-web/` — Next.js 14 + TypeScript + Tailwind demo.
* `packages/khmerdoc-demo/` — Gradio single-command demo (entry point
  for "users can easily test it").

Synthetic data only. The dataset generator in
`packages/khmerdoc-core/src/khmedoc/synthetic/generate.py` is the only
source of in-repo documents. **Never commit real receipts, real
merchant names, or any private data.**

## Quick commands

```bash
# install everything
make install
make install-web         # one-time, for the Next.js demo

# tests
make test                # full suite
make test-core           # khmerdoc-core only
make test-api            # khmerdoc-api only

# lint / format
make lint
make format

# run locally
make api                 # uvicorn on :8000
make web                 # Next.js on :3000
make demo-gradio         # Gradio on :7860 (single command, no API needed)

# data / benchmark
make synth               # regenerate datasets/synthetic
khmerdoc benchmark datasets/synthetic
```

## Code conventions

* **Python ≥ 3.11.** Use `from __future__ import annotations`. Prefer
  PEP 604 unions (`int | None`) in *runtime* annotations, but
  `Optional[int]` in Pydantic v2 model fields where the field name
  shadows an imported type (known Pydantic v2 limitation).
* **Pydantic v2** for all typed documents. Models live in
  `packages/khmerdoc-core/src/khmedoc/schemas.py`.
* **Ruff** for lint and format. 100-char line limit.
* **No hardcoded business logic.** Schemas / extractors / validators
  must stay generic.
* **Document the public surface.** Anything imported by another package
  belongs in `__all__`.
* **Never add a real OCR engine as a hard dependency.** OCR adapters
  live behind optional extras (`paddle`, `tesseract`, future
  `easyocr` / `doctr`).

## Where things live

| Concern | File / dir |
| --- | --- |
| Typed document models | `packages/khmerdoc-core/src/khmedoc/schemas.py` |
| OCR adapter interface | `packages/khmerdoc-core/src/khmedoc/ocr/base.py` |
| Rule-based extractor | `packages/khmerdoc-core/src/khmedoc/extractors/rules.py` |
| Cambodia validators | `packages/khmerdoc-core/src/khmedoc/validators/cambodia.py` |
| Synthetic data generator | `packages/khmerdoc-core/src/khmedoc/synthetic/generate.py` |
| CLI entry point | `packages/khmerdoc-core/src/khmedoc/cli.py` |
| FastAPI app | `packages/khmerdoc-api/src/khmerdoc_api/main.py` |
| API settings | `packages/khmerdoc-api/src/khmerdoc_api/settings.py` |
| Gradio demo | `packages/khmerdoc-demo/src/khmedoc_demo/app.py` |
| Public docs | `docs/` |
| Synthetic dataset | `datasets/synthetic/` |
| CI | `.github/workflows/ci.yml` |
| Issue templates | `.github/ISSUE_TEMPLATE/` |
| Project governance | `MAINTAINERS.md` |
| Code review policy | `.github/CODEOWNERS` |

## Common tasks

### Add a new Cambodia-specific validation rule

1. Add a function returning `list[Warning]` in
   `packages/khmerdoc-core/src/khmedoc/validators/cambodia.py`.
2. Wire it into `validate_extraction()`.
3. Add a unit test in `tests/test_validators.py`.
4. Document the rule in `docs/cambodia_validation_rules.md`.

### Add a new OCR adapter

1. Subclass `OCRAdapter` in
   `packages/khmerdoc-core/src/khmedoc/ocr/base.py`.
2. Register the factory in `_register_defaults()` (same file).
3. Add the import inside a `try / except ImportError` block in
   `khmerdoc/ocr/<your_backend>.py` so the package still imports
   without the optional dep installed.
4. Add a unit test in `tests/test_ocr.py` that uses the `mock` adapter
   to simulate the new engine.
5. Document the install step in `docs/ocr_adapters.md`.

### Add a new synthetic document template

1. Add (or extend) a generator in
   `packages/khmerdoc-core/src/khmedoc/synthetic/generate.py`.
2. Register it in the `GENERATORS` dict at the bottom of the file.
3. Add a test in `tests/test_synthetic.py` that checks the layout.
4. Run `khmerdoc benchmark datasets/synthetic` and inspect the scores.

### Add a new API endpoint

1. Add a router module under
   `packages/khmerdoc-api/src/khmedoc_api/routes/`.
2. Wire it into `routes/__init__.py` and `main.py`.
3. Add a test in `packages/khmerdoc-api/tests/test_api.py`.
4. Update `examples/curl_examples.md` with a curl invocation.

## Test expectations

* Run `make test` before opening a PR. All tests must pass.
* Add a test for any new behaviour. Tests live next to the code they
  exercise (`packages/<pkg>/tests/`).
* The synthetic benchmark is the public regression baseline. If you
  change the rule-based extractor in a way that improves (or
  intentionally changes) extraction behaviour, update
  `docs/RELEASE-v0.1.0.md` and `CHANGELOG.md`.

## "Don't" list

* **Don't** commit real user documents, real merchant names, real
  account numbers, or anything that looks private.
* **Don't** add an OCR / LLM SDK as a hard dependency. Optional extras
  only.
* **Don't** make the LLM extractor required. It must remain opt-in
  via `KHMERDOC_LLM_ENABLED=true`.
* **Don't** merge schema changes without a backwards-compatibility
  note in `CHANGELOG.md`. v0.1.0 is the first public release; the
  schemas are now part of the public contract.
* **Don't** raise on recoverable errors inside an extractor. Return
  a low-confidence result with a `Warning` instead.
* **Don't** invent metrics, stars, downloads, or users in the docs.

## Public contracts (do not break without a deprecation cycle)

* `khmerdoc.schemas.{Receipt, Invoice, Quotation, BankSlip, LineItem,
  ExtractionResult, OCRResult, Warning, DocumentType, Currency}` —
  serialised to JSON in the API response.
* `khmerdoc.ocr.OCRAdapter.extract_text(file_path) -> OCRResult`.
* `khmerdoc.extractors.Extractor.extract(ocr, document_type=...) ->
  ExtractionResult`.
* The `/v1/parse`, `/v1/ocr`, `/v1/schemas`, `/health` HTTP endpoints.
* The `khmerdoc parse|ocr|benchmark|list-schemas` CLI subcommands.

## Reference docs for the agent

* `README.md` — top-level pitch + quickstart.
* `docs/architecture.md` — package boundaries + extension points.
* `docs/schemas.md` — public JSON schemas.
* `docs/ocr_adapters.md` — OCR backend contracts.
* `docs/llm_extractors.md` — planned LLM extraction design.
* `docs/cambodia_validation_rules.md` — Cambodia-specific rules.
* `docs/benchmark.md` — how the public benchmark works.
* `CONTRIBUTING.md` — contributor workflow.
* `MAINTAINERS.md` — governance.
* `SECURITY.md` — private vulnerability reporting.
* `CODE_OF_CONDUCT.md` — community standards.
* `ROADMAP.md` — what is planned after v0.1.
