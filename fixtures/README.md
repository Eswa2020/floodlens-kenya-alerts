# Teaching fixture

- File: `flood_reports_sample.jsonl`, **300 rows** (rule: 200 to 500 rows)
- 100% synthetic, generated offline: `python scripts/make_fixture.py --rows 300`
- **No production scrape.** Place names are real county areas, but every report, phone number and email is invented.
  Phone numbers and emails exist only so redaction can be tested.
- 34 rows are marked `"gold": true` and copied to `evals/golden.jsonl` (known-good subset for the eval and unit tests).
- Flood-domain data only: no health or marketplace rows.

## Row fields
| field | meaning |
|---|---|
| id | FR-001 ... FR-300 |
| county | Nairobi, Kisumu, Tana River |
| language | en, sw, sheng |
| text | the community report or question |
| image_tags | stands in for the image classifier output (stub mode) |
| has_person | true if a person is visible in the photo (triggers photo redaction) |
| photo_ref | placeholder reference; no real photos are stored |
| label | expected route: flood_report, guidance_lookup, review_queue |
| truth | flood / no_flood / n/a (ground truth from the scenario, not from the scorer) |
| expected_decision | draft_alert / review / low_priority_review / n/a |
| scenario | which generator scenario produced the row |
| gold | part of the known-good subset |

## Scenario mix (300 rows)
strong flood 60, partial flood 17, hard partial 3, person in photo 10, PII in text 10, vague text 15, no image 15,
mismatch 30, not a flood 10, Kiswahili 25, Sheng 15, injection 10, guidance questions 50, hard guidance 5, queue 25.

The "hard" scenarios are deliberately difficult and are **not** gold: they keep the full-fixture score honest (below 1.0).

## Checks
`python scripts/diagnose_fixture.py fixtures/flood_reports_sample.jsonl` fails loudly on invalid JSON, comment lines,
missing fields, duplicate ids, unknown labels, or a row count outside 200 to 500.
