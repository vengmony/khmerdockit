# Contributing on-ramp

> **First-time contributor?** Start here. This page points you at the
> easiest 1-hour tasks, the conventions you need to follow, and the
> people to ask.

## Pick something

The **fastest** way to land your first PR:

* **[`good first issue`][gfi]** — small, scoped, with a hint in the
  description.
* **Fix a typo / broken link** — 30 seconds of work, gets you used to
  the PR flow.
* **Add a synthetic document template** — see the
  [`document template request`][dtr] issue template and
  [`docs/synthetic.md`](./synthetic.md).

The **highest-leverage** things to work on right now:

* **OCR adapter for EasyOCR / DocTR / Surya** — see
  [`docs/ocr_adapters.md`](./ocr_adapters.md) and an existing adapter
  like `khmerdoc/ocr/tesseract.py`.
* **Cambodia validation rule** — see
  [`docs/cambodia_validation_rules.md`](./cambodia_validation_rules.md).
* **Khmer (ភាសាខ្មែរ) translation** — `docs/khmer.md` is a stub.
* **Bank-slip extractor** — the v0.1.0 rule-based extractor handles
  date / amount / reference on bank slips but doesn't yet read
  `bank_name` / `sender_name` / `receiver_account`. v0.2 work.

## What you need

* **Python 3.11+** (the project uses `from __future__ import annotations`
  and PEP 604 unions).
* **Git** and a GitHub account.
* **A working OCR backend is optional.** The default `mock` backend
  makes the test suite and the Gradio demo work with no system
  dependencies.

## Set up locally (5 minutes)

```bash
git clone https://github.com/vengmony/khmerdockit
cd khmerdockit

pip install -e packages/khmerdoc-core[dev]
pip install -e packages/khmerdoc-api[dev]
# (one-time, only if you'll touch the web demo)
make install-web

make test        # 57 tests, should all pass
make lint        # ruff
```

## Read the project context

Before you start, read:

* [`README.md`](../../README.md) — 5-minute orientation.
* [`AGENTS.md`](../../AGENTS.md) — the project's instructions to AI
  coding agents. Also useful for humans; covers do's, don'ts, and
  common tasks.
* [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — the full contributor
  workflow.
* [`MAINTAINERS.md`](../../MAINTAINERS.md) — who reviews what.

## The PR lifecycle

1. **Open an issue first** for non-trivial changes (anything that
   touches the public schema, the `/v1/...` endpoints, or the synthetic
   data layout). Use one of the issue templates in
   `.github/ISSUE_TEMPLATE/`.
2. **Branch from `main`.** Use a descriptive name:
   `feat/khmer-date-parser`, `fix/ocr-paddle-windows`, etc.
3. **Make focused commits** with messages like:
   ```
   feat(schemas): add quotation_number to Quotation
   fix(extractor): correct phone regex for 10-digit Cambodian numbers
   docs: add EasyOCR adapter section
   ```
4. **Run `make test && make lint`** before pushing.
5. **Open the PR** using `.github/PULL_REQUEST_TEMPLATE.md`. Mention
   the issue it closes (`Fixes #123`).
6. **Wait for review.** The Codex-powered PR review workflow will
   post an automated check; a human maintainer will follow up within a
   few business days. Be patient — this is a small project.

## Asking for help

* **On the PR itself** is usually the best place. Future contributors
  can read the thread.
* **GitHub Discussions** for design questions, "is this worth doing?",
  roadmap debates.
* **Discord / Matrix** — TBD. The maintainer will spin one up when the
  contributor count crosses three.

## Code review expectations

* Be specific. "This is wrong" is unhelpful; "`x` should be
  `Optional[x]` because the rule-based extractor returns `None` when
  the document doesn't have a buyer" is helpful.
* Be kind. Read the [Code of Conduct](../../CODE_OF_CONDUCT.md).
* Reviewers will try to merge within a week of a green PR. If we're
  slow, ping `@vengmony` on the PR.

## Recognition

Contributors are added to the credits of the next release. Long-term
contributors are nominated as co-maintainers per
[`MAINTAINERS.md`](../../MAINTAINERS.md).

Thanks for making KhmerDocKit better. 🙏

[gfi]: https://github.com/vengmony/khmerdockit/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22
[dtr]: https://github.com/vengmony/khmerdockit/issues/new?template=document_template_request.yml
