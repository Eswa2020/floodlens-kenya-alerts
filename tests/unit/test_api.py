"""API boundary tests with FastAPI's in-process TestClient (no network)."""
from fastapi.testclient import TestClient

from services.reports.app import app

client = TestClient(app)
REPORTER = {"X-Api-Key": "demo-reporter"}
OFFICER = {"X-Api-Key": "demo-officer"}
FLOOD = {"text": "Water has covered the road at Kibera, cars cannot pass.", "county": "Nairobi",
         "image_tags": ["submerged_road", "submerged_vehicle"]}


def test_health_200_with_version_header():
    r = client.get("/health")
    assert r.status_code == 200 and r.headers["X-Prompt-Version"]


def test_invalid_payload_rejected():
    assert client.post("/messages", json={"text": ""}, headers=REPORTER).status_code == 422


def test_full_human_gate_flow():
    r = client.post("/messages", json=FLOOD, headers=REPORTER)
    assert r.status_code == 200
    alert = r.json()["result"]["alert"]
    assert alert["approved_by"] is None
    assert client.post(f"/alerts/{alert['alert_id']}/approve", headers=REPORTER).status_code == 403
    ok = client.post(f"/alerts/{alert['alert_id']}/approve", headers=OFFICER)
    assert ok.status_code == 200 and ok.json()["approved_by"] == "duty_officer_demo"


def test_review_queue_is_officer_only():
    assert client.get("/review-queue", headers=REPORTER).status_code == 403
    assert client.get("/review-queue", headers=OFFICER).status_code == 200


def test_unknown_alert_404():
    assert client.post("/alerts/AL-99999/approve", headers=OFFICER).status_code == 404
