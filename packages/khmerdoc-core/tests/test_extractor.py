"""Tests for the rule-based extractor."""

from __future__ import annotations

import pytest

from khmerdoc.extractors import RuleBasedExtractor
from khmerdoc.schemas import DocumentType


RECEIPT = """
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

INVOICE = """
Mekong Minimart
INVOICE
Invoice No: INV-123
Date: 02/06/2026
Due Date: 16/06/2026
Bill To: Sokha Construction
Tel: +85512345678
--------------------------------
Rice 5kg            2 x 25.00  =  50.00
Soap Bar            5 x  1.50  =   7.50
--------------------------------
SUBTOTAL    $57.50
TOTAL       $57.50
"""

BANK = """
ACLEDA Bank
BANK TRANSFER CONFIRMATION
Reference: TRF123456
Date: 2026-05-30
From: Sokha Construction  Acc: 12345678
To:   Mekong Minimart     Acc: 87654321
Amount: $250.00
Status: SUCCESS
"""

KHMER_NUMS = """
Example Mart
RECEIPT
No: INV-007
Date: ២០២៦-០៦-០១
Tel: 015 234 567
------------------------
Classic Clog        1 x 12.50   12.50
------------------------
TOTAL       $12.50
"""


@pytest.fixture
def extractor() -> RuleBasedExtractor:
    return RuleBasedExtractor()


def test_receipt_total(extractor: RuleBasedExtractor) -> None:
    r = extractor.extract(RECEIPT)
    assert r.document_type is DocumentType.RECEIPT
    assert r.document is not None
    assert r.document.total == 18.5
    assert r.document.currency == "USD"
    assert r.document.invoice_number == "INV-001"
    assert "012345678" in r.document.phone_numbers
    assert len(r.document.line_items) == 2
    assert r.warnings == []  # everything we look for is present


def test_invoice_international_phone(extractor: RuleBasedExtractor) -> None:
    r = extractor.extract(INVOICE)
    assert r.document_type is DocumentType.INVOICE
    assert r.document is not None
    assert r.document.invoice_number == "INV-123"
    assert r.document.total == 57.5
    assert any("+85512345678" in p for p in r.document.phone_numbers)


def test_bank_slip(extractor: RuleBasedExtractor) -> None:
    r = extractor.extract(BANK)
    assert r.document_type is DocumentType.BANK_SLIP
    assert r.document is not None
    assert r.document.amount == 250.0
    assert r.document.reference == "TRF123456"


def test_khmer_numerals_normalized(extractor: RuleBasedExtractor) -> None:
    r = extractor.extract(KHMER_NUMS)
    assert r.document is not None
    # 2026-06-01 after Khmer-numeral normalization
    assert r.document.date is not None
    assert r.document.date.year == 2026 and r.document.date.month == 6 and r.document.date.day == 1
    assert r.document.invoice_number == "INV-007"


def test_currency_khr_default_in_khmer_text(extractor: RuleBasedExtractor) -> None:
    text = "ហាងឧបត្តិយោគ\nRECEIPT\nTOTAL 12,500 ៛\nTel: 012345678"
    r = extractor.extract(text)
    assert r.document is not None
    assert r.document.currency == "KHR"


def test_unknown_type_defaults_to_receipt_with_warning(extractor: RuleBasedExtractor) -> None:
    text = "Random shop\n$10.00"
    r = extractor.extract(text)
    assert r.document_type is DocumentType.RECEIPT
    codes = {w.code for w in r.warnings}
    assert "document_type_inferred" in codes


def test_empty_input_returns_warning(extractor: RuleBasedExtractor) -> None:
    r = extractor.extract("")
    assert r.document_type is DocumentType.UNKNOWN
    assert any(w.code == "empty_input" for w in r.warnings)
