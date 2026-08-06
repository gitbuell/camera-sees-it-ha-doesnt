# reference: evidence-checklist

What to feed the diagnostician so it can locate the dead link instead of guessing. You don't need all of
it — but the more links you can supply evidence for, the earlier and more confidently the break can be
pinned. Bring what you have; the diagnostician will tell you which missing piece would decide an
otherwise-tied call.

---

## Always include

- **Camera make / model / OEM lineage** — Hikvision, Dahua/IC-Realtime, or a XiongMai-OEM board / ANPVIZ
  / generic N601L rebrand. Behavior differs sharply across these.
- **Firmware version and rough date.** This is not optional trivia — the cosmetic-shim behavior
  (failure-mode 1a) and ONVIF write reliability are *firmware-dependent*. "Older" vs. "2024+" changes the
  diagnosis.
- **The delivery method** — ONVIF PullPoint, Hik ISAPI `alertStream`, or the camera's own
  FTP/snapshot-on-alarm. And whether **more than one** path is wired at once (this is what hides outages —
  failure-mode 2c).
- **The exact symptom, precisely stated.** These three are different diagnoses:
  - "Never worked — HA has never seen motion from this camera."
  - "Worked, then went quiet after a few minutes" (and does a restart revive it?).
  - "Plain motion works, but person/vehicle classification never arrives."

## The single most useful artifact: a log with timestamps

In rough order of diagnostic power:

1. **The bridge log across a confirmed motion event** — ideally a `subscribe` line (does it show
   `InitialTerminationTime` / a lease?), the `PullMessages` responses, and any `motion ON/OFF`. Timestamps
   matter: the *periodicity* is often the whole diagnosis (the 5-minute cliff of an expired subscription).
2. **The camera's own alarm / event log** for the same wall-clock window — this is how link 1 (did the
   detector actually fire?) is verified independently of everything downstream.
3. **A raw event body off the wire** — the actual ONVIF `NotificationMessage` / SOAP payload. This is what
   proves whether `ClassTypes` arrived intact (failure-mode 3a) and whether a "200" is hiding a `Fault`
   (2a/3b). Status codes alone can't show either.
4. **The retained MQTT state topic** at the broker — to separate a bridge that isn't publishing from HA
   that isn't updating (link 4).

## Confirm the stimulus

Whatever window your log covers, say **what actually happened in view** during it: "I walked the yard at
12:02," "a car passed at 12:47." A log over an unconfirmed-quiet window can't tell a dead detector from
an empty scene (principle 1). No confirmed stimulus = the strongest evidence you can bring is missing.

## How you captured it matters — a warning

If your evidence came from a **test listener you attached** (a standalone subscriber, a fresh
subscription "just to check"), say so explicitly. On single-subscriber boards that very act can starve
the production path and manufacture the silence you're trying to explain (failure-mode X / principle 6).
Evidence from **observing the already-running bridge** (its own log, or a live trace of the live process)
is far safer than evidence from a competing subscription — and a *fresh* test subscription can "work"
precisely because it hasn't expired yet, hiding the real bug.

---

## Quick template to paste

```
Camera:        <make / model / OEM lineage>
Firmware:      <version + approx date>
Delivery:      <ONVIF PullPoint | Hik alertStream | FTP-on-alarm> (any second path? __)
Symptom:       <never worked | worked-then-quiet | classification-missing | other>
Restart revives it?   <yes / no / n/a>
Confirmed stimulus:   <what moved in view, and when>
Evidence source:      <bridge's own log | camera's own log | wire capture | attached test listener>
--- paste log / event body below ---
```
