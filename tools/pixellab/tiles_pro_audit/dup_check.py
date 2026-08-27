#!/usr/bin/env python3
"""Independent check of the blind seat's strongest claim, at zero cost.

Flip-list item 6 from the kit A0 seat, verbatim:

    "The set is not forty pieces. cand_13 and cand_33 are byte-identical; cand_22 and cand_39
     are 100% identical across their whole overlap; ... 105 of 715 overlapping pairs are 90%+
     identical. Author each role from scratch instead of re-cropping one master painting."

That is a mechanical claim about pixels, made by a process with no access to this repo, the
grammar, or the fact that the endpoint composes 60 of its 80 tiles from 20 painted swatches.
It is checkable here without another generation, and checking it does two things: it tells us
whether the seat is reliable on facts as well as on taste, and it measures `building_layout:
"materials"` from the output side rather than from the schema.

Comparison is over the OVERLAP of two pieces' opaque regions, aligned on the shared canvas —
the same thing a critic looking at two sprites is comparing. A pair with no overlap is skipped
rather than scored 0, because "these two never coincide" is not evidence of anything.
"""
import itertools
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheet as SH  # noqa: E402


def overlap_identity(a, b):
    """(fraction identical over the shared opaque region, size of that region)."""
    pa, pb = a.convert("RGBA").getdata(), b.convert("RGBA").getdata()
    same = n = 0
    for p, q in zip(pa, pb):
        if p[3] == 0 or q[3] == 0:
            continue
        n += 1
        if p == q:
            same += 1
    return (same / float(n) if n else None), n


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "kitA0"
    kit_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "yield", "kit_A0")
    kit = SH.load_kit(kit_dir)
    idx = [i for i in SH.WALL_SET if i in kit]

    pairs, identical, over90 = [], [], 0
    for i, j in itertools.combinations(idx, 2):
        frac, n = overlap_identity(kit[i], kit[j])
        if frac is None:
            continue
        pairs.append((i, j, frac, n))
        if frac == 1.0:
            identical.append((i, j, n))
        if frac >= 0.90:
            over90 += 1

    pairs.sort(key=lambda p: -p[2])
    print("kit: %s   %d wall pieces, %d overlapping pairs" % (kit_dir, len(idx), len(pairs)))
    print("\ntop 12 pairs by identity over their shared opaque region:")
    for i, j, f, n in pairs[:12]:
        print("  tile_%02d / tile_%02d   %6.2f%% identical over %5d px" % (i, j, f * 100, n))
    print("\n100%% identical pairs: %d" % len(identical))
    for i, j, n in identical[:20]:
        print("  tile_%02d / tile_%02d  (%d px)" % (i, j, n))
    print("\npairs >=90%% identical: %d of %d overlapping pairs" % (over90, len(pairs)))

    # How much unique art is actually in the wall set?
    seen, uniq = set(), 0
    for i in idx:
        h = kit[i].tobytes()
        if h not in seen:
            seen.add(h)
            uniq += 1
    print("byte-distinct wall sprites: %d of %d" % (uniq, len(idx)))

    out = {"kit": os.path.relpath(kit_dir, HERE), "n_wall_pieces": len(idx),
           "n_overlapping_pairs": len(pairs), "n_identical_pairs": len(identical),
           "identical_pairs": [[i, j, n] for i, j, n in identical],
           "n_pairs_ge_90pct": over90, "byte_distinct_sprites": uniq,
           "top_pairs": [[i, j, round(f, 4), n] for i, j, f, n in pairs[:30]]}
    d = os.path.join(HERE, "columns")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "dup_%s.json" % label), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print("\nwrote columns/dup_%s.json" % label)


if __name__ == "__main__":
    main()
