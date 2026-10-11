"""Report pipeline: guard -> redact -> score -> decide -> (draft alert) -> store.

Pure Python, no network in stub mode. Used by the MCP tool, the eval and the
analytics, so all three judge exactly the same logic.
"""
import logging

from services.reports import pins, rag, store
from services.reports.guard import check_injection
from services.reports.redact import redact, redact_photo_ref
from services.reports.scoring import agreement_score, decide, image_concepts, severity
from services.reports.settings import config, is_stub

log = logging.getLogger("floodlens.pipeline")

# Resident-safety query per evidence concept (what the photo shows), so the alert
# cites safety guidance rather than echoing the report text back into retrieval.
CONCEPT_QUERY = {
    "road": "moving water road turn around",
    "vehicle": "drive matatu float moving water",
    "house": "evacuate water rising house higher ground",
    "river": "river overflowing riverside low-lying",
    "people": "evacuate help children older people",
}


def alert_query(image_tags: list[str]) -> str:
    concepts = sorted(image_concepts(image_tags) - {"water"})
    return " ".join(CONCEPT_QUERY[c] for c in concepts if c in CONCEPT_QUERY) or "evacuate water rising"


def assess(report: dict) -> dict:
    """Score and decide without side effects (used by eval and analytics)."""
    text = report.get("text", "")
    language = report.get("language", "en")
    inj = check_injection(text)
    score = agreement_score(text, report.get("image_tags", []))
    decision, reason = decide(score, language, inj["flagged"], has_image=bool(report.get("image_tags")))
    return {
        "evidence_score": score,
        "decision": decision,
        "reason": reason,
        "severity": severity(report.get("image_tags", [])),
        "injection_flagged": inj["flagged"],
    }


def draft_alert(report_id: str, county: str, sev: str, score: float, guidance: dict) -> dict:
    p = pins.load_pins()
    return {
        "alert_id": store.next_id("AL"),
        "report_id": report_id,
        "county": county,
        "severity": sev,
        "evidence_score": score,
        "message": f"Possible flooding reported in {county} (severity: {sev}). {guidance['answer']}",
        "citations": guidance["citations"],
        "official_channels": config()["official_channels"],
        "status": "pending_approval",
        "approved_by": None,
        "prompt_version": p["prompt_version"],
        "model_id": guidance["model_id"],
        "disclaimer": "Decision support only. Not an official warning. Confirm with the official channels.",
    }


def process_report(report: dict, stub: bool | None = None) -> dict:
    stub = is_stub() if stub is None else stub
    county = report.get("county", "unknown")
    if county not in config()["counties"]:
        county = "unknown"
    clean_text = redact(report.get("text", ""))
    result = assess(report)
    report_id = store.next_id("RP")
    record = {
        "report_id": report_id,
        "county": county,
        "language": report.get("language", "en"),
        "text_redacted": clean_text,
        "photo_ref": redact_photo_ref(report.get("photo_ref"), bool(report.get("has_person"))),
        **result,
        "alert_id": None,
    }
    alert = None
    if result["decision"] == "draft_alert":
        guidance = rag.answer(alert_query(report.get("image_tags", [])), clean_text, stub=stub)
        alert = draft_alert(report_id, county, result["severity"], result["evidence_score"], guidance)
        record["alert_id"] = alert["alert_id"]
        store.save_alert(alert)
    store.save_report(record)
    # Log ids and scores only: never report text, phone numbers or photos.
    log.info("report=%s county=%s decision=%s score=%.2f",
             report_id, county, result["decision"], result["evidence_score"])
    return {"report": record, "alert": alert}
