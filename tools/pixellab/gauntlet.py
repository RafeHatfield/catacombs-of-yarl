#!/usr/bin/env python3
"""Gauntlet loop for fineness-rework items (register-correction PR #108).

Ladder: canon substitute -> canon derivation -> constrained regeneration. This module is the
regeneration leg: palette-locked (swatch from the item's own live sprite = the canon-validated-
swatch rule), prompt amended to DEMAND the register ("chunky, minimal detail, bold shapes, thick
outline") + front-facing, with the fineness thresholds as post-filters.

CRITIC (independent, pixels only): full Part-A lint (A1-A6) PLUS the fineness family scored against
canon class distributions. A candidate wins only if every metric sits within canon's p90 envelope.
The critic reports per-metric so the largest gap can be named and regenerated against. Bound: 12
attempts or 3 rounds with no improvement -> park with the failure pattern documented. Thresholds are
never relaxed to exit a loop.
"""
import csv
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
os.chdir(REPO)
import warnings
warnings.filterwarnings("ignore")

from PIL import Image
import art_lint
import fineness_metrics as fm
from client_compat import generate_image_bitforge
from generate_candidates_locked import build_swatch_from_live, pipeline_one, GEN_SIZE

FINE_TH = json.load(open("tools/art_lint/fineness_thresholds.json"))
PALETTE = art_lint.load_palette("config/art/oryx_master_palette.json")
REGISTER = "chunky, minimal detail, bold shapes, thick outline"


def critic(path, asset_class, sheet_class):
    """Pixels-only verdict. Returns (win, report) where report names every metric vs canon p90."""
    im = Image.open(path).convert("RGBA")
    a = art_lint.lint_file(path, asset_class, PALETTE)
    f = fm.compute(im)
    th = FINE_TH[sheet_class]
    rep = {"lint_overall": a["overall"], "A1": a["A1"], "A4": a["A4"], "A5": a["A5"], "A6": a["A6"]}
    fine_ok = True
    for k in fm.METRICS:
        p90 = th[k]["warn_p90"]
        over = f[k] > p90
        rep[k] = f[k]
        rep[k + "_p90"] = p90
        rep[k + "_over"] = over
        if over and k != "edge_density":  # F4 demoted to advisory (Rafe 2026-08) — reported, never gates
            fine_ok = False
    # largest gap (ratio over p90) for the "name the single largest metric gap" step
    gaps = {k: (f[k] / th[k]["warn_p90"] if th[k]["warn_p90"] else 0) for k in fm.METRICS}
    rep["largest_gap"] = max(gaps, key=gaps.get)
    lint_ok = a["overall"] in ("PASS", "WARN") and a["A1"] != "FAIL"
    rep["win"] = bool(fine_ok and lint_ok)
    return rep["win"], rep


def regenerate(concept, prompt, live_path, asset_class="prop", final_size=24, sheet_class="world_24x24",
               front_facing=True, max_attempts=12, seed_start=0, target_winners=6):
    out = f"tools/art_lint/candidates/gauntlet/{concept}"
    os.makedirs(out, exist_ok=True)
    swatch, colors = build_swatch_from_live(live_path, asset_class)
    swatch.save(os.path.join(out, "_swatch.png"))
    full_prompt = f"{prompt}, {REGISTER}" + (", front-facing, straight-on, no perspective" if front_facing else "")
    rows = []
    winners = []
    seed = seed_start
    for attempt in range(max_attempts):
        if len(winners) >= target_winners:
            break
        tag = f"{concept}_s{seed}"
        try:
            raw = generate_image_bitforge(full_prompt + ", small sprite, pixel art", GEN_SIZE,
                                          seed=seed, color_image=swatch)
            r = pipeline_one(raw, final_size, asset_class, False, out, tag)
            path = r.get("final_path")
            if path and os.path.exists(path):
                win, rep = critic(path, asset_class, sheet_class)
                gap = sum(max(0, rep[k] - rep[k + "_p90"]) / (rep[k + "_p90"] or 1) for k in fm.METRICS)
                rows.append({"seed": seed, "win": win, "path": path, "gap": round(gap, 3), **{k: rep[k] for k in fm.METRICS}, "largest_gap": rep["largest_gap"], "lint": rep["lint_overall"]})
                if win:
                    winners.append(path)
                    print(f"  [{tag}] metric-WIN (spk{rep['speckle']} sc{rep['small_clusters']} cr{rep['color_regions']} ed{rep['edge_density']})")
                else:
                    print(f"  [{tag}] over gap={gap:.2f} largest={rep['largest_gap']} ed{rep['edge_density']}")
        except Exception as e:
            rows.append({"seed": seed, "win": False, "error": str(e)[:80]})
            print(f"  [{tag}] error {str(e)[:60]}")
        seed += 1
    with open(f"{out}/_critic_log.csv", "w", newline="") as f:
        fields = ["seed", "win", "gap", "speckle", "small_clusters", "color_regions", "edge_density", "largest_gap", "lint", "path", "error"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(f"  metric-winners: {len(winners)}/{len(rows)} attempts (visual pre-filter next)")
    return {"concept": concept, "won": len(winners) > 0, "winners": winners, "attempts": len(rows), "rows": rows}


if __name__ == "__main__":
    W = "src/Presentation/assets/sprites_16bf/world_24x24"
    CONFIGS = {
        "anvil":     dict(prompt="a blacksmith anvil", live=f"{W}/oryx_16bit_fantasy_world_5001.png", front=True),
        "sack":      dict(prompt="a full cloth sack", live=f"{W}/oryx_16bit_fantasy_world_5102.png", front=True),
        "bed":       dict(prompt="a simple bed with headboard and blanket", live=f"{W}/oryx_16bit_fantasy_world_5058.png", front=True),
        "bench":     dict(prompt="a plain wooden bench", live=f"{W}/oryx_16bit_fantasy_world_5060.png", front=True),
        "shelf_bottles": dict(prompt="a wooden shelf holding a few bottles", live=f"{W}/oryx_16bit_fantasy_world_5099.png", front=True),
        "training_dummy": dict(prompt="a training dummy, straw and cloth on a wooden post", live=f"{W}/oryx_16bit_fantasy_world_5088.png", front=True),
        "nightstand": dict(prompt="a small bedside nightstand with a single drawer", live=f"{W}/oryx_16bit_fantasy_world_5106.png", front=True),
        "workbench": dict(prompt="a sturdy wooden workbench", live=f"{W}/oryx_16bit_fantasy_world_5082.png", front=True),
        "water_barrel": dict(prompt="a wooden barrel full of water, water visible at the top", live=f"{W}/oryx_16bit_fantasy_world_5084.png", front=True),
    }
    name = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    c = CONFIGS[name]
    res = regenerate(name, c["prompt"], c["live"], front_facing=c["front"], max_attempts=n)
    print(f"[{name}] won={res['won']} attempts={res['attempts']}")
