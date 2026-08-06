# reference: failure-modes

The catalog of causes for *"camera detects, HA doesn't hear it."* Each is placed on the four-link chain
(`detector → transport → parse → entity`), with the **fingerprint** that identifies it in evidence and
a rough **likelihood** on cheap OEM hardware. Use this to name the earliest dead link — not to hand the
operator a checklist.

The chain, for reference:

```
[1] detector fires  →  [2] camera transports  →  [3] bridge parses  →  [4] HA entity updates
```

---

## Link 1 — Detector didn't actually fire

### 1a. Cosmetic-shim detection enable (firmware-dependent)
- **Link:** 1 (detector). **Likelihood:** high on older XiongMai-OEM / ANPVIZ firmware.
- **Mechanism:** ONVIF (or an API) write that "enables motion detection" is accepted, normalized, and
  echoed back — but does not drive the real detector on this firmware. The vendor web UI reflects the
  true state; the ONVIF write does not.
- **Fingerprint:** detection appears enabled via ONVIF/readback, yet the camera's *own* alarm log shows
  no events during confirmed motion. An identical newer-firmware sibling behaves differently. The write
  "succeeded" but changed nothing.
- **Caveat:** newer firmware *does* honor these writes. Never conclude from the vendor name alone —
  settle it with an independent read of behavior (the camera's own log during confirmed motion).

### 1b. "Detects" is a recording schedule, not the motion detector
- **Link:** 1. **Likelihood:** medium — it's the operator's assumption more than a device fault.
- **Mechanism:** the operator's proof that "the camera detects" is a vendor-app recording, which was
  produced by continuous/scheduled recording, not by the motion detector firing.
- **Fingerprint:** recordings exist at a steady cadence unrelated to actual events; the camera's motion
  event list is empty even though "there's footage."

---

## Link 2 — Event fired but never transported

### 2a. Expired pull-point subscription (the classic)
- **Link:** 2 (transport). **Likelihood:** very high wherever nothing renews the lease.
- **Mechanism:** the PullPoint subscription is created with a short `InitialTerminationTime` (commonly
  `PT300S` — a 5-minute lease, not a connection). Nothing renews it. After expiry the board answers every
  `PullMessages` with a SOAP `Fault` **wrapped in an HTTP 200**, indistinguishable from "no events" to a
  client that only checks the status code.
- **Fingerprint:** events flow for ~5 minutes after every (re)subscribe, then stop; a restart resets the
  clock and it repeats; the post-expiry log is a stream of `200 / 0 messages` with no errors. The
  periodicity is the giveaway.

### 2b. Busy-wait after expiry (a consequence of 2a, sometimes the presenting symptom)
- **Link:** 2. **Likelihood:** follows 2a on affected boards.
- **Mechanism:** the faulting-`200` from an expired subscription returns *instantly* instead of honoring
  the long-poll timeout, so the pull loop becomes a busy-wait — high CPU and thousands of requests per
  minute hammering the camera, still delivering zero events.
- **Fingerprint:** CPU spike on the bridge host + a flood of connections to the camera, with no motion
  reaching HA. Presents as "high CPU / camera hammered" but the root is the same expired subscription.

### 2c. Vendor push is a dead path; the feature survives on a redundant one
- **Link:** 2. **Likelihood:** medium where two delivery paths were wired (ONVIF push + FTP/snapshot-on-alarm).
- **Mechanism:** the richer path (ONVIF events, carrying classification) dies completely, while a
  redundant path (e.g. FTP-on-alarm firing plain motion) keeps the headline sensor alive. The only
  symptom is a *lost capability* (classification), not a dead sensor — so it reads as a parser bug.
- **Fingerprint:** plain motion works; a specific richer signal (person/vehicle class, or events from one
  particular camera) is 100% absent. Health looks fine because the merged result still updates.

### 2d. XiongMai-OEM ONVIF push is unreliable by nature
- **Link:** 2. **Likelihood:** high on older OEM boards specifically.
- **Mechanism:** the board detects and records fine, but its ONVIF live-event push is flaky-to-dead —
  adequate for the camera's own recording, weak as a real-time HA trigger.
- **Fingerprint:** the camera's own alarm log shows events (`alarm(type=…)`) within a second of a
  confirmed walk, while the ONVIF subscription delivers nothing for the same event.

---

## Link 3 — Transported but parsed/handled wrong

### 3a. Class silently discarded by branch ordering
- **Link:** 3 (parse). **Likelihood:** high wherever a handler treats motion and class as either/or.
- **Mechanism:** the event carries `State=true` **and** `ClassTypes=…` on the *same* message; an
  `if State … elif ClassTypes …` handler matches the boolean branch and never evaluates the class branch.
  The field is well-formed and present — it is simply never read.
- **Fingerprint:** plain motion works perfectly; classification never fires; a raw wire capture shows
  `ClassTypes` arriving intact on a `MotionAlarm` message. No errors anywhere — the tell is the *absence*
  of errors combined with working plain motion.

### 3b. Fault-inside-200 not detected by the client
- **Link:** 3. **Likelihood:** the parse-side twin of 2a.
- **Mechanism:** the bridge's HTTP client only raises on non-2xx, so a SOAP `Fault` returned inside a 200
  passes as a valid-but-empty response. The bridge never learns the subscription is dead.
- **Fingerprint:** identical to 2a from the log — the distinction is *where you'd intervene*, not what you
  see. Body contains `<...Fault>`; status is 200.

---

## Link 4 — Parsed correctly but never reaches HA

### 4a. MQTT delivery / discovery / retained-state issue
- **Link:** 4 (entity). **Likelihood:** lower for a bridge that was ever working; check it last.
- **Mechanism:** the bridge publishes but HA doesn't update — broker unreachable, discovery topic wrong
  or not retained, availability topic stuck `offline`, or a state topic mismatch.
- **Fingerprint:** the bridge log shows motion published, but the broker's retained state topic doesn't
  change, or HA shows the entity `unavailable`. Confirm at the broker (subscribe to the raw topic), not
  in HA's UI.

---

## The observation trap (not a device fault — a method fault that fakes one)

### X. Single-subscriber starvation
- **Link:** none — it corrupts your *measurement* of links 2–3.
- **Mechanism:** the board serves exactly one event subscription. Attaching a second "just to check"
  displaces the production bridge's subscription, so your test both sees nothing *and* causes an outage
  in the real path.
- **Fingerprint:** production automations go dark exactly when your test listener starts and recover when
  it stops; the test's only "event" is a subscribe-time `Initialized` snapshot. Never read "my listener
  saw nothing" as "the camera is silent." Observe the live production process instead of attaching a
  competitor.

---

## Ranking guide

When more than one fingerprint matches, the primary cause is the **earliest dead link** (§2 of
`rules.md`). Rough order of prior likelihood on cheap OEM hardware, worst offenders first:

1. **2a — expired pull-point subscription** (the single most common real cause of "worked then quiet").
2. **1a — cosmetic-shim detection enable** (when it *never* worked on older OEM firmware).
3. **3a — class discarded by branch ordering** (when plain motion works but classification never does).
4. **2c / 2d — dead/unreliable push masked by a redundant path** (when a *capability* is missing, not the
   whole sensor).
5. **X — single-subscriber starvation** (whenever the evidence came from an attached test listener).
6. **4a — MQTT/HA delivery** (check last on a bridge that ever worked).
