"""Codex-powered PR review for the KhmerDocKit repository.

Designed to be run from a GitHub Actions workflow. Reads the diff of the
target PR, asks an OpenAI model to review it against the project's
AGENTS.md conventions, and prints a Markdown summary that the workflow
then posts as a PR comment.

This script is intentionally minimal and offline-friendly: it does not
require the ``openai`` SDK if the secret isn't set (the workflow will
skip the step). When the secret IS set, the SDK is installed and used.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
PROJECT_CONTEXT = (
    "KhmerDocKit is an open-source, MIT-licensed toolkit for extracting "
    "structured data from Khmer / English business documents (receipts, "
    "invoices, quotations, bank transfer slips). Monorepo with three "
    "Python packages (khmerdoc-core, khmerdoc-api, khmerdoc-demo) plus a "
    "Next.js demo. Synthetic data only. Pydantic v2, FastAPI, Gradio, "
    "Next.js 14. Python 3.11+. Ruff + mypy + pytest. \n\n"
    "Read AGENTS.md for full project context, code conventions, and the "
    "do/don't list."
)


def _http_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_pr_diff(repo: str, pr_number: int, token: str | None) -> str:
    """Fetch the unified diff for the PR via the GitHub REST API."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff", "User-Agent": "khmerdoc-codex-bot"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _http_text(url, headers)


def _http_text(url: str, headers: dict[str, str]) -> str:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_pr_meta(repo: str, pr_number: int, token: str | None) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "khmerdoc-codex-bot"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _http_json(url, headers)


def call_openai(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 1500) -> str:
    """Call the OpenAI Chat Completions API over HTTPS. Returns the model text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a code review assistant for the open-source "
                    "KhmerDocKit project. You are reviewing a GitHub pull "
                    "request. Produce a concise Markdown review that "
                    "highlights (1) blockers, (2) suggestions, and (3) "
                    "nits. Be specific (file:line) and brief. If there is "
                    "nothing significant, say so."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "khmerdoc-codex-bot/0.1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI API error: {e.code} {e.reason}") from e
    return data["choices"][0]["message"]["content"].strip()


def build_prompt(pr_title: str, pr_body: str, diff: str) -> str:
    """Compose the user prompt from the PR metadata and diff."""
    agents_excerpt = AGENTS_MD.read_text(encoding="utf-8") if AGENTS_MD.exists() else ""
    # Trim AGENTS.md to keep the prompt manageable.
    if len(agents_excerpt) > 6000:
        agents_excerpt = agents_excerpt[:6000] + "\n... (truncated)"
    return (
        f"{PROJECT_CONTEXT}\n\n"
        f"## Project conventions (excerpt from AGENTS.md)\n\n"
        f"{agents_excerpt}\n\n"
        f"## Pull request\n\n"
        f"**Title:** {pr_title}\n\n"
        f"**Description:**\n{pr_body or '(no description provided)'}\n\n"
        f"## Diff (unified, may be truncated)\n\n"
        f"```diff\n"
        f"{(diff or '')[:18000]}\n"
        f"```\n\n"
        f"## Your task\n\n"
        f"Write a focused review that calls out anything that would block "
        f"this PR from being merged against the conventions in AGENTS.md. "
        f"In particular, watch for: (a) real user documents in the diff, "
        f"(b) hardcoded secrets / API keys, (c) breaking changes to the "
        f"public schema or API without a CHANGELOG note, (d) tests that "
        f"weren't updated, (e) hard dependencies on optional OCR / LLM "
        f"packages."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex PR review for KhmerDocKit.")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument(
        "--model", default=os.environ.get("KHMERDOC_CODEX_MODEL", "gpt-4o-mini")
    )
    parser.add_argument("--max-tokens", type=int, default=1500)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    pr = fetch_pr_meta(args.repo, args.pr, token)
    diff = fetch_pr_diff(args.repo, args.pr, token)

    prompt = build_prompt(
        pr_title=pr.get("title", ""),
        pr_body=pr.get("body", ""),
        diff=diff,
    )

    try:
        review = call_openai(prompt, model=args.model, max_tokens=args.max_tokens)
    except Exception as e:
        print(f"::warning::Codex review failed: {e}", file=sys.stderr)
        # Fall back to a stub so the workflow still posts a comment.
        review = (
            "_Codex review is currently unavailable in this environment. "
            "A human reviewer will pick this up shortly._\n"
        )

    header = (
        f"## Codex automated review\n\n"
        f"PR #{args.pr}: *{pr.get('title', '')}*\n\n"
        f"_Powered by `{args.model}` against `AGENTS.md` conventions._\n\n"
    )
    print(header + review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
