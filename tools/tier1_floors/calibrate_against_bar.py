#!/usr/bin/env python3
"""CALIBRATE `field_laws` AGAINST THE ASSET BAR. Measurements leave; pixels never do.

THE QUESTION THIS RUN EXISTS TO ANSWER
--------------------------------------
`field_laws.incident_and_frame` flags every component CONTAINED in one cell as an incident,
on §8.3.1's own words — *where does it sit, and does it sit there every time.* Run against a
legal, hand-built, wrapping, irregular flagstone bond, it flagged four components of 126-160 px:
**the stone faces themselves.**

That is either the instrument being right and the fixture being illegal (a bond whose stones sit
wholly inside the cell IS the seat's verbatim cull — *"the identical bracket-shaped stone sits
at the identical position inside every single cell"*), or the instrument over-firing on large
regions of ordinary material. **Nothing about the clause decides between those two**, and
choosing by taste is how a threshold becomes a preference wearing a number.

§13.6 LOCKED says where to look instead: *where a constant must be calibrated, derive it from
the corpus already accepted, never from the work seeking acceptance.* Yarl has no accepted floor
corpus — this session is the project's first landing gate. **The asset bar is the accepted
corpus that exists**: a shipped, commercial, professionally drawn floor set that §13.3 names as
the standard a Yarl asset must meet or beat.

So: run the identical instrument over the bar's own floor tiles and read what a floor set that
DOES ship actually does about containment.

WHAT THIS IS NOT
----------------
§13.3's origination rule — LAW: *the bar may occasion a law; only the register may justify one.
A proposed rule whose only justification is "the bar does it" is conformance and is refused.*

**No law is proposed here and none is taken from the bar.** §8.3 is already RULED, with its
register derivation written (repetition converts accident into intent; §1's *nothing is staged*
broken by arithmetic). What is taken from the bar is the OPERATING POINT of a mechanical screen
— which §13.6 explicitly directs to the accepted corpus and which has nowhere else to come from.
The distinction is the one the sighted round's recipe already drew: the bar supplies numbers,
the register supplies reasons, and a number without a reason is FLAGGED rather than adopted.

MEASUREMENTS LEAVE; PIXELS NEVER DO — §13.3, LAW.
`measure_bar.py` is the pattern and its machinery is imported rather than re-written. This module
writes a JSON table of statistics and NOTHING ELSE. No bar pixel is written to this repo, in any
composite, reference, or corpus, and the known path does not relax that by one pixel.

⚠ AND THE FLOOR TILES ARE 48px WHERE YARL'S ARE 32px. That is a real difference and it is not
smoothed over: absolute pixel counts are reported BOTH raw and as a fraction of the tile's own
area, and only the fraction is used for anything, because a fraction is the quantity that
survives the scale change. Stated here rather than discovered later.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools/sighted_round"))
import field_laws as FL       # noqa: E402
import measure_bar as MB      # noqa: E402

OUT = os.path.join(HERE, "bar_calibration.json")


def bar_floor_tiles():
    """The bar's floor tiles, read through each map's OWN tileset table.

    A GID ONLY MEANS SOMETHING AGAINST THE TABLE OF THE MAP THAT WROTE IT, and the first version
    of this function forgot it. It accumulated `tilesets[firstgid] = ts` across all six maps, and
    the sixth — `uf_map_example.tmx`, the overworld — declares **firstgid 1 pointing at
    `uf_map.png`**, a different sheet from the `uf_terrain.png` every other map declares at the
    same firstgid. Sorting last by name, it overwrote the entry for every gid below 1651.

    The symptom was every floor tile reading 14-89% opaque, which cannot be true of a floor; the
    same gids read 1.000 opaque by direct indexing into the terrain sheet. `bar_sheet_probe.py`
    and `bar_resolver_probe.py` are the two runs that separated those, and they are kept.

    ⚠ CHECKED, BECAUSE IT WOULD HAVE BEEN THE MORE SERIOUS FINDING: `measure_bar.py` DOES NOT
    have this bug, and `bar_measurements.json` is unaffected. It `continue`s past any map with no
    walls layer BEFORE accumulating that map's tilesets, so the overworld never enters its table.
    §6.5's value stack — the bible's load-bearing law, and WALL-RECIPE.md's six adopted numbers —
    stand exactly as measured.

    ⚠ BUT THE GUARD THAT SAVED IT IS INCIDENTAL, AND THAT IS ITS OWN FINDING (LOOP-PROCESS §4.2).
    `measure_bar` skips the overworld because *"it cannot answer a wall question"* — a reason
    about layers, not about gid resolution. `Tiles` keys its table on firstgid alone and will
    silently resolve against whichever sheet was written last; nothing in it goes red when two
    sheets share a firstgid. Any future reuse that does not happen to need a walls layer inherits
    the mis-resolution, silently, exactly as §4.2 predicts: *a claim in a docstring with no
    enforcement behind it, discovered later and somewhere else.*

    This function therefore does not rely on a guard at all. It resolves each map's floor gids
    against that map's own tilesets and never builds a shared table, so the collision cannot
    occur; and it ALSO asserts the collision explicitly, so that if the library changes under it
    the failure is loud.
    """
    if not MB.require_source():
        raise SystemExit(2)
    import collections
    maps = sorted(f for f in os.listdir(MB.EXAMPLES) if f.endswith(".tmx"))
    by_key, usage, collisions = {}, collections.Counter(), []
    seen_firstgid = {}
    for fn in maps:
        m = MB.load_tmx(os.path.join(MB.EXAMPLES, fn))
        for ts in m["tilesets"]:
            prev = seen_firstgid.get(ts["firstgid"])
            if prev and prev != ts["image"]:
                collisions.append(dict(firstgid=ts["firstgid"], map=fn,
                                       sheets=sorted({os.path.basename(prev),
                                                      os.path.basename(ts["image"])})))
            seen_firstgid[ts["firstgid"]] = ts["image"]
        lay = m["layers"]
        key = next((k for k in lay if k.lower().startswith("floor")), None)
        if key is None:
            continue
        res = MB.Tiles(list(m["tilesets"]))        # THIS map's table, never a shared one
        for row in lay[key]:
            for gid in row:
                if not gid:
                    continue
                a = res.get(gid)
                if a is None or not a.size or a.shape[0] != a.shape[1]:
                    continue
                sheet = next(s["image"] for s in res.sets if gid >= s["firstgid"])
                k = (os.path.basename(sheet), int(gid))
                usage[k] += 1
                if k not in by_key:
                    by_key[k] = np.asarray(a).astype(float)

    out, rejected = [], []
    for k, arr in sorted(by_key.items()):
        # A floor tile is opaque by definition — §8.3's base tile is the material under
        # everything. A sheet cell that is not is either padding or not a floor, and it is
        # REPORTED as excluded rather than silently dropped.
        opaque = float((arr[..., 3] > 128).mean())
        if opaque < 0.99:
            rejected.append(dict(sheet=k[0], gid=k[1], map_cells=int(usage[k]),
                                 opaque_fraction=round(opaque, 4),
                                 why="not opaque: padding, or not a floor tile"))
            continue
        out.append((k, int(usage[k]), arr[..., :3]))
    return maps, out, rejected, collisions


def main():
    maps, tiles, rejected, collisions = bar_floor_tiles()
    print("CALIBRATION AGAINST THE ASSET BAR — measurements only, no pixel leaves the library")
    print("source: %s" % MB.BAR_ROOT)
    print("maps:   %d   floor gids kept: %d   excluded as non-opaque: %d"
          % (len(maps), len(tiles), len(rejected)))
    for r in rejected:
        print("    excluded %s gid %-5d opaque=%.3f  (%s)"
              % (r["sheet"], r["gid"], r["opaque_fraction"], r["why"]))
    for c in collisions:
        print("    ⚠ FIRSTGID COLLISION in the library: firstgid %d names %s (seen in %s). "
              "Resolution is per-map here, so this is recorded, not fatal."
              % (c["firstgid"], " and ".join(c["sheets"]), c["map"]))
    print("")
    if not tiles:
        raise SystemExit("REFUSING: no opaque floor tile survived. An empty calibration table is "
                         "a silent no-op (LOOP-PROCESS §4.2), not a result.")

    rows = []
    print("  %-8s %6s %5s %7s %7s %8s %8s %6s %6s"
          % ("gid", "cells", "cell", "seam_x", "seam_y", "maxCont", "frac", "nInc", "codes"))
    for (sheet, gid), n, rgb in tiles:
        t = rgb.shape[0]
        inc, fr = FL.incident_and_frame(rgb, t=t)
        sm = FL.seam(rgb)
        gr = FL.grid(rgb)
        area = float(t * t)
        biggest = max([i["px"] for i in inc], default=0)
        codes = []
        if fr:
            codes.append("FRAME")
        if sm["seamed"]:
            codes.append("SEAM")
        if gr:
            codes.append("GRID")
        rows.append(dict(sheet=sheet, gid=int(gid), map_cells=n, cell=t,
                         seam_ratio=[sm["ratio_x"], sm["ratio_y"]],
                         wrap=[sm["wrap_x"], sm["wrap_y"]],
                         interior_p95=[sm["interior_p95_x"], sm["interior_p95_y"]],
                         n_contained=len(inc),
                         contained_px=sorted((i["px"] for i in inc), reverse=True)[:8],
                         max_contained_px=biggest,
                         max_contained_frac=round(biggest / area, 4),
                         contained_frac=[round(i["px"] / area, 4) for i in
                                         sorted(inc, key=lambda r: -r["px"])[:8]],
                         max_contrast=max([i["contrast"] for i in inc], default=0.0),
                         n_frames=len(fr), n_grid=len(gr), other_codes=codes))
        print("  %-8d %6d %5d %7.2f %7.2f %8d %8.3f %6d %6s"
              % (gid, n, t, sm["ratio_x"], sm["ratio_y"], biggest, biggest / area,
                 len(inc), "+".join(codes) or "-"))

    fracs = sorted(r["max_contained_frac"] for r in rows)
    seams = sorted(max(r["seam_ratio"]) for r in rows)
    summary = dict(
        n_floor_tiles=len(rows),
        max_contained_frac=dict(
            min=fracs[0], p50=float(np.percentile(fracs, 50)),
            p90=float(np.percentile(fracs, 90)), max=fracs[-1],
            n_zero=sum(1 for f in fracs if f == 0.0)),
        seam_ratio=dict(min=seams[0], p50=float(np.percentile(seams, 50)),
                        p90=float(np.percentile(seams, 90)), max=seams[-1]),
        n_with_frame=sum(1 for r in rows if r["n_frames"]),
        n_with_grid=sum(1 for r in rows if r["n_grid"]),
        n_seamed_at_current_threshold=sum(1 for r in rows
                                          if max(r["seam_ratio"]) > FL.MAX_SEAM_RATIO))
    print("\n-- WHAT A SHIPPING FLOOR SET ACTUALLY DOES --")
    print("  largest CONTAINED component, as a fraction of its own tile:")
    print("     min %.3f   median %.3f   p90 %.3f   max %.3f   (tiles with none: %d of %d)"
          % (summary["max_contained_frac"]["min"], summary["max_contained_frac"]["p50"],
             summary["max_contained_frac"]["p90"], summary["max_contained_frac"]["max"],
             summary["max_contained_frac"]["n_zero"], len(rows)))
    print("  seam ratio (wrap step / interior p95 step):")
    print("     min %.2f   median %.2f   p90 %.2f   max %.2f"
          % (summary["seam_ratio"]["min"], summary["seam_ratio"]["p50"],
             summary["seam_ratio"]["p90"], summary["seam_ratio"]["max"]))
    print("  tiles the CURRENT seam threshold (%.1f) would call SEAMED: %d of %d"
          % (FL.MAX_SEAM_RATIO, summary["n_seamed_at_current_threshold"], len(rows)))
    print("  tiles carrying a FRAME: %d    a GRID: %d" % (summary["n_with_frame"],
                                                          summary["n_with_grid"]))

    res = dict(source=MB.BAR_ROOT, maps=maps, commit=FL.git_commit(),
               instrument=os.path.relpath(FL.__file__, REPO),
               instrument_sha256=FL.sha256_file(FL.__file__),
               note=("Statistics only. No bar pixel is written by this module or by anything it "
                     "calls. Bar tiles are 48px against Yarl's 32px, so only FRACTIONS are "
                     "carried forward."),
               summary=summary, tiles=rows, excluded=rejected,
               firstgid_collisions=collisions)
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
