#!/usr/bin/env python3
"""Derive a bottle-shelf on canon 318's shelf frame (register-correction, rank 9/36).

shelf_bottles concept survives via derivation: keep canon 318's chunky 2-cavity shelf frame,
mount a row of simple bottles in each cavity. Bottle colours are taken from the live shelf_bottles
sprite's own dominant non-wood colours (canon-validated-swatch rule), so they stay master-palette
and read as the same bottles. No canon pixels are sent to any generator.
"""
import os
import sys
from collections import Counter

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
import art_lint

W = "src/Presentation/assets/sprites_16bf/world_24x24"
OUTLINE = (38, 38, 38)


def bottle_colours(live_path):
    """Dominant non-wood, non-dark colours from the live shelf_bottles = the bottle glass ramp."""
    im = Image.open(live_path).convert("RGBA")
    c = Counter(p[:3] for p in im.getdata() if p[3] == 255)
    picks = []
    for col, _ in c.most_common():
        r, g, b = col
        # skip wood (r>g>b warm) and near-black outline; keep the glassy blues/greys
        if max(col) < 60:
            continue
        if r >= g >= b and r - b > 30:  # warm wood
            continue
        picks.append(col)
        if len(picks) >= 2:
            break
    if len(picks) < 2:
        picks = [(60, 178, 199), (201, 201, 201)]
    return picks[0], picks[1]  # body, highlight


def derive(live_path, out_path, seed_shift=0):
    im = Image.open(f"{W}/oryx_16bit_fantasy_world_318.png").convert("RGBA")
    px = im.load()
    body, hi = bottle_colours(live_path)

    def put(x, y, col):
        if 0 <= x < 24 and 0 <= y < 24:
            px[x, y] = (*col, 255)

    # Two cavities: top rows 5-10, bottom rows 14-19; interior cols 3..20.
    for base_y in (10, 19):  # bottle sits on the shelf floor at these rows
        xs = [4, 8, 12, 16, 20] if seed_shift == 0 else [5, 9, 13, 17]
        for x in xs:
            # body (2 wide, 3 tall), neck (1), outline sides
            put(x - 1, base_y - 3, OUTLINE); put(x, base_y - 3, hi); put(x + 1, base_y - 3, OUTLINE)  # neck+cap
            for dy in (2, 1, 0):
                put(x - 1, base_y - dy, OUTLINE)
                put(x, base_y - dy, body)
                put(x + 1, base_y - dy, hi if dy == 1 else body)
                put(x + 2, base_y - dy, OUTLINE)

    im.save(out_path)
    ps = art_lint.load_palette("config/art/oryx_master_palette.json")
    l = art_lint.lint_file(out_path, "prop", ps)
    print(f"{os.path.basename(out_path)}: lint {l['overall']} A1={l['A1']}(off={l['A1_off_palette_colors']}) "
          f"A4={l['A4_color_count']}/{l['A4']} A5={l['A5']} A6={l['A6']} | body={body} hi={hi}")


if __name__ == "__main__":
    out = "tools/art_lint/candidates/burndown3/bottle_shelf_derived"
    os.makedirs(out, exist_ok=True)
    derive(f"{W}/oryx_16bit_fantasy_world_5099.png", f"{out}/bottle_shelf_5099_derived.png", 0)
    derive(f"{W}/oryx_16bit_fantasy_world_5101.png", f"{out}/bottle_shelf_5101_derived.png", 1)
