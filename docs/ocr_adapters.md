# OCR adapters

OCR adapters convert a file on disk into an `OCRResult` (text + optional
per-token confidences). KhmerDocKit ships with three adapters and a tiny
registry.

## Adapters

### `mock` (default)

* **What it does:** returns whatever text it was initialised with.
* **Install:** built in.
* **Use case:** tests, offline demos, and the synthetic dataset.

```python
from khmerdoc.ocr import MockOCRAdapter
ocr = MockOCRAdapter(lines=open("receipt.txt").read().splitlines())
print(ocr.extract_text("ignored.jpg").text)
```

### `tesseract`

* **What it does:** wraps `pytesseract` + the system `tesseract` binary.
* **Install:** `pip install -e "packages/khmerdoc-core[tesseract]"` and
  install the system package (`apt install tesseract-ocr tesseract-ocr-khm`
  on Debian/Ubuntu, `brew install tesseract tesseract-lang` on macOS).
* **Use case:** local OCR for English (`eng`) and Khmer (`khm`) scripts.

```python
from khmerdoc.ocr import TesseractOCRAdapter
ocr = TesseractOCRAdapter(lang="eng+khm")
ocr.extract_text("receipt.jpg")
```

### `paddle`

* **What it does:** wraps the PaddleOCR Python package.
* **Install:** `pip install -e "packages/khmerdoc-core[paddle]"`. The
  first run downloads model weights.
* **Use case:** better quality on Khmer-script documents, low-light
  phone photos.

```python
from khmerdoc.ocr import PaddleOCRAdapter
ocr = PaddleOCRAdapter(lang="km", use_angle_cls=True)
ocr.extract_text("receipt.jpg")
```

## Selecting an adapter

The API and CLI pick the adapter from `KHMERDOC_OCR_BACKEND`. You can also
instantiate adapters directly in Python.

```bash
# API
KHMERDOC_OCR_BACKEND=tesseract KHMERDOC_OCR_LANG=eng+khm make api

# CLI
khmerdoc ocr sample.jpg --ocr-backend paddle
```

## Adding your own backend

1. Subclass `OCRAdapter` in
   `packages/khmerdoc-core/src/khmedoc/ocr/base.py`.
2. Register the factory in `_register_defaults()` (same file).
3. Add a test in `tests/test_ocr.py` that uses `MockOCRAdapter` to
   simulate the new engine's behaviour.
4. Add a section to this document with install / usage instructions.

The adapter must:

* Accept a `str | Path` and return an `OCRResult` with non-empty `text`.
* Raise `FileNotFoundError` if the file does not exist.
* **Never** silently return empty text on real errors — return a
  low-confidence result with an explanatory warning, or raise.
