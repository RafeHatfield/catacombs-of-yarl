# Plan: Configurable Map Renderer (Isometric / Top-Down 2D)

**Status:** Phase 1 complete (TASK-001 through TASK-004)

## What this plan does

Extracts the hardcoded `IsometricMapper` static class into an `IMapRenderer` interface with two implementations: `IsometricRenderer` (current behavior, fully wired) and `TopDownRenderer` (working math stub, no tile assets yet). All presentation-layer consumers receive the renderer via injection. The mode is config-driven via `game_settings.yaml` from day one.

**Entirely presentation-layer work.** Logic layer: zero changes.

**Current intent:** Continue building and playing in iso. Top-down is a future option, not a current deliverable. The goal here is a clean seam — the abstraction exists, swapping in top-down later requires only tile assets and calibration.

## Why this matters

The logic layer is already completely grid-based and renderer-agnostic. Locking the presentation layer to `IsometricMapper` static calls makes a future mode switch unnecessarily invasive. The tileset switching system proved the config-injection-at-boot pattern — this applies the same approach to coordinate mapping.

## Phase 1 (this plan) vs Phase 2 (future)

**Phase 1 — Build the seam:**
- `IMapRenderer` interface + `IsometricRenderer` (complete)
- `TopDownRenderer` (working coordinate math, no tile assets)
- All 21 call sites migrated, `IsometricMapper.cs` deleted
- `game_settings.yaml` drives mode selection

**Phase 2 — Ship top-down (future plan):**
- Top-down tile assets (`td_*` prefix, UF terrain)
- `DungeonRenderer` and tap indicator asset switching
- OptionsPanel UI for player mode selection
- Visual calibration across all 4 tileset×renderer combinations
- `user://` settings persistence for mobile

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
- Status: complete
- Files changed: `src/Presentation/Map/IMapRenderer.cs` (created), `src/Presentation/Map/IsometricRenderer.cs` (created)
- Notes: Math is a direct port of IsometricMapper. HalfTileHeight = TileHeight/4 = 12 preserved exactly. Zoom constants (4.0/1.5/6.0) match previous PlayerCamera hardcodes.

### TASK-002: Create TopDownRenderer stub implementing IMapRenderer
- Status: complete
- Files changed: `src/Presentation/Map/TopDownRenderer.cs` (created)
- Notes: ScreenToGrid round-trips correctly through GridToScreenCenter for all grid positions. No tile assets wired. Boot in top-down will fail at DungeonRenderer (expected, Phase 2).

### TASK-003: Migrate all call sites from IsometricMapper to IMapRenderer injection
- Status: complete
- Files changed: `DungeonRenderer.cs`, `EntitySpriteManager.cs`, `ItemSpriteManager.cs`, `TurnAnimator.cs`, `InputHandler.cs`, `GameController.cs`, `PlayerCamera.cs`, `Main.cs`, `FloorTransitionTests.cs`, `TweenCompletionTests.cs`; `IsometricMapper.cs` deleted
- Notes:
  - EntitySpriteManager gained a two-arg test constructor `(Node2D, IMapRenderer)` with nullable SpriteMapping to allow the existing integration tests to compile without a real SpriteMapping.
  - PlayerCamera.Update/AnimateTo take optional `IMapRenderer?` parameter — defaults to `new IsometricRenderer()` when null (safe for any remaining call sites).
  - OnLongPress bug fixed: `_gameView.ToLocal(screenPos)` applied before `_renderer.ScreenToGrid`, matching the transform that Main._UnhandledInput always applied for HandleTap.
  - `_gameView` is now passed into `GameController.Initialize()` via optional parameter.
  - 734 tests pass, identical to pre-migration baseline.

### TASK-004: Wire renderer selection into Main._Ready() via game_settings.yaml
- Status: complete
- Layer: presentation
- Type: system
- Dependencies: TASK-001
- Description: Replace all 21 `IsometricMapper.*` static calls with calls on an injected `IMapRenderer` instance. The renderer flows from `Main._Ready()` through constructors. Also: fix the `OnLongPress` coordinate bug (missing `_gameView.ToLocal()` call) and update camera zoom to read from `renderer.DefaultZoom/MinZoom/MaxZoom` instead of hardcoded constants.
- Files to modify:
  - `DungeonRenderer.cs` — `Render()` takes `IMapRenderer` parameter (6 call sites)
  - `EntitySpriteManager.cs` — constructor takes `IMapRenderer` (4 call sites). **Do NOT change the Y offset formula in Phase 1** — leave `SpriteMapping.GetEntityYOffset` math exactly as-is; offset calibration for top-down is Phase 2 TASK-007.
  - `ItemSpriteManager.cs` — constructor takes `IMapRenderer` (2 call sites)
  - `TurnAnimator.cs` — constructor takes `IMapRenderer` directly (not via EntitySpriteManager)
  - `InputHandler.cs` — constructor or setter takes `IMapRenderer` (1 call site)
  - `GameController.cs` — receives `IMapRenderer`; fix `OnLongPress` bug: `GameController.Initialize()` must also receive the `_gameView` Node2D reference so `OnLongPress` can call `_gameView.ToLocal(screenPos)` before passing to `ScreenToGrid` (same transform that `HandleTap` already applies via `Main._UnhandledInput`)
  - `PlayerCamera.cs` — pass `IMapRenderer` as parameter to `Update`/`AnimateTo`; read zoom limits from renderer
  - `Main.cs` — creates renderer, passes to all consumers; migrate `ZoomMin`/`ZoomMax` constants and the `_currentZoom` initializer and `BuildZoomPanel()` lambda captures to read from `renderer.MinZoom/MaxZoom/DefaultZoom`; `SpawnTapIndicator` tap indicator path extracted to a variable (resolved in TASK-006)
  - `FloorTransitionTests.cs` — use `new IsometricRenderer()` explicitly
  - `tests/Integration/TweenCompletionTests.cs` — update 3 `EntitySpriteManager` constructor call sites to pass `new IsometricRenderer()`
- After all call sites migrated: delete `IsometricMapper.cs`. Compiler catches any missed references.
- Acceptance criteria:
  - Zero `IsometricMapper` references in production code
  - `IsometricMapper.cs` deleted
  - `OnLongPress` coordinate bug fixed (long-press on tile (3,5) resolves to (3,5)); `_gameView` plumbed into `GameController.Initialize()`
  - Camera zoom reads from `renderer.DefaultZoom/MinZoom/MaxZoom` (including `BuildZoomPanel` lambdas)
  - Entity Y offset math unchanged — no visual difference from pre-plan
  - Game boots and plays identically to before in iso mode
  - All existing tests pass

### TASK-004: Wire renderer selection into Main._Ready() via game_settings.yaml
- Status: complete
- Files changed: `config/game_settings.yaml` (map_mode field added), `Main.cs` (ReadMapMode(), CreateRenderer() methods added)
- Notes: Follows exact same pattern as ReadTilesetId(). CLI --map-mode arg checked first, then YAML, then default "iso". "topdown" falls back to iso with GD.PrintErr (no tile assets). Camera zoom reads from renderer.DefaultZoom/MinZoom/MaxZoom automatically via _currentZoom initialised in _Ready.
- Layer: presentation
- Type: system
- Dependencies: TASK-003
- Description: Add `map_mode` field to `config/game_settings.yaml`. Add `ReadMapMode()` to `Main.cs` following the exact same pattern as `ReadTilesetId()` (CLI arg `--map-mode` first, then YAML, then default "iso"). Create the correct `IMapRenderer` instance and pass it through the presentation layer. Unknown or "topdown" values fall back to iso with a log warning (since top-down tile assets don't exist yet).
- Acceptance criteria:
  - Default (no config change): game boots in iso mode, identical to current
  - `map_mode: "iso"` explicit boots correctly
  - `--map-mode iso` CLI arg works
  - Invalid value falls back to iso with `GD.PrintErr` warning
  - Camera zoom reads from `renderer.DefaultZoom/MinZoom/MaxZoom` automatically
  - All tests pass, game plays identically to pre-plan

### TASK-005 (Phase 2): Add map_mode selector to OptionsPanel
- Status: deferred — Phase 2 (requires top-down tile assets first)

### TASK-006 (Phase 2): Top-down dungeon tile assets and DungeonRenderer adaptation
- Status: deferred — Phase 2 (wire top-down tile paths, copy UF terrain tiles, adapt DungeonRenderer)

### TASK-007 (Phase 2): Calibration — tile size, zoom, sprite offsets in top-down mode
- Status: deferred — Phase 2

### TASK-008 (Phase 2): Visual validation across all 4 tileset×renderer combinations
- Status: deferred — Phase 2

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
