#!/usr/bin/env python3
"""Aggregate quality-cost metrics from task-level observations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from skill_economy.metrics import load_rows, summarize_conditions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=Path("results/summary/condition_summary.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("results/summary/condition_summary.csv"))
    args = parser.parse_args()

    rows = load_rows(args.observations)
    summary = summarize_conditions(rows)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in summary for key in row})
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    print(f"Wrote {args.out_json} and {args.out_csv}")


if __name__ == "__main__":
    main()
