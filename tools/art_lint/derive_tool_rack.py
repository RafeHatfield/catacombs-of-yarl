#!/usr/bin/env python3
"""Derive a tool_rack (5090 replacement) from canon weapon-stand 323's construction — same method
as the landed armor stand (fineness rework rank 11). Keep 323's frame (posts/crossbar/rack/legs),
remove the sword, hang two simple chunky tools (a hammer and a mallet/maul) on the rack. Colours
from 323's ramp plus its wood brown; no canon pixels fed to any generator."""
import os
import sys

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
import art_lint

W = "src/Presentation/assets/sprites_16bf/world_24x24"
A = (38, 38, 38); B = (87, 71, 0); C = (71, 71, 71); D = (145, 145, 145); E = (201, 201, 201)
T = (0, 0, 0, 0)


def main():
    im = Image.open(f"{W}/oryx_16bit_fantasy_world_323.png").convert("RGBA")
    px = im.load()

    # Strip the sword (hilt/guard rows 0-6 cols 8-15; blade centre row 12 + tip rows 16-20; base r21).
    for y in range(0, 7):
        for x in range(8, 16):
            px[x, y] = T
    for x in range(11, 13):
        px[x, 12] = T
    for y in range(16, 21):
        for x in range(9, 14):
            px[x, y] = T
    for x in range(10, 12):
        px[x, 21] = T
    # Heal the rack centre where the sword crossed it.
    for x in range(11, 13):
        px[x, 7] = (*A, 255)
    for x in range(10, 14):
        px[x, 8] = (*D, 255)

    def put(x, y, col):
        if 0 <= x < 24 and 0 <= y < 24:
            px[x, y] = (*col, 255)

    # Hammer hung left-of-centre: dark iron head + wood handle, hanging from the rack.
    hammer = {
        1: [(8, A), (9, A), (10, A)],
        2: [(8, A), (9, C), (10, D), (11, A)],
        3: [(8, A), (9, C), (10, C), (11, A)],
        4: [(9, A), (10, B), (11, A)],
        5: [(9, A), (10, B), (11, A)],
        6: [(9, A), (10, B), (11, A)],
    }
    # Maul/mallet hung right-of-centre: bigger wood/stone head + handle.
    maul = {
        1: [(13, A), (14, A), (15, A)],
        2: [(12, A), (13, D), (14, E), (15, D), (16, A)],
        3: [(12, A), (13, D), (14, D), (15, D), (16, A)],
        4: [(13, A), (14, B), (15, A)],
        5: [(13, A), (14, B), (15, A)],
        6: [(13, A), (14, B), (15, A)],
    }
    for shape in (hammer, maul):
        for y, cells in shape.items():
            for x, col in cells:
                put(x, y, col)

    out = "tools/art_lint/candidates/burndown3/tool_rack_derived/tool_rack_5090_derived.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)
    ps = art_lint.load_palette("config/art/oryx_master_palette.json")
    l = art_lint.lint_file(out, "prop", ps)
    print(f"tool_rack derived -> {out}  lint {l['overall']} "
          f"A1={l['A1']}(off={l['A1_off_palette_colors']}) A4={l['A4_color_count']}/{l['A4']} "
          f"A5={l['A5']} A6={l['A6']}")


if __name__ == "__main__":
    main()
