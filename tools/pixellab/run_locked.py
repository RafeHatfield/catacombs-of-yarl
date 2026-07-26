#!/usr/bin/env python3
"""Driver for burn-down 3's fresh (non-bank) palette-locked generation:
anvil, armor_stand, club, mushroom_cluster. One concept per invocation
(sys.argv[1]), small batches -- burn-down 2b found background generation
runs vulnerable to being killed under resource contention from concurrent
sessions sharing the same PixelLab account."""
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
os.chdir(REPO)
import warnings
warnings.filterwarnings("ignore")

from generate_candidates_locked import generate_concept_locked

CONCEPTS = {
    "anvil": dict(
        file_ids=[5001], asset_class="prop", final_size=24, exempt=False,
        prompt="blacksmith anvil with horn, heavy iron block",
        live_path="src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_5001.png"),
    "armor_stand": dict(
        file_ids=[5002], asset_class="prop", final_size=24, exempt=False,
        prompt="iron armor stand shaped like a headless torso mannequin",
        live_path="src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_5002.png"),
    "club": dict(
        file_ids=[4001], asset_class="item", final_size=16, exempt=False,
        prompt="wooden club weapon, thick knobbed end tapering to a handle",
        live_path="src/Presentation/assets/sprites_16bf/items_16x16/oryx_16bit_fantasy_items_4001.png"),
    "mushroom_cluster": dict(
        file_ids=[5109], asset_class="prop", final_size=24, exempt=False,
        prompt="cluster of pale mushrooms growing from a floor crack",
        live_path="src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_5109.png"),
}

LOG_PATH = "tools/art_lint/reports/burndown3_generation_log.csv"


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


def run_one(concept_name, target=6, max_attempts=15, seed_start=0):
    cfg = CONCEPTS[concept_name]
    result = generate_concept_locked(
        concept_name=concept_name, prompt=cfg["prompt"], file_ids=cfg["file_ids"],
        asset_class=cfg["asset_class"], final_size=cfg["final_size"], exempt=cfg["exempt"],
        live_path=cfg["live_path"], target=target, max_attempts=max_attempts, seed_start=seed_start,
    )
    for r in result["results"]:
        r["concept"] = concept_name
    append_log(result["results"])
    print(f"[{concept_name}] attempts={result['attempts']} passers={result['passers']}")
    return result


if __name__ == "__main__":
    concept = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    max_attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    seed_start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    run_one(concept, target, max_attempts, seed_start)
