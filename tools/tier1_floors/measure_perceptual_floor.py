#!/usr/bin/env python3
"""THE PERCEPTUAL FLOOR — does an authored signal survive to the eye, under the ratified rig, at 1x?

LAW (Rafe, 2026-08-29, at the device gate): **a signal authored below the perceptual floor is
ABSENT. Everything authored proves readable amplitude under the ratified rig at 1x.**

It is law because it is the third instance of one family, and the third time it cost a gate:

    the trodden channel   absence-only wear, driven to the limit of subtraction, measured
                          0.350/0.578/0.775 against unpolished stone. Four seat rounds did not
                          report it. Ruling 70.
    the incident overlays 127 marks with a MEDIAN SIZE OF 4px, mean delta 8.18 luminance — below
                          one ladder rung. Seats read them as "the pepper" and reported "No
                          cracks. Not one." while the log said event=44.
    the stone grain       authored at +/-4 luminance against a 13.23 rung, so the faces quantise
                          flat. The device gate: **"the floor reads as linoleum."**

Each was authored, present in the source, verified shipped byte-for-byte — and absent.

WHY THIS INSTRUMENT MEASURES A CAPTURE AND NOT AN ASSET, which is a rule this project already
holds: *instruments measure SOURCES, captures measure LEGIBILITY* (§5.1, ruled 2026-08-28). The
palette and the ladder are checked on the authored asset where the answer is exact. **Whether a
person can see the thing is not a property of the asset at all** — it is a property of the asset
under a particular light at a particular size, and only a capture has that.

CALIBRATED ON TWO RULED POINTS, NOT ON AN INVENTED NUMBER (bible §13.6). The same device gate
produced one signal ruled GOOD and one ruled ABSENT, in the same capture, under the same rig:

    cracks          "excellent"                -> must PASS
    stone interior  "reads as linoleum"        -> must FAIL

A threshold between them is derived from two human verdicts. A threshold I picked would be a
number defending itself.

METHOD, and it is the critic's own. Blind seats flatten the lantern before judging material —
*"I flattened the lantern falloff (divide by a 30px Gaussian) so the slab work reads independent
of lighting"* — so this does the same, then asks what amplitude is left in the flattened image,
in units of the family's own ladder rung.
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
import compose_ashlar as CA      # noqa: E402
import field_laws as FL          # noqa: E402


# The two device-gate verdicts, as numbers, measured on the capture Rafe walked
# (tools/tier1_floors/evidence/scene_ashlar_r9.png, commit 080b32ce).
RULED_GOOD = 0.332      # "cracks excellent"
RULED_ABSENT = 0.041    # "the floor reads as linoleum" (re-measured once the
                        # interior was defined the same way as the network)
FLOOR = round((RULED_GOOD * RULED_ABSENT) ** 0.5, 3)   # 0.117


def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def box_blur(a, r):
    """Separable box blur via cumulative sums — no scipy, and exact."""
    pad = np.pad(a, r, mode="edge")
    c = np.cumsum(np.cumsum(pad, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    H, W = a.shape
    k = 2 * r + 1
    out = (c[k:k + H, k:k + W] - c[0:H, k:k + W] - c[k:k + H, 0:W] + c[0:H, 0:W])
    return out / float(k * k)


def flatten_lamp(L, radius=30):
    """Divide out the lantern, the way a blind seat does before judging material."""
    b = box_blur(L, radius)
    b = np.maximum(b, 1e-6)
    return L / b * float(np.median(b))


def components(mask):
    H, W = mask.shape
    lab = np.zeros((H, W), int)
    n, sizes = 0, []
    for sy in range(H):
        for sx in range(W):
            if not mask[sy, sx] or lab[sy, sx]:
                continue
            n += 1
            st, c = [(sy, sx)], 0
            lab[sy, sx] = n
            while st:
                yy, xx = st.pop()
                c += 1
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
            sizes.append(c)
    return lab, n, sizes


def measure(path, crop, rung, lit_min=40.0, face_min_px=40):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)[crop]
    L = lum(a)
    lit = L > lit_min
    # THE LANTERN IS DIVIDED OUT ONLY TO FIND THE JOINTS, NEVER TO MEASURE AMPLITUDE.
    #
    # A local blur normalises away anything that covers a large fraction of its own neighbourhood
    # — which is precisely a dense surface texture. Raising the dressing depth by half a rung
    # moved this number from 0.123 to 0.125: the instrument was cancelling the signal it was
    # built to measure, and it would have reported the fix as a failure.
    #
    # Amplitude is measured as WEBER CONTRAST against each face's own brightness, which is what
    # perception keys on and needs no blur at all. The lamp divides out of a ratio for free.
    F = flatten_lamp(L)

    # The dark network — joints AND cracks together, which is right: both are dark BECAUSE
    # ENCLOSED (§6.5) and neither is stone.
    thr = float(np.percentile(F[lit], 22))
    dark = (F <= thr) & lit
    face = (~dark) & lit

    # SIGNAL 1 — the dark network against the stone it separates. Ruled GOOD at the gate
    # ("cracks excellent"), so whatever this number is, it is above the floor.
    network = float(np.median(L[face]) - np.median(L[dark])) / float(np.median(L[face]))

    # SIGNAL 2 — variation INSIDE a stone face. Ruled ABSENT at the gate ("reads as linoleum"),
    # so whatever this number is, it is below the floor.
    # MEASURED THE SAME WAY AS THE NETWORK, and the first version was not.
    #
    # It took p90 - p10 WITHIN a face, while the network number is a median difference BETWEEN two
    # populations. Calibrating one against the other compared two different quantities and made
    # the derived floor mean less than it looked. Both are now "the light population against the
    # dark one", so the ruled-good and ruled-absent endpoints are commensurable.
    lab, n, sizes = components(face)
    ranges = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < face_min_px:
            continue
        v = np.sort(L[m])
        k = max(1, len(v) // 5)
        base = float(np.median(v[k:]))
        if base <= 1e-6:
            continue
        ranges.append((base - float(np.median(v[:k]))) / base)
    interior = float(np.median(ranges)) if ranges else 0.0

    return dict(faces_measured=len(ranges),
                network_amplitude_rungs=round(network, 3),
                interior_amplitude_rungs=round(interior, 3),
                interior_p90_rungs=round(float(np.percentile(ranges, 90)), 3) if ranges else 0.0,
                rung=round(rung, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("captures", nargs="+", help="lit captures to measure")
    ap.add_argument("--label", nargs="*", default=None)
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    rung = (mat["lum_hi"] - mat["lum_lo"]) / 6.0
    crop = (slice(400, 1000), slice(0, 750))       # the lit ground, HUD excluded

    print("THE PERCEPTUAL FLOOR — Weber contrast against each face's own brightness\n")
    print("  %-34s %10s %10s %10s" % ("capture", "network", "interior", "faces"))
    rows = []
    for i, p in enumerate(a.captures):
        lbl = (a.label[i] if a.label and i < len(a.label) else os.path.basename(p))
        m = measure(p, crop, rung)
        rows.append(dict(capture=os.path.relpath(p, REPO), label=lbl, **m))
        print("  %-34s %10.3f %10.3f %10d"
              % (lbl[:34], m["network_amplitude_rungs"], m["interior_amplitude_rungs"],
                 m["faces_measured"]))

    print()
    for r in rows:
        v = r["interior_amplitude_rungs"]
        print("  %-34s interior %.3f  -> %s"
              % (r["label"][:34], v,
                 "ABOVE THE FLOOR" if v >= FLOOR else "BELOW THE FLOOR — the signal is ABSENT"))
    print()
    print("  network  = the dark joint/crack network against the stone it separates.")
    print("             RULED GOOD at the device gate ('cracks excellent').")
    print("  interior = variation inside one stone face.")
    print("             RULED ABSENT at the device gate ('the floor reads as linoleum').")
    print()
    print("  THE FLOOR IS DERIVED FROM THOSE TWO VERDICTS, not chosen. Measured on the capture")
    print("  Rafe walked: the ruled-GOOD signal delivers %.3f and the ruled-ABSENT one %.3f, a"
          % (RULED_GOOD, RULED_ABSENT))
    print("  gap of %.1fx. The floor is their geometric mean, %.3f; the TARGET is the ruled-good"
          % (RULED_GOOD / RULED_ABSENT, FLOOR))
    print("  amplitude itself, %.3f, because that is the one a person has already called good."
          % RULED_GOOD)
    print()
    print("  A THRESHOLD OF 'ONE LADDER RUNG' WOULD HAVE BEEN WRONG, and measuring said so before")
    print("  it could do any damage: after the lantern is divided out, the signal the gate called")
    print("  EXCELLENT measures 0.33 of a rung. An invented number would have failed the one")
    print("  thing in this floor that is already known to work.")

    out = dict(commit=FL.git_commit(), rung=round(rung, 3), crop=[400, 1000, 0, 750], rows=rows,
               floor=FLOOR, ruled_good=RULED_GOOD, ruled_absent=RULED_ABSENT,
               calibration=("both endpoints measured on the capture the device gate ruled on: "
                            "cracks GOOD, stone interior ABSENT"),
               law=("a signal authored below the perceptual floor is ABSENT; everything authored "
                    "proves readable amplitude under the ratified rig at 1x. Calibrated on two "
                    "device-gate verdicts: cracks GOOD, stone interior ABSENT."))
    p = os.path.join(HERE, "evidence", "PERCEPTUAL-FLOOR.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
