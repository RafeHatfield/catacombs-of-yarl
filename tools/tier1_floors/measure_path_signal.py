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


def bands_many(captures, logs, tile, **kw):
    """Pool several stations into one set of traffic buckets."""
    out = {}
    for c, l in zip(captures, logs):
        for lvl, vs in bands(c, l, tile, **kw).items():
            out.setdefault(lvl, []).extend(vs)
    return out


def bands(capture, log, tile, plant=None, shuffle=False, hue=None, min_illum=0.0):
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
    # THE ORIGIN COMES FROM THE ENGINE, NEVER FROM AN ASSUMPTION OF CENTRING. The camera
    # follows the player; a centred formula was 160px out in x on the standing station and
    # every delivered reading taken through it sampled the wrong tiles.
    ox, oy = MTR.tile_origin(log, tile) or ((W - fw * tile) // 2, (H - fh * tile) // 2)

    # The lit mask comes from the UNPLANTED image, always. Deriving it after the plant lets the
    # plant delete its own darkest tiles from the sample and then take credit for the difference.
    lit = MPF.lum(img) > 60
    # THE POPULATION IS FIXED ON THE UNPLANTED FRAME, all of it. The lit mask was already taken
    # here; the pool filter below was not, and dimming the frame pushed tiles out of the sample
    # entirely — so the exposure control was changing WHICH tiles were measured as well as how
    # bright they were, and reported a leak that was its own doing. One frame decides membership.
    pool_lum = MPF.lum(img)

    if plant is not None:
        # THE PLANT. A lane of known amplitude, painted straight onto the delivered capture at the
        # tiles the field itself calls trodden. Applied to the RGB, not to a luminance copy — the
        # first version darkened a luminance array while the colour arm went on reading the
        # untouched image, so the plant and the measurement were looking at different pictures and
        # the control came back MISSED for a reason that had nothing to do with the floor.
        # THE WHOLE FRAME, not just the lane. This control asks one question — are these
        # readings illumination? — and it must perturb only that. Darkening the trodden tiles
        # alone made them genuinely different from their partners, which a fixed pairing is
        # obliged to report; it looked like a leak and was a badly posed question. Dimming the
        # entire capture changes the light and nothing else, and ΔE must not move.
        img *= (1.0 - plant)
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
            # ================= INSIDE THE LAMP'S POOL, OR NOT AT ALL =================
            #
            # RULED at the gate, overturning Ruling 70's execution: the path signal is keyed to
            # where the player WALKS, and the player carries the lamp. Measuring it across a
            # static scene samples it where its reader never is — the capture that closed the
            # channel had its busiest tiles at 7/255, where the whole nine-rung palette renders
            # into four 8-bit values. That was a true measurement of the wrong population.
            #
            # So a tile is only compared if the lamp actually reaches it. Dark illegibility is
            # accepted by design and is no longer evidence about the floor.
            if float(np.median(pool_lum[y0:y0 + tile, x0:x0 + tile])) < min_illum:
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


OFF_MAX, TRODDEN_MIN = 2, 7


PAIRING = None


def report(bk, label):
    rows = []
    for lvl in sorted(bk):
        vs = bk[lvl]
        rows.append((lvl, len(vs),
                     float(np.mean([x[0] for x in vs])),
                     float(np.mean([x[1] for x in vs])),
                     np.mean([x[2] for x in vs], axis=0),
                     [x[3] for x in vs]))
    # THE BUCKETS ARE A PARAMETER INSIDE THE POOL, and widening the quiet one is a CONSERVATIVE
    # move rather than a convenient one. Restricted to tiles the lamp actually reaches, the
    # traffic field's own dynamic range narrows — a station standing in room A has nothing at
    # level 0-2 inside its pool, because the unwalked ground is also the unlit ground. Comparing
    # level 4 against level 8 is a SMALLER traffic contrast than 0 against 9, so a signal that
    # reads here reads more easily at the extremes.
    quiet = [r for r in rows if r[0] <= OFF_MAX]
    busy = [r for r in rows if r[0] >= TRODDEN_MIN]
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

    # ⚠ THE PAIRING IS FIXED ONCE, ON THE SHIPPED ARM, AND REUSED BY EVERY OTHER ARM.
    #
    # Both controls broke at once when the signal got large, and for a single reason: a plant
    # CHANGES the tiles, and matching-on-luminance then RE-PAIRS them. The lightness plant moved
    # every trodden tile away from its partner, the matcher found different partners, and ΔE fell
    # — reported as "MATCHING LEAKS" when the matcher had actually done its job on a different
    # question. The hue plant was invisible for the mirror-image reason.
    #
    # A control has to perturb ONE thing. Re-deriving the pairing under the plant perturbs two.
    global PAIRING
    if PAIRING is None:
        PAIRING = [min(range(len(q_raw)), key=lambda i: abs(lum1(q_raw[i]) - lum1(bt)))
                   for bt in b_raw]
    pairs = []
    for k, bt in enumerate(b_raw):
        if k >= len(PAIRING) or PAIRING[k] >= len(q_raw):
            continue
        qt = q_raw[PAIRING[k]]
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
    print("  off-route (0-%d)   value %7.2f   roughness %6.3f   relchroma %.4f   over %d tiles"
          % (OFF_MAX, qv, qr, q_rc, sum(r[1] for r in quiet)))
    print("  trodden   (%d-9)   value %7.2f   roughness %6.3f   relchroma %.4f   over %d tiles"
          % (TRODDEN_MIN, bv, br, b_rc, sum(r[1] for r in busy)))
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
    # ================= THE POPULATION IS THE WALK, NOT ONE FRAME =================
    #
    # Several stations pooled, deliberately. One player-centered capture puts a handful of tiles
    # inside the lamp — that is what a lamp is — and a paired design over four tiles has no more
    # power than the scene-wide one it replaced, for the opposite reason. Pooling the stations of
    # a traversal restores the sample WITHOUT leaving the corrected population: every tile in it
    # is still a tile the player is standing near, lit by the lamp the player carries.
    ap.add_argument("--capture", required=True, action="append")
    ap.add_argument("--log", required=True, action="append")
    ap.add_argument("--tile", type=int, default=64)
    ap.add_argument("--plant", type=float, default=0.20,
                    help="absorbed control: darken every trodden tile by this fraction")
    ap.add_argument("--off-max", type=int, default=2, dest="off_max")
    ap.add_argument("--trodden-min", type=int, default=7, dest="trodden_min")
    ap.add_argument("--min-illum", type=float, default=0.0, dest="min_illum",
                    help="only compare tiles whose delivered median luminance reaches this")
    ap.add_argument("--hue", type=float, default=0.15,
                    help="plant: rotate every trodden tile toward green by this fraction")
    a = ap.parse_args()

    global OFF_MAX, TRODDEN_MIN, PAIRING
    OFF_MAX, TRODDEN_MIN = a.off_max, a.trodden_min
    real = report(bands_many(a.capture, a.log, a.tile, min_illum=a.min_illum),
                  "AS SHIPPED — tiles inside the lamp's pool (delivered >= %.0f)" % a.min_illum)
    ctrl = report(bands_many(a.capture, a.log, a.tile, hue=a.hue, min_illum=a.min_illum),
                  "THE PLANT — every trodden tile rotated %.0f%% toward green" % (a.hue * 100))
    # THE SECOND CONTROL, AND IT MUST FAIL TO FIRE. Matching each trodden tile to the off-route
    # tile nearest it in luminance is what removes the lamp — so a plant that changes only
    # lightness has to be invisible here, absorbed by the matching. If darkening every trodden
    # tile by a fifth DID move this number, the pairing would not be doing its job and every
    # reading above would be part illumination.
    absorbed = report(bands_many(a.capture, a.log, a.tile, plant=a.plant, min_illum=a.min_illum),
                      "THE EXPOSURE CONTROL — the whole frame dimmed %.0f%%; a reading that is "
                      "about the floor must not move" % (a.plant * 100))
    # FOUR NULLS, AND THE MEDIAN OF THEM. One flip is a single draw and it can be an unlucky
    # one: flipping this scene puts the "trodden" labels on the room's lit centre and the
    # "off-route" labels down the dark corridor, the worst arrangement the lamp allows. Judging a
    # real result against one adversarial draw is not a control, it is a coin toss the floor has
    # to win. Four rearrangements, median taken.
    nulls = []
    for k in (1, 2, 3, 4):
        try:
            PAIRING = None      # a rearranged field is a different population and pairs itself
            nulls.append(report(bands_many(a.capture, a.log, a.tile, shuffle=k, min_illum=a.min_illum),
                                "NULL %d — the traffic field rearranged, so no label matches "
                                "its floor" % k))
        except SystemExit as e:  # noqa: PERF203
            # A rearrangement can land every busy tile outside the captured frame, leaving
            # nothing to compare. That draw is discarded rather than scored as zero — a null of
            # zero would be a free pass, which is the opposite of what a control is for.
            print("\nNULL %d — discarded: %s" % (k, e))
    # A DRAW THAT SCORED ZERO IS NOT A CLEAN NULL, IT IS NO DRAW. A rearrangement can pair a tile
    # with itself, or leave two tiles matched to 0.00 luminance apart; ΔE then comes back 0.000 and
    # drags the median down, handing the real reading a free pass. That is the opposite of what a
    # control is for, and it is the same mistake as the discarded-draw case one line above wearing
    # a number instead of an exception.
    nulls = [n for n in nulls if n["delta_e"] > 1e-6]
    if len(nulls) < 2:
        raise SystemExit("fewer than two usable null draws — the control cannot be trusted here")
    nde = sorted(n["delta_e"] for n in nulls)
    null = dict(nulls[0])
    null["delta_e"] = round(float(np.median(nde)), 3)
    null["draws"] = nde

    print()
    ok = True
    if abs(absorbed["delta_e"] - real["delta_e"]) < 2.0:
        print("  EXPOSURE HOLDS: dimming the whole frame %.0f%% moved ΔE %.3f -> %.3f. The "
              "reading is about\n                  the floor, not the light on it."
              % (a.plant * 100, real["delta_e"], absorbed["delta_e"]))
    else:
        print("  EXPOSURE LEAKS: dimming the whole frame moved ΔE %.3f -> %.3f, so these readings "
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
    # THE INSTRUMENT'S OWN CONTROLS BIND ITS VERDICT. `ok` carries the plant and the absorbed
    # control; a run where a lightness-only plant moved the number is a run whose readings are
    # part illumination, and printing PASS over that would be reporting a measurement the
    # instrument has just told me not to trust.
    verdict = ok and c1 and (c2 or not null_usable)
    if not ok:
        print("  CONTROLS FAILED — the verdict below is withheld, whatever the numbers say.")
    print("  COMBINED VERDICT: %s%s"
          % ("THE SIGNAL CLEARS THE FLOOR" if verdict
             else ("NOT ADJUDICATED — CONTROLS FAILED" if not ok
                   else "THE SIGNAL IS BELOW THE FLOOR"),
             " — seat to confirm it reads as a path" if (verdict and not null_usable) else ""))

    out = dict(commit=FL.git_commit(),
               captures=[os.path.relpath(c, REPO) for c in a.capture],
               floor=FLOOR, margin=MARGIN, shipped=real, plant=ctrl, null=null,
               null_usable=bool(null_usable), verdict=bool(verdict), absorbed=absorbed)
    p = os.path.join(HERE, "evidence", "PATH-SIGNAL.json")
    json.dump(out, open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
