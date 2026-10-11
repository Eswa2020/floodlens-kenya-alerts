# Skill coverage matrix

Each required skill maps to the programme week that taught it, the prior artefact reused, and where it lives in this repo.

| Skill | Week resource to open | Prior artefact reused | My module / file | Required / Optional |
|---|---|---|---|---|
| API or agent path | Week 6 triage API lab | afyaplus-platform (FastAPI, auth, version header, health) | `services/reports/app.py`, `auth.py`, `schemas.py` | Required |
| Agent + MCP tools | Week 6 MCP agent, Week 7 MCP logistics tools | afyaplus-platform (MCP logistics agent) | `agents/agent.py`, `agents/mcp_server.py`, `agents/tools/flood_tools.py` | Required |
| Cost / spend honesty | Week 7 cost model and cache/batch levers | afyaplus-platform cost-optimization | `docs/cost_analysis.md` | Required |
| Pin / versioning | Week 8 pin.json, CI eval gates | afyaplus-platform release-control | `services/reports/prompts/pin.json`, `services/reports/pins.py`, `tests/unit/test_pins.py` | Required |
| Security hygiene | Week 9 security smoke, injection guard, Kenya DPA | afyaplus-platform security-compliance | `tests/test_security_smoke.py`, `services/reports/redact.py`, `guard.py`, `secret_refs.yaml` | Required |
| RAG grounding | Weeks 1 to 3 LLM / RAG labs | urban-parking-rag-app (retrieval + citations habit) | `services/reports/rag.py`, `knowledge/` | Required |
| Eval / test | Week 11 Tuesday pyramid + golden set | Week 8 CI eval gate | `tests/unit/`, `evals/golden.jsonl`, `evals/run_eval.py` | Required |
| Docs | Prior READMEs + Week 11 doc pack | afyaplus-platform runbook / executive brief | `docs/` | Required |
| Optional multimodal (one lane) | Week 10 cross-modal catalog mismatch lane; Week 5 multimodal | sokonihub-catalog-intelligence (mismatch score + review queue), floodlens-kenya (red-zone classifier) | `services/reports/scoring.py`, `analytics/county_report.py` | Optional (chosen) |
| Fine-tuned model | Week 4 fine-tuning | kenya-flood-finetune (Llama-3.1-8B flood assistant) | not wired; declared stretch in `docs/build_checkpoint.md` | Optional (deferred) |
