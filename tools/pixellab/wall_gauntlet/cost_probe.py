#!/usr/bin/env python3
"""What does a BitForge call ACTUALLY cost, with and without `init_image`?

The gauntlet declared a budget of 100 generations and made 100 calls. Every response reported
`usage: {generations: 1.0}` and the running total came to exactly 100. The subscription pool
moved **3950 -> 3530: 420 generations.** The gauntlet overran its declared budget by 4.2x while
the server told it, call by call, that it had not.

This is the audit's §8.4 shape repeating — a stated cost that is simply wrong — and §8.5's rule
biting exactly where it was aimed: a cost figure that has not been read against a settled
balance is not a measurement. The probe measured 1.00 generation per call, settled at both
ends, and that number was true for the calls it was measured on. It was carried into a call
shape it had never been measured on.

Four calls, three settled brackets, and the answer is a division rather than an inference.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab/probe_6_4"))
import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "cost_probe")
N = 2


def main():
    led = v2.Ledger(OUT)
    spec = json.load(open(os.path.join(HERE, "prompts", "wall_round04.json")))
    base = dict(spec["parameters"])
    base["description"] = spec["description"]
    base["negative_description"] = spec["negative_description"]

    guide = Image.open(os.path.join(HERE, "guides", "guide_00.png")).convert("RGB")

    p0, s0 = v2.settled_pool()
    print("pool start: %s (settled=%s)" % (p0, s0))

    reported = 0.0
    for i in range(N):
        p = dict(base); p["seed"] = 60000 + i
        _, row = v2.generate(p, led, "plain_%d" % i, image_subdir="plain",
                             claim="cost:plain", extra={"kind": "plain"})
        reported += ((row.get("usage") or {}).get("generations") or 0)
        print("  plain %d: %s reported=%s" % (i, row["verdict"], row.get("usage")))
    p1, s1 = v2.settled_pool()
    plain_cost = (p0 - p1) / float(N)
    print("pool after plain: %s (settled=%s)  -> %.2f generations per PLAIN call" % (p1, s1, plain_cost))

    rep2 = 0.0
    for i in range(N):
        p = dict(base); p["seed"] = 61000 + i
        p["init_image"] = v2.enc(guide)
        p["init_image_strength"] = 350
        _, row = v2.generate(p, led, "init_%d" % i, image_subdir="init",
                             claim="cost:init", extra={"kind": "init_image"})
        rep2 += ((row.get("usage") or {}).get("generations") or 0)
        print("  init  %d: %s reported=%s" % (i, row["verdict"], row.get("usage")))
    p2, s2 = v2.settled_pool()
    init_cost = (p1 - p2) / float(N)
    print("pool after init: %s (settled=%s)  -> %.2f generations per INIT_IMAGE call" % (p2, s2, init_cost))

    print("\n--- RESULT ---")
    print("plain call:      reported %.2f/call, ACTUAL %.2f/call" % (reported / N, plain_cost))
    print("init_image call: reported %.2f/call, ACTUAL %.2f/call" % (rep2 / N, init_cost))
    print("\nThe `usage` field in the response is not the billed amount. Budget against a")
    print("SETTLED BALANCE BRACKET, per call shape, or do not budget at all.")
    led.write({"claim": "cost:result", "verdict": "INFO",
               "plain_reported_per_call": reported / N, "plain_actual_per_call": plain_cost,
               "init_reported_per_call": rep2 / N, "init_actual_per_call": init_cost,
               "pool_start": p0, "pool_mid": p1, "pool_end": p2,
               "settled": bool(s0 and s1 and s2)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
