#!/usr/bin/env python3
"""WHAT THE LAMP REACHES — the cast-shadows instrument (§12.1a, §3.2, §6.3).

    python3 tools/cast_shadows/measure_occlusion.py <capture.png> <capture.log> <scene.json> [--tag T]

Reads the delivered frame by CELL CLASS, so a shadow pass can be proved rather than eyeballed:

    floor           carved cells inside the lamp's radius — must not move
    face            wall cells with floor to the SOUTH: the lower half is the reveal (§3
                    FACE_TOP_ROW), the upper half the cap. The r29 failure was face 37.90 -> 5.51;
                    a correct occluder leaves the face where it was
    unexcavated     wall cells with no floor in their 8-neighbourhood — the mass the lamp must
                    NOT reach; falls toward ambient when the occluders are right
    prop base       a strip on the floor immediately south of each prop's bottom edge — the
                    contact shadow (§12.1 form), and #212's base question in numbers
    prop sprite     the props' own opaque pixels — must NOT move when occluders go on, because a
                    prop that self-shadows has failed §3.2's ½-depth side

Geometry is taken from the capture log's own legibility probes (px for known cells), never
re-derived (§13.10). Luminance is Rec.709 on 0..255.
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def geometry(log):
    """cell -> pixel mapping from two legibility probes; tile px from their spacing."""
    pts = []
    for line in open(log):
        m = re.search(r"legibility\((\d+),(\d+)\).*at px\((\d+),(\d+)\)", line)
        if m:
            pts.append(tuple(int(v) for v in m.groups()))
    if len(pts) < 2:
        raise SystemExit("no legibility probes in %s — cannot place the grid" % log)
    (x0, y0, px0, py0) = pts[0]
    tile = None
    for (x1, y1, px1, py1) in pts[1:]:
        if x1 != x0:
            tile = (px1 - px0) / (x1 - x0); break
        if y1 != y0:
            tile = (py1 - py0) / (y1 - y0); break
    tile = int(round(abs(tile)))
    ox = px0 - x0 * tile - tile // 2
    oy = py0 - y0 * tile - tile // 2
    return tile, ox, oy


def carved_set(spec):
    cells = set()
    for c in spec["carve"]:
        for y in range(c["y0"], c["y1"] + 1):
            for x in range(c["x0"], c["x1"] + 1):
                cells.add((x, y))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png"); ap.add_argument("log"); ap.add_argument("scene")
    ap.add_argument("--tag", default="")
    ap.add_argument("--radius", type=float, default=6.0)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    im = np.asarray(Image.open(a.png).convert("RGB")).astype(float)
    L = lum(im)
    H, W = L.shape
    tile, ox, oy = geometry(a.log)
    spec = json.load(open(a.scene))
    carved = carved_set(spec)
    px, py = spec["player"]["x"], spec["player"]["y"]
    props = spec.get("props", [])
    prop_cells = set()
    for p in props:
        for i in range(p.get("w", 1) * p.get("h", 1)):
            prop_cells.add((p["x"] + i % p.get("w", 1), p["y"] + i // p.get("w", 1)))

    def cell_box(x, y, top=0.0, bottom=1.0):
        X0 = ox + x * tile; Y0 = oy + y * tile
        y0 = int(Y0 + top * tile); y1 = int(Y0 + bottom * tile)
        x0 = X0 + tile // 4; x1 = X0 + 3 * tile // 4          # the central half, off the joints
        if y0 < 0 or x0 < 0 or y1 > H or x1 > W: return None
        return L[y0:y1, x0:x1]

    def near(x, y):
        return math.hypot(x - px, y - py) <= a.radius

    floor, face, cap, unex = [], [], [], []
    for y in range(spec["height"]):
        for x in range(spec["width"]):
            if not near(x, y): continue
            if (x, y) in carved:
                if (x, y) in prop_cells or (x, y) == (px, py): continue
                b = cell_box(x, y)
                if b is not None: floor.append(b.mean())
                continue
            south_open = (x, y + 1) in carved
            any_floor = any((x + dx, y + dy) in carved for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if south_open:
                bf = cell_box(x, y, 0.5, 1.0); bc = cell_box(x, y, 0.0, 0.5)
                if bf is not None: face.append(bf.mean())
                if bc is not None: cap.append(bc.mean())
            elif not any_floor:
                b = cell_box(x, y)
                if b is not None: unex.append(b.mean())

    # prop base contact + prop sprite
    bases, sprites = {}, {}
    for p in props:
        w, h = p.get("w", 1), p.get("h", 1)
        X0 = ox + p["x"] * tile; Y1 = oy + (p["y"] + h) * tile
        strip = L[Y1:Y1 + max(4, tile // 8), X0:X0 + w * tile]        # just south of the base
        bases[p["tileId"]] = float(strip.mean()) if strip.size else float("nan")
        body = L[oy + p["y"] * tile: Y1, X0:X0 + w * tile]
        # OPAQUE PIXELS ONLY, from the tiles' own alpha, so a shadow on the floor around a sprite
        # cannot be mistaken for a shadow ON it — the no-self-shadow claim is about the sprite.
        ids = p.get("layout") or [p["tileId"]]
        mask = np.zeros((h * tile, w * tile), bool)
        for i, tid in enumerate(ids):
            tp = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar/tier1_ashlar_%d.png" % tid)
            if not os.path.exists(tp): continue
            ta = np.asarray(Image.open(tp).convert("RGBA"))[:, :, 3] > 0
            k = tile // ta.shape[0]
            ta = np.kron(ta, np.ones((k, k), bool))
            cx, cy = (i % w) * tile, (i // w) * tile
            mask[cy:cy + tile, cx:cx + tile] = ta[:tile, :tile]
        if body.shape == mask.shape and mask.any():
            sprites[p["tileId"]] = float(body[mask].mean())
        else:
            sprites[p["tileId"]] = float(body.mean()) if body.size else float("nan")

    def m(v): return float(np.mean(v)) if v else float("nan")
    out = dict(tag=a.tag, png=os.path.relpath(a.png, REPO), tile=tile,
               floor=m(floor), face=m(face), cap=m(cap), unexcavated=m(unex),
               deep_over_face=(m(unex) / m(face)) if face and unex else float("nan"),
               n=dict(floor=len(floor), face=len(face), cap=len(cap), unexcavated=len(unex)),
               prop_base=bases, prop_sprite=sprites)
    print("%-10s floor %6.2f   face %6.2f   cap %6.2f   unexcavated %6.2f   deep/face %5.3f   "
          "(n floor %d face %d unex %d)" % (a.tag, out["floor"], out["face"], out["cap"],
                                          out["unexcavated"], out["deep_over_face"],
                                          len(floor), len(face), len(unex)))
    print("           prop base strip: " + "  ".join("%d=%.2f" % (k, v) for k, v in bases.items()))
    print("           prop sprite:     " + "  ".join("%d=%.2f" % (k, v) for k, v in sprites.items()))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
