#!/usr/bin/env python3
"""Land the style-matched props: 64px canvas down to the family's 32px native.

WHAT CHANGED THE PASS, and it was the method rather than the prompt. Waves 1 and 2 ran BASIC
generation — no background — and came back isometric, vegetated, and as objects the identity
cards reject by name. `CC-SESSION-tier2-props.md` asks for generation *"conditioned on the landed
corpus"*, and I had not done it. Wave 3 fed the generator a 64px crop of the landed frame as
style context and inpainted into it:

    marker      orthogonal, square to the screen, rope legible, the scene's own palette. §3 held.
    fire        a ring of stones seen from directly above, charred interior. §3 held.
    barricade   FAILED SIX TIMES at first — four fences in basic mode, two floor-fills in
                style-match — and then landed as a FAMILY once the prompt stopped naming the
                object and described the ARRANGEMENT instead. "A heap of thick timber beams lying
                crossed over one another, seen from directly above" produced crossed baulks with
                rope at the join; "a barricade" never did. Top-down has no strong prior for the
                word; it has one for the shape.

So conditioning on the corpus is what makes §3 survive generation. That is worth more than the
three assets: it is the difference between "generation cannot do architecture" (§13.7, measured on
a TILED surface) and what a discrete prop can do when it is shown the room it will stand in.

THE DOWNSAMPLE IS 2:1 AND IT IS NOT A RESIZE. The context crop was the delivered frame, which is
the family at 2x, so the generator drew at 2px per art-pixel: 87% of its 2x2 blocks are uniform.
Taking one sample per block recovers the native art rather than inventing an average of it —
§4.3 forbids a sub-pixel gradient, and a bilinear resize would author one.
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASHLAR = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar")
SRC = os.path.join(HERE, "gen")

LAND = [("wave3/marker_styled.png", 9800, "B-PROP-001 the boundary marker stone"),
        ("wave3/fire_styled.png", 9820, "B-PROP-003 the orc fire"),
        # B-PROP-002, the barricade — A FAMILY, not a sprite (§8.3.1). It repeats along a line by
        # construction, so an incident baked into one becomes a motif at the second placement.
        # These three are one grammar — crossed baulks, rope at the join, iron through it —
        # differing in which repair was needed where.
        ("wave4/barricade_heap.png", 9810, "B-PROP-002a barricade, crossed baulks"),
        ("wave4/barricade_stack.png", 9811, "B-PROP-002b barricade, bound stack"),
        ("wave4/barricade_three.png", 9812, "B-PROP-002c barricade, parallel bound beams")]


def quantised(a):
    """How much of the art is already 2x2 blocks — the evidence the downsample is lossless."""
    bad = tot = 0
    for y in range(0, a.shape[0], 2):
        for x in range(0, a.shape[1], 2):
            blk = a[y:y + 2, x:x + 2].reshape(4, -1)
            tot += 1
            if not np.all(blk == blk[0]):
                bad += 1
    return 1.0 - bad / float(tot)


def land(name, tid, what):
    a = np.asarray(Image.open(os.path.join(SRC, name)).convert("RGBA"), dtype=np.uint8)
    q = quantised(a)
    # one sample per 2x2 block — never an average (§4.3: no sub-pixel gradients)
    small = a[::2, ::2, :]
    # trim fully transparent margin, then centre in 32x32 so the prop sits in its cell
    op = small[:, :, 3] > 128
    ys, xs = np.where(op)
    crop = small[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((32, 32, 4), dtype=np.uint8)
    h, w = min(32, crop.shape[0]), min(32, crop.shape[1])
    y0, x0 = (32 - h) // 2, (32 - w) // 2
    out[y0:y0 + h, x0:x0 + w] = crop[:h, :w]
    p = os.path.join(ASHLAR, "tier1_ashlar_%d.png" % tid)
    Image.fromarray(out, "RGBA").save(p)
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print("  %-34s id %d  %2dx%2d content, %.0f%% 2x2-quantised  %s"
          % (what, tid, w, h, q * 100, sha[:12]))
    return dict(name=what, id=tid, source=name, sha256=sha,
                content=[int(w), int(h)], quantised=round(q, 3))


def main():
    print("landing the style-matched props at the family's native size\n")
    tiles = [land(*x) for x in LAND]
    mf = os.path.join(HERE, "MANIFEST.json")
    man = json.load(open(mf)) if os.path.exists(mf) else {}
    man["family"] = "boundary_props_v1"
    man["method"] = ("style-matched generation conditioned on the LANDED FRAME, inpainted into a "
                     "64px crop of the delivered scene, downsampled 2:1 to the family's native "
                     "32px. Basic generation was tried first and could not hold §3.")
    man["landed"] = tiles
    man["outstanding"] = {
        "B-PROP-002 fourth variant": "THREE VARIANTS LANDED, NOT FOUR. The identity card asks for "
            "a variant family and three is a family; the fourth slot is open. Two attempts at it "
            "came back PALE — washed-out scattered debris rather than timber — and the pattern is "
            "worth keeping: 'beams crossed over one another' works, 'a baulk with beams across "
            "it' produces pale debris however the colour is described. The grammar that works is "
            "crossing, not stacking.",
        "history": "It took nine generations. Four basic-mode fences (the card's `role_reject` by "
                   "name), two style-matched floor-fills, two pale failures, and two composition "
                   "passes of my own that read as LADDERS — the same 'too light, too regular' "
                   "failure reached by a second route. What changed it was describing the "
                   "ARRANGEMENT rather than naming the object.",
    }
    man["palette_regime"] = ("ladder, not locked — §5.1's values are PLACEHOLDER and its "
                             "derivation has not landed")
    json.dump(man, open(mf, "w"), indent=1)
    print("\nmanifest: %s" % os.path.relpath(mf, REPO))


if __name__ == "__main__":
    main()
