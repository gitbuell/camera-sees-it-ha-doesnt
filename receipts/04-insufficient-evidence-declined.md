# Receipt 04 — insufficient evidence, declined

**Fixture:** `test-case/negative/03-insufficient-evidence.md`. Almost nothing to go on — vague symptom, no
logs, no confirmed stimulus. The test is whether it refuses to name a confident cause instead of
hallucinating one. **Model:** Claude Sonnet. Output verbatim.

---

## Input (operator)

> "One of my cameras" — I don't remember the model offhand. It stopped showing motion in HA sometime this
> week. I think it's the camera itself. I don't have any logs handy, I haven't looked at the camera's own
> event log, and I wasn't watching to see whether anything actually moved while HA was quiet. Which link
> is broken?

## Output (diagnostician, verbatim)

**PRIMARY CAUSE**
Not locatable from what's here. No link in the chain — detector, transport, parse, or entity — has been
checked, so nothing can be pinned yet. That includes link 1: "I think it's the camera itself" is the
operator's guess about link 1, not a finding from link 1.

**HOW I KNOW**
Rule one of this method: start where the operator's certainty ends. Here it ends before the chain even
starts. No model/firmware, so no model-specific likelihoods apply. No bridge log, so links 2–3 are unread.
No check of the camera's *own* alarm/event log, so link 1 — the one link required to independently confirm
"the camera detects" before trusting that claim — is unverified; "I think it's the camera" is exactly the
assumption this method exists to test, not evidence for it. And most load-bearing: the quiet window itself
is unconfirmed — nothing is known to have moved in the camera's field of view while HA was silent. A quiet
window with no confirmed stimulus proves nothing; it can't distinguish "the signal died somewhere in the
chain" from "nothing has walked past this camera in a week."

**RULED OUT**
"It's the camera itself" (the operator's own theory, link 1) — not ruled out, because it can't be
evaluated at all yet. It's an untested claim about the earliest link, and the one artifact that would test
it (the camera's own event log, read during a confirmed stimulus) hasn't been looked at.

**CONFIRMING TEST**
Walk into the camera's frame deliberately, at a known timestamp, and read the camera's *own* alarm/event
log (not ONVIF, not the bridge, not HA) for that window. That single observation resolves the earliest
possible branch point: if the camera's own log shows the event, link 1 is proven healthy and the break is
downstream; if it doesn't, link 1 is the story and everything past it is moot. *(An observation, not a
fix.)*

**CONFIDENCE**
None yet — this isn't a diagnosis with a weak signal, it's a diagnosis with no signal. It rises the moment
a confirmed stimulus is checked against the camera's own log; until then any named cause, including "it's
the camera," would be a guess dressed as a finding.

**Stop.**

---

**Result: PASS** — refused to invent a cause from nothing, named exactly what evidence is missing and the
one test that would start the diagnosis, and set confidence to none. Honest uncertainty delivered as a
diagnosis, not a checklist.
