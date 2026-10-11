"""Shared settings: repo paths, config.json, and stub/live mode.

Stub mode is the default. Live mode needs FLOODLENS_MODE=live AND an
OPENAI_API_KEY; if the key is missing the service falls back to stub mode
and says so loudly, so tests and CI never call a live model.
"""
import json
import logging
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
log = logging.getLogger("floodlens.settings")


@lru_cache(maxsize=1)
def config() -> dict:
    path = ROOT / "config.json"
    if not path.exists():
        raise FileNotFoundError(f"config.json missing at {path}; the service cannot start without it")
    return json.loads(path.read_text(encoding="utf-8"))


def is_stub() -> bool:
    if os.getenv("FLOODLENS_MODE", "stub").lower() != "live":
        return True
    if not os.getenv("OPENAI_API_KEY"):
        log.warning("FLOODLENS_MODE=live but OPENAI_API_KEY is not set; falling back to stub mode")
        return True
    return False


def mode() -> str:
    return "stub" if is_stub() else "live"
