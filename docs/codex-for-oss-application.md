# Codex for Open Source — Application draft

> This page is a working draft for a future **Codex for Open Source**
> application. It is **not** a submission — it is the kind of artefact a
> serious OSS project keeps in `docs/` so a future application can lift
> text verbatim.

## 1. Why this repository matters

KhmerDocKit is **open infrastructure for low-resource-language document
understanding**, starting with Cambodia. It fills a real gap:

* **Coverage gap.** Mainstream document-AI services (Textract, Document
  AI, Azure Form Recognizer, veryfi.com) are trained on US / EU data.
  They misread Khmer numerals, Cambodian phone formats, and bilingual
  receipts.
* **Vendor lock-in.** Closed SaaS makes it expensive to build a
  Cambodian POS, fintech, or govtech product on top. KhmerDocKit is MIT
  licensed; the API and schemas are stable contracts the community owns.
* **Data sovereignty.** Cambodia-focused businesses should not have to
  ship every receipt overseas to get structured data out of it. The
  library runs offline, the API can self-host, the Docker image is
  reproducible.

It is also a **template** other low-resource-language communities can
fork: the OCR / extractor / validator boundaries are clean, the synthetic
data generator is a small standalone file, and the docs explicitly call
out where to plug in your own scripts.

## 2. Why it benefits the Cambodia tech industry

Concrete audiences:

* **POS vendors** integrating with the General Department of Taxation
  e-invoicing mandate (planned for 2026–2027) need reliable line-item
  extraction.
* **Fintechs** (Wing, ABA, Pi Pay, …) want to automate reconciliation
  from bank-transfer screenshots.
* **Accountants & SMEs** who currently type receipts into spreadsheets
  by hand.
* **Govtech builders** — NCDD, GDT, and ministries produce
  Khmer-language documents that need to flow into a database.

The project is intentionally small and maintainable so a single
maintainer (or two) can keep it going between releases. Synthetic data
keeps the barrier to contribution near zero.

## 3. How Codex / API credits would help maintainers

| Use                                          | Today (no credits) | With credits                        |
| -------------------------------------------- | ------------------ | ----------------------------------- |
| Triage & draft issue responses               | Manual, slow       | Faster first reply, better docs     |
| Translate docs English → Khmer               | None               | Real Khmer README + `docs/khmer.md` |
| Add OCR adapters (EasyOCR, DocTR)            | Infeasible locally | Prototype + benchmark in days       |
| Expand the benchmark dataset                 | 20 samples         | 100+ samples across more layouts    |
| Reproduce & debug PaddleOCR regressions      | Slow               | Faster turnaround, more variants    |
| Self-hosting guides                          | Stub               | Real, tested step-by-step recipes   |
| Code review of community PRs                 | Manual             | Higher signal-to-noise              |

API credits specifically let the maintainer run a *private* LLM
extractor benchmark to compare v0.3 candidate prompts before merging —
something that is not feasible on a personal budget.

## 4. Maintainer workflows that need AI assistance

* **Triage new issues.** Most incoming issues are "my receipt didn't
  parse correctly" with a photo attached. An assistant that can ask
  follow-up questions, propose a synthetic analogue, and tag the
  issue would be a multiplier.
* **Write / update tests.** A regression test is a few lines but the
  mental overhead of deciding what the expected output *should* be
  takes longer than the code.
* **Generate the next template.** The synthetic generator is
  template-driven; expanding it is a matter of describing a new layout
  in natural language and reviewing the generated code.
* **Khmer-language translation.** Native-fluent review is still on
  humans; the assistant can produce a first draft from the English
  sources.
* **Release notes.** Pulling the diff between `git log v0.X-1..main`
  and writing a CHANGELOG entry is exactly the kind of structured
  writing an LLM is good at.

## 5. Milestones that will be accelerated by Codex access

* **v0.2 — better Khmer dates & line items.** Estimated 2× faster with
  Codex: the maintainer can run batch experiments on the synthetic
  dataset to pick the best regex, and write the regression test
  alongside the fix.
* **v0.3 — LLM extraction adapter.** Estimated 3–4× faster: most of
  the time is in prompt iteration and benchmarking against the v0.1
  rules baseline, both of which Codex can do overnight.
* **v0.4 — community templates + Khmer docs.** Estimated 2× faster:
  translating + writing template descriptors in parallel.
* **v1.0 — stable schemas, eval suite.** Estimated 2× faster: the
  eval suite is mostly authoring test cases; a Codex assistant
  reduces the per-case cost to minutes.

## 6. Responsible AI / data handling

KhmerDocKit is built with the assumption that *real user documents
never enter the repo*:

* The `datasets/synthetic/` generator is the only source of
  in-repo documents. The generator is deterministic, uses fictional
  merchant names, and is documented in `datasets/synthetic/README.md`.
* The synthetic generator never produces real phone numbers, real
  account numbers, or any other private-looking sequence.
* The `SECURITY.md` policy and the `CONTRIBUTING.md` both call this
  out and link to `conduct@khmerdockit.local` for takedown requests.
* The API has a hard size limit and an allow-list of MIME types. It
  writes uploads to a `TemporaryDirectory` that is cleaned up after
  each request.
* The maintainer will not use real user documents as benchmark
  inputs without explicit, informed consent and an anonymisation
  pipeline. (No such documents exist at v0.1.)

## 7. What success looks like

* 50+ GitHub stars by v0.3.
* 5+ external contributors (docs, templates, OCR adapters).
* A Khmer-language README and at least 3 translated docs.
* A reproducible public benchmark with the v0.1 numbers as a baseline.
* At least one POS vendor or fintech in Cambodia actively using the
  library in production.

If you are reading this and would like to help with any of the above,
see [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
