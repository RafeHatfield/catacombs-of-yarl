#!/usr/bin/env python3
"""THE YIELD RUN — 24 generations of floor material, two cells of twelve.

DECLARED BEFORE THE FIRST CALL, and not tuned after.

    SUBJECT   `prompts/floor_material_rd.json` — the same subject, in the same register, as
              tier one's `base_material.json`, translated to RD's payload shape. The
              translation is LOSSY and its losses are enumerated in that file's
              `translation_losses`; they cap what a NEGATIVE result may claim and do not touch
              what a POSITIVE one may.

    BUDGET    24 generations, 12 per cell, BOTH CELLS SPENT IN FULL whatever cell N shows.
              This is a measurement, not a search. Under the 40 hard ceiling in `rd.py`.

    CELLS     N   tile_x/tile_y OFF   the like-for-like ring-rate comparison
              T   tile_x/tile_y ON    the seamless census, and the flag's own axis
              Nothing else differs between them. §4.1 LAW: a lever is proven on its axis, not
              on the diff — with one variable between two cells of twelve, the difference in
              seam rate IS the flag's effect, and the difference in ring rate says whether the
              flag costs anything in the currency the bar is denominated in.

    LEVERS    None. `prompt_style` is resolved live and recorded; no strength, no conditioning,
              no reference. Material acquisition, not a lever search.

    SCREEN    Every child, mechanically, through TWO instruments neither of which this session
              wrote or altered:
                `../../floor_remediation/ring_instrument.py`  — constants UNTOUCHED, shelled
                    out to rather than imported, so no monkeypatch is even possible.
                `census.py` — this session's, and certified: its control suite caught its own
                    first draw and is recorded doing so.

    BASELINE  C-GAB line on BitForge: 5/20 instrument, 9/20 seat-adjusted (REPORT-PARENT-RATE
              §2). The brief's 25-45% band is those two figures. ⚠ THE BASELINE IS A
              CONDITIONED RATE AND THIS RUN IS UNCONDITIONED — see `baseline_comparability` in
              the prompt file. The comparison is stated with that asymmetry attached, every
              time it is stated.

    REFUSALS  Promotes nothing, in any state. Writes nothing outside this directory. Touches no
              tier-one file, no corpus file, no survivor, no manifest. Alters no constant in any
              instrument. Buys nothing. Never exceeds the ceiling.

WHY 12 AND NOT 20. The baseline's own cells were tens (REPORT-PARENT-RATE ran two cells of 10
for 20). Twelve per cell buys a slightly tighter interval on each while keeping the pair inside
24, and 24 is what the brief allocated. The report computes the exact one-sided Fisher against
both baseline readings rather than eyeballing the gap, exactly as `parent_rate_summary.py` did.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "yield_out")
PROMPTS = os.path.join(HERE, "prompts")

CELLS = {
    "N": dict(n=12, seed0=20250, tiling=False),
    "T": dict(n=12, seed0=20350, tiling=True),
}
RUN_BUDGET = 24

# The baseline this run is measured against. Recorded here so the ledger carries the comparison
# it was declared against rather than the one that looks best afterwards.
BASELINE = {
    "source": "tools/floor_remediation/REPORT-PARENT-RATE.md §2",
    "surface": "PixelLab v2 BitForge, create-image-bitforge",
    "parent": "C-GAB, style_strength 50",
    "instrument": [5, 20],
    "seat_adjusted": [9, 20],
    "band_pct": [25, 45],
    "caveat": "CONDITIONED. This run is UNCONDITIONED. See prompts/floor_material_rd.json "
              "-> baseline_comparability.",
}


def spec():
    return json.load(open(os.path.join(PROMPTS, "floor_material_rd.json")))


def run_cell(led, budget, sess, cell, style, dry):
    s = spec()
    c = CELLS[cell]
    spent = 0
    for i in range(c["n"]):
        seed = c["seed0"] + i
        p = dict(s["parameters"])
        p["prompt"] = s["prompt"]
        p["prompt_style"] = style
        p["seed"] = seed
        if c["tiling"]:
            p["tile_x"] = True
            p["tile_y"] = True
        if dry:
            print("  [dry] cell %s seed %d  tiling=%s" % (cell, seed, c["tiling"]))
            continue
        _, row = rd.generate(p, led, "%s_%05d" % (cell, seed), budget,
                             image_subdir="cell_" + cell,
                             claim="rd_yield:%s:%d" % (cell, seed),
                             extra={"cell": cell, "tiling": c["tiling"], "seed_used": seed,
                                    "style": style, "conditioned": False})
        sess.note_billed(row)
        spent += 1
        print("  cell %s seed %d  %s  %ss  est=%s act=%s%s"
              % (cell, seed, row["verdict"], row.get("seconds"), row.get("estimated_cost"),
                 row.get("actual_cost"),
                 "  DIVERGENT" if row.get("estimate_matched") is False else ""))
    return spent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", required=True, help="prompt_style, resolved live by audit.py")
    ap.add_argument("--cell", choices=sorted(CELLS) + ["both"], default="both")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; spends nothing")
    a = ap.parse_args()

    rd.preflight()
    os.makedirs(OUT, exist_ok=True)
    led = rd.Ledger(OUT, "yield_ledger.jsonl")
    cells = sorted(CELLS) if a.cell == "both" else [a.cell]

    if a.dry_run:
        print("-- DRY RUN: nothing spent --")
        print(json.dumps({"cells": {k: CELLS[k] for k in cells}, "budget": RUN_BUDGET,
                          "baseline": BASELINE, "style": a.style}, indent=1))
        for cell in cells:
            run_cell(led, None, None, cell, a.style, True)
        return 0

    budget = rd.Budget(ceiling=min(RUN_BUDGET, rd.SESSION_CEILING))
    sess = rd.Session(OUT, "rd_yield", budget=budget,
                      declaration={"cells": {k: CELLS[k] for k in cells},
                                   "run_budget": RUN_BUDGET, "baseline": BASELINE,
                                   "style": a.style, "conditioned": False,
                                   "subject": "prompts/floor_material_rd.json",
                                   "refusals": [
                                       "promotes nothing in any state",
                                       "touches no tier-one file, corpus file, or survivor",
                                       "alters no constant in any instrument",
                                       "both cells spent in full whatever cell N shows"]}).open()
    total = 0
    for cell in cells:
        print("\n== cell %s (tiling=%s) ==" % (cell, CELLS[cell]["tiling"]))
        total += run_cell(led, budget, sess, cell, a.style, False)
    sess.close()
    print("\nspent %d generations -> %s" % (total, os.path.relpath(OUT, rd.REPO)))
    print("next: screen.py (ring + census), then the blind A/B.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
