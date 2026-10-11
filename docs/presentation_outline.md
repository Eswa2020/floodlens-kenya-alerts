# Presentation outline (8-10 slides, 7 min talk + 3 min demo)

1. **Problem and user:** county duty officers flooded with photo + text reports in 3 languages; a missed alarm costs lives.
2. **Path chosen and why:** domain alternative, built from my own flood work (fine-tuning, multimodal) + the platform weeks.
3. **Architecture:** FastAPI -> agent -> MCP tools -> guard / redact / score / decide -> RAG -> human approval.
4. **Skill coverage:** the skill matrix table, one row per skill, week and file.
5. **Live demo:** `python run_all.py`, or the 3-command demo (backup: `docs/demo_transcript.md`).
6. **Testing evidence:** 84 passed; security smoke; golden 34/34; missed alarms 0/20; full fixture 0.973 with hard rows.
7. **Security and compliance:** auth roles, Kenyan phone redaction, no PII in logs, person-photo redaction, injection guard, Kenya DPA.
8. **Cost table:** $0 in CI; about $0.13 per 1,000 reports live (teaching estimate); demo well under $1.
9. **What works vs deferred:** live LLM, live CLIP, fine-tuned Llama, cloud deploy, persistence.
10. **Process:** feature branches, PR, peer review outcome, the Ngong Road missed-alarm bug and fix, next steps.
