#!/usr/bin/env python3
"""Golden-set eval (stub mode, no network, no cost).

    python evals/run_eval.py evals/golden.jsonl

Scores routing and decisions on the gold rows, and reports the two numbers
that matter most for flooding, with n:
  - missed alarms: real floods that ended up in low priority
  - false alarms:  non-floods that got an alert drafted
Exit 1 if the gate in config.json is not met (CI fails).
Also prints the same metrics on the full fixture for context (not gated).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.router import route  # noqa: E402
from services.reports.pipeline import assess  # noqa: E402
from services.reports.settings import config  # noqa: E402


def evaluate(rows: list[dict]) -> dict:
    correct = 0
    route_ok = 0
    floods = missed = non_floods = false_alarms = 0
    errors = []
    for r in rows:
        got_route = route(r["text"])
        ok = got_route == r["label"]
        route_ok += ok
        got_decision = "n/a"
        if got_route == "flood_report":
            got_decision = assess(r)["decision"]
        if r["label"] == "flood_report":
            ok = ok and got_decision == r["expected_decision"]
            if r["truth"] == "flood":
                floods += 1
                missed += got_decision == "low_priority_review"
            elif r["truth"] == "no_flood":
                non_floods += 1
                false_alarms += got_decision == "draft_alert"
        correct += ok
        if not ok:
            errors.append({"id": r["id"], "scenario": r["scenario"], "expected": [r["label"], r["expected_decision"]],
                           "got": [got_route, got_decision]})
    n = len(rows)
    return {
        "n": n,
        "score": round(correct / n, 3) if n else 0.0,
        "correct": correct,
        "route_accuracy": round(route_ok / n, 3) if n else 0.0,
        "missed_alarms": missed, "floods_n": floods,
        "false_alarms": false_alarms, "non_floods_n": non_floods,
        "errors": errors,
    }


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    gold_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evals" / "golden.jsonl"
    gate = config()["eval_gate"]
    gold = evaluate(load(gold_path))
    full = evaluate(load(ROOT / config()["fixture"]["path"]))
    print(f"golden-set score: {gold['score']:.3f} ({gold['correct']}/{gold['n']}) | "
          f"missed alarms {gold['missed_alarms']}/{gold['floods_n']} | "
          f"false alarms {gold['false_alarms']}/{gold['non_floods_n']} | mode=stub")
    print(f"full fixture (context, not gated): {full['score']:.3f} ({full['correct']}/{full['n']}) | "
          f"route accuracy {full['route_accuracy']:.3f} | missed alarms {full['missed_alarms']}/{full['floods_n']} | "
          f"false alarms {full['false_alarms']}/{full['non_floods_n']}")
    for e in full["errors"]:
        print("  full-fixture miss:", e)
    (ROOT / "evals" / "last_score.json").write_text(json.dumps({"gold": gold, "full_fixture": full}, indent=2),
                                                    encoding="utf-8")
    passed = gold["score"] >= gate["min_decision_accuracy"] and gold["missed_alarms"] <= gate["max_missed_alarms"]
    print("eval gate:", "PASS" if passed else "FAIL",
          f"(needs score >= {gate['min_decision_accuracy']} and missed alarms <= {gate['max_missed_alarms']})")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
