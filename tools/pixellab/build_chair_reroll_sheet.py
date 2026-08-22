#!/usr/bin/env python3
"""ONE combined chair re-roll sheet for the gate (Route A + Route B), composed next to table 5053.

Route A (transform): the three incumbent chairs (5051/5056/5057) recoloured to table 5053's palette
via snap_to_palette — front-facing orientation preserved (the gate said the incumbents had this
right; only colour/weight failed).
Route B (regenerate): fresh BitForge v1 candidates generated with a front-facing / straight-on
prompt constraint, palette-locked to table 5053. Non-front-facing candidates are discarded before
the sheet (see DISCARD list).

Each candidate is shown NEXT TO table 5053 so the set read is judgeable, with full labels.
"""
import glob
import os
import re

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
WORLD = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/remediation_review"
os.makedirs(OUT, exist_ok=True)

# Route B seeds discarded for not being front-facing (three-quarter/side view).
ROUTE_B_DISCARD = {1}


def load(p):
    return Image.open(p).convert("RGBA")


def checker(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    px = im.load()
    for y in range(size[1]):
        for x in range(size[0]):
            px[x, y] = (70, 66, 60, 255) if (x // 8 + y // 8) % 2 else (48, 45, 41, 255)
    return im


def tile(im, scale):
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    base = checker(big.size)
    base.alpha_composite(big)
    return base


def rows_for():
    rows = [("REFERENCE — table 5053 + the gate-rejected incumbent 5051 (front-facing, wrong colour)",
             load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
             load(f"{WORLD}/oryx_16bit_fantasy_world_5051.png"))]
    # Route A — recoloured incumbents
    for fid in (5051, 5056, 5057):
        rows.append((f"ROUTE A (recolour incumbent {fid} -> table 5053 palette; orientation preserved)",
                     load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
                     load(f"tools/art_lint/candidates/burndown3/chair_route_a/chair_{fid}_route_a.png")))
    # Route B — fresh front-facing, discard non-front-facing
    b = sorted(glob.glob("tools/art_lint/candidates/burndown3/chair_route_b/chair_route_b_locked_s*_snapped.png"),
               key=lambda p: int(re.search(r"_s(\d+)_", p).group(1)))
    for p in b:
        s = int(re.search(r"_s(\d+)_", p).group(1))
        if s in ROUTE_B_DISCARD:
            continue
        rows.append((f"ROUTE B (regenerate, front-facing prompt, palette-locked; seed {s})",
                     load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"), load(p)))
    return rows


def build():
    rows = rows_for()
    scale, pad, gap = 6, 12, 18
    rowh = 24 * scale + 24
    w = 24 * scale * 2 + gap + pad * 2
    h = len(rows) * (rowh + pad) + pad
    sheet = Image.new("RGBA", (w, h), (56, 50, 44, 255))
    d = ImageDraw.Draw(sheet)
    y = pad
    for title, left, right in rows:
        d.text((pad, y), title, font=FONT, fill=(255, 255, 255, 255))
        yy = y + 20
        sheet.alpha_composite(tile(left, scale), (pad, yy))
        sheet.alpha_composite(tile(right, scale), (pad + 24 * scale + gap, yy))
        y += rowh + pad
    sheet.convert("RGB").save(f"{OUT}/chairs_reroll_next_to_table_5053.png")
    print(f"combined chair re-roll sheet: {len(rows)} rows "
          f"(1 reference + 3 Route A + {len(rows) - 4} Route B), discarded Route B seeds {sorted(ROUTE_B_DISCARD)}")


if __name__ == "__main__":
    build()
