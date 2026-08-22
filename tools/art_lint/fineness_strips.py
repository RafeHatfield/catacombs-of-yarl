#!/usr/bin/env python3
"""Review strips for the fineness rubric session (Part B.3).

For every generated asset above WARN on any fineness metric (from fineness_sweep.csv, worst-first),
build a strip: the sprite at 6x seated between two canon neighbours of the same sheet-class, with
full labels (no clipping). Canon neighbours are drawn from a median-fineness canon pool per class —
representative of the canonical register, so the "is the generated one the outsider?" read is fair.
Batched ~10 strips per composite, ranked worst-first.

Verdicts are Rafe's (keep / rework). This tool ranks and presents; it does not pre-judge.
"""
import csv
import os
import re

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
OUT = "tools/art_lint/reports/fineness_strips"
SWEEP = "tools/art_lint/reports/fineness_sweep.csv"
BASELINE = "tools/art_lint/fineness_canon_baseline.csv"
PER_COMPOSITE = 10
SCALE = 6


# Curated clean-register canon PROPS for the world class — actual objects, not the many simple
# floor/wall tiles a median pick would return, so the "same hand?" read is against comparable
# canon objects. (Furniture cluster 317-324 + barrel 268, all confirmed chunky-register.)
WORLD_PROP_ANCHORS = [268, 317, 319, 321, 322, 323, 324]
WDIR = "src/Presentation/assets/sprites_16bf/world_24x24"


def canon_anchor_pool(cls, n=10):
    if cls == "world_24x24":
        return [f"{WDIR}/oryx_16bit_fantasy_world_{i}.png" for i in WORLD_PROP_ANCHORS]
    # items / creatures: median-fineness canon of the class are real objects — representative register.
    rows = [r for r in csv.DictReader(open(BASELINE)) if r["class"] == cls]
    rows.sort(key=lambda r: int(r["color_regions"]))
    mid = len(rows) // 2
    picks = rows[max(0, mid - n // 2): mid + (n - n // 2)]
    return [r["file"] for r in picks]


def load6(path):
    im = Image.open(path).convert("RGBA")
    big = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    base = Image.new("RGBA", big.size, (0, 0, 0, 0))
    px = base.load()
    for y in range(big.height):
        for x in range(big.width):
            px[x, y] = (74, 70, 64, 255) if (x // 8 + y // 8) % 2 else (52, 49, 45, 255)
    base.alpha_composite(big)
    return base


def _wrap(text, max_px):
    def tw(s):
        try:
            return FONT.getlength(s)
        except AttributeError:
            return FONT.getsize(s)[0]
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if tw(t) <= max_px or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def strip(gen_path, gen_label, canon_l, canon_r):
    imgs = [("canon " + re.search(r"_(\d+)\.png", canon_l).group(1), load6(canon_l)),
            ("GENERATED", load6(gen_path)),
            ("canon " + re.search(r"_(\d+)\.png", canon_r).group(1), load6(canon_r))]
    pad, gap, line_h = 10, 10, 16
    cw = max(c[1].width for c in imgs)
    ch = max(c[1].height for c in imgs)
    w = len(imgs) * (cw + gap) + pad
    # Full-width wrapped ranking label on top — never clipped.
    lbl_lines = _wrap(gen_label, w - pad * 2)
    hdr_h = len(lbl_lines) * line_h + 6
    cell_lbl_h = 16
    h = hdr_h + cell_lbl_h + ch + pad
    s = Image.new("RGBA", (w, h), (30, 28, 26, 255))
    d = ImageDraw.Draw(s)
    for i, ln in enumerate(lbl_lines):
        d.text((pad, 3 + i * line_h), ln, font=FONT, fill=(210, 150, 40, 255))
    x = pad
    for label, img in imgs:
        col = (210, 150, 40) if label == "GENERATED" else (140, 140, 140)
        d.text((x, hdr_h), label, font=FONT, fill=(*col, 255))
        s.alpha_composite(img, (x, hdr_h + cell_lbl_h))
        x += cw + gap
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    flagged = [r for r in csv.DictReader(open(SWEEP)) if r["fineness_verdict"] in ("WARN", "FAIL")]
    # already ranked worst-first in the CSV; keep that order
    pools = {c: canon_anchor_pool(c) for c in ("world_24x24", "items_16x16", "creatures_24x24")}

    batches = [flagged[i:i + PER_COMPOSITE] for i in range(0, len(flagged), PER_COMPOSITE)]
    for bi, batch in enumerate(batches, 1):
        strips = []
        for r in batch:
            pool = pools[r["class"]]
            k = int(r["rank"])
            cl, cr = pool[k % len(pool)], pool[(k + 3) % len(pool)]
            label = (f"#{r['rank']} id {r['id']} [{r['game_key']}] {r['fineness_verdict']} "
                     f"dev={r['deviation_score']} worst={r['worst_metric']}  "
                     f"spk{r['speckle']} sc{r['small_clusters']} cr{r['color_regions']} "
                     f"ed{r['edge_density']} ({r['conformance_status']})")
            strips.append(strip(r["path"], label, cl, cr))
        w = max(s.width for s in strips)
        gap = 8
        h = sum(s.height + gap for s in strips) + gap
        comp = Image.new("RGBA", (w, h), (18, 17, 16, 255))
        y = gap
        for s in strips:
            comp.alpha_composite(s, (0, y))
            y += s.height + gap
        comp.convert("RGB").save(f"{OUT}/fineness_strips_batch{bi:02d}_ranks{batch[0]['rank']}-{batch[-1]['rank']}.png")
        print(f"batch {bi}: ranks {batch[0]['rank']}-{batch[-1]['rank']} ({len(batch)} strips)")
    print(f"total flagged: {len(flagged)} across {len(batches)} composites -> {OUT}/")


if __name__ == "__main__":
    main()
