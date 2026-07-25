#!/usr/bin/env python3
"""Driver: runs generate_concept() for every burn-down 2b concept, writes the
master candidate log CSV. Run one concept at a time via sys.argv[1] (concept key)
so a single long-running batch never risks losing everything to one bad exception.
"""
import csv
import json
import os
import sys

REPO = "/Users/rafehatfield/development/c-yarl/.claude/worktrees/art-burndown-2b"
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
os.chdir(REPO)
import warnings
warnings.filterwarnings("ignore")

from generate_candidates import generate_concept

# file_ids: single concepts have 1 id; variant-group concepts have 2 (candidate pairs
# are formed downstream from passers, not generated as literal pairs per call).
CONCEPTS = {
    "club":            dict(file_ids=[4001], asset_class="item", final_size=16, exempt=False,
                             prompt="wooden club weapon, thick knobbed end tapering to a handle"),
    "anvil":           dict(file_ids=[5001], asset_class="prop", final_size=24, exempt=False,
                             prompt="blacksmith anvil with horn, heavy iron block"),
    "armor_stand":     dict(file_ids=[5002], asset_class="prop", final_size=24, exempt=False,
                             prompt="iron armor stand shaped like a headless torso mannequin"),
    "forge":           dict(file_ids=[5011], asset_class="prop", final_size=24, exempt=False,
                             prompt="stone blacksmith forge furnace with firebox and coals"),
    "globe":           dict(file_ids=[5012], asset_class="prop", final_size=24, exempt=False,
                             prompt="brass celestial globe on a wooden stand"),
    "table":           dict(file_ids=[5053], asset_class="prop", final_size=24, exempt=False,
                             prompt="simple crude wooden table"),
    "desk":            dict(file_ids=[5063], asset_class="prop", final_size=24, exempt=False,
                             prompt="wooden writing desk with papers on top"),
    "pillar":          dict(file_ids=[5094], asset_class="prop", final_size=24, exempt=False,
                             prompt="stone pillar column"),
    "mushroom_cluster":dict(file_ids=[5109], asset_class="prop", final_size=24, exempt=False,
                             prompt="cluster of pale mushrooms growing from a floor crack"),
    "candelabra":      dict(file_ids=[5080, 5081], asset_class="prop", final_size=24, exempt=False,
                             prompt="ornate iron candelabra with lit candles"),
    "workbench":       dict(file_ids=[5082, 5083], asset_class="prop", final_size=24, exempt=False,
                             prompt="scarred wooden workbench with tools and stains"),
    "water_barrel":    dict(file_ids=[5084, 5085], asset_class="prop", final_size=24, exempt=False,
                             prompt="wooden barrel filled with visible water"),
    "shelf_bottles":   dict(file_ids=[5099, 5101], asset_class="prop", final_size=24, exempt=False,
                             prompt="wooden shelf lined with glass bottles"),
    "rock":            dict(file_ids=[5104, 5105], asset_class="prop", final_size=24, exempt=False,
                             prompt="large loose boulder rock"),
}

LOG_PATH = "tools/art_lint/reports/burndown2b_generation_log.csv"


def append_log(rows):
    fieldnames = ["concept", "tag", "seed", "prompt", "status", "overall", "colors",
                  "A5", "A6", "collapse_merges", "final_path"]
    exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def run_one(concept_name, target=6, max_attempts=20, seed_start=0):
    cfg = CONCEPTS[concept_name]
    result = generate_concept(
        concept_name=concept_name, prompt=cfg["prompt"], file_ids=cfg["file_ids"],
        asset_class=cfg["asset_class"], final_size=cfg["final_size"], exempt=cfg["exempt"],
        target=target, max_attempts=max_attempts, seed_start=seed_start,
    )
    for r in result["results"]:
        r["concept"] = concept_name
    append_log(result["results"])
    print(f"[{concept_name}] attempts={result['attempts']} passers={result['passers']}")
    return result


if __name__ == "__main__":
    concept = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    max_attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    seed_start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    run_one(concept, target, max_attempts, seed_start)
