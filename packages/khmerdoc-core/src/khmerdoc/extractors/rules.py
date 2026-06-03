"""A small, dependency-free rule-based extractor.

It uses regular expressions and a handful of heuristics tuned for the kinds of
documents we see in the synthetic dataset. It is intentionally NOT a full NLP
pipeline — the goal is to give the rest of the system a working baseline
without requiring a model download, GPU, or API key.

The extractor is conservative: when in doubt, it leaves a field empty and
emits a :class:`Warning` rather than guessing. The LLM adapter (v0.3) is
responsible for filling in harder fields with explicit confidence.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from ..schemas import (
    BankSlip,
    DocumentType,
    ExtractionResult,
    Invoice,
    LineItem,
    OCRResult,
    Quotation,
    Receipt,
    Warning,
)
from .base import Extractor

# ---- regexes ---------------------------------------------------------------

# Currency tokens we recognize.
_CURRENCY_RE = re.compile(
    r"(?P<sym>\$|៛|USD|KHR|US\$)\s*",
    re.IGNORECASE,
)

# Cambodian phone numbers: 0XXXXXXXX, +855XXXXXXXX, 855XXXXXXXX, with optional
# spaces/dashes. Mobile prefixes commonly used: 0[1-9][0-9]{7,8}.
_PHONE_RE = re.compile(
    r"(?:\+?855\s*|0)(?:\s|-)?[1-9](?:\s|-)?\d{3}(?:\s|-)?\d{3,5}\b"
)

# Invoice / reference numbers: the actual reference id (e.g. ``INV-001``)
# with the prefix embedded in the captured ``num``.
_REF_BARE_RE = re.compile(
    r"\b(?P<num>INV[-/]?\d{2,12}|RCP[-/]?\d{2,12}|RCPT[-/]?\d{2,12}"
    r"|QUOT[-/]?\d{2,12}|QT[-/]?\d{2,12}"
    r"|REF[-/]?[A-Z0-9-]{2,12}|TRF\d{4,12}|TXN\d{4,12})\b",
    re.IGNORECASE,
)

# ``Keyword: ID`` form: e.g. ``No: INV-001``, ``Invoice No: INV-001``,
# ``Ref TRF123456``. The keyword (e.g. ``No``, ``Invoice No``, ``Ref``)
# is captured in ``kw`` and the actual reference ID in ``num``.
_REF_KEYWORD_RE = re.compile(
    r"\b(?:Invoice\s+No\.?|Receipt\s+No\.?|Quotation\s+No\.?|Quote\s+No\.?"
    r"|Inv\.?|Receipt|Quotation|Quote|No\.?|Ref\.?|Reference|Txn|Trf|Trans(?:fer)?|ID)\b"
    r"\s*[#:.\-]?\s*"
    r"(?P<num>INV[-/]?\d{2,12}|RCP[-/]?\d{2,12}|RCPT[-/]?\d{2,12}"
    r"|QUOT[-/]?\d{2,12}|QT[-/]?\d{2,12}"
    r"|REF[-/]?[A-Z0-9-]{2,12}|TRF\d{4,12}|TXN\d{4,12}|\d{3,12})\b",
    re.IGNORECASE,
)

# Legacy name for backwards-compat (used by tests/callers that introspect).
_REF_RE = _REF_KEYWORD_RE

# Dates: a few common formats we see on Cambodian receipts/invoices.
_DATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"),              # 2026-06-02
    re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b"),  # 02/06/2026, 02-06-26
    re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{2,4})\b", re.IGNORECASE),
]

# A line that looks like a money value: optional sign, digits, optional
# thousand separators, optional decimal part.
_MONEY_RE = re.compile(r"-?\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")

# Total / grand total lines. We look for explicit keywords first.
_TOTAL_KEYWORDS = (
    "GRAND TOTAL",
    "TOTAL DUE",
    "AMOUNT DUE",
    "BALANCE DUE",
    "TOTAL",
    "NET TOTAL",
)

# Subtotal / tax keywords.
_SUBTOTAL_KEYWORDS = ("SUBTOTAL", "SUB-TOTAL", "SUB TOTAL")
_TAX_KEYWORDS = ("VAT", "TAX", "GST")
_DISCOUNT_KEYWORDS = ("DISCOUNT",)

# Heuristics for line items: a line with at least 2 numbers and a non-numeric
# description. We keep it conservative to avoid misreading headers. The
# optional currency glyph (`$` / `៛`) is allowed in front of unit/total
# values to handle the common "Item  1 x $12.50   $12.50" layout.
_LINE_ITEM_RE = re.compile(
    r"""^(?P<name>.*?)\s+
        (?P<qty>\d+(?:\.\d+)?)\s*[xX*]?\s*
        (?:[$៛]\s*)?
        (?P<unit>\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s+
        (?:[$៛]\s*)?
        (?P<total>\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)
        \s*$
    """,
    re.VERBOSE,
)

# Khmer numerals map (used for merchants that print in Khmer script).
_KHMER_NUMERALS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")


def _to_float(token: str) -> float | None:
    if not token:
        return None
    cleaned = token.replace(",", "").replace(" ", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_currency(token: str | None) -> str | None:
    if not token:
        return None
    t = token.strip().upper().replace("US$", "USD")
    if t in ("$", "USD"):
        return "USD"
    if t in ("៛", "KHR", "RIEL"):
        return "KHR"
    return t


def _detect_currency(text: str) -> str:
    if "៛" in text or re.search(r"\bKHR\b", text, re.IGNORECASE):
        return "KHR"
    if "$" in text or re.search(r"\bUSD\b", text, re.IGNORECASE):
        return "USD"
    return "USD"  # default


def _parse_date(text: str) -> date | None:
    for pat in _DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        groups = m.groups()
        try:
            if len(groups) == 3 and len(groups[0]) == 4:
                return date(int(groups[0]), int(groups[1]), int(groups[2]))
            if len(groups) == 3 and groups[1].isdigit():
                # dd/mm/yyyy or mm/dd/yyyy — we assume dd/mm/yyyy (Cambodia).
                d, mo, y = int(groups[0]), int(groups[1]), int(groups[2])
                if y < 100:
                    y += 2000
                return date(y, mo, d)
            if len(groups) == 3:
                # "02 Jun 2026"
                d = int(groups[0])
                mo_name = groups[1].lower()[:3]
                y = int(groups[2])
                if y < 100:
                    y += 2000
                months = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                }
                if mo_name in months:
                    return date(y, months[mo_name], d)
        except (ValueError, TypeError):
            continue
    return None


def _detect_phones(text: str) -> list[str]:
    raw = _PHONE_RE.findall(text)
    cleaned: list[str] = []
    for r in raw:
        c = re.sub(r"[\s-]", "", r)
        if c not in cleaned:
            cleaned.append(c)
    return cleaned


def _classify_ref(num: str) -> str:
    """Return the field name for a reference ID like ``INV-001`` or ``TRF123``."""
    n = num.upper()
    if n.startswith("INV"):
        return "invoice_number"
    if n.startswith("RCP") or n.startswith("RCPT") or n.startswith("RECEIPT"):
        return "receipt_number"
    if n.startswith("QUOT") or n.startswith("QT"):
        return "quotation_number"
    return "reference"


def _detect_ref(text: str) -> tuple[str | None, str | None]:
    """Return (field_name, value) for the most likely reference number."""
    candidates: list[tuple[int, str, str]] = []  # (priority, kind, value)

    # 1) Bare forms: "INV-001" appears anywhere in the document.
    for m in _REF_BARE_RE.finditer(text):
        num = m.group("num").upper()
        kind = _classify_ref(num)
        candidates.append((20 + len(num), kind, num))

    # 2) Keyword form: "No: INV-001" / "Invoice No: INV-001" / "Ref TRF123".
    for m in _REF_KEYWORD_RE.finditer(text):
        num = m.group("num").upper()
        kind = _classify_ref(num)
        # Keyword form is a slightly stronger signal than the bare form
        # (the user explicitly said "No:" etc).
        candidates.append((25 + len(num), kind, num))

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[0], reverse=True)
    _, kind, value = candidates[0]
    return kind, value


def _detect_total_amount(text: str) -> tuple[float | None, str | None]:
    """Find the most likely total / grand-total amount on the document.

    In addition to the explicit TOTAL / GRAND TOTAL keywords, we also treat
    bank-slip ``Amount: $X`` lines as totals so the same helper works for
    receipts, invoices, quotations, and bank transfers.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for kw in _TOTAL_KEYWORDS:
        for ln in lines:
            up = ln.upper()
            if up.startswith(kw) or f" {kw} " in f" {up} ":
                nums = _MONEY_RE.findall(ln)
                if not nums:
                    continue
                val = _to_float(nums[-1])
                if val is not None and val >= 0:
                    return val, kw.title()
    # Bank slip / transfer style.
    amt_pat = re.compile(r"\bAMOUNT\b[^\d\-]*(-?\d[\d,\s]*(?:\.\d+)?)", re.IGNORECASE)
    m = amt_pat.search(text)
    if m:
        val = _to_float(m.group(1))
        if val is not None and val >= 0:
            return val, "Amount"
    return None, None


def _detect_money_for_keywords(text: str, keywords: Iterable[str]) -> float | None:
    for kw in keywords:
        pat = re.compile(rf"\b{re.escape(kw)}\b[^\d\-]*(-?\d[\d,\s]*(?:\.\d+)?)", re.IGNORECASE)
        m = pat.search(text)
        if m:
            val = _to_float(m.group(1))
            if val is not None:
                return val
    return None


def _detect_line_items(text: str) -> list[LineItem]:
    items: list[LineItem] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = _LINE_ITEM_RE.match(line)
        if not m:
            continue
        name = m.group("name").strip(" -:")
        qty = _to_float(m.group("qty")) or 1.0
        unit = _to_float(m.group("unit"))
        total = _to_float(m.group("total"))
        if not name or unit is None or total is None:
            continue
        items.append(LineItem(name=name, quantity=qty, unit_price=unit, total=total))
    return items


def _guess_merchant(text: str) -> str | None:
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        # Skip lines that are clearly not a name.
        if _MONEY_RE.fullmatch(s):
            continue
        if _REF_RE.search(s) and len(s) < 40:
            continue
        if any(kw in s.upper() for kw in ("RECEIPT", "INVOICE", "QUOTATION", "TEL", "PHONE", "DATE", "TOTAL")):
            continue
        if _PHONE_RE.search(s):
            continue
        # First plausible header line.
        if 3 <= len(s) <= 60:
            return s
    return None


def _classify(text: str) -> DocumentType:
    up = text.upper()
    if "BANK" in up and ("TRANSFER" in up or "PAYMENT" in up or "TRF" in up or "TXN" in up):
        return DocumentType.BANK_SLIP
    if "QUOTATION" in up or "QUOTE" in up or "ESTIMATE" in up:
        return DocumentType.QUOTATION
    if "INVOICE" in up or "TAX INVOICE" in up:
        return DocumentType.INVOICE
    if "RECEIPT" in up or "CASH RECEIPT" in up:
        return DocumentType.RECEIPT
    return DocumentType.UNKNOWN


class RuleBasedExtractor(Extractor):
    """Regex + heuristics extractor.

    It is intentionally simple. The LLM adapter (planned for v0.3) will be
    layered on top for harder cases.
    """

    name = "rules"

    def extract(
        self,
        ocr: OCRResult | str,
        document_type: DocumentType | str | None = None,
    ) -> ExtractionResult:
        text = ocr.text if isinstance(ocr, OCRResult) else ocr
        if not text:
            return ExtractionResult(
                document_type=DocumentType.UNKNOWN,
                raw_ocr_text="",
                confidence=0.0,
                warnings=[Warning(code="empty_input", message="No OCR text provided.")],
                engine=self.name,
            )

        # Pre-normalize Khmer numerals if any.
        if any(ch in text for ch in "០១២៣៤៥៦៧៨៩"):
            text = text.translate(_KHMER_NUMERALS)

        warnings: list[Warning] = []
        if document_type in (None, "", "auto"):
            inferred = _classify(text)
        elif isinstance(document_type, DocumentType):
            inferred = document_type
        else:
            inferred = DocumentType(str(document_type))

        currency = _detect_currency(text)
        date_value = _parse_date(text)
        phones = _detect_phones(text)
        ref_kind, ref_value = _detect_ref(text)
        total_value, total_label = _detect_total_amount(text)
        subtotal = _detect_money_for_keywords(text, _SUBTOTAL_KEYWORDS)
        tax = _detect_money_for_keywords(text, _TAX_KEYWORDS)
        discount = _detect_money_for_keywords(text, _DISCOUNT_KEYWORDS)
        line_items = _detect_line_items(text)
        merchant = _guess_merchant(text)

        # Confidence heuristic: count how many fields we filled.
        filled = sum(
            1
            for v in (date_value, phones, ref_value, total_value, merchant, line_items)
            if v
        )
        confidence = round(min(0.95, 0.45 + 0.08 * filled), 3)

        if total_value is None:
            warnings.append(Warning(code="total_missing", message="No total amount detected."))
        if not phones:
            warnings.append(Warning(code="phone_missing", message="No phone number detected."))
        if date_value is None:
            warnings.append(Warning(code="date_missing", message="No date detected."))
        if merchant is None:
            warnings.append(Warning(code="merchant_missing", message="No merchant name detected."))
        if not line_items:
            warnings.append(
                Warning(
                    code="line_items_missing",
                    message="No structured line items detected.",
                )
            )

        if inferred is DocumentType.BANK_SLIP:
            doc: Receipt | Invoice | Quotation | BankSlip = BankSlip(
                currency=currency,
                amount=total_value,
                date=date_value,
                phone_numbers=phones,
                reference=ref_value if ref_kind == "reference" else None,
            )
        elif inferred is DocumentType.INVOICE:
            doc = Invoice(
                merchant_name=merchant,
                date=date_value,
                currency=currency,
                subtotal=subtotal,
                tax=tax,
                discount=discount,
                total=total_value,
                phone_numbers=phones,
                invoice_number=ref_value if ref_kind == "invoice_number" else None,
                line_items=line_items,
            )
        elif inferred is DocumentType.QUOTATION:
            doc = Quotation(
                merchant_name=merchant,
                date=date_value,
                currency=currency,
                subtotal=subtotal,
                tax=tax,
                discount=discount,
                total=total_value,
                phone_numbers=phones,
                quotation_number=ref_value if ref_kind == "quotation_number" else None,
                line_items=line_items,
            )
        else:
            # Default: receipt (most common low-formality doc).
            doc = Receipt(
                merchant_name=merchant,
                date=date_value,
                currency=currency,
                subtotal=subtotal,
                tax=tax,
                discount=discount,
                total=total_value,
                phone_numbers=phones,
                invoice_number=ref_value if ref_kind in ("invoice_number", "receipt_number") else None,
                line_items=line_items,
            )
            if inferred is DocumentType.UNKNOWN:
                inferred = DocumentType.RECEIPT
                warnings.append(
                    Warning(
                        code="document_type_inferred",
                        message="Document type not detected; defaulted to receipt.",
                    )
                )

        return ExtractionResult(
            document_type=inferred,
            document=doc,
            raw_ocr_text=text,
            confidence=confidence,
            warnings=warnings,
            engine=self.name,
        )
