# Self-hosting KhmerDocKit

This guide covers running the **khmerdoc-api** server in a production-like
setup: a real OCR backend, a process manager, and basic observability.

For day-to-day hacking on the library or trying the demo, the
[quickstart](../quickstart.md) is enough. Come back here when you want
to put KhmerDocKit in front of real users.

## Pick an OCR backend

| Backend    | Install                              | Languages       | Speed       | Quality (Khmer) | When to use |
| ---------- | ------------------------------------ | --------------- | ----------- | --------------- | ----------- |
| `mock`     | nothing extra                        | n/a (text only) | instant     | n/a             | tests, CI, demos |
| `tesseract`| `apt install tesseract-ocr tesseract-ocr-khm` + `pip install pytesseract` | `eng`, `khm` | fast on CPU | OK | low-resource VPS, no GPU |
| `paddle`   | `pip install paddleocr` (downloads weights on first run) | `en`, `km`, ... | medium | good | high-quality Khmer OCR, has GPU |
| `easyocr`  | `pip install easyocr` (downloads weights on first run) | 80+ languages | medium | good | multilingual, no Khmer-native script but works |

For production, **PaddleOCR** is the best fit for Khmer. **Tesseract**
is a good fallback on small VPS instances without a GPU.

## Run the API with a real OCR backend

```bash
# one-time
pip install -e "packages/khmerdoc-core[paddle]"

# daily
export KHMERDOC_OCR_BACKEND=paddle
export KHMERDOC_OCR_LANG=km
export KHMERDOC_EXTRACTOR_BACKEND=rules
export KHMERDOC_API_MAX_UPLOAD_MB=10
uvicorn khmerdoc_api.main:app --host 0.0.0.0 --port 8000 --workers 2
```

## Run with Docker

The repo ships a `docker-compose.yml` that runs the API + the Next.js
demo. The Gradio demo is an opt-in profile.

```bash
# API + Next.js demo
docker compose up --build

# + the single-command Gradio demo (on port 7860)
docker compose --profile gradio up --build
```

## Production hardening checklist

The current FastAPI server is intentionally minimal. Before exposing it
to the public internet, do at least these:

* **Run behind a reverse proxy** (nginx, Caddy, Cloudflare) that
  terminates TLS, rate-limits requests, and adds a request-size cap.
* **Put uploads behind auth.** v0.1.0 has no auth — anyone with the
  URL can upload. Add an API key, OAuth2, or a session cookie before
  going live.
* **Wire real logging.** The server uses `logging.basicConfig`; replace
  this with a structured-logging setup that ships to your
  observability stack.
* **Add `/metrics` and `/healthz`.** v0.1.0 has `/health` (returns
  `{"status": "ok"}`); production should add a deep healthcheck that
  verifies the OCR backend is actually loadable.
* **Pin versions in production.** The `pyproject.toml` declares
  `>=` constraints. For Docker, install with `pip install
  khmerdoc-api==0.1.0` instead of `-e .`.
* **Set `KHMERDOC_API_CORS_ORIGINS`** to your real web origin, not
  the default `http://localhost:3000`.

## Deployment patterns

### Single-VPS (smallest setup)

```text
       ┌────────────┐
       │  nginx     │  TLS, rate-limit, request size cap
       └─────┬──────┘
             │ 127.0.0.1:8000
       ┌─────▼──────┐
       │  uvicorn   │  1 worker, 4 threads (PaddleOCR benefits from threads)
       │  + khmerdoc-api
       └────────────┘
```

### Container (small / medium)

```text
       ┌────────────┐
       │  Cloudflare│  TLS + WAF
       └─────┬──────┘
             │
       ┌─────▼──────┐
       │  nginx     │  reverse proxy + size cap
       └─────┬──────┘
             │
       ┌─────▼──────┐
       │  uvicorn   │  docker compose
       │  (2 replicas behind a load balancer)
       └────────────┘
```

### Multi-tenant / SaaS

Out of scope for v0.1.0. The schemas and the FastAPI app are
multi-tenant-friendly (the `ExtractionResult` carries the full input
and the warnings, so a downstream service can do its own bookkeeping).
For v0.3+ we expect a thin auth + per-tenant rate-limit layer to be
added; see [`ROADMAP.md`](../ROADMAP.md).

## Operational metrics worth watching

* **Requests per minute** by document type.
* **P50 / P95 latency** of `/v1/parse` (target: <2s for a typical
  receipt on CPU, <500ms with GPU).
* **OCR confidence** distribution (sudden drops = OCR backend
  regression).
* **Warning-rate** per field (e.g. `line_item_total_mismatch` rising =
  extractor regression on a new layout).
* **OOM / GPU memory** when using PaddleOCR.

## What to do when something breaks

1. Check the obvious: `pip show khmerdoc-core` and `pip show
   khmerdoc-api` should both be at the version you expect.
2. Reproduce with `khmerdoc parse <file>` — the CLI uses the same code
   path as the API and is much easier to debug.
3. Run the benchmark: `khmerdoc benchmark datasets/synthetic`. A
   regression here is the single most actionable signal.
4. File a bug at
   <https://github.com/vengmony/khmerdockit/issues/new?template=bug_report.yml>.
