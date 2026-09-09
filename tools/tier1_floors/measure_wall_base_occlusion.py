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

⚠ ALL FOUR SIDES — AND THE CLAIM THAT SAID OTHERWISE WAS MINE AND WAS WRONG.

This header used to read: *"the four occlusion sprites are not symmetric — N and W carry a ramp
from 0.72 alpha at the edge to zero seven art-pixels in, while E and S carry a flat ~0.05 wash."*
**That is false.** All four sprites are symmetric and carry the same 0.72 ramp; E's lies along its
LAST columns and S's along its LAST rows, and the reading that produced the claim printed only the
first four rows/columns of each — the far end from E's and S's ramps. `compose_family.build_occlusion`
builds all four from one expression and always did.

    side   ramp at            first 4                last 4
    N      top rows           0.72 0.52 0.36 0.23    0.00 0.00 0.00 0.00
    E      last columns       0.00 0.00 0.00 0.00    0.23 0.36 0.52 0.72
    S      last rows          0.00 0.00 0.00 0.00    0.23 0.36 0.52 0.72
    W      first columns      0.72 0.53 0.36 0.23    0.00 0.00 0.00 0.00

It is recorded rather than quietly deleted because the false version was cited as evidence in a
filed issue and in a routing, and a correction that leaves no trace teaches nothing. §13.10's
standard cuts both ways: a measurement that convicts a witness needs the witness's proof standard,
and this one convicted the composer of an asymmetry it never had.

So the seam is measured on EVERY side a wall actually adjoins. The reference band is taken across
the cell's middle on the axis perpendicular to the edge, so each side is compared against its own
interior rather than against a fixed strip.

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

import re

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
LOCAL = 12            # the strip just inside the seam -- the ground a viewer compares it to
REF0, REF1 = 24, 48   # retained: the mid-cell band, no longer used as the reference
FLOOR = 0.1440    # §13.8's ruled perceptual floor, in Weber contrast
LIT = 60          # below this the cell is not being judged: dark illegibility is design (§8.2.1)


PLAYER_RE = re.compile(r"player=\((\d+),(\d+)\)")


def _player(log):
    """The station, from the engine's own log rather than from an assumption (S13.10)."""
    txt = open(log, errors="ignore").read()
    m = PLAYER_RE.search(txt)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"--corridor-scene res://(\S+\.json)", txt)
    if not m:
        return None
    d = json.load(open(os.path.join(REPO, m.group(1))))
    return d["player"]["x"], d["player"]["y"]


SIDES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def _bands(blk, side):
    """(contact band, reference band) for one side of one cell.

    THE REFERENCE IS LOCAL, and the mid-cell reference it replaces was an artefact factory.
    It compared the contact band against the cell's MIDDLE, 24-48px away, and a 64px cell
    under a carried lamp has a steep gradient across it. On the corridor-mouth cell (8,11)
    the west edge faces the lamp: contact 103.4, mid-cell 109.4, but the strip just inside
    the edge 161.2. The seam measured 0.0546 against the middle and 0.3582 against its own
    neighbourhood -- a 6.5x understatement that read as a missing boundary and WAS FILED AS
    A DEFECT (#199).

    A seam is a LOCAL step, so it is measured against the ground immediately inside it,
    which is also what a viewer compares it to. The lamp's gradient then falls out of both
    terms instead of landing entirely in one.
    """
    if side == "N":
        return blk[:CONTACT, :], blk[CONTACT:CONTACT + LOCAL, :]
    if side == "S":
        return blk[-CONTACT:, :], blk[-CONTACT - LOCAL:-CONTACT, :]
    if side == "W":
        return blk[:, :CONTACT], blk[:, CONTACT:CONTACT + LOCAL]
    return blk[:, -CONTACT:], blk[:, -CONTACT - LOCAL:-CONTACT]


def cells(png, log, side="N"):
    """Floor cells with a wall on `side`, as (route_level, contact_band, reference_band, pos)."""
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
    player = _player(log)
    out = []
    for ty in range(1, fh):
        for tx in range(fw):
            lv = int(f[ty, tx])
            if lv < 0:                      # this cell is solid
                continue
            # THE PLAYER'S OWN CELL IS EXCLUDED -- A SPRITE STANDS IN IT. The second
            # artefact behind #199: at (6,12) the hero occupies the north contact band, so
            # its mean is lifted by pixels that are not floor -- 131.5 against 113.3 and
            # 126.3 at the two neighbours on a similar reference, pushing the seam to
            # 0.1289 and reading as a cell whose boundary had gone. A floor's contact seam
            # cannot be measured through a figure standing on it.
            if player and (tx, ty) == player:
                continue
            dx, dy = SIDES[side]
            nx, ny = tx + dx, ty + dy
            if not (0 <= ny < fh and 0 <= nx < fw) or int(f[ny, nx]) >= 0:
                continue                     # no wall on that side: no seam to measure
            y0, x0 = oy + ty * T, ox + tx * T
            if y0 < 0 or x0 < 0 or y0 + T > H or x0 + T > W:
                continue
            blk = L[y0:y0 + T, x0:x0 + T]
            contact, ref = _bands(blk, side)
            if np.median(ref) < LIT:
                continue
            out.append((lv, contact, ref, (tx, ty)))
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


def measure(png, log, side="N"):
    cs = cells(png, log, side)
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
    print("§12.1's CONTACT OCCLUSION ON THE DELIVERED FRAME — every side a wall adjoins, "
          "against §13.8's %.4f\n" % FLOOR)
    print("  %-18s %-4s %-6s %5s %9s %8s %9s %8s"
          % ("capture", "side", "band", "n", "weber", "levels", "worst", "worst cell"))
    out = {}
    for stem in a.stems:
        png = os.path.join(HERE, "evidence", stem + ".png")
        log = os.path.join(HERE, "evidence", stem + ".log")
        if not (os.path.exists(png) and os.path.exists(log)):
            print("  %-22s (missing capture or log)" % stem)
            continue
        out[stem] = {}
        first = True
        for side in ("N", "E", "S", "W"):
            r = measure(png, log, side)
            if r is None:
                continue
            out[stem][side] = r
            for key in ("all", "lane", "flank"):
                b = r[key]
                if not b:
                    continue
                print("  %-18s %-4s %-6s %5d %9.4f%s %8.2f %9.4f %8s"
                      % (stem if first else "", side if key == "all" else "", key, b["n"],
                         b["weber_mean"], " " if b["weber_mean"] >= FLOOR else "!",
                         b["levels_mean"], b["worst_weber"], str(tuple(b["worst_cell"]))))
                first = False
        if not out[stem]:
            print("  %-18s (no wall-adjacent lit floor cell in view)" % stem)
    p = os.path.join(HERE, a.json_out)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(commit=FL.git_commit(), floor=FLOOR, contact_rows=CONTACT,
                   reference_rows=[REF0, REF1], captures=out), open(p, "w"), indent=1)
    print("\n  ! marks a band whose mean seam is below the perceptual floor.")
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
