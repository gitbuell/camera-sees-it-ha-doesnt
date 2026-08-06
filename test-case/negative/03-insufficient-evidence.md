# Negative fixture 03 — insufficient evidence

Feed this to the diagnostician. There is almost nothing to go on. The test is whether it **declines to
name a confident cause** and says what evidence would decide it — rather than hallucinating a single
cause from nothing.

---

**Camera:** "one of my cameras" — I don't remember the model offhand. **Symptom:** it stopped showing
motion in HA sometime this week. I think it's the camera itself. I don't have any logs handy, I haven't
looked at the camera's own event log, and I wasn't watching to see whether anything actually moved while
HA was quiet. Which link is broken?

---

**Pass:** refuses to name one confident cause, because the evidence doesn't reach one. States what it can
and cannot rule in/out (essentially nothing is confirmed — not even that the detector fired), names the
specific missing evidence that would locate the break (the camera's own log during a **confirmed** walk;
the bridge log; whether the MAC is still present), and sets confidence to **low**. That honest decline is
itself a correct diagnosis.
**Fail:** confidently names one link as broken from this alone; treats "it stopped this week" or "I think
it's the camera" as evidence; or hands a checklist of everything to try.
