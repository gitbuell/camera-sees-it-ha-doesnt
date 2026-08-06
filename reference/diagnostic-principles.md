# reference: diagnostic-principles

The transferable rules behind the diagnoses. The `failure-modes.md` catalog is domain-specific; these
principles are why the method works, and they carry to any event-driven IoT integration. Each one was
learned by being burned by its violation.

---

### 1. A quiet window is inconclusive, not a result
"I watched and saw nothing" is evidence only if you *know* the thing you're watching for happened during
the window. Absent a confirmed stimulus, silence proves nothing — the detector may be dead, or nothing
may have moved. Never promote an unconfirmed quiet window to "it's broken" or "it's fine." Get a
confirmed event in the actual field of view, then read what happened.

### 2. HTTP 200 ≠ success
A transport-layer OK is not an application-layer success. Cheap boards routinely return SOAP `Fault`
bodies inside a 200. A client that branches on status code alone is structurally blind to it and will
report a faulting device as merely idle. **Read the body, parse the payload — don't trust the envelope.**

### 3. Check the path, then the feature
A working feature does not certify the path you care about. If motion "mostly works," that tells you
*some* path is alive — not that the specific path carrying the missing signal (classification, one
camera's events, one delivery route) is alive. Verify the exact path the absent data would travel, not
the healthy-looking aggregate.

### 4. A redundant path hides outages
Redundancy that isn't observable converts a total outage into a silent capability loss. When two routes
feed the same sensor, one can be 100% dead while the only symptom is "we lost the labels." That reads as
a parser bug and sends you into the wrong code. Ask what *each* path independently carries before
diagnosing the merged result — and treat "a feature that depends on one path died" as a reason to check
*that path is alive* before debugging the feature.

### 5. Verify in the artifact, never the status string
Intent is not behavior. "Motion detection: ON" in a UI, an ONVIF `GetStatus` that returns a clean value,
a config file that reads `127.0.0.1`, a write that echoes back "saved" — these describe what *should* be,
not what *is*. On this hardware a saved-but-unapplied write is indistinguishable from a rejected one
until you read the actual behavior. Trust the log line, the wire capture, the retained MQTT payload, the
pixels — not the label the device prints about itself.

### 6. The single-subscriber observation trap
Instrumentation can cause the outage it's meant to observe. When a device serves exactly one subscriber,
attaching a second one starves the first — so a test listener both sees nothing and breaks the real path,
and "my listener saw nothing" becomes false evidence for "the device is silent." Prefer observing the
live production process over attaching a competing consumer. If you must attach one, know that you are
now testing a *different* subscription than the one that failed.

### 7. Name one cause; work backward to find it
A diagnosis is a location, not a list. Model the system as a chain of links and find the **earliest**
one where the evidence goes dark — everything upstream is proven healthy, everything downstream is
symptom. A ranked inventory of everything that looks wrong is what you produce when you *haven't* located
the break. Commit to the earliest dead link, or state honestly that the evidence doesn't yet reach one
and name the single experiment that would decide it.

### 8. Separate the cause from the symptom the operator brought you
The operator arrives with a symptom ("HA is silent") and usually a *guess at the link* ("the parser is
broken"). Both are data about their experience, not the diagnosis. The frame they hand you is frequently
pointed at the wrong link — the discipline is to re-derive where the break actually is from evidence,
and to name the mechanism underneath the symptom, not restate the symptom in fancier words.
