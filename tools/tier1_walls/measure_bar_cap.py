#!/usr/bin/env python3
"""HOW THE ASSET BAR BUILDS A WALL TOP — the one thing the recipe never measured.

RULED (Rafe, 2026-08-30): *"Measure the bar's top-band construction and add it to WALL-RECIPE
(we measured faces and ratios, never the cap)."*

`WALL-RECIPE.md` measured the bar's FACE across 23 tiles, its value stack, its proportions and its
shadow ramp. The top band it measured exactly once and only as a value — *"91.5% of those pixels
are literally 90"* — which was then read as *the top is flat* and cost a device gate when the flat
was delivered as a ruled grid (§8.3.1). The cap has never been measured as a CONSTRUCTION.

WHAT THIS ASKS, and each question is one the cap pass has to answer for Yarl:

    CONTINUITY    does the bar's cap run across tile boundaries, or restart at each one? Measured
                  as the value step across a shared edge between two horizontally adjacent wall
                  tiles, against the step between neighbouring columns inside one.
    FLATNESS      how much of the cap is one value, and how many values does it use at all.
    FIELD SCALE   does the cap carry anything larger than a tile - a drift, a crack, a stain -
                  measured as the spread of per-tile means across the wall tiles of one map.
    SEPARATION    cap against the floor it adjoins, in the bar's own uniformly-lit screenshot:
                  value, and hue.

MEASUREMENTS LEAVE; PIXELS NEVER DO (§13.3). This reads a licensed local library and writes
numbers. No bar pixel enters this repo, in any composite, reference or corpus, and the path being
known does not relax that by one pixel.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "sighted_round"))
import measure_bar as MB            # noqa: E402

OUT = os.path.join(HERE, "evidence", "BAR-CAP.json")


def rgb_of(ts, gid):
    t = ts.get(gid)
    if t is None or t.size == 0:
        return None
    if (t[..., 3] > 128).sum() < 200:
        return None
    return t[..., :3].astype(float)


def hue_sat(rgb):
    """Mean hue angle and saturation of a patch, in HSV terms, ignoring near-black."""
    mx = rgb.max(2)
    mn = rgb.min(2)
    keep = mx > 12
    if keep.sum() < 20:
        return None, None
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.zeros_like(mx)
    m = (mx == r)
    h[m] = ((g - b) / d)[m] % 6
    m = (mx == g)
    h[m] = ((b - r) / d + 2)[m]
    m = (mx == b)
    h[m] = ((r - g) / d + 4)[m]
    return float((h[keep] * 60).mean()), float(sat[keep].mean())


def main():
    MB.require_source()
    maps = sorted(f for f in os.listdir(MB.EXAMPLES) if f.endswith(".tmx"))

    # ⚠ EVERYTHING IS RESOLVED PER MAP, WITH THAT MAP'S OWN TILESET TABLE.
    #
    # The first version of this file accumulated every map's tilesets into one table and then
    # classified against the merged result. It returned ZERO top tiles where a per-map pass
    # returns 39, because `Tiles` resolves a gid by picking the highest `firstgid` at or below it
    # — so a gid from map A can land in map B's sheet once both are in the table. `measure_bar`'s
    # own docstring warns about exactly this: *a gid only means something within its own map.*
    # It failed loudly (an empty array) rather than quietly, which is the only reason it is a
    # footnote instead of a retraction.
    flat, levels, edge_steps, inner_steps, hues, sats, lums = [], [], [], [], [], [], []
    flum, fhue, fsat = [], [], []
    per_map, cap_tiles = [], 0

    for fn in maps:
        m = MB.load_tmx(os.path.join(MB.EXAMPLES, fn))
        ts = MB.Tiles(list(m["tilesets"]))

        def gids(name):
            rows = m["layers"].get(name) or []
            return sorted({g for r in rows for g in r if g})

        caps = []
        for g in gids("walls"):
            c = MB.classify(ts, g)
            if not c or c["kind"] != "TOP":
                continue
            t = ts.get(g)
            L = MB.lum(t)
            A = t[..., 3]
            v = L[A > 128]
            if v.size < 200:
                continue
            mode = float(np.bincount(np.round(v).astype(int)).argmax())
            flat.append(float((np.abs(v - mode) < 1.5).mean()))
            levels.append(int(len(np.unique(np.round(v)))))
            inner_steps.append(float(np.abs(np.diff(L.astype(float), axis=1)).mean()))
            rgb = rgb_of(ts, g)
            if rgb is not None:
                h, s_ = hue_sat(rgb)
                if h is not None:
                    hues.append(h)
                    sats.append(s_)
            lums.append(float(v.mean()))
            caps.append(float(v.mean()))
            cap_tiles += 1

        # CONTINUITY, MEASURED ON ACTUAL ADJACENT PLACEMENTS.
        #
        # ⚠ The first version compared a tile's own left column against its own right column,
        # which asks whether the tile WRAPS ONTO ITSELF - a different question, and one the bar
        # has no reason to answer yes to. What matters is whether two tiles the map actually puts
        # side by side agree at the boundary they share. Same numbers, completely different
        # claim, and the first one would have been reported as "the bar's cap restarts at every
        # tile" when the map had never been consulted.
        rows = m["layers"].get("walls") or []
        for y, row in enumerate(rows):
            for x in range(len(row) - 1):
                ga, gb = row[x], row[x + 1]
                if not ga or not gb:
                    continue
                ca, cb = MB.classify(ts, ga), MB.classify(ts, gb)
                if not ca or not cb or ca["kind"] != "TOP" or cb["kind"] != "TOP":
                    continue
                ta, tb = ts.get(ga), ts.get(gb)
                if ta is None or tb is None or ta.size == 0 or tb.size == 0:
                    continue
                la, lb = MB.lum(ta), MB.lum(tb)
                edge_steps.append(float(np.abs(la[:, -1].astype(float)
                                               - lb[:, 0].astype(float)).mean()))

        for g in gids("floor"):
            rgb = rgb_of(ts, g)
            if rgb is None:
                continue
            t = ts.get(g)
            flum.append(float(MB.lum(t)[t[..., 3] > 128].mean()))
            h, s_ = hue_sat(rgb)
            if h is not None:
                fhue.append(h)
                fsat.append(s_)

        if caps:
            per_map.append(dict(map=fn, n_top_tiles=len(caps),
                                mean=round(float(np.mean(caps)), 2),
                                spread=round(float(np.std(caps)), 2),
                                lo=round(float(np.min(caps)), 2),
                                hi=round(float(np.max(caps)), 2)))

    if not flat:
        raise SystemExit("no cap tiles classified - the bar's layer names or tilesets have moved")

    out = dict(
        produced_by="tools/tier1_walls/measure_bar_cap.py",
        source=MB.BAR_ROOT, note="measurements only; no bar pixel is in this repo (§13.3)",
        cap_tiles=cap_tiles,
        flatness=dict(modal_share_mean=round(float(np.mean(flat)), 4),
                      modal_share_min=round(float(np.min(flat)), 4),
                      distinct_levels_mean=round(float(np.mean(levels)), 2),
                      distinct_levels_max=int(np.max(levels))),
        continuity=dict(adjacent_pairs=len(edge_steps),
                        edge_step_mean=round(float(np.mean(edge_steps)), 3),
                        interior_step_mean=round(float(np.mean(inner_steps)), 3),
                        edge_over_interior=round(float(np.mean(edge_steps)
                                                       / max(np.mean(inner_steps), 1e-6)), 3)),
        field_scale=per_map,
        separation=dict(cap_lum=round(float(np.mean(lums)), 2),
                        floor_lum=round(float(np.mean(flum)), 2),
                        cap_over_floor=round(float(np.mean(lums) / max(np.mean(flum), 1e-6)), 4),
                        levels=round(float(np.mean(lums) - np.mean(flum)), 2),
                        cap_hue=round(float(np.mean(hues)), 1) if hues else None,
                        floor_hue=round(float(np.mean(fhue)), 1) if fhue else None,
                        hue_delta=round(float(np.mean(hues) - np.mean(fhue)), 1)
                        if hues and fhue else None,
                        cap_sat=round(float(np.mean(sats)), 4) if sats else None,
                        floor_sat=round(float(np.mean(fsat)), 4) if fsat else None),
    )
    json.dump(out, open(OUT, "w"), indent=2)

    print("THE BAR'S CAP — %d top tiles across %d example maps" % (cap_tiles, len(per_map)))
    print()
    print("  FLATNESS")
    print("    modal share      %.1f%% of cap pixels hold one value (worst tile %.1f%%)"
          % (out["flatness"]["modal_share_mean"] * 100, out["flatness"]["modal_share_min"] * 100))
    print("    distinct levels  %.1f mean, %d max"
          % (out["flatness"]["distinct_levels_mean"], out["flatness"]["distinct_levels_max"]))
    print()
    print("  CONTINUITY across a tile boundary the map ACTUALLY DRAWS (%d adjacent cap pairs)"
          % out["continuity"]["adjacent_pairs"])
    print("    edge step %.2f against an interior step of %.2f  ->  %.2fx"
          % (out["continuity"]["edge_step_mean"], out["continuity"]["interior_step_mean"],
             out["continuity"]["edge_over_interior"]))
    print()
    print("  FIELD SCALE — spread of per-tile cap means within one map")
    for r in per_map:
        print("    %-24s n=%2d  mean %6.2f  sd %5.2f  range %.0f..%.0f"
              % (r["map"], r["n_top_tiles"], r["mean"], r["spread"], r["lo"], r["hi"]))
    print()
    print("  SEPARATION from the floor it adjoins")
    s = out["separation"]
    print("    cap %.2f vs floor %.2f   ->  %.3fx, %+.1f levels"
          % (s["cap_lum"], s["floor_lum"], s["cap_over_floor"], s["levels"]))
    print("    hue  cap %s  floor %s  delta %s" % (s["cap_hue"], s["floor_hue"], s["hue_delta"]))
    print("    sat  cap %s  floor %s" % (s["cap_sat"], s["floor_sat"]))
    print()
    print("  wrote %s" % os.path.relpath(OUT, REPO))


if __name__ == "__main__":
    main()
