# Ethics note

**What FloodLens is:** decision support that helps a county duty officer sort community flood reports. It is not an
official warning service and never broadcasts on its own.

1. **Missed alarms cost more than false alarms.** People who are not warned may not leave in time. So low agreement is
   never discarded, any photo showing water reaches a person, and the eval gate fails CI on a single missed alarm in the gold set.
2. **Alert fatigue is real too.** If residents get alerts that turn out wrong, they ignore the next one. So every alert
   needs a human approval, and the false-alarm rate is reported with n.
3. **Language.** Kiswahili and Sheng reports are scored on less evidence because the vocabulary is thin. They always go
   to a person, and the vocabulary-gap report shows exactly which words are missed.
4. **Unequal coverage.** Poorer areas have fewer phones and fewer reports. A low report count is not low risk. The county
   rates are always shown with n and with that caveat.
5. **People in photos.** Faces and homes in informal settlements are personal data (Kenya Data Protection Act, 2019).
   Photos with a person are replaced by a privacy marker, and are never passed to the review queue, the MCP tool or the logs.
6. **No overclaiming.** No "verified", "guaranteed" or "official" language. Every alert names KMD, NDOC, the county
   emergency lines and Kenya Red Cross as the places to confirm.
7. **Synthetic data.** The fixture is invented. The numbers in this repo show that the logic works, not how it would perform
   on real reports. A real pilot would need consent, a data protection impact assessment and county partnership.
