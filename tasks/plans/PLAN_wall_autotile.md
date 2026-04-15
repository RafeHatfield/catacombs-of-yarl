# Plan: Wall Autotile Overhaul (8-bit Hybrid)

**Status:** planning

## Current State

Plan created. All tasks pending. Ready for execution.

## Overview

The current 4-bit cardinal autotile system cannot distinguish outer corners from interior fill. When all four cardinal neighbors are walls, the bitmask is always 15 regardless of whether a diagonal neighbor is floor (outer corner) or all diagonals are walls (interior fill). This causes room corners to render as solid fill instead of showing the correct corner piece, making room boundaries visually ambiguous.

The fix is a two-step hybrid algorithm: resolve cardinals first (handles edges, T-junctions, straights), then check diagonals when all cardinals are walls (handles outer corners vs interior fill). This is simpler than a full 8-bit 256-entry bitmask while covering every case that matters for rectangular dungeon rooms.

Additionally, the floor tiles should switch from the current picks (1091, 1034, 1090, 1089, 1088) to the TMX-verified IDs (746, 747, 748) since those are the tiles proven to work visually with the TMX wall set.

**Entirely presentation-layer work.** Logic layer: zero changes. Balance pipeline: unaffected. Tests: unaffected (tests don't render).

## Why This Matters

Every wall tile at a room corner currently renders as the same "interior fill" tile (1095) because the 4-bit bitmask cannot tell the difference. This makes rooms look like undifferentiated blobs of wall rather than having clean, visible edges. The TMX example file (Oryx's official demo) solves this with outer corner tiles (189-192) that the current system has no way to select.

## Reference

- Current renderer: `src/Presentation/Map/DungeonRenderer.cs` (lines 273-281: `ComputeWallBitmask`)
- Current config: `src/Presentation/TileThemeConfig.cs` (lines 98-120: `GetAutoWallTile`)
- Current YAML: `config/tile_themes.yaml`
- YAML parser: `src/Presentation/TileThemeLoader.cs`
- Parent plan: `tasks/plans/PLAN_topdown_switch.md` (this is a Phase 2 task from that plan)
- TMX ground truth: Oryx 16bf example TMX (pixel-matched tile IDs verified by Rafe)
- Python PoC: Not applicable (PoC used tcod console rendering, not sprite tiles)

## TMX-Verified Tile ID Reference (Grey Stone Theme)

These IDs are confirmed by pixel-matching TMX tiles to sliced sprite files:

### Wall Edge Pieces (183-199 range)
| ID  | Role | Description |
|-----|------|-------------|
| 184 | edge_north | North-facing edge (floor to south, walls N/E/W) |
| 186 | edge_south | South-facing edge (floor to north, walls S/E/W) -- needs visual verification |
| 187 | edge_west | West-facing edge (floor to east, walls N/S/W) |
| 198 | edge_east | East-facing edge (floor to west, walls N/S/E) |
| 189 | corner_outer_nw | NW outer corner (floor diagonally to SE) |
| 190 | corner_outer_ne | NE outer corner (floor diagonally to SW) |
| 191 | corner_outer_sw | SW outer corner (floor diagonally to NE) |
| 192 | corner_outer_se | SE outer corner (floor diagonally to NW) |
| 183 | t_junction_variant | Needs direction verification |
| 185 | t_junction_variant | Needs direction verification |
| 199 | edge_variant | Needs role verification |

### Floor Tiles (TMX-verified)
| ID  | Role |
|-----|------|
| 746 | Floor primary (dark stone) |
| 747 | Floor variant 1 |
| 748 | Floor variant 2 |

### Tiles Still Needing Identification
- Interior fill (all 8 neighbors are walls) -- solid dark tile, may be in a different range
- Inner corner L-pieces (where two walls meet at a right angle from the floor side)
- Dead-end caps
- Cross/intersection pieces
- Isolated pillar

## The Algorithm

### Current (broken): 4-bit Cardinal Only

```
For each wall tile:
  Check N, S, E, W neighbors for wall/floor
  4-bit mask (N=8, S=4, E=2, W=1) -> one of 16 tiles
  Problem: mask=15 for outer corners AND interior fill AND all-wall T-junctions
```

### Proposed: Hybrid Two-Step

```
For each wall tile at (x, y):

Step 1 -- Cardinal check (same as current):
  Compute 4-bit mask: N(8) + S(4) + E(2) + W(1)
  If mask < 15: use cardinal edge/corner/T-junction tile (existing behavior)
  If mask == 15: proceed to Step 2

Step 2 -- Diagonal disambiguation (new):
  Check NE (x+1, y-1), NW (x-1, y-1), SE (x+1, y+1), SW (x-1, y+1)
  Count how many diagonals are floor (walkable)

  If 0 diagonals are floor -> interior_fill (solid dark tile)
  If 1 diagonal is floor -> outer corner facing that diagonal:
    SE floor -> corner_outer_nw (tile 189)
    SW floor -> corner_outer_ne (tile 190)
    NE floor -> corner_outer_sw (tile 191)
    NW floor -> corner_outer_se (tile 192)
  If 2+ diagonals are floor -> pick based on priority or use a multi-corner tile
    (In practice, 2+ exposed diagonals happen at T-junction backs and cross-shaped
    intersections. Use the first exposed diagonal found, clockwise from NE.)
```

### Why Not Full 8-bit?

A full 8-bit bitmask has 256 entries. Most are unused in rectangular room dungeons. The hybrid approach needs only 16 cardinal entries + 5 diagonal entries (4 corners + 1 interior fill) = 21 total tile definitions. Much simpler to configure and maintain.

---

## Tasks

### Phase 1: Tile ID Audit and Mapping

- [ ] **TASK-001: Complete tile ID audit for all wall roles**
  - Status: pending
  - Layer: presentation (asset inspection only)
  - Type: art direction
  - Dependencies: none
  - Description: Systematically identify every tile needed for the hybrid autotile system. The TMX gives us partial mapping (corners, some edges). We need to fill in the gaps for: south-facing edge, T-junctions (all 4 directions), dead-end caps (all 4 directions), horizontal/vertical straights, cross/intersection, isolated pillar, and interior fill.
  - Method:
    1. Open `tools/sprite_browser_16bf_world.html` and examine tiles 183-199 systematically
    2. For each tile, determine its wall role by visual inspection (which edges have lit faces, which are dark)
    3. Cross-reference against the TMX-verified IDs listed above
    4. Identify any tiles in 183-199 not yet mapped (188, 193, 194, 195, 196, 197 are unmapped)
    5. Look for interior fill candidates in nearby ranges (dark solid stone)
    6. Look for L-shaped inner corner tiles if they exist (may be in 1095-1111 range or nearby)
    7. Determine whether the current 1095-1109 tiles should be kept as an alternative set or replaced entirely
  - Output: A complete mapping table in this plan file, updated under the "TMX-Verified Tile ID Reference" section above
  - Acceptance criteria:
    - Every role needed by the hybrid algorithm has at least one tile ID assigned
    - All assigned IDs verified to exist as files in `world_24x24/`
    - Interior fill tile identified (critical -- this is the most visible bug)
    - Rafe has visually confirmed the mapping using the sprite browser
  - Notes:
    - This is a collaborative task. The builder can propose IDs based on visual inspection of the sprite images, but Rafe should confirm the final picks.
    - The 183-199 range and the 1095-1109 range are two different visual styles. The TMX uses the 183-199 range. A decision is needed on whether to use the TMX style (183-199), the current style (1095-1109), or a mix. The plan recommends TMX style since those are proven to work together.

### Phase 2: Config and Data Structure Update

- [ ] **TASK-002: Redesign TileThemeData for role-based wall mapping**
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-001
  - Description: Replace the `Dictionary<int, int> WallAutotile` (bitmask-keyed) with a role-based wall mapping. The new structure maps semantic role names to tile IDs, since the hybrid algorithm has two lookup paths (cardinal bitmask for edges, role name for corners/fill).
  - Files to modify:
    - `src/Presentation/TileThemeConfig.cs` -- `TileThemeData` class, `GetAutoWallTile` method
  - New data structure:
    ```csharp
    // Replace Dictionary<int, int> WallAutotile with:
    public Dictionary<int, int> WallCardinal { get; set; } = new();  // bitmask 0-14 -> tile ID
    public Dictionary<string, int> WallDiagonal { get; set; } = new(); // role name -> tile ID
    // WallDiagonal keys: "corner_outer_nw", "corner_outer_ne", "corner_outer_sw",
    //                     "corner_outer_se", "interior_fill"
    ```
  - New API:
    ```csharp
    // GetAutoWallTile changes signature:
    public string? GetWallTile(string theme, int cardinalMask, int diagonalFloorMask)
    // cardinalMask: 0-15 (same as before)
    // diagonalFloorMask: 4-bit mask of which diagonals are floor
    //   bit3=NE, bit2=NW, bit1=SE, bit0=SW (only checked when cardinalMask==15)
    ```
  - Algorithm inside `GetWallTile`:
    1. If `cardinalMask < 15`: look up `WallCardinal[cardinalMask]` (same as current `WallAutotile`)
    2. If `cardinalMask == 15` and `diagonalFloorMask > 0`: determine which outer corner role applies, look up `WallDiagonal["corner_outer_XX"]`
    3. If `cardinalMask == 15` and `diagonalFloorMask == 0`: look up `WallDiagonal["interior_fill"]`
    4. Fallback chain: missing role -> interior_fill -> first available tile
  - Acceptance criteria:
    - `TileThemeData` has both `WallCardinal` and `WallDiagonal` dictionaries
    - `GetWallTile(theme, 15, 0)` returns interior fill tile
    - `GetWallTile(theme, 15, 1)` returns SW outer corner (diagonal bit 0 = SW is floor)
    - `GetWallTile(theme, 7, 0)` returns the bitmask-7 cardinal tile (unchanged behavior)
    - Backwards-compatible: if only `WallCardinal` is defined (no `WallDiagonal`), falls back to current behavior
    - Build: 0 errors introduced

- [ ] **TASK-003: Update TileThemeLoader for new YAML structure**
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-002
  - Description: Extend the manual YAML parser in `TileThemeLoader.cs` to handle the new `wall_diagonal` mapping block alongside the existing `wall_autotile` (renamed to `wall_cardinal`).
  - Files to modify:
    - `src/Presentation/TileThemeLoader.cs` -- parser state machine
  - New YAML structure (backwards-compatible):
    ```yaml
    themes:
      grey_stone:
        floor_primary: [746]
        floor_accent: [747, 748]
        wall_cardinal:           # renamed from wall_autotile
          0: 1105               # isolated pillar
          1: 1109               # dead end W
          # ... bitmasks 0-14 ...
          15: 189               # fallback for mask=15 (if wall_diagonal missing)
        wall_diagonal:           # NEW block
          corner_outer_nw: 189  # floor at SE diagonal
          corner_outer_ne: 190  # floor at SW diagonal
          corner_outer_sw: 191  # floor at NE diagonal
          corner_outer_se: 192  # floor at NW diagonal
          interior_fill: 188    # all 8 neighbors are walls (or whatever ID is correct)
        stair_down: [1036]
        stair_up: [1035]
        bones: [96, 90, 95]
    ```
  - Parser changes:
    - Recognize `wall_cardinal` as an alias for `wall_autotile` (accept either key, both populate `WallCardinal`)
    - Add `InDiagonal` parse state for `wall_diagonal:` block (string key -> int value at indent >= 6)
    - Populate `TileThemeData.WallDiagonal` from parsed entries
  - Backwards compatibility: if YAML has `wall_autotile:` instead of `wall_cardinal:`, still works (loader accepts both keys)
  - Acceptance criteria:
    - Loader parses both `wall_cardinal` and `wall_diagonal` blocks
    - Old `wall_autotile` key still works (mapped to `WallCardinal`)
    - `WallDiagonal` populated with role -> tile ID mapping
    - Build: 0 errors introduced
    - Existing tile_themes.yaml loads without errors (backwards-compatible)

- [ ] **TASK-004: Update tile_themes.yaml with verified tile IDs**
  - Status: pending
  - Layer: presentation (config only)
  - Type: art direction
  - Dependencies: TASK-001, TASK-003
  - Description: Update `config/tile_themes.yaml` with the complete tile mapping from TASK-001. Switch to TMX-verified floor tiles. Add the `wall_diagonal` block.
  - Files to modify:
    - `config/tile_themes.yaml`
  - Changes:
    - `floor_primary` -> TMX-verified IDs (746 or whichever Rafe confirms)
    - `floor_accent` -> TMX-verified accent tiles
    - `wall_autotile` -> renamed to `wall_cardinal` with updated IDs (if switching to 183-199 range)
    - Add `wall_diagonal` block with corner and fill IDs
    - Update `dirt` theme to match (or continue sharing grey_stone walls)
    - Verify `bones` IDs (96, 90, 95) still work with the new floor tiles visually
  - Acceptance criteria:
    - YAML loads without parser errors
    - All referenced tile IDs exist as files on disk
    - `wall_diagonal` block has all 5 required entries (4 corners + interior_fill)
    - Floor tiles updated to TMX-verified IDs

### Phase 3: Algorithm Update

- [ ] **TASK-005: Implement hybrid autotile algorithm in DungeonRenderer**
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-002
  - Description: Replace `ComputeWallBitmask` with a hybrid method that computes both cardinal and diagonal masks. Update the wall tile selection call in `Render()` to use the new `GetWallTile` API.
  - Files to modify:
    - `src/Presentation/Map/DungeonRenderer.cs`
  - Changes:
    - Replace `ComputeWallBitmask(map, x, y)` with `ComputeWallMasks(map, x, y)` returning `(int cardinal, int diagonal)`
    - Cardinal mask: same as current (bits: N=8, S=4, E=2, W=1)
    - Diagonal mask: only computed when cardinal == 15 (optimization). Bits: NE=8, NW=4, SE=2, SW=1. A bit is SET when that diagonal neighbor is floor (walkable).
    - Update wall tile lookup: `themeConfig.GetWallTile(themeName, cardinal, diagonal)` instead of `themeConfig.GetAutoWallTile(themeName, bitmask)`
    - Out-of-bounds positions continue to count as walls (existing behavior via `IsWalkable` returning false)
  - Implementation detail for diagonal mask:
    ```csharp
    private static (int Cardinal, int Diagonal) ComputeWallMasks(GameMap map, int x, int y)
    {
        int cardinal = 0;
        if (!map.IsWalkable(x,     y - 1)) cardinal |= 8; // North
        if (!map.IsWalkable(x,     y + 1)) cardinal |= 4; // South
        if (!map.IsWalkable(x + 1, y    )) cardinal |= 2; // East
        if (!map.IsWalkable(x - 1, y    )) cardinal |= 1; // West

        int diagonal = 0;
        if (cardinal == 15) // Only check diagonals when all cardinals are walls
        {
            if (map.IsWalkable(x + 1, y - 1)) diagonal |= 8; // NE is floor
            if (map.IsWalkable(x - 1, y - 1)) diagonal |= 4; // NW is floor
            if (map.IsWalkable(x + 1, y + 1)) diagonal |= 2; // SE is floor
            if (map.IsWalkable(x - 1, y + 1)) diagonal |= 1; // SW is floor
        }

        return (cardinal, diagonal);
    }
    ```
  - Acceptance criteria:
    - `ComputeWallMasks` returns correct cardinal mask for all 16 combinations
    - Diagonal mask is always 0 when cardinal < 15
    - Diagonal mask correctly identifies floor diagonals when cardinal == 15
    - Wall tile selection in `Render()` uses the new method
    - Build: 0 errors introduced

### Phase 4: Visual Verification

- [ ] **TASK-006: Integration test -- visual room corner verification**
  - Status: pending
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-004, TASK-005
  - Description: Boot the game and verify wall rendering. This is a manual visual test that confirms the autotile algorithm produces correct tiles at room boundaries.
  - Verification checklist:
    - [ ] Room edges show directional edge tiles (not all the same)
    - [ ] Room corners show outer corner tiles (not interior fill)
    - [ ] Interior walls (far from any room) show solid fill tile
    - [ ] Corridors have correct edge tiles on both sides
    - [ ] T-junctions where corridors meet rooms look correct
    - [ ] No "missing tile" errors in console
    - [ ] Floor tiles are the TMX-verified set (darker stone, not the bright grey flagstone)
    - [ ] Bones decorations still appear and look reasonable on the new floor tiles
    - [ ] Stair tiles still render correctly
    - [ ] Minimap unaffected
    - [ ] FOV dimming still works on wall tiles
    - [ ] Multiple floor transitions produce consistent results
  - Acceptance criteria:
    - All checklist items pass
    - No `GD.PrintErr` related to tile loading
    - Room boundaries are visually distinct from interior fill
    - A screenshot comparison shows clear improvement over current rendering

- [ ] **TASK-007: Verify bones decoration tile compatibility**
  - Status: pending
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-006
  - Description: The bones decoration tiles (96, 90, 95) were selected to work with the original floor tiles (1091). With the floor switching to TMX-verified tiles (746-748), the bones may not look right (color mismatch, wrong scale, etc.). Verify visually and re-pick if needed.
  - Acceptance criteria:
    - Bones tiles look natural on the new floor tiles
    - If bones need new IDs, the YAML is updated and verified
    - ~2.5% decoration frequency unchanged

### Phase 5: Polish (Optional -- Inner Corner Overlays)

- [ ] **TASK-008: Research inner corner overlay system**
  - Status: pending
  - Layer: presentation
  - Type: analysis
  - Dependencies: TASK-006
  - Description: The TMX "corners" layer uses overlay tiles (1095-1111 range) placed on top of floor tiles at inner corners where two walls meet at a right angle. These smooth the diagonal transition between wall and floor. This is a second-pass rendering system that would require:
    1. A new render pass in DungeonRenderer (Pass 1.5, between base tiles and stair overlays)
    2. For each floor tile, check if adjacent walls form an inner corner
    3. If so, overlay the appropriate inner corner tile on top of the floor
  - This task is analysis only: determine whether the visual improvement justifies the complexity. Produce a recommendation (implement / defer / skip).
  - Acceptance criteria:
    - Clear recommendation with visual examples
    - If "implement": a task breakdown for the overlay system
    - If "defer": what trigger would make it worth revisiting

---

## Risks and Decisions

### DECISION NEEDED: Which tile set for walls?

Two complete wall tile sets exist in the Oryx 16bf world sheet:
- **183-199 range**: TMX-verified. Darker stone texture. Proven to work together in Oryx's own example maps. Some IDs still need role verification.
- **1095-1109 range**: Currently used. Brighter "lit face" stone. All 16 cardinal bitmask entries mapped. Missing outer corner tiles (the whole reason for this plan).

**Options:**
1. **Switch entirely to 183-199** (TMX set). Requires completing TASK-001 audit. Visually consistent with TMX floor tiles (746-748). Outer corners already identified (189-192).
2. **Keep 1095-1109 for cardinals, add 189-192 for outer corners**. Mixes two visual styles -- may look inconsistent.
3. **Keep 1095-1109 and find outer corners in the same visual family**. Need to find matching corner tiles -- they may not exist in this style.

**Recommendation:** Option 1 (full switch to TMX set). The TMX is Oryx's own proof that these tiles work together. Mixing styles risks visual inconsistency.

### RISK: Multiple exposed diagonals (LOW)

When `cardinalMask == 15` and 2+ diagonals are floor, the wall is at the back of a T-junction or cross intersection. For rectangular room dungeons this is uncommon. The simplest handling: pick the first exposed diagonal (clockwise from NE) and use that corner tile. Visually this will be slightly wrong for multi-corner cases, but these positions are typically in explored-but-dark fog-of-war and rarely scrutinized.

For a more correct solution, the inner corner overlay system (TASK-008) would handle these cases by layering multiple overlays.

### RISK: Backwards compatibility of YAML key rename (LOW)

Renaming `wall_autotile` to `wall_cardinal` could break if anything else reads this YAML. Mitigated by accepting both keys in the loader. The old key continues to work.

### RISK: Interior fill tile identification (MEDIUM)

The TMX-verified list does not include a definitive interior fill tile. Tile 188 or a solid dark tile from another range may be needed. TASK-001 must identify this before Phase 2 can proceed. If no suitable tile exists in the world sheet, a programmatic solid-color rect could be used (like the tap indicator).

### NOT IN SCOPE

- Logic layer changes (zero)
- Balance pipeline changes (zero)
- Isometric rendering changes (dormant code, untouched)
- Inner corner overlay system (Phase 5 is optional/deferred)
- Additional themes (crypt, moss) -- those are TASK-011 in PLAN_topdown_switch.md
- NUnit tests (this is purely visual rendering; the logic layer GameMap is unchanged)
