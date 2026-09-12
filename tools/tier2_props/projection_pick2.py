#!/usr/bin/env python3
"""Pick one generation per cell of the 5 x 5 matrix — by geometry HOLD first, then by eye.

    python3 tools/tier2_props/projection_pick2.py            # order, sheet, write picks.json
    python3 tools/tier2_props/projection_pick2.py --stage     # copy the picks into place for landing

For every (candidate, archetype) the seeds are ordered by how faithfully the generation kept the
template's projection:

    hold   = IoU of the generation's silhouette with the template's (1.0 = the same outline)
    shear  = signed top-edge shear, compared with the template's (which side recedes, how much)

The best-hold seed is the pick unless picks.json carries a hand override, which is how the eye
gets its say: a generation can hold the outline perfectly and still not be a nameable object.
An override is recorded with a reason, and the sheet shows every seed so the override can be
checked. Nothing here rules anything — the projection is Rafe's to name on device.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import projection_round2 as pr    # noqa: E402

RAW = os.path.join(pr.GEN, "raw")
PICKS = os.path.join(pr.GEN, "picks.json")


def alpha(p):
    return np.asarray(Image.open(p).convert("RGBA"))[:, :, 3] > 0


def iou(a, b):
    return float((a & b).sum()) / float((a | b).sum() or 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    a = ap.parse_args()
    picks = json.load(open(PICKS)) if os.path.exists(PICKS) else {}
    rows = []
    print("%-6s %-7s %-6s %6s %8s %8s   %s" % ("cand", "arch", "seed", "hold", "shear", "t.shear", ""))
    for cand in pr.CANDIDATES:
        for name, w, h, _, _ in pr.ARCHETYPES:
            tpath = os.path.join(RAW, "init_%s_%s.png" % (cand, name))
            if not os.path.exists(tpath):
                continue
            t = alpha(tpath)
            tsh = pr.signed_shear(t)
            seeds = sorted(int(f.split("_s")[-1][:-4]) for f in os.listdir(RAW)
                           if f.startswith("%s_%s_s" % (cand, name)) and f.endswith(".png"))
            if not seeds:
                continue
            meas = []
            for s in seeds:
                g = alpha(os.path.join(RAW, "%s_%s_s%d.png" % (cand, name, s)))
                meas.append((s, iou(t, g), pr.signed_shear(g)))
            meas.sort(key=lambda m: -m[1])
            key = "%s_%s" % (cand, name)
            ov = picks.get(key, {}).get("override")
            chosen = ov if ov is not None else meas[0][0]
            for s, hold, sh in meas:
                mark = "<- pick" + (" (override: %s)" % picks[key]["reason"] if ov == s else "") \
                    if s == chosen else ""
                print("%-6s %-7s %-6d %6.3f %+8.3f %+8.3f   %s" % (cand, name, s, hold, sh, tsh, mark))
            picks[key] = dict(picks.get(key, {}), seed=chosen,
                              ordered=[dict(seed=s, hold=round(h_, 4), shear=round(sh, 4))
                                       for s, h_, sh in meas],
                              template_shear=round(tsh, 4))
            rows.append((cand, name, chosen, seeds))
    json.dump(picks, open(PICKS, "w"), indent=1)

    # the sheet: rows = candidates, columns = archetypes, each cell shows [template | seeds...]
    # with the pick boxed. 2x for the eye.
    cw, ch = 4 * 72 + 8, 2 * 72 + 8
    cols = len(pr.ARCHETYPES)
    sheet = Image.new("RGBA", (cols * (cw * 2), len(pr.CANDIDATES) * (ch * 2)), (24, 24, 28, 255))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for r, cand in enumerate(pr.CANDIDATES):
        for c, (name, _, _, _, _) in enumerate(pr.ARCHETYPES):
            key = "%s_%s" % (cand, name)
            if key not in picks:
                continue
            x0, y0 = c * cw * 2, r * ch * 2
            dr.text((x0 + 4, y0 + 2), "%s %s" % (cand, name), fill=(200, 200, 200, 255))
            items = [("T", os.path.join(RAW, "init_%s_%s.png" % (cand, name)))]
            items += [(str(o["seed"]), os.path.join(RAW, "%s_%s_s%d.png" % (cand, name, o["seed"])))
                      for o in picks[key]["ordered"]]
            for k, (lab, p) in enumerate(items):
                im = Image.open(p).convert("RGBA")
                big = im.resize((im.size[0] * 2, im.size[1] * 2), Image.NEAREST)
                px, py = x0 + 4 + k * (128 + 8), y0 + 16
                sheet.paste(big, (px, py), big)
                if lab != "T" and int(lab) == picks[key]["seed"]:
                    dr.rectangle([px - 2, py - 2, px + big.size[0] + 1, py + big.size[1] + 1],
                                 outline=(90, 220, 120, 255), width=2)
                dr.text((px, py + big.size[1] + 2), lab, fill=(160, 160, 160, 255))
    sheet.save(os.path.join(pr.GEN, "matrix_sheet.png"))
    print("\nsheet: %s" % os.path.relpath(os.path.join(pr.GEN, "matrix_sheet.png"), pr.REPO))

    if a.stage:
        for cand, name, seed, _ in rows:
            src = os.path.join(RAW, "%s_%s_s%d.png" % (cand, name, seed))
            dst = os.path.join(pr.GEN, "%s_%s.png" % (cand, name))
            shutil.copy(src, dst)
        print("staged %d picks into %s" % (len(rows), os.path.relpath(pr.GEN, pr.REPO)))


if __name__ == "__main__":
    main()
