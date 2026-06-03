# khmerdoc-api

FastAPI server for **KhmerDocKit**. Exposes:

* `GET  /health`
* `POST /v1/parse`  — upload a document image/PDF, get structured JSON
* `POST /v1/ocr`    — upload a document, get raw OCR text
* `GET  /v1/schemas` — public Pydantic JSON schemas
* `GET  /docs`      — Swagger UI (auto-generated)
* `GET  /redoc`     — ReDoc (auto-generated)

## Run

```bash
make install         # installs khmerdoc-core and khmerdoc-api
make api             # uvicorn with reload
# or
uvicorn khmerdoc_api.main:app --host 0.0.0.0 --port 8000
```

## Configuration

All configuration is via environment variables; see `.env.example` in the
repo root.

| Variable                     | Default                                     | Description                                    |
| ---------------------------- | ------------------------------------------- | ---------------------------------------------- |
| `KHMERDOC_OCR_BACKEND`       | `mock`                                      | `mock`, `paddle`, or `tesseract`               |
| `KHMERDOC_OCR_LANG`          | `en`                                        | OCR language code                              |
| `KHMERDOC_EXTRACTOR_BACKEND` | `rules`                                     | `rules` (only in v0.1)                         |
| `KHMERDOC_API_PORT`          | `8000`                                      | Listen port                                    |
| `KHMERDOC_API_CORS_ORIGINS`  | `http://localhost:3000`                     | Comma-separated CORS allow-list                |
| `KHMERDOC_API_MAX_UPLOAD_MB` | `10`                                        | Max upload size in MB                          |
| `KHMERDOC_API_ALLOWED_MIME`  | `image/jpeg,image/png,image/webp,application/pdf` | Comma-separated MIME allow-list       |

## Curl example

```bash
curl -X POST http://localhost:8000/v1/parse \
  -F "file=@examples/sample_receipt.jpg" \
  -F "document_type=receipt"
```
