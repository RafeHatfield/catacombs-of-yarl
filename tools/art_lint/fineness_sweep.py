#!/usr/bin/env python3
"""Sweep every generated-origin manifest entry against the Structural-fineness thresholds (§AF).

Scores each of the four fineness metrics (F1–F4) against the canon-derived per-class thresholds,
assigns a per-metric verdict (PASS / WARN>p90 / FAIL>max), and ranks all entries by total
deviation from canon norms so the worst-offending "too fine" assets sort to the top.

Deviation score = sum over the four metrics of (value / canon_p90_for_class) — 1.0 per metric means
"exactly at the WARN line", so a total near 4.0 is canon-typical and higher is finer-than-canon.
Ranks the whole inventory; the strips (fineness_strips.py) then pull everything above WARN.

Emits tools/art_lint/reports/fineness_sweep.csv (ranked, worst-first).
"""
import csv
import json
import os

from PIL import Image

import fineness_metrics as fm

MANIFEST = "config/art/generated_assets_manifest.json"
THRESHOLDS = "tools/art_lint/fineness_thresholds.json"
OUT = "tools/art_lint/reports/fineness_sweep.csv"
ADVISORY_METRIC = "edge_density"  # F4 demoted to advisory (Rafe 2026-08) — reported, never gates


def sheet_class(path):
    if "/world_24x24/" in path:
        return "world_24x24"
    if "/items_16x16/" in path:
        return "items_16x16"
    if "/creatures_24x24/" in path:
        return "creatures_24x24"
    return "world_24x24"


def verdict(value, warn, fail):
    if value > fail:
        return "FAIL"
    if value > warn:
        return "WARN"
    return "PASS"


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    th = json.load(open(THRESHOLDS))
    manifest = json.load(open(MANIFEST))

    rows = []
    for e in manifest["entries"]:
        path = e["path"]
        if not os.path.exists(path):
            continue
        cls = sheet_class(path)
        ct = th[cls]
        m = fm.compute(Image.open(path).convert("RGBA"))
        fid = path.split("_")[-1].replace(".png", "")

        per_metric = {}
        total = 0.0
        worst_metric, worst_ratio = None, 0.0
        for metric in fm.METRICS:
            v = m[metric]
            warn = ct[metric]["warn_p90"]
            fail = ct[metric]["fail_max"]
            per_metric[metric] = v
            # F4 edge_density DEMOTED to advisory (Rafe ruling 2026-08): reported, never gates.
            if metric == ADVISORY_METRIC:
                per_metric[metric + "_verdict"] = "ADVISORY"
                continue
            per_metric[metric + "_verdict"] = verdict(v, warn, fail)
            ratio = v / warn if warn else (0.0 if v == 0 else float("inf"))
            total += ratio
            if ratio > worst_ratio:
                worst_ratio, worst_metric = ratio, metric

        gating = [mm for mm in fm.METRICS if mm != ADVISORY_METRIC]
        any_warn = any(per_metric[mm + "_verdict"] in ("WARN", "FAIL") for mm in gating)
        any_fail = any(per_metric[mm + "_verdict"] == "FAIL" for mm in gating)
        rows.append({
            "id": fid, "class": cls, "game_key": e.get("game_key"),
            "conformance_status": e.get("conformance_status"), "route": e.get("route"),
            **per_metric,
            "deviation_score": round(total, 3),
            "worst_metric": worst_metric,
            "fineness_verdict": "FAIL" if any_fail else ("WARN" if any_warn else "PASS"),
            "path": path,
        })

    rows.sort(key=lambda r: -r["deviation_score"])
    fields = (["rank", "id", "class", "game_key", "conformance_status", "route"]
              + [c for m in fm.METRICS for c in (m, m + "_verdict")]
              + ["deviation_score", "worst_metric", "fineness_verdict", "path"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            r["rank"] = i
            w.writerow(r)

    n_warn = sum(1 for r in rows if r["fineness_verdict"] in ("WARN", "FAIL"))
    n_fail = sum(1 for r in rows if r["fineness_verdict"] == "FAIL")
    print(f"swept {len(rows)} entries -> {OUT}")
    print(f"  above WARN (any metric): {n_warn}   of which FAIL (>canon max): {n_fail}")
    print("  worst 12:")
    for r in rows[:12]:
        print(f"    #{r['rank']:2d} id={r['id']:5} {r['class']:14} {r['fineness_verdict']:4} "
              f"dev={r['deviation_score']:.2f} worst={r['worst_metric']} "
              f"(spk={r['speckle']} sc={r['small_clusters']} cr={r['color_regions']} ed={r['edge_density']}) "
              f"key={r['game_key']} status={r['conformance_status']}")


if __name__ == "__main__":
    main()
