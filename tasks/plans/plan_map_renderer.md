# Plan: Configurable Map Renderer (Isometric / Top-Down 2D)

**Status:** Not started

## What this plan does

Extracts the hardcoded `IsometricMapper` static class into an `IMapRenderer` interface with two implementations: `IsometricRenderer` (current behavior) and `TopDownRenderer` (flat 2D grid). The render mode is a player-facing config option in `game_settings.yaml`, switchable from the Options menu (restart to apply, same pattern as tileset switching). All presentation-layer consumers receive the renderer via injection rather than calling static methods.

**Entirely presentation-layer work.** Logic layer: zero changes.

## Why this matters

Some players prefer isometric, some prefer top-down. The architecture already supports this cleanly — the logic layer is completely grid-based and renderer-agnostic. The tileset switching system (plan_tileset_switching.md) proved the config-injection-at-boot pattern. This applies the same approach to coordinate mapping.

## PoC reference

No direct PoC equivalent — the Python prototype was terminal-based (curses). The coordinate mapping abstraction is new to the C# build.

## Current state

### IsometricMapper call sites (complete audit)

All calls are in the presentation layer. No logic layer references exist.

| File | Methods used | Call count | Notes |
|------|-------------|------------|-------|
| `DungeonRenderer.cs` | `GridToScreen`, `GetTileSortOrder` | 6 | |
| `EntitySpriteManager.cs` | `GridToScreenCenter`, `GetEntitySortOrder` | 4 | |
| `ItemSpriteManager.cs` | `GridToScreenCenter`, `GetTileSortOrder` | 2 | |
| `TurnAnimator.cs` | `GridToScreenCenter` | 1 | |
| `InputHandler.cs` | `ScreenToGrid` | 1 | |
| `GameController.cs` | `ScreenToGrid` | 1 | Called from `OnLongPress` — missing `ToLocal()` (see risks) |
| `PlayerCamera.cs` | `GridToScreen` | 3 | |
| `Main.cs` | `ScreenToGrid`, `GridToScreenCenter` | 2 | Tap indicator path also hardcoded to iso asset |
| `FloorTransitionTests.cs` | `GridToScreenCenter` | 1 (test) | |

**Total: 21 call sites across 9 files (8 production + 1 test).**

### Renderer-varying assets (beyond coordinate math)

These assets are hardcoded to iso-specific files and must vary by renderer mode. All addressed in TASK-006:

| Location | Hardcoded path | Problem |
|----------|---------------|---------|
| `Main.SpawnTapIndicator` | `iso_dun_selectA.png` | Diamond shape wrong in top-down |
| `ItemSpriteManager.FallbackTilePath` | `iso_dun_selectA.png` | Diamond fallback wrong in top-down |
| `DungeonRenderer.StairDownTexture` | `iso_dun_stairdown_grey` | Iso-prefixed, no top-down equivalent yet |
| `DungeonRenderer.StairUpTexture` | `iso_dun_stairup_grey` | Iso-prefixed, no top-down equivalent yet |
| `DungeonRenderer.bonesVariants` | `iso_dun_bonesA/B/C` | Iso-prefixed, no top-down equivalent yet |

### What varies between modes

| Aspect | Isometric | Top-Down 2D |
|--------|-----------|-------------|
| Tile size | 32×48 (diamond) | 48×48 (square, UF terrain native) |
| GridToScreen | `(x-y)*16, (x+y)*12` | `x*48, y*48` |
| GridToScreenCenter | top-left + `(16, 24)` | top-left + `(24, 24)` |
| ScreenToGrid | Diamond inversion with offset | Simple division |
| Z-order tiles | `(x+y)*2` (painter's algo) | `y*2` (row-major) |
| Z-order entities | `(x+y)*2+1` | `y*2+1` |
| Entity Y offset | `-0.15 * h * scale` (in EntitySpriteManager) | `0` (centered) |
| Tile rendering | `Centered = false` (top-left positioned) | `Centered = false` |
| Tile assets | `iso_dun_*` (32×48) | `td_*` (48×48 UF terrain) |
| Tap indicator | `iso_dun_selectA.png` (diamond) | `td_selectA.png` (square) |
| Fallback item sprite | `iso_dun_selectA.png` | `td_selectA.png` |

### Tile assets available

**UF terrain (top-down):** 455 tiles at 48×48 in `~/development/oryx/oryx_ultimate_fantasy_1.2/uf_split/uf_terrain/`. Includes `floor_crusted_grey`, `floor_diagonal_*`, `wall_cave_*`, `wall_crypt_*`, `wall_dungeon_*`, `door_stone_*`. Named descriptively, top-down perspective, pairs naturally with UF entity sprites.

**16bf world (top-down):** 1784 tiles at 24×24 in `~/development/oryx/oryx_16-bit_fantasy_1.1/Sliced/world_24x24/`. Numbered `oryx_16bit_fantasy_world_NNN.png`. Requires a tile key mapping (same problem as 16bf creature keys). Deferred.

**Decision:** UF terrain tiles for 2D mode. Descriptively named, 48×48 (entity sprites fit 1:1), visually consistent with UF entity tileset.

## The core abstraction

```csharp
/// <summary>
/// Converts between grid coordinates and screen positions.
/// Two implementations: IsometricRenderer and TopDownRenderer.
/// Injected into all presentation-layer consumers.
/// </summary>
public interface IMapRenderer
{
    /// <summary>Screen position of tile top-left corner.</summary>
    Vector2 GridToScreen(int gridX, int gridY);

    /// <summary>Screen position of tile center (for entity/item placement).</summary>
    Vector2 GridToScreenCenter(int gridX, int gridY);

    /// <summary>Convert screen position to nearest grid coordinate.</summary>
    (int gridX, int gridY) ScreenToGrid(Vector2 screenPos);

    /// <summary>Z-index for floor/wall tiles at this position.</summary>
    int GetTileSortOrder(int gridX, int gridY);

    /// <summary>Z-index for entities at this position (always above tiles).</summary>
    int GetEntitySortOrder(int gridX, int gridY);

    /// <summary>Tile image width in pixels.</summary>
    int TileWidth { get; }

    /// <summary>Tile image height in pixels.</summary>
    int TileHeight { get; }

    /// <summary>Default camera zoom for this renderer mode.</summary>
    float DefaultZoom { get; }

    /// <summary>Minimum camera zoom for this renderer mode.</summary>
    float MinZoom { get; }

    /// <summary>Maximum camera zoom for this renderer mode.</summary>
    float MaxZoom { get; }
}
```

**Note on `EntityYOffset`:** This was considered for `IMapRenderer` but belongs in `EntitySpriteManager` instead. It is a sprite positioning concern, not a coordinate mapping concern. `EntitySpriteManager.CreateSprite()` already reads `SpriteMapping.SpriteSize` — it should read `_renderer.TileHeight` to compute offset rather than encoding it in the interface.

`IsometricRenderer` wraps the existing `IsometricMapper` math. `TopDownRenderer` uses simple grid multiplication.

## Config extension

`config/game_settings.yaml`:
```yaml
tileset: "ultimate_fantasy"
map_mode: "iso"          # "iso" or "topdown"
```

Options panel gets a second cycle button: "Map: Isometric" / "Map: Top-Down". Same boot-time-only pattern (restart to apply). `OptionsPanel.WriteSetting(string key, string value)` is generalized (replaces the tileset-specific write method) so both settings reuse the same write path.

**Note on runtime switching:** `IMapRenderer` is stateless (pure coordinate functions). Floor transitions already tear down and rebuild all presentation state via `SetupPresentation`. The architecture naturally supports per-floor switching — no structural changes needed. "Restart to apply" is a conservative UX choice for now, not an architectural constraint.

**Note on mobile persistence:** `game_settings.yaml` writes currently target `res://`, which is read-only in a shipped `.pck`. Both `tileset` and `map_mode` will silently fail to persist on mobile. Migration to `user://` (with `res://` fallback for development) is required before mobile release. This is a prerequisite for shipping, tracked separately.

---

## Tasks

### TASK-001: Extract IMapRenderer interface, make IsometricRenderer implement it
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: none
- Description: Create `src/Presentation/Map/IMapRenderer.cs` with the interface above. Create `src/Presentation/Map/IsometricRenderer.cs` implementing `IMapRenderer` by wrapping existing `IsometricMapper` math. Add zoom properties: `IsometricRenderer` returns `DefaultZoom=4.0f`, `MinZoom=1.5f`, `MaxZoom=6.0f` (current hardcoded values). Keep `IsometricMapper` as-is temporarily for backwards compatibility during migration — deleted in TASK-003.
- Acceptance criteria:
  - `IMapRenderer` interface exists with all members (GridToScreen, GridToScreenCenter, ScreenToGrid, GetTileSortOrder, GetEntitySortOrder, TileWidth, TileHeight, DefaultZoom, MinZoom, MaxZoom)
  - `IsometricRenderer` implements `IMapRenderer` and produces identical results to `IsometricMapper` for all coordinate methods
  - Zoom properties return current hardcoded values
  - `IsometricMapper` still compiles and works (not yet removed)
  - Tests pass

### TASK-002: Create TopDownRenderer implementing IMapRenderer
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-001
- Description: Create `src/Presentation/Map/TopDownRenderer.cs` implementing `IMapRenderer` with flat 2D grid math. Default tile size: 48×48 (UF terrain native). GridToScreen = `(x * TileWidth, y * TileHeight)`. ScreenToGrid = simple division + rounding. Z-order by row only. Zoom defaults: `DefaultZoom=2.5f`, `MinZoom=1.0f`, `MaxZoom=5.0f` (initial guess — calibrated in TASK-007). Tile size configurable via constructor for future flexibility.
- Acceptance criteria:
  - `TopDownRenderer` implements `IMapRenderer`
  - GridToScreen(0,0) = (0,0); GridToScreen(1,0) = (48,0); GridToScreen(0,1) = (0,48)
  - ScreenToGrid round-trips correctly: ScreenToGrid(GridToScreenCenter(x,y)) == (x,y) for all valid grid positions
  - Z-order increases with Y, entities sort above tiles at same Y
  - dotnet test passes

### TASK-003: Migrate all call sites from IsometricMapper to IMapRenderer injection
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-001
- Description: Replace all 21 `IsometricMapper.*` static calls with calls on an injected `IMapRenderer` instance. The renderer flows from `Main._Ready()` through constructors. Also: fix the `OnLongPress` coordinate bug (missing `_gameView.ToLocal()` call) and update camera zoom to read from `renderer.DefaultZoom/MinZoom/MaxZoom` instead of hardcoded constants.
- Files to modify:
  - `DungeonRenderer.cs` — `Render()` takes `IMapRenderer` parameter (6 call sites)
  - `EntitySpriteManager.cs` — constructor takes `IMapRenderer`; compute entity Y offset from renderer tile height rather than hardcoded 0.15f: `offset = _renderer.TileHeight * 0.15f * scale` for iso, `0` for top-down (check renderer type or use a helper)
  - `ItemSpriteManager.cs` — constructor takes `IMapRenderer` (2 call sites)
  - `TurnAnimator.cs` — constructor takes `IMapRenderer` directly (not via EntitySpriteManager)
  - `InputHandler.cs` — constructor or setter takes `IMapRenderer` (1 call site)
  - `GameController.cs` — receives `IMapRenderer`; fix `OnLongPress` to call `_gameView.ToLocal()` before passing coords to `ScreenToGrid` (same as HandleTap does)
  - `PlayerCamera.cs` — pass `IMapRenderer` as parameter to `Update`/`AnimateTo`; read zoom limits from renderer
  - `Main.cs` — creates renderer, passes to all consumers; `SpawnTapIndicator` tap indicator path extracted to a variable (resolved in TASK-006)
  - `FloorTransitionTests.cs` — use `new IsometricRenderer()` explicitly
- After all call sites migrated: delete `IsometricMapper.cs`. Compiler catches any missed references.
- Acceptance criteria:
  - Zero `IsometricMapper` references in production code
  - `IsometricMapper.cs` deleted
  - `OnLongPress` coordinate bug fixed (long-press on tile (3,5) resolves to (3,5))
  - Camera zoom reads from `renderer.DefaultZoom/MinZoom/MaxZoom`
  - Game boots and plays identically to before in iso mode
  - All existing tests pass

### TASK-004: Wire renderer selection into Main._Ready() via game_settings.yaml
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-003
- Description: Add `map_mode` field to `config/game_settings.yaml`. Add `ReadMapMode()` to `Main.cs` following the exact same pattern as `ReadTilesetId()` (CLI arg `--map-mode` first, then YAML, then default "iso"). Create the correct `IMapRenderer` instance and pass it through the presentation layer.
- Acceptance criteria:
  - Default (no config change): game boots in iso mode, identical to current
  - `map_mode: "topdown"` boots with `TopDownRenderer`
  - `--map-mode topdown` CLI arg overrides YAML
  - Invalid value falls back to iso with a log warning
  - Camera zoom uses renderer's defaults automatically

### TASK-005: Add map_mode selector to OptionsPanel
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-004
- Description: Add a second cycle button to `OptionsPanel.cs` for map mode. Generalize the YAML write logic from `WriteTilesetSetting()` into `WriteSetting(string key, string value)` — reused by both tileset and map mode buttons.
- Files to modify:
  - `src/Presentation/UI/OptionsPanel.cs`
- Acceptance criteria:
  - Options panel shows "Map: Isometric" / "Map: Top-Down" cycle button
  - `WriteSetting(key, value)` is the single YAML write path (no duplicate method)
  - Both settings (tileset + map mode) persist independently to `game_settings.yaml`
  - "Restart to apply" label shows when either setting differs from boot value
  - Both buttons work correctly together (all 4 combinations selectable)

### TASK-006: Top-down dungeon tile assets and DungeonRenderer adaptation
- Status: pending
- Layer: presentation
- Type: system
- Dependencies: TASK-003
- Description: Make DungeonRenderer, tap indicator, and item fallback work with both iso and top-down assets.

  **Sub-part 1 — Tile assets:** Copy and rename a subset of UF terrain tiles into `res://src/Presentation/assets/tiles/topdown/` using the `td_` prefix. Minimum required: 2 floor variants + 1 wall variant per theme (Grey, Crypt, Moss, Dirt) = ~12 tiles. Also create a `td_selectA.png` (square selection indicator) for the tap indicator and item fallback — copy from a suitable UF terrain tile or create a simple placeholder. Stair tiles: identify UF terrain stair equivalents and copy as `td_stairdown_grey.png` / `td_stairup_grey.png`. Bones overlay: disabled in top-down for phase 1 (no equivalent exists).

  **Sub-part 2 — DungeonRenderer adaptation:** Add a `string tileRoot` parameter to `DungeonRenderer.Render()` (or derive from renderer type). `PickFloorTile`/`PickWallTile` receive the prefix and prepend it. Stair constants (`StairDownTexture`, `StairUpTexture`) become non-constant, resolved per tileRoot. Bones variants: skip gracefully in top-down mode (check tileRoot, skip if "topdown").

  **Sub-part 3 — Renderer-varying asset paths in Main + ItemSpriteManager:** `Main.SpawnTapIndicator` resolves the selection indicator path from the renderer mode (iso: `iso_dun_selectA.png`, topdown: `td_selectA.png`). `ItemSpriteManager.FallbackTilePath` does the same — either receives the path via constructor or reads it from the renderer (add a `SelectionIndicatorPath` property to `IMapRenderer`, or pass as a string at construction).

- Acceptance criteria:
  - Top-down tile assets exist in `res://src/Presentation/assets/tiles/topdown/` (minimum 12 floor/wall tiles + stair tiles + selection square)
  - `DungeonRenderer` renders correctly in both modes without iso assets in top-down
  - Tap indicator shows a square in top-down mode, diamond in iso mode
  - Item fallback sprite is visually appropriate in both modes
  - Stair tiles render in top-down (or gracefully absent)
  - Bones disabled in top-down with no error

### TASK-007: Calibration — tile size, zoom, and sprite offsets in top-down mode
- Status: pending
- Layer: presentation
- Type: analysis/tuning
- Dependencies: TASK-002, TASK-006
- Description: Visual calibration pass. Boot in top-down mode and evaluate rendering across all 4 tileset×renderer combinations:
  - UF + iso (baseline, should be unchanged)
  - UF + topdown
  - 16bf + iso
  - 16bf + topdown

  Evaluate and tune:
  - **Tile size:** 48×48 UF terrain at native vs scaled. Does the viewport feel right?
  - **Entity sprite sizing:** UF entities (48px) on 48px tiles = 1:1 natural. 16bf entities (24px, 2× scaled by tileset system) = 48px effective — also 1:1. Should be fine; confirm visually.
  - **Entity Y offset:** In top-down mode `EntitySpriteManager` should use offset=0 (centered). Confirm no floating/clipping.
  - **Camera zoom:** `TopDownRenderer` initial guesses (Default=2.5, Min=1.0, Max=5.0) — adjust based on how much map is visible and whether it feels right on mobile.
  - **Attack bump distance:** `TurnAnimator` hardcodes 8px bump and (4,-2) miss shake — tuned for iso. Evaluate in top-down, adjust if needed.
  - **Touch targets:** Are 48px tiles large enough to tap reliably at the chosen zoom?

- Acceptance criteria:
  - Tile size chosen and documented
  - All 4 tileset×renderer combinations boot and render without errors
  - Zoom defaults feel right in top-down (more map visible than iso)
  - Entity sprites correctly sized on tiles in all 4 combinations
  - Attack/miss animations don't look broken in top-down
  - Touch target size acceptable on mobile

### TASK-008: Visual validation — confirm all combinations
- Status: pending
- Layer: presentation
- Type: analysis
- Dependencies: TASK-004, TASK-006, TASK-007
- Description: Final validation across all 4 tileset×renderer combinations. Confirm every major system works in both modes.
- Test matrix: UF+iso, UF+topdown, 16bf+iso, 16bf+topdown
- Per combination, verify:
  - Tile rendering: floors, walls, stairs, doors
  - Entity positioning: player and monsters centered on tiles
  - Item positioning: floor items centered on tiles
  - Tap-to-move: tap tile (3,5) → player moves to (3,5) (not off-by-one)
  - Long-press inspect: resolves correct tile
  - Click-to-move multi-step: correct pathfinding and movement
  - Auto-explore: works
  - Camera: follows player, zoom limits respected, minimap correct
  - Status tints: visible
  - TurnAnimator move animation: entity slides to correct screen position
  - Attack/miss animation: visually correct
  - Options panel: both selectors functional, all 4 combinations selectable
- Acceptance criteria:
  - All items confirmed working in all 4 combinations
  - Screenshots captured per combination
  - Any visual issues documented
  - No regression vs pre-plan iso baseline

---

## Risks and open questions

### `OnLongPress` coordinate bug (MEDIUM — existing bug, fix in TASK-003)
`GameController.OnLongPress` passes raw screen-space coordinates to `ScreenToGrid` without the `_gameView.ToLocal()` transform that `InputHandler.HandleTap` applies. Long-press currently resolves to the wrong tile in iso mode. TASK-003 fixes this as part of the migration.

### PlayerCamera.cs is a static class (MEDIUM)
Three `IsometricMapper` call sites. Plan: pass `IMapRenderer` as a parameter to each affected method. Zoom constants also move to the renderer interface. Three extra parameters is a small cost for clarity.

### TurnAnimator — inject IMapRenderer directly (LOW)
One call site. Inject `IMapRenderer` into `TurnAnimator`'s constructor directly. Do not route through `EntitySpriteManager` — unnecessary coupling.

### Zoom limits tuning (MEDIUM — resolved in TASK-007)
Current zoom constants are tuned for iso tile sizes. `TopDownRenderer` starts with guesses (Default=2.5, Min=1.0, Max=5.0). TASK-007 calibrates these visually. The `IMapRenderer` interface carries them so the camera reads the right values automatically per mode.

### Top-down tile asset curation (MEDIUM)
UF terrain tiles need manual selection and renaming (~12-20 tiles). Visual design task, not a code task. Budget time accordingly. The tile naming convention differs from iso tiles.

### `user://` settings migration (HIGH — mobile release blocker)
`game_settings.yaml` writes to `res://`, which is read-only in a shipped mobile `.pck`. Both `tileset` and `map_mode` silently fail to persist on mobile. Must migrate to `user://` (with `res://` fallback for dev) before any mobile release. Track separately — not in scope for this plan but must not be forgotten.

### 4 tileset×renderer combinations (MEDIUM)
Each combination has different sprite-to-tile size ratios. TASK-007 validates all 4. Anticipated: UF entities (48px) and 16bf entities (24px, 2× scaled = 48px effective) both fit 1:1 on 48px top-down tiles naturally. But must be confirmed visually.

### MiniMap is renderer-agnostic (NO RISK)
Verified: MiniMap draws from grid coordinates at 2px per tile. No `IsometricMapper` usage. No changes needed. Works identically in both modes.

### DungeonRenderer is static (LOW — future refactor)
Currently static with parameters. Can stay static for this plan (add `IMapRenderer` and tileRoot as params). Converting to an instance class is a future cleanup task.

### Runtime hot-swap is architecturally free (NOTE — not in scope)
`IMapRenderer` is stateless. Floor transitions already tear down and rebuild all presentation state. Runtime switching could be added with zero structural changes — just re-call `SetupPresentation` with a new renderer. Not building it now; calling it out so the conservative "restart to apply" choice is understood as intentional.

---

## Not in scope

- Runtime hot-swapping between modes (restart required)
- Hex grid or other render modes
- Logic layer changes of any kind
- Full terrain tileset switching system (TASK-006 creates a minimal top-down tile set; a full terrain config system is a separate plan)
- 16bf world tile mapping (1784 numbered tiles, need key doc)
- `user://` settings migration (mobile release prerequisite, tracked separately)
