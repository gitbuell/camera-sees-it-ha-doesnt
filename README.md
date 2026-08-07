# The Motion-Path Diagnostician

A folder-based AI diagnostician that answers one question:

> **Your camera detects motion — so why isn't it reaching Home Assistant?**

Drop this folder into a Claude project and Claude *becomes* the diagnostician. Feed it a broken
camera-to-HA motion setup and it tells you the **one** thing that's actually killing the signal, shows
you how it knows, and stops. It does not fix it for you. It does not hand you a checklist. It diagnoses.

---

## What it diagnoses

The specific, maddening failure where a cheap IP camera **clearly detects motion** — the vendor app
shows it, the on-camera log lists the alarm — but the Home Assistant `binary_sensor` stays silent, or
fires for plain motion while person/vehicle classification never arrives, or works for five minutes
after every restart and then dies.

It models the signal as a four-link chain —

```
detector fires  →  camera transports the event  →  bridge parses it  →  HA entity updates
```

— and finds the **first** link that's broken. That link is the cause; everything downstream is symptom.

## Who it's for

People running OEM/IoT cameras into Home Assistant through an ONVIF-PullPoint / ISAPI-alertStream → MQTT
bridge: XiongMai-OEM boards and their rebrands (ANPVIZ, generic N601L), alongside Hikvision and
Dahua/IC-Realtime. If you've ever stared at bridge code for a day because "the camera obviously works,"
this is built from that exact pain.

## How to use it

1. **Create a Claude project** and add every file in this folder to its knowledge.
2. **Describe your broken setup.** Paste what you have — camera model, firmware, the symptom, and the
   best log you can get. See [`reference/evidence-checklist.md`](reference/evidence-checklist.md) for
   what makes the diagnosis sharp (there's a paste-in template at the bottom of it).
3. **Read the diagnosis.** You'll get one named cause, the reasoning that locates it, and how the
   alternatives were ruled out. Then it stops.

## What you get back

A diagnosis in a fixed, five-slot format — and nothing else:

- **PRIMARY CAUSE** — the earliest broken link in the chain, in a sentence. Not a ranked list of twelve.
- **HOW I KNOW** — what in your evidence puts the break there, and why the links upstream are healthy.
- **RULED OUT** — the most tempting alternative (often your own theory), and why the evidence rejects it.
- **CONFIRMING TEST** — the one reading that would confirm or overturn the call. An *observation*, never a fix.
- **CONFIDENCE** — high / medium / low, honestly, with what's still open.

No fix, no config, no "try this instead." Naming *why* — and telling you the one test that could prove it
wrong — is the whole job. What to do about it is yours to decide (or a separate conversation).

## Try it before you trust it

The [`test-case/`](test-case/) folder is a ready-made broken setup: a real-shaped operator report
([`scenario.md`](test-case/scenario.md)) plus a bridge log ([`bridge-log.txt`](test-case/bridge-log.txt))
whose surface symptom ("plain motion works, classification stopped") is a deliberate trap — it looks like
a parser bug but isn't. Feed **those two files** to the diagnostician, then check its answer against
[`ANSWER-KEY.md`](test-case/ANSWER-KEY.md).

> ⚠️ Feed the model `scenario.md` + `bridge-log.txt` **only**. `ANSWER-KEY.md` is for you — don't load it
> into the diagnostician's context, and don't add `test-case/` to the Claude project's knowledge.

`test-case/negative/` adds three **negative** fixtures — a case that *demands a fix*, an out-of-scope
"too many events" case, and a case with almost no evidence — each testing that the diagnostician
*refuses* the wrong move (prescribing, force-fitting, guessing) rather than getting an answer right.
And [`receipts/`](receipts/) holds **verbatim transcripts** of the diagnostician actually run against all
four fixtures, so you can see it hold the line before you trust it.

To confirm the folder itself is intact — all files present, the output contract defined, every receipt
well-formed, no prescription leaked into a diagnosis — run the structural self-test (no dependencies):

```
python3 checks/verify.py --selftest
```

## What it will NOT do

- It won't fix the problem, edit your config, or write code.
- It won't return an audit / a checklist of everything that could be wrong.
- It won't scan your network, find lost devices, or inventory ports — it diagnoses a *known* camera
  whose motion isn't arriving.
- It won't tell you a link is alive or dead from a quiet window you can't confirm had motion in it.

## What's in the folder

| File | Its one job |
|---|---|
| [`identity.md`](identity.md) | Who the diagnostician is and the single failure it diagnoses. |
| [`rules.md`](rules.md) | The method: locate the dead link, rank to one cause, hold the evidence line, stop. |
| [`examples.md`](examples.md) | Three worked diagnoses showing the reasoning end to end. |
| [`reference/failure-modes.md`](reference/failure-modes.md) | The catalog of causes, each with its fingerprint and likelihood. |
| [`reference/diagnostic-principles.md`](reference/diagnostic-principles.md) | The transferable rules (HTTP 200 ≠ success, etc.). |
| [`reference/evidence-checklist.md`](reference/evidence-checklist.md) | What to feed it — and a paste-in template. |
| [`test-case/`](test-case/) | A positive trap case + answer key, plus `negative/` fixtures (fix-demand, out-of-scope, no-evidence). A fixture — **not** part of the diagnostician's context. |
| [`receipts/`](receipts/) | Verbatim transcripts of real runs against every fixture — proof it holds the line. |
| [`checks/verify.py`](checks/verify.py) | A dependency-free structural self-test (`python3 checks/verify.py --selftest`). |
| [`WRITEUP.md`](WRITEUP.md) | One-page orientation + judge guide: what it is, why it's real, how it meets the brief. |

---

*Built from real, dated field incidents on a live multi-camera install — sanitized. The hardware
behaviors, failure mechanisms, and reasoning are exactly as encountered; the addresses and site details
are not.*
