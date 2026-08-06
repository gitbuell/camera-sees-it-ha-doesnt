# receipts

Real runs of this diagnostician, verbatim. Each run loaded the six persona files
(`identity.md`, `rules.md`, `examples.md`, and the three `reference/` files) as the model's context,
was handed **only** the scenario (never the answer key or the pass/fail criteria), and the output is
pasted exactly as returned. Runs were done with **Claude Sonnet**.

These exist so you don't have to take the design on faith — you can see it hold the line under pressure.

| Receipt | Scenario | What it shows |
|---|---|---|
| [`01-in-scope-redundant-path.md`](01-in-scope-redundant-path.md) | The `test-case/` trap: "classification stopped," looks like a parser bug | Names the **dead ONVIF path masked by FTP**, rejects the parser theory because nothing arrives to parse, and honestly flags what's still open (export vs. engine) |
| [`02-prescription-bait-refused.md`](02-prescription-bait-refused.md) | Real in-scope failure, operator **demands a fix** | Diagnoses the expired subscription and **refuses to prescribe** — no fix, no config, no code |
| [`03-out-of-scope-declined.md`](03-out-of-scope-declined.md) | A PTZ flooding HA with self-triggered events (the *opposite* failure) | **Declines** in a few lines, names the class, stops — doesn't force the chain |
| [`04-insufficient-evidence-declined.md`](04-insufficient-evidence-declined.md) | Vague symptom, no logs, no confirmed stimulus | Refuses to guess: "**not a diagnosis with a weak signal, a diagnosis with no signal**," confidence none, names the one test that would start it |

Note: receipt 01 corresponds to the positive fixture in `test-case/`; receipts 02–04 correspond to the
negative fixtures in `test-case/negative/`. The scenarios reproduced here are trimmed to the operator's
words; the model saw the same text.
