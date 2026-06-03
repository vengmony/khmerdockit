# curl examples

The API server speaks HTTP. Below are minimal curl invocations that work
against a server started with `make api`.

## Health

```bash
curl -s http://localhost:8000/health | jq
```

## Parse (auto-detect)

```bash
curl -s -X POST http://localhost:8000/v1/parse \
  -F "file=@datasets/synthetic/receipts/receipt-001/document.txt" \
  | jq
```

## Parse (forced type)

```bash
curl -s -X POST http://localhost:8000/v1/parse \
  -F "file=@datasets/synthetic/invoices/invoice-001/document.txt" \
  -F "document_type=invoice" \
  | jq
```

## OCR only

```bash
curl -s -X POST http://localhost:8000/v1/ocr \
  -F "file=@datasets/synthetic/bank_slips/bankslip-001/document.txt" \
  | jq
```

## Schemas

```bash
# All
curl -s http://localhost:8000/v1/schemas | jq '.schemas[].name'

# Single
curl -s http://localhost:8000/v1/schemas/Receipt | jq
```
