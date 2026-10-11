#!/usr/bin/env python3
"""Diagnose a JSONL fixture. Fails loudly (exit 1) on any broken row.

    python scripts/diagnose_fixture.py fixtures/flood_reports_sample.jsonl

Checks: every line is valid JSON (no '#' comment lines), required fields,
unique ids, allowed labels/counties/languages/decisions, row count within
200-500, gold rows present, no gold row whose label disagrees with its scenario.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["id", "county", "language", "text", "image_tags", "has_person", "label", "truth",
            "expected_decision", "scenario", "gold"]
DECISIONS = {"draft_alert", "review", "low_priority_review", "n/a"}
SCENARIO_LABEL = {"guidance": "guidance_lookup", "hard_guidance": "guidance_lookup", "queue": "review_queue"}


def diagnose(path: Path) -> list[str]:
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    problems, ids, gold = [], set(), 0
    if not path.exists():
        return [f"fixture not found: {path}"]
    lines = path.read_text(encoding="utf-8").splitlines()
    for n, line in enumerate(lines, start=1):
        if not line.strip():
            problems.append(f"line {n}: blank line")
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: invalid JSON ({e.msg})")
            continue
        missing = [f for f in REQUIRED if f not in row]
        if missing:
            problems.append(f"line {n}: missing fields {missing}")
            continue
        if row["id"] in ids:
            problems.append(f"line {n}: duplicate id {row['id']}")
        ids.add(row["id"])
        if row["label"] not in cfg["tools"]:
            problems.append(f"line {n} {row['id']}: unknown label {row['label']!r}")
        if row["county"] not in cfg["counties"]:
            problems.append(f"line {n} {row['id']}: unknown county {row['county']!r}")
        if row["language"] not in cfg["languages"]:
            problems.append(f"line {n} {row['id']}: unknown language {row['language']!r}")
        if row["expected_decision"] not in DECISIONS:
            problems.append(f"line {n} {row['id']}: unknown decision {row['expected_decision']!r}")
        want = SCENARIO_LABEL.get(row["scenario"], "flood_report")
        if row["label"] != want:
            problems.append(f"line {n} {row['id']}: label {row['label']!r} contradicts scenario "
                            f"{row['scenario']!r} (expected {want!r})")
        gold += bool(row["gold"])
    lo, hi = cfg["fixture"]["min_rows"], cfg["fixture"]["max_rows"]
    if not lo <= len(lines) <= hi:
        problems.append(f"row count {len(lines)} outside teaching range {lo}-{hi}")
    if gold == 0:
        problems.append("no gold rows marked")
    return problems


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "fixtures" / "flood_reports_sample.jsonl"
    problems = diagnose(path)
    if problems:
        print(f"FAIL {len(problems)} problem(s) in {path}:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"fixture OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
