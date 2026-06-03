"""Programmatic example: parse a receipt via the rule-based extractor."""

from __future__ import annotations

import json
from pathlib import Path

from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.ocr import MockOCRAdapter
from khmerdoc.schemas import DocumentType
from khmerdoc.validators import validate_extraction

RECEIPT = """\
Example Mart
RECEIPT
No: INV-001
Date: 2026-06-02
Tel: 012345678
------------------------
Classic Clog        1 x 12.50   12.50
USB-C Cable 1m      2 x  3.00    6.00
------------------------
SUBTOTAL    $18.50
TOTAL       $18.50
Thank you!
"""


def main() -> None:
    ocr = MockOCRAdapter(lines=RECEIPT.splitlines())
    # The mock adapter doesn't read the file, but the API takes a path
    # so we just pass a placeholder.
    placeholder = Path("__not_used__.txt")
    ocr_result = ocr.extract_text(placeholder)

    extractor = RuleBasedExtractor()
    result = extractor.extract(ocr_result, document_type=DocumentType.RECEIPT)
    validate_extraction(result)

    print(json.dumps(result.to_jsonable(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
