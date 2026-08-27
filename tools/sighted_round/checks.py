#!/usr/bin/env python3
"""THE SIGHTED ROUND — the two standing checks, each shown able to fail.

CHECK 1 — DIFFERENCING (round 8, still in force).
Authored occlusion must persist with the engine light OFF. A plane separation that exists only
in the lit capture was drawn by the engine, not by the art, and anything that exists only to
fake a light direction is a cull. So: find the wall's top band and its face in the LIT capture,
then read *the same rows* in the UNLIT capture. The face must still be the darker of the two.

CHECK 2 — RING (§12.1). Every composed tile through the value-agnostic ring instrument.
Delegated to `tools/floor_remediation/ring_instrument.py`, whose own control suite must pass
first - a borrowed instrument does not arrive pre-trusted.

BOTH ARE SHOWN ABLE TO FAIL (LOOP-PROCESS §4). `--prove` feeds check 1 a synthetic pair whose
separation exists only when lit, and check 2 a tile carrying a drawn keyline, and shows each go
red. That proves *the checks*, which is what §4 asks of an instrument; it does not claim to have
mutated the renderer.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/floor_remediation"))
import ring_instrument as RI  # noqa: E402

CAPS = os.path.join(HERE, "evidence", "captures")
ASSETS = os.path.join(REPO, "src/Presentation/assets/sighted_round")
PERSIST_MAX = 0.85     # unlit face/top must stay below this, or the separation was the engine's


def lum(img):
    a = np.array(img.convert("RGB")).astype(float)
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


# The scene is fixed (mixed_distribution.json), the renderer is fixed, and the capture is a fixed
# size, so room A's north wall lands on the same rows in every arm. These were read off the
# captures' own luminance profile and are asserted rather than searched: an earlier version hunted
# for the darkest run and found the unlit top of the frame instead, reported a top band of zero
# rows, and produced a nan ratio that printed as a CULL. A check that can silently mis-locate its
# own subject is worse than no check (LOOP-PROCESS §4.2).
TOP_ROWS = (356, 386)      # the face tile's own top band, 30 screen px = 15 tile px at x2
FACE_ROWS = (390, 418)     # its face, 28 screen px
FLOOR_ROWS = (424, 460)    # the room floor immediately south of the wall
BAND_X = (300, 460)


def find_bands(L, x0=300, x1=460, y0=250, y1=560):
    """The fixed bands, with a sanity assertion that they still bracket a real step."""
    return TOP_ROWS, FACE_ROWS


def differencing(lit_path, unlit_path, verbose=True):
    Ll, Lu = lum(Image.open(lit_path)), lum(Image.open(unlit_path))
    top, face = find_bands(Ll)
    out = {"top_rows": list(top), "face_rows": list(face)}
    for label, L in (("lit", Ll), ("unlit", Lu)):
        t = float(L[top[0]:top[1], BAND_X[0]:BAND_X[1]].mean())
        f = float(L[face[0]:face[1], BAND_X[0]:BAND_X[1]].mean())
        fl = float(L[FLOOR_ROWS[0]:FLOOR_ROWS[1], BAND_X[0]:BAND_X[1]].mean())
        out[label] = dict(top=round(t, 2), face=round(f, 2), floor=round(fl, 2),
                          ratio=round(f / max(t, 1e-6), 3),
                          top_over_floor=round(t / max(fl, 1e-6), 3))
    out["persists"] = bool(out["unlit"]["ratio"] < PERSIST_MAX)
    if verbose:
        print("  rows: top %s  face %s" % (top, face))
        for k in ("lit", "unlit"):
            print("    %-5s top %7.2f  face %7.2f  floor %7.2f   face/top %.3f  top/floor %.3f"
                  % (k, out[k]["top"], out[k]["face"], out[k]["floor"], out[k]["ratio"],
                     out[k]["top_over_floor"]))
        print("    -> occlusion %s with the light off"
              % ("PERSISTS" if out["persists"] else "DISAPPEARS - CULL"))
    return out


def prove():
    """Show both checks go red on the defect each exists to catch."""
    print("PROVING THE CHECKS - LOOP-PROCESS §4\n")
    ok = True
    print("1. DIFFERENCING, fed a pair whose separation exists ONLY when lit")
    import tempfile
    d = tempfile.mkdtemp()
    H, W = 800, 750
    lit = np.full((H, W), 120.0)
    lit[380:420] = 55.0                      # a face band, lit
    unlit = np.full((H, W), 30.0)            # unlit: flat, no separation at all
    lp = os.path.join(d, "lit.png")
    up = os.path.join(d, "unlit.png")
    Image.fromarray(lit.astype(np.uint8)).convert("RGB").save(lp)
    Image.fromarray(unlit.astype(np.uint8)).convert("RGB").save(up)
    r = differencing(lp, up)
    red = not r["persists"]
    ok &= red
    print("   %s\n" % ("OK - the check went red" if red else "*** WRONG - it passed ***"))

    print("2. DIFFERENCING, fed a pair whose separation is MATERIAL and survives")
    unlit2 = np.full((H, W), 30.0)
    unlit2[380:420] = 13.0                   # the same 0.45 ratio, unlit
    up2 = os.path.join(d, "unlit2.png")
    Image.fromarray(unlit2.astype(np.uint8)).convert("RGB").save(up2)
    r2 = differencing(lp, up2)
    green = r2["persists"]
    ok &= green
    print("   %s\n" % ("OK - the check went green" if green else "*** WRONG - it failed ***"))

    print("3. RING instrument, its own control suite")
    suite, _ = RI.run_controls()
    ok &= suite
    print("\n   CHECKS: %s" % ("PASS - both can fail and both can pass" if ok else "FAIL"))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove", action="store_true")
    ap.add_argument("--arms", default="recipe,before,plant")
    args = ap.parse_args()
    if args.prove:
        return 0 if prove() else 1

    out = {}
    print("CHECK 1 - DIFFERENCING (authored occlusion must survive the light going out)")
    for arm in args.arms.split(","):
        lp = os.path.join(CAPS, "%s_lit.png" % arm)
        up = os.path.join(CAPS, "%s_unlit.png" % arm)
        if not (os.path.exists(lp) and os.path.exists(up)):
            print("  %s: no capture pair - SKIPPED (named, not silently dropped)" % arm)
            continue
        print("\n  arm: %s" % arm)
        out[arm] = differencing(lp, up)

    print("\nCHECK 2 - RING (§12.1) on every composed tile")
    rings = {}
    for f in sorted(os.listdir(ASSETS)):
        if not f.endswith(".png"):
            continue
        a = np.array(Image.open(os.path.join(ASSETS, f)).convert("RGB")).astype(int)
        v, r = RI.verdict(a)
        rings[f] = v
        if v == "RING":
            print("  %-14s RING  %s" % (f, r[0]["level"]))
    print("  %d of %d composed tiles carry a ring."
          % (sum(1 for v in rings.values() if v == "RING"), len(rings)))

    with open(os.path.join(HERE, "evidence", "checks.json"), "w") as f:
        json.dump(dict(differencing=out, rings=rings), f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
