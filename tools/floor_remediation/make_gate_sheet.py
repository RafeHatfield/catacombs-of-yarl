#!/usr/bin/env python3
"""Before/after crops for the gate, under the session's ruling trigger.

NOT A VERDICT SURFACE. Bible §13.1: no candidate is approved from a contact sheet, and this is
a contact sheet. The verdict comes from the full lit captures in evidence/captures/, which are
the production renderer at the reference device's pixel size and are what the blind seat saw.
This exists so the before/after pairing can be looked at side by side without flipping between
twelve 750x1334 screenshots, and for nothing else.

Crops are 1:1 - no resampling - taken from the identical region of every capture, so the pair
differs by the floor tile and by nothing else.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CAPS = os.path.join(HERE, "evidence", "captures")
OUT = os.path.join(HERE, "evidence")
CODES = ("A-VAB", "A-HEB", "B-KAB", "C-GAB")

# The lit corridor crossing, centred on the player. Identical for every capture.
CROP = (185, 330, 565, 710)
GAP, LABEL_H, MARGIN = 10, 22, 34
ROUTE = {"A-VAB": "surgery - 108 px stripped, no colour invented",
         "A-HEB": "carried unchanged - never carried a ring",
         "B-KAB": "regenerated - surgery measured to empty the tile",
         "C-GAB": "carried unchanged - never carried a ring"}


def main():
    w, h = CROP[2] - CROP[0], CROP[3] - CROP[1]
    sheet = Image.new("RGB", (MARGIN + 2 * w + GAP + MARGIN,
                              MARGIN + len(CODES) * (h + LABEL_H + GAP)), (18, 18, 24))
    d = ImageDraw.Draw(sheet)
    d.text((MARGIN, 10), "SURVIVOR FLOORS - BEFORE (left, in the ledger) / AFTER (right, "
                         "remediated).  Walls, rig, geometry identical; the floor is the only "
                         "variable.", fill=(210, 210, 215))
    for i, code in enumerate(CODES):
        y = MARGIN + i * (h + LABEL_H + GAP)
        d.text((MARGIN, y), "%s   %s" % (code, ROUTE[code]), fill=(235, 225, 190))
        for j, setname in enumerate(("orig", "remed")):
            src = os.path.join(CAPS, "%s_%s_lit.png" % (setname, code))
            sheet.paste(Image.open(src).convert("RGB").crop(CROP),
                        (MARGIN + j * (w + GAP), y + LABEL_H))
    p = os.path.join(OUT, "gate_before_after.png")
    sheet.save(p)
    print("-> %s   (navigation only; the verdict surface is evidence/captures/)"
          % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
