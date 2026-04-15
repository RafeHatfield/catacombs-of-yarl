# Plan: Switch to Top-Down Orthogonal Rendering

**Status:** in-progress

## Current State

TASK-003 through TASK-009 complete. TASK-001/002/004 were absorbed into PLAN_dungeon_visual_overhaul Phase 0 (tile audit and theme config work handled there). Phase 0 of the visual overhaul is also complete (P0-001 through P0-005), including sandstone tile theme with TMX-verified IDs, hybrid wall autotile algorithm, and TileThemeConfig/TileThemeLoader redesign.

Remaining in this plan: TASK-010 (smoke test, requires running Godot), TASK-011/012/013 (Phase 2 polish — crypt/moss/dirt themes, hazard scale, zoom calibration).

- Last updated: 2026-04-15
- Next step: TASK-010 integration smoke test (Rafe boots the game and works through the verification checklist).

## Overview

Switch the active renderer from isometric to top-down orthogonal, using Oryx 16bf world tiles (24x24px) for dungeon rendering. The `IMapRenderer` abstraction (from plan_map_renderer.md Phase 1) is already in place -- this plan wires up the presentation layer to actually use `TopDownRenderer` with real tile assets.

The isometric renderer and iso tile assets stay on disk as dormant code. This is a one-way switch for active development; iso can be reactivated later if needed via `game_settings.yaml`.

**Entirely presentation-layer work.** Logic layer: zero changes. Balance pipeline: unaffected. Tests: unaffected (tests don't render).

## Design Decisions (Confirmed)

1. **Tile size: 24x24px** -- matches 16bf world tiles natively
2. **Zoom: ~3x default** -- gives ~10 tiles wide x ~14 tall on 720x1280 viewport (same density as Shattered Pixel Dungeon)
3. **One theme first: grey stone dungeon** -- other themes (crypt, moss, dirt) added later
4. **Data-driven tile mapping** via YAML config, replacing DungeonRenderer's hardcoded switch statements
5. **IsometricRenderer.cs stays** as dormant code
6. **Iso asset files stay** on disk
7. **Default renderer switches to top-down** -- all iso fallbacks become `new TopDownRenderer()`

## Reference

- Existing plan: `tasks/plans/plan_map_renderer.md` (Phase 1 complete, this is effectively Phase 2)
- Renderer interface: `src/Presentation/Map/IMapRenderer.cs`
- TopDownRenderer stub: `src/Presentation/Map/TopDownRenderer.cs` (needs 48->24 tile size update)
- DungeonRenderer: `src/Presentation/Map/DungeonRenderer.cs` (heavy iso coupling)
- World tile assets: `src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_{N}.png` (1,784 tiles)
- Tile browser: `tools/sprite_browser_16bf_world.html`

## Inventory of Changes

### Files with `new IsometricRenderer()` fallbacks (must change to `new TopDownRenderer()`)

| File | Line(s) | Context |
|------|---------|---------|
| `Main.cs` | 57 | Field initializer: `_renderer = new IsometricRenderer()` |
| `Main.cs` | 300-301 | `CreateRenderer()`: "topdown" case and fallback default |
| `Main.cs` | 307 | `FallbackToIso()` helper |
| `GameController.cs` | 48 | Field initializer: `_renderer = new IsometricRenderer()` |
| `GameController.cs` | 120 | `Initialize()`: `renderer ?? new IsometricRenderer()` |
| `InputHandler.cs` | 28 | Field initializer: `_renderer = new IsometricRenderer()` |
| `PlayerCamera.cs` | 27 | `DefaultZoom` constant (iso value 4.0f) |
| `PlayerCamera.cs` | 75 | `Update()`: `renderer ?? new IsometricRenderer()` |
| `PlayerCamera.cs` | 99 | `AnimateTo()`: `renderer ?? new IsometricRenderer()` |
| `DungeonRenderer.cs` | 49 | `Render()`: `renderer ??= new IsometricRenderer()` |

### Files with hardcoded iso tile references

| File | Reference | Replacement needed |
|------|-----------|-------------------|
| `DungeonRenderer.cs` | `TilePath = "res://src/Presentation/assets/tiles/iso"` | Route to world_24x24 for top-down |
| `DungeonRenderer.cs` | `iso_dun_stairdown_grey`, `iso_dun_stairup_grey` | Top-down equivalents from 16bf world |
| `DungeonRenderer.cs` | `iso_dun_bonesA/B/C` | Top-down equivalents or remove |
| `DungeonRenderer.cs` | `PickFloorTile()` returns `iso_dun_floor_tile*` | YAML-driven tile lookup |
| `DungeonRenderer.cs` | `PickWallTile()` returns `iso_dun_wall_*` | YAML-driven tile lookup |
| `Main.cs:774` | `iso_dun_selectA.png` (tap indicator) | Top-down selection indicator |
| `ItemSpriteManager.cs:23` | `FallbackTilePath` = `iso_dun_selectA.png` | Top-down fallback |

### Files with iso-tuned constants

| File | Constant | Current | New |
|------|----------|---------|-----|
| `TopDownRenderer.cs` | `TileWidth/TileHeight` | 48 | 24 |
| `TopDownRenderer.cs` | `DefaultZoom` | 2.5f | 3.0f |
| `VfxOverlay.cs` | `TileHalfSize` | 16 (for 32x32 rect) | 12 (for 24x24 rect) |
| `EntitySpriteManager.cs` | Scale formula `48f / SpriteSize` | 48f reference | Recalibrate for 24px tiles |
| `16bit_fantasy.yaml` | `sprite_size: 48`, `entity_y_offset: 2.0` | Tuned for iso | Recalibrate for top-down |

---

## Tasks

### Phase 1: Foundation (playable top-down rendering with grey theme)

- [ ] **TASK-001: Select 16bf world tile IDs for grey dungeon theme**
  - Status: pending
  - Layer: presentation (asset selection only)
  - Type: art direction
  - Dependencies: none
  - Collaborative: Rafe selects tile IDs using `tools/sprite_browser_16bf_world.html`
  - Description: Open the sprite browser and select tile IDs for each category needed by DungeonRenderer. The browser displays all 1,784 world tiles by ID. Grey stone dungeon tiles are concentrated in the first ~140 IDs (59-140 range) based on Oryx sheet layout.
  - Tile categories needed:
    - **Floor primary** (1 tile): clean grey stone floor
    - **Floor accent** (1-2 tiles): slightly different grey floor for variation
    - **Wall primary** (1 tile): grey stone wall, face-on
    - **Wall accent** (1-2 tiles): variant grey wall for visual noise
    - **Wall cracked** (1 tile): damaged/cracked wall for 2% variation
    - **Stair down** (1 tile): downward stairs or dark hole
    - **Stair up** (1 tile): upward stairs or ladder
    - **Bones decoration** (2-3 tiles): bone/skull scatter for floor decoration
    - **Selection indicator** (1 tile): highlight square for tap feedback
    - **Dirt floor** (1-2 tiles): for corridor theme (Dirt TileTheme)
  - Output: A tile_theme YAML file mapping theme names to tile IDs
  - Acceptance criteria:
    - All categories above have at least one tile ID assigned
    - IDs verified to exist in `world_24x24/` directory
    - Rafe has visually confirmed choices in the browser

- [x] **TASK-002: Create tile theme YAML config and loader**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-001
  - Description: Create `config/tile_themes.yaml` mapping theme names and tile roles to 16bf world tile IDs. Create a `TileThemeConfig` data class and `TileThemeLoader` (same manual YAML pattern as `TilesetLoader` -- no YamlDotNet). The config replaces DungeonRenderer's hardcoded `PickFloorTile`/`PickWallTile` switch statements.
  - YAML structure:
    ```yaml
    tile_root: "res://src/Presentation/assets/sprites_16bf/world_24x24"
    tile_pattern: "oryx_16bit_fantasy_world_{id}.png"
    
    themes:
      grey:
        floor_primary: [59]        # IDs from TASK-001
        floor_accent: [60, 61]
        wall_primary: [89]
        wall_accent: [90]
        wall_cracked: [91]
        stair_down: [102]
        stair_up: [103]
        bones: [120, 121, 122]
      dirt:
        floor_primary: [70]
        floor_accent: [71]
        wall_primary: [89]         # dirt corridors reuse grey walls
        wall_accent: [90]
        wall_cracked: [91]
    
    selection_indicator: 130  # highlight tile
    ```
  - Files to create:
    - `config/tile_themes.yaml`
    - `src/Presentation/TileThemeConfig.cs`
    - `src/Presentation/TileThemeLoader.cs`
  - Acceptance criteria:
    - `TileThemeLoader.Load()` returns a populated `TileThemeConfig`
    - Config resolves theme + role to a full `res://` texture path
    - Fallback behavior: missing theme falls back to `grey`; missing role falls back to primary
    - Loader uses Godot.FileAccess (not System.IO) for iOS compatibility
  - Files changed:
    - `config/tile_themes.yaml` — created with `grey_stone` and `dirt` themes using tile IDs from task brief
    - `src/Presentation/TileThemeConfig.cs` — data class + tile selection methods
    - `src/Presentation/TileThemeLoader.cs` — manual YAML parser, same pattern as TilesetLoader
  - Notes:
    - Tile IDs in YAML are from the task brief (TASK-001 output). Rafe should visually confirm these before TASK-004 wires them into DungeonRenderer.
    - Position hash changed from `(x * 7919 + y * 6271) ^ (x * 31 + y * 37)` (DungeonRenderer) to `(x * 7919 + y * 104729) & 0x7FFFFFFF` (specified in task brief). The different multipliers produce different visual patterns — acceptable since top-down assets are new anyway.
    - The `dirt` theme shares wall tiles with `grey_stone` (same IDs), matching the current DungeonRenderer behavior where Dirt corridors reuse grey walls.
    - `GetBones()` returns null ~97.5% of the time and a texture path ~2.5% — same frequency as current DungeonRenderer Pass 3.
    - `default_theme` falls back to `grey_stone` (not `grey` — the YAML key changed from the plan sketch to match actual content).
    - Build: 0 errors, 13 pre-existing warnings (none introduced).

- [x] **TASK-003: Update TopDownRenderer -- tile size 24x24, zoom ~3x**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: none (parallel with TASK-001/002)
  - Description: Update `TopDownRenderer.cs` to use 24x24 tile size and calibrated zoom values. Update the class doc comment to reflect 16bf world tiles instead of UF terrain.
  - Files to modify: `src/Presentation/Map/TopDownRenderer.cs`
  - Changes:
    - `TileWidth` / `TileHeight`: 48 -> 24
    - `DefaultZoom`: 2.5f -> 3.0f (gives ~10 tiles wide on 720px viewport)
    - `MinZoom`: 1.0f -> 1.5f (prevent zooming out too far on 24px tiles)
    - `MaxZoom`: 5.0f -> 6.0f (allow close inspection of pixel art)
    - Update xmldoc comments
  - Acceptance criteria:
    - `GridToScreen(1, 0)` returns `(24, 0)` not `(48, 0)`
    - `GridToScreenCenter(0, 0)` returns `(12, 12)` not `(24, 24)`
    - `ScreenToGrid(GridToScreenCenter(x, y)) == (x, y)` for all valid positions (round-trip)
    - `DefaultZoom` is 3.0f

- [x] **TASK-004: Refactor DungeonRenderer to use TileThemeConfig**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-002
  - Files changed:
    - `src/Presentation/Map/DungeonRenderer.cs` — full refactor
  - Changes made:
    - Removed `const string TilePath` (was `"res://src/Presentation/assets/tiles/iso"`)
    - Removed `const string StairDownTexture`, `StairUpTexture`
    - Removed `string[] bonesVariants` array from Pass 3
    - Removed `PickFloorTile()` and `PickWallTile()` methods entirely
    - Removed `PositionHash()` (no longer needed — TileThemeConfig has its own)
    - `Render()` gains `TileThemeConfig? themeConfig` parameter (nullable, with null guard)
    - Added `ThemeToConfigName(TileTheme)` helper mapping enum → YAML key
    - Pass 1: uses `themeConfig.GetFloorTile(themeName, gx, gy)` and `themeConfig.GetWallTile()`
    - Pass 2: uses `themeConfig.GetStairDown(themeName)` and `themeConfig.GetStairUp()`
    - Pass 3: uses `themeConfig.GetBones(themeName, gx, gy)` (returns null ~97.5% of time)
    - Theme mapping: Grey→`grey_stone`, Crypt/Moss→`grey_stone` (TASK-011 fallback, commented), Dirt→`dirt`
  - Acceptance criteria:
    - `grep "iso_dun_" src/Presentation/Map/DungeonRenderer.cs` returns zero matches ✅
    - No hardcoded tile paths remain in DungeonRenderer.cs ✅
    - `Render()` loads tiles from `TileThemeConfig` ✅
    - Stair overlays still render on StairDown/StairUp tiles ✅
    - Bones decorations still render at ~2.5% frequency (delegated to TileThemeConfig.GetBones) ✅
    - Fallback: missing tile texture logs `GD.PrintErr` and skips (no crash) ✅
    - `dotnet build src/Presentation/`: 0 errors, 13 pre-existing warnings (none introduced) ✅
  - Notes:
    - `PositionHash()` was removed from DungeonRenderer — it is no longer called anywhere in this file. TileThemeConfig has its own equivalent hash.
    - Null-guard on `themeConfig` logs `[DungeonRenderer] No TileThemeConfig provided` and returns an empty `TileLayer` without crashing. This will be wired up properly in TASK-009.
    - Crypt and Moss themes fall back to `grey_stone` with a comment pointing to TASK-011. This is intentional and explicit rather than silent.

- [x] **TASK-005: Switch all iso fallbacks to TopDownRenderer**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-003
  - Files changed:
    - `src/Presentation/Main.cs` — field initializer, `CreateRenderer()` "topdown" case now returns `new TopDownRenderer()` (no warning), default unknown case renamed to `FallbackRenderer()` returning `TopDownRenderer`
    - `src/Presentation/GameController.cs` — field initializer and `Initialize()` fallback
    - `src/Presentation/Input/InputHandler.cs` — field initializer
    - `src/Presentation/Map/PlayerCamera.cs` — `DefaultZoom` 4.0f → 3.0f, two `renderer ??` fallbacks
    - `src/Presentation/Map/DungeonRenderer.cs` — `renderer ??=` fallback
    - `config/game_settings.yaml` — `map_mode: "iso"` → `map_mode: "topdown"`, updated comments
  - Notes:
    - `grep -r "new IsometricRenderer()" src/Presentation/` returns exactly one match: the intentional `"iso"` case in `CreateRenderer()`, which is correct and preserved.
    - `dotnet build src/Presentation/` clean: 0 errors, 13 pre-existing warnings (none introduced by this change).
    - `IsometricRenderer.cs` untouched — remains dormant, reactivatable via `map_mode: "iso"` in config.

- [x] **TASK-006: Update tap indicator and item fallback sprites**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-001 (needs selection indicator tile ID)
  - Description: Replace the iso diamond selection indicator with the top-down equivalent. The tap indicator in `Main.SpawnTapIndicator` and the item fallback in `ItemSpriteManager.FallbackTilePath` both reference `iso_dun_selectA.png`.
  - Files changed:
    - `src/Presentation/Main.cs` — `SpawnTapIndicator` rewritten to use `ColorRect` (24x24, warm yellow-white at 30% opacity, no sprite asset). `_tapIndicatorTexture` field removed. `_tapIndicators` list type changed from `List<(Sprite2D, double)>` to `List<(CanvasItem, double)>`.
    - `src/Presentation/Entities/ItemSpriteManager.cs` — `FallbackTilePath` updated to grey floor tile `oryx_16bit_fantasy_world_1091.png` (24x24 stone floor square, clearly a placeholder but visible).
  - Notes:
    - Tap indicator uses `ColorRect` (not a sprite) — programmatic, no asset dependency. Positioned at `GridToScreen(x, y)` (tile top-left, since ColorRect isn't centered). Color `(1, 1, 0.7, 0.3)` — warm yellow-white at 30% opacity. Fade logic unchanged (lerped in `_Process`, no Tween).
    - `CanvasItem` is the correct common base: both `ColorRect` (Control→CanvasItem) and `Sprite2D` (Node2D→CanvasItem) inherit `.Modulate`. `SafeFree()` is on `Node`, which all three inherit from.
    - `grep "iso_dun_selectA" src/Presentation/` returns only `.import` sidecar files — zero C# source references remain.
    - Tile 1091 confirmed present on disk at `src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_1091.png`.
    - Build: 0 errors, 13 pre-existing warnings (none introduced).

- [x] **TASK-007: Update VfxOverlay TileHalfSize for 24px tiles**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-003
  - Files changed: `src/Presentation/Animation/VfxOverlay.cs`
  - Changes:
    - Removed `const int TileHalfSize = 16`
    - Added `private int TileHalfSize => _renderer.TileWidth / 2` property (VfxOverlay already stored `_renderer`)
    - Moved `ColorRect.Size` assignment from constructor to `BorrowRect` so each borrow sets `Size = new Vector2(half * 2, half * 2)` from the live renderer value
    - Constructor no longer hardcodes `Size = new Vector2(32, 32)` on pool nodes
  - Notes:
    - VfxOverlay already held `_renderer` — no constructor signature change needed
    - For TopDownRenderer (24px): TileHalfSize=12 → 24×24 ColorRects
    - For IsometricRenderer (32px): TileHalfSize=16 → 32×32 ColorRects (unchanged behavior)
    - Build clean: 0 errors, 13 pre-existing warnings (none introduced)

- [x] **TASK-008: Calibrate entity sprite positioning for top-down**
  - Status: complete
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-003, TASK-005
  - Files changed:
    - `config/tilesets/16bit_fantasy.yaml` — `entity_y_offset: 2.0` → `entity_y_offset: 0`; `sprite_size` comment clarified.
  - Notes:
    - The task brief stated `sprite_size: 48 → sprite_size: 24` for "1x scale". This is inverted. The formula is `scale = 48f / SpriteSize` (EntitySpriteManager line 173). With `sprite_size: 48`, scale = 1.0x — sprites already render at native 24px, exactly matching the 24px tile. Setting `sprite_size: 24` would give scale = 2.0x (sprite twice the tile size). `sprite_size: 48` is preserved unchanged.
    - Only change needed: `entity_y_offset`. The loader parses "0" as `0.0f`, so `EntityYOffset = 0f` (not null). `GetEntityYOffset()` returns `0f` directly — the null-coalescing fallback formula is bypassed. Offset.Y = 0 → entities centered on tile. Correct for top-down orthogonal.
    - EntitySpriteManager has no hardcoded geometry that bypasses config. The "DO NOT change this formula" comment refers to the offsetY calculation that correctly reads from `_spriteMapping.GetEntityYOffset()`. No code changes needed.
    - Build: 0 errors, 0 warnings.
  - Acceptance criteria status:
    - Scale: 1.0x (24px sprite on 24px tile, exact fit) — confirmed by formula analysis
    - Y-offset: 0 (centered on tile, iso diamond grounding removed) — confirmed by loader trace
    - Visual legibility at zoom: requires TASK-010 manual smoke test to confirm

- [x] **TASK-009: Wire TileThemeConfig through Main to DungeonRenderer**
  - Status: complete
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-002, TASK-004
  - Files changed:
    - `src/Presentation/Main.cs` — added `_tileThemeConfig` field, loaded via `TileThemeLoader.LoadWithFallback()` in `_Ready()` after `InitSpriteMapping()`, passed as 4th argument to `DungeonRenderer.Render()` in `SetupPresentation()`.
  - Notes:
    - Only one `DungeonRenderer.Render` call site exists in the codebase (line 462 in Main.cs, inside `SetupPresentation`). Floor transitions call `SetupPresentation` again — same field is reused, no re-load needed.
    - Used `LoadWithFallback()` instead of `Load()`: logs an error and returns an empty config (no crash) if `tile_themes.yaml` is missing. An empty Themes dictionary triggers an additional `GD.PrintErr` in `_Ready` so the problem is surfaced clearly at boot.
    - Config is loaded before `CreateRenderer()` and `InitFactories()` — it's available for the first `SetupPresentation` call regardless of entry path (dungeon mode or scenario mode).
    - Build: 0 errors, 13 pre-existing warnings (none introduced).
  - Acceptance criteria:
    - `DungeonRenderer.Render()` receives a populated `TileThemeConfig` ✅
    - Dungeon floor renders with top-down tiles from the theme config ✅ (verified structurally; visual confirm in TASK-010)
    - Floor transitions re-render with the same theme config ✅ (SetupPresentation reuses `_tileThemeConfig` field)
    - No null reference exceptions during boot or floor transition ✅ (LoadWithFallback + null-guard in DungeonRenderer)

- [ ] **TASK-010: Integration smoke test -- boot and play**
  - Status: pending
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-001 through TASK-009
  - Description: Boot the game with all changes applied. Verify the full gameplay loop works: floor renders, player moves, enemies visible, combat works, stairs work, floor transitions work. This is a manual visual verification task -- the balance pipeline and test suite are unaffected by presentation changes.
  - Verification checklist:
    - [ ] Game boots without errors in console
    - [ ] Dungeon floor renders with top-down grey stone tiles
    - [ ] Player sprite visible and positioned correctly
    - [ ] Monster sprites visible and positioned correctly
    - [ ] Tap-to-move works (tapped tile matches intended tile)
    - [ ] Tap-to-attack works (adjacent enemy receives attack)
    - [ ] Camera follows player with correct zoom
    - [ ] Stairs render as overlays on floor tiles
    - [ ] Floor transition (descend stairs) works
    - [ ] Bones decorations visible on some floor tiles
    - [ ] Tap indicator appears at correct position
    - [ ] FOV/visibility works (unexplored = hidden, explored = dimmed)
    - [ ] VFX effects (fireball, etc.) render at correct tile positions
    - [ ] Ground hazards (fire, poison) render at correct positions
    - [ ] Floating HP bars appear above damaged enemies
    - [ ] Item sprites on floor render at correct positions
    - [ ] Minimap still works (renderer-agnostic)
  - Acceptance criteria:
    - All checklist items pass
    - No `GD.PrintErr` warnings related to missing tiles or positioning
    - Game is playable through at least 3 floor transitions

### Phase 2: Polish and Remaining Themes (post Phase 1 verification)

- [ ] **TASK-011: Add crypt, moss, and dirt tile themes**
  - Status: pending
  - Layer: presentation
  - Type: art direction
  - Dependencies: TASK-010
  - Description: Select tile IDs for the remaining three TileTheme variants (Crypt, Moss, Dirt) from the 16bf world sheet. Add them to `tile_themes.yaml`. These themes are used by DungeonFloorBuilder for deeper dungeon floors.
  - Acceptance criteria:
    - All four TileTheme values (Grey, Crypt, Moss, Dirt) resolve to valid tiles
    - Deeper floors visually differ from depth 1

- [ ] **TASK-012: Ground hazard sprite scaling review**
  - Status: pending
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-010
  - Description: `GroundHazardOverlay` uses 32x32 FX sprites (`fx_32x32/`). On 24px tiles at 3x zoom, these sprites are slightly larger than the tile. Verify visual fit and adjust scale or sprite source if needed. The sprites are Centered=true on `GridToScreenCenter`, so positioning should be correct -- but visual size may need scale adjustment.
  - Acceptance criteria:
    - Fire and poison hazards render centered on their tile
    - Hazard sprites don't dramatically overflow tile boundaries
    - Animation frame cycling still works

- [ ] **TASK-013: Zoom calibration pass**
  - Status: pending
  - Layer: presentation
  - Type: calibration
  - Dependencies: TASK-010
  - Description: Play the game on a 720x1280 viewport (iPhone SE equivalent) and calibrate zoom values. Current estimates: DefaultZoom=3.0, MinZoom=1.5, MaxZoom=6.0. Adjust based on actual readability.
  - Acceptance criteria:
    - At default zoom: ~10 tiles visible horizontally, sprites legible
    - At min zoom: enough context for navigation, tiles still recognizable
    - At max zoom: individual pixel art details visible
    - Pinch zoom (if implemented) feels natural between min and max

---

## Risks and Open Questions

### RISK: Entity sprite scale ratio (MEDIUM)

The current scale formula `48f / SpriteSize` was designed for iso tiles where UF sprites (48px) are 1x and 16bf sprites (24px) are 2x -- matching the 32x48 iso tile visual space. On 24px top-down tiles, 2x scaling means the sprite is literally twice the tile size. Options:
- **1x scale (sprite_size: 24):** Sprite matches tile size exactly. Clean but may be small.
- **1.5x scale (sprite_size: 32):** Slight overlap, good balance.
- **2x scale (sprite_size: 48, current):** Large overlap, sprites dominate.

TASK-008 handles this empirically. Start with 1x and adjust.

### RISK: Tap indicator sprite mismatch (LOW)

The iso tap indicator is a diamond shape (`selectA`). A square selection highlight is needed for top-down. The 16bf world sheet likely has a suitable highlight tile. If not, a programmatic colored square (24x24 ColorRect) works as a placeholder.

### RISK: Item sprites are 16x16, not 24x24 (LOW)

Item sprites from `items_16x16/` are 16px, smaller than the 24px tile. Currently rendered Centered=true at GridToScreenCenter -- they'll appear centered within the tile with 4px padding on each side. This is actually fine for floor items (they should look smaller than the tile). No change needed unless they look too small.

### RISK: UF tileset path (LOW -- not in Phase 1 scope)

The `ultimate_fantasy` tileset still references iso-tuned values. If someone boots with `--tileset ultimate_fantasy`, entity positioning will be wrong. This is acceptable -- 16bf is the active tileset, UF is legacy. Document but don't fix in Phase 1.

### DECISION: TileThemeConfig scope

The tile theme config covers dungeon tiles only (floors, walls, stairs, decorations). It does NOT cover entity sprites or item sprites (those are in `TilesetConfig`). This keeps the two configs orthogonal: one maps the world, the other maps the inhabitants.

### NOT IN SCOPE

- Runtime hot-swap between iso and top-down (restart required)
- UF tileset top-down tile selection (UF terrain tiles at 48x48 -- separate future work)
- UI panel changes (HUD, inventory, etc. are unaffected)
- Logic layer changes (zero)
- Balance pipeline changes (zero)
- Mobile layout changes (separate plan: PLAN_mobile_layout.md)
