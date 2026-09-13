#!/usr/bin/env python3
"""OBJECT-PROJECTION RULING, ROUND TWO — one layout, one projection per scene, five scenes.

    python3 tools/tier2_props/projection_round2.py scenes      # write the 6 scene JSONs
    python3 tools/tier2_props/projection_mesh.py               # draw the projection templates
    python3 tools/tier2_props/projection_round2.py plan        # write the landing plans
    python3 tools/tier2_props/projection_round2.py measure     # the instrument (ordering only)

WHAT ROUND ONE GOT WRONG, in Rafe's words, and what this file does about each:

  "the standing stone was the same (wrong) object in all three builds"
      Every archetype is regenerated PER CANDIDATE, the stone included. The marker is never
      reused. CANDIDATES x ARCHETYPES below is the whole matrix and every cell is its own
      generation.

  "C mixed projections within one scene; objects within a build disagreed with each other"
      One projection per scene. The projection is stated as GEOMETRY — a projected model drawn by
      projection_mesh.py, exact side and exact depth — and every generation for that scene is handed
      the same template. A scene is judged for whole-scene feel, which is the entire question,
      and that needs everything in it to agree.

  "the table read as a glowing slab and the standing stone as a black rectangle"
      Placement, not projection. Round one had the altar two tiles from the lamp and the rack
      five. LAYOUT below puts every archetype between 2.83 and 3.16 tiles from the player, and
      the GROUND scene carries a legibility probe on every archetype cell so the delivered
      luminance at each is a measured number in the capture log, not a claim.

THE CANDIDATES, as geometry (screen y down; the front face is always the south face):

  W        front + top, no side. The walls' grammar. Top is an axis-aligned rectangle.
  O-L      OBLIQUE, cabinet depth. Front face square-on; the LEFT side recedes up-left at 45
           degrees; receding edges drawn at 1/3 of true depth. Top is a parallelogram sheared
           LEFT.
  O-R      the same, receding up-RIGHT. Top sheared RIGHT.
  O-deep   oblique at cavalier depth — receding edges at 1/2 of true depth. Side per O_DEEP_SIDE
           (stated, below), because the brief allows either and the choice must be on record.
  A        the volume control. 2:1 DIMETRIC: the object is turned so TWO vertical faces show,
           each foreshortened, edges at 2:1 pixel slopes; the top is a rhombus. No square-on
           face. This is the "looks best as an object" reading from round one, rebuilt so that
           every object in the scene is drawn the same way.

The receding side is a whole-game constant — no fixed light motivates it — so L vs R is a
real ruling and both are built.

⚠ NOTHING HERE ENTERS THE GAME'S PROP SET. Ids 9850-9884 are a reserved review block: round
one's 9850-9872 are superseded and overwritten (their generations stay in gen/projection/ and in
git history), and the block is EXTENDED to 9884 because five candidates need 35 cells. No props
manifest lists them, no placer places them, no game scene names them.

⚠ THE INSTRUMENT ORDERS, IT DOES NOT RULE. §13.2: the eye rules, on device. Seats may order
candidates and name which archetype breaks; Rafe rules one projection, and for oblique the side
and the depth.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENES = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes")
ASHLAR = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar/tier1_ashlar_%d.png")
GEN = os.path.join(HERE, "gen", "projection2")
CELL = 32          # native
DEVICE = 2         # the frame, and the generator's canvas, is 2x

# ── the layout: ONE, shared by every scene ───────────────────────────────────────────────────
PLAYER = (7, 14)

# archetype, footprint w, footprint h, top-left cell, what it stresses
ARCHETYPES = [
    ("stone",  1, 2, (4, 13),  "tall vertical — does its side read against the wall's, or fight it"),
    ("chest",  1, 1, (10, 14), "low horizontal — the classic oblique case; top-to-face ratio"),
    ("barrel", 1, 1, (9, 16),  "ROUND — no flat face to hide behind; the lid states the camera"),
    ("altar",  2, 1, (6, 17),  "wide flat — mostly top; does the top share the floor plane"),
    ("rack",   1, 1, (9, 12),  "AGAINST A WALL — the discriminator; (9,11) is solid rock"),
]

# ONE material per archetype, held verbatim across every candidate, so the projection is the
# only thing that varies. No candidate gets a nicer wood.
MATERIALS = {
    "stone":  "a tall standing stone: one upright block of dressed grey limestone, weathered, "
              "plain faces, no carving, no moss, no runes",
    "chest":  "a low wooden chest: dark oak planks, two black iron bands, a black iron lock "
              "plate, lid closed",
    "barrel": "a wooden barrel standing upright: oak staves, three dark iron hoops, closed lid",
    "altar":  "a low wide altar slab: one block of pale grey limestone, flat plain top, "
              "no cloth, no candles, nothing on it",
    "rack":   "a wooden shelf rack: dark oak, three open shelves, empty, open front",
}

CANDIDATES = ["W", "OL", "OR", "Odeep", "A"]
O_DEEP_SIDE = "R"      # stated, not hidden: O-deep recedes to the same side as O-R. See the doc.
DEPTH = {"OL": 1.0 / 3, "OR": 1.0 / 3, "Odeep": 0.5}
SIDE = {"OL": -1, "OR": +1, "Odeep": (+1 if O_DEEP_SIDE == "R" else -1)}

# ids: 7 cells per candidate, in ARCHETYPES order, multi-cell footprints row-major
FIRST_ID = 9850


def ids_for(cand):
    base = FIRST_ID + CANDIDATES.index(cand) * 7
    out, n = {}, 0
    for name, w, h, _, _ in ARCHETYPES:
        out[name] = list(range(base + n, base + n + w * h))
        n += w * h
    return out


# ── the room: the ratified combined room, carve list verbatim from round one ─────────────────
CARVE = [
    {"x0": 3, "y0": 12, "x1": 13, "y1": 14},
    {"x0": 3, "y0": 16, "x1": 13, "y1": 19},
    {"x0": 3, "y0": 15, "x1": 4, "y1": 15},
    {"x0": 6, "y0": 15, "x1": 13, "y1": 15},
    {"x0": 8, "y0": 6, "x1": 8, "y1": 11},
    {"x0": 3, "y0": 2, "x1": 13, "y1": 5},
    {"x0": 1, "y0": 16, "x1": 2, "y1": 17},
]
BOUND_LIT, BOUND_DARK = 0.100404, 0.08367
BOUND_WHY = ("ABSOLUTE delivered luminance (0..1). RULED (Rafe, 2026-09-07): the ratio-against-"
             "the-brightest-pixel bound this replaces was measured against a reference cell that "
             "CLIPPED at 255 — a ratio against the ceiling, not the scene. Derived as "
             "reference_lum_on_the_NULLED_build_at_the_ratified_rig (0.8367) x the retired ratio "
             "bound.")


def carved(x, y):
    return any(c["x0"] <= x <= c["x1"] and c["y0"] <= y <= c["y1"] for c in CARVE)


def cells_of(w, h, tl):
    return [(tl[0] + i % w, tl[1] + i // w) for i in range(w * h)]


def dist(cell):
    return math.hypot(cell[0] - PLAYER[0], cell[1] - PLAYER[1])


def check_layout():
    """The controls, asserted: every archetype cell carved, none overlapping, none on the
    player, the rack's north neighbour solid, and every cell inside the same distance band."""
    seen = set()
    for name, w, h, tl, _ in ARCHETYPES:
        for c in cells_of(w, h, tl):
            assert carved(*c), "%s cell %s is rock" % (name, c)
            assert c not in seen, "%s cell %s overlaps another prop" % (name, c)
            assert c != PLAYER, "%s stands on the player" % name
            seen.add(c)
    rx, ry = dict((a[0], a[3]) for a in ARCHETYPES)["rack"]
    assert not carved(rx, ry - 1), "the rack is not against a wall"
    # the room's pillar at (5,15): no footprint cell may sit directly on any solid cell's
    # south side or north side, or the object is read for the rock it abuts, not its projection
    for c in seen:
        assert (c[0], c[1] + 1) != (5, 15) and (c[0], c[1] - 1) != (5, 15), "%s stacks on the pillar" % (c,)
    ds = [dist(c) for _, w, h, tl, _ in ARCHETYPES for c in cells_of(w, h, tl)]
    return min(ds), max(ds)


def probe(x, y, expect, why):
    return {"x": x, "y": y, "expect": expect, "why": why,
            "bound_lum": BOUND_LIT if expect == "lit" else BOUND_DARK,
            "bound_derivation": BOUND_WHY}


def scene(cand):
    lo, hi = check_layout()
    ground = cand is None
    name = "tier1_projection2_ground" if ground else "tier1_projection2_%s" % cand
    what = [
        "OBJECT-PROJECTION RULING, ROUND TWO — one projection per scene. NOT A PROPS PASS.",
        "",
        ("GROUND: the layout with NO props, a legibility probe on every archetype cell, so the "
         "delivered luminance each object will stand in is a measured number." if ground else
         "%s — see tools/tier2_props/projection_round2.py for the candidate's geometry. Every "
         "archetype in this scene was generated at THIS projection from THIS candidate's template; "
         "nothing is reused from another scene or from the marker." % cand),
        "",
        "Five archetypes at IDENTICAL cells in every scene, all between %.2f and %.2f tiles from "
        "the player, so placement is not the variable (round one's altar sat at 2.0 and its rack "
        "at 5.0, and both were read for their placement)." % (lo, hi),
        "",
    ] + ["  %-7s %dx%d at %s  d=%.2f  %s" % (n, w, h, tl, dist(tl), why)
         for n, w, h, tl, why in ARCHETYPES] + [
        "",
        "⚠ IDS 9850-9884 ARE A RESERVED REVIEW BLOCK, referenced by these scenes and nothing else. "
        "No props manifest lists them, no placer places them, no game scene names them. The ruling "
        "is Rafe's, on device (§13.1/§13.2).",
    ]
    d = {"name": name, "_what": what, "width": 17, "height": 21,
         "player": {"x": PLAYER[0], "y": PLAYER[1]}, "carve": CARVE}
    if ground:
        leg = [probe(c[0], c[1], "lit", "%s cell — the illumination the object will stand in" % n)
               for n, w, h, tl, _ in ARCHETYPES for c in cells_of(w, h, tl)]
    else:
        leg = [probe(6, 13, "lit", "floor beside the player, inside the radius"),
               probe(8, 15, "lit", "floor between the archetypes, clear of every footprint")]
    leg += [probe(8, 7, "dark", "up the corridor, beyond the radius"),
            probe(3, 19, "dark", "the far corner; the room must have an outside")]
    d["legibility"] = leg
    d["props"] = []
    if not ground:
        ids = ids_for(cand)
        for n, w, h, tl, _ in ARCHETYPES:
            p = {"tileId": ids[n][0], "x": tl[0], "y": tl[1], "blocks": True,
                 "why": "%s — %s" % (n, cand)}
            if w * h > 1:
                p.update(w=w, h=h, layout=ids[n])
            d["props"].append(p)
    return d


def write_scenes():
    lo, hi = check_layout()
    print("layout: player %s; archetype cells at %.2f..%.2f tiles" % (PLAYER, lo, hi))
    for cand in [None] + CANDIDATES:
        d = scene(cand)
        p = os.path.join(SCENES, d["name"] + ".json")
        json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
        print("  wrote %s  (%d props, %d probes)" % (os.path.relpath(p, REPO),
                                                     len(d["props"]), len(d["legibility"])))


# ── the templates live in projection_mesh.py ────────────────────────────────────────────────
# The first version of this file drew each candidate's box by hand. That was replaced by a
# projector (projection_mesh.py) the moment the barrel needed its lid: a hand-drawn box cannot
# tell you what oblique does to a circle, and a candidate has to be ONE function applied to every
# archetype. canvas_for() is kept here because the scene builder and the lander share it.

def canvas_for(name):
    _, w, h, _, _ = [a for a in ARCHETYPES if a[0] == name][0]
    return (w * CELL * DEVICE, h * CELL * DEVICE)


# ── landing plans, one per candidate, for land_scaled_props.py ───────────────────────────────
def write_plans():
    for cand in CANDIDATES:
        ids = ids_for(cand)
        props = []
        for name, w, h, _, _ in ARCHETYPES:
            props.append({"key": "%s_%s" % (cand, name), "w": w, "h": h, "ids": ids[name],
                          "url": "FILL-ME"})
        p = os.path.join(GEN, "plan_%s.json" % cand)
        json.dump({"wave": "projection2", "candidate": cand, "props": props},
                  open(p, "w"), indent=1)
        print("  plan %s: ids %d..%d" % (cand, ids["stone"][0], ids["rack"][-1]))


# ── the instrument: symmetry, SIGNED shear, depth, and material match ───────────────────────
def assemble(ids, w, h):
    im = Image.new("RGBA", (w * CELL, h * CELL))
    for i, tid in enumerate(ids):
        im.paste(Image.open(ASHLAR % tid).convert("RGBA"), ((i % w) * CELL, (i // w) * CELL))
    return np.asarray(im)


def symmetry(op):
    cols = np.where(op.any(axis=0))[0]
    rows = np.where(op.any(axis=1))[0]
    if not len(cols):
        return 0.0
    box = op[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    m = box[:, ::-1]
    return float((box & m).sum()) / float((box | m).sum() or 1)


def signed_shear(op):
    """Top edge height at the right extreme minus the left, over the width. NEGATIVE means the
    top rises to the LEFT (a left-receding side); POSITIVE rises to the right. Zero is flat."""
    cols = np.where(op.any(axis=0))[0]
    if len(cols) < 4:
        return 0.0
    lo, hi = cols.min(), cols.max()
    span = hi - lo + 1
    a, b = lo + int(span * 0.10), hi - int(span * 0.10)
    tops = []
    for x in range(a, b + 1):
        r = np.where(op[:, x])[0]
        if len(r):
            tops.append(r.min())
    if len(tops) < 4:
        return 0.0
    k = max(2, len(tops) // 5)
    left, right = float(np.mean(tops[:k])), float(np.mean(tops[-k:]))
    return (left - right) / float(span)      # right higher on screen => smaller y => positive


def material_lab(rgba):
    """Mean Lab of the opaque pixels — the material's colour, for the cross-candidate match."""
    a = rgba.astype(float)
    op = a[:, :, 3] > 0
    rgb = a[op][:, :3] / 255.0
    def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = lin(rgb[:, 0]), lin(rgb[:, 1]), lin(rgb[:, 2])
    X = 0.4124 * r + 0.3576 * g + 0.1805 * b
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    Z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    def f(t): return np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16.0 / 116)
    fx, fy, fz = f(X / 0.95047), f(Y), f(Z / 1.08883)
    L, A, B = 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)
    return np.array([L.mean(), A.mean(), B.mean()])


def measure():
    print("OBJECT PROJECTION, ROUND TWO — the instrument (orders; never rules)\n")
    print("  %-6s %-7s %9s %9s %10s   %s" % ("cand", "arch", "symmetry", "shear", "side", "reads"))
    labs = {}
    for cand in CANDIDATES:
        ids = ids_for(cand)
        for name, w, h, _, _ in ARCHETYPES:
            if not all(os.path.exists(ASHLAR % t) for t in ids[name]):
                continue
            a = assemble(ids[name], w, h)
            op = a[:, :, 3] > 0
            s, sh = symmetry(op), signed_shear(op)
            side = "left" if sh < -0.03 else ("right" if sh > 0.03 else "none")
            reads = "2 planes" if (s >= 0.90 and abs(sh) <= 0.06) else "3 planes"
            labs[(cand, name)] = material_lab(a)
            print("  %-6s %-7s %9.3f %+9.3f %10s   %s" % (cand, name, s, sh, side, reads))
    print("\n  MATERIAL MATCH — mean-colour ΔE (CIE76) of each archetype against candidate W."
          "\n  Small is matched; a big number says the material drifted and the comparison is"
          " confounded.\n")
    print("  %-7s " % "arch" + " ".join("%7s" % c for c in CANDIDATES))
    for name, _, _, _, _ in ARCHETYPES:
        row = []
        for cand in CANDIDATES:
            if (cand, name) in labs and ("W", name) in labs:
                row.append("%7.1f" % float(np.linalg.norm(labs[(cand, name)] - labs[("W", name)])))
            else:
                row.append("%7s" % "-")
        print("  %-7s " % name + " ".join(row))
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "scenes":
        write_scenes()
    elif cmd == "plan":
        os.makedirs(GEN, exist_ok=True)
        write_plans()
    elif cmd == "measure":
        return measure()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
