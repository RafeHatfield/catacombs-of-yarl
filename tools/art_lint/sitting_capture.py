#!/usr/bin/env python3
"""Full-inventory sitting: capture every generated prop in-scene (live), grouped into
six category scenes. All cells render live (nothing temp-written) — these are the landed
assets as they ship. Output -> tools/art_lint/review_scenes/sitting_*.png."""
import json
import review_capture

man=json.load(open("config/art/generated_assets_manifest.json"))
id2key={}
for e in man["entries"]:
    tid=int(e["path"].split("_")[-1].split(".")[0])
    id2key[tid]=e.get("game_key", "?")

GROUPS=[
 ("sitting_1_seating_tables","Sitting 1/6 — seating, tables, desks, benches, sign",
  [5051,5056,5057,5052,5053,5054,5055,5062,5063,5064,5060,5061,5077]),
 ("sitting_2_storage_surfaces","Sitting 2/6 — shelves, bottle-shelves, nightstands, workbench, tool racks",
  [5096,5097,5098,5099,5100,5101,5106,5107,5082,5083,5089,5090]),
 ("sitting_3_beds_containers_chests","Sitting 3/6 — beds (TERMINAL exhibit), bucket, water barrels, sack, chests, cages",
  [5058,5059,5005,5084,5085,5102,5111,5112,5113,5114,5065,5066]),
 ("sitting_4_smithy_workshop","Sitting 4/6 — anvil, forge, chain, coal, iron bars, grate, drain, armor stand, training dummies, globe, candelabra",
  [5001,5011,5007,5008,5015,5014,5010,5002,5087,5088,5012,5080]),
 ("sitting_5_stone_murals_pillars","Sitting 5/6 — pillars (LANDED), murals, candelabra, key",
  [5093,5094,5095,5070,5071,5072,5073,5074,5075,5076,5081,5039]),
 ("sitting_6_depths_nature_decals","Sitting 6/6 — bone pile (LANDED 5115), mushrooms, rocks, straw, vine, moss, rubble, puddle, worn floor",
  [5115,5108,5109,5067,5068,5069,5104,5105,5091,5092,5086,5016,5078,5079,5110,3001]),
]

def nn(tid):
    return (tid, f"{id2key.get(tid,'?')} {tid}", False, None)

for name,title,ids in GROUPS:
    cells=[nn(t) for t in ids]
    review_capture.run_round(name, title, cells, cols=4)
