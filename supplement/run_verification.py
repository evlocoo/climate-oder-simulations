"""Run all Climate ODER supplement checks and write a JSON summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from oder_supplement.examples import verification_summary
from oder_supplement.reporting import assert_no_failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports/verification_summary.json")
    parser.add_argument("--diagnostic-out", default="reports/verification_diagnostics.json")
    args = parser.parse_args()

    summary = verification_summary()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    if summary["verification"]["failure_count"]:
        diagnostic = {"failures": summary["verification"]["failures"]}
        Path(args.diagnostic_out).write_text(json.dumps(diagnostic, indent=2, sort_keys=True), encoding="utf-8")
        assert_no_failures(summary["verification"])

    print(f"verification failures: {summary['verification']['failure_count']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

