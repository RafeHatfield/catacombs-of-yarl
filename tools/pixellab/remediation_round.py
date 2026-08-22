#!/usr/bin/env python3
"""Track A gate-remediation generation (chairs, candelabra).

Both concepts were gate-rejected in PR #101. Bank-first was checked first:
- chairs: tables_stools bank holds only grey/pale-topped STOOLS, which carry the same
  warm-vs-cool palette clash against table 5053 that got the chairs rejected -> no real
  choice, so a fresh palette-locked round with the swatch built from table 5053's OWN colors
  (not the rejected chairs') is run here.
- candelabra: see comment in run_candelabra.

Swatch source is passed via live_path (generate_concept_locked builds the color_image lock
from it). One concept per invocation. Palette-locked, same discipline as burn-down 3.
"""
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
os.chdir(REPO)
import warnings
warnings.filterwarnings("ignore")

from generate_candidates_locked import generate_concept_locked

WORLD = "src/Presentation/assets/sprites_16bf/world_24x24"

CONCEPTS = {
    # Chairs must read as a SET with table 5053 -> swatch from 5053's warm-wood palette.
    "chair_remediation": dict(
        file_ids=[5051, 5056, 5057], asset_class="prop", final_size=24, exempt=False,
        prompt="a simple wooden chair with a tall plank backrest and four sturdy legs, side view",
        live_path=f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
    # Candelabra: simple silhouette only (new rubric Part B item 7) -> swatch from the live
    # rejected candelabra's own palette (it was rejected for readability, not colour).
    "candelabra_remediation": dict(
        file_ids=[5080, 5081], asset_class="prop", final_size=24, exempt=False,
        prompt="a candelabra: a single upright stand with two arms and three lit candle flames, "
               "simple clear silhouette, nothing else",
        live_path=f"{WORLD}/oryx_16bit_fantasy_world_5080.png"),
}

LOG_PATH = "tools/art_lint/reports/remediation_generation_log.csv"


def append_log(rows):
    fields = ["concept", "tag", "seed", "prompt", "status", "overall", "colors",
              "A5", "A6", "collapse_merges", "final_path"]
    exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def run_one(name, target=6, max_attempts=16, seed_start=0):
    cfg = CONCEPTS[name]
    res = generate_concept_locked(
        concept_name=name, prompt=cfg["prompt"], file_ids=cfg["file_ids"],
        asset_class=cfg["asset_class"], final_size=cfg["final_size"], exempt=cfg["exempt"],
        live_path=cfg["live_path"], target=target, max_attempts=max_attempts, seed_start=seed_start)
    for r in res["results"]:
        r["concept"] = name
    append_log(res["results"])
    print(f"[{name}] attempts={res['attempts']} passers={res['passers']}")
    return res


if __name__ == "__main__":
    name = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    max_attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    seed_start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    run_one(name, target, max_attempts, seed_start)
