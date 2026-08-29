#!/usr/bin/env python3
"""THE EDGE-MATCHED FLOOR FAMILY — floor session two, task 1.

SESSION ONE'S TERMINAL FINDING, measured by a blind seat:

    "Joints enclose nothing — 99.1% of the floor is one connected region. No stones, only
     scratches. ... the entire 440x376 floor contains TWO enclosed cells of meaningful size.
     Every 'stone' leaks into every other stone. ... For an underworld whose whole premise is
     that it is ADMINISTERED, a floor that cannot show a single completed stone is arguing the
     opposite case."

A joint network can only close if joints AGREE ACROSS CELL BOUNDARIES. Session one's tiles each
wrapped against themselves, so every tile tiled — and tile A's joints met tile B's stone, so the
regions leaked diagonally through the whole room. No amount of bond, palette or grain work
reaches that; it is a property of the tile SYSTEM.

THE CLARIFIED LAW (ruling, this session): **matching is agreement, not constancy.** Edge-matched
sets are legal. A set is lattice-degenerate when its edge families are too few to vary the
crossing positions. The checkable floors: >= 3 edge families per boundary orientation, and
crossing-position variance across the assembled field, measured and reported.

THE CONSTRUCTION, and why it needs no solver
--------------------------------------------
The obvious way to lay a Wang set is to scan the map choosing tiles that fit their already-placed
neighbours. That needs a solver, can dead-end, and makes the result depend on scan order — three
properties a deterministic scene build should not have.

So the family is indexed the other way round. **The EDGE owns its family, not the tile.** Every
horizontal boundary in the map is assigned a family by hashing its own coordinates; every vertical
boundary likewise. A cell then simply reads the four boundaries it already has:

    N = H(x, y)      S = H(x, y+1)      W = V(x, y)      E = V(x+1, y)

Two neighbours read THE SAME boundary — cell (x,y)'s S and cell (x,y+1)'s N are both H(x, y+1) —
so agreement is guaranteed by construction rather than by search. There is no dead end, no scan
order, and the assembly is deterministic from the map alone.

The cost is that the family must contain a tile for every combination: 3^4 = 81. That is cheap
procedurally and is why >= 3 families per orientation is affordable rather than aspirational.

WHAT AN EDGE FAMILY IS
----------------------
A family is a CROSSING POSITION: where the joint passes through that boundary. Three families per
orientation means a joint crosses the northern boundary at one of three offsets, and its choice is
independent of the crossing on the southern one — so the joint through a cell leans, and across
the field the crossings do not line up. That independence is what the clarified law's variance
floor is measuring, and it is the difference between "matched" and "constant".

Inside the tile the crossings are connected: north-to-south and west-to-east, meeting in the
middle. Two crossing joints divide the cell into FOUR regions, and because every crossing agrees
with its neighbour's, those regions close across the whole field. That is the finding answered.

THE CHANNEL IS A SECOND RENDERING OF THE SAME BOND, not a lift
--------------------------------------------------------------
§6.3 at design time, which session one learned the hard way: a value lift cannot signal under a
carried lamp, because brightness is what the light is saying. A blind seat read the old channel's
polish as the torch — "the warmth is entirely the torch" — and three rounds of seats never saw
the channel at all.

So the channel is the SAME edge-matched tile, drawn worn: fewer joints (the minor ones sanded
away), the survivors shallower, the grain tighter. It signals by ABSENCE. It keeps the same edge
families, so a channel cell still matches its ordinary neighbours and the enclosure survives the
transition — which a separate channel tileset could not have done.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402

T = 32
FAMILIES = 3                       # per boundary orientation. The clarified law's floor.
ASSETS_REL = "src/Presentation/assets/tier1_wang"
ASSETS = os.path.join(REPO, ASSETS_REL)

# Crossing offsets, one per family. Unequal spacing on purpose: three families at 8/16/24 would
# put every crossing on a 8px lattice, which is the degenerate case the clarified law names.
CROSS = [7, 15, 24]

BASE_ID0 = 9800        # 81 ordinary tiles
CHAN_ID0 = 9900        # 81 channel tiles, same indices


def _i32(v):
    """Wrap to signed 32-bit, so this file computes exactly what the C# side computes."""
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def mix(x, y, salt):
    """The engine's hash, reproduced bit-for-bit.

    ⚠ THIS FUNCTION EXISTS TWICE — here and in C# — and that is the exact "copy that drifts"
    hazard this project has already been bitten by. It is tolerated only because the two are
    CHECKED against each other: the manifest carries a cross-check vector of sample values and
    the engine asserts it reproduces them at load. A duplicate with an enforcement is a different
    thing from a duplicate with a comment.
    """
    h = _i32(x * 7919 + y * 104729 + salt * 15485863)
    h = _i32(h ^ (h >> 13))            # C# >> on int is ARITHMETIC; Python's is too, on negatives
    h = _i32(h * 1274126177)
    h = _i32(h ^ (h >> 16))
    return h & 0x7FFFFFFF


def edge_family(a, b, salt, seed):
    """Family of one boundary, from its OWN coordinates. Both neighbours compute the same value.

    `salt` separates the horizontal boundary lattice from the vertical one; `seed` lets a map vary
    without changing the tile set.
    """
    return mix(a, b, salt + seed) % FAMILIES


HORIZ, VERT = 101, 202     # salts. Named so the two boundary lattices cannot collide.


def cross_check_vector(seed, n=64):
    """Sample (x, y, salt) -> family, stored in the manifest for the engine to reproduce."""
    out = []
    for i in range(n):
        x, y = i % 17, (i * 7) % 21
        out.append(dict(x=x, y=y, salt=HORIZ, family=edge_family(x, y, HORIZ, seed)))
        out.append(dict(x=x, y=y, salt=VERT, family=edge_family(x, y, VERT, seed)))
    return out


def tile_index(n, e, s, w):
    """A tile's position in the 81-tile family, from its four edge families."""
    return ((n * FAMILIES + e) * FAMILIES + s) * FAMILIES + w


def build_tile(n, e, s, w, mat, seed, worn=False):
    """One edge-matched tile: crossings connected, four regions, enclosing.

    `worn` is the channel rendering — the same bond with the minor joints sanded away and the
    survivors shallower. Same crossings, so it still matches its ordinary neighbours.
    """
    rng = np.random.default_rng(seed + tile_index(n, e, s, w) * 7919 + (99991 if worn else 0))
    stone = mat["lum_median"]
    L = np.full((T, T), stone, dtype=float)

    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)
    joints = np.zeros((T, T), dtype=bool)

    # The meeting point. Off-centre and jittered so the four regions are unequal — a cross through
    # the middle of every cell would be a constant position, which is §8.3.1's lattice arriving
    # through the very mechanism that fixes the enclosure.
    mx = int(np.clip((CROSS[w] + CROSS[e]) / 2 + rng.integers(-3, 4), 6, T - 7))
    my = int(np.clip((CROSS[n] + CROSS[s]) / 2 + rng.integers(-3, 4), 6, T - 7))

    def draw(p0, p1, wobble=0.8):
        """A joint from p0 to p1, wandering — straight to the eye, not straight to a ruler.

        OVERSAMPLED 4x, and that is the difference between a joint and a dotted line. Stepping
        once per pixel of the longer axis leaves gaps as soon as the wobble displaces a sample,
        because two consecutive samples can then land two pixels apart diagonally. The field
        rendered as dashed joints and the enclosure measured 100% single region — the network
        looked right and leaked at every gap. A joint with holes in it encloses nothing, which is
        session one's finding reappearing through the drawing rather than through the tiling.
        """
        (x0, y0), (x1, y1) = p0, p1
        span = max(abs(x1 - x0), abs(y1 - y0)) + 1
        steps = span * 4
        for i in range(steps + 1):
            t = i / steps
            jitter = (1 - abs(2 * t - 1))
            x = x0 + (x1 - x0) * t + rng.normal(0, wobble) * jitter
            y = y0 + (y1 - y0) * t + rng.normal(0, wobble) * jitter
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= xi < T and 0 <= yi < T):
                continue
            joints[yi, xi] = True
            # Two pixels wide: a mortar joint has constant width where a crack tapers. Widened
            # INWARD at the east edge rather than wrapping — `(xi+1) % T` put the second pixel on
            # the opposite side of the tile, drawing a stray joint on the west boundary.
            joints[yi, xi + 1 if xi + 1 < T else xi - 1] = True

    # North and south crossings meet the middle; west and east likewise. The four arms divide the
    # cell into four regions and every arm ends ON a boundary its neighbour also crosses.
    draw((CROSS[n], 0), (mx, my))
    draw((CROSS[s], T - 1), (mx, my))
    draw((0, CROSS[w]), (mx, my))
    draw((T - 1, CROSS[e]), (mx, my))

    # Region label, so each stone can take its own value.
    lab = np.full((T, T), -1, dtype=int)
    nxt = 0
    for sy in range(T):
        for sx in range(T):
            if joints[sy, sx] or lab[sy, sx] >= 0:
                continue
            stack, cur = [(sy, sx)], nxt
            lab[sy, sx] = cur
            nxt += 1
            while stack:
                yy, xx = stack.pop()
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx2 = yy + dy, xx + dx
                    if 0 <= ny < T and 0 <= nx2 < T and not joints[ny, nx2] and lab[ny, nx2] < 0:
                        lab[ny, nx2] = cur
                        stack.append((ny, nx2))

    # STONE-TO-STONE VALUE, BLENDED TO AN EDGE VALUE THE NEIGHBOUR ALSO COMPUTES.
    #
    # The first version gave each region an independent random offset, and that put a hard value
    # step through every stone that spans a cell boundary — the two halves are separate regions in
    # separate tiles and drew separate values. Measured across an assembled field: boundary steps
    # averaged 8.72 against 1.17 inside a tile, 7.4x, max 39.9. A blind seat found it before the
    # measurement did — "axis-aligned value blocks on an exact 64-pixel lattice ... the grid reads
    # before the floor does" — and it is §8.3.1 arriving through VALUE rather than through shape,
    # which is the same way session one's mean-spread defect arrived.
    #
    # Edge matching fixed WHERE the joints cross. It said nothing about what the stone either side
    # of the crossing is worth, and a stone is not one stone if its two halves are different
    # colours.
    #
    # The fix: every boundary carries a value derived from ITS OWN FAMILY — data both neighbours
    # already share — and each tile's material is blended toward that value as it approaches the
    # edge. At the seam itself the blend is complete, so both tiles compute the identical value
    # and the step is zero by construction. Away from the edges each region keeps its own offset,
    # so stone-to-stone variation survives where it is legible and vanishes only where it would
    # have drawn a lattice.
    edge_value = {f: (f - (FAMILIES - 1) / 2.0) * step * 0.55 for f in range(FAMILIES)}
    yy, xx = np.mgrid[0:T, 0:T]
    dN, dS, dW, dE = yy, (T - 1 - yy), xx, (T - 1 - xx)
    reach = 9                         # px over which a tile hands over to its boundary's value
    wN = np.clip(1.0 - dN / reach, 0, 1)
    wS = np.clip(1.0 - dS / reach, 0, 1)
    wW = np.clip(1.0 - dW / reach, 0, 1)
    wE = np.clip(1.0 - dE / reach, 0, 1)
    wsum = wN + wS + wW + wE
    edge_field = np.where(wsum > 0,
                          (wN * edge_value[n] + wS * edge_value[s]
                           + wW * edge_value[w] + wE * edge_value[e]) / np.maximum(wsum, 1e-6),
                          0.0)
    blend = np.clip(wsum, 0, 1)       # 1 at the edges, 0 in the tile's interior

    region = np.zeros((T, T), dtype=float)
    for cid in range(nxt):
        region[lab == cid] = rng.normal(0, step * (0.30 if worn else 0.50))
    L += region * (1 - blend) + edge_field * blend

    amp = max(mat["grain_mad"], 1.0)
    # WORN: tighter grain. Traffic polishes tooth away — §8.1, "stone smoothed to a shine".
    L += CF.wrap_noise(T, 8, rng) * amp * (0.16 if worn else 0.34)
    L += CF.wrap_noise(T, 16, rng) * amp * (0.06 if worn else 0.14)

    # JOINTS. Worn cells keep them — a polished floor still has joints — but shallower, because
    # feet round the arrises off. §8.1's polish, delivered as depth rather than as brightness.
    L[joints] = stone * (0.80 if worn else 0.62) + rng.normal(0, 1.0, int(joints.sum()))

    # HOLD THE FAMILY'S VALUE. Applied to the whole tile, and the alternative was MEASURED rather
    # than reasoned about: normalising only the interior — to leave the edge band exactly as the
    # shared boundary value set it — made both numbers worse. Boundary steps 3.99 -> 4.93 and the
    # per-tile mean spread 8.40, past the 6.4 a seat culled in session one as "the grid draws
    # itself onto the ground". Two lattices are not better than one, so the whole-tile
    # normalisation stays and the residual boundary step is carried as a named limitation.
    L += (mat["lum_median"] - float(L.mean()))
    L = CF.quantise(L, mat["ladder"])
    return CF.colourise(L, mat["tint"]).astype(np.uint8), joints


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=ASSETS)
    a = ap.parse_args()

    src = json.load(open(os.path.join(CF.ASSETS, "MANIFEST.json")))
    mat = src["material"]
    os.makedirs(a.out, exist_ok=True)

    man = dict(family="boundary_floor_wang_v1", commit=FL.git_commit(), seed=a.seed,
               material=mat, families=FAMILIES, crossings=CROSS,
               salts=dict(horizontal=HORIZ, vertical=VERT),
               edge_family_check=cross_check_vector(a.seed),
               donors=src.get("donors", []), base=[], channel=[],
               law=("§8.3.1 clarified: matching is agreement, not constancy. >=3 edge families "
                    "per boundary orientation; crossing-position variance measured on the "
                    "assembled field."))

    print("EDGE-MATCHED FAMILY — %d families/orientation, %d combinations"
          % (FAMILIES, FAMILIES ** 4))
    print("  crossings: %s  (unequal on purpose — 8/16/24 would be an 8px lattice)" % CROSS)
    print("  material: median %.1f, ladder %s"
          % (mat["lum_median"], [round(v) for v in mat["ladder"]]))

    for worn, id0, key in ((False, BASE_ID0, "base"), (True, CHAN_ID0, "channel")):
        for n in range(FAMILIES):
            for e in range(FAMILIES):
                for s in range(FAMILIES):
                    for w in range(FAMILIES):
                        img, joints = build_tile(n, e, s, w, mat, a.seed, worn)
                        tid = id0 + tile_index(n, e, s, w)
                        p = os.path.join(a.out, "tier1_wang_%d.png" % tid)
                        Image.fromarray(img).save(p)
                        man[key].append(dict(id=tid, n=n, e=e, s=s, w=w,
                                             file=os.path.basename(p),
                                             sha256=FL.sha256_file(p),
                                             joint_px=int(joints.sum())))
        print("  %-8s %d tiles, ids %d-%d" % (key, len(man[key]), id0, id0 + FAMILIES ** 4 - 1))

    ids = [e["id"] for e in man["base"] + man["channel"]]
    if len(set(ids)) != len(ids):
        raise SystemExit("REFUSING: duplicate ids in the edge-matched family.")

    mp = os.path.join(a.out, "MANIFEST.json")
    with open(mp, "w") as f:
        json.dump(man, f, indent=1)
    print("\nid check: %d ids, all distinct, %d..%d" % (len(ids), min(ids), max(ids)))
    print("written: %s" % os.path.relpath(mp, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
