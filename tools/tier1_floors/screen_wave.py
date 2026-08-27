#!/usr/bin/env python3
"""Screen a generation wave, mechanically, and write the counts. No candidate is promoted here.

Runs `ring_instrument` (unchanged, untuned) and this session's `field_laws` over every child in
a wave and writes SCREEN-<wave>.json: the per-child verdict, the cull reason, and the counts the
report needs — generated / screened-out / by-which-law / survived.

Per the gauntlet clause §1.1.1, mechanical disqualifiers are culled without ceremony and the
morgue goes to the ledger. Rafe sees survivors and counts, never the morgue.
"""
import argparse
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import field_laws as FL      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GEN = os.path.join(HERE, "gen")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", required=True)
    ap.add_argument("--glob", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pat = a.glob or os.path.join(GEN, a.wave, "**", "*.png")
    paths = sorted(glob.glob(pat, recursive=True))
    if not paths:
        raise SystemExit("REFUSING: no images matched %s. An empty screen is a silent no-op "
                         "(LOOP-PROCESS §4.2), not a result." % pat)

    rows, codes = [], collections.Counter()
    for p in paths:
        v = FL.verdict(p)
        rows.append(v)
        if v["codes"]:
            for c in v["codes"]:
                codes[c] += 1
        else:
            codes["CLEAN"] += 1

    clean = [r for r in rows if not r["codes"]]
    out = a.out or os.path.join(HERE, "SCREEN-%s.json" % a.wave)
    res = dict(wave=a.wave, commit=FL.git_commit(),
               instrument=os.path.relpath(FL.__file__, REPO),
               instrument_sha256=FL.sha256_file(FL.__file__),
               instrument_controls="tools/tier1_floors/controls/CONTROLS.json",
               constants=dict(MIN_INCIDENT_FRAC=FL.MIN_INCIDENT_FRAC,
                              MIN_INCIDENT_BBOX=FL.MIN_INCIDENT_BBOX,
                              MIN_CONTRAST=FL.MIN_CONTRAST,
                              MIN_FRAME_INTERIOR=FL.MIN_FRAME_INTERIOR,
                              MAX_SEAM_RATIO=FL.MAX_SEAM_RATIO),
               generated=len(rows), survived=len(clean),
               culled_by_code=dict(codes), children=rows,
               survivors=[r["file"] for r in clean])
    with open(out, "w") as f:
        json.dump(res, f, indent=1)

    print("wave %s: %d generated, %d survived every mechanical screen" % (a.wave, len(rows), len(clean)))
    print("  culls by code (a child may carry several):")
    for c, n in codes.most_common():
        print("     %-10s %3d" % (c, n))
    print("written: %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
