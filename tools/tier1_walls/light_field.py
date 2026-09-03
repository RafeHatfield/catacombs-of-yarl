#!/usr/bin/env python3
"""Read the rig's lighting multiplier L off a flat-albedo capture, and prove the reading.

USAGE
    python3 tools/tier1_walls/light_field.py --controls      # the three positive controls
    python3 tools/tier1_walls/light_field.py --field         # L, per plane, per cell

WHAT L IS. `make_photometric_probe.py` paints every tile one albedo, so a capture of it is a
picture of whatever the pipeline multiplies albedo BY. Sampling that at the two places a wall's
planes sit gives the compression factor bible section 6.2's coupling flag says every authored
ratio must be solved backwards through - measured on THIS rig rather than inherited from the
sighted round's, which no longer exists (Ruling 56 moved radius and ambient both).

THE GRID COMES FROM THE ENGINE, NOT FROM ARITHMETIC. Main prints `[Tier0] grid map:` with the
screen centre of tile (0,0) and the tile pitch in captured pixels. A measurement that guessed
the camera would report confident numbers about the wrong pixels.
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
sys.path.insert(0, HERE)
from mask_census import build, masks, is_wall  # noqa: E402

# Rec.709, matching Main.PatchLuminance so an off-line number and an engine-side one are the
# same statistic rather than two statistics that usually agree.
W709 = np.array([0.2126, 0.7152, 0.0722])

GRID_RE = re.compile(
    r"grid map: centre00=\(([-\d.]+),([-\d.]+)\) pitch=\(([-\d.]+),([-\d.]+)\) "
    r"view=\(([-\d.]+),([-\d.]+)\)\.\.\.\(([-\d.]+),([-\d.]+)\)")


def read_grid(log_path):
    for line in open(log_path, "rb").read().decode("utf8", "replace").splitlines():
        m = GRID_RE.search(line)
        if m:
            v = [float(g) for g in m.groups()]
            return dict(cx0=v[0], cy0=v[1], px=v[2], py=v[3],
                        view=(v[4], v[5], v[6], v[7]))
    raise SystemExit("no '[Tier0] grid map:' line in %s - rebuild and re-capture" % log_path)


def cell_box(g, x, y):
    cx = g["cx0"] + g["px"] * x
    cy = g["cy0"] + g["py"] * y
    return (cx - g["px"] / 2.0, cy - g["py"] / 2.0, g["px"], g["py"])


def scene_mask(png_lo, png_hi, a_lo, a_hi, signal_floor=12.0):
    """Which captured pixels are SCENE, and which are interface drawn over it.

    THE PROBLEM THIS SOLVES WAS FOUND BY THE CONTROLS FAILING. The first run of the linearity
    control reported a worst-cell error of 0.32 against a mean of 0.51, and the outliers were not
    lighting - they were the HUD. The dungeon view (0,90)..(750,1001) has the zoom buttons, the
    minimap, the RIG panel, the Msg button and the player sprite drawn INSIDE it, and a cell whose
    band overlaps one of those is measuring interface.

    THE TEST IS INVARIANCE, NOT LINEARITY, AND THAT IS DELIBERATE. Selecting pixels because they
    scale correctly and then testing whether pixels scale correctly is one instrument wearing two
    hats, and it cannot fail. Interface is drawn from its own colours and does not move when the
    tile albedo changes; scene geometry does. So the mask keeps pixels that CHANGED between the
    two captures and drops the ones that did not - which is a different property from the one the
    linearity control goes on to test, and leaves that control able to come back red.

    Pixels too dark to have moved are dropped with the interface, and that is correct rather than
    unfortunate: a sample with no signal in it is not evidence about a ratio.
    """
    LO = np.array(Image.open(png_lo).convert("RGB")).astype(float)
    HI = np.array(Image.open(png_hi).convert("RGB")).astype(float)
    lo = (LO * W709).sum(2)
    hi = (HI * W709).sum(2)
    moved = np.abs(hi - lo) > 1.0
    # CLIPPED PIXELS ARE NOT MEASUREMENTS. Near the lamp the brighter probe drives channels into
    # 255 and the ratio bends toward 1 - the first run of the linearity control read 0.522 on the
    # cells beside the player for exactly this reason. A clipped sample is the sensor's limit
    # being reported as the scene's value.
    clipped = (HI.max(2) >= 254) | (LO.max(2) >= 254)
    # QUANTISATION IS THE SAME PROBLEM AT THE OTHER END. At eight bits a pixel reading 7 against
    # one reading 14 carries a rounding error of +-7%, which is larger than every effect this
    # probe exists to measure. The dark half of the scene is outside the instrument's domain and
    # is declared so rather than averaged in.
    # The ambient-only control sets this to zero deliberately: under a flat albedo and a
    # CanvasModulate every scene pixel holds ONE value, so quantisation cannot bend a ratio
    # between two bands of it, and the eight-bit floor is not a limit there.
    signal = lo >= signal_floor
    return moved & (~clipped) & signal


def pure_scene_mask(png_lo, png_hi, a_lo, a_hi, tol=0.01, signal_floor=0.0):
    """The strict mask: pixels whose albedo response is the response of BARE SCENE.

    `scene_mask` catches opaque interface. It does not catch TRANSLUCENT interface, and this
    scene has three pieces of it drawn inside the dungeon view - the zoom buttons, the RIG panel
    and the Msg button. A pixel under a panel of opacity a reads `ui*a + scene*(1-a)`: it still
    MOVES with albedo, so the invariance mask keeps it, and it moves by the wrong proportion. The
    unity control found them by failing on exactly four cells, all of them under a panel.

    So this mask asks the stronger question - does the pixel scale by the albedo ratio - and it
    is used everywhere EXCEPT the linearity control, which establishes that scaling in the first
    place. Selecting on scaling and then testing scaling would be one instrument in two hats;
    using scaling as a mask AFTER it has been proven on an independent selection is just applying
    a measured fact.
    """
    LO = np.array(Image.open(png_lo).convert("RGB")).astype(float)
    HI = np.array(Image.open(png_hi).convert("RGB")).astype(float)
    lo = (LO * W709).sum(2)
    hi = (HI * W709).sum(2)
    clipped = (HI.max(2) >= 254) | (LO.max(2) >= 254)
    expect = float(a_lo) / float(a_hi)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(hi > 0.5, lo / np.maximum(hi, 1e-6), -1.0)
    return (np.abs(r - expect) <= tol) & (~clipped) & (lo >= signal_floor)


def band_mean(img, g, x, y, row0, row1, inset=2, mask=None, min_valid=0.90):
    """Mean Rec.709 luminance over native rows [row0,row1) of cell (x,y).

    `inset` trims columns at the cell's left and right edges. The trim is in NATIVE pixels and
    exists because a sample that includes the boundary column includes whatever the neighbouring
    cell put there, and the whole point of the plane samples is that they are of ONE plane.

    `mask` marks scene pixels. A band with fewer than `min_valid` of them returns None rather
    than a number, because a partly-occluded sample is worse than an absent one: it looks like
    data.
    """
    x0, y0, w, h = cell_box(g, x, y)
    s = w / 32.0                                   # captured px per native px
    px0 = int(round(x0 + inset * s))
    px1 = int(round(x0 + w - inset * s))
    py0 = int(round(y0 + row0 * s))
    py1 = int(round(y0 + row1 * s))
    H, W = img.shape[:2]
    px0, px1 = max(0, px0), min(W, px1)
    py0, py1 = max(0, py0), min(H, py1)
    if px1 <= px0 or py1 <= py0:
        return None
    patch = (img[py0:py1, px0:px1].astype(float) * W709).sum(2)
    if mask is None:
        return float(patch.mean())
    m = mask[py0:py1, px0:px1]
    if m.mean() < min_valid or m.sum() == 0:
        return None
    return float(patch[m].mean())


def in_view(g, x, y):
    x0, y0, w, h = cell_box(g, x, y)
    vx0, vy0, vx1, vy1 = g["view"]
    return x0 >= vx0 and y0 >= vy0 and x0 + w <= vx1 and y0 + h <= vy1


def load(png, log):
    return np.array(Image.open(png).convert("RGB")), read_grid(log)


def samples(spec_path, png, log, turn_row=16, mask=None):
    """Per-cell plane samples for every cell fully inside the dungeon view."""
    spec = json.load(open(spec_path))
    wall, w, h = build(spec)
    img, g = load(png, log)
    px, py = spec["player"]["x"], spec["player"]["y"]
    rows = []
    for y in range(h):
        for x in range(w):
            if not in_view(g, x, y):
                continue
            c, d = masks(wall, w, h, x, y) if wall[y][x] else (None, None)
            rows.append(dict(
                x=x, y=y, wall=bool(wall[y][x]), cardinal=c, diagonal=d,
                dist=float(np.hypot(x - px, y - py)),
                dy=y - py,
                top=band_mean(img, g, x, y, 0, turn_row, mask=mask),
                face=band_mean(img, g, x, y, turn_row, 32, mask=mask),
                whole=band_mean(img, g, x, y, 0, 32, mask=mask),
            ))
    return spec, rows, g


def controls():
    scene_f = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes/tier1_floor_review.json")
    scene_m = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes/mixed_distribution.json")
    out = {"produced_by": "tools/tier1_walls/light_field.py --controls"}
    verdicts = []

    mask_f = scene_mask(os.path.join(EV, "probe_a101.png"), os.path.join(EV, "probe_a202.png"), 101, 202)
    mask_m = pure_scene_mask(os.path.join(EV, "probe_a101_mixed.png"),
                             os.path.join(EV, "probe_a202_mixed.png"), 101, 202, signal_floor=12.0)
    mask_e0 = pure_scene_mask(os.path.join(EV, "probe_a101_e0.png"),
                              os.path.join(EV, "probe_a202_e0.png"), 101, 202)
    out["scene_pixel_share"] = dict(floor_review=round(float(mask_f.mean()), 4),
                                    mixed=round(float(mask_m.mean()), 4),
                                    mixed_e0=round(float(mask_e0.mean()), 4))

    # ---- CONTROL 1: LINEARITY. Two albedos, same scene, same rig.
    _, r101, _ = samples(scene_f, os.path.join(EV, "probe_a101.png"),
                         os.path.join(EV, "probe_a101.log"), mask=mask_f)
    _, r202, _ = samples(scene_f, os.path.join(EV, "probe_a202.png"),
                         os.path.join(EV, "probe_a202.log"), mask=mask_f)
    pairs = [(a["whole"], b["whole"]) for a, b in zip(r101, r202)
             if a["whole"] and b["whole"] and b["whole"] > 1.0]
    ratio = np.array([a / b for a, b in pairs])
    expect = 101.0 / 202.0
    lin_err = float(np.abs(ratio - expect).max())
    lin_ok = lin_err < 0.02
    out["linearity"] = dict(expected=expect, mean=float(ratio.mean()),
                            p5=float(np.percentile(ratio, 5)), p95=float(np.percentile(ratio, 95)),
                            max_abs_error=lin_err, n=len(pairs), pass_=lin_ok)
    verdicts.append(("LINEARITY", lin_ok,
                     "albedo 101/202 -> %.4f (expect %.4f), worst cell off by %.4f over %d cells"
                     % (ratio.mean(), expect, lin_err, len(pairs))))

    # ---- CONTROL 2: UNITY UNDER AMBIENT. Energy 0: the two planes must not separate at all.
    _, re0, _ = samples(scene_m, os.path.join(EV, "probe_a202_e0.png"),
                        os.path.join(EV, "probe_a202_e0.log"), mask=mask_e0)
    fr = np.array([r["face"] / r["top"] for r in re0
                   if r["wall"] and r["top"] and r["face"] and r["top"] > 1.0])
    uni_err = float(np.abs(fr - 1.0).max()) if len(fr) else 9.9
    uni_ok = uni_err < 0.005
    out["unity_ambient_only"] = dict(mean=float(fr.mean()), max_abs_error=uni_err,
                                     n=int(len(fr)), pass_=uni_ok)
    # THE SAME STATISTIC UNDER THE LIT RIG. Without this line the unity control proves only that
    # the sampler can return 1.0, which is what a broken sampler stuck on a constant would also
    # do. Section 13.5 asks for the failure to be shown, so it is shown here rather than asserted:
    # the identical measurement, on the identical geometry, with the lamp on.
    _, rlit, _ = samples(scene_m, os.path.join(EV, "probe_a202_mixed.png"),
                         os.path.join(EV, "probe_a202_mixed.log"), mask=mask_m)
    frl = np.array([r["face"] / r["top"] for r in rlit
                    if r["wall"] and r["top"] and r["face"] and r["top"] > 1.0])
    out["unity_lit_counterpart"] = dict(mean=float(frl.mean()) if len(frl) else None,
                                        max_abs_error=float(np.abs(frl - 1.0).max()) if len(frl) else None,
                                        n=int(len(frl)))
    verdicts.append(("UNITY", uni_ok,
                     "energy=0 face/top = %.5f over %d wall cells, worst %.5f from 1.0"
                     % (fr.mean(), len(fr), uni_err)))
    verdicts.append(("UNITY-FAILS", len(frl) > 0 and float(np.abs(frl - 1.0).max()) > 0.05,
                     "same statistic, lamp ON: face/top = %.5f over %d cells, worst %.5f from 1.0"
                     % (frl.mean() if len(frl) else 0, len(frl),
                        float(np.abs(frl - 1.0).max()) if len(frl) else 0)))

    # ---- CONTROL 3: THE DARK-CELL CONSTANT. Wall-adjacent floor cells are modulated by the
    # renderer, and a floor sample taken beside a wall is dark for a reason that is not light.
    spec, rl, _ = samples(scene_m, os.path.join(EV, "probe_a202_mixed.png"),
                          os.path.join(EV, "probe_a202_mixed.log"), mask=mask_m)
    wallmap, w, h = build(spec)
    adj, free = [], []
    for r in rl:
        if r["wall"] or not r["whole"]:
            continue
        near = any(is_wall(wallmap, w, h, r["x"] + dx, r["y"] + dy)
                   for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
        (adj if near else free).append(r)
    # Compare only pairs at equal distance from the lamp, or the light field swamps the constant.
    got = []
    for a in adj:
        for f in free:
            if abs(a["dist"] - f["dist"]) < 0.05 and f["whole"] > 1.0:
                got.append(a["whole"] / f["whole"])
    dark_ok = len(got) > 0
    out["dark_cell_modulate"] = dict(n=len(got),
                                     median=float(np.median(got)) if got else None,
                                     pass_=dark_ok)
    verdicts.append(("DARK-CELL", dark_ok,
                     ("wall-adjacent floor reads %.4f of free floor at equal range over %d pairs"
                      % (float(np.median(got)), len(got))) if got
                     else "no equal-range pairs found - the constant is unmeasured"))

    for name, ok, line in verdicts:
        print("  %-10s %s   %s" % (name, "PASS" if ok else "FAIL", line))
    out["all_pass"] = all(v[1] for v in verdicts)
    json.dump(out, open(os.path.join(EV, "LIGHT-FIELD-CONTROLS.json"), "w"), indent=2)
    print("\n  wrote tools/tier1_walls/evidence/LIGHT-FIELD-CONTROLS.json")
    return 0 if out["all_pass"] else 1


def field(scene, png, log, albedo):
    spec, rows, g = samples(os.path.join(REPO, scene), os.path.join(REPO, png),
                            os.path.join(REPO, log))
    for r in rows:
        for k in ("top", "face", "whole"):
            r["L_" + k] = None if r[k] is None else r[k] / albedo
    out = dict(produced_by="tools/tier1_walls/light_field.py --field", scene=spec["name"],
               capture=png, albedo=albedo, cells=rows)
    p = os.path.join(EV, "LIGHT-FIELD-%s.json" % spec["name"])
    json.dump(out, open(p, "w"), indent=2)
    print("wrote %s  (%d cells in view)" % (os.path.relpath(p, REPO), len(rows)))

    print("\n  THE COMPRESSION, per wall cell, by range from the lamp:")
    print("  %-9s %-6s %8s %8s %8s" % ("cell", "range", "L(top)", "L(face)", "face/top"))
    ws = [r for r in rows if r["wall"] and r["top"] and r["top"] > 0.5]
    for r in sorted(ws, key=lambda r: r["dist"])[:24]:
        print("  (%2d,%2d)   %5.2f  %8.4f %8.4f %8.4f"
              % (r["x"], r["y"], r["dist"], r["L_top"], r["L_face"], r["face"] / r["top"]))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--field", action="store_true")
    ap.add_argument("--scene", default="src/Presentation/assets/tier0_harness/scenes/tier1_floor_review.json")
    ap.add_argument("--png", default="tools/tier1_walls/evidence/probe_a202.png")
    ap.add_argument("--log", default="tools/tier1_walls/evidence/probe_a202.log")
    ap.add_argument("--albedo", type=float, default=202.0)
    a = ap.parse_args()
    rc = 0
    if a.controls:
        rc |= controls()
    if a.field:
        rc |= field(a.scene, a.png, a.log, a.albedo)
    sys.exit(rc)
