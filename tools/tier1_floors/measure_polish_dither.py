#!/usr/bin/env python3
"""THE DITHER — is the polish term surface response, or a noise stamp laid over the light?

Round 28's blind seat, flip 1, first of six: *"A uniform ~45 degree hatch overlay runs across the
entire lit floor ... it is screen-space, not surface texture."* Two instruments said the seat was
wrong — a lag autocorrelation found no 45 degree preference, a structure tensor put the dominant
orientation at the bond — and both were measuring the wrong thing: **a cross-hatch weave has
energy at every angle and no direction dominates.** §13.10 nearly ran the wrong way there, so this
instrument does not ask about ORIENTATION at all.

It asks about SPATIAL FREQUENCY, which is what a dither actually is. `refl = PolishByAge[fa]`
picks one of FOUR discrete reflectivities PER PIXEL from a noise-derived wear scalar, so the
polish term's value changes at almost every pixel step and ignores stone boundaries entirely.
Wear, lanes, dishing and grit all vary slowly across a stone face. **The flip rate separates them
and nothing else here does.**

THE POLISH TERM IS ISOLATED EXACTLY, not estimated: `delta = lum(polish_gain 1.0) -
lum(polish_gain 0.0)`, same scene, same station, same rig, same seed, one variable (§4.2).

    flip rate     share of horizontally adjacent pixel pairs INSIDE floor cells whose delta
                  differs by >= 1 delivered level. A four-way per-pixel stamp approaches the
                  share of pairs that straddle a class boundary; a lane does not.
    amplitude     mean and p95 of |delta| over the same population, in delivered levels — because
                  §13.9 measures on the delivered frame or it has not measured the asset.
    levels        distinct delta values present. Four discrete reflectivities under one falloff
                  produce a small, banded population.

HOW IT DEMONSTRATES IT CAN FAIL (§13.5). It is run on the PRE-FIX captures, which carry the
dither a frame critic culled, and on the post-fix ones. A number that does not separate those two
states is not measuring the artefact. The reference population — the diffuse floor's own
pixel-to-pixel flip rate, printed beside it — is the material this thing is supposed to look like:
an honest surface response flips no more often than the stone it sits on.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "tier1_walls"))
import light_field as LF          # noqa: E402
from mask_census import build     # noqa: E402

INSET = 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--on", required=True, help="capture with polish_gain 1.0 (png,log)")
    ap.add_argument("--off", required=True, help="capture with polish_gain 0.0 (png,log)")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--max-tiles", type=float, default=4.0,
                    help="lit band: the delivered reach of the ratified rig is ~4 tiles")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    wall, w, h = build(spec)
    px, py = spec["player"]["x"], spec["player"]["y"]

    def load(pair):
        png, log = pair.split(",")
        img = np.array(Image.open(os.path.join(REPO, png)).convert("RGB")).astype(float)
        return (img * LF.W709).sum(2), LF.read_grid(os.path.join(REPO, log))

    on, g1 = load(a.on)
    off, g0 = load(a.off)
    if g1 != g0:
        raise SystemExit("the two arms disagree about the engine's grid (§13.10)")
    delta = on - off

    flips = pairs = 0
    base_flips = base_pairs = 0
    amps = []
    vals = []
    for y in range(h):
        for x in range(w):
            if wall[y][x] or not LF.in_view(g1, x, y):
                continue
            if max(abs(x - px), abs(y - py)) <= 1:
                continue
            if np.hypot(x - px, y - py) > a.max_tiles:
                continue
            x0, y0, cw, ch = LF.cell_box(g1, x, y)
            sl = (slice(int(y0) + INSET, int(y0 + ch) - INSET),
                  slice(int(x0) + INSET, int(x0 + cw) - INSET))
            d, b = delta[sl], off[sl]
            if d.size == 0:
                continue
            flips += int((np.abs(np.diff(d, axis=1)) >= 1.0).sum())
            pairs += d.shape[0] * (d.shape[1] - 1)
            base_flips += int((np.abs(np.diff(b, axis=1)) >= 1.0).sum())
            base_pairs += b.shape[0] * (b.shape[1] - 1)
            amps.append(np.abs(d).ravel())
            vals.append(d.ravel())

    amp = np.concatenate(amps)
    val = np.concatenate(vals)
    out = dict(
        tag=a.tag, scene=a.scene, on=a.on, off=a.off, max_tiles=a.max_tiles,
        pixels=int(amp.size),
        flip_rate=flips / pairs if pairs else float("nan"),
        diffuse_flip_rate=base_flips / base_pairs if base_pairs else float("nan"),
        amplitude_mean=float(amp.mean()), amplitude_p95=float(np.percentile(amp, 95)),
        amplitude_max=float(amp.max()),
        distinct_levels=int(np.unique(np.round(val)).size),
    )
    print(f"=== polish dither — {a.tag} ===")
    print(f"   lit band <= {a.max_tiles} tiles, {out['pixels']} floor pixels")
    print(f"   flip rate, polish term     {out['flip_rate']:.4f}")
    print(f"   flip rate, diffuse floor   {out['diffuse_flip_rate']:.4f}   <- the material it sits on")
    print(f"   ratio                      {out['flip_rate'] / out['diffuse_flip_rate']:.3f}x")
    print(f"   amplitude mean / p95 / max {out['amplitude_mean']:.2f} / "
          f"{out['amplitude_p95']:.2f} / {out['amplitude_max']:.2f} levels")
    print(f"   distinct delta levels      {out['distinct_levels']}")
    if a.json_out:
        json.dump(out, open(os.path.join(REPO, a.json_out), "w"), indent=2)
    return out


if __name__ == "__main__":
    main()
