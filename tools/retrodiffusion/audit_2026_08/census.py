#!/usr/bin/env python3
"""THE SEAMLESS CENSUS — does a tile the vendor calls seamless actually lay without a seam?

    The research doc's own warning governs: vendor "seamless" is marketing until baked off.

Two mechanical measures, both declared here before any tile is generated, both value-agnostic,
and both carrying a positive control that plants the defect it exists to catch (bible §13.5,
LOOP-PROCESS §4). Run `--controls` to see them go red.

MEASURE 1 — THE WRAP SEAM
-------------------------
A tile is laid against a copy of itself. The question is whether the join it makes is
distinguishable from the joins inside it.

    wrap_x   = mean |luminance(column 0) - luminance(column W-1)|
    inner_x  = the same difference for every adjacent column pair INSIDE the tile
    SEAM if wrap_x > median(inner_x) + 3 * robust_sigma(inner_x)

Stated in words: **the seam is visible when the wrap join is an OUTLIER against the steps the
material makes on its own.** That is the honest form of the question — a stone floor is full of
edges, and a tile is not un-seamless for having them. What makes a seam is being an edge the
material would not otherwise produce, at a position that repeats.

`robust_sigma` is 1.4826 x the median absolute deviation, floored at 0.5 luminance levels so a
perfectly flat tile does not divide by a vanishing spread. The run reports the margin as well as
the verdict so a borderline is visible as a borderline rather than collapsing to a bit.

    THE CUT WAS REDRAWN BEFORE ANY RD TILE EXISTED, AND THE FIRST DRAW IS RECORDED RATHER THAN
    TIDIED AWAY. The first version of this measure cut at the 90th percentile of the interior
    steps. Its own control suite failed it immediately: `control_seamless` (a periodic field
    that wraps exactly, by construction) and `control_flat` both came back SEAM=True. The
    reason is arithmetic, not tuning — a 32px tile has 31 interior steps, so a wrap step drawn
    from the SAME distribution as the interior sits above the 90th percentile about 10% of the
    time per axis, and the measure ORs two axes. A ~19% false-seam rate on material with no
    seam was baked into the constant.

    This is LOOP-PROCESS §4 doing the job it exists for: the instrument was mis-drawn, the
    plant caught it, and the correction happened with zero real data on disk — so nothing was
    cut to fit (§8). The verbatim first-draw failure is kept in the report.

    ⚠ WHAT THIS CANNOT DO. It measures VALUE continuity across the join. It cannot see a
    STRUCTURAL discontinuity that happens to be value-matched — a bond whose stones line up
    into a continuous grout line exactly at the wrap, for instance, reads clean here and reads
    as a ruled line to the eye (§8.3.1's lattice, on the seam). The eye rules; this orders
    attention. Same relabelling Rafe applied to the ring instrument: MEASURED ERROR IN BOTH
    DIRECTIONS; ORDERS ATTENTION, RULES NOTHING.

MEASURE 2 — THE CENTRE-TO-EDGE VIGNETTE
---------------------------------------
    ratio = mean luminance(centre block) / mean luminance(outer ring)
    VIGNETTE if ratio outside [0.87, 1.15]

This is not a cosmetic check. A vignette is a treatment at a CONSTANT POSITION INSIDE EVERY
TILE, which is bible §8.3.1's lattice in its purest form — *"any treatment applied at a constant
position within a tile becomes a lattice when tiled, whatever it depicts and however well it is
drawn."* Tiled, a centre-bright tile is a grid of spotlights. It is also §6.3: a baked
centre-light is depicted lighting, which the bible forbids outright.

The band is symmetric because both directions are the defect — a dark centre is as much a
lattice as a bright one.

NEITHER MEASURE APPROVES ANYTHING. A pass here is a mechanical floor, not an acceptance; §13.1
holds that only Rafe, in-scene on device, lands an asset, and the blind seat culls before that.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# Declared before the data. Neither constant is tuned after a run — if one is ever changed, the
# change and its reason belong in this docstring and in the report, per LOOP-PROCESS §8.
SEAM_SIGMAS = 3.0        # how far above the interior's own spread a wrap step must sit
SEAM_SIGMA_FLOOR = 0.5   # luminance levels; below this a difference is not visible at 8-bit
VIGNETTE_LO, VIGNETTE_HI = 0.87, 1.15
CENTRE_FRAC = 0.375      # centre block is the middle 3/8 of the tile
RING_PX = 4              # outer ring width in pixels at 32px


def lum(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float64)
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def robust_sigma(v):
    """1.4826 x MAD, floored. Robust because a stone tile's step distribution is not normal —
    a few grout lines are genuine large steps and must not inflate the cut into uselessness."""
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med)))
    return max(1.4826 * mad, SEAM_SIGMA_FLOOR), med


def seam(L):
    """Returns dict with wrap/inner steps per axis and the verdict."""
    out = {}
    for axis, name in ((1, "x"), (0, "y")):
        if axis == 1:
            wrap = float(np.mean(np.abs(L[:, 0] - L[:, -1])))
            inner = np.abs(np.diff(L, axis=1)).mean(axis=0)
        else:
            wrap = float(np.mean(np.abs(L[0, :] - L[-1, :])))
            inner = np.abs(np.diff(L, axis=0)).mean(axis=1)
        sigma, med = robust_sigma(inner)
        cut = med + SEAM_SIGMAS * sigma
        out["wrap_" + name] = round(wrap, 4)
        out["cut_" + name] = round(cut, 4)
        out["sigma_" + name] = round(sigma, 4)
        out["margin_" + name] = round(wrap - cut, 4)
        out["seam_" + name] = bool(wrap > cut)
    out["SEAM"] = bool(out["seam_x"] or out["seam_y"])
    return out


def vignette(L):
    h, w = L.shape
    ch, cw = int(h * CENTRE_FRAC), int(w * CENTRE_FRAC)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    centre = L[y0:y0 + ch, x0:x0 + cw]
    ring = np.concatenate([L[:RING_PX, :].ravel(), L[-RING_PX:, :].ravel(),
                           L[RING_PX:-RING_PX, :RING_PX].ravel(),
                           L[RING_PX:-RING_PX, -RING_PX:].ravel()])
    cm, rm = float(centre.mean()), float(ring.mean())
    ratio = cm / rm if rm else float("inf")
    return {"centre_mean": round(cm, 3), "ring_mean": round(rm, 3),
            "ratio": round(ratio, 4),
            "VIGNETTE": bool(ratio < VIGNETTE_LO or ratio > VIGNETTE_HI)}


def plate(img, n=2):
    """The 2x2 self-tiled plate. §8.3's scale rule: a tile is judged AS LAID, and a contact
    sheet of single tiles cannot pose the question."""
    w, h = img.size
    out = Image.new("RGBA", (w * n, h * n))
    for j in range(n):
        for i in range(n):
            out.paste(img, (i * w, j * h))
    return out


def measure(path, plate_dir=None):
    img = Image.open(path).convert("RGBA")
    L = lum(img)
    r = {"file": os.path.relpath(path, HERE), "size": list(img.size)}
    r.update(seam(L))
    r.update(vignette(L))
    r["PASS"] = not (r["SEAM"] or r["VIGNETTE"])
    if plate_dir:
        os.makedirs(plate_dir, exist_ok=True)
        p = plate(img)
        rel = os.path.join(plate_dir, os.path.basename(path).replace(".png", "_2x2.png"))
        p.resize((p.width * 4, p.height * 4), Image.NEAREST).save(rel)
        r["plate"] = os.path.relpath(rel, HERE)
    return r


# --- positive controls -------------------------------------------------------

def _control_tiles():
    """Four planted tiles. Two carry the defect, two do not, so each measure is shown BOTH
    firing and staying quiet — §4's requirement that a guard which only ever fires is as
    decorative as one that never does."""
    rng = np.random.default_rng(1337)
    t = {}

    # SEAMLESS by construction: a periodic function whose period divides 32, so column 0 and
    # column 31 are genuine neighbours. Grain added at the same amplitude everywhere so the
    # tile has interior structure to compare the wrap against.
    yy, xx = np.mgrid[0:32, 0:32]
    per = 110 + 26 * np.sin(2 * np.pi * xx / 16) + 26 * np.sin(2 * np.pi * yy / 16)
    per = per + rng.normal(0, 4, per.shape)
    t["control_seamless"] = per

    # NOT SEAMLESS: the same field with a hard value step welded along one edge — the shape of a
    # tile whose left and right do not meet.
    ns = per.copy()
    ns[:, -3:] += 70
    t["control_seam"] = ns

    # NOT SEAMLESS, SUBTLY. The redrawn cut is stricter than the first one, so it owes a
    # control proving it did not buy its false-positive rate down by going blind. A 12-level
    # step is a seam a person sees on a phone. If this one stops firing, the measure has been
    # blunted and the constant is wrong in the other direction.
    #
    # THE SIGN IS COMPUTED, NOT ASSUMED, and the first draft of this plant is why. Written as a
    # flat `+= 12` it made the tile MORE seamless: the periodic field's own wrap step is about
    # -10 levels, so +12 very nearly cancelled it and the wrap fell from 8.7 to 5.3. The
    # instrument correctly reported no seam and the control read as a failure of the
    # instrument. §4.1 LAW in miniature — *the plant must carry the defect on the axis the
    # lever claims* — and a plant whose sign is left to chance does not.
    sub = per.copy()
    sign = 1.0 if per[:, -1].mean() >= per[:, 0].mean() else -1.0
    sub[:, -3:] += 12 * sign
    t["control_seam_subtle"] = sub

    # VIGNETTED: a radial falloff on an otherwise seamless field. This is the §8.3.1 lattice
    # defect and it must fire measure 2 while NOT firing measure 1 — the two measures are
    # independent and the control proves it.
    cy, cx = 15.5, 15.5
    rr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    vg = per * (1.0 - 0.42 * (rr / rr.max()))
    t["control_vignette"] = vg

    # FLAT CLONE: no vignette, no seam. The GREEN half of measure 2.
    t["control_flat"] = np.full((32, 32), 118.0) + rng.normal(0, 4, (32, 32))
    return t


def run_controls(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    expect = {"control_seamless":    {"SEAM": False, "VIGNETTE": False},
              "control_seam":        {"SEAM": True,  "VIGNETTE": False},
              "control_seam_subtle": {"SEAM": True,  "VIGNETTE": False},
              "control_vignette":    {"SEAM": False, "VIGNETTE": True},
              "control_flat":        {"SEAM": False, "VIGNETTE": False}}
    rows, ok = [], True
    for name, arr in _control_tiles().items():
        a = np.clip(arr, 0, 255).astype(np.uint8)
        img = Image.fromarray(np.dstack([a, a, a, np.full_like(a, 255)]), "RGBA")
        p = os.path.join(out_dir, name + ".png")
        img.save(p)
        m = measure(p)
        want = expect[name]
        good = all(m[k] == v for k, v in want.items())
        ok = ok and good
        rows.append({"control": name, "expected": want,
                     "got": {"SEAM": m["SEAM"], "VIGNETTE": m["VIGNETTE"]},
                     "ok": good, "detail": m})
        print("  [%s] %-20s want SEAM=%-5s VIG=%-5s | got SEAM=%-5s VIG=%-5s"
              " | wrap_x %6.2f vs cut %6.2f  wrap_y %6.2f vs cut %6.2f  ratio %.3f"
              % ("PASS" if good else "FAIL", name, want["SEAM"], want["VIGNETTE"],
                 m["SEAM"], m["VIGNETTE"], m["wrap_x"], m["cut_x"],
                 m["wrap_y"], m["cut_y"], m["ratio"]))
    print("\n  CONTROL SUITE: %s" % ("PASS" if ok else "FAIL"))
    if ok:
        print("  Both measures fired on the defect they exist to catch and stayed quiet on\n"
              "  material that does not carry it, including a SUBTLE seam. Bible §13.5\n"
              "  satisfied for this instrument before any of its passes are counted.")
    return ok, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--plates", help="write 2x2 plates here")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()

    out = {"seam_sigmas": SEAM_SIGMAS, "seam_sigma_floor": SEAM_SIGMA_FLOOR,
           "vignette_band": [VIGNETTE_LO, VIGNETTE_HI],
           "centre_frac": CENTRE_FRAC, "ring_px": RING_PX}

    if a.controls or not a.files:
        print("SEAMLESS CENSUS — positive controls")
        ok, rows = run_controls(os.path.join(HERE, "census_controls"))
        out["controls"] = {"suite_pass": ok, "cases": rows}
        if not ok:
            if a.json:
                json.dump(out, open(a.json, "w"), indent=1)
            return 1

    files = []
    for f in a.files:
        files.extend(sorted(glob.glob(f)) if any(c in f for c in "*?[") else [f])
    if files:
        print("\nCENSUS — %d tile(s)" % len(files))
        rows = [measure(f, a.plates) for f in files]
        out["census"] = rows
        npass = sum(1 for r in rows if r["PASS"])
        print("  %-44s %-6s %-9s %s" % ("file", "SEAM", "VIGNETTE", "verdict"))
        for r in rows:
            print("  %-44s %-6s %-9s %s" % (r["file"][-44:], r["SEAM"], r["VIGNETTE"],
                                            "PASS" if r["PASS"] else "FAIL"))
        print("\n  %d of %d passed both measures." % (npass, len(rows)))
        out["summary"] = {"n": len(rows), "passed": npass,
                          "seam": sum(1 for r in rows if r["SEAM"]),
                          "vignette": sum(1 for r in rows if r["VIGNETTE"])}

    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
        print("\n-> %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
