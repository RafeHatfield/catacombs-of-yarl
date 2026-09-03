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
import field_laws as FL
import route_polyline as RP          # noqa: E402

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
CRACK = 3006                       # the field-scale crack network
MARKS = 3007                       # the worked surface of a stone
WEAR = 3008                        # the differential-wear field
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


# =================================================================================================
# THE CRACK NETWORK, AT FIELD SCALE
# =================================================================================================
#
# RULING: incident moves to field scale, minimum readable extent, per-tile marks retired.
#
# The overlay system it replaces was measured before it was replaced: over the lit ground it
# changed 48.72% of pixels but only 7.21% by a whole ladder rung, in 127 connected marks with a
# MEDIAN SIZE OF FOUR PIXELS. At the review build's 2x display that is a two-by-two speck. Blind
# seats read it as "the pepper", "static before it reads as stone", and — decisively — reported
# "No cracks. Not one. Across ~140 visible blocks" in a capture whose log said event=44.
#
# A crack is not a decal. It is one event that happened once, and it is long. So:
#
#   * A crack belongs to an ANCHOR TILE and runs for whole tiles beyond it. Both the anchor's own
#     cell and every cell it crosses generate the SAME polyline from the SAME world address, so it
#     is continuous across tile boundaries by the same construction that makes a stone continuous.
#   * MINIMUM READABLE EXTENT is a refusal, not a preference: a crack shorter than
#     CRACK_MIN_TILES is not drawn at all. A mark too small to read is worse than no mark, because
#     it costs contrast and returns noise.
#   * NO TAPER AND NO FEATHER. The old crack tapered to nothing at both ends and was feathered
#     into the floor, which is most of why its median mark was four pixels — and a feathered edge
#     is an anti-aliased edge, which §4.3 forbids in authored pixels.
#
# ⚠ THE WALK USES NO TRIGONOMETRY AND NO FLOATING-POINT RNG, because it has to run identically in
# Python and in C#. Direction is an INDEX into a fixed table of unit vectors held as integers in
# the manifest, and it random-walks by one step at a time. A `cos()` agreeing to the last bit
# across two runtimes is an assumption; a table lookup is not.
CRACK_RATE = 7             # anchors in a hundred that carry a crack
CRACK_MIN_TILES = 3        # the minimum readable extent, as a refusal
CRACK_MAX_TILES = 7
CRACK_DIRS = 32
CRACK_TURN = 5             # turn on one pixel in five, not on two in three
CRACK_SCALE = 1024


def crack_dir_table():
    """Unit vectors as integers. Written into the manifest so both sides read one table."""
    import math
    return [[int(round(math.cos(2 * math.pi * i / CRACK_DIRS) * CRACK_SCALE)),
             int(round(math.sin(2 * math.pi * i / CRACK_DIRS) * CRACK_SCALE))]
            for i in range(CRACK_DIRS)]


DIRS = crack_dir_table()


# THE CRACK IS NOT ONE VALUE. The frame critic, twice: "uniform 1px black crossing joints
# without deflection... the identical overlay". A crack that is one value along its whole length
# is a drawn line; a real one is deepest where it has opened and shallows to nothing at its ends.
# The depth is modulated per pixel from the crack's own world position, so it varies ALONG the
# fracture and both tiles either side of a boundary agree about it.
CRACK_DEPTH_VARY = 0.18    # +/- share of the crack's depth, keyed on world position
CRACK_VARY_SALT = 3017
CRACK_DEPTH = 0.42         # the joint's own depth: a crack is dark because ENCLOSED (§6.5),
                           # and one that met a joint at a different value would announce itself
                           # as a decal laid over the bond rather than a split through it.


def _lcg(state):
    """The same pseudo-random step in both languages. Nothing clever, and nothing float."""
    return (state * 1103515245 + 12345) & 0x7FFFFFFF


def crack_polyline(ax, ay, seed):
    """The crack anchored at tile (ax, ay), in WORLD PIXELS, or [] if this anchor carries none.

    Deterministic from the anchor's own coordinates and nothing else, so every cell the crack
    crosses computes the identical line.
    """
    h = mix(ax, ay, CRACK + seed)
    if h % 100 >= CRACK_RATE:
        return []
    st = _lcg(h | 1)
    length = CRACK_MIN_TILES + (st >> 7) % (CRACK_MAX_TILES - CRACK_MIN_TILES + 1)
    st = _lcg(st)
    x = ax * T + (st >> 5) % T
    st = _lcg(st)
    y = ay * T + (st >> 5) % T
    st = _lcg(st)
    d = (st >> 9) % CRACK_DIRS

    pts, px, py = [], x * CRACK_SCALE, y * CRACK_SCALE
    # A CRACK IS NOT A VINE. Turning by one step of the direction table on two thirds of pixels
    # gave a heavy meander that read as root or creeper rather than as a split through stone —
    # 11.25 degrees at almost every pixel is a random walk, not a fracture. Stone parts along a
    # line and changes its mind rarely, so the walk turns on one pixel in CRACK_TURN.
    for _ in range(length * T):
        st = _lcg(st)
        if (st >> 11) % CRACK_TURN == 0:
            st = _lcg(st)
            d = (d + (1 if (st >> 13) % 2 else -1)) % CRACK_DIRS
        px += DIRS[d][0]
        py += DIRS[d][1]
        pts.append((px // CRACK_SCALE, py // CRACK_SCALE))
    return pts


def crack_pixels(tx, ty, seed, cache=None):
    """Which pixels of tile (tx, ty) a crack passes through, in tile-local coordinates.

    Scans every anchor whose crack could possibly reach this tile. The polylines are cached
    because a crack seven tiles long is regenerated by seven cells, and it must be the same seven
    times — caching is an optimisation here and the determinism is in the address, not the cache.
    """
    if cache is None:
        cache = {}
    out = set()
    reach = CRACK_MAX_TILES + 1
    x0, y0 = tx * T, ty * T
    for ay in range(ty - reach, ty + reach + 1):
        for ax in range(tx - reach, tx + reach + 1):
            key = (ax, ay)
            if key not in cache:
                cache[key] = crack_polyline(ax, ay, seed)
            for (wx, wy) in cache[key]:
                lx, ly = wx - x0, wy - y0
                if 0 <= lx < T and 0 <= ly < T:
                    out.add((ly, lx))
    return out


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

# WEAR'S FOURTH TERM, and it was nearly shipped unnamed. Feet take the dressing off a stone before
# they take anything else off it, so a trodden stone carries fewer tool bands and fewer pits. That
# is correct — but it was written inline as `3 if worn else 5`, outside the wear block, and so the
# `flat_channel` plant (which nulls the wear terms and asserts the channel then delivers NOTHING)
# went silent: it nulled three terms out of four and the channel stayed visible through the one it
# could not see. The plant caught an omission that would otherwise have ridden along as a channel
# nobody had agreed to.
MARK_BANDS, MARK_PITS = 5, 3        # on ordinary stone
# A THIRD OF THE STONES CARRY NOTHING. The frame critic: "the diagonal-hatch motif recurs on a
# visible rhythm across the lit area — vary the hatch angle, density, or omit it on a third of the
# slabs." An even scatter over every stone is a texture, and a texture that covers everything
# stops being an event and becomes the material — which is §8.3's motif trap arriving through the
# dressing rather than through the bond. Keyed on the stone's own address, so a bare stone is bare
# from both tiles that see it.
MARK_BARE_SHARE = 0.34
WEAR_BANDS, WEAR_PITS = 3, 1        # on trodden stone


def stone_offset(key, step, worn=False, bias=0):
    """Additive value offset, in luminance. WHOLE LADDER STEPS ONLY — a value off the ladder is
    not a legal value (§5.1 zero-mercy, §4.3 no anti-aliasing), so the bias is added before the
    multiply and clamped in steps, never blended in afterwards."""
    k = OFFSET_STEPS[key % len(OFFSET_STEPS)] + bias
    k = max(-3, min(3, k))
    return k * step * (WEAR_SPREAD if worn else 1.0)


# =================================================================================================
# THE WORKED SURFACE — dressing marks, tool striations, pits
# =================================================================================================
#
# THE DEVICE GATE: *"material texture is below the perceptual floor — the floor reads as
# linoleum."* And the law that came with it: **a signal authored below the perceptual floor is
# ABSENT; everything authored proves readable amplitude under the ratified rig at 1x.**
#
# The grain this replaces was authored at about +/-4 luminance against a 13.23 rung. It never
# survived quantisation, so a stone face was one flat value with a border — which is exactly what
# linoleum is. Measured after the lantern is divided out: 0.068 of a rung inside a face, against
# 0.332 for the crack network the same gate called excellent. A 4.9x gap, and the wrong side of it.
#
# WHAT REPLACES IT IS NOT LOUDER NOISE. Noise at any amplitude is still noise, and §8.1 asks for a
# floor that is USED UP, not textured. These are the marks of a stone that was DRESSED:
#
#   STRIATIONS  the parallel grooves a claw chisel leaves. One direction per stone, because one
#               mason worked one stone one way — and that is the material identity the ruling
#               asks for. Four directions in the world, chosen by the stone's address.
#   PITS        where the tooth of the stone tore out rather than cut.
#
# ALL OF IT IS OCCLUSION VOCABULARY AND NOTHING ELSE (§6.3, §6.5). Every mark is a RECESS, so
# every mark is darker, and none of them has a lit side and a shaded side. A dressing mark drawn
# with a highlight would be depicted lighting and would be illegal.
#
# MINIMUM READABLE EXTENT, DERIVED RATHER THAN GUESSED. The gate ruled the cracks — 1px wide,
# tens of pixels long — as excellent, and ruled 4px overlay marks as absent. So a 1px-wide feature
# is readable IF IT IS LONG: striations are 1px by 5..10. A blob is not, so pits are at least 2x2,
# never the 1px speck a seat once called "the pepper".
MARK_DIRS = ((1, 0), (0, 1), (1, 1), (1, -1))
MARK_MIN_LEN = 5
MARK_MAX_LEN = 8
# DEPTH IN LADDER RUNGS, and deliberately NOT whole numbers.
#
# A whole rung lands every mark on exactly one value. A rung and a half lands between two, so
# quantisation resolves it up or down depending on what the stone underneath is already worth —
# and a dressed face ends up with marks of two depths instead of one, which is what a claw chisel
# actually leaves and also raises the delivered amplitude. A pit is deeper than a scratch because
# the tooth tore out rather than cut.
MARK_DEPTH = 1.5
PIT_DEPTH = 2.0


def stone_extent(fw, fe, kind, c, drop, split_i):
    """The stone's own extent in STONE-LOCAL coordinates: (u_lo, u_hi, v_hi).

    Marks were first scattered across the whole 64x32 stone-local box, and a stone occupies a
    fraction of it — so roughly three quarters of every stone's dressing landed outside the class
    mask and was thrown away. Measured: the interior amplitude moved 0.068 -> 0.073 of a rung,
    which is nothing, on a change that was supposed to be the whole point.

    The extent is derivable from the same family tables both tiles already share, so this needs no
    new agreement between them. It mirrors `stone_origin` case for case, and the head joints are
    straight, so the numbers are exact rather than approximate.
    """
    a_w, mv_w = A_TABLE[fw][c], MV_TABLE[fw][c]
    a_e, mv_e = A_TABLE[fe][c], MV_TABLE[fe][c]
    y0, y1 = course_rows(split_i, c)
    v_hi = y1 - y0

    # THE EXTENT MUST BE DERIVED FROM THE BOUNDARY ALONE, never from the merge.
    #
    # The first version let a merged stone report the extent it actually occupies, which depends
    # on THIS tile's drop and on the family of its FAR side — neither of which the tile across the
    # boundary can see. So the two tiles dressed the same stone from different extents, the marks
    # desynced, and the seam landed exactly on the tile boundary. The boundary-step instrument
    # caught it at 1.277, above 1.00 for the first time in three sessions, on an axis the device
    # gate had already passed.
    #
    # The shared, un-merged extent is a SUBSET of the real one, so a merged stone simply gets no
    # dressing in its extension. That costs a little coverage and buys back the one property this
    # whole construction exists for.
    if kind == 0 or (kind == 0 and drop == 1):     # spans the WEST boundary
        return mv_w, T + a_w, v_hi
    if kind == 2 or drop == 2:                     # spans the EAST boundary
        return mv_e, T + a_e, v_hi
    return 0, mv_e - a_w, v_hi                     # interior


def stone_marks(key, seed, extent, worn=False, wear=0.0):
    """The dressing on one stone, in STONE-LOCAL pixels: [(u, v, depth_in_rungs), ...].

    Addressed by the stone, like its value and its grain, so it cannot repeat on the tile grid —
    and sampled in stone-local coordinates measured from the boundary, so both tiles either side
    of a spanning stone dress it identically.
    """
    st = _lcg((key ^ (MARKS + seed)) | 1)
    # BARE STONE. Drawn from the stone's own key before anything else, so it is stable and shared
    # across a boundary, and so the marks that DO appear read as events rather than as a coat.
    if ((key ^ (MARKS + seed)) % 1000) / 1000.0 < MARK_BARE_SHARE:
        return []
    u_lo, u_hi, v_hi = extent
    u_span = max(1, u_hi - u_lo - 1)
    v_span = max(1, v_hi - 1)
    out = []

    # ONE DIRECTION PER STONE. A mason does not change hands halfway across a flag.
    dx, dy = MARK_DIRS[(st >> 6) % len(MARK_DIRS)]

    # STROKES COME IN BANDS, because a claw chisel has several teeth and a mason works in passes.
    #
    # Scattered singly they read as SCRATCHES — a few long slashes at odd angles across a face,
    # which is damage, not dressing. Clustered into parallel runs 2px apart they read as tooling.
    # Each stroke still clears the readable-extent bar on its own (the gate ruled 1px-wide-but-
    # long readable, and 4px blobs absent), so the clustering costs nothing and buys the register.
    px_, py_ = -dy, dx                      # perpendicular, for the offset between teeth
    # MORE BANDS, NOT MORE TEETH PER BAND. Teeth raise regularity; bands raise coverage
    # while staying ragged. At three bands the delivered contrast sat at 0.148 against a
    # floor of 0.144 — a 3% margin is not a proof of readable amplitude, which is what the
    # law asks for.
    # (c) TRAFFICKED STONES POLISH SMOOTHER AS THEIR JOINTS OPEN; sheltered stones stay sharp
    # and tight. The dressing is what traffic takes off first, so its count and its depth both
    # fall with wear — a continuous quantity now, where it used to be a binary channel flag.
    keep = 1.0 - DRESSING_KEEP * wear
    n = max(1, int(round(((WEAR_BANDS if worn else MARK_BANDS) + ((st >> 9) % 2)) * keep)))
    for _ in range(n):
        st = _lcg(st)
        u = u_lo + (st >> 5) % u_span
        st = _lcg(st)
        v = (st >> 5) % v_span
        st = _lcg(st)
        length = MARK_MIN_LEN + (st >> 7) % (MARK_MAX_LEN - MARK_MIN_LEN + 1)
        st = _lcg(st)
        teeth = 2 + (st >> 10) % 2
        st = _lcg(st)
        gap = 2 + (st >> 12) % 2            # 2 or 3 px between teeth, not always 2
        for t in range(teeth):
            ou = u + px_ * t * gap
            ov = v + py_ * t * gap
            # EVERY TOOTH A DIFFERENT LENGTH. Equal-length teeth on an equal pitch is a barcode:
            # the first clustered version read as tally marks on some stones. A chisel skips and
            # bites unevenly, and a ragged end is the difference between tooling and hatching.
            st = _lcg(st)
            ln = max(MARK_MIN_LEN, length - (st >> 8) % 3)
            for i in range(ln):
                out.append((ou + dx * i, ov + dy * i, MARK_DEPTH * keep))

    m = max(0, int(round(((WEAR_PITS if worn else MARK_PITS) + ((st >> 11) % 3)) * keep)))
    for _ in range(m):
        st = _lcg(st)
        u = u_lo + (st >> 5) % u_span
        st = _lcg(st)
        v = (st >> 5) % v_span
        st = _lcg(st)
        wdt = 2 + (st >> 13) % 2          # 2 or 3 across — never the 1px speck
        for a in range(wdt):
            for b in range(2):
                out.append((u + a, v + b, PIT_DEPTH * keep))
    return out


# =================================================================================================
# THE WEAR FIELD — one scalar, sampled by world position, driving everything differential
# =================================================================================================
#
# THE DEVICE GATE, second walk: *"all the gaps look standardized… freshly laid and mortared, like
# someone scoured new stone to make it look old."* Ruled: **uniform joints are staged age, and
# staging is a register violation. Wear is EARNED, differentially.**
#
# The four things asked for are not four systems. A joint opens where feet passed; the stones
# beside an open joint lose their arrises and polish smooth; a sheltered joint stays tight and its
# stones stay sharp. That is ONE quantity with several consequences, so it is built as one:
#
#     W(x, y) in [0,1], sampled by WORLD PIXEL, drives
#         joint width and darkness      (a)
#         chipping and spall at arrises (b)
#         stone dressing amplitude      (c)   worn stones polish; sheltered stones stay sharp
#         and it takes a bias along the traffic line (d)
#
# NOTHING LATTICES, and the periods are why. The field is two octaves of value noise at FIVE and
# ELEVEN tiles — coprime with each other and with 1, so nothing in it lands on the tile grid or on
# any harmonic of it. A single octave at any period would draw its own grid.
#
# BOTH TILES EITHER SIDE OF A BOUNDARY COMPUTE THE SAME W, because it is a function of world
# position and nothing else. That is the same discipline as the stone address, applied to the
# joint — which is what "keyed to joint identity, boundaries agree" asks for.
WEAR_OCTAVES = ((5, 160), (11, 96))     # (period in tiles, weight out of 256)


def _wear_octave(px, py, period, seed):
    """One octave, bilinear, in integer arithmetic so C# reproduces it exactly."""
    span = period * T
    gx, gy = px // span, py // span
    fx, fy = px - gx * span, py - gy * span
    v00 = mix(gx, gy, WEAR + seed) & 255
    v10 = mix(gx + 1, gy, WEAR + seed) & 255
    v01 = mix(gx, gy + 1, WEAR + seed) & 255
    v11 = mix(gx + 1, gy + 1, WEAR + seed) & 255
    top = v00 * (span - fx) + v10 * fx
    bot = v01 * (span - fx) + v11 * fx
    return (top * (span - fy) + bot * fy) // (span * span)


def _mix_np(x, y, salt):
    """`mix`, vectorised. Verified against the scalar version element for element.

    The scalar one is the definition and the C# reproduces IT; this exists only because a
    per-pixel Python loop over the wear field killed the plant run outright (exit 137). A fast
    path that disagreed with the definition would be worse than a slow one, so `--check-wear`
    asserts they agree over a large sample before anything trusts this.
    """
    with np.errstate(over="ignore", invalid="ignore"):
        h = (x.astype(np.int64) * 7919 + y.astype(np.int64) * 104729
             + np.int64(salt) * 15485863).astype(np.int32)
        h = (h ^ (h >> 13)).astype(np.int32)
        h = (h.astype(np.int64) * 1274126177).astype(np.int32)
        h = (h ^ (h >> 16)).astype(np.int32)
    return h.astype(np.int64) & 0x7FFFFFFF


def wear_block(x0, y0, n, seed):
    """The wear scalar over an n x n block of world pixels whose top-left is (x0, y0)."""
    yy, xx = np.mgrid[0:n, 0:n]
    px, py = xx + x0, yy + y0
    total = np.zeros((n, n), dtype=np.int64)
    wsum = 0
    for period, weight in WEAR_OCTAVES:
        span = period * T
        gx, gy = px // span, py // span
        fx, fy = px - gx * span, py - gy * span
        v00 = _mix_np(gx, gy, WEAR + seed) & 255
        v10 = _mix_np(gx + 1, gy, WEAR + seed) & 255
        v01 = _mix_np(gx, gy + 1, WEAR + seed) & 255
        v11 = _mix_np(gx + 1, gy + 1, WEAR + seed) & 255
        top = v00 * (span - fx) + v10 * fx
        bot = v01 * (span - fx) + v11 * fx
        total += ((top * (span - fy) + bot * fy) // (span * span)) * weight
        wsum += weight
    return total // wsum


def traffic_block(traffic, x0, y0, n):
    """THE TRAFFIC FIELD sampled over an n x n block, bilinear between TILE CENTRES.

    Per-tile is what the level graph can say; per-pixel is what the floor needs. Consuming the
    per-tile scalar directly would paint the traffic model onto the tile grid — §8.3.1's lattice
    with a better excuse — so a route crosses a tile boundary without knowing there was one.
    """
    tw, th = traffic.shape
    yy, xx = np.mgrid[0:n, 0:n]
    sx, sy = xx + x0 - T // 2, yy + y0 - T // 2
    gx, gy = sx // T, sy // T
    fx, fy = sx - gx * T, sy - gy * T

    def smp(ax, ay):
        return traffic[np.clip(ax, 0, tw - 1), np.clip(ay, 0, th - 1)].astype(np.int64)

    top = smp(gx, gy) * (T - fx) + smp(gx + 1, gy) * fx
    bot = smp(gx, gy + 1) * (T - fx) + smp(gx + 1, gy + 1) * fx
    return (top * (T - fy) + bot * fy) // (T * T)


# THE ROUTES, AS LINES. Set by whoever knows the level — the engine from its own graph, the
# instruments from a declared synthetic route. Empty means no route model, and then the old
# per-tile field is the fallback rather than the truth.
LINES = []


def wear_scalar_block(x0, y0, n, seed, traffic=None):
    """What the wear pass consumes: the traffic field FRAYED by the old noise.

    The register guardrail is that the path is discovered, never staged — and a pure interpolation
    of an accumulated route is a smooth ribbon, which is what "reads as a drawn route" means. A
    quarter of the old two-octave field is mixed back in so the edges break up and the width
    wanders, without moving where the route goes.
    """
    noise = wear_block(x0, y0, n, seed)
    if LINES:
        # RE-KEYED TO THE ROUTE ITSELF. Round 21 measured that a per-tile field cannot supply a
        # line — its derived direction agreed between neighbours only 34% of the time. Distance to
        # the polyline is a pure function of world position, so it is coherent along the route by
        # construction. The noise stays at the same quarter it always was: a pure distance falloff
        # is a smooth ribbon, and a smooth ribbon is what "reads as a drawn route" means.
        import numpy as _np
        yy, xx = _np.mgrid[0:n, 0:n]
        v = _np.empty((n, n), dtype=float)
        for iy in range(n):
            for ix in range(n):
                v[iy, ix] = RP.strength(LINES, (x0 + ix + 0.5) / T, (y0 + iy + 0.5) / T)
        return (_np.round(v * 255.0).astype(_np.int64) * 3 + noise) // 4
    if traffic is None:
        return noise
    return (traffic_block(traffic, x0, y0, n) * 3 + noise) // 4


def wear01_block(raw, channel=False):
    """`wear01`, vectorised. Snapped to the same four ages."""
    r = np.maximum(raw, CHANNEL_WEAR) if channel else raw
    f = np.clip((r - WEAR_LO) / float(WEAR_HI - WEAR_LO), 0.0, 1.0)
    ages = np.array(WEAR_AGES)
    return ages[np.abs(f[..., None] - ages).argmin(-1)]


def wear_at(px, py, seed):
    """The wear scalar at a world pixel, 0..255. Integer throughout."""
    total = wsum = 0
    for period, weight in WEAR_OCTAVES:
        total += _wear_octave(px, py, period, seed) * weight
        wsum += weight
    return total // wsum


# HOW THE SCALAR IS SPENT. Every one of these is a SUBTRACTION or a widening — occlusion
# vocabulary only, as ruled. Nothing here brightens anything.
# TIGHT IS THE MINORITY, and that is an authored ratio rather than a fitted one. The device
# gate approved the OPEN joint — dark, deep, the cobbled read — and complained only that
# every joint looked the same. A split that made most joints tight would answer the
# complaint by inverting the thing that passed: measured, at 70/200 it put 71% of the room's
# joints in the tight state and the network contrast fell 0.207 -> 0.162.
#
# At 30/150 roughly a third are sheltered. The floor keeps the look it earned and gains an
# age gradient across it.
WEAR_LO, WEAR_HI = 30, 150
DRESSING_KEEP = 0.45            # how much of its dressing a fully worn stone LOSES.
                                # Carried in the manifest because the first version of this
                                # was a bare 0.75 written into both languages, changed in
                                # one of them, and caught only by the paint check — a magic
                                # number duplicated across a language boundary is the exact
                                # drift this project has already paid for twice.
# ============================ THE JOINT AS A TRAFFIC LEVER ============================
#
# RULING, after the measured ceiling: unfreeze the joints. The lever set that was available —
# dressing count, dressing depth, chipping — has a ceiling of 0.875 trodden-to-off-route
# roughness EVEN WITH A TRODDEN STONE STRIPPED COMPLETELY BARE, because local contrast is
# dominated by the joints, which sat at full depth everywhere regardless of traffic. A blind seat
# routed by the walls and the torchlight and said the floor told it nothing.
#
# So the joints carry it now, and the direction is the opposite of what was there before:
#
#     OFF-ROUTE   deep, tight, dark, continuous — nothing has happened to it
#     TRODDEN     compacted, FILLED, interrupted — grit packed into the gap, stones worn into
#                 one another until the line between them stops being a line
#
# OCCLUSION-LEGAL BY CONSTRUCTION, which is the whole reason this is allowed at all: a filled
# joint is a SHALLOWER joint, and a shallower recess holds less shadow. Lighter is a consequence
# of geometry, never a coat of paint. Nothing here brightens anything; it fills a hole.
#
# THE BOND IS UNTOUCHED. Filling changes what is VISIBLE, not what is there — the class mask still
# divides the stones, so every stone keeps its address and the corner theorem is unaffected. What
# degrades along a path is the VISIBLE enclosure, deliberately, because "stones wearing into one
# another" is the thing being drawn.
# ============================ THE CHROMA CHANNEL — STEP TWO OF THE LADDER ============================
#
# RULED, after the joint lever was discharged BY PROOF rather than by defeat: a lever confined to
# the joints owns 21.85% of the surface, and at its physical ceiling reaches 0.1253 Weber against
# §13.8's floor of 0.1440. No setting of it closes the value channel. So the path is carried by a
# second channel, on the 78.14% the joints never touched.
#
# WHY COLOUR IS THE RIGHT SECOND CHANNEL, and it is not just "the next thing on the list":
# the light rig multiplies every channel by the same falloff, so an authored VALUE difference
# arrives at the dark end of a room scaled down along with everything else. A RATIO BETWEEN
# CHANNELS SURVIVES THAT MULTIPLICATION UNTOUCHED. A stone 7% greener than its neighbour is still
# 7% greener in the dark, and half of this floor is dark — the seat measured 53.6% of it below
# luminance 70, where value work is spent where nobody can see it.
#
# §5.4 SANCTIONS IT AND ALSO CONSTRAINS IT. *Chroma is signal; a saturated pixel should mean
# something happened; general richness is forbidden.* A worn path is the clearest "something
# happened" a floor has. And the direction is not free: warmth is reserved for Sasha, for
# Hollowmark and for the Boundary's own fires, and spending warmth on the ground would compete
# with the one thing that must never be lost on a small screen. So the path goes COOL — the
# grey-green of stone walked free of its dry warm dust, and of what gets tracked into it.
#
# A CONSTANT-LUMINANCE ROTATION, deliberately. The multiplier below is projected onto the plane
# of constant luminance before it is used, so the chroma lever moves NO value at all. Three things
# follow, and each of them is a defect avoided rather than a nicety:
#   * the combined verdict is not double-counting one lever under two names;
#   * §6.5's value stack and the floor's anchor are untouched, so the wall session's numbers do
#     not move under it;
#   * a colour that also darkened would be an occlusion claim, and there is no recess here.
#
# FACES ONLY. The additive-remap law — offsets land on stone faces, joints are never touched —
# governs colour exactly as it governs value. A joint is dark because it is ENCLOSED (§6.5), and
# enclosure has no hue.
# ============================ FORM AS EROSION ============================
#
# RULED (Rafe, 2026-08-29) on the seat's own finding, which was not about amplitude:
#
#   "There is no directional grain, no lengthwise slab, no kerb, no drain line, no centre track,
#    nothing that runs WITH the corridor. The mouth does not change by a single pixel."
#
# Every lever before this one modulated the same stones per pixel. None of them changed the
# floor's FORM, and a path is read from form. So the route is WORN, NEVER BUILT — the register
# governs the mechanism, not just the look: the Boundary is found-and-annexed and administration
# is thin at this depth, so traffic carved what it needed. Nobody laid a path here. (A paved
# route is at most a deep-region dialect, filed for later.)
#
# THE TRAVEL AXIS. Erosion has a direction, so the floor needs one, and it is DERIVED FROM THE
# TRAFFIC FIELD rather than added beside it — one field, one source of truth, and both painters
# reach the same answer from the same numbers without a second channel to fall out of sync.
#
# Traffic is roughly constant ALONG a route and falls away ACROSS it. So the gradient points
# across the path and the travel axis is perpendicular to it. Quantised to four axes because the
# floor is 32px and there are only four directions a line can take on a pixel grid without
# anti-aliasing, which §4.3 forbids.
DIR_NONE = -1                    # no usable gradient: flat ground, and erosion has no story there
DIR_MIN_GRAD = 6                 # below this the gradient is noise, not a route


def axis_block(x0, y0, n):
    """The travel axis at every pixel of an n x n block, from the line's own tangent.

    Per pixel because ANY WEAR BOUNDARY COINCIDING WITH A TILE EDGE IS STAGED. Taking the axis
    once at the tile handed one direction to every joint in it, so the compaction changed where
    the tiles changed.
    """
    import numpy as _np
    out = _np.full((n, n), DIR_NONE, dtype=int)
    if not LINES:
        return out
    for iy in range(n):
        for ix in range(n):
            out[iy, ix] = RP.axis(LINES, (x0 + ix + 0.5) / T, (y0 + iy + 0.5) / T)
    return out


def travel_axis(traffic, tx, ty):
    """(see below) — the line's own tangent takes precedence when there is a line."""
    if LINES:
        return RP.axis(LINES, tx + 0.5, ty + 0.5)
    return _travel_axis_from_field(traffic, tx, ty)


def _travel_axis_from_field(traffic, tx, ty):
    """The local axis of travel: 0 = E-W, 1 = NE-SW, 2 = N-S, 3 = NW-SE, or DIR_NONE.

    THE ROUTE RUNS WHERE THE TRAFFIC CONTINUES. For each of the four axes a pixel grid allows,
    sum the traffic of the two neighbours that lie along it; the busiest axis is the way the feet
    went. Walls carry no traffic, so they contribute zero and a corridor's own walls vote against
    crossing them, which is exactly right.

    ⚠ THE FIRST VERSION OF THIS TOOK THE PERPENDICULAR OF THE GRADIENT and was wrong in the one
    place the floor most needed it — a one-tile corridor. Both across-neighbours are wall there,
    so the across-gradient is identically zero and cannot be measured at all; the only signal left
    is the variation ALONG the route, which the perpendicular then reads as a route running the
    other way. Mapped over the review scene it labelled the north-south chokepoint E-W down its
    whole length and scattered the room into diagonals. The lever was live, measured, plant-tested
    and aimed ninety degrees away from the truth, which no plant would have caught: the plants ask
    whether direction is expressed, not whether it is the right direction.

    `traffic` is indexed [x, y], matching `traffic_block`.
    """
    if traffic is None:
        return DIR_NONE
    w, h = traffic.shape

    def at(x, y):
        if x < 0 or y < 0 or x >= w or y >= h:
            return 0.0
        return float(traffic[x, y])

    # (dx, dy) for E-W, NE-SW, N-S, NW-SE
    axes = ((1, 0), (1, -1), (0, 1), (1, 1))
    sums = [at(tx + dx, ty + dy) + at(tx - dx, ty - dy) for dx, dy in axes]
    best = max(range(4), key=lambda i: sums[i])
    # A route has to be a route: the busiest axis must beat the quietest by a real margin, or the
    # ground is open floor with no direction in it and must not acquire a grain.
    if sums[best] - min(sums) < DIR_MIN_GRAD * 2:
        return DIR_NONE
    return best


# THE THREE EROSION LEVERS, all keyed to the field that already exists.
#
# (a) STONES GROUND LOWER AND FLATTER. A walked stone loses its crown: its own value collapses
#     toward the material's median (flatter) and it sits below its neighbours, which is drawn the
#     only legal way — as shadow at its edges, never as an overall darkening, because a stone that
#     is merely darker is a stone that was painted.
# CUT by the frame critic: "every lit tile sits inside one narrow brown band, so slab, repair,
# hatched patch and ground-in dirt all read as the same material at the same distance."
#
# This pass is what was closing the band. It pulls a walked stone's value toward the material
# median to say "ground down", and at 0.60 a fully worn stone had lost most of the value that
# distinguished it from its neighbours — the stone-to-stone variation the bond spends five
# families and two tables to produce, flattened out again at paint time on exactly the ground the
# player is standing on. Ground-down is a real thing to say; saying it this loudly costs the floor
# its material.
DEFORM_FLATTEN = (0.0, 0.04, 0.14, 0.24)   # by wear age: how far a stone's value is pulled to the
                                           # material median. Flat is what ground-down looks like.
#
# (b) THE COMPACTION ITSELF IS THE DIRECTIONAL LEVER, and the first attempt at this had it
#     backwards. Rounding the arris beside a crossed joint was tried first and MEASURED WORSE
#     (bed/head 1.111 where it should have fallen below 1.00) for a reason worth keeping: on
#     trodden ground the joint has already been packed UP toward the stone, so darkening the face
#     pixel beside it moves that pixel AWAY from the joint's value rather than toward it. The two
#     levers were fighting, and the arris one lost.
#
#     So the direction weights the compaction that already works. Feet cross the joints lying
#     ACROSS a route and pack them shut; a joint running WITH the route takes far less of that,
#     and stays open and dark. In a north-south corridor the bed joints close up and the head
#     joints survive as continuous dark lines — long unbroken runs in the direction of travel,
#     out of geometry that was already there, with no new families and no new bond. That is the
#     seat's "something that runs with the corridor", and it is the joint lever doing it.
DEFORM_ROUND = (0.0, 0.0, 0.0, 0.0)        # RETIRED, kept at its null so the manifest key and the
                                           # engine path stay live and any revival is deliberate
DEFORM_ANISO = 0.80                        # 0 = rounding ignores direction (isotropic, the old
                                           # behaviour); 1 = only the crossed edges round at all


def aniso_weights(axis):
    """How much a north-south-normal edge and an east-west-normal edge each round, on this axis.

    An edge is CROSSED by travel when its normal lies along the travel axis, and a crossed edge is
    the one feet actually hit. With no usable gradient there is no route and the old isotropic
    behaviour is correct — an unwalked floor should not acquire a grain.
    """
    k = 1.0 - DEFORM_ANISO
    if axis == DIR_NONE:
        return 1.0, 1.0
    if axis == 2:            # travelling north-south: the bed joints are crossed
        return 1.0, k
    if axis == 0:            # travelling east-west: the head joints are crossed
        return k, 1.0
    d = 1.0 - DEFORM_ANISO / 2.0
    return d, d              # diagonal travel crosses both, and neither cleanly                        # 0 = rounding ignores direction (isotropic, the old
                                           # behaviour); 1 = only the crossed edges round at all
#
# (c) THRESHOLD HOLLOWS. Where routes converge on a mouth the stone dishes: genuinely lower in the
#     middle, with a rim that shadows. Occlusion-legal by construction and NEVER a sill, a kerb or
#     an installed piece — nothing is built here, things are used up (§8.1).
HOLLOW_DEPTH = 1.30                        # ladder rungs at the centre of the dish
HOLLOW_RIM = 0.45                          # rungs of extra shadow just inside the rim
HOLLOW_SALT = 3011                         # so two mouths are not the same dish (§8.3.1)

# ============================ POLISH AS LIGHT RESPONSE ============================
#
# RULED after Ruling 70's execution was overturned at the gate: the closure named the wrong
# illumination, because the path signal is keyed to where the player walks and THE PLAYER CARRIES
# THE LAMP. A static scene-wide capture measures the signal precisely where its reader never is.
#
# This lever is the one that could not have been reached from the wrong population, and it is the
# physics of the thing being drawn: a stone walked smooth REFLECTS MORE, and reflection is a
# response to light rather than a property of pigment.
#
#   BANNED, still (§8.2.1): baked value-lift. Painting a trodden stone brighter makes it brighter
#   in the dark too, spends the delta where nobody is, and reads as wear drawn on.
#   LEGAL: engine response modulation. The mask below feeds a shader that touches ONLY the light
#   pass, so a polished stone and a rough one are identical in ambient, and the difference grows
#   FASTER THAN LINEARLY with the light actually delivered.
#
# The perceptual-floor law applies to the delivered LIT delta, which is the quantity the corrected
# captures measure and the quantity §13.9 was always about.
# ============================ THE ADDITIVE LAYER ============================
#
# RULED (Rafe, 2026-08-30). Round 22 moved the failure axis: the signal is keyed to a real,
# coherent line (79% axis coherence, 100% where the route is straight) and is present on it
# (1.22x the off-route detail), and is still too small for a viewer to route by. The seat named
# three treatments it expects and does not find, and ALL THREE ARE ADDITIVE — polish down the
# centre, grit driven to the wall edges, dishing where feet land.
#
# Everything this session built before now SUBTRACTS: flattening removes value spread, compaction
# removes joints, chipping removes arrises. A floor made only of absence reads as unfinished
# rather than used. These three put something back.
#
# ⚠ BANKED AS LAW BEFORE ANY OF IT WAS BUILT: a seat reports PERCEPTS; its EXPLANATIONS are
# hypotheses and are measured before anything is built on them. Round 22's cull — "the floor is
# blank exactly where the lamp lights it" — was a compelling structural story and was FALSE at
# tile scale (+0.772 correlation the other way). The three treatments below are taken because the
# seat OBSERVED their absence, not because it explained why.

# ---- (1) THE SPECULAR LANE, off the line rather than off the frayed field --------------------
# The polish shader has read the wear scalar since it was built, and that scalar is traffic FRAYED
# BY NOISE — deliberately, so a path's edges break up rather than ending on a pixel. That is right
# for age and wrong for a lane: a specular streak that is chopped into noise cannot be followed.
# Width now comes from the line distance UNFRAYED, so the lane runs continuous down the centre,
# and the noise returns only at its shoulders.
POLISH_LANE_GAIN = 0.6    # RULED DOWN from 1.9 at the gate: 'it looks like all the tiles on
                          # the walked path have been replaced'. At 1.9 the on-lane masonry
                          # measured 0.157 — NINE PERCENT above §13.8's floor, and BELOW its
                          # own flank's 0.177. The lane was washing the stones out. At 1.0 it
                          # reads 0.421, nearly three times the floor, while lane-vs-flank
                          # holds at 0.394. Wear modulates the same stones; it never replaces
                          # their identity.
                          #
                          # STEPPED AGAIN, 1.0 -> 0.6, at the gate that found the tile
                          # quantisation: with the staircase gone the lane was re-judged and 1.0
                          # still read as different material. At 0.6 the wash is gone, the stone
                          # reads as stone and the cracks still carry. On-lane masonry 0.291,
                          # twice the floor.          # how much brighter the lane's specular is than the aged surface
POLISH_LANE_WIDTH = 0.62        # in tiles, half-width of the fully-polished centre
POLISH_SHOULDER = 1.15          # in tiles, where the lane's specular has faded to nothing

# STRIATIONS ALONG THE TANGENT. Dragged feet do not polish evenly; they leave streaks running the
# way they went. The bands are laid in a coordinate PERPENDICULAR to the tangent, so the streaks
# themselves run ALONG it, and they are floored to whole pixels because §4.3 forbids the
# anti-aliasing a smooth stripe would need.
STRIA_PERIOD = 3                # pixels between streaks
STRIA_DEPTH = 0.12        # CUT by the frame critic, which called it a '45 degree hatch
                          # OVERLAY' — read as applied to the floor rather than worn into
                          # it, which is a decal by another name. At 0.45 every third
                          # pixel line lost nearly half its specular and the pattern
                          # covered the whole lit area as an even weave. Measured earlier
                          # at a third of the on-lane 'legibility' the metric credited.              # how much of the lane's specular a dark streak gives up
STRIA_SALT = 3012
LANE_FRAY = 0.32          # tiles of jitter on the distance BEFORE the lane's falloff, so
                          # its shoulder wanders instead of arriving on a line. A
                          # smoothstep to zero at a fixed distance gave the lane a hard
                          # upper edge, and the walk read it as a spotlight stripe laid on
                          # the floor — staging, which §8.1 does not allow.
LANE_FRAY_SALT = 3016
JOINT_POLISH_FLOOR = 0.70  # no joint is more than 30% below the face beside it in specular

# ---- (2) DISHING ALONG THE LINE ---------------------------------------------------------------
# The threshold hollows stay exactly as they are; this is the shallow version that follows the
# whole route rather than only its mouths. Deepest on the centre-line, gone by the shoulder.
# Occlusion-legal by construction: genuinely lower stone, with the rim shadow that implies.
LANE_DISH_DEPTH = 0.85          # ladder rungs at the centre-line
LANE_DISH_RIM = 0.30            # rungs of extra shadow at the dish's edge
LANE_DISH_SALT = 3013

# ---- (3) MARGIN GRIT — THE ONE NEW LEVER ------------------------------------------------------
# Traffic sweeps the centre clean and drives debris to the flanks. The grit is placed at the
# route's MARGINS and the swept lane is left conspicuously clean between gritty edges: THE
# CONTRAST BETWEEN SWEPT AND UNSWEPT IS THE SIGNAL, not the grit itself.
#
# §8.3.1-LEGAL BY CONSTRUCTION. Keyed on world position and on distance from the line, never on a
# tile — so it does not repeat with the grid, and a stone spanning a boundary gets the same grit
# from both tiles. Field-scale, like the crack network, which is the one system class seats have
# consistently praised here.
GRIT_INNER = 0.70               # tiles from the line: inside this the sweep has taken it away
GRIT_OUTER = 1.90               # tiles from the line: beyond this nobody swept anything anywhere
GRIT_RATE = 0.13                # share of face pixels in the margin band carrying a speck
GRIT_DEPTH = 1.25               # ladder rungs a speck sits below the stone it lies on
GRIT_SALT = 3014

POLISH_BY_AGE = (0.0, 0.05, 0.22, 0.45)   # reflectivity by wear age; sheltered stone is matte
POLISH_EXP = 2.0                          # how much faster than linear. 1.0 would BE an albedo
                                          # change, which is the banned lever wearing this one's
                                          # name, so the engine asserts it is greater than 1.
POLISH_GAIN = 1.0

CHROMA_DIR = (-1.0, 0.35, -0.15)          # toward a cool grey-green, before the luminance projection
CHROMA_BY_AGE = (0.0, 0.0, 0.06, 0.12)    # by wear age; the first two are silent ON PURPOSE — a
                                          # signal that starts at the first hint of traffic is a
                                          # wash over the whole floor, and washes identify nothing


def line_geometry_block(x0, y0, n):
    """Per-pixel (distance to the route in tiles, tangent x, tangent y) over an n x n block.

    ONE definition, three painters. Everything additive keys off this: the specular lane's width,
    the dish's depth, and which side of the sweep a pixel is on.
    """
    import numpy as _np
    d = _np.empty((n, n), dtype=float)
    tx = _np.empty((n, n), dtype=float)
    ty = _np.empty((n, n), dtype=float)
    if not LINES:
        d[:] = 1e9
        tx[:] = 1.0
        ty[:] = 0.0
        return d, tx, ty
    for iy in range(n):
        for ix in range(n):
            dd, _w, a, b = RP.nearest(LINES, (x0 + ix + 0.5) / T, (y0 + iy + 0.5) / T)
            d[iy, ix], tx[iy, ix], ty[iy, ix] = dd, a, b
    return d, tx, ty


def lane_polish_block(dist, tx, ty, wx, wy, seed):
    """The specular lane: continuous down the centre, streaked along the way the feet went.

    UNFRAYED, deliberately. The polish has read the noise-frayed wear scalar since it was built,
    which is right for AGE — a path's edges should break up rather than end on a pixel — and wrong
    for a LANE: a specular streak chopped into noise cannot be followed. Width comes from the line
    distance directly; the noise returns at the shoulders through the age layer underneath.
    """
    import numpy as _np
    # THE SHOULDER FRAYS. A smoothstep to zero at a fixed distance gives the lane a hard upper
    # edge, which the walk read as a spotlight stripe laid on the floor — staging, which §8.1 does
    # not allow. The distance is jittered on a coarse world block BEFORE the falloff, so the
    # shoulder wanders by a fraction of a tile instead of arriving on a line.
    fray = ((_mix_np(wx // SHELTER_BLOCK, wy // SHELTER_BLOCK, LANE_FRAY_SALT) % 1000) / 1000.0
            - 0.5) * 2.0 * LANE_FRAY
    lane = _np.clip((POLISH_SHOULDER - (dist + fray))
                    / max(POLISH_SHOULDER - POLISH_LANE_WIDTH, 1e-6), 0.0, 1.0)
    lane = lane * lane * (3.0 - 2.0 * lane) * POLISH_LANE_GAIN

    # STRIATIONS ALONG THE TANGENT. The band coordinate is PERPENDICULAR to the tangent, so the
    # streaks themselves run along it. Floored to whole pixels: §4.3 forbids the anti-aliasing a
    # smooth stripe would need, and at 32px a hard edge is the only honest edge.
    n = _np.hypot(tx, ty)
    n = _np.where(n < 1e-9, 1.0, n)
    perp = (-ty / n) * wx + (tx / n) * wy
    band = _np.floor(perp).astype(_np.int64) % STRIA_PERIOD
    h = (_mix_np(wx, wy, STRIA_SALT + seed) % 100) / 100.0
    dark = (band == 0) | ((band == 1) & (h < 0.35))
    return lane * _np.where(dark, 1.0 - STRIA_DEPTH, 1.0)


def lane_dish_block(dist, wx, wy, seed):
    """A shallow dish following the whole route, deepest on the centre-line.

    The threshold hollows are untouched; this is the version that follows the line rather than
    only its mouths. Genuinely lower stone with the rim shadow that implies — occlusion-legal by
    construction, and salted so the dish is not the same dish everywhere (§8.3.1).
    """
    import numpy as _np
    jit = (_mix_np(wx, wy, LANE_DISH_SALT + seed) % 100) / 500.0
    u = _np.clip(1.0 - dist / max(POLISH_SHOULDER, 1e-6) - jit, 0.0, 1.0)
    dish = u * u * LANE_DISH_DEPTH
    rim = _np.where((dist > POLISH_SHOULDER * 0.80) & (dist < POLISH_SHOULDER * 1.05),
                    LANE_DISH_RIM, 0.0)
    return dish + rim


def grit_block(dist, wx, wy, seed):
    """Debris swept off the centre and left at the margins.

    THE CONTRAST IS THE SIGNAL, not the grit. Traffic sweeps the lane clean and drives what it
    lifts to the flanks, so the swept lane reads as conspicuously bare BETWEEN gritty edges —
    which is a thing absence can say only when there is something either side of it.

    §8.3.1-legal by construction: keyed on world position and on distance from the line, never on
    a tile. It does not repeat with the grid, and a stone spanning a boundary gets the same grit
    from both tiles.
    """
    import numpy as _np
    band = (dist > GRIT_INNER) & (dist < GRIT_OUTER)
    # densest just outside the sweep and thinning outward — debris piles where it was pushed to
    t = _np.clip((dist - GRIT_INNER) / max(GRIT_OUTER - GRIT_INNER, 1e-6), 0.0, 1.0)
    rate = GRIT_RATE * (1.0 - t) * (1.0 - t)
    h = (_mix_np(wx, wy, GRIT_SALT + seed) % 1000) / 1000.0
    return band & (h < rate)


def chroma_strength_block(x0, y0, n, seed, traffic, channel=False):
    """The chroma channel's strength over an n x n block. ONE definition, three painters.

    NO TRAFFIC MODEL MEANS NO CHROMA, and that is a semantic rather than a convenience. The joint
    lever consumes `wear_scalar_block`, which falls back to raw noise when no field is supplied —
    correct there, because a joint's AGE is a property of the stone whether or not anyone has
    modelled the routes. Chroma marks the PATH, and a floor with no traffic model has no path to
    mark. Letting it fall back to noise painted 77% of a fieldless floor with the cast: general
    richness, which §5.4 forbids by name, and a signal that means nothing because it is everywhere.
    """
    import numpy as _np
    if traffic is None:
        return _np.zeros((n, n), dtype=float)
    # THE CHANNEL FLAG IS NOT OPTIONAL. Omitting it read the wear scalar one way in the
    # composer and another in the engine, and the paint check caught the two painting the same
    # pixel a different colour — rgb(108,118,113) against rgb(102,121,113), one wear age apart.
    w = wear01_block(wear_scalar_block(x0, y0, n, seed, traffic), channel)
    ages = _np.array(WEAR_AGES)
    return _np.array(CHROMA_BY_AGE)[_np.abs(w[..., None] - ages).argmin(-1)]


def chroma_tint(tint, strength):
    """The material tint rotated toward CHROMA_DIR at constant luminance.

    Projecting out the luminance component is what makes this a colour lever and not a second,
    quieter value lever wearing colour's clothes.
    """
    import numpy as _np
    w = _np.array([0.299, 0.587, 0.114])
    t = _np.asarray(tint, dtype=float)
    d = _np.asarray(CHROMA_DIR, dtype=float)
    d = d - (w @ (t * d)) / (w @ t)       # the component that changes hue and nothing else
    return t * (1.0 + strength * d)


# ============================ THE SHELTERED JOINT'S DEPTH IS A DISTRIBUTION ============================
#
# RULED (Rafe, 2026-08-31) after the device walk came back reading as outlined chips: none of
# A-D — reshape the distribution and KEEP THE RUNGS.
#
# PR #161 gave the sheltered joints somewhere darker to go and they all went. 92.7% of joint pixels
# landed on the bottom two rungs, mean contrast against the stone went 0.272 -> 0.510, and every
# stone acquired an outline. The rungs are not the problem — they are still needed for §6.5's wall
# face, which cannot be authored without them. WHAT WENT WRONG IS THAT ONE VALUE WAS HANDED TO
# EVERY JOINT IN THE WORLD, and it was the darkest one available.
#
# So a sheltered joint now DRAWS its depth:
#
#   THE MODE IS MORTAR, not a line — shallow enough that its contrast against the stone sits
#   under §13.8's floor, where a signal is absent. Most of the floor's joints stop outlining.
#   A MINORITY TAIL still reaches the deep rungs, which is what keeps #161's spread: a floor with
#   some joints blown open and most of them packed is a floor with a history, and it is exactly
#   what the "all the gaps look standardized" cull asked for in the first place.
#
# KEYED ON A COARSE WORLD BLOCK, not per pixel and not per joint. Per pixel would be noise; per
# joint run would put one flat value along a whole line, which is the defect at a smaller scale.
# An 8px block means a joint run of twenty pixels crosses two or three of them and varies ALONG
# its length — which is what mortar looks like, and it is world-keyed, so both tiles either side
# of a boundary draw the identical depth for the identical pixel.
# FOUR DRAWS, and the widest one is at the LIGHT end. The first table tried (4, 3, 0) hit four of
# the five declared targets and lost the spread — 3.997 rungs against #161's 5.024 — because
# capping the joint at its stone's level had cut off the tail that was carrying the width. Adding
# a share PACKED SHUT recovers it at the light end instead, which widens the distribution while
# LOWERING the mean and the share above the floor. Measured: spread 4.99, mean 0.112, mode 0.078.
SHELTER_LIFT_RUNGS = (5.0, 4.0, 3.0, 0.0)   # packed shut / mode / middle / the deep tail
SHELTER_WEIGHTS = (0.04, 0.26, 0.52, 0.18)   # RAISED BACK by the frame critic: 'the floor's
                                             # joint structure has dissolved... no legible
                                             # slab edge anywhere: a soft brown gradient.'
                                             # The keyline fix had put the MODAL joint at
                                             # 0.107 Weber, UNDER §13.8's floor, so the
                                             # typical joint was not merely subtle but
                                             # absent — the overshoot flagged two rounds
                                             # before the critic named it. The mode now
                                             # sits at 0.154, just clear of the floor and
                                             # far below the 0.579 that outlined every
                                             # stone. Spread unchanged at 4.99 rungs.   # a smaller packed-shut share keeps the median
                                             # joint faintly present: at 0.15 the field's
                                             # spread fell to 2.95 rungs because half the
                                             # joints had closed. 0.06 restores it to 4.01
                                             # without moving any declared target.
SHELTER_BLOCK = 8                      # world px per draw
SHELTER_SALT = 3015


def shelter_lift_block(wx, wy, seed):
    """How far each joint pixel is lifted off the ladder's bottom, in rungs.

    One definition, three painters. The draw is on a coarse world block so the depth varies along
    a joint's run rather than being constant on it — mortar, not a drawn line.
    """
    import numpy as _np
    h = (_mix_np(wx // SHELTER_BLOCK, wy // SHELTER_BLOCK, SHELTER_SALT + seed) % 1000) / 1000.0
    cuts = _np.cumsum(_np.array(SHELTER_WEIGHTS))
    idx = _np.searchsorted(cuts, h, side="right").clip(0, len(SHELTER_LIFT_RUNGS) - 1)
    return _np.array(SHELTER_LIFT_RUNGS)[idx]


JOINT_FILL_RUNGS = (0.0, 0.0, 1.0, 2.0)   # by wear age: how far up the ladder a joint is packed
JOINT_BREAK = (0.0, 0.0, 0.20, 0.45)      # by wear age: share of the joint packed level with the
                                          # floor, so the line stops being continuous
JOINT_BREAK_SALT = 3010
CHIP_RATE = 0.55                # of stone pixels beside a fully-open joint, how many go with it
SPALL_RATE = 0.10               # of those, how many take a second pixel — a corner gone
CHANNEL_WEAR = 235              # what the trodden channel raises W to. Nulled by the plant.
CHIP = 3009


# A JOINT HAS AN AGE, NOT A REAL NUMBER — and this is a correctness fix before it is a taste one.
#
# A continuous scalar against a seven-rung ladder puts pixels on quantisation knife-edges: at
# exactly w=0.5 the joint lands HALF A RUNG between two levels, the tie is broken by floating-
# point noise in how `step` was computed, and the composer and its mirror disagreed on 65 pixels
# for no reason either of them could be said to be wrong about. A third implementation would have
# been a third coin flip.
#
# Snapping to four ages removes the knife-edge — none of 0.00, 0.34, 0.67, 1.00 rungs lands on a
# half — and it is what the material wants anyway: mortar is tight, opening, open, or gone.
WEAR_AGES = (0.0, 0.34, 0.67, 1.0)


def _snap_age(f):
    best = WEAR_AGES[0]
    for a in WEAR_AGES:
        if abs(a - f) < abs(best - f):
            best = a
    return best


def wear01(raw, channel=False):
    """The wear scalar as one of four ages, with the channel's bias folded in (ruling (d))."""
    if channel:
        raw = max(raw, CHANNEL_WEAR)
    if raw <= WEAR_LO:
        return 0.0
    if raw >= WEAR_HI:
        return 1.0
    return _snap_age((raw - WEAR_LO) / float(WEAR_HI - WEAR_LO))


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
    # A TIGHT JOINT MUST HAVE SOMEWHERE TO GO. At 0.42 the joint quantised to the BOTTOM RUNG of
    # the ladder — every joint in the world already as dark as the palette can hold — so the
    # differential-wear pass had no headroom and measured a spread of 0.000 rungs. That is the
    # standardized-gap defect stated in numbers: not that the joints were the wrong darkness, but
    # that they were all the SAME darkness because they were all clipped against the floor.
    #
    # The bond now bakes a SHALLOWER joint, one rung up, and wear deepens it to the floor. The
    # deepest joints are exactly as dark as they were; the sheltered ones are visibly tighter.
    # Pure subtraction at paint time, which is what "occlusion vocabulary only" requires.
    # ANCHORED AT THE DARK END. The first attempt baked a shallow joint and let wear deepen it,
    # which moved EVERY joint in the world up a rung and only brought the worn ones back — and
    # since most of a room is not a thoroughfare, most joints simply got lighter. The whole floor
    # washed out: the network contrast the device gate had praised fell 0.207 -> 0.160.
    #
    # The complaint was never that the gaps were too dark. It was that they were all the SAME.
    # So the bond keeps the dark joint it had, and the differential is spent the only way the
    # palette leaves room for: a SHELTERED joint is shallower, and an open one takes the arris off
    # the stones beside it instead of going darker, because it cannot.
    # Overridable so a diagnosis can cost alternatives without editing the file it is
    # measuring. Production always reads the literal.
    depth = np.full((T, T), globals().get('_JOINT_DEPTH_OVERRIDE', 0.42), dtype=float)
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
    # RE-DERIVE THE LADDER rather than inherit it. The base family's manifest was written before
    # the ruling that put two rungs below the donors' band, and a stored ladder is a snapshot of
    # the rule on the day it was written. `lum_lo`/`lum_hi` are the measurement; the ladder is a
    # rule applied to it.
    mat = CF.rehydrate(src["material"])
    # The chroma channel travels in the material, beside the tint it rotates. The DIRECTION ships
    # unprojected and the projection happens in each painter, so the constant-luminance invariant
    # is enforced where the tint is used rather than trusted to a number in a file.
    mat["chroma_dir"] = list(CHROMA_DIR)
    mat["chroma_by_age"] = list(CHROMA_BY_AGE)
    mat["polish_by_age"] = list(POLISH_BY_AGE)
    mat["polish_exp"] = POLISH_EXP
    mat["polish_gain"] = POLISH_GAIN
    mat["deform_flatten"] = list(DEFORM_FLATTEN)
    mat["deform_round"] = list(DEFORM_ROUND)
    mat["deform_aniso"] = DEFORM_ANISO
    mat["hollow_depth"] = HOLLOW_DEPTH
    mat["hollow_rim"] = HOLLOW_RIM
    mat["shelter_lift"] = list(SHELTER_LIFT_RUNGS)
    mat["shelter_weights"] = list(SHELTER_WEIGHTS)
    mat["shelter_block"] = SHELTER_BLOCK
    mat["lane_fray"] = LANE_FRAY
    mat["crack_depth_vary"] = CRACK_DEPTH_VARY
    mat["mark_bare_share"] = MARK_BARE_SHARE
    mat["joint_polish_floor"] = JOINT_POLISH_FLOOR
    mat["polish_lane"] = [POLISH_LANE_GAIN, POLISH_LANE_WIDTH, POLISH_SHOULDER]
    mat["striation"] = [STRIA_PERIOD, STRIA_DEPTH]
    mat["lane_dish"] = [LANE_DISH_DEPTH, LANE_DISH_RIM]
    mat["grit"] = [GRIT_INNER, GRIT_OUTER, GRIT_RATE, GRIT_DEPTH]
    os.makedirs(a.out, exist_ok=True)
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)

    man = dict(family="boundary_floor_ashlar_v1", commit=FL.git_commit(), seed=a.seed,
               material=mat, families=FAMILIES, tile=T, courses=COURSES, splits=SPLITS,
               a_table=A_TABLE, mv_table=MV_TABLE,
               salts=dict(horizontal=HORIZ, vertical=VERT, span=SPAN, interior=INTERIOR,
                          drop=DROP, cluster=CLUSTER, split=SPLIT_SALT, crack=CRACK,
                          marks=MARKS, wear=WEAR, chip=CHIP, joint_break=JOINT_BREAK_SALT,
                          hollow=HOLLOW_SALT, stria=STRIA_SALT, lane_dish=LANE_DISH_SALT,
                          grit=GRIT_SALT, shelter=SHELTER_SALT, lane_fray=LANE_FRAY_SALT, crack_vary=CRACK_VARY_SALT),
               offset_steps=OFFSET_STEPS, cluster_table=CLUSTER_TABLE,
               marks=dict(dirs=[list(d) for d in MARK_DIRS], min_len=MARK_MIN_LEN,
                          max_len=MARK_MAX_LEN, depth=MARK_DEPTH, pit_depth=PIT_DEPTH,
                          law=("occlusion vocabulary only — every mark is a recess, so every mark "
                               "is darker and none has a lit side. Minimum extent derived from "
                               "the device gate: 1px is readable if long (the cracks), a blob is "
                               "not (the retired 4px overlay marks).")),
               crack=dict(rate=CRACK_RATE, min_tiles=CRACK_MIN_TILES, max_tiles=CRACK_MAX_TILES,
                          dirs=DIRS, scale=CRACK_SCALE, depth=CRACK_DEPTH, turn=CRACK_TURN,
                          law=("field scale, minimum readable extent as a refusal, no taper and "
                               "no feather. Replaces a per-tile overlay whose median mark was "
                               "4px.")), ladder_step=round(step, 3),
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
    man["differential"] = dict(octaves=[list(o) for o in WEAR_OCTAVES],
                               lo=WEAR_LO, hi=WEAR_HI,
                               joint_fill=list(JOINT_FILL_RUNGS), joint_break=list(JOINT_BREAK),
                               chip_rate=CHIP_RATE, spall_rate=SPALL_RATE,
                               dressing_keep=DRESSING_KEEP,
                               channel_wear=CHANNEL_WEAR, ages=list(WEAR_AGES),
                               law=("one scalar sampled by world position drives joint opening, "
                                    "chipping, dressing amplitude and the traffic bias. Periods "
                                    "5 and 11 tiles: coprime with each other and with the tile, "
                                    "so nothing lands on the grid."))
    man["wear"] = dict(grain=WEAR_GRAIN, spread=WEAR_SPREAD, arris=WEAR_ARRIS,
                       bands=WEAR_BANDS, pits=WEAR_PITS,
                       bands_ordinary=MARK_BANDS, pits_ordinary=MARK_PITS,
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
