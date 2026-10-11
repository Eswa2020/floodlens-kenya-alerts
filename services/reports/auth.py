"""API key auth with roles (reporter, officer).

Keys come from the environment variable FLOODLENS_API_KEYS, format
"key:role:user,key:role:user". In stub mode, if it is unset, two teaching keys
are used (demo-reporter, demo-officer); they are not secrets and only work in
stub mode. In live mode with no keys configured, every request is refused
(fail closed). Real key names are listed in secret_refs.yaml, never the values.
"""
import logging
import os

from fastapi import Header, HTTPException

from services.reports.settings import is_stub

log = logging.getLogger("floodlens.auth")
TEACHING_KEYS = {
    "demo-reporter": {"role": "reporter", "user": "demo_reporter"},
    "demo-officer": {"role": "officer", "user": "duty_officer_demo"},
}


def load_keys() -> dict:
    raw = os.getenv("FLOODLENS_API_KEYS", "").strip()
    if raw:
        keys = {}
        for entry in raw.split(","):
            parts = entry.strip().split(":")
            if len(parts) == 3:
                keys[parts[0]] = {"role": parts[1], "user": parts[2]}
        return keys
    if is_stub():
        return dict(TEACHING_KEYS)
    log.error("live mode with no FLOODLENS_API_KEYS configured: refusing all requests")
    return {}


def current_user(x_api_key: str | None = Header(default=None)) -> dict:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="missing X-Api-Key header")
    user = load_keys().get(x_api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid API key")
    return user


def require_officer(user: dict) -> dict:
    if user.get("role") != "officer":
        raise HTTPException(status_code=403, detail="officer role required")
    return user
