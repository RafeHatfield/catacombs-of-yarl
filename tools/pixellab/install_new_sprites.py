#!/usr/bin/env python3
"""
Install selected PixelLab sprites into game assets (IDs 5067–5109).
Also deletes placeholder IDs 5017–5038 that are being replaced.
Run once from project root.
"""

from pathlib import Path
from PIL import Image

BATCH = Path("tools/pixellab/batch_new_sprites_results")
ASSETS = Path("src/Presentation/assets/sprites_16bf/world_24x24")

# (sprite_id, object_folder, seed)
INSTALL = [
    # glowing_mushroom
    (5067, "glowing_mushroom", 1),
    (5068, "glowing_mushroom", 2),
    (5069, "glowing_mushroom", 1337),
    # mural_wood_cool
    (5070, "mural_wood_cool",  1337),
    # mural_gold_warm (treating user's "32" as seed 3)
    (5071, "mural_gold_warm",  999),
    (5072, "mural_gold_warm",  42),
    (5073, "mural_gold_warm",  3),
    (5074, "mural_gold_warm",  0),
    # mural_gold_land
    (5075, "mural_gold_land",  137),
    (5076, "mural_gold_land",  0),
    # signpost
    (5077, "signpost",         0),
    # rubble
    (5078, "rubble",           137),
    (5079, "rubble",           2),
    # candelabra
    (5080, "candelabra",       0),
    (5081, "candelabra",       1),
    # workbench
    (5082, "workbench",        0),
    (5083, "workbench",        1337),
    # water_barrel
    (5084, "water_barrel",     1),
    (5085, "water_barrel",     999),
    # vine
    (5086, "vine",             42),
    # training_dummy
    (5087, "training_dummy",   0),
    (5088, "training_dummy",   42),
    # tool_rack
    (5089, "tool_rack",        137),
    (5090, "tool_rack",        1337),
    # straw
    (5091, "straw",            0),
    (5092, "straw",            1),
    # pillar
    (5093, "pillar",           0),
    (5094, "pillar",           1),
    (5095, "pillar",           137),
    # shelf
    (5096, "shelf",            0),
    (5097, "shelf",            42),
    (5098, "shelf",            999),
    # bottle_shelf
    (5099, "bottle_shelf",     1),
    (5100, "bottle_shelf",     42),
    (5101, "bottle_shelf",     137),
    # sack
    (5102, "sack",             0),
    (5103, "sack",             2),
    # rock
    (5104, "rock",             1),
    (5105, "rock",             2),
    # nightstand
    (5106, "nightstand",       42),
    (5107, "nightstand",       999),
    # mushroom_cluster
    (5108, "mushroom_cluster", 0),
    (5109, "mushroom_cluster", 1),
]

# Placeholder IDs to DELETE (being replaced by the above, or deferred/removed)
DELETE_IDS = list(range(5017, 5039))  # 5017–5038 inclusive (5039 = key_item, keep)

print("=== Installing PixelLab sprites ===\n")
for sprite_id, obj, seed in INSTALL:
    src = BATCH / obj / f"{obj}_s{seed}_32px.png"
    dst = ASSETS / f"oryx_16bit_fantasy_world_{sprite_id}.png"
    if not src.exists():
        print(f"  MISSING: {src}")
        continue
    img = Image.open(src).resize((24, 24), Image.NEAREST)
    img.save(dst)
    print(f"  {sprite_id} ← {obj} s{seed}")

print(f"\n=== Deleting old placeholder sprites ===\n")
for i in DELETE_IDS:
    for suffix in ["", ".import"]:
        p = ASSETS / f"oryx_16bit_fantasy_world_{i}.png{suffix}"
        if p.exists():
            p.unlink()
            print(f"  deleted {p.name}")

print("\nDone.")
