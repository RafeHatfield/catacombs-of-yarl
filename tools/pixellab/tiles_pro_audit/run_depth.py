#!/usr/bin/env python3
"""The authorised `tile_depth_ratio` call — the audit's last camera parameter.

Ruling (Rafe, 2026-08-26): *"Approved: the one `tile_depth_ratio` call, your prediction on file
before it runs."* The prediction is `PREDICTION.md`, committed at `069aff5`, before this script
was ever executed. Nothing in this file may be changed after the result is seen except to record
what happened.

One call: yield kit A's payload byte-for-byte, seed 1337, plus `tile_depth_ratio: 0.5`. One
variable moved, against a baseline that already exists on disk.

The readout is the structural one — grammar and geometry, never pixels — because the pixel
channel on this endpoint has a noise floor of 1.0000 of the visible area and is NO INSTRUMENT.
The bar is judged by a fresh blind seat afterwards, with the same two plants; that seat is not
told a prediction exists.
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

OUT = os.path.join(HERE, "depth")

# Copied from PREDICTION.md so the script prints its own scorecard rather than leaving the
# comparison to prose written afterwards.
PREDICTED = {
    "1 readout moves": "floor_cell and stack_stride_px at minimum",
    "2 floor cell SHORTER": "~32x16 against the baseline 32x24",
    "3 clause 1 still 0/38": "no candidate reads as having a top surface",
    "4 face-on coursing on N-S pieces": "the seat says so again",
    "5 clause 3 degrades below 38/38": "weakest of the five; may not fire",
}


def main():
    spec = P.load("wall_kit")
    seed = spec["seeds"]["kit_a"]
    over = {"tile_depth_ratio": 0.5}
    spend.check(1, "depth")

    os.makedirs(OUT, exist_ok=True)
    led = tp.Ledger(OUT, "depth_ledger.jsonl")
    base = DM.readout(os.path.join(HERE, "yield", "kit_A0"))

    print("PREDICTION ON FILE (PREDICTION.md, committed 069aff5):")
    for k, v in PREDICTED.items():
        print("  %-34s %s" % (k, v))
    print()

    with tp.Bracket(led, "depth"):
        payload, _ = P.build_payload("wall_kit", seed, **over)
        tiles, crow, meta = tp.run_kit(
            payload, led, "kit_depth", claim="depth:tile_depth_ratio_0.5",
            extra={"arm": "depth", "overrides": over,
                   "authorised_by": "Rafe ruling 2026-08-26",
                   "prediction": "PREDICTION.md @ 069aff5"})
        if not tiles:
            print("CALL FAILED: %s  %s" % (crow.get("verdict"),
                                           (crow.get("reason") or "")[:400]))
            return

    r = DM.readout(os.path.join(OUT, "kit_depth"))
    moved = {k: [base[k], r[k]] for k in base if base[k] != r[k]}
    print("%-18s %-16s %-16s" % ("readout", "baseline", "depth 0.5"))
    for k in ("canvas", "floor_cell", "stack_stride_px", "view_angle", "n_painted"):
        print("%-18s %-16s %-16s %s" % (k, json.dumps(base[k])[:16], json.dumps(r[k])[:16],
                                        "<- moved" if base[k] != r[k] else ""))
    print("\nn_tiles=%d canvas=%s wait=%ss usage=%s" %
          (meta["n_tiles"], meta["sizes"], meta["wait_seconds"], meta["usage"]))

    p1 = bool(moved)
    cell = r["floor_cell"]
    p2 = cell is not None and cell[1] < base["floor_cell"][1]
    print("\nSCORECARD, geometry half (the art half needs the seat):")
    print("  prediction 1 — readout moves            : %s  (%s)" %
          ("HIT" if p1 else "MISS", ", ".join(sorted(moved)) or "nothing moved"))
    print("  prediction 2 — floor cell gets SHORTER  : %s  (%s -> %s)" %
          ("HIT" if p2 else "MISS", base["floor_cell"], cell))
    print("  predictions 3-5 — pending the blind seat")

    with open(os.path.join(OUT, "depth_result.json"), "w") as f:
        json.dump({"overrides": over, "baseline_readout": base, "readout": r,
                   "moved_fields": sorted(moved), "moved_detail": moved,
                   "n_tiles": meta["n_tiles"], "usage": meta["usage"],
                   "prediction_1_readout_moves": p1,
                   "prediction_2_cell_shorter": p2,
                   "authorised_by": "Rafe ruling 2026-08-26",
                   "prediction_commit": "069aff5"},
                  f, indent=2, sort_keys=True, default=str)
    print("\nwrote", os.path.join(OUT, "depth_result.json"))


if __name__ == "__main__":
    main()
