#!/usr/bin/env python3
"""SUPERSEDED 2026-08-27 by tools/floor_remediation/ - DO NOT USE AS A RING TEST.

This file decides what is a ring with a luminance threshold (RING_FRACTION = 0.30 of the tile's
own median). Bible §12.1's worked example - written into the bible by this same spike, one round
after this file was written - holds that THE RING PROHIBITION IS VALUE-AGNOSTIC: A PALE RING IS
A RING, and that what separates occlusion from a ring "is whether the treatment answers to the
geometry it sits on, not whether it is lighter or darker than its surroundings".

Measured consequence, not a theoretical objection. This file's table kept A-VAB as "a mid-tone
rebate" at 0.48 of the median. A-VAB carries TWO closed 1px loops - 76 px and 32 px, each of one
width and one value the whole way round - and this file removed neither. The de-ringed floor it
produced for A-VAB is byte-identical to the raw survivor, and so is its lit in-scene capture
(sha256 9e9890c0fa4db115 either way). A blind seat, shown that capture and never shown §12.1,
culled it `keyline`: "Two concentric closed rectangles inset in the middle of every tile, each
one width and one value the whole way round - the tile is a framed plaque."

Its removal of B-KAB's 62px near-black ring was correct, and its fill rule - the MODAL non-ring
neighbour, never a per-channel median, so no colour is invented - was right and is kept
unchanged in the successor.

Retained because the round-8 captures on disk were taken through it and their provenance must
stay readable. Nothing new should call it.

--- ORIGINAL HEADER FOLLOWS ---

Strip the baked keyline from the §6.4 survivor floors, as a labelled MOCK derivation.

WHY THIS EXISTS, AND WHY IT IS NOT A CORRECTION OF SOMEONE ELSE'S WORK
---------------------------------------------------------------------
Round 7 culled ALL FIVE candidates `outline` at step 1, and not one of the culls was about a
wall:

    "Every floor plate is a lighter square inside a closed, single-value near-black ring
     measured at 11% of the adjacent floor - four to five times harder than any mortar joint in
     the same frame - which is a keyline, and it sits on every second tile of every corridor."

That ring is in the §6.4 STOP-1 survivor floors. It was already reported qualitatively in round
3 ("a uniform 3px near-black ring on all four sides"); round 7 measured it and killed the round
with it. **Bible §12.1 is LOCKED: nothing in Yarl carries a baked dark ring.**

So the survivors, as they stand, cull any review round they appear in before the wall questions
are reached. The ruled rounds are for §3 and §12.1 and cannot be answered through a step-1 cull
caused by the floor.

This is a harness gap. Named, smallest fix, proceed:

  - It does NOT correct the survivors. Their files are untouched and this writes nowhere near
    tools/pixellab/probe_6_4/.
  - It derives a MOCK floor for instrument use only, marked MOCK in the filename like every
    other composed tile here, and it never lands. §13.1 governs landing.
  - The finding goes to Rafe intact and is not quietly absorbed by the fix: the survivors carry
    a construction §12.1 forbids, and that is his to rule on, not this session's to repair.

WHAT IT DOES
------------
A ring pixel is one that is far darker than its own tile's stone AND has a lighter neighbour on
the opposite side - i.e. a hard edge drawn around something rather than a shadow cast between
planes. Each is replaced by the median of its non-ring neighbours, so the plate keeps its shape
and its material and loses only the keyline.

Nothing is brightened, no colour is invented, and the result is snapped back to the survivors'
own palette.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
OUT = os.path.join(REPO, "src/Presentation/assets/composition_spike/floors_deringed")

# A ring pixel sits below this fraction of its own tile's median luminance. 0.30 is chosen
# against the measured survivors, not picked round:
#
#   A-VAB  median 126, darkest band 60  -> 0.48   a mid-tone rebate. KEPT.
#   A-HEB  median 136, darkest band 78  -> 0.57   a mid-tone rebate. KEPT.
#   C-GAB  median 139, darkest band 74  -> 0.53   a mid-tone rebate. KEPT.
#   B-KAB  median 130, darkest band 14  -> 0.11   a NEAR-BLACK CLOSED RING. Removed.
#
# 0.11 is the number the round-7 seat measured independently ("11% of the adjacent floor"), and
# it named the discrimination this threshold makes: "Within a single corridor one plate is
# ringed in near-black and the next in mid-brown double line, for what is meant to be the same
# object. Keep the mid-brown rebate, delete the black-ringed variant."
RING_FRACTION = 0.30


def lum(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def dering(a):
    L = lum(a.astype(float))
    med = float(np.median(L))
    ring = L < med * RING_FRACTION
    if not ring.any():
        return a.copy(), 0
    out = a.copy()
    H, W = ring.shape
    # Several passes: a 2-3px ring needs its outer band resolved before its inner one has
    # non-ring neighbours to borrow from.
    for _ in range(4):
        remaining = np.argwhere(ring)
        if not len(remaining):
            break
        progressed = False
        for y, x in remaining:
            vals = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and not ring[ny, nx]:
                        vals.append(out[ny, nx])
            if vals:
                # The MODAL neighbour, not the median. A per-channel median mixes channels and
                # can produce a colour that is in neither neighbour - this script must not
                # invent one, and the assertion below would catch it.
                uniq, counts = np.unique(np.array(vals), axis=0, return_counts=True)
                out[y, x] = uniq[counts.argmax()].astype(a.dtype)
                ring[y, x] = False
                progressed = True
        if not progressed:
            break
    return out, int((L < med * RING_FRACTION).sum())


def main():
    os.makedirs(OUT, exist_ok=True)
    surv = json.load(open(os.path.join(SURVIVORS, "MANIFEST.json")))["survivors"]
    pal = set()
    for s in surv:
        a = np.array(Image.open(os.path.join(SURVIVORS, s["file"])).convert("RGB"))
        pal |= set(map(tuple, a.reshape(-1, 3).astype(int)))
    print("de-ringing the §6.4 survivor floors - MOCK derivation, instrument use only")
    print("the survivors themselves are NOT modified; §12.1's finding goes to the gate intact\n")
    for i, s in enumerate(surv):
        a = np.array(Image.open(os.path.join(SURVIVORS, s["file"])).convert("RGB"))
        out, n = dering(a)
        assert set(map(tuple, out.reshape(-1, 3).astype(int))) <= pal, \
            "de-ring invented a colour - it must not"
        p = os.path.join(OUT, "MOCK_dering_%d.png" % (9120 + i))
        Image.fromarray(out).save(p)
        print("  %-6s %-12s  %3d ring pixels removed of 1024" % (s["code"], s["file"], n))
    print("\n-> %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
