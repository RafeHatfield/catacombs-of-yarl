#!/usr/bin/env python3
"""§6.4 probe — WALL MICRO-PROBE. Bar declared here, in this file, before a single call runs.

RULED (Rafe, STOP 1): walls take zero picks and route to a micro-probe.

    20 generations with surface-framing prompts (seamless wall tile, architectural segment,
    tileable — not object framings).

    BAR: >= 5 usable-as-wall in 20.
         Below the bar, text-to-image is ruled WRONG for architectural surfaces and the wall
         pipeline re-plans — conditioning, composition, or hand-authored seeds.

    Contact sheet to Rafe either way.

WHAT "USABLE-AS-WALL" MEANS — fixed before the run, so it cannot be shaded afterwards
-------------------------------------------------------------------------------------
A generation is usable-as-wall if ALL THREE hold:

  1. **Surface, not object.** It reads as a continuous wall surface, not as a discrete thing
     sitting on a background field. A centred item with a margin of empty ground around it
     fails, however well drawn.
  2. **Full-frame.** The material reaches all four edges. No border, no frame, no vignette.
  3. **Orthogonal.** Straight-on. An isometric or three-quarter slab fails on §3, which bans
     an isometric map outright.

Explicitly NOT part of the bar, because none of it is what the ruling asked:
  * whether it is beautiful, or would pass a landing gate (§13.1 — nothing lands from a sheet)
  * whether it is on-register, chunky enough, or correctly worn (§13.4 — eye-side, at the
    human gate, and never instrumented)
  * whether it tiles *seamlessly* — that is a stricter property than the bar names and is not
    checkable from a single tile at all
  * its lighting treatment — the micro-probe carries no arm

LOOP-PROCESS §8: nothing is cut to fit. The bar is 5. It is not re-tuned once the number is
visible, in either direction.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "wall_microprobe")
PROMPTS = os.path.join(HERE, "prompts")
N = 20
BAR = 5
SEED_BASE = 9100


def main():
    subj = json.load(open(os.path.join(PROMPTS, "subject_wall_surface.json")))
    led = v2.Ledger(OUT)

    print("WALL MICRO-PROBE")
    print("commit:  %s" % led.commit)
    print("surface: v2 HTTP %s%s  [FROZEN]" % (v2.V2_BASE, v2.ENDPOINT))
    print("batch:   %d generations, no arms" % N)
    print("BAR:     >= %d usable-as-wall in %d, DECLARED BEFORE THIS RUN.\n"
          "         Below it, text-to-image is ruled wrong for architectural surfaces and the\n"
          "         wall pipeline re-plans. The bar is not re-tuned once the number is visible.\n"
          % (BAR, N))

    before, stable_b = v2.settled_pool()
    print("pool before: %s (settled=%s)\n" % (before, stable_b))
    led.write({"claim": "microprobe:pool_before", "verdict": "INFO", "pool": before,
               "settled": stable_b, "planned_generations": N,
               "bar": BAR, "bar_declared": "before the run, per LOOP-PROCESS §8"})

    payload_base = dict(subj["parameters"])
    payload_base["description"] = subj["description"]
    payload_base["negative_description"] = subj["negative_description"]

    ok = 0
    for i in range(N):
        p = dict(payload_base)
        p["seed"] = SEED_BASE + i
        img, row = v2.generate(p, led, "wallsurf_%02d" % i, image_subdir="images",
                               claim="microprobe:wall_surface:%02d" % i,
                               extra={"subject": "wall_surface", "index": i})
        ok += row["verdict"] == "OK"
        print("  [%2d/%2d] %s %s" % (i + 1, N, row["verdict"], row.get("out_size") or ""))

    after, stable_a = v2.settled_pool()
    print("\nreturned OK: %d/%d" % (ok, N))
    print("pool after: %s (settled=%s)  spent: %s" %
          (after, stable_a, (before - after) if (before and after) else "UNMEASURED"))
    led.write({"claim": "microprobe:pool_after", "verdict": "INFO", "pool": after,
               "settled": stable_a, "returned_ok": ok})
    print("\nThe usable-as-wall count is an EYE call against the three-part definition in this\n"
          "file's docstring, made from the contact sheet. It is not computed here, and no\n"
          "script in this probe scores it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
