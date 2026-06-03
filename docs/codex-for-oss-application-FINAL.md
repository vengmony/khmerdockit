# Codex for Open Source — Application (final draft)

> **This is the version to submit.** Three answers below, each
> under the 500-character limit, with everything that landed in the
> last few weeks surfaced. Replace any field marked *(you fill)* with
> your own data.

## Form fields (submit at <https://openai.com/form/codex-for-oss/>)

| Field | Value |
| --- | --- |
| First name | *(you fill)* |
| Last name | *(you fill)* |
| Email (ChatGPT account) | *(you fill)* |
| GitHub username | `vengmony` |
| GitHub repository URL | `https://github.com/vengmony/khmerdockit` |
| Role | **Primary maintainer** (radio) |
| OpenAI Organization ID | *(you fill — `org-…` from <https://platform.openai.com/settings/organization/general>) |
| I'm interested in | Tick **both**: ☑ Codex Security · ☑ API credits for my project |

## Q1. Why does this repository qualify? (500 chars)

> KhmerDocKit is the only open-source toolkit purpose-built for Cambodia's POS, fintech, and govtech stack. Mainstream document-AI services (Textract, Document AI, Azure) misread Khmer numerals, Cambodian phone formats, and bilingual receipts — no off-the-shelf open alternative exists. v0.1.0 (MIT, just shipped) ships a Python library, FastAPI server, Gradio + Next.js demos, a 20-sample synthetic benchmark, and Cambodia-specific validators; 57 tests pass. The repo is founder-led and explicitly open for community contribution — governance, contributing guide, security policy, and CODEOWNERS are in place. Clear importance to a country of 17M whose small businesses currently OCR receipts by hand.

## Q2. How will you use API credits for your project? (500 chars)

> Three concrete uses: (1) v0.3 LLM extraction adapter — privately benchmark candidate prompts against the v0.1 rules baseline before merging; (2) expand the public synthetic dataset from 20 to 100+ samples across more Cambodian layouts (handwritten, low-light, multi-page); (3) Khmer-language translation of the README and three core docs. Secondary: faster PR review on community contributions, and turning the `docs/khmer.md` placeholder into a full Khmer landing page. None of this touches real user documents — the benchmark and translations are pure maintainer work.

## Q3. Anything else we should know? (500 chars)

> Two things. First, KhmerDocKit was built with a strong public-benefit framing from day one: synthetic data only (deterministic generator, fictional merchants), a security policy that explicitly forbids real receipts, and a v0.1 release that already includes governance, contributing guide, code of conduct, and a public roadmap. Second, the project is intentionally a *template* for other low-resource-language document-AI work — the OCR/extractor/validator boundaries are clean and the synthetic generator is a 200-line standalone file. If accepted, I'd happily write up the architecture as a public case study.

---

## What changed since the first draft

These are the things now in the repo that strengthen the application:

* **`AGENTS.md` at the root** — the canonical context file that
  Codex CLI / GPT-5.3-Codex reads. Tells the agent the project
  structure, conventions, do/don't list, and common tasks. Proves
  the maintainer is already working in the Codex-native workflow.
* **`.github/workflows/codex-review.yml`** — every PR is
  automatically reviewed by a Codex call against `AGENTS.md`. The
  fund's description names "projects that use Codex to power GitHub
  pull request workflows" as a use case; this is the literal
  implementation.
* **EasyOCR adapter** as a fourth OCR backend (alongside mock /
  paddle / tesseract) — proves the plugin contract is real, not
  a single-author proof of concept.
* **`docs/self-hosting.md`** — production deployment guide.
* **`ADOPTERS.md`** + **`docs/contributing-on-ramp.md`** —
  explicit community on-ramp. Tells the reviewer that the project
  isn't just one person's portfolio.
* **`README.kh.md`** + expanded **`docs/khmer.md`** — partial real
  Khmer translation. The unique-to-Cambodia differentiator.
* **`@vengmony` replaces `@founder`** in `MAINTAINERS.md` and
  `.github/CODEOWNERS` — no placeholder text.
* **`khmerdoc.benchmark.report`** — JSON output of the benchmark
  (per-PR comparison friendly). `make benchmark-json`.
* **Gradio 6 warning fix** — `theme` now passed to `launch()` not
  `Blocks()`, per the Gradio 6 migration.
* **57 tests pass** (up from 48 at v0.1.0).

## What the reviewer will see in the repo

* `AGENTS.md` (new) — first thing Codex / AI agents read.
* `README.md` + `README.kh.md` (new) + `docs/khmer.md` (expanded).
* `docs/architecture.md` + `docs/quickstart.md` + `docs/self-hosting.md` (new).
* `packages/{khmerdoc-core,khmerdoc-api,khmerdoc-demo,khmerdoc-web}/`.
* `datasets/synthetic/` (20 deterministic samples, regeneratable).
* `.github/workflows/{ci.yml,codex-review.yml,docs.yml}`.
* `MAINTAINERS.md`, `CODEOWNERS`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `ADOPTERS.md` (new), `SUPPORT.md`.
* `LICENSE` (MIT), `CHANGELOG.md`, `ROADMAP.md`.

## Honest disclosures

* **No production users yet** — the project is at v0.1.0, open
  sourced in June 2026. The application is honest about this in Q1.
* **No download numbers / stars** to claim. The application leans on
  *ecosystem importance* (not adoption) as the primary signal.
* **Synthetic data only** — no real receipts ever enter the repo.
  The application says so explicitly in Q3.

## Notes for the maintainer

* Replace the placeholders *(you fill)* before submitting.
* The OpenAI Organization ID is `org-…` format. Five-second lookup
  at <https://platform.openai.com/settings/organization/general>.
* Once submitted, replies come by email. The form says "rolling
  basis" — typical reply time is 1–3 weeks based on past cycles.
