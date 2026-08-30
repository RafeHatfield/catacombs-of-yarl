#!/usr/bin/env python3
"""THE ORC LAYER — a small family of bindings, drawn as overlays and never baked into a segment.

WHY THEY ARE OVERLAYS AND NOT PART OF THE WALL (bible section 8.3.1, LAW)
------------------------------------------------------------------------
    *"Any treatment applied at a constant position within a tile becomes a lattice when tiled,
    whatever it depicts and however well it is drawn."*

A strap drawn into a wall tile is a strap on every wall cell that tile lands on — thirty
identical repairs to a wall nobody repaired thirty times, which is section 1's *nothing is
staged* broken by arithmetic. So the bindings are a separate family, placed per instance from a
world address, at rates that are a property of the WORLD and not of the tile.

WHAT THEY HAVE TO DO (section 7.1, section 7.3 RULED)
-----------------------------------------------------
    *"Show me what holds this together."*
    Orc-made, at the Boundary: **redundant and visible. Lashed twice. Over-built. Repaired on
    top of prior repairs.** Competent but tough, strength only, no interest in appearance —
    *nothing on an orc-made object exists for appearance.*

The failure test is by eye and has a name: **can you see what holds it, and what would fall if
you cut it?** Every element below is required to GRIP something nameable in the wall beneath it,
and the composer refuses to emit one that does not:

    strap    crosses a bed joint and wraps the arris onto the plane above
    pin      is driven INTO a head joint - never into the middle of a block
    cramp    spans two blocks across the joint between them, feet in each
    patch    fills a break in a course, laid over the joint on both sides
    lash     three turns around the arris, over a strap that is already there

The last one is section 7.3's *repaired on top of prior repairs* made literal: a lash is only
ever placed where a strap already is, so the wall carries work laid over older work rather than
five kinds of new hardware sprinkled evenly.

DRAWING RULE (section 6.3, section 12.1)
----------------------------------------
Occlusion under a lip only, one pixel, never a keyline around the element. The composition
spike's round 1 drew a 1px shadow down BOTH sides of every strap and called it symmetric contact
occlusion; the seat read it exactly as section 12.1 warns — *"each sits on top of the brick
inside a hard black keyline ... nothing is held"*, *"stickers laid on wallpaper"*. A dark line on
every side of a small element is a closed keyline, which is a ring around a thing because it is
a thing.

NO COLOUR IS INVENTED. Iron, rope and timber are taken from the family's own ladder, which is
the working palette of bible section 5.6. Nothing here proposes a value.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_walls as CW      # noqa: E402

T = CW.T
BIND_BASE = 9800

# Placement rates. Properties of the WORLD, derived from section 7.3 and not from any statistic
# of the tile set: the Boundary is a line held for four centuries by people who over-build and
# repair on top of repairs, so bindings are COMMON on the reveals a player walks past and rarer
# on wall the player only sees the top of.
# FACE ONLY. There is no `top` rate any more and there must not be one.
#
# RULED (Rafe, at the gate): *"the comb/spike marks on the top band — if they are bindings on
# tops, remove (incident-free tops)."* They were. Identified: `lash` is a vertical iron strap with
# three rope turns across it, which at 32px on a wall top is a comb; `strap` is the plain vertical
# bar, which is the spike; `patch` is four sawn-grain strokes, which is a second comb. Three blind
# seats had already described the first one without knowing what it was — *"a vertical post with
# three horizontal crossbars"*, *"a stake or rack"* — and every one of them said it was holding
# nothing.
#
# §8.3.1 outranks §7.1 here and the ruling says so: an overlay at a hashed position on a plane the
# bible says carries no incident is still incident on that plane. What it costs is real and is not
# hidden: **a wall mass seen from above now shows no orc work at all**, and §7.1's *show me what
# holds this together* is answered only where a reveal is.
RATES = dict(face=0.45)


def ink(ladder, plane_rung):
    """Iron, rope, timber and shadow, taken from the family's ladder RELATIVE TO THE PLANE.

    ⚠ ONE INK SET FOR BOTH PLANES DOES NOT WORK, and round 1's second seat found the consequence
    without being told there were bindings at all:

        *"There is exactly one made object anywhere on the standing structure … It sits in the
        middle of a wall course. It does not span a joint, does not bridge a break, does not
        cross the corner it sits beside. IT IS HOLDING NOTHING."*

    Part of that is range - at four percent luminance nothing reads - and part of it is this: iron
    fixed at rung 1 sits two rungs under a top plane and reads, and sits half a rung under the
    FACE, where §6.5 has already put the stone, and vanishes. A strap you cannot see is not a
    strap that failed to grip; it is a strap that is not there (§13.8).

    So the ink is derived from the plane it lands on. Iron is three rungs under its own plane
    wherever that plane sits, which keeps the ratio - and a ratio is the thing the rig preserves.
    """
    L = list(ladder)
    def at(off):
        return L[max(0, min(len(L) - 1, plane_rung + off))]
    return dict(shadow=at(-4), iron=at(-3), rope=at(-1), timber=at(-2), pale=at(+2))


def _rect(a, x, y, w, h, v):
    a[max(0, y):y + h, max(0, x):x + w] = v


def strap(a, k, face):
    """A vertical iron strap: it starts ON the plane above and runs down the face. The WRAP is
    the grip — a band that stops at the turn is a painted stripe."""
    x = 6 + (k % 3) * 9
    y0 = CW.FACE_TOP_ROW - 4 if face else 4
    y1 = T - 2 if face else T - 4
    _rect(a, x, y0, 3, y1 - y0, ink_v["iron"])
    # Occlusion under the FOOT only. Not down the sides: that is the keyline the spike was culled
    # for, and it also swallows the courses running up to the strap, so nothing can be seen to be
    # crossed.
    _rect(a, x, y1, 3, 1, ink_v["shadow"])
    return [("strap", x, y0, 3, y1 - y0)]


def pin(a, k, face):
    """Driven INTO a joint. A pin in the middle of a block is decoration."""
    x = 4 + (k % 5) * 5
    y = (CW.FACE_TOP_ROW + 7) if face else (8 + (k % 3) * 7)
    _rect(a, x, y, 2, 2, ink_v["iron"])
    _rect(a, x, y + 2, 2, 1, ink_v["shadow"])
    return [("pin", x, y, 2, 2)]


def cramp(a, k, face):
    """Spans two blocks across the joint between them, feet driven into each."""
    x = 5 + (k % 4) * 6
    y = (CW.FACE_TOP_ROW + 5) if face else (10 + (k % 2) * 9)
    _rect(a, x, y, 10, 2, ink_v["iron"])          # the bar
    _rect(a, x, y, 2, 4, ink_v["iron"])           # feet
    _rect(a, x + 8, y, 2, 4, ink_v["iron"])
    _rect(a, x, y + 4, 2, 1, ink_v["shadow"])
    _rect(a, x + 8, y + 4, 2, 1, ink_v["shadow"])
    return [("cramp", x, y, 10, 4)]


def patch(a, k, face):
    """Salvage timber filling a break in a course, laid OVER the joint on both sides so it is
    visibly bridging rather than sitting in a hole cut to fit it."""
    x = 3 + (k % 3) * 8
    y = (CW.FACE_TOP_ROW + 4) if face else (7 + (k % 3) * 6)
    w, hgt = 13, 6
    _rect(a, x, y, w, hgt, ink_v["timber"])
    for i in range(0, w, 3):                       # sawn grain, one value down
        _rect(a, x + i, y, 1, hgt, ink_v["iron"])
    _rect(a, x, y + hgt, w, 1, ink_v["shadow"])
    return [("patch", x, y, w, hgt)]


def lash(a, k, face):
    """Three turns of rope around the arris, OVER a strap that is already there (section 7.3:
    repaired on top of prior repairs)."""
    strap(a, k, face)
    x = 6 + (k % 3) * 9
    y0 = (CW.FACE_TOP_ROW + 2) if face else 9
    for i in range(3):
        _rect(a, x - 3, y0 + i * 3, 9, 2, ink_v["rope"])
    _rect(a, x - 3, y0 + 8, 9, 1, ink_v["shadow"])
    return [("lash", x - 3, y0, 9, 10)]


KINDS = dict(strap=strap, pin=pin, cramp=cramp, patch=patch, lash=lash)
ink_v = {}


def compose(out_dir, arm):
    man = json.load(open(os.path.join(REPO, CW.ASSETS_REL if arm == "material"
                                      else CW.ASSETS_REL + "_" + arm, "MANIFEST.json")))
    ladder = man["ladder"]
    top_rung = man["planes"]["top_rung"]
    face_rung = man["planes"]["face_rung"]
    global ink_v
    tint = np.array(json.load(open(os.path.join(
        REPO, "src/Presentation/assets/tier1_ashlar/MANIFEST.json")))["material"]["tint"])

    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png") or f.endswith(".png.import"):
            os.remove(os.path.join(out_dir, f))

    tiles, n = [], 0
    for kind in sorted(KINDS):
        for face in (True,):
            for k in range(3):
                ink_v.clear()
                ink_v.update(ink(ladder, face_rung if face else top_rung))
                a = np.zeros((T, T), dtype=float)
                alpha = np.zeros((T, T), dtype=float)
                before = a.copy()
                grips = KINDS[kind](a, k, face)
                alpha[a > 0] = 255
                rgb = np.stack([a * tint[0], a * tint[1], a * tint[2]], axis=2)
                img = np.dstack([np.clip(np.rint(rgb), 0, 255), alpha]).astype(np.uint8)
                tid = BIND_BASE + n
                p = os.path.join(out_dir, "tier1_bind_%d.png" % tid)
                Image.fromarray(img, "RGBA").save(p)
                cover = float((alpha > 0).mean())
                tiles.append(dict(id=tid, kind=kind, plane="face" if face else "top",
                                  variant=k, file=os.path.basename(p),
                                  coverage=round(cover, 4),
                                  grips=[g[0] for g in grips],
                                  sha256=hashlib.sha256(open(p, "rb").read()).hexdigest()))
                n += 1

    out = dict(family="boundary_binding_v1", arm=arm,
               commit=os.popen("git -C %s rev-parse HEAD" % REPO).read().strip(),
               rates=RATES,
               rates_note="Properties of the world (section 7.3), never of the tile set. The "
                          "engine planner and this file read the same numbers; neither carries "
                          "its own copy.",
               law="Section 8.3.1 - incident arrives at the INSTANCE level, randomised. Nothing "
                   "here may be baked into a wall segment.",
               ink=dict(face={k: round(float(v), 2) for k, v in ink(ladder, face_rung).items()}),
               tops="NO BINDINGS ON TOP PLANES - ruled at the gate, §8.3.1. See RATES.",
               age_by_implication=(
                   "RECORDED (Rafe, at the gate): the orc repairs ARE age. A strap over a joint "
                   "means the joint moved; a patch means a course broke; a lash over a strap "
                   "means the first repair failed and nobody replaced it (§7.3, repaired on top "
                   "of prior repairs). The wall's history is carried by the binding family as "
                   "much as by the aging pass, and neither is decoration."),
               tiles=tiles)
    mp = os.path.join(out_dir, "MANIFEST.json")
    json.dump(out, open(mp, "w"), indent=2)
    return out, mp


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=sorted(CW.ARMS), default="material")
    a = ap.parse_args()
    out_dir = os.path.join(REPO, "src/Presentation/assets/tier1_bindings"
                           + ("" if a.arm == "material" else "_" + a.arm))
    man, mp = compose(out_dir, a.arm)
    per = {}
    for t in man["tiles"]:
        per.setdefault(t["kind"], []).append(t["coverage"])
    for k in sorted(per):
        print("  %-6s %d variants  coverage %.3f..%.3f"
              % (k, len(per[k]), min(per[k]), max(per[k])))
    print("  %d overlays -> %s" % (len(man["tiles"]), os.path.relpath(out_dir, REPO)))
