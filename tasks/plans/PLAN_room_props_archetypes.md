# Plan: Room Props and Archetypes

**Status:** planning
**Depends on:** PLAN_dungeon_visual_overhaul Phases 0-2 (complete)

## Current State

SROOM-002 complete (2026-04-15). Grand Shrine upgrade implemented alongside PROP-012. 11 new Grand Shrine tests added; 1245 total tests passing.

**Next step:** PROP-013 (EntityPlacer prop-awareness verification — likely verification only, no code changes).

## Overview

Every room currently has interesting geometry (6 shape types, floor composition, edge shadows) but no *purpose*. A cave room and a rectangular room feel the same because neither has furniture. This plan adds a room archetype system (15 archetypes) that assigns semantic identity to rooms during generation, then places props according to archetype-specific recipes with constraint satisfaction. The result: rooms that read as libraries, forges, crypts, and sewers -- not just shapes.

The system is split cleanly across the architecture boundary: all prop placement logic is pure C# in the logic layer (testable by harness and NUnit), while prop rendering is a new pass in DungeonRenderer (presentation layer). Props are defined in `config/props.yaml` as data; archetypes are defined in `config/room_archetypes.yaml`. Zero hardcoded tile IDs in C#.

## Reference

- Design doc: `docs/floor-and-room-design.md` (Layer 4b: room dressing and prop placement)
- Visual overhaul plan: `tasks/plans/PLAN_dungeon_visual_overhaul.md` (Phases 0-2 complete)
- Room record: `src/Logic/ECS/Room.cs` (has RoomShape, needs RoomArchetype)
- Map generator: `src/Logic/ECS/MapGenerator.cs` (assigns shape, will assign archetype)
- Shape generator: `src/Logic/ECS/RoomShapeGenerator.cs` (pattern to follow for archetype assignment)
- GameMap: `src/Logic/ECS/GameMap.cs` (needs PropCells + IsWallTile split)
- GeneratedMap: `src/Logic/ECS/GeneratedMap.cs` (needs PlacedProps list)
- DungeonRenderer: `src/Presentation/Map/DungeonRenderer.cs` (needs prop render pass)
- Entity placer: `src/Logic/Core/EntityPlacer.cs` (FindFreePosition must respect prop cells)
- Tile theme config: `src/Presentation/TileThemeConfig.cs` / `config/tile_themes.yaml`
- Sprite browser: `tools/sprite_browser_16bf_world.html` (1784 world tiles, 24x24px)
- Python prototype: `~/development/rlike/map_objects/room_generators.py` (room types but no props)

---

## Archetypes (15 total)

### Assignment Rules

- Room 0 (player spawn): always **Generic** (safe, predictable start)
- Room N (last room, stair down): always **Generic** or **StairRoom** (no blocking props near exit)
- All other rooms: weighted random selection filtered by room size, shape, and depth
- Small rooms (walkable area <= 16): restricted to Generic, Closet, or Bedroom
- Large rooms (walkable area >= 80): boosted weight for Throne, Hall, Library, Temple
- Cave-shaped rooms: restricted to Generic, Crypt, Sewer, Mushroom Garden
- CorridorRoom-shaped rooms: restricted to Generic, Hallway, Sewer

### Archetype Table

| # | Archetype | Story | Min Walkable | Symmetry | Preferred Shapes | Depth Weight |
|---|-----------|-------|-------------|----------|-----------------|-------------|
| 1 | Generic | Empty or lightly scattered -- breathing room | 9 | none | any | all |
| 2 | Library | Scholar's study; knowledge and dust | 25 | none | Rectangle, Union, Alcove | 1-4 |
| 3 | Armory | Weapons of the garrison, some still sharp | 25 | bilateral | Rectangle, Union | 2-6 |
| 4 | Kitchen | Hearth warmth and rotten feasts | 30 | none | Rectangle, Union | 1-4 |
| 5 | ThroneRoom | Seat of forgotten power | 64 | bilateral | Rectangle, Circle | 3-6 |
| 6 | Prison | Iron and misery | 25 | none | Rectangle, Union, Alcove | 2-6 |
| 7 | Laboratory | Alchemical experiments gone wrong | 25 | none | Rectangle, Union, Cave | 2-5 |
| 8 | Shrine | Altar to something best left unnamed | 25 | bilateral | Rectangle, Circle | all |
| 9 | Storage | Barrels, crates, and forgotten supplies | 16 | none | Rectangle, Alcove | all |
| 10 | Bedroom | Someone once slept here | 16 | none | Rectangle, Alcove | 1-3 |
| 11 | Crypt | Resting place of the dead | 30 | bilateral | Rectangle, Alcove | 2-6 |
| 12 | FountainRoom | Water still flows from somewhere | 36 | radial | Circle, Rectangle | all |
| 13 | Forge | Hammer and anvil, cold now | 30 | none | Rectangle, Union | 3-6 |
| 14 | Sewer | Pipes, grates, and things that lurk in drains | 16 | none | Rectangle, CorridorRoom, Cave | 1-3 |
| 15 | MushroomGarden | Bioluminescent growth in damp chambers | 25 | none | Cave, Circle | 3-6 |

### Per-Archetype Detail

**1. Generic**
No required props. Optional scatter: rubble (20%), cobwebs in corners (15%), small bones (10%). This is the default -- rooms that don't get assigned a special archetype. ~30-40% of rooms on any floor should be Generic to create pacing contrast.

**2. Library**
- Required: bookshelf (wall-adjacent, 2-4 instances, longest wall first)
- Required: table (center zone, 1x1)
- Optional: chair adjacent to table (70%), candelabra on table (40%), globe in corner (15%), desk+chair cluster (20%)
- Density: 40-60%
- Floor pattern candidate: bordered

**3. Armory**
- Required: weapon_rack (wall-adjacent, 2-3, longest wall)
- Required: armor_stand (free-standing, 1-2)
- Optional: training_dummy (center, needs 2-tile clear radius, 30%), workbench (wall, 20%), chest (corner, 25%)
- Density: 30-45%
- Symmetry: bilateral

**4. Kitchen**
- Required: hearth (wall, farthest from any corridor entrance tile)
- Required: table (center zone)
- Optional: chair around table (2-4, 60%), barrel_cluster in corner (2-3 barrels, 50%), shelving near hearth (30%)
- Density: 35-50%

**5. ThroneRoom**
- Required: throne (center of wall farthest from entrance)
- Optional: pillar pairs (symmetrical, 20% each pair up to 3 pairs), brazier flanking throne (40%), banner (wall, 25%)
- Density: 15-25% (deliberately sparse for grandeur)
- Symmetry: bilateral mandatory

**6. Prison**
- Required: chain (wall-adjacent, 2-4)
- Optional: cage (free-standing, 30%), shackle (wall, 20%), straw_pile (floor, 25%), bucket (corner, 20%), skeleton_prop (floor, 15%)
- Density: 35-50%
- Note: full cell-partition subdivision is deferred (too complex for v1). Chains + cages sell the story.

**7. Laboratory**
- Required: alchemy_table (center or wall-adjacent)
- Required: cauldron (center zone)
- Optional: shelf_with_bottles (wall, 40%), bookshelf (wall, 25%), brazier near cauldron (30%)
- Density: 40-55%

**8. Shrine**
- Required: altar (center-back or exact center)
- Optional: candle flanking altar in pairs (2-4, 60%), statue (center-back flanking altar, 25%), prayer_mat (floor before altar, 20%)
- Density: 20-35%
- Symmetry: bilateral preferred
- Note: clear 2-wide path from any entrance to altar

**9. Storage**
- Required: barrel_cluster (wall-adjacent, 2-4 barrels)
- Required: crate_cluster (wall-adjacent or corner, 2-4 crates)
- Optional: chest (corner, 30%), sack (floor near barrels, 25%), shelving (wall, 20%)
- Density: 55-70%
- Note: one clear aisle from entrance to back wall

**10. Bedroom**
- Required: bed (wall-adjacent, head against wall)
- Optional: chest at foot of bed (40%), nightstand adjacent to bed head (35%), desk+chair cluster (20%), wardrobe (wall perpendicular to bed wall, 15%)
- Density: 30-45%
- Note: bed never within 2 tiles of entrance

**11. Crypt**
- Required: sarcophagus (center row, 1-2) OR tombstone (rows, 2-4)
- Optional: urn flanking sarcophagus (30%), candelabra at sarcophagus head (40%), cobweb in corners (25%)
- Density: 25-40%
- Symmetry: bilateral preferred

**12. FountainRoom**
- Required: fountain (exact center)
- Optional: bench at cardinal points (25% each), pillar at inner corners (20% each), planter along wall (15%)
- Density: 15-25%
- Symmetry: radial

**13. Forge**
- Required: forge (wall-adjacent)
- Required: anvil (1-2 tiles from forge, not wall-adjacent)
- Optional: water_barrel within 2 tiles of forge (40%), weapon_rack (wall, 25%), tool_rack (wall, 20%), coal_pile (floor near forge, 30%)
- Density: 35-50%
- Note: clear 2x2 workspace in front of anvil

**14. Sewer**
- Required: grate (floor, 1-2, non-blocking)
- Optional: pipe (wall-adjacent, 40%), puddle (floor cluster, 50% -- non-blocking), moss_patch (wall-adjacent floor, 30%), drain (floor, 20% -- non-blocking)
- Density: 20-35%
- Note: grates and puddles are non-blocking floor overlays, not movement obstacles

**15. MushroomGarden**
- Required: mushroom_cluster (floor, 2-3 clusters of 1-2 tiles)
- Optional: glowing_mushroom (floor, 30%), moss_patch (floor, 40%), puddle (floor, 25%), vine (wall-adjacent, 20%)
- Density: 25-40%
- Note: most props here are non-blocking overlays (atmospheric, not tactical)

---

## Architecture

### Data Model (Logic Layer)

```
RoomArchetype enum (Room.cs, alongside RoomShape):
  Generic, Library, Armory, Kitchen, ThroneRoom, Prison, Laboratory,
  Shrine, Storage, Bedroom, Crypt, FountainRoom, Forge, Sewer, MushroomGarden

Room record gains:
  public RoomArchetype Archetype { get; init; } = RoomArchetype.Generic;

PlacedProp record (new file: src/Logic/ECS/PlacedProp.cs):
  string PropId          -- references props.yaml definition
  int X, int Y           -- grid position (top-left of footprint)
  int FootprintW         -- 1 or 2
  int FootprintH         -- 1 or 2
  bool BlocksMovement    -- true for furniture, false for overlays
  int TileId             -- resolved from props.yaml, passed to renderer

PropDefinition record (loaded from config/props.yaml):
  string Id              -- "bookshelf", "barrel", "throne", etc.
  int[] TileIds          -- one or more tile IDs (variant selection)
  int FootprintW, H      -- 1x1 default
  bool BlocksMovement    -- default true
  PlacementType Type     -- Center, WallAdjacent, Corner, FreeStanding, FloorOverlay
  string[] Tags          -- ["furniture", "storage", "light", etc.]

ArchetypeDefinition record (loaded from config/room_archetypes.yaml):
  string Id
  int MinWalkable
  SymmetryType Symmetry  -- None, Bilateral, Radial
  string[] PreferredShapes
  (int Min, int Max)? DepthRange
  int Weight             -- base selection weight
  float DensityMin, DensityMax
  List<PropRule> Required
  List<PropRule> Optional

PropRule record:
  string PropId
  PlacementType Placement
  int CountMin, CountMax
  float Chance           -- 1.0 for required, < 1.0 for optional
```

### GameMap Changes (PropCells + IsWallTile split)

Current state: `IsWalkable(x,y)` checks `_walkable[x,y]` which is set by `SetTile`. The wall autotile system in DungeonRenderer calls `IsWalkable` to compute bitmasks. If we mark prop cells as non-walkable via `_walkable`, the autotile system will render wall tiles where props are, which is wrong.

Solution:

```csharp
// New in GameMap:
private readonly HashSet<(int, int)> _propCells = new();

public void MarkPropCell(int x, int y) { if (InBounds(x, y)) _propCells.Add((x, y)); }
public bool IsPropCell(int x, int y) => _propCells.Contains((x, y));

// IsWalkable now checks prop cells too:
public bool IsWalkable(int x, int y) => InBounds(x, y) && _walkable[x, y] && !_propCells.Contains((x, y));

// New: wall autotile uses this instead of IsWalkable:
public bool IsWallTile(int x, int y) => InBounds(x, y) && !_walkable[x, y];

// Existing methods (CanMoveTo, IsBlocked, MoveToward) all use IsWalkable
// and will automatically block movement through props. No changes needed.
```

DungeonRenderer.ComputeWallMasks changes from `IsWalkable` to `IsWallTile` for the autotile check. This means props don't produce wall tiles around them.

### GeneratedMap Changes

```csharp
// New property:
public IReadOnlyList<PlacedProp> Props { get; }

// Constructor gains a props parameter (defaults to empty for existing callers)
```

### Archetype Assignment (MapGenerator)

After shape selection and carving, before returning:

```csharp
// For each room (except room 0 and last room):
var archetype = RoomArchetypeSelector.Select(room, map, depth, rng);
room = room with { Archetype = archetype };
```

RoomArchetypeSelector is a new static class in `src/Logic/ECS/` that:
1. Filters eligible archetypes by room walkable area, shape, and depth
2. Weighted random selection from eligible set
3. Enforces Generic for room 0 and last room

### Prop Placement (RoomPropPlacer)

New static class: `src/Logic/ECS/RoomPropPlacer.cs`

Implements a simplified version of the 7-pass algorithm. For v1, implement passes 0-4 and skip best-of-N (pass 7). Best-of-N is an optimization for later.

```
Pass 0: Initialize placement grid (walls=FULL, door-adjacent=MARGIN, else=EMPTY)
Pass 1: Place required center/focal props
Pass 2: Place required wall-adjacent props (longest walls first)
Pass 3: Place optional props by type
Pass 4: Connectivity validation (A* or flood-fill from every entrance to every other)
```

Constraints enforced at every placement:
- Minimum 40% of walkable area remains empty
- Door adjacency zones (1 tile in each direction from every corridor/door tile touching the room) always clear
- Flood-fill from all entrances succeeds after each required prop

### Finding Room Entrances

The current codebase has no explicit door positions. Entrances can be inferred: scan the room's perimeter (1 tile outside the bounding box) for Corridor tiles. Each corridor tile adjacent to a room floor tile is an entrance point. This is deterministic and works for all room shapes.

### Config Files

**config/props.yaml** -- prop definitions:
```yaml
props:
  bookshelf:
    tile_ids: [TBD]
    footprint: [1, 1]
    blocks_movement: true
    placement: wall_adjacent
    tags: [furniture, library]

  barrel:
    tile_ids: [TBD]
    footprint: [1, 1]
    blocks_movement: true
    placement: corner
    tags: [storage, container]

  # ... etc
```

**config/room_archetypes.yaml** -- archetype definitions with prop rules:
```yaml
archetypes:
  library:
    min_walkable: 25
    symmetry: none
    preferred_shapes: [Rectangle, Union, Alcove]
    depth_range: [1, 4]
    weight: 10
    density: [0.40, 0.60]
    required:
      - prop: bookshelf
        placement: wall_adjacent
        count: [2, 4]
      - prop: table
        placement: center
        count: [1, 1]
    optional:
      - prop: chair
        placement: adjacent_to_table
        count: [1, 2]
        chance: 0.70
      # ... etc
```

### Presentation Layer

DungeonRenderer gains a new pass (Pass 4: props) after bones (Pass 3):

```csharp
// Pass 4: room props
foreach (var prop in generatedMap.Props)
{
    var tilePath = themeConfig.GetPropTile(prop.TileId);
    // Create Sprite2D, position at GridToScreen(prop.X, prop.Y)
    // ZIndex: tile sort order + 1 (same band as bones/stairs)
    // Track in TileLayer for FOV modulation
}
```

TileThemeConfig gains `GetPropTile(int tileId)` which is just `GetTexturePath(tileId)` -- props use raw tile IDs from props.yaml, no theme indirection needed (props look the same in all themes for now).

### EntityPlacer Integration

`EntityPlacer.FindFreePosition` already checks `map.IsWalkable(x, y)`. Since `IsWalkable` will return false for prop cells, entities will never spawn on top of props. No changes needed to EntityPlacer.

### Pathfinding Integration

A* pathfinding uses `IsWalkable` for traversal. Prop cells will be automatically non-traversable. Monsters and the player will path around furniture. This is correct -- props should be obstacles.

---

## Tile ID Survey for Rafe

Browse `tools/sprite_browser_16bf_world.html`. For each prop below, find the best matching tile in the Oryx 16bf world_24x24 sheet. Write the tile ID number in the "Tile ID" column. Some props may have multiple variants -- list all IDs comma-separated.

If a prop has no good match in the world sheet, write "NONE" and we will either skip it or check other Oryx sheets.

### Dungeon Basics

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| barrel | 1x1 | Common wooden barrel | TBD |
| barrel_open | 1x1 | Open/broken barrel variant | TBD |
| crate | 1x1 | Wooden crate/box | TBD |
| crate_large | 1x1 | Larger crate variant (if distinct from crate) | TBD |
| chest_closed | 1x1 | Closed treasure chest (decorative prop, not lootable) | TBD |
| sack | 1x1 | Cloth sack/bag | TBD |
| rubble | 1x1 | Broken stone rubble pile | TBD |
| cobweb | 1x1 | Spider web in corner (non-blocking overlay) | TBD |
| pillar | 1x1 | Stone column/pillar | TBD |
| bones_pile | 1x1 | Pile of bones (larger than scatter bones) | TBD |
| skeleton_prop | 1x1 | Decorative skeleton (non-entity, just visual) | TBD |

### Furniture / Living Quarters

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| table | 1x1 | Wooden table | TBD |
| table_long | 2x1 or 1x2 | Long dining/work table (if available) | TBD |
| chair | 1x1 | Wooden chair/stool | TBD |
| bed | 1x2 or 2x1 | Single bed (head + foot, might be 2 tiles) | TBD |
| bed_single | 1x1 | Single-tile bed if 1x2 not available | TBD |
| nightstand | 1x1 | Small bedside table | TBD |
| wardrobe | 1x1 | Tall wardrobe/dresser/cabinet | TBD |
| desk | 1x1 | Writing desk | TBD |
| bookshelf | 1x1 | Wall bookcase full of books | TBD |
| shelf | 1x1 | Generic wall shelf (not books) | TBD |
| candelabra | 1x1 | Floor standing candle holder | TBD |
| candle | 1x1 | Small candle (non-blocking overlay) | TBD |
| fireplace | 1x1 | Hearth/fireplace (wall-adjacent) | TBD |
| rug | 1x1 | Floor rug/carpet (non-blocking overlay) | TBD |

### Grand Spaces

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| throne | 1x1 | Royal throne/ornate chair | TBD |
| banner | 1x1 | Wall-mounted banner/tapestry | TBD |
| statue | 1x1 | Stone statue (humanoid or abstract) | TBD |
| statue_large | 1x1 | Larger/more ornate statue variant | TBD |
| brazier | 1x1 | Fire brazier on stand | TBD |
| fountain | 1x1 | Water fountain (decorative) | TBD |
| bench | 1x1 | Stone or wooden bench | TBD |
| planter | 1x1 | Plant pot / decorative planter | TBD |

### Religious / Ritual

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| altar | 1x1 | Stone altar for worship/sacrifice | TBD |
| sarcophagus | 1x1 | Stone coffin/sarcophagus lid | TBD |
| tombstone | 1x1 | Grave marker / headstone | TBD |
| urn | 1x1 | Burial urn / vase | TBD |
| prayer_mat | 1x1 | Floor mat (non-blocking overlay) | TBD |

### Workshop / Forge

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| forge | 1x1 | Blacksmith's forge/furnace | TBD |
| anvil | 1x1 | Blacksmith's anvil | TBD |
| weapon_rack | 1x1 | Wall-mounted weapon display | TBD |
| armor_stand | 1x1 | Armor mannequin/stand | TBD |
| tool_rack | 1x1 | Tools hanging on wall | TBD |
| workbench | 1x1 | Work surface / crafting table | TBD |
| coal_pile | 1x1 | Pile of coal/charcoal (non-blocking overlay) | TBD |
| water_barrel | 1x1 | Barrel of water (quenching) | TBD |

### Alchemy / Laboratory

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| cauldron | 1x1 | Large bubbling cauldron/pot | TBD |
| alchemy_table | 1x1 | Table with bottles/apparatus | TBD |
| shelf_bottles | 1x1 | Shelf lined with potion bottles | TBD |
| globe | 1x1 | Decorative globe or orb on stand | TBD |

### Prison

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| chain | 1x1 | Wall-mounted chain/shackle | TBD |
| cage | 1x1 | Iron cage (floor standing) | TBD |
| iron_bars | 1x1 | Cell bars / iron gate section | TBD |
| bucket | 1x1 | Simple bucket | TBD |
| straw_pile | 1x1 | Straw/hay on floor (non-blocking overlay) | TBD |
| training_dummy | 1x1 | Practice dummy (for armory too) | TBD |

### Sewer / Industrial

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| grate | 1x1 | Floor drain grate (non-blocking overlay) | TBD |
| pipe_horizontal | 1x1 | Wall pipe segment (horizontal) | TBD |
| pipe_vertical | 1x1 | Wall pipe segment (vertical) | TBD |
| puddle | 1x1 | Water puddle on floor (non-blocking overlay) | TBD |
| moss_patch | 1x1 | Moss/algae growth (non-blocking overlay) | TBD |
| drain | 1x1 | Larger drain opening (non-blocking overlay) | TBD |

### Natural / Organic

| Prop | Footprint | Notes | Tile ID |
|------|-----------|-------|---------|
| mushroom_cluster | 1x1 | Group of mushrooms | TBD |
| glowing_mushroom | 1x1 | Bioluminescent mushroom (if distinct) | TBD |
| vine | 1x1 | Wall vine / hanging plant | TBD |
| rock | 1x1 | Natural rock / boulder (blocks movement) | TBD |
| stalagmite | 1x1 | Cave formation (blocks movement) | TBD |

**Total: ~65 prop types across 8 visual families.**

Many of these will map to the same Oryx tile with different names (e.g., "shelf" and "bookshelf" might be variants of the same base tile). That is fine -- the YAML layer handles the mapping and variant selection.

---

## Implementation Tasks

### Phase A: Foundation (visible results after 4 tasks)

- [ ] PROP-001: RoomArchetype enum and Room property
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: none
  - Files: `src/Logic/ECS/Room.cs`
  - Description: Add `RoomArchetype` enum (15 values) to Room.cs alongside RoomShape. Add `RoomArchetype Archetype { get; init; } = RoomArchetype.Generic;` to the Room record. Pattern matches exactly how RoomShape was added.
  - Acceptance criteria:
    - Enum has all 15 archetype values
    - Room record compiles with new property, default Generic
    - All existing tests pass unchanged (Generic default means no behavioral change)

- [ ] PROP-002: RoomArchetypeSelector -- assigns archetypes during generation
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-001
  - Files: `src/Logic/ECS/RoomArchetypeSelector.cs` (new), `src/Logic/ECS/MapGenerator.cs`
  - Description: New static class that selects an archetype for a room based on walkable area, shape, depth, and weighted random selection. Wire into MapGenerator after shape carving. Room 0 = Generic, last room = Generic. All others draw from filtered eligible set. Archetype definitions (weights, size minimums, shape preferences, depth ranges) are hardcoded constants initially -- will move to YAML in PROP-005.
  - Acceptance criteria:
    - Room 0 always Generic, last room always Generic
    - Rooms too small for an archetype's minimum get filtered out
    - Cave-shaped rooms never assigned Library/Armory/Kitchen etc.
    - Deterministic with same seed
    - New test file: `tests/ECS/RoomArchetypeSelectorTests.cs` with at least 8 test cases
    - All existing tests pass

- [ ] PROP-003: PlacedProp record and GeneratedMap extension
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: none (parallel with PROP-001)
  - Files: `src/Logic/ECS/PlacedProp.cs` (new), `src/Logic/ECS/GeneratedMap.cs`
  - Description: Define `PlacedProp` record with PropId, X, Y, FootprintW, FootprintH, BlocksMovement, TileId. Add `IReadOnlyList<PlacedProp> Props` to GeneratedMap. Default to empty list for existing callers (MapGenerator passes `Array.Empty<PlacedProp>()`).
  - Acceptance criteria:
    - PlacedProp is a sealed record in the Logic namespace
    - GeneratedMap constructor accepts optional props parameter
    - Existing MapGenerator.Generate compiles without changes (empty props)
    - All existing tests pass

- [ ] PROP-004: GameMap PropCells and IsWallTile split
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: none (parallel with PROP-001)
  - Files: `src/Logic/ECS/GameMap.cs`
  - Description: Add `HashSet<(int,int)> _propCells`, `MarkPropCell`, `IsPropCell`, `IsWallTile` methods. `IsWalkable` checks `!_propCells.Contains((x,y))` in addition to `_walkable[x,y]`. `IsWallTile` only checks the tile array (used by wall autotile, not affected by props). This is the key change that makes props block movement without producing wall graphics.
  - Acceptance criteria:
    - `IsWalkable(x,y)` returns false when (x,y) is in PropCells, even if _walkable is true
    - `IsWallTile(x,y)` returns true only for actual wall tiles, not prop cells
    - `CanMoveTo`, `IsBlocked`, `MoveToward` all respect prop cells (via IsWalkable)
    - New test cases in `tests/ECS/GameMapTests.cs` (or new file) covering prop cell behavior
    - All existing tests pass (no props placed = no behavior change)

- [ ] PROP-005: Props YAML definition and loader
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-003
  - Files: `config/props.yaml` (new), `src/Logic/Content/PropRegistry.cs` (new)
  - Description: Create `config/props.yaml` with all ~65 prop definitions. Tile IDs default to placeholder value (e.g., 182 = isolated wall) until Rafe fills in real IDs. Create `PropRegistry` that loads props.yaml and provides lookup by ID. Follow the pattern of existing YAML loaders (MonsterFactory, ConsumableFactory). The registry lives in the Logic layer -- it does not reference Godot. Tile IDs are integers, not texture paths.
  - Acceptance criteria:
    - `config/props.yaml` parses without error
    - PropRegistry loads all definitions and provides `TryGet(string id, out PropDefinition def)`
    - Every prop referenced by any archetype exists in the registry
    - Test: `tests/Content/PropRegistryTests.cs` validates loading

- [ ] PROP-006: RoomPropPlacer -- constraint-based prop placement
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-002, PROP-004, PROP-005
  - Files: `src/Logic/ECS/RoomPropPlacer.cs` (new)
  - Description: Core placement engine. For each room with a non-Generic archetype, runs the placement algorithm:
    - Pass 0: Build placement grid (FULL/MARGIN/EMPTY). Find room entrances by scanning perimeter for corridor tiles.
    - Pass 1: Place required center/focal props. Validate connectivity after each.
    - Pass 2: Place required wall-adjacent props. Longest walls first. 1-tile margin in front.
    - Pass 3: Place optional props by type, each with chance roll and max 10 attempts.
    - Pass 4: Final connectivity validation. If failed, remove last placed prop and retry.
    - Enforce density cap: never exceed archetype's density maximum.
    - Enforce small room limits: <=9 walkable: max 1 prop. <=16: max 2. <=25: max 4.
    - Mark all blocking prop positions on GameMap via MarkPropCell.
    - Return List<PlacedProp>.
  - Wire into MapGenerator after room carving and archetype assignment. Props are placed, marked on GameMap, and included in GeneratedMap.
  - Acceptance criteria:
    - No prop placed within 1 tile of a room entrance
    - Every room with props passes flood-fill connectivity from all entrances to all other entrances
    - At least 40% of walkable area remains empty after placement
    - Small room caps respected
    - Wall-adjacent props placed only on tiles touching a wall
    - Center props placed within center 60% of room
    - Deterministic with same seed
    - New test file: `tests/ECS/RoomPropPlacerTests.cs` with at least 12 test cases covering:
      - Connectivity preservation
      - Density cap enforcement
      - Small room limits
      - Entrance clearance
      - Wall-adjacent placement correctness
      - Center placement correctness
    - All existing tests pass

### Phase B: Presentation (rooms look dressed in-game)

- [ ] PROP-007: DungeonRenderer prop pass
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: PROP-006, tile IDs from Rafe
  - Files: `src/Presentation/Map/DungeonRenderer.cs`, `src/Presentation/TileThemeConfig.cs`
  - Description: Add Pass 4 to DungeonRenderer that iterates `generatedMap.Props` and creates Sprite2D nodes for each. Props use raw tile IDs (no theme indirection). Props are tracked in TileLayer for FOV modulation. Non-blocking overlay props get 0.7 alpha like bones. Add `GetPropTile(int tileId)` to TileThemeConfig.
  - Acceptance criteria:
    - Props render at correct grid positions
    - Props are visible/hidden based on FOV (same as floor tiles)
    - Non-blocking props (puddles, grates, moss) render with 0.7 alpha
    - Blocking props render at full opacity
    - No null-reference errors when props list is empty (backward compat)

- [ ] PROP-008: DungeonRenderer wall autotile uses IsWallTile
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: PROP-004
  - Files: `src/Presentation/Map/DungeonRenderer.cs`
  - Description: Change `ComputeWallMasks` to use `map.IsWallTile(x, y)` instead of `!map.IsWalkable(x, y)` for neighbor checks. This prevents props from generating wall tile graphics around them. The IsWalkable check for "is this cell a floor" stays unchanged for the current-cell render decision.
  - Acceptance criteria:
    - Props adjacent to floor tiles do not produce wall autotile artifacts
    - Wall rendering unchanged when no props are present
    - Visual verification in Godot

### Phase C: Polish and Tuning

- [ ] PROP-009: Room archetypes YAML config (move from hardcoded to data-driven)
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-006
  - Files: `config/room_archetypes.yaml` (new), `src/Logic/Content/ArchetypeRegistry.cs` (new), `src/Logic/ECS/RoomArchetypeSelector.cs` (update)
  - Description: Move archetype definitions (weights, size requirements, prop rules, depth ranges) from hardcoded C# into `config/room_archetypes.yaml`. Create ArchetypeRegistry loader. Update RoomArchetypeSelector to use the registry. This is the data-driven step -- after this, adding a new archetype requires only YAML edits.
  - Acceptance criteria:
    - All 15 archetypes defined in YAML
    - Behavior identical to hardcoded version (same seed = same output)
    - New archetype can be added by editing YAML only (no C# changes)
    - Tests updated to load from YAML

- [ ] PROP-010: Symmetry enforcement for bilateral/radial archetypes
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-006
  - Files: `src/Logic/ECS/RoomPropPlacer.cs`
  - Description: For archetypes with bilateral symmetry (ThroneRoom, Armory, Crypt), mirror optional prop placement across the room's long axis. For radial symmetry (FountainRoom), place optional props at cardinal or diagonal offsets from center. This is a refinement of Pass 3/4 in RoomPropPlacer.
  - Acceptance criteria:
    - ThroneRoom props are mirrored across the vertical center axis
    - FountainRoom optional props appear at symmetric cardinal positions
    - Connectivity still validated after symmetric placement

- [ ] PROP-011: Best-of-N room scoring
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-006
  - Files: `src/Logic/ECS/RoomPropPlacer.cs`
  - Description: Implement Pass 7 from the spec: generate each room's prop layout N times (default 5 for mobile perf), score by `(required * 10 + optional * 3 + symmetry * 5 - blocked_path * 100)`, keep the best. This improves prop placement quality at the cost of generation time. Keep N configurable.
  - Acceptance criteria:
    - Same seed produces same result (deterministic across N attempts)
    - Higher N produces equal or higher scoring layouts
    - Generation time stays under 200ms per floor with N=5

- [x] PROP-012: Maintenance state variation
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: PROP-006
  - Files created:
    - `src/Logic/ECS/RoomMaintenanceState.cs` (new enum)
  - Files modified:
    - `src/Logic/ECS/Room.cs` (added MaintenanceState property)
    - `src/Logic/ECS/MapGenerator.cs` (assigns state per room, public RollMaintenanceState helper)
    - `src/Logic/ECS/RoomPropPlacer.cs` (density multiplier, required-prop removal for Ruined, jitter for Neglected/Abandoned, scatter overlays for Abandoned/Ruined)
    - `tests/ECS/MaintenanceStateTests.cs` (11 new tests: distribution, density, jitter, scatter, connectivity)
  - Notes:
    - `RollMaintenanceState` is `public static` (no InternalsVisibleTo configured in this project)
    - Required-prop removal in Ruined rooms changes RNG state relative to other maintenance states — density comparisons must be averaged across seeds, not compared single-seed
    - Scatter overlays are additive (don't count against effectiveMaxProps cap)
    - Jitter only moves blocking props (floor overlays are already loosely placed)
    - Player spawn (room 0) is always WellMaintained

- [ ] PROP-013: EntityPlacer prop awareness for FindFreePosition
  - Status: pending
  - Layer: logic
  - Type: system
  - Dependencies: PROP-004
  - Files: `src/Logic/Core/EntityPlacer.cs`
  - Description: Verify that EntityPlacer.FindFreePosition correctly skips prop cells. Since it already checks `map.IsWalkable(x, y)` and PROP-004 makes IsWalkable check PropCells, this should work automatically. This task is verification + test coverage only. Add explicit tests that place props in a room and confirm entities never spawn on prop tiles.
  - Acceptance criteria:
    - Test: room with props has entities placed only on non-prop walkable tiles
    - Test: room where all tiles are propped up returns null from FindFreePosition
    - No code changes expected (verification only)

---

## Decisions Needed from Rafe

1. **Sewer depth range.** Currently spec'd at depths 1-3. Should sewer rooms appear at all depths, or is there a thematic progression where sewers give way to deeper dungeon types?

2. **Props as combat obstacles only, or interactive?** This plan treats props as movement-blocking scenery (like walls, but with a prop sprite). Should any props be destroyable by combat (e.g., smashing a barrel, breaking a table)? If yes, that is a separate system (props become entities with HP) and should be a future plan.

3. **Prop visibility behind FOV.** Should explored-but-not-visible props show in the fog-of-war dim state (like floor tiles do), or should they be hidden? The current plan shows them dimmed like floor tiles.

4. **Lootable props.** Should decorative chests, barrels, or bookshelves eventually be lootable (tap to search)? This plan makes them purely visual. Lootable props are a significant system (interaction model, loot tables, UI) and should be a separate plan if desired.

5. **Archetype distribution tuning.** The current weights give Generic ~30-40% of rooms. Should there be a minimum number of "special" (non-Generic) rooms per floor? E.g., "every floor must have at least 2 rooms with props."

6. **MushroomGarden vs. a broader "natural" archetype.** MushroomGarden is niche. Would a broader "Cavern" archetype (stalagmites, rocks, mushrooms, puddles) be more useful? It could cover both natural caves and mushroom gardens via the maintenance state system.

7. **Multi-tile props.** The Oryx tileset is 24x24px per tile. Some props (beds, long tables, sarcophagi) might look better as 2-tile composites. Should we support 1x2/2x1 footprints in v1, or keep everything 1x1 and revisit multi-tile later? 1x1-only is simpler and the sprite browser needs to be checked for whether multi-tile prop art even exists in the sheet.

8. **Generation performance budget.** The spec says 200ms per floor. Prop placement with connectivity validation adds cost. Is 200ms still the target, or can we go higher for richer rooms? Mobile devices are the constraint.
