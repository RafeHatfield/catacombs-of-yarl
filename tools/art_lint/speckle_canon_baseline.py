#!/usr/bin/env python3
"""Emit the A7 speckle distribution for the canonical Oryx sample.

Covers every canonical (non-generated) file in world_24x24 (id < 5000,
excluding the id-3001 orphan), creatures_24x24, and items_16x16 (id < 4001)
— i.e. the exact same canonical set used by extract_master_palette.py. This
is the full canonical population, not a re-sample, so it is reproducible
without a new sampling decision. A7 is report-only per the lint spec: this
script does not propose or apply a threshold, only collects the distribution
so one can be ruled later.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from art_lint import count_speckle
from PIL import Image

from extract_master_palette import (
    ID_RE, WORLD_EXTRA_EXCLUDED_IDS, iter_id_filtered_pngs, iter_all_pngs,
)


def main():
    world_paths, _ = iter_id_filtered_pngs(
        "src/Presentation/assets/sprites_16bf/world_24x24", 5000, WORLD_EXTRA_EXCLUDED_IDS)
    creatures_paths = iter_all_pngs("src/Presentation/assets/sprites_16bf/creatures_24x24")
    items_paths, _ = iter_id_filtered_pngs(
        "src/Presentation/assets/sprites_16bf/items_16x16", 4001)

    rows = []
    for label, paths in [("world_24x24", world_paths), ("creatures_24x24", creatures_paths),
                          ("items_16x16", items_paths)]:
        for p in paths:
            im = Image.open(p).convert("RGBA")
            speckle = count_speckle(im)
            rows.append({"file": p, "class": label, "speckle_count": speckle})

    out_path = "tools/art_lint/speckle_canon_baseline.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "class", "speckle_count"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path}: {len(rows)} files")
    for label in ("world_24x24", "creatures_24x24", "items_16x16"):
        vals = sorted(r["speckle_count"] for r in rows if r["class"] == label)
        n = len(vals)
        median = vals[n // 2] if n else 0
        print(f"  {label}: n={n} median={median} max={max(vals) if vals else 0} "
              f"mean={sum(vals)/n:.2f}" if n else f"  {label}: n=0")


if __name__ == "__main__":
    main()
