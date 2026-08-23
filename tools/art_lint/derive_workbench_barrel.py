#!/usr/bin/env python3
"""Derive workbench (from canon table 319) and water barrels (from canon barrel 268), Round-C verdicts.

Workbench: keep canon 319's table frame, add simple chunky tool clutter on the top (hammer + board +
bolts), colours from 319's wood ramp + a grey metal ramp (all master-palette). Armor-stand method.
Water barrel: keep canon 268's barrel, carve an open top and lay a visible blue water surface in it
(palette blues, worn-floor method). Applied to 5084/5085 as a variant pair — differ the water only.
No canon pixels sent to any generator.
"""
import os
import sys
from collections import Counter

from PIL import Image

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "tools/art_lint")
import art_lint

W = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/burndown3"
PS = art_lint.load_palette("config/art/oryx_master_palette.json")
A = (38, 38, 38)                    # outline
WOOD_D, WOOD = (87, 71, 0), (105, 63, 0)
MET_D, MET = (105, 105, 105), (145, 145, 145)


def lint(p, tag):
    l = art_lint.lint_file(p, "prop", PS)
    print(f"{tag}: {l['overall']} A1={l['A1']}(off={l['A1_off_palette_colors']}) "
          f"A4={l['A4_color_count']}/{l['A4']} A5={l['A5']} A6={l['A6']}")


def workbench():
    im = Image.open(f"{W}/oryx_16bit_fantasy_world_319.png").convert("RGBA")
    px = im.load()

    def put(x, y, col):
        if 0 <= x < 24 and 0 <= y < 24:
            px[x, y] = (*col, 255)

    # Hammer lying on the top-left of the table: dark iron head + wood handle.
    for x in range(4, 8):   # handle
        put(x, 6, A); put(x, 7, WOOD_D); put(x, 8, A)
    for y in range(4, 9):   # head block at the left end
        put(3, y, A); put(4, y, MET_D); put(5, y, MET); put(6, y, A) if y in (4, 8) else None
    put(3, 5, A); put(3, 6, A); put(3, 7, A)
    # A board/plank across the top-right.
    for x in range(13, 20):
        put(x, 5, A); put(x, 6, WOOD_D); put(x, 7, WOOD); put(x, 8, A)
    put(12, 6, A); put(12, 7, A); put(20, 6, A); put(20, 7, A)
    # Two bolts/nails (small dark clusters) mid-top.
    for cx in (9, 11):
        put(cx, 11, A); put(cx, 12, MET)

    out = f"{OUT}/workbench_derived/workbench_5082_derived.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out); lint(out, "workbench_5082 (319+tools)")


def water_barrel(fid, water, hi):
    im = Image.open(f"{W}/oryx_16bit_fantasy_world_268.png").convert("RGBA")
    px = im.load()

    def put(x, y, col):
        if 0 <= x < 24 and 0 <= y < 24:
            px[x, y] = (*col, 255)

    # Carve an open top filled with a blue water surface, framed by the barrel's own wood rim.
    # Water ellipse centred ~ (11.5, 5), cols 6..17, rows 2..8. Rim = wood ring one pixel outside.
    cx, cy = 11.5, 5.0
    rx, ry = 6.0, 3.6
    for y in range(1, 9):
        for x in range(4, 20):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1.0:
                # surface: highlight band near the back/top, water below
                put(x, y, hi if y <= cy - 1 else water)
            elif d <= 1.5:
                put(x, y, (105, 63, 0))  # 268's own wood — rim around the opening
    # a couple of ripple highlights
    put(9, 6, hi); put(14, 6, hi)

    out = f"{OUT}/water_barrel_derived/water_barrel_{fid}_derived.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out); lint(out, f"water_barrel_{fid} (268+water)")


if __name__ == "__main__":
    workbench()
    # palette blues (verified members): mid + light
    water_barrel(5084, (60, 178, 199), (212, 255, 255))
    water_barrel(5085, (60, 178, 199), (60, 178, 199))
