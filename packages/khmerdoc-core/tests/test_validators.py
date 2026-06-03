"""Tests for Cambodia-specific validators."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from khmerdoc.schemas import (
    DocumentType,
    ExtractionResult,
    Invoice,
    LineItem,
    Receipt,
    Warning,
)
from khmerdoc.validators import (
    validate_currency,
    validate_date,
    validate_extraction,
    validate_phone,
)


def test_valid_local_phone() -> None:
    assert validate_phone("012345678") == []
    assert validate_phone("012 345 678") == []


def test_valid_international_phone() -> None:
    assert validate_phone("+85512345678") == []
    assert validate_phone("85512345678") == []


def test_invalid_phone() -> None:
    w = validate_phone("999")
    assert any(x.code == "phone_format" for x in w)


def test_empty_phone() -> None:
    w = validate_phone("")
    assert any(x.code == "phone_empty" for x in w)


def test_currency_normal() -> None:
    assert validate_currency("USD") == []
    assert validate_currency("$") == []
    assert validate_currency("KHR") == []
    assert validate_currency("៛") == []


def test_currency_unusual() -> None:
    w = validate_currency("EUR")
    assert any(x.code == "currency_unusual" for x in w)


def test_currency_missing() -> None:
    w = validate_currency(None)
    assert any(x.code == "currency_missing" for x in w)


def test_date_in_range() -> None:
    assert validate_date(date.today()) == []


def test_date_far_past() -> None:
    old = date.today() - timedelta(days=365 * 15)
    w = validate_date(old)
    assert any(x.code == "date_far_past" for x in w)


def test_date_far_future() -> None:
    future = date.today() + timedelta(days=365 * 2)
    w = validate_date(future)
    assert any(x.code == "date_far_future" for x in w)


def test_line_item_total_mismatch_flagged() -> None:
    r = ExtractionResult(
        document_type=DocumentType.RECEIPT,
        document=Receipt(
            line_items=[
                LineItem(name="x", quantity=2, unit_price=5.0, total=20.0),  # 2*5=10, not 20
            ]
        ),
    )
    validate_extraction(r)
    assert any(w.code == "line_item_total_mismatch" for w in r.warnings)


def test_full_extraction_validation_dedups_warnings() -> None:
    r = ExtractionResult(
        document_type=DocumentType.INVOICE,
        document=Invoice(currency="EUR", phone_numbers=["abc"]),
        warnings=[
            Warning(
                code="phone_format",
                message="Phone 'abc' does not match Cambodian formats (0XXXXXXXX, +855XXXXXXXX, or 0XXX XXX XXX).",
                field="phone_numbers",
            )
        ],
    )
    validate_extraction(r)
    codes = [w.code for w in r.warnings]
    assert codes.count("phone_format") == 1
    assert "currency_unusual" in codes
