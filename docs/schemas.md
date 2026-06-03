# JSON Schemas

KhmerDocKit exposes its typed documents as Pydantic v2 models. The JSON
schemas are served at runtime by the API (`GET /v1/schemas` /
`GET /v1/schemas/{name}`) and can also be generated offline.

## Document types

| Model             | Used for                                              |
| ----------------- | ----------------------------------------------------- |
| `Receipt`         | Point-of-sale receipts                                |
| `Invoice`         | Tax / commercial invoices                             |
| `Quotation`       | Price quotes, estimates                               |
| `BankSlip`        | Bank transfer confirmations, payment proofs           |
| `LineItem`        | A single line on a receipt / invoice / quotation      |
| `ExtractionResult`| The wrapper around a typed document + diagnostics     |

## Common fields

All money-bearing documents share a `_MoneyMixin` base that contributes:

* `currency` — `"USD"`, `"KHR"`, or any ISO-4217 string. Glyphs (`$`, `៛`)
  are normalised at the API boundary.
* `subtotal`, `discount`, `tax`, `total` — all `float | null`, all
  non-negative.

## Currency normalisation

The `currency` field accepts the following inputs and normalises them:

| Input       | Stored as |
| ----------- | --------- |
| `"USD"`     | `"USD"`   |
| `"usd"`     | `"USD"`   |
| `"$"`       | `"USD"`   |
| `"US$"`     | `"USD"`   |
| `"KHR"`     | `"KHR"`   |
| `"khr"`     | `"KHR"`   |
| `"៛"`        | `"KHR"`   |
| `"RIEL"`    | `"KHR"`   |

Anything else is kept as-is and a `currency_unusual` warning is added by
`validate_extraction()`.

## Date handling

Dates are stored as ISO-8601 (`YYYY-MM-DD`). The rule-based extractor
parses:

* `2026-06-02`
* `02/06/2026`, `02-06-2026`, `02.06.2026` (Cambodian day-first convention)
* `02 Jun 2026` (English month name, any case)
* Khmer numerals (`២០២៦-០៦-០១`) — automatically normalised before parsing.

Two-digit years are interpreted as 20YY.

## Phone numbers

Stored as a list of normalised strings (digits only, with the leading `0` or
`+855`). Validated against:

* Local: `0XXXXXXXX` (mobile) or `0XXX XXX XXX` (Phnom Penh landline).
* International: `+855XXXXXXXX` or `855XXXXXXXX`.

Anything else triggers a `phone_format` warning.

## Line items

```json
{
  "name": "Classic Clog",
  "quantity": 1,
  "unit_price": 12.5,
  "total": 12.5
}
```

The Cambodia validator checks that `quantity * unit_price ≈ total`
(within 0.02) and emits `line_item_total_mismatch` otherwise.

## Extraction result wrapper

```json
{
  "document_type": "receipt | invoice | quotation | bank_slip | unknown",
  "document": { ... },            // one of the typed models above, or null
  "raw_ocr_text": "...",
  "confidence": 0.0,
  "warnings": [ { "code": "...", "message": "...", "field": "..." } ],
  "engine": "rules"
}
```

`to_jsonable()` flattens the typed document's fields into the top-level
dict, matching the shape of the public example in the project spec.

## Generating schemas offline

```bash
khmerdoc list-schemas                # print all schemas to stdout
curl -s http://localhost:8000/v1/schemas/Receipt | jq
```
