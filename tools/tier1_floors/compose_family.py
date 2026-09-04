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
N_MATERIALS = 3           # §8.3: THE MATERIAL. Three is the width the brief declares, and it is
                          # a count of materials, not of tiles.
N_BONDS = 4               # bond layouts per material. §8.2.1's tier-one requirement item 1, in
                          # the blind seat's own words: "author variants whose bond is OFFSET
                          # BETWEEN THEM, so a joint starting at x=8 in one cell lands mid-stone
                          # in the next." Same stone, laid differently — still one material.
N_VARIANTS = N_MATERIALS * N_BONDS
# 3 materials x 4 bonds x 8 orientations = 96 ids, and the number is DERIVED rather than chosen.
#
# A blind seat measured the old pool's failure exactly: "42 floor tiles visible ... at least 21
# are duplicates of another tile on the same screen. Four distinct tiles each appear 3-4 times."
# That is not a defect in any tile. It is the arithmetic of the pool: for N ids drawn uniformly
# across 42 cells, the expected number of cells sharing an id with another is
# 42 - N(1-(1-1/N)^42), which at N=24 is **22.0**. The seat measured 21.
#
#     N=24   22.0 cells with a twin      N=96    7.8
#     N=48   13.8                        N=200   4.0
#
# So no amount of better drawing reaches it, and neither does a plausible number of hand-authored
# assets — 200 variants of one material is not a floor system, it is a spritesheet.
#
# ⚠ THE REAL SCALING LEVER IS THE OVERLAY, NOT THE TILE, and this is §8.3's mechanism showing why
# it is a law rather than a preference: a base-variant system is O(assets), an overlay system is
# COMBINATORIAL. 96 base ids times an incident drawn per instance from six families at four flips
# is a space no screen can exhaust. Widening the bond pool is the cheap half; making the incident
# individuate every cell is the half that actually solves it, and it is the next round's work.
PALETTE_LEVELS = 7        # §5's values are PLACEHOLDER; this is a quantisation, not a palette law.

# ============================ TWO RUNGS BELOW THE DONORS ============================
#
# RULED, and the provenance is recorded here because the working ladder is a PLACEHOLDER scaffold
# rather than §5.1 law — a later palette-derivation pass inherits this, so it inherits the reason.
#
# EARNED BY `measure_ladder_reach.py`. The seven rungs above are the donors' own 5th-to-95th
# percentile band, and a FLOOR DONOR HAS NO REASON TO CONTAIN THE DARKEST VALUE IN THE ROOM. Two
# things need one and neither was in the frame when the band was cut:
#
#   THE FLOOR'S OWN JOINTS   the bond authors a sheltered joint at 0.42 x its stone — about 47.8
#                            — and the quantiser clamped every one of them to the bottom rung,
#                            75.02. Not the wrong darkness: the SAME darkness, all of them, with
#                            zero spread. That is the device gate's second verdict, *"all the gaps
#                            look standardized,"* stated as a number.
#   THE WALL FACE            §6.5 puts it at 0.50-0.60 x the floor. Against the corrected anchor
#                            that is 52.95 and 63.55, and both landed under 75.02, so a wall face
#                            could not be authored on this palette at either end of its own band.
#
# Same spacing, same tint, two rungs down: 48.56 and 61.79. Count 7 -> 9, noted for the future
# palette-derivation pass, which should derive this reach rather than extend it after the fact.
#
# ============================ AND TWO MORE, FOR THE SAME REASON ============================
#
# RULED (Rafe, 2026-09-03), and it is the SECOND instance of one shortfall rather than a new one.
# The reason above is reproduced exactly: a treatment that must reach below the donors' band gets
# clamped against the ladder's own end, and the clamp is invisible because every clamped pixel is
# arithmetically correct.
#
#   THE CONTACT OCCLUSION   §12.1's plane boundary, ambient-anchored (RULED 2026-09-02) so it is
#                           re-drawn up to three times where the lamp does not reach. It blends
#                           the floor toward rgb(22,22,22) — the ambient itself — and at its
#                           deepest it wants 24.07, which is 1.85 rungs BELOW 48.56. Snapping it
#                           to a nine-rung ladder does not merely quantise the seam, it DELETES
#                           the stacking: every layer past the first lands on the same bottom
#                           rung, which is the 2026-08-31 sheltered-joint failure repeated on a
#                           different treatment. Measured before the change: at 1 layer the clamp
#                           costs 0.64 luminance at the contact edge and nothing beyond it; at 2
#                           and 3 layers it costs 19.24 and 24.49, all of it in the dark band the
#                           ruling exists to serve.
#
# Same spacing, same tint, two rungs further down: 35.34 and 22.11. 22.11 is the first rung that
# reaches the deepest stack, so the reach is DERIVED from what has to be representable rather than
# chosen. Count 9 -> 11.
#
# WHAT IT MOVES, MEASURED RATHER THAN ASSERTED — and the first answer was wrong. The obvious
# claim is that nothing but the occlusion can reach the new rungs, because the bond authors its
# joint at 0.42 x its stone (47.79 at the median) and 47.79 is nearer 48.56 than 35.34. That is
# true of a joint under a MEDIAN stone and false of the field: a joint is 0.42 x THE STONE IT IS
# CUT INTO, so under a stone at 88.24 it is authored at 37.06 — which the nine-rung ladder
# clamped to 48.56 and the eleven-rung one puts on 35.34, where it belongs. `--ladder-delta`
# reports it: 2.78% of the composed field moves, 83.6% of those pixels are joints, and every
# move is one rung or two.
#
# THAT IS THE CLAMP RELEASING, NOT PR #161's FAILURE REPEATING, and the difference is in the
# distribution rather than in the mean. #161 put 92.7% of joint pixels on the bottom two rungs
# and took mean joint contrast 0.272 -> 0.510; here the joint spread is UNCHANGED at 5.026 rungs
# with both deciles identical (open 48.0, tight 114.47), and mean Weber contrast moves
# 0.1765 -> 0.1886. A 6.9% lift with the distribution held is a minority of joints going to the
# rung they always wanted.
#
# ⚠ AN ANCHOR SAYING "THE BOTTOM" IS AN ANCHOR THAT MOVES. `SHELTER_LIFT_RUNGS` lifts a joint off
# the ladder's bottom, so extending the ladder moves every sheltered joint with it. It survived
# this change because the lift is applied to the joint's own authored VALUE and not to
# `ladder[0]`, but the next treatment written against "the bottom rung" will not. Bible §5.7's
# rule for anchors — a mean, stable under field size — wants its twin here: an anchor is named
# by what it IS, never by where the ladder happens to end.
PALETTE_EXTEND_BELOW = 4

# Tile ids. 9600 block: clear of the composition spike's sparse wall ids (which reach 9343) and
# of the floor-remediation captures at 9400 — the id collision LOOP-PROCESS §4.2 logs as its
# second instance was exactly this kind of quiet overlap, so the block is chosen to not touch
# anything any existing theme names.
# ID BLOCKS, SPACED AND ASSERTED.
#
# Widening the bond pool from 3 to 12 pushed BASE_IDS from 9600-9602 to 9600-9611, and the
# channel block started at 9610 — **two of the new base tiles and two channel overlays would have
# shared an id.** Nothing about that would have been visible: the theme would have resolved a
# floor id to a channel wash, or the overlay loader to a base tile, and the scene would have
# rendered something plausible.
#
# It is LOOP-PROCESS §4.2's second logged instance repeating in a new session — `capture_children`
# staged floor candidates from id 9200, which was `wall_autotile: 0` in the theme it was using,
# and every capture quietly made the floor tile double as a wall. That clause's generalisation is
# the one that binds here: **any step that asserts something is HELD CONSTANT must be able to go
# red when it is not.** So the blocks are spaced with room to grow AND checked, because a comment
# saying "these do not overlap" is a docstring with no enforcement behind it.
BASE_IDS      = list(range(9600, 9600 + 12))   # 3 materials x 4 bond layouts
CHANNEL_IDS   = [9620, 9621, 9622, 9623]       # left edge, mid, right edge, chokepoint full-width
OCCLUSION_IDS = [9630, 9631, 9632, 9633]       # contact occlusion: N, E, S, W edges
INCIDENT_ID0  = 9640                           # incident overlays are numbered from here
ORIENT_ID0    = 9700                           # the oriented base variants

_FIXED = BASE_IDS + CHANNEL_IDS + OCCLUSION_IDS
if len(set(_FIXED)) != len(_FIXED):
    raise SystemExit("REFUSING: tier-one floor id blocks collide: %s"
                     % sorted(i for i in _FIXED if _FIXED.count(i) > 1))
if max(BASE_IDS) >= min(CHANNEL_IDS) or INCIDENT_ID0 <= max(OCCLUSION_IDS):
    raise SystemExit("REFUSING: tier-one floor id blocks are out of order.")


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


def ladder_for(lo, hi, n_levels=PALETTE_LEVELS, extend_below=PALETTE_EXTEND_BELOW):
    """The family's value ladder, DERIVED — never stored and trusted.

    `lo` and `hi` are the donors' 5th and 95th percentiles, so this function is a pure restatement
    of them and reproduces the donors' own derivation without needing the donors. That matters
    because the extension below was ruled after the base family's manifest was already written:
    a stored ladder is a snapshot of whatever the rule was on the day, and every consumer that
    trusted one would have gone on quantising against seven rungs while the rule said nine.
    """
    step = (hi - lo) / (n_levels - 1)
    return ([lo - step * (extend_below - i) for i in range(extend_below)]
            + [lo + step * i for i in range(n_levels)])


def rehydrate(mat):
    """Re-derive a stored material's ladder from its own band, in place.

    Called by every consumer that loads a manifest someone else wrote. `lum_lo`/`lum_hi` are the
    measurement; the ladder is a rule applied to it, and the rule is allowed to change.
    """
    mat["ladder"] = [float(v) for v in ladder_for(mat["lum_lo"], mat["lum_hi"])]
    mat["derived_levels"] = PALETTE_LEVELS
    mat["extended_below"] = PALETTE_EXTEND_BELOW
    return mat


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
    # `lum_lo`/`lum_hi` stay the DONORS' band — every `step` in this codebase is derived from
    # them, and moving them would silently rescale the grain, the offsets and the crack depth.
    # The extension is on the LADDER only, which is what quantises and what clips.
    ladder = ladder_for(lo, hi, n_levels)
    return dict(lum_lo=lo, lum_hi=hi, lum_median=float(np.median(L)),
                grain_sd=float(np.std(G)), grain_mad=float(np.median(np.abs(G))),
                tint=[float(t) for t in tint], ladder=[float(v) for v in ladder],
                derived_levels=n_levels, extended_below=PALETTE_EXTEND_BELOW,
                n_donors=len(donor_paths))


def quantise(L, ladder):
    """Snap a luminance field onto the family's ladder. §4.3 LOCKED: no anti-aliasing."""
    lad = np.array(ladder)
    idx = np.abs(L[..., None] - lad[None, None, :]).argmin(axis=-1)
    return lad[idx]


def colourise_map(L, tint_map):
    """`colourise` with a PER-PIXEL tint — the chroma channel's only entry point.

    `tint_map` is (H, W, 3). Nothing here changes a pixel's value: the tints handed in are
    projected onto the plane of constant luminance by `compose_ashlar.chroma_tint` before they
    ever arrive, so this multiplies colour and leaves the ladder alone.
    """
    return np.clip(np.asarray(L, dtype=float)[..., None] * np.asarray(tint_map, dtype=float),
                   0, 255)


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


def slab_bond(variant, seed, t=T):
    """A wrapping irregular ASHLAR bond — straight joints, T-junctions, unequal slabs.

    ⚠ THIS REPLACES A VORONOI PARTITION, AND THE REASON IS THE JUNCTION TOPOLOGY.

    Voronoi cells meet at three-way Y-junctions at roughly 120 degrees, with boundaries that
    curve. That is not a stylistic near-miss for paving — **it is the exact signature of
    desiccation cracking**, and a blind seat named the material off it without hedging:

        "Dried, cracked mud — a parched riverbed or a dry clay pan. Baked earth, not stone. ...
         irregular polygons meeting at 3-way junctions, with the cracks drawn as 1px dark lines
         that thin and taper — the exact signature of desiccation cracking in mud, not of cut,
         laid or quarried stone. There are no straight edges anywhere, no mortar line."

    Two rounds were spent tuning the wrong axis: joint width, joint value, stone value break,
    grain amplitude. None of them could work, because what says *laid* is not how the joints look
    — it is **how they meet**. Cut stone is bounded by straight lines that terminate against each
    other in T-junctions. Mud is bounded by curves that meet in Y-junctions.

    So: one horizontal and one vertical cut, at positions that differ per variant, then the whole
    pattern ROLLED by a per-variant offset. The roll is what makes every slab wrap — after it,
    all four cross a tile edge and continue into the neighbour, which is §12.1's test for a joint
    and the reason no slab reads as a contained incident (`field_laws` screens for exactly that).

    Four slabs of roughly sixteen pixels is also the right size rather than a convenience: at
    32 native pixels a cell shows something like a metre and a half of floor, so a flagstone is
    twelve to eighteen pixels. The asset bar's own paving tiles are built from a similarly small
    number of large regions — it is the only way a floor tile at this scale is not a mosaic.

    The cuts WANDER by a pixel. A perfectly ruled line is a machine's edge; a laid joint is
    straight to the eye and not straight to a ruler. It is also what keeps `field_laws.grid` a
    meaningful check rather than one this bond happens to slip past.

    ⚠ Not a grid, and the distinction is §8.3.1's own: it culled "a regular 2px joint grid on a
    16px pitch" from the wall tops, where REGULAR is the operative word — a fixed pitch at a
    fixed offset in every cell. Two cuts per axis is below `GRID_MIN_TERMS`, their positions are
    unequal and differ per variant, and the roll moves them again.
    """
    rng = np.random.default_rng(seed + variant * 7919)
    cut_y = int(rng.integers(11, 22))
    cut_x = int(rng.integers(11, 22))
    wob_y = np.clip(np.cumsum(rng.normal(0, 0.55, t)), -1.4, 1.4)
    wob_x = np.clip(np.cumsum(rng.normal(0, 0.55, t)), -1.4, 1.4)

    joints = np.zeros((t, t), dtype=bool)
    lab = np.zeros((t, t), dtype=int)
    for i in range(t):
        yy = int(round(cut_y + wob_y[i])) % t
        joints[yy, i] = True
        joints[(yy + 1) % t, i] = True          # a joint is two pixels: consistent width is
        xx = int(round(cut_x + wob_x[i])) % t   # what a mortar joint has and a crack does not
        joints[i, xx] = True
        joints[i, (xx + 1) % t] = True

    for y in range(t):
        for x in range(t):
            below = y > int(round(cut_y + wob_y[x]))
            right = x > int(round(cut_x + wob_x[y]))
            lab[y, x] = (2 if below else 0) + (1 if right else 0)

    # THE ROLL. Without it every slab sits wholly inside the tile, which is a contained component
    # at a constant position — the seat's own cull, "the identical bracket-shaped stone sits at
    # the identical position inside every single cell". Rolled, all four cross an edge.
    # THE ROLL, CONSTRAINED SO NO JOINT LANDS ON A TILE EDGE.
    #
    # Unconstrained, a roll can put a joint at x=0 or y=31, and then the tile is literally
    # outlined — its own mortar drawn along the cell boundary. Across 24 ids several landed that
    # way, and with the uniform grit removed there was nothing left masking them. A blind seat
    # put it first: "**Every tile is outlined.** I measured dark-pixel density by position within
    # the cell", and its flip named the fix in pixels — "move mortar off the 64px boundary: no
    # seam within 6px of a tile edge".
    #
    # ⚠ AND THE GRIT REMOVAL IS WHAT EXPOSED IT, which the previous round's seat predicted almost
    # exactly: "fixing the light terracing will make the crack repeats MORE visible, not less —
    # the vignette is currently hiding some of them." A texture loud enough to hide a lattice was
    # hiding this one too. Two defects, one masking the other, and removing the mask is what a
    # round is for.
    # THE ROLL IS UNIFORM, AND A KEEP-OUT BAND WAS TRIED AND REVERTED.
    #
    # Constraining the roll so no joint lands within 5px of a tile edge does stop the cell being
    # outlined — and it puts the joint cross near the MIDDLE of every cell instead, which is the
    # same law broken at a different offset. §8.3.1: "any treatment applied at a constant position
    # within a tile becomes a lattice when tiled, whatever it depicts". Offset 16 is as constant
    # as offset 0. Measured on the field instrument, not judged by eye: see below.
    #
    # What actually removes the preferred offset is a UNIFORM roll across a POOL WIDE ENOUGH for
    # the distribution to be flat. At 24 ids a handful landed on the edge and the eye found them;
    # at 96 the joint offsets are spread over the whole cell with no mode, so no offset adds up.
    # The fix for a lattice is width, not a keep-out — a keep-out only moves the mode.
    dy, dx = int(rng.integers(t)), int(rng.integers(t))
    joints = np.roll(np.roll(joints, dy, axis=0), dx, axis=1)
    lab = np.roll(np.roll(lab, dy, axis=0), dx, axis=1)
    return lab, joints


def build_base(variant, mat, seed):
    """One base tile: an irregular wrapping bond, filled with the wave's measured material."""
    rng = np.random.default_rng(seed + variant * 977)
    lab, joints = slab_bond(variant, seed)

    stone_v = mat["lum_median"]
    L = np.full((T, T), stone_v, dtype=float)

    # STONE-TO-STONE VALUE BREAK. §8.3.1's mirror clause names it as material structure and the
    # base prompt asks for it. It has to be big enough to SURVIVE QUANTISATION: the ladder's step
    # is about 13 luminance points, so the first draft's sigma of 3 almost never crossed a level
    # and every stone came out the same value. Sized against the ladder rather than guessed.
    step = (mat["lum_hi"] - mat["lum_lo"]) / (PALETTE_LEVELS - 1)
    for cid in np.unique(lab):
        # SIZED AGAINST THE LADDER, and both directions have been overshot getting here. At
        # 0.75 of a step the break vanished under quantisation and every stone came out one
        # value; at 1.25 adjacent slabs landed three levels apart and the field read as a
        # high-contrast mosaic of broken tile. Half a step keeps most neighbours within one
        # level of each other — present, and not the loudest thing in the cell, which is what
        # "no single stone stands out from its neighbours" asks for.
        L[lab == cid] += rng.normal(0, step * 0.5)

    # GRAIN, at the amplitude measured off the donors and at two spatial scales. This is the
    # wave's actual contribution: the texture of the stone, carried as a statistic rather than
    # as a picture (§13.7 — conditioning supplies material, not architecture).
    # GRAIN, at the amplitude measured off the donors and at two spatial scales — but QUIETER
    # than the first pass. A seat read the surface as "fine dark speckle over the whole surface
    # reading as dust or grit", which is the base tile competing with the grit OVERLAY for the
    # same job. §8.3's division applies to texture as well as to shape: the tile carries the
    # material's tooth, the overlay carries the dust. Cut stone is fairly flat.
    amp = max(mat["grain_mad"], 1.0)
    L += wrap_noise(T, 8, rng) * amp * 0.34       # patchiness within a stone
    L += wrap_noise(T, 16, rng) * amp * 0.14      # a fine tooth, not speckle

    # JOINTS: darker because ENCLOSED, which is §6.5's own derivation ("joints, recesses and
    # undercuts sit darker because they are enclosed") and is direction-free, so it survives
    # §6.3. Grime along EVERY joint, not some — §8.1's "walked into a surface until it is part
    # of it" is distributed material; grime in one place would be a stain, which is incident.
    # Joints at a CONSISTENT value as well as a consistent width — a crack varies in depth
    # along its length, a mortar joint does not.
    L[joints] = stone_v * 0.62 + rng.normal(0, 1.0, int(joints.sum()))

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
    # CLUMPED AND SPARSER. At 0.16 flat the speckle was even enough to read as film grain over
    # the whole room rather than as dust lying somewhere — "it doesn't pool in joints, doesn't
    # gather at the wall bases". Cubing the density field makes the noise pick a corner of the
    # tile and mostly stay in it, and the lower coefficient stops the dust competing with the
    # stone for the eye.
    a = (rng.random((t, t)) < (dens ** 3) * 0.30).astype(float)
    return rgb_v, a * 0.45


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
def incident_repair(mat, rng, t=T):
    """A cracked slab PINNED FLAT with driven iron pins. §7.4's orc work, on the ground.

    §8.2.1's tier-one requirements name this family in its own words, banked from a blind seat
    that had never seen the clause:

        A floor-repair vocabulary. §7.4's orc work exists on walls and nowhere on the ground —
        "a cracked slab pinned flat with four driven iron pins, or a salvaged timber baulk
        dropped across a hole and worn smooth on its top edge."

    Two further independent seats asked for it unprompted in this session's own rounds — *"add
    orc repair to the ground itself: driven pins, a lashed timber, a hide patch"*, and *"there is
    no repair anywhere on the walkable ground ... for a place held for four hundred years by a
    company that repairs things endlessly, the floor is untouched by hands."* Three seats, three
    rounds, one finding, and a clause that already required it.

    THE SPLIT AND THE PINS ARE ONE OBJECT, deliberately. Four dots on a floor are four dots; four
    dots straddling a split are a repair. §7.3 — nothing on an orc-made object exists for
    appearance — so the pins sit where the work needed them and nowhere else.

    IRON, NOT TIMBER, and that is a palette decision rather than a preference. §5.4 LOCKED:
    warmth is reserved, and *"chroma is signal ... a saturated pixel should mean something
    happened; general richness is forbidden."* A salvaged timber baulk is the clause's other
    example and it would spend a hue. Whether the Boundary's floors are where that hue gets spent
    is a real design question and not a builder's to answer on a first landing round, so this
    family is achromatic — dark iron in grey stone — and the timber half is left unbuilt and
    named as unbuilt.
    """
    dark = mat["lum_lo"] * 0.38
    iron = mat["lum_lo"] * 0.30
    a = np.zeros((t, t))
    vals = np.zeros((t, t))

    horiz = rng.random() < 0.5
    pos = int(rng.integers(9, t - 9))
    lo, hi = int(rng.integers(4, 10)), int(rng.integers(t - 10, t - 4))
    wob = np.clip(np.cumsum(rng.normal(0, 0.5, t)), -2, 2)
    for i in range(lo, hi):
        j = int(round(pos + wob[i])) % t
        y, x = (j, i) if horiz else (i, j)
        a[y, x] = 1.0
        vals[y, x] = dark

    # Pins in pairs, straddling the split — driven either side of the break, which is what
    # pinning a slab flat actually requires.
    for k in range(2):
        at = lo + 3 + int((hi - lo - 6) * (0.15 + 0.6 * k) + rng.integers(-2, 3))
        at = max(lo + 1, min(hi - 2, at))
        j = int(round(pos + wob[min(at, t - 1)]))
        for side in (-3, 3):
            cy, cx = (j + side, at) if horiz else (at, j + side)
            for dy in range(2):
                for dx in range(2):
                    a[(cy + dy) % t, (cx + dx) % t] = 1.0
                    vals[(cy + dy) % t, (cx + dx) % t] = iron
    return vals, a


INCIDENT_FAMILIES = [("repair", incident_repair, 9, 0.035),
                     ("crack", incident_crack, 6, 0.11), ("chip", incident_chip, 5, 0.14),
                     ("wear", incident_wear, 6, 0.34), ("grit", incident_grit, 5, 0.85),
                     ("debris", incident_debris, 5, 0.07)]


def build_incident(fn, mat, rng):
    """A family builder returns (value, alpha). `value` is a scalar for a single-value mark, or
    a full field where a mark is made of more than one material — the repair's iron pins sit at a
    different value from the split they hold, and one object with two materials is what makes it
    read as a repair rather than as four dots."""
    v, a = fn(mat, rng)
    if np.isscalar(v) or np.ndim(v) == 0:
        rgb = np.zeros((T, T, 3), dtype=float)
        rgb[:] = np.array(colourise(np.array([[float(v)]]), mat["tint"])[0, 0])
    else:
        rgb = colourise(np.asarray(v, dtype=float), mat["tint"])
    return np.dstack([rgb, np.clip(a * 255, 0, 255)]).astype(np.uint8)


def build_occlusion(side, mat, rng, t=T):
    """CONTACT OCCLUSION at a wall edge — §12.1, RULED: form, legal, and REQUIRED.

    §12.1 (Rafe, 2026-08-26): *"a wall-top meeting floor without its occluded edge is not purity,
    it is a missing plane"*, and the composition spike measured the consequence — a lit wall top
    at 96 beside a lit floor at 122 with no boundary of any kind, and a blind critic that could
    not tell solid from walkable. `cannot-read`, twice.

    WHY IT IS BUILT HERE RATHER THAN LEFT TO THE RENDERER. `DungeonRenderer` already darkens
    wall-adjacent floor, by applying `DarkFloorModulate` — a flat 0.92 multiply — to the WHOLE
    CELL. That is contact occlusion drawn as a cell rather than as a boundary, and it fails
    §12.1's own test twice over:

      * its edge is the CELL's edge, so it is a hard 32px square step. §8.3.1: a treatment at a
        constant position within a tile becomes a lattice when tiled. A blind seat measured it
        without being told it existed — *"the torchlight steps down in hard-edged 64px squares
        aligned to the tile grid ... gradient magnitude spikes ~35% above background at a strict
        32px pitch ... the room reads as a spreadsheet of cells rather than a continuous floor."*
      * it does not answer to WHAT ADJOINS IT. The same 8% darkening lands on a cell with a wall
        to its north and a cell with a wall to its south-west. §12.1: *"what separates occlusion
        from a ring is whether the treatment answers to the geometry it sits on ... a uniform
        ribbon of constant width and constant value applied to every edge answers to nothing."*

    So this family draws it as the clause describes: a gradient fading inward from ONE named
    edge, placed only on the side a wall actually lies, so a cell in a corner gets two and a cell
    in open floor gets none. Direction-free as a material claim — it is darker BECAUSE ENCLOSED
    (§6.5's derivation), which is true from every azimuth, so it survives §6.3 exactly as the
    plane-boundary ruling says form does.

    The ramp's depth is jittered per row along the edge so the band is not a ruled stripe either
    — the same correction the channel's shoulders needed.
    """
    depth = 7.0
    a = np.zeros((t, t))
    jitter = np.cumsum(rng.normal(0, 0.6, t))
    jitter = np.clip(jitter - jitter.mean(), -1.6, 1.6)
    for i in range(t):
        d = max(2.0, depth + jitter[i])
        for k in range(t):
            v = max(0.0, 1.0 - k / d)
            v = v * v                       # falls away fast, as an enclosed edge does
            if side == "N":
                a[k, i] = max(a[k, i], v)
            elif side == "S":
                a[t - 1 - k, i] = max(a[t - 1 - k, i], v)
            elif side == "W":
                a[i, k] = max(a[i, k], v)
            else:                            # "E"
                a[i, t - 1 - k] = max(a[i, t - 1 - k], v)
    rgb = np.zeros((t, t, 3), dtype=float)
    rgb[:] = np.array(colourise(np.array([[mat["lum_lo"] * 0.30]]), mat["tint"])[0, 0])
    return np.dstack([rgb, np.clip(a * 0.72 * 255, 0, 255)]).astype(np.uint8)


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

    # --- contact occlusion, §12.1 --------------------------------------------------------------
    print("\nCONTACT OCCLUSION — §12.1, one per wall edge, placed by adjacency")
    rng_occ = np.random.default_rng(a.seed + 991)
    manifest["occlusion"] = []
    for i, side in enumerate(("N", "E", "S", "W")):
        img = build_occlusion(side, mat, rng_occ)
        tid = OCCLUSION_IDS[i]
        p = os.path.join(a.out, "tier1_floor_%d.png" % tid)
        Image.fromarray(img).save(p)
        cov = float((img[..., 3] > 40).mean())
        print("  %-2s id %d  coverage %.3f" % (side, tid, cov))
        manifest["occlusion"].append(dict(id=tid, side=side, file=os.path.basename(p),
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
    print("\nORIENTED VARIANTS — %d base tiles x 8 orientations of the square" % len(manifest["base"]))
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

    # EVERY id in the finished manifest, checked. The block constants above are asserted at
    # import; this catches the case they cannot — a family growing past its block at run time.
    all_ids = [e["id"] for k in ("base", "channel", "occlusion", "incident", "oriented")
               for e in manifest.get(k, [])]
    if len(set(all_ids)) != len(all_ids):
        dupes = sorted({i for i in all_ids if all_ids.count(i) > 1})
        raise SystemExit("REFUSING: the composed family assigns the same id twice: %s. A tile "
                         "resolving to two different images renders something plausible and says "
                         "nothing (LOOP-PROCESS §4.2)." % dupes)
    print("\nid check: %d ids, all distinct, %d..%d" % (len(all_ids), min(all_ids), max(all_ids)))

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
