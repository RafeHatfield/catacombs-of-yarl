#!/usr/bin/env python3
"""Contact sheets for the Track A gate-remediation round (chairs, candelabra).

Chairs are shown composed NEXT TO table 5053 (they must read as a set with it), each with its
full seed label and at gameplay-ish scale. Candelabra are shown beside the live rejected sprite.
Only candidates that survive the 1x-identifiability filter are included (candelabra); the filter
and any removals are recorded in the PR comment, not silently applied.
"""
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
WORLD = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/remediation_review"
os.makedirs(OUT, exist_ok=True)
BG = (56, 50, 44, 255)


def load(p):
    return Image.open(p).convert("RGBA")


def seed_of(p):
    return int(re.search(r"_s(\d+)_", p).group(1))


def checker(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    px = im.load()
    for y in range(size[1]):
        for x in range(size[0]):
            px[x, y] = (70, 66, 60, 255) if (x // 8 + y // 8) % 2 else (48, 45, 41, 255)
    return im


def tile(im, scale, cbg=True):
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if cbg:
        base = checker(big.size)
        base.alpha_composite(big)
        return base
    return big


def build_chairs():
    table = load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png")
    rejected = [("rejected 5051", load(f"{WORLD}/oryx_16bit_fantasy_world_5051.png"))]
    cands = sorted(glob.glob("tools/art_lint/candidates/burndown3/chair_remediation/chair_remediation_locked_s*_snapped.png"), key=seed_of)

    # Each row: [table 5053] [chair] at 6x, so the "set" reads; label carries full seed.
    rows = []
    # reference row: table + the rejected chair
    rows.append(("reference — table 5053 + gate-rejected chair 5051", table, rejected[0][1], rejected[0][0]))
    for p in cands:
        rows.append((f"table 5053 + chair_remediation seed {seed_of(p)}", table, load(p), f"seed {seed_of(p)}"))

    scale = 6
    pad = 12
    rowh = 24 * scale + 26
    gap = 18
    w = 24 * scale * 2 + gap + pad * 2 + 40
    h = len(rows) * (rowh + pad) + pad
    sheet = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(sheet)
    y = pad
    for title, left, right, rlabel in rows:
        d.text((pad, y), title, font=FONT, fill=(255, 255, 255, 255))
        yy = y + 20
        sheet.alpha_composite(tile(left, scale), (pad, yy))
        sheet.alpha_composite(tile(right, scale), (pad + 24 * scale + gap, yy))
        y += rowh + pad
    sheet.convert("RGB").save(f"{OUT}/chairs_next_to_table_5053.png")
    print(f"chairs sheet: {len(cands)} candidates, composed next to table 5053")


def build_candelabra(keep_seeds):
    live = load(f"{WORLD}/oryx_16bit_fantasy_world_5080.png")
    cands = [p for p in sorted(glob.glob("tools/art_lint/candidates/burndown3/candelabra_remediation/candelabra_remediation_locked_s*_snapped.png"), key=seed_of)
             if seed_of(p) in keep_seeds]
    items = [("LIVE rejected 5080", live)] + [(f"seed {seed_of(p)}", load(p)) for p in cands]
    big_scale, small_scale = 8, 2
    pad = 14
    colw = 24 * big_scale + pad
    w = len(items) * colw + pad
    h = 24 * big_scale + 24 * small_scale + 52
    sheet = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(sheet)
    x = pad
    for name, im in items:
        d.text((x, 4), name, font=FONT, fill=(255, 255, 255, 255))
        sheet.alpha_composite(tile(im, big_scale), (x, 22))
        d.text((x, 22 + 24 * big_scale + 4), "1x-ish:", font=FONT, fill=(200, 200, 200, 255))
        sheet.alpha_composite(tile(im, small_scale, cbg=False), (x, 22 + 24 * big_scale + 20))
        x += colw
    sheet.convert("RGB").save(f"{OUT}/candelabra_candidates.png")
    print(f"candelabra sheet: {len(cands)} candidates (kept {sorted(keep_seeds)})")


if __name__ == "__main__":
    build_chairs()
    # 1x-identifiability filter: seed 3 rejected (reads as a single candle/torch, not a candelabra).
    build_candelabra(keep_seeds={0, 1, 2, 4, 5})
