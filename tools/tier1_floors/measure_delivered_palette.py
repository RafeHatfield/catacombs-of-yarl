#!/usr/bin/env python3
"""HOW MANY COLOURS DOES THE FLOOR ACTUALLY DELIVER? — a builder's tool, and only that.

A BUILDER'S TOOL. It prints its numbers every round and it votes on nothing (LOOP-PROCESS §4.3,
`ART-LOOP-PROCESS-v0.md` §1.2). There is no threshold in this file and no verdict line: the only
thing that judges an art round is a blind seat's eyes on the delivered frames.

WHAT IT IS FOR. The family authors ELEVEN values and ships them as a ladder. Anything that puts a
value BETWEEN two rungs on the way to the screen is off the palette, and it is invisible in every
other instrument here — the lattice score, the grid-coincidence ratio, the enclosure census and
the ladder-reach audit all read a field the composer built and are therefore blind to a layer
drawn OVER it. The contact occlusion was exactly that layer for as long as it was a sprite: one
colour, rgb(22,22,22), carrying a 130-step alpha ramp, which took the family's authored albedo to
**132 values**. It is the wall cap's disease (107 -> 9) on a different surface, and nothing in the
repo would have said so.

⚠ THE THING THIS TOOL WILL NOT DO IS COUNT COLOURS IN A LIT FRAME AND CALL THAT A PALETTE.
A carried lamp is a continuous radial field and 8-bit output quantises it into hundreds of values
whatever the albedo is. Measured on `mottle_lit` at the ratified rig: the floor carries 196
colours per cell on average and the WALL carries 107 — both far above either surface's palette,
neither of them evidence of an off-palette layer. A whole-frame count of ~4700 is a measurement
of the rig. So:

    --field     (default) the ALBEDO, from the reference painter, with every layer that reaches
                the delivered pixel applied. This is the number a palette claim can be made on.
    --capture   the delivered frame, per cell, floor AND wall side by side. Reported because it
                is what a seat looks at, and labelled as the rig's number rather than the art's.

CONTROLS (§13.5's habit, kept even though nothing here gates). `--controls` re-runs the field
census with the occlusion composited the OLD way — an alpha blend toward rgb(22,22,22) instead of
a rung subtraction — and asserts the count goes up. A census that cannot be made to report a
smear is a census that would have missed this one.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_ashlar as FA        # noqa: E402

W709 = np.array([0.2126, 0.7152, 0.0722])


def legal_palette(mat):
    """Every colour the family is ALLOWED to deliver, from the material alone.

    A ladder rung times one of the chroma tints, and nothing else. Derived rather than harvested
    from the field: a palette read off the work is a palette that can never be violated.
    """
    lad = np.asarray(mat["ladder"], dtype=float)
    tints = [CA.chroma_tint(mat["tint"], s) for s in CA.CHROMA_BY_AGE]
    out = set()
    for L in lad:
        for t in tints:
            v = np.clip(L * np.asarray(t), 0, 255)
            # BOTH RENDERINGS OF THE SAME LEGAL VALUE. The reference painter finishes with
            # `.astype(np.uint8)`, which TRUNCATES; the engine writes a float into an Rgb8 Image,
            # which ROUNDS. The two therefore land a level apart on the same rung — a real
            # difference, worth its own look, and not the thing this file is measuring. Counting
            # only one of them reported 29 of 30 authored colours as off-palette, which is the
            # instrument being wrong rather than the floor.
            out.add(tuple(int(x) for x in np.floor(v)))
            out.add(tuple(int(x) for x in np.round(v)))
    return out


def authored_count(mat):
    """How many colours the family AUTHORS — rungs x chroma tints, counted once each.

    Distinct from `legal_palette`, which holds two 8-bit renderings of each of these because the
    two painters round differently. The ratio a reader wants is against what was authored; the
    membership test wants both renderings. Reporting one number for both jobs is how an
    instrument ends up 2x wrong in the direction that flatters it.
    """
    lad = np.asarray(mat["ladder"], dtype=float)
    tints = {tuple(np.round(CA.chroma_tint(mat["tint"], s), 9)) for s in CA.CHROMA_BY_AGE}
    return len(lad) * len(tints)


def census(img, mat, label):
    """Distinct colours, and how many of them the family never authored."""
    a = np.asarray(img).reshape(-1, 3)
    uniq = {tuple(int(v) for v in c) for c in np.unique(a, axis=0)}
    legal = legal_palette(mat)
    off = uniq - legal
    auth = authored_count(mat)
    ratio = len(uniq) / max(auth, 1)
    print("  %-28s delivered=%4d   authored=%3d   ratio=%6.1f%%   OFF-PALETTE=%d"
          % (label, len(uniq), auth, 100 * ratio, len(off)))
    if off:
        # THE WORST CELL, EVERY BAND — never the summary that agrees with you. A count alone
        # cannot say whether the strays are one stray or a continuous ramp, and a ramp is the
        # defect. The widest run of consecutive luminances that the ladder does not contain is
        # what a smear looks like as a number.
        lums = sorted({int(round(np.dot(c, W709))) for c in off})
        run, best = 1, 1
        for i in range(1, len(lums)):
            run = run + 1 if lums[i] == lums[i - 1] + 1 else 1
            best = max(best, run)
        print("      %d off-palette colours span %d luminances, longest unbroken run %d"
              % (len(off), len(lums), best))
    return len(uniq), len(legal), len(off)


def wall_sides(w, h):
    """A ring of wall around the field, so every edge cell carries a real occlusion decision."""
    def at(x, y):
        mask = 0
        if y == 0:     mask |= 1          # N
        if x == w - 1: mask |= 2          # E
        if y == h - 1: mask |= 4          # S
        if x == 0:     mask |= 8          # W
        return (mask, 1) if mask else None
    return at


def field_census(mat, n=16, seed=1337, layers_probe=True):
    traffic = np.zeros((n, n), dtype=np.uint8)
    traffic[n // 2 - 1:n // 2 + 1, :] = 255
    print("\nTHE ALBEDO — the reference painter, %dx%d cells, seed %d" % (n, n, seed))
    bare, _, _, _, _ = FA.assemble(n, n, seed, mat, None, traffic=traffic)
    census(bare, mat, "no walls in the field")
    occ, _, _, _, _ = FA.assemble(n, n, seed, mat, None, traffic=traffic,
                                  occlusion=wall_sides(n, n))
    census(occ, mat, "with contact occlusion")
    if layers_probe:
        for L in (2, 3):
            def at(x, y, L=L, base=wall_sides(n, n)):
                r = base(x, y)
                return None if r is None else (r[0], L)
            img, _, _, _, _ = FA.assemble(n, n, seed, mat, None, traffic=traffic, occlusion=at)
            census(img, mat, "occlusion stacked x%d" % L)
    return bare, occ


def blended_control(mat, n=16, seed=1337):
    """THE PLANT. The occlusion composited the way it used to be — an alpha blend.

    Introduced on the FIELD rather than in the composer, so it differs from the shipped arm in
    this one thing. If the census cannot see a 130-step ramp blended into a quantised floor it
    would not have seen the one that shipped, and its clean readings mean nothing.
    """
    traffic = np.zeros((n, n), dtype=np.uint8)
    traffic[n // 2 - 1:n // 2 + 1, :] = 255
    img, _, _, _, _ = FA.assemble(n, n, seed, mat, None, traffic=traffic)
    a = np.asarray(img).astype(float)
    at = wall_sides(n, n)
    T = CA.T
    for y in range(n):
        for x in range(n):
            oc = at(x, y)
            if oc is None:
                continue
            keep = np.ones((T, T), dtype=float)
            for i, side in enumerate(CA.OCCLUSION_SIDES):
                if oc[0] & (1 << i):
                    keep *= 1.0 - CA.occlusion_alpha(side)
            sl = (slice(y * T, (y + 1) * T), slice(x * T, (x + 1) * T))
            alpha = (1.0 - keep)[..., None]
            a[sl] = a[sl] * (1.0 - alpha) + CA.OCCLUSION_FLOOR * alpha
    return np.round(a).astype(np.uint8)


def capture_census(png, log, spec_path, mat):
    """The DELIVERED frame, per cell. The rig's number, reported as the rig's number."""
    from PIL import Image
    sys.path.insert(0, os.path.join(REPO, "tools", "tier1_walls"))
    import light_field as LF          # noqa: E402
    from mask_census import build     # noqa: E402

    spec = json.load(open(spec_path))
    wall, w, h = build(spec)
    g = LF.read_grid(log)
    img = np.array(Image.open(png).convert("RGB"))
    px, py = spec["player"]["x"], spec["player"]["y"]
    print("\nTHE DELIVERED FRAME — %s" % os.path.relpath(png, REPO))
    print("  ⚠ a carried lamp is continuous: these counts are the RIG's, not the palette's.")
    print("     The wall row is here so the floor's number has something to be read against.")
    for kind in ("floor", "wall"):
        rows = []
        for y in range(h):
            for x in range(w):
                if wall[y][x] != (kind == "wall"):
                    continue
                if not LF.in_view(g, x, y):
                    continue
                if abs(x - px) <= 1 and abs(y - py) <= 1:
                    continue          # the figure is not the ground
                x0, y0, cw, ch = LF.cell_box(g, x, y)
                p = img[int(y0) + 6:int(y0 + ch) - 6, int(x0) + 6:int(x0 + cw) - 6].reshape(-1, 3)
                if p.size < 48:
                    continue
                rows.append((len(np.unique(p, axis=0)), (x, y),
                             float((p * W709).sum(1).mean())))
        if not rows:
            print("  %-6s no cells in view" % kind)
            continue
        rows.sort(reverse=True)
        print("  %-6s cells=%2d  mean=%6.1f colours/cell   WORST=%4d at %s   brightest cell=%d"
              % (kind, len(rows), sum(r[0] for r in rows) / len(rows), rows[0][0], rows[0][1],
                 max(rows, key=lambda r: r[2])[0]))


def ladder_delta(mat, n=16, seed=1337):
    """What extending the ladder below the donors' band actually moved, in the composed field.

    Referenced from `PALETTE_EXTEND_BELOW` in compose_family, which is where the reasoning lives.
    """
    traffic = np.zeros((n, n), dtype=np.uint8)
    traffic[n // 2 - 1:n // 2 + 1, :] = 255
    out = {}
    for ex in (2, CF.PALETTE_EXTEND_BELOW):
        m = dict(mat)
        m["ladder"] = list(CF.ladder_for(mat["lum_lo"], mat["lum_hi"], extend_below=ex))
        img, joints, _, cracks, _ = FA.assemble(n, n, seed, m, None, traffic=traffic)
        out[ex] = (np.asarray(img), joints, cracks, m["ladder"])
    a, ja, ca, la = out[2]
    b, jb, cb, lb = out[CF.PALETTE_EXTEND_BELOW]
    ch = (np.abs(a.astype(int) - b.astype(int)).max(2) > 0)
    tot = ch.size
    print("\nLADDER DELTA — extend_below 2 (%d rungs, bottom %.2f) -> %d (%d rungs, bottom %.2f)"
          % (len(la), la[0], CF.PALETTE_EXTEND_BELOW, len(lb), lb[0]))
    print("  pixels moved: %d of %d (%.2f%%)" % (ch.sum(), tot, 100 * ch.sum() / tot))
    if ch.sum():
        print("    joints %5.1f%%   cracks %5.1f%%   stone faces %5.1f%%"
              % (100 * (ch & ja).sum() / ch.sum(), 100 * (ch & ca).sum() / ch.sum(),
                 100 * (ch & ~ja & ~ca).sum() / ch.sum()))
    for lbl, img, jm in (("9 rungs", a, ja), ("%d rungs" % len(lb), b, jb)):
        jc = FA.joint_contrast(img, jm)
        jv = FA.joint_variation(img, jm, n, n, lb[1] - lb[0])
        print("  %-9s joint contrast mean %.4f p50 %.4f  |  spread %.3f rungs, "
              "deciles open %.1f tight %.1f"
              % (lbl, jc["mean_weber"], jc["p50"], jv["spread_rungs"],
                 jv["open_decile"], jv["tight_decile"]))
    print("  The distribution is what says whether this is PR #161 repeating; the mean is not.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=CA.ASSETS)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--capture", nargs=2, metavar=("PNG", "LOG"),
                    help="also census a delivered capture (the rig's number, labelled as such)")
    ap.add_argument("--scene", default=os.path.join(
        REPO, "src/Presentation/assets/tier0_harness/scenes/tier1_floor_route_onroute.json"))
    ap.add_argument("--controls", action="store_true",
                    help="re-run with the occlusion BLENDED, and assert the census sees it")
    ap.add_argument("--ladder-delta", action="store_true",
                    help="what the ladder extension moved in the composed field")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    man = json.load(open(os.path.join(a.assets, "MANIFEST.json")))
    mat = man["material"]
    lad = mat["ladder"]
    print("DELIVERED PALETTE — %s" % os.path.relpath(a.assets, REPO))
    print("  ladder: %d rungs, %.2f .. %.2f, step %.3f"
          % (len(lad), lad[0], lad[-1], lad[1] - lad[0]))
    print("  authored: %d colours (%d rungs x chroma tints); %d legal 8-bit renderings of them"
          % (authored_count(mat), len(lad), len(legal_palette(mat))))

    bare, occ = field_census(mat, a.n, a.seed)
    result = dict(ladder_rungs=len(lad), authored=authored_count(mat),
                  legal_renderings=len(legal_palette(mat)))

    if a.controls:
        print("\nCONTROL — the occlusion BLENDED, the way the sprite did it")
        img = blended_control(mat, a.n, a.seed)
        n_blend, _, off_blend = census(img, mat, "alpha-blended occlusion")
        n_snap = len({tuple(int(v) for v in c)
                      for c in np.unique(np.asarray(occ).reshape(-1, 3), axis=0)})
        ok = n_blend > n_snap and off_blend > 0
        print("  %s: blended %d vs snapped %d colours, %d off-palette under the blend"
              % ("CONTROL BINDS" if ok else "CONTROL DID NOT BIND — the census is not measuring "
                 "what it claims", n_blend, n_snap, off_blend))
        result["control"] = dict(blended=n_blend, snapped=n_snap, off_palette=off_blend, binds=ok)
        if not ok:
            return 1

    if a.ladder_delta:
        ladder_delta(mat, a.n, a.seed)

    if a.capture:
        capture_census(a.capture[0], a.capture[1], a.scene, mat)

    if a.json_out:
        json.dump(result, open(a.json_out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
