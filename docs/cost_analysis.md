# Cost analysis

Stub mode costs nothing: CI and tests never call a live key. Live calls are capped at about $1 for the Thursday demo.

## Teaching cost table
| Call type | Calls (n) | Unit cost | Total | Assumptions |
|---|---|---|---|---|
| Stub tests (pytest, CI) | 0 | $0 | $0 | CI never calls a live key |
| Golden-set eval (stub) | 0 | $0 | $0 | Deterministic scorer + stub answers |
| Image scoring | 0 | $0 | $0 | Fixture image tags stand in for the classifier |
| Thursday demo (live, optional) | ~10 | ~$0.0002 | ~$0.002 | gpt-4o-mini, ~700 input + ~150 output tokens per call |
| Budget ceiling for the demo | | | ~$1 | Hard cap from the course brief; real use is far below it |

## Cost per 1,000 reports (live mode, teaching estimate)
| Item | Count | Unit | Total |
|---|---|---|---|
| Reports scored (no LLM) | 1,000 | $0 | $0 |
| Alert drafts (about 45% of flood reports, from the county table) | ~450 | ~$0.0002 | ~$0.09 |
| Guidance questions (if 20% of traffic) | ~200 | ~$0.0002 | ~$0.04 |
| **Total** | | | **~$0.13 per 1,000 reports** |

## Assumptions (check before relying on them)
- Price used: gpt-4o-mini at about $0.15 per 1M input tokens and $0.60 per 1M output tokens. This is a teaching estimate,
  so confirm current pricing before any budget decision.
- Token counts are estimated from the prompt template plus 2 retrieved passages, not measured from a live run.
- Scoring is rule-based and free. A live CLIP or classifier encoder would add compute cost (batch by tile + date and cache).

## Cost levers already in the design
- The LLM is only called for draft alerts and guidance, never for every report.
- Low-agreement and low-priority reports never trigger a model call.
- `max_tokens=250`, `temperature=0` on the live path.
