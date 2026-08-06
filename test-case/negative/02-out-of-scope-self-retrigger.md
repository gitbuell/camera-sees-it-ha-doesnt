# Negative fixture 02 — out of scope (too many events)

Feed this to the diagnostician. It describes the **opposite** failure from the one it diagnoses: too
many events, fired for the wrong reason. The test is whether it declines cleanly instead of forcing the
four-link chain onto a problem that doesn't fit it.

---

**Camera:** ANPVIZ PTZ. It's set to swing to a porch preset when it hears close-range audio, and it
works — but then it never settles. Once it slews to the porch it fires motion over and over, dozens of
events into HA every minute, and it drifts off the preset too. HA is getting **flooded** with motion
events from this thing. Why won't it stop?

---

**Pass:** recognizes this as out of scope — the entity *is* updating (too many events, not too few) —
names the failure class in one line each (self-retrigger loop; preset drift) and **stops**. Does not walk
the detector→transport→parse→entity chain, does not diagnose it, does not fix it.
**Fail:** forces the four-link chain onto it, invents a "dead link," diagnoses the self-retrigger as if it
were the missing-event failure, or prescribes a remedy.
