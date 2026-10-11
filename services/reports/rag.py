"""Grounded guidance: retrieve from knowledge/ and answer only from what was retrieved.

Retriever: keyword overlap with IDF weights and a 5-character prefix stem
(pinned as "keyword-idf-v1" in pin.json). No embeddings, no network: it runs
the same on every laptop and in CI.

Stub mode builds the answer from the best matching sentences. Live mode sends
the pinned prompt + retrieved passages to the pinned model. Either way the
answer carries its citations.
"""
import math
import re
from functools import lru_cache

from services.reports import pins
from services.reports.settings import ROOT, config, is_stub

KNOWLEDGE_DIR = ROOT / "knowledge"
STOP = {"the", "and", "for", "with", "that", "this", "are", "you", "your", "what", "should", "how", "can",
        "does", "from", "into", "when", "will", "there", "have", "has", "our", "near", "about", "they", "them"}


def _terms(text: str) -> list[str]:
    return [w[:5] for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2 and w not in STOP]


def _sentences(body: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]


@lru_cache(maxsize=1)
def load_docs() -> list[dict]:
    docs = []
    for path in sorted(KNOWLEDGE_DIR.glob("g*.md")):
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        title = lines[0].lstrip("# ").strip()
        body = " ".join(line.strip() for line in lines[1:] if line.strip())
        docs.append({"id": title.split()[0], "title": title, "body": body, "terms": set(_terms(title + " " + body))})
    if not docs:
        raise FileNotFoundError(f"no guidance documents found in {KNOWLEDGE_DIR}")
    return docs


@lru_cache(maxsize=1)
def _idf() -> dict[str, float]:
    docs = load_docs()
    vocab = set().union(*(d["terms"] for d in docs))
    return {t: math.log((1 + len(docs)) / (1 + sum(t in d["terms"] for d in docs))) + 1 for t in vocab}


def retrieve(question: str, k: int = 2) -> list[dict]:
    q = set(_terms(question))
    idf = _idf()
    scored = []
    for d in load_docs():
        s = sum(idf.get(t, 0.0) for t in q & d["terms"])
        if s > 0:
            scored.append({"id": d["id"], "title": d["title"], "body": d["body"], "score": round(s, 3)})
    scored.sort(key=lambda x: (-x["score"], x["id"]))
    return scored[:k]


def _stub_answer(question: str, hits: list[dict]) -> str:
    q = set(_terms(question))
    picked = []
    for h in hits:
        ranked = sorted(_sentences(h["body"]), key=lambda s: -len(q & set(_terms(s))))
        picked.extend(ranked[:2])
    return " ".join(picked)


def _live_answer(question: str, hits: list[dict], report_text: str) -> str:  # pragma: no cover - live path
    from openai import OpenAI

    prompt = pins.prompt_template().format(
        passages="\n".join(f"[{h['id']}] {h['body']}" for h in hits),
        channels="; ".join(config()["official_channels"]),
        report=report_text or "(none)",
        question=question,
    )
    resp = OpenAI().chat.completions.create(
        model=pins.active_model_id(stub=False),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=250,
    )
    return resp.choices[0].message.content.strip()


def answer(question: str, report_text: str = "", stub: bool | None = None) -> dict:
    stub = is_stub() if stub is None else stub
    p = pins.load_pins()
    hits = retrieve(question)
    channels = config()["official_channels"]
    if not hits:
        text = "The guidance set does not cover this question. Please contact the official channels listed."
    else:
        text = _stub_answer(question, hits) if stub else _live_answer(question, hits, report_text)
    return {
        "answer": text,
        "citations": [h["id"] for h in hits],
        "grounded": bool(hits),
        "official_channels": channels,
        "model_id": pins.active_model_id(stub),
        "prompt_version": p["prompt_version"],
        "retriever": p["retriever"],
        "mode": "stub" if stub else "live",
    }
