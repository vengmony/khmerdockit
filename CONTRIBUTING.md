# Contributing to KhmerDocKit

Thanks for your interest in **KhmerDocKit** — we welcome contributions from
developers, designers, accountants, and Cambodia tech enthusiasts.

This project is in an **early MVP state (v0.1.0)**. The best ways to help right
now are:

1. Try the demo, file a bug, or request a feature.
2. Add a new synthetic document template.
3. Improve a Cambodia-specific validation rule.
4. Add a new OCR backend.
5. Improve documentation (English first, Khmer later).

## Ground rules

* Be respectful. Read and follow the [Code of Conduct](./CODE_OF_CONDUCT.md).
* **Do not commit real receipts, real merchant names, or any private data.** The
  `datasets/synthetic/` directory is the only place documents live; everything
  there is generated.
* **Do not commit API keys, passwords, or `.env` files.** The repo's
  `.gitignore` already excludes `.env`.

## Local setup

```bash
git clone https://github.com/<your-fork>/khmerdockit
cd khmerdockit

make install           # installs khmerdoc-core + khmerdoc-api in editable mode
make install-web       # installs the Next.js demo deps (Node 20+)
make test              # runs pytest across packages
make lint              # runs ruff
make api               # starts the FastAPI server on :8000
make web               # starts the Next.js demo on :3000
```

You can also use `docker compose up --build` to run the whole stack.

## Development workflow

1. Create a branch from `main` (e.g. `feat/khmer-date-parser`).
2. Make focused commits with descriptive messages.
3. Update tests when you change behaviour. The existing tests live in
   `packages/khmerdoc-core/tests` and `packages/khmerdoc-api/tests`.
4. If you add a new dependency, add it to the matching `pyproject.toml` /
   `package.json`.
5. Open a PR using the [PR template](./.github/PULL_REQUEST_TEMPLATE.md).

## Adding a new document template

The synthetic generator is in
`packages/khmerdoc-core/src/khmedoc/synthetic/generate.py`. To add a new
template:

1. Add (or extend) a generator function (e.g. `gen_market_receipt`).
2. Register it in the `GENERATORS` dict at the bottom of the file.
3. Add a test in `tests/test_synthetic.py` that checks the layout.
4. Run `khmerdoc benchmark datasets/synthetic` and inspect the scores.

## Adding a new OCR backend

OCR backends live in `packages/khmerdoc-core/src/kmedoc/ocr/`:

1. Subclass `OCRAdapter` in `ocr/base.py`.
2. Register the adapter in the `OcrAdapterRegistry` (the
   `_register_defaults()` function in `ocr/base.py`).
3. Add a test in `tests/test_ocr.py` that uses the `mock` adapter to simulate
   the new engine's behaviour.

## Adding a new validation rule

Cambodia-specific checks live in
`packages/khmerdoc-core/src/kmedoc/validators/cambodia.py`. Add a new
function that returns `list[Warning]`, then wire it into
`validate_extraction`. Add a test in `tests/test_validators.py`.

## Release process

(Once v0.2+ is cut)

1. Bump versions in `packages/*/pyproject.toml` and `CHANGELOG.md`.
2. Tag the release: `git tag v0.X.Y && git push --tags`.
3. The maintainers will cut a GitHub release and (eventually) build Docker
   images.

## Questions?

Open an issue. We're friendly. 🙂
