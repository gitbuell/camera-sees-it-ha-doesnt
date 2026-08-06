# examples

Three worked diagnoses in the output format from `rules.md`: **Primary cause → How I know → Ruled out →
Confirming test → Confidence → Stop.** Notice what is *not* here — no fix, no config, no "try this
instead." The **confirming test** is a diagnostic *observation* (what to read to confirm or overturn the
call), never a remediation. The reasoning is the product.

---

## Example 1 — Motion works, then goes quiet after a few minutes

### Input
> Dahua-clone camera, ONVIF PullPoint into the bridge. Motion sensors in HA work perfectly right after
> I restart the bridge — I walk the yard, the `binary_sensor` fires. Then, five or ten minutes later,
> it just stops. No errors in the bridge log. The subscription is still open. If I restart the bridge
> it works again for a few minutes, then dies the same way. Camera's own event list shows motion the
> whole time.
>
> Bridge log tail:
> ```
> 12:00:03  subscribed pullpoint, InitialTerminationTime=PT300S
> 12:00:31  motion ON
> 12:01:10  motion OFF
> 12:02:48  motion ON
> 12:03:15  motion OFF
> 12:05:04  PullMessages -> 200, 0 messages
> 12:05:26  PullMessages -> 200, 0 messages
> 12:05:41  PullMessages -> 200, 0 messages
>   ...(continues, every response 200, always 0 messages)...
> ```

### Reasoning
Walk the chain. **Link 1 (detector):** confirmed — the camera's own event list shows motion throughout,
and the first few minutes of HA events prove the detector is alive. **Link 4 (entity) and link 3
(parse):** also proven healthy, because motion *did* reach HA correctly right after restart. So the
break is not a stuck sensor, not a broken parser, not an MQTT problem — all four links worked minutes
ago. Something *changed* between minute two and minute five.

The one thing that changes on its own timer here is the subscription. Look at the numbers: the
subscription was created with `InitialTerminationTime=PT300S` — a **300-second lease**, not a permanent
connection — at `12:00:03`. The events stop at almost exactly `12:05`. That is the lease expiring.

Now the trap: after `12:05` the log is not silent. Every `PullMessages` returns **HTTP 200** with zero
messages. That reads as "camera has nothing to report." But a 200 with an empty body from an expired
pull-point on these boards is not "no events" — it is the board answering a dead subscription with a
SOAP `Fault` wrapped inside a 200. The bridge's HTTP client sees a 200 and raises nothing; the body
merely lacks a `NotificationMessage`, so it looks identical to a quiet camera. The "no errors in the
log" the operator noticed is itself the evidence: a healthy-looking 200 stream is exactly what an
expired-and-faulting subscription produces.

The restart "fixes" it only because it creates a **fresh** 300-second lease — and the cycle repeats.

### Primary cause
The pull-point subscription is expiring at its 300-second lease and nothing renews it. After expiry the
camera faults every `PullMessages` *inside* an HTTP 200, which the bridge cannot distinguish from a
camera with nothing to report — so events silently stop while everything looks healthy.

### How I know
The timing pins it: events die at ~5 minutes against a logged `PT300S` lease, and a restart resets the
clock every time. The post-`12:05` `200 / 0 messages` stream is the signature of the fault-inside-200,
not of a quiet camera — a genuinely idle camera and an expired subscription look the same at the HTTP
layer, and only the 5-minute periodicity tells them apart.

### Ruled out
A genuinely idle camera — it produces the *identical* `200 / 0 messages` stream, so at the HTTP layer the
two are indistinguishable. Rejected by the ~5-minute periodicity and the restart-resets-the-clock
behavior, neither of which an idle camera would show.

### Confirming test
Read the **body** of one post-`12:05` `PullMessages` response: an expired subscription carries a SOAP
`<...Fault>` (e.g. `ter:InvalidArgVal`) *inside* the 200, where a truly idle camera returns a valid
empty `PullMessagesResponse`. One packet capture settles it. *(An observation, not a fix.)*

### Confidence
High — timing, periodicity, and the restart signature all converge on the same mechanism.

### Stop.

---

## Example 2 — Motion fires, but person/vehicle labels never arrive

### Input
> Everything works — motion turns the HA sensor on and off correctly. But I built automations on the
> *classification* (person vs. vehicle) and those never fire. It's like the class parser is broken. I've
> been staring at the classification-handling code for a day.
>
> Raw event captured off the wire during a car passing:
> ```
> Topic: VideoSource/MotionAlarm
>   SimpleItem Name=State           Value=true
>   SimpleItem Name=ObjectId        Value=10448
>   SimpleItem Name=ClassTypes      Value=Vehicle
> ```
> Bridge handler (paraphrased):
> ```
> if item["State"] == "true":
>     publish_motion(ON)
> elif item.get("ClassTypes"):
>     publish_class(item["ClassTypes"])
> ```

### Reasoning
The operator's framing — "the class parser is broken" — is the symptom, and it's pointing them at the
wrong link. Walk the chain. **Link 1 and 2:** the raw wire capture proves the camera both detected *and*
transported a fully-formed event carrying `ClassTypes=Vehicle`. So the class data physically arrived at
the bridge. That rules out the camera, the firmware, and the transport in one stroke — whatever is
wrong is at **link 3, the parse**, but it is not a *parsing* failure. The field parsed fine; the capture
shows it right there.

Look at the control flow. The event carries **both** `State=true` and `ClassTypes=Vehicle` on the *same*
message. The handler is an `if / elif`: it tests the boolean motion branch first, and because that
branch matches (`State == "true"`), the `elif` never runs. On exactly the messages that carry a class,
the class is dropped — not because the code fails to understand it, but because the code never *looks* at
it. Plain-motion messages (no class) fall through to... also nothing useful, but the operator never
noticed because plain motion works via the `State` branch.

This is why the symptom is so misleading: the classification path isn't erroring, so there's nothing in
the log; and plain motion works perfectly, so three of four links look flawless. The redundant boolean
branch is *masking* the class branch's total inaccessibility.

### Primary cause
Branch ordering, not a parse failure. The camera delivers `State=true` and `ClassTypes` on the *same*
`MotionAlarm` message; the handler's `if State … elif ClassTypes` structure matches the boolean branch
first and never evaluates the `elif`, so the class is silently discarded on precisely the messages that
carry it.

### How I know
The wire capture shows `ClassTypes=Vehicle` arriving intact — so the data is present and well-formed,
and "the parser can't read it" is disproven. The `if/elif` guarantees the two branches are mutually
exclusive on a message that populates both fields, which is exactly the message a classified event is.
The absence of any error, plus plain motion working, is the fingerprint of a masked branch rather than a
broken one.

### Ruled out
A broken parser or a codec/format issue on the class field. Rejected by the wire capture: `ClassTypes=
Vehicle` arrives intact and well-formed, so there is nothing wrong with *reading* it — the code simply
never reaches the read.

### Confirming test
Log which branch each `MotionAlarm` message takes: every message with `State=true` will be seen entering
the boolean branch and never the `elif`. Confirmed the instant a message that carries `ClassTypes` is
shown taking the `State` branch. *(An observation, not a fix.)*

### Confidence
High — the control flow is deterministic, and the capture shows both fields riding one message.

### Stop.

---

## Example 3 — A test listener "proves" the camera is silent

### Input
> HA stopped getting motion from one camera. To check whether the camera was even emitting, I ran a
> little standalone ONVIF subscriber on my laptop against it and watched: over a couple of minutes it
> received nothing but one `Initialized` message at subscribe time. So the camera is dead / not
> emitting, right? But the weird part — while my test was running, a colleague said the *other* motion
> automations on that same camera also went dark, and they came back after I killed my script.

### Reasoning
The operator has drawn "my listener saw nothing → the camera is silent." On this class of board that
inference is unsafe, and the second observation is the tell.

Walk it. The only "event" the test listener got was an `Initialized` notification — that is the
subscribe-time snapshot every new pull-point emits; it is not a motion event and proves only that the
subscription was *created*, not that the camera is quiet. So the test has, at best, an inconclusive
quiet window (rule: a quiet window is not a result unless motion was confirmed to occur during it — and
nothing here confirms a walk happened in view while the laptop was listening).

Now the decisive clue: the production automations died *when the test started* and recovered *when it
stopped*. Many of these boards support exactly **one** active event subscription. Attaching the laptop's
subscriber didn't observe the system — it *displaced* the bridge's subscription, starving the real path.
So the outage the operator "confirmed" with the test was, during the test, partly *caused* by the test.
That means the test tells us nothing about why HA was silent *before* the laptop was attached — the two
are different subscriptions.

The evidence rules the camera-is-dead theory out: the camera clearly still emits (the bridge got events
until the single subscription slot was contended), and the only proof offered for silence is a starved
listener plus an inconclusive window.

### Primary cause
The diagnostic method is invalid, not the camera. The board serves a single event subscription; the
test listener starved the production bridge rather than observing it, and its only "result" was a
subscribe-time `Initialized` snapshot over an unconfirmed-quiet window. The original HA silence is
therefore still un-located — the test cannot speak to it, because it measured a different subscription
it also broke.

### How I know
The perfect correlation — other automations dark *during* the test, restored *after* — is the signature
of single-subscriber starvation, not of a silent camera. The lone `Initialized` message is a
subscription-created artifact, not a motion event. And no confirmed motion occurred in the watch window,
so its silence is inconclusive by rule.

### Ruled out
"The camera is dead / not emitting" — the operator's own conclusion. Rejected by the correlation: the
board kept emitting to the bridge until the test contended its single subscription slot. A dead camera
cannot go dark *because* you attached a listener.

### Confirming test
Re-observe without a competing subscriber — read the live bridge's *own* event stream (or trace the
running process) during a **confirmed** walk. If the bridge receives events with no second listener
attached, the camera was never the silent party. *(An observation, not a fix.)*

### Confidence
Medium — the starvation is well-evidenced, but note what this diagnosis does *not* claim: the *original*
pre-test silence is still un-located, because the only measurement of it was invalid. The finding is that
the method broke, and the real cause remains open until observed cleanly.

### Stop.
