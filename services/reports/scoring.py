"""Cross-modal agreement: does the photo evidence back up what the report says?

Text is mapped to flood concepts with a small vocabulary (English plus some
Kiswahili). Image tags come from the fixture in stub mode (standing in for the
red-zone classifier / CLIP tags) and map to the same concepts.

score = share of the report's claims that the image confirms. An image with
no water can never support an alert (score 0.0). Low scores are never
dropped: they go to a human queue (see decide()).
"""
import re

from services.reports.settings import config

TEXT_VOCAB = {
    # water
    "water": "water", "flood": "water", "flooded": "water", "flooding": "water", "floods": "water",
    "floodwater": "water", "overflow": "water", "overflowing": "water", "burst": "water", "submerged": "water",
    "maji": "water", "mafuriko": "water",
    # road
    "road": "road", "roads": "road", "street": "road", "bridge": "road", "highway": "road", "barabara": "road",
    # house
    "house": "house", "houses": "house", "home": "house", "homes": "house", "plot": "house",
    "shop": "house", "shops": "house", "school": "house", "nyumba": "house",
    # vehicle
    "car": "vehicle", "cars": "vehicle", "matatu": "vehicle", "vehicle": "vehicle", "bus": "vehicle",
    "boda": "vehicle", "gari": "vehicle",
    # river
    "river": "river", "stream": "river", "dam": "river", "canal": "river", "mto": "river",
    # people
    "stranded": "people", "trapped": "people", "rescue": "people", "children": "people", "watu": "people",
}

IMAGE_TAGS = {
    "standing_water": {"water"},
    "floodwater": {"water"},
    "submerged_road": {"road", "water"},
    "flooded_house": {"house", "water"},
    "submerged_vehicle": {"vehicle", "water"},
    "overflowing_river": {"river", "water"},
    "people_wading": {"people", "water"},
    "rooftop_refuge": {"people", "house", "water"},
    "dry_road": {"road"},
    "traffic": {"vehicle"},
    "dry_riverbed": {"river"},
    "building": {"house"},
    "market_stall": set(),
    "clear_sky": set(),
    "crowd": {"people"},
}

STOPWORDS = {"the", "and", "with", "this", "that", "near", "from", "have", "there", "here", "our", "please",
             "sana", "kwa", "hapa", "yetu", "wetu", "kwenye", "leo", "sasa", "na", "ya", "za", "wa", "la"}

IMAGE_ONLY_SCORE = 0.35   # water in the photo: never below human review


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z]+", (text or "").lower())


def text_concepts(text: str) -> set[str]:
    return {TEXT_VOCAB[t] for t in tokens(text) if t in TEXT_VOCAB}


def image_concepts(tags: list[str]) -> set[str]:
    out: set[str] = set()
    for tag in tags or []:
        out |= IMAGE_TAGS.get(tag, set())
    return out


def unknown_tokens(text: str) -> list[str]:
    """Words we could not map: the raw material for the vocab-gap report."""
    return [t for t in tokens(text) if t not in TEXT_VOCAB and t not in STOPWORDS and len(t) > 3]


def agreement_score(text: str, image_tags: list[str]) -> float:
    t, i = text_concepts(text), image_concepts(image_tags)
    if "water" not in i:
        return 0.0
    if not t:
        return IMAGE_ONLY_SCORE
    # Floor: if the photo shows water, the report always reaches a human
    # (found in eval: place names like "Ngong Road" read as a road claim and
    # pushed a real flood to low priority = a missed alarm).
    return round(max(len(t & i) / len(t), IMAGE_ONLY_SCORE), 2)


def severity(image_tags: list[str]) -> str:
    i = image_concepts(image_tags)
    if "water" not in i:
        return "none"
    if "people" in i or "house" in i:
        return "high"
    if "vehicle" in i or "road" in i or "river" in i:
        return "medium"
    return "low"


def decide(score: float, language: str, injection_flagged: bool, has_image: bool = True) -> tuple[str, str]:
    """Return (decision, reason). Decisions: draft_alert | review | low_priority_review.

    Nothing is ever dropped. draft_alert still needs a human approval.
    """
    rules = config()["scoring"]
    if injection_flagged:
        return "review", "possible_injection"
    if language in rules["always_review_languages"]:
        return "review", "language_review"
    if not has_image:
        return "review", "no_image_evidence"
    if score >= rules["draft_threshold"]:
        return "draft_alert", "strong_agreement"
    if score >= rules["low_priority_below"]:
        return "review", "weak_agreement"
    return "low_priority_review", "mismatch_or_no_evidence"
