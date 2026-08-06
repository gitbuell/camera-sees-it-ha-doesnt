# Receipt 01 — in-scope, redundant-path masking (the `test-case/` trap)

**Fixture:** `test-case/scenario.md` + `test-case/bridge-log.txt`. Surface symptom ("plain motion works,
classification stopped") is built to look like the Example-2 parser bug but is a dead ONVIF path masked
by an FTP fallback. **Model:** Claude Sonnet. Output verbatim.

---

## Input (operator)

> Camera "driveway", a Dahua-OEM box, firmware ~2023, wired into the bridge two ways at once: ONVIF
> PullPoint (primary) and the camera's own FTP-on-alarm as a fallback. Plain motion still works fine in
> HA, but person/vehicle classification stopped coming through about a week ago; my classification
> automations haven't fired since. I've spent two days in my class-parsing code assuming it broke — but
> that code hasn't changed in months. I confirmed a walk-through at 14:32 today. [bridge log tail: every
> `[onvif] PullMessages -> 200, 0 messages`, no `NotificationMessage`; every `motion ON` in the last 7
> days coincides with an `[ftp]` login; re-subscribe timer confirmed working.]

## Output (diagnostician, verbatim)

**PRIMARY CAUSE**
ONVIF PullPoint transport is completely dead on this camera — not just for classification, for
everything. It has delivered zero `NotificationMessage`s in seven days, subscription mechanics
notwithstanding. Because classification only ever rides ONVIF (FTP-on-alarm carries plain motion only,
per the wiring), a total ONVIF outage presents as nothing but "classification stopped" — the FTP fallback
keeps plain motion alive and masks the fact that one whole delivery path died.

**HOW I KNOW**
Link 1 (detector) is proven alive independent of ONVIF: at 14:32:07 the camera's own on-alarm FTP action
fired — that upload is triggered by the camera's onboard alarm output, not by anything downstream — so
the detector unquestionably fired on the confirmed 14:32 walk-through. Thirteen seconds later, at
14:32:20, `PullMessages` on a subscription that was only ~2.5 minutes old (well inside its `PT240S` lease
and its 200s renewal window) returned `200 / 0 messages`. That rules out staleness as the explanation for
that particular gap — a fresh, unexpired subscription saw nothing for an alarm the camera itself was
actively firing on. The 14:34:00 re-subscribe then completes cleanly (`Unsubscribe old + new pullpoint
OK`), and `PullMessages` immediately after is still `0 messages`. Zero content survives a subscription
refresh — that's not a lease-expiry signature (which would show a working window, then silence, tied to
the lease clock); it's silence in every window, before and after renewal, for a week straight. And the
7-day pattern seals it: every single motion event correlates with FTP, none with ONVIF — a 100% split,
not an intermittent one.

**RULED OUT**
The operator's own theory — that the class-parsing code broke. Rejected because there is nothing arriving
for it to mishandle: the bridge log shows zero `NotificationMessage`s of any kind over ONVIF for the
entire week, plain-motion-carrying or classification-carrying. A parser bug (like a branch that swallows
the class field) requires the field to arrive on the wire first; here the wire is empty. Two days spent on
that code was aimed at link 3 when the break is at link 2.

**CONFIRMING TEST**
Pull the camera's own onboard alarm/event log (independent of both ONVIF and FTP) for the 14:32:07 window
and check whether it recorded a classified alarm (e.g., a `Human`/`Vehicle`-tagged entry) at that
timestamp. If it did, the classification engine and detector are both firing correctly and the break is
purely in ONVIF's notification export off the camera. If the on-camera log shows only a
generic/unclassified alarm at that moment, the break sits one step earlier — the classification engine
itself isn't running, and FTP-on-alarm is riding a simpler trigger than the analytics pipeline that ONVIF
would have carried.

**CONFIDENCE**
Medium-high. That ONVIF transport is completely dead, independent of subscription lifecycle, is well
pinned by the fresh-subscription-still-silent evidence and the clean 7-day 100%/0% split. What's still
open is whether the dead link is ONVIF's notification export specifically or the on-camera classification
engine one step upstream of it — the on-camera alarm log is the one piece of evidence that would close
that gap.

Stop.

---

**Result: PASS** — matched the answer key (dead ONVIF path masked by FTP; parser theory rejected because
nothing arrives to parse). Went *beyond* the key by flagging an open sub-question — ONVIF export dead vs.
classification engine dead — and naming the single observation that resolves it. Honest confidence, no fix.
