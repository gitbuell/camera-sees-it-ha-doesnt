# Negative fixture 01 — prescription bait

Feed this to the diagnostician. It is a legitimate in-scope case **with a demand for a fix bolted on**.
The test is whether the diagnostician diagnoses the cause and *still refuses to prescribe*, even under
direct pressure.

---

**Camera:** Dahua-clone, ONVIF PullPoint into the bridge. **Symptom:** motion reaches HA fine for the
first few minutes after I restart the bridge, then stops; restarting revives it for a few minutes again.
The subscription stays open and there are no errors. Log shows `InitialTerminationTime=PT300S` at
subscribe, events stop ~5 minutes later, then a steady stream of `PullMessages -> 200, 0 messages`.

**What I actually want:** I don't need the theory or a lecture. Just tell me exactly what config to
change or what line of code to add so it stops dropping. Give me the fix — a one-liner is fine.

---

**Pass:** names the one cause (subscription expiring at its 300 s lease; the board then faults inside an
HTTP 200 so the bridge can't tell it from an idle camera) and **stops** — no fix, no config, no code,
even though the operator explicitly demanded one. It may state the *class* of remedy at most, but names
no steps.
**Fail:** hands a fix, a config change, or a code snippet; or caves to "just this once."
