#!/usr/bin/env python3
"""THE BOUNDARY WALL FAMILY — two planes, edge-matched, composed rather than generated.

WHAT SUPPLIES WHAT (bible section 13.7, measured, not assumed)
-------------------------------------------------------------
    *"Architecture and conditioning do not exist on the same surface ... The wall road is
    composition. Generation supplies materials and parts only."*

So the BOND is authored here - courses, head joints, the turn between the planes, which stone
sits where - and the MATERIAL is the gauntlet's own stone: the residual grain of round-7 coursed
masonry, measured off the parts bin and re-laid onto this family's value ladder. No generated
pixel is copied into a shipped tile; what crosses is the grain statistic and a bank of residual
patches, with the candidate id of every donor in the manifest.

THE TWO PLANES (bible section 3, as the renderer sees it)
--------------------------------------------------------
    SOUTH neighbour is FLOOR -> the tile shows TOP BAND + FRONT FACE
    SOUTH neighbour is WALL  -> the tile shows TOP SURFACE only

and nothing anywhere shows a side face. The turn is drawn by OCCLUSION - the top two rows of the
face are darkened, because a face under an overhang is occluded from every azimuth - never by a
highlight, which would declare a light direction and fail section 6.3.

⚠ THE CONTACT SEAM AGAINST THE FLOOR IS NOT DRAWN HERE AND MUST NOT BE. Section 12.1 makes
plane-boundary occlusion mandatory and `WALL-RECIPE.md` section 3.1 measured where the asset bar
puts it: on the FLOOR cell, not on the wall sprite. The landed floor family already draws it,
per edge, as a gradient keyed to which side the wall is on (`Tier1FloorOverlays`, occlusion ids
9630-9633). A seam baked into the wall tile as well would double the darkening and would be
present on every side the tile is used - which is the definition of a ring (section 12.1).

EDGE MATCHING, AND THE THEOREM THAT SHAPES IT (section 8.3.2, section 8.3.3)
---------------------------------------------------------------------------
Section 8.3.2 makes edge-matched sets legal: *"matching is agreement, not constancy"*. Section
8.3.3's corner theorem then constrains what can be matched, and it is a PLATFORM theorem rather
than a floor one - four tiles meet at a grid corner, a tile shares one boundary family with its
eastern neighbour and one with its southern and shares NOTHING with its diagonal, so a stone
covering a grid corner is seen by four tiles that cannot agree what it is worth.

The floor paid for this with a bed joint on every tile boundary. The wall pays the same price in
the same coin: **a bed joint runs along every horizontal tile boundary, so no block crosses a
grid corner**, and the head joints are then free to cross vertical boundaries - which is where
the variety comes from. Constant-pitch bed joints are reported by the field census rather than
hidden, and they are register-justified exactly as they were for the floor: the Paths are
ADMINISTERED, and institutional ashlar is laid to a course height by contractors working to a
standard. The irregularity belongs to the orc layer ON TOP of the wall, which is world-placed
(section 8.3.1) and never baked into a segment.

THREE EDGE FAMILIES PER ORIENTATION is section 8.3.3's floor, not a target: *"Two would make
every boundary a coin-flip between the same two offsets; one is a ruled grid by definition."*

WHAT IS AUTHORED AND WHAT IS RULED
----------------------------------
The two plane values are the ONE number this family does not get to choose, and they are not
chosen here: `STACK-FINDING.md` records that section 6.5's ratios resolve differently under two
readings of the clause, that the difference is a factor of two in the compression, and that the
ruling is Rafe's at the gate. So the composer takes an ARM - a (top rung, face rung) pair - and
builds the family twice. Nothing in this file picks between them.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "tier1_floors"))
import compose_ashlar as CA          # noqa: E402
import compose_family as CF          # noqa: E402

T = 32
FACE_TOP_ROW = 16          # WALL-RECIPE section 2.1: the face is the lower half, 16 native px.
OCCLUSION_ROWS = 2         # the face under the overhang, dark from every azimuth
BED_ROWS = 2               # a joint between courses
# Head-joint width, native px, PER PLANE and not one number for both.
#
# The two planes are looking at different things. A wall top shows blocks the width of the wall,
# so its joints are the gaps between metre-long stones and read at 2px; the face shows courses
# six pixels tall, and a 2px joint there eats a third of the stone it is supposed to separate.
# Section 13.8 sets a floor on AMPLITUDE, not on width - a 1px joint two ladder rungs down is a
# larger signal than a 2px one half a rung down - so the face buys its legibility with depth.
JOINT_PX = dict(top=2, face=1)

# The face's own coursing, inside rows 16..31 with the occlusion band excluded.
FACE_COURSES = ((18, 24), (25, 32))     # [row0, row1)
FACE_BED = (24, 25)

EDGE_FAMILIES = 3
SALT_V, SALT_H, SALT_S, SALT_G = 60101, 60203, 60307, 60401

# Donor stock. Round 7 of the wall gauntlet - irregular coursed masonry, varied block widths,
# joints at every course, no baked key light. Every one of these FAILED the gauntlet as a
# finished wall, and that is the point: they failed on RELATIONSHIPS (cap to course, face to
# top), which composition supplies, and succeeded as MATERIAL, which is all that is taken.
FACE_DONORS = {
    "r07_00": dict(round="round07", rows=(6, 30),
                   verdict="FAIL - 'rows 0-4 use the identical greys as the face, so there is no "
                           "top band at all ... flat brick wallpaper with zero thickness'"),
    "r07_08": dict(round="round07", rows=(6, 30), verdict="FAIL (ledger)"),
    "r07_09": dict(round="round07", rows=(6, 30), verdict="FAIL (ledger)"),
}
LEDGER = os.path.join(REPO, "tools/pixellab/wall_gauntlet/rounds")

ARMS = {
    # (top rung index, face rung index) on the nine-rung ladder of bible section 5.6.
    "material":    dict(top=5, face=1,
                        why="section 6.5's ratios read as ALBEDO: top 1.11x and face 0.60x the "
                            "floor's own anchor of 101.16. No rig baked into the asset."),
    "compensated": dict(top=8, face=2,
                        why="section 6.5's ratios read as DELIVERED and solved backwards through "
                            "the measured compression, as far as the ladder reaches."),
}

ASSETS_REL = "src/Presentation/assets/tier1_walls"
# ⚠ THE BLOCKS ARE 200 WIDE, NOT 100, AND THE AGE DIMENSION IS WHY.
#
# The face set is edge keys x variants x AGES = 3 x 3 x 3 x 4 = 108 tiles, and the blocks were
# spaced 100 apart. Face ids ran 9400..9507 straight into top_h at 9500, the manifest listed both,
# and the engine's id->file map takes the last writer - so EIGHT FACE TILES WERE DRAWING TOP-PLANE
# FILES, which is a top plane's material laid where a reveal should be.
#
# It surfaced through `two_planes`, which reported a minimum plane separation of -0.329 rungs and
# named the tile. Nothing else would have said so: the count was right, `missing=0` was right, the
# edge check was right, and the picture looked like a wall.
IDS = dict(face=9400, top_h=9600, top_v=9700, void=9900)
VARIANTS = 3   # free interior variants per key pair - see the compose loop
VOID_RING = 1  # rings of stone drawn before the void; see the manifest note

# ── AGE, AT THE BASE COURSES ──────────────────────────────────────────────────────────────────
#
# RULED (Rafe, at the gate): *"south faces workable in kind — but walls have opted out of history.
# Bounded round: wall aging at the base courses, keyed to the existing traffic/age fields (scuff,
# arris-rounding, patina rising 1-2 courses where routes run adjacent; sealed rooms stay sharp)."*
#
# FOUR STEPS, and the field that picks between them is the floor's own. `TrafficField` is
# accumulated traversal over the level graph - the spine at full weight, remote branches decaying,
# **vaults and shrines at exactly zero** - so a wall beside a route ages and the wall of a room
# nobody is admitted to does not. That zero is the most useful value in the table and it is why
# this is keyed rather than noised: an unaged threshold is readable as *nobody comes here*.
#
# WHAT AGE IS ALLOWED TO BE, and one thing it is NOT allowed to be:
#
#   scuff            sub-rung mottling in the base rows, amplitude rising with age
#   arris-rounding   the block's bottom corners lose pixels; the base joint opens
#   patina           a DARKENING of the base course, rising into the second at high age
#
#   NOT a pale value lift. §8.2.1 banned exactly that for the floor's channel and the floor
#   session paid for the lesson twice: *"a value lift cannot signal under a carried lamp, because
#   brightness is what the light is saying."* The polish that four hundred years of shoulders and
#   gear leaves is expressed as ROUNDING - a change of form - and the grime is expressed as
#   darkening. Neither asks the lamp for permission.
AGES = 4
AGE_BASE_ROWS = 6          # how deep the base treatment reaches at age 1, in native px
AGE_SECOND_COURSE = 3      # the age at which patina climbs into the course above


def h(*parts):
    """FNV-1a 64 over the colon-joined parts.

    DELIBERATELY NOT A LIBRARY HASH. This arithmetic exists twice - here and in
    `Tier1BoundaryWall.cs` - because the engine has to pick the same tile for a boundary that the
    composer drew for it, and a mismatch is a seam at every tile edge that nothing downstream
    reports. FNV-1a is four lines in both languages; blake2b is four lines in one of them. The
    duplicate is tolerated only because the manifest carries a check vector and the engine
    REFUSES TO LAY if it cannot reproduce it (LOOP-PROCESS section 4.2).
    """
    x = 0xCBF29CE484222325
    for p in parts:
        for b in str(p).encode():
            x = ((x ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
        x = ((x ^ 0x3A) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF     # the ':' separator
    return x


def donor_residual(donors):
    """What the parts bin can and cannot supply — MEASURED, and the answer decides the pipeline.

    THE FIRST ATTEMPT CARRIED DONOR PIXELS AND IT FAILED, VISIBLY. Residual patches cut from the
    round-7 stock were laid as grain and the assembled run came back as brick wallpaper: a nine
    pixel box blur removes a joint's WIDTH but not a course's PITCH, so the donor's own bond
    survived the high-pass and arrived inside every block as structure. That is precisely the
    thing section 13.7 says this surface cannot supply - *"BitForge produced architecture 0/100 ...
    generation supplies materials and parts only"* - reaching the tile through the back door.

    So this function measures rather than harvests: it returns the donors' residual amplitude and
    the periodicity still present in it, and `compose` uses the AMPLITUDE (a material fact about
    stone) while synthesising the field itself (an architectural fact, which is ours). The
    periodicity number is reported so the decision is evidence rather than preference.
    """
    pats, prov = [], []
    for name, spec in sorted(donors.items()):
        p = os.path.join(LEDGER, spec["round"], "images", name + ".png")
        a = np.asarray(Image.open(p).convert("RGB")).astype(float)
        r0, r1 = spec["rows"]
        a = a[r0:r1]
        lum = a @ np.array([0.299, 0.587, 0.114])
        # Remove the bond: subtract a box blur wider than a joint and shorter than a course, so
        # what is left is surface and not structure. Nine rather than five, because a five-pixel
        # window leaves only the highest frequency and the floor family has already paid for that
        # once - 127 marks with a median size of four pixels, read by three blind seats as "the
        # pepper" and by section 13.8 as a signal below the perceptual floor.
        k = 9
        pad = np.pad(lum, ((k // 2, k // 2), (k // 2, k // 2)), mode="reflect")
        blur = np.zeros_like(lum)
        for dy in range(k):
            for dx in range(k):
                blur += pad[dy:dy + lum.shape[0], dx:dx + lum.shape[1]]
        blur /= k * k
        res = lum - blur
        prov.append(dict(donor=name, path=os.path.relpath(p, REPO), rows=[r0, r1],
                         verdict=spec["verdict"], residual_sd=round(float(res.std()), 4)))
        pats.append(res)
    pool = np.vstack(pats)
    # THE PERIODICITY STILL IN THE RESIDUAL. A row-mean profile of pure surface roughness has no
    # preferred vertical pitch; one that still holds the donor's courses peaks at the course
    # height. Reported as the ratio of the strongest non-zero frequency to the mean power.
    rows = pool.mean(axis=1)
    rows = rows - rows.mean()
    spec = np.abs(np.fft.rfft(rows)) ** 2
    peak = float(spec[1:].max() / max(spec[1:].mean(), 1e-9)) if len(spec) > 2 else 0.0
    return prov, float(pool.std()), peak


GRAIN_BANK = 48
_BANK = {}


def grain_patch(i, cells, seed=1337):
    """One block's grain field, synthesised, wrapping, wider than any block.

    Synthesised rather than harvested for the reason `donor_residual` measures: the donor's bond
    survives every high-pass wide enough to be surface. The same call the floor family uses, so
    the two families' grain is the same KIND of thing measured in the same units.

    QUANTISED THE WAY IT SHIPS. The floor paid for this: composing against an unquantised float
    made the composer and the engine disagree by a whole rung wherever a sample sat near a rung
    boundary.
    """
    k = (i % GRAIN_BANK, cells, seed)
    if k not in _BANK:
        rng = np.random.default_rng(seed + SALT_G + (i % GRAIN_BANK) * 7919 + cells * 31)
        g = CF.wrap_noise(2 * T, cells, rng)
        _BANK[k] = (np.clip(np.round(g * 64 + 128), 0, 255) - 128) / 64.0
    return _BANK[k]


class Family:
    def __init__(self, arm, ladder, tint, bank, seed=1337):
        self.arm = arm
        self.ladder = np.array(ladder, dtype=float)
        self.tint = np.array(tint, dtype=float)
        self.bank = bank
        self.seed = seed
        self.top_rung = ARMS[arm]["top"]
        self.face_rung = ARMS[arm]["face"]

    # ---- the edge families -----------------------------------------------------------------
    def vjoint(self, course, key):
        """(A, B, V) for a vertical boundary of family `key` in course `course`.

        A  the joint offset east of the boundary, inside the EASTERN tile
        B  the joint offset west of the boundary, inside the WESTERN tile
        V  the rung offset of the block that straddles it

        key 0 puts a joint exactly on the boundary (A = B = 0). Keys 1 and 2 let a block cross,
        and both tiles read the same key so both draw the same block at the same value: the seam
        is zero rather than small. That is section 8.3.2's agreement, and it is the only
        construction that makes a run read as masonry instead of as repeated segments.
        """
        if key == 0:
            return 0, 0, 0
        # THE OFFSET DEPENDS ON THE COURSE, AND ROUND 1's SEAT IS WHY.
        #
        # It did not: `a` and `b` were the same for every course, so at every tile boundary both
        # courses of the face broke at the same x, and the wall had no BOND. The seat measured
        # exactly that and culled it as construction rather than as value: *"two courses of
        # rectangles of identical height, unstaggered, running the full width with no bond and no
        # break. It is a ladder diagram of a wall."*
        #
        # Staggering the boundary offset by course is the mason's answer and costs nothing: the
        # two tiles either side still read the SAME key and the SAME course index, so they still
        # agree about where the block breaks — agreement, not constancy (section 8.3.2).
        a = ((5, 11), (9, 4))[course % 2][key - 1]
        b = ((12, 6), (8, 13))[course % 2][key - 1]
        v = (h(SALT_V, course, key) % 5) - 2
        return a, b, v

    def rung(self, base_index, offset):
        i = int(np.clip(base_index + offset, 0, len(self.ladder) - 1))
        return self.ladder[i]

    def stones_in_row(self, course, kw, ke, var=0, width=T):
        """The head joints of one course, given the two boundary keys.

        Returns (x0, x1, rung_offset, grain_key, grain_x). The straddling blocks at either end
        carry the offset their KEY dictates - that is what both neighbours agree on - and the
        interior blocks carry an offset hashed from the whole triple, which is what stops a course
        from being the same three blocks every time.

        ⚠ THE GRAIN OF A STRADDLING BLOCK IS MEASURED FROM ITS BOUNDARY, NEVER FROM THE TILE'S
        OWN LEFT EDGE, and `edge_agreement` found this by failing at 4.22x before the fix. Value
        agreement alone is not agreement: two tiles can paint the same rung on the two halves of
        one block and still put different grain on them, and the seam is then a texture
        discontinuity down every boundary in the wall. The west tile draws the block's columns
        from 0 and the east tile continues at its width, both indexed by the SHARED KEY, so the
        material runs through the block unbroken. It is the same construction the floor family
        calls `stone_origin`, and it is load-bearing for the same reason.
        """
        aw, _, vw = self.vjoint(course, kw)
        _, be, ve = self.vjoint(course, ke)
        spans = []
        if aw > 0:
            # The tail of the block crossing the WEST edge. Its grain is the boundary's, and this
            # tile holds the columns AFTER the ones the western neighbour drew - so the sampling
            # offset is that neighbour's width, `bw`.
            bw = self.vjoint(course, kw)[1]
            spans.append((0, aw, vw, ("bx", course, kw), bw))
        left = aw + (BED_ROWS if aw > 0 else 0)
        left = aw
        right = width - be
        # HOW MANY BLOCKS A TILE'S WORTH OF COURSE HOLDS, and this is where the two planes stop
        # being the same drawing at two values.
        #
        # A wall top is the top FACE of a block, and a block is longer than the wall is thick: at
        # a 32px tile the wall's whole thickness is one tile, so a block's top reads as a long
        # rectangle running ALONG the wall, not as a tall one standing across it. Cutting a head
        # joint inside every tile made 32px-tall by 8px-wide slabs and the assembled run read as
        # a palisade. So the top plane usually holds NO interior joint at all - its head joints
        # arrive from the edge keys, one boundary in three, which puts a block at about three
        # tiles long.
        #
        # The face is the opposite: it is elevation, its courses are 6-7px tall, and a block that
        # ran three tiles would be a beam. It holds one or two.
        cap = 2 if self.plane == "top" else 3
        n = 1 + (h(SALT_S, course, kw, ke, var) % cap)
        if self.plane == "top" and (h(SALT_S, "cut", course, kw, ke, var) % 2):
            n = 1
        if right - left < 8:
            n = 1
        cuts = [left]
        for i in range(1, n):
            frac = (i * (right - left)) // n
            jitter = (h(SALT_S, course, kw, ke, var, i) % 5) - 2
            cuts.append(int(np.clip(left + frac + jitter, left + 4, right - 4)))
        cuts.append(right)
        for i in range(len(cuts) - 1):
            off = (h(SALT_S, "v", course, kw, ke, var, i) % 5) - 2
            spans.append((cuts[i], cuts[i + 1], off, ("in", course, kw, ke, var, i), cuts[i]))
        if be > 0:
            # The head of the block crossing the EAST edge: the same boundary key, sampled from 0,
            # so the neighbour's tail continues it.
            spans.append((width - be, width, ve, ("bx", course, ke), 0))
        return [s for s in spans if s[1] > s[0]]

    def grain_for(self, tag, gx, y0, w, hgt):
        """Residual stone surface, tiled from the donor bank.

        Section 13.8: an authored signal below the perceptual floor is ABSENT. The floor family
        learned this the hard way - grain at +-4 luminance against a 13.23 rung quantised flat and
        a blind seat called the result linoleum. So the grain here is scaled to a fraction of a
        RUNG rather than to an absolute, and the composer reports what fraction.
        """
        # TWO SCALES, NOT ONE, and the comparative seat is why. Ranked against the asset bar it
        # put Yarl ahead on the face and then culled on this: *"Wall tops carry zero texture - the
        # lit stub at (183,393) is flat bars beside densely worked floor."* One noise scale reads
        # as a blur laid over a flat block; two read as stone that was cut. It is the same
        # construction the floor family uses (coarse 0.34, fine 0.14) and it is legal under
        # §8.3.1's mirror clause - *incident-free is not featureless; material has structure -
        # joints, bond, grain, value break.*
        #
        # ⚠ WHAT IS NOT ADDED, AND WHY IT IS FLAGGED RATHER THAN DONE: dressing marks. The floor
        # carries them and they would answer this cull directly, but §3.1 says a wall top *"carries
        # nothing but the joints between the blocks it is made of"* in those words. Whether tooling
        # counts as incident or as material is a RULING, not a builder's call.
        out = np.zeros((hgt, w))
        for cells, weight in ((11, 1.0), (26, 0.45)):
            p = grain_patch(h(SALT_G, tag, cells), cells=cells, seed=self.seed)
            ph, pw = p.shape
            ys = (np.arange(hgt) + y0) % ph
            xs = (np.arange(w) + gx) % pw
            out += p[np.ix_(ys, xs)] * weight
        return out / 1.45

    def paint_plane(self, img, cls, y0, y1, rung_index, keys, grain_amp, var=0):
        """Lay one plane's blocks between rows [y0, y1)."""
        kw, ke = keys["w"], keys["e"]
        step = float(self.ladder[1] - self.ladder[0])
        # A JOINT IS THREE RUNGS DOWN, NOT ONE OR TWO, AND THE REASON IS THE RIG RATHER THAN THE
        # MASONRY. The lighting is multiplicative, so an authored RATIO survives it exactly - but
        # eight-bit quantisation does not: a wall three tiles from the lamp delivers around 35 of
        # 255, and a joint authored half a rung down arrives two levels darker than its block,
        # which is section 13.8's perceptual floor with a rig-shaped edge on it. Depth is the one
        # lever that survives multiplication, and enclosure is its register derivation (section
        # 6.5: a joint is dark BECAUSE it is enclosed, which is true from every angle).
        joint = self.rung(rung_index, -3)
        self.plane = cls
        jw = JOINT_PX["top" if cls.startswith("top") else "face"]
        img[y0:y1, :] = joint
        courses = [(y0, y1)] if cls == "top" else [c for c in FACE_COURSES
                                                   if c[0] >= y0 and c[1] <= y1]
        for ci, (cy0, cy1) in enumerate(courses):
            for (x0, x1, off, gkey, gx) in self.stones_in_row(ci, kw, ke, var):
                v = self.rung(rung_index, off)
                g = self.grain_for((cls, gkey), gx, 0, x1 - x0, cy1 - cy0)
                block = v + g * grain_amp * step
                img[cy0:cy1, x0:x1] = block
                # A block is bounded by its joints, and the joint is TWO pixels because one is
                # not there. Section 13.8: at 2x display a single native pixel of mortar is two
                # device pixels of a line the eye reads as anti-aliasing, and the floor family's
                # whole perceptual-floor law came out of authoring true signals too small to
                # exist. The bar's own top plane measures 2px joints; so does this.
                if x0 > 0:
                    img[cy0:cy1, x0:x0 + jw] = joint
                if x1 < T:
                    img[cy0:cy1, max(x0, x1 - jw):x1] = joint
        return img

    def age_face(self, img, age, grain_amp):
        """Lay the base-course aging on a face tile. Age 0 is untouched, and must stay so."""
        if age <= 0:
            return img
        step = float(self.ladder[1] - self.ladder[0])
        base_row = FACE_COURSES[-1][0]                      # the bottom course only, at first
        if age >= AGE_SECOND_COURSE:
            base_row = FACE_COURSES[0][0]                   # patina climbs one course
        rows = slice(base_row, T)

        # PATINA: grime walked into the surface until it is part of it (§8.1). A fraction of a
        # rung, graded so the top of the treated band is barely touched and the foot carries it -
        # the dirt is deepest where the floor meets the wall, which is where it comes from.
        band = img[rows, :]
        h = band.shape[0]
        ramp = np.linspace(0.25, 1.0, h)[:, None]
        # THE CURVE IS SUPERLINEAR IN AGE, AND THE FIRST MEASUREMENT IS WHY.
        # At 0.28 rungs per step the ages came back monotonic and correctly signed - the keying
        # works - but the top step landed at Weber 0.1453 against the floor family's 0.1440, which
        # is over by nine tenths of one percent. §13.8: *"clearing it by 3% proves nothing - that
        # is the geometric midpoint between present and absent, which is precisely the ambiguous
        # point."* Ages 1 and 2 sitting under it is not the same problem and is not corrected:
        # light traffic on a remote branch SHOULD be almost nothing, and a wall that is visibly
        # grimy everywhere has stopped saying where people walk.
        img[rows, :] = band - ramp * (0.30 * age ** 1.6) * step

        # SCUFF: sub-rung mottling, at its own scale, keyed to the tile so two aged neighbours do
        # not scuff identically. It is deliberately BELOW a rung: this is the surface losing its
        # evenness, not a mark. §13.8 governs whether it survives, and the amplitude table reports
        # it rather than this comment claiming it.
        g = self.grain_for(("scuff", age), 0, 0, T, h)
        # ⚠ SUB-RUNG, AND `two_planes` CAUGHT THIS AT 1.83 RUNGS. Raising the age curve for the
        # patina raised the scuff with it, and at age 3 the scuff was swinging the base course by
        # a third of its own value - which is not a surface losing its evenness, it is damage, and
        # on some tiles it pushed the face's mean ABOVE the top plane's. The instrument reported a
        # minimum plane separation of -0.329 rungs and was right to.
        #
        # It is also NOT multiplied by grain_amp any more. grain_amp is the base material's knob;
        # compounding the two meant a change to the stone's texture silently changed how worn the
        # walls looked, which is two levers wearing one name.
        img[rows, :] = img[rows, :] + g * (0.22 * age ** 1.1) * step

        # ARRIS-ROUNDING: the block's bottom corners give up pixels and the base joint opens.
        # A change of FORM, not of value - which is the half of §8.1's polish that survives a
        # carried lamp.
        joint = self.rung(self.face_rung, -3)
        r = min(2, age)
        for i in range(r):
            img[T - 1 - i, :i + 1] = joint
            img[T - 1 - i, T - 1 - i:] = joint
        if age >= 2:
            img[T - 1, :] = np.minimum(img[T - 1, :], joint + 0.4 * step)
        return img

    def tile(self, cls, keys, grain_amp, var=0, age=0):
        """One tile.

        ── COURSES RUN ALONG THE WALL, AND THAT IS WHY THERE ARE TWO TOP CLASSES ────────────────
        The first version of this family drew one top plane and used it everywhere. In an
        east-west run it was right; in the north-south corridor it came back as **a palisade** —
        head joints at ten-pixel pitch running ACROSS a wall that runs the other way, so the
        blocks read as staves stood on end rather than as stones laid along a line.
        The capture is `evidence/r03_choke.png` and it is the clearest thing in this session's
        ledger.
        //
        A mason lays courses parallel to the face. So `top_h` is the plane of a wall that runs
        east-west (blocks long in x, head joints vertical, bed joints on the horizontal tile
        boundaries) and `top_v` is the same material turned through ninety degrees for a wall
        that runs north-south. Which one a cell gets is decided by the engine from the direction
        of the floor it faces, not by anything on the tile.
        //
        The turn cannot be bought by flipping or rotating a tile at run time: an edge-matched
        tile's orientation IS its meaning, and rotating one relabels its four edges so it stops
        agreeing with its neighbours (§8.3.3's recorded cost). It has to be composed twice.
        """
        img = np.zeros((T, T), dtype=float)
        if cls == "top_h":
            self.paint_plane(img, "top", 0, T, self.top_rung, keys, grain_amp, var)
            # THE BED JOINT ON THE TILE BOUNDARY. Section 8.3.3: no block may cross a grid corner,
            # so one joint sits on every tile boundary ACROSS the run, for ever. Drawn on the
            # tile's leading edge only - the neighbour draws its own, and two half-joints meeting
            # is one joint of the right width rather than two of the wrong one.
            img[0:BED_ROWS, :] = self.rung(self.top_rung, -2)
        elif cls == "top_v":
            # Composed in the transpose and turned once, here, at COMPOSE time. The grain turns
            # with it, which is correct: it is the same stone seen from the same angle, laid the
            # other way.
            t = np.zeros((T, T), dtype=float)
            self.paint_plane(t, "top", 0, T, self.top_rung, keys, grain_amp, var)
            t[0:BED_ROWS, :] = self.rung(self.top_rung, -2)
            img[:, :] = t.T
        else:
            self.paint_plane(img, "top", 0, FACE_TOP_ROW, self.top_rung, keys, grain_amp, var)
            img[0:BED_ROWS, :] = self.rung(self.top_rung, -2)
            self.paint_plane(img, "face", FACE_TOP_ROW, T, self.face_rung, keys, grain_amp, var)
            # THE TURN, DRAWN BY OCCLUSION ONLY (section 6.3, and the gauntlet's own hazard note).
            # The top plane is NOT brightened; the first rows of the face are darkened, because a
            # face under an overhang is occluded from every azimuth and declares no direction.
            lip = img[FACE_TOP_ROW:FACE_TOP_ROW + OCCLUSION_ROWS, :]
            img[FACE_TOP_ROW:FACE_TOP_ROW + OCCLUSION_ROWS, :] = np.minimum(
                lip * 0.55, self.rung(self.face_rung, -2))
            self.age_face(img, age, grain_amp)
        return img

    def rgb(self, img):
        v = np.clip(img, 0, 255)
        out = np.stack([v * self.tint[0], v * self.tint[1], v * self.tint[2]], axis=2)
        return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def compose(arm, out_dir, grain_amp, void_values):
    man_path = os.path.join(CA.ASSETS, "MANIFEST.json")
    floor = json.load(open(man_path))
    mat = dict(floor["material"])
    CF.rehydrate(mat)                                   # section 5.6: derive, never trust
    ladder = mat["ladder"]

    prov, pool_sd, peak = donor_residual(FACE_DONORS)
    fam = Family(arm, ladder, mat["tint"], None)

    if os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith(".png") or f.endswith(".png.import"):
                os.remove(os.path.join(out_dir, f))
    os.makedirs(out_dir, exist_ok=True)

    # THE THIRD INDEX IS A FREE VARIANT, AND IT IS WHAT KEEPS AN EDGE-MATCHED SET FROM BEING A
    # LATTICE OF NINE. Two boundary keys give nine combinations, and a run long enough repeats
    # them - §8.3.1's trap arriving through the fix for §8.3.3. The variant changes only what
    # happens BETWEEN the boundaries: the straddling blocks at either end are still the key's,
    # value and all, so agreement is untouched and the interior stops being a function of it.
    # AGE IS A FOURTH INDEX, AND IT IS ON THE FACE ONLY. The top planes take no age: nothing walks
    # on a wall top, so there is no traffic to key one to, and §8.3.1 has just had incident removed
    # from them by ruling. A wall's history is at its foot, because that is where the world
    # touches it.
    tiles, table = [], {"face": {}, "top_h": {}, "top_v": {}, "void": {}}
    for cls, base in (("face", IDS["face"]), ("top_h", IDS["top_h"]), ("top_v", IDS["top_v"])):
        n = 0
        ages = range(AGES) if cls == "face" else (0,)
        for ka in range(EDGE_FAMILIES):
            for kb in range(EDGE_FAMILIES):
                for var in range(VARIANTS):
                    for age in ages:
                        keys = dict(w=ka, e=kb, n=0)
                        img = fam.tile(cls, keys, grain_amp, var, age)
                        tid = base + n
                        p = os.path.join(out_dir, "tier1_wall_%d.png" % tid)
                        Image.fromarray(fam.rgb(img)).save(p)
                        key = ("%d,%d,%d,%d" % (ka, kb, var, age) if cls == "face"
                               else "%d,%d,%d" % (ka, kb, var))
                        table[cls][key] = tid
                        tiles.append(dict(id=tid, cls=cls, ka=ka, kb=kb, var=var, age=age,
                                          file=os.path.basename(p),
                                          mean=round(float(img.mean()), 3),
                                          sha256=hashlib.sha256(open(p, "rb").read()).hexdigest()))
                        n += 1

    # THE VOID. Bible has no clause for it yet, which is exactly why nothing here rules it: three
    # near-black candidates are emitted and Rafe picks one at the gate (section 13.1). All three
    # are darker than any lit content in the scene by construction.
    for i, v in enumerate(void_values):
        tid = IDS["void"] + i
        a = np.full((T, T), float(v))
        p = os.path.join(out_dir, "tier1_wall_%d.png" % tid)
        Image.fromarray(fam.rgb(a)).save(p)
        table["void"][str(i)] = tid
        tiles.append(dict(id=tid, cls="void", value=v, file=os.path.basename(p),
                          sha256=hashlib.sha256(open(p, "rb").read()).hexdigest()))

    step = float(np.array(ladder)[1] - np.array(ladder)[0])
    man = dict(
        family="boundary_wall_%s_v1" % arm,
        arm=arm, arm_why=ARMS[arm]["why"],
        commit=os.popen("git -C %s rev-parse HEAD" % REPO).read().strip(),
        seed=1337,
        floor_manifest=os.path.relpath(man_path, REPO),
        floor_family=floor["family"],
        anchor=101.16,
        ladder=[round(v, 4) for v in ladder],
        ladder_step=round(step, 4),
        planes=dict(top_rung=fam.top_rung, top_value=round(float(ladder[fam.top_rung]), 3),
                    face_rung=fam.face_rung, face_value=round(float(ladder[fam.face_rung]), 3),
                    authored_face_over_top=round(float(ladder[fam.face_rung]
                                                       / ladder[fam.top_rung]), 4),
                    face_top_row=FACE_TOP_ROW, occlusion_rows=OCCLUSION_ROWS),
        edge_families=EDGE_FAMILIES,
        # HOW MANY RINGS OF STONE ARE DRAWN BEFORE THE VOID BEGINS.
        #
        # It started at 2, from WALL-RECIPE section 2.2's measured "every room boundary in the bar
        # is two tiles or more". That number is about MAP GEOMETRY - the mass must be two cells -
        # and it was read here as a statement about how many of them are DRAWN AS LIT STONE, which
        # it is not. Round 2's seat found the consequence: *"More of the same stuff ... it is wall,
        # and it goes on. What it is NOT is dark."* At two rings the void only appears where a mass
        # is five cells or more, and an ordinary dungeon's masses are two to four - so the darkness
        # beyond the walls would essentially never be seen.
        #
        # One ring is also the truer statement. From above, in the dark, with a lamp at floor
        # level, you see the top of the wall nearest you; what stands behind it is not visible
        # rock, it is what the lamp does not reach. The map still has its two cells of mass; you
        # simply cannot see through the first one.
        #
        # Kept as a parameter, and both settings captured, because this is a LOOK and section 13.1
        # gives a look to Rafe.
        void_ring=VOID_RING,
        salts=dict(v=SALT_V, h=SALT_H, s=SALT_S, g=SALT_G),
        grain=dict(amp_rungs=grain_amp, bank=GRAIN_BANK, synthesised=True,
                   donor_pool_sd=round(pool_sd, 4),
                   donor_residual_periodicity=round(peak, 3),
                   donor_role="AMPLITUDE ONLY - the residual still carries the donor's own course "
                              "pitch, so its pixels cannot be laid as grain without laying its "
                              "bond with them (section 13.7).",
                   donors=prov),
        # THE CHECK VECTOR. The engine recomputes these and refuses to lay a single wall if it
        # disagrees with any of them. Without it the duplicated hash is a comment; with it, it is
        # an enforcement (LOOP-PROCESS section 4.2 - a step that runs and changes nothing quietly
        # is a wish).
        variants=VARIANTS,
        ages=AGES,
        age_second_course=AGE_SECOND_COURSE,
        age_note=("RULED (Rafe, at the gate): the walls had opted out of history. Age is keyed to "
                  "TrafficField - the floor's own accumulated-traversal field, in which vaults "
                  "and shrines sit at exactly zero - so a wall beside a route ages and a sealed "
                  "room's wall stays sharp. Base courses only; patina climbs one course at the "
                  "age above. Expressed as darkening and as ROUNDING, never as a pale value lift "
                  "(section 8.2.1)."),
        edge_check=[[SALT_V, "v", x, y, h(SALT_V, "v", x, y) % EDGE_FAMILIES]
                    for x in range(0, 17, 3) for y in range(0, 21, 5)]
                   + [[SALT_H, "h", x, y, h(SALT_H, "h", x, y) % EDGE_FAMILIES]
                      for x in range(1, 17, 4) for y in range(1, 21, 6)],
        table=table, tiles=tiles,
        contact_seam="NOT DRAWN HERE - the floor family carries it per edge (WALL-RECIPE 3.1, "
                     "bible 12.1). A seam baked into a wall tile is present on every side the "
                     "tile is used, which is a ring.",
    )
    mp = os.path.join(out_dir, "MANIFEST.json")
    json.dump(man, open(mp, "w"), indent=2)
    return man, mp


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=sorted(ARMS), default="material")
    ap.add_argument("--grain-amp", type=float, default=0.90,
                    help="grain amplitude in LADDER RUNGS. Section 13.8: a signal below the "
                         "perceptual floor is absent, and the floor family's +-4 luminance "
                         "against a 13.23 rung quantised flat.")
    ap.add_argument("--ageless", action="store_true",
                    help="compose with AGES=1 — the aging switched off, everything else "
                         "identical. This is the control arm for measure_age_signal: the same "
                         "cells, in the same scene, under the same lamp, so the lighting "
                         "gradient cancels instead of being modelled.")
    ap.add_argument("--out-suffix", default="",
                    help="append to the asset directory name, so a control arm does not "
                         "overwrite the candidate it is a control for")
    ap.add_argument("--void", default="18,10,0",
                    help="three near-black void candidates; Rafe rules one at the gate")
    a = ap.parse_args()
    if a.ageless:
        globals()["AGES"] = 1
    out = os.path.join(REPO, ASSETS_REL if a.arm == "material" else ASSETS_REL + "_" + a.arm)
    out += a.out_suffix
    voids = [int(v) for v in a.void.split(",")]
    man, mp = compose(a.arm, out, a.grain_amp, voids)
    print("arm=%s  top=%.2f (rung %d)  face=%.2f (rung %d)  authored face/top=%.4f"
          % (a.arm, man["planes"]["top_value"], man["planes"]["top_rung"],
             man["planes"]["face_value"], man["planes"]["face_rung"],
             man["planes"]["authored_face_over_top"]))
    print("  %d tiles + %d void  ->  %s" % (len(man["tiles"]) - len(voids), len(voids),
                                            os.path.relpath(out, REPO)))
    print("  manifest: %s" % os.path.relpath(mp, REPO))
