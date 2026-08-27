#!/usr/bin/env python3
"""The unfiltered evidence sheet: every candidate the critic saw, labelled with its verdict.

Bible §13.1 — a contact sheet approves nothing. This exists so a reader can check the counts
in the report against the images that produced them, INCLUDING the ones that failed and
including the plants. A report that shows only survivors is asking to be believed rather than
checked.

Labels carry the critic's own machine-parsed outcome: the cull if it culled, otherwise the
four structural clauses as a four-letter code, so a claim of "N structural candidates" can be
counted off the sheet by eye.

  T = two planes    S = segment identity    K = no key light    O = no baked outline
  lower case = the clause failed
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Named rather than coded: a mixed-case four-letter code is unreadable at label size, and an
# evidence sheet whose labels cannot be read is not evidence.
CLAUSE = [("two_planes", "no top surface"), ("segment_identity", "no role"),
          ("no_key_light", "key light"), ("no_baked_outline", "outline")]


def label_for(r):
    if r.get("verdict") == "MISSING":
        return "NOT JUDGED"
    c = r.get("clauses") or {}
    cull = ((r.get("raw") or {}).get("cull") or "").strip().lower()
    if cull and cull not in ("none", "n/a", "-"):
        return "CULL " + cull[:18]
    if r.get("structural"):
        return "%s  STRUCTURAL" % r.get("verdict", "?")
    failed = [name for f, name in CLAUSE if not c.get(f)]
    return "%s: %s" % (r.get("verdict", "?"), ", ".join(failed) or "clauses held")


def build(label, out_png, zoom=3, cols=7):
    res = json.load(open(os.path.join(HERE, "critic", label, "result.json")))
    rows_ = res["results"]
    work = os.path.join(HERE, "critic", label)
    imgs = []
    for r in rows_:
        src = os.path.join(HERE, r["source"])
        imgs.append((r, Image.open(src).convert("RGBA")))
    tw = max(i.width for _, i in imgs) * zoom
    th = max(i.height for _, i in imgs) * zoom
    pad, cap = 8, 26
    n = len(imgs)
    nrows = (n + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (tw + pad) + pad,
                               nrows * (th + cap + pad) + pad + 30), (20, 20, 24, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((pad, 8), "%s — all %d files the blind critic saw, unfiltered "
                      "(plants included). Sheets approve nothing (bible §13.1)."
            % (label, n), fill=(230, 230, 235, 255))
    for k, (r, im) in enumerate(imgs):
        row, col = divmod(k, cols)
        x = pad + col * (tw + pad)
        y = 30 + pad + row * (th + cap + pad)
        big = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        sheet.alpha_composite(big, (x, y))
        is_plant = r["kind"] == "plant"
        dr.text((x, y + th + 2),
                ("PLANT " if is_plant else "") + r["label"][:22],
                fill=(255, 170, 90, 255) if is_plant else (190, 190, 195, 255))
        dr.text((x, y + th + 13), label_for(r)[:34],
                fill=(120, 220, 140, 255) if r.get("structural")
                else (210, 130, 130, 255))
    sheet.save(out_png)
    print("%s  %d files  %s" % (out_png, n, sheet.size))
    return out_png


def main():
    for label in sys.argv[1:] or ["kitA0"]:
        build(label, os.path.join(HERE, "critic", label, "sheet_%s.png" % label))


if __name__ == "__main__":
    main()
