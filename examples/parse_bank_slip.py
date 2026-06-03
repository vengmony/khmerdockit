"""Programmatic example: parse a bank transfer confirmation."""

from __future__ import annotations

import json
from pathlib import Path

from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.ocr import MockOCRAdapter
from khmerdoc.schemas import DocumentType
from khmerdoc.validators import validate_extraction

BANK = """\
ACLEDA Bank
BANK TRANSFER CONFIRMATION
Reference: TRF123456
Date: 2026-05-30
From: Sokha Construction  Acc: 12345678
To:   Mekong Minimart     Acc: 87654321
Amount: $250.00
Status: SUCCESS
"""


def main() -> None:
    ocr = MockOCRAdapter(lines=BANK.splitlines())
    ocr_result = ocr.extract_text(Path("__not_used__.txt"))
    extractor = RuleBasedExtractor()
    result = extractor.extract(ocr_result, document_type=DocumentType.AUTO if hasattr(DocumentType, "AUTO") else DocumentType.BANK_SLIP)
    validate_extraction(result)
    print(json.dumps(result.to_jsonable(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
