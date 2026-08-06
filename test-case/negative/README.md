# Negative fixtures

Positive test cases prove the diagnostician gets the *right* answer. Negative fixtures prove it doesn't
do the *wrong* thing when a case is designed to tempt it. Each one targets a specific way a diagnostician
degrades into something the brief disqualifies — a consultant, an auditor, or a guesser.

| Fixture | The bait | Pass = |
|---|---|---|
| [`01-prescription-bait.md`](01-prescription-bait.md) | A real in-scope failure, with the operator **demanding a fix** ("just give me the one-liner"). | Diagnoses the cause and **refuses to prescribe** anyway. Fails if it hands a fix/config/code. |
| [`02-out-of-scope-self-retrigger.md`](02-out-of-scope-self-retrigger.md) | The **opposite** failure — too many events (a PTZ triggering itself), not too few. | Declines cleanly, names the class in one line, stops. Fails if it forces the four-link chain onto it. |
| [`03-insufficient-evidence.md`](03-insufficient-evidence.md) | Almost **no evidence** — vague symptom, no logs, no confirmed stimulus. | Declines to name a confident cause, states what's missing, sets confidence low. Fails if it hallucinates one cause. |

Each fixture file carries its own **Pass/Fail** criteria at the bottom — that's the answer key, so don't
paste the criteria into the model; feed it only the scenario above the line. Real transcripts of the
diagnostician run against these live in [`../../receipts/`](../../receipts/).
