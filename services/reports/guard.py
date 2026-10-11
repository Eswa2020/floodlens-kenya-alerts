"""Prompt-injection guard for community report text.

Reports are data, never instructions. A report that looks like it is trying
to steer the system (approve itself, broadcast, change the rules) is never
auto-drafted: it goes to a human with reason "possible_injection".
"""
import re

PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|rules)",
    r"disregard (the |all )?(rules|instructions)",
    r"system prompt",
    r"you are now",
    r"act as (an? )?(admin|officer|system)",
    r"(send|broadcast|push) (an? )?(alert|warning|sms)s? to (all|every)",
    r"approve (this|the|my) (alert|report)",
    r"mark (this|it) as (verified|approved)",
    r"<\s*script",
    r"\bsudo\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def check_injection(text: str) -> dict:
    hits = [p.pattern for p in _COMPILED if text and p.search(text)]
    return {"flagged": bool(hits), "matched": len(hits)}
