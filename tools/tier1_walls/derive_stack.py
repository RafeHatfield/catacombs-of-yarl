#!/usr/bin/env python3
"""STEP 1 OF THE WALL SESSION — the anchor, re-derived at consumption, and section 6.5's stack.

WHY THIS RUNS RATHER THAN READING A NUMBER OFF A MANIFEST
---------------------------------------------------------
Bible section 5.6: *"The ladder is DERIVED, never stored and trusted ... Every consumer of a
written manifest re-derives (compose_family.ladder_for, compose_family.rehydrate); a manifest
written under an older rule cannot silently keep it."*  The landed floor's MANIFEST.json carries
a `ladder` key and a `lum_median`, and both are snapshots. This script takes `lum_lo`/`lum_hi`
- the measurement - and re-applies the rule.

Bible section 5.7 (LAW): *"A median may not be used as an anchor ... Any value another clause
takes ratios against must be shown stable across at least two field sizes, and the statistic
must be area-weighted."*  So the anchor here is the AREA-WEIGHTED MEAN of the assembled field,
including its joints, measured at two field sizes, and the spread between them is reported
rather than assumed.

WHAT IT EMITS
-------------
The three rows of section 6.5's stack as DELIVERED targets, their nearest rungs on the derived
ladder, and the authored values those rungs imply. It does NOT solve the engine's compression -
that is measured in the lit scene by `measure_delivered_stack.py`, because a compression factor
read off anything but this rig is a number with a fuse in it (section 6.2's coupling flag).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "tier1_floors"))

import compose_ashlar as CA          # noqa: E402
import compose_family as CF          # noqa: E402
import field_ashlar as FA            # noqa: E402

# Section 6.5's ruled stack, floor-relative. Targets carrying section 5's PLACEHOLDER status,
# not constants - the bible says so in the clause itself.
STACK = (("wall top", 1.11), ("floor", 1.00),
         ("wall face (0.60, light end)", 0.60), ("wall face (0.50, dark end)", 0.50))

FIELDS = (12, 16)
SEED = 1337


def anchor(mat, n, seed=SEED):
    """Area-weighted mean luminance of the assembled floor, joints included (section 5.7)."""
    img, joints, _, cracks, dress = FA.assemble(n, n, seed, mat, None)
    lum = np.asarray(img).astype(float)[..., 0] / mat["tint"][0]
    return float(lum.mean()), float(np.median(lum)), lum


def main():
    man_path = os.path.join(CA.ASSETS, "MANIFEST.json")
    man = json.load(open(man_path))
    mat = man["material"]

    stored = list(mat.get("ladder", []))
    CF.rehydrate(mat)                       # section 5.6: derive, never trust
    ladder = np.array(mat["ladder"])

    out = {
        "produced_by": "tools/tier1_walls/derive_stack.py",
        "floor_manifest": os.path.relpath(man_path, REPO),
        "floor_family": man["family"],
        "floor_commit": man["commit"],
        "ladder_stored": [round(v, 3) for v in stored],
        "ladder_derived": [round(v, 3) for v in ladder],
        "ladder_agrees_with_stored": [round(v, 6) for v in stored] == [round(v, 6) for v in ladder],
        "ladder_step": round(float(ladder[1] - ladder[0]), 4),
        "fields": {},
    }

    print("THE LADDER, re-derived from lum_lo=%.3f lum_hi=%.3f under the ruled rule"
          % (mat["lum_lo"], mat["lum_hi"]))
    print("  %s" % [round(v, 2) for v in ladder])
    print("  stored ladder agrees: %s" % out["ladder_agrees_with_stored"])
    print()

    means, medians = [], []
    for n in FIELDS:
        m, med, _ = anchor(mat, n)
        means.append(m)
        medians.append(med)
        out["fields"]["%dx%d" % (n, n)] = {"area_weighted_mean": round(m, 3),
                                           "median": round(med, 3)}
        print("  field %2dx%-2d   area-weighted mean %7.3f    median %7.3f" % (n, n, m, med))

    spread_mean = abs(means[0] - means[1]) / max(means) * 100.0
    spread_med = abs(medians[0] - medians[1]) / max(medians) * 100.0
    anchor_v = means[FIELDS.index(16)]
    out["anchor"] = round(anchor_v, 3)
    out["mean_spread_pct"] = round(spread_mean, 3)
    out["median_spread_pct"] = round(spread_med, 3)
    print()
    print("  mean   spread across field sizes: %.2f%%   <- the statistic section 5.7 requires"
          % spread_mean)
    print("  median spread across field sizes: %.2f%%   <- the statistic section 5.7 forbids"
          % spread_med)
    print()
    print("  THE ANCHOR (16x16, area-weighted mean): %.2f" % anchor_v)
    print("  bible section 5.7 records 101.16. delta %+.2f" % (anchor_v - 101.16))
    print()

    print("SECTION 6.5's STACK against this anchor - DELIVERED targets, not authored values:")
    rows = []
    for name, ratio in STACK:
        v = anchor_v * ratio
        idx = int(np.abs(ladder - v).argmin())
        rung = float(ladder[idx])
        inside = ladder[0] - 1e-6 <= v <= ladder[-1] + 1e-6
        rows.append({"plane": name, "ratio": ratio, "target": round(v, 2),
                     "nearest_rung": round(rung, 2), "rung_index": idx,
                     "on_ladder": bool(inside),
                     "rung_error_pct": round((rung - v) / v * 100.0, 2)})
        print("  %-28s %5.2f x  ->  %7.2f   nearest rung %7.2f (#%d, %+.1f%%)   %s"
              % (name, ratio, v, rung, idx, (rung - v) / v * 100.0,
                 "" if inside else "*** OFF THE LADDER ***"))
    out["stack"] = rows

    top = [r for r in rows if r["plane"].startswith("wall top")][0]
    faces = [r for r in rows if r["plane"].startswith("wall face")]
    print()
    print("  face / top, DELIVERED, at the two ends of section 6.5's band:")
    for f in faces:
        print("    %-28s  %.3f" % (f["plane"], f["target"] / top["target"]))
    out["delivered_face_over_top"] = {f["plane"]: round(f["target"] / top["target"], 4)
                                      for f in faces}

    ev = os.path.join(HERE, "evidence", "STACK-DERIVATION.json")
    json.dump(out, open(ev, "w"), indent=2)
    print()
    print("  wrote %s" % os.path.relpath(ev, REPO))


if __name__ == "__main__":
    main()
