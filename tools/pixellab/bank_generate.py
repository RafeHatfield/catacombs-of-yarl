#!/usr/bin/env python3
"""
PixelLab candidate bank generator — speculative, pre-reset material banking.

Nothing this script produces lands in src/Presentation/assets or touches the
generated_assets_manifest. Output goes only under
tools/art_lint/candidates/bank/<category>/<subcategory>/*.png, plus one
index.csv per category.

Hard constraints (verbatim from Burn-Down 2b / PIXELLAB_CONVENTIONS.md):
  - License guard: BitForge calls take description/image_size/no_background/seed
    ONLY. No color_image, no style_image, ever — no Oryx image is used as
    conditioning of any kind. This is enforced structurally: generate_one()
    below has no parameter through which a reference image could be passed.
  - Prompt template: "{object}, small sprite, pixel art" (PIXELLAB_CONVENTIONS.md).
  - Pipeline: generate -> structural clean (binarize alpha) -> palette snap
    (tools/art_lint/snap_to_palette.py) -> lint (tools/art_lint/art_lint.py),
    same as the art bible's landing pipeline (docs/art_bible.md #10), run here
    for triage tagging only.

Resumable: skips any candidate whose final PNG already exists. Safe to
interrupt (Ctrl-C or backgrounded process kill) and re-run.

Run from repo root:
  source ~/.bashrc && python3 tools/pixellab/bank_generate.py [--max-total N] [--category NAME]
"""
import argparse
import csv
import os
import sys
import time

from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "art_lint"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "pixellab"))
import art_lint as al          # noqa: E402
import snap_to_palette as sp   # noqa: E402

# pixellab==1.0.5's SDK response model hardcodes usage.type: Literal["usd"], but this
# account's subscription billing returns {"type": "generations", ...} which fails
# pydantic validation before the image can be read out. client_compat bypasses the
# SDK's response parsing with a raw HTTP call (same fix already in use on
# art/burndown-2b-generation-tier — see tools/pixellab/client_compat.py).
import client_compat  # noqa: E402

MAX_CONSECUTIVE_FAILURES = 5

BANK_ROOT = os.path.join(REPO_ROOT, "tools", "art_lint", "candidates", "bank")
PALETTE_PATH = os.path.join(REPO_ROOT, "config", "art", "oryx_master_palette.json")

SEEDS_8 = [0, 1, 2, 3, 42, 137, 999, 1337]
SEEDS_10 = SEEDS_8 + [7, 21]

GEN_SIZE = {"width": 32, "height": 32}
FINAL_SIZE = 24


def slugify(s):
    return "".join(c if c.isalnum() else "_" for c in s.lower()).strip("_")


# ---------------------------------------------------------------------------
# Category definitions
# ---------------------------------------------------------------------------
# Each category: name, lint_class (None => skip lint triage), subcategories.
# Each subcategory: tag, list of (concept, motif_description) with SEEDS_8/10.

MURAL_DESIGN = {
    "name": "mural_design",
    "lint_class": "prop",
    "seeds": SEEDS_10,
    "subcategories": {
        "heraldic": [
            ("heraldic_lion", "heraldic lion emblem on flat shield-shaped mural"),
            ("heraldic_eagle", "heraldic eagle crest emblem mural"),
            ("heraldic_shield", "heraldic shield emblem mural"),
            ("heraldic_sword_star", "heraldic sword and star emblem mural"),
            ("heraldic_dragon", "heraldic dragon crest emblem mural"),
        ],
        "banner_tapestry": [
            ("banner_sun", "hanging cloth banner with sun motif"),
            ("tapestry_tree", "hanging tapestry with tree motif"),
            ("banner_wave", "hanging cloth banner with wave motif"),
            ("tapestry_star", "hanging tapestry with star motif"),
            ("banner_crescent", "hanging cloth banner with crescent moon motif"),
        ],
        "simplified_pictorial": [
            ("pictorial_mountain", "simplified flat mountain landscape mural"),
            ("pictorial_forest", "simplified flat forest landscape mural"),
            ("pictorial_sea_cliff", "simplified flat sea and cliff landscape mural"),
            ("pictorial_sunset", "simplified flat sunset landscape mural"),
            ("pictorial_river_valley", "simplified flat river valley landscape mural"),
        ],
    },
}

PROP_VARIETY = {
    "name": "prop_variety",
    "lint_class": "prop",
    "seeds": SEEDS_8,
    "subcategories": {
        "rocks_rubble": [
            ("small_rock", "small stone rock"),
            ("rubble_pile", "pile of broken stone rubble"),
            ("boulder_fragment", "boulder fragment"),
            ("cracked_stone_chunk", "cracked stone chunk"),
            ("gravel_pile", "scattered gravel pile"),
            ("moss_rock", "large moss-covered rock"),
            ("stone_debris_pile", "broken stone debris pile"),
        ],
        "crates": [
            ("wooden_crate", "wooden crate"),
            ("stacked_crates", "stack of two wooden crates"),
            ("broken_crate", "broken wooden crate"),
            ("small_crate", "small wooden shipping crate"),
            ("banded_crate", "wooden crate with iron bands"),
            ("open_crate", "open wooden crate"),
            ("labeled_crate", "wooden crate with stenciled markings"),
        ],
        "sacks": [
            ("tied_sack", "tied burlap sack"),
            ("bulging_sack", "bulging burlap sack of grain"),
            ("slumped_sack", "slumped empty burlap sack"),
            ("stacked_sacks", "stack of two burlap sacks"),
            ("torn_sack", "torn burlap sack"),
            ("small_pouch_sack", "small cinched burlap pouch"),
            ("grain_sack", "burlap sack spilling grain"),
        ],
        "pots": [
            ("clay_pot", "small clay pot"),
            ("cracked_pot", "cracked clay pot"),
            ("cauldron_pot", "iron cooking pot"),
            ("tall_urn", "tall ceramic urn"),
            ("broken_pot_shards", "broken clay pot shards"),
            ("glazed_pot", "glazed ceramic pot"),
            ("cooking_pot_on_stand", "iron cooking pot on a small stand"),
        ],
        "bones_skulls": [
            ("skull", "bleached skull"),
            ("bone_pile", "pile of bones"),
            ("rib_cage", "bare rib cage bones"),
            ("skull_stack", "small stack of skulls"),
            ("femur_bones", "crossed femur bones"),
            ("bone_scatter", "scattered bone fragments"),
            ("horned_skull", "horned animal skull"),
        ],
        "torches_sconces": [
            ("wall_torch", "lit wall-mounted torch"),
            ("standing_torch", "lit standing torch on a post"),
            ("iron_sconce", "empty iron wall sconce"),
            ("unlit_torch", "unlit wooden torch"),
            ("dual_sconce", "wall sconce with two candles"),
            ("brazier_torch", "small lit floor brazier"),
            ("wall_torch_bracket", "iron torch bracket mounted on stone"),
        ],
        "tables_stools": [
            ("small_stool", "small wooden stool"),
            ("round_table", "small round wooden table"),
            ("bench_stool", "low wooden bench"),
            ("three_leg_stool", "three-legged wooden stool"),
            ("side_table", "small wooden side table"),
            ("stump_stool", "wooden stump used as a stool"),
            ("cracked_table", "small cracked wooden table"),
        ],
        "barrels": [
            ("sealed_barrel", "sealed wooden barrel"),
            ("open_barrel", "open wooden barrel"),
            ("broken_barrel", "broken wooden barrel"),
            ("stacked_barrels", "stack of two wooden barrels"),
            ("small_keg", "small wooden keg"),
            ("banded_barrel", "wooden barrel with iron bands"),
            ("leaking_barrel", "wooden barrel with a small leak"),
        ],
        "debris": [
            ("wood_splinters", "pile of broken wood splinters"),
            ("cobweb_clump", "clump of tangled cobweb"),
            ("scattered_straw", "scattered pile of straw"),
            ("broken_cart_wheel", "broken wooden cart wheel"),
            ("rusty_scrap", "pile of rusty metal scrap"),
            ("cloth_scraps", "pile of torn cloth scraps"),
            ("shattered_glass", "pile of shattered glass shards"),
        ],
    },
}

FLOOR_WALL_TEXTURE = {
    "name": "floor_wall_texture",
    "lint_class": "decal",
    "seeds": SEEDS_10,
    "subcategories": {
        "worn_floor": [
            ("worn_floor_scuff", "subtly scuffed stone floor tile"),
            ("worn_floor_crack", "subtly worn stone floor tile with a hairline crack"),
            ("worn_floor_patch", "stone floor tile with a faint worn patch"),
            ("worn_floor_chip", "stone floor tile with a small chipped corner"),
            ("worn_floor_fade", "stone floor tile with faint color fading"),
        ],
        "cracked_wall": [
            ("cracked_wall_hairline", "stone wall tile with a hairline crack"),
            ("cracked_wall_corner", "stone wall tile with a cracked corner"),
            ("cracked_wall_web", "stone wall tile with a small web of cracks"),
            ("cracked_wall_chip", "stone wall tile with a chipped chunk missing"),
            ("cracked_wall_seam", "stone wall tile with a cracked mortar seam"),
        ],
        "moss_patch": [
            ("moss_patch_small", "small moss patch on stone"),
            ("moss_patch_creeping", "creeping moss patch on stone corner"),
            ("moss_patch_damp", "damp moss patch on stone"),
            ("moss_patch_sparse", "sparse moss growth on stone"),
            ("moss_patch_thick", "thick moss patch on stone"),
        ],
        "stain_decal": [
            ("stain_water", "faint water stain on stone"),
            ("stain_soot", "faint soot stain on stone"),
            ("stain_rust", "faint rust stain streak on stone"),
            ("stain_dark_patch", "faint dark stain patch on stone"),
            ("stain_dripstreak", "faint drip streak stain on stone"),
        ],
    },
}

M3_DESIGN_REFERENCE = {
    "name": "m3_design_reference",
    "lint_class": None,  # exempt from lint triage
    "seeds": SEEDS_10,
    "subcategories": {
        "creature_silhouette": [
            ("fungal_cave_creature", "fungal cave dwelling creature, mood silhouette"),
            ("fungal_cave_creature_alt", "fungal cave spore-covered creature, mood silhouette"),
            ("fungal_cave_creature_lurker", "fungal cave lurking creature in the shadows, mood silhouette"),
            ("flooded_ruins_creature", "flooded ruins lurking creature, mood silhouette"),
            ("flooded_ruins_creature_alt", "flooded ruins eel-like creature, mood silhouette"),
            ("flooded_ruins_creature_lurker", "flooded ruins creature rising from water, mood silhouette"),
            ("bone_crypt_creature", "bone crypt guardian creature, mood silhouette"),
            ("bone_crypt_creature_alt", "bone crypt skeletal creature, mood silhouette"),
            ("bone_crypt_creature_lurker", "bone crypt creature emerging from a sarcophagus, mood silhouette"),
            ("forge_ember_creature", "forge ember creature, mood silhouette"),
            ("forge_ember_creature_alt", "forge molten-cracked creature, mood silhouette"),
            ("forge_ember_creature_lurker", "forge ember creature wreathed in smoke, mood silhouette"),
        ],
        "npc_silhouette": [
            ("hooded_wanderer", "hooded wandering figure, mood silhouette"),
            ("hooded_wanderer_alt", "hooded traveler leaning on a staff, mood silhouette"),
            ("cloaked_merchant", "cloaked merchant figure, mood silhouette"),
            ("cloaked_merchant_alt", "cloaked merchant with a pack, mood silhouette"),
            ("armored_guard", "armored guard figure, mood silhouette"),
            ("armored_guard_alt", "armored guard with a halberd, mood silhouette"),
            ("robed_scholar", "robed scholar figure, mood silhouette"),
            ("robed_scholar_alt", "robed scholar holding a book, mood silhouette"),
        ],
        "region_mood": [
            ("fungal_cave_mood", "fungal cave mood prop, glowing fungus cluster"),
            ("fungal_cave_mood_alt", "fungal cave mood prop, spore cloud over rocks"),
            ("fungal_cave_mood_glow", "fungal cave mood prop, bioluminescent moss patch"),
            ("flooded_ruins_mood", "flooded ruins mood prop, waterlogged debris"),
            ("flooded_ruins_mood_alt", "flooded ruins mood prop, submerged broken column"),
            ("flooded_ruins_mood_wreckage", "flooded ruins mood prop, algae-covered wreckage"),
            ("bone_crypt_mood", "bone crypt mood prop, skull pile in alcove"),
            ("bone_crypt_mood_alt", "bone crypt mood prop, cracked stone sarcophagus"),
            ("bone_crypt_mood_altar", "bone crypt mood prop, bone-adorned altar"),
            ("forge_ember_mood", "forge ember mood prop, glowing coal pile"),
            ("forge_ember_mood_alt", "forge ember mood prop, molten metal pour"),
            ("forge_ember_mood_coals", "forge ember mood prop, ash-covered ember bed"),
        ],
    },
}

CATEGORIES = [MURAL_DESIGN, PROP_VARIETY, FLOOR_WALL_TEXTURE, M3_DESIGN_REFERENCE]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def check_api_key():
    if not (os.environ.get("PIXELLAB_API_KEY") or os.environ.get("PIXELLAB_API_TOKEN")):
        print("ERROR: neither PIXELLAB_API_KEY nor PIXELLAB_API_TOKEN is set", file=sys.stderr)
        sys.exit(1)


def generate_one(description, seed):
    """BitForge call — description/image_size/no_background/seed ONLY.
    No color_image, no style_image: structurally impossible to pass one here.
    """
    return client_compat.generate_image_bitforge(
        description=description,
        image_size=GEN_SIZE,
        no_background=True,
        seed=seed,
    )


def structural_clean(im):
    """Binarize alpha (bible: alpha is 0 or 255, never partial)."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return im


def downscale(im, size):
    return im.resize((size, size), Image.NEAREST)


def run_pipeline(description, seed, out_path):
    raw = generate_one(description, seed)
    cleaned = structural_clean(raw)
    final = downscale(cleaned, FINAL_SIZE)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.save(out_path)
    return final


def lint_and_tag(path, lint_class, palette_set):
    row = al.lint_file(path, lint_class, palette_set)
    verdict = {"PASS": "pass", "WARN": "marginal", "FAIL": "fail"}[row["overall"]]
    return verdict, row["A4_color_count"], row["overall"]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def iter_candidates(category):
    for subcat, concepts in category["subcategories"].items():
        for concept, motif in concepts:
            for seed in category["seeds"]:
                yield subcat, concept, motif, seed


def run_category(category, palette_set, max_remaining, consecutive_failures):
    cat_name = category["name"]
    cat_dir = os.path.join(BANK_ROOT, cat_name)
    index_path = os.path.join(cat_dir, "index.csv")
    os.makedirs(cat_dir, exist_ok=True)

    new_file = not os.path.exists(index_path)
    f = open(index_path, "a", newline="")
    writer = csv.writer(f)
    if new_file:
        writer.writerow(["category", "subcategory", "concept", "prompt", "seed",
                          "filename", "resolution", "color_count", "lint_overall", "verdict", "notes"])
        f.flush()

    generated_this_run = 0
    for subcat, concept, motif, seed in iter_candidates(category):
        if max_remaining[0] <= 0:
            break
        fname = f"{concept}_s{seed}.png"
        out_path = os.path.join(cat_dir, subcat, fname)
        if os.path.exists(out_path):
            continue  # resumable: already generated

        description = f"{motif}, small sprite, pixel art"
        try:
            final = run_pipeline(description, seed, out_path)
        except Exception as e:
            print(f"  ERROR generating {cat_name}/{subcat}/{fname}: {e}", file=sys.stderr)
            consecutive_failures[0] += 1
            if consecutive_failures[0] >= MAX_CONSECUTIVE_FAILURES:
                print(f"ABORTING: {consecutive_failures[0]} consecutive failures — "
                      f"likely a systematic bug, not per-image bad luck. Stopping before "
                      f"burning more quota on a broken pipeline.", file=sys.stderr)
                f.close()
                sys.exit(1)
            time.sleep(3.0)
            continue
        consecutive_failures[0] = 0

        if category["lint_class"] is not None:
            try:
                verdict, color_count, lint_overall = lint_and_tag(out_path, category["lint_class"], palette_set)
            except Exception as e:
                verdict, color_count, lint_overall = "fail", "", f"lint_error:{e}"
        else:
            verdict, color_count, lint_overall = "design_reference", "", ""

        writer.writerow([cat_name, subcat, concept, description, seed, fname,
                          f"{FINAL_SIZE}x{FINAL_SIZE}", color_count, lint_overall, verdict, ""])
        f.flush()

        generated_this_run += 1
        max_remaining[0] -= 1
        if generated_this_run % 10 == 0:
            print(f"  [{cat_name}] {generated_this_run} generated this run, {max_remaining[0]} of total budget remaining")
        time.sleep(0.4)  # courtesy delay — burn-down 2b shares this API token/machine and has priority

    f.close()
    print(f"[{cat_name}] done this pass: {generated_this_run} generated")
    return generated_this_run


def count_existing():
    total = 0
    if not os.path.isdir(BANK_ROOT):
        return 0
    for root, _, files in os.walk(BANK_ROOT):
        total += sum(1 for fn in files if fn.endswith(".png"))
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-total", type=int, default=1500,
                        help="hard cap on total PNGs across the whole bank (existing + new)")
    parser.add_argument("--category", default=None,
                        help="restrict to one category name (mural_design, prop_variety, "
                             "floor_wall_texture, m3_design_reference)")
    args = parser.parse_args()

    palette_set = al.load_palette(PALETTE_PATH)
    check_api_key()

    existing = count_existing()
    remaining_budget = max(0, args.max_total - existing)
    print(f"Existing bank PNGs: {existing}. Budget remaining this run: {remaining_budget} (cap {args.max_total})")
    max_remaining = [remaining_budget]
    consecutive_failures = [0]

    cats = [c for c in CATEGORIES if args.category is None or c["name"] == args.category]

    for category in cats:
        if max_remaining[0] <= 0:
            print(f"Budget exhausted before category {category['name']}; stopping.")
            break
        print(f"=== Category: {category['name']} ===")
        run_category(category, palette_set, max_remaining, consecutive_failures)

    print(f"Run complete. Total bank PNGs now: {count_existing()}")


if __name__ == "__main__":
    main()
