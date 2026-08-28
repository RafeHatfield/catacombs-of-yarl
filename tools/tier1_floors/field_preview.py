#!/usr/bin/env python3
"""Lay the family as a FIELD and measure the one thing §8.3 actually cares about.

    §8.3, THE SCALE RULE: the property lives at field scale and does not exist at tile scale.
    Judge a tile AS LAID.

`field_laws` answers that for ONE tile by tiling it 3x3. This module answers it for the FAMILY:
several variants distributed the way the renderer distributes them, with the overlay and channel
systems running, which is the only configuration that can pass. A single tile repeated is a
clone field BY CONSTRUCTION, whatever is drawn on it — that is the law, not a defect of any
tile — so the variant system is not a way of improving the field, it is the only thing that
makes a passing field possible at all.

THE LATTICE SCORE, and what makes it an instrument rather than a preference.

For every intra-cell position (u,v), take the values at that position across all cells of the
field. If the field is one tile repeated, every one of those samples is identical and the
variance is zero. If the cells are independent, the variance at a position is the variance of
the field. So:

    lattice = 1 - mean_over_positions(variance at that position) / variance of the whole field

    1.0   a clone field. Every cell identical. "It sits there every time."
    0.0   position carries no information. Nothing to lock onto.

It is geometry, not taste: it measures whether a value is predictable from its offset within a
cell, which is §8.3.1's test — *where does it sit, and does it sit there every time* — written
as a number. It says nothing whatever about whether the floor is any good; §13.4 keeps that at
the human gate and there is no dread score here.

⚠ ITS OPERATING POINT IS NOT SET BY THIS SESSION. A target for "how low is low enough" would be
a threshold nobody has derived, and §13.6 forbids calibrating it on the work seeking acceptance.
What this module reports is the score and its two ANCHORS, both computed from the same code on
the same field geometry: the clone field the seats culled, and the independent-cells limit. The
family's score is read between them. That is an ordering, and per Rafe's 2026-08-27 relabelling
of the ring instrument, an ordering RULES NOTHING.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import field_laws as FL      # noqa: E402

T = 32


def lattice_score(field, t=T):
    """See the module docstring. Returns the score and the two variances it is built from."""
    H, W = field.shape[:2]
    L = FL.RI.lum(field.astype(float))
    ny, nx = H // t, W // t
    cells = np.stack([L[r * t:(r + 1) * t, c * t:(c + 1) * t]
                      for r in range(ny) for c in range(nx)])       # (n, t, t)
    per_position = cells.var(axis=0)                                # variance across cells
    total = float(L.var())
    if total < 1e-9:
        return dict(lattice=1.0, var_total=total, var_per_position=0.0, cells=len(cells))
    score = 1.0 - float(per_position.mean()) / total
    return dict(lattice=round(score, 4), var_total=round(total, 2),
                var_per_position=round(float(per_position.mean()), 2), cells=int(len(cells)))


def compose_field(variants, overlays, ny, nx, seed, rates=None, t=T, orient=True):
    """Lay a field the way the renderer does: variant by position hash, overlay by seeded noise.

    The hash is the SAME one `TileThemeConfig.PickVariant` uses — `|x*7919 + y*104729|` — so this
    preview is not a different distribution wearing the renderer's name. A preview that laid
    tiles differently from the engine would be evidence about the preview.
    """
    out = np.zeros((ny * t, nx * t, 3), dtype=float)
    rng = np.random.default_rng(seed)
    by_family = {}
    for fam, img in overlays or []:
        by_family.setdefault(fam, []).append(img)
    rates = rates or {}
    events = [f for f in by_family if f != "grit"]

    def put(cell, img):
        # FLIP ONLY — four orientations, not eight, because that is what the ENGINE does.
        #
        # `Tier1FloorOverlays` sets FlipH/FlipV on a Sprite2D and cannot rotate: a floor sprite
        # is positioned by its top-left corner (`Centered = false`), so a rotation would turn the
        # tile about that corner and place it somewhere else entirely. The base tiles get their
        # eight orientations as baked assets instead, which is why they are not affected.
        #
        # This preview rotated. It was therefore laying a field the engine cannot produce, which
        # makes it evidence about the preview — the same failure `compose_field`'s own docstring
        # warns about for the position hash. Aligned to the engine rather than the engine to it.
        ov = img.astype(float)
        if rng.random() < 0.5:
            ov = ov[:, ::-1]
        if rng.random() < 0.5:
            ov = ov[::-1, :]
        ov = np.ascontiguousarray(ov)
        a = ov[..., 3:4] / 255.0
        return cell * (1 - a) + ov[..., :3] * a

    for r in range(ny):
        for c in range(nx):
            h = abs((c * 7919 + r * 104729) & 0x7FFFFFFF)
            cell = variants[h % len(variants)].astype(float).copy()
            # ORIENTATION. Three variants over a room is a visible repeat — measured, and seen:
            # the same bracket-shaped stone recurs on the variant pitch, which is the seat's own
            # cull almost word for word. Rotating and flipping per position turns 3 tiles into 24
            # distinct cells at zero asset cost.
            #
            # It is legal HERE for a reason that is worth naming, because it is §6.3 paying out:
            # an asset authored to RECEIVE light carries no direction, so there is no up in it to
            # break. A tile with a baked key light could not be turned at all. And a tile that
            # wraps stays wrapping under any rotation or flip of the square, so the seam
            # criterion survives the operation unchanged.
            #
            # The renderer already does exactly this for accent floors, by the same position
            # hash — this is that mechanism applied to the base family rather than a new one.
            #
            # `orient` is off for the CLONE ANCHOR only. That anchor has to stay a true clone
            # field — one tile, one orientation — because it is standing in for the thing five
            # seats culled. Rotating it would move the anchor along with the family and quietly
            # destroy the comparison the anchor exists to provide.
            if orient:
                o = (h >> 3) % 8
                cell = np.rot90(cell, o % 4)
                if o >= 4:
                    cell = cell[:, ::-1]
                cell = np.ascontiguousarray(cell)
            # grit is a dither, not an event: it composites first and independently.
            if "grit" in by_family and rng.random() < rates.get("grit", 0.0):
                cell = put(cell, by_family["grit"][int(rng.integers(len(by_family["grit"])))])
            # AT MOST ONE EVENT PER CELL. Two reads as damage rather than as use, and §8.1's
            # failure test is "is the state of this thing explained by traffic and indifference?"
            for fam in events:
                if rng.random() < rates.get(fam, 0.0):
                    cell = put(cell, by_family[fam][int(rng.integers(len(by_family[fam])))])
                    break
            out[r * t:(r + 1) * t, c * t:(c + 1) * t] = cell
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=os.path.join(REPO, "src/Presentation/assets/tier1_floors"))
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--rows", type=int, default=8)
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    man = json.load(open(os.path.join(a.assets, "MANIFEST.json")))
    variants = [np.asarray(Image.open(os.path.join(a.assets, b["file"])).convert("RGB"))
                for b in man["base"]]
    overlays = [(o["family"], np.asarray(Image.open(os.path.join(a.assets, o["file"]))
                                         .convert("RGBA")))
                for o in man["incident"]]
    # SINGLE SOURCE OF TRUTH: the rates come from the manifest the composer wrote, never from a
    # copy kept here. A preview laying tiles by its own numbers would be evidence about itself.
    rates = man.get("placement", {}).get("rates", {})
    os.makedirs(a.out, exist_ok=True)

    rows = []
    def run(label, vs, ovs, rs, orient=True):
        f = compose_field(vs, ovs, a.rows, a.cols, a.seed, rs, orient=orient)
        p = os.path.join(a.out, "field_%s.png" % label)
        Image.fromarray(f).save(p)
        s = lattice_score(f)
        s.update(label=label, file=os.path.relpath(p, REPO), variants=len(vs),
                 overlays=len(ovs), rates=rs, oriented=orient)
        rows.append(s)
        print("  %-26s lattice %.4f   (var total %.1f, per-position %.1f, %d cells)"
              % (label, s["lattice"], s["var_total"], s["var_per_position"], s["cells"]))
        return s

    print("FIELD LATTICE — 1.0 is a clone field, 0.0 is position carrying no information\n")
    print("  ANCHORS, computed by the same code on the same geometry:")
    run("anchor_clone", variants[:1], [], {}, orient=False)
    # The independent-cells limit: the same material, but every cell drawn with its own noise.
    # A TRUE independent limit: every cell is its OWN composed tile, built by the same composer
    # with its own seed and its own bond. Not "one variant plus noise" — that was the first
    # version of this anchor and it read 0.64, which is not the independent limit at all but the
    # residual structure of a single tile surviving additive noise. Reported as an anchor it
    # would have flattered the family by comparison, so it is replaced rather than kept.
    sys.path.insert(0, HERE)
    import compose_family as CF   # noqa: E402
    mat = man["material"]
    indep = [CF.build_base(i % CF.N_VARIANTS, mat, a.seed + 7919 * (i + 1))[0]
             for i in range(a.rows * a.cols)]
    f = np.zeros((a.rows * T, a.cols * T, 3), dtype=np.uint8)
    for i in range(a.rows * a.cols):
        f[(i // a.cols) * T:(i // a.cols + 1) * T, (i % a.cols) * T:(i % a.cols + 1) * T] = indep[i]
    p = os.path.join(a.out, "field_anchor_independent.png")
    Image.fromarray(f).save(p)
    s = lattice_score(f); s.update(label="anchor_independent", file=os.path.relpath(p, REPO),
             note="every cell its own composed tile, own seed, own bond")
    rows.append(s)
    print("  %-26s lattice %.4f   (var total %.1f, per-position %.1f, %d cells)"
          % ("anchor_independent", s["lattice"], s["var_total"], s["var_per_position"], s["cells"]))

    print("\n  THE FAMILY, laid as the renderer lays it:")
    run("base_only", variants, [], {})
    run("base_plus_incident", variants, overlays, rates)

    res = dict(commit=FL.git_commit(), assets=os.path.relpath(a.assets, REPO),
               grid=[a.rows, a.cols], seed=a.seed, fields=rows,
               note=("Ordering, not a verdict. No threshold is declared: §13.6 forbids "
                     "calibrating one on the work seeking acceptance, and no accepted floor "
                     "field exists yet to calibrate on."))
    op = os.path.join(a.out, "FIELD-LATTICE.json")
    with open(op, "w") as f2:
        json.dump(res, f2, indent=1)
    print("\nwritten: %s" % os.path.relpath(op, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
