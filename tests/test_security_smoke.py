"""Security smoke: the minimum bar, wired as code."""
import logging
import re
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.reports.redact import redact

_LIVE_KEY = re.compile(r"sk-(live|proj)-[A-Za-z0-9_-]{6,}")
SKIP_DIRS = {"venv", ".venv", "tests", ".git", "node_modules", "__pycache__"}
SCAN_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".toml"}


def _tracked_files() -> list[str]:
    try:
        return subprocess.check_output(["git", "ls-files"], text=True, stderr=subprocess.DEVNULL).splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("not inside a git repository yet (run git init first)")


def test_env_not_tracked():
    assert ".env" not in _tracked_files()


def test_gitignore_covers_env():
    assert ".env" in Path(".gitignore").read_text(encoding="utf-8").splitlines()


def test_no_live_looking_key_in_repo():
    for p in Path(".").rglob("*"):
        if not p.is_file() or SKIP_DIRS & set(p.parts) or p.suffix not in SCAN_SUFFIXES:
            continue
        assert _LIVE_KEY.search(p.read_text(encoding="utf-8", errors="ignore")) is None, f"live-looking key in {p}"


def test_secret_refs_lists_names_not_values():
    text = Path("secret_refs.yaml").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY" in text and not _LIVE_KEY.search(text)


def test_auth_required_on_messages():
    from services.reports.app import app
    client = TestClient(app)
    assert client.post("/messages", json={"text": "hello"}).status_code == 401
    assert client.post("/messages", json={"text": "hello"}, headers={"X-Api-Key": "wrong"}).status_code == 401


def test_redaction_strips_email():
    assert "user@example.com" not in redact("contact user@example.com now")


def test_redaction_strips_kenyan_phones():
    for phone in ["0712 345 678", "+254712345678", "254 712 345 678", "0110-123-456"]:
        assert phone not in redact(f"call me on {phone} please"), phone


def test_no_pii_in_logs(caplog):
    from services.reports.app import app
    client = TestClient(app)
    with caplog.at_level(logging.INFO):
        client.post("/messages", headers={"X-Api-Key": "demo-reporter"}, json={
            "text": "Houses flooded at Kibera. Call 0712 345 678 or mail jane@example.com",
            "county": "Nairobi", "image_tags": ["flooded_house"]})
    logs = caplog.text
    assert "0712 345 678" not in logs and "jane@example.com" not in logs
    assert "Houses flooded at Kibera" not in logs  # raw report text never logged


def test_person_photo_redacted_in_response():
    from services.reports.app import app
    client = TestClient(app)
    r = client.post("/messages", headers={"X-Api-Key": "demo-reporter"}, json={
        "text": "People wading through water on the road at Garsen.", "county": "Tana River",
        "image_tags": ["people_wading", "submerged_road"], "has_person": True, "photo_ref": "photos/p1.jpg"})
    assert r.json()["result"]["report"]["photo_ref"] == "[REDACTED_PHOTO:person_present]"
