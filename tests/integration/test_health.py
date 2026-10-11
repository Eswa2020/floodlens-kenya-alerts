import os

import httpx
import pytest

pytestmark = pytest.mark.integration
BASE = os.getenv("SERVICE_URL", "http://localhost:8080")


@pytest.mark.skipif(os.getenv("SERVICE_UP") != "1", reason="set SERVICE_UP=1 when the service is running")
def test_health_returns_200():
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200


@pytest.mark.skipif(os.getenv("SERVICE_UP") != "1", reason="set SERVICE_UP=1 when the service is running")
def test_message_over_http_needs_auth_and_returns_json():
    assert httpx.post(f"{BASE}/messages", json={"text": "hello"}, timeout=5).status_code == 401
    r = httpx.post(f"{BASE}/messages", json={"text": "What should we do if water enters the house?"},
                   headers={"X-Api-Key": "demo-reporter"}, timeout=10)
    assert r.status_code == 200 and r.json()["result"]["grounded"] is True
