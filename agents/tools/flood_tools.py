"""Tool functions the agent can call. Each returns a structured dict an agent
can parse. Tool boundary rules:
- review queue returns scores and routing only: never report text, phones or photos
- report text is redacted before it is stored or returned
"""
from services.reports import pipeline, rag, store
from services.reports.redact import redact


def score_report(text: str, county: str = "unknown", language: str = "en",
                 image_tags: list[str] | None = None, has_person: bool = False,
                 photo_ref: str | None = None) -> dict:
    """Score a community flood report against its image evidence and draft an alert if strong."""
    out = pipeline.process_report({
        "text": text, "county": county, "language": language,
        "image_tags": image_tags or [], "has_person": has_person, "photo_ref": photo_ref,
    })
    return {"tool": "score_report", **out}


def lookup_guidance(question: str) -> dict:
    """Answer a flood-safety question grounded in the guidance document set."""
    return {"tool": "lookup_guidance", **rag.answer(redact(question))}


def list_review_queue(limit: int = 20) -> dict:
    """List reports waiting for a duty officer: ids, county, scores and reasons only."""
    rows = store.queue(limit)
    return {"tool": "list_review_queue", "count": len(rows), "items": rows}
