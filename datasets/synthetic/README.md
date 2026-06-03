# Synthetic datasets (deterministic, no real data)

This directory contains **synthetic** documents and their expected JSON
labels, used by tests, the demo, and the public benchmark.

The generator is fully deterministic when given a seed — see
``packages/khmerdoc-core/src/khmedoc/synthetic/generate.py``.

## Layout

```
datasets/synthetic/
  receipts/
    receipt-001/
      document.txt      # what OCR would have produced
      expected.json     # ground-truth labels
  invoices/...
  quotations/...
  bank_slips/...
```

## Regenerate

```bash
make synth                     # uses default seed=42, 5 per type
python -m khmerdoc.synthetic.generate --out datasets/synthetic --per-type 5
```

## What this is NOT

* This is **not** real receipts, real merchants, or real personal data.
* Do not commit real documents here.
* For real-world evaluation, build a separate, anonymised test set
  (out of scope for v0.1).
