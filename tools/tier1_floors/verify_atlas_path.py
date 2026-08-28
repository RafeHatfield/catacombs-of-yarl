#!/usr/bin/env python3
"""DOES THE SHIPPED ASSET REPRODUCE THE MEASURED FIELD?

Every number on the record — enclosure 0.8%, boundary step 0.75x, continuity 1.00, grid hiding
1.00 — was measured on a field the Python composer built directly, calling `build_tile` and
painting from its own arrays. THAT IS NOT WHAT SHIPS. What ships is 81 atlases and a grain bank,
and an engine that reads them and paints. If those two paths disagree by even a ladder step, the
measurements describe a floor nobody will ever see, and the disagreement would surface as a value
seam in the one place there is no instrument watching: between the tool and the game.

So this file walks the SHIPPED path in Python — atlas in, ladder index out, grain sampled from
the bank, stone addressed exactly as `Tier1AshlarFloor.cs` addresses it — and compares it pixel
for pixel against the direct path. It is the same discipline as the manifest's cross-check
vectors, one level up: those prove the engine's ARITHMETIC matches the composer's, and this
proves the composer's OUTPUT matches its own input.

⚠ IT MUST BE ABLE TO FAIL. `--plant` corrupts one atlas byte and asserts the comparison catches
it (bible §13.5: no instrument's pass counts until it has demonstrated it can fail).
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
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_ashlar as FA        # noqa: E402
import field_laws as FL          # noqa: E402

T = CA.T


def paint_from_atlas(w, h, seed, man, worn=None, corrupt=None, assets=None):
    """The engine's algorithm, in Python. Deliberately written from the C# rather than from the
    composer, so a shared mistake in the composer cannot hide behind a shared implementation."""
    A = assets or CA.ASSETS
    mat = man["material"]
    ladder = np.array(mat["ladder"])
    tint = mat["tint"]
    step = ladder[1] - ladder[0]
    gs = man["grain_scales"]
    amp = man["grain_amp"]
    bank = np.asarray(Image.open(os.path.join(A, man["grain_file"])).convert("RGB")).astype(float)
    side = 2 * T

    atlases = {}
    for e in man["base"]:
        idx = CA.tile_index(e["n"], e["e"], e["s"], e["w"])
        a = np.asarray(Image.open(os.path.join(A, e["file"])).convert("RGB")).copy()
        if corrupt is not None and idx == corrupt[0]:
            cr, cc, py, px = corrupt[1:]
            a[cr * T + py, cc * T + px, 0] = (int(a[cr * T + py, cc * T + px, 0]) + 3) % len(ladder)
        atlases[idx] = a

    crack_cache = {}
    crack_v = mat["lum_median"] * man["crack"]["depth"]
    img = np.zeros((h * T, w * T, 3), dtype=np.uint8)
    yy, xx = np.mgrid[0:T, 0:T]
    for y in range(h):
        for x in range(w):
            n = CA.edge_family(x, y, CA.HORIZ, seed)
            s_ = CA.edge_family(x, y + 1, CA.HORIZ, seed)
            fw = CA.edge_family(x, y, CA.VERT, seed)
            fe = CA.edge_family(x + 1, y, CA.VERT, seed)
            at = atlases[CA.tile_index(n, fe, s_, fw)]
            drops = [CA.drop_choice(x, y * CA.COURSES + c, seed) for c in range(CA.COURSES)]
            split_i = CA.row_split(y, seed)
            ci = split_i * 9 + drops[0] * 3 + drops[1]
            cr, cc = ci // 6, ci % 6
            cell = at[cr * T:(cr + 1) * T, cc * T:(cc + 1) * T]
            L = ladder[cell[..., 0]].astype(float)
            cls = cell[..., 1]

            wornc = {}
            for c in range(CA.COURSES):
                course_k = y * CA.COURSES + c
                for kind in (0, 1, 2):
                    cid = 1 + c * 3 + kind
                    m = cls == cid
                    if not m.any():
                        continue
                    addr = CA.stone_kind_address(kind, drops[c])
                    bx = x + 1 if addr == 2 else x
                    key = (CA.stone_key_span(bx, course_k, seed) if addr in (0, 2)
                           else CA.stone_key_interior(x, course_k, seed))
                    k = max(-3, min(3, CA.OFFSET_STEPS[key % len(CA.OFFSET_STEPS)]
                                    + CA.cluster_bias(bx, course_k, seed)))
                    is_worn = FA.stone_worn(worn, addr, x, y)
                    wornc[cid] = is_worn
                    off = k * step * (man["wear"]["spread"] if is_worn else 1.0)
                    gm = amp * (gs["worn_multiplier"] if is_worn else 1.0)
                    b = key % man["grain_bank"]
                    bx0, by0 = (b % 8) * side, (b // 8) * side
                    ox = CA.stone_origin(fw, fe, kind, c, drops[c])
                    oy = CA.course_origin_y(split_i, c)
                    lx, ly = (xx - ox) % side, (yy - oy) % side
                    g = ((bank[by0 + ly, bx0 + lx, 0] - 128) / 64.0 * gs["coarse"]
                         + (bank[by0 + ly, bx0 + lx, 1] - 128) / 64.0 * gs["fine"])
                    v = np.clip(L + off + g * gm, ladder[0], ladder[-1])
                    L = np.where(m, ladder[np.abs(v[..., None] - ladder).argmin(-1)], L)

            # The arris pass, walked the way the engine walks it: bounds-checked, from the class
            # mask, quantised back onto the ladder.
            if any(wornc.values()) and man["wear"]["arris"] > 0:
                ws = np.zeros((T, T), dtype=bool)
                for cid, w_ in wornc.items():
                    if w_:
                        ws |= (cls == cid)
                jw = np.zeros((T, T), dtype=bool)
                jw[1:, :] |= ws[:-1, :]
                jw[:-1, :] |= ws[1:, :]
                jw[:, 1:] |= ws[:, :-1]
                jw[:, :-1] |= ws[:, 1:]
                jw &= (cls == 0)
                if jw.any():
                    v = L + (mat["lum_median"] - L) * man["wear"]["arris"]
                    v = np.clip(v, ladder[0], ladder[-1])
                    L = np.where(jw, ladder[np.abs(v[..., None] - ladder).argmin(-1)], L)

            for (ly, lx) in CA.crack_pixels(x, y, seed, crack_cache):
                L[ly, lx] = ladder[int(np.abs(crack_v - ladder).argmin())]

            img[y * T:(y + 1) * T, x * T:(x + 1) * T] = \
                np.clip(np.stack([L * tint[0], L * tint[1], L * tint[2]], -1), 0, 255)
    return img


def a_byte_the_field_actually_reads(w, h, seed):
    """Pick the plant's target from what the field LAYS, not from what exists.

    The first plant corrupted a byte in tile index 40, cell (1,1) — a family-and-merge combination
    that never occurs in an 8x8 field. Nothing read it, the comparison stayed at zero, and the
    check reported itself decorative. Correct verdict, wrong reason: the instrument was fine and
    the plant was aimed at nothing. A control has to be pointed at live data.
    """
    for y in range(h):
        for x in range(w):
            n = CA.edge_family(x, y, CA.HORIZ, seed)
            s_ = CA.edge_family(x, y + 1, CA.HORIZ, seed)
            fw = CA.edge_family(x, y, CA.VERT, seed)
            fe = CA.edge_family(x + 1, y, CA.VERT, seed)
            drops = [CA.drop_choice(x, y * CA.COURSES + c, seed) for c in range(CA.COURSES)]
            ci = CA.row_split(y, seed) * 9 + drops[0] * 3 + drops[1]
            return (CA.tile_index(n, fe, s_, fw), ci // 6, ci % 6, 8, 8)
    raise SystemExit("no cells in the field")


def compare(a, b):
    d = np.abs(a.astype(int) - b.astype(int))
    bad = (d.max(axis=2) > 0)
    return dict(pixels=int(bad.size), differing=int(bad.sum()),
                differing_pct=round(100.0 * float(bad.mean()), 4),
                max_channel_delta=int(d.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--h", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--plants", action="store_true")
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]

    print("DOES THE SHIPPED ASSET REPRODUCE THE MEASURED FIELD? — %dx%d, seed %d\n"
          % (a.w, a.h, a.seed))

    direct, _joints, _, _cr = FA.assemble(a.w, a.h, a.seed, mat)
    shipped = paint_from_atlas(a.w, a.h, a.seed, man)
    c = compare(direct, shipped)
    ok = c["differing"] == 0
    print("  direct composer vs shipped atlases: %d of %d pixels differ (%.4f%%), "
          "max channel delta %d  -> %s"
          % (c["differing"], c["pixels"], c["differing_pct"], c["max_channel_delta"],
             "IDENTICAL" if ok else "DISAGREE"))

    # THE CHANNEL ARM. Wear is the half of the family with the most arithmetic in it and it was
    # verified nowhere: the comparison above runs with no channel declared, so every wear term
    # could have been wrong in both directions and this file would still have said IDENTICAL.
    band = lambda x, y: a.w // 2 - 1 <= x <= a.w // 2
    d2, _j2, _t2, _c2 = FA.assemble(a.w, a.h, a.seed, mat, band)
    s2 = paint_from_atlas(a.w, a.h, a.seed, man, worn=band)
    c2 = compare(d2, s2)
    ok = ok and c2["differing"] == 0
    print("  with the trodden channel declared:  %d of %d pixels differ (%.4f%%)  -> %s"
          % (c2["differing"], c2["pixels"], c2["differing_pct"],
             "IDENTICAL" if c2["differing"] == 0 else "DISAGREE"))

    plant = None
    if a.plants:
        corrupt = a_byte_the_field_actually_reads(a.w, a.h, a.seed)
        shipped_bad = paint_from_atlas(a.w, a.h, a.seed, man, corrupt=corrupt)
        cb = compare(direct, shipped_bad)
        fired = cb["differing"] > 0
        plant = dict(corrupted=dict(tile_index=corrupt[0], cell=[corrupt[1], corrupt[2]],
                                    pixel=[corrupt[3], corrupt[4]]),
                     fired=fired, measured=cb)
        print("  PLANT: ONE ladder index altered — tile %d, atlas cell (%d,%d), pixel (%d,%d)"
              % corrupt)
        print("         -> %s (%d pixels differ)"
              % ("CAUGHT" if fired else "MISSED — this check is decorative", cb["differing"]))
        if not fired:
            print("  REFUSING: the comparison cannot fail, so its pass means nothing.")
            ok = False

    out = dict(commit=FL.git_commit(), grid=[a.w, a.h], seed=a.seed, identical=ok,
               comparison=c, comparison_with_channel=c2, plant=plant)
    p = os.path.join(HERE, "evidence", "ATLAS-PATH.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
