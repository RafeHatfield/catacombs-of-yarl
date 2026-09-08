#!/usr/bin/env python3
"""DOES §12.1's CONTACT OCCLUSION SURVIVE THE LAMP — ON THE LANE, WHERE THE SHINE IS?

Issue #184, second reading, in Rafe's words at the 2026-09-07 room walk:

    "the worn lane is slightly too shiny and its shine washes out the wall-base occlusion
     shadow, so walls lose mass where the lane meets them."

That is a claim about a DIFFERENCE, not about a level, and it is why this instrument reports two
populations rather than one number. The floor's contact occlusion is subtracted from the ALBEDO in
whole ladder rungs; the polish specular is ADDED in the light() pass and, before this round, was
computed from `polish_by_age` and the lane mask with no knowledge of the occlusion at all. So on a
flank cell the seam is drawn against a matte stone and on a lane cell it is drawn against a stone
carrying a superlinear specular — the same subtraction, two different pictures.

    LANE CONTACT CONTRAST     wall-adjacent floor cells the route runs through (level >= 7)
    FLANK CONTACT CONTRAST    wall-adjacent floor cells off the route          (level <= 4)

Both measured on the DELIVERED frame, in luminance levels and in Weber contrast against §13.8's
ruled floor of 0.1440. The ratio lane/flank is the number the complaint is about: at 1.00 the seam
reads the same wherever it is, and below it the lane is eating the boundary.

⚠ NORTH EDGES ONLY, AND THAT IS NOT A SHORTCUT. The four occlusion sprites are not symmetric — N
and W carry a ramp from 0.72 alpha at the edge to zero seven art-pixels in, while E and S carry a
flat ~0.05 wash (measured off the shipped PNGs). The wall-base seam the walk is about is the one
under a wall's SOUTH FACE, which is the N edge of the floor cell below it. Pooling the four would
average the seam with three washes and report a smaller effect than exists.

⚠ AND IT READS THE ENGINE'S OWN FIELD FOR BOTH THE WALLS AND THE ROUTE (§13.10). The route-strength
map in the capture log marks solid cells '#'; the tile origin comes from the engine's legibility
probe, never from an assumption that the field is centred — the camera follows the player and a
centred formula was 160px out in x on this very station.

    measure_wall_base_occlusion.py <stem> [<stem> ...]

Each stem names `evidence/<stem>.png` and `evidence/<stem>.log`.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import field_laws as FL                  # noqa: E402
import measure_perceptual_floor as MPF   # noqa: E402
import measure_traffic_read as MTR       # noqa: E402

T = 64            # screen px per tile (32 art at 2x)
CONTACT = 8       # screen rows at the wall foot: art rows 0-3, alpha 0.72/0.52/0.36/0.23
REF0, REF1 = 24, 48   # the cell's own interior, clear of the seam and of the far edge
FLOOR = 0.1440    # §13.8's ruled perceptual floor, in Weber contrast
LIT = 60          # below this the cell is not being judged: dark illegibility is design (§8.2.1)


def cells(png, log):
    """Wall-adjacent floor cells, as (route_level, contact_band, reference_band)."""
    L = MPF.lum(np.asarray(Image.open(png).convert("RGB")).astype(float))
    f = MTR.read_field(log)
    if f is None:
        return None
    H, W = L.shape
    fh, fw = f.shape
    o = MTR.tile_origin(log)
    if o is None:
        return None
    ox, oy = o
    out = []
    for ty in range(1, fh):
        for tx in range(fw):
            lv = int(f[ty, tx])
            if lv < 0:                      # this cell is solid
                continue
            if int(f[ty - 1, tx]) >= 0:     # no wall to the north: no seam to measure
                continue
            y0, x0 = oy + ty * T, ox + tx * T
            if y0 < 0 or x0 < 0 or y0 + T > H or x0 + T > W:
                continue
            blk = L[y0:y0 + T, x0:x0 + T]
            ref = blk[REF0:REF1, :]
            if np.median(ref) < LIT:
                continue
            out.append((lv, blk[:CONTACT, :], ref, (tx, ty)))
    return out


def band(rows):
    """Contact contrast for one population: levels, Weber, and THE WORST CELL.

    The worst cell is reported for every band on purpose. A mean over wall-adjacent cells hides
    the one where the seam has gone entirely, and one cell with no boundary at all is what a seat
    sees as *the wall has no foot* — the whole band reading 'fine' does not answer it.
    """
    if not rows:
        return None
    per = []
    for lv, contact, ref, pos in rows:
        r = float(np.mean(ref))
        c = float(np.mean(contact))
        per.append((float((r - c) / max(r, 1e-6)), r - c, pos))
    per.sort()
    webers = [p[0] for p in per]
    return dict(n=len(per),
                weber_mean=round(float(np.mean(webers)), 4),
                levels_mean=round(float(np.mean([p[1] for p in per])), 2),
                worst_weber=round(per[0][0], 4),
                worst_levels=round(per[0][1], 2),
                worst_cell=list(per[0][2]),
                below_floor=sum(1 for w in webers if w < FLOOR))


def measure(png, log):
    cs = cells(png, log)
    if not cs:
        return None
    lane = [c for c in cs if c[0] >= 7]
    flank = [c for c in cs if c[0] <= 4]
    r = dict(all=band(cs), lane=band(lane), flank=band(flank))
    if r["lane"] and r["flank"] and r["flank"]["weber_mean"] > 1e-6:
        r["lane_over_flank"] = round(r["lane"]["weber_mean"] / r["flank"]["weber_mean"], 3)
    else:
        r["lane_over_flank"] = None
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stems", nargs="+")
    ap.add_argument("--json-out", default="evidence/WALL-BASE-OCCLUSION.json")
    a = ap.parse_args()
    print("§12.1's CONTACT OCCLUSION ON THE DELIVERED FRAME — north edges, "
          "against §13.8's %.4f\n" % FLOOR)
    print("  %-22s %-6s %5s %9s %8s %9s %8s %8s"
          % ("capture", "band", "n", "weber", "levels", "worst", "wlevels", "<floor"))
    out = {}
    for stem in a.stems:
        png = os.path.join(HERE, "evidence", stem + ".png")
        log = os.path.join(HERE, "evidence", stem + ".log")
        if not (os.path.exists(png) and os.path.exists(log)):
            print("  %-22s (missing capture or log)" % stem)
            continue
        r = measure(png, log)
        if r is None:
            print("  %-22s (no wall-adjacent lit floor cell in view)" % stem)
            continue
        out[stem] = r
        for key in ("all", "lane", "flank"):
            b = r[key]
            if not b:
                print("  %-22s %-6s (none)" % (stem if key == "all" else "", key))
                continue
            print("  %-22s %-6s %5d %9.4f%s %8.2f %9.4f %8.2f %4d/%d"
                  % (stem if key == "all" else "", key, b["n"],
                     b["weber_mean"], " " if b["weber_mean"] >= FLOOR else "!",
                     b["levels_mean"], b["worst_weber"], b["worst_levels"],
                     b["below_floor"], b["n"]))
        print("  %-22s lane/flank = %s"
              % ("", "n/a" if r["lane_over_flank"] is None else "%.3f" % r["lane_over_flank"]))
    p = os.path.join(HERE, a.json_out)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(commit=FL.git_commit(), floor=FLOOR, contact_rows=CONTACT,
                   reference_rows=[REF0, REF1], captures=out), open(p, "w"), indent=1)
    print("\n  ! marks a band whose mean seam is below the perceptual floor.")
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
