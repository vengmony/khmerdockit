"""Cambodia-specific validation rules.

These are *additive* checks layered on top of the Pydantic schemas. They never
raise: they return :class:`Warning` objects that are appended to the
extraction result so the caller can see what is suspect.

The rules are documented in ``docs/cambodia_validation_rules.md``.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Iterable

from ..schemas import (
    BankSlip,
    ExtractionResult,
    Invoice,
    LineItem,
    Quotation,
    Receipt,
    Warning,
)

# ---- Phone numbers ---------------------------------------------------------

# Local mobile format: 0X XXX XXXX (10 digits, sometimes written 0XX XXX XXX).
# Landline in Phnom Penh: 023 XXX XXX.
_PHONE_LOCAL_RE = re.compile(r"^0\d{8,9}$")
_PHONE_INTL_RE = re.compile(r"^\+?855\d{8,9}$")


def validate_phone(value: str) -> list[Warning]:
    """Return warnings for a phone number that does not match Cambodia formats."""
    warnings: list[Warning] = []
    v = re.sub(r"[\s\-]", "", value or "")
    if not v:
        warnings.append(
            Warning(code="phone_empty", message="Phone number is empty.", field="phone_numbers")
        )
        return warnings
    if not (_PHONE_LOCAL_RE.match(v) or _PHONE_INTL_RE.match(v)):
        warnings.append(
            Warning(
                code="phone_format",
                message=(
                    f"Phone '{value}' does not match Cambodian formats "
                    "(0XXXXXXXX, +855XXXXXXXX, or 0XXX XXX XXX)."
                ),
                field="phone_numbers",
            )
        )
    return warnings


# ---- Currency --------------------------------------------------------------

_VALID_CURRENCIES = {"USD", "KHR"}


def validate_currency(value: str | None) -> list[Warning]:
    """Warn when currency is not USD or KHR."""
    if value is None:
        return [Warning(code="currency_missing", message="Currency not set.")]
    v = str(value).upper()
    if v in ("$", "USD"):
        return []
    if v in ("៛", "KHR", "RIEL"):
        return []
    return [
        Warning(
            code="currency_unusual",
            message=f"Currency '{value}' is not USD or KHR; double-check the document.",
            field="currency",
        )
    ]


# ---- Dates -----------------------------------------------------------------


def validate_date(
    value: date | None,
    *,
    field: str = "date",
    max_future_years: int = 1,
    max_past_years: int = 10,
    today: date | None = None,
) -> list[Warning]:
    """Warn when a date is far in the past/future, or unparseable."""
    if value is None:
        return []
    today = today or date.today()
    if value > today + timedelta(days=365 * max_future_years):
        return [
            Warning(
                code="date_far_future",
                message=f"Date {value.isoformat()} is far in the future.",
                field=field,
            )
        ]
    if value < today - timedelta(days=365 * max_past_years):
        return [
            Warning(
                code="date_far_past",
                message=f"Date {value.isoformat()} is far in the past.",
                field=field,
            )
        ]
    return []


# ---- Full-result validation ------------------------------------------------


def _doc_phone_numbers(doc: Receipt | Invoice | Quotation | BankSlip | None) -> list[str]:
    if doc is None:
        return []
    return list(getattr(doc, "phone_numbers", []) or [])


def _line_items(doc: Receipt | Invoice | Quotation | BankSlip | None) -> list[LineItem]:
    if isinstance(doc, (Receipt, Invoice, Quotation)):
        return list(doc.line_items or [])
    return []


def _line_total_check(item: LineItem) -> list[Warning]:
    if item.unit_price is None or item.total is None:
        return []
    expected = round(item.unit_price * item.quantity, 2)
    if abs(expected - round(item.total, 2)) > 0.02:
        return [
            Warning(
                code="line_item_total_mismatch",
                message=(
                    f"Line '{item.name}': qty × unit ({expected:.2f}) "
                    f"does not match total ({item.total:.2f})."
                ),
                field="line_items",
            )
        ]
    return []


def validate_extraction(result: ExtractionResult) -> ExtractionResult:
    """Add Cambodia-specific warnings to ``result`` in-place and return it."""
    doc = result.document

    # Currency
    if doc is not None:
        cur = getattr(doc, "currency", None)
        result.warnings.extend(validate_currency(cur))

    # Phones
    for phone in _doc_phone_numbers(doc):
        result.warnings.extend(validate_phone(phone))

    # Dates
    for field in ("date", "due_date", "valid_until"):
        d = getattr(doc, field, None) if doc is not None else None
        result.warnings.extend(validate_date(d, field=field))

    # Line items
    for item in _line_items(doc):
        result.warnings.extend(_line_total_check(item))

    # De-duplicate (same code+message+field).
    seen: set[tuple[str, str, str | None]] = set()
    deduped: list[Warning] = []
    for w in result.warnings:
        key = (w.code, w.message, w.field)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(w)
    result.warnings = deduped
    return result


__all__ = [
    "validate_currency",
    "validate_date",
    "validate_extraction",
    "validate_phone",
]
