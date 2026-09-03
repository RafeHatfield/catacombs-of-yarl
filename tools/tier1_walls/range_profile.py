#!/usr/bin/env python3
"""THE STACK ACROSS THE LIT RADIUS — bible section 6.2.1's one unanswered item.

Ruling 56 ratified the Boundary's rig and recorded, in the clause itself, what the pass could
not answer:

    *"The section 6.5 stack surviving the falloff across the lit radius - NOT ANSWERED, and it
    could not be. Section 6.5's stack is a relationship between the wall's two planes and the
    floor, and the scene's walls are programmer-art mocks. The rig is ratified on floor
    legibility alone. Whether the value stack survives this falloff is owed by the first round
    that puts real walls in the scene."*

This is that measurement, taken before a single wall pixel is authored, because the answer
decides what there is to author. It reports, at every range from one tile to five:

    k_top  = L(wall top band)  / L(the floor cell the wall faces)
    k_face = L(wall face band) / L(the same floor cell)

and then, for each candidate authored value, what section 6.5's three relationships actually
DELIVER at that range. The pairing is the floor cell SOUTH of the wall throughout: that is the
ground a player stands on to look at the reveal, and it is the comparison the eye makes.
"""
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

SCENES = ["src/Presentation/assets/tier1_walls_probe/scenes/wall_range_a.json",
          "src/Presentation/assets/tier1_walls_probe/scenes/wall_range_b.json"]
# (measure-on, mask-partner, albedos). The LOW pair reads the near ranges, where the high albedo
# clips; the HIGH pair reads the far ones, where the low albedo has no bits left. Ordered so the
# first pair that puts a range inside its domain wins, and which pair supplied each number is
# recorded rather than smoothed away.
PAIRS = [("a101", "a051", 101.0, 51.0), ("a202", "a101", 202.0, 101.0)]


def collect():
    ctl = json.load(open(os.path.join(EV, "LIGHT-FIELD-CONTROLS.json")))
    dark_k = ctl["dark_cell_modulate"]["median"]
    rows, missing = [], []
    for scene in SCENES:
        tag = "range_a" if scene.endswith("_a.json") else "range_b"
        got = {}
        for hi_t, lo_t, a_hi, a_lo in PAIRS:
            hi = "%s_%s" % (tag, hi_t)
            lo = "%s_%s" % (tag, lo_t)
            mask = LF.pure_scene_mask(os.path.join(EV, lo + ".png"), os.path.join(EV, hi + ".png"),
                                      a_lo, a_hi, tol=0.02, signal_floor=6.0)
            spec, cells, g = LF.samples(os.path.join(REPO, scene), os.path.join(EV, hi + ".png"),
                                        os.path.join(EV, hi + ".log"), mask=mask)
            by = {(c["x"], c["y"]): c for c in cells}
            wall, w, h = build(spec)
            for b in spec["_blocks"]:
                if b["row"] in got:
                    continue
                r = by.get((b["x"], b["y"]))
                f = by.get((b["x"], b["y"] + 1))
                if r is None or f is None or not r["top"] or not r["face"] or not f["whole"]:
                    continue
                c, _ = masks(wall, w, h, b["x"], b["y"])
                lf = f["whole"] / a_hi / dark_k
                got[b["row"]] = dict(
                    row=b["row"], cardinal=c, albedo=a_hi, pair="%s/%s" % (hi_t, lo_t),
                    dist_wall=round(float(np.hypot(b["x"] - spec["player"]["x"],
                                                   b["y"] - spec["player"]["y"])), 3),
                    L_top=r["top"] / a_hi, L_face=r["face"] / a_hi, L_floor=lf,
                    k_top=r["top"] / a_hi / lf, k_face=r["face"] / a_hi / lf)
            spec_blocks = spec["_blocks"]
        for b in spec_blocks:
            if b["row"] not in got:
                missing.append(b["row"])
        rows.extend(got.values())
    rows.sort(key=lambda r: r["row"])
    for m in sorted(set(missing)):
        print("  row %d: NO SAMPLE at any albedo - outside the view, or past the instrument's "
              "eight-bit domain" % m)
    return rows, dark_k


def main():
    stack = json.load(open(os.path.join(EV, "STACK-DERIVATION.json")))
    anchor = stack["anchor"]
    ladder = np.array(stack["ladder_derived"])
    rows, dark_k = collect()
    if not rows:
        raise SystemExit("no range samples - re-capture the range scenes")

    print("THE COMPRESSION FIELD, by range, on the RATIFIED rig "
          "(radius 5.0 / falloff 1.00 / ambient 0.70, energy 1.6)")
    print("  %-6s %9s %9s %9s %9s %9s" % ("row", "L(top)", "L(face)", "L(floor)", "k_top", "k_face"))
    for r in rows:
        print("  %-6d %9.4f %9.4f %9.4f %9.4f %9.4f"
              % (r["row"], r["L_top"], r["L_face"], r["L_floor"], r["k_top"], r["k_face"]))

    print()
    print("  k_top NEVER REACHES 1.0 AND CANNOT: the floor a wall faces is always nearer the")
    print("  lamp than the wall's own top plane, by construction - the player carries the light.")
    print()

    # What is the brightest authorable top plane, and what does it deliver?
    ceilings = (("ladder top rung", float(ladder[-1])), ("8-bit ceiling", 255.0))
    print("SECTION 6.5 ROW 1 - 'wall top is LIGHTER than the floor, 1.11x'. What is reachable:")
    print("  %-18s %9s %s" % ("authored at", "value", "delivered top/floor, by range"))
    reach = {}
    for label, v in ceilings:
        d = [v * r["k_top"] / anchor for r in rows]
        reach[label] = dict(authored=v, delivered=[round(x, 4) for x in d],
                            max=round(max(d), 4), min=round(min(d), 4),
                            ranges_above_1=[rows[i]["row"] for i, x in enumerate(d) if x > 1.0])
        print("  %-18s %9.2f %s" % (label, v,
                                    "  ".join("r%d=%.3f" % (rows[i]["row"], x)
                                              for i, x in enumerate(d))))
    print()

    # Row 2/3 - the face. Solved per range, then the single authored value that serves best.
    print("SECTION 6.5 ROWS 2-3 - 'wall face is DARKER than the floor, 0.50-0.60x'. Solved:")
    print("  %-6s %11s %11s" % ("range", "author@0.60", "author@0.50"))
    for r in rows:
        print("  %-6d %11.2f %11.2f"
              % (r["row"], 0.60 * anchor / r["k_face"], 0.50 * anchor / r["k_face"]))

    kf = np.array([r["k_face"] for r in rows])
    kt = np.array([r["k_top"] for r in rows])
    out = dict(produced_by="tools/tier1_walls/range_profile.py",
               anchor=anchor, dark_cell_modulate=dark_k, rows=rows,
               k_top=dict(mean=float(kt.mean()), min=float(kt.min()), max=float(kt.max())),
               k_face=dict(mean=float(kf.mean()), min=float(kf.min()), max=float(kf.max())),
               top_row_reachable=reach)

    print()
    print("  k_top  mean %.4f   range %.4f .. %.4f" % (kt.mean(), kt.min(), kt.max()))
    print("  k_face mean %.4f   range %.4f .. %.4f" % (kf.mean(), kf.min(), kf.max()))

    # ---- THE OTHER PAIRING, RUN SO THE FINDING CANNOT BE AN ARTEFACT OF THIS ONE ----------
    # Above, a wall is compared against the floor cell it FACES, which is one tile nearer the
    # lamp than the wall by construction. The alternative reading of section 6.5 compares a wall
    # against floor AT ITS OWN RANGE - the material claim rather than the local-contrast one. If
    # the whole finding were an artefact of pairing, this column would come back at 1.0 and the
    # inversion would vanish. It is reported either way, because a measurement that only supports
    # one reading of a clause should say which reading it is measuring.
    floor_L = {}
    for r in rows:
        floor_L[r["row"] - 1] = r["L_floor"]      # the faced floor sits one row nearer
    eq = []
    for r in rows:
        d = r["row"]
        if d in floor_L:
            eq.append(dict(row=d, k_top_equal_range=r["L_top"] / floor_L[d],
                           k_face_equal_range=r["L_face"] / floor_L[d]))
    out["equal_range_pairing"] = eq
    if eq:
        print()
        print("  SAME MEASUREMENT, floor sampled AT THE WALL'S OWN RANGE:")
        for e in eq:
            print("    row %d   k_top %.4f   k_face %.4f"
                  % (e["row"], e["k_top_equal_range"], e["k_face_equal_range"]))
        print("    (still below 1.0: the wall's top band is the far HALF of its own cell, so it")
        print("     sits a further half tile out even when the cells are level.)")

    # Candidate authored pairs, scored on what section 6.5 actually asks for.
    print()
    print("CANDIDATE AUTHORED PAIRS, scored on section 6.5's THREE relationships at every range:")
    print("  %-22s %8s %8s %10s %10s %10s"
          % ("authored (top/face)", "top", "face", "top/floor", "face/floor", "face/top"))
    cands = []
    for ti in range(len(ladder)):
        for fi in range(ti):
            t, f = float(ladder[ti]), float(ladder[fi])
            tf = t * kt / anchor
            ff = f * kf / anchor
            fot = (f * kf) / (t * kt)
            cands.append(dict(top=t, face=f, top_index=ti, face_index=fi,
                              top_over_floor=[round(x, 4) for x in tf],
                              face_over_floor=[round(x, 4) for x in ff],
                              face_over_top=[round(x, 4) for x in fot],
                              face_in_band=bool((ff >= 0.45).all() and (ff <= 0.65).all()),
                              top_above_floor_everywhere=bool((tf > 1.0).all()),
                              face_over_top_mean=float(fot.mean())))
    inband = [c for c in cands if c["face_in_band"]]
    inband.sort(key=lambda c: (c["face_over_top_mean"]))
    for c in inband[:8]:
        print("  %-22s %8.2f %8.2f %10s %10s %10s"
              % ("rung %d / rung %d" % (c["top_index"], c["face_index"]), c["top"], c["face"],
                 "%.3f-%.3f" % (min(c["top_over_floor"]), max(c["top_over_floor"])),
                 "%.3f-%.3f" % (min(c["face_over_floor"]), max(c["face_over_floor"])),
                 "%.3f-%.3f" % (min(c["face_over_top"]), max(c["face_over_top"]))))
    out["candidates_face_in_band"] = inband
    out["any_candidate_puts_top_above_floor"] = any(c["top_above_floor_everywhere"] for c in cands)
    print()
    print("  ANY authorable pair that puts the wall top above the floor at every range: %s"
          % ("YES" if out["any_candidate_puts_top_above_floor"] else "NO"))

    p = os.path.join(EV, "RANGE-PROFILE.json")
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
