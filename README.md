# FloodLens Kenya

Flood alert **decision support** for county duty officers in Kenya. It scores how well a community flood report
(text + photo evidence) agrees with itself, grounds safety guidance in a small document set, and drafts an alert that
**a duty officer must approve before anything is sent**. It never broadcasts on its own and always points residents to the
official channels (Kenya Meteorological Department, National Disaster Operations Centre, county emergency lines, Kenya Red Cross).

![ci](https://github.com/Eswa2020/floodlens-kenya-alerts/actions/workflows/ci.yml/badge.svg) [![DOI](https://zenodo.org/badge/1414072567.svg)](https://doi.org/10.5281/zenodo.23433888)

## Overview
Module 4 capstone, **domain alternative path** (`proposal.md`). One FastAPI service with API-key roles, an agent that
calls tools over MCP, pinned prompt and model versions, a security smoke suite, a golden-set eval in CI, and one
multimodal lane (report-vs-image agreement). Everything runs in stub mode with no API key, on a 300-row synthetic fixture.

## Project path
- [ ] AfyaPlus Module 4 Capstone (recommended)
- [x] Domain / field alternative with skill checklist: flood alerting (FloodLens Kenya)

## Quick start (one command)
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_all.py
```
`run_all.py` diagnoses the fixture, runs the tests and security smoke, prints the eval score, starts the API, runs
integration tests, measures perf, runs the demo calls and writes `docs/demo_transcript.md`.

## Results (stub mode)
| Check | Result |
|---|---|
| `pytest -q` | 84 passed |
| Golden-set eval | 1.000 (34/34), missed alarms 0/20, false alarms 0/8 |
| Full fixture (incl. deliberately hard rows, not gated) | 0.973 (292/300), missed alarms 0/170 |
| `/health` p95 | 2.28 ms over 10 calls (laptop teaching stub, not a production SLA) |

## Week reuse
Full mapping: `skill_matrix.md` and `integration_map.json`.
- Weeks 1-5: RAG with citations (`services/reports/rag.py`); multimodal habit from floodlens-kenya; fine-tuned model deferred
- Week 6: API, auth and MCP agent pattern -> `services/reports/`, `agents/`
- Week 7: MCP tools and cost honesty -> `agents/tools/flood_tools.py`, `docs/cost_analysis.md`
- Week 8: pins -> `services/reports/prompts/pin.json`
- Week 9: security smoke -> `tests/test_security_smoke.py`
- Week 10: cross-modal mismatch lane -> `services/reports/scoring.py`

## Dataset
- `fixtures/`: 300 synthetic rows (200-500 rule), 34 gold. No production scrape. See `fixtures/README.md`.

## Repo layout
```
services/reports/   API, auth, schemas, pipeline, scoring, RAG, redaction, guard, pins
agents/             router (config.json), agent, MCP server, tools
knowledge/          8 guidance documents (RAG corpus)
fixtures/           teaching fixture + README
evals/              golden.jsonl + run_eval.py
analytics/          county rates with n + vocab gaps
scripts/            make_fixture, diagnose_fixture, measure_perf
tests/              unit/, integration/, perf/, test_security_smoke.py
docs/               doc pack, ethics note, runbook, transcript, slides
deploy/             Dockerfile (optional)
```

## Docs
- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [Cost analysis](docs/cost_analysis.md)
- [User guide](docs/user_guide.md)
- [Build checkpoint](docs/build_checkpoint.md)
- [Ethics note](docs/ethics_note.md) · [Runbook](docs/runbook.md) · [Demo transcript](docs/demo_transcript.md)

## Testing
- unit default: `pytest -q`
- integration: `SERVICE_UP=1 pytest -m integration -q` (service running)
- perf: `python scripts/measure_perf.py --url http://localhost:8080/health --n 10 --out perf_stub.json`
- security: `pytest tests/test_security_smoke.py -q`
- eval: `python evals/run_eval.py evals/golden.jsonl`

## Demo
Three commands: start the service, curl `/health`, POST a flood report to `/messages`. See `docs/user_guide.md`.
```bash
uvicorn services.reports.app:app --port 8080 &
curl localhost:8080/health
curl -X POST localhost:8080/messages -H "X-Api-Key: demo-reporter" -H "Content-Type: application/json" -d '{"text":"Water has covered the road at Kibera, cars cannot pass.","county":"Nairobi","image_tags":["submerged_road","submerged_vehicle"]}'
```

## Presentation
[docs/presentation.pdf](docs/presentation.pdf), presented Week 12 Monday.

## Peer review
- review_log.md entry: [review_log.md](review_log.md)
- checklist: [docs/peer_review_checklist.md](docs/peer_review_checklist.md)

## Fallbacks declared
- [x] no live OpenAI key (stub agent; live path optional, about $1 cap)
- [x] no Docker in CI (Dockerfile provided, integration tests run against uvicorn)
- [x] no cloud deploy executed (docs only)
- [x] solo reviewer (self-review with checklist); mentor review requested on PR #1, pending

## Submission checklist
- [x] proposal + skill_matrix + map
- [x] five docs linked
- [x] self-review completed (review_log.md); mentor review pending
- [x] slides PDF in docs/ and demo command documented

## How to cite
Kamau, E. W. (2026). *FloodLens Kenya: Human-in-the-Loop Flood Alert Decision Support for County Duty Officers*. Zenodo. https://doi.org/10.5281/zenodo.23433888
