#!/usr/bin/env python3
"""Flag and alert rates by county (with n) and Kiswahili/Sheng vocabulary gaps.

    python analytics/county_report.py

Rates are over flood reports in the teaching fixture. Read with care: fewer
phones and fewer reports in poorer areas mean low counts are NOT low risk.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.reports.pipeline import assess  # noqa: E402
from services.reports.scoring import unknown_tokens  # noqa: E402
from services.reports.settings import config  # noqa: E402


def build() -> dict:
    rows = [json.loads(line) for line in (ROOT / config()["fixture"]["path"]).read_text(encoding="utf-8").splitlines()
            if line.strip()]
    by_county: dict[str, Counter] = defaultdict(Counter)
    gaps: dict[str, Counter] = {"sw": Counter(), "sheng": Counter()}
    for r in rows:
        if r["label"] != "flood_report":
            continue
        a = assess(r)
        c = by_county[r["county"]]
        c["n"] += 1
        c[a["decision"]] += 1
        if r["language"] in gaps:
            gaps[r["language"]].update(unknown_tokens(r["text"]))
    table = {}
    for county, c in sorted(by_county.items()):
        n = c["n"]
        table[county] = {
            "n": n,
            "alert_draft_rate": round(c["draft_alert"] / n, 3),
            "review_rate": round(c["review"] / n, 3),
            "low_priority_rate": round(c["low_priority_review"] / n, 3),
        }
    return {
        "by_county": table,
        "vocab_gaps": {lang: cnt.most_common(10) for lang, cnt in gaps.items()},
        "caveat": "Synthetic teaching fixture. Low report counts are not low risk (unequal phone access).",
    }


def main() -> int:
    out = build()
    print(f"{'county':<12}{'n':>5}{'draft':>9}{'review':>9}{'low_pri':>9}")
    for county, t in out["by_county"].items():
        print(f"{county:<12}{t['n']:>5}{t['alert_draft_rate']:>9.2f}{t['review_rate']:>9.2f}{t['low_priority_rate']:>9.2f}")
    for lang, items in out["vocab_gaps"].items():
        print(f"vocab gaps ({lang}):", ", ".join(f"{w}({n})" for w, n in items))
    print("caveat:", out["caveat"])
    (ROOT / "analytics" / "county_rates.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
