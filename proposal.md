# Capstone proposal: FloodLens Kenya

## Path
**Domain alternative**: flood alerting decision support for Kenyan county duty officers.
It covers the same skill checklist as the AfyaPlus path (API and agent path, pins, security hygiene,
eval/test, docs, one multimodal lane). Every skill is mapped to a programme week in `skill_matrix.md`.

Mentor approval: ____________________ (name) on ____________ (date)

## Problem
- **Who is blocked today:** county duty officers in Nairobi, Kisumu and Tana River receive community flood reports
  (photo + text) faster than they can check them, in English, Kiswahili and Sheng.
- **What decision the system supports:** for each report, should a draft alert be prepared for approval, should a person
  review it, or is it low priority? The officer always makes the final call. Nothing is broadcast automatically.
- **How we know it worked:** on the gold rows, decision accuracy of at least 0.85 with **zero missed alarms**
  (a real flood sent to low priority), false alarms reported with n, and every alert carrying `approved_by: null`
  until an authenticated officer approves it.
- **Why it matters:** in flooding a missed alarm costs more than a false one, so the threshold and the human gate are
  the core design decisions, not details.

## Dataset
`fixtures/flood_reports_sample.jsonl`: 300 synthetic rows (teaching only), 34 of them marked gold and copied to
`evals/golden.jsonl`. Generated offline by `scripts/make_fixture.py`. Three counties, three languages, and scenarios that
include matching and mismatched photos, a person in the photo, phone numbers in text, and injection attempts.
Do not scrape production. Do not use millions of rows. The grounding document set is 8 short teaching summaries in `knowledge/`.

## Milestones
- **Monday:** proposal, skill_matrix, integration_map, base service, `/health` returns 200
- **Tuesday:** pytest pyramid, security smoke, CI, RAG + MCP agent in stub mode, fixture diagnosis, eval score
- **Thursday:** docs pack, peer-reviewed PR, presentation deck, 3-command demo
- **Week 12 Monday:** presentation and demo

## Minimum Working Product (how each requirement is met)
| # | Requirement | Where |
|---|---|---|
| 1 | Authenticated FastAPI endpoint returns validated JSON | `POST /messages`, `services/reports/app.py`, `schemas.py` |
| 2 | One answer grounded in a small document set (RAG) | `services/reports/rag.py` over `knowledge/` |
| 3 | Agent calls at least one MCP tool, stub mode works | `agents/agent.py` -> `agents/mcp_server.py` |
| 4 | Prompt and model versions from pin.json | `services/reports/prompts/pin.json` |
| 5 | Security smoke: no secrets, auth required, PII redacted in logs | `tests/test_security_smoke.py` |
| 6 | Golden-set eval score printed in CI | `evals/run_eval.py`, `.github/workflows/ci.yml` |
| 7 | 200-500 row fixture, one documented command | `fixtures/`, `python run_all.py` |
| Optional lane | Cross-modal mismatch (report text vs image evidence) | `services/reports/scoring.py` |

## Risks and controls
| Risk | Control |
|---|---|
| Missed alarm | Low agreement goes to a queue, never dropped. If the photo shows water the report always reaches a person. Missed-alarm rate is gated in CI. |
| False alarm / alert fatigue | Human approval before any alert. False-alarm rate is reported with n. |
| Kiswahili/Sheng coverage | Always reviewed by a person. Vocab-gap report in `analytics/`. |
| Faces and homes in photos | Photo reference redacted when a person is present. Never in public outputs (Kenya DPA 2019). |
| Prompt injection | Injection guard. Report text is data, never instructions. |
| Overclaiming | Every alert names the official channels and carries a "decision support only" disclaimer. |

## Out of scope
- Training a new foundation model (the fine-tuned Llama-3.1-8B flood assistant stays a declared stretch)
- Live crawl of social media, phone numbers or any personal data
- Live satellite or CLIP inference in tests (fixture image tags stand in; live encoder is a pinned candidate only)
- Voice notes / Whisper (only one optional lane is allowed)
- Sending SMS or broadcasts of any kind; claims of "verified" or "official" warnings
- Mixing data from other projects (no health or marketplace fixtures in this repo)
