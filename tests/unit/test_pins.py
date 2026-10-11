import json

from services.reports import pins


def test_pin_has_model_and_version():
    pin = json.loads(open("services/reports/prompts/pin.json", encoding="utf-8").read())
    assert pin.get("model_id") and pin.get("prompt_version")


def test_pins_consistent_with_prompt_file():
    assert pins.verify_pins() == []


def test_prompt_edit_without_repin_is_caught():
    tampered = dict(pins.load_pins(), prompt_sha256="0" * 64)
    assert any("prompt_sha256" in p for p in pins.verify_pins(tampered))


def test_stub_and_live_model_ids_differ():
    assert pins.active_model_id(stub=True) != pins.active_model_id(stub=False)
