"""Gold fixture checks: the known-good rows must keep routing and deciding correctly."""
import json
from pathlib import Path

import pytest

from agents.router import route
from scripts.diagnose_fixture import diagnose
from services.reports.pipeline import assess

FIXTURE = Path("fixtures/flood_reports_sample.jsonl")
GOLD = [json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines() if line.strip()]
GOLD = [r for r in GOLD if r["gold"]]


def test_fixture_is_healthy():
    assert diagnose(FIXTURE) == []


def test_fixture_size_in_teaching_range():
    n = len(FIXTURE.read_text(encoding="utf-8").splitlines())
    assert 200 <= n <= 500


def test_gold_rows_present_in_every_route():
    assert {r["label"] for r in GOLD} == {"flood_report", "guidance_lookup", "review_queue"}


@pytest.mark.parametrize("row", GOLD, ids=[r["id"] for r in GOLD])
def test_gold_row(row):
    assert route(row["text"]) == row["label"]
    if row["label"] == "flood_report":
        assert assess(row)["decision"] == row["expected_decision"]


def test_gold_delivery_style_flood_row():
    # a road/vehicle report routes to scoring and drafts an alert
    row = {"text": "Flooding on the main road at Hola, a matatu is stuck in the water.",
           "image_tags": ["submerged_road", "submerged_vehicle"], "language": "en"}
    assert route(row["text"]) == "flood_report"
    assert assess(row)["decision"] == "draft_alert"


def test_gold_photo_mismatch_row():
    row = {"text": "Flooding everywhere at Bura, the road is completely under water!",
           "image_tags": ["dry_road", "clear_sky"], "language": "en"}
    assert assess(row)["decision"] == "low_priority_review"
