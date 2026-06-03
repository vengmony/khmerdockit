"""khmerdoc-core: reusable Cambodia-focused document understanding primitives."""

from .schemas import (  # noqa: F401
    BankSlip,
    Currency,
    DocumentType,
    ExtractionResult,
    Invoice,
    LineItem,
    OCRResult,
    Quotation,
    Receipt,
    Warning,
)

__version__ = "0.1.0"

__all__ = [
    "BankSlip",
    "Currency",
    "DocumentType",
    "ExtractionResult",
    "Invoice",
    "LineItem",
    "OCRResult",
    "Quotation",
    "Receipt",
    "Warning",
    "__version__",
]
