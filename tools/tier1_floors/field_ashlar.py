#!/usr/bin/env python3
"""ASSEMBLE THE ASHLAR FIELD, APPLY THE RUNTIME REMAP, AND MEASURE THE FIVE THINGS THAT DECIDE IT.

    ENCLOSURE       session one's terminal finding was "joints enclose nothing — 99.1% of the
                    floor is one connected region". That number is the bar.

    BOUNDARY STEP   ruling (1)'s metric. The crossing-joint geometry put a value step through
                    every stone spanning a cell boundary: 8.72 against 1.17 inside a tile, 7.44x.
                    Blending it got to 2.95x and no further, because a blend hides a disagreement
                    rather than removing one. Under a shared stone address it should be exactly
                    1.00x, and "exactly" is the point — if it is 1.03 something is still keyed
                    per-tile and must be found, not tuned.

    CONTINUITY      the governing test for coursing, per ruling: A LINE THAT TRAVELS ACROSS
                    BOUNDARIES IS MATERIAL; A TREATMENT LOCKED TO BOUNDARIES IS A FRAME. Measured
                    as the share of joint pixels arriving at a tile boundary that carry on
                    through it.

    GRID HIDING     the other half of the same ruling — coursing must HIDE the grid, not reveal
                    it. The bed joint on a tile boundary and the bed joint halfway up the tile
                    are both bed joints of one 16px lattice, so they must be indistinguishable.
                    Measured as the ratio of their joint density and of their mean value. A
                    coursing that travels but draws its boundary line heavier has still drawn the
                    grid, and this is the number that would say so.

    CROSSING SPREAD the clarified law's floor, reported where crossings exist. Under an ashlar
                    bond nothing crosses a horizontal boundary — a bed joint RUNS ALONG it — so
                    that orientation reports n=0 by construction rather than by degeneracy, and
                    the continuity and grid-hiding numbers are what carry it. Reported plainly
                    either way; a zero that is explained is still a zero on the record.

EVERY ONE OF THESE HAS A PLANT (§4, bible §13.5: no instrument's pass counts until it has
demonstrated it can fail). `--plants` builds four deliberately broken fields and asserts that the
matching instrument fires on each and that the others stay quiet.
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
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402
import ring_instrument as RI     # noqa: E402

T = CA.T


# =================================================================================================
# ASSEMBLY — the tiles supply material and bond; this supplies the stone values.
# =================================================================================================

def stone_worn(worn, kind, x, y):
    """Is this stone in the trodden channel?

    Decided from the MAP, which both tiles either side of a boundary can read, and never from
    "which tile am I". A stone spanning a boundary counts as trodden only when the cells on both
    sides are — so the channel ends at a JOINT rather than at a tile edge, and its boundary is
    the last stone the feet actually polished.
    """
    if worn is None:
        return False
    if kind == 0:
        return bool(worn(x - 1, y)) and bool(worn(x, y))
    if kind == 2:
        return bool(worn(x, y)) and bool(worn(x + 1, y))
    return bool(worn(x, y))


def assemble(w, h, seed, mat, worn=None, defect=None):
    """Lay a w x h field, then paint the material onto it one stone at a time.

    The tiles supply the bond. Everything else — a stone's value and a stone's grain — is chosen
    by that stone's WORLD ADDRESS and sampled in STONE-LOCAL coordinates, so both tiles either
    side of a boundary paint the identical material onto the identical stone.

    `defect` names a plant; see `PLANTS`.
    """
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)
    amp = max(mat["grain_mad"], 1.0)
    img = np.zeros((h * T, w * T, 3), dtype=np.uint8)
    joints = np.zeros((h * T, w * T), dtype=bool)
    yy, xx = np.mgrid[0:T, 0:T]

    for y in range(h):
        for x in range(w):
            n = CA.edge_family(x, y, CA.HORIZ, seed)
            s_ = CA.edge_family(x, y + 1, CA.HORIZ, seed)
            wf = CA.edge_family(x, y, CA.VERT, seed)
            e = CA.edge_family(x + 1, y, CA.VERT, seed)
            drops = tuple(CA.drop_choice(x, y * CA.COURSES + c, seed)
                          for c in range(CA.COURSES))
            _tile, jm, cls, L = CA.build_tile(n, e, s_, wf, mat, seed, drops)
            L = L.astype(float)

            for c in range(CA.COURSES):
                course_k = y * CA.COURSES + c
                for kind in (0, 1, 2):
                    m = cls == (1 + c * 3 + kind)
                    if not m.any():
                        continue
                    # THE ADDRESS. A spanning stone is addressed by ITS BOUNDARY — the one piece
                    # of data both tiles either side of it possess — so both compute the same key
                    # and the step is zero rather than small.
                    addr = CA.stone_kind_address(kind, drops[c])
                    if addr == 0:
                        bx, key = x, CA.stone_key_span(x, course_k, seed)
                    elif addr == 2:
                        bx, key = x + 1, CA.stone_key_span(x + 1, course_k, seed)
                    else:
                        bx, key = x, CA.stone_key_interior(x, course_k, seed)
                    if defect == "per_tile_value":
                        # THE PLANT FOR RULING (1): address the stone by the tile it is seen from
                        # instead of by the boundary it straddles — the old geometry's mistake.
                        key = CA.mix(x * 31 + kind, course_k, CA.INTERIOR + seed)

                    is_worn = stone_worn(worn, addr, x, y)
                    ox = CA.stone_origin(wf, e, kind, c, drops[c])
                    oy = c * CA.COURSE_H + 1
                    lx, ly = (xx - ox) % (2 * T), (yy - oy) % (2 * T)
                    g = (CA.grain_patch(key, 8, seed)[ly, lx] * 0.34
                         + CA.grain_patch(key, 16, seed)[ly, lx] * 0.14)
                    # Wear is absence: the grain is walked off the stone and its value closes up
                    # on the family median. No brightening anywhere — §8.2.1.
                    bias = CA.cluster_bias(bx, course_k, seed)
                    L = L + m * (CA.stone_offset(key, step, worn=is_worn, bias=bias)
                                 + g * amp * (0.38 if is_worn else 1.0))

            if defect == "boundary_frame":
                # THE PLANT FOR GRID HIDING: an extra joint along the tile's own edge.
                L[0, :] = mat["lum_median"] * 0.35
                L[:, 0] = mat["lum_median"] * 0.35
                jm = jm.copy()
                jm[0, :] = True
                jm[:, 0] = True
            if defect == "broken_courses":
                # THE PLANT FOR CONTINUITY: bed joints stop short of the EAST edge. Cut on one
                # side only — cutting both removes the arrival as well as the crossing, and an
                # instrument must be shown to fail on a defect it can still see.
                for col in (T - 2, T - 1):
                    L[:, col] = np.where(jm[:, col], mat["lum_median"], L[:, col])
                jm = jm.copy()
                jm[:, T - 2:] = False

            L = CF.quantise(np.clip(L, mat["lum_lo"], mat["lum_hi"]), mat["ladder"])
            img[y * T:(y + 1) * T, x * T:(x + 1) * T] = \
                CF.colourise(L, mat["tint"]).astype(np.uint8)
            joints[y * T:(y + 1) * T, x * T:(x + 1) * T] = jm

    if defect == "value_lattice":
        # THE PLANT FOR THE TINT LATTICE ITSELF: a value ramp locked to the tile grid.
        L = RI.lum(img.astype(float))
        _, gx = np.mgrid[0:h * T, 0:w * T]
        L = L + ((gx // T) % 2) * step * 1.2
        L = CF.quantise(np.clip(L, mat["lum_lo"], mat["lum_hi"]), mat["ladder"])
        img = CF.colourise(L, mat["tint"]).astype(np.uint8)

    # NO TRANSITION LIST. Wear is now decided per stone, so the channel's edge falls on a joint
    # rather than on a tile boundary, and there is no longer an intended material step at any
    # vertical boundary to exclude. The empty list is the finding, not an omission.
    return img, joints, []


# =================================================================================================
# INSTRUMENTS
# =================================================================================================

def enclosure(joints):
    """Connected components of the NON-joint pixels: the stones. Reported as session one did."""
    h, w = joints.shape
    lab = np.full((h, w), -1, dtype=int)
    sizes, nxt = [], 0
    for sy in range(h):
        for sx in range(w):
            if joints[sy, sx] or lab[sy, sx] >= 0:
                continue
            stack, size = [(sy, sx)], 0
            lab[sy, sx] = nxt
            while stack:
                yy, xx = stack.pop()
                size += 1
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < h and 0 <= nx < w and not joints[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = nxt
                        stack.append((ny, nx))
            sizes.append(size)
            nxt += 1
    total = int((~joints).sum())
    sizes.sort(reverse=True)
    return dict(regions=len(sizes), floor_px=total,
                largest_share=round(sizes[0] / total, 4) if total else 1.0,
                median_region=int(np.median(sizes)) if sizes else 0,
                regions_over_64px=sum(1 for s in sizes if s >= 64))


def boundary_step(img, joints, w, h, transitions=()):
    """RULING (1)'s metric: is a value step at a tile boundary bigger than one inside a tile?

    Measured on STONE pixels only. A joint is meant to be a step — measuring across joints would
    report the bond as a defect and would have let the real defect hide behind it.
    """
    L = RI.lum(img.astype(float))
    stone = ~joints
    dx = np.abs(np.diff(L, axis=1))
    ok = stone[:, :-1] & stone[:, 1:]
    cols = np.arange(dx.shape[1])
    at = np.zeros_like(cols, dtype=bool)
    trans = np.zeros_like(cols, dtype=bool)
    for x in range(1, w):
        (trans if x in set(transitions) else at)[x * T - 1] = True
    interior = ~(at | trans)
    b = dx[:, at][ok[:, at]]
    i = dx[:, interior][ok[:, interior]]
    bm = float(b.mean()) if b.size else 0.0
    im = float(i.mean()) if i.size else 0.0
    t = dx[:, trans][ok[:, trans]]
    return dict(boundary_mean=round(bm, 3), interior_mean=round(im, 3),
                ratio=round(bm / im, 3) if im else None,
                boundary_max=round(float(b.max()), 2) if b.size else 0.0, n=int(b.size),
                channel_edge_mean=round(float(t.mean()), 3) if t.size else None,
                channel_edge_n=int(t.size))


def _travelling(joints, y, x, run=3):
    """Is this joint pixel part of a HORIZONTAL run — a line going somewhere, not a head joint?

    The first version of `continuity` counted every joint pixel next to a boundary, which meant
    head joints (vertical, a few px long, ending at a bed line) were counted as lines that had
    "failed to continue". On the clean field that read 0.4978 and would have condemned a floor
    whose coursing was in fact unbroken. A joint that was never travelling cannot fail to travel.
    """
    W = joints.shape[1]
    n = 0
    for d in (-1, 1):
        xx = x + d
        while 0 <= xx < W and joints[y, xx] and n < run:
            n += 1
            xx += d
    return n >= run


def continuity(joints, w, h):
    """Does a line arriving at a tile boundary carry on through it?

    A line that travels is material; one that stops at the boundary is a frame. Counted from BOTH
    sides — the first version only looked left, so a plant that cut the courses on the east side
    of every tile produced no arrivals at all and the instrument reported None instead of failing.
    An instrument that goes quiet on the defect it exists to find is worse than no instrument.
    """
    arrive = carry = 0
    for x in range(1, w):
        c = x * T
        for y in range(joints.shape[0]):
            l, r = bool(joints[y, c - 1]), bool(joints[y, c])
            if not (l or r):
                continue
            if not ((l and _travelling(joints, y, c - 1)) or (r and _travelling(joints, y, c))):
                continue                      # a head joint, which was never going anywhere
            arrive += 1
            carry += int(l and r)
    return dict(arriving=arrive, continuing=carry,
                continued=round(carry / arrive, 4) if arrive else None)


def grid_hiding(img, joints, w, h):
    """Is the bed joint ON a tile boundary distinguishable from the one halfway up the tile?

    If it is, the coursing has revealed the grid instead of hiding it, whatever its continuity
    says. Two ratios, both of which should sit at 1.00: joint density, and mean value.

    Also reports the VERTICAL boundary's excess, where there is no bed joint to hide behind and
    any excess at all is a frame.
    """
    L = RI.lum(img.astype(float))
    H, W = joints.shape
    ry = np.arange(H) % T
    bnd = (ry == 0) | (ry == T - 1)                       # the boundary bed line, both halves
    mid = (ry == CA.COURSE_H - 1) | (ry == CA.COURSE_H)    # the mid-tile bed line
    bd, md = float(joints[bnd].mean()), float(joints[mid].mean())
    bv, mv = float(L[bnd].mean()), float(L[mid].mean())

    cx = np.arange(W) % T
    at_col = (cx == 0)
    other = ~at_col
    cbd, cod = float(joints[:, at_col].mean()), float(joints[:, other].mean())
    return dict(bed_density_boundary=round(bd, 4), bed_density_mid=round(md, 4),
                bed_density_ratio=round(bd / md, 4) if md else None,
                bed_value_boundary=round(bv, 2), bed_value_mid=round(mv, 2),
                bed_value_ratio=round(bv / mv, 4) if mv else None,
                col_density_boundary=round(cbd, 4), col_density_other=round(cod, 4),
                col_density_ratio=round(cbd / cod, 4) if cod else None)


def crossing_spread(joints, w, h):
    """Where joints cross each boundary, and how spread those offsets are. n=0 where a joint runs
    ALONG the boundary instead of across it, which under an ashlar bond is the horizontal case."""
    xs, ys = [], []
    for cy in range(1, h):
        row = joints[cy * T, :]
        if row.mean() > 0.5:            # a bed joint runs along it; there is nothing to cross
            continue
        for cx in range(w):
            seg = np.where(row[cx * T:(cx + 1) * T])[0]
            if len(seg):
                ys.append(int(seg.mean()))
    for cx in range(1, w):
        col = joints[:, cx * T]
        for cy in range(h):
            seg = np.where(col[cy * T:(cy + 1) * T])[0]
            for v in seg:
                xs.append(int(v))
    def stats(v):
        if not v:
            return dict(n=0)
        a = np.array(v)
        vals, counts = np.unique(a, return_counts=True)
        return dict(n=len(a), distinct=int(len(vals)), sd=round(float(a.std()), 2),
                    spread=int(a.max() - a.min()),
                    modal_share=round(float(counts.max()) / len(a), 3))
    return dict(horizontal_boundaries=stats(ys), vertical_boundaries=stats(xs))


def measure(img, joints, w, h, transitions=()):
    return dict(enclosure=enclosure(joints),
                boundary_step=boundary_step(img, joints, w, h, transitions),
                continuity=continuity(joints, w, h), grid_hiding=grid_hiding(img, joints, w, h),
                crossings=crossing_spread(joints, w, h))


# =================================================================================================
# THE PLANTS — §4 and bible §13.5. No instrument's pass counts until it has failed.
# =================================================================================================
#
# Each plant names the instrument that MUST fire and the threshold that decides it. A plant that
# fires the wrong instrument is as much a failure as one that fires nothing.

PLANTS = [
    dict(name="per_tile_value", must_fire="boundary_step",
         why="stones addressed by the tile they are seen from instead of by the boundary they "
             "straddle — ruling (1)'s defect, restated exactly",
         test=lambda m: (m["boundary_step"]["ratio"] or 0) > 1.5),
    dict(name="value_lattice", must_fire="boundary_step",
         why="a value ramp locked to the tile grid — session one's tint lattice in its purest form",
         test=lambda m: (m["boundary_step"]["ratio"] or 0) > 1.5),
    dict(name="boundary_frame", must_fire="grid_hiding",
         why="an extra joint drawn along the tile's own edge: a treatment at a constant position",
         test=lambda m: (m["grid_hiding"]["col_density_ratio"] or 0) > 1.5),
    dict(name="broken_courses", must_fire="continuity",
         why="bed joints stopping short of the vertical boundaries — coursing that does not travel",
         # `x or 1.0` on a measured 0.0 yields 1.0, because 0.0 is falsy — so the plant that
         # severed EVERY course scored a perfect failure and was reported as a pass. Explicit
         # None, never truthiness, on any value whose legitimate range includes zero.
         test=lambda m: m["continuity"]["continued"] is not None
         and m["continuity"]["continued"] < 0.75),
]


def run_plants(w, h, seed, mat):
    print("PLANTS — every instrument must demonstrate it can fail (§4, bible §13.5)\n")
    rows, ok = [], True
    for p in PLANTS:
        img, joints, tr = assemble(w, h, seed, mat, defect=p["name"])
        m = measure(img, joints, w, h, tr)
        fired = bool(p["test"](m))
        rows.append(dict(plant=p["name"], must_fire=p["must_fire"], why=p["why"],
                         fired=fired, measured=m))
        ok &= fired
        print("  %-16s -> %-14s %s" % (p["name"], p["must_fire"], "FIRED" if fired else "SILENT"))
        print("       %s" % p["why"])
        print("       boundary_step ratio %s | continuity %s | col_density_ratio %s"
              % (m["boundary_step"]["ratio"], m["continuity"]["continued"],
                 m["grid_hiding"]["col_density_ratio"]))
        if not fired:
            print("       ^^ THIS INSTRUMENT HAS NOT SHOWN IT CAN FAIL. Its pass does not count.")
    print()
    return ok, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--h", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--plants", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    os.makedirs(a.out, exist_ok=True)

    plants = None
    if a.plants:
        ok, plants = run_plants(a.w, a.h, a.seed, mat)
        if not ok:
            print("REFUSING: an instrument could not be made to fail. Fix the instrument first.")
            return 1

    print("ASHLAR FIELD — %dx%d cells, seed %d\n" % (a.w, a.h, a.seed))
    rows = {}
    for label, worn in (("ordinary", None),
                        ("with_channel", lambda x, y: a.w // 2 - 1 <= x <= a.w // 2)):
        img, joints, tr = assemble(a.w, a.h, a.seed, mat, worn)
        p = os.path.join(a.out, "ashlar_%s.png" % label)
        Image.fromarray(img).save(p)
        m = measure(img, joints, a.w, a.h, tr)
        try:
            import field_preview as FP
            m["lattice"] = FP.lattice_score(img)
        except Exception:
            m["lattice"] = None
        rows[label] = dict(file=os.path.relpath(p, REPO), **m)
        e, b, c, g = m["enclosure"], m["boundary_step"], m["continuity"], m["grid_hiding"]
        print("  %s" % label)
        print("     enclosure:    %d regions, largest holds %.1f%% (session one: 99.1%%), "
              "median %dpx, %d over 64px"
              % (e["regions"], 100 * e["largest_share"], e["median_region"],
                 e["regions_over_64px"]))
        print("     boundary step: %.3f at boundaries vs %.3f inside — ratio %s  (was 7.44x, "
              "then 2.95x)" % (b["boundary_mean"], b["interior_mean"], b["ratio"]))
        if b["channel_edge_mean"] is not None:
            print("                    channel edge %.3f over %d px — an INTENDED transition, "
                  "reported apart" % (b["channel_edge_mean"], b["channel_edge_n"]))
        print("     continuity:   %s of joints arriving at a vertical boundary carry through "
              "(%d of %d)" % (c["continued"], c["continuing"], c["arriving"]))
        print("     grid hiding:  boundary bed vs mid bed — density %s, value %s; "
              "boundary column vs others %s"
              % (g["bed_density_ratio"], g["bed_value_ratio"], g["col_density_ratio"]))
        if m["lattice"]:
            print("     lattice:      %.4f" % m["lattice"]["lattice"])

    res = dict(commit=FL.git_commit(), grid=[a.w, a.h], seed=a.seed,
               session_one_largest_share=0.991,
               prior_boundary_step_ratio=dict(unblended=7.44, blended=2.95),
               plants=plants, fields=rows)
    p = os.path.join(a.out, "ASHLAR-FIELD.json")
    with open(p, "w") as f:
        json.dump(res, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
