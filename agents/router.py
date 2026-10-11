"""Keyword router. Tool names and keywords come from config.json, not code,
so the same file works for any project (starter-pack pattern)."""
import json

from services.reports.settings import ROOT

CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TOOLS = CONFIG["tools"]
KEYWORDS = CONFIG["route_keywords"]


def route(intent: str) -> str:
    t = (intent or "").lower()
    for tool, words in KEYWORDS.items():
        if any(w in t for w in words):
            return tool
    return TOOLS[0]
