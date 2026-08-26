#!/usr/bin/env python3
"""§6.4 probe — FRAMING DIAGNOSTIC. Not an arm. Not a candidate. Not part of any count.

WHY THIS EXISTS
---------------
Stage 1's candidates split three ways on FRAMING, uniformly across all three arms:
a full-bleed tile texture, an isometric slab, or a small object floating on a background
field. Only the first is a usable tile. The split is a property of the SUBJECT and the
SURFACE, not of the lighting treatment, so it lands on every arm equally and does not
confound the arm comparison — but it sets the yield ceiling for all three, and it will set
Stage 2's too.

`coverage_percentage` ("Percentage of the canvas to cover") is the parameter that addresses
exactly this, and Stage 1 deliberately did not use it: it is untested on this endpoint, and
AUDIT 9.3 measured a parameter being silently ignored AND fully charged on a neighbour. That
was a defensible call and it looks like the wrong one. This measures it rather than arguing
about it.

WHAT IT DOES NOT DO
-------------------
It does not change Stage 1. The declared batch runs in full and its counts stand exactly as
generated — the kill criterion is frozen and no arm is re-run to look better. Nothing here
enters any arm, any count, any contact sheet, or the effort ratio. Its output is evidence for
one ruling at STOP 1: whether Stage 2 should carry `coverage_percentage`.

The instrument is AUDIT 9.3's own method, which is the only one that catches a silent no-op:
run the same call twice varying exactly one parameter, and diff the pixels.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "diag_framing")
PROMPTS = os.path.join(HERE, "prompts")
N = 4  # per condition


def main():
    subj = json.load(open(os.path.join(PROMPTS, "subject_floor.json")))
    arm = json.load(open(os.path.join(PROMPTS, "arm_B.json")))  # one arm only; not an arm run

    led = v2.Ledger(OUT)
    print("FRAMING DIAGNOSTIC — not an arm, not a candidate, not in any count.")
    print("commit: %s" % led.commit)

    base = dict(subj["parameters"])
    base.update(arm["parameters"])
    base["description"] = subj["description"] + " " + arm["lighting"]
    base["negative_description"] = subj["negative_description"]

    for cov in (None, 100):
        for i in range(N):
            p = dict(base)
            p["seed"] = 4200 + i
            if cov is not None:
                p["coverage_percentage"] = cov
            tag = "cov%s" % ("none" if cov is None else cov)
            img, row = v2.generate(p, led, "%s_%02d" % (tag, i), image_subdir=tag,
                                   claim="diag:framing:%s" % tag,
                                   extra={"condition": tag, "diagnostic": True})
            print("  %-9s %02d  %s  %s" % (tag, i, row["verdict"], row.get("out_size")))

    print("\nImages -> %s" % OUT)
    print("Framing is an eye call and is made from the sheet, not from a number in this file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
