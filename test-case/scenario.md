# Test scenario — feed this to the diagnostician

Paste this report (and `bridge-log.txt`) into the diagnostician. Do **not** paste `ANSWER-KEY.md` — that
is for you, not the model.

---

**Camera:** "driveway", a Dahua-OEM box, firmware ~2023. It's wired into the bridge **two ways at once**:
ONVIF PullPoint (the primary path) and the camera's own FTP-on-alarm as a fallback.

**Symptom:** Plain motion still works fine in HA — the `binary_sensor` turns on when someone walks the
driveway. But the **person/vehicle classification** stopped coming through about a week ago; my
classification automations haven't fired since. I've spent two days in my class-parsing code assuming it
broke — but that code hasn't changed in months.

I confirmed a walk-through at 14:32 today. The bridge log tail is in `bridge-log.txt`.

**Diagnose this — why did classification stop?**
