#!/usr/bin/env python3
"""
verify.py — structural self-test for the camera-sees-it-ha-doesnt diagnostician.

This checks the *integrity of the folder*, not the quality of any single diagnosis
(that's what the human reads the receipts for). It is intentionally language-agnostic
and dependency-free — standard-library Python only.

It enforces four things:
  1. every required file is present (the five-file methodology + fixtures + receipts)
  2. rules.md actually defines the five-slot output contract
  3. each full receipt carries all five output slots; the out-of-scope receipt declines
  4. each negative fixture states its Pass/Fail criteria, and no prescriptive
     ("here's the fix") language leaked into a diagnosis output

Usage:
    python3 checks/verify.py --selftest

Exit code 0 = all checks pass, 1 = one or more failed, 2 = bad invocation.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED = [
    "identity.md", "rules.md", "examples.md", "README.md", "WRITEUP.md",
    "reference/failure-modes.md", "reference/diagnostic-principles.md",
    "reference/evidence-checklist.md",
    "test-case/scenario.md", "test-case/bridge-log.txt", "test-case/ANSWER-KEY.md",
    "test-case/negative/README.md",
    "test-case/negative/01-prescription-bait.md",
    "test-case/negative/02-out-of-scope-self-retrigger.md",
    "test-case/negative/03-insufficient-evidence.md",
    "receipts/README.md",
    "receipts/01-in-scope-redundant-path.md",
    "receipts/02-prescription-bait-refused.md",
    "receipts/03-out-of-scope-declined.md",
    "receipts/04-insufficient-evidence-declined.md",
]

SLOTS = ["PRIMARY CAUSE", "HOW I KNOW", "RULED OUT", "CONFIRMING TEST", "CONFIDENCE"]

# Phrases that would mean a diagnosis drifted into prescription. Scanned ONLY inside a
# receipt's verbatim Output section (never the operator Input, which may quote a fix demand).
PRESCRIPTION_PATTERNS = [
    r"\byou should\b", r"\bi recommend\b", r"\bthe fix is\b", r"\bto fix (?:this|it)\b",
    r"\bhere'?s how to fix\b", r"\bnext steps?\b", r"\bstep 1\b",
    r"\bchange the config\b", r"\badd the following\b",
]


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def output_section(text):
    """Extract a receipt's verbatim diagnosis (between '## Output' and the trailing rule/Result)."""
    m = re.search(r"##\s*Output.*?\n(.*?)(?:\n---|\n\*\*Result)", text, re.S | re.I)
    return m.group(1) if m else text


def check_files():
    return [f"missing: {p}" for p in REQUIRED if not os.path.isfile(os.path.join(ROOT, p))]


def check_output_contract():
    text = read("rules.md")
    missing = [s for s in SLOTS if s not in text]
    return [f"rules.md does not define slot(s): {', '.join(missing)}"] if missing else []


def check_receipts():
    problems = []
    receipts = [p for p in REQUIRED if p.startswith("receipts/") and not p.endswith("README.md")]
    for r in receipts:
        out = output_section(read(r))
        if "out-of-scope" in r:
            if not re.search(r"out of scope", out, re.I):
                problems.append(f"{r}: expected an out-of-scope decline, marker not found")
        else:
            missing = [s for s in SLOTS if s not in out]
            if missing:
                problems.append(f"{r}: missing output slot(s): {', '.join(missing)}")
        for pat in PRESCRIPTION_PATTERNS:
            if re.search(pat, out, re.I):
                problems.append(f"{r}: prescriptive language in diagnosis output: /{pat}/")
    return problems


def check_negatives():
    problems = []
    for n in ("01-prescription-bait", "02-out-of-scope-self-retrigger", "03-insufficient-evidence"):
        text = read(f"test-case/negative/{n}.md")
        if "Pass:" not in text:
            problems.append(f"negative/{n}.md: no Pass criteria")
        if "Fail:" not in text:
            problems.append(f"negative/{n}.md: no Fail criteria")
    return problems


def main():
    checks = [
        ("required files present", check_files),
        ("output contract defined in rules.md", check_output_contract),
        ("receipts well-formed (slots / decline / no prescription)", check_receipts),
        ("negative fixtures carry Pass/Fail criteria", check_negatives),
    ]
    failed = 0
    for name, fn in checks:
        problems = fn()
        if problems:
            failed += 1
            print(f"FAIL  {name}")
            for p in problems:
                print(f"        - {p}")
        else:
            print(f"ok    {name}")
    if failed:
        print(f"\n{failed} check(s) failed.")
        sys.exit(1)
    print("\nAll checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    if "--selftest" not in sys.argv:
        print("usage: python3 checks/verify.py --selftest")
        sys.exit(2)
    main()
