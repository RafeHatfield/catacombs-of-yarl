#!/usr/bin/env python3
"""Side-by-side sheets for the human gate.

These are pairs of DEVICE-SIZED LIT CAPTURES set beside each other, not contact sheets of
tiles. Each pair differs by exactly one thing, named in the caption, so what the eye is being
asked to compare is unambiguous:

    held_vs_unheld_A / _B   bound arm beside its control - the MOCK binding overlays are the
                            only difference; everything else is the same stones, same rig.
    top_plane_A_vs_B        the two top-plane treatments beside each other - native R4 value
                            against the value-matched derivation.
    lit_vs_unlit_B          §6.3's claim made checkable: the same tiles under the carried
                            light and under ambient alone.
    solofloor_pair          the same held/unheld comparison with the floor held to one
                            survivor instead of all four.

Bible §13.1 still governs: NOTHING IS APPROVED FROM A SHEET. These exist so a human looking at
the device has the comparison in front of them; the verdict is taken on the device.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.join(HERE, "evidence")
OUT = os.path.join(EVIDENCE, "sheets")

PAIRS = [
    ("held_vs_unheld", "before_lit.png", "before_unbound_lit.png",
     "HELD vs UNHELD - round 8's first-ranked arm",
     "before: MOCK straps, pins, cramps, lashing, one tag",
     "before_unbound: the same stones, overlays omitted"),
    ("ruled_value_separation", "before_lit.png", "after_nocap_lit.png",
     "WALL-TOP VALUE SEPARATION and JOINT DEEPENING",
     "before: 5px occlusion, 0.62 albedo, joints untouched (ranked 1st)",
     "after_nocap: the same, joints deepened (ranked 2nd)"),
    ("ruled_coping_cap", "before_lit.png", "after_lit.png",
     "THE COPING CAP - and why it is a ring",
     "before: no cap (ranked 1st)",
     "after: coping course on every floor-facing edge (ranked 3rd)"),
    ("authored_vs_baked", "before_lit.png", "plant_lit.png",
     "AUTHORED OCCLUSION vs DEPICTED LIGHT - the within-arm A/B",
     "before: form only. No light direction anywhere.",
     "plant: the same stones + a baked key light (culled key-light, ranked 4th)"),
    ("lit_vs_unlit", "before_lit.png", "before_unlit.png",
     "THE SAME TILES, LIT AND UNLIT (bible §6.3)",
     "carried light on - energy 1.6",
     "ambient only - energy 0, nothing else changed"),
]

BAR = 34
GAP = 12
BG = (18, 18, 22)
FG = (232, 232, 232)
DIM = (150, 150, 156)


def build(name, left, right, title, cap_l, cap_r):
    a = Image.open(os.path.join(EVIDENCE, left)).convert("RGB")
    b = Image.open(os.path.join(EVIDENCE, right)).convert("RGB")
    w, h = a.size
    sheet = Image.new("RGB", (w * 2 + GAP * 3, h + BAR * 2 + GAP * 2), BG)
    d = ImageDraw.Draw(sheet)
    d.text((GAP, 10), title, fill=FG)
    d.text((GAP, 24), "identical rig, identical geometry, identical floors - "
                      "the caption names the only difference", fill=DIM)
    sheet.paste(a, (GAP, BAR + GAP))
    sheet.paste(b, (GAP * 2 + w, BAR + GAP))
    y = BAR + GAP + h + 6
    d.text((GAP, y), cap_l, fill=FG)
    d.text((GAP * 2 + w, y), cap_r, fill=FG)
    d.text((GAP, y + 14), "%s   |   %s" % (left, right), fill=DIM)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".png")
    sheet.save(p)
    return p


def main():
    for spec in PAIRS:
        p = build(*spec)
        print("  %s" % os.path.relpath(p, os.path.dirname(os.path.dirname(HERE))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
