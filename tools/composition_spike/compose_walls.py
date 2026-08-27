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
    "r04_03": dict(round="round04", rows=(11, 24),
                   why="third slab stock, added in round 4 so the top plane's variants differ "
                       "in content and not only in phase. Rows 0-10 hold a centred dark bar "
                       "the ledger critic called a stamped motif; only the clean mottle below "
                       "it is used.",
                   verdict="FAIL - 'the bottom seven rows are a single flat dark value with no "
                           "incident - a painted floor shadow, not wall - and the plate above "
                           "it is a centred motif that stamps identically every tile'"),
}


def PART_TABLE(name):
    """Top stock now draws on both tables: R4 slabs and, under the brief's own fallback clause,
    R6/R7 coursed material cropped for use as a top plane."""
    return TOP_PARTS if name in TOP_PARTS else FACE_PARTS


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
        # ROUND 5: longer, so it runs a full brick past the break at each end, and the pin heads
        # sit INSIDE the bar's silhouette. The seat: "delete every instance where two pale dots
        # sit above a dark bar rather than inside it - at played size that arrangement reads as
        # two eyes over a mouth." It does, and that is bible §1.3's named trap arriving by
        # accident in a mock.
        cramp(a, ink, x - 6, 22, w=13)
        pin(a, ink, x - 6, 22, spall_x=x - 8)
        pin(a, ink, x + 5, 22, spall_x=x + 8)
    elif v == 2:
        x = joint_in_band(a, TOP_BAND + 2, 24)
        strap(a, ink, x - 1, 0, 26, w=4)
        pin(a, ink, x, 3, spall_x=x + 4)
        pin(a, ink, x, 23, spall_x=x - 3)
        tag(a, ink, 4, 20)                            # §7.1: things wear their paperwork
    elif v == 3:
        lash(a, ink, 12, 4)                           # rope over the lip and down the face
        x = joint_in_band(a, 22, 30)
        cramp(a, ink, x - 6, 25, w=13)                # a repair laid over a prior repair
        pin(a, ink, x - 6, 25, spall_x=x - 8)
    # v 4, 5, 6 are bare stone: a run where every tile carries a repair reads as pattern.


def bind_slab(a, ink, v):
    """ROUND 2. The wall seen from above: cramps between coping stones, banding straps
    crossing the mass, pins driven into the top. Four of seven variants bare."""
    if v == 0:
        x = joint_in_band(a, 8, 16)
        cramp(a, ink, x - 6, 11, w=13)
        pin(a, ink, x - 6, 11, spall_x=x - 8)         # ROUND 5: heads inside the bar
        pin(a, ink, x + 5, 11, spall_x=x + 8)
    elif v == 1:
        x = snap_to_joint(a, 18, 4, 28)
        rect(a, x, 5, 3, 21, ink.iron)           # a banding strap seen from above
        rect(a, x, 26, 3, 1, ink.shadow)         # under the end only - no keyline (round 2)
        pin(a, ink, x, 7, spall_x=x + 4)
        pin(a, ink, x, 21, spall_x=x - 2)
    elif v == 2:
        x = joint_in_band(a, 18, 26)
        cramp(a, ink, x - 6, 21, w=13)
        pin(a, ink, x - 6, 21, spall_x=x - 8)
    # v 3..6 are bare stone.


# ---------------------------------------------------------------------------------------
# TILE CONSTRUCTION
# ---------------------------------------------------------------------------------------
# ROUND 5. The face plane gets the same treatment the top plane got in round 4, for the same
# reason and on the seat's own instruction: "replace whole 32px stretches of wall with re-laid
# patches using a different brick module, bond and mortar colour, hard-edged against the
# original brickwork." Three ledger parts with DIFFERENT course rows means neighbouring face
# tiles do not line up - which in ordinary masonry would be a defect and here is the point.
# The face is constant across arms by design; the arms vary the top plane.
# ROUND 6 — REVERTED. Round 5 gave the face plane three parts on the seat's instruction to lay
# "re-laid patches using a different brick module ... hard-edged against the original
# brickwork", and it REGRESSED both arms it touched: the R4 arms went from `cannot-read` to
# `noise` ("vertical autocorrelation shows no course period at all"), because three parts with
# three different course rows destroy the course period that made the masonry read as masonry
# in the first place. LOOP-PROCESS §2 says fix rounds regress and that it is measured fact
# rather than caution; this is the measurement.
#
# The face keeps ONE part, therefore, and one course period. The round-5 overlay fixes stay —
# they were a real defect and they did not regress. Mixing parts works on the top plane, whose
# material has no period to destroy, and not on the face, whose whole legibility is its period.
FACE_STOCK = ["r07_00"]

# The top-plane question is settled: round 4 put R7-coursed material against R4 slab stock and
# the coursed top took the top two ranking places while R4 was culled `cannot-read` five times.
# The ruled rounds hold it constant and vary only what the ruling names.
TOP_COURSED = ["r07_00", "r07_08", "r07_09"]

# The coping course. r04_00 is R4 slab stock - mottled, smooth, no coursing, and about 28
# luminance above the coursed material - so a cap drawn from it is a different STONE beside the
# wall face rather than a brighter band of the same stone. Held at its native value: the point
# is the material contrast, and scaling it would just make it a highlight again.
COPING_PART = "r04_00"


def build_face_stock():
    out = []
    for i in range(NVAR):
        name = FACE_STOCK[i % len(FACE_STOCK)]
        src, _, _ = load_part(name, FACE_PARTS)
        out.append((src, name, i // len(FACE_STOCK)))
    return out


def build_top_stock(part_names, face_src, albedo=None, floors_lum=None):
    """ROUND 4. The top plane's variants come from SEVERAL parts, not several offsets of one.

    Round 3 measured 0.441 tile-to-mean correlation across nine interior_fill variants and
    control 3 moved 18% of the capture's pixels, so the variants were unquestionably reaching
    the renderer - and the seat still reported "the same 32px stamp repeated identically ...
    without a single variation". Measuring the RENDERED FIELD settled it: median block
    correlation 0.772, zero identical pairs out of 300. The seat's literal claim is false and
    its perception is correct. Nine vertical offsets of ONE part still read as one part.

    The fix is therefore more PARTS, not more offsets - which is the whole thesis of this spike
    applied to itself. Each arm now names a list of ledger parts and the variants cycle through
    them, so variant content differs rather than only variant phase.
    """
    stock = []
    for i in range(NVAR):
        name = part_names[i % len(part_names)]
        table = TOP_PARTS if name in TOP_PARTS else FACE_PARTS
        src, _, spec = load_part(name, table)
        if albedo is None:
            src, _ = match_top(src, face_src)          # rounds 1-6: match the FACE
        else:
            src, _ = scale_top_to(src, albedo * floors_lum)   # ruled rounds: target the FLOOR
        stock.append((src, name, i // len(part_names)))
    return stock


def make_slab(top_src, pal, ink, phase, bind, v=None):
    # ROUND 2: dy only, dx=0. Rolling the slab in x gave every variant different left and right
    # edges, so a wall mass built from mixed variants carried a hard vertical seam at EVERY tile
    # boundary — and the seat could not then tell the corridor edge from those, reporting the
    # boundary line as "identical to seams that recur every two tiles inside the solid mass".
    # With dx=0 all variants share the part's own left/right edges and the only line left on a
    # wall/floor boundary is the occlusion, which now means exactly one thing.
    a = wrap_window(top_src, 0, TILE, 0, dy=phase * 11 + 1)
    if bind:
        bind_slab(a, ink, v if v is not None else phase)
    return snap(a, pal)


def make_face(face_src, top_src, pal, ink, v, bind, phase=None):
    ph = v if phase is None else phase
    band = wrap_window(top_src, 0, TOP_BAND, 0, dy=ph * 11 + 1)
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
# PLANE-BOUNDARY OCCLUSION - RULED (Rafe, 2026-08-26): "plane-boundary occlusion is form,
# legal and required; the ring stays banned." The §12.1 tension this session flagged is resolved
# and this is no longer a risk to hedge, it is a requirement. What the two ruled rounds spend
# themselves on is how DEEP it has to be before the boundary reads as a plane rather than as a
# hairline - six critic rounds called it "a 1-2px line", "a single dark pixel line", "a hairline".
#
# Legal because it sits on the wall's own edge, only where floor is adjacent, and is identical
# under every azimuth. Banned would be a RING: a dark outline around a thing regardless of what
# adjoins it. This is the opposite construction - not on the sprite, on the boundary between two
# planes - and under the ruling it is form.
EDGE_PROFILES = {
    "round6": (0.42, 0.62, 0.82),               # what rounds 2-6 carried
    "deep":   (0.26, 0.40, 0.56, 0.72, 0.86),   # five steps: form, not a line
    "none":   (),                               # round 7's isolation arm
    # ROUND 8. Round 7's seat, blind, said of the five-step version: "the wall carries a graded
    # dark rim on all four sides that is equally dark on the edge facing the player's lamp and
    # the edge facing away, so it is a RIM, NOT A THICKNESS". It is right, and the omnidirectional
    # property it objects to is the very thing that makes the construction legal. Depth cannot
    # come from making the rim more directional - that is the forbidden move. It has to come from
    # the edge being a different MATERIAL, which is what it asked for twice:
    #
    #   "Replace it with a 3px cap band drawn in a smoother, paler stone than the wall face,
    #    running along the wall's top surface so the cap is a different material from the
    #    coursing below it."
    #
    # Legal under the 2026-08-26 ruling: §6.3 forbids a light DIRECTION, and a coping course of
    # smoother, paler stone laid along every floor-facing edge equally declares none. It is a
    # material, not a lamp. See CAP_ROWS below - "cap" puts the hard occlusion on the outermost
    # pixel where the mass actually stops, the coping inside it, and a soft step back into the
    # coursed body.
    "cap":    (0.30, None, None, None, 0.86),
}
CAP_ROWS = (1, 2, 3)      # indices in the "cap" profile that take coping MATERIAL, not shading

# The top plane's ALBEDO as a fraction of the floors' mean luminance. A declared material value
# and not a light: §6.3 forbids depicting a light DIRECTION, and a stone darker than the floor
# beneath it is a stone, not a lamp. Every seat that culled `cannot-read` measured this ratio,
# and round 4's asked for 0.70 or below in as many words.
TOP_ALBEDO_TARGET = 0.62


def occlude_edges(a, mask, steps=EDGE_PROFILES["round6"], coping=None):
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
    for k, f in enumerate(steps):
        # f is None where the profile wants COPING MATERIAL rather than shading. The coping is
        # a different part - paler, smoother, no coursing - so the wall's top edge reads as a
        # coping course laid on a coursed mass, which is a material change and not a highlight.
        if not (mask & NORTH_BIT):
            a[k] = coping[k] if (f is None and coping is not None) \
                else (a[k] * (f if f is not None else 1.0)).astype(np.int16)
        if not (mask & WEST_BIT):
            a[:, k] = coping[:, k] if (f is None and coping is not None) \
                else (a[:, k] * (f if f is not None else 1.0)).astype(np.int16)
        if not (mask & EAST_BIT):
            a[:, TILE - 1 - k] = coping[:, TILE - 1 - k] if (f is None and coping is not None) \
                else (a[:, TILE - 1 - k] * (f if f is not None else 1.0)).astype(np.int16)
    return a


def deepen_joints(a, factor):
    """Deepen the mortar joints already in the stone. Authored SELF-OCCLUSION between blocks.

    ROUND 8, and it is the variable round 7's seat identified without being asked. Its ranking
    separator: "The top has the deepest gaps between courses, so the wall reads as stones
    somebody stacked and something is holding; the bottom has the shallowest, so the same wall
    reads as a pattern printed on the ground." The arm it ranked first got its deep joints from
    the PLANT's baked per-course banding - i.e. illegally, and only on one axis. This gets the
    same read legally: every joint in the material, deepened equally, no direction declared.

    RULED (Rafe, 2026-08-26): authored occlusion is law; receive-light never meant form-free.
    A joint is the gap between two stones and the shadow in it is form.
    """
    if factor >= 1.0:
        return a
    L = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    joints = L < np.median(L) * 0.82
    out = a.copy()
    out[joints] = (out[joints] * factor).astype(np.int16)
    return out


def make_wall(mask, face_src, top_src, pal, ink, v, bind, keylight=False, phase=None,
              edge="round6", joints=1.0, coping_src=None):
    """One wall tile for one autotile mask.

    SOUTH BIT CLEAR -> floor below -> top band + occlusion + front face (bible §3).
    SOUTH BIT SET   -> wall below  -> top surface only; the face is behind the wall in front.
    Then the edges adjacent to floor are occluded.
    """
    ph = v if phase is None else phase
    if mask & SOUTH_BIT_:
        a = make_slab(top_src, pal, ink, ph, bind, v)
    elif keylight:
        a = make_plant(face_src, top_src, pal, ink, v, ph)
    else:
        a = make_face(face_src, top_src, pal, ink, v, bind, ph)
    a = deepen_joints(a, joints)
    coping = None
    if coping_src is not None and edge == "cap":
        coping = wrap_window(coping_src, 0, TILE, 0, dy=(v * 11 + 1))
    return snap(occlude_edges(a.copy(), mask, EDGE_PROFILES[edge], coping), pal)


def make_corner(diag_bit, face_src, top_src, pal, ink, v, bind, phase=0):
    """A mask-15 outer corner: all four cardinals are wall, one DIAGONAL is floor. Only that
    corner of the tile touches open space, so only that corner is occluded."""
    a = make_slab(top_src, pal, ink, phase, bind, v).copy()
    xs = range(3) if diag_bit in ("nw", "sw") else range(TILE - 3, TILE)
    ys = range(3) if diag_bit in ("nw", "ne") else range(TILE - 3, TILE)
    for j in ys:
        for i in xs:
            a[j, i] = (a[j, i] * 0.62).astype(np.int16)
    return snap(a, pal)


def make_plant(face_src, top_src, pal, ink, v=0, phase=None):
    """THE PLANT (LOOP-PROCESS §4, bible §13.5). A composed segment carrying the exact defect
    §6.3 forbids: every course run light at its top rows and dark at its bottom rows - a baked
    overhead key light. The gauntlet's round 8 manufactured this defect by accident and its own
    critic culled three candidates for it. A critic that passes this one has not demonstrated it
    can fail, and its verdicts on the real arms do not count."""
    a = make_face(face_src, top_src, pal, ink, v, True, phase).astype(np.float32)
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
    # ROUND 8 - the second and last ruled round. Round 7 answered half the ruling and was culled
    # at step 1 on the other half by something no arm varied:
    #
    #   * WALL-TOP VALUE SEPARATION: ANSWERED. `after` at 0.62 of the floors' luminance ranked
    #     2nd; `before` at 0.76 ranked LAST of five, the seat reading the lighter wall as "the
    #     ambient lift kills the light pool's edge". The ruled variable moved the right way.
    #   * PLANE-BOUNDARY OCCLUSION: ANSWERED, and it is the §12.1 ruling's evidence. The arm
    #     with it switched off was the one the seat said had "no edge treatment whatsoever ...
    #     stripping the wall/floor boundary shading removes the last thing making the wall read
    #     as a mass rather than a change of pattern". That isolation is done; its slot is
    #     reused here.
    #   * ALL FIVE CULLED `outline` - for the §6.4 SURVIVOR FLOORS' baked keyline, which no arm
    #     varies. Removed as a labelled MOCK derivation (dering_floors.py) so the wall questions
    #     can be reached. The finding goes to the gate intact; the survivors are untouched.
    #
    # What round 7 did NOT answer is depth, and it said exactly why: "the wall carries a graded
    # dark rim on all four sides that is equally dark on the edge facing the player's lamp and
    # the edge facing away, so it is a RIM, NOT A THICKNESS". The omnidirectionality it objects
    # to is what makes the construction legal, so depth cannot come from making the rim
    # directional. This round takes the two legal routes it named instead, both of them form
    # rather than light, and both newly permitted by the 2026-08-26 ruling:
    #
    #   JOINTS  deepen the mortar joints already in the stone - self-occlusion between blocks.
    #           The seat's own separator identified joint depth as the variable dividing "stones
    #           somebody stacked" from "a pattern printed on the ground", and the arm it ranked
    #           first got that depth from the PLANT's baked banding. This gets it legally.
    #   CAP     a coping course of paler, smoother stone along every floor-facing top edge - a
    #           different MATERIAL, not a lighter value of the same one, laid equally on all
    #           edges so it declares no direction.
    #
    #   before      round 7's `after`: 5px occlusion, 0.62 albedo, and neither new variable
    #   after       + deepened joints + coping cap. THE RULED TEST.
    #   after_unbound   `after` with the MOCK overlays omitted - the held control
    #   after_nocap `after`'s joints WITHOUT the coping cap - isolates the cap as the cause
    #   plant       `after` plus a baked key light - the within-arm A/B, now with legal form on
    #               the same stone it has beaten four times out of seven
    "before":        dict(tops=TOP_COURSED, edge="deep", albedo=TOP_ALBEDO_TARGET, bind=True,
                          joints=1.0, cap=False,
                          note="round 7's `after`, unchanged: 5-step plane-boundary occlusion "
                               "and a 0.62 top-plane albedo, with neither of round 8's two "
                               "variables. The baseline the ruled test is measured against."),
    # Built for the DEVICE PAIR, not for a critic round. Round 8 ranked `before` first of five,
    # so the held/unheld comparison Rafe takes on the device has to be built from that
    # configuration rather than from the arms round 8 showed to be worse.
    "before_unbound": dict(tops=TOP_COURSED, edge="deep", albedo=TOP_ALBEDO_TARGET, bind=False,
                           joints=1.0, cap=False,
                           note="control for `before` - the same stones with the MOCK overlays "
                                "omitted. The device pair is built from this and `before`."),
    "after":         dict(tops=TOP_COURSED, edge="cap", albedo=TOP_ALBEDO_TARGET, bind=True,
                          joints=0.62, cap=True,
                          note="THE RULED TEST. Mortar joints deepened as self-occlusion, and a "
                               "coping course of paler stone along every floor-facing top edge. "
                               "Both are form; neither declares a direction."),
    "after_unbound": dict(tops=TOP_COURSED, edge="cap", albedo=TOP_ALBEDO_TARGET, bind=False,
                          joints=0.62, cap=True,
                          note="control for `after` - the same stones with the MOCK overlays "
                               "omitted, so the held question keeps its control."),
    "after_nocap":   dict(tops=TOP_COURSED, edge="deep", albedo=TOP_ALBEDO_TARGET, bind=True,
                          joints=0.62, cap=False,
                          note="`after`'s deepened joints WITHOUT the coping cap. If depth "
                               "arrives in `after` and not here, the cap is the cause; if it "
                               "arrives in both, the joints did it."),
    "plant":         dict(tops=TOP_COURSED, edge="cap", albedo=TOP_ALBEDO_TARGET, bind=True,
                          joints=0.62, cap=True, keylight=True,
                          note="THE PLANT, and the within-arm A/B. Identical to `after` except "
                               "every course runs light at its top rows and dark at its bottom "
                               "- the baked key light §6.3 forbids. It has ranked first in four "
                               "of seven rounds on a depth read the legal arms could not "
                               "produce; this is the first round where they are given legal "
                               "form to answer it with. A critic that passes it has not "
                               "demonstrated it can fail (LOOP-PROCESS §4, bible §13.5)."),
}


def match_top(top_src, face_src):
    fl, tl = mean_lum(face_src), mean_lum(top_src)
    scaled = np.clip(top_src.astype(np.float32) * (fl / tl), 0, 255).astype(np.int16)
    return scaled, ("DERIVATION: luminance scaled by %.3f to match the face plane (%.1f -> %.1f)"
                    % (fl / tl, tl, fl))


def scale_top_to(top_src, target_lum):
    """Set the top plane's albedo to a declared value rather than to the face's.

    Rounds 1-6 matched the top plane to the FACE, which left it at roughly 0.76 of the floors'
    luminance; every seat that culled `cannot-read` measured that ratio and round 4's asked for
    0.70 or below. This targets the floor instead, because the floor is what the wall has to be
    told apart from.
    """
    tl = mean_lum(top_src)
    k = target_lum / tl
    scaled = np.clip(top_src.astype(np.float32) * k, 0, 255).astype(np.int16)
    return scaled, ("ALBEDO: top plane scaled by %.3f to %.1f, %.2f of the floors' mean "
                    "(a declared material value, not a light)" % (k, target_lum, TOP_ALBEDO_TARGET))


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
    # ROUND 8: the DE-RINGED derivation, not the raw survivors. Round 7 culled all five
    # candidates `outline` at step 1 for the survivors' baked keyline - a construction §12.1
    # forbids - so the wall questions were never reached. dering_floors.py removes only the
    # near-black closed ring (62 pixels, in B-KAB alone) and invents no colour. The survivors
    # themselves are untouched and the finding goes to the gate intact.
    dering_dir = os.path.join(REPO, ASSETS, "floors_deringed")
    for i, s in enumerate(surv):
        d_path = os.path.join(dering_dir, "MOCK_dering_%d.png" % (FLOOR_BASE + i))
        used = d_path if os.path.exists(d_path) else os.path.join(SURVIVORS, s["file"])
        fa = np.array(Image.open(used).convert("RGB")).astype(np.int16)
        floor_arrs.append(fa)
        manifest["parts"].append(dict(role="floor", id=FLOOR_BASE + i, code=s["code"],
                                      provenance="§6.4 probe survivor %s" % s["file"],
                                      derivation=("MOCK de-ring: the baked keyline §12.1 "
                                                  "forbids, removed for instrument use only"
                                                  if used == d_path else ""),
                                      mock=used == d_path))
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

    faces = build_face_stock()
    # The floors are the thing a wall has to be told apart from, so their mean luminance is the
    # denominator the ruled albedo target is expressed against. Held constant across every arm.
    floors_lum = float(np.mean([mean_lum(f) for f in floor_arrs]))
    print("floors mean luminance %.1f   ruled top-plane albedo target %.2f -> %.1f\n"
          % (floors_lum, TOP_ALBEDO_TARGET, TOP_ALBEDO_TARGET * floors_lum))
    for arm, cfg in ARMS.items():
        stock = build_top_stock(cfg["tops"], face_src, cfg.get("albedo"), floors_lum)
        first = load_part(cfg["tops"][0], PART_TABLE(cfg["tops"][0]))[0]
        if cfg.get("albedo") is None:
            _, derived = match_top(first, face_src)
        else:
            _, derived = scale_top_to(first, cfg["albedo"] * floors_lum)

        extra = [load_part(COPING_PART, TOP_PARTS)[0]] if cfg.get("cap") else []
        pal = palette_of(*[f[0] for f in faces], *[t[0] for t in stock], *extra, *floor_arrs)
        ink = Ink(pal)
        coping_src = load_part(COPING_PART, TOP_PARTS)[0] if cfg.get("cap") else None
        walls = {m: [make_wall(m, faces[v][0], stock[v][0], pal, ink, v, cfg["bind"],
                               cfg.get("keylight", False), phase=stock[v][2],
                               edge=cfg["edge"], joints=cfg.get("joints", 1.0),
                               coping_src=coping_src)
                     for v in range(mask_variants(m))]
                 for m in range(16)}
        corners = [make_corner(k, faces[v][0], stock[v][0], pal, ink, v, cfg["bind"],
                               phase=stock[v][2])
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
            face_parts=[dict(variant=i, part=faces[i][1], phase=faces[i][2])
                        for i in range(NVAR)],
            top_parts=[dict(part=n, rows=list(PART_TABLE(n)[n]["rows"]),
                            why=PART_TABLE(n)[n]["why"],
                            ledger_verdict=PART_TABLE(n)[n]["verdict"]) for n in cfg["tops"]],
            variant_sources=[dict(variant=i, part=stock[i][1], phase=stock[i][2])
                             for i in range(NVAR)],
            bindings="MOCK - authored in compose_walls.py" if cfg["bind"] else "none (control)",
            derivation=derived, note=cfg["note"],
            edge_profile=cfg["edge"], edge_steps=[str(x) for x in EDGE_PROFILES[cfg["edge"]]],
            joint_deepening=cfg.get("joints", 1.0),
            coping_part=COPING_PART if cfg.get("cap") else None,
            albedo_target=cfg.get("albedo"),
            floors_mean_lum=round(floors_lum, 1),
            top_over_floor=round(float(np.mean([mean_lum(t[0]) for t in stock])) / floors_lum, 3),
            theme=os.path.relpath(theme, REPO), segment_sheets=sheets,
            palette_size=int(len(pal)),
            face_plane_lum=round(mean_lum(face_src), 1),
            top_plane_lum=round(float(np.mean([mean_lum(t[0]) for t in stock])), 1),
            tiles={os.path.basename(p): sha256(p) for p in written})
        tl = float(np.mean([mean_lum(t[0]) for t in stock]))
        print("%-14s edge=%-6s joints=%.2f cap=%-5s bind=%-5s top/floor=%.2f palette=%d"
              % (arm, cfg["edge"], cfg.get("joints", 1.0), bool(cfg.get("cap")), cfg["bind"],
                 tl / floors_lum, len(pal)))

    # The plant sheet, built from the same stones so nothing separates it by material.
    stock = build_top_stock(ARMS["plant"]["tops"], face_src, ARMS["plant"]["albedo"], floors_lum)
    pal = palette_of(*[f[0] for f in faces], *[t[0] for t in stock], *floor_arrs)
    ink = Ink(pal)
    pc = load_part(COPING_PART, TOP_PARTS)[0]
    walls = {m: [make_wall(m, faces[v][0], stock[v][0], pal, ink, v, True, True,
                           phase=stock[v][2], edge=ARMS["plant"]["edge"],
                           joints=ARMS["plant"]["joints"], coping_src=pc)
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
