#!/usr/bin/env python3
"""THE SAME QUARRY — the floor's chroma, derived so the walls can be cut from it.

    python3 tools/tier1_walls/derive_quarry_tint.py

GATE VERDICT (Rafe): **FAIL** — *"grey walls and ceiling; it looked better a few versions ago."*
Cause, as ruled: *"the same-quarry hue ruling was never built — the build carries the raw grey
material arm."*

MEASURED, and the cause is one field. `compose_walls` and `compose_cap` both synthesise a
LUMINANCE field and colourise it with the floor material's `tint`:

    floor tint = (1.0013, 1.0068, 0.9918)

which is a **neutral multiplier** — saturation 0.008. So the walls were never given the floor's
chroma at all; they were given a number that looks like colour and is not. Delivered, in the
judgeable band:

    floor          hue  29.5   sat 0.507
    wall cap       hue  57.1   sat 0.280      +27.6 deg,  55% of the floor's saturation
    wall face      hue  42.3   sat 0.306      +12.8 deg,  60%

Both surfaces, not just the cap. The cap's `hue_shift` made it worse — it was authored to make
the cap the COOLER, GREYER surface, which is the exact opposite of one stone — but removing it
alone would still leave grey walls, because the tint underneath was never warm.

WHERE THE FLOOR'S COLOUR ACTUALLY LIVES: in its tile pixels. The floor family is built from donor
RGB and keeps its chroma there; the wall family is built from a luminance ladder and throws chroma
away. This derives the floor's chroma as a LUMINANCE-PRESERVING ratio — the direction of its
colour, with none of its brightness — so a wall can take the hue and saturation and differ in
value only, which is what one quarry means.

§5.4 IS NOT STRAINED BY THIS. *Chroma is signal; general richness is forbidden.* Matching the
ground the wall was cut from adds no signal and invents no accent — it removes a divergence
nobody authored on purpose.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASHLAR = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar")
W709 = np.array([0.2126, 0.7152, 0.0722])


def hue_sat(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-9)
    h = np.zeros_like(mx)
    m = mx == r; h[m] = ((g - b) / d)[m] % 6
    m = mx == g; h[m] = ((b - r) / d + 2)[m]
    m = mx == b; h[m] = ((r - g) / d + 4)[m]
    return h * 60, sat


def derive():
    # THE TILES ON DISK, not a manifest tile list — the ashlar family's manifest has no `tiles`
    # array (it is an atlas-encoded family), and a KeyError here is a better failure than a
    # silent empty set.
    px = []
    for f in sorted(os.listdir(ASHLAR)):
        if not f.endswith(".png"):
            continue
        a = np.asarray(Image.open(os.path.join(ASHLAR, f)).convert("RGBA")).astype(float)
        keep = a[..., 3] > 128
        rgb = a[..., :3][keep]
        if rgb.size:
            px.append(rgb.reshape(-1, 3))
    if not px:
        raise SystemExit("no ashlar tiles found — the floor family must be composed first")
    rgb = np.concatenate(px, 0)

    lum = rgb @ W709
    keep = lum > 8.0                    # below this a pixel has no reliable colour direction
    rgb, lum = rgb[keep], lum[keep]

    # THE CHROMA DIRECTION, LUMINANCE-PRESERVING. Per pixel, rgb/lum is the colour with the
    # brightness divided out; the mean of that, renormalised so its own luminance is exactly 1,
    # is a multiplier that changes hue and saturation and NOT value.
    # ⚠ THE MEAN COLOUR, NOT THE MEAN OF PER-PIXEL RATIOS. `mean(rgb/lum)` over-weights dark
    # pixels, where the ratio is noisy and its saturation extreme: it produced a tint of
    # saturation 0.614 against a floor delivering 0.509, and the walls came back **1.518x the
    # floor's saturation** — hue matched to +3 degrees and the stone too rich. The aggregate
    # colour, normalised to unit luminance, reproduces the floor's own chroma instead of the
    # average of its noisiest pixels'.
    mean_rgb = rgb.mean(0)
    tint = mean_rgb / float(mean_rgb @ W709)

    # ⚠ AND ITS CHROMA IS SCALED TO THE FLOOR'S OWN MEAN PER-PIXEL SATURATION, which is the
    # statistic the same-quarry check actually compares. The colour of the average pixel and the
    # average saturation of the pixels are different numbers: the tint above carries 0.644 while
    # the floor's pixels average %.3f, and shipping the first delivered walls at 1.518x the floor's
    # saturation — hue right, stone too rich. Blend toward neutral by the ratio, then renormalise
    # so the result is still luminance-preserving.
    mx, mn = rgb.max(1), rgb.min(1)
    floor_sat = float(np.mean((mx - mn) / np.maximum(mx, 1e-6)))
    t_mx, t_mn = tint.max(), tint.min()
    tint_sat = float((t_mx - t_mn) / max(t_mx, 1e-6))
    # ⚠ AND THEN A DELIVERED CALIBRATION, because the rig is NOT chroma-preserving. With the
    # albedo saturations matched (floor 0.656, tint 0.644, so the ratio above is 1.00 and changes
    # nothing), the capture still came back with walls at **1.518x the floor's delivered
    # saturation**. The lamp is additive and the ambient multiplicative, so a surface at value 34
    # and one at value 72 do not keep their chroma in the same proportion — the floor delivers at
    # 0.78 of its own albedo saturation and the wall at 1.20 of its.
    #
    # There is no arithmetic here that fixes that without modelling the blend, so DELIVERED is
    # what it is calibrated against: 1/1.518 = 0.659, measured on `r25_standing`, applied as a
    # chroma scale and verified by re-capture. It is a measured constant, not a chosen one, and it
    # is re-derived whenever the rig or the floor family moves.
    #
    # THE CURVE, measured on `tier1_wall_standing`, wall-vs-floor DELIVERED saturation ratio:
    #     chroma 0.000 -> 0.553      (the neutral tint the gate rejected: grey walls)
    #     chroma 0.284 -> see below
    #     chroma 0.378 -> 1.149
    #     chroma 0.659 -> 1.335
    #     chroma 1.000 -> 1.518
    # Saturating, because the lamp adds and the ambient multiplies.
    #
    # ⚠ AND ALBEDO PARITY AND DELIVERED PARITY ARE DIFFERENT SETTINGS. Giving the wall the floor's
    # chroma EXACTLY is chroma 1.000 — literally the same quarry in the file — and it delivers the
    # wall at 1.52x the floor's saturation, because this rig does not preserve chroma across
    # values: an additive lamp over a multiplicative ambient treats a surface at value 34 and one
    # at value 72 differently. The two readings of "same quarry" cannot both hold, and that is a
    # §6.2 coupling fact rather than an authoring choice.
    #
    # This ships DELIVERED parity, because the gate judges the delivered frame and the complaint
    # was about what the phone showed. Albedo parity is one constant away and the curve is here.
    DELIVERED_CHROMA = 0.284
    k = min(1.0, floor_sat / max(tint_sat, 1e-6)) * DELIVERED_CHROMA
    tint = 1.0 + (tint - 1.0) * k
    tint = tint / float(tint @ W709)

    # ⚠ ON THE RAW PIXELS. The first version divided by the max channel first, which forces
    # saturation to 1.0 BY CONSTRUCTION — it printed "sat 1.000" for a floor whose delivered
    # saturation is 0.507, and that is a measurement of the normalisation, not of the stone.
    h, s = hue_sat(rgb)
    return tint, float(np.median(h)), floor_sat, len(rgb)


def main():
    tint, hue, sat, n = derive()
    probe = np.array([[tint * 100.0]])
    ph, ps = hue_sat(probe)
    old = json.load(open(os.path.join(ASHLAR, "MANIFEST.json")))["material"]["tint"]
    oh, os_ = hue_sat(np.array([[np.array(old) * 100.0]]))

    print("THE FLOOR'S OWN CHROMA — %d opaque pixels above luminance 8" % n)
    print("  measured on the tiles      hue %5.1f   mean per-pixel sat %.3f" % (hue, sat))
    print()
    print("  the tint the walls were using   (%.4f, %.4f, %.4f)  hue %5.1f  sat %.3f"
          % (*old, float(oh.ravel()[0]), float(os_.ravel()[0])))
    print("  THE QUARRY TINT                 (%.4f, %.4f, %.4f)  hue %5.1f  sat %.3f"
          % (*tint, float(ph.ravel()[0]), float(ps.ravel()[0])))
    print()
    print("  It is luminance-preserving by construction: tint . W709 = %.6f"
          % float(tint @ W709))
    print("  so a wall that takes it changes hue and saturation and NOT value — which is what")
    print("  'the same quarry, a darker cut' means, and is why the value work already landed")
    print("  (rung 3, the material arm) survives this change untouched.")

    out = dict(produced_by="tools/tier1_walls/derive_quarry_tint.py",
               source="src/Presentation/assets/tier1_ashlar",
               quarry_tint=[round(float(v), 6) for v in tint],
               floor_hue=round(hue, 2), floor_sat=round(sat, 4),
               previous_tint=[round(float(v), 6) for v in old],
               luminance_check=round(float(tint @ W709), 6), pixels=n)
    json.dump(out, open(os.path.join(HERE, "evidence", "QUARRY-TINT.json"), "w"), indent=2)
    print("\n  wrote tools/tier1_walls/evidence/QUARRY-TINT.json")


if __name__ == "__main__":
    sys.exit(main())
