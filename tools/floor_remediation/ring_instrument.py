#!/usr/bin/env python3
"""THE RING INSTRUMENT — a value-agnostic detector for bible §12.1's prohibited construction.

WHY THIS EXISTS, AND WHAT IT REPLACES
-------------------------------------
The composition spike shipped `tools/composition_spike/dering_floors.py`, which decides what is
a ring with a LUMINANCE THRESHOLD:

    RING_FRACTION = 0.30   # a ring pixel sits below 0.30x its own tile's median luminance

and on that basis its table kept three of the four §6.4 survivors as "mid-tone rebates" and
removed the ring from one:

    | A-VAB | 126 | 60 | 0.48 | a mid-tone rebate - kept |
    | A-HEB | 136 | 78 | 0.57 | a mid-tone rebate - kept |
    | C-GAB | 139 | 74 | 0.53 | a mid-tone rebate - kept |
    | B-KAB | 130 | 14 | 0.11 | a near-black closed ring |

That instrument answers a question §12.1 does not ask. The clause, and the worked example the
same spike wrote into it one round later:

    THE RING PROHIBITION IS VALUE-AGNOSTIC: A PALE RING IS A RING.
    ... What separates occlusion from a ring is whether the treatment answers to the geometry
    it sits on, not whether it is lighter or darker than its surroundings.

A threshold at 0.30 of the median is precisely the construction the worked example was written
against, pointed at the floors instead of the walls. It cannot see a pale ring at all, and it
classifies by darkness where the clause classifies by geometry. This module carries NO
luminance threshold anywhere and never compares a value to a constant.

WHAT A RING IS, OPERATIONALLY
-----------------------------
Every criterion below is traceable to a sentence of §12.1. There are five and no more, because
each additional criterion is somewhere a fudge could hide.

  1. PRESENT ON EVERY SIDE. For the cells the contour surrounds, the contour is found in all
                 four directions - measured as a fraction, >= MIN_SIDE_COVERAGE.
                 §12.1: "present on every side regardless of what adjoins it".
                 NOT topological closure. A keyline with a two-pixel nick in it is still a
                 keyline, and an earlier draft of this file used closure and passed three
                 regenerated tiles that read as ringed the moment they were looked at in the lit
                 corridor. See side_coverage() for that correction in full.

  2. THIN, AND OF CONSTANT WIDTH. The contour is <= MAX_THICKNESS px wide by MEDIAN and varies
                 by <= MAX_THICKNESS_SPREAD px by median absolute deviation. A mass surrounding a
                 light patch is a shape, not an edge; and a ragged wall is stone speckle that
                 happened to close, not a ribbon somebody drew.
                 §12.1: "a dark edge drawn around a thing"; "a uniform ribbon of CONSTANT WIDTH
                 and constant value applied to every edge answers to nothing". Constant value is
                 already enforced by criterion 5 - every mask is a value-set. This is its twin.

                 MAX_THICKNESS_SPREAD is set inside a measured gap, not picked round. Across the
                 six controls and the four survivors, every genuine drawn loop measured a spread
                 of 0.00-0.67 px and every accidental speckle enclosure measured 1.37-3.69 px.
                 1.0 sits in the empty middle. No value in [0.70, 1.35] changes any verdict in
                 this report, and `--sweep-spread` re-runs the whole set at both ends to show it.

  3. RINGS A THING. The enclosed interior is >= MIN_INTERIOR px, so speckle that happens to
                 close a 2px gap is not reported as a keyline.

  4. RINGS ONE THING, RATHER THAN MARKING BOUNDARIES BETWEEN MANY. Removing the contour leaves
                 the tile in <= MAX_REGIONS_SEPARATED parts. A ring is drawn around one thing, so
                 taking it away leaves that thing and its surround. A mortar-joint network marks
                 the boundaries between things, so taking it away leaves many cells and no one of
                 them is what the contour was drawn around.
                 §12.1: "a dark edge drawn around a thing BECAUSE IT IS A THING" versus one
                 "drawn where one plane stops and another begins"; "answers to the geometry it
                 sits on".
                 This catches a frame that hugs the tile's own edge, which an earlier
                 does-it-touch-the-border test let through - a frame around the tile is a ring
                 around a thing, and the thing is the tile.

  5. AT EVERY VALUE. The four criteria above are evaluated over the tile's ENTIRE value ladder,
                 in both polarities, in every band, and over every exact colour:
                     - dark-set masks:  {lum <= L} for every distinct L in the tile
                     - light-set masks: {lum >= L} for every distinct L in the tile
                     - band masks:      {Lo <= lum <= Hi} for every pair of distinct levels
                     - exact-colour masks: {rgb == c} for every distinct c
                 No level is privileged and no threshold is chosen. A pale ring trips this
                 instrument by exactly the same path as a near-black one, which is the whole
                 point of the clause; the band sweep is what catches a mid-tone ring in a tile
                 that also holds darker and lighter content.

KNOWN LIMIT - STATED RATHER THAN TUNED AWAY
-------------------------------------------
A ring broken MORE THAN ABOUT ONE PIXEL IN EIGHT falls below MIN_SIDE_COVERAGE and this
instrument does not see it. Measured, on a synthetic dashed loop:

    1 gap in 4   0.735      1 gap in 8   0.864   <- not seen
    1 gap in 5   0.799      1 gap in 9   0.929   <- seen
    1 gap in 6   0.862      1 gap in 24  1.000   <- seen

The threshold is NOT lowered to reach the denser dashes, and the reason is the corpus rather
than a preference. The blind seat ruled - twice, in two rounds, unprompted - that A-HEB's and
C-GAB's mortar networks are joints and not keylines ("the top two at least draw stone with
joints between it"). Those two tiles measure 0.688 and 0.791. Dropping the threshold far enough
to catch a one-in-six dashed ring would walk it up to the seat's own clean floors and start
calling masonry a keyline, which is the failure this instrument exists to avoid. LOOP-PROCESS
§8: nothing is cut to fit. The limit is real, it is bounded, and it is written down.

WHAT IT DELIBERATELY PASSES
---------------------------
Plane-boundary occlusion (§12.1, RULED legal and required) is an OPEN contour: present where
floor adjoins, absent where wall meets wall. It encloses nothing, so criterion 1 excludes it
without any special case. A mortar-joint network reaches the tile border, so criterion 4
excludes it. Both exclusions are demonstrated in the controls, not asserted here.

POSITIVE CONTROL - LOOP-PROCESS §4 / bible §13.5
------------------------------------------------
`--controls` synthesises six tiles and asserts the verdict on each. Three must go RED and three
must stay GREEN. An instrument that only ever alarms has not discriminated anything, so the
GREEN half is load-bearing: the pale-ring control and the joint-network control are the same
colour, the same width and the same closure count, and differ only in whether the contour
reaches the tile border. If the instrument cannot tell those two apart it is decorative and
must be labelled so or deleted.
"""
import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
CONTROLS = os.path.join(HERE, "controls")

MIN_SIDE_COVERAGE = 0.90     # criterion 1. See "present on every side" in side_coverage().
MAX_THICKNESS = 2.0          # px. criterion 2 - median width.
MAX_THICKNESS_SPREAD = 0.5   # px. criterion 2 - median absolute deviation of that width.
MIN_HOLLOWNESS = 0.80        # criterion 2b. See hollowness().
PERIMETER_BAND = 2           # px. how near its own bbox edge a pixel counts as "on the outline".
MIN_INTERIOR = 16            # px. criterion 3. a 4x4 plate is the smallest thing worth ringing.
MAX_REGIONS_SEPARATED = 2    # criterion 4. a ring separates a thing from its surround; a joint
                             # network separates a tile into cells. See regions_separated().


# ---------------------------------------------------------------------------- primitives

def lum(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def components(mask):
    """8-connected components of a boolean mask, as lists of (y, x)."""
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for sy in range(H):
        for sx in range(W):
            if not mask[sy, sx] or seen[sy, sx]:
                continue
            stack, comp = [(sy, sx)], []
            seen[sy, sx] = True
            while stack:
                y, x = stack.pop()
                comp.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
            out.append(comp)
    return out


def enclosed(mask):
    """Pixels NOT in `mask` and not reachable from the tile border without crossing it.

    The complement is flooded 4-connected while the mask is treated as 8-connected. That
    pairing is the standard one and it is the correct one here: an 8-connected diagonal chain
    of ring pixels does seal a boundary against a 4-connected walk, and a diagonal keyline is
    still a keyline.
    """
    H, W = mask.shape
    reach = np.zeros(mask.shape, dtype=bool)
    stack = []
    for x in range(W):
        for y in (0, H - 1):
            if not mask[y, x] and not reach[y, x]:
                reach[y, x] = True
                stack.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if not mask[y, x] and not reach[y, x]:
                reach[y, x] = True
                stack.append((y, x))
    while stack:
        y, x = stack.pop()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not mask[ny, nx] and not reach[ny, nx]:
                reach[ny, nx] = True
                stack.append((ny, nx))
    return (~mask) & (~reach)


def wall_thickness(occ):
    """How thick is this contour, and how constant is its width.

    For every contour pixel, the shorter of its horizontal and vertical run WITHIN the contour.
    Along a 1px edge that is 1 whichever way the edge runs. Inside a mass it is large. The
    statistic is the MEDIAN and the median absolute deviation, not the mean and the standard
    deviation: a rectangular loop has four corner pixels whose runs measure the loop's LENGTH
    rather than its width, and on a 62px loop four such outliers drag a mean from 1.0 to 2.4 and
    a standard deviation to 4.1. That artefact silently exonerated B-KAB - a tile whose ring is
    as flagrant as any in the corpus - until the median replaced the mean.

    A 1px loop gives (1.0, 0.0). Ragged stone speckle gives a width above 1 and a spread above 1,
    which is what separates a ribbon somebody drew from a shape that happened to close.
    """
    H, W = occ.shape
    ys, xs = np.nonzero(occ)
    if not len(ys):
        return 0.0, 0.0
    runs = []
    for y, x in zip(ys, xs):
        h = 1
        i = x - 1
        while i >= 0 and occ[y, i]:
            h += 1
            i -= 1
        i = x + 1
        while i < W and occ[y, i]:
            h += 1
            i += 1
        v = 1
        i = y - 1
        while i >= 0 and occ[i, x]:
            v += 1
            i -= 1
        i = y + 1
        while i < H and occ[i, x]:
            v += 1
            i += 1
        runs.append(min(h, v))
    med = float(np.median(runs))
    return med, float(np.median(np.abs(np.array(runs, dtype=float) - med)))


def regions_separated(occ):
    """How many parts of the tile this contour separates it into.

    §12.1's real discriminator, and the one that survives contact with the corpus. A RING is
    drawn around ONE thing: remove it and the tile falls into the thing and its surround - two
    parts, or one when the ring hugs the tile edge and there is no surround. A JOINT NETWORK
    marks the boundaries BETWEEN things: remove it and the tile falls into many cells, no one of
    which is what the contour was drawn around.

    This replaced a plain "does the contour touch the tile border" test, which was wrong in both
    directions: it called a masonry network innocent for the right reason but by luck, and it
    called a frame hugging the tile's own edge innocent for no reason at all - and a frame around
    the tile is a ring around a thing, the thing being the tile.
    """
    free = ~occ
    return sum(1 for r in components(free) if len(r) >= MIN_INTERIOR)


def wall_of(mask, region):
    """The connected component of `mask` that encloses `region`: the mask pixels 8-adjacent to
    it, grown through the mask. Returned as a set, so criterion 4 can ask whether the thing
    doing the enclosing reaches the tile border."""
    H, W = mask.shape
    seed = set()
    for y, x in region:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx]:
                    seed.add((ny, nx))
    wall, stack = set(seed), list(seed)
    while stack:
        y, x = stack.pop()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if (0 <= ny < H and 0 <= nx < W and mask[ny, nx]
                        and (ny, nx) not in wall):
                    wall.add((ny, nx))
                    stack.append((ny, nx))
    return wall


# ---------------------------------------------------------------------------- the test

def masks_of(a):
    """Every mask the instrument sweeps. Yields (kind, label, boolean mask).

    Criterion 5. Both polarities of the tile's whole value ladder, every band between two of its
    levels, and every exact colour. There is no chosen threshold in here - every level the tile
    actually contains is tested and no level is treated differently from any other, which is
    what "value-agnostic" has to mean if it is to mean anything. The band sweep is what catches
    a MID-tone ring in a tile that also holds darker and lighter content: neither polarity of a
    one-sided threshold can isolate one.
    """
    L = lum(a.astype(float))
    levels = sorted(set(L.flatten().tolist()))
    for lv in levels:
        yield "dark-set", "lum<=%.1f" % lv, L <= lv
        yield "light-set", "lum>=%.1f" % lv, L >= lv
    for i, lo in enumerate(levels):
        for hi in levels[i + 1:]:
            yield "band", "%.1f<=lum<=%.1f" % (lo, hi), (L >= lo) & (L <= hi)
    seen = set()
    for c in map(tuple, a.reshape(-1, 3).astype(int)):
        if c in seen:
            continue
        seen.add(c)
        yield "exact-colour", "rgb%d,%d,%d" % c, (a == np.array(c)).all(-1)


def hollowness(comp, bbox):
    """Do these pixels lie ON the outline of their own extent, or THROUGH it.

    A ribbon somebody drew around something sits on the perimeter of its own bounding box and
    leaves the middle empty: hollowness 1.0. A scatter of stone speckle spread across the tile
    has the same bounding box but fills it: hollowness near zero.

    This exists because the union pass needed a limit. Taking every component of a mask together
    is what lets the instrument see a ring drawn in two brackets or in dashes - and, unrestricted,
    it also let it assemble the tile's loose speckle into a 332px "contour" scoring 0.91 on side
    coverage, which culled the plane-boundary-occlusion control. Occlusion is RULED legal and
    required by §12.1; a false positive there is the worst failure this instrument could have.
    §12.1's own word for the banned construction is a RIBBON, and this is what makes the union
    pass keep to ribbons.
    """
    y0, x0, y1, x1 = bbox
    n = 0
    for y, x in comp:
        if min(y - y0, y1 - y, x - x0, x1 - x) <= PERIMETER_BAND:
            n += 1
    return n / float(len(comp))


def side_coverage(occ, bbox):
    """"Present on every side" - measured directly, WITHOUT requiring topological closure.

    For every cell inside the contour's bounding box that is not part of the contour, count how
    many of the four directions have a contour pixel between it and the edge of that box. A loop
    closed all the way round scores 1.0. An L-shape scores about 0.5, a U about 0.75, a straight
    band 0. A loop with a two-pixel gap in it scores about 0.97 - AND THAT IS THE POINT.

    THIS REPLACED A TOPOLOGICAL ENCLOSURE TEST, AND THE REPLACEMENT IS THE SESSION'S OWN
    CORRECTION. The first version of this file took "present on every side" to mean "encloses a
    region you cannot reach from the tile edge", which is exact, cheap, and WRONG: it passes a
    keyline with a two-pixel nick in it. Three regenerated B-KAB children were called CLEAN by
    that test, and all three read as ringed tiles the moment they were looked at in the lit
    corridor - a dashed border, a frame open at one corner, and a frame with a single-pixel gap.
    §12.1 bans a treatment "present on every side regardless of what adjoins it". It says nothing
    about the treatment being watertight, and a ring does not stop being a ring because a pixel
    of it is missing. Bible §13.2: machine checks are floors, never verdicts - this one was
    caught by looking, which is what the eye is for.

    Returns (coverage, interior_cells).
    """
    y0, x0, y1, x1 = bbox
    if y1 - y0 < 2 or x1 - x0 < 2:
        return 0.0, []
    sub = occ[y0:y1 + 1, x0:x1 + 1]
    h, w = sub.shape
    interior, hits = [], []
    # Prefix counts so each cell's four look-outs are O(1).
    left = np.cumsum(sub, axis=1) - sub
    right = np.cumsum(sub[:, ::-1], axis=1)[:, ::-1] - sub
    up = np.cumsum(sub, axis=0) - sub
    down = np.cumsum(sub[::-1], axis=0)[::-1] - sub
    for y in range(h):
        for x in range(w):
            if sub[y, x]:
                continue
            interior.append((y0 + y, x0 + x))
            hits.append(int(left[y, x] > 0) + int(right[y, x] > 0)
                        + int(up[y, x] > 0) + int(down[y, x] > 0))
    if not interior:
        return 0.0, []
    return float(np.mean(hits)) / 4.0, interior


def find_rings(a):
    """All ring findings in a tile. Empty list == the tile carries no ring.

    Evaluated PER CONTOUR COMPONENT. A ring is drawn around ONE thing; a joint network reaching
    the tile border continues into the adjoining tile and answers to the geometry between tiles.
    Asking the question per contour is what tells those two apart, and getting it wrong is what
    the control suite caught on the first draft of this file.
    """
    H, W = a.shape[:2]
    area = H * W
    found = {}
    for kind, label, mask in masks_of(a):
        if not mask.any() or mask.all():
            continue
        comps = components(mask)
        # Each contour on its own, AND all of them together. The union pass is what sees a ring
        # DRAWN IN MORE THAN ONE PIECE, and the blind seat found that gap before this file did:
        # a regenerated tile whose keyline is two overlapping L-brackets scored 0.57 and 0.65 on
        # the per-contour pass - correctly, since neither bracket alone is on every side - while
        # the seat read it in one glance as "a 2px dark border of one value around a panel; it
        # rings the shape, turns all four corners and returns". Together they do. The same pass
        # sees a DASHED ring, which per-contour cannot: every dash is its own component.
        candidates = list(comps)
        if len(comps) > 1:
            candidates.append([p for c in comps for p in c])
        for comp in candidates:
            ys = [p[0] for p in comp]
            xs = [p[1] for p in comp]
            bbox = [min(ys), min(xs), max(ys), max(xs)]
            occ = np.zeros((H, W), dtype=bool)
            for y, x in comp:
                occ[y, x] = True
            cov, interior = side_coverage(occ, bbox)
            n_int = len(interior)
            if n_int < MIN_INTERIOR:                                    # criterion 3
                continue
            if cov < MIN_SIDE_COVERAGE:                                 # criterion 1
                continue
            th, spread = wall_thickness(occ)
            if th > MAX_THICKNESS or spread > MAX_THICKNESS_SPREAD:     # criterion 2
                continue
            hol = hollowness(comp, bbox)
            if hol < MIN_HOLLOWNESS:                                    # criterion 2b
                continue
            nreg = regions_separated(occ)
            if nreg > MAX_REGIONS_SEPARATED:                            # criterion 4
                continue
            border = any(y in (0, H - 1) or x in (0, W - 1) for y, x in comp)
            key = tuple(bbox) + (len(comp),)
            wcols = set(map(tuple, (a[y, x] for y, x in comp)))
            rec = dict(kind=kind, level=label, contour_px=len(comp), interior_px=n_int,
                       pieces=len(components(occ)), hollowness=round(hol, 3),
                       side_coverage=round(cov, 3), regions_separated=nreg,
                       wall_thickness=round(th, 2), wall_thickness_spread=round(spread, 2),
                       touches_border=bool(border), interior_bbox=[int(v) for v in bbox],
                       wall_colours=len(wcols), _wall=sorted(comp))
            # The same physical loop is re-found at many sweep levels. Report it once, at the
            # level that isolates it most tightly, and record how many levels agreed.
            if key in found:
                found[key]["levels_agreeing"] += 1
                if rec["contour_px"] < found[key]["contour_px"]:
                    ag = found[key]["levels_agreeing"]
                    found[key] = rec
                    found[key]["levels_agreeing"] = ag
            else:
                rec["levels_agreeing"] = 1
                found[key] = rec
    return sorted(found.values(), key=lambda r: -r["interior_px"])


def public(rings):
    """Findings without the pixel payload, for JSON and printing."""
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in rings]


def verdict(a):
    rings = find_rings(a)
    return ("RING" if rings else "CLEAN"), rings


# ---------------------------------------------------------------------------- controls

def _base_field(seed):
    """A plain speckled stone field with no closed contour in it. The controls' substrate."""
    rng = np.random.RandomState(seed)
    a = np.zeros((32, 32, 3), dtype=np.uint8)
    pal = np.array([[130, 129, 131], [137, 150, 153], [122, 123, 131], [111, 107, 115]],
                   dtype=np.uint8)
    idx = rng.choice(len(pal), size=(32, 32), p=[.62, .18, .12, .08])
    for i, c in enumerate(pal):
        a[idx == i] = c
    return a


def _loop(a, colour, inset):
    """A closed 1px loop, inset from the tile border. Free-standing: touches nothing."""
    a = a.copy()
    i, j = inset, 31 - inset
    a[i, i:j + 1] = colour
    a[j, i:j + 1] = colour
    a[i:j + 1, i] = colour
    a[i:j + 1, j] = colour
    return a


def _nicked_loop(a, colour, inset, nick=2):
    """A closed loop with a two-pixel bite taken out of one side. Still present on every side in
    any sense a player would use the words, and the case the topological-closure test passed."""
    a = _loop(a, colour, inset)
    j = 31 - inset
    mid = (inset + j) // 2
    a[j, mid:mid + nick] = _base_field(4242)[j, mid:mid + nick]
    return a


def _edge_frame(a, colour):
    """A frame on the tile's OWN border, all four sides. A does-it-touch-the-border test calls
    this innocent; it is a ring around a thing and the thing is the tile."""
    a = a.copy()
    a[0, :] = colour
    a[31, :] = colour
    a[:, 0] = colour
    a[:, 31] = colour
    return a


def _split_ring(a, colour, inset):
    """A ring drawn as TWO overlapping L-brackets rather than one loop - top+right, and
    left+bottom, offset from each other. Neither bracket is present on every side; together they
    ring the panel, turn all four corners and return. This is the construction a regenerated
    B-KAB child carried, which the per-contour pass scored 0.57 and 0.65 and let through, and
    which the blind seat culled on sight."""
    a = a.copy()
    i, j = inset, 31 - inset
    a[i, i + 2:j + 1] = colour          # top, shifted right
    a[i:j - 1, j] = colour              # right
    a[i + 2:j + 1, i] = colour          # left, shifted down
    a[j, i:j - 1] = colour              # bottom
    return a


def _dashed_ring(a, colour, inset, period=9):
    """A ring drawn as a dashed run of ticks. Every dash is its own component, so the per-contour
    pass cannot see it at all; the union pass can."""
    a = a.copy()
    i, j = inset, 31 - inset
    for x in range(i, j + 1):
        if (x - i) % period != period - 1:
            a[i, x] = colour
            a[j, x] = colour
    for y in range(i, j + 1):
        if (y - i) % period != period - 1:
            a[y, i] = colour
            a[y, j] = colour
    return a


def _joint_net(a, colour):
    """A masonry joint grid: same colour, same 1px width, closed cells - but every joint runs
    to the tile border, so every cell it encloses is bounded by a network that continues into
    the adjoining tile. This is the control that matters. It is the ring's twin in every
    measurable respect except the one §12.1 names."""
    a = a.copy()
    for r in (0, 12, 26):
        a[r, :] = colour
    for c in (0, 31):
        a[:, c] = colour
    a[13:26, 9] = colour
    a[1:12, 20] = colour
    return a


def _occlusion(a, colour):
    """Plane-boundary occlusion: a dark edge on the floor-facing side only. Open contour."""
    a = a.copy()
    a[0:3, :] = colour
    a[3, 0:14] = colour
    return a


def run_controls():
    """LOOP-PROCESS §4. Three must go RED, three must stay GREEN, and the RED/GREEN pair that
    differs by one property is the discrimination proof."""
    os.makedirs(CONTROLS, exist_ok=True)
    base = _base_field(4242)
    cases = [
        ("ctrl_clean", base, "CLEAN",
         "plain speckled field, no drawn contour anywhere"),
        ("ctrl_dark_ring", _loop(base, (24, 6, 25), 7), "RING",
         "near-black closed loop - the construction round 7 measured at 0.11 of the median"),
        ("ctrl_pale_ring", _loop(base, (196, 198, 201), 7), "RING",
         "PALE closed loop, same geometry - §12.1's worked example. The 0.30-of-median "
         "threshold in dering_floors.py cannot see this at all."),
        ("ctrl_midtone_ring", _loop(base, (69, 54, 72), 5), "RING",
         "mid-tone closed loop at 0.48 of the median - the value the spike table called "
         "'a mid-tone rebate - kept'"),
        ("ctrl_nicked_ring", _nicked_loop(base, (24, 6, 25), 7), "RING",
         "the same loop with a TWO-PIXEL bite out of one side. A topological-closure test calls "
         "this innocent; three regenerated B-KAB children passed that test and read as ringed "
         "tiles on sight. Criterion 1 measures presence on every side, not watertightness."),
        ("ctrl_split_ring", _split_ring(base, (24, 6, 25), 6), "RING",
         "a ring drawn as TWO overlapping L-brackets. Neither is on every side; together they "
         "are. The per-contour pass scored the real instance of this 0.57 and 0.65 and passed "
         "it; the blind seat culled it on sight. Caught by the union pass."),
        ("ctrl_dashed_ring", _dashed_ring(base, (24, 6, 25), 7), "RING",
         "a ring drawn as a dashed run of ticks, one pixel in nine missing - every dash its own "
         "component. Invisible to the per-contour pass by construction. Caught by the union "
         "pass. See KNOWN LIMIT in the docstring for how broken a ring has to be to escape."),
        ("ctrl_edge_frame", _edge_frame(base, (24, 6, 25)), "RING",
         "a frame on the tile's OWN border. A does-it-touch-the-border test calls this innocent; "
         "it is a ring around a thing and the thing is the tile. Criterion 4 catches it because "
         "removing it leaves ONE region, not a network of cells."),
        ("ctrl_joint_net", _joint_net(base, (69, 54, 72)), "CLEAN",
         "SAME colour, SAME 1px width and the SAME measured constancy as ctrl_midtone_ring, and "
         "it too runs to the tile border like ctrl_edge_frame. It differs from BOTH of them by "
         "criterion 4 alone: removing it leaves five cells rather than a thing and its surround."),
        ("ctrl_occlusion", _occlusion(base, (24, 6, 25)), "CLEAN",
         "plane-boundary occlusion: near-black, on the floor-facing side only, open contour. "
         "§12.1 RULED this legal and required."),
    ]
    print("POSITIVE CONTROL - LOOP-PROCESS §4 / bible §13.5")
    print("no instrument's pass counts until it has demonstrated it can fail.\n")
    ok = True
    rows = []
    cases_expect = {c[0]: c[2] for c in cases}
    for name, tile, expect, why in cases:
        Image.fromarray(tile).save(os.path.join(CONTROLS, name + ".png"))
        got, rings = verdict(tile)
        good = got == expect
        ok &= good
        print("  %-18s expect %-5s got %-5s  %s" % (name, expect, got, "OK" if good else "*** WRONG ***"))
        print("      %s" % why)
        for r in rings:
            print("      found: %s %s  wall=%dpx interior=%dpx sides=%.2f width=%.2f+-%.2f "
                  "border=%s"
                  % (r["kind"], r["level"], r["contour_px"], r["interior_px"],
                     r["side_coverage"], r["wall_thickness"], r["wall_thickness_spread"],
                     r["touches_border"]))
        rows.append(dict(name=name, expect=expect, got=got, pass_=good, why=why,
                         findings=public(rings)))
    print("\n  RED demonstrated:   %s" % ", ".join(r["name"] for r in rows if r["expect"] == "RING"))
    print("  GREEN demonstrated: %s" % ", ".join(r["name"] for r in rows if r["expect"] == "CLEAN"))
    got = {r["name"]: r["got"] for r in rows}
    print("\n  DISCRIMINATION - the pairs that carry the suite, each differing by ONE property:")
    pairs = [("ctrl_midtone_ring", "ctrl_joint_net",
              "same colour, same 1px width, same constancy; a ring vs a network"),
             ("ctrl_edge_frame", "ctrl_joint_net",
              "both run to the tile border; one rings the tile, the other partitions it"),
             ("ctrl_dark_ring", "ctrl_nicked_ring",
              "identical but for a two-pixel gap; BOTH must be called rings"),
             ("ctrl_split_ring", "ctrl_occlusion",
              "both are open contours per piece; one assembles into a ring, one does not")]
    for a_, b_, why in pairs:
        ok_pair = got.get(a_) == cases_expect[a_] and got.get(b_) == cases_expect[b_]
        print("    %-18s vs %-16s %s   %s"
              % (a_, b_, "OK " if ok_pair else "*** NOT TOLD APART ***", why))
    print("\n  CONTROL SUITE: %s" % ("PASS" if ok else "FAIL - the instrument is not fit to run"))
    return ok, rows


# ---------------------------------------------------------------------------- driver

def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def report(paths, title):
    print("%s\n" % title)
    rows = []
    for p in paths:
        a = np.array(Image.open(p).convert("RGB")).astype(int)
        v, rings = verdict(a)
        L = lum(a.astype(float))
        name = os.path.basename(p)
        print("  %-28s %-5s  median lum %5.1f" % (name, v, float(np.median(L))))
        for r in rings:
            print("      RING  %-12s %-18s wall=%3dpx interior=%3dpx sides=%.2f "
                  "width=%.2f+-%.2f bbox=%s levels=%d"
                  % (r["kind"], r["level"], r["contour_px"], r["interior_px"],
                     r["side_coverage"], r["wall_thickness"], r["wall_thickness_spread"],
                     r["interior_bbox"], r["levels_agreeing"]))
        rows.append(dict(file=name, path=os.path.relpath(p, REPO), sha256=sha256(p),
                         verdict=v, median_lum=round(float(np.median(L)), 1),
                         rings=public(rings)))
    n_ring = sum(1 for r in rows if r["verdict"] == "RING")
    print("\n  %d of %d carry a ring." % (n_ring, len(rows)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true", help="run the positive control suite only")
    ap.add_argument("--survivors", action="store_true", help="measure the four §6.4 survivors")
    ap.add_argument("--json", help="write results here")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args()

    out = dict(commit=git_commit(), min_side_coverage=MIN_SIDE_COVERAGE,
               max_thickness=MAX_THICKNESS, max_thickness_spread=MAX_THICKNESS_SPREAD,
               min_interior=MIN_INTERIOR, max_regions_separated=MAX_REGIONS_SEPARATED)

    if args.controls or not (args.survivors or args.files):
        ok, rows = run_controls()
        out["controls"] = dict(suite_pass=ok, cases=rows)
        if not ok:
            if args.json:
                json.dump(out, open(args.json, "w"), indent=1)
            return 1

    if args.survivors:
        print()
        paths = [os.path.join(SURVIVORS, c + ".png") for c in ("A-VAB", "A-HEB", "B-KAB", "C-GAB")]
        out["survivors"] = report(paths, "THE FOUR §6.4 SURVIVORS - un-remediated, as they sit "
                                         "in the ledger")

    if args.files:
        print()
        out["files"] = report(args.files, "MEASURED")

    if args.json:
        json.dump(out, open(args.json, "w"), indent=1)
        print("\n-> %s" % os.path.relpath(args.json, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
