"""Real service-function tests in stub mode (not just router logic)."""
import json

from services.reports.app import handle_message


def test_service_runs_in_stub_mode():
    out = handle_message({"text": "hello"}, stub=True)
    assert out["status"] == "ok"
    assert out["mode"] == "stub"


def test_flood_report_drafts_alert_that_needs_human_approval():
    out = handle_message({"text": "Houses flooded at Kibera, water inside homes since morning.",
                          "county": "Nairobi", "image_tags": ["flooded_house", "standing_water"]}, stub=True)
    alert = out["result"]["alert"]
    assert out["tool"] == "score_report"
    assert alert["approved_by"] is None
    assert alert["status"] == "pending_approval"
    assert alert["official_channels"]
    assert "verified" not in alert["message"].lower() and "guaranteed" not in alert["message"].lower()


def test_guidance_answer_is_grounded_with_citations():
    out = handle_message({"text": "What should we do if water enters the house?"}, stub=True)
    assert out["route"] == "guidance_lookup"
    assert out["result"]["grounded"] is True
    assert out["result"]["citations"]


def test_review_queue_forbidden_for_reporter():
    out = handle_message({"text": "Show queue for Kisumu"}, stub=True, role="reporter")
    assert out["status"] == "forbidden"


def test_output_is_valid_json():
    out = handle_message({"text": "hello"}, stub=True)
    assert json.loads(json.dumps(out)) == out
