"""Programmatic example: parse an invoice via the rule-based extractor."""

from __future__ import annotations

import json
from pathlib import Path

from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.ocr import MockOCRAdapter
from khmerdoc.schemas import DocumentType
from khmerdoc.validators import validate_extraction

INVOICE = """\
Mekong Minimart
INVOICE
Invoice No: INV-123
Date: 02/06/2026
Due Date: 16/06/2026
Bill To: Sokha Construction Co., Ltd.
Tel: +85512345678
--------------------------------
Rice 5kg            2 x 25.00  =  50.00
Soap Bar            5 x  1.50  =   7.50
USB-C Cable 1m      3 x  3.00  =   9.00
--------------------------------
SUBTOTAL    $66.50
TOTAL       $66.50
"""


def main() -> None:
    ocr = MockOCRAdapter(lines=INVOICE.splitlines())
    ocr_result = ocr.extract_text(Path("__not_used__.txt"))
    extractor = RuleBasedExtractor()
    result = extractor.extract(ocr_result, document_type=DocumentType.INVOICE)
    validate_extraction(result)
    print(json.dumps(result.to_jsonable(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
