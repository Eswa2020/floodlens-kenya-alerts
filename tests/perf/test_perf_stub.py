import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.perf


def test_perf_stub_measured_not_guessed():
    p = Path("perf_stub.json")
    assert p.exists(), "run scripts/measure_perf.py (or python run_all.py) first"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["n"] >= 10 and data["p95_ms"] > 0
    assert "not a production SLA" in data["caption"]
