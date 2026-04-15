# Plan: Dungeon Visual Overhaul

**Status:** in-progress
**Supersedes:** `PLAN_wall_autotile.md` (absorbed as Phase 0)

## Current State

Phase 1 and Phase 2 implementation complete (2026-04-15). P1-001 through P1-010 and P2-001 through P2-007 all done. P0-006 (visual verification) still requires running Godot.

**What was just done:** Phase 1 — room shape variety (RoomShapeGenerator, 6 shape carvers, 45 new tests, 1150 total). Phase 2 — floor composition pipeline (SimplexNoise, FloorComposer with edge darkening + noise variation, DungeonRenderer wired, FloorWorn/GetFloorDark/GetFloorAccent/GetFloorWorn added).

**Next step:** P0-006 — boot the game and visually verify wall rendering + room shape variety + edge-darkened floors. Then: pick distinct tile IDs for floor_dark, floor_accent, floor_worn in tile_themes.yaml (all currently 774 placeholder).

**Open issues:** floor_dark/floor_worn tile IDs are placeholder (774 = same as primary). Visual edge darkening effect won't be visible until Rafe picks different tile IDs via tools/sprite_browser_16bf_world.html.

## Overview

Three phases that together transform the dungeon from "programmer art rectangles" to "this looks designed."

- **Phase 0 -- Wall Autotile Fix.** The hybrid cardinal+diagonal algorithm, role-based tile config, verified tile IDs. Entirely presentation layer. This is the prerequisite for everything visual.
- **Phase 1 -- Room Shape Variety.** Replace rectangular-only rooms with L-shapes, caves, circles, alcoves, and corridor-rooms. Entirely logic layer (pure C#, no Godot). The single highest-impact change for visual quality.
- **Phase 2 -- Floor Composition Pipeline.** Multi-pass floor decoration: edge darkening, noise variation, scatter, checkered patterns, worn paths. Entirely presentation layer.

Phase 1 and Phase 2 can run in parallel after Phase 0 completes (logic vs presentation, no dependency between them).

## What Is NOT In Scope

- Combat, AI, balance, ECS, balance pipeline, harness -- untouched
- IsometricRenderer -- stays dormant
- Room archetypes and props (Layer 4b in the design doc -- future plan)
- Level feelings and theme blending (Layer 5 in the design doc -- future plan)
- LoopBuilder layout algorithm (Layer 2 in the design doc -- future plan)
- Additional theme tile sets (crypt, moss) -- separate plan

## Reference

- Design doc: `docs/floor-and-room-design.md` (Layers 3, 4a, 5)
- Absorbed plan: `tasks/plans/PLAN_wall_autotile.md`
- Current renderer: `src/Presentation/Map/DungeonRenderer.cs`
- Current config: `src/Presentation/TileThemeConfig.cs`
- YAML loader: `src/Presentation/TileThemeLoader.cs`
- Tile config: `config/tile_themes.yaml`
- Map generator: `src/Logic/ECS/MapGenerator.cs`
- Room record: `src/Logic/ECS/Room.cs`
- GameMap: `src/Logic/ECS/GameMap.cs`
- Entity placement: `src/Logic/Core/EntityPlacer.cs`
- Floor builder: `src/Logic/Core/DungeonFloorBuilder.cs`
- Python prototype rooms: `~/development/rlike/map_objects/room_generators.py` (type-based but rectangular only)
- Python prototype map gen: `~/development/rlike/map_objects/game_map.py`

## Key Architectural Facts (from code audit)

1. **Room is a sealed record:** `Room(int X, int Y, int Width, int Height)` -- purely rectangular. Non-rectangular shapes need a different representation or Room must evolve.

2. **EntityPlacer.FindFreePosition already handles non-rectangular rooms.** It iterates the Room's bounding box but filters by `map.IsWalkable(x, y)`. A cave room carved inside the bounding box will place entities only on walkable tiles.

3. **DungeonFloorBuilder.AssignTileThemes uses `map.SetTileThemeRect` over room bounds.** This will over-paint wall tiles for non-rectangular rooms, but that is harmless -- wall tiles always render using the wall autotile lookup regardless of theme. The theme only affects floor tile selection.

4. **MapGenerator uses Room for intersection testing, center computation, and Contains checks.** Non-rectangular rooms can keep the same bounding box for overlap detection (conservative -- prevents rooms from clashing) while carving a different shape inside the bounding box.

5. **GeneratedMap.Rooms is `IReadOnlyList<Room>`.** All downstream consumers (EntityPlacer, DungeonFloorBuilder, theme assignment) iterate this list. The Room type can be extended or wrapped without breaking consumers as long as bounding box properties remain available.

6. **No simplex noise exists in the C# codebase.** Floor composition pipeline will need a minimal implementation in the logic layer (pure math, no Godot deps).

---

## Phase 0: Wall Autotile Fix

**Layer:** Presentation only. Logic layer: zero changes.
**Prerequisite for:** Phase 1 and Phase 2 (walls must render correctly first).

### TASK-P0-001: Complete tile ID audit for all wall roles

- Status: ✅ complete
- Notes: Decision taken (option A): full switch to TMX sandstone tile set (183-199 range). grey_stone theme renamed sandstone. TMX-verified IDs provided by Rafe and applied directly.
- Layer: presentation (asset inspection)
- Type: art direction
- Dependencies: none
- Description: Systematically identify every tile ID needed for the hybrid autotile algorithm. The TMX pixel-matching work has confirmed partial mappings (corners 189-192, edges 184/187/198, floors 746-748). Gaps remain: south-facing edge, T-junction directions, interior fill, dead-end caps, isolated pillar, cross/intersection.
- Method:
  1. Use `tools/sprite_browser_16bf_world.html` to inspect tiles 183-199 systematically
  2. Verify the TMX-established mappings: 184=edge_north, 187=edge_west, 198=edge_east, 189-192=outer corners
  3. Map unmapped IDs in the 183-199 range: 183, 185, 186, 188, 193, 194, 195, 196, 197, 199
  4. Identify interior fill candidate (solid dark tile -- may be 188 or in a different range)
  5. For each bitmask 0-14, determine which tile from the 183-199 range matches (or confirm the current 1095-1109 IDs are better for those roles)
  6. Decide: full switch to 183-199 TMX set, or hybrid (183-199 for diagonal roles, keep 1095-1109 for cardinal roles)?
- Output: Complete mapping table added to this plan under "Verified Tile ID Reference" section
- Acceptance criteria:
  - Every role needed by the hybrid algorithm has a tile ID assigned
  - Interior fill tile identified (this is the most visible current bug)
  - All assigned IDs verified to exist as files in `world_24x24/`
  - Decision documented: TMX-only vs hybrid tile set

**DECISION NEEDED (Rafe):** The 183-199 range (TMX sandstone) and 1095-1109 range (current grey stone) are two different visual styles. The TMX set has proven outer corner tiles. Options: (A) full switch to TMX set, (B) keep 1095-1109 for cardinals + add 183-199 for diagonals, (C) find outer corners in the 1095-1109 family. Recommendation: option A (TMX set is internally consistent).

### TASK-P0-002: Redesign TileThemeData for role-based wall mapping

- Status: ✅ complete
- Files changed: `src/Presentation/TileThemeConfig.cs`
- Notes: Added WallDiagonal dict to TileThemeData; added FloorDark and FloorInterior for Phase 2 pipeline. GetWallTile() implements the hybrid algorithm. GetAutoWallTile() delegates to GetWallTile with diagonalFloorMask=0 for backwards compat.
- Layer: presentation
- Type: system
- Dependencies: TASK-P0-001
- Files to modify:
  - `src/Presentation/TileThemeConfig.cs`
- Description: Add `WallDiagonal` dictionary to `TileThemeData` alongside the existing `WallAutotile`. Create new `GetWallTile(theme, cardinalMask, diagonalFloorMask)` method that implements the hybrid lookup: cardinal mask 0-14 uses `WallAutotile`, cardinal mask 15 checks `WallDiagonal` for outer corners vs interior fill. Keep `GetAutoWallTile` as deprecated wrapper for backwards compatibility.
- New data structure:
  ```csharp
  // Add to TileThemeData:
  public Dictionary<string, int> WallDiagonal { get; set; } = new();
  // Keys: "corner_outer_nw", "corner_outer_ne", "corner_outer_sw",
  //        "corner_outer_se", "interior_fill"
  ```
- New method signature:
  ```csharp
  public string? GetWallTile(string theme, int cardinalMask, int diagonalFloorMask)
  ```
- Algorithm:
  1. cardinalMask < 15: look up `WallAutotile[cardinalMask]` (same as current)
  2. cardinalMask == 15 AND diagonalFloorMask > 0: map diagonal bits to corner role name, look up `WallDiagonal`
  3. cardinalMask == 15 AND diagonalFloorMask == 0: look up `WallDiagonal["interior_fill"]`
  4. Fallback: if `WallDiagonal` missing or key not found, fall back to `WallAutotile[15]`
- Acceptance criteria:
  - `GetWallTile("grey_stone", 15, 0)` returns interior fill tile
  - `GetWallTile("grey_stone", 15, 2)` returns SE outer corner (bit 1 = SE floor)
  - `GetWallTile("grey_stone", 7, 0)` returns bitmask-7 cardinal tile (unchanged)
  - Backwards-compatible: themes without `WallDiagonal` fall back to `WallAutotile[15]`
  - Build: 0 errors

### TASK-P0-003: Update TileThemeLoader for wall_diagonal YAML block

- Status: ✅ complete
- Files changed: `src/Presentation/TileThemeLoader.cs`
- Notes: Added InDiagonal parse state. wall_diagonal entries are parsed as string key → int value at indent >= 6. floor_dark and floor_interior list roles added to the switch. Backwards-compatible: themes without wall_diagonal load without errors.
- Layer: presentation
- Type: system
- Dependencies: TASK-P0-002
- Files to modify:
  - `src/Presentation/TileThemeLoader.cs`
- Description: Extend the manual YAML parser to handle `wall_diagonal:` as a new block type at indent >= 4. Entries are string key -> int value at indent >= 6 (same pattern as `wall_autotile` but with string keys instead of int keys). Add `InDiagonal` parser state.
- New YAML structure:
  ```yaml
  wall_diagonal:
    corner_outer_nw: 189
    corner_outer_ne: 190
    corner_outer_sw: 191
    corner_outer_se: 192
    interior_fill: 188
  ```
- Parser changes:
  - New `ParseState.InDiagonal` state (parallel to `InAutotile`)
  - When key is `wall_diagonal` at indent 4: enter `InDiagonal` state
  - In `InDiagonal` state at indent >= 6: parse `string_key: int_value` into `WallDiagonal`
  - Exit `InDiagonal` when indent drops below 6 (same pattern as `InAutotile`)
- Acceptance criteria:
  - Loader parses `wall_diagonal` block with string keys
  - `WallDiagonal["corner_outer_nw"]` populated correctly
  - Old YAML without `wall_diagonal` loads without errors (backwards-compatible)
  - Build: 0 errors

### TASK-P0-004: Update tile_themes.yaml with verified tile IDs

- Status: ✅ complete
- Files changed: `config/tile_themes.yaml`
- Notes: grey_stone theme removed and replaced with sandstone. All 16 wall_autotile entries updated to TMX-verified IDs. wall_diagonal block added with 5 entries (4 corners + interior_fill). floor_dark and floor_interior roles added. Old 1095-1109 IDs gone.
- Layer: presentation (config only)
- Type: art direction
- Dependencies: TASK-P0-001, TASK-P0-003
- Files to modify:
  - `config/tile_themes.yaml`
- Description: Add `wall_diagonal` block to grey_stone and dirt themes with the tile IDs determined in TASK-P0-001. Optionally update `wall_autotile` entries if switching to the TMX tile set. Update floor tiles to TMX-verified IDs if decision in TASK-P0-001 favors it.
- Acceptance criteria:
  - YAML loads without parser errors
  - All referenced tile IDs exist as files on disk
  - `wall_diagonal` block has all 5 entries (4 corners + interior_fill)
  - Both grey_stone and dirt themes updated

### TASK-P0-005: Implement hybrid autotile algorithm in DungeonRenderer

- Status: ✅ complete
- Files changed: `src/Presentation/Map/DungeonRenderer.cs`
- Notes: ComputeWallBitmask replaced with ComputeWallMasks returning (Cardinal, Diagonal) tuple. Diagonal only computed when cardinal==15. ThemeToConfigName returns "sandstone" for all TileTheme values. Wall tile lookup calls GetWallTile(). Build: 0 errors.
- Layer: presentation
- Type: system
- Dependencies: TASK-P0-002
- Files to modify:
  - `src/Presentation/Map/DungeonRenderer.cs`
- Description: Replace `ComputeWallBitmask` with `ComputeWallMasks` returning `(int Cardinal, int Diagonal)`. Diagonal bits are only computed when cardinal == 15. Update the wall tile lookup in `Render()` to call `themeConfig.GetWallTile(themeName, cardinal, diagonal)`.
- Implementation:
  ```csharp
  private static (int Cardinal, int Diagonal) ComputeWallMasks(GameMap map, int x, int y)
  {
      int cardinal = 0;
      if (!map.IsWalkable(x,     y - 1)) cardinal |= 8; // N
      if (!map.IsWalkable(x,     y + 1)) cardinal |= 4; // S
      if (!map.IsWalkable(x + 1, y    )) cardinal |= 2; // E
      if (!map.IsWalkable(x - 1, y    )) cardinal |= 1; // W

      int diagonal = 0;
      if (cardinal == 15)
      {
          if (map.IsWalkable(x + 1, y - 1)) diagonal |= 8; // NE floor
          if (map.IsWalkable(x - 1, y - 1)) diagonal |= 4; // NW floor
          if (map.IsWalkable(x + 1, y + 1)) diagonal |= 2; // SE floor
          if (map.IsWalkable(x - 1, y + 1)) diagonal |= 1; // SW floor
      }
      return (cardinal, diagonal);
  }
  ```
- Acceptance criteria:
  - Wall tile selection uses both cardinal and diagonal masks
  - Room corners show outer corner tiles (not interior fill)
  - Interior walls show solid fill tile
  - Build: 0 errors

### TASK-P0-006: Visual verification -- wall rendering

- Status: ⬜ not started (requires running Godot game)
- Layer: presentation
- Type: calibration
- Dependencies: TASK-P0-004, TASK-P0-005
- Description: Boot the game and verify correct wall rendering across all tile configurations: room edges, room corners (outer corners), interior fill, corridors, T-junctions, corridor-room intersections.
- Verification checklist:
  - [ ] Room edges show directional edge tiles
  - [ ] Room corners show outer corner tiles (NOT interior fill)
  - [ ] Interior walls show solid fill
  - [ ] Corridors have correct edge tiles on both sides
  - [ ] T-junctions where corridors meet rooms render correctly
  - [ ] No missing-tile console errors
  - [ ] Floor tiles render correctly
  - [ ] Bones decorations still appear
  - [ ] Stairs render correctly
  - [ ] FOV dimming works on wall tiles
  - [ ] Minimap unaffected
- Acceptance criteria:
  - All checklist items pass
  - Room boundaries visually distinct from interior fill
  - No GD.PrintErr related to tile loading

---

## Phase 1: Room Shape Variety

**Layer:** Logic only. Pure C#, no Godot dependencies.
**Can run in parallel with Phase 2 after Phase 0 completes.**

### Design Decisions

**Room representation strategy:** The current `Room` record is `(X, Y, Width, Height)` -- a bounding box. Non-rectangular shapes need the actual carved tile set, but most consumers (EntityPlacer, DungeonFloorBuilder) already use the bounding box for iteration and filter by `map.IsWalkable()`. The plan:

1. Keep `Room` as the bounding box for overlap testing and entity placement.
2. Add a `RoomShape` enum to Room (or a new `ShapedRoom` record) that records what shape was carved.
3. The actual shape lives in the GameMap's walkability grid -- that IS the ground truth.
4. Shape generators carve directly into the GameMap within the Room's bounding box.

This is the minimum-disruption approach. No consumer changes needed.

### TASK-P1-001: Extend Room with shape metadata and walkable tile tracking

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/Room.cs`
- Notes: RoomShape enum added (Rectangle/Union/Cave/Circle/Alcove/CorridorRoom). Room.Shape property added as `{ get; init; } = RoomShape.Rectangle;`. WalkableTiles not added — EntityPlacer already filters by map.IsWalkable() so the actual tile set in GameMap IS the ground truth. All existing construction sites unchanged. Build: 0 errors.

### TASK-P1-002: Room shape generator infrastructure

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs` (created)
- Notes: Static class with SelectShape() weight table (Rectangle 30/Union 30/Cave 15/Circle 8/Alcove 10/CorridorRoom 7) and CarveRoom() dispatch. All 6 carvers implemented in the same file. Center-tile floor invariant enforced at the CarveRoom dispatch level.

### TASK-P1-003: Implement two-rectangle union shapes

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs`
- Notes: CarveUnion() implemented. rectA forced to touch at least one bounding-box edge. 50% axis-alignment bias for T/cross shapes. 60% coverage check with 3 retries, falls back to rectangle. Connectivity check with ResetRoom() on failure.

### TASK-P1-004: Implement cellular automata cave shapes

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs`
- Notes: CarveCave() with 4-5 CA rule, 45% initial wall density, 4 iterations. 3×3 center neighborhood pinned as floor. Flood fill from center discards disconnected pockets. Min 7×7, falls back to rectangle. All floor tiles reachable from center guaranteed.

### TASK-P1-005: Implement circle/oval room shapes

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs`
- Notes: CarveCircle() with ellipse equation using (Width-1)/2 and (Height-1)/2 semi-axes so boundary fits inside bounding box. One CA smoothing pass (wall with <= 2 wall neighbors → floor) to reduce staircase jaggedness. Min 7×7, falls back to rectangle.

### TASK-P1-006: Implement alcove addition

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs`
- Notes: CarveAlcove() carves base rect with 2-tile margin, then TryAddAlcove() for each of 4 wall faces. 20% chance per face, 1-2 deep, 1-3 wide, position randomised along segment. Bounding-box check via room.Contains() before each tile write. Min 8×8, falls back to rectangle.

### TASK-P1-007: Implement corridor-room shape

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/RoomShapeGenerator.cs`
- Notes: CarveCorridorRoom() — horizontal if Width>Height, vertical if Height>Width, random when square. Width 2-3 tiles (rng), centered on short axis, full bounding-box length. Min one dim >= 8 and other >= 3, falls back to rectangle otherwise.

### TASK-P1-008: Wire shape generation into MapGenerator

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/MapGenerator.cs`
- Notes: SelectShape() called after room placement succeeds (after overlap check). RoomShapeGenerator.CarveRoom() replaces old CarveRoom() call. newRoom assigned `with { Shape = shape }`. Private CarveRoom kept for pathological 0-room fallback. EnsureConnectivity() added (see P1-009). RNG sequence differs from old code — acceptable, per-floor seeding means no cross-session requirements.

### TASK-P1-009: Connectivity validation post-generation

- Status: ✅ complete
- Layer: logic
- Files changed: `src/Logic/ECS/MapGenerator.cs`
- Notes: EnsureConnectivity() added — BFS flood fill from playerSpawn, finds nearest reachable room to connect any unreachable room via emergency H+V tunnel. Max 3 passes. Also ensures unreachable room center is set to Floor explicitly. Called between room generation and stair placement.

### TASK-P1-010: Tests for room shape generation

- Status: ✅ complete
- Layer: logic
- Files changed: `tests/Core/RoomShapeGeneratorTests.cs` (created)
- Notes: 45 new tests. Covers: Room.Shape default/init/with, SelectShape distribution (2000 samples ±15%), small room fallbacks for all shapes, connectivity for Union/Cave/Alcove, bounding-box containment for all shapes, determinism parameterized over all 6 shapes, center invariant parameterized over all 6 shapes, full-map connectivity over 5 seeds, player spawn walkability, shape recording on rooms. 1105 → 1150 tests, 0 failures.

---

## Phase 2: Floor Composition Pipeline

**Layer:** Presentation (except simplex noise, which is logic-layer math).
**Can run in parallel with Phase 1 after Phase 0 completes.**

### TASK-P2-001: Simplex noise implementation (Logic layer)

- Status: ✅ complete
- Files changed: `src/Logic/Map/SimplexNoise.cs`
- Notes: Gustavson 2D simplex algorithm with standard 256-value permutation table doubled to 512. Pure static class, no Godot deps. Deterministic by input.
- Layer: logic
- Type: system
- Dependencies: none (can start before Phase 0 finishes)
- Files to create:
  - `src/Logic/Map/SimplexNoise.cs`
- Description: Minimal 2D simplex noise implementation. Pure math, no Godot deps. Used by the floor composition pipeline for noise-driven tile variation. Should support:
  - `float Evaluate(float x, float y)` returning [-1, 1]
  - Deterministic for same inputs
  - Frequency and amplitude controlled by the caller (multiply inputs/outputs)
- Reference: Ken Perlin's simplex noise algorithm. Many MIT-licensed C# implementations available for reference.
- Acceptance criteria:
  - `SimplexNoise.Evaluate(x, y)` returns values in [-1, 1]
  - Deterministic: same inputs produce same output
  - Spatial coherence: nearby positions produce similar values
  - No Godot dependencies
  - 3 tests: range validation, determinism, spatial coherence

### TASK-P2-002: Extend tile_themes.yaml with floor variants

- Status: ✅ complete
- Files changed: `config/tile_themes.yaml`, `src/Presentation/TileThemeConfig.cs`, `src/Presentation/TileThemeLoader.cs`
- Notes: FloorWorn added to TileThemeData. GetFloorDark/GetFloorAccent/GetFloorWorn added to TileThemeConfig (all fallback to GetFloorTile when variant list is empty). floor_worn added to TileThemeLoader role switch. floor_worn: [774] added to YAML as placeholder. All three variants currently → tile 774; Rafe to update with distinct IDs.
- Layer: presentation (config)
- Type: art direction
- Dependencies: TASK-P0-006 (wall fix verified first)
- Files to modify:
  - `config/tile_themes.yaml`
  - `src/Presentation/TileThemeConfig.cs`
  - `src/Presentation/TileThemeLoader.cs`
- Description: Add new floor tile variant categories to support the decoration pipeline. Current config has `floor_primary` and `floor_accent`. Need:
  - `floor_dark` -- wall-adjacent shadow tiles (for edge darkening)
  - `floor_worn` -- high-traffic path tiles (for worn paths)
  - Keep `floor_primary` as the standard tile
  - Keep `floor_accent` for noise-driven variation
- YAML additions:
  ```yaml
  floor_dark: [TBD]    # Rafe picks these
  floor_worn: [TBD]    # Rafe picks these
  ```
- TileThemeData additions:
  ```csharp
  public List<int> FloorDark { get; set; } = new();
  public List<int> FloorWorn { get; set; } = new();
  ```
- TileThemeLoader: add `floor_dark` and `floor_worn` to the role switch statement.
- TileThemeConfig: add `GetFloorDark(theme, x, y)` and `GetFloorWorn(theme, x, y)` methods.

**DECISION NEEDED (Rafe):** Select tile IDs for floor_dark and floor_worn variants. Browse tiles in `tools/sprite_browser_16bf_world.html` and pick IDs. Tiles 746-748 are the current floor set. Look for darker variants nearby.

- Acceptance criteria:
  - YAML loads with new floor variant categories
  - New getter methods return valid tile paths
  - Backwards-compatible: missing categories return null gracefully
  - Build: 0 errors

### TASK-P2-003: Floor composition data structure

- Status: ✅ complete
- Files changed: `src/Presentation/Map/FloorComposer.cs`
- Notes: FloorTileType enum (Standard/Dark/Accent/Worn) and FloorComposer static class created. Compose(map, seed) runs 3 passes. No Godot deps.
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-001, TASK-P2-002
- Files to create:
  - `src/Presentation/Map/FloorComposer.cs`
- Description: Create a `FloorComposer` static class that pre-computes the floor tile variant for every floor tile on the map. Takes a GameMap and returns a `Dictionary<(int,int), FloorTileType>` where FloorTileType is an enum: Standard, Dark, Worn, Accent.
- The composer runs the passes in order, with later passes overriding earlier ones where they apply:
  1. Base fill (all Standard)
  2. Edge darkening (overrides to Dark)
  3. Noise variation (overrides Standard to Accent)
  4. [Future: Worn paths]
  5. [Future: Checkered patterns]
- DungeonRenderer reads the pre-computed map instead of doing its current simple primary/accent selection.
- Acceptance criteria:
  - FloorComposer.Compose(map, seed) returns a complete tile-type map
  - Deterministic: same map + seed = same output
  - No Godot dependencies (this is pure data computation)
  - Build: 0 errors

### TASK-P2-004: Pass 2 -- Edge darkening

- Status: ✅ complete
- Files changed: `src/Presentation/Map/FloorComposer.cs`
- Notes: ApplyEdgeDarkening() implemented. 8-directional neighbor check: distance-0 tiles (any of 8 neighbors is wall) always Dark; distance-1 tiles 50% Dark by PositionHash. Dark tiles never overridden by later passes.
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-003
- Files to modify:
  - `src/Presentation/Map/FloorComposer.cs`
- Description: For each floor tile, compute Manhattan distance to nearest wall. Distance 0 (floor tile adjacent to wall) gets `Dark` variant. Distance 1 gets Dark with 50% probability. Distance 2+ stays Standard.
- Algorithm:
  ```
  for each walkable tile (x, y):
    minDist = min Manhattan distance to any non-walkable neighbor
    if minDist == 0: assign Dark  (always)
    if minDist == 1: assign Dark  (50% based on position hash)
    else: leave as Standard
  ```
- Note: "Manhattan distance to nearest wall" means checking the 4 cardinal + 4 diagonal neighbors for distance 0, then an expanding ring for distance 1. For distance 0, just check if any of the 8 neighbors is a wall.
- Acceptance criteria:
  - Tiles adjacent to walls get Dark variant
  - Tiles 1 step from walls get Dark ~50% of the time
  - Interior tiles remain Standard
  - Deterministic by position
  - Visual result: rooms have dark edges, lighter centers

### TASK-P2-005: Pass 4 -- Noise variation

- Status: ✅ complete
- Files changed: `src/Presentation/Map/FloorComposer.cs`
- Notes: ApplyNoiseVariation() samples SimplexNoise at 0.25 frequency, threshold 0.6 → ~10% of Standard tiles become Accent. Seed offset (×0.37, ×0.73) gives per-map variation. Dark tiles never overridden.
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-001, TASK-P2-003
- Files to modify:
  - `src/Presentation/Map/FloorComposer.cs`
- Description: Sample simplex noise at each floor tile. Noise value determines whether the tile uses an accent variant. Only affects tiles that are still Standard after edge darkening.
- Parameters (from design doc):
  - Frequency: 0.25 (controls cluster size)
  - Threshold: noise > 0.6 -> Accent (~10% of tiles)
  - Seed: derived from map seed for determinism
- Algorithm:
  ```
  for each Standard tile:
    noise = SimplexNoise.Evaluate(x * 0.25, y * 0.25)
    if noise > 0.6: assign Accent
  ```
- Acceptance criteria:
  - ~10% of standard tiles become Accent
  - Accent tiles form organic clusters (not random salt-and-pepper)
  - Deterministic with same seed
  - Does not override Dark tiles

### TASK-P2-006: Pass 7 -- Scatter decoration (enhance existing)

- Status: ✅ complete
- Files changed: `src/Presentation/Map/DungeonRenderer.cs`
- Notes: Bones pass (Pass 3) now skips Dark tiles via floorMap lookup. Density unchanged at hash % 40 (2.5%); can be tuned later via tile_themes.yaml.
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-003
- Files to modify:
  - `src/Presentation/Map/DungeonRenderer.cs`
- Description: The current bones decoration pass (Pass 3 in DungeonRenderer) already places bones at ~2.5% density. Enhance it to use the FloorComposer data -- skip decoration on Dark tiles (bones against dark walls look weird), increase density slightly to 3-4%, and add variety by checking theme for additional scatter types beyond bones (future: rubble, debris, dust).
- Acceptance criteria:
  - Bones skip Dark tiles
  - Density adjustable per theme
  - Visual result: scatter feels purposeful, not random

### TASK-P2-007: Wire FloorComposer into DungeonRenderer

- Status: ✅ complete
- Files changed: `src/Presentation/Map/DungeonRenderer.cs`
- Notes: Render() takes optional seed=0 parameter. floorMap pre-computed before Pass 1. Floor tile selection dispatches by FloorTileType (Dark→GetFloorDark, Accent→GetFloorAccent, Worn→GetFloorWorn, Standard→GetFloorTile). Fallback to GetFloorTile if variant path is null. All existing callers unchanged (seed defaults to 0).
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-004, TASK-P2-005, TASK-P2-006
- Files to modify:
  - `src/Presentation/Map/DungeonRenderer.cs`
- Description: Replace the current `GetFloorTile(themeName, gx, gy)` call with a lookup into the pre-computed FloorComposer data. The composer runs once at render time, then each floor tile reads its FloorTileType and calls the appropriate getter (GetFloorTile for Standard, GetFloorDark for Dark, GetFloorAccent for Accent, GetFloorWorn for Worn).
- Changes to Render():
  1. Before the tile loop: `var floorMap = FloorComposer.Compose(map, rngSeed);`
  2. Inside the tile loop for walkable tiles: look up `floorMap[(gx, gy)]` and call the corresponding theme getter
  3. Fallback: if the FloorTileType doesn't have a configured tile variant, fall back to Standard
- Acceptance criteria:
  - Floor tiles render with edge darkening visible
  - Noise clusters of accent tiles visible
  - No regression in stair, wall, or bones rendering
  - Build: 0 errors
  - No new Godot dependencies in logic layer

### TASK-P2-008: Pass 3 -- Checkered floor patterns (stretch goal)

- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-007
- Description: For 25% of medium/large rooms, apply a checkered floor pattern using `(x+y)%2` alternation between primary and accent tiles. Overrides the noise pass for those rooms. Requires knowing which tiles belong to which room -- can use the Room's bounding box + IsWalkable check.
- Note: This is a stretch goal. Edge darkening + noise variation provide 80% of the visual improvement. Checkered patterns add the remaining polish.
- Acceptance criteria:
  - ~25% of rooms (medium/large) have checkered floors
  - Checkered pattern uses primary and accent tiles
  - Edge darkening still applies at room borders (checkered stops 1 tile from walls)

### TASK-P2-009: Pass 5 -- Worn paths (stretch goal)

- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-P2-007
- Description: For each room, compute A* paths between door positions (corridor entry points). Mark tiles on the path as Worn variant. Requires identifying door positions per room -- the intersection of corridor and room edge tiles.
- Note: Stretch goal. Requires corridor-to-room junction detection which is not currently tracked. May need to scan the map for tiles that are TileKind.Corridor adjacent to TileKind.Floor.
- Acceptance criteria:
  - Worn tiles visible along high-traffic paths
  - Paths connect corridor entry points within each room
  - 1-tile jitter from noise for organic feel

### TASK-P2-010: Visual verification -- floor composition

- Status: pending
- Layer: presentation
- Type: calibration
- Dependencies: TASK-P2-007
- Description: Boot the game and verify floor rendering across multiple generated floors.
- Verification checklist:
  - [ ] Edge darkening visible -- rooms have dark perimeter, lighter center
  - [ ] Noise variation creates organic accent clusters
  - [ ] Bones/scatter skip dark tiles
  - [ ] Corridors render with appropriate floor tiles
  - [ ] Different rooms have slightly different floor character
  - [ ] No performance regression (tile creation time)
  - [ ] FOV dimming still works correctly on varied floor tiles
- Acceptance criteria:
  - All checklist items pass
  - Multiple floor transitions produce consistent, attractive results
  - Side-by-side before/after comparison shows clear improvement

---

## Verified Tile ID Reference

### TMX-Verified (Sandstone/Tan Theme, 183-199 range)

| Sliced ID | TMX ID | Role | Status |
|-----------|--------|------|--------|
| 183 | 93 | T-junction variant (needs direction verification) | Partial |
| 184 | 94 | edge_north (floor to south) | Verified |
| 185 | 95 | T-junction variant (needs direction verification) | Partial |
| 186 | -- | edge_south candidate (needs verification) | Unverified |
| 187 | 97 | edge_west (floor to east) | Verified |
| 188 | -- | Interior fill candidate | Unverified |
| 189 | 99 | corner_outer_nw (floor diag SE) | Verified |
| 190 | 100 | corner_outer_ne (floor diag SW) | Verified |
| 191 | 101 | corner_outer_sw (floor diag NE) | Verified |
| 192 | 102 | corner_outer_se (floor diag NW) | Verified |
| 193-197 | -- | Unmapped | Unverified |
| 198 | 108 | edge_east (floor to west) | Verified |
| 199 | 109 | Edge variant (needs role verification) | Partial |

### Current Grey Stone Theme (1095-1109 range)

| ID | Bitmask | Role | Status |
|----|---------|------|--------|
| 1095 | 15 | Interior fill (all cardinal walls) | In use |
| 1096 | 11 | T-junction N+E+W, floor S | In use |
| 1097 | 14 | T-junction N+S+E, floor W | In use |
| 1098 | 9 | Corner N+W, floor S+E | In use |
| 1099 | 13 | T-junction N+S+W, floor E | In use |
| 1100 | 10 | Corner N+E, floor S+W | In use |
| 1102 | 7 | T-junction S+E+W, floor N | In use |
| 1103 | 6 | Corner S+E, floor N+W | In use |
| 1104 | 3 | Horizontal straight E+W | In use |
| 1105 | 0,4,8 | Isolated pillar / dead ends | In use |
| 1106 | 5 | Corner S+W, floor N+E | In use |
| 1107 | 12 | Vertical straight N+S | In use |
| 1108 | 2 | Dead end E | In use |
| 1109 | 1 | Dead end W | In use |

### Floor Tiles (TMX-Verified)

| ID | Role |
|----|------|
| 746 | Floor primary (dark stone) |
| 747 | Floor variant 1 |
| 748 | Floor variant 2 |

### Floor Variants (Needed for Phase 2 -- Rafe to select)

| Role | Candidate IDs | Notes |
|------|---------------|-------|
| floor_dark | TBD | Darker stone for wall-adjacent shadow effect |
| floor_worn | TBD | Lighter/polished stone for high-traffic paths |

---

## Risks and Decisions

### RISK: Room shape changes affect RNG sequence (MEDIUM)

Adding shape selection to MapGenerator consumes additional random calls, changing the room placement pattern for any given seed. This means existing dungeon layouts (for a given seed) will look different. This is acceptable because:
- Dungeon seeds are not saved or communicated to players
- The balance pipeline uses scenario mode (fixed arenas), not dungeon mode
- No cross-prototype seed matching is required for room shapes (Python prototype is rectangular-only)

### RISK: Cave rooms may not connect at room center (LOW, MITIGATED)

The corridor system connects room centers. Cave rooms pin the center tile, but if the CA erodes the connection to the corridor entry point, the room could be disconnected. Mitigated by TASK-P1-009 (connectivity validation with emergency corridor).

### RISK: Performance of non-rectangular rooms (LOW)

Cellular automata runs in O(w*h*iterations) -- for a 18x18 room, that's ~1300 cells * 4 iterations = ~5000 ops. With ~75 rooms, worst case is ~375K ops. Trivial on any device.

### RISK: FloorComposer requires passing seed to DungeonRenderer (LOW)

DungeonRenderer currently doesn't receive a seed. FloorComposer needs one for noise. Options: (A) derive seed from map dimensions (hacky but works), (B) pass the seed through the render call, (C) use position-based deterministic hash (no seed needed). Recommendation: option C, using the existing `PositionHash` pattern already in TileThemeConfig.

### RISK: Floor variant tile IDs not yet selected (BLOCKS Phase 2 final tasks)

Phase 2 tasks P2-004 through P2-010 need floor_dark and floor_worn tile IDs. Rafe needs to browse tiles and select these. This is a blocking dependency for visual verification but not for code structure.

### DECISION NEEDED: Interior fill tile for Phase 0

The TMX-verified list doesn't include a confirmed interior fill tile. Tile 188 is a candidate. If no suitable dark solid tile exists in the 183-199 range, tile 1095 (from the current grey stone set) could serve as interior fill even with the TMX tiles for edges and corners.

### DECISION: Room record evolution strategy

The plan extends Room with optional properties (Shape, WalkableTileCount) rather than creating a new ShapedRoom class. This preserves backwards compatibility -- all existing code that constructs `new Room(x, y, w, h)` continues to work. The Shape defaults to Rectangle. If this proves insufficient, a sealed hierarchy (Room base, ShapedRoom subclass) can be introduced later.

---

## Task Dependency Graph

```
Phase 0 (Wall Fix):
  P0-001 (tile audit) ─────┐
  P0-002 (TileThemeData) ──┼──> P0-004 (YAML) ──> P0-006 (verify)
  P0-003 (Loader) ─────────┘                  │
  P0-005 (Algorithm) ──────────────────────────┘

Phase 1 (Room Shapes) -- can start P1-001 before Phase 0:
  P1-001 (Room extend) ──> P1-002 (infrastructure) ──┬──> P1-003 (union)
                                                      ├──> P1-004 (cave)
                                                      ├──> P1-005 (circle)
                                                      ├──> P1-006 (alcove)
                                                      └──> P1-007 (corridor-room)
                                                              │
  P1-003 + P1-004 + P1-005 + P1-006 + P1-007 ──> P1-008 (wire into MapGenerator)
                                                      │
                                                  P1-009 (connectivity validation)
                                                      │
                                                  P1-010 (tests)

Phase 2 (Floor Composition) -- can start P2-001 before Phase 0:
  P2-001 (simplex noise) ──┐
  P2-002 (floor variants) ─┼──> P2-003 (FloorComposer) ──> P2-004 (edge darken)
                            │                            ──> P2-005 (noise variation)
                            │                            ──> P2-006 (scatter enhance)
                            │                                    │
                            │   P2-004 + P2-005 + P2-006 ──> P2-007 (wire into renderer)
                            │                                    │
                            │                            ──> P2-008 (checkered, stretch)
                            │                            ──> P2-009 (worn paths, stretch)
                            │                                    │
                            └────────────────────────────── P2-010 (visual verify)
```

## Estimated Effort

| Phase | Core Tasks | Stretch Tasks | Est. Sessions |
|-------|-----------|---------------|---------------|
| Phase 0 | 6 tasks | 0 | 2-3 sessions |
| Phase 1 | 10 tasks | 0 | 3-4 sessions |
| Phase 2 | 7 core tasks | 2 stretch | 3-4 sessions |
| **Total** | **23 tasks** | **2 stretch** | **8-11 sessions** |
