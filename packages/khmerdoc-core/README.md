# khmerdoc-core

Reusable Python core for **KhmerDocKit**: Pydantic schemas, OCR adapter interface,
rule-based extraction, and Cambodia-specific validators for business documents
(receipts, invoices, quotations, bank slips).

This package is part of the [KhmerDocKit monorepo](../../). It is usable on its
own as a library, and is also consumed by the `khmerdoc-api` server and the
`khmerdoc-web` demo.

## Install

```bash
pip install -e packages/khmerdoc-core[dev]
```

## Quickstart

```python
from khmerdoc import DocumentType
from khmerdoc.ocr import MockOCRAdapter
from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.validators import validate_extraction

ocr = MockOCRAdapter(lines=[
    "Example Mart",
    "INV-000123  2026-06-02",
    "Classic Clog       1 x 12.50   12.50",
    "TOTAL USD         12.50",
    "Tel: 012345678",
])
text = ocr.extract_text("ignored-in-mock").text
result = RuleBasedExtractor().extract(text, document_type=DocumentType.RECEIPT)
validate_extraction(result)  # adds warnings, never raises
print(result.model_dump_json(indent=2))
```

## CLI

```bash
khmerdoc parse ./sample.jpg --type receipt
khmerdoc ocr ./sample.jpg
khmerdoc benchmark datasets/synthetic
```

## Why this exists

See the top-level [`README.md`](../../README.md) for the project mission and the
[`docs/cambodia_validation_rules.md`](../../docs/cambodia_validation_rules.md)
for the data-validation rules this package implements.
