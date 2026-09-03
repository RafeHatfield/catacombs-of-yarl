#!/usr/bin/env python3
"""SOLVE THE AUTHORED VALUES BACKWARDS FROM SECTION 6.5's DELIVERED TARGETS.

    delivered_plane / delivered_floor  =  (authored_plane / authored_floor) * (L_plane / L_floor)

so, with the floor's authored anchor known (section 5.7: 101.16, re-derived at consumption by
`derive_stack.py`) and L measured on the ratified rig by `light_field.py`:

    authored_plane = target_ratio * anchor * (L_floor / L_plane)

THE ANSWER IS A PROFILE, NOT A NUMBER, AND THAT IS THE FINDING THIS SCRIPT EXISTS TO REPORT.
L is a field. A wall two tiles from the lamp and a wall four tiles from it do not share a
compression factor, and one asset has to serve both. Bible section 6.2.1 recorded the open
question in those terms - *"the section 6.5 stack surviving the falloff ACROSS the lit radius,
not only at its middle"* - and marked it NOT ANSWERED and owed by the first round that puts real
walls in the scene. This is that round, so what is reported is the whole profile: what each
authored value delivers at every range a wall cell actually occupies.

THE PAIRING RULE. A wall's planes are compared against the floor a player is standing on when
they look at it, which is the floor cell SOUTH of the wall - the cell the reveal faces. Pairing a
north wall against a floor cell somewhere else in the room measures the light field's gradient
and calls it a material ratio.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
sys.path.insert(0, HERE)
import light_field as LF                    # noqa: E402
from mask_census import build, masks        # noqa: E402

SCENE = "src/Presentation/assets/tier0_harness/scenes/tier1_floor_review.json"
TARGETS = {"top": 1.11, "face_light": 0.60, "face_dark": 0.50}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default=SCENE)
    ap.add_argument("--png", default=os.path.join(EV, "probe_a101.png"))
    ap.add_argument("--log", default=os.path.join(EV, "probe_a101.log"))
    ap.add_argument("--pair-lo", default=os.path.join(EV, "probe_a051.png"))
    ap.add_argument("--albedo", type=float, default=101.0)
    ap.add_argument("--albedo-lo", type=float, default=51.0)
    a = ap.parse_args()

    stack = json.load(open(os.path.join(EV, "STACK-DERIVATION.json")))
    anchor = stack["anchor"]
    ladder = np.array(stack["ladder_derived"])

    mask = LF.pure_scene_mask(a.pair_lo, a.png, a.albedo_lo, a.albedo, tol=0.02, signal_floor=6.0)
    spec, rows, g = LF.samples(os.path.join(REPO, a.scene), a.png, a.log, mask=mask)
    by = {(r["x"], r["y"]): r for r in rows}
    wall, w, h = build(spec)

    # THE SOUTH REVEALS. A wall cell showing a front face is one whose south neighbour is floor,
    # and its paired floor sample is that neighbour.
    pairs = []
    for (x, y), r in by.items():
        if not r["wall"]:
            continue
        c, d = masks(wall, w, h, x, y)
        if c & 4:                                   # south is wall - no reveal, no pairing
            continue
        f = by.get((x, y + 1))
        if f is None or f["wall"] or not f["whole"]:
            continue
        if not r["top"] or not r["face"]:
            continue
        pairs.append(dict(x=x, y=y, cardinal=c, dist=r["dist"],
                          L_top=r["top"] / a.albedo,
                          L_face=r["face"] / a.albedo,
                          L_floor=f["whole"] / a.albedo,
                          floor_dark_modulated=True))

    if not pairs:
        raise SystemExit("no south-reveal wall/floor pairs survived the mask - nothing to solve")

    # The renderer multiplies wall-adjacent floor cells by DarkFloorModulate, measured by the
    # DARK-CELL control at 0.928. Every paired floor sample is wall-adjacent by construction, so
    # the constant is divided out - otherwise the floor looks 7.2% darker than it is and every
    # authored wall value comes out 7.2% too dark with it.
    ctl = json.load(open(os.path.join(EV, "LIGHT-FIELD-CONTROLS.json")))
    dark_k = ctl["dark_cell_modulate"]["median"]
    for p in pairs:
        p["L_floor_true"] = p["L_floor"] / dark_k
        p["k_top"] = p["L_top"] / p["L_floor_true"]
        p["k_face"] = p["L_face"] / p["L_floor_true"]

    pairs.sort(key=lambda p: p["dist"])
    print("THE COMPRESSION FIELD at the south reveals, ratified rig, DarkFloorModulate %.4f "
          "divided out" % dark_k)
    print("  %-9s %6s %9s %9s %9s %9s" % ("cell", "range", "L(top)", "L(face)", "k_top", "k_face"))
    for p in pairs:
        print("  (%2d,%2d)   %6.2f %9.4f %9.4f %9.4f %9.4f"
              % (p["x"], p["y"], p["dist"], p["L_top"], p["L_face"], p["k_top"], p["k_face"]))

    kt = np.array([p["k_top"] for p in pairs])
    kf = np.array([p["k_face"] for p in pairs])
    print()
    print("  k_top  (wall top vs the floor it faces)  mean %.4f  range %.4f..%.4f"
          % (kt.mean(), kt.min(), kt.max()))
    print("  k_face (wall face vs the same floor)     mean %.4f  range %.4f..%.4f"
          % (kf.mean(), kf.min(), kf.max()))
    print()

    out = dict(produced_by="tools/tier1_walls/solve_authored_stack.py",
               scene=spec["name"], anchor=anchor, dark_cell_modulate=dark_k,
               pairs=pairs, solutions={})

    print("AUTHORED VALUES, solved against the MEAN compression, then quantised to the ladder:")
    print("  %-12s %7s %9s %9s %9s %9s"
          % ("plane", "target", "k(mean)", "authored", "rung", "delivered"))
    for name, ratio in TARGETS.items():
        k = kt.mean() if name == "top" else kf.mean()
        authored = ratio * anchor / k
        idx = int(np.abs(ladder - authored).argmin())
        rung = float(ladder[idx])
        # What that rung actually delivers, at every range in the scene.
        ks = kt if name == "top" else kf
        delivered = rung * ks / anchor
        out["solutions"][name] = dict(
            target_ratio=ratio, k_mean=float(k), authored_exact=round(float(authored), 2),
            rung=round(rung, 2), rung_index=idx,
            delivered_mean=round(float(delivered.mean()), 4),
            delivered_min=round(float(delivered.min()), 4),
            delivered_max=round(float(delivered.max()), 4))
        print("  %-12s %7.2f %9.4f %9.2f %9.2f %9.4f  (range %.3f..%.3f across the scene)"
              % (name, ratio, k, authored, rung, delivered.mean(),
                 delivered.min(), delivered.max()))

    top = out["solutions"]["top"]
    print()
    print("  face / top AUTHORED : %.4f (light end)   %.4f (dark end)"
          % (out["solutions"]["face_light"]["rung"] / top["rung"],
             out["solutions"]["face_dark"]["rung"] / top["rung"]))
    print("  face / top DELIVERED: %.4f (light end)   %.4f (dark end)"
          % (out["solutions"]["face_light"]["delivered_mean"] / top["delivered_mean"],
             out["solutions"]["face_dark"]["delivered_mean"] / top["delivered_mean"]))
    out["authored_face_over_top"] = {
        k: round(out["solutions"][k]["rung"] / top["rung"], 4)
        for k in ("face_light", "face_dark")}

    # THE ORDERING TEST. Section 6.5's law is not the three numbers, it is that the floor sits
    # BETWEEN the planes. A stack that hits its ratios on average and inverts at the edge of the
    # light has not delivered the law - and inversion, not error, is what section 6.5 calls the
    # whole finding of the wall campaign.
    ok = (out["solutions"]["top"]["delivered_min"] > 1.0
          and out["solutions"]["face_light"]["delivered_max"] < 1.0)
    out["stack_ordered_across_the_scene"] = bool(ok)
    print()
    print("  SECTION 6.5's ORDERING (top > floor > face) holds at EVERY sampled range: %s"
          % ("YES" if ok else "NO - this is a section 6.2 coupling finding, not a tuning task"))

    p = os.path.join(EV, "AUTHORED-STACK.json")
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
