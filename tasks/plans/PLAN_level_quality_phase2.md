# Plan: Level Quality Phase 2 -- Props Polish, Doors, Special Rooms, Corridor Polish

**Status:** complete (PROP-009 deferred)
**Depends on:** PLAN_room_props_archetypes Phase A+B (PROP-001 through PROP-008, all complete)

## Current State

All tasks complete as of 2026-04-16. 1253 tests passing.

**Complete:** PROP-010 (symmetry), PROP-011 (best-of-N), PROP-012 (maintenance state), DOOR-001 (DoorPlacer logic), DOOR-002 (door rendering + FOV), DOOR-003 (DoorPlacerTests covers integration), SROOM-001 (dead-end tagging), SROOM-002 (Grand Shrine), SROOM-003 (vault designation).

**Deferred/removed:** CORR-001/002/003 (wide corridors, alcoves, stubs — intentionally removed when layout switched to MST algorithm). PROP-009 (YAML recipe migration — zero visual impact, highest regression risk, deferred indefinitely).

**Next:** Nothing in this plan. Next visual work is floor_dark/accent/worn tile IDs (blocked on Rafe's sprite survey).

## Overview

The dungeon has room shapes (6 types), floor composition (edge shadows, noise), and 15 archetypes with prop placement. That covers the basics. This plan addresses the next tier of quality:

- **Track A: Props Phase C Polish** -- Symmetry, best-of-N scoring, maintenance state decay, YAML-driven recipes. Makes rooms feel more intentional and less random.
- **Track B: Door System** -- Visual doors at corridor-room boundaries. Rooms start reading as enclosed spaces, not widenings of corridors. Walkable-only doors (no locking yet -- that's in plan_doors_secrets_portals).
- **Track C: Special Rooms** -- Vaults, grand shrines, dead-end treasure rooms. Break the procedural rhythm with rare, designed-feeling rooms.
- **Track D: Corridor Polish** -- Width variation, alcoves at corridor midpoints, dead-end stubs. Corridors stop being mechanical 1-tile connections.

All four tracks work within the existing architecture: logic layer pure C# (no Godot), presentation layer thin rendering passes. Scenario harness and balance pipeline are unaffected -- scenarios use `CreateArena`, not dungeon generation.

## Reference

- Props plan: `tasks/plans/PLAN_room_props_archetypes.md` (Phase A+B complete, Phase C is this plan's Track A)
- Visual overhaul plan: `tasks/plans/PLAN_dungeon_visual_overhaul.md` (Phase 0+1+2 complete)
- Doors/secrets plan: `tasks/plans/plan_doors_secrets_portals.md` (not started -- this plan implements the visual door subset)
- Python prototype: `~/development/rlike/map_objects/game_map.py` (place_corridor_doors, designate_vaults, secret_door.py)
- Room record: `src/Logic/ECS/Room.cs`
- Map generator: `src/Logic/ECS/MapGenerator.cs`
- Prop placer: `src/Logic/ECS/RoomPropPlacer.cs`
- Corridor segment: `src/Logic/ECS/CorridorSegment.cs`
- GeneratedMap: `src/Logic/ECS/GeneratedMap.cs`
- GameMap: `src/Logic/ECS/GameMap.cs` (TileKind.Door already exists, unused)
- DungeonRenderer: `src/Presentation/Map/DungeonRenderer.cs`
- Tile themes: `config/tile_themes.yaml`
- Props YAML: `config/props.yaml`

---

## New Tile IDs Needed

The following new tile IDs are required from the Oryx 16bf world_24x24 sheet. Rafe needs to survey `tools/sprite_browser_16bf_world.html` and fill these in before the relevant presentation tasks can start.

| Purpose | Used By | Status | Tile ID |
|---------|---------|--------|---------|
| Door (closed, vertical) | DOOR-002 | TBD | ? |
| Door (closed, horizontal) | DOOR-002 | TBD | ? |
| Door (open, vertical) | Future (locked doors plan) | Deferred | -- |
| Door (open, horizontal) | Future (locked doors plan) | Deferred | -- |

Notes:
- We only need closed-door tiles for this plan. Doors are walkable and have no open/closed state yet -- that's in `plan_doors_secrets_portals`. The door tile is purely visual, communicating "there was a doorway here."
- If only one door tile exists (no directional variant), use it for both orientations. The placement pass knows the corridor direction and can pick accordingly.
- Vault rooms do NOT need a special wall tile. They use the existing sandstone theme with prop dressing to feel distinct.

---

## Track A: Props Phase C -- Polish

Continues the PROP-009 through PROP-012 numbering from `PLAN_room_props_archetypes.md`. PROP-013 (EntityPlacer verification) is already defined there and is independent.

### PROP-009: YAML-driven archetype recipes

- Status: pending
- Layer: logic
- Type: system
- Dependencies: none (PROP-006 already complete)
- Files to create:
  - `config/room_archetypes.yaml`
  - `src/Logic/Content/ArchetypeRecipeRegistry.cs`
- Files to modify:
  - `src/Logic/ECS/RoomPropPlacer.cs` (remove hardcoded `Recipes` dict, load from registry)
  - `src/Logic/ECS/RoomArchetypeSelector.cs` (optionally load constraint table from YAML too)
- Description: The archetype prop recipe table is currently hardcoded in `RoomPropPlacer.cs` (the `Recipes` dictionary, ~170 lines of PropRule definitions). Move all recipe data to `config/room_archetypes.yaml`. Create `ArchetypeRecipeRegistry` that loads the YAML and provides recipe lookup by archetype. `RoomPropPlacer` becomes a pure recipe executor -- it receives a recipe from the registry and places props, with no knowledge of what archetypes exist. Optionally also move the `RoomArchetypeSelector.Constraints` table to the same YAML file (weight, min_walkable, depth range, allowed shapes per archetype).
- YAML schema:
  ```yaml
  archetypes:
    library:
      # Selector constraints (currently in RoomArchetypeSelector.cs)
      min_walkable: 25
      depth_range: [1, 4]
      weight: 10
      allowed_shapes: [Rectangle, Union, Alcove]
      dense: false
      # Prop recipe (currently in RoomPropPlacer.Recipes)
      props:
        required:
          - id: bookshelf
            placement: wall_adjacent
            count: [2, 3]
          - id: table
            placement: center
            count: [1, 1]
        optional:
          - id: chair
            placement: free_standing
            count: [1, 2]
            chance: 0.70
          - id: candelabra
            placement: free_standing
            count: [1, 1]
            chance: 0.40
  ```
- Acceptance criteria:
  - All 14 non-Generic archetypes defined in YAML with prop recipes
  - `RoomPropPlacer.Recipes` dictionary removed from C# -- recipes come from the registry
  - Same seed produces identical prop layouts before and after migration (regression test)
  - Adding a new archetype requires only YAML edits (no C# changes)
  - New archetype added to YAML as a test (e.g., "TestArchetype") validates the loader end-to-end
  - Tests: `tests/Content/ArchetypeRecipeRegistryTests.cs` with loading, lookup, and missing-archetype cases

### PROP-010: Symmetry enforcement for bilateral/radial archetypes

- Status: complete
- Layer: logic
- Type: system
- Dependencies: none (PROP-006 already complete)
- Files to modify:
  - `src/Logic/ECS/RoomPropPlacer.cs` (add symmetry pass to optional prop placement)
- Description: Four archetypes declare symmetry in the archetype table: ThroneRoom (bilateral), Armory (bilateral), Crypt (bilateral), FountainRoom (radial). Currently `RoomPropPlacer` places optional props randomly with no mirroring.
  - **Bilateral symmetry:** Compute the room's long axis (horizontal or vertical based on Width vs Height). For each optional prop placed on one side, attempt to place a mirror copy on the opposite side. If the mirror position is invalid (wall, occupied, entrance), skip -- symmetry is best-effort, not required. Only applies to Pass 2 (optional props). Required props place first and are not mirrored (e.g., one throne, one altar).
  - **Radial symmetry:** FountainRoom places its fountain at center (required). Optional props (bench, planter, pillar) should be placed at cardinal offsets from center (N/S/E/W at equal distance). Attempt all 4 positions; place as many as the count allows. If a cardinal position is invalid, try the next.
  - Symmetry type is a per-archetype property. When recipes move to YAML (PROP-009), this becomes a `symmetry: bilateral | radial | none` field. For now, hardcode the mapping in a small lookup table.
- Acceptance criteria:
  - ThroneRoom with bilateral symmetry: if a brazier is placed at (cx-2, cy), a second brazier is attempted at (cx+2, cy)
  - FountainRoom pillars placed at cardinal offsets from center fountain
  - Connectivity validation still runs after symmetric placement
  - Symmetry is best-effort: if mirror position is blocked, the original prop still places
  - Deterministic with same seed
  - Tests: at least 4 cases covering bilateral mirror, radial placement, blocked mirror fallback, connectivity after symmetry

### PROP-011: Best-of-N layout scoring

- Status: complete
- Layer: logic
- Type: system
- Dependencies: none (PROP-006 already complete)
- Files to modify:
  - `src/Logic/ECS/RoomPropPlacer.cs` (wrap PlaceProps in a scoring loop)
- Description: Currently `RoomPropPlacer.PlaceProps` generates one layout and keeps it. Replace with a best-of-N approach:
  1. For each room, generate N candidate layouts (default N=5)
  2. Score each layout: `(required_placed * 10 + optional_placed * 3 + symmetry_bonus * 5 - connectivity_failures * 100)`
  3. Keep the highest-scoring layout
  4. RNG management: the caller provides a single `SeededRandom`. For determinism, fork N child RNGs from the parent using `rng.Next()` as seed for each child. This ensures the parent RNG advances a fixed amount regardless of which layout wins.
  5. N is a parameter on PlaceProps (default 5). Pass N=1 in tests that need exact layout control.
- Performance constraint: < 200ms per floor on mobile. The current PlaceProps runs per-room; with N=5 and ~20 rooms, that's 100 layout evaluations per floor. Each evaluation is the same flood-fill-based placement -- should be well within budget for 5-10 tile rooms.
- Acceptance criteria:
  - Same seed produces same result (deterministic across N attempts)
  - N=1 produces identical output to the current single-pass behavior
  - Layout quality improves measurably: over 100 floors with N=5 vs N=1, average score should be higher
  - Parent RNG advances a fixed amount per room regardless of N (no downstream seed drift)
  - Generation time measured via test: 100 floors with N=5 completes in < 20 seconds on dev machine
  - Tests: determinism test, N=1 equivalence test, score-improvement statistical test

### PROP-012: Maintenance state variation

- Status: complete
- Layer: logic
- Type: system
- Dependencies: none (PROP-006 already complete)
- Files to create:
  - `src/Logic/ECS/RoomMaintenanceState.cs` (enum)
- Files to modify:
  - `src/Logic/ECS/Room.cs` (add `MaintenanceState` property)
  - `src/Logic/ECS/RoomPropPlacer.cs` (density modifier, scatter overlay, jitter)
  - `src/Logic/ECS/MapGenerator.cs` (assign maintenance state during generation)
- Description: Rooms currently feel uniformly "fresh" regardless of depth. Add a maintenance state per room assigned during generation:
  - **WellMaintained** -- full prop density, no scatter. Rare (10% on depth 1-2 only).
  - **Normal** -- current behavior. Default state. 50% of rooms depth 1-3, drops off deeper.
  - **Neglected** -- 80% density multiplier, props may be offset 0-1 tiles from ideal position (jitter applied after initial placement if the jittered position is valid). 30% of rooms depth 2-4, increasing deeper.
  - **Abandoned** -- 60% density multiplier, 1-2 rubble/cobweb scatter overlays added regardless of archetype. 20% of rooms depth 3-5, increasing deeper.
  - **Ruined** -- 40% density multiplier, 2-4 rubble/bones_pile scatter overlays. Required props may be removed (50% chance each). Primarily depth 4+.
  - Assignment uses a depth-weighted random roll. Deeper floors bias toward worse states. The exact distribution is configurable but starts with the percentages above.
  - Jitter: for Neglected/Abandoned, after initial prop placement, each optional prop has a 40% chance to shift 1 tile in a random cardinal direction. If the shifted position is valid (walkable, not occupied, not entrance/margin), move the prop. If not, keep original position. Connectivity is re-validated after all jitter.
- Acceptance criteria:
  - `RoomMaintenanceState` enum with 5 values
  - Room record gains `MaintenanceState` property (default Normal)
  - Maintenance state assigned per room during generation based on depth + RNG
  - Density multiplier correctly reduces maxProps for Neglected/Abandoned/Ruined
  - Ruined rooms have rubble/bones scatter overlays even in Generic archetype rooms
  - Jitter applied to Neglected/Abandoned rooms without breaking connectivity
  - Deterministic with same seed
  - Tests: state assignment distribution by depth, density modifier application, jitter validity, ruined scatter placement

---

## Track B: Door System

Visual doors placed at corridor-room boundaries. Doors are walkable (pass-through) -- no open/closed/locked state in this plan. That functionality is deferred to `plan_doors_secrets_portals.md`. These are "visual doors" that make rooms feel enclosed.

### DOOR-001: Door placement logic

- Status: complete
- Layer: logic
- Type: system
- Dependencies: none
- Files to create:
  - `src/Logic/ECS/DoorPlacer.cs`
- Files to modify:
  - `src/Logic/ECS/MapGenerator.cs` (call DoorPlacer after corridor carving, before prop placement)
  - `src/Logic/ECS/GeneratedMap.cs` (add `IReadOnlyList<(int X, int Y)> DoorPositions` property)
- Description: New `DoorPlacer` static class that scans corridor-room boundaries and places `TileKind.Door` tiles at chokepoints.

  Algorithm:
  1. Iterate all tiles on the map. For each tile that is `TileKind.Corridor`:
     a. Check if any cardinal neighbor is `TileKind.Floor` (a room tile).
     b. If yes, this corridor tile is a candidate door position.
     c. Validate chokepoint: the tile must have exactly 2 cardinal wall neighbors on opposite axes (i.e., walls N+S with open E+W, or walls E+W with open N+S). This ensures the door is at a single-tile-wide passage, not in the middle of a wide corridor or room interior.
     d. Skip if the tile is a stair tile.
  2. For each valid candidate, call `map.SetTile(x, y, TileKind.Door)`.
  3. Return the list of door positions for GeneratedMap.

  `TileKind.Door` is already in the enum and already mapped to walkable in `GameMap.SetTile`. No changes needed to walkability logic.

  Door placement runs after all corridors are carved and the connectivity check completes, but before prop placement. This ordering is important because:
  - `RoomPropPlacer.FindEntrancesAndMargins` currently detects entrances by scanning for corridor tiles adjacent to room floor tiles. Door tiles will need to be treated as equivalent to corridor tiles for entrance detection. Add `TileKind.Door` to the entrance scan condition in `RoomPropPlacer`.
  - Props must not be placed on door tiles. Door positions should be added to the Forbidden set in the placement grid.

- Files also modified:
  - `src/Logic/ECS/RoomPropPlacer.cs` (entrance detection includes Door tiles; door tiles are Forbidden in grid)

- Acceptance criteria:
  - Every corridor-room boundary where the corridor is 1 tile wide gets a door tile
  - No door placed at stair positions
  - No door placed where the corridor is 2+ tiles wide (would be an ineffective door)
  - Door tiles are walkable (player and monsters pass through)
  - `RoomPropPlacer` detects door tiles as entrances and forbids props on them
  - GeneratedMap exposes door positions for the renderer
  - Deterministic with same seed
  - Tests: `tests/ECS/DoorPlacerTests.cs` with at least 8 cases:
    - Single corridor meets room: door placed
    - Wide corridor (2-tile): no door
    - Stair tile: no door
    - L-corridor with two room-adjacent tiles: door at each
    - Room with multiple corridors: multiple doors
    - Door positions included in GeneratedMap
    - RoomPropPlacer treats doors as entrances
    - Connectivity preserved after door placement

### DOOR-002: Door rendering in DungeonRenderer

- Status: complete
- Layer: presentation
- Type: system
- Dependencies: DOOR-001, door tile ID from Rafe
- Files to modify:
  - `config/tile_themes.yaml` (add `door` tile ID under sandstone theme)
  - `src/Presentation/TileThemeConfig.cs` (add `GetDoorTile(string theme)` method)
  - `src/Presentation/Map/DungeonRenderer.cs` (add door overlay pass or handle in stair overlay pass)
- Description: Extend the stair overlay pass (Pass 2) in `DungeonRenderer` to also handle `TileKind.Door`. When a door tile is encountered:
  1. Render the floor tile as usual in Pass 1 (doors have a floor underneath).
  2. In Pass 2, render a door overlay sprite on top at ZIndex = tile sort order + 1 (same band as stairs).
  3. Look up door tile ID from `TileThemeConfig.GetDoorTile(themeName)`.
  4. If no door tile ID is configured (theme has no door tile), skip the overlay silently -- the door is invisible but still functions correctly for gameplay (walkable, detected by prop placer as entrance).
  5. Track door overlay sprites in TileLayer for FOV modulation.

  Directional doors: if `tile_themes.yaml` defines `door_h` and `door_v` (horizontal and vertical variants), pick based on the door's corridor direction. The corridor direction can be inferred from the door's wall neighbors: if walls are N+S, the passage runs E-W (horizontal door). If walls are E+W, the passage runs N-S (vertical door). If only one tile ID is defined (just `door`), use it for both orientations.

- YAML addition to `config/tile_themes.yaml`:
  ```yaml
  sandstone:
    door: [???]        # Single door tile, or:
    door_h: [???]      # Horizontal passage door
    door_v: [???]      # Vertical passage door
  ```

- Acceptance criteria:
  - Door tiles render with an overlay sprite at the correct position
  - Doors respect FOV (visible/explored/hidden like all other tiles)
  - Missing door tile ID falls back gracefully (no crash, invisible door)
  - Door direction detected from wall neighbor pattern

### DOOR-003: Door integration tests and visual verification

- Status: complete (covered by DoorPlacerTests.cs)
- Layer: both
- Type: test
- Dependencies: DOOR-001, DOOR-002
- Files to create:
  - `tests/ECS/DoorIntegrationTests.cs`
- Description: Integration tests that generate full dungeon floors and verify door placement properties across multiple seeds. Also includes a visual verification checklist for Godot.
- Acceptance criteria:
  - Over 50 generated floors (seeds 1-50): every floor has at least 1 door
  - No floor has a connectivity regression (all rooms reachable)
  - No door placed on a stair tile
  - Average doors per floor is reasonable (roughly equal to number of corridor-room connections)
  - Visual verification in Godot: doors appear at room entrances, look correct

---

## Track C: Special Rooms

Rare, pre-designed rooms that break the procedural rhythm. These are post-generation modifications to existing rooms -- they don't change the room placement algorithm, they tag and modify rooms after the standard generation pipeline.

### SROOM-001: Dead-end room tagging and loot bias

- Status: complete
- Layer: logic
- Type: system
- Dependencies: none
- Files to modify:
  - `src/Logic/ECS/Room.cs` (add `IsDeadEnd` boolean property or add DeadEnd as a room tag/flag)
  - `src/Logic/ECS/MapGenerator.cs` (post-generation pass to tag dead-end rooms)
  - `src/Logic/Core/EntityPlacer.cs` (boost item spawn in dead-end rooms)
- Description: After all rooms are placed and corridors carved, scan for dead-end rooms: rooms connected by exactly 1 corridor AND with walkable area <= 16 tiles. Tag these rooms so EntityPlacer can give them a loot bias.

  Detection algorithm:
  1. For each room, count how many corridor segments connect to it. A corridor segment "connects to" a room if any tile in the segment is within 1 cardinal step of the room's bounding box (within its walkable tiles).
  2. If a room has exactly 1 connection and walkable area <= 16, tag it as DeadEnd.
  3. First room (player spawn) and last room (stair) are never tagged as DeadEnd.

  EntityPlacer modification: when placing floor items, dead-end rooms get a 2x item count multiplier (if a room would normally get 0-1 items, dead-end rooms get 1-2). This is a simple bias -- full loot policy is in `plan_loot_policy.md`.

  Room tagging: add `bool IsDeadEnd { get; init; }` to Room record (default false). This is lightweight and avoids a whole new archetype -- dead-end is a structural property, not a semantic archetype.

- Acceptance criteria:
  - Rooms with exactly 1 corridor connection and <= 16 walkable tiles are tagged
  - First and last rooms are never tagged
  - Dead-end rooms get increased item spawns
  - Tagging is deterministic with same seed
  - Tests: `tests/ECS/SpecialRoomTests.cs` with dead-end detection cases

### SROOM-002: Grand Shrine upgrade

- Status: complete
- Layer: logic
- Type: system
- Dependencies: PROP-010 (symmetry enforcement, for radial symmetry)
- Files to modify:
  - `src/Logic/ECS/RoomPropPlacer.cs` (add Grand Shrine recipe override)
  - `src/Logic/Core/EntityPlacer.cs` (place reward item at altar position in Grand Shrines)
- Description: When a Shrine archetype room has walkable area >= 36, upgrade it to "Grand Shrine" behavior:
  1. Force radial symmetry for all prop placement (not just FountainRoom).
  2. Override the recipe to guarantee: altar (center), 2 braziers (flanking altar E and W), candle ring (4 candles at cardinal offsets from altar), and 1-2 statues (free-standing, symmetrically placed).
  3. Place a real item entity at the altar position (a guaranteed reward). The item is drawn from the floor's loot table with a rarity bias (minimum uncommon). Item placement goes through EntityPlacer, not through the prop system -- this is a real pickup, not a decorative prop.

  The Grand Shrine is not a new archetype -- it's a recipe override that activates conditionally within the Shrine archetype. This keeps the archetype system simple while adding dramatic visual variety.

  Implementation: in `RoomPropPlacer.PlaceProps`, before running the standard recipe, check if `room.Archetype == Shrine && walkable >= 36`. If so, substitute the Grand Shrine recipe and enable radial symmetry. After prop placement, record the altar position in `PlacedProp` metadata (or return it as part of GeneratedMap's special positions) so EntityPlacer can place the reward item there.

- Acceptance criteria:
  - Shrine rooms with >= 36 walkable tiles use the Grand Shrine recipe
  - Grand Shrine has radial symmetry (braziers/candles at symmetric positions)
  - A real item entity is placed at the altar position
  - Smaller Shrine rooms (< 36 walkable) use the standard Shrine recipe unchanged
  - Tests: Grand Shrine detection, recipe override, altar position tracking

### SROOM-003: Vault room designation

- Status: complete
- Layer: logic
- Type: system
- Dependencies: DOOR-001 (doors, for vault entrance concept)
- Files to modify:
  - `src/Logic/ECS/Room.cs` (add `IsVault` boolean property)
  - `src/Logic/ECS/MapGenerator.cs` (post-generation vault designation pass)
  - `src/Logic/Core/EntityPlacer.cs` (guaranteed item in vault rooms, monster upgrade)
- Description: After normal room placement, designate one room per floor (on depth 3+) as a vault. Based on the Python prototype's `designate_vaults` pattern.

  Selection criteria:
  1. Not the first room (player spawn) or last room (stair exit).
  2. Walkable area >= 25 tiles.
  3. Not already a Grand Shrine.
  4. Roll: 15% chance on depth 3-4, 20% on depth 5-6, 25% on depth 7+. If no roll succeeds, no vault on this floor (vaults are optional).

  Vault properties:
  - Tagged `IsVault = true` on the Room record.
  - EntityPlacer places 1-2 guaranteed items with rarity bias (minimum uncommon, 30% chance of rare).
  - EntityPlacer spawns one upgraded monster: same type as would normally spawn but with +2 to all stats (HP, AC, damage). This is the "vault guardian."
  - Visually: vault rooms use the Generic archetype (no prop recipe override) but get 1-2 chest_closed props placed as a visual indicator. The actual loot is entity items, not the chest props.

  Note: The Python prototype's vault system uses golden wall tiles and door locking. This plan implements the simpler version: room tagging + guaranteed loot + guardian monster. Locked doors and visual distinction are deferred to `plan_doors_secrets_portals.md`.

- Acceptance criteria:
  - Vault designation runs only on depth 3+
  - At most 1 vault per floor
  - Vault rooms get guaranteed items and a guardian monster
  - First/last rooms never become vaults
  - Vault chance increases with depth
  - Deterministic with same seed
  - Tests: vault designation at various depths, no vault on depth 1-2, guaranteed item/monster placement

---

## Track D: Corridor Polish

Improvements to corridor carving that make connections between rooms feel less mechanical.

### CORR-001: Corridor width variation

- Status: deferred (intentionally removed — MST layout algorithm makes wide corridors impractical)
- Layer: logic
- Type: system
- Dependencies: none
- Files to modify:
  - `src/Logic/ECS/MapGenerator.cs` (modify ConnectRooms, CarveHTunnel, CarveVTunnel)
- Description: Currently all corridors are 1 tile wide. Add optional 2-wide corridors for some connections.

  Implementation:
  1. In `ConnectRooms`, after deciding H-then-V or V-then-H, roll a 30% chance for wide corridor.
  2. If wide: for each tunnel segment, carve the parallel row/column as well (H tunnel at y also carves y+1; V tunnel at x also carves x+1).
  3. Only carve the parallel row if it stays in bounds and doesn't overlap an existing room's interior (to avoid creating unwanted room connections).
  4. Record corridor width in `CorridorSegment` (add an `int Width` property, default 1).
  5. Wide corridors affect door placement: `DoorPlacer` should skip 2-wide corridors (a single door tile can't seal a 2-wide passage).

- CorridorSegment change: `public sealed record CorridorSegment(int X1, int Y1, int X2, int Y2, int Width = 1);`

- Acceptance criteria:
  - ~30% of corridor connections are 2 tiles wide
  - Wide corridors stay in map bounds
  - Wide corridors don't accidentally merge into room interiors
  - DoorPlacer does not place doors at wide corridor boundaries
  - Deterministic with same seed
  - Tests: wide corridor carving bounds check, DoorPlacer skip for wide, width recorded in CorridorSegment

### CORR-002: Corridor alcoves / widenings

- Status: deferred
- Layer: logic
- Type: system
- Dependencies: CORR-001 (uses CorridorSegment width info)
- Files to modify:
  - `src/Logic/ECS/MapGenerator.cs` (post-carve pass over corridors)
- Description: At the midpoint of long corridors (> 6 tiles), occasionally carve a small widening. This breaks the "narrow tube" monotony and creates natural-feeling gathering points.

  Implementation:
  1. After all rooms and corridors are carved, iterate `GeneratedMap.Corridors`.
  2. For each corridor segment longer than 6 tiles, roll 20% chance.
  3. If triggered: find the midpoint tile. Carve a 2x2 or 3x2 widening perpendicular to the corridor direction. Carve as `TileKind.Corridor` (not Floor -- these are corridor widenings, not rooms).
  4. Bounds checking: all carved tiles must be in bounds and currently Wall. Skip if any target tile is already carved (would merge into another space unexpectedly).

- Acceptance criteria:
  - ~20% of long corridors (> 6 tiles) get a midpoint widening
  - Widenings are 2x2 or 3x2 tiles perpendicular to the corridor
  - No widening carved outside map bounds
  - No widening that merges into an existing room or other corridor
  - Deterministic with same seed
  - Tests: long corridor gets widening, short corridor does not, bounds respected, no merge into room

### CORR-003: Dead-end corridor stubs

- Status: deferred
- Layer: logic
- Type: system
- Dependencies: none
- Files to modify:
  - `src/Logic/ECS/MapGenerator.cs` (post-carve stub generation pass)
- Description: After all rooms are connected, occasionally extend a short branch from a corridor into solid wall. These dead-end stubs give the map a more organic, explorable feel. They serve as future placement sites for traps, secrets, or hidden items (from `plan_traps_chests_features.md`).

  Implementation:
  1. After all corridors are carved, roll 25% chance per floor to add stubs.
  2. If triggered: pick 1-2 corridor tiles that are in the interior of a corridor (not adjacent to a room). For each, pick a perpendicular direction that is currently Wall.
  3. Carve 3-5 tiles in that direction as `TileKind.Corridor`. Stop if you hit an existing carved tile (avoid merging) or go out of bounds.
  4. Cap at 2 stubs per floor.

- Acceptance criteria:
  - 0-2 dead-end stubs per floor (probabilistic, 25% chance of any)
  - Stubs are 3-5 tiles long, perpendicular to the source corridor
  - Stubs never merge into rooms or other corridors
  - Stubs are carved as Corridor tiles (not Floor)
  - Deterministic with same seed
  - Tests: stub generation, length bounds, no-merge check, cap enforcement

---

## Task Execution Order

Dependencies are minimal between tracks. Within each track, tasks are ordered by dependency.

**Can start immediately (no dependencies):**
- PROP-009 (YAML recipes)
- PROP-010 (symmetry)
- PROP-011 (best-of-N)
- PROP-012 (maintenance state)
- DOOR-001 (door placement logic)
- SROOM-001 (dead-end rooms)
- CORR-001 (corridor width)
- CORR-002 (corridor alcoves)
- CORR-003 (dead-end stubs)

**Blocked on preceding tasks:**
- DOOR-002 (needs DOOR-001 + door tile ID from Rafe)
- DOOR-003 (needs DOOR-001 + DOOR-002)
- SROOM-002 (needs PROP-010 for radial symmetry)
- SROOM-003 (needs DOOR-001 for vault entrance concept, though vault works without doors)

**Suggested build order for a single builder:**
1. DOOR-001 -- highest visual impact, unlocks DOOR-002/003 and SROOM-003
2. CORR-001 -- corridor width variation, fast to build
3. CORR-002 + CORR-003 -- corridor alcoves and stubs, fast
4. SROOM-001 -- dead-end detection, fast
5. PROP-010 -- symmetry, medium complexity
6. SROOM-002 -- Grand Shrine, builds on PROP-010
7. PROP-012 -- maintenance state, medium complexity
8. PROP-011 -- best-of-N scoring, medium complexity
9. PROP-009 -- YAML migration, highest risk of regression
10. SROOM-003 -- vault designation, needs EntityPlacer changes
11. DOOR-002 -- presentation, blocked on tile ID
12. DOOR-003 -- integration tests

---

## Performance Constraints

- Floor generation must complete in < 200ms on mobile (iPhone 12 baseline)
- Current generation (rooms + shapes + corridors + props) is well under budget
- Best-of-N (PROP-011) is the highest risk for perf: N=5 multiplies prop placement work 5x per room. With ~20 rooms and 5-10 tile rooms, this is ~100 small flood fills per floor -- should be fine but must be measured
- Corridor polish (CORR-001/002/003) adds minimal overhead -- single-pass scans over a ~120x80 grid
- Door placement (DOOR-001) is a single scan pass -- negligible

## Scenario Harness Safety

All balance scenarios use `GameMap.CreateArena()` for map construction, not `MapGenerator.Generate()`. None of the changes in this plan affect arena construction, combat resolution, or entity stats. The scenario harness and all balance tests are unaffected.

Verification: after implementing any task, run `dotnet test --filter "Category!=Slow"` to confirm no regressions.

---

## Open Decisions

### Decision 1: Door tile IDs
**Status:** Needs Rafe input
**Question:** What tile IDs from the Oryx 16bf world_24x24 sheet should be used for door sprites? Are there directional variants (horizontal/vertical)?
**Impact:** Blocks DOOR-002 (presentation). DOOR-001 (logic) can proceed without this.

### Decision 2: Vault loot policy
**Status:** Needs design decision
**Question:** Vault rooms guarantee items with rarity bias. What should the minimum rarity be? The Python prototype uses "rare/legendary." For the C# version, the loot policy system (`plan_loot_policy.md`) isn't built yet. Options:
- (A) Hardcode "guaranteed 1-2 items from the floor's item pool with no rarity filter" (simplest, defers rarity to loot policy plan)
- (B) Add a simple rarity bias (minimum uncommon) ahead of the full loot policy system
- (C) Defer vault loot entirely until loot policy is implemented

**Recommendation:** Option A. Place items from the existing floor item pool. The vault guardian monster provides the challenge; the guaranteed item is the reward. Rarity refinement comes later.

### Decision 3: Grand Shrine reward item
**Status:** Needs design decision
**Question:** Grand Shrine altar places a "real item entity." Same question as vaults -- what item? Options:
- (A) Random item from floor pool (same as vault recommendation)
- (B) Always a potion (thematic -- shrine = blessing)
- (C) A new "shrine blessing" consumable (future feature)

**Recommendation:** Option A for now. Grand Shrines are rare enough that a floor-pool item feels rewarding without needing special logic.

### Decision 4: CorridorSegment Width -- breaking change?
**Status:** Technical decision
**Question:** Adding `int Width = 1` to the `CorridorSegment` record is backwards-compatible (default parameter). But some code may pattern-match on CorridorSegment. Should we verify all usages first?
**Answer:** CorridorSegment is only used in MapGenerator (creation) and GeneratedMap (storage). No external consumers pattern-match on it. The default parameter is safe.

---

## Risks

1. **PROP-009 regression risk.** Migrating hardcoded recipes to YAML is the highest-risk task. A subtle difference in YAML parsing (e.g., float precision on chance values, int parsing for count ranges) could change prop layouts. Mitigation: write a deterministic seed-comparison test before migration, validate that output is identical after.

2. **Best-of-N RNG determinism.** PROP-011 forks the RNG for N candidate layouts. If the fork strategy isn't implemented carefully, downstream generation (monster placement, loot) could shift. Mitigation: use a fixed-advance pattern -- advance the parent RNG by N positions at the start (one per candidate seed), then run candidates in order.

3. **Door placement edge cases.** Some room shapes (Cave, Alcove) have irregular perimeters that may produce unexpected corridor-room boundary patterns. A cave room with multiple protrusions touching a corridor could generate multiple doors in close proximity. Mitigation: add a minimum-distance-between-doors constraint (no two doors within 2 tiles of each other).

4. **Corridor width and pathfinding.** Wide corridors are purely visual in this plan (all tiles are walkable). But monsters using BasicMonsterAI path through corridors. 2-wide corridors shouldn't cause AI issues since A* works on walkable tiles regardless of width. No risk expected, but worth a quick pathfinding test.

5. **Vault guardian monster stats.** SROOM-003 adds +2 to all stats for the vault guardian. This is outside the balance pipeline's measurement scope (scenarios don't generate dungeons). Risk of over/under-tuning. Mitigation: flag for manual playtesting, and revisit when the dungeon soak harness (`plan_testing_infra_phase1.md`) is available.
