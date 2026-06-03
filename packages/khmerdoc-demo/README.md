# khmerdoc-demo

A single-command Gradio web UI for **KhmerDocKit**. Drop a file, click a
sample, or paste OCR text — get the typed JSON, formatted fields, and
warnings back. No API server, no Node.js, no two-process dance.

## Install

```bash
pip install -e packages/khmerdoc-demo
```

## Run

```bash
khmerdoc-demo                      # → http://localhost:7860
khmerdoc-demo --share              # also get a free public URL (72h)
khmerdoc-demo --port 8080          # custom port
```

## Features

* File upload (`.txt` / `.csv` / `.json` in the default mock mode).
* Text paste box for OCR output.
* Four built-in synthetic sample buttons (receipt / invoice / quotation / bank slip).
* Auto-detect or pinned document type.
* Formatted markdown view + raw JSON view.
* Per-field warnings.
* Renders line items as a Markdown table.

## How it works

The demo calls `khmerdoc-core` directly — there is **no API server**
involved. The same `RuleBasedExtractor` and Cambodia validators that the
FastAPI server uses run inside this process.

```python
from khmerdoc_demo import _build_ui   # not public; use the script entry point
```

## Limitations in v0.1.0

* Default OCR backend is `mock`, so image / PDF uploads display a
  placeholder. To run OCR on real images, install a real backend:

  ```bash
  pip install -e packages/khmerdoc-core[paddle]
  KHMERDOC_OCR_BACKEND=paddle khmerdoc-demo
  ```

  or

  ```bash
  pip install -e packages/khmerdoc-core[tesseract]
  KHMERDOC_OCR_BACKEND=tesseract khmerdoc-demo
  ```

  (The demo doesn't yet expose the OCR backend as a UI control — that's
  a v0.2 item.)

* Single user. Gradio's queueing works but is not tuned for production.

## Docker

A Docker image is provided at this package's root. The root
`docker-compose.yml` runs the API + the Next.js demo; the Gradio demo
runs standalone with `docker run` — see the Dockerfile.

## License

MIT — see [`../../LICENSE`](../../LICENSE).
