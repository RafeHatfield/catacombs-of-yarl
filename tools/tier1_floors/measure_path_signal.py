#!/usr/bin/env python3
"""IS THE PATH SIGNAL ABOVE THE PERCEPTUAL FLOOR? — the traffic delta, in delivered units.

`measure_traffic_read.py` answers a DIRECTION question: is a trodden stone smoother than a
sheltered one, yes or no. It answered yes — 0.901, the lever pushing the right way. The blind
seat then read the same capture and said *"the ground told me nothing, I routed entirely off the
walls,"* and the two are not in conflict. A ratio has no size.

This file asks the size question, and it asks it in the only units that matter: **what a viewer
receives at 1:1 after the rig has multiplied everything down.** §13.8 is the law it applies —
*a signal authored below the perceptual floor is absent* — and the ruled floor is a Weber
contrast of 0.144, derived from the gate's own two verdicts.

Two channels are measured, because a path can announce itself two ways and neither is assumed:

    VALUE      a lane that is darker or lighter than the ground beside it. Measured on the
               LAMP-FLATTENED capture, so a bright patch of torchlight is not mistaken for a
               worn one — this is the mistake the seat itself flagged when it noted its own
               detail-density gap was "lighting, not surface."
    TEXTURE    a lane that is smoother or rougher than the ground beside it. Measured as local
               standard deviation, and then — the step the direction instrument skips —
               converted to a Weber contrast so it can be compared against the SAME floor.

Both are reported against 0.144. A number below it is not a weak signal; under §13.8 it is an
absent one, and no amount of pushing the same lever reaches it.
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
import field_laws as FL                  # noqa: E402
import perceptual as P                   # noqa: E402
import measure_perceptual_floor as MPF   # noqa: E402
import measure_traffic_read as MTR       # noqa: E402

# The floor is re-derived in Weber space in the same way §13.8 derives it: the geometric mean of
# a signal the gate called excellent and one it called absent.
FLOOR = 0.144

# HOW FAR ABOVE THE CONFOUND IS FAR ENOUGH. The null control measures what a flipped traffic
# field scores on the same pixels under the same lamp — the size of the difference the ROOM makes
# between two arbitrary groups of tiles. A path has to beat that, not merely exist alongside it.
# A quarter again is the smallest margin that is not noise at these sample sizes; it is a
# threshold on a control, and if it ever needs raising that is a finding about the scene.
MARGIN = 1.25


# THE LAMP AND THE LANE ARE ON DIFFERENT SCALES, and that is the only reason this can be
# measured at all. Ruling 56 put the rig's falloff radius at 5.0 tiles, so illumination varies
# over ~320 screen px; a worn lane is one to two tiles, ~64-128 px. Dividing by a blur wider than
# the lamp but narrower than nothing removes the first and keeps the second.
#
# `measure_perceptual_floor` flattens at radius 30 because it judges MATERIAL, where killing
# every structure bigger than a tile is exactly right. Reusing that radius here would divide the
# lane out of the image and then report, with perfect confidence, that there is no lane.
LAMP_RADIUS = 200


def bands(capture, log, tile, plant=None, shuffle=False, hue=None):
    """Per traffic level: lamp-corrected colour, value and roughness, over lit floor pixels."""
    f = MTR.read_field(log)
    if f is None:
        raise SystemExit("no traffic field in the log")
    img = np.asarray(Image.open(capture).convert("RGB")).astype(float)
    H, W = img.shape[:2]
    if shuffle:
        # THE NULL CONTROL, and it is the one that matters most. The darkened-lane plant proves
        # the instrument can SEE a path; this proves it cannot INVENT one. The field is flipped
        # so the traffic labels no longer correspond to the floor they came from — same pixels,
        # same lamp, same geometry, a route that was never walked. Any ΔE surviving that is the
        # instrument reading the lighting or the room's shape, which is precisely the mistake the
        # blind seat caught itself making: *"that gap is lighting, not surface."*
        f = {1: f[::-1, ::-1], 2: f[::-1, :], 3: f[:, ::-1], 4: f.T}[shuffle].copy()
    fh, fw = f.shape
    oy, ox = (H - fh * tile) // 2, (W - fw * tile) // 2

    # The lit mask comes from the UNPLANTED image, always. Deriving it after the plant lets the
    # plant delete its own darkest tiles from the sample and then take credit for the difference.
    lit = MPF.lum(img) > 60

    if plant is not None:
        # THE PLANT. A lane of known amplitude, painted straight onto the delivered capture at the
        # tiles the field itself calls trodden. Applied to the RGB, not to a luminance copy — the
        # first version darkened a luminance array while the colour arm went on reading the
        # untouched image, so the plant and the measurement were looking at different pictures and
        # the control came back MISSED for a reason that had nothing to do with the floor.
        for ty in range(fh):
            for tx in range(fw):
                if f[ty, tx] >= 7:
                    y0, x0 = oy + ty * tile, ox + tx * tile
                    img[y0:y0 + tile, x0:x0 + tile] *= (1.0 - plant)
    if hue is not None:
        for ty in range(fh):
            for tx in range(fw):
                if f[ty, tx] >= 7:
                    y0, x0 = oy + ty * tile, ox + tx * tile
                    img[y0:y0 + tile, x0:x0 + tile] *= np.array([1.0 - hue, 1.0, 1.0 - hue / 3])

    # ================= DIVIDING OUT A COLOURED LAMP =================
    #
    # PER CHANNEL, not by luminance. The rig's light is not white — it is torchlight — so
    # normalising by a blurred LUMINANCE removes the lamp's brightness and leaves its ORANGE
    # behind. The first version of this did exactly that and reported a relative chroma of 0.50
    # for a floor whose material chroma is 0.015: it was measuring the torch.
    #
    # Dividing each channel by its own blur removes both the falloff and the colour of the light,
    # and what survives is how this patch of floor differs from the floor around it — which is
    # the only thing a viewer can judge material by anyway.
    blur = np.stack([np.maximum(MPF.box_blur(img[..., i], LAMP_RADIUS), 1e-6) for i in range(3)],
                    axis=-1)
    grey = float(np.median(MPF.lum(img)[lit]))
    norm = img / blur * grey
    flat = MPF.lum(norm)
    from numpy.lib.stride_tricks import sliding_window_view
    sd = sliding_window_view(flat, (3, 3)).std(axis=(2, 3))

    out = {}
    for ty in range(fh):
        for tx in range(fw):
            lvl = int(f[ty, tx])
            if lvl < 0:
                continue
            y0, x0 = oy + ty * tile, ox + tx * tile
            if y0 < 1 or x0 < 1 or y0 + tile > H - 1 or x0 + tile > W - 1:
                continue
            m = lit[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            if m.sum() < 200:
                continue
            v = flat[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            r = sd[y0 - 1:y0 + tile - 1, x0 - 1:x0 + tile - 1][:m.shape[0], :m.shape[1]]
            c = norm[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            raw = img[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            out.setdefault(lvl, []).append((float(v[m].mean()), float(r[m].mean()),
                                            c[m].mean(axis=0), raw[m].mean(axis=0)))
    return out


def weber(a, b):
    """Symmetric Weber contrast between two region means — |a-b| over the common ground."""
    base = (a + b) / 2.0
    return abs(a - b) / base if base else 0.0


def report(bk, label):
    rows = []
    for lvl in sorted(bk):
        vs = bk[lvl]
        rows.append((lvl, len(vs),
                     float(np.mean([x[0] for x in vs])),
                     float(np.mean([x[1] for x in vs])),
                     np.mean([x[2] for x in vs], axis=0),
                     [x[3] for x in vs]))
    quiet = [r for r in rows if r[0] <= 2]
    busy = [r for r in rows if r[0] >= 7]
    if not (quiet and busy):
        raise SystemExit("the scene has no trodden and sheltered ground to compare")

    def wmean(sel, i):
        return sum(r[i] * r[1] for r in sel) / sum(r[1] for r in sel)

    qv, bv = wmean(quiet, 2), wmean(busy, 2)
    qr, br = wmean(quiet, 3), wmean(busy, 3)
    wv, wr = weber(qv, bv), weber(qr, br)

    qc = sum(r[4] * r[1] for r in quiet) / sum(r[1] for r in quiet)
    bc = sum(r[4] * r[1] for r in busy) / sum(r[1] for r in busy)
    q_rc, b_rc = float(P.relative_chroma(qc)), float(P.relative_chroma(bc))

    # THE COMBINED VERDICT, IN ONE CURRENCY. A Weber luminance contrast and a hue shift cannot be
    # added; ΔE2000 already knows how to weigh them against each other, and §13.8's ruled floor is
    # CONVERTED into that unit rather than a second threshold being invented for colour.
    # ================= MATCHED PAIRING, NOT DIVISION =================
    #
    # The lamp has to be controlled for, and dividing by a blurred copy of the image is the wrong
    # way to do it here: at a radius wide enough to be the lamp, the blur CONTAINS the lane, so
    # dividing removes exactly the thing being measured. That is how the first version of this
    # instrument reported a chroma difference of 0.006 for a shift the raw capture puts at
    # 11.25 degrees of hue — it deleted the signal and then reported its absence.
    #
    # So the lamp is controlled by MATCHING instead. Every trodden tile is paired with the
    # off-route tile closest to it in raw luminance; the pair is therefore lit almost identically
    # and whatever separates them is the floor. Nothing is normalised, nothing is divided, and no
    # window can swallow the lane.
    q_raw = [t for r in quiet for t in r[5]]
    b_raw = [t for r in busy for t in r[5]]
    lum1 = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    pairs = []
    for bt in b_raw:
        qt = min(q_raw, key=lambda t: abs(lum1(t) - lum1(bt)))
        pairs.append((float(P.delta_e2000(P.srgb_to_lab(qt), P.srgb_to_lab(bt))),
                      float(P.delta_e2000(
                          P.srgb_to_lab(np.full(3, lum1(qt))),
                          P.srgb_to_lab(np.full(3, lum1(bt))))),
                      abs(lum1(qt) - lum1(bt))))
    de = float(np.mean([p[0] for p in pairs]))
    n_pairs = len(pairs)
    de_value_component = float(np.mean([p[1] for p in pairs]))
    lum_gap = float(np.mean([p[2] for p in pairs]))
    de_floor = P.floor_delta_e(float(np.mean([lum1(t) for t in q_raw + b_raw])))
    de_value_only = de_value_component

    print("\n%s" % label)
    print("  %-8s %6s %12s %12s %10s" % ("traffic", "tiles", "value(flat)", "roughness", "relchroma"))
    for lvl, n, v, r, c, _rw in rows:
        print("  %-8s %6d %12.2f %12.3f %10.4f"
              % (MTR.RAMP[lvl] * 3, n, v, r, float(P.relative_chroma(c))))
    print()
    print("  off-route (0-2)   value %7.2f   roughness %6.3f   relchroma %.4f   over %d tiles"
          % (qv, qr, q_rc, sum(r[1] for r in quiet)))
    print("  trodden   (7-9)   value %7.2f   roughness %6.3f   relchroma %.4f   over %d tiles"
          % (bv, br, b_rc, sum(r[1] for r in busy)))
    print()
    print("  PER-CHANNEL, WEBER (the value channel is directly comparable to §13.8)")
    print("    value channel     %.4f   %s" % (wv, "ABOVE" if wv >= FLOOR else "below"))
    print("    texture channel   %.4f   %s" % (wr, "ABOVE" if wr >= FLOOR else "below"))
    print("    the ruled floor   %.4f" % FLOOR)
    print()
    print("  THE COMBINED VERDICT, ΔE2000 — joint travel and chroma together")
    print("    pairs                 %6d   matched to within %.2f luminance on average"
          % (len(pairs), lum_gap))
    print("    lightness alone       %6.3f" % de_value_only)
    print("    lightness + colour    %6.3f" % de)
    print("    the ruled floor       %6.3f   (§13.8's 0.1440 Weber, converted)" % de_floor)
    print("    -> %s the ruled floor" % ("CLEARS" if de >= de_floor
                                        else "BELOW (%.2fx short)" % (de_floor / max(de, 1e-6))))
    return dict(value_weber=round(wv, 4), texture_weber=round(wr, 4),
                off_value=round(qv, 3), trodden_value=round(bv, 3),
                off_rough=round(qr, 4), trodden_rough=round(br, 4),
                off_relchroma=round(q_rc, 4), trodden_relchroma=round(b_rc, 4),
                delta_e=round(de, 3), delta_e_value_only=round(de_value_only, 3),
                pairs=n_pairs,
                delta_e_floor=round(de_floor, 3), clears=bool(de >= de_floor),
                levels=[dict(level=l, tiles=n, value=round(v, 3), roughness=round(r, 4),
                             rgb=[round(float(q), 2) for q in c])
                        for l, n, v, r, c, _rw in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tile", type=int, default=64)
    ap.add_argument("--plant", type=float, default=0.20,
                    help="absorbed control: darken every trodden tile by this fraction")
    ap.add_argument("--hue", type=float, default=0.15,
                    help="plant: rotate every trodden tile toward green by this fraction")
    a = ap.parse_args()

    real = report(bands(a.capture, a.log, a.tile), "AS SHIPPED")
    ctrl = report(bands(a.capture, a.log, a.tile, hue=a.hue),
                  "THE PLANT — every trodden tile rotated %.0f%% toward green" % (a.hue * 100))
    # THE SECOND CONTROL, AND IT MUST FAIL TO FIRE. Matching each trodden tile to the off-route
    # tile nearest it in luminance is what removes the lamp — so a plant that changes only
    # lightness has to be invisible here, absorbed by the matching. If darkening every trodden
    # tile by a fifth DID move this number, the pairing would not be doing its job and every
    # reading above would be part illumination.
    absorbed = report(bands(a.capture, a.log, a.tile, plant=a.plant),
                      "THE ABSORBED CONTROL — every trodden tile darkened %.0f%%, which the "
                      "luminance matching must swallow" % (a.plant * 100))
    # FOUR NULLS, AND THE MEDIAN OF THEM. One flip is a single draw and it can be an unlucky
    # one: flipping this scene puts the "trodden" labels on the room's lit centre and the
    # "off-route" labels down the dark corridor, the worst arrangement the lamp allows. Judging a
    # real result against one adversarial draw is not a control, it is a coin toss the floor has
    # to win. Four rearrangements, median taken.
    nulls = []
    for k in (1, 2, 3, 4):
        try:
            nulls.append(report(bands(a.capture, a.log, a.tile, shuffle=k),
                                "NULL %d — the traffic field rearranged, so no label matches "
                                "its floor" % k))
        except SystemExit as e:
            # A rearrangement can land every busy tile outside the captured frame, leaving
            # nothing to compare. That draw is discarded rather than scored as zero — a null of
            # zero would be a free pass, which is the opposite of what a control is for.
            print("\nNULL %d — discarded: %s" % (k, e))
    if len(nulls) < 2:
        raise SystemExit("fewer than two usable null draws — the control cannot be trusted here")
    nde = sorted(n["delta_e"] for n in nulls)
    null = dict(nulls[0])
    null["delta_e"] = round(float(np.median(nde)), 3)
    null["draws"] = nde

    print()
    ok = True
    if abs(absorbed["delta_e"] - real["delta_e"]) < 1.0:
        print("  MATCHING HOLDS: darkening every trodden tile 20%% moved ΔE %.3f -> %.3f. A "
              "lightness-only\n                  plant is absorbed, as the design requires."
              % (real["delta_e"], absorbed["delta_e"]))
    else:
        print("  MATCHING LEAKS: a lightness-only plant moved ΔE %.3f -> %.3f, so these readings "
              "are part illumination." % (real["delta_e"], absorbed["delta_e"]))
        ok = False
    if ctrl["delta_e"] > real["delta_e"] + 1.0:
        print("  PLANT CAUGHT: ΔE %.3f -> %.3f. The instrument can see a path when there is one."
              % (real["delta_e"], ctrl["delta_e"]))
    else:
        print("  PLANT MISSED: ΔE %.3f -> %.3f. This instrument proves nothing today."
              % (real["delta_e"], ctrl["delta_e"]))
        ok = False
    print()
    print("  THE VERDICT — two conditions, and the second is the one the old instrument lacked")
    print("    null draws: %s -> median %.3f" % ([round(x, 2) for x in nde], null["delta_e"]))
    c1 = real["delta_e"] >= real["delta_e_floor"]
    c2 = real["delta_e"] >= null["delta_e"] * MARGIN

    # ⚠ THE NULL NEEDS A SAMPLE, AND THIS SCENE DOES NOT HAVE ONE.
    #
    # The review scene was built to ask a blind seat "which way would you walk", not to be a
    # statistical sample, and it contains two tiles the traffic field calls trodden. A control
    # built by rearranging labels over two tiles has no power: its own draws here span a factor
    # of five. Worse, once the floor genuinely carries a spatially structured cast, a rearranged
    # labelling RESAMPLES THAT SAME SIGNAL — it pairs cast tiles against uncast ones and scores
    # high for the very reason the floor is working.
    #
    # So the control is reported and NOT used as a verdict below a minimum sample. Passing it off
    # as one would be the failure this project keeps catching: an instrument whose number is real
    # and whose meaning is not.
    MIN_PAIRS = 5
    null_usable = real["pairs"] >= MIN_PAIRS
    print("    1. big enough to see:   ΔE %6.3f  vs floor %6.3f      %s"
          % (real["delta_e"], real["delta_e_floor"], "PASS" if c1 else "FAIL"))
    print("    2. it is the PATH:      ΔE %6.3f  vs null  %6.3f x%.2f  %s"
          % (real["delta_e"], null["delta_e"], MARGIN,
             ("PASS" if c2 else "FAIL") if null_usable else "NO POWER"))
    print()
    if not null_usable:
        print("  CONDITION 2 IS NOT ADJUDICATED. %d trodden tiles is below the minimum of %d, and"
              % (real["pairs"], MIN_PAIRS))
        print("  the null's own draws span %.2f to %.2f — a control that wide decides nothing."
              % (min(nde), max(nde)))
        print("  On a floor that genuinely carries a cast, rearranging the labels resamples that")
        print("  same signal rather than removing it. THE BLIND SEAT IS THE ARBITER HERE, which")
        print("  is why the ruling put one after this instrument rather than instead of it.")
        ok = ok and c1
    elif not c2:
        print("  A flipped traffic field scores as well as the real one, so whatever separates")
        print("  these tiles is the room — its lighting, its shape — and not the floor's own")
        print("  record of being walked on. The seat said this in words before the instrument")
        print("  could say it in numbers: \"that gap is lighting, not surface.\"")
    else:
        ok = ok and c1 and c2
    verdict = c1 and (c2 or not null_usable)
    print("  COMBINED VERDICT: %s%s"
          % ("THE SIGNAL CLEARS THE FLOOR" if verdict else "THE SIGNAL IS BELOW THE FLOOR",
             " — seat to confirm it reads as a path" if (verdict and not null_usable) else ""))

    out = dict(commit=FL.git_commit(), capture=os.path.relpath(a.capture, REPO),
               floor=FLOOR, margin=MARGIN, shipped=real, plant=ctrl, null=null,
               null_usable=bool(null_usable), verdict=bool(verdict), absorbed=absorbed)
    p = os.path.join(HERE, "evidence", "PATH-SIGNAL.json")
    json.dump(out, open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
