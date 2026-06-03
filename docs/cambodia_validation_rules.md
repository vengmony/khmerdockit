# Cambodia validation rules

KhmerDocKit implements a set of Cambodia-specific validation rules on top
of the generic Pydantic schemas. The rules never **reject** a document —
they add `Warning` objects to the extraction result so the caller can
decide what to do.

## Phone numbers

**Accepted formats**

* `0XXXXXXXX` — local mobile, 9 or 10 digits starting with `0` (the
  second digit is `1`–`9`).
* `0XXX XXX XXX` — Phnom Penh landline (3-3-3 grouping is allowed).
* `+855XXXXXXXX` / `855XXXXXXXX` — international form.

**Warnings**

| Code           | Triggered when                                  |
| -------------- | ----------------------------------------------- |
| `phone_empty`  | The phone string is empty.                      |
| `phone_format` | The phone does not match any of the formats.    |

The extractor normalises phones by stripping spaces and dashes; the
validator only runs on the normalised value.

## Currency

**Accepted inputs** (all normalised to `USD` or `KHR`):

* `USD`, `usd`, `$`, `US$` → `"USD"`
* `KHR`, `khr`, `៛`, `RIEL`, `riel` → `"KHR"`

**Warnings**

| Code                | Triggered when                                |
| ------------------- | --------------------------------------------- |
| `currency_missing`  | `currency` is `None`.                         |
| `currency_unusual`  | Currency is neither USD nor KHR.              |

## Dates

**Parsed formats**

* `YYYY-MM-DD` (ISO 8601)
* `DD/MM/YYYY`, `DD-MM-YYYY`, `DD.MM.YYYY` — day-first (Cambodian)
* `02 Jun 2026` — English month name, any case
* Khmer numerals (`០១២៣…`) — auto-normalised before parsing

**Warnings**

| Code              | Triggered when                                            |
| ----------------- | --------------------------------------------------------- |
| `date_far_past`   | Date is more than 10 years in the past.                   |
| `date_far_future` | Date is more than 1 year in the future.                   |

The threshold is configurable via `validate_date(value, max_past_years=…)`.

## Line-item totals

For every line on a receipt / invoice / quotation, the validator checks
that `quantity × unit_price ≈ total` (within 0.02 to absorb floating-point
noise).

| Code                          | Triggered when                       |
| ----------------------------- | ------------------------------------ |
| `line_item_total_mismatch`    | `qty × unit != total` (by more than 0.02) |

## Document type detection

If the caller did not pass a `document_type` hint (or passed `"auto"`),
the rule-based extractor classifies the document by keyword:

* "BANK" + ("TRANSFER" / "PAYMENT" / "TRF" / "TXN") → `bank_slip`
* "QUOTATION" / "QUOTE" / "ESTIMATE" → `quotation`
* "INVOICE" / "TAX INVOICE" → `invoice`
* "RECEIPT" / "CASH RECEIPT" → `receipt`
* otherwise → `receipt` (with `document_type_inferred` warning)

## Reference number detection

Recognised patterns:

* `INV-001`, `Invoice No: INV-001`, `No: INV-001`
* `RCP-704`, `Receipt No: RCP-704`
* `QUOT-001`, `Quote No: QUOT-001`
* `TRF123456`, `TXN123456`
* `REF-…` (generic)

The detector picks the best match (longest numeric, plus an explicit
keyword promotes the result to the right field). The fallback
`reference` field on `BankSlip` holds the raw string otherwise.

## What we deliberately don't do (yet)

* **Cambodian tax ID validation.** VAT/TIN formats are not yet modelled;
  v0.2 will add a `tax_id` field and a validator stub.
* **Address parsing.** Free-form addresses are common on receipts; v0.2
  will start with a simple "city, province" extractor.
* **Khmer-language date parsing.** Buddhist Era years and `ថ្ងៃទី…` forms
  are planned for v0.2.
