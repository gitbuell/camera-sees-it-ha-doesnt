# Writeup — camera-sees-it-ha-doesnt

*A one-page orientation, doubling as a judge guide. If you're evaluating this, start here.*

## What it is, in one line

A folder-based diagnostician for a single, real, expensive failure: **an IP camera clearly detects
motion, but the event never reaches Home Assistant.** Drop the folder into a Claude project, feed it a
camera model + a bridge log, and it names the *one* thing killing the signal — and stops.

## Why this failure, and why it's real

This isn't a hypothetical domain picked for a contest. It's extracted from the log of a live,
multi-camera home install where this exact failure ate days at a time. Cheap OEM camera boards
(XiongMai and its rebrands, ANPVIZ, generic N601L) misbehave in consistent, documented, *counter-
intuitive* ways, and the person running the bridge burns hours because every obvious signal lies:
the camera "clearly works," the subscription "looks healthy," the logs show "no errors." Every failure
mode, every trap, and all three worked examples come from incidents that actually happened. The
site-identifying details (addresses, hostnames, coordinates) are stripped; the **mechanisms and
reasoning are exactly as encountered.** That authenticity is the point — this diagnoses like someone
who has been burned by the hardware, because it was written from those burns.

## How it meets the brief

| The brief asks for… | Where it delivers |
|---|---|
| **Root cause, not a symptom list** | It models the signal as a four-link chain (`detector → transport → parse → entity`) and names the **first** dead link. Everything downstream is explicitly labeled symptom. `rules.md` forbids ranked lists: "a ranked list of twelve is a confession that you did not diagnose." |
| **A specific enough domain** | Not "camera problems." One failure — motion detected, never arrives at HA — on one class of hardware, through one integration path (ONVIF-PullPoint / ISAPI-alertStream → MQTT). It even names what it *won't* touch (self-retrigger loops, PTZ drift) as the *opposite* failure. |
| **Clean methodology, each file one job** | `identity.md` (who + scope) · `rules.md` (the method + output format) · `examples.md` (three worked diagnoses) · `reference/` (failure catalog, transferable principles, evidence checklist). Nothing restated across files. |
| **README a stranger can follow** | `README.md` gives the one-line failure, who it's for, how to load it, exactly what to feed it, and the fixed output format you get back. |

## The design stance (what makes it a diagnosis, not a critique)

- **One primary cause**, chosen as the earliest dead link — never a checklist.
- **Falsifiable output.** Every diagnosis names the one alternative it *ruled out* and the single
  *confirming test* — an observation that would overturn it. A cause with no test behind it is a guess,
  and it says so in a confidence line.
- **It refuses to prescribe.** No fix, no config, no "try this instead." Naming *why* is the whole job.
- **It declines the wrong case cleanly.** Hand it a false-positive / self-retrigger problem (the
  *opposite* failure) and it names the class in one line and stops, rather than forcing the wrong chain.

## Run it yourself

`test-case/` is a ready-made trap: its surface symptom ("plain motion works, classification stopped")
looks like a parser bug but is actually a dead ONVIF path masked by a redundant FTP fallback. Feed the
diagnostician `test-case/scenario.md` + `test-case/bridge-log.txt` and check its answer against
`test-case/ANSWER-KEY.md`. (Don't load the answer key into the model.)

## Honest limits

- It diagnoses the **missing** event, not the **unwanted** one — false positives and PTZ self-retrigger
  are out of scope by design, and it says so.
- It is only as good as the evidence fed to it; `reference/evidence-checklist.md` states what makes a
  diagnosis sharp, and the confidence line is honest when the evidence only narrows the cause.
- The failure modes are drawn from a real but finite fleet; a new board can always surprise it. The
  method (walk the chain, find the earliest dead link) holds even where a specific fingerprint doesn't.
