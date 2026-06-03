"""Run the public benchmark and emit a JSON file alongside the table.

Lets a maintainer (or CI) compare two versions by diffing the JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from khmerdoc.benchmark import BenchmarkRunner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the public benchmark and write a JSON report.",
    )
    parser.add_argument("dataset", type=Path, help="Path to the synthetic dataset root.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("benchmark-report.json"),
        help="Where to write the JSON report (default: ./benchmark-report.json).",
    )
    args = parser.parse_args(argv)

    runner = BenchmarkRunner(args.dataset)
    report = runner.run()
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"wrote {args.out}  (samples={report['n_samples']}, fields={len(report['fields'])})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
