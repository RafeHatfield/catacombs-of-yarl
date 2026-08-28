#!/usr/bin/env python3
"""THE SCREEN — every child of the yield run, mechanically, through both instruments.

    ring     `../../floor_remediation/ring_instrument.py`, CONSTANTS UNTOUCHED. Shelled out to
             as a subprocess rather than imported, so this module cannot monkeypatch a
             threshold even by accident, and its `--controls` suite is run in the same
             invocation — bible §13.5, its passes do not count until it has demonstrated it can
             fail, on every run, not once.
    census   `census.py`, this session's, certified by its own control suite (which caught its
             own first draw; see that file's docstring).

Then the arithmetic against the declared baseline, with the exact one-sided Fisher rather than
an eyeballed gap — the same test `parent_rate_summary.py` used to establish the baseline, so
the two numbers are computed the same way. `fisher_less` below is that function, reimplemented
rather than imported for the same reason the ring instrument is shelled out to.

WHAT THIS FILE MAY AND MAY NOT CONCLUDE
---------------------------------------
It may report rates and p-values. It may NOT conclude adoption: the bar in AUDIT-RD.md has
three limbs and two of them (the blind A/B, and Rafe's ruling) are not mechanical. A screen is
a floor, not a verdict — Rafe's own relabelling of the ring instrument governs here too:
MEASURED ERROR IN BOTH DIRECTIONS; ORDERS ATTENTION, RULES NOTHING.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RING = os.path.join(REPO, "tools/floor_remediation/ring_instrument.py")
CENSUS = os.path.join(HERE, "census.py")
OUT = os.path.join(HERE, "screen_out")

BASELINE = {"instrument": (5, 20), "seat_adjusted": (9, 20),
            "source": "REPORT-PARENT-RATE.md §2 — C-GAB line on BitForge, CONDITIONED"}


def fisher_less(a, n1, b, n2):
    """One-sided P(X <= a) for group 1's ringed count, hypergeometric. No scipy.
    Identical in form to `parent_rate_summary.fisher_less`, so the RD-vs-BitForge p is computed
    by the same arithmetic that produced the baseline's own p-values."""
    N, K = n1 + n2, a + b
    return sum(comb(K, x) * comb(N - K, n1 - x) / comb(N, n1)
               for x in range(0, a + 1) if 0 <= n1 - x <= N - K)


def run_ring(files, out_json):
    """Shell out. `--controls` is NOT optional here: the instrument re-proves it can fail on
    every screening run, and a control-suite failure aborts the screen rather than being
    reported alongside its findings."""
    cmd = [sys.executable, RING, "--controls", "--json", out_json] + files
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-3000:] if r.stdout else "")
    if r.returncode != 0:
        raise SystemExit("STOP — ring_instrument.py's own control suite did not pass. Its "
                         "findings are void, not discounted (LOOP-PROCESS §4).\n" + r.stderr[-2000:])
    return json.load(open(out_json))


def run_census(files, out_json, plates):
    cmd = [sys.executable, CENSUS, "--controls", "--json", out_json, "--plates", plates] + files
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-4000:] if r.stdout else "")
    if r.returncode != 0:
        raise SystemExit("STOP — census.py's control suite did not pass.\n" + r.stderr[-2000:])
    return json.load(open(out_json))


def cell_of(path):
    b = os.path.basename(path)
    return b.split("_")[0] if b[:1] in ("N", "T") else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yield-dir", default=os.path.join(HERE, "yield_out"))
    ap.add_argument("--json", default=os.path.join(OUT, "SCREEN.json"))
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    files = sorted(glob.glob(os.path.join(a.yield_dir, "cell_*", "*.png")))
    if not files:
        raise SystemExit("No children in %s — run yield_run.py first." % a.yield_dir)
    print("screening %d children\n" % len(files))

    ring = run_ring(files, os.path.join(OUT, "ring.json"))
    cen = run_census(files, os.path.join(OUT, "census.json"),
                     os.path.join(OUT, "plates"))

    by_file = {}
    for r in ring.get("files", {}).get("rows", ring.get("files", [])) or []:
        if isinstance(r, dict) and r.get("file"):
            by_file.setdefault(os.path.basename(r["file"]), {})["ring"] = r
    for r in cen.get("census", []):
        by_file.setdefault(os.path.basename(r["file"]), {})["census"] = r

    rows, cells = [], {}
    for f in files:
        b = os.path.basename(f)
        e = by_file.get(b, {})
        ringed = (e.get("ring", {}).get("verdict") == "RING")
        row = {"file": b, "cell": cell_of(f), "ringed": ringed,
               "seam": e.get("census", {}).get("SEAM"),
               "vignette": e.get("census", {}).get("VIGNETTE"),
               "census_pass": e.get("census", {}).get("PASS")}
        rows.append(row)
        c = cells.setdefault(row["cell"], {"n": 0, "ring": 0, "seam": 0, "vig": 0, "pass": 0})
        c["n"] += 1
        c["ring"] += bool(ringed)
        c["seam"] += bool(row["seam"])
        c["vig"] += bool(row["vignette"])
        c["pass"] += bool(row["census_pass"])

    pooled_ring = sum(c["ring"] for c in cells.values())
    pooled_n = sum(c["n"] for c in cells.values())

    print("\n%-6s %4s %6s %6s %6s %8s" % ("cell", "n", "ringed", "seam", "vignette", "census"))
    for k in sorted(cells):
        c = cells[k]
        print("%-6s %4d %6d %6d %6d %8d" % (k, c["n"], c["ring"], c["seam"], c["vig"], c["pass"]))
    print("%-6s %4d %6d" % ("POOL", pooled_n, pooled_ring))

    comp = {}
    for name, (b, bn) in BASELINE.items():
        if name == "source":
            continue
        comp[name] = {"baseline": "%d/%d" % (b, bn),
                      "rd": "%d/%d" % (pooled_ring, pooled_n),
                      "p_rd_lower": round(fisher_less(pooled_ring, pooled_n, b, bn), 6)}
    print("\nvs baseline (%s)" % BASELINE["source"])
    for k, v in comp.items():
        print("  %-14s RD %s vs BitForge %s   one-sided p(RD lower) = %s"
              % (k, v["rd"], v["baseline"], v["p_rd_lower"]))

    # The seamless flag on its own axis: cells N and T differ in nothing but tile_x/tile_y.
    if "N" in cells and "T" in cells:
        n, t = cells["N"], cells["T"]
        p_flag = fisher_less(t["seam"], t["n"], n["seam"], n["n"])
        print("\ntile_x/tile_y on its own axis (§4.1): seam %d/%d with the flag vs %d/%d without"
              "   one-sided p(flag lower) = %.6f" % (t["seam"], t["n"], n["seam"], n["n"], p_flag))
        comp["tiling_flag"] = {"with": "%d/%d" % (t["seam"], t["n"]),
                               "without": "%d/%d" % (n["seam"], n["n"]),
                               "p_flag_lower": round(p_flag, 6)}

    out = {"n": pooled_n, "cells": cells, "pooled_ringed": pooled_ring,
           "baseline": BASELINE, "comparisons": comp, "rows": rows,
           "ring_controls_passed": True, "census_controls_passed": True,
           "NOTE": "A screen orders attention and rules nothing. Adoption needs the blind A/B "
                   "and Rafe's ruling; see AUDIT-RD.md."}
    json.dump(out, open(a.json, "w"), indent=1, sort_keys=True)
    print("\n-> %s" % os.path.relpath(a.json, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
