#!/usr/bin/env python3
"""ARM 3 — the last 20 generations, and what they are NOT.

⚠ **THIS IS NOT PART OF THE YIELD RUN AND DOES NOT DECIDE THE BAR.** The bar's verdict was
settled by kits A and B at the declared configuration, both judged by a blind seat that caught
its plants. This arm is chosen AFTER seeing those results, so counting it toward the bar would
be rolling until a pass — bible §13.6, a candidate never contributes to its own acceptance bar.
It is reported separately, as a lead for whoever runs next, with its own count stated against
the same unchanged bar.

WHY THIS CONFIGURATION AND NOT ANOTHER. Two measurements collided:

  * The blind seat's single most repeated objection across 38 candidates was that the pale band
    at the top of each piece is *"a lighter stripe, no lip, no near edge"* — a material band,
    not a horizontal surface. That is bible §3's top surface failing, and it is the same
    objection the wall gauntlet's seat made in all ten of its rounds on a different endpoint.
  * `tile_view_angle: 90` was measured live here, and it buys bible §3's SQUARE ground cell
    (32x24 -> 32x32) that `tile_view` was measured unable to buy. But at 90 the wall loses its
    cap entirely — zero ground pitch means zero top surface. The parameter trades one half of
    §3 for the other.

`building_wall_angle` is documented to decouple exactly those two: *"square_topdown only: wall
storey height as its own camera angle, decoupled from the ground pitch."* So this call asks the
one question that both measurements point at and neither answers:

  **Can the ground cell be square AND the wall still show a face with a top on it?**

45 is chosen as the mid-point of the documented 5-90 range, with no prior measurement of this
parameter to aim it. Stated so the choice is not mistaken for a derivation.

Budget: this is the final 20 generations under the declared 220 ceiling. `spend.check` refuses
it if it would cross.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag_metadata as DM  # noqa: E402
import prompt as P  # noqa: E402
import spend  # noqa: E402
import tiles_pro as tp  # noqa: E402

OUT = os.path.join(HERE, "arm3")


def main():
    spec = P.load("wall_kit")
    seed = spec["seeds"]["kit_a"]
    over = {"tile_view_angle": 90, "building_wall_angle": 45}
    spend.check(1, "arm3")

    os.makedirs(OUT, exist_ok=True)
    led = tp.Ledger(OUT, "arm3_ledger.jsonl")
    base = DM.readout(os.path.join(HERE, "yield", "kit_A0"))

    with tp.Bracket(led, "arm3"):
        payload, _ = P.build_payload("wall_kit", seed, **over)
        tiles, crow, meta = tp.run_kit(
            payload, led, "kit_arm3", claim="arm3:square_ground_walled",
            extra={"arm": "arm3", "overrides": over,
                   "role": "LEAD, not a bar outcome — chosen after the yield run's results "
                           "were seen (bible §13.6)"})
        if not tiles:
            print("CALL FAILED: %s  %s" % (crow.get("verdict"),
                                           (crow.get("reason") or "")[:300]))
            return

    r = DM.readout(os.path.join(OUT, "kit_arm3"))
    print("\n%-18s %-14s %-14s" % ("readout", "baseline", "arm3"))
    for k in ("canvas", "floor_cell", "stack_stride_px", "view_angle", "n_painted"):
        print("%-18s %-14s %-14s %s" % (k, json.dumps(base[k])[:14], json.dumps(r[k])[:14],
                                        "" if base[k] == r[k] else "<- moved"))
    print("\nn_tiles=%d  canvas=%s  wait=%ss  usage=%s" %
          (meta["n_tiles"], meta["sizes"], meta["wait_seconds"], meta["usage"]))
    with open(os.path.join(OUT, "arm3_result.json"), "w") as f:
        json.dump({"overrides": over, "baseline_readout": base, "readout": r,
                   "n_tiles": meta["n_tiles"], "usage": meta["usage"],
                   "role": "LEAD — not counted toward the declared yield bar"},
                  f, indent=2, sort_keys=True, default=str)
    print("\nwrote", os.path.join(OUT, "arm3_result.json"))


if __name__ == "__main__":
    main()
