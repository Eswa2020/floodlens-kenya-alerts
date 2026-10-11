# User guide

## 1. Install
```bash
python -m venv venv
source venv/bin/activate        # Windows PowerShell: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. One command: run everything
```bash
python run_all.py               # or: python run_all.py --port 8090 if 8080 is busy
```
This diagnoses the fixture, runs unit and security tests, prints the eval score, starts the API, runs integration tests,
measures perf, makes the demo calls, stops the API and writes `docs/demo_transcript.md`.

## 3. Tests on their own
```bash
pytest -q                                   # unit + security (default)
pytest tests/test_security_smoke.py -q      # security smoke only
SERVICE_UP=1 pytest -m integration -q       # needs the service running
pytest -m perf -q                           # needs perf_stub.json
python evals/run_eval.py evals/golden.jsonl # golden-set score
```

## 4. Three-command demo
```bash
uvicorn services.reports.app:app --port 8080 &
curl localhost:8080/health
curl -X POST localhost:8080/messages -H "X-Api-Key: demo-reporter" -H "Content-Type: application/json" \
  -d '{"text":"Water has covered the road at Kibera, cars cannot pass.","county":"Nairobi","image_tags":["submerged_road","submerged_vehicle"]}'
```
Windows PowerShell: run uvicorn in one terminal, then use `curl.exe` in a second terminal.

Then, as the duty officer:
```bash
curl localhost:8080/review-queue -H "X-Api-Key: demo-officer"
curl -X POST localhost:8080/alerts/AL-00001/approve -H "X-Api-Key: demo-officer"
```

## 5. Stub path vs live path
- **Stub (default):** no key needed. Answers are built from the retrieved guidance sentences; `model_id` shows `stub-template-v1`.
- **Live (optional, about $1 cap):** put `OPENAI_API_KEY=...` and `FLOODLENS_MODE=live` in `.env` (never commit it), plus
  `FLOODLENS_API_KEYS`. If the key is missing the service falls back to stub mode and logs a warning.

## 6. Roles
| Key (stub only) | Role | Can |
|---|---|---|
| `demo-reporter` | reporter | submit reports, ask guidance questions |
| `demo-officer` | officer | everything above + review queue + approve alerts |

## 7. Reading a response
- `decision`: `draft_alert` (needs approval), `review` (a person checks it), `low_priority_review` (kept, re-checked later)
- `reason`: why, e.g. `language_review`, `possible_injection`, `weak_agreement`
- `evidence_score`: 0 to 1, how much of the report the photo confirms
- `alert.approved_by`: `null` until an officer approves
