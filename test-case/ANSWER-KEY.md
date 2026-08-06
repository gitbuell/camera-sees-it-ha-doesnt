# Answer key

> **Do NOT load this file into the diagnostician's context.** It contains the answer. It exists so *you*
> can check whether the diagnostician got it right. Feed the model `scenario.md` + `bridge-log.txt` only.

## What this fixture tests

One thing: can the diagnostician tell a **dead transport masked by a redundant path**
(`reference/failure-modes.md` → 2c) apart from the **branch-discard parser bug** (3a / Example 2)? Both
produce the *identical* surface symptom — "plain motion works, classification is gone" — and the
operator's own theory ("my parser broke") points at the wrong one. It also has to *not* mistake this for
the expired-subscription cause (Example 1), which the log deliberately rules out.

## Expected diagnosis

**PRIMARY CAUSE** — The ONVIF event path is fully dead (link 2, transport): every `PullMessages` returns
`200 / 0 messages` with no `NotificationMessage`, across the confirmed 14:32 walk and the whole week.
Plain motion survives *only* because the redundant **FTP-on-alarm** path is carrying it — every
`motion ON` coincides with an `[ftp]` login. Classification is gone because it rode ONVIF **exclusively**;
FTP-on-alarm can signal "something happened," never "it was a vehicle."

**HOW I KNOW** — Link 1 is confirmed (a real walk at 14:32; FTP snapshots are firing). Motion reaches HA,
so link 4 works. But every motion event is triggered by an `[ftp]` login while the ONVIF side delivers
zero messages the entire capture — despite a healthy, renewing subscription. A dead ONVIF path explains
*both* facts at once: plain motion alive (FTP) and classification gone (ONVIF-only).

**RULED OUT** — The parser (the operator's theory, and Example 2's branch-discard). Rejected because no
ONVIF `NotificationMessage` arrives at all — there is no `ClassTypes` field reaching the parser to
discard. You cannot blame a parser for data that never arrives. (Example 2 was the opposite: a wire
capture *showed* `ClassTypes` arriving intact.)

**CONFIRMING TEST** — During a confirmed walk, capture the ONVIF `PullMessages` bodies: expect zero
`NotificationMessage`s while the same walk produces an `[ftp] login → motion ON`. That coincidence — FTP
carrying every event, ONVIF carrying none — confirms the masking. *(An observation, not a fix.)*

**CONFIDENCE** — High. The log shows both paths' behavior directly, and the working re-subscribe line
(`Unsubscribe old + new pullpoint OK`) closes off the Example-1 expiry alternative.

## Scoring

A strong answer:
- ✅ Names the **dead ONVIF transport, masked by the FTP fallback**, as the one cause.
- ✅ Rejects the parser theory **specifically because no class data is arriving to parse**.
- ✅ Distinguishes this from Example 1 (expiry — ruled out by the healthy re-subscribe) and Example 2
  (branch-discard — ruled out because nothing arrives).
- ✅ Offers a confirming test that is an *observation*, not a fix.

Fails if it:
- ❌ Blames the class parser / tells them to reorder an `if/elif` (that's Example 2, and a fix).
- ❌ Lists both "dead path" and "parser bug" without committing to one.
- ❌ Prescribes a remedy (re-subscribe, switch cameras, rewrite the bridge).
