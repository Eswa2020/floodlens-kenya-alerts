# Build checkpoint

Status as of the end of the build. Evidence lines point to files or commands anyone can re-run.

## Works now (with evidence)
- **Path:** domain alternative, FloodLens Kenya (`proposal.md`). Skill matrix complete (`skill_matrix.md`).
- **Integration map:** 9 rows, all paths exist (`python check_integration_map.py` -> `integration map OK 9`).
- **Tests:** `pytest -q` -> 84 passed (unit + security smoke). Integration (2) and perf (1) pass with the service up.
- **Security smoke:** auth required, `.env` not tracked, no live-looking keys, email + Kenyan phone redaction,
  no PII or raw report text in logs, person-photo redaction.
- **Eval:** `python evals/run_eval.py evals/golden.jsonl` -> golden-set score 1.000 (34/34), missed alarms 0/20,
  false alarms 0/8. Full fixture (not gated, includes deliberately hard rows): 0.973 (292/300), route accuracy 0.983,
  missed alarms 0/170, false alarms 0/50.
- **MWP end to end in stub mode:** `python run_all.py` -> Overall PASS. Transcript: `docs/demo_transcript.md`.
- **RAG:** grounded answers with citations from 8 guidance docs (`python -m services.reports.rag_smoke`).
- **MCP:** agent calls tools over a real MCP client session (in-memory transport); 3 tools exposed.
- **Pins:** `pin.json` with prompt sha256; the service refuses to start if the prompt and pin disagree.
- **Perf (measured):** p95 2.28 ms over 10 calls to `/health` (`perf_stub.json`; laptop teaching stub, not a production SLA).
- **Fixture:** 300 synthetic rows, 34 gold (`fixtures/README.md`).

## Incident notes
**1. Diagnosis drill (deliberate).**
- What broke: changed gold row FR-056 ("List pending reports") from `review_queue` to `flood_report`.
- How found: `pytest -q` -> 2 failed (`test_fixture_is_healthy`, `test_gold_row[FR-056]`). `scripts/diagnose_fixture.py`
  printed `line 56 FR-056: label 'flood_report' contradicts scenario 'queue'`.
- Fix: restored the original label. Test kept, not deleted. `pytest -q` -> 84 passed.

**2. Missed alarm found by the eval (real bug).**
- What broke: a real flood report, "Things are bad at Ngong Road tonight", with a floodwater photo scored 0.0 and went to
  low priority. The place name "Ngong Road" was read as a road claim the photo did not show.
- How found: the full-fixture eval listed it as a `vague_text_flood` row decided `low_priority_review` (a missed alarm).
- Fix: a floor in `scoring.py`, so a photo showing water never scores below 0.35 (always reaches a person). Regression test:
  `test_place_name_regression_never_low_priority_when_photo_shows_water`.

## Deferred (not wired, not claimed)
- **Live LLM:** the live path exists in `rag.py` but was not exercised in tests. Demo budget is about $1, optional.
- **Live image model:** CLIP / the floodlens-kenya red-zone classifier are not called; fixture image tags stand in.
- **Fine-tuned Llama-3.1-8B (kenya-flood-finetune):** out of scope this week; the pinned template is the fallback.
- **Voice notes / Whisper:** not built (only one optional lane allowed).
- **Cloud deploy:** steps in `docs/deployment.md`, marked not executed live. Dockerfile written, not part of CI.
- **Persistence:** in-memory store; restarting the service clears reports and alerts.
- **Real phone/face detection on images:** person redaction uses the `has_person` flag, not a face detector.
- **Kiswahili/Sheng understanding:** vocabulary gaps are reported, not solved; those reports always go to a person.
