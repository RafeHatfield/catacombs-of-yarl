#!/usr/bin/env python3
"""THE BOUNDARY'S PROPS — composed, with generated material.

WHY THIS IS COMPOSITION AND NOT GENERATION, decided by fifteen generations rather than by
preference. Bible §13.7, measured on this project's own surface:

    "Architecture and conditioning do not exist on the same surface ... The wall road is
     composition. Generation supplies materials and parts only."

Two waves went out with the clause list in the prompt text — *orthographic, square to the screen,
no perspective, no isometric*, *no grass, no moss, no plants*, *not a gravestone, no skull*, *not
a fence, not a gate*. What came back:

    wave 1 (12)   4 markers: one standing stone in GRASS, one GRAVESTONE WITH A SKULL, two
                  isometric. 4 barricades: four FENCES, one in grass. 4 fires: four cosy
                  campfires with painted glow, including the one asked for with NO FLAME.
    wave 2 (3)    the refusals restated and sharpened. All three came back ISOMETRIC, two still
                  carrying green.

§3 is orthogonal and was ratified two hours ago; a diamond footprint is not a near miss. And the
role rejections the identity cards name BY NAME — gravestone, fence — came back anyway.

⚠ AND THE NUMERIC SCREEN PASSED THREE OF THE FAILURES. `screen_wave.py` measures outline, glow,
mass and value band, and it cleared the gravestone and two of the fences, because §13.4 is right:
**register conformance is never instrumented.** The eye caught what no number would. That is the
clause working as designed, not the screen failing.

So the generated frames become what the wall gauntlet's failures became — MATERIAL. The wall
composer says it in its own words about its donors: *"Every one of these FAILED the gauntlet as a
finished wall, and that is the point: they failed on RELATIONSHIPS, which composition supplies,
and succeeded as MATERIAL, which is all that is taken."*

WHAT IS AUTHORED HERE (structure), AND WHAT IS TAKEN (material):

    authored   the silhouette, the two planes of §3, the course lines, where every rope band
               sits, where every pin is driven, the value of each of those on the family's ladder
    taken      the grain statistic of the generated stone and timber — the residual after a box
               blur removes the donor's own structure — re-laid onto this family's ladder

No generated pixel is copied into a shipped prop. What crosses is the grain, and the donor of
every patch is recorded in the manifest.

PALETTE REGIME: ladder, not locked. §5.1's values are PLACEHOLDER and its derivation has not
landed, so every value here is a rung of the ashlar family's own measured ladder, read from its
manifest rather than restated (§13.12: assertions derive, never copy).
"""
import hashlib
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASHLAR = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar")
GEN = os.path.join(HERE, "gen")
T = 32

# ── §3'S TWO PLANES, AT THIS TILE SIZE ────────────────────────────────────────────────────────
# The wall family splits its 32 rows at 16: top plane above, front face below, with a 2-row
# occlusion band at the turn. A prop is a smaller mass than a wall, so it carries the same
# grammar at its own height rather than a different one — the top plane is what you see of its
# upper surface, the face is what the carried lamp reaches.
TOP_ROWS = 10          # the prop's top surface
LIP_ROWS = 2           # the turn, drawn by occlusion only (§6.3)
IDS = dict(marker=9800, barricade_a=9810, barricade_b=9811, barricade_c=9812, barricade_d=9813,
           fire=9820, fire_flame=9821)


def ladder():
    """The family's measured value ladder — DERIVED from its manifest, never restated."""
    m = json.load(open(os.path.join(ASHLAR, "MANIFEST.json")))["material"]
    return np.array(m["ladder"], dtype=float), m


def grain_bank(paths, k=3):
    """The donors' residual: what is left of a generated image once its own structure is gone.

    A box blur wider than the donor's detail removes its composition and leaves its material.
    This is `compose_walls.donor_residual`'s argument applied to props, and it is the only thing
    that crosses from a generated frame into a shipped one.
    """
    out = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        a = np.asarray(im, dtype=float)
        rgb, alpha = a[:, :, :3], a[:, :, 3]
        lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        op = alpha > 128
        if op.sum() < 64:
            continue
        pad = np.where(op, lum, np.nan)
        # box blur ignoring transparent pixels
        blur = np.zeros_like(lum)
        for y in range(lum.shape[0]):
            for x in range(lum.shape[1]):
                y0, y1 = max(0, y - k), min(lum.shape[0], y + k + 1)
                x0, x1 = max(0, x - k), min(lum.shape[1], x + k + 1)
                w = pad[y0:y1, x0:x1]
                blur[y, x] = np.nanmean(w) if np.any(~np.isnan(w)) else 0.0
        res = np.where(op, lum - blur, 0.0)
        sd = res[op].std()
        if sd > 1e-6:
            out.append((os.path.basename(p), res / sd, op))
    return out


def grain_at(bank, rng, h, w):
    """A patch of donor grain, normalised, sized to fit."""
    if not bank:
        return np.zeros((h, w))
    name, res, op = bank[rng.integers(len(bank))]
    H, W = res.shape
    y = int(rng.integers(0, max(1, H - h)))
    x = int(rng.integers(0, max(1, W - w)))
    patch = res[y:y + h, x:x + w]
    if patch.shape != (h, w):
        patch = np.pad(patch, ((0, h - patch.shape[0]), (0, w - patch.shape[1])), mode="wrap")
    return patch


def png(path, rgba):
    h, w, _ = rgba.shape
    raw = b"".join(b"\x00" + rgba[y].astype(np.uint8).tobytes() for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)

    hdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr)
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def tint(v, warm=0.0):
    """A ladder value to RGB. The family's stone is neutral; rope and timber take a warm bias.

    NOT A HUE INVENTED HERE: the bias is the quarry tint the wall family already derived, read
    from its manifest, so a prop standing against a wall is the same rock.
    """
    r = np.clip(v * (1.0 + 0.10 * warm), 0, 255)
    g = np.clip(v * (1.0 + 0.02 * warm), 0, 255)
    b = np.clip(v * (1.0 - 0.06 * warm), 0, 255)
    return r, g, b


def canvas():
    return np.zeros((T, T, 4), dtype=float)


def put(img, y0, y1, x0, x1, v, warm=0.0, a=255):
    r, g, b = tint(v, warm)
    img[y0:y1, x0:x1, 0] = r
    img[y0:y1, x0:x1, 1] = g
    img[y0:y1, x0:x1, 2] = b
    img[y0:y1, x0:x1, 3] = a


def rung(lad, i):
    return float(lad[int(np.clip(i, 0, len(lad) - 1))])


# ── THE PLANES' VALUES ARE THE WALL FAMILY'S OWN — DERIVED, NEVER RESTATED (§13.12) ──────────
#
# A prop stands against a wall in the same lit room, so it is the same rock at the same rungs.
# The wall manifest carries top_rung 5 / face_rung 1 on a shared 9-rung ladder, and an authored
# face-over-top ratio of 0.5387. Reading them means a prop cannot drift away from the surface it
# stands against: re-derive the wall family and the props follow.
def planes():
    w = json.load(open(os.path.join(REPO, "src/Presentation/assets/tier1_walls/MANIFEST.json")))
    p, lad = w["planes"], np.array(w["ladder"], dtype=float)
    return lad, int(p["top_rung"]), int(p["face_rung"]), np.array(w["quarry_tint"], dtype=float)


def qtint(v, q, warm=0.0):
    """A ladder value through the family's own quarry tint, with an optional warm bias for
    rope and timber. The tint is READ from the wall manifest, so props and walls are one quarry."""
    m = q * (1.0 + np.array([0.10, 0.02, -0.06]) * warm)
    return np.clip(v * m[0], 0, 255), np.clip(v * m[1], 0, 255), np.clip(v * m[2], 0, 255)


def paint(img, ys, xs, v, q, warm=0.0, grain=None, amp=0.0):
    """Lay a value over a region, with donor grain if supplied."""
    val = np.full((len(ys), len(xs)), v, dtype=float)
    if grain is not None and amp:
        val = val + grain[:len(ys), :len(xs)] * amp
    r, g, b = qtint(val, q, warm)
    sl = np.ix_(ys, xs)
    img[sl[0], sl[1], 0] = r
    img[sl[0], sl[1], 1] = g
    img[sl[0], sl[1], 2] = b
    img[sl[0], sl[1], 3] = 255


def occlude(img, ys, xs, f=0.55):
    """THE TURN, DRAWN BY OCCLUSION ONLY (§6.3). The top plane is never brightened; the first
    rows of the face are darkened, because a face under an overhang is occluded from every
    azimuth and declares no light direction."""
    sl = np.ix_(ys, xs)
    img[sl[0], sl[1], 0:3] *= f


# ══ SECOND COMPOSITION PASS — the first one's faults, named ═══════════════════════════════════
#
# Pass 1 was composed, rendered and LOOKED AT, and it was worse than the generations it replaced.
# The three faults, and each fix is aimed at one of them:
#
# 1. THE MARKER TURNED WITH A HARD CUT AND READ AS TWO OBJECTS — a pale slab hovering over a dark
#    box. That is #202's defect, reproduced in a new asset three hours after it was filed: a 2-row
#    occlusion band at 0.55 between two lit planes is a black rule, and a black rule separates.
#    #202's own exit is the fix and it is applied here first: STRUCTURE AT THE MEETING. A coping
#    course belongs to both planes — darker than the top, lighter than the face — so the mass
#    turns a corner instead of being cut in half. The occlusion is kept, at the coping's own foot,
#    where it is one stone's shadow rather than a plane boundary.
#
# 2. THE BARRICADES CAME OUT AS LADDERS. Evenly spaced rungs between two identical posts is the
#    "too light, too regular, too agricultural" fence the identity card rejects BY NAME — the
#    same failure the generator produced, arrived at by a different route. The fix is that
#    NOTHING SHARES A MEASUREMENT: timbers differ in depth, gaps differ, the two posts differ in
#    height and width, and one variant is braced diagonally because that repair was needed there.
#
# 3. THE FIRE READ AS A MANHOLE COVER. An ellipse of one value with faint streaks is not a ring
#    of stones. The fix is to draw the stones as STONES — individual blocks with joints between
#    them, laid round the ring — and to make the fuel legible as charred timber crossing ash.
def coping(img, y, x0, x1, v_top, v_face, q):
    """The turn, with a stone in it. #202's exit applied at prop scale.

    The coping course is its own value between the two planes, so the eye reads one mass changing
    direction. The occlusion then sits UNDER the coping — a stone's own shadow, which declares no
    light direction (§6.3) — rather than between the planes, where it reads as a gap.
    """
    v = (v_top + v_face) * 0.5
    paint(img, range(y, y + 3), range(x0, x1), v, q)
    for jx in range(x0 + 3, x1 - 2, 7):                    # the coping's own joints
        paint(img, range(y, y + 3), range(jx, jx + 1), v * 0.82, q)
    occlude(img, range(y + 3, y + 4), range(x0, x1), 0.74)


def marker(bank, rng, lad, top_r, face_r, q):
    img = canvas()
    stone_top, stone_face = rung(lad, top_r), rung(lad, face_r)
    # A block seen from high above: the top plane is INSET, not overhanging. The first pass had
    # it wider than the face, which is why it hovered.
    base_x0, base_x1 = 6, 26
    top_x0, top_x1 = 9, 23
    top_y0, top_y1 = 4, 12

    g = grain_at(bank, rng, top_y1 - top_y0, top_x1 - top_x0)
    paint(img, range(top_y0, top_y1), range(top_x0, top_x1), stone_top, q, 0.0, g, 2.0)

    # the face, splaying to a wider foot — mass in the silhouette, weight straight down
    for y in range(top_y1 + 3, 30):
        t = (y - (top_y1 + 3)) / float(29 - (top_y1 + 3))
        x0 = int(round(top_x0 - t * (top_x0 - base_x0)))
        x1 = int(round(top_x1 + t * (base_x1 - top_x1)))
        gg = grain_at(bank, rng, 1, x1 - x0)
        paint(img, [y], range(x0, x1), stone_face, q, 0.0, gg, 2.4)

    coping(img, top_y1, top_x0 - 1, top_x1 + 1, stone_top, stone_face, q)

    # the institution: one recessed seal, minimal and correct, and nothing else
    paint(img, range(19, 23), range(13, 19), stone_face * 0.86, q)
    paint(img, range(20, 22), range(14, 18), stone_face * 1.12, q)

    # the orc work: bands at heights nobody would choose twice, pins beside older pins
    rope, iron = rung(lad, face_r + 2), rung(lad, max(0, face_r - 1))
    for by, doubled in ((17, False), (25, True)):
        for dy in range(2):
            y = by + dy
            row = np.where(img[y, :, 3] > 0)[0]
            if len(row):
                paint(img, [y], range(row.min(), row.max() + 1), rope, q, warm=1.0)
        if doubled:
            y = by + 2
            row = np.where(img[y, :, 3] > 0)[0]
            if len(row):
                paint(img, [y], range(row.min(), row.max() + 1), rope * 0.84, q, warm=1.0)
        row = np.where(img[by, :, 3] > 0)[0]
        if len(row):
            for px in (row.min() + 1, row.max() - 2):
                paint(img, range(by, by + 2), range(px, px + 2), iron, q, warm=0.3)
    paint(img, range(27, 29), range(8, 10), iron, q, warm=0.3)      # the pin that failed, left in
    return img


def barricade(bank, rng, lad, top_r, face_r, q, variant):
    img = canvas()
    wood_top, wood_face = rung(lad, top_r - 1), rung(lad, face_r + 1)
    rope, iron = rung(lad, face_r + 3), rung(lad, max(0, face_r - 1))

    # NOTHING SHARES A MEASUREMENT. Two posts of different width and height; timbers of
    # different depth at gaps that do not repeat.
    P = {
        "a": ((2, 8, 3), (25, 29, 6), [(7, 12), (15, 18), (21, 27)], True),
        "b": ((3, 7, 5), (23, 29, 2), [(6, 9), (12, 18), (22, 26)], False),
        "c": ((2, 7, 4), (24, 28, 7), [(8, 11), (13, 16), (18, 21), (23, 28)], False),
        "d": ((4, 9, 2), (22, 28, 5), [(5, 11), (16, 19), (23, 28)], False),
    }[variant]
    (ax0, ax1, ay), (bx0, bx1, by), timbers, braced = P

    for (x0, x1, y0) in ((ax0, ax1, ay), (bx0, bx1, by)):
        g = grain_at(bank, rng, 30 - y0, x1 - x0)
        paint(img, range(y0, 30), range(x0, x1), wood_face, q, 0.6, g, 2.4)
        paint(img, range(y0, y0 + 3), range(x0, x1), wood_top, q, 0.4)
        occlude(img, range(y0 + 3, y0 + 4), range(x0, x1), 0.76)

    if braced:                                   # a diagonal, because this one needed it
        for i in range(22):
            y, x = 27 - i, 6 + i
            if 0 <= y < 30 and 0 <= x < 30:
                paint(img, range(y, y + 2), range(x, x + 2), wood_face * 0.92, q, warm=0.6)

    for (y0, y1) in timbers:
        x0, x1 = ax0 + 1, bx1 - 1
        if variant == "c" and y0 in (18, 23):
            x0, x1 = 10, 24                       # an offcut that does not span
        g = grain_at(bank, rng, y1 - y0, x1 - x0)
        paint(img, range(y0, y1), range(x0, x1), wood_face, q, 0.7, g, 2.8)
        paint(img, range(y0, min(y0 + 2, y1)), range(x0, x1), wood_top, q, 0.5)
        occlude(img, range(y1 - 1, y1), range(x0, x1), 0.72)

        for (px0, px1) in ((ax0, ax1), (bx0, bx1)):
            if variant == "c" and y0 in (18, 23) and px0 == ax0:
                continue
            paint(img, range(y0, min(y0 + 2, 30)), range(px0, px1), rope, q, warm=1.0)
            paint(img, range(y0, min(y0 + 2, 30)), range(px0 + 1, px0 + 3), iron, q, warm=0.3)
    return img


def fire_pit(bank, rng, lad, top_r, face_r, q):
    img = canvas()
    stone_top, stone_face = rung(lad, top_r), rung(lad, face_r)
    ash, char = rung(lad, face_r + 2), rung(lad, 0)
    iron = rung(lad, max(0, face_r - 1))
    cy, cx, ry, rx = 17.0, 16.0, 9.5, 13.0

    # the interior first: ash, so the stones are laid ON it
    for y in range(T):
        for x in range(T):
            if ((y - cy) / ry) ** 2 + ((x - cx) / rx) ** 2 <= 1.0:
                img[y, x, 0:3] = qtint(ash * 0.80, q)
                img[y, x, 3] = 255

    # THE STONES ARE DRAWN AS STONES — individual blocks round the ring, with joints between.
    import math
    n = 13
    for i in range(n):
        a0 = 2 * math.pi * i / n
        sy = cy + (ry - 2.0) * math.sin(a0)
        sx = cx + (rx - 2.5) * math.cos(a0)
        w, h = 4 + (i % 2), 3 + (i % 3)
        y0, x0 = int(round(sy - h / 2)), int(round(sx - w / 2))
        v = stone_top if sy < cy else stone_face
        gg = grain_at(bank, rng, h, w)
        paint(img, range(max(0, y0), min(T, y0 + h)), range(max(0, x0), min(T, x0 + w)),
              v, q, 0.0, gg, 2.2)
        occlude(img, range(min(T - 1, y0 + h - 1), min(T, y0 + h)),
                range(max(0, x0), min(T, x0 + w)), 0.72)      # each stone's own foot

    # the fuel, legible as charred timber crossing ash — a fire that is TENDED has fuel in it
    paint(img, range(15, 18), range(9, 24), char * 1.5, q, warm=0.9)
    paint(img, range(19, 21), range(12, 22), char * 1.25, q, warm=0.9)
    paint(img, range(13, 15), range(14, 19), char * 1.7, q, warm=0.9)

    # iron bands, each holding two stones together
    for by in (11, 23):
        row = np.where(img[by, :, 3] > 0)[0]
        if len(row):
            paint(img, range(by, by + 2), range(row.min(), row.min() + 5), iron, q, warm=0.3)
            paint(img, range(by, by + 2), range(row.max() - 4, row.max() + 1), iron, q, warm=0.3)
    return img


def fire_flame(lad, q):
    """The flame body ALONE — no glow, no halo, no spill. Bigger than pass 1, which was a blob
    too small to read at 1x. The engine emits; this is only the visible body of the flame."""
    img = canvas()
    hot, mid, low = 240.0, 196.0, 140.0
    shape = [(9, 15, 18), (10, 14, 19), (11, 13, 20), (12, 13, 20), (13, 12, 21),
             (14, 12, 21), (15, 13, 20), (16, 13, 20), (17, 14, 19)]
    for (y, x0, x1) in shape:
        for x in range(x0, x1):
            t = abs(x - 16.5) / 4.0
            v = hot if t < 0.35 else (mid if t < 0.7 else low)
            img[y, x, 0] = min(255, v * 1.02)
            img[y, x, 1] = v * 0.60
            img[y, x, 2] = v * 0.22
            img[y, x, 3] = 255
    return img


def main():
    lad, top_r, face_r, q = planes()
    donors = []
    for wave in ("wave1", "wave2"):
        d = os.path.join(GEN, wave)
        if os.path.isdir(d):
            donors += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".png")]
    print("donors: %d generated frames, taken for GRAIN ONLY" % len(donors))
    bank = grain_bank(donors)
    print("grain bank: %d usable residuals" % len(bank))

    rng = np.random.default_rng(1337)
    out, man = ASHLAR, []

    def emit(name, img):
        tid = IDS[name]
        p = os.path.join(out, "tier1_ashlar_%d.png" % tid)
        png(p, img)
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        opaque = float((img[:, :, 3] > 128).mean())
        man.append(dict(name=name, id=tid, file=os.path.basename(p), sha256=sha,
                        opaque_fraction=round(opaque, 4)))
        print("  %-12s id %d  %5.1f%% opaque  %s" % (name, tid, opaque * 100, sha[:12]))

    emit("marker", marker(bank, rng, lad, top_r, face_r, q))
    for v in "abcd":
        emit("barricade_%s" % v, barricade(bank, rng, lad, top_r, face_r, q, v))
    emit("fire", fire_pit(bank, rng, lad, top_r, face_r, q))
    emit("fire_flame", fire_flame(lad, q))

    mf = os.path.join(HERE, "MANIFEST.json")
    json.dump({
        "family": "boundary_props_v1",
        "_what": [
            "THE BOUNDARY'S PROPS — structure composed, material taken from generation.",
            "",
            "No generated pixel is copied into a shipped tile. What crosses is the GRAIN "
            "STATISTIC: each donor's residual after a box blur removes its own structure, "
            "re-laid onto this family's ladder. The donors are listed so the audit trail is "
            "complete, and every one of them FAILED as a finished object — on projection, on "
            "role, or on a painted glow.",
            "",
            "Values are rungs of the WALL family's ladder, read from its manifest rather than "
            "restated (§13.12), so a prop standing against a wall is the same rock at the same "
            "rungs. Re-derive the walls and the props follow.",
            "",
            "PALETTE REGIME: ladder, not locked. §5.1's values are PLACEHOLDER.",
        ],
        "planes": {"top_rung": top_r, "face_rung": face_r, "top_rows": TOP_ROWS,
                   "occlusion_rows": LIP_ROWS},
        "ladder": [float(x) for x in lad],
        "donors": [os.path.relpath(p, REPO) for p in donors],
        "donor_note": "taken for grain only; every one failed as a finished object",
        "tiles": man,
    }, open(mf, "w"), indent=1)
    print("manifest: %s" % os.path.relpath(mf, REPO))


if __name__ == "__main__":
    main()
