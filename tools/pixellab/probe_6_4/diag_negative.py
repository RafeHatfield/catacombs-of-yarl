#!/usr/bin/env python3
"""§6.4 probe — NEGATIVE-DESCRIPTION DIAGNOSTIC. Not an arm. Not a candidate. Not in any count.

WHY
---
Stage 1's output contains bones, candles, open flame, a pedestal, and vegetation. Not one of
those nouns is in either subject's positive description. Every one of them IS in the
`negative_description`. A floor-tile prompt does not spontaneously produce a femur.

The hypothesis is therefore that `negative_description` is not subtracting on this endpoint —
it is either inert (so the exclusions never applied) or, worse, additive (so the probe spent
120 generations asking for the exact contents it forbade).

This is not a small bookkeeping point. If it is true, Stage 1's yield is depressed by an
instrument error rather than by anything about lighting treatment, and every count in the
STOP 1 table has to be read in that light. It is uniform across arms — so it does not
invalidate the arm *comparison* — but it sets a false ceiling under all three.

METHOD — AUDIT 9.3's, which is the only one that catches a silent no-op: run the same call
varying exactly one parameter and diff the pixels. Three conditions:

  none  : no negative_description at all
  ours  : the Stage 1 negative_description, verbatim
  probe : a negative list of ONE unmistakable noun that the positive prompt cannot produce
          on its own. If that noun then appears, the field is additive. If it never appears
          in any condition, the test is inconclusive rather than exonerating, and says so.

Nothing here changes Stage 1. The declared batch stands exactly as generated.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "diag_negative")
PROMPTS = os.path.join(HERE, "prompts")
N = 4

# One vivid noun, absent from the positive prompt, impossible to arrive at by accident from
# "a worn grey stone floor tile".
PROBE_NEG = "a large bright red parrot"


def main():
    subj = json.load(open(os.path.join(PROMPTS, "subject_floor.json")))
    arm = json.load(open(os.path.join(PROMPTS, "arm_B.json")))

    led = v2.Ledger(OUT)
    print("NEGATIVE-DESCRIPTION DIAGNOSTIC — not an arm, not a candidate, not in any count.")
    print("commit: %s\n" % led.commit)

    base = dict(subj["parameters"])
    base.update(arm["parameters"])
    base["description"] = subj["description"] + " " + arm["lighting"]

    conditions = {
        "none": None,
        "ours": subj["negative_description"],
        "probe": PROBE_NEG,
    }
    for tag, neg in conditions.items():
        for i in range(N):
            p = dict(base)
            p["seed"] = 7700 + i
            if neg is not None:
                p["negative_description"] = neg
            img, row = v2.generate(p, led, "%s_%02d" % (tag, i), image_subdir=tag,
                                   claim="diag:negative:%s" % tag,
                                   extra={"condition": tag, "diagnostic": True,
                                          "negative_used": neg})
            print("  %-6s %02d  %s" % (tag, i, row["verdict"]))

    print("\nImages -> %s" % OUT)
    print("\nThe read is by eye, from the sheet, and it is a yes/no about CONTENT:")
    print("  * 'probe' cells containing a red parrot  -> the field is ADDITIVE. Severe.")
    print("  * 'ours' cells containing bones/candles/flame at about the rate 'none' does")
    print("    -> the field is INERT, and Stage 1's exclusions never applied.")
    print("  * 'ours' visibly cleaner than 'none'     -> the field works and the Stage 1")
    print("    contamination has some other cause.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
