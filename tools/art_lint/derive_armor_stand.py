#!/usr/bin/env python3
"""Derive an armor_stand (5002 replacement) from canon weapon-stand 323's construction.

Register ruling (play review 2026-08): chunky, low-detail, bold-read — the opposite of the
current 5002 (a noisy, over-rivetted cuirass). This takes 323's ACTUAL post/crossbar/leg/rack
pixels (the stand frame), removes the mounted sword, and mounts a simple helm + cuirass in the
same register, using only colours already present in 323 (all master-palette members, canon-
derived). No canon pixels are ever sent to any generator — this is local pixel composition of art
already licensed in this game.

Colours borrowed from 323: A dark outline, B wood, C/D/E/F greys. Metal = the C/D/E ramp.
"""
import os
import sys

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
import art_lint

W = "src/Presentation/assets/sprites_16bf/world_24x24"

# Colours read out of canon 323 (all confirmed master-palette members).
A = (38, 38, 38)      # dark outline
B = (87, 71, 0)       # wood
C = (71, 71, 71)      # metal shadow
D = (145, 145, 145)   # metal mid
E = (201, 201, 201)   # metal highlight

TRANSPARENT = (0, 0, 0, 0)


def main():
    im = Image.open(f"{W}/oryx_16bit_fantasy_world_323.png").convert("RGBA")
    px = im.load()

    # ── 1. Strip the sword ────────────────────────────────────────────────
    # Hilt + guard + upper blade (rows 0-6, centre cols 8-15) and the blade tip that runs
    # down the centre through the frame (row 12 cols 11-12; rows 16-20 cols 9-13).
    for y in range(0, 7):
        for x in range(8, 16):
            px[x, y] = TRANSPARENT
    for x in range(11, 13):
        px[x, 12] = TRANSPARENT
    for y in range(16, 21):
        for x in range(9, 14):
            px[x, y] = TRANSPARENT
    for x in range(10, 12):        # row-21 sword-base remnant between the legs
        px[x, 21] = TRANSPARENT
    # Heal the rack where the sword passed through it (row 7 centre outline, row 8 centre surface).
    for x in range(11, 13):
        px[x, 7] = (*A, 255)
    for x in range(10, 14):
        px[x, 8] = (*D, 255)

    # ── 2. Mount the helm (great-helm dome) above the rack, where the hilt was ─────
    def put(x, y, col):
        if 0 <= x < 24 and 0 <= y < 24:
            px[x, y] = (*col, 255)

    helm = {
        1: [(10, A), (11, A), (12, A), (13, A)],
        2: [(9, A), (10, D), (11, E), (12, E), (13, D), (14, A)],
        3: [(9, A), (10, D), (11, E), (12, E), (13, D), (14, A)],
        4: [(9, A), (10, A), (11, A), (12, A), (13, A), (14, A)],   # visor slit (dark band)
        5: [(9, A), (10, D), (11, D), (12, D), (13, D), (14, A)],
        6: [(10, A), (11, C), (12, C), (13, A)],                    # neck
    }
    for y, cells in helm.items():
        for x, col in cells:
            put(x, y, col)

    # ── 3. Mount the cuirass (breastplate) below the rack, over the wooden crossbar ─
    # Hangs from the rack centre (rows 9-16). Chunky trapezoid, single centre ridge, thick
    # outline. Sits in front of the frame; the legs/feet remain visible either side.
    cuirass = {
        9:  [(9, A), (10, A), (11, A), (12, A), (13, A), (14, A)],           # shoulders top
        10: [(8, A), (9, D), (10, E), (11, E), (12, E), (13, E), (14, D), (15, A)],
        11: [(8, A), (9, D), (10, E), (11, D), (12, D), (13, E), (14, D), (15, A)],  # centre ridge
        12: [(8, A), (9, C), (10, D), (11, D), (12, D), (13, D), (14, C), (15, A)],
        13: [(9, A), (10, D), (11, D), (12, D), (13, D), (14, A)],
        14: [(9, A), (10, C), (11, D), (12, D), (13, C), (14, A)],
        15: [(10, A), (11, C), (12, C), (13, A)],                            # waist
    }
    for y, cells in cuirass.items():
        for x, col in cells:
            put(x, y, col)

    out = f"tools/art_lint/candidates/burndown3/armor_stand_derived/armor_stand_5002_derived.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)

    ps = art_lint.load_palette("config/art/oryx_master_palette.json")
    l = art_lint.lint_file(out, "prop", ps)
    print(f"derived -> {out}")
    print(f"  lint {l['overall']}  A1={l['A1']}(off={l['A1_off_palette_colors']}) "
          f"A2={l['A2']} A3={l['A3']} A4={l['A4_color_count']}/{l['A4']} "
          f"A5={l['A5']} A6={l['A6_outline_fraction']}/{l['A6']}")


if __name__ == "__main__":
    main()
