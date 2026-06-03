"""Tests for ``khmerdoc.schemas`` — focused on public Pydantic v2 behaviour."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from khmerdoc.schemas import (
    BankSlip,
    DocumentType,
    ExtractionResult,
    Invoice,
    LineItem,
    Quotation,
    Receipt,
    Warning,
)


def test_receipt_minimal() -> None:
    r = Receipt()
    assert r.document_type is DocumentType.RECEIPT
    assert r.currency == "USD"
    assert r.line_items == []


def test_currency_glyph_normalization() -> None:
    assert Receipt(currency="$").currency == "USD"
    assert Receipt(currency="៛").currency == "KHR"
    assert Receipt(currency="usd").currency == "USD"
    assert Receipt(currency="KHR").currency == "KHR"


def test_line_item_total_must_be_non_negative() -> None:
    with pytest.raises(ValidationError):
        LineItem(name="x", quantity=1, unit_price=-1, total=1)


def test_line_item_empty_name_rejected() -> None:
    with pytest.raises(ValidationError):
        LineItem(name="   ")


def test_extraction_result_to_jsonable_flattens_document() -> None:
    r = ExtractionResult(
        document_type=DocumentType.RECEIPT,
        document=Receipt(
            merchant_name="X",
            total=12.5,
            currency="USD",
            date=date(2026, 6, 2),
            line_items=[LineItem(name="a", quantity=1, unit_price=12.5, total=12.5)],
        ),
        confidence=0.9,
        raw_ocr_text="X",
        warnings=[Warning(code="x", message="y")],
    )
    out = r.to_jsonable()
    assert out["document_type"] == "receipt"
    assert out["merchant_name"] == "X"
    assert out["total"] == 12.5
    assert out["line_items"][0]["name"] == "a"


def test_document_type_literal_for_invoice() -> None:
    inv = Invoice(total=1.0)
    assert inv.document_type is DocumentType.INVOICE
    # Receipt/Invoice classes default to their own document_type; the user
    # is allowed to set it explicitly if needed.
    inv2 = Invoice(document_type=DocumentType.QUOTATION)  # type: ignore[arg-type]
    assert inv2.document_type is DocumentType.QUOTATION


def test_bank_slip_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        BankSlip(amount=-1.0)


def test_quotation_uses_quotation_number() -> None:
    q = Quotation(quotation_number="QT-001")
    assert q.quotation_number == "QT-001"
    # Receipt/Invoice/Quotation have type-specific number fields; the
    # ``invoice_number`` accessor only exists on Receipt/Invoice.
    assert not hasattr(q, "invoice_number") or getattr(q, "invoice_number", None) is None
