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
ROUTE = {"A-VAB": "surgery - 108 px stripped, no colour invented.  RULED prop stock regardless",
         "A-HEB": "carried unchanged - never carried a ring.  RULED secondary style parent",
         "B-KAB": "RETIRED, no remediation.  right-hand tile is the culled candidate, NOT promoted",
         "C-GAB": "carried unchanged - never carried a ring.  RULED primary style parent"}


def vab_sheet():
    """A-VAB alone, before and after, larger - the re-curation deliverable.

    Your eye picked A-VAB and this is what surgery did to it. The ruling that A-VAB is prop stock
    is already made and does not depend on this: it is about composition, not the keyline. What
    is open is whether the de-ringed tile is still the tile you picked, as a prop.
    """
    crop = (150, 300, 600, 750)
    w, h = crop[2] - crop[0], crop[3] - crop[1]
    sheet = Image.new("RGB", (MARGIN + 2 * w + GAP + MARGIN, MARGIN + h + LABEL_H + 26),
                      (18, 18, 24))
    d = ImageDraw.Draw(sheet)
    d.text((MARGIN, 10), "A-VAB - RE-CURATION.  Left: as it sits in the ledger.  "
                         "Right: after surgery (108 px, 2 closed loops, no colour invented).",
           fill=(235, 225, 190))
    d.text((MARGIN, 26), "Walls, rig and geometry identical - the floor is the only variable.  "
                         "Ring-clean by instrument; the blind seat still culls it `keyline`.",
           fill=(190, 190, 198))
    for j, setname in enumerate(("orig", "remed")):
        src = os.path.join(CAPS, "%s_A-VAB_lit.png" % setname)
        sheet.paste(Image.open(src).convert("RGB").crop(crop),
                    (MARGIN + j * (w + GAP), MARGIN + LABEL_H))
    p = os.path.join(OUT, "recurate_A-VAB.png")
    sheet.save(p)
    return p


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
    v = vab_sheet()
    for q in (p, v):
        print("-> %s" % os.path.relpath(q, REPO))
    print("   navigation only; the verdict surface is evidence/captures/ (bible §13.1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
