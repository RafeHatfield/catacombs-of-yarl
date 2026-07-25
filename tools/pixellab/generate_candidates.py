#!/usr/bin/env python3
"""Burn-down 2b candidate generation harness.

For each concept: call PixelLab BitForge with a minimal, content-only prompt (no
style_image/color_image/init_image — never feeds Oryx pixels into the model, per
the license guard), downscale nearest-neighbor to final size, palette-snap, lint,
and — if the result fails only on A4 within reach — run the same extended
deep-collapse routine from burn-down 2a (up to 8 merges, aborting if A5/A6 would
fail at any step). Keeps generating seeds until `target` lint-passing candidates
exist or `max_attempts` is reached, whichever comes first — never relaxes the
pipeline to hit quota.

Deliberately does NOT pass outline/shading/detail/view/isometric/oblique_projection
kwargs or style_image — tools/pixellab/PIXELLAB_CONVENTIONS.md documents that
extensive in-repo testing (sweep.py) showed these degrade output quality, so the
color-budget/outline/shading conformance work is left entirely to the deterministic
pipeline below, not to prompt engineering.
"""
import csv
import json
import os
import random
import sys
import time
from itertools import combinations
from collections import Counter

REPO = "/Users/rafehatfield/development/c-yarl/.claude/worktrees/art-burndown-2b"
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
os.chdir(REPO)

import warnings
warnings.filterwarnings("ignore")

from PIL import Image
from client_compat import generate_image_bitforge
import importlib.util


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


snap_mod = load_module("snap_to_palette", "tools/art_lint/snap_to_palette.py")
lint_mod = load_module("art_lint", "tools/art_lint/art_lint.py")
palette = snap_mod.load_palette("config/art/oryx_master_palette.json")
palette_set = lint_mod.load_palette("config/art/oryx_master_palette.json")

FLOOR_BY_CLASS = {"world_tile": 8, "prop": 8, "decal": 8, "fx": 8, "item": 12, "creature": 16, "class": 16}
FAIL_ABOVE = {"world_tile": 10, "prop": 10, "decal": 10, "fx": 10, "item": 21, "creature": 18, "class": 18}
MAX_MERGES = 8
GEN_SIZE = {"width": 32, "height": 32}


def deep_collapse(im, asset_class, exempt):
    """Same algorithm as burn-down 2a: merge nearest in-sprite color pairs, checking
    A5/A6 before applying each merge, up to MAX_MERGES."""
    floor = FLOOR_BY_CLASS.get(asset_class, 8)
    fail_above = FAIL_ABOVE.get(asset_class, 10)
    pixels = list(im.getdata())
    merges = []
    step = 0
    while True:
        opaque = [(r, g, b) for (r, g, b, a) in pixels if a == 255]
        counts = Counter(opaque)
        colors = list(counts.keys())
        n_colors = len(colors)
        if n_colors <= fail_above:
            break
        if step >= MAX_MERGES or n_colors - 1 < floor:
            break
        best_pair, best_dist = None, None
        for c1, c2 in combinations(colors, 2):
            d = sum((a - b) ** 2 for a, b in zip(c1, c2))
            if best_dist is None or d < best_dist:
                best_dist, best_pair = d, (c1, c2)
        c1, c2 = best_pair
        rare, common = (c1, c2) if counts[c1] <= counts[c2] else (c2, c1)
        trial = [(common[0], common[1], common[2], a) if (r, g, b) == rare and a == 255 else (r, g, b, a)
                 for (r, g, b, a) in pixels]
        trial_im = Image.new("RGBA", im.size)
        trial_im.putdata(trial)
        trial_path = "/tmp/_deep_collapse_trial.png"
        trial_im.save(trial_path)
        trial_row = lint_mod.lint_file(trial_path, asset_class, palette_set, exempt)
        os.remove(trial_path)
        if trial_row["A5"] == "FAIL" or trial_row["A6"] == "FAIL":
            break
        pixels = trial
        step += 1
        merges.append({"step": step, "merged_from": rare, "merged_into": common})
    out = Image.new("RGBA", im.size)
    out.putdata(pixels)
    return out, merges


def pipeline_one(raw_img, final_size, asset_class, exempt, out_dir, tag):
    """Downscale -> snap -> lint -> deep-collapse if marginal. Returns (result_dict)."""
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, f"{tag}_raw32.png")
    raw_img.save(raw_path)

    down = raw_img.resize((final_size, final_size), Image.NEAREST)
    down_path = os.path.join(out_dir, f"{tag}_down.png")
    down.save(down_path)

    snapped_path = os.path.join(out_dir, f"{tag}_snapped.png")
    snap_result = snap_mod.snap_file(down_path, palette, snapped_path)
    if snap_result["status"] == "aborted":
        return {"tag": tag, "status": "aborted", "reason": snap_result["reason"], "final_path": None}

    row = lint_mod.lint_file(snapped_path, asset_class, palette_set, exempt)
    collapse_applied = 0
    if row["overall"] == "FAIL":
        fails_which = [k for k in ("A1", "A2", "A3", "A4", "A5", "A6") if row[k] == "FAIL"]
        if fails_which == ["A4"] or (set(fails_which) <= {"A4"}):
            im = Image.open(snapped_path).convert("RGBA")
            collapsed, merges = deep_collapse(im, asset_class, exempt)
            if merges:
                collapsed.save(snapped_path)
                row = lint_mod.lint_file(snapped_path, asset_class, palette_set, exempt)
                collapse_applied = len(merges)

    return {
        "tag": tag, "status": "ok", "final_path": snapped_path,
        "overall": row["overall"], "colors": row["A4_color_count"],
        "A5": row["A5"], "A6": row["A6"], "collapse_merges": collapse_applied,
    }


def generate_concept(concept_name, prompt, file_ids, asset_class, final_size,
                      exempt, target=6, max_attempts=20, seed_start=0):
    """Generate up to max_attempts raw seeds, pipeline each, stop at `target` passers."""
    out_dir = f"tools/art_lint/candidates/burndown2b/{concept_name}"
    os.makedirs(out_dir, exist_ok=True)
    results = []
    passers = []
    attempt = 0
    seed = seed_start
    while attempt < max_attempts and len(passers) < target:
        attempt += 1
        tag = f"{concept_name}_s{seed}"
        try:
            raw = generate_image_bitforge(prompt + ", small sprite, pixel art", GEN_SIZE, seed=seed)
        except Exception as e:
            results.append({"tag": tag, "status": "error", "reason": str(e)})
            seed += 1
            time.sleep(0.3)
            continue
        r = pipeline_one(raw, final_size, asset_class, exempt, out_dir, tag)
        r["seed"] = seed
        r["prompt"] = prompt
        results.append(r)
        if r["status"] == "ok" and r["overall"] in ("PASS", "WARN"):
            passers.append(r)
        seed += 1
        time.sleep(0.2)

    return {
        "concept": concept_name, "file_ids": file_ids, "attempts": attempt,
        "passers": len(passers), "results": results,
    }


if __name__ == "__main__":
    print("Import this module from a driver script; not meant to run standalone.")
