# Suggested GitHub issues (next milestones)

> **Not a real file in the repo** — this is a checklist of issues the
> maintainer should file right after tagging v0.1.0. Use it as a starting
> point; titles, labels, and acceptance criteria are all editable.

## v0.2 — Better Khmer dates & line items

* [ ] **[v0.2] Add Buddhist Era / `ថ្ងៃទី…` Khmer date parsing** (label: `enhancement`, `khmer`)
  * Parse `ថ្ងៃទី២ ខែមិថុនា ឆ្នាំ២៥៦៩` to ISO `2026-06-02`.
  * Add fixtures in `datasets/synthetic/` and a unit test.

* [ ] **[v0.2] Improve line-item extraction (multi-line items, wrapping)**
  * Handle a description that wraps across two lines.
  * Reconcile `qty × unit_price` with the document total.

* [ ] **[v0.2] Add PDF support** (text layer first, OCR fallback)
  * Use `pypdf` for text layer; fall back to OCR for image-only PDFs.

* [ ] **[v0.2] Expand synthetic dataset to 50+ samples**
  * Add handwritten-style and low-light variations.

* [ ] **[v0.2] Benchmark scoring for list-valued fields** (label: `benchmark`)
  * Replace the comma-join norm with element-wise matching for `line_items`.

## v0.3 — LLM extraction

* [ ] **[v0.3] LLM extraction adapter (OpenAI-compatible)** (label: `enhancement`, `llm`)
  * See `docs/llm_extractors.md` for the design.
  * Pluggable via `KHMERDOC_EXTRACTOR_BACKEND=llm`.

* [ ] **[v0.3] Confidence blending (rules × LLM)**
  * Weight per-field agreement; expose `confidence` and per-field confidences.

* [ ] **[v0.3] Human-correction UI in the web demo**
  * Edit a field, see the JSON re-render, optional "save as training pair".

## v0.4 — Ecosystem

* [ ] **[v0.4] Plugin / template registry** (label: `enhancement`, `plugins`)
  * Community-submitted templates via `importlib.metadata.entry_points`.

* [ ] **[v0.4] Khmer-language documentation**
  * Translate `README.md`, `quickstart.md`, `cambodia_validation_rules.md`.

* [ ] **[v0.4] Public benchmark leaderboard**
  * Per-PR benchmark numbers, rendered to a `gh-pages` site.

## v1.0 — Stable

* [ ] **[v1.0] Stable schemas (semver-locked)**
  * `pydantic` model versions, deprecation policy.

* [ ] **[v1.0] Production Docker images (multi-arch, signed)**
  * Build, sign, and publish via GitHub Actions.

* [ ] **[v1.0] Eval suite with reproducible numbers**
  * Pin the exact commit, Python version, and dataset checksum.

## Housekeeping (any time)

* [ ] **Triage `good first issue` candidates** — small docs typos, simple
  CLI flags, additional sample docs.
* [ ] **Add a CODEOWNERS file** once maintainer count > 1.
* [ ] **Set up Renovate / Dependabot** to keep `paddleocr`, `fastapi`,
  `next` versions current.

## Bug-bash backlog (v0.1 follow-ups)

* [ ] Benchmark list-comparison gives 0 for `line_items` — fix the scorer
      (see `v0.2 — benchmark scoring` above).
* [ ] Rule-based extractor doesn't yet read `bank_name` / `sender_name` /
      `receiver_account` from bank slips. Track under v0.2.
* [ ] `phone_numbers` benchmark recall is 0.75 because bank-slip samples
      have `phone_numbers: []` in the expected JSON but the field is
      still scored. Adjust the scorer to skip empty-expected lists.

## How to use this file

1. Pick an item.
2. File the corresponding GitHub issue (copy the title, expand the
   description).
3. Close this entry by replacing the checkbox with a link to the issue.
4. Move the issue through `needs-triage → ready → in-progress → done`
   as work progresses.
