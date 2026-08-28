#!/usr/bin/env python3
"""FIELD LAWS — the §8.3 / §8.3.1 / §12.1 tests, run on a tile AS LAID.

WHY THIS EXISTS AND WHY IT COULD NOT BE A TUNING OF `ring_instrument.py`
-----------------------------------------------------------------------
Bible §12.1, RULED 2026-08-27 at the gate:

    A ring is judged AS LAID. A single tile — and a contact sheet of single tiles — cannot
    answer this clause. ... it is why the ring instrument's limit is STRUCTURAL rather than a
    tuning failure: it reads one 32x32 tile, so the evidence is not in its input at any
    threshold.

And §8.3's scale rule, stated the same way from the other end: *the property lives at field
scale and does not exist at tile scale.*

So this is not a better threshold. It is a different **input**: every test here runs on the
3x3 tiling of the candidate, where the centre cell has neighbours to continue into. That one
change is the whole design, and it is what lets a single mechanical test tell apart the two
things §8.3.1's mirror clause says must be told apart:

    a property of the material  a joint between two stones   — RUNS OFF THE EDGE, joins its
                                                               copy next door, forms one
                                                               component spanning cells
    a thing that happened to it a crack through one stone    — TERMINATES INSIDE THE CELL,
                                                               forms a component contained
                                                               in one cell, and therefore
                                                               appears at the SAME OFFSET in
                                                               every cell of the field

§12.1 states that discriminator in one sentence — *the test that separates a ring from a joint
is whether it continues into the neighbour* — and §8.3.1 generalises it past rings to anything:
*the test is not what is it, it is where does it sit, and does it sit there every time.*

`ring_instrument.py` IS NOT REPLACED AND NOT TUNED. It runs first and unchanged, as the keyline
screen it has always been; its constants are not touched by this session. This module is a
second, independent screen answering a question that one is structurally unable to reach.

WHAT IS INSTRUMENTED HERE, AND WHAT IS DELIBERATELY NOT
------------------------------------------------------
Every test below is GEOMETRY: connected components, containment, edge continuity, periodicity.
None of them scores a register clause. §13.4 is LOCKED and it is the most important process
clause in the bible — *there will be no dread score and no staging detector*, and 'nothing is
staged', 'the art plays it straight' and 'nothing is ruined, things are used up' have NO
INSTRUMENT here and are carried at the human gate. What makes §8.3.1 instrumentable when its
neighbours are not is that it was RULED as a geometric property in its own text: a treatment at
a constant position within a tile. That is a measurable fact about pixels. Whether the result is
any good is not, and this module never says.

THE FOUR TESTS
--------------
    incident   a component CONTAINED in one cell, big enough and contrasty enough to be a
               thing rather than grain. §8.3: the incident that becomes a motif when tiled.
    frame      a contained component that ENCLOSES interior — C-GAB's measured failure, the
               'frame at field scale' the gate ruled and the tile-scale instrument could not
               see. §12.1, §5.5.
    seam       the tile does not meet itself at its own edges, so the field carries a
               discontinuity at every cell boundary. This is a lattice at 32px pitch that no
               amount of good drawing inside the tile removes, and it is a candidate
               explanation for a seat's verbatim cull — 'the eye locks onto a 32-unit lattice
               within one screen'.
    grid       continuing structure whose positions form an exact arithmetic progression.
               §8.3.1's own culled case, ported from wall tops to floors so it is refused by
               measurement rather than earned a third time.

THRESHOLDS, AND AN HONEST NOTE ON WHERE THEY COME FROM
------------------------------------------------------
§13.6 LOCKED: *where a constant must be calibrated, derive it from the corpus already accepted,
never from the work seeking acceptance.* **There is no accepted floor corpus.** This session is
the first landing gate the project has ever run, so the clause's preferred source does not
exist yet, and saying so is the correct output rather than quietly calibrating on the
candidates.

So the constants below are derived from GEOMETRY AND THE REFERENCE DEVICE, not from any
candidate, and each states its derivation. They are then proven against PLANTED defects
(`run_controls`), which is the requirement that actually binds: §13.5 / LOOP-PROCESS §4, *no
instrument's pass counts until it has demonstrated it can fail.*
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/floor_remediation"))
import ring_instrument as RI      # noqa: E402

T = 32                            # Yarl's cell size. §4.3 PLACEHOLDER as to derivation; RULED as
                                  # as to value. Every function takes `t` so the SAME instrument
                                  # can read the 48px asset bar — §13.6 calibration is only
                                  # possible if the accepted corpus is inside the input domain.

# --- criterion 1: an incident is a CONTAINED component that is a thing, not grain -------------
MIN_INCIDENT_FRAC = 12.0 / (32 * 32)      # 0.0117 of the tile — see below
# Derivation, from the reference device rather than from any tile. The harness runs 32px native
# at x2 (harness_config.yaml, RULED 2026-08-25), so one native pixel is 2 device pixels. A
# 12-pixel component on a 32px tile is ~3.5x3.5 native, ~7x7 device px — about the size at which
# §12's 'names itself at 1x' starts to apply to a mark at all. Below it the eye reads grain,
# which §8.3.1's mirror clause positively requires the material to have.
#
# CARRIED AS A FRACTION, not as 12 px, and that correction is worth its line. Stated absolutely,
# the same constant is 1.17% of Yarl's 32px tile and 0.52% of the bar's 48px one — so the corpus
# being used to check the threshold was being held to less than half the strictness of the work
# being checked. A fraction is the only form of this number that means the same thing on both.
#
# CORROBORATED, NOT SET, BY THE ACCEPTED CORPUS — `calibrate_against_bar.py`, 29 floor tiles
# across the asset bar's six shipped example maps, 431 laid floor cells:
#
#     55.2% of the floor cells those maps actually lay carry ZERO contained components.
#     The cell-weighted p90 of the largest contained component is 0.046 of the tile.
#
# So a strict threshold is ACHIEVABLE rather than utopian: more than half of a shipped,
# commercial floor set already passes at 12 px equivalent (12/1024 = 0.012 of a tile).
#
# ⚠ AND IT IS STRICTER THAN THE BAR, DELIBERATELY. About 40% of the bar's laid cells would NOT
# pass this. That is not a defect in the threshold. §8.3 is Yarl's law with Yarl's register
# derivation, and the same corpus carries FRAMEs on 7 tiles and GRIDs on 3 — constructions
# §12.1 and §8.3.1 forbid outright here. §13.3's origination rule LAW: the bar may occasion a
# law, only the register may justify one, and a rule whose only justification is "the bar does
# it" is conformance and is refused. The bar's job in this constant is to show the bar is
# reachable, not to set it.
MIN_INCIDENT_BBOX = 3
# A 12-pixel component spread over a 2px-tall line is a joint fragment; one occupying at least
# 3x3 has extent in both axes. Guards the count against a thin diagonal that the containment
# test would otherwise have to adjudicate.
MIN_CONTRAST = 15.0
# Luminance points (0-255) between the component and the material immediately around it. Set
# below any plausible JOINT contrast on purpose: joints are excluded by CONTINUATION, not by
# contrast, so this constant's only job is to sit above image noise. The tile's own median
# absolute deviation is reported beside every verdict so a reader can see whether it did.

# --- criterion 2: a frame is a contained component that encloses ------------------------------
MIN_FRAME_INTERIOR = 16
# Same figure `ring_instrument.MIN_INTERIOR` uses, and taken from it deliberately rather than
# chosen again: 'a 4x4 plate is the smallest thing worth ringing'. Reused so the two instruments
# agree about what counts as enclosed and differ only in the input they read it from.

# --- criterion 3: the tile must meet itself ---------------------------------------------------
MAX_SEAM_RATIO = 2.0
# The step across the wrap boundary, divided by the 95th percentile of the steps between
# interior neighbours. A tile that tiles has a wrap step drawn from the same distribution as its
# interior steps, so the ratio sits near 1. 2.0 says the boundary is a bigger discontinuity than
# anything the tile already contains, which is a boundary the eye can find.
#
# VALIDATED AGAINST THE ACCEPTED CORPUS, and this is the one constant here the bar can properly
# support because it is a mechanical property of tiling rather than a register judgement:
#
#     across all 29 of the bar's floor tiles and all 431 laid cells, the seam ratio NEVER
#     EXCEEDS 1.64. Zero tiles would be called SEAMED at 2.0. Median 1.09.
#
# A shipping floor set clears this threshold with 22% of margin, which is what makes it a floor
# rather than a hurdle. §13.6 satisfied: derived from the corpus already accepted, not from the
# work seeking acceptance.
#
# ⚠ Recorded because the first calibration said the opposite. Run with the alpha channel dropped
# and the gids resolved against the wrong sheet, this same statistic read 4 of 7 tiles SEAMED
# with ratios to 8.23, and would have retired a correct criterion as unreachable. Two probes
# separated it: `bar_sheet_probe.py` and `bar_resolver_probe.py`.

# --- criterion 4: continuing structure must not be on a fixed pitch ---------------------------
GRID_MIN_TERMS = 3
GRID_MAX_PERIOD = 16
# §8.3.1's culled construction, stated in its own numbers: 'a regular 2px joint grid on a 16px
# pitch'. Three terms is the fewest that establish a progression rather than a coincidence, and
# it is what that clause's own example has room for on a 32px tile.
#
# MEASURED ON RUN CENTRES, NOT RUN STARTS — a correctness fix, not a threshold, and the oriented
# variants are what surfaced it. Reflection maps a position p to t-1-p, so it maps a run's start
# to the mirror of its END: with runs of unequal length that MOVES the spacing between starts,
# and an exact progression can be created or destroyed by flipping the tile. Base variant 9601
# screened CLEAN and four of its eight orientations then screened GRID, with nothing about the
# tile changed. A criterion whose verdict depends on which way up you hold the tile is not
# measuring a property of the tile. Centres are reflection-invariant.
#
# The corrected criterion is also strictly better at the job: it catches NEAR-regular coursing
# that unequal starts concealed. Its first act was to red the module's own clean fixture, whose
# courses of 11/10/11 put the stone bands at centres 5.5/16.0/26.5 — an exact progression. That
# fixture was the same construction the first composed field showed as plain brickwork.


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def load_rgb(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(float)
    # An overlay is judged on its opaque pixels only; a base tile is opaque everywhere.
    alpha = a[..., 3] / 255.0
    return a[..., :3], alpha


def field_of(rgb, n=3):
    """The candidate AS LAID. Everything in this module reads this, never the bare tile."""
    return np.tile(rgb, (n, n, 1))


def levels_of(L):
    """Every distinct luminance the tile actually contains, coarsest first.

    Same value-agnostic move as `ring_instrument.masks_of`: no chosen threshold, every level
    the image holds is swept. §12.1's prohibition is value-agnostic and a pale ring is a ring,
    so an instrument that picks one polarity cannot be reading the clause.
    """
    return sorted(set(np.round(L).flatten().tolist()))


def _mad(L):
    return float(np.median(np.abs(L - np.median(L))))


def _component_contrast(F_lum, comp_pixels):
    """Mean luminance gap between a component and the ring of material one pixel outside it."""
    H, W = F_lum.shape
    inside = set(comp_pixels)
    halo = set()
    for y, x in comp_pixels:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                p = (y + dy, x + dx)
                if 0 <= p[0] < H and 0 <= p[1] < W and p not in inside:
                    halo.add(p)
    if not halo:
        return 0.0
    a = np.mean([F_lum[p] for p in inside])
    b = np.mean([F_lum[p] for p in halo])
    return float(abs(a - b))


def incident_and_frame(rgb, n=3, t=T):
    """Criteria 1 and 2, together, because they read the same components."""
    F = field_of(rgb, n)
    FL = RI.lum(F)
    c0, c1 = t * (n // 2), t * (n // 2) + t
    incidents, frames = [], []
    for lv in levels_of(RI.lum(rgb)):
        for kind, mask in (("dark", FL <= lv), ("light", FL >= lv)):
            sub = mask[c0:c1, c0:c1]
            if not sub.any() or sub.all():
                continue
            enc = None
            for comp in RI.components(mask):
                ys = [y for y, _ in comp]
                xs = [x for _, x in comp]
                if not (c0 <= min(ys) and max(ys) < c1 and c0 <= min(xs) and max(xs) < c1):
                    continue                              # continues into the neighbour: material
                w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
                if len(comp) < MIN_INCIDENT_FRAC * t * t or min(w, h) < MIN_INCIDENT_BBOX:
                    continue                              # grain
                con = _component_contrast(FL, comp)
                if con < MIN_CONTRAST:
                    continue
                rec = dict(kind=kind, level=float(lv), px=len(comp), bbox=[int(w), int(h)],
                           contrast=round(con, 1),
                           at=[int(min(xs) - c0), int(min(ys) - c0)])
                incidents.append(rec)
                if enc is None:
                    enc = RI.enclosed(mask)
                interior = int(enc[min(ys):max(ys) + 1, min(xs):max(xs) + 1].sum())
                if interior >= MIN_FRAME_INTERIOR:
                    frames.append(dict(rec, interior=interior))
    return incidents, frames


def seam(rgb):
    """Criterion 3. Does the tile meet itself at its own edges?"""
    L = RI.lum(rgb)
    H, W = L.shape
    inner_x = [float(np.mean(np.abs(L[:, c] - L[:, c + 1]))) for c in range(W - 1)]
    inner_y = [float(np.mean(np.abs(L[r, :] - L[r + 1, :]))) for r in range(H - 1)]
    wrap_x = float(np.mean(np.abs(L[:, -1] - L[:, 0])))
    wrap_y = float(np.mean(np.abs(L[-1, :] - L[0, :])))
    mx, my = float(np.percentile(inner_x, 95)), float(np.percentile(inner_y, 95))
    rx = wrap_x / mx if mx > 1e-6 else (0.0 if wrap_x < 1e-6 else 999.0)
    ry = wrap_y / my if my > 1e-6 else (0.0 if wrap_y < 1e-6 else 999.0)
    return dict(wrap_x=round(wrap_x, 2), wrap_y=round(wrap_y, 2),
                interior_p95_x=round(mx, 2), interior_p95_y=round(my, 2),
                ratio_x=round(rx, 2), ratio_y=round(ry, 2),
                seamed=bool(rx > MAX_SEAM_RATIO or ry > MAX_SEAM_RATIO))


def grid(rgb):
    """Criterion 4. Is the continuing structure on an exact fixed pitch?"""
    L = RI.lum(rgb)
    hits = []
    for lv in levels_of(L):
        for kind, mask in (("dark", L <= lv), ("light", L >= lv)):
            if mask.all() or not mask.any():
                continue
            for axis, name in ((0, "columns"), (1, "rows")):
                dens = mask.mean(axis=axis)               # over the perpendicular axis
                idx = [int(i) for i, v in enumerate(dens) if v >= 0.9]
                if len(idx) < GRID_MIN_TERMS:
                    continue
                # collapse runs (a 2px joint is two adjacent full lines, one joint)
                runs, cur = [], [idx[0]]
                for i in idx[1:]:
                    if i == cur[-1] + 1:
                        cur.append(i)
                    else:
                        runs.append(cur)
                        cur = [i]
                runs.append(cur)
                # RUN CENTRES, not run starts — and the difference is not cosmetic.
                #
                # Reflection maps a position p to t-1-p, so it maps a run's START to the mirror
                # of its END. When runs have unequal lengths that MOVES THE SPACING between
                # starts, and an exact arithmetic progression can be created or destroyed purely
                # by flipping the tile. Measured: base variant 9601 screened CLEAN, and four of
                # its eight orientations then screened GRID. Nothing about the tile changed.
                #
                # A criterion whose verdict depends on which way up you hold the tile is not
                # measuring a property of the tile. Centres are invariant under reflection, so
                # this is a correctness fix rather than a threshold change; no constant moves.
                # Caught only because the oriented variants are re-screened rather than assumed
                # to inherit their parent's verdict (LOOP-PROCESS §4.2).
                centres = [(r[0] + r[-1]) / 2.0 for r in runs]
                if len(centres) < GRID_MIN_TERMS:
                    continue
                starts = centres
                deltas = {round(starts[i + 1] - starts[i], 3) for i in range(len(starts) - 1)}
                if len(deltas) == 1 and 0 < list(deltas)[0] <= GRID_MAX_PERIOD:
                    hits.append(dict(kind=kind, level=float(lv), axis=name,
                                     period=float(list(deltas)[0]), terms=len(starts)))
    return hits


def verdict(path, rgb=None, label=None):
    """One tile, judged AS LAID. `ring_instrument` runs first and unchanged.

    The cell size is READ FROM THE IMAGE, not assumed: this instrument is pointed at Yarl's
    32px candidates and at the 48px asset bar by the same call, and §13.6's calibration is only
    honest if both go through identical code.
    """
    if rgb is None:
        rgb, _alpha = load_rgb(path)
    t = rgb.shape[0]
    ring_v = RI.verdict(rgb.astype(np.uint8))
    ring = ring_v[0] if isinstance(ring_v, tuple) else ring_v
    inc, fr = incident_and_frame(rgb, t=t)
    sm = seam(rgb)
    gr = grid(rgb)
    codes = []
    if ring == "RING":
        codes.append("RING")
    if fr:
        codes.append("FRAME")
    if inc:
        codes.append("INCIDENT")
    if sm["seamed"]:
        codes.append("SEAM")
    if gr:
        codes.append("GRID")
    return dict(file=label or os.path.relpath(path, REPO),
                sha256=sha256_file(path) if path else None, cell=int(t),
                ring_instrument=ring, mad=round(_mad(RI.lum(rgb)), 2),
                incidents=inc[:4], n_incidents=len(inc),
                frames=fr[:2], n_frames=len(fr),
                seam=sm, grid=gr[:2], n_grid=len(gr),
                verdict="CLEAN" if not codes else "+".join(sorted(set(codes))),
                codes=sorted(set(codes)))


# =============================================================================================
# POSITIVE CONTROLS — §13.5 LOCKED, LOOP-PROCESS §4.
#
# "Stub the metric to a constant, plant the defect it exists to catch, mutate the thing it
# guards. Show it goes red. Record the verbatim failure. An instrument that cannot be made to
# fail is decorative and must be labelled so or deleted."
#
# LOOP-PROCESS §4.1 LAW binds the SHAPE of every control here: "the plant must carry the defect
# ON THE AXIS THE LEVER CLAIMS". So each plant below carries exactly one of the four defects and
# the control asserts the matching code fires AND that the clean fixture does not — a control
# that only asked "did anything change?" would certify connectivity and report it as efficacy.
# =============================================================================================

def _material(seed=7, size=T, levels=6):
    """A NEGATIVE control fixture: seamless irregular bond, incident-free, palette-quantised.

    Built to PASS, and it is the more important half of the suite. An instrument that reds on
    everything is as decorative as one that greens on everything; §13.5 asks that a pass mean
    something, which it only can if a legal construction produces one.

    Three properties, each answering a clause:

      QUANTISED   real pixel art holds a handful of values, and the level sweep in this module
                  is over the levels the image actually contains. The first version of this
                  fixture used continuous Gaussian grain, which gave nearly every pixel its own
                  level and let the sweep carve arbitrary blobs out of noise. That is a fixture
                  bug rather than an instrument bug, and it is recorded because it is the shape
                  of mistake that would otherwise be discovered on a candidate.
      WRAPPING    every joint position is computed modulo the tile, so the bond meets itself.
      IRREGULAR   course heights and head-joint offsets are unequal, which is the licensed
                  construction under §8.3.1's mirror clause ('joints, bond, grain, value
                  break') and NOT the ruled grid that clause culled from the wall tops.

                  ⚠ AND IT HAD TO BE MADE MORE IRREGULAR THAN IT FIRST WAS. Courses of 11, 10
                  and 11 put the three stone bands at centres 5.5, 16.0 and 26.5 — an exact
                  arithmetic progression, which is a regular coursing wearing unequal numbers.
                  `grid` (correctly) fired on it once the criterion moved to run centres, and
                  the fixture is what changed. This is the same defect the very first field
                  render showed as plain brickwork, arriving through a number instead of an eye.
    """
    rng = np.random.default_rng(seed)
    base, joint = 104.0, 68.0
    a = np.full((size, size, 3), base, dtype=float)
    a += rng.normal(0, 5.0, (size, size, 1))              # close even grain

    rows = [0, 13, 20]                                    # irregular course heights, wrapping
    for i, r in enumerate(rows):                          # stone-to-stone value break
        nxt = rows[i + 1] if i + 1 < len(rows) else size
        a[r:nxt, :, :] += (i - 1) * 7.0
    for r in rows:                                        # bed joints, edge to edge
        a[r, :, :] = joint
    # ONE head joint per course, offset per course — and this is the fixture's whole correction.
    #
    # The first version laid TWO head joints per course, which cuts each course into two stones
    # and leaves one of them wholly inside the cell. The instrument flagged those stones, at
    # 0.12-0.16 of the tile, and the question of whether that was the instrument over-firing or
    # the fixture being illegal went to the accepted corpus: the bar's laid floor cells sit at
    # ZERO contained components 55% of the time, cell-weighted p90 = 0.046. The fixture was in
    # the bar's top decile. It was the fixture.
    #
    # With one head joint, the course's single stone wraps around the tile and continues into its
    # own neighbour — which is §12.1's test for a joint passed by a STONE, and it is how a 32px
    # cell holds real paving at all: at this size a cell is a window onto a few large stones, not
    # a tray holding several small ones.
    for i, r in enumerate(rows):
        nxt = rows[i + 1] if i + 1 < len(rows) else size
        a[r:nxt, (i * 11 + 5) % size, :] = joint

    step = 255.0 / (levels - 1)                           # palette-quantise
    return np.clip(np.round(a / step) * step, 0, 255)


def _plant_incident(a):
    """A crack THROUGH ONE STONE that stops inside the cell. §8.3's own example."""
    a = a.copy()
    t = a.shape[0]
    y, x = 9, 8
    for i in range(14):
        a[y % t, x % t, :] = 40.0
        a[y % t, (x + 1) % t, :] = 40.0
        y += 1
        x += (1 if i % 3 else 0)
    return a


def _plant_frame(a):
    """An inset closed rectangle — C-GAB's measured construction, the 'frame at field scale'."""
    a = a.copy()
    t = a.shape[0]
    lo, hi = 6, t - 7
    for x in range(lo, hi + 1):
        a[lo, x, :] = a[hi, x, :] = 44.0
    for y in range(lo, hi + 1):
        a[y, lo, :] = a[y, hi, :] = 44.0
    return a


def _plant_seam(a):
    """A tile that does not meet itself: one edge column driven away from its wrap partner."""
    a = a.copy()
    a[:, -1, :] = 220.0
    return a


def _plant_grid(a):
    """§8.3.1's culled wall-top construction: a regular 2px joint grid on a 16px pitch."""
    t = a.shape[0]
    a = np.full_like(a, 150.0)
    for k in range(0, t, 8):
        a[k:k + 2, :, :] = 100.0
        a[:, k:k + 2, :] = 100.0
    return a


CONTROLS = [
    ("clean_material", _material, None, [], "the legal construction — bond and grain, no incident"),
    ("planted_incident", _material, _plant_incident, ["INCIDENT"], "a crack that stops inside the cell"),
    ("planted_frame", _material, _plant_frame, ["FRAME", "INCIDENT"], "an inset closed rectangle"),
    ("planted_seam", _material, _plant_seam, ["SEAM"], "a tile that does not meet itself"),
    ("planted_grid", _material, _plant_grid, ["GRID"], "a regular 2px joint grid on a 16px pitch"),
]


def run_controls(out_dir=None):
    out_dir = out_dir or os.path.join(HERE, "controls")
    os.makedirs(out_dir, exist_ok=True)
    rows, failures = [], []
    for name, fixture, plant, expect, why in CONTROLS:
        a = fixture()
        if plant:
            a = plant(a)
        p = os.path.join(out_dir, name + ".png")
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
        v = verdict(p)
        got = set(v["codes"])
        ok = set(expect).issubset(got) if expect else not got
        rows.append(dict(control=name, why=why, expect=expect or ["CLEAN"],
                         got=v["verdict"], codes=v["codes"], passed=ok,
                         seam=v["seam"],
                         n_incidents=v["n_incidents"], n_frames=v["n_frames"],
                         n_grid=v["n_grid"], mad=v["mad"], sha256=v["sha256"]))
        line = "%-18s expect %-22s got %-24s %s" % (
            name, "+".join(expect) or "CLEAN", v["verdict"], "PASS" if ok else "*** FAIL ***")
        print(line)
        if not ok:
            failures.append(line)
    res = dict(commit=git_commit(), instrument=os.path.relpath(__file__, REPO),
               instrument_sha256=sha256_file(__file__),
               constants=dict(MIN_INCIDENT_FRAC=MIN_INCIDENT_FRAC, MIN_INCIDENT_BBOX=MIN_INCIDENT_BBOX,
                              MIN_CONTRAST=MIN_CONTRAST, MIN_FRAME_INTERIOR=MIN_FRAME_INTERIOR,
                              MAX_SEAM_RATIO=MAX_SEAM_RATIO, GRID_MIN_TERMS=GRID_MIN_TERMS,
                              GRID_MAX_PERIOD=GRID_MAX_PERIOD),
               controls=rows, all_passed=not failures, verbatim_failures=failures)
    with open(os.path.join(out_dir, "CONTROLS.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("\n%s  (%d/%d)" % ("ALL CONTROLS PASSED" if not failures else "CONTROLS FAILED",
                             sum(1 for r in rows if r["passed"]), len(rows)))
    print("written: %s" % os.path.relpath(os.path.join(out_dir, "CONTROLS.json"), REPO))
    return 0 if not failures else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.controls:
        return run_controls()
    out = [verdict(p) for p in a.paths]
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for v in out:
            print("%-46s %-22s ring=%-6s mad=%.1f seam=%.2f/%.2f inc=%d frame=%d grid=%d"
                  % (os.path.basename(v["file"]), v["verdict"], v["ring_instrument"], v["mad"],
                     v["seam"]["ratio_x"], v["seam"]["ratio_y"],
                     v["n_incidents"], v["n_frames"], v["n_grid"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
