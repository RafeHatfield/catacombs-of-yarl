#!/usr/bin/env python3
"""The yield run, and the noise floor, in the same five calls.

FOUR IDENTICAL CALLS at seed 1337, then ONE at a second seed.

The four identical calls do double duty and this is deliberate, not thrift:

  * they are the **noise floor** — the negative control every lever verdict is read against.
    §6.4's first lever pass reported HONOURED on all four surfaces at pixdiff 1.0000
    *including a control*, an instrument that could not fail, and the repeated-identical-call
    control is what made the column readable. A two-sample check is not enough: on this
    platform a two-sample check once read 0.0000 and an eight-sample census disproved it.
  * they are also the **determinism** column, which the audit assumes absent until measured.
  * and the FIRST of them is **yield kit A**.

Declared before the run so it cannot be chosen afterwards: **kit A is call 0 of the four.** If
the four differ, the other three are reported as variance and the bar is still applied to call
0 — plus, in that case, to each of them, because four samples of a yield is more information
than one and reporting only the best would be picking the flattering number.

Kit B is a second seed, declared in the prompt file before any result, so that a second kit
cannot later be mistaken for a retry.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prompt as P  # noqa: E402
import spend  # noqa: E402
import tiles_pro as tp  # noqa: E402

OUT = os.path.join(HERE, "yield")
N_IDENTICAL = 4


def main():
    spec = P.load("wall_kit")
    seed_a = spec["seeds"]["kit_a"]
    seed_b = spec["seeds"]["kit_b"]
    spend.check(N_IDENTICAL + 1, "yield")

    os.makedirs(OUT, exist_ok=True)
    led = tp.Ledger(OUT, "yield_ledger.jsonl")
    kits = {}
    metas = {}

    with tp.Bracket(led, "yield"):
        for i in range(N_IDENTICAL):
            payload, _ = P.build_payload("wall_kit", seed_a)
            label = "A%d" % i
            tiles, crow, meta = tp.run_kit(
                payload, led, "kit_" + label, claim="yield:" + label,
                extra={"kit": label, "seed": seed_a, "role":
                       "yield kit A + noise floor sample" if i == 0 else "noise floor sample"})
            kits[label] = tiles
            metas[label] = meta
            print("%-4s n=%-3d sizes=%s usage=%s wait=%ss" %
                  (label, len(tiles), meta["sizes"] if meta else "-",
                   (meta or {}).get("usage"), (meta or {}).get("wait_seconds")))

        payload, _ = P.build_payload("wall_kit", seed_b)
        tiles, crow, meta = tp.run_kit(
            payload, led, "kit_B", claim="yield:B",
            extra={"kit": "B", "seed": seed_b, "role": "yield kit B, second seed"})
        kits["B"] = tiles
        metas["B"] = meta
        print("%-4s n=%-3d sizes=%s usage=%s wait=%ss" %
              ("B", len(tiles), meta["sizes"] if meta else "-",
               (meta or {}).get("usage"), (meta or {}).get("wait_seconds")))

    # --- the noise floor -----------------------------------------------------
    print("\n== NOISE FLOOR: %d identical calls, seed %d ==" % (N_IDENTICAL, seed_a))
    pairs = []
    base = kits.get("A0") or {}
    for i in range(N_IDENTICAL):
        for j in range(i + 1, N_IDENTICAL):
            a, b = kits.get("A%d" % i), kits.get("A%d" % j)
            if not a or not b:
                continue
            mean, moved, n = tp.kitdiff(a, b)
            pairs.append({"pair": "A%d/A%d" % (i, j), "mean_pixdiff": mean,
                          "tiles_moved": moved, "tiles_compared": n})
            print("  A%d vs A%d   mean pixdiff %.6f   %d of %d tiles moved"
                  % (i, j, mean, moved, n))
    floor = max((p["mean_pixdiff"] for p in pairs), default=None)
    print("  NOISE FLOOR (worst identical-call pair) = %s"
          % ("%.6f" % floor if floor is not None else "UNMEASURED"))

    # --- seed separation -----------------------------------------------------
    seedrow = None
    if base and kits.get("B"):
        mean, moved, n = tp.kitdiff(base, kits["B"])
        seedrow = {"mean_pixdiff": mean, "tiles_moved": moved, "tiles_compared": n}
        print("\n== SEED SEPARATION: A0 vs B ==\n  mean pixdiff %.6f, %d of %d tiles moved"
              % (mean, moved, n))
        if floor is not None:
            print("  vs noise floor %.6f -> %s" %
                  (floor, "SEED IS LIVE" if mean > floor else
                   "NOT SEPARATED FROM NOISE — seed does nothing"))

    # --- did the empty style_images list do anything? ------------------------
    # Free: that kit is already on disk from the constraint phase. It carried a DIFFERENT
    # description, so it is compared only for canvas, never for content.
    result = {"seed_a": seed_a, "seed_b": seed_b, "noise_pairs": pairs,
              "noise_floor": floor, "seed_separation": seedrow,
              "kits": {k: (metas[k] or {}) for k in metas}}
    with open(os.path.join(OUT, "yield_result.json"), "w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print("\nwrote", os.path.join(OUT, "yield_result.json"))


if __name__ == "__main__":
    main()
