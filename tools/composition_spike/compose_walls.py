#!/usr/bin/env python3
"""THE COMPOSITION SPIKE — build two-plane wall segments from the wall gauntlet's parts bin.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
The wall gauntlet (tools/pixellab/wall_gauntlet/FINDING.md) spent 100 generations and passed
nothing. Reading its ten rounds, everything that failed was a RELATIONSHIP between parts
(face-to-top, cap-to-course, strap-to-strapped) and everything that succeeded was a PART
(coursed masonry material, flat weathered slab material). This script takes the thesis
seriously: the generator is a materials supplier, not a mason. It supplies stone; the
composition is authored here.

THIS SESSION MAKES ZERO API CALLS. Every stone pixel comes off disk, out of the gauntlet
ledger, with its round and candidate id recorded in the manifest.

NOTHING HERE IS ART AND NOTHING HERE LANDS. The binding overlays are programmer-art mocks,
authored in this file, marked MOCK in every filename and in the manifest. ART-BIBLE-v0 §13.1
governs landing and no output of this script is a candidate for it. The question these
composites exist to put in front of a human eye is only: does a composed wall read as a wall,
and does it read as HELD.

THE TWO-PLANE RULE, AS THE RENDERER ACTUALLY SEES IT (bible §3)
--------------------------------------------------------------
DungeonRenderer computes a 4-bit cardinal mask — bit3(8)=N, bit2(4)=S, bit1(2)=E, bit0(1)=W,
set when that neighbour is WALL — then collapses 7/11 to 3 and 13/14 to 12. So the composition
rule is one line:

    SOUTH BIT CLEAR  -> floor below this wall -> the tile shows TOP BAND + FRONT FACE
    SOUTH BIT SET    -> wall below this wall  -> the tile shows TOP SURFACE only

That is the whole of §3 expressed in the mask, and it is what the gauntlet could not do: a
single generated tile had to carry a cap band whether or not the wall below it wanted one,
which is exactly the critic's round-10 objection that an identical hard-edged cap "stripes the
wall every 32 pixels when stacked".

DRAFTING RULE (bible §6.3, and the gauntlet's §5 hazard)
-------------------------------------------------------
Geometry is drawn by OCCLUSION, never by highlight. The top plane is not brightened; the top
two rows of the FACE are darkened, because a face under an overhang is occluded from every
azimuth. Nothing in these tiles declares a light direction. The gauntlet's own finding — that
at 32px "describe geometry with value" and "bake a key light" are the same vocabulary — is
why the value-matched top arm (B) exists alongside the native-value arm (A).

PALETTE (bible §5 — PLACEHOLDER, and this script proposes nothing)
------------------------------------------------------------------
Every pixel written is snapped to the union of the colours present in the parts it was built
from. Occlusion, iron, rope and tag values are all chosen FROM that set. No colour is invented
and no palette is proposed.
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
LEDGER = os.path.join(REPO, "tools/pixellab/wall_gauntlet/rounds")
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
ASSETS = "src/Presentation/assets/composition_spike"

TILE = 32
TOP_BAND = 8          # rows of top plane on a face tile. 1/4 tile; not a derived value.
OCCLUSION_ROWS = 2    # rows of face immediately under the overhang

# Tile IDs. A distinct 91xx block so a composite can never collide with a shipped tile id or
# with the tier-0 stubs (90xx).
WALL_BASE = 9200      # 9200 + mask*NVAR + variant, for masks 0..15
CORNER_BASE = 9280    # 9280..9283 — the four mask-15 outer corners
FLOOR_BASE = 9120     # 9120..9123 — the four §6.4 probe survivors
STAIR_DOWN, STAIR_UP = 9140, 9141
# VARIANT COUNT - chosen against PositionHash, not picked round.
#
# PositionHash is 7919x + 104729y. Three properties matter and they pull against each other:
#
#   MIRROR      the review corridor is deliberately symmetric about the player's column, so
#               cells x=c+d and x=c-d collide when 2*7919*d == 0 mod N. Round 1 ran N=4, where
#               that is every EVEN d - half the map an exact reflection of the other half. The
#               seat measured it (MAD 6.1 against a local texture std of 34.5) and spent a flip
#               item on it.
#   DIAGONALS   if 7919 and 104729 are congruent mod N the index depends only on (x+y) and the
#               field bands along anti-diagonals. N=7 has both congruent to 2 and does exactly
#               that - which is why round 2's seven is not round 3's nine.
#   NEIGHBOURS  orthogonally adjacent cells must not share a variant (the seat asked for this
#               in as many words).
#
# N=9: 7919 = 8 mod 9, 104729 = 5 mod 9. Different, so no diagonal banding. Neither is 0, so no
# orthogonal neighbour repeats. Mirror collisions need 16d == 0 mod 9, i.e. every 9th cell.
NVAR = 9


# Masks that occur in quantity in any real map and therefore need variants. The rest occur
# once or twice and a single tile is honest for them; emitting nine of each would be 100 dead
# PNGs per arm.
VARIANT_MASKS = frozenset((3, 12, 15))


def mask_variants(mask):
    return NVAR if mask in VARIANT_MASKS else 1


def wall_id(mask, v):
    return WALL_BASE + mask * NVAR + v

# ---------------------------------------------------------------------------------------
# THE PARTS BIN. Every entry is a real candidate on disk in the wall gauntlet ledger, with
# the rows actually used and the reason the rest were discarded.
# ---------------------------------------------------------------------------------------
FACE_PARTS = {
    "r07_00": dict(round="round07", rows=(5, 30),
                   why="coursed masonry, irregular block widths, joints at every course; "
                       "no key-light cull. Rows 0-4 (its failed cap band) discarded.",
                   verdict="FAIL - 'rows 0-4 use the identical greys as the face, so there is "
                           "no top band at all ... flat brick wallpaper with zero thickness'"),
    "r07_08": dict(round="round07", rows=(5, 30),
                   why="alternate face stock; larger blocks, more wear incident.",
                   verdict="FAIL (ledger)"),
    "r07_09": dict(round="round07", rows=(5, 30),
                   why="alternate face stock; higher contrast between blocks.",
                   verdict="FAIL (ledger)"),
}
TOP_PARTS = {
    "r04_08": dict(round="round04", rows=(0, 28),
                   why="flat weathered slab with cracks - the closest thing the gauntlet "
                       "produced to a wall top. Rows 29-31 (its baked floor shadow) discarded.",
                   verdict="FAIL (ledger)"),
    "r04_00": dict(round="round04", rows=(0, 25),
                   why="alternate slab stock; mottled, one dark stain.",
                   verdict="FAIL - 'soft mottled blobs with no joint, no course, no fixing'"),
}


def load_part(name, table):
    spec = table[name]
    p = os.path.join(LEDGER, spec["round"], "images", name + ".png")
    a = np.array(Image.open(p).convert("RGB")).astype(np.int16)
    r0, r1 = spec["rows"]
    return a[r0:r1], p, spec


def palette_of(*arrays):
    cols = set()
    for a in arrays:
        cols |= set(map(tuple, a.reshape(-1, 3).astype(int)))
    return np.array(sorted(cols), dtype=np.int16)


def snap(a, pal):
    """Snap every pixel to the nearest colour in the parts' own palette."""
    flat = a.reshape(-1, 1, 3).astype(np.int32)
    d = ((flat - pal.reshape(1, -1, 3).astype(np.int32)) ** 2).sum(2)
    return pal[d.argmin(1)].reshape(a.shape).astype(np.int16)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def mean_lum(a):
    return float((a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114).mean())


def pal_nearest_lum(pal, target):
    return min(map(tuple, pal), key=lambda c: abs(lum(c) - target))


def wrap_window(src, y0, h, dx, dy=0):
    """An h-row, 32-wide window of a part, wrapped in both axes.

    Rolling in x preserves course ROWS exactly - so neighbouring tiles keep their courses
    aligned - while moving the vertical joints, which is what stops the 32px joint signature
    the critic named in r04_08 from repeating. Rolling in y is used only for the slab, whose
    material has no courses to keep aligned and whose one strong crack would otherwise stamp
    at every cell the mask occurs.

    The source is tiled first, so a part shorter than the window never produces a seam. An
    earlier revision of this function stacked the part on itself and left a hard discontinuity
    at row 28 of every slab tile.
    """
    reps = int(np.ceil((h + abs(dy)) / src.shape[0])) + 1
    tall = np.vstack([src] * reps)
    band = np.roll(tall, dy, axis=0)[y0:y0 + h]
    return np.roll(band, dx, axis=1)[:, :TILE].copy()


# ---------------------------------------------------------------------------------------
# BINDING OVERLAYS - authored HERE, not generated. MOCK. Crude on purpose.
#
# bible §7.1: show me what holds this together.  §7.3 (Boundary, RULED): redundant, over-built,
# competent, nothing decorative, nothing exists for appearance.
#
# The thing the generator never once did, in ten rounds and a hundred candidates, is GRIP.
# Every overlay here is required to grip something nameable:
#   strap  crosses a joint AND wraps the top edge onto the top plane
#   pin    sits IN a crack - snapped to the darkest column near its nominal x
#   cramp  spans two stones across a vertical joint, feet driven into each
#   lash   wraps the edge in three turns
#   tag    hangs from a pin (§7.1: everything is tagged)
# Occlusion only: a 1px shadow under a lip, symmetric on both sides of a raised element, so
# nothing declares a direction (§6.3).
# ---------------------------------------------------------------------------------------
class Ink:
    def __init__(self, pal):
        p = sorted(map(tuple, pal), key=lum)
        self.shadow = p[0]
        self.iron = p[max(1, len(p) // 6)]
        self.pale = p[-1]
        self.rope = pal_nearest_lum(pal, lum(p[-1]) * 0.72)
        self.timber = pal_nearest_lum(pal, lum(p[0]) * 1.9)


def snap_to_joint(a, x, y0, y1, radius=5):
    """Find the darkest column within +-radius of x over rows y0..y1 - that is a mortar joint
    or a crack in the real stone. A pin driven anywhere else is decoration."""
    lo, hi = max(0, x - radius), min(TILE, x + radius + 1)
    band = a[y0:y1, lo:hi]
    scores = (band[..., 0] * .299 + band[..., 1] * .587 + band[..., 2] * .114).mean(0)
    return lo + int(scores.argmin())


def px(a, x, y, c):
    if 0 <= x < TILE and 0 <= y < TILE:
        a[y, x] = c


def rect(a, x, y, w, h, c):
    for j in range(y, y + h):
        for i in range(x, x + w):
            px(a, i, j, c)


def strap(a, ink, x, y0, y1, w=3):
    """Vertical iron strap. Starts ON the top plane (y0=0) and runs down the face: the wrap IS
    the grip.

    ROUND 2 — THE RING IS GONE. Round 1 drew a 1px shadow down BOTH sides and called it a
    symmetric contact occlusion. A dark line on every side of a small element is a closed
    keyline, and the seat read the result exactly as §12.1 warns: "each sits on top of the brick
    inside a hard black keyline ... nothing is held", "stickers laid on wallpaper". It also
    swallowed the mortar courses running up to the strap, so nothing could be seen to be
    crossed. Occlusion is now only UNDER the lip - the foot of the strap - which is what the
    drafting rule actually asks for, and the courses now run visibly into the strap on both
    sides."""
    rect(a, x, y0, w, y1 - y0 + 1, ink.iron)
    rect(a, x, y1 + 1, w, 1, ink.shadow)


def pin(a, ink, x, y, spall_x=None):
    """Driven pin: pale head, 1px occlusion under the head, sunk into the stone.

    ROUND 2: a driven pin chips the stone it is driven into. `spall_x` puts two light pixels in
    the brick beside the head, so the fixing has left a mark and reads as having gone IN rather
    than having been placed on top. The seat's words: "no pin passes into the stone"."""
    rect(a, x, y, 2, 2, ink.pale)
    rect(a, x, y + 2, 2, 1, ink.shadow)
    if spall_x is not None:
        px(a, spall_x, y, ink.pale)
        px(a, spall_x, y + 1, ink.pale)


def cramp(a, ink, x, y, w=9):
    """Iron cramp spanning two stones: a bar with a foot driven into each stone.

    ROUND 2: the caller now centres this on a real vertical joint found in the stone, and the
    bar is short enough that the joint is visible entering above it and leaving below it. A
    cramp that covers the joint it spans cannot be seen to span anything - the seat's "none
    bridges a joint or a crack"."""
    rect(a, x, y, w, 2, ink.iron)
    rect(a, x, y + 2, w, 1, ink.shadow)
    rect(a, x, y - 1, 2, 1, ink.iron)
    rect(a, x + w - 2, y - 1, 2, 1, ink.iron)


def joint_in_band(a, y0, y1, x_lo=3, x_hi=TILE - 3):
    """The darkest column over a course band - a vertical mortar joint in the real stone."""
    band = a[y0:y1, x_lo:x_hi]
    scores = (band[..., 0] * .299 + band[..., 1] * .587 + band[..., 2] * .114).mean(0)
    return x_lo + int(scores.argmin())


def lash(a, ink, x, y0, turns=3):
    """Rope wrapping the edge - three turns over the lip and down onto the face."""
    for t in range(turns):
        yy = y0 + t * 3
        rect(a, x, yy, 7, 2, ink.rope)
        rect(a, x, yy + 2, 7, 1, ink.shadow)   # under the turn only


def tag(a, ink, x, y):
    """§7.1: the institution has inventoried its world. Things wear their paperwork."""
    px(a, x + 2, y - 2, ink.iron)
    px(a, x + 2, y - 1, ink.iron)
    rect(a, x, y, 5, 4, ink.pale)
    rect(a, x + 1, y + 1, 3, 1, ink.shadow)
    rect(a, x + 1, y + 2, 2, 1, ink.shadow)
    rect(a, x, y + 4, 5, 1, ink.shadow)


# Per-variant binding scripts. Not every variant is bound: a run in which every tile carries a
# repair reads as pattern, not as repair. Two of four face variants are heavily bound, one is
# lightly bound, one is bare stone.
def bind_face(a, ink, v):
    """ROUND 2. Seven variants, three of them bare stone.

    Every element is now placed against a joint FOUND in the stone rather than at a nominal x,
    and is narrow enough that the joint is visible arriving and leaving. The seat's round-1
    charge was that the hardware "crosses nothing" and "none bears on anything"; position now
    has to explain itself.
    """
    if v == 0:
        x = joint_in_band(a, TOP_BAND + 2, TILE)      # a vertical joint in the face
        strap(a, ink, x - 1, 0, 21)                   # straddles it, wraps the top lip
        pin(a, ink, x - 1, 2, spall_x=x + 3)
        pin(a, ink, x - 1, 18, spall_x=x - 3)         # over-built: pinned top and bottom
    elif v == 1:
        x = joint_in_band(a, 20, 28)
        cramp(a, ink, x - 4, 22, w=9)                 # spans the two stones either side of it
        pin(a, ink, x - 4, 25, spall_x=x - 6)
        pin(a, ink, x + 3, 25, spall_x=x + 6)
    elif v == 2:
        x = joint_in_band(a, TOP_BAND + 2, 24)
        strap(a, ink, x - 1, 0, 26, w=4)
        pin(a, ink, x, 3, spall_x=x + 4)
        pin(a, ink, x, 23, spall_x=x - 3)
        tag(a, ink, 4, 20)                            # §7.1: things wear their paperwork
    elif v == 3:
        lash(a, ink, 12, 4)                           # rope over the lip and down the face
        x = joint_in_band(a, 22, 30)
        cramp(a, ink, x - 4, 25, w=9)                 # a repair laid over a prior repair
    # v 4, 5, 6 are bare stone: a run where every tile carries a repair reads as pattern.


def bind_slab(a, ink, v):
    """ROUND 2. The wall seen from above: cramps between coping stones, banding straps
    crossing the mass, pins driven into the top. Four of seven variants bare."""
    if v == 0:
        x = joint_in_band(a, 8, 16)
        cramp(a, ink, x - 5, 11, w=11)
        pin(a, ink, x - 5, 14, spall_x=x - 7)
        pin(a, ink, x + 4, 14, spall_x=x + 7)
    elif v == 1:
        x = snap_to_joint(a, 18, 4, 28)
        rect(a, x, 5, 3, 21, ink.iron)           # a banding strap seen from above
        rect(a, x, 26, 3, 1, ink.shadow)         # under the end only - no keyline (round 2)
        pin(a, ink, x, 7, spall_x=x + 4)
        pin(a, ink, x, 21, spall_x=x - 2)
    elif v == 2:
        x = joint_in_band(a, 18, 26)
        cramp(a, ink, x - 4, 21, w=8)
        pin(a, ink, snap_to_joint(a, 24, 4, 14), 8, spall_x=None)
    # v 3..6 are bare stone.


# ---------------------------------------------------------------------------------------
# TILE CONSTRUCTION
# ---------------------------------------------------------------------------------------
def make_slab(top_src, pal, ink, v, bind):
    # ROUND 2: dy only, dx=0. Rolling the slab in x gave every variant different left and right
    # edges, so a wall mass built from mixed variants carried a hard vertical seam at EVERY tile
    # boundary — and the seat could not then tell the corridor edge from those, reporting the
    # boundary line as "identical to seams that recur every two tiles inside the solid mass".
    # With dx=0 all variants share the part's own left/right edges and the only line left on a
    # wall/floor boundary is the occlusion, which now means exactly one thing.
    a = wrap_window(top_src, 0, TILE, 0, dy=v * 11 + 1)
    if bind:
        bind_slab(a, ink, v)
    return snap(a, pal)


def make_face(face_src, top_src, pal, ink, v, bind):
    band = wrap_window(top_src, 0, TOP_BAND, 0, dy=v * 11 + 1)
    body_h = TILE - TOP_BAND
    body = wrap_window(face_src, 0, body_h, v * 8)
    a = np.vstack([band, body]).astype(np.int16)

    # OCCLUSION, not highlight. The face directly under the overhang is shadowed; the top plane
    # is left exactly as the part supplied it. Nothing is brightened anywhere in this file.
    for k, f in enumerate((0.55, 0.78)[:OCCLUSION_ROWS]):
        a[TOP_BAND + k] = (a[TOP_BAND + k] * f).astype(np.int16)

    a = snap(a, pal)
    if bind:
        bind_face(a, ink, v)
    return snap(a, pal)


NORTH_BIT, SOUTH_BIT_, EAST_BIT, WEST_BIT = 8, 4, 2, 1
# ROUND 2: three steps rather than two. The seat culled both native-top arms `cannot-read` at
# 8 and 6 grey levels of wall-to-floor separation and asked for 25 or more, holding under low
# light. The value-matched arm already carries 26 by material; this deepens the boundary itself
# so the mass edge reads as an edge on all four orientations, not only where a face exists.
EDGE_STEPS = (0.42, 0.62, 0.82)


def occlude_edges(a, mask):
    """Darken the wall's own edge wherever the neighbouring cell is FLOOR.

    This is not in the brief and it is not decoration; without it the corridor does not read.
    The first lit capture (evidence/boundB_solofloor_lit.png, before this) put a lit wall top
    at luminance 96 beside a lit floor at 122 with no boundary of any kind between them, and
    a player could not tell which cells they could walk on. The shipped Oryx placeholder tiles
    this renderer's mask table was fitted to do exactly this — 184 carries a dark band along
    its bottom edge, 187 dark columns down both sides — so the grammar the engine already
    expects includes an occluded edge, and §3's two planes do not on their own supply one.

    Occlusion, not illumination (§6.3): a wall edge is occluded from the floor beside it from
    every azimuth, so nothing here declares a light direction. Flagged for the human gate as a
    possible §12.1 tension — a dark edge on every wall/floor boundary is a second linear
    system, and §12.1 reserves that job for straps and bands.

    The SOUTH edge is never treated here: where south is floor the tile already carries a front
    face, which is §3's answer to that edge.
    """
    for k, f in enumerate(EDGE_STEPS):
        if not (mask & NORTH_BIT):
            a[k] = (a[k] * f).astype(np.int16)
        if not (mask & WEST_BIT):
            a[:, k] = (a[:, k] * f).astype(np.int16)
        if not (mask & EAST_BIT):
            a[:, TILE - 1 - k] = (a[:, TILE - 1 - k] * f).astype(np.int16)
    return a


def make_wall(mask, face_src, top_src, pal, ink, v, bind, keylight=False):
    """One wall tile for one autotile mask.

    SOUTH BIT CLEAR -> floor below -> top band + occlusion + front face (bible §3).
    SOUTH BIT SET   -> wall below  -> top surface only; the face is behind the wall in front.
    Then the edges adjacent to floor are occluded.
    """
    if mask & SOUTH_BIT_:
        a = make_slab(top_src, pal, ink, v, bind)
    elif keylight:
        a = make_plant(face_src, top_src, pal, ink, v)
    else:
        a = make_face(face_src, top_src, pal, ink, v, bind)
    return snap(occlude_edges(a.copy(), mask), pal)


def make_corner(diag_bit, face_src, top_src, pal, ink, v, bind):
    """A mask-15 outer corner: all four cardinals are wall, one DIAGONAL is floor. Only that
    corner of the tile touches open space, so only that corner is occluded."""
    a = make_slab(top_src, pal, ink, v, bind).copy()
    xs = range(3) if diag_bit in ("nw", "sw") else range(TILE - 3, TILE)
    ys = range(3) if diag_bit in ("nw", "ne") else range(TILE - 3, TILE)
    for j in ys:
        for i in xs:
            a[j, i] = (a[j, i] * 0.62).astype(np.int16)
    return snap(a, pal)


def make_plant(face_src, top_src, pal, ink, v=0):
    """THE PLANT (LOOP-PROCESS §4, bible §13.5). A composed segment carrying the exact defect
    §6.3 forbids: every course run light at its top rows and dark at its bottom rows - a baked
    overhead key light. The gauntlet's round 8 manufactured this defect by accident and its own
    critic culled three candidates for it. A critic that passes this one has not demonstrated it
    can fail, and its verdicts on the real arms do not count."""
    a = make_face(face_src, top_src, pal, ink, v, bind=True).astype(np.float32)
    for y in range(TOP_BAND, TILE):
        phase = (y - TOP_BAND) % 8
        a[y] *= (1.28 if phase < 3 else 0.72)
    return snap(np.clip(a, 0, 255).astype(np.int16), pal)


# ---------------------------------------------------------------------------------------
# THEME CONFIG
#
# The mask table is where §3 lives. South bit set -> slab; south bit clear -> face.
# Every mask gets the full variant list; the engine picks by PositionHash, exactly as floors
# already do. Before this session wall masks were scalar-only and a corridor edge stamped one
# tile at every cell it occurred - see tools/composition_spike/README.md.
# ---------------------------------------------------------------------------------------
SOUTH_BIT = 4


def theme_yaml(tile_root, pattern, floor_ids):
    masks = "\n".join(
        "      %d: [%s]   # %s" % (
            m, ", ".join(str(wall_id(m, v)) for v in range(mask_variants(m))),
            "top surface (wall below)" if (m & SOUTH_BIT)
            else "top band + front face (floor below)")
        for m in range(16))
    fill = ", ".join(str(wall_id(15, v)) for v in range(NVAR))
    floors = "[" + ", ".join(str(i) for i in floor_ids) + "]"
    return f"""# GENERATED by tools/composition_spike/compose_walls.py - do not hand-edit.
# THE COMPOSITION SPIKE. Composed wall segments + MOCK binding overlays. NOT ART, NOT A PALETTE,
# NOT A CANDIDATE. ART-BIBLE-v0 §13.1 governs landing; nothing here is offered for it.
tile_root: "{tile_root}"
tile_pattern: "{pattern}"

themes:
  sandstone:
    floor_primary: {floors}
    floor_accent: {floors}
    floor_dark: {floors}
    floor_interior: {floors}
    floor_worn: {floors}
    wall_autotile:
{masks}
    wall_diagonal:
      corner_outer_nw: [{CORNER_BASE + 0}]
      corner_outer_ne: [{CORNER_BASE + 1}]
      corner_outer_sw: [{CORNER_BASE + 2}]
      corner_outer_se: [{CORNER_BASE + 3}]
      # ROUND 3: a LIST. interior_fill is 267 of the ~300 wall cells in this corridor, so a
      # scalar here stamped one tile across nearly the whole solid mass while the mask lists
      # varied the visible 6%. The seat culled on it twice before the cause was found.
      interior_fill: [{fill}]
    stair_down: [{STAIR_DOWN}]
    stair_up: [{STAIR_UP}]

default_theme: sandstone
"""


# ---------------------------------------------------------------------------------------
# SEGMENT SHEET - the composition made visible outside the engine.
#
# NOT A REVIEW INSTRUMENT. Bible §13.1: no candidate is ever approved from a contact sheet, and
# §6.3: a receive-light asset judged unlit is judged by the wrong instrument. This sheet exists
# so the composition round has something to critique between engine captures, and so the report
# can show what was assembled. The verdict comes from the lit capture, on device.
# ---------------------------------------------------------------------------------------
SEGMENTS = {
    "south_facing_run": [
        "########",
        "########",
        "........",
        "########",
        "########",
    ],
    "straight_run": [
        "#####",
        "##.##",
        "##.##",
        "##.##",
        "##.##",
        "##.##",
        "#####",
    ],
    "corner": [
        "#######",
        "###.###",
        "###.###",
        "#.....#",
        "###.###",
        "###.###",
        "#######",
    ],
}


def position_hash(x, y):
    return abs((x * 7919 + y * 104729) & 0x7FFFFFFF)


def render_segment(grid, walls, floors):
    """Reimplements DungeonRenderer's mask + 7/11->3, 13/14->12 collapse + PositionHash pick.
    If this disagrees with the engine, the engine capture is the truth and this is the bug."""
    H, W = len(grid), len(grid[0])

    def isw(x, y):
        if x < 0 or y < 0 or x >= W or y >= H:
            return True
        return grid[y][x] == "#"

    out = Image.new("RGB", (W * TILE, H * TILE))
    for y in range(H):
        for x in range(W):
            if not isw(x, y):
                t = floors[position_hash(x, y) % len(floors)]
            else:
                c = (8 if isw(x, y - 1) else 0) | (4 if isw(x, y + 1) else 0) \
                    | (2 if isw(x + 1, y) else 0) | (1 if isw(x - 1, y) else 0)
                c = {7: 3, 11: 3, 13: 12, 14: 12}.get(c, c)
                pool = walls[c]
                t = pool[position_hash(x, y) % len(pool)]
            out.paste(Image.fromarray(t.astype(np.uint8)), (x * TILE, y * TILE))
    return out


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ROUND 2 - TOP PART SWAPPED. r04_08 carries one strong branching crack, and with four variants
# it landed on a regular two-tile pitch in mirrored pairs; the seat called it "bird tracks" and
# spent a flip item on it. r04_00 is the alternate slab already in the parts bin - mottled, one
# dark stain, no linear signature - so the swap is a parts choice, not a redraw. Exactly the
# move this spike exists to test: change the material, keep the composition.
ARMS = {
    # arm            top part   value-match the top plane to the face?  bindings?
    "boundA":   dict(top="r04_00", match=False, bind=True,
                     note="native R4 slab top. The top plane keeps the part's own value, which "
                          "is ~30 luminance above the face. That value step is the gauntlet's "
                          "§5 hazard: at 32px it may read as a key light from above."),
    "boundB":   dict(top="r04_00", match=True, bind=True,
                     note="DERIVED top: the same R4 slab, luminance-matched to the face and "
                          "snapped back to the parts palette. Plane separation is then carried "
                          "by material and occlusion ONLY, which is the strict §6.3 reading."),
    "ctrlA":    dict(top="r04_00", match=False, bind=False,
                     note="control for boundA - same stones, overlays omitted."),
    "ctrlB":    dict(top="r04_00", match=True, bind=False,
                     note="control for boundB - same stones, overlays omitted."),
    "plant":    dict(top="r04_00", match=True, bind=True, keylight=True,
                     note="THE PLANT. Identical to boundB except every course is run light at "
                          "its top rows and dark at its bottom rows - a baked overhead key "
                          "light, the exact defect §6.3 forbids and the one the gauntlet's own "
                          "round 8 manufactured by accident. It goes into the critic set under "
                          "an anonymous code. A critic that passes it has not demonstrated it "
                          "can fail and its verdicts on the real arms do not count "
                          "(LOOP-PROCESS §4, bible §13.5)."),
}


def match_top(top_src, face_src):
    fl, tl = mean_lum(face_src), mean_lum(top_src)
    scaled = np.clip(top_src.astype(np.float32) * (fl / tl), 0, 255).astype(np.int16)
    return scaled, ("DERIVATION: luminance scaled by %.3f to match the face plane (%.1f -> %.1f)"
                    % (fl / tl, tl, fl))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--face", default="r07_00", choices=list(FACE_PARTS))
    ap.add_argument("--out", default=ASSETS)
    ap.add_argument("--sheet-zoom", type=int, default=6)
    args = ap.parse_args()

    face_src, face_path, face_spec = load_part(args.face, FACE_PARTS)
    manifest = {
        "what": "MOCK composed wall segments. Not art, not a palette, not a landing candidate.",
        "api_calls": 0,
        "generated_by": "tools/composition_spike/compose_walls.py",
        "parts": [], "arms": {},
    }

    out_root = os.path.join(REPO, args.out)
    os.makedirs(out_root, exist_ok=True)

    # Floors: all four §6.4 probe survivors, held constant across every arm, so a difference
    # between arms can never be a floor difference. They are context here, not the subject.
    surv = json.load(open(os.path.join(SURVIVORS, "MANIFEST.json")))["survivors"]
    floor_ids = [FLOOR_BASE + i for i in range(len(surv))]
    floor_arrs = []
    for i, s in enumerate(surv):
        fa = np.array(Image.open(os.path.join(SURVIVORS, s["file"])).convert("RGB")).astype(np.int16)
        floor_arrs.append(fa)
        manifest["parts"].append(dict(role="floor", id=FLOOR_BASE + i, code=s["code"],
                                      provenance="§6.4 probe survivor %s" % s["file"],
                                      mock=False))
    manifest["parts"].append(dict(role="face", id="FACE_%s" % args.face, mock=False,
                                  provenance="wall gauntlet ledger %s/images/%s.png"
                                             % (face_spec["round"], args.face),
                                  rows_used=list(face_spec["rows"]), why=face_spec["why"],
                                  ledger_verdict=face_spec["verdict"]))
    manifest["parts"].append(dict(role="binding overlays", id="MOCK", mock=True,
                                  provenance="authored in compose_walls.py this session; "
                                             "never generated, never corpus"))

    sheet_dir = os.path.join(HERE, "segments")
    os.makedirs(sheet_dir, exist_ok=True)

    for arm, cfg in ARMS.items():
        top_src, top_path, top_spec = load_part(cfg["top"], TOP_PARTS)
        derived = ""
        if cfg["match"]:
            top_src, derived = match_top(top_src, face_src)

        pal = palette_of(face_src, top_src, *floor_arrs)
        ink = Ink(pal)
        walls = {m: [make_wall(m, face_src, top_src, pal, ink, v, cfg["bind"],
                              cfg.get("keylight", False)) for v in range(mask_variants(m))]
                 for m in range(16)}
        corners = [make_corner(k, face_src, top_src, pal, ink, v, cfg["bind"])
                   for v, k in enumerate(("nw", "ne", "sw", "se"))]

        d = os.path.join(out_root, arm)
        os.makedirs(d, exist_ok=True)
        written = []

        def emit(tid, arr):
            p = os.path.join(d, "MOCK_comp_%d.png" % tid)
            Image.fromarray(arr.astype(np.uint8)).save(p)
            written.append(p)

        for m in range(16):
            for v, a in enumerate(walls[m]):
                emit(wall_id(m, v), a)
        for i, a in enumerate(corners):
            emit(CORNER_BASE + i, a)
        for i, fa in enumerate(floor_arrs):
            emit(FLOOR_BASE + i, fa)
        emit(STAIR_DOWN, walls[15][0])   # unused by the review scene; the role must resolve
        emit(STAIR_UP, walls[15][1])

        theme = os.path.join(out_root, "tile_themes_%s.yaml" % arm)
        with open(theme, "w") as f:
            f.write(theme_yaml("res://%s/%s" % (args.out, arm), "MOCK_comp_{id}.png", floor_ids))

        sheets = {}
        for name, grid in SEGMENTS.items():
            im = render_segment(grid, walls, floor_arrs)
            z = args.sheet_zoom
            im = im.resize((im.width * z, im.height * z), Image.NEAREST)
            p = os.path.join(sheet_dir, "%s_%s.png" % (arm, name))
            im.save(p)
            sheets[name] = os.path.relpath(p, REPO)

        manifest["arms"][arm] = dict(
            face_part=args.face, top_part=cfg["top"], top_rows=list(top_spec["rows"]),
            top_why=top_spec["why"],
            bindings="MOCK - authored in compose_walls.py" if cfg["bind"] else "none (control)",
            derivation=derived, note=cfg["note"],
            theme=os.path.relpath(theme, REPO), segment_sheets=sheets,
            palette_size=int(len(pal)),
            face_plane_lum=round(mean_lum(face_src), 1),
            top_plane_lum=round(mean_lum(top_src), 1),
            tiles={os.path.basename(p): sha256(p) for p in written})
        print("%-8s face=%s top=%s bind=%-5s palette=%d  face_lum=%.1f top_lum=%.1f -> %s"
              % (arm, args.face, cfg["top"], cfg["bind"], len(pal),
                 mean_lum(face_src), mean_lum(top_src), os.path.relpath(d, REPO)))

    # The plant, built from the same stones so the critic cannot separate it by material.
    top_src, _, _ = load_part(ARMS["boundB"]["top"], TOP_PARTS)
    top_src, _ = match_top(top_src, face_src)
    pal = palette_of(face_src, top_src, *floor_arrs)
    ink = Ink(pal)
    walls = {m: [make_wall(m, face_src, top_src, pal, ink, v, True, keylight=True)
                 for v in range(NVAR)] for m in range(16)}
    im = render_segment(SEGMENTS["south_facing_run"], walls, floor_arrs)
    z = args.sheet_zoom
    im.resize((im.width * z, im.height * z), Image.NEAREST).save(
        os.path.join(sheet_dir, "plant_south_facing_run.png"))
    manifest["plant"] = dict(
        file="tools/composition_spike/segments/plant_south_facing_run.png",
        defect="key-light - every course light at its top rows, dark at its bottom rows",
        why="LOOP-PROCESS §4 / bible §13.5: no instrument's pass counts until it has "
            "demonstrated it can fail. A critic that passes this voids its round.")
    print("plant    -> tools/composition_spike/segments/plant_south_facing_run.png")

    with open(os.path.join(HERE, "PARTS_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("\nmanifest -> tools/composition_spike/PARTS_MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
