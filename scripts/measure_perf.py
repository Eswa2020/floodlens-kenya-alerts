#!/usr/bin/env python3
"""Time N calls to an endpoint and write the measured p50/p95 to a JSON file.

    python scripts/measure_perf.py --url http://localhost:8080/health --n 10 --out perf_stub.json
"""
import argparse
import json
import platform
import statistics
import time
from datetime import datetime, timezone

import httpx

CAPTION = "laptop teaching stub; not a production SLA"


def percentile(values: list[float], pct: float) -> float:
    s = sorted(values)
    k = max(0, min(len(s) - 1, round(pct / 100 * len(s) + 0.5) - 1))
    return s[k]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8080/health")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--out", default="perf_stub.json")
    args = ap.parse_args()
    timings = []
    with httpx.Client(timeout=10) as client:
        client.get(args.url)  # warm-up, not counted
        for _ in range(args.n):
            t0 = time.perf_counter()
            r = client.get(args.url)
            timings.append((time.perf_counter() - t0) * 1000)
            if r.status_code != 200:
                print(f"FAIL {args.url} returned {r.status_code}")
                return 1
    out = {
        "url": args.url,
        "n": args.n,
        "p50_ms": round(statistics.median(timings), 2),
        "p95_ms": round(percentile(timings, 95), 2),
        "max_ms": round(max(timings), 2),
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "machine": f"{platform.system()} {platform.machine()} / Python {platform.python_version()}",
        "caption": CAPTION,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
