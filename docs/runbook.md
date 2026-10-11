# Runbook

| Symptom | Likely cause | Action |
|---|---|---|
| Service refuses to start: `pin check failed` | `alert_guidance_v1.txt` edited without re-pinning | Revert the edit, or bump `prompt_version`, update `prompt_sha256` in `pin.json`, re-run tests |
| All requests 401 in live mode | `FLOODLENS_API_KEYS` not set (fail closed by design) | Set the keys from the secret store; restart |
| `mode` shows `stub` when live was expected | `OPENAI_API_KEY` missing | Add it to `.env` or the secret store; check the warning in logs |
| CI fails on the eval gate | Scoring change caused a missed alarm or accuracy below 0.85 | Read `evals/last_score.json` errors; fix the rule, do not lower the gate |
| `diagnose_fixture.py` fails | Broken or edited fixture row | Read the line number it prints; fix the row; never delete the test |
| `run_all.py` says port busy | Another process on 8080 | `python run_all.py --port 8090` |
| Many Kiswahili/Sheng reports waiting | Expected: they always need a person | Add Kiswahili-speaking reviewers on shift; check `analytics/county_rates.json` vocab gaps |
| Possible injection reports | Someone trying to trigger alerts | Do not approve; review the text; the guard already blocked auto-drafting |
