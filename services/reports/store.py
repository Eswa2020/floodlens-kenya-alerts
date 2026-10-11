"""In-memory store for reports and alert drafts (teaching scope; no database).

Only redacted text is ever stored. Restarting the service clears the store,
which is stated in docs/build_checkpoint.md.
"""
import threading
from collections import defaultdict
from itertools import count

_lock = threading.Lock()
_ids: dict[str, count] = defaultdict(lambda: count(1))
REPORTS: dict[str, dict] = {}
ALERTS: dict[str, dict] = {}


def next_id(prefix: str) -> str:
    with _lock:
        return f"{prefix}-{next(_ids[prefix]):05d}"


def save_report(report: dict) -> None:
    with _lock:
        REPORTS[report["report_id"]] = report


def save_alert(alert: dict) -> None:
    with _lock:
        ALERTS[alert["alert_id"]] = alert


def queue(limit: int = 50) -> list[dict]:
    """Review queue: scores and routing only. Never report text or photos."""
    order = {"review": 0, "draft_alert": 1, "low_priority_review": 2}
    with _lock:
        rows = [
            {
                "report_id": r["report_id"],
                "county": r["county"],
                "language": r["language"],
                "decision": r["decision"],
                "reason": r["reason"],
                "evidence_score": r["evidence_score"],
                "severity": r["severity"],
                "alert_id": r.get("alert_id"),
            }
            for r in REPORTS.values()
            if not (r.get("alert_id") and ALERTS.get(r["alert_id"], {}).get("approved_by"))
        ]
    rows.sort(key=lambda x: (order.get(x["decision"], 9), -x["evidence_score"]))
    return rows[:limit]


def approve(alert_id: str, officer: str) -> dict | None:
    with _lock:
        alert = ALERTS.get(alert_id)
        if alert is None:
            return None
        alert["approved_by"] = officer
        alert["status"] = "approved"
        return dict(alert)


def reset() -> None:
    with _lock:
        REPORTS.clear()
        ALERTS.clear()
