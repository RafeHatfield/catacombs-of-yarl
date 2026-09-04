#!/usr/bin/env python3
"""THE CAP — one continuous field, cut into world-positioned windows.

RULED (Rafe, 2026-08-30, at the wall gate). The tops read as dim floor:
  (1) tile-frequency seams visible — a lattice;
  (2) featureless — §8.3.1's mirror, *incident-free is not empty*;
  (3) insufficient separation from the ground.

WHY A FIELD AND NOT A TILE SET
------------------------------
The old cap was coursed masonry: blocks, head joints keyed to the boundaries, and — forced by
§8.3.3's corner theorem — **a bed joint on every tile boundary**. That joint at 32px pitch IS the
lattice the gate saw. It could not be removed while the cap was made of blocks whose values are
addressed per tile.

So the cap stops being blocks. **A wall top in the Boundary is found rock that a wall was built
under, not a course of dressed stone**, and §7.4 says so directly: *the Boundary is mostly found
stone with orc work pinned into it; the deepest regions are made all the way down.* Rock has no
courses, so the theorem has nothing to bite on: there are no stones whose values must agree.

The cap is therefore ONE SEAMLESS FIELD, tiled toroidally, cut into a grid of windows. The engine
picks the window by WORLD POSITION — cell (x, y) draws the window at (x mod N, y mod N) — so two
adjacent cells draw adjacent windows and **the boundary between them is not a boundary at all.**
It is continuous by construction rather than by agreement, which is stronger than edge matching
and costs nothing at run time.

FIELD-SCALE ONLY (the second ruling)
------------------------------------
Because the field is authored whole, everything drawn into it is field-scale by definition:
    * a slow value drift across the whole field, one span, no per-cell anything;
    * cracks that run for several tiles, seeded in field coordinates and clipped by nothing;
    * grain at two scales, continuous across every window.
There is no per-cell decision anywhere in this file. There cannot be — the file never sees a cell.

THE BAR SAYS THE TEXTURE IS THE POINT (`WALL-RECIPE.md` addendum A.1-A.2)
------------------------------------------------------------------------
The bar's cap holds **16.1 distinct values per tile and only 53.8% on its modal value**, and its
own tile boundaries step by 4.44x an interior step — and read fine. It buys continuity with
texture, not with matching. Yarl's seam was visible because Yarl's cap was empty. This does both.
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
sys.path.insert(0, os.path.join(REPO, "tools", "tier1_floors"))
import compose_walls as CW          # noqa: E402
import compose_family as CF         # noqa: E402

T = CW.T
FIELD_TILES = 16                    # 16 x 16 windows = a 512px field; 256 cap tiles
SALT_FIELD = 71001

# The void's three candidates, and its grain. Authored in LEVELS rather than in rungs, because at
# a delivered value of two a fraction of a rung is nothing at all (§13.9).
VOID_LEVELS = (14, 8, 4)
VOID_GRAIN_LEVELS = 1.6

# HOW HARD THE CAP SNAPS TO THE LADDER — and it is DERIVED, not chosen.
#
# §5.6 wants tier-one surfaces on the nine-rung ladder; the bar's cap carries 16.1 distinct values
# in a 32x32 tile (`BAR-CAP.json`). Those pull opposite ways, so the cap sits between them: hard
# snap, then blend the unsnapped field back in. The first value here was 0.72, picked by eye, and
# `cap_not_featureless` caught it at 13.7 levels against the bar's 16.1 — under the thing it was
# written to match. The value below is the sweep's answer (see `--snap-sweep`), and the
# instrument, not the author, decides whether it is enough.
#
# The sweep (levels/window, bar = 16.1):  0.85 -> 9.5   0.72 -> 14.6   0.62 -> 18.4   0.52 -> 21.5
#                                         0.42 -> 25.3  0.30 -> 29.4   0.00 -> 37.3
# ⚠⚠ 1.00 — A HARD SNAP, NO BLEND (RULED, Rafe, 2026-09-03). THE FLOOR CARRIES EIGHT COLOURS.
#
# *"The continuous-tone mottle is the real defect ... an off-palette continuous-tone layer over
# the pixel art (the 'filtered/cement' read all along). Hunt the render stage adding sub-ladder
# intermediate values and quantise it to the palette."*
#
# Hunted, and the render stage is innocent: turning the whole floor-overlay pass off moved the
# delivered count 5763 -> 5402. THE COMPOSER IS THE STAGE. Measured on the assets themselves:
#
#     the ashlar FLOOR, approved, 300 tiles :    8 unique colours
#     this cap, 256 windows                 :  107
#
# Eight. The floor this cap is cut from is strict palette pixel art and the cap was continuous
# tone sitting on top of it. Any soft blend at all puts values BETWEEN rungs, and a value between
# rungs is not in the palette — so the blend goes to zero rather than down a notch.
#
# ⚠ AND THIS BREAKS `cap_not_featureless`, WHICH WANTS 16.1 LEVELS PER WINDOW. That bound came
# off the commercial asset bar, and the bar is a different game with a different palette
# discipline; Yarl's own approved floor uses eight colours in total. The instrument is a
# builder's tool and gates nothing (frame-critic skill §2) — when it and the eye disagree about
# whether a surface should be continuous, the eye wins and the number gets a note, not a retune.
#
# The blend history, kept because it is the shape of the mistake: 0.62 -> 0.80 -> 1.00. The soft
# blend was 38% unsnapped, and unsnapped values sit
# BETWEEN rungs — which is a gradient, and a gradient has no hard edge. With the slab tooling now
# carrying the level count (36 per window against the bar's 16.1) the blend is no longer needed to
# clear `cap_not_featureless`, so it goes back toward the ladder where §5.6 wants it.
#
# 0.62 was the HARDEST snap that clears the bar, and that is the right end to choose from: §5.6
# wants the ladder, so the cap departs from it by the least the bar's own construction allows,
# not by the most the instrument tolerates.
SNAP = 1.00


def wrap_noise(size, cells, rng):
    """Toroidal value noise at `cells` periods across `size`, so every edge wraps."""
    g = rng.normal(size=(cells, cells))
    # bilinear upsample with wraparound
    ys = np.arange(size) * cells / size
    xs = np.arange(size) * cells / size
    y0 = np.floor(ys).astype(int) % cells
    x0 = np.floor(xs).astype(int) % cells
    y1 = (y0 + 1) % cells
    x1 = (x0 + 1) % cells
    fy = (ys - np.floor(ys))[:, None]
    fx = (xs - np.floor(xs))[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    a = g[np.ix_(y0, x0)] * (1 - fx) + g[np.ix_(y0, x1)] * fx
    b = g[np.ix_(y1, x0)] * (1 - fx) + g[np.ix_(y1, x1)] * fx
    out = a * (1 - fy) + b * fy
    return out / max(out.std(), 1e-6)


def field_cracks(size, rng, n, step_rungs, ladder_step):
    """Cracks that run for SEVERAL TILES, seeded in field coordinates and wrapping.

    A crack that stops at a tile edge is a per-cell mark wearing a crack's clothes. These are
    walked in the field's own space and wrapped, so one can leave the right edge and arrive at
    the left — which is what continuity means when the field is a torus.
    """
    out = np.zeros((size, size))
    for i in range(n):
        x, y = rng.integers(0, size), rng.integers(0, size)
        ang = rng.uniform(0, 2 * np.pi)
        length = int(rng.integers(size // 3, size))       # several tiles, always
        for _ in range(length):
            ang += rng.normal(0, 0.16)
            x = (x + np.cos(ang)) % size
            y = (y + np.sin(ang)) % size
            xi, yi = int(x), int(y)
            out[yi, xi] -= step_rungs * ladder_step
            # a crack has a shoulder; one pixel wide is a scratch nobody sees at 1x
            out[yi, (xi + 1) % size] -= 0.45 * step_rungs * ladder_step
    return out


def field_slabs(size, rng, step, spacing=104, offset_rungs=0.55, fracture_rungs=2.2,
                tooling_rungs=0.42, gradient_rungs=0.34):
    """SLAB / FRACTURE ARCHITECTURE at multi-tile scale — RULED (Rafe, 2026-09-03).

    *"Cap architecture approved as a new construction — field-scale slab/fracture structure via
    world-positioned polylines across the cap mass at multi-tile scale (the crack network's
    machinery), crossing tile boundaries; the corner theorem binds constant-position constructions
    and this has none. Courses remain culled on caps; found rock keeps its grain but stops being
    structureless."*

    WHY THIS IS NOT THE THING THE GATE CULLED. §8.3.3's corner theorem binds constructions whose
    features sit at a CONSTANT POSITION in every tile: an edge-matched course set must agree at
    every boundary, so it forces a bed joint onto every boundary, and that joint at 32px pitch was
    the lattice the device gate rejected. This has no constant position at all — the seeds are
    placed in FIELD coordinates on a jittered lattice at ~3 tiles' spacing, wrap toroidally, and
    a slab edge crosses a tile boundary exactly as often as it crosses anything else. There is
    nothing for the theorem to bite on, which is the same argument that licensed found rock.

    WHAT IT DRAWS. The field is partitioned into slabs by nearest-seed distance; each slab takes a
    small value offset, so the mass reads as broken rock with parts rather than as one tone with
    noise on it. Where the two nearest seeds are near-equidistant a FRACTURE runs — the boundary
    between two blocks of stone, drawn as a value break rather than a ruled line.

    Two critic rounds asked for exactly this and were refused a course grid twice:
        r001  "Replace with drawn courses at the frame's own pixel size."
        r002  "fine mottle with no architecture under it. Draw the stone through it."
    The complaint was ARCHITECTURE, not courses. This answers the complaint without the geometry.
    """
    n = max(2, int(round(size / spacing)))
    cell = size / n
    # Jittered lattice, so the slabs are irregular but never clustered into a blank half-field.
    sy, sx = np.mgrid[0:n, 0:n]
    seeds = np.stack([(sy + rng.uniform(0.15, 0.85, (n, n))) * cell,
                      (sx + rng.uniform(0.15, 0.85, (n, n))) * cell], axis=-1).reshape(-1, 2)
    vals = rng.normal(0.0, 1.0, len(seeds))
    vals = (vals - vals.mean()) / max(vals.std(), 1e-6) * offset_rungs * step

    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    best = np.full((size, size), 1e18)
    second = np.full((size, size), 1e18)
    who = np.zeros((size, size), dtype=int)
    for i, (cy, cx) in enumerate(seeds):
        # TOROIDAL distance, so a slab that leaves one edge arrives at the other and the field
        # still tiles. A non-wrapping partition would put a seam down the field's own join.
        dy = np.abs(yy - cy); dy = np.minimum(dy, size - dy)
        dx = np.abs(xx - cx); dx = np.minimum(dx, size - dx)
        d = dy * dy + dx * dx
        closer = d < best
        second = np.where(closer, best, np.minimum(second, d))
        who = np.where(closer, i, who)
        best = np.where(closer, d, best)

    out = vals[who]

    # ── DRESSED STONE, NOT POURED CONCRETE (RULED, Rafe, 2026-09-03) ──────────────────────────
    #
    # *"The slab construction reads as poured concrete — it needs dressed-stone character:
    # visible tooling, grain, and value variation within each slab, not smooth fill between
    # fracture lines."*
    #
    # A flat offset per slab is exactly a smooth fill: the partition gave the mass PARTS, and
    # parts made of nothing still read as cast. Three things go inside each slab, and all three
    # are keyed to the SLAB rather than to the tile or to the pixel:
    #
    #   TOOLING   a directional chisel hatch at the slab's own angle. Per-slab angle is the
    #             lesson from the floor's own critic flip — *"a single 45 degree angle across
    #             every slab in the frame"* — learned here without paying for it twice.
    #   GRADIENT  each slab is lit-and-cut slightly unevenly across its own span, so its interior
    #             has somewhere to go. This is what a flat offset lacked.
    #   GRAIN     a per-slab amplitude jitter on the field grain, so two slabs are not the same
    #             stone at a different value.
    #
    # None of it is per-cell and none of it repeats at the tile pitch: the angle, the gradient
    # axis and the jitter are all indexed by slab id, and slabs are field-scale.
    ang = rng.uniform(0.0, np.pi, len(seeds))
    freq = rng.uniform(0.55, 1.15, len(seeds))
    grad = rng.normal(0.0, 1.0, (len(seeds), 2))
    jit = rng.uniform(0.6, 1.45, len(seeds))

    ca, sa = np.cos(ang)[who], np.sin(ang)[who]
    # Toroidal offset from the owning seed, so a slab that wraps is still one slab.
    dy = yy - seeds[who, 0]; dy -= size * np.round(dy / size)
    dx = xx - seeds[who, 1]; dx -= size * np.round(dx / size)

    # ⚠ HARD-EDGED STROKES, NOT A SINE WAVE — and the first version was a sine wave.
    #
    # It was shaped with a power curve and a comment claiming "a chisel bites; it does not
    # undulate", and it undulated anyway: a continuous function has no 1px edge anywhere in it.
    # Measured on the delivered frame, the build carried 12.5% hard gradients against the last
    # APPROVED frame's 15.6% — the capture really was softer, and the critic said so from the
    # picture alone: *"render it at 1:1 so slab joints are hard 1px edges again."*
    #
    # A chisel groove is a STEP: stone is there, then it is not. So the phase is thresholded
    # rather than shaped, which puts a hard edge at both sides of every cut.
    phase = ((dx * ca + dy * sa) * freq[who] / (2.0 * np.pi)) % 1.0
    tooling = np.where(phase < 0.22, -tooling_rungs * step,
                       np.where(phase < 0.30, -0.45 * tooling_rungs * step, 0.0))

    gradient = ((dx * grad[who, 1] + dy * grad[who, 0]) / max(spacing, 1.0)) \
        * gradient_rungs * step
    out = out + tooling + gradient

    # THE FRACTURE. Near-equidistance between the two nearest seeds is the slab boundary; the
    # width is in field pixels and does not know the tile size, which is the whole point.
    edge = np.sqrt(second) - np.sqrt(best)
    # A fracture between two blocks of stone is a hard line, not a 3px ramp. 1.2 keeps it to
    # roughly a pixel at the field's own scale, which is what "hard 1px edges" means here.
    out -= np.clip(1.0 - edge / 1.2, 0.0, 1.0) * fracture_rungs * step
    return out, jit[who]


def build_field(ladder, tint, top_rung, hue_shift, seed=1337,
                grain_rungs=0.85, drift_rungs=1.10, cracks=7, crack_rungs=1.6, snap=None):
    size = FIELD_TILES * T
    rng = np.random.default_rng(seed + SALT_FIELD)
    step = float(ladder[1] - ladder[0])
    base = float(ladder[top_rung])

    # SLOW DRIFT across the whole field — one span, three periods, so a room-sized view sees a
    # gradient rather than a plateau. The bar's caps drift by sd 7 to 30 luminance within a single
    # map (`WALL-RECIPE.md` A.4); this is authored to sit inside that.
    # ⚠ AND THE DRIFT IS HALVED. It is the term that made the field a cloud: a single 3-cell span
    # carries enormous power in very few frequency bins, and it was drowning every octave above
    # it. It still has to exist — the bar's caps drift by sd 7 to 30 within one map — so it is
    # reduced rather than removed, and `cap_field_scale` still requires it to be there.
    drift = wrap_noise(size, 3, rng) * drift_rungs * step * 0.38

    # GRAIN — AN OCTAVE STACK REACHING STONE SCALE, and the two-octave version it replaces was
    # measured as a cloud.
    #
    # GATE (Rafe): *"the cap texture is arriving as grey cloud, not stone grain."* Quantified on
    # the composed field: **94.4% of its power sat at periods coarser than two tiles and 0.3% at
    # half a tile or finer.** Mean period 428.7px on a 512px field — almost all of the variation
    # was one slow drift.
    #
    # THE TARGET IS THE FLOOR'S OWN STONE, which is the same quarry argument applied to texture
    # rather than to colour: measured over 120 ashlar tiles, **84.8% of their power is at periods
    # of half a tile or finer.** That is what stone looks like at this tile size, and it is
    # derived rather than chosen.
    #
    # 26 cells over 512px is a 20px period; 61 is 8px; 128 is 4px; 256 is 2px. §4.3 is not
    # strained — every octave lands on whole pixels and nothing here is a sub-pixel gradient.
    # ⚠ AND THE FIRST TUNING OF THIS WENT PAST STONE INTO NOISE. Chasing the floor's 84.8%
    # fine-power share, the 2px octave was weighted 1.60 and the frame critic — eyes on the
    # delivered picture — called the result exactly what it was:
    #
    #     "The upper wall masses at x≈60–370 and x≈440–700 are dense SPONGE SPECKLE that reads
    #      as loose gravel, not a surface."
    #
    # That is the failure the frame-critic skill exists to catch, and I walked straight into it:
    # `grain32.py` is a builder's tool and I treated its number as a target. "Masonry frequency"
    # is structure at stone scale, not the maximum high frequency a field can carry — and the
    # metric cannot tell those apart, because a metric never can. The weights below sit between
    # the cloud the gate rejected (49.6%) and the gravel the critic rejected (73.6%).
    # The 2px term is the speckle; 8px and 4px are stone-scale structure. So the fine-power
    # share is bought from STRUCTURE and the pure-noise octave is held down, which is the
    # difference the share alone cannot see.
    octaves = ((26, 0.25), (61, 0.90), (128, 1.05), (256, 0.22))
    grain = sum(wrap_noise(size, c, rng) * a for c, a in octaves)
    grain = grain / max(grain.std(), 1e-6)
    grain = grain * grain_rungs * step

    slabs, slab_jitter = field_slabs(size, rng, step)
    # The grain is modulated PER SLAB, so two slabs are not one stone at two values.
    img = base + drift + grain * slab_jitter
    img = img + slabs
    img = img + field_cracks(size, rng, cracks, crack_rungs, step)

    # QUANTISE ONTO THE LADDER, the way every other tier-one surface does — but softly, so the
    # cap keeps the value count the bar's does. Snapping hard to nine rungs would deliver a cap
    # with nine values against the bar's sixteen, which is the featurelessness this pass exists
    # to remove arriving through the palette instead of through the drawing.
    lad = np.array(ladder)
    idx = np.abs(img[..., None] - lad[None, None, :]).argmin(-1)
    snapped = lad[idx]
    w = SNAP if snap is None else snap
    img = snapped * w + img * (1.0 - w)

    # HUE: the cap is the COOLER, GREYER surface and the floor is the warmer, dirtier one. Measured
    # on the bar at 55.3 degrees of hue separation with the cap 42% less saturated
    # (`WALL-RECIPE.md` A.3), and derived from §8.1 rather than from the bar: the floor is grimed
    # because it is walked and the cap is clean because nothing has ever touched it.
    #
    # ⚠ §5.4 BOUNDS THIS. *Chroma is signal* — a saturated pixel should mean something happened,
    # and general richness is forbidden. What is applied here is a TEMPERATURE difference between
    # two stones, not an accent, and the composer reports its own delivered saturation so the
    # claim is checkable rather than asserted.
    v = np.clip(img, 0, 255)
    rgbf = np.stack([v * tint[0] * (1.0 - hue_shift),
                     v * tint[1] * (1.0 - hue_shift * 0.35),
                     v * tint[2] * (1.0 + hue_shift)], axis=2)
    return np.clip(np.rint(rgbf), 0, 255).astype(np.uint8), img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=sorted(CW.ARMS), default="material")
    # 0.18, AND IT WAS PROBED RATHER THAN PICKED.
    #
    # At 0.055 the DELIVERED hue delta was -1.3 degrees against the bar's 55.3, because a strongly
    # coloured carried lamp fixes the hue ANGLE of everything it lights. Tripling the authored
    # shift moved the angle to -3.7 - still nothing - and moved the SATURATION ratio from 0.857 to
    # 0.560, which is the bar's own measured cap-vs-floor figure of 0.58 arrived at independently.
    #
    # So under this rig **hue angle is not an available axis and saturation is.** And the value
    # separation came with it, free: L(cap, floor) at the standing case went 14.64 -> 19.29 levels,
    # because a less saturated, cooler surface receives less of a warm lamp.
    #
    # §5.4 is SATISFIED by this rather than strained. *Chroma is signal; general richness is
    # forbidden.* Making the cap LESS saturated than the floor spends no chroma at all - it is the
    # opposite of a saturated accent, and it is the direction that costs nothing.
    # ⚠ DEFAULT 0.18 -> 0.0, BY RULING. This knob was authored to make the cap the COOLER,
    # GREYER surface than the floor — the exact opposite of one quarry — and the gate named the
    # result: *"grey walls and ceiling."* The separation the cap needs is VALUE (rung 3, already
    # landed) and not chroma. Kept as a knob rather than deleted so the divergence can be
    # measured again if anyone proposes it, but it ships at zero.
    ap.add_argument("--hue-shift", type=float, default=0.0,
                    help="cool/desaturated split between cap and floor. §5.4 bounds it: a "
                         "material difference, never a saturated event.")
    ap.add_argument("--top-rung", type=int, default=None,
                    help="override the arm's top rung for the cap only")
    ap.add_argument("--snap-sweep", action="store_true",
                    help="report levels/window against the bar for a range of SNAP, and stop")
    a = ap.parse_args()

    floor = json.load(open(os.path.join(REPO,
                      "src/Presentation/assets/tier1_ashlar/MANIFEST.json")))
    mat = dict(floor["material"])
    CF.rehydrate(mat)
    ladder = mat["ladder"]
    top_rung = a.top_rung if a.top_rung is not None else CW.ARMS[a.arm]["top"]

    out_dir = os.path.join(REPO, "src/Presentation/assets/tier1_cap"
                           + ("" if a.arm == "material" else "_" + a.arm))
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png") or f.endswith(".png.import"):
            os.remove(os.path.join(out_dir, f))

    # THE QUARRY TINT (see compose_walls). The cap is the same stone as the ground it sits over.
    import derive_quarry_tint as QT
    tint, _, _, _ = QT.derive()

    if a.snap_sweep:
        # The record for SNAP. Same measure `cap_not_featureless` uses and the same measure
        # `measure_bar_cap.py` took off the bar — per 32x32 window, opaque pixels, rounded.
        print("snap   levels/window   modal share      (bar: 16.1 levels, 53.8%% modal)")
        for w in (0.85, 0.72, 0.62, 0.52, 0.42, 0.30, 0.0):
            _, L = build_field(ladder, tint, top_rung, a.hue_shift, snap=w)
            lv, md = [], []
            for gy in range(FIELD_TILES):
                for gx in range(FIELD_TILES):
                    win = L[gy * T:(gy + 1) * T, gx * T:(gx + 1) * T]
                    lv.append(len(np.unique(np.round(win))))
                    mode = float(np.bincount(np.clip(np.round(win), 0, 255)
                                             .astype(int).ravel()).argmax())
                    md.append(float((np.abs(win - mode) < 1.5).mean()))
            print("%4.2f   %11.1f   %8.1f%%%s"
                  % (w, np.mean(lv), np.mean(md) * 100,
                     "   <- SNAP" if abs(w - SNAP) < 1e-9 else ""))
        return 0

    rgb, lumf = build_field(ladder, tint, top_rung, a.hue_shift)

    tiles, table = [], {}
    base_id = 9200
    # ⚠ 9500, NOT 9300, AND THIS IS THE SECOND ID COLLISION OF THE SESSION.
    #
    # The cap is 256 windows at 9200..9455 and the void is THREE candidates of 256 at
    # void_base + vi*256. At 9300 the first void candidate ran 9300..9555 straight through the
    # cap's own block, and the engine's id->file map takes the last writer — so 156 of the 256 cap
    # windows resolved to VOID files. The walls came back three times too dark and everything else
    # was green: the counts were right, `missing=0` was right, the edge check was right.
    #
    # It was found by measuring the same cells in two captures (93.1 -> 25.8) rather than by
    # anything in the apparatus, which is why `assert_unique_ids` now exists below.
    void_base = 9500
    for gy in range(FIELD_TILES):
        for gx in range(FIELD_TILES):
            win = rgb[gy * T:(gy + 1) * T, gx * T:(gx + 1) * T]
            tid = base_id + gy * FIELD_TILES + gx
            p = os.path.join(out_dir, "tier1_cap_%d.png" % tid)
            Image.fromarray(win).save(p)
            table["%d,%d" % (gx, gy)] = tid
            tiles.append(dict(id=tid, gx=gx, gy=gy, file=os.path.basename(p),
                              mean=round(float(win.mean()), 2),
                              sha256=hashlib.sha256(open(p, "rb").read()).hexdigest()))

    # ── THE VOID: UNLIT ROCK, NOT A FLAT FILL ───────────────────────────────────────────────
    #
    # RULED (Rafe, 2026-08-30): *"void construction: unlit rock with faint grain at ambient, not a
    # flat fill — the seat's zero-variance finding rules out every flat candidate."*
    #
    # The seat found it by measuring: *"exactly one colour, RGB(1,1,2), across 57,000 pixels,
    # standard deviation 0.00 … a flat fill."* A zero-variance region reads as NOTHING WAS DRAWN
    # THERE, which is a different statement from darkness.
    #
    # So the void is the SAME FIELD — same rock, same windows, same world positioning — carried
    # down to ambient. The one thing that cannot simply scale with it is the grain: at a delivered
    # value of two or three, a grain authored as a fraction of a rung quantises to zero and the
    # flat fill returns wearing a texture's name. The void's grain is therefore authored in
    # LEVELS, at the amplitude eight bits can still hold there. §13.9's lesson, applied at the
    # darkest place in the game.
    void_stats = []
    for vi, vbase in enumerate(VOID_LEVELS):
        g = lumf - lumf.mean()
        g = g / max(g.std(), 1e-6) * VOID_GRAIN_LEVELS
        vf = np.clip(vbase + g, 0, 255)
        vrgb = np.clip(np.rint(np.stack([vf * tint[0], vf * tint[1], vf * tint[2] * 1.06],
                                        axis=2)), 0, 255).astype(np.uint8)
        for gy in range(FIELD_TILES):
            for gx in range(FIELD_TILES):
                win = vrgb[gy * T:(gy + 1) * T, gx * T:(gx + 1) * T]
                tid = void_base + vi * 256 + gy * FIELD_TILES + gx
                Image.fromarray(win).save(os.path.join(out_dir, "tier1_cap_%d.png" % tid))
                tiles.append(dict(id=tid, gx=gx, gy=gy, cls="void", candidate=vi,
                                  file="tier1_cap_%d.png" % tid))
        vl = (vrgb.astype(float) * np.array([0.2126, 0.7152, 0.0722])).sum(2)
        void_stats.append(dict(candidate=vi, authored=vbase,
                               sd=round(float(vl.std()), 3),
                               distinct=int(len(np.unique(np.round(vl)))),
                               mean=round(float(vl.mean()), 2)))

    # SELF-REPORTED PROPERTIES, so the claims in the docstring are checkable numbers.
    L = lumf
    seam_h = float(np.abs(L[:, -1] - L[:, 0]).mean())          # the field's own wrap
    inner = float(np.abs(np.diff(L, axis=1)).mean())
    tile_means = [t["mean"] for t in tiles if t.get("cls") != "void"]
    flat = []
    for gy in range(FIELD_TILES):
        for gx in range(FIELD_TILES):
            w = L[gy * T:(gy + 1) * T, gx * T:(gx + 1) * T]
            mode = float(np.bincount(np.clip(np.round(w), 0, 255).astype(int).ravel()).argmax())
            flat.append(float((np.abs(w - mode) < 1.5).mean()))

    man = dict(
        family="boundary_cap_%s_v1" % a.arm,
        arm=a.arm,
        commit=os.popen("git -C %s rev-parse HEAD" % REPO).read().strip(),
        seed=1337, field_tiles=FIELD_TILES, tile=T,
        construction=("ONE seamless toroidal field, cut into %d x %d windows. The engine picks a "
                      "window by WORLD POSITION, so adjacent cells draw adjacent windows and the "
                      "tile boundary is not a boundary. Continuous by construction rather than by "
                      "agreement." % (FIELD_TILES, FIELD_TILES)),
        top_rung=top_rung, top_value=round(float(ladder[top_rung]), 3),
        hue_shift=a.hue_shift,
        quarry_tint=[round(float(v), 6) for v in tint],   # see compose_walls: the gate reads it
        ladder=[round(v, 4) for v in ladder],
        measured=dict(
            wrap_step=round(seam_h, 3), interior_step=round(inner, 3),
            wrap_over_interior=round(seam_h / max(inner, 1e-6), 3),
            distinct_levels=int(len(np.unique(np.round(L)))),
            modal_share_mean=round(float(np.mean(flat)), 4),
            tile_mean_sd=round(float(np.std(tile_means)), 3),
            tile_mean_range=[round(float(min(tile_means)), 2), round(float(max(tile_means)), 2)],
        ),
        void=dict(levels=list(VOID_LEVELS), grain_levels=VOID_GRAIN_LEVELS, stats=void_stats,
                  note=("unlit rock, not a flat fill. Same field, same windows, same world "
                        "positioning; grain authored in LEVELS because a fraction of a rung is "
                        "nothing at a delivered value of two.")),
        void_table={str(vi): {k: void_base + vi * 256 + v - base_id for k, v in table.items()}
                    for vi in range(len(VOID_LEVELS))},
        table=table, tiles=tiles)
    # THE CHECK THAT WOULD HAVE CAUGHT BOTH COLLISIONS. Two id blocks in this session have
    # overlapped — the aged face set into top_h, and the void into the cap — and in both cases
    # every other number stayed green while the wrong pixels were drawn. An id is a name; two
    # things cannot have one.
    ids = [t["id"] for t in tiles]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit("REFUSED: %d duplicate tile ids, e.g. %s. An id is a name and two tiles "
                         "cannot share one - the engine's id->file map takes the last writer and "
                         "the wrong pixels are drawn with every other check still green."
                         % (len(dupes), dupes[:8]))

    json.dump(man, open(os.path.join(out_dir, "MANIFEST.json"), "w"), indent=2)

    m = man["measured"]
    print("cap: arm=%s top=%.2f (rung %d) hue_shift=%.3f" % (a.arm, man["top_value"],
                                                             top_rung, a.hue_shift))
    print("  %d windows from one %dpx field -> %s"
          % (len(tiles), FIELD_TILES * T, os.path.relpath(out_dir, REPO)))
    print("  wrap step %.2f vs interior %.2f  ->  %.3fx   (the bar's drawn boundary: 4.44x)"
          % (m["wrap_step"], m["interior_step"], m["wrap_over_interior"]))
    print("  distinct levels %d   modal share %.1f%%   (the bar: 16.1 per tile, 53.8%%)"
          % (m["distinct_levels"], m["modal_share_mean"] * 100))
    print("  per-window mean sd %.2f  range %.1f..%.1f   (the bar drifts sd 7..30 per map)"
          % (m["tile_mean_sd"], m["tile_mean_range"][0], m["tile_mean_range"][1]))
    print("  THE VOID - unlit rock, not a flat fill:")
    for v in void_stats:
        print("    candidate %d  authored %2d  ->  mean %5.2f  sd %.2f levels  %d distinct values"
              % (v["candidate"], v["authored"], v["mean"], v["sd"], v["distinct"]))


if __name__ == "__main__":
    main()
