#!/usr/bin/env python3
"""HOW MANY COLOURS DOES THE DELIVERED FRAME CARRY — a builder's tool. It prints; it never gates.

    python3 tools/tier1_walls/measure_colour_count.py <png> [<png> ...]
    python3 tools/tier1_walls/measure_colour_count.py --assets

RULED (Rafe, 2026-09-03): *"add a delivered-colour-count builder's-tool check (prints, never
gates) — delivered frame should carry ~its palette's count, not 69% more."*

WHY IT EXISTS. The frame critic read it off the picture before any instrument here could:

    "The whole frame carries a soft continuous-tone mottle over the pixel work (5763 unique
     colours against 2's 3414 for the same scene). Drop that layer; it's the single thing making
     the image read as filtered."

Confirmed — 5763 against the plant's 3414 on the same scene, 69% more. **Pixel art has a palette;
continuous tone does not.** A frame carrying far more colours than its palette has a stage
somewhere producing sub-ladder intermediate values, and the eye reads that as filtered, cemented,
or blurred long before anyone can name which stage did it.

§2 OF THE FRAME-CRITIC SKILL BINDS THIS FILE: instruments gate nothing. This one is a torch for
finding the stage, not a bar for the build to clear. It has no threshold and returns 0 always.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
VIEW = (90, 1001)          # the dungeon view; the HUD is not the art


def colours(path, view=True):
    a = np.asarray(Image.open(path).convert("RGB"))
    if view and a.shape[0] > VIEW[1]:
        a = a[VIEW[0]:VIEW[1]]
    flat = a.reshape(-1, 3)
    uniq, counts = np.unique(flat, axis=0, return_counts=True)
    # How much of the frame the top N colours cover — a palette-shaped frame is top-heavy.
    order = np.sort(counts)[::-1]
    tot = counts.sum()
    return dict(unique=len(uniq), px=int(tot),
                top16=float(order[:16].sum() / tot), top64=float(order[:64].sum() / tot),
                singletons=int((counts == 1).sum()))


def asset_palette():
    """The palette the cap is authored on: ladder rungs times the quarry tint."""
    m = json.load(open(os.path.join(REPO, "src/Presentation/assets/tier1_cap/MANIFEST.json")))
    lad, tint = m["ladder"], m.get("quarry_tint") or [1, 1, 1]
    return len(lad), [[round(v * t) for t in tint] for v in lad]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pngs", nargs="*")
    ap.add_argument("--assets", action="store_true",
                    help="count the colours in the cap's own tiles, not in a capture")
    a = ap.parse_args()

    if a.assets:
        d = os.path.join(REPO, "src/Presentation/assets/tier1_cap")
        man = json.load(open(os.path.join(d, "MANIFEST.json")))
        px = []
        for t in man["tiles"]:
            if t.get("cls") == "void":
                continue
            px.append(np.asarray(Image.open(os.path.join(d, t["file"])).convert("RGB"))
                      .reshape(-1, 3))
        flat = np.concatenate(px, 0)
        n, pal = asset_palette()
        print("THE CAP AS AUTHORED — %d windows" % len(px))
        print("  unique colours in the asset : %d" % len(np.unique(flat, axis=0)))
        print("  the ladder it is authored on: %d rungs" % n)
        print("  a palette-quantised cap would carry AT MOST the rung count, times nothing else.")
        return 0

    print("DELIVERED COLOUR COUNT — dungeon view only (rows %d..%d)" % VIEW)
    print("  frame                                unique   top16    top64  singletons")
    for p in a.pngs:
        try:
            r = colours(os.path.join(REPO, p) if not os.path.isabs(p) else p)
        except FileNotFoundError:
            print("  %-34s (missing)" % os.path.basename(p))
            continue
        print("  %-34s %7d %6.1f%% %7.1f%% %11d"
              % (os.path.basename(p), r["unique"], 100 * r["top16"], 100 * r["top64"],
                 r["singletons"]))
    print("\n  A palette-shaped frame is TOP-HEAVY: a few colours cover most of it, and there are")
    print("  few singletons. Continuous tone is the opposite — a long tail of near-duplicates.")
    print("  This prints. It does not gate (frame-critic skill §2).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
