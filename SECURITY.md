# Security policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Email **security@khmerdockit.local** with a clear description of the issue,
the affected component, and a reproducer. We aim to acknowledge within 3
business days.

If the report includes a document you believe is sensitive, please also
confirm whether the file may be retained for testing, or whether you would
prefer it be deleted after triage.

## What we care about

* **Document uploads** — the API server enforces a max upload size and an
  allow-list of MIME types. If you find a way to bypass these, please report.
* **Path traversal** — uploads are written into a temporary directory and
  never used as paths in user-controlled locations.
* **Dependency CVEs** — pinned dev dependencies; production installs should
  use a lockfile.
* **Secrets** — `.env` is gitignored; the README / docs only ever show
  example values.

## Data we never want to see in this repo

* Real receipts, invoices, bank statements.
* Real merchant or personal names.
* API keys, OAuth tokens, or `.env` files with real values.
* Synthetic data that mimics a real business too closely (e.g. the actual
  logo, address, or signature of a real shop).

If you accidentally commit any of the above, contact the maintainers and we
will help purge it from history.
