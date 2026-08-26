#!/usr/bin/env python3
"""§6.4 probe — PRECONDITION A and the API half of PRECONDITION C.

PRECONDITION A (canvas). The 32x32 area floor was proven on `pixflux` only. The declared
canvas is 32x32 native at x2 integer scale, and it is expected to be RATIFIED at tier 1 —
the probe's survivors become the seed corpus and the seed corpus canvas becomes the game
canvas. So the canvas ruling must be shown to hold on the FROZEN surface before anything
is generated against it. **If v2 BitForge refuses 32x32, this script STOPS the probe.**

PRECONDITION C (API half). One trivial call must return a real image.

Both are answered by the same calls, so they are run together. A third thing is measured
because Stage 1 cannot be authorised without it: **the settled cost of one BitForge
generation**, so ~120 Stage 1 generations can be costed against the remaining pool BEFORE
they are spent rather than after. AUDIT 8.5: an unsettled bracket yields a lower bound, not
a measurement, so both ends are read to stability.

Nothing here ratifies a canvas, creates a palette, or promotes a candidate.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "precondition_evidence")
CANVAS = 32
N_CALLS = 2  # two, so cost-per-call is a division rather than an assumption


def main():
    led = v2.Ledger(OUT)
    print("commit:", led.commit)
    print("surface: v2 HTTP %s%s  [FROZEN for the whole probe]" % (v2.V2_BASE, v2.ENDPOINT))

    raw_before = v2.balance()
    print("\nbalance (whole object, AUDIT 8.1):", json.dumps(raw_before))
    before, stable_b = v2.settled_pool()
    print("pool before: %s  (settled=%s)" % (before, stable_b))
    led.write({"claim": "precondition:balance_before", "verdict": "INFO",
               "balance": raw_before, "pool": before, "settled": stable_b})

    sizes = []
    for i in range(N_CALLS):
        payload = {
            "description": "a plain grey stone floor tile",
            "image_size": {"width": CANVAS, "height": CANVAS},
            "seed": 1337 + i,
        }
        img, row = v2.generate(payload, led, "precondition_32x32_%d" % i,
                               claim="precondition:A 32x32 on v2 BitForge")
        print("  call %d: %s  size=%s  usage=%s  %ss"
              % (i, row["verdict"], row.get("out_size"), row.get("usage"),
                 row.get("seconds")))
        if row["verdict"] != "OK":
            print("\nSTOP — v2 BitForge did not return an image at %dx%d." % (CANVAS, CANVAS))
            print("reason:", row.get("reason", "")[:600])
            print("PRECONDITION A FAILS. The canvas ruling re-opens; nothing proceeds.")
            return 2
        sizes.append(tuple(row["out_size"]))

    print("\n--- PRECONDITION A ---")
    ok_a = all(s == (CANVAS, CANVAS) for s in sizes)
    print("returned sizes: %s" % (sizes,))
    print("VERDICT: %s — v2 BitForge %s a real %dx%d image."
          % ("PASS" if ok_a else "FAIL",
             "returns" if ok_a else "DOES NOT return", CANVAS, CANVAS))
    if not ok_a:
        print("STOP — canvas ruling re-opens; nothing proceeds.")
        return 2

    print("\n--- PRECONDITION C (API half) ---")
    print("VERDICT: PASS — a trivial call returns a real image.")

    after, stable_a = v2.settled_pool()
    spent = (before - after) if (before is not None and after is not None) else None
    print("\n--- COST (settled both ends, AUDIT 8.5) ---")
    print("pool after: %s  (settled=%s)" % (after, stable_a))
    if spent is None:
        print("cost: UNMEASURED — a balance read failed.")
    else:
        per = spent / float(N_CALLS)
        print("spent over %d calls: %s  ->  %.2f generations per BitForge call%s"
              % (N_CALLS, spent, per, "" if (stable_b and stable_a) else
                 "   [LOWER BOUND, not a measurement — a bracket end never settled]"))
        print("forecast, Stage 1 at ~120 generations: %.0f from the pool; %s would remain."
              % (per * 120, after - per * 120))
    led.write({"claim": "precondition:cost", "verdict": "INFO",
               "pool_before": before, "pool_after": after, "calls": N_CALLS,
               "spent": spent, "settled_both_ends": bool(stable_b and stable_a)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
