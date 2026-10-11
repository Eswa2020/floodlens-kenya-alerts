"""Load and verify pin.json: prompt version + hash, model ids, retriever and encoder.

A prompt edit without a pin bump changes the hash, and verify_pins() fails.
That is the release-control habit: versions live in git, not in someone's head.
"""
import hashlib
import json
from functools import lru_cache

from services.reports.settings import ROOT

PIN_PATH = ROOT / "services" / "reports" / "prompts" / "pin.json"
REQUIRED_FIELDS = ("model_id", "stub_model_id", "prompt_version", "prompt_file", "prompt_sha256",
                   "retriever", "image_encoder")


def sha256_of(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def load_pins() -> dict:
    if not PIN_PATH.exists():
        raise FileNotFoundError(f"pin.json missing at {PIN_PATH}")
    return json.loads(PIN_PATH.read_text(encoding="utf-8"))


def verify_pins(pins: dict | None = None) -> list[str]:
    """Return a list of problems; empty list means the pins are consistent."""
    pins = pins or load_pins()
    problems = [f"missing field: {f}" for f in REQUIRED_FIELDS if not pins.get(f)]
    prompt_path = PIN_PATH.parent / pins.get("prompt_file", "")
    if not prompt_path.is_file():
        problems.append(f"prompt file not found: {prompt_path.name}")
    elif sha256_of(prompt_path) != pins.get("prompt_sha256"):
        problems.append("prompt_sha256 does not match the prompt file; bump prompt_version and re-pin")
    return problems


def prompt_template() -> str:
    pins = load_pins()
    return (PIN_PATH.parent / pins["prompt_file"]).read_text(encoding="utf-8")


def active_model_id(stub: bool) -> str:
    pins = load_pins()
    return pins["stub_model_id"] if stub else pins["model_id"]
