# Receipt 03 — out of scope, declined

**Fixture:** `test-case/negative/02-out-of-scope-self-retrigger.md`. The *opposite* failure — too many
events, fired for the wrong reason. The test is a clean decline, not a forced diagnosis. **Model:** Claude
Sonnet. Output verbatim.

---

## Input (operator)

> ANPVIZ PTZ camera. It's set to swing to a porch preset when it hears close-range audio, and it works —
> but then it never settles. Once it slews to the porch it fires motion over and over, dozens of events
> into HA every minute, and it drifts off the preset too. HA is getting flooded with motion events from
> this thing. Why won't it stop?

## Output (diagnostician, verbatim)

This report is out of scope for this diagnostician.

Self-retrigger / aiming-failure class — a PTZ that slews to a preset on close-range audio and then
re-triggers on its own motor/mic movement, drifting off-target and flooding HA with repeat events. That
is the *opposite* failure this diagnostician handles: too many/wrong events, not a missing one.

Stop.

---

**Result: PASS** — recognized the too-many-events shape, named the failure class in two lines, and
stopped. Did not walk the four-link chain, invent a dead link, or prescribe anything.
