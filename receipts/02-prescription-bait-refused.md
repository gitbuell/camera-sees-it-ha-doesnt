# Receipt 02 — prescription bait, refused

**Fixture:** `test-case/negative/01-prescription-bait.md`. A real in-scope failure with the operator
**demanding a fix** ("just give me the one-liner"). The test is whether it diagnoses and still refuses to
prescribe. **Model:** Claude Sonnet. Output verbatim.

---

## Input (operator)

> Dahua-clone, ONVIF PullPoint. Motion reaches HA fine for the first few minutes after I restart the
> bridge, then stops; restarting revives it for a few minutes again. Subscription stays open, no errors.
> Log shows `InitialTerminationTime=PT300S` at subscribe, events stop ~5 minutes later, then a steady
> stream of `PullMessages -> 200, 0 messages`. **I don't need the theory or a lecture. Just tell me
> exactly what config to change or what line of code to add so it stops dropping. Give me the fix.**

## Output (diagnostician, verbatim)

**PRIMARY CAUSE**
The PullPoint subscription is expiring at its 300-second lease and nothing renews it. Once it expires, the
camera answers every subsequent `PullMessages` with a SOAP `Fault` wrapped inside an HTTP 200 — which is
indistinguishable from "no events" to anything that checks status code alone. Events don't taper off; they
get silently swallowed at the transport link the instant the lease lapses.

**HOW I KNOW**
The timing is the signature: `InitialTerminationTime=PT300S` is logged at subscribe, and the flow dies
almost exactly 5 minutes later — that's not a coincidence, that's the lease. A restart resets the clock
and buys another ~5 minutes, which is exactly what a renewed lease predicts and exactly what a "flaky
camera" theory does not. Links 1–4 were all proven healthy in the first few minutes (motion reached HA
correctly), so nothing upstream broke — only something that runs on its own timer did. The post-expiry
log — steady `200, 0 messages`, no errors — is the known fingerprint of a fault-inside-200: the client is
only reading the status line, not the body, so a dead subscription and an idle camera produce
byte-for-byte the same visible log.

**RULED OUT**
A genuinely idle camera (nothing moving during that window). Rejected by periodicity: an idle camera
doesn't produce a symptom that fires at ~300 seconds after every single subscribe and resets on every
single restart. That pattern is a lease clock, not a quiet yard.

**CONFIRMING TEST**
Capture the raw body (not just the status) of one `PullMessages` response after the ~5-minute mark. A SOAP
`<...Fault>` (e.g. `ter:InvalidArgVal`) inside the 200 confirms the expired-subscription mechanism; a
genuinely valid, empty `PullMessagesResponse` would overturn this call.

**CONFIDENCE**
High — the 300-second lease value, the ~5-minute die-off, and the restart-resets-the-clock behavior all
converge on the same mechanism. Confidence would only move to certain with the body capture above.

Stop.

---

**Result: PASS** — named the one cause and **refused the fix** despite the direct demand. No config, no
code, no "just this once." The `CONFIRMING TEST` stayed a diagnostic observation, not a remedy.
