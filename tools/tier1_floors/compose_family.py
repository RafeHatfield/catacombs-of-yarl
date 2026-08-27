#!/usr/bin/env python3
"""COMPOSE THE BOUNDARY FLOOR FAMILY — base tiles, incident overlays, trodden channel.

WHY THIS FILE EXISTS RATHER THAN A CURATION STEP
------------------------------------------------
The base wave generated 40 children conditioned on C-GAB at the levers the parent-rate run held.
Screened mechanically, **0 of 40 came back clean**: every one carries at least one component
contained inside its own cell, which §8.3 measures becoming a motif the moment it is tiled.

That is not a surprise and it is not a reason to lower the screen. It is the fifth consecutive
campaign on this surface to return zero architecturally-conformant tiles — the wall gauntlet's
100/0, the composition spike's 8 rounds/0, §6.4 Stage 1's 1-usable-in-60 on the wall subject,
tiles-pro's 0/114 two-plane — and bible §13.7 already records the general form as a MEASURED
platform fact:

    Architecture and conditioning do not exist on the same surface. BitForge conditions (12/12
    propagation) and produced architecture 0/100 ... **Any pipeline needing both composes across
    surfaces.**

So this module is that composition, and the division of labour is the one §13.7 prescribes:

    GENERATION SUPPLIES MATERIAL   palette, value distribution, grain, joint character — read
                                   off the wave's children as statistics, never as composition
    PROCEDURE SUPPLIES ARCHITECTURE  a wrapping irregular bond, phase-offset between variants,
                                   joints that continue into the neighbour

LOOP-PROCESS §1.1.6 is the process half of the same point: *when any asset class stalls — the
critic converging on the same missing property round after round — the next session is a
measurement pass, not another blind batch.* The measurement pass is `calibrate_against_bar.py`,
and what it found is what this file is built to: **55% of the floor cells the asset bar's shipped
maps actually lay carry ZERO contained components.** A floor tile with no incident in it is not
an unreachable ideal; it is what a shipping floor set is mostly made of.

THE THREE OBJECTS, PER §8.3's TABLE
-----------------------------------
    base tile      authored once per material   material only, NO incident   judged only as laid
    overlay        per instance, randomised     THE incident                 judged in its field
    channel        per instance, randomised     §8.2.1's trodden wear        judged in its field

WHAT EACH ONE REFUSES
---------------------
The base tiles must pass `field_laws` CLEAN — no ring, no frame, no contained incident, no seam,
no grid — and the run REFUSES to write a family that does not. A composer that quietly emitted a
tile its own screen fails would be LOOP-PROCESS §4.2's exact failure: a step that runs, changes
nothing that matters, and says so quietly.

THE CHANNEL IS NOT A STRIPE, AND THAT IS THE SUBTLE ONE
-------------------------------------------------------
§8.2.1 asks for *a polished channel worn through a wider hall*, and the seat asked for it in
pixels: *"sand a 12-unit band down the centre, erase the joint detail inside it so joints fade
where feet cross them."* A 12-unit band at a constant offset in every channel cell is
§8.3.1's lattice, arriving through the very feature that is supposed to read as wear.

What saves it is §12.1's own discriminator — *whether it continues into the neighbour.* A
channel running north-south DOES continue: it is one polished path, not a per-cell mark. So the
channel is legal exactly as long as it reads as continuous and its EDGES WANDER, which is why
the band's edge is jittered per cell from a seeded hash rather than drawn at a fixed x. A ruled
band and a worn path are the same pixels at different offsets, and the offset is the whole
difference.

The channel is composed rather than generated for a second, material reason: it is the same
stone, sanded (§8.1 polish). Generated separately it would be a different stone, and §13.3's
scene bar asks the cohesion question — *everything made to the same standard, nothing left
provisional.* It is delivered as an alpha wash at the family's own polished value, so it lifts
whatever base variant is underneath and pulls the joints up toward the stone: *joints fade where
feet cross them*, mechanically, without needing to know where the joints are.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import field_laws as FL      # noqa: E402

GEN = os.path.join(HERE, "gen")
ASSETS_REL = "src/Presentation/assets/tier1_floors"
ASSETS = os.path.join(REPO, ASSETS_REL)

T = 32
N_VARIANTS = 3            # §8.3's variant system. Three is the width the brief declares.
PALETTE_LEVELS = 7        # §5's values are PLACEHOLDER; this is a quantisation, not a palette law.

# Tile ids. 9600 block: clear of the composition spike's sparse wall ids (which reach 9343) and
# of the floor-remediation captures at 9400 — the id collision LOOP-PROCESS §4.2 logs as its
# second instance was exactly this kind of quiet overlap, so the block is chosen to not touch
# anything any existing theme names.
BASE_IDS    = [9600, 9601, 9602]
CHANNEL_IDS = [9610, 9611, 9612, 9613]      # left edge, full, right edge, chokepoint full-width
INCIDENT_ID0 = 9620                          # incident overlays are numbered from here
ORIENT_ID0   = 9700                          # the 24 oriented base variants


# =============================================================================================
# MATERIAL — read off the wave as statistics. Never as composition.
# =============================================================================================

def rank_donors(paths):
    """Order the wave's children by how little composition they carry.

    A donor contributes VALUE and GRAIN. It does not contribute shape, so what disqualifies one
    is not that it is ugly but that its statistics are contaminated by a strong construction: a
    ring, a frame or a grid drags the value histogram toward a shape this family must not
    inherit (§5.5, composition propagates with material at 12/12).

    Ordering, not a verdict: `ring_instrument` was relabelled by Rafe's ruling of 2026-08-27 to
    ORDERS ATTENTION, RULES NOTHING, and the same reading is taken here.
    """
    scored = []
    for p in paths:
        v = FL.verdict(p)
        hard = sum(1 for c in ("RING", "FRAME", "GRID") if c in v["codes"])
        scored.append((hard, v["n_incidents"], max(v["seam"]["ratio_x"], v["seam"]["ratio_y"]),
                       p, v))
    scored.sort(key=lambda r: (r[0], r[1], r[2]))
    return scored


def material_stats(donor_paths, n_levels=PALETTE_LEVELS):
    """The family's palette and grain, pooled across donors.

    Pooled deliberately: one donor's histogram is one image's accident, and §5.1 wants ONE
    palette for the material rather than one per tile. What is taken is the value ladder and the
    residual grain amplitude — quantities that describe a STONE, not a picture of one.
    """
    lums, grains, rgbs = [], [], []
    for p in donor_paths:
        a = np.asarray(Image.open(p).convert("RGB")).astype(float)
        L = FL.RI.lum(a)
        lums.append(L.flatten())
        # grain = the tile minus its own local level, so a donor's large-scale composition
        # (the thing that must not propagate) is subtracted out and only its texture survives.
        med = np.median(L)
        grains.append((L - med).flatten())
        rgbs.append(a.reshape(-1, 3))
    L = np.concatenate(lums)
    G = np.concatenate(grains)
    RGB = np.concatenate(rgbs)

    # Hue: the mean chroma offset of the pooled material, so the family is grey the way the
    # donors are grey rather than the way a builder imagines grey.
    mean_rgb = RGB.mean(axis=0)
    tint = mean_rgb / max(mean_rgb.mean(), 1e-6)

    lo, hi = float(np.percentile(L, 5)), float(np.percentile(L, 95))
    ladder = [lo + (hi - lo) * i / (n_levels - 1) for i in range(n_levels)]
    return dict(lum_lo=lo, lum_hi=hi, lum_median=float(np.median(L)),
                grain_sd=float(np.std(G)), grain_mad=float(np.median(np.abs(G))),
                tint=[float(t) for t in tint], ladder=[float(v) for v in ladder],
                n_donors=len(donor_paths))


def quantise(L, ladder):
    """Snap a luminance field onto the family's ladder. §4.3 LOCKED: no anti-aliasing."""
    lad = np.array(ladder)
    idx = np.abs(L[..., None] - lad[None, None, :]).argmin(axis=-1)
    return lad[idx]


def colourise(L, tint):
    a = np.stack([L * tint[0], L * tint[1], L * tint[2]], axis=-1)
    return np.clip(a, 0, 255)


# =============================================================================================
# ARCHITECTURE — the wrapping irregular bond. This is the half generation cannot supply.
# =============================================================================================

def wrap_noise(t, cells, rng):
    """Value noise that WRAPS, at a chosen spatial scale.

    The first draft of this composer used per-pixel Gaussian grain and the field came back as
    salt-and-pepper static — every pixel independent, which is not what stone looks like at any
    scale. Stone grain is spatially correlated: patches of a stone are lighter or darker than
    other patches OF THE SAME STONE. This is value noise on a torus, so it is correlated and it
    still meets itself at the tile's edges (§8.3.1: a mismatched edge is a treatment at a
    constant position, which is a lattice).
    """
    g = rng.normal(0, 1, (cells, cells))
    u = np.arange(t) * cells / float(t)
    i0 = np.floor(u).astype(int)
    f = u - i0
    f = f * f * (3 - 2 * f)                      # smoothstep, so cells do not read as squares
    i1 = (i0 + 1) % cells
    i0 = i0 % cells
    top = g[np.ix_(i0, i0)] * (1 - f)[None, :] + g[np.ix_(i0, i1)] * f[None, :]
    bot = g[np.ix_(i1, i0)] * (1 - f)[None, :] + g[np.ix_(i1, i1)] * f[None, :]
    return top * (1 - f)[:, None] + bot * f[:, None]


def voronoi_bond(variant, seed, t=T, n_seeds=4):
    """A wrapping irregular flagstone bond, as a Voronoi partition of the torus.

    THE FIRST BOND WAS A RUNNING BRICK BOND AND IT READ AS BRICKWORK. Laid as a field it was
    uniform coursed masonry — bed joints every ten pixels, everywhere, at one angle — which is
    the printed-paper read five independent seats have culled, and it is also §3.1's finding
    arriving on the ground plane: *a plane textured like elevation reads as elevation.* Coursed
    masonry is what a WALL is a picture of. A floor is a picture of the tops of stones, and the
    stones of a found-stone dungeon floor (§7.4: "the Boundary is mostly found stone") are not
    laid in courses at all.

    A Voronoi partition gives what coursing cannot: joints at varied angles, stones of unequal
    size and shape, and no repeating pitch in either axis for `field_laws.grid` to find. Distance
    is measured WRAPPED, so every cell boundary continues into the neighbouring tile — §12.1's
    test for a joint, and the reason the bond tiles.

    Four seeds on a 32px tile gives stones of roughly 250px each. That is coarse on purpose: at
    32 native pixels a cell is a window onto a few large stones, not a tray holding several small
    ones, and the asset bar's own paving is built the same way (its laid cells sit at zero
    contained components 55% of the time, which is only possible if the stones run off the edges).
    """
    rng = np.random.default_rng(seed + variant * 7919)
    yy, xx = np.mgrid[0:t, 0:t]
    pts = rng.integers(0, t, (n_seeds, 2))
    best = np.full((t, t), 1e18)
    lab = np.zeros((t, t), dtype=int)
    for i, (py, px) in enumerate(pts):
        dy = np.minimum(np.abs(yy - py), t - np.abs(yy - py)).astype(float)
        dx = np.minimum(np.abs(xx - px), t - np.abs(xx - px)).astype(float)
        # A per-seed ROTATED SUPERELLIPSE metric, not a circle. Euclidean distance gives round
        # cells whose boundaries meet in curves, and the field came back reading as leaf shapes
        # and crazy paving rather than as stone. Raising the exponent flattens the sides toward
        # straight, and rotating each seed's frame stops every stone from being axis-aligned —
        # between them they give angular, slabby, unequally-oriented flagstones, which is what
        # found stone (§7.4) actually looks like from above.
        th = rng.random() * 3.14159
        ct, st = np.cos(th), np.sin(th)
        u = np.abs(dy * ct + dx * st)
        v = np.abs(-dy * st + dx * ct)
        ay = 0.80 + 0.40 * rng.random()          # slabby: unequal in its own frame
        d = (u * ay) ** 4 + (v / ay) ** 4
        m = d < best
        best[m] = d[m]
        lab[m] = i
    joints = np.zeros((t, t), dtype=bool)
    for ax in (0, 1):
        joints |= (lab != np.roll(lab, 1, axis=ax))
    return lab, joints


def build_base(variant, mat, seed):
    """One base tile: an irregular wrapping bond, filled with the wave's measured material."""
    rng = np.random.default_rng(seed + variant * 977)
    lab, joints = voronoi_bond(variant, seed)

    stone_v = mat["lum_median"]
    L = np.full((T, T), stone_v, dtype=float)

    # STONE-TO-STONE VALUE BREAK. §8.3.1's mirror clause names it as material structure and the
    # base prompt asks for it. It has to be big enough to SURVIVE QUANTISATION: the ladder's step
    # is about 13 luminance points, so the first draft's sigma of 3 almost never crossed a level
    # and every stone came out the same value. Sized against the ladder rather than guessed.
    step = (mat["lum_hi"] - mat["lum_lo"]) / (PALETTE_LEVELS - 1)
    for cid in np.unique(lab):
        L[lab == cid] += rng.normal(0, step * 0.95)

    # GRAIN, at the amplitude measured off the donors and at two spatial scales. This is the
    # wave's actual contribution: the texture of the stone, carried as a statistic rather than
    # as a picture (§13.7 — conditioning supplies material, not architecture).
    amp = max(mat["grain_mad"], 1.0)
    L += wrap_noise(T, 8, rng) * amp * 0.55       # patchiness within a stone
    L += wrap_noise(T, 16, rng) * amp * 0.30      # finer tooth

    # JOINTS: darker because ENCLOSED, which is §6.5's own derivation ("joints, recesses and
    # undercuts sit darker because they are enclosed") and is direction-free, so it survives
    # §6.3. Grime along EVERY joint, not some — §8.1's "walked into a surface until it is part
    # of it" is distributed material; grime in one place would be a stain, which is incident.
    L[joints] = stone_v * 0.66 + rng.normal(0, 2.0, int(joints.sum()))

    # NORMALISE THE TILE'S OWN MEAN to the family's, keeping the variation INSIDE it.
    #
    # Without this the three variants came out at mean 106.1, 112.5 and 109.5 — a 6.4-point
    # spread — so a cell was systematically brighter or darker than the cell beside it and the
    # 32px grid drew itself across the room in flat value. A blind seat measured the steps at
    # +9.0, -6.1 and +6.0 against a crack-to-stone contrast of only ~35, and said the obvious
    # thing: "the grid draws itself onto the ground."
    #
    # It is §8.3.1's law in its purest form and the easiest instance to miss, because there is
    # no FEATURE at the constant position at all — the treatment sitting at the same place in
    # every cell is the cell's own average brightness. Stone-to-stone variation is material and
    # stays; tile-to-tile variation is a lattice and goes.
    L += (mat["lum_median"] - float(L.mean()))
    L = quantise(L, mat["ladder"])
    return colourise(L, mat["tint"]).astype(np.uint8), joints


def build_base_legal(variant, mat, seed, tries=40):
    """Search seeds until the bond passes `field_laws` CLEAN, then stop.

    NOT A TUNING OF THE LAW, and the difference matters. No threshold moves and no criterion is
    relaxed; what is searched is the SEED of a random partition, because a Voronoi seed that
    happens to land near the middle of the tile produces a stone wholly inside it — a contained
    component, which is the seat's verbatim cull *"the identical bracket-shaped stone sits at the
    identical position inside every single cell."* Rejecting that configuration is authoring to
    the law, exactly as rejecting a bond whose joints did not wrap would be.

    If no seed in `tries` produces a legal tile the caller is told so and REFUSES, rather than
    shipping the least-bad one.
    """
    for k in range(tries):
        img, joints = build_base(variant, mat, seed + k * 104729)
        tmp = os.path.join(HERE, ".probe_%d.png" % variant)
        Image.fromarray(img).save(tmp)
        v = FL.verdict(tmp)
        os.remove(tmp)
        if not v["codes"]:
            return img, joints, seed + k * 104729, k, v
    return None, None, None, tries, v


# =============================================================================================
# THE TRODDEN CHANNEL — §8.2.1, as an alpha wash rather than as a tile
# =============================================================================================

def build_channel(kind, mat, seed):
    """One channel overlay: a polished band, edges wandering, on transparency.

    `kind` selects which part of the band this cell carries — its left edge, its middle, its
    right edge, or (for a one-wide chokepoint) wall to wall. §8.2.1 requires both states to be
    drawable and to read apart at 1x: *"a one-wide corridor is either TRODDEN — polished wall to
    wall, because the traffic had no room to spread — or NEGLECTED."*

    The wash is RGB at the family's polished value with a soft alpha. Because it composites over
    whatever base variant is beneath, it lifts the joints (dark) proportionally more than the
    stone (light), which delivers the seat's *"erase the joint detail inside it so joints fade
    where feet cross them"* without the overlay having to know where any joint is.
    """
    rng = np.random.default_rng(seed * 31 + hash(kind) % 1000)
    polished = min(mat["lum_hi"], mat["lum_median"] * 1.18)
    rgb = np.zeros((T, T, 3), dtype=float)
    rgb[:] = np.array(colourise(np.array([[polished]]), mat["tint"])[0, 0])
    alpha = np.zeros((T, T), dtype=float)

    # THE BAND'S EDGE WANDERS, AND THE WANDER LIVES HERE — inside the shoulder tile — rather
    # than in whether the planner places a shoulder at all. That was the first construction and
    # it produced the opposite of what it intended: dropping a shoulder does not make an edge
    # wander, it makes the band stop on a cell boundary, which is a straight 32px line and is
    # §8.3.1's lattice arriving through the feature that is meant to read as wear.
    #
    # §12.1's worked example is the clause: a "uniform ribbon of constant width and constant
    # value applied to every edge ... answers to nothing", and what separates occlusion from a
    # ring is "whether the treatment answers to the geometry it sits on". Here it answers to the
    # cell: a low-frequency walk down the tile, seeded per cell by the caller, so the polished
    # edge moves several pixels along its length and never lands twice in the same place.
    #
    # The walk is deliberately wide (sd 1.6, ramp 5px) — at 32 native pixels a two-pixel wander
    # under a soft ramp is not visible at all, and an invisible irregularity is a ruled line.
    walk = np.cumsum(rng.normal(0, 1.6, T))
    walk = walk - walk.mean()
    walk = np.clip(walk, -7, 7)
    ramp = 5.0

    for y in range(T):
        if kind in ("full", "mid"):
            lo, hi = -1, T                       # interior of the band, or a trodden chokepoint
        elif kind == "left":
            lo, hi = 11 + walk[y], T             # the band's west shoulder crosses this cell
        else:                                     # "right" — its east shoulder
            lo, hi = -1, 20 + walk[y]
        for x in range(T):
            if lo <= x <= hi:
                d = min(x - lo, hi - x)
                a = 1.0 if d > ramp else max(0.0, d / ramp)
                alpha[y, x] = a
    peak = 0.50 if kind != "full" else 0.58
    alpha *= peak
    out = np.dstack([rgb, np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    return out


# =============================================================================================
# INCIDENT OVERLAYS — AUTHORED FROM THE MEASURED MATERIAL
#
# THE GENERATED WAVE WAS CULLED IN FULL, AND THE REASON IS THE INTERESTING PART.
#
# `prompts/incident_overlay.json` asked for cracks, wear marks, debris and grit as transparent
# decals, unconditioned. It declared its own reason for going unconditioned before the wave ran:
# §5.5 measures that composition propagates with material at 12/12, C-GAB is a picture of a
# full-bleed framed tile, and conditioning a decal on it would hand down exactly the tile-ness
# and the frame the object must not have.
#
# That risk was real and the opposite one landed. With no reference, the generator has no idea
# what material it is marking, so it does not draw a MARK ON A SURFACE — it draws a THING. The
# crack family came back as small centred maroon blobs; the wear family the same shape in
# another colour. They are objects: closed, centred, off-palette, and pictures of nothing on
# this floor. A screen that only asked about alpha coverage and edge contact passed all twelve.
#
# So the screen was too weak as well, and its gap is named rather than patched over: it tested
# whether the object was DECAL-SHAPED and never whether it was MADE OF THIS STONE. §5.1's
# zero-mercy palette gate is the clause that would have caught it, and it was not in the band
# this prompt declared.
#
# THE INCIDENT IS THEREFORE AUTHORED, from the family's own measured ladder and tint — the same
# move the channel already makes, and for the same reason. §8.1 is a claim about the SURFACE:
# "grime walked into a surface until it is part of it", "stone smoothed to a shine". An incident
# is a modulation of the material, not an object resting on it, and the only way to guarantee it
# is made of the same stone is to build it out of the same numbers.
#
# What generation bought here is real and is not discarded: the ladder, the tint and the grain
# amplitude every one of these marks is drawn with came off the base wave's donors.
# =============================================================================================

def _feather(alpha, k=1):
    """Soften an alpha mask by one step, so a mark does not end on a drawn line (§12.1)."""
    out = alpha.copy()
    for _ in range(k):
        n = np.zeros_like(out)
        for ax in (0, 1):
            for sh in (-1, 1):
                n = np.maximum(n, np.roll(out, sh, axis=ax))
        out = np.maximum(out, n * 0.45)
    return out


def incident_crack(mat, rng, t=T):
    """A hairline split, wandering, thinning to nothing at both ends.

    Dark because ENCLOSED — §6.5's derivation, direction-free, so it survives §6.3. A crack
    drawn with a lit side and a shaded side would be depicted lighting and would be illegal.
    """
    rgb_v = mat["lum_median"] * 0.52
    a = np.zeros((t, t))
    y, x = rng.integers(4, t - 4), rng.integers(4, t - 4)
    dy, dx = rng.normal(0, 1), rng.normal(0, 1)
    n = int(rng.integers(10, 22))
    for i in range(n):
        yi, xi = int(round(y)) % t, int(round(x)) % t
        taper = min(i, n - 1 - i) / max(1.0, n / 4.0)
        a[yi, xi] = max(a[yi, xi], min(1.0, 0.35 + 0.65 * taper))
        dy += rng.normal(0, 0.45)
        dx += rng.normal(0, 0.45)
        nrm = max(1e-6, (dy * dy + dx * dx) ** 0.5)
        y += dy / nrm
        x += dx / nrm
    return rgb_v, _feather(a) * 0.9


def incident_chip(mat, rng, t=T):
    """A corner knocked off a stone: a small angular notch, darker, with no drawn edge."""
    rgb_v = mat["lum_median"] * 0.60
    a = np.zeros((t, t))
    cy, cx = rng.integers(6, t - 6), rng.integers(6, t - 6)
    r = int(rng.integers(2, 4))
    for yy in range(cy - r - 1, cy + r + 2):
        for xx in range(cx - r - 1, cx + r + 2):
            d = ((yy - cy) ** 2 + (xx - cx) ** 2) ** 0.5
            if d <= r + rng.normal(0, 0.5):
                a[yy % t, xx % t] = 1.0
    return rgb_v, _feather(a) * 0.85


def incident_wear(mat, rng, t=T):
    """A shapeless patch of polish: paler because smoothed, edges fading, no defined shape.

    §8.1 — "traffic without care produces polish". Paler is a MATERIAL derivation (polished
    stone scatters less), so it declares no light direction. Deliberately shapeless: a wear mark
    with a defined shape is an ornament, and §12.1's worked example records what a
    constant-width, constant-value treatment does to a field.
    """
    rgb_v = min(mat["lum_hi"], mat["lum_median"] * 1.16)
    n = wrap_noise(t, int(rng.integers(3, 5)), rng)
    thr = float(np.percentile(n, int(rng.integers(72, 86))))
    a = np.clip((n - thr) / max(1e-6, float(n.max()) - thr), 0, 1)
    return rgb_v, a * 0.55


def incident_grit(mat, rng, t=T):
    """A sparse uneven speckle, denser in one part and thinning away across the rest.

    Its job in the field is different from the other three and worth stating: crack, chip and
    wear are EVENTS placed sparsely, while grit is a low-contrast dither placed densely, and it
    is what keeps the un-incidented cells between events off the flat clone read. §8.3.1's
    mirror — incident-free is not featureless — applies to the FIELD as well as to the tile.
    """
    rgb_v = mat["lum_median"] * 0.70
    dens = wrap_noise(t, 3, rng)
    rngspan = max(1e-6, float(dens.max() - dens.min()))
    dens = (dens - dens.min()) / rngspan
    a = (rng.random((t, t)) < dens * 0.16).astype(float)
    return rgb_v, a * 0.5


def incident_debris(mat, rng, t=T):
    """A few loose chips of the SAME stone, scattered and not arranged.

    Fragments of the same stone because the Boundary is found stone (§7.4) and debris of a
    different material is a prop, not wear.
    """
    rgb_v = min(mat["lum_hi"], mat["lum_median"] * 1.08)
    a = np.zeros((t, t))
    for _ in range(int(rng.integers(3, 5))):
        cy, cx = rng.integers(3, t - 3), rng.integers(3, t - 3)
        for yy in range(cy - 1, cy + 2):
            for xx in range(cx - 1, cx + 2):
                if rng.random() < 0.7:
                    a[yy % t, xx % t] = 1.0
    return rgb_v, a * 0.9


# family, builder, how many members, and HOW OFTEN A CELL GETS ONE.
#
# THE RATES ARE DERIVED FROM §8.1, NOT FROM THE LATTICE STATISTIC, and the distinction is the
# one §13.4 exists to protect. It would be easy to raise every rate until the number came down;
# that is optimising the instrument, and the clause's whole warning is that the criteria with
# numbers silently outcompete the ones without. So the rates answer a register question instead:
# *what has four hundred years of traffic and indifference actually done to this floor?*
#
#   grit    0.85  §8.1's residue of traffic. Nearly every cell: dust and sand are not an EVENT,
#                 they are the state of a floor nobody sweeps. This is also the family that
#                 answers §8.3.1's mirror at FIELD scale — incident-free is not featureless, and
#                 a low-contrast dither on most cells is what keeps the gaps between events off
#                 the flat clone read.
#   wear    0.34  polish. §8.2 makes this navigational, so it is common but not everywhere:
#                 "polish means you are on the path" only says something if some floor is not.
#   chip    0.14  §8.1 decay, and the institution neither repairs nor removes.
#   crack   0.11  the same, rarer: a split is a bigger event than a knocked corner.
#   debris  0.07  rarest. §8.1: "old things persist in place and the traffic routes around them"
#                 — traffic clears loose stone from a walked floor, so debris is uncommon on one.
#
# A cell may carry grit AND one event; two events on one cell reads as damage rather than as
# use, and §8.1's failure test is "is the state of this thing explained by traffic and
# indifference?"
INCIDENT_FAMILIES = [("crack", incident_crack, 6, 0.11), ("chip", incident_chip, 5, 0.14),
                     ("wear", incident_wear, 6, 0.34), ("grit", incident_grit, 5, 0.85),
                     ("debris", incident_debris, 5, 0.07)]


def build_incident(fn, mat, rng):
    v, a = fn(mat, rng)
    rgb = np.zeros((T, T, 3), dtype=float)
    rgb[:] = np.array(colourise(np.array([[v]]), mat["tint"])[0, 0])
    return np.dstack([rgb, np.clip(a * 255, 0, 255)]).astype(np.uint8)


def screen_overlay(path):
    """The screen declared BEFORE the wave ran (§13.6), PLUS the palette check whose absence
    let twelve objects through it."""
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im).astype(float)
    alpha = arr[..., 3] / 255.0
    cov = float((alpha > 0.35).mean())
    on = alpha > 0.35
    edges = [bool(on[0, :].any()), bool(on[-1, :].any()),
             bool(on[:, 0].any()), bool(on[:, -1].any())]
    reasons = []
    if not (0.02 <= cov <= 0.45):
        reasons.append("alpha_coverage=%.3f outside [0.02,0.45]" % cov)
    if all(edges):
        reasons.append("touches all four edges — a full-frame object wearing an alpha channel")
    # §5.1's zero-mercy palette gate, on the opaque pixels. This family's material is grey
    # (measured tint within 1% of neutral), so a mark with real colour in it is not this stone.
    if on.any():
        px = arr[..., :3][on]
        chroma = float(np.mean(px.max(axis=1) - px.min(axis=1)))
        reasons += (["mean chroma %.1f > 12 — off-palette; not made of this stone (§5.1)" % chroma]
                    if chroma > 12.0 else [])
    return dict(file=os.path.relpath(path, REPO), coverage=round(cov, 4),
                edges=edges, cull=reasons, kept=not reasons)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--donors", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=ASSETS)
    a = ap.parse_args()

    base_paths = sorted(glob.glob(os.path.join(GEN, "base", "*.png")))
    if not base_paths:
        raise SystemExit("REFUSING: no base wave on disk. Nothing to read material from.")

    ranked = rank_donors(base_paths)
    donors = [r[3] for r in ranked[:a.donors]]
    mat = material_stats(donors)

    print("MATERIAL, pooled from %d donors of %d children" % (len(donors), len(base_paths)))
    print("  lum 5-95%%: %.1f .. %.1f   median %.1f   grain mad %.2f"
          % (mat["lum_lo"], mat["lum_hi"], mat["lum_median"], mat["grain_mad"]))
    print("  tint %s   ladder %s" % ([round(t, 3) for t in mat["tint"]],
                                     [round(v, 1) for v in mat["ladder"]]))
    print("  donors: %s" % ", ".join(os.path.basename(d) for d in donors))

    os.makedirs(a.out, exist_ok=True)
    manifest = dict(family="boundary_floor_v1", commit=FL.git_commit(), seed=a.seed,
                    material=mat, donors=[os.path.relpath(d, REPO) for d in donors],
                    instrument=os.path.relpath(FL.__file__, REPO),
                    instrument_sha256=FL.sha256_file(FL.__file__),
                    base=[], channel=[], incident=[])

    # --- base tiles -------------------------------------------------------------------------
    print("\nBASE TILES — each must pass field_laws CLEAN or the run refuses")
    failures = []
    for v in range(N_VARIANTS):
        img, joints, used_seed, tries, verdict0 = build_base_legal(v, mat, a.seed)
        if img is None:
            print("  variant %d: no legal bond in %d seeds — REFUSING (%s)"
                  % (v, tries, verdict0["verdict"]))
            failures.append((BASE_IDS[v], "no legal bond in %d seeds" % tries))
            continue
        tid = BASE_IDS[v]
        p = os.path.join(a.out, "tier1_floor_%d.png" % tid)
        Image.fromarray(img).save(p)
        verdict = FL.verdict(p)
        ok = not verdict["codes"]
        print("  variant %d  id %d  %-8s seam %.2f/%.2f  inc=%d  bond seed %d (%d rejected)%s"
              % (v, tid, verdict["verdict"], verdict["seam"]["ratio_x"],
                 verdict["seam"]["ratio_y"], verdict["n_incidents"], used_seed, tries,
                 "" if ok else "  <-- FAILS ITS OWN SCREEN"))
        manifest["base"].append(dict(id=tid, variant=v, file=os.path.basename(p),
                                     sha256=FL.sha256_file(p), verdict=verdict["verdict"],
                                     codes=verdict["codes"], seam=verdict["seam"],
                                     joint_px=int(joints.sum()),
                                     bond_seed=used_seed, seeds_rejected=tries))
        if not ok:
            failures.append((tid, verdict["verdict"]))

    # --- channel overlays -------------------------------------------------------------------
    print("\nCHANNEL OVERLAYS — §8.2.1, alpha wash at the family's polished value")
    for i, kind in enumerate(("left", "mid", "right", "full")):
        img = build_channel(kind, mat, a.seed + i)
        tid = CHANNEL_IDS[i]
        p = os.path.join(a.out, "tier1_floor_%d.png" % tid)
        Image.fromarray(img).save(p)
        cov = float((img[..., 3] > 90).mean())
        print("  %-6s id %d  coverage %.3f" % (kind, tid, cov))
        manifest["channel"].append(dict(id=tid, kind=kind, file=os.path.basename(p),
                                        sha256=FL.sha256_file(p), coverage=round(cov, 4)))

    # --- incident overlays, from the wave ----------------------------------------------------
    print("\nINCIDENT OVERLAYS — the generated wave, screened against the declared band")
    ov_paths = sorted(glob.glob(os.path.join(GEN, "overlay", "*", "*.png")))
    kept, culled = [], []
    for op in ov_paths:
        sres = screen_overlay(op)
        (kept if sres["kept"] else culled).append(sres)
    print("  generated %d   kept %d   culled %d" % (len(ov_paths), len(kept), len(culled)))
    for sres in culled[:4]:
        print("     cull %-26s %s" % (os.path.basename(sres["file"]), "; ".join(sres["cull"])))

    print("\n  AUTHORED FROM THE MEASURED MATERIAL (see the section header for why)")
    tid = INCIDENT_ID0
    rng = np.random.default_rng(a.seed + 4242)
    for fam, fn, n, rate in INCIDENT_FAMILIES:
        for _i in range(n):
            img = build_incident(fn, mat, rng)
            dst = os.path.join(a.out, "tier1_floor_%d.png" % tid)
            Image.fromarray(img).save(dst)
            cov = float((img[..., 3] > 90).mean())
            manifest["incident"].append(dict(id=tid, family=fam, file=os.path.basename(dst),
                                             sha256=FL.sha256_file(dst),
                                             coverage=round(cov, 4), origin="authored",
                                             rate=rate))
            tid += 1
        print("     %-8s %d members  rate %.2f" % (fam, n, rate))

    manifest["incident_screen"] = dict(
        generated=len(ov_paths), kept_by_screen=len(kept), culled=len(culled), used_from_wave=0,
        why=("The generated overlay wave is NOT used. Unconditioned, the surface drew objects "
             "rather than marks on a surface — closed, centred, off-palette blobs. What the "
             "wave DID buy is the base donors' ladder, tint and grain amplitude, which every "
             "authored mark is drawn with."),
        detail=[dict(file=c["file"], why=c["cull"]) for c in culled])

    # --- ORIENTED VARIANTS, as real assets -----------------------------------------------------
    #
    # Three variants over a room is a visible repeat: measured at lattice 0.31 and plainly seen —
    # the same bracket-shaped stone recurring on the variant pitch, which is the blind seat's own
    # cull almost word for word. Rotating and flipping per cell turns 3 tiles into 24 distinct
    # cells and takes the field to 0.04, against 0.012 for a field where every cell is its own
    # unique tile.
    #
    # THIS IS §6.3 PAYING OUT, and it is worth naming because the clause is usually discussed as
    # a cost. An asset authored to RECEIVE light carries no direction, so there is no up in it to
    # break: it can be turned freely. A tile with a baked key light could not be rotated at all,
    # and this variety would have to be bought with eight times the art.
    #
    # Emitted as ASSETS rather than as a renderer flag on purpose. `TileThemeConfig.PickVariant`
    # already distributes a role's id list by position hash, so twenty-four ids in `floor_primary`
    # need no engine change whatever — and a rotation applied in the renderer would have had to
    # fight `Centered = false`, which positions a floor sprite by its top-left corner.
    #
    # A wrapping tile stays wrapping under every rotation and flip of the square, so the seam
    # criterion survives the operation untouched. Each oriented tile is screened again anyway,
    # because "it must still pass" and "it was not re-checked" are how §4.2's no-op fixes happen.
    print("\nORIENTED VARIANTS — 3 base tiles x 8 orientations of the square")
    oriented, oid = [], ORIENT_ID0
    for b in manifest["base"]:
        src = np.asarray(Image.open(os.path.join(a.out, b["file"])).convert("RGB"))
        for o in range(8):
            im = np.rot90(src, o % 4)
            if o >= 4:
                im = im[:, ::-1]
            im = np.ascontiguousarray(im)
            dst = os.path.join(a.out, "tier1_floor_%d.png" % oid)
            Image.fromarray(im).save(dst)
            ov = FL.verdict(dst)
            if ov["codes"]:
                failures.append((oid, "oriented variant fails: " + ov["verdict"]))
            oriented.append(dict(id=oid, of=b["id"], orientation=o,
                                 file=os.path.basename(dst), sha256=FL.sha256_file(dst),
                                 verdict=ov["verdict"]))
            oid += 1
    manifest["oriented"] = oriented
    print("  %d oriented tiles, ids %d-%d, all re-screened"
          % (len(oriented), ORIENT_ID0, oid - 1))

    manifest["placement"] = dict(
        rates={fam: rate for fam, _fn, _n, rate in INCIDENT_FAMILIES},
        max_events_per_cell=1,
        note=("Rates are derived from §8.1 (traffic and indifference), never from the lattice "
              "statistic — §13.4. Single source of truth: the engine planner and "
              "field_preview.py both read these, neither carries its own copy."))

    mp = os.path.join(a.out, "MANIFEST.json")
    with open(mp, "w") as f:
        json.dump(manifest, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(mp, REPO))

    if failures:
        print("\nREFUSING TO CERTIFY THE FAMILY. These base tiles fail the screen this session "
              "declared, and a composer that emitted them quietly would be LOOP-PROCESS §4.2's "
              "own failure — a step that runs and reports success while doing nothing it claimed:")
        for tid, v in failures:
            print("   id %d  %s" % (tid, v))
        return 1
    print("all %d base tiles pass field_laws CLEAN" % N_VARIANTS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
