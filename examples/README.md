# Examples

Runnable usage examples.

## Python

```bash
# Make sure the package is installed (pip install -e packages/khmerdoc-core)
python examples/parse_receipt.py
python examples/parse_invoice.py
python examples/parse_bank_slip.py
```

Each script uses the **mock** OCR backend by default, so it runs offline
without any system dependencies.

## CLI

```bash
# Use the synthetic samples committed under datasets/synthetic
khmerdoc parse datasets/synthetic/receipts/receipt-001/document.txt --type receipt
khmerdoc parse datasets/synthetic/invoices/invoice-001/document.txt --type invoice
khmerdoc parse datasets/synthetic/bank_slips/bankslip-001/document.txt --type bank_slip

# Or generate fresh samples:
python -m khmerdoc.synthetic.generate --out /tmp/synth --per-type 5
khmerdoc parse /tmp/synth/receipts/receipt-001/document.txt
```

## curl

See [`curl_examples.md`](./curl_examples.md).
