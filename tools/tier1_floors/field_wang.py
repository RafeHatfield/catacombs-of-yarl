#!/usr/bin/env python3
"""ASSEMBLE the edge-matched field and measure the two things the clarified law asks for.

    ENCLOSURE          session one's terminal finding: "joints enclose nothing — 99.1% of the
                       floor is one connected region. No stones, only scratches." The number to
                       beat is that 99.1%.

    CROSSING VARIANCE  the clarified law's second floor: "a field whose joint crossings cluster
                       at constant offsets has re-derived the lattice and fails." Three families
                       per orientation is necessary and not sufficient — the families have to be
                       USED, and used evenly.

Both are measured on the field as ASSEMBLED, not on a tile, because both are properties that do
not exist at tile scale (§8.3's scale rule, and the reason session one's per-tile screen could
pass a set whose joints did not meet).

It assembles with the same `edge_family` the engine will use, from the same manifest — so this is
not a second implementation of the layout with the renderer's name on it.
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
import compose_wang as CW      # noqa: E402
import field_laws as FL        # noqa: E402

T = CW.T


def assemble(w, h, seed, mat, worn=None):
    """Lay a w x h field of cells. `worn(x,y)` selects the channel rendering for that cell."""
    img = np.zeros((h * T, w * T, 3), dtype=np.uint8)
    joints = np.zeros((h * T, w * T), dtype=bool)
    fams = {"H": [], "V": []}
    for y in range(h):
        for x in range(w):
            n = CW.edge_family(x, y, CW.HORIZ, seed)
            s = CW.edge_family(x, y + 1, CW.HORIZ, seed)
            wf = CW.edge_family(x, y, CW.VERT, seed)
            e = CW.edge_family(x + 1, y, CW.VERT, seed)
            fams["H"].append(n)
            fams["V"].append(wf)
            tile, jm = CW.build_tile(n, e, s, wf, mat, seed,
                                     worn=bool(worn and worn(x, y)))
            img[y * T:(y + 1) * T, x * T:(x + 1) * T] = tile
            joints[y * T:(y + 1) * T, x * T:(x + 1) * T] = jm
    return img, joints, fams


def enclosure(joints):
    """Connected components of the NON-joint pixels — the stones.

    Reported as session one reported its failure, so the two numbers are comparable: the share of
    floor sitting in the single largest region. At 99.1% every stone leaks into every other and
    there are no stones; the lower it goes, the more of the floor is actually enclosed.
    """
    h, w = joints.shape
    lab = np.full((h, w), -1, dtype=int)
    sizes = []
    nxt = 0
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
                largest_px=sizes[0] if sizes else 0,
                largest_share=round(sizes[0] / total, 4) if total else 1.0,
                median_region=int(np.median(sizes)) if sizes else 0,
                regions_over_64px=sum(1 for s in sizes if s >= 64))


def crossing_variance(joints, w, h):
    """Where does the joint actually cross each cell boundary, and how spread are those offsets?

    Measured on the ASSEMBLED field rather than read off the family table, because the table says
    what was intended and the pixels say what happened. A set can declare three families and still
    draw them at one place.
    """
    xs, ys = [], []
    for cy in range(1, h):
        row = joints[cy * T, :]
        for cx in range(w):
            seg = np.where(row[cx * T:(cx + 1) * T])[0]
            if len(seg):
                ys.append(int(seg.mean()))
    for cx in range(1, w):
        col = joints[:, cx * T]
        for cy in range(h):
            seg = np.where(col[cy * T:(cy + 1) * T])[0]
            if len(seg):
                xs.append(int(seg.mean()))
    def stats(v):
        if not v:
            return dict(n=0)
        a = np.array(v)
        vals, counts = np.unique(a, return_counts=True)
        return dict(n=len(a), distinct=int(len(vals)), sd=round(float(a.std()), 2),
                    spread=int(a.max() - a.min()),
                    modal_share=round(float(counts.max()) / len(a), 3),
                    offsets=[int(x) for x in vals[:8]])
    return dict(horizontal_boundaries=stats(ys), vertical_boundaries=stats(xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--h", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    a = ap.parse_args()

    man = json.load(open(os.path.join(CW.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    os.makedirs(a.out, exist_ok=True)

    print("EDGE-MATCHED FIELD — %dx%d cells, seed %d\n" % (a.w, a.h, a.seed))
    rows = {}
    for label, worn in (("ordinary", None),
                        ("with_channel", lambda x, y: a.w // 2 - 1 <= x <= a.w // 2)):
        img, joints, fams = assemble(a.w, a.h, a.seed, mat, worn)
        p = os.path.join(a.out, "wang_%s.png" % label)
        Image.fromarray(img).save(p)
        enc = enclosure(joints)
        cv = crossing_variance(joints, a.w, a.h)
        lat = None
        try:
            import field_preview as FP
            lat = FP.lattice_score(img)
        except Exception:
            pass
        rows[label] = dict(file=os.path.relpath(p, REPO), enclosure=enc, crossings=cv,
                           lattice=lat)
        print("  %s" % label)
        print("     enclosure: %d regions, largest holds %.1f%% of floor "
              "(session one: 99.1%%), median region %dpx, %d regions >=64px"
              % (enc["regions"], 100 * enc["largest_share"], enc["median_region"],
                 enc["regions_over_64px"]))
        print("     crossings: horizontal n=%d distinct=%d sd=%.2f modal=%.3f | "
              "vertical n=%d distinct=%d sd=%.2f modal=%.3f"
              % (cv["horizontal_boundaries"]["n"], cv["horizontal_boundaries"]["distinct"],
                 cv["horizontal_boundaries"]["sd"], cv["horizontal_boundaries"]["modal_share"],
                 cv["vertical_boundaries"]["n"], cv["vertical_boundaries"]["distinct"],
                 cv["vertical_boundaries"]["sd"], cv["vertical_boundaries"]["modal_share"]))
        if lat:
            print("     lattice:   %.4f" % lat["lattice"])

    res = dict(commit=FL.git_commit(), grid=[a.w, a.h], seed=a.seed,
               families=man["families"], crossings=man["crossings"],
               session_one_largest_share=0.991, fields=rows)
    p = os.path.join(a.out, "WANG-FIELD.json")
    with open(p, "w") as f:
        json.dump(res, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
