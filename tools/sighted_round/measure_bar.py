#!/usr/bin/env python3
"""THE SIGHTED ROUND — STEP 1. Measure the asset bar's wall construction.

MEASUREMENTS LEAVE. PIXELS NEVER DO.
------------------------------------
Bible §13.3's origination rule and §1.3: *nothing conditions generation that we do not own.*
This module reads a licensed local copy of the asset bar, emits **numbers**, and writes nothing
but numbers. No source pixel is copied into the repo, into a composite, into a reference, or
into the corpus. The only outputs are `bar_measurements.json` and the table this prints.

Every wall round on this project so far has been blind: builder, critic and seats deriving a
top-down wall grammar from first principles with no one ever shown a correct answer. This is the
first round with sight, and what it is allowed to take away is a recipe of numbers and rules -
never an image.

THE SOURCE IS OUTSIDE THE REPO AND MUST BE DECLARED
---------------------------------------------------
`BAR_ROOT` points at a licensed library on this machine. If it is absent this module REFUSES
loudly rather than emitting an empty table - LOOP-PROCESS §4.2: a step that silently does
nothing is a wish. A run that measures zero sources is an error, not a result.

WHAT IS MEASURED, AND WHY EACH ONE
-----------------------------------
The brief names five, and one more turned up while measuring and is reported because it is
load-bearing:

  1. wall-face height on south reveals, in tile fractions
  2. top-band thickness as rooms wrap
  3. top-band vs floor value separation, in ramp steps
  4. occlusion-seam width and darkness at plane boundaries
  5. how corners and reveals terminate - the cap/course treatment at the top-to-face turn
  6. FOUND WHILE MEASURING: the occlusion is not in the wall sprite at all. It is a separate
     tile on the FLOOR cell south of the wall, on its own map layer, with a stepped alpha ramp.
     Named here because it changes what "authored occlusion" has to mean in the rebuild.

HOW THE BAR'S MAPS ARE READ
---------------------------
The example rooms ship as Tiled `.tmx` alongside their PNGs, so the structure is read from the
map data rather than guessed from pixels: layer names, per-cell tile ids, and therefore exactly
which cells are wall-top, which are wall-face, and where the shadow layer puts its tiles. Tile
appearance is then measured from the tileset by id. This is why the numbers below are exact
rather than estimated off a screenshot.
"""
import argparse
import base64
import collections
import json
import os
import re
import struct
import sys
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BAR_ROOT = "/Users/rafehatfield/development/assets/oryx/oryx_ultimate_fantasy_1.2"
EXAMPLES = os.path.join(BAR_ROOT, "uf_examples")
TILESET = os.path.join(BAR_ROOT, "uf_terrain.png")
OUT = os.path.join(HERE, "bar_measurements.json")

FACE_RATIO_MAX = 0.70     # a tile whose lower half is below this fraction of its upper half is
                          # classified a FACE tile. Classification only; nothing is adopted from it.


def lum(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def require_source():
    missing = [p for p in (BAR_ROOT, EXAMPLES, TILESET) if not os.path.exists(p)]
    if missing:
        print("REFUSING: the asset bar is not on this machine.", file=sys.stderr)
        for m in missing:
            print("  missing: %s" % m, file=sys.stderr)
        print("\nThis module measures a licensed local library. It does not ship with the repo\n"
              "and nothing here reconstructs it. Emitting an empty measurement table would be a\n"
              "silent no-op (LOOP-PROCESS §4.2), so this is an error.", file=sys.stderr)
        return False
    return True


def load_tmx(path):
    """Layer name -> 2D grid of gids, plus the map's own tileset table.

    A map cites several tilesets, each with its own `firstgid`, so a gid only means something
    against that table. Resolving a gid on the wrong sheet is how the first run of this file
    crashed, and it would have silently mis-measured rather than crashed if the index had
    happened to land in range.
    """
    s = open(path).read()
    m = re.search(r'<map[^>]*width="(\d+)" height="(\d+)" tilewidth="(\d+)" tileheight="(\d+)"', s)
    w, h, tw, th = (int(m.group(i)) for i in (1, 2, 3, 4))
    sets = []
    for tm in re.finditer(r'<tileset firstgid="(\d+)" name="([^"]+)"[^>]*tilecount="(\d+)"[^>]*>'
                          r'\s*<image source="([^"]+)"', s):
        sets.append(dict(firstgid=int(tm.group(1)), name=tm.group(2),
                         count=int(tm.group(3)),
                         image=os.path.normpath(os.path.join(os.path.dirname(path), tm.group(4)))))
    layers = {}
    for lm in re.finditer(r'<layer name="([^"]+)"[^>]*>.*?<data encoding="base64"'
                          r'(?: compression="(\w+)")?>(.*?)</data>', s, re.S):
        name, comp, payload = lm.group(1), lm.group(2), lm.group(3).strip()
        raw = base64.b64decode(payload)
        if comp == "zlib":
            raw = zlib.decompress(raw)
        elif comp == "gzip":
            raw = zlib.decompress(raw, 16 + zlib.MAX_WBITS)
        g = struct.unpack("<%dI" % (len(raw) // 4), raw)
        layers[name] = [list(g[y * w:(y + 1) * w]) for y in range(h)]
    return dict(width=w, height=h, tilew=tw, tileh=th, layers=layers, tilesets=sets)


class Tiles(object):
    """Resolves a gid through the map's own tileset table, never by assuming one sheet."""

    def __init__(self, tilesets):
        self.T = 48
        self.sets = sorted(tilesets, key=lambda s: -s["firstgid"])
        self.cache = {}

    def _img(self, path):
        if path not in self.cache:
            self.cache[path] = np.array(Image.open(path).convert("RGBA")).astype(float)
        return self.cache[path]

    def get(self, gid):
        for s in self.sets:
            if gid >= s["firstgid"]:
                img = self._img(s["image"])
                i = gid - s["firstgid"]
                if i >= s["count"]:
                    return None
                cols = img.shape[1] // self.T
                r, c = i // cols, i % cols
                T = self.T
                return img[r * T:(r + 1) * T, c * T:(c + 1) * T]
        return None


def classify(ts, gid):
    """TOP / FACE / other, plus the row where the plane turns."""
    t = ts.get(gid)
    if t is None or t.size == 0:
        return None
    A, L = t[..., 3], lum(t)
    if (A > 128).sum() < 200:
        return None
    T = ts.T
    upper = L[1:T // 2][A[1:T // 2] > 128]
    lower = L[T // 2:][A[T // 2:] > 128]
    if not len(upper) or not len(lower):
        return None
    um, lm = float(upper.mean()), float(lower.mean())
    return dict(gid=gid, upper=um, lower=lm, ratio=lm / um,
                kind="FACE" if lm < um * FACE_RATIO_MAX else "TOP")


def face_geometry(ts, gid):
    """Where the top band ends, where the face begins, and what sits at the turn."""
    t = ts.get(gid)
    if t is None or t.size == 0:
        return None
    L, A = lum(t), t[..., 3]
    T = ts.T
    rows = [float(L[y][A[y] > 128].mean()) if (A[y] > 128).any() else None for y in range(T)]
    body = [r for r in rows if r is not None]
    if not body:
        return None
    hi = float(np.median([r for r in body if r > np.median(body)]))
    lo = float(np.median([r for r in body if r <= np.median(body)]))
    mid = (hi + lo) / 2.0
    # first row from the bottom that is still dark == the face; walk up to the turn
    turn = None
    for y in range(T - 1, 0, -1):
        if rows[y] is not None and rows[y] > mid:
            turn = y
            break
    face_rows = T - 1 - turn if turn is not None else 0
    cap = rows[turn] if turn is not None else None
    return dict(gid=gid, turn_row=turn, face_px=face_rows, face_fraction=face_rows / float(T),
                top_px=turn, top_fraction=turn / float(T),
                cap_row_lum=cap, top_band_lum=hi, face_lum=lo, cap_over_top=(cap / hi) if cap else None)


def shadow_ramp(ts, gid):
    t = ts.get(gid)
    if t is None or t.size == 0:
        return None
    A = t[..., 3]
    rgb = t[..., :3][A > 0]
    steps = []
    prev, run = None, 0
    for y in range(ts.T):
        a = float(np.median(A[y]))
        if prev is None or a == prev:
            run += 1
        else:
            steps.append(dict(alpha=prev, rows=run))
            run = 1
        prev = a
    steps.append(dict(alpha=prev, rows=run))
    steps = [s for s in steps if s["alpha"] > 0]
    return dict(gid=gid, steps=steps,
                extent_px=sum(s["rows"] for s in steps),
                extent_fraction=sum(s["rows"] for s in steps) / float(ts.T),
                colour=sorted(set(map(tuple, rgb.astype(int).reshape(-1, 3).tolist())))[:3],
                max_alpha=max(s["alpha"] for s in steps) if steps else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=OUT)
    args = ap.parse_args()
    if not require_source():
        return 2

    maps = sorted(f for f in os.listdir(EXAMPLES) if f.endswith(".tmx"))
    print("THE SIGHTED ROUND - STEP 1: MEASURE THE BAR")
    print("source:  %s  (licensed, outside the repo)" % BAR_ROOT)
    print("outputs: numbers only. No source pixel enters the repo.")
    print("maps:    %d\n" % len(maps))

    wall_gids, shadow_gids, floor_gids = collections.Counter(), collections.Counter(), collections.Counter()
    per_map, tilesets, skipped = [], {}, []
    for fn in maps:
        m = load_tmx(os.path.join(EXAMPLES, fn))
        lay = m["layers"]
        if not lay.get("walls"):
            # the overworld map: no walls layer, so it cannot answer a wall question. Named,
            # never silently dropped.
            skipped.append(fn)
            continue
        for s_ in m["tilesets"]:
            tilesets[s_["firstgid"]] = s_
        w = collections.Counter(v for r in lay.get("walls", []) for v in r if v)
        s = collections.Counter(v for r in lay.get("shadows", []) for v in r if v)
        f = collections.Counter(v for r in lay.get("floor", []) for v in r if v)
        wall_gids += w
        shadow_gids += s
        floor_gids += f
        per_map.append(dict(map=fn, layers=sorted(lay), wall_cells=sum(w.values()),
                            shadow_cells=sum(s.values()), floor_cells=sum(f.values())))
        print("  %-24s layers=%-58s walls=%3d shadow=%3d floor=%3d"
              % (fn, ",".join(sorted(lay)), sum(w.values()), sum(s.values()), sum(f.values())))

    if skipped:
        print("\n  SKIPPED (no walls layer - cannot answer a wall question): %s" % ", ".join(skipped))
    ts = Tiles(list(tilesets.values()))

    cls = [c for c in (classify(ts, g) for g in sorted(wall_gids)) if c]
    faces = [c for c in cls if c["kind"] == "FACE"]
    tops = [c for c in cls if c["kind"] == "TOP"]
    floors = [(g, float(np.median(lum(ts.get(g))))) for g in sorted(floor_gids)
              if ts.get(g) is not None and ts.get(g).size]
    geo = [g for g in (face_geometry(ts, c["gid"]) for c in faces) if g]
    shad = [s for s in (shadow_ramp(ts, g) for g in sorted(shadow_gids)) if s]

    top_lum = float(np.mean([c["upper"] for c in cls]))
    face_lum = float(np.mean([c["lower"] for c in faces])) if faces else None
    floor_lum = float(np.mean([v for _, v in floors])) if floors else None

    print("\n-- WALL TILE CLASSES (from the maps' own wall layer) --")
    print("  %-6s %8s %8s %8s  %s" % ("gid", "top", "lower", "ratio", "class"))
    for c in cls:
        print("  %-6d %8.1f %8.1f %8.3f  %s" % (c["gid"], c["upper"], c["lower"], c["ratio"], c["kind"]))

    print("\n-- FACE GEOMETRY --")
    print("  %-6s %8s %10s %8s %10s %10s" % ("gid", "turn@y", "face px", "of tile", "cap lum", "cap/top"))
    for g in geo:
        print("  %-6d %8d %10d %8.3f %10.1f %10.3f"
              % (g["gid"], g["turn_row"], g["face_px"], g["face_fraction"], g["cap_row_lum"],
                 g["cap_over_top"]))

    print("\n-- OCCLUSION (separate layer, on the FLOOR cell south of the wall) --")
    for s in shad:
        print("  gid %-5d colour=%s  ramp=%s  extent=%dpx (%.3f tile)"
              % (s["gid"], s["colour"][:2], " -> ".join("a%d x%d" % (x["alpha"], x["rows"]) for x in s["steps"]),
                 s["extent_px"], s["extent_fraction"]))

    print("\n-- VALUE STACK, FLOOR-RELATIVE (the headline) --")
    print("  wall TOP  %6.1f   = %.2f x floor" % (top_lum, top_lum / floor_lum))
    print("  floor     %6.1f   = 1.00 x floor" % floor_lum)
    print("  wall FACE %6.1f   = %.2f x floor" % (face_lum, face_lum / floor_lum))
    print("  face/top ratio          %.3f" % (face_lum / top_lum))

    out = dict(source=BAR_ROOT, maps=per_map,
               wall_classes=cls, face_geometry=geo, shadow=shad,
               floors=[dict(gid=g, median_lum=v) for g, v in floors],
               value_stack=dict(wall_top=top_lum, floor=floor_lum, wall_face=face_lum,
                                top_over_floor=top_lum / floor_lum,
                                face_over_floor=face_lum / floor_lum,
                                face_over_top=face_lum / top_lum))
    with open(args.json, "w") as f:
        json.dump(out, f, indent=1)
    print("\n-> %s   (numbers only)" % os.path.relpath(args.json, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
