"""Pydantic v2 schemas for KhmerDocKit.

All public models are exported from :mod:`khmerdoc.schemas`. The shapes are
intentionally kept close to the example in the project spec and are versioned
together — see ``ROADMAP.md`` and ``CHANGELOG.md``.
"""

from __future__ import annotations

from datetime import date as _date_cls
from enum import Enum
from typing import Any, Optional

# Pydantic v2 has a known issue where a class field whose name shadows an
# imported type (e.g. ``date``/``datetime``) gets resolved to the field's
# default value instead of the type. We work around this by aliasing the
# import and using it in the annotations. The plain ``date`` symbol is
# re-exported so external callers / docs keep working.
date = _date_cls  # noqa: A001  (intentional re-export)


_Date = _date_cls

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentType(str, Enum):
    """High-level classification of a business document."""

    RECEIPT = "receipt"
    INVOICE = "invoice"
    QUOTATION = "quotation"
    BANK_SLIP = "bank_slip"
    UNKNOWN = "unknown"


class Currency(str, Enum):
    """Currencies we currently model. Other ISO-4217 codes are allowed as strings."""

    USD = "USD"
    KHR = "KHR"


class Warning(BaseModel):
    """Non-fatal signal raised by an extractor or validator.

    The :attr:`code` is a stable, machine-readable identifier; the
    :attr:`message` is a human-readable explanation.
    """

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Stable machine-readable warning code, e.g. 'phone_format'.")
    message: str = Field(..., description="Human-readable explanation of the warning.")
    field: Optional[str] = Field(default=None, description="Optional field the warning applies to.")


class LineItem(BaseModel):
    """A single line on a receipt, invoice, or quotation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Description of the item or service.")
    quantity: float = Field(default=1.0, ge=0, description="Quantity purchased.")
    unit_price: Optional[float] = Field(default=None, ge=0, description="Price per single unit.")
    total: Optional[float] = Field(default=None, ge=0, description="Line total (quantity × unit_price).")

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("line item name must not be empty")
        return v


class _MoneyMixin(BaseModel):
    """Common money/totals fields shared by receipt / invoice / quotation."""

    model_config = ConfigDict(extra="forbid")

    currency: Currency | str = Field(default=Currency.USD, description="ISO-4217 or 'KHR' / 'USD'.")
    subtotal: Optional[float] = Field(default=None, ge=0)
    discount: Optional[float] = Field(default=None, ge=0)
    tax: Optional[float] = Field(default=None, ge=0)
    total: Optional[float] = Field(default=None, ge=0)

    @field_validator("currency", mode="before")
    @classmethod
    def _normalize_currency(cls, v: Any) -> Any:
        if v is None:
            return Currency.USD
        if isinstance(v, str):
            v_up = v.strip().upper()
            # Accept common glyphs by mapping them to ISO codes.
            glyph_map = {"$": "USD", "៛": "KHR", "KHR": "KHR", "USD": "USD", "US$": "USD"}
            if v_up in glyph_map:
                return glyph_map[v_up]
            return v_up
        return v


class Receipt(_MoneyMixin):
    """A point-of-sale receipt."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = DocumentType.RECEIPT
    merchant_name: Optional[str] = None
    date: Optional[_Date] = None
    phone_numbers: list[str] = Field(default_factory=list)
    invoice_number: Optional[str] = None
    line_items: list[LineItem] = Field(default_factory=list)


class Invoice(_MoneyMixin):
    """A tax/commercial invoice."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = DocumentType.INVOICE
    merchant_name: Optional[str] = None
    buyer_name: Optional[str] = None
    date: Optional[_Date] = None
    due_date: Optional[_Date] = None
    phone_numbers: list[str] = Field(default_factory=list)
    invoice_number: Optional[str] = None
    line_items: list[LineItem] = Field(default_factory=list)


class Quotation(_MoneyMixin):
    """A price quotation / estimate."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = DocumentType.QUOTATION
    merchant_name: Optional[str] = None
    buyer_name: Optional[str] = None
    date: Optional[_Date] = None
    valid_until: Optional[_Date] = None
    phone_numbers: list[str] = Field(default_factory=list)
    quotation_number: Optional[str] = None
    line_items: list[LineItem] = Field(default_factory=list)


class BankSlip(BaseModel):
    """A bank transfer / payment proof."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = DocumentType.BANK_SLIP
    bank_name: Optional[str] = None
    sender_name: Optional[str] = None
    sender_account: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_account: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    currency: Currency | str = Field(default=Currency.USD)
    date: Optional[_Date] = None
    reference: Optional[str] = None
    phone_numbers: list[str] = Field(default_factory=list)

    @field_validator("currency", mode="before")
    @classmethod
    def _normalize_currency(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_up = v.strip().upper()
            glyph_map = {"$": "USD", "៛": "KHR", "KHR": "KHR", "USD": "USD"}
            return glyph_map.get(v_up, v_up)
        return v


class OCRToken(BaseModel):
    """A single OCR token with optional bounding-box info."""

    model_config = ConfigDict(extra="forbid")

    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bbox: Optional[list[tuple[float, float, float, float]]] = None  # 4-point polygon


class OCRResult(BaseModel):
    """Output of an OCR adapter."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., description="Full extracted text, with lines joined by '\\n'.")
    tokens: list[OCRToken] = Field(default_factory=list)
    language: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    engine: str = Field(default="unknown", description="OCR engine identifier, e.g. 'mock' or 'paddle'.")
    raw: Optional[dict[str, Any]] = Field(default=None, description="Engine-specific raw output, if any.")


class ExtractionResult(BaseModel):
    """Top-level extraction result: typed document + diagnostics."""

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = DocumentType.UNKNOWN
    document: Optional[Receipt | Invoice | Quotation | BankSlip] = None
    raw_ocr_text: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: list[Warning] = Field(default_factory=list)
    engine: str = Field(default="rules", description="Extractor engine identifier.")

    def to_jsonable(self) -> dict[str, Any]:
        """Return a JSON-friendly dict matching the public example output."""
        out: dict[str, Any] = {
            "document_type": self.document_type.value,
            "confidence": round(self.confidence, 3),
            "warnings": [w.model_dump() for w in self.warnings],
            "raw_ocr_text": self.raw_ocr_text,
            "engine": self.engine,
        }
        if self.document is not None:
            # Merge the typed document's fields into the top-level dict so the
            # output shape matches the spec example (merchant_name, total, ...).
            doc_dump = self.document.model_dump(mode="json")
            for k, v in doc_dump.items():
                if k == "document_type":
                    continue
                out[k] = v
        return out


__all__ = [
    "BankSlip",
    "Currency",
    "DocumentType",
    "ExtractionResult",
    "Invoice",
    "LineItem",
    "OCRResult",
    "OCRToken",
    "Quotation",
    "Receipt",
    "Warning",
]
