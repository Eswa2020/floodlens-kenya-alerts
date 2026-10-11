# services/reports: flood report API

Adapted from the triage API pattern (FastAPI + auth + version header), reshaped for flood reports.

- Routes: `GET /health`, `POST /messages`, `GET /review-queue`, `POST /alerts/{alert_id}/approve`
- Auth: `X-Api-Key` header, roles `reporter` and `officer` (see `auth.py`)
- Pins: `prompts/pin.json` (prompt version + sha256, model ids, retriever, image encoder). The service refuses to start if the pins do not match.
- Version header: `X-Prompt-Version` on `/health`
- Logs carry ids, county, decision and score only. **Never log raw report text, phone numbers or photos.**
