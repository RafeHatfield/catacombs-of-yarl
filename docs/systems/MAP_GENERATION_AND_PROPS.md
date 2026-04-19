# Map Generation and Props

**Sources:** `src/Logic/Core/DungeonFloorBuilder.cs`, `config/level_templates.yaml`, `config/props.yaml`  
**Implementation status:** Procedural generation fully implemented. Props rendered in-engine. Room archetypes implemented via prop placement system. Traps — not yet implemented (see note).

---

## Map Generation

### Floor Parameters

**Defaults (all depths unless overridden in `level_templates.yaml`):**
- Map size: 120×80 tiles
- Max room attempts: 25 (produces ~15–18 actual placed rooms)
- Room size: 5–10 tiles wide/tall (rectangular)
- Corridor connection: Nearest-room MST (minimum spanning tree) — prevents spaghetti layouts

**Per-depth overrides (`level_templates.yaml`):**

| Depth(s) | max_rooms | max_monsters/room | max_items/room | ETP Max | Notes |
|---|---|---|---|---|---|
| 1 | 25 | 1 | 2 | 50 | Gentle intro |
| 2 | 25 | 2 | 2 | 50 | |
| 3 | 25 | 3 | 2 | 50 | |
| 6 | 25 | 3 | 2 | 120 | B2 start |
| 11 | 25 | 4 | 2 | 180 | B3 start |
| 16 | 25 | 4 | 2 | 240 | B4 start |
| 21 | 25 | 4 | 2 | 300 | B5 start |
| 25 | 30 | 5 | 3 | 350 | Endgame |

### Guaranteed Spawns

Early floors guarantee healing potions to smooth the curve:
- Depth 1: 2–3 healing potions placed as additional items (mode: "additional")
- Depth 2: 1–2 healing potions
- Depth 3: 1–2 healing potions

"Additional" mode adds items on top of normal loot generation rather than replacing it.

### Encounter Budget (ETP)

ETP = Encounter Threat Points. Each monster has an `etp_base` value (see `MONSTERS.md`). The floor builder selects monster encounters until the total ETP budget is consumed. `allow_spike: false` prevents any single encounter from exceeding ~40% of the floor budget.

---

## Tile Types

| TileKind | Description |
|---|---|
| Floor | Walkable, no special behaviour |
| Wall | Solid, blocks movement and line-of-sight |
| StairDown | Descends to next floor; ends current floor session |
| StairUp | Ascends (not yet used — no return-to-previous-floor) |
| Door (closed) | Blocks movement and LOS; opened by bumping or `can_open_doors` AI |
| Door (open) | Walkable, transparent |

Doors render with directional rotation based on corridor orientation (N/S vs E/W corridor).

### Wall Autotile

Walls use a 4-bit bitmask autotile system. Each wall tile checks its 4 cardinal neighbors and maps to one of 16 tile variants for visual variety. The tile IDs for each bitmask combination are defined in `config/tile_themes.yaml` under `wall_autotile`.

---

## Props System

### Overview

Props are decorative/atmospheric objects placed in rooms. They are **not** interactive — no loot, no effects. Pure visual. Defined in `config/props.yaml`.

### Prop Attributes

| Attribute | Values | Meaning |
|---|---|---|
| `tile_ids` | Array of int | Tile(s) from the Oryx 16bf world sheet. Multiple = random pick |
| `footprint` | [w, h] | Size in tiles. Most are [1,1]; rug is [3,3], alchemy_table is [3,1] |
| `blocks_movement` | bool | Whether entities can walk through |
| `placement` | wall_adjacent, center, corner, free_standing, floor_overlay | Placement constraint for room archetype engine |
| `tags` | Array | Category hints used by archetype recipes |
| `tile_layouts` | Array of arrays | Multi-tile props: explicit tile IDs per cell in row-major order |

### Placement Rules

- `wall_adjacent`: Must be placed against a room wall
- `corner`: Placed in room corners
- `center`: Placed near room center
- `free_standing`: Can be anywhere that's not a wall/door/stair
- `floor_overlay`: Placed on walkable floor, does not block movement

### Multi-Tile Props

Two props use `tile_layouts` (array of arrays) for multiple layout variants:
- **rug** [3×3]: Two colour variants (tan/brown or blue), chosen randomly at placement
- **alchemy_table** [3×1]: Single variant, three tiles side-by-side along a wall

### Props Catalogue

**Dungeon Basics** (tags: dungeon_basic)
- barrel, barrel_open, crate, chest_closed, sack (storage)
- rubble, cobweb, bones_pile, skeleton_prop (scatter/floor overlay)
- pillar, stalagmite (structure/natural)
- rock (natural, blocks movement)

**Furniture / Living** (tags: furniture, living)
- table, chair, bed, nightstand, wardrobe, desk, bookshelf, shelf
- candelabra, candle (light sources, visual only)
- fireplace, rug

**Grand Spaces** (tags: grand)
- throne (throne_room), banner, statue, brazier (with flame overlay), fountain, bench, planter

**Religious / Ritual** (tags: ritual)
- altar, sarcophagus, tombstone, urn, prayer_mat
- Tags: shrine, crypt

**Workshop / Forge** (tags: forge, workshop)
- forge, anvil, weapon_rack, armor_stand, tool_rack, workbench, coal_pile, water_barrel, training_dummy

**Alchemy / Laboratory** (tags: laboratory)
- cauldron, alchemy_table, shelf_bottles, globe

**Prison** (tags: prison)
- chain, cage, iron_bars, bucket, straw_pile

**Sewer / Industrial** (tags: sewer)
- grate, pipe_horizontal, pipe_vertical, puddle, moss_patch, drain

**Natural / Organic** (tags: natural)
- mushroom_cluster, glowing_mushroom, vine

### Brazier Special Case

The `brazier` prop has both a `tile_ids` (the bowl-on-stand base tile) and an `overlay_tile_id` (the flame tile rendered on top at the same position). This gives it a layered appearance without using the multi-tile system.

### Grand Shrine (Room Archetype)

The "Grand Shrine" archetype spawns:
- Central altar (placement: center)
- 2 braziers at fixed offset positions flanking the altar
- Banner(s) on adjacent walls

This is the most complex archetype currently implemented.

---

## Traps

**Not yet implemented.** The `level_templates.yaml` references `trap_rules` as a deferred field (parsed but not processed). The PoC has a trap system — this is in the future plans (`plan_interactive_props_traps.md`).

Ground hazards (fire, poison gas from spells) are implemented — see `GROUND_HAZARDS.md`. These are the closest thing to environmental hazards currently in the game.

---

## FOV and Visibility

- FOV radius: 8 tiles (computed via shadow-casting algorithm)
- Alert radius for monsters to detect player: 5 tiles
- Tiles outside FOV fade to partial visibility (seen-but-not-visible tinting)
- Auto-explore reveals the map tile by tile, stopping when a monster or item is spotted

---

## Signposts and Murals

Two interactive room features (not props — they're functional entities):

**Signposts** — placed rarely in rooms, tap to read. Message pool in `config/signpost_messages.yaml`. Flavour text only.

**Murals** — decorative wall art with lore inscriptions. Message pool in `config/murals_inscriptions.yaml`. Tile IDs from `TileThemeConfig` (mural_gold_landscape, mural_gold_warm, mural_wood_cool). Each mural is tracked by `MuralTracker` — each mural can only be "discovered" once per floor.

**Chests** — spawn on floors as interactive entities. Can be open, closed, trapped, or empty. Closed chests contain loot. Trapped chests deal damage when opened. Sprites from `TileThemeConfig.ChestClosed` / `ChestOpen` etc.
