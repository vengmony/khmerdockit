# Benchmark

The benchmark scores a single extractor against a labelled synthetic
dataset. v0.1 ships a baseline over 20 deterministic samples; later
versions will add a leaderboard and CI integration.

## What it measures

For each (sample, field) pair, the benchmark computes:

* **precision** — of the fields the extractor *produced*, how many match the
  ground truth? (`(correct + 0.5 × partial) / produced`)
* **recall** — of the fields the ground truth *expects*, how many did the
  extractor produce? (`(correct + 0.5 × partial) / expected`)
* **F1** — harmonic mean of precision and recall.

A field is `correct` if its normalised value equals the expected value,
`partial` if the values overlap (reserved for v0.2 list matching), and
`missing`/`wrong` otherwise.

## Running it

```bash
# Default: 5 samples per type, seed=42
make synth
khmerdoc benchmark datasets/synthetic

# Custom
python -m khmerdoc.synthetic.generate --out /tmp/synth --per-type 20
khmerdoc benchmark /tmp/synth
```

## Sample output

```
| Field            |    P |    R |   F1 | OK | Miss | Wrong |
| amount           | 1.00 | 1.00 | 1.00 |  5 |    0 |     0 |
| currency         | 1.00 | 1.00 | 1.00 | 20 |    0 |     0 |
| date             | 1.00 | 1.00 | 1.00 | 20 |    0 |     0 |
| document_type    | 1.00 | 1.00 | 1.00 | 20 |    0 |     0 |
| merchant_name    | 1.00 | 1.00 | 1.00 | 15 |    0 |     0 |
| total            | 1.00 | 1.00 | 1.00 | 15 |    0 |     0 |
| ...              |      |      |      |    |      |       |
```

The first column of numbers is *good* (close to 1.0); zeros in the
`bank_name` / `sender_name` / `receiver_name` columns are *expected* in
v0.1 — the rule-based extractor does not yet parse those fields, and the
goal of v0.1 is honest reporting of what works and what doesn't.

## What it does NOT do

* It does not test OCR quality. The benchmark reads the `.txt` files
  directly, so PaddleOCR / Tesseract regressions are out of scope.
* It does not score warning quality. The `warnings` field is reported but
  not yet compared against an expected set.
* It does not compare extractors. v0.4 will add `--extractor llm` style
  comparison runs.

## Roadmap

* **v0.2** — proper list matching for `line_items`; field-level confidence
  calibration; per-document-type sub-scores.
* **v0.4** — public leaderboard generated from PR benchmark runs.
* **v1.0** — reproducibility script that pins the exact commit, Python
  version, and dataset checksum used for the published numbers.
