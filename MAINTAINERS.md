# Maintainers

**KhmerDocKit** is maintained by a small group of volunteers led by the
founder. The project is **founder-led and community-driven** — anyone is
welcome to send a PR, and significant decisions happen on the GitHub
issues / discussions.

## Current maintainers

| Handle          | Role                                | Focus area                          |
| --------------- | ----------------------------------- | ----------------------------------- |
| @founder        | Core creator & lead maintainer      | Architecture, releases, governance  |

> Replace the handle above with your real GitHub handle before tagging
> v0.1.0. (If you'd rather not single-name yourself yet, leave the
> table as-is and add co-maintainers as they join.)

## Becoming a co-maintainer

We promote active contributors to co-maintainers based on:

1. **Sustained, high-quality PRs** (≥5 merged, well-tested, on-spec).
2. **Triage activity** in issues and discussions.
3. **Domain expertise** — OCR, Khmer NLP, POS / fintech, govtech, etc.
4. **Community trust** — follows the [Code of Conduct](./CODE_OF_CONDUCT.md).

The current maintainers will propose a vote in a public discussion before
adding a new maintainer. Co-maintainers get:

* Triage / label / merge rights on the repo.
* Their handle in the table above.
* A say in the public roadmap (see [ROADMAP.md](./ROADMAP.md)).

## Decision-making

* **Day-to-day** (typo fixes, doc tweaks, small bug fixes): any
  maintainer can merge once CI is green.
* **Schema / API changes** (anything that touches
  `packages/khmerdoc-core/src/khmerdoc/schemas.py` or the public
  `/v1/...` endpoints): requires an accepted GitHub discussion / issue
  describing the change and at least one approving review.
* **Releases** (cutting a tag, publishing Docker images): the founder
  has the final call, with a 3-day comment window in a `Release: vX.Y.Z`
  discussion.

## Communications

* **GitHub issues** — bug reports, feature requests, design questions.
* **GitHub discussions** — open-ended questions, "is this worth doing?",
  roadmap debates.
* **Security reports** — see [SECURITY.md](./SECURITY.md) for the private
  channel.

We do not maintain a separate chat for v0.1. When the maintainer count
crosses three we will spin up a Discord / Matrix room and link it from
here.
