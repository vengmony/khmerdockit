"""Synthetic document generation for tests, demos, and the public benchmark.

The generator is fully deterministic when given a seed. It produces:

  * plain-text ``.txt`` files that simulate OCR output, and
  * matching ``expected.json`` label files used by the benchmark.

No real merchant or personal data is ever used.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

# ---- templates -------------------------------------------------------------

MERCHANTS_EN = [
    "Example Mart",
    "Phnom Penh Coffee",
    "Mekong Minimart",
    "Sisowath Supplies",
    "BKK1 Books",
    "Angkor Mobile Shop",
    "Riverside Restaurant",
    "Central Market Vendor",
]

MERCHANTS_KH = [
    "ហាងឧបត្តិយោគ",
    "ផ្សារធំថ្មី",
    "កាហ្វេភ្នំពេញ",
    "ទីផ្សារមេគង្គ",
]

BUYERS = [
    "Sokha Construction Co., Ltd.",
    "Channa Trading",
    "Rithy Bakery",
    "Mey Mom Cosmetics",
    "Phally Bookshop",
]

ITEM_NAMES = [
    "Classic Clog",
    "Iced Coffee",
    "Rice 5kg",
    "Soap Bar",
    "USB-C Cable 1m",
    "Notebook A5",
    "T-Shirt M",
    "Bottled Water 1.5L",
]

BANKS = [
    "ACLEDA Bank",
    "Wing Bank",
    "Canadia Bank",
    "ABA Bank",
    "Sathapana Bank",
]


@dataclass
class Sample:
    text: str
    expected: dict[str, Any]
    relpath: str


def _fmt_money(value: float, currency: str) -> str:
    if currency == "KHR":
        return f"{value:,.0f} ៛"
    return f"${value:,.2f}"


def _rand_phone(rng: random.Random) -> str:
    prefix = rng.choice(["012", "015", "017", "078", "093"])
    rest = "".join(str(rng.randint(0, 9)) for _ in range(7))
    return f"{prefix}{rest}"


def _rand_invoice_no(rng: random.Random, prefix: str = "INV") -> str:
    return f"{prefix}-{rng.randint(100, 999):03d}"


def _rand_date(rng: random.Random, *, max_ago_days: int = 120) -> date:
    delta = rng.randint(0, max_ago_days)
    return date.today() - timedelta(days=delta)


def _rand_line_items(
    rng: random.Random,
    *,
    currency: str,
    n: int | None = None,
) -> tuple[list[dict[str, Any]], float, float]:
    n = n or rng.randint(1, 4)
    items: list[dict[str, Any]] = []
    subtotal = 0.0
    for _ in range(n):
        name = rng.choice(ITEM_NAMES)
        qty = rng.choice([1, 1, 1, 2, 3])
        if currency == "KHR":
            unit = round(rng.uniform(1_000, 25_000), -2)
        else:
            unit = round(rng.uniform(0.5, 25.0), 2)
        total = round(unit * qty, 2 if currency == "USD" else 0)
        subtotal += total
        items.append(
            {
                "name": name,
                "quantity": qty,
                "unit_price": unit,
                "total": total,
            }
        )
    return items, round(subtotal, 2), round(subtotal, 2)  # tax/discount 0 for MVP


# ---- individual generators ------------------------------------------------


def gen_receipt(rng: random.Random, idx: int) -> Sample:
    merchant = rng.choice(MERCHANTS_EN + MERCHANTS_KH)
    phone = _rand_phone(rng)
    inv_no = _rand_invoice_no(rng, prefix=rng.choice(["RCP", "INV"]))
    d = _rand_date(rng)
    currency = rng.choice(["USD", "USD", "KHR"])  # USD more common
    items, sub, total = _rand_line_items(rng, currency=currency, n=rng.randint(2, 4))

    lines = [
        merchant,
        "RECEIPT",
        f"No: {inv_no}",
        f"Date: {d.isoformat()}",
        f"Tel: {phone}",
        "-" * 24,
    ]
    for it in items:
        lines.append(
            f"{it['name']:<18}{it['quantity']} x {_fmt_money(it['unit_price'], currency)}   "
            f"{_fmt_money(it['total'], currency)}"
        )
    lines += [
        "-" * 24,
        f"SUBTOTAL    {_fmt_money(sub, currency)}",
        f"TOTAL       {_fmt_money(total, currency)}",
        "Thank you!",
    ]
    text = "\n".join(lines)

    expected = {
        "document_type": "receipt",
        "merchant_name": merchant,
        "date": d.isoformat(),
        "currency": currency,
        "subtotal": sub,
        "discount": 0,
        "tax": 0,
        "total": total,
        "phone_numbers": [phone],
        "invoice_number": inv_no,
        "line_items": items,
        "confidence": 0.0,
        "warnings": [],
    }
    return Sample(text=text, expected=expected, relpath=f"receipts/receipt-{idx:03d}")


def gen_invoice(rng: random.Random, idx: int) -> Sample:
    merchant = rng.choice(MERCHANTS_EN)
    buyer = rng.choice(BUYERS)
    phone = _rand_phone(rng)
    inv_no = _rand_invoice_no(rng, prefix="INV")
    d = _rand_date(rng)
    due = d + timedelta(days=rng.choice([7, 14, 30]))
    currency = rng.choice(["USD", "USD", "KHR"])
    items, sub, total = _rand_line_items(rng, currency=currency, n=rng.randint(2, 5))

    lines = [
        merchant,
        "INVOICE",
        f"Invoice No: {inv_no}",
        f"Date: {d.isoformat()}",
        f"Due Date: {due.isoformat()}",
        f"Bill To: {buyer}",
        f"Tel: {phone}",
        "-" * 32,
    ]
    for it in items:
        lines.append(
            f"{it['name']:<20}{it['quantity']:>2} x {_fmt_money(it['unit_price'], currency)}"
            f"  =  {_fmt_money(it['total'], currency)}"
        )
    lines += [
        "-" * 32,
        f"SUBTOTAL    {_fmt_money(sub, currency)}",
        f"TOTAL       {_fmt_money(total, currency)}",
    ]
    text = "\n".join(lines)

    expected = {
        "document_type": "invoice",
        "merchant_name": merchant,
        "buyer_name": buyer,
        "date": d.isoformat(),
        "due_date": due.isoformat(),
        "currency": currency,
        "subtotal": sub,
        "discount": 0,
        "tax": 0,
        "total": total,
        "phone_numbers": [phone],
        "invoice_number": inv_no,
        "line_items": items,
        "confidence": 0.0,
        "warnings": [],
    }
    return Sample(text=text, expected=expected, relpath=f"invoices/invoice-{idx:03d}")


def gen_quotation(rng: random.Random, idx: int) -> Sample:
    merchant = rng.choice(MERCHANTS_EN)
    buyer = rng.choice(BUYERS)
    phone = _rand_phone(rng)
    qno = _rand_invoice_no(rng, prefix="QUOT")
    d = _rand_date(rng)
    valid = d + timedelta(days=rng.choice([7, 14, 30]))
    currency = rng.choice(["USD", "KHR"])
    items, sub, total = _rand_line_items(rng, currency=currency, n=rng.randint(2, 4))

    lines = [
        merchant,
        "QUOTATION",
        f"Quote No: {qno}",
        f"Date: {d.isoformat()}",
        f"Valid Until: {valid.isoformat()}",
        f"Attn: {buyer}",
        f"Tel: {phone}",
        "-" * 32,
    ]
    for it in items:
        lines.append(
            f"{it['name']:<20}{it['quantity']:>2} x {_fmt_money(it['unit_price'], currency)}"
            f"  =  {_fmt_money(it['total'], currency)}"
        )
    lines += [
        "-" * 32,
        f"SUBTOTAL    {_fmt_money(sub, currency)}",
        f"TOTAL       {_fmt_money(total, currency)}",
    ]
    text = "\n".join(lines)
    expected = {
        "document_type": "quotation",
        "merchant_name": merchant,
        "buyer_name": buyer,
        "date": d.isoformat(),
        "valid_until": valid.isoformat(),
        "currency": currency,
        "subtotal": sub,
        "discount": 0,
        "tax": 0,
        "total": total,
        "phone_numbers": [phone],
        "quotation_number": qno,
        "line_items": items,
        "confidence": 0.0,
        "warnings": [],
    }
    return Sample(text=text, expected=expected, relpath=f"quotations/quotation-{idx:03d}")


def gen_bank_slip(rng: random.Random, idx: int) -> Sample:
    bank = rng.choice(BANKS)
    sender = rng.choice(BUYERS)
    receiver = rng.choice(MERCHANTS_EN)
    sender_acc = str(rng.randint(10_000_000, 99_999_999))
    receiver_acc = str(rng.randint(10_000_000, 99_999_999))
    currency = rng.choice(["USD", "KHR"])
    if currency == "KHR":
        amount = round(rng.uniform(10_000, 500_000), -2)
    else:
        amount = round(rng.uniform(5, 500), 2)
    d = _rand_date(rng)
    ref = f"TRF{rng.randint(100000, 999999)}"

    text = "\n".join(
        [
            bank,
            "BANK TRANSFER CONFIRMATION",
            f"Reference: {ref}",
            f"Date: {d.isoformat()}",
            f"From: {sender}  Acc: {sender_acc}",
            f"To:   {receiver}  Acc: {receiver_acc}",
            f"Amount: {_fmt_money(amount, currency)}",
            "Status: SUCCESS",
        ]
    )
    expected = {
        "document_type": "bank_slip",
        "bank_name": bank,
        "sender_name": sender,
        "sender_account": sender_acc,
        "receiver_name": receiver,
        "receiver_account": receiver_acc,
        "amount": amount,
        "currency": currency,
        "date": d.isoformat(),
        "reference": ref,
        "phone_numbers": [],
        "confidence": 0.0,
        "warnings": [],
    }
    return Sample(text=text, expected=expected, relpath=f"bank_slips/bankslip-{idx:03d}")


# ---- public entry point ----------------------------------------------------


GENERATORS = {
    "receipts": gen_receipt,
    "invoices": gen_invoice,
    "quotations": gen_quotation,
    "bank_slips": gen_bank_slip,
}


def generate(out_dir: str | Path, *, seed: int = 42, per_type: int = 5) -> list[Sample]:
    """Generate ``per_type`` samples of each kind into ``out_dir``."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    samples: list[Sample] = []
    for kind, fn in GENERATORS.items():
        kind_dir = out_dir / kind
        kind_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, per_type + 1):
            sample = fn(rng, i)
            sample_dir = kind_dir / sample.relpath.split("/", 1)[1]
            sample_dir.mkdir(parents=True, exist_ok=True)
            (sample_dir / "document.txt").write_text(sample.text, encoding="utf-8")
            (sample_dir / "expected.json").write_text(
                json.dumps(sample.expected, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            samples.append(sample)
    return samples


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the synthetic KhmerDocKit dataset.")
    parser.add_argument("--out", default="datasets/synthetic", help="Output directory.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-type", type=int, default=5)
    args = parser.parse_args(argv)
    samples = generate(args.out, seed=args.seed, per_type=args.per_type)
    print(f"Generated {len(samples)} samples under {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
