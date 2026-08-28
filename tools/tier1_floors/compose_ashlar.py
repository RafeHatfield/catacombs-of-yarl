#!/usr/bin/env python3
"""THE COURSE-ALIGNED ASHLAR FAMILY — rulings (1) and (2), built as one rebuild.

WHAT THE TWO RULINGS ASKED FOR

  (1) The tint lattice is the motif trap in the VALUE domain. §8.3.1 extends: constant extent is
      constant position. Fix it STRUCTURALLY by assigning value at the STONE level from the
      family distribution, so that the tile boundary loses its special status. The 2.95x residue
      is to be superseded by construction, not tuned away.

  (2) Q1 returns via course-aligned edge families — ashlar bond as family structure, offsets per
      family. The crossing-variance floor still binds.

Both land in one geometry, because they are the same problem seen twice. The crossing-joint
construction had no shared name for a stone: a stone straddling a cell boundary was two regions
in two tiles, and the two tiles could not agree what it was worth. Every value fix was therefore
a blend, a reach, a falloff — a way of HIDING a disagreement rather than removing it. An ashlar
bond removes it, because in an ashlar bond every stone has an address.

WHY COURSING SOLVES THE ADDRESSING PROBLEM, AND THE CORNER THAT FORCED IT

Consider the four tiles meeting at one grid corner. Tile (x,r) knows the families of its own four
boundaries. Its eastern neighbour shares exactly ONE of them, V(x+1,r). Its southern neighbour
shares exactly one, H(x,r+1). Its DIAGONAL neighbour, (x+1,r+1), shares NOTHING.

So a stone covering a grid corner is seen by four tiles that have no common data, and there is no
scheme by which they can agree on its value. Measured on the crossing-joint geometry: 27 of 77
stones spanned a cell boundary with no shared key at all, holding 19.9% of stone pixels. That is
not a flaw in the keying idea — it is a theorem about the corner.

  THEREFORE: NO STONE MAY CONTAIN A GRID CORNER. A joint must pass through every one.

Coursing supplies that for free. With bed joints at every world y = 16k — half of them landing on
a horizontal tile boundary and half exactly between — a bed joint passes through every grid corner
because 32 is a multiple of 16. No stone spans a horizontal tile boundary; a stone spans at most
ONE vertical boundary; and the two tiles either side of a vertical boundary DO share its family.
Every stone is addressable. The key is total, and K becomes a runtime value rather than a
multiplier on the tile count.

THE CONTINUITY TEST, WHICH GOVERNS HERE

Courses at constant world-y pattern-match §8.3.1 and must not be waved through on the strength of
the bond's name. The governing test is CONTINUITY: a line that travels across boundaries is
material; a treatment locked to boundaries is a frame. Bed joints travel — they run unbroken
across every vertical boundary — and, decisively, THE COURSE AT THE TILE BOUNDARY IS
INDISTINGUISHABLE FROM THE COURSE HALFWAY UP THE TILE. Both are bed joints of one 16px lattice.
The coursing hides the grid rather than revealing it, and `field_ashlar.grid_hiding` measures
exactly that: if the boundary row were special, its joint density would differ from the mid row.

WHAT EACH FAMILY DOES — every one of the four does real work

  fW = V(x,r)      head-joint offsets just EAST of the west boundary (table A), and, because tile
                   x-1's east family IS this same family, the offset of tile x-1's interior joint
                   (table MV) — which is what lets tile x place the far edge of the stone that
                   spans their shared boundary.
  fE = V(x+1,r)    this tile's interior head-joint offsets (table MV).
  fN = H(x,r)      the arris profile of the bed joint ON the northern boundary. Both tiles either
                   side draw that line and must agree about it.
  fS = H(x,r+1)    the same for the southern boundary.

Arris profiles are built to return to zero at both ends of a tile span, so a profile change at a
vertical boundary is invisible — continuity by construction rather than by blending.

WHAT THE TILE DELIBERATELY DOES NOT CARRY: ANY MATERIAL AT ALL

The tiles are THE BOND AND NOTHING ELSE — joints, and flat stone between them. Both halves of the
material, value and grain, are applied at compose time from the stone's world address.

That was not the first plan. The first plan kept the grain in the tile and addressed only the
value, and it measured a boundary step of 2.793 where ruling (1) demands 1.00. Switching the grain
off dropped it to EXACTLY 0.000, which named the culprit precisely: `wrap_noise` makes a field
that wraps against ITSELF, so two adjacent tiles drew unrelated material and the seam was a
texture jump. Crossfading each tile's grain between two family-keyed fields got to 0.771 and left
tile interiors measurably rougher than tile edges — a smaller lattice, still a lattice.

Grain belongs to the STONE. A stone is one piece of quarried rock; its grain runs through it and
STOPS AT ITS JOINTS, which is the one place a discontinuity is invisible because a joint is
already there. So each stone draws a grain patch chosen by its address and samples it in
STONE-LOCAL coordinates — coordinates both tiles either side of a boundary compute identically,
because the stone's origin is fixed by the boundary family they share and not by where either
tile happens to have wavered its joint. Value and grain are then the same construction applied
twice, and the tile has nothing left in it that a neighbour could disagree with.

AND SO THERE IS NO CHANNEL TILE SET

Wear is a property of the STONE, not of the tile: the trodden channel is stones whose grain has
been walked off and whose value spread has closed up. It needs no second set of 81 tiles, and it
no longer has a straight edge on the tile lattice — the channel now ends where a stone ends,
which is what §8.2.1 was asking for and what a per-tile channel could never give.

THE ADDITIVE-REMAP LAW, ENFORCED BY THE MASK RATHER THAN BY CARE

Offsets land on stone faces only; joints are never touched, because the ladder's bottom is where
the occlusion lives (measured: an offset applied to every pixel clips 17.02% of them at the floor
of the palette; applied to stone faces only, 0.00%). The law is carried by the CLASS MASK: joints
are class 0 and class 0's offset is defined to be exactly zero. A remap cannot touch a joint
without first misreading the mask.
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
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402

T = 32
# FIVE, NOT THREE, AND THE THIRD FAMILY COUNT A SEAT HAS RULED ON.
#
# Three families put only 3^4 = 81 joint skeletons in the world, and a blind seat measured the
# consequence directly:
#
#   "The joint layout has a hard 64px period. Duplicate 32x32 patches across the whole floor: the
#    top matches are all at displacement exactly (64,0) or (0,64), correlating 0.99+."
#
# Two cells share a skeleton when all four of their families agree. Horizontally adjacent cells
# already share one boundary by construction, so at three families the other three agree once in
# 27 — about 2% of adjacent pairs after the merges are accounted for, which over a 74-cell room is
# the two or three exact duplicates the seat found and named. At five families it is once in 125.
#
# This is the one axis where more is simply better and the cost is linear: 625 atlases instead of
# 81, about 2 MB, a minute to generate. The alternative — more joint POSITIONS per family — is not
# available, because a position must be agreed by both tiles either side of a boundary and the
# boundary's family is the only thing they share. Position variety IS family count.
FAMILIES = 5
COURSES = 2                        # courses fully inside one tile

# WHERE THE INTERIOR BED JOINT SITS, AND WHY IT MOVES.
#
# The first version put it dead centre, so every course in the world was 16px tall and a bed joint
# ran unbroken across the whole map at every 16px. The blind seat's loudest finding was exactly
# that: *"the floor reads as a stack of horizontal stripes before it reads as stone"*, and
# *"real floors under four hundred years of traffic do not hold a ruled line like that."*
#
# The joint at the TILE BOUNDARY cannot move — the corner theorem requires one through every grid
# corner, or a stone spans a horizontal boundary and becomes unaddressable. But the INTERIOR one
# is free, and moving it costs nothing: it is chosen per TILE ROW, so every tile in a row agrees
# and the joint stays continuous across every vertical boundary, while successive rows give
# courses of genuinely different heights. The 16px stripe becomes a bond.
SPLITS = [[16, 16], [11, 21], [21, 11], [13, 19]]
SPLIT_SALT = 3005


def row_split(r, seed):
    """Which course split this TILE ROW uses. A property of the row, so a whole row agrees."""
    return mix(0, r, SPLIT_SALT + seed) % len(SPLITS)


def course_rows(split_i, c):
    """(first row, last row exclusive) of course c under this split, excluding its bed joints."""
    a = SPLITS[split_i][0]
    return (1, a - 1) if c == 0 else (a + 1, T - 1)
ASSETS_REL = "src/Presentation/assets/tier1_ashlar"
ASSETS = os.path.join(REPO, ASSETS_REL)

BASE_ID0 = 10100

HORIZ, VERT = 101, 202             # boundary-lattice salts
SPAN, INTERIOR = 3001, 3002        # stone-address salts
DROP, CLUSTER = 3003, 3004         # merged-stone and value-cluster salts
CLUSTER_TABLE = [-1, 0, 0, 1]      # the coarse patch bias; more zeros than not, so most of the
                                   # field keeps the family median and the patches read as runs

# HEAD-JOINT TABLES, one row per family, one column per course. The two courses differ so that
# head joints do not stack between courses — that offset IS the bond. Values chosen so every
# stone lands between 10 and 22 px wide against a 14px course: ashlar proportions, varied enough
# to read as cut rather than cast.
# A stone SPANNING a boundary is bounded by A[f][c] on one side and by MV[f][c] on the other —
# the SAME family both times, because tile x-1's east family is tile x's west family. So its width
# is 32 + A[f][c] - MV[f][c], and the first draft made that difference -16 for every family: every
# spanning stone came out exactly 16px wide, everywhere on the map. A constant extent is a
# constant position (§8.3.1 as ruling (1) extended it), so the tables are now chosen to vary the
# spanning width as well as the interior one, under two constraints:
#   min(MV[.][c]) - max(A[.][c]) >= 9   so no interior stone is a sliver
#   32 + A[f][c] - MV[f][c]      >= 10  so no spanning stone is either
# Five rows now, under the same two constraints, and they bind hard at T=32: interior width is
# MV[fe] - A[fw] and must clear 9, so max(A) <= min(MV) - 9; spanning width is 32 + A[f] - MV[f]
# with the SAME family both times and must clear 10, so MV[f] - A[f] <= 22. Five distinct values
# each is very nearly all this tile size will hold.
A_TABLE = [[3, 8], [6, 11], [9, 14], [13, 16], [16, 5]]
# MV is capped at 29 so that a head joint plus its 2px width plus its waver cannot reach the
# tile's own edge column. At 30 it did, which put a short vertical joint hard against the boundary
# in every tile whose east family was 1 — legal by agreement (both tiles place it identically) but
# a line at a constant position all the same, and the continuity instrument saw it before the eye
# would have.
MV_TABLE = [[25, 26], [26, 29], [29, 25], [27, 28], [28, 27]]

# ARRIS PROFILES for the bed joints. Each returns to 0.0 at t=0 and t=1 so that neighbouring
# spans meet without a step — continuity by construction, which is what lets fN and fS vary at
# all without drawing a frame at the vertical boundaries.
def arris_profile(f, t):
    if f == 0:
        return np.sin(np.pi * t) * 0.55
    if f == 1:
        return np.sin(2 * np.pi * t) * 0.40
    return np.sin(np.pi * t) ** 3 * 0.75


# =================================================================================================
# GRAIN THAT BELONGS TO A STONE
# =================================================================================================
#
# A bank of grain patches. A stone picks one by its address and samples it in stone-local
# coordinates, so the two tiles either side of a boundary sample consecutive columns of the same
# patch and the material runs through the stone unbroken. The bank is finite, but it is indexed by
# a world address rather than by anything on the tile grid, so a repeat lands where the addresses
# repeat and not on any lattice.
GRAIN_SALT = 5501
GRAIN_BANK = 64
_BANK = {}


def grain_patch(key, cells, seed):
    """One stone's grain, chosen by address. Wider than any stone so no stone runs off it."""
    i = key % GRAIN_BANK
    k = (i, cells, seed)
    if k not in _BANK:
        rng = np.random.default_rng(seed + GRAIN_SALT + i * 7919 + cells * 31)
        g = CF.wrap_noise(2 * T, cells, rng)
        # QUANTISED THE WAY IT SHIPS. The bank leaves here as a PNG, one byte per sample at
        # 1/64 luminance, and composing against the unquantised float meant the composer and the
        # engine disagreed by a whole ladder rung on 50 pixels of an 8x8 field, wherever a sample
        # sat near a rung boundary. The composer must compose with what ships, not with what it
        # happened to have in memory.
        _BANK[k] = (np.clip(np.round(g * 64 + 128), 0, 255) - 128) / 64.0
    return _BANK[k]


def stone_origin(fw, fe, kind, c, drop=0):
    """Stone-local x = 0, expressed in this tile's local coordinates.

    A SPANNING stone is measured from ITS BOUNDARY, never from its own left edge. That looks like
    a detail and is not: with a head joint sanded away, the stone spanning a boundary can begin
    back in the previous tile at an offset chosen by a family THE FAR TILE CANNOT SEE. Measured
    from the boundary, the west tile's columns run 0..31 and the east tile's 32.. — contiguous,
    and computed from nothing but which side of the boundary the tile is on.
    """
    if kind == 0:                        # this tile is EAST of the boundary it spans
        return -T
    if kind == 2:                        # this tile is WEST of the boundary it spans
        return 0
    if drop == 2:                        # merged eastward: also a spanning stone
        return 0
    return A_TABLE[fw][c]                # interior; nobody else can see it


def course_origin_y(split_i, c):
    """Stone-local y = 0 for this course. Moves with the split, like everything else about it."""
    return course_rows(split_i, c)[0]


def stone_kind_address(kind, drop):
    """Which address a class carries once joints have been sanded away.

    With the MV joint gone, the stone labelled `interior` is not interior any more — it runs on
    into the tile to the east, and must be addressed by THAT boundary or the two tiles will paint
    it differently. This one line is the difference between a merge and a seam.
    """
    if kind == 1 and drop == 2:
        return 2
    return kind


def _i32(v):
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def mix(x, y, salt):
    """The engine's hash, reproduced bit-for-bit. Cross-checked at load from the manifest."""
    h = _i32(x * 7919 + y * 104729 + salt * 15485863)
    h = _i32(h ^ (h >> 13))
    h = _i32(h * 1274126177)
    h = _i32(h ^ (h >> 16))
    return h & 0x7FFFFFFF


def edge_family(a, b, salt, seed):
    return mix(a, b, salt + seed) % FAMILIES


def tile_index(n, e, s, w):
    return ((n * FAMILIES + e) * FAMILIES + s) * FAMILIES + w


def cross_check_vector(seed, n=64):
    out = []
    for i in range(n):
        x, y = i % 17, (i * 7) % 21
        out.append(dict(x=x, y=y, salt=HORIZ, family=edge_family(x, y, HORIZ, seed)))
        out.append(dict(x=x, y=y, salt=VERT, family=edge_family(x, y, VERT, seed)))
    return out


# ---- THE STONE ADDRESS ------------------------------------------------------------------------
#
# Two kinds of stone and two salts, and the whole of ruling (1) rests on the first one being
# computable from both sides.
#
#   SPANNING   the stone straddling vertical boundary V(x,r) in global course k. Tile x calls it
#              its west stone and tile x-1 calls it its east stone, and BOTH ADDRESS IT BY THE
#              BOUNDARY, so both get the same key without needing to know anything about each
#              other's other three families.
#   INTERIOR   the stone wholly inside tile (x,r), course k. Nobody else can see it, so its
#              address is the tile's own.

def stone_key_span(bx, course_k, seed):
    return mix(bx, course_k, SPAN + seed)


def stone_key_interior(tx, course_k, seed):
    return mix(tx, course_k, INTERIOR + seed)


# ---- MERGED STONES ------------------------------------------------------------------------------
#
# Two head joints per course in every tile gives every stone the same height and a width from a
# short list, and the field came back reading as BRICKWORK — session one's failure mode in its
# third form. Coursing is ruled in; a brick rhythm is not, and the rhythm is what a uniform stone
# does, not what a course does.
#
# So a tile may SAND ONE HEAD JOINT AWAY, merging two stones into one wide one. Exactly one, never
# both: dropping both would leave a stone spanning two vertical boundaries, which is unaddressable
# (three tiles see it and only two of them share anything), and that is the constraint that decides
# this rather than taste. The choice is keyed on the tile's own column and course, so the tile to
# the west can work out whether tile x kept its A joint — it needs to, because that joint is the
# far edge of the stone they share.

def drop_choice(tx, course_k, seed):
    """0 = keep both, 1 = drop the A joint, 2 = drop the MV joint."""
    d = mix(tx, course_k, DROP + seed) % 7
    return 1 if d == 0 else (2 if d == 1 else 0)


def cluster_bias(bx, course_k, seed):
    """A coarse value bias shared by a patch of neighbouring stones.

    Independent per-stone values read as a checkerboard: real paving is quarried in batches and
    laid in runs, so light and dark come in PATCHES. The bias is a function of a coarse bucket of
    the same world address the stone already uses, so neighbours agree about it exactly as they
    agree about everything else.
    """
    return CLUSTER_TABLE[mix(bx // 3, course_k // 2, CLUSTER + seed) % len(CLUSTER_TABLE)]


# The value ladder the offsets are drawn from. Whole ladder steps only, so an offset stone is
# still ON the palette (§5.1 is a zero-mercy gate and §4.3 forbids anti-aliasing, so a value that
# is not a ladder level is not a legal value). The distribution is centred and short-tailed: most
# stones sit at the family's median and a few are a step or two off it, which is what a quarried
# course looks like and is also what keeps the clipping measured at 0.00% low / 1.78% high.
OFFSET_STEPS = [-2, -1, -1, 0, 0, 0, 0, 1, 1, 2]


# HOW MUCH A TRODDEN STONE LOSES. Named here, carried in the manifest, and reproduced by the
# engine, because these are the only three numbers that make the channel visible at all and a
# blind seat could not find it: *"There is no wear lane, no debris drift, no scuff, no stain, no
# difference in joint width, nothing that says traffic went one way."*
#
# Every one of them is a SUBTRACTION. §8.2.1 is binding — polish signals by ABSENCE, never by
# brightness, because under a carried lamp brightness is what the light is saying and a lift is
# read as the torch. So a trodden stone has its grain walked off, its value closed up toward the
# family median, and its arris rounded so the joint beside it holds less shadow. Nothing is added.
WEAR_GRAIN = 0.08          # grain amplitude multiplier on a trodden stone
WEAR_SPREAD = 0.20         # value-offset multiplier on a trodden stone
WEAR_ARRIS = 0.45          # how far a joint beside trodden stone rises toward the stone


def stone_offset(key, step, worn=False, bias=0):
    """Additive value offset, in luminance. WHOLE LADDER STEPS ONLY — a value off the ladder is
    not a legal value (§5.1 zero-mercy, §4.3 no anti-aliasing), so the bias is added before the
    multiply and clamped in steps, never blended in afterwards."""
    k = OFFSET_STEPS[key % len(OFFSET_STEPS)] + bias
    k = max(-3, min(3, k))
    return k * step * (WEAR_SPREAD if worn else 1.0)


def build_tile(n, e, s, w, mat, seed, drops=(0, 0), split_i=0):
    """One ashlar tile: two courses, three bed lines, two head joints per course. THE BOND ONLY.

    `drops` is one entry per course: 0 keep both head joints, 1 sand the A joint away, 2 sand the
    MV joint away. It comes from the world address rather than from the four families, so the tile
    SET is still 81 and the merge is a compose-time decision — the same division of labour as the
    value and the grain.

    Returns (rgb, joints, cls, L). L is the QUANTISED LUMINANCE, handed back rather than
    recovered from the rgb: the shipped atlas stores an exact ladder index, and a caller that
    re-derived luminance from the colourised pixels disagreed with it on 0.5% of the field by
    about a ladder step. Same construction, two arithmetics, one of which does not ship.

    `cls` is the class mask everything else is keyed on — 0 for
    joints, then 1..6 for (course, west-spanning | interior | east-spanning). Where a joint has
    been sanded away the two classes it separated become one, and the merged stone takes the
    address of the boundary it still spans.
    """
    rng = np.random.default_rng(seed + tile_index(n, e, s, w) * 7919)
    stone = mat["lum_median"]
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)
    L = np.full((T, T), stone, dtype=float)
    joints = np.zeros((T, T), dtype=bool)
    cls = np.zeros((T, T), dtype=np.uint8)

    # ---- BED JOINTS. Straight, and that is a decision rather than an omission.
    #
    # A wavering bed line would have to waver identically in the tile above and the tile below,
    # and identically to its left and right, and the only data all four of those tiles share is
    # nothing (see the corner theorem above). A bed line that wobbles per-tile is a bed line that
    # jogs at every boundary — which is precisely the frame the continuity test exists to catch.
    # So the line runs true and the WORK shows in its arris: depth varies along it, and it is
    # chipped where head joints meet it.
    #
    # Line at world y=Y occupies rows Y-1 and Y, so the boundary lines are drawn half by this
    # tile and half by its neighbour and come out 2px like every other one. No line is thicker or
    # thinner for being on a boundary — the first place a grid would show.
    t_axis = np.arange(T) / float(T - 1)
    bed_rows = []
    for k, Y in enumerate((0, SPLITS[split_i][0], T)):
        if k == 0:
            prof, rows = arris_profile(n, t_axis), [0]
        elif k == COURSES:
            prof, rows = arris_profile(s, t_axis), [T - 1]
        else:
            # Interior line: needs to agree only across the VERTICAL boundaries, so it runs from
            # a depth set by the west family to one set by the east family.
            prof = (1 - t_axis) * (0.30 + 0.20 * w) + t_axis * (0.30 + 0.20 * e)
            rows = [Y - 1, Y]
        for r in rows:
            # Bounds-guarded: a split whose interior line lands on the far boundary (which is how
            # the one-course plant is built) asks for row T, and an unguarded write there is an
            # IndexError rather than a floor. Cheap, and it keeps degenerate splits expressible —
            # which matters, because the plant for the corner theorem's own cost IS a degenerate
            # split.
            if 0 <= r < T:
                bed_rows.append((r, prof))

    # ---- HEAD JOINTS and the class map, course by course.
    for c in range(COURSES):
        y0, y1 = course_rows(split_i, c)
        xa = A_TABLE[w][c]
        xm = MV_TABLE[e][c]
        drop = drops[c]
        # STRAIGHT. The first version wandered each head joint down its length, and the seat found
        # the wander before it found the floor: *"the same little two-step zigzag jog appears on
        # vertical seams at (420,218), (450,245), (345,150), (485,60), (430,335)... it is the SAME
        # shape every time, which converts it from irregularity into a motif."*
        #
        # That is §8.3.1 exactly. A wander is an INCIDENT, the tile is a PARENT, and an incident
        # baked into a parent becomes a motif the moment the parent tiles. The wander was seeded
        # per tile index, so every tile sharing four families drew the identical jog, everywhere
        # on the map, forever. There is no amplitude of it that is safe.
        #
        # So the joints run true and the irregularity comes from the things that are addressed by
        # WORLD POSITION and therefore cannot repeat on the grid: stone width (9..23px), the
        # merges, the course split, the value, the grain.
        for yy in range(y0, y1):
            ja, jm = xa, xm
            if drop == 1:
                cls[yy, :jm] = 1 + c * 3 + 0               # merged: spans the WEST boundary
                cls[yy, jm:] = 1 + c * 3 + 2
                heads = (jm,)
            elif drop == 2:
                cls[yy, :ja] = 1 + c * 3 + 0
                cls[yy, ja:] = 1 + c * 3 + 1               # merged: runs to the EAST boundary
                heads = (ja,)
            else:
                cls[yy, :ja] = 1 + c * 3 + 0               # spans the WEST boundary
                cls[yy, ja:jm] = 1 + c * 3 + 1             # interior to this tile
                cls[yy, jm:] = 1 + c * 3 + 2               # spans the EAST boundary
                heads = (ja, jm)
            for x in heads:
                for xx in (x, x + 1):
                    if 0 <= xx < T:
                        joints[yy, xx] = True

    for r, prof in bed_rows:
        joints[r, :] = True

    # ---- MATERIAL. Grain only; the tiles carry NO stone-to-stone value. See the docstring.
    # ---- JOINT VALUES. §6.5: the joint is dark BECAUSE ENCLOSED, so its depth is the form.
    # Depth does NOT vary with wear. A trodden channel that changed its joint depth would change
    # it along a straight line on the tile grid, because wear is decided per cell — a lattice
    # wearing a channel's name. The channel signals through its STONES, by absence of grain.
    # Head and bed joints sit at the SAME depth. They are equally enclosed, so §6.5 gives them
    # the same value; drawing the bed deeper was what tipped the field into horizontal banding.
    depth = np.full((T, T), 0.42, dtype=float)
    for r, prof in bed_rows:
        depth[r, :] = 0.44 - prof * 0.09
    L = np.where(joints, stone * depth + rng.normal(0, 1.0, (T, T)), L)

    L = CF.quantise(L, mat["ladder"])
    cls[joints] = 0                                  # the additive law, made structural
    return CF.colourise(L, mat["tint"]).astype(np.uint8), joints, cls, L


def stone_check_vector(seed, n=48):
    """Sample (tile x, course k, class) -> the offset the composer will apply, in LADDER STEPS.

    The engine reproduces this or refuses to lay the floor. The edge-family vector already
    guarantees the two agree about the BOND; this one guarantees they agree about the MATERIAL,
    which is now the larger half of the family and the half a silent disagreement would show in
    as a value seam at every tile boundary.
    """
    out = []
    for i in range(n):
        x, k = i % 13, (i * 5) % 19
        for kind in (0, 1, 2):
            drop = drop_choice(x, k, seed)
            addr = stone_kind_address(kind, drop)
            bx = x + 1 if addr == 2 else x
            key = stone_key_span(bx, k, seed) if addr in (0, 2) \
                else stone_key_interior(x, k, seed)
            steps = max(-3, min(3, OFFSET_STEPS[key % len(OFFSET_STEPS)]
                                + cluster_bias(bx, k, seed)))
            out.append(dict(x=x, k=k, kind=kind, drop=drop, steps=steps))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=ASSETS)
    a = ap.parse_args()

    # The constant-pitch plant appends a degenerate split to this table at runtime. If a caller
    # ever runs the plants and the composer in one interpreter, that split would be written into
    # the manifest and shipped to the engine as if it were art.
    if SPLITS != [[16, 16], [11, 21], [21, 11], [13, 19]]:
        raise SystemExit("REFUSING: SPLITS is not the declared table — %s. Something mutated it; "
                         "a manifest written now would ship a split nobody authored." % SPLITS)

    src = json.load(open(os.path.join(CF.ASSETS, "MANIFEST.json")))
    mat = src["material"]
    os.makedirs(a.out, exist_ok=True)
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)

    man = dict(family="boundary_floor_ashlar_v1", commit=FL.git_commit(), seed=a.seed,
               material=mat, families=FAMILIES, tile=T, courses=COURSES, splits=SPLITS,
               a_table=A_TABLE, mv_table=MV_TABLE,
               salts=dict(horizontal=HORIZ, vertical=VERT, span=SPAN, interior=INTERIOR,
                          drop=DROP, cluster=CLUSTER, split=SPLIT_SALT),
               offset_steps=OFFSET_STEPS, cluster_table=CLUSTER_TABLE, ladder_step=round(step, 3),
               edge_family_check=cross_check_vector(a.seed),
               grain_bank=GRAIN_BANK, donors=src.get("donors", []), base=[],
               classes={"0": "joint — offset is defined zero, never remapped",
                        "1": "course 0, spans the WEST boundary", "2": "course 0, interior",
                        "3": "course 0, spans the EAST boundary",
                        "4": "course 1, spans the WEST boundary", "5": "course 1, interior",
                        "6": "course 1, spans the EAST boundary"},
               law=("ruling (1): stone value assigned at the stone from a shared address, so the "
                    "tile boundary has no special status. ruling (2): course-aligned families, "
                    "ashlar bond as family structure. §8.3.1 continuity test governs the "
                    "coursing: bed joints travel and the boundary course is indistinguishable "
                    "from the mid-tile course."))

    print("COURSE-ALIGNED ASHLAR — %d families/orientation, %d combinations"
          % (FAMILIES, FAMILIES ** 4))
    print("  courses: %d per tile, splits %s, bed joint through every grid corner"
          % (COURSES, SPLITS))
    print("  head joints: A=%s  MV=%s" % (A_TABLE, MV_TABLE))
    print("  material: median %.1f, ladder step %.2f" % (mat["lum_median"], step))
    print("  tiles carry the BOND ONLY; value and grain are applied per stone at compose time")

    interior, spanning = [], []
    for c in range(COURSES):
        for fw in range(FAMILIES):
            spanning.append(T + A_TABLE[fw][c] - MV_TABLE[fw][c])
            for fe in range(FAMILIES):
                interior.append(MV_TABLE[fe][c] - A_TABLE[fw][c])
    print("  stone widths: interior %d..%d, spanning %d..%d, shortest course %dpx"
          % (min(interior), max(interior), min(spanning), max(spanning), min(min(x) for x in SPLITS) - 2))
    if min(interior) < 9 or min(spanning) < 9:
        raise SystemExit("REFUSING: a stone narrower than 9px is a sliver, not a stone.")
    if len(set(spanning)) == 1:
        raise SystemExit("REFUSING: every spanning stone is the same width — constant extent is "
                         "constant position (§8.3.1, ruling (1)).")

    # ---- ATLASES, not 729 loose files.
    #
    # A tile now varies with its four families AND with which head joints have been sanded away
    # (3 choices per course, 9 per tile), which would be 729 bond images and 729 class masks. They
    # ship instead as 81 atlases of 3x3, one per family combination, with the LUMINANCE in R and
    # the CLASS in G — the engine needs both for every pixel and loading them as one texture means
    # they cannot be mismatched.
    for n in range(FAMILIES):
        for e in range(FAMILIES):
            for s_ in range(FAMILIES):
                for w in range(FAMILIES):
                    idx = tile_index(n, e, s_, w)
                    at = np.zeros((6 * T, 6 * T, 3), dtype=np.uint8)
                    for sp in range(len(SPLITS)):
                        for d0 in range(3):
                            for d1 in range(3):
                                cell_i = sp * 9 + d0 * 3 + d1
                                cr, cc = cell_i // 6, cell_i % 6
                                _img, _j, cls, L = build_tile(n, e, s_, w, mat, a.seed,
                                                              (d0, d1), sp)
                                # R carries the LADDER INDEX, not a luminance, and it is taken
                                # from the composer's own quantised L rather than reconstructed
                                # from the colourised pixels. Reconstruction was off by a rung on
                                # 0.5% of the field — a seam living in the gap between the tool
                                # and the game, where none of the field instruments look.
                                lad = np.array(mat["ladder"])
                                li = np.abs(L[..., None] - lad[None, None, :]).argmin(axis=-1)
                                cell = at[cr * T:(cr + 1) * T, cc * T:(cc + 1) * T]
                                cell[..., 0] = li
                                cell[..., 1] = cls
                    p = os.path.join(a.out, "tier1_ashlar_%d.png" % (BASE_ID0 + idx))
                    Image.fromarray(at).save(p)
                    man["base"].append(dict(id=BASE_ID0 + idx, n=n, e=e, s=s_, w=w,
                                            file=os.path.basename(p), sha256=FL.sha256_file(p)))
    print("  atlases: %d files, 6x6 of %dpx (4 course splits x 9 merge cases), "
          "R=ladder index G=stone class" % (len(man["base"]), T))

    # ---- THE GRAIN BANK, one file. 8x8 patches of 64px, R and G carrying the two scales.
    bank = np.zeros((8 * 2 * T, 8 * 2 * T, 3), dtype=np.uint8)
    for i in range(GRAIN_BANK):
        r, c = divmod(i, 8)
        for ch, cells in ((0, 8), (1, 16)):
            g = grain_patch(i, cells, a.seed)
            bank[r * 2 * T:(r + 1) * 2 * T, c * 2 * T:(c + 1) * 2 * T, ch] = \
                np.clip(np.round(g * 64 + 128), 0, 255)     # g is already bank-quantised
    bp = os.path.join(a.out, "tier1_ashlar_grain.png")
    Image.fromarray(bank).save(bp)
    man["grain_file"] = os.path.basename(bp)
    man["grain_encoding"] = "value = (channel - 128) / 64; R = 8-cell scale, G = 16-cell scale"
    man["atlas_encoding"] = ("6x6 of 32px; cell = split*9 + drop0*3 + drop1, row-major. "
                             "R = index into ladder, G = stone class 0..6")
    man["grain_scales"] = dict(coarse=0.34, fine=0.14, worn_multiplier=WEAR_GRAIN)
    man["wear"] = dict(grain=WEAR_GRAIN, spread=WEAR_SPREAD, arris=WEAR_ARRIS,
                       law="every term is a subtraction; §8.2.1 forbids signalling polish by "
                           "brightness, so nothing is added anywhere")
    man["grain_amp"] = round(max(mat["grain_mad"], 1.0), 4)
    man["stone_check"] = stone_check_vector(a.seed)
    print("  grain bank: %d patches in one %dx%d file" % (GRAIN_BANK, bank.shape[1], bank.shape[0]))
    print("  stone cross-check: %d samples the engine must reproduce" % len(man["stone_check"]))

    ids = [e["id"] for e in man["base"]]
    if len(set(ids)) != len(ids):
        raise SystemExit("REFUSING: duplicate ids in the ashlar family.")

    mp = os.path.join(a.out, "MANIFEST.json")
    with open(mp, "w") as f:
        json.dump(man, f, indent=1)
    print("\nid check: %d ids, all distinct, %d..%d" % (len(ids), min(ids), max(ids)))
    print("written: %s" % os.path.relpath(mp, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
