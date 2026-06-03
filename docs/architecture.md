# Architecture

KhmerDocKit is a small monorepo with three packages and a clear data flow.
This page gives the bird's-eye view plus the extension points.

## High-level data flow

```
                ┌──────────────┐
   user file ──▶│  FastAPI API │──┐
                │  (uvicorn)   │  │
                └──────┬───────┘  │
                       │          │
                ┌──────▼───────┐  │  HTTP / JSON
                │ Extraction   │  │
                │ Service      │  │
                └──────┬───────┘  │
                       │          │
        ┌──────────────┼──────────┤
        │              │          │
   ┌────▼─────┐   ┌────▼─────┐    │
   │ OCR      │   │ Extractor│    │
   │ Adapter  │   │          │    │
   │          │   │          │    │
   │ mock     │   │ rules    │    │
   │ paddle   │   │ (v0.3    │    │
   │ tesseract│   │  llm)    │    │
   └────┬─────┘   └────┬─────┘    │
        │              │          │
        └──────┬───────┘          │
               │                  │
        ┌──────▼───────┐          │
        │ Pydantic     │          │
        │ Schemas +    │          │
        │ Validators   │          │
        └──────┬───────┘          │
               │                  │
               ▼                  ▼
           JSON output        HTTP response
```

## Package boundaries

* `khmerdoc-core` — the library. Has no FastAPI / no HTTP / no Next.js
  dependencies. Imports `pydantic`, `pillow`, `opencv-python-headless`,
  `click`, `rich`. The OCR / LLM adapters are optional and loaded lazily.
* `khmerdoc-api` — a thin FastAPI wrapper around the core. It owns
  configuration, request validation, file size / MIME checks, and CORS.
* `khmerdoc-web` — a Next.js 14 (TypeScript + Tailwind) SPA. Talks to the
  API at `NEXT_PUBLIC_API_BASE_URL` and ships with 4 inline sample
  documents so it works without the dataset on disk.

## Why a monorepo?

* **One PR = one coherent change.** Schema, extractor, API, and demo can
  move together.
* **One CI runs everything.** The GitHub Actions workflow lints, tests, and
  Docker-builds all three packages from a single Python matrix.
* **One release.** Versions in `pyproject.toml` and the changelog move
  together; future v0.4 plugin work will live under the same root.

## Extension points

### Adding an OCR backend

1. Subclass `OCRAdapter` in `packages/khmerdoc-core/src/khmerdoc/ocr/base.py`.
2. Register it in `_register_defaults()` (same file).
3. Document the install step in `docs/ocr_adapters.md`.

### Adding an extractor backend

1. Subclass `Extractor` in
   `packages/khmerdoc-core/src/khmerdoc/extractors/base.py`.
2. Register it in `ExtractorRegistry.register` (same file).
3. The CLI / API will pick it up via
   `KHMERDOC_EXTRACTOR_BACKEND=<name>`.

### Adding a Cambodia-specific rule

1. Add a function returning `list[Warning]` in
   `packages/khmerdoc-core/src/khmerdoc/validators/cambodia.py`.
2. Wire it into `validate_extraction()`.
3. Add a unit test in `tests/test_validators.py`.

### Adding a document template

1. Add (or extend) a generator in
   `packages/khmerdoc-core/src/khmerdoc/synthetic/generate.py`.
2. Register it in the `GENERATORS` dict.
3. Add a test in `tests/test_synthetic.py`.

## Data flow invariants

* **No silent failures.** Every layer that encounters an unexpected
  condition either returns a low-confidence result with a `Warning` or
  raises a typed error that the API layer maps to a clear HTTP 4xx.
* **No real data in the repo.** The `datasets/synthetic/` directory is the
  only place documents live; the generator is fully deterministic.
* **No required external services.** The mock OCR + rule-based extractor
  run end-to-end with no network access, no GPU, and no API key.
* **Adapters are optional.** If a backend isn't installed, the registry
  raises a clear `ImportError`/`KeyError` with a hint to install the right
  extra.

## Open design questions (deliberately unresolved in v0.1)

* **LLM extraction contract.** v0.3 will define an OpenAI-compatible
  interface; until then, the rule-based extractor is the source of truth.
* **Plugin discovery.** v0.4 will let community templates register via
  entry-points (`importlib.metadata.entry_points`).
* **Benchmark leaderboard.** v0.4 will publish per-PR benchmark numbers;
  for v0.1 the benchmark is local-only.
