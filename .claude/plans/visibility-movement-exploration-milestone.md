# Milestone: Visibility, Movement & Exploration

**Status:** PLANNING (Opus-reviewed)
**Created:** 2026-03-23
**Reviewed:** 2026-03-23 (Opus deep review — 3 critical, 6 significant, 6 minor issues resolved)
**Priority:** High — prerequisite for playable dungeon campaign

Three tightly coupled systems built in dependency order. Each phase is a prerequisite for the next.

---

## Context & Motivation

The dungeon generation milestone landed a fully working 40×40 procedural dungeon, but three UX problems make it unplayable:

1. **Camera** — `CenterView` scales the entire map to fit the viewport. At 40×40, tiles are ~12px — illegible. Need player-following camera with a fixed zoom.
2. **Fog of war** — Every tile is always visible. No discovery. No tension. Also prerequisite for auto-explore interrupts.
3. **Movement** — Tapping a distant tile moves one greedy step per tap. Multi-step pathfinding (A*) is needed for click-to-move and auto-explore.

Auto-explore is not optional here — it's the primary navigation mode for a mobile roguelike. The Python prototype went through significant pain to get it right. This plan is designed to port it correctly the first time.

---

## Architecture Decisions

### FOV in Logic layer
`FovComputer` is pure C# — no Godot. `GameMap` grows two arrays: `_visible[,]` (per-turn) and `_explored[,]` (permanent). The renderer reads these. FOV computed twice per turn: once after the player action (player may have moved), once after monster turns (monsters may have moved into/out of FOV).

### Shadowcasting algorithm
Standard 8-octant recursive shadowcasting. Proven, efficient, well-tested. Matches Python prototype's `FOV_RESTRICTIVE` behavior closely enough for cross-prototype seed comparison.

### Path queue in GameController (Presentation)
The multi-step path for click-to-move is UI state — it lives in `GameController`, not the Logic layer. The Logic layer gets one `MoveTo` per turn (same as today). `Pathfinder.AStar` is Logic layer (testable by harness). The queue management is Presentation.

### AutoExploreState component on player (Logic layer)
Auto-explore state lives in Logic so the harness bot can eventually use it. `AutoExploreSystem` is a static class (matches the stateless `TurnController` pattern). `GameController` drives it by calling `GetNextAction` and auto-submitting turns. **Harness bot integration with auto-explore is explicitly out of scope for this milestone.**

### Scenario harness compatibility — non-negotiable
- FOV in scenario mode: all tiles immediately visible (no fog). `GameStateFactory.FromScenario` calls `map.RevealAll()` after map creation. `IsDungeonMode` guard in `RecomputeFov()` skips recomputation for scenarios.
- `IsGameOver`, `AliveMonsters`, `PlayerWon` — unchanged.
- All existing harness tests must pass after every phase.

### `MoveToward` vs exact tile — accepted limitation
`TurnController.ResolvePlayerMove` calls `GameMap.MoveToward` (greedy single-step) even for `MoveTo(x,y)`. When the path step is an adjacent tile (which A* always produces), `MoveToward` gives the correct result in the common case. Edge case: if a blocking entity has moved into the next path step between path-compute and execution, `MoveToward` will try axis-aligned alternatives instead of stopping. The player may deviate slightly from the computed path. This is acceptable for this milestone. The stuck-detection in Phase 5 handles the worst cases. An exact `MoveExact` action is deferred.

---

## Phase 1: Camera System

**Goal:** Make 40×40 dungeon floors legible and playable.

### 1.1 PlayerCamera class
**File:** `src/Presentation/Map/PlayerCamera.cs`

```csharp
public static class PlayerCamera
{
    public const float DefaultZoom = 2.5f;  // Tweak during testing

    // Extract HUD margins to shared constants (also used by CenterView previously)
    public const float UiTopMargin = 130f;
    public const float UiBottomMargin = 210f;

    /// <summary>
    /// Position and scale GameView so the player is centered in the available
    /// viewport area (accounting for HUD margins).
    /// </summary>
    public static void Update(Node2D gameView, Entity player, float zoom = DefaultZoom)
    {
        var viewport = gameView.GetViewport().GetVisibleRect().Size;
        var playerScreen = IsometricMapper.GridToScreen(player.X, player.Y);

        float availableH = viewport.Y - UiTopMargin - UiBottomMargin;
        float centerY = UiTopMargin + availableH / 2f;

        gameView.Scale = new Vector2(zoom, zoom);
        gameView.Position = new Vector2(
            viewport.X / 2f - playerScreen.X * zoom,
            centerY - playerScreen.Y * zoom
        );
    }
}
```

### 1.2 Replace CenterView in Main.cs
- Remove the static `CenterView` method entirely.
- Replace the `CenterView` call in `SetupPresentation` with `PlayerCamera.Update(_gameView!, _state!.Player)`.
- Add `PlayerCamera.Update` call in `OnTurnCompleted` (after HUD refresh) so camera tracks the player after each move.
- `OnFloorTransitionRequested` → `SetupPresentation` → `PlayerCamera.Update` at end of setup — floor transitions covered automatically.

### Acceptance
- [ ] 40×40 floor renders at comfortable zoom
- [ ] Camera follows player after each move
- [ ] HUD margins are respected (player doesn't render behind HUD)

---

## Phase 2: Fog of War

**Goal:** Tile visibility and exploration tracking. Prerequisite for auto-explore interrupts and entity hiding.

### 2.1 GameMap visibility arrays
**File:** `src/Logic/ECS/GameMap.cs` (modify)

Add arrays and API:
```csharp
private readonly bool[,] _visible;    // Per-turn: cleared each FOV recompute
private readonly bool[,] _explored;   // Permanent: set when tile first becomes visible

public bool IsVisible(int x, int y) => InBounds(x, y) && _visible[x, y];
public bool IsExplored(int x, int y) => InBounds(x, y) && _explored[x, y];

public void SetVisible(int x, int y)
{
    if (!InBounds(x, y)) return;
    _visible[x, y] = true;
    _explored[x, y] = true;  // Seeing = explored, always
}

public void ClearAllVisible()
{
    Array.Clear(_visible, 0, _visible.Length);
}

/// <summary>
/// Mark all tiles as visible and explored. Used by scenarios — no fog of war.
/// Called by GameStateFactory.FromScenario after map creation.
/// NOT called from CreateArena (arena is generic; the policy "scenarios have no fog"
/// belongs in GameStateFactory, not in the map constructor).
/// </summary>
public void RevealAll()
{
    for (int x = 0; x < Width; x++)
        for (int y = 0; y < Height; y++)
        {
            _visible[x, y] = true;
            _explored[x, y] = true;
        }
}
```

Both `_visible` and `_explored` initialized to `false` in **all** constructors (default, `allWalls`, `CreateArena`). `RevealAll()` is called explicitly by `GameStateFactory.FromScenario` — not baked into map construction — because the "no fog in scenarios" policy lives at the factory level, not the map level.

### 2.2 FovComputer — recursive shadowcasting
**File:** `src/Logic/Map/FovComputer.cs` (new — placed in `Logic/Map/`, not `Logic/ECS/`)

```csharp
public static class FovComputer
{
    /// <summary>
    /// Compute FOV from (centerX, centerY) with given radius.
    /// Marks visible tiles on the map (and explored as a side effect).
    /// Uses 8-octant recursive shadowcasting (Björn Bergström's algorithm).
    /// </summary>
    public static void Compute(GameMap map, int centerX, int centerY, int radius = 8)
    {
        map.ClearAllVisible();
        map.SetVisible(centerX, centerY);  // Player's own tile always visible

        for (int octant = 0; octant < 8; octant++)
            CastLight(map, centerX, centerY, radius, 1, 1.0f, 0.0f, octant);
    }

    private static bool BlocksSight(GameMap map, int x, int y)
    {
        if (!map.InBounds(x, y)) return true;
        return map.GetTileKind(x, y) == TileKind.Wall;
        // Doors: transparent (see through open doors — revisit when door open/close added)
    }

    // Standard recursive shadowcasting: 8-octant decomposition, slope-based propagation.
    // Full implementation per Björn Bergström's published algorithm.
    private static void CastLight(GameMap map, int cx, int cy, int radius,
        int row, float startSlope, float endSlope, int octant) { ... }

    // Octant transform lookup table (8 rows, 4 cols: xx, xy, yx, yy)
    private static readonly int[,] _mult = { ... };
}
```

**Algorithm notes:**
- Wall tiles block sight; floor/corridor/stair/door are transparent
- `radius=8` default matches Python prototype's FOV radius
- Pure C#, no Godot, no external deps — fully testable
- Doors are currently transparent (see through them) — correct for the current game state since there's no open/close mechanic yet

### 2.3 FovComputer unit tests
**File:** `tests/Logic/FovComputerTests.cs` (new)

```
FovComputer_OpenRoom_AllTilesVisible
FovComputer_Wall_BlocksLos
FovComputer_CornerWall_CorrectShadow
FovComputer_Pillar_CastsShadowBehind
FovComputer_EdgeOfMap_NoCrash
FovComputer_Radius_LimitsVisibility
FovComputer_PlayerTile_AlwaysVisible
FovComputer_Corridor_VisibleAheadNotBehindWall
FovComputer_ExploredSetOnVisible_PermanentAfterClear
```

### 2.4 TurnController FOV integration
**File:** `src/Logic/Core/TurnController.cs` (modify)

```csharp
public static TurnResult ProcessTurn(GameState state, PlayerAction action)
{
    var events = new List<TurnEvent>();
    state.TurnCount++;

    ResolvePlayerAction(state, action, events);

    // FOV after player moves — player may have stepped to a new position
    state.RecomputeFov();

    bool descended = events.Any(e => e is DescendEvent);
    if (!descended && state.PlayerFighter.IsAlive)
    {
        ResolveMonsterTurns(state, events);

        // FOV after monster turns — monsters may have moved into/out of player's FOV.
        // Required for: click-to-move interrupt detection, entity visibility updates,
        // and auto-explore interrupt checks (which run at the start of the NEXT call to GetNextAction).
        state.RecomputeFov();
    }

    // ... rest unchanged
}
```

**File:** `src/Logic/Core/GameState.cs` (modify)

```csharp
public void RecomputeFov(int radius = 8)
{
    // Guard: scenarios have RevealAll() called at startup; don't clear that.
    if (!IsDungeonMode) return;
    FovComputer.Compute(Map, Player.X, Player.Y, radius);
}
```

Also call `RecomputeFov()` in `DungeonFloorBuilder.Build()` after player placement — starting area is visible immediately on floor load.

**File:** `src/Logic/Content/GameStateFactory.cs` (modify)

Add `map.RevealAll()` call in `FromScenario` after `GameMap.CreateArena(...)` returns — this is the canonical location of the "scenarios have no fog" policy.

```csharp
var map = GameMap.CreateArena(scenario.MapWidth, scenario.MapHeight);
map.RevealAll();  // Scenarios: all tiles visible from turn 0 (no fog of war)
```

### 2.5 DungeonRenderer FOV-aware rendering
**File:** `src/Presentation/Map/DungeonRenderer.cs` (modify)

Current `Render` is `static void`. It must now return a `TileLayer` so visibility can be updated per turn. `Main.cs` stores the `TileLayer` as a field.

**New API:**
```csharp
// Called once on floor load — creates all tile sprites and returns reference map
public static TileLayer Render(GameMap map, Node2D tileMapLayer)

// Called each turn — updates Modulate/Visible on existing sprites
public static void UpdateVisibility(TileLayer layer, GameMap map)
```

**`TileLayer` wrapper:**
```csharp
public sealed class TileLayer
{
    public Dictionary<(int X, int Y), Node2D> TileSprites { get; } = new();
}
```

**Color scheme:**
- `IsVisible(x,y)` → `Modulate = Colors.White` (full brightness)
- `IsExplored(x,y) && !IsVisible(x,y)` → `Modulate = new Color(0.4f, 0.4f, 0.5f)`, `Visible = true`
- `!IsExplored(x,y)` → `Visible = false`

**Main.cs changes:**
- Add `private TileLayer? _tileLayer;` field
- `SetupPresentation`: `_tileLayer = DungeonRenderer.Render(state.Map, tileMapLayer);`
- `OnTurnCompleted`: call `DungeonRenderer.UpdateVisibility(_tileLayer!, _state!.Map)` after HUD refresh

### 2.6 EntitySpriteManager FOV filtering
**File:** `src/Presentation/Entities/EntitySpriteManager.cs` (modify)

```csharp
public void UpdateVisibility(GameState state)
{
    foreach (var (entityId, sprite) in _sprites)
    {
        var entity = state.Monsters.FirstOrDefault(m => m.Id == entityId)
                     ?? (state.Player.Id == entityId ? state.Player : null);
        if (entity == null) { sprite.Visible = false; continue; }

        sprite.Visible = state.Map.IsVisible(entity.X, entity.Y);
    }
}
```

Called from `Main.OnTurnCompleted` after tile visibility update.

### Acceptance
- [ ] Unexplored tiles not rendered
- [ ] Explored tiles render at ~40% brightness
- [ ] Visible tiles render at full brightness
- [ ] Monsters outside FOV are hidden
- [ ] FOV updates after each player turn AND after monster turns
- [ ] Scenario harness tests pass (RevealAll in GameStateFactory.FromScenario)
- [ ] FovComputer unit tests all pass

---

## Phase 3: A* Pathfinding

**Goal:** Pure C# pathfinding primitives. No Godot dependencies. Testable by harness.

**File:** `src/Logic/Map/Pathfinder.cs` (new — in `Logic/Map/`, alongside `FovComputer`)

### 3.1 Entity blocking API in GameMap

Before `Pathfinder` can check entity blocking, `GameMap` needs a method that accepts exclusions. Add:

```csharp
/// <summary>
/// Check if a tile can be moved into.
/// excludeEntity: this entity doesn't count as a blocker (can't block itself).
/// ignoreDestination: if true, entity blocking at (x,y) is ignored — allows pathing TO an occupied tile.
/// </summary>
public bool CanMoveToWith(int x, int y, Entity? excludeEntity, bool ignoreDestination = false)
{
    if (!IsWalkable(x, y)) return false;
    return !_entities.Any(e =>
        e.X == x && e.Y == y
        && e.BlocksMovement
        && IsEntityAlive(e)
        && (excludeEntity == null || e.Id != excludeEntity.Id)
        && !ignoreDestination);
}
```

`Pathfinder` calls `CanMoveToWith(nx, ny, movingEntity, ignoreDestination: (nx == toX && ny == toY))` for each candidate tile.

### 3.2 Pathfinder.AStar

```csharp
public static class Pathfinder
{
    /// <summary>
    /// A* pathfinding on the logical grid.
    /// Returns path as (x,y) positions NOT including start, inclusive of goal.
    /// Returns null if no path exists.
    /// movingEntity excluded from blocking checks (can't block itself).
    /// Destination tile is pathable even if occupied.
    /// Diagonal moves blocked when either cardinal neighbor is a wall (no corner-cutting).
    /// </summary>
    public static List<(int X, int Y)>? AStar(
        GameMap map, int fromX, int fromY, int toX, int toY,
        Entity? movingEntity = null)
    {
        if (fromX == toX && fromY == toY) return new List<(int, int)>();
        // A* with octile distance heuristic h = max(|dx|,|dy|)*10 + min(|dx|,|dy|)*4
        // Open set: PriorityQueue<(x,y), int> (available in .NET 6+)
        // g costs: cardinal=10, diagonal=14
        // Returns reconstructed path via came_from dictionary
    }

    /// <summary>
    /// Dijkstra flood-fill from source. Returns int[,] distance array.
    /// int.MaxValue = unreachable. Used by AutoExploreSystem to find nearest unexplored tile.
    /// </summary>
    public static int[,] DijkstraMap(GameMap map, int fromX, int fromY)
    {
        // BFS flood-fill, 8-directional, walkable tiles only
        // Does NOT exclude entities — auto-explore targets tiles, not paths through entities
    }

    /// <summary>
    /// Find the reachable (x,y) with minimum DijkstraMap value where predicate holds.
    /// Returns null if none found.
    /// </summary>
    public static (int X, int Y)? NearestWhere(
        int[,] dijkstra, int width, int height, Func<int, int, bool> predicate)
    {
        // Linear scan: find min dijkstra[x,y] where predicate(x,y) && dijkstra[x,y] != int.MaxValue
    }
}
```

**Implementation notes:**
- Use `System.Collections.Generic.PriorityQueue<TElement, TPriority>` (.NET 6, available in .NET 8 project)
- Octile heuristic in scaled integers avoids floats: `h = max(dx,dy)*10 + min(dx,dy)*4`
- Diagonal: only allowed when BOTH adjacent cardinal tiles are walkable (prevents wall-corner shortcuts)
- `NearestWhere` takes explicit `width`/`height` to avoid coupling to `GameMap` — caller can pass `state.Map.Width`

### 3.3 Pathfinder unit tests
**File:** `tests/Logic/PathfinderTests.cs` (new)

```
AStar_DirectPath_ReturnsCorrectSteps
AStar_PathAroundWall_FindsDetour
AStar_BlockedDestination_ReturnsNull (all routes blocked)
AStar_SameTile_ReturnsEmptyList
AStar_DiagonalMovement_AllowedWhenNoCornerCut
AStar_DiagonalMovement_BlockedByCornerWall
AStar_EntityBlocking_ExcludesMovingEntity
AStar_Destination_PathableWhenOccupied
DijkstraMap_DistancesFromCenter_Correct
DijkstraMap_WallTile_ReturnsMaxValue
DijkstraMap_UnreachableIsland_ReturnsMaxValue
NearestWhere_FindsClosestMatchingTile
NearestWhere_NoMatch_ReturnsNull
```

### Acceptance
- [ ] All Pathfinder unit tests pass
- [ ] A* produces shortest paths on simple maps
- [ ] A* returns null for blocked destinations
- [ ] Diagonal moves never cut through wall corners
- [ ] Dijkstra distances correct on arena map

---

## Phase 4: Multi-Step Click-to-Move

**Goal:** Tapping a distant tile auto-walks the entire path, one step per turn.

### 4.1 Entity.GetOrAdd helper
**File:** `src/Logic/ECS/Entity.cs` (modify)

Add:
```csharp
/// <summary>
/// Returns existing component of type T, or creates and adds a new one.
/// </summary>
public T GetOrAdd<T>() where T : IComponent, new()
{
    var existing = Get<T>();
    if (existing != null) return existing;
    return Add(new T());
}
```

Required by `AutoExploreSystem.Activate`. Added in Phase 4 since it's a prerequisite for Phase 5. The pattern `state.Player.Get<T>() ?? state.Player.Add(new T())` is acceptable as an alternative if `Entity` is hard to modify, but `GetOrAdd<T>()` is cleaner and generalizable.

### 4.2 Path queue and visible-monster snapshot in GameController
**File:** `src/Presentation/GameController.cs` (modify)

```csharp
private Queue<(int X, int Y)>? _pendingPath;
private int _pathInterruptHp = -1;
private HashSet<int> _pathStartVisibleMonsterIds = new();  // Monster IDs visible when path started
```

### 4.3 OnActionChosen — path building
`InputHandler` is unchanged — it emits `PlayerAction.MoveTo(x, y)` for any walkable tile tap. `GameController.OnActionChosen` intercepts distant `MoveTo` and computes the A* path:

```csharp
private void OnActionChosen(PlayerAction action)
{
    if (_state == null || Phase != GamePhase.WaitingForInput) return;

    // Cancel auto-explore on any manual tap
    if (_autoExploreMode)
    {
        _autoExploreMode = false;
        var ae = _state.Player.Get<AutoExploreState>();
        if (ae != null) ae.IsActive = false;
    }

    if (action.Kind == PlayerAction.ActionKind.Move
        && action.TargetX.HasValue && action.TargetY.HasValue)
    {
        int tx = action.TargetX.Value, ty = action.TargetY.Value;
        int dist = _state.Player.ChebyshevDistanceTo(tx, ty);

        if (dist > 1)
        {
            var path = Pathfinder.AStar(_state.Map,
                _state.Player.X, _state.Player.Y, tx, ty, _state.Player);
            if (path == null || path.Count == 0) return;  // Unreachable — ignore tap

            _pendingPath = new Queue<(int, int)>(path);
            _pathInterruptHp = _state.PlayerFighter.CurrentHp;

            // Snapshot of monsters currently in FOV — only interrupt on NEW monsters
            _pathStartVisibleMonsterIds.Clear();
            foreach (var m in _state.AliveMonsters)
                if (_state.Map.IsVisible(m.X, m.Y))
                    _pathStartVisibleMonsterIds.Add(m.Id);

            action = PlayerAction.MoveTo(_pendingPath.Dequeue().X, _pendingPath.Dequeue().Y);
            // BUG NOTE: this dequeues twice; should be:
        }
        else
        {
            _pendingPath = null;
        }
    }
    else
    {
        _pendingPath = null;
    }

    ExecuteTurn(action);
}
```

**Corrected first-step dequeue:**
```csharp
var (nx, ny) = _pendingPath.Dequeue();
action = PlayerAction.MoveTo(nx, ny);
```

### 4.4 ExecuteTurn extraction
Extract the turn execution body into a helper so both `OnActionChosen` and auto-advance can use it:

```csharp
private void ExecuteTurn(PlayerAction action)
{
    Phase = GamePhase.Processing;
    _input.SetAcceptingInput(false);

    var result = TurnController.ProcessTurn(_state!, action);
    TurnCompleted?.Invoke(result);

    foreach (var evt in result.Events.OfType<DeathEvent>())
        _entitySprites?.RemoveEntity(evt.ActorId);

    _pendingDescend = result.Events.OfType<DescendEvent>().FirstOrDefault();

    if (result.GameOver)
    {
        Phase = GamePhase.GameOver;
        _animator?.PlayTurn(result);
    }
    else
    {
        Phase = GamePhase.Animating;
        _animator?.PlayTurn(result);
    }
}
```

### 4.5 OnAnimationComplete — path continuation

```csharp
private void OnAnimationComplete()
{
    if (_state == null) return;
    _entitySprites?.UpdatePositions(_state);

    if (Phase == GamePhase.GameOver) { GameEnded?.Invoke(_state.PlayerWon); return; }
    if (_pendingDescend != null)
    {
        var d = _pendingDescend; _pendingDescend = null;
        FloorTransitionRequested?.Invoke(d.NewDepth); return;
    }

    // Auto-explore takes priority over pending path
    if (_autoExploreMode) { AdvanceAutoExplore(); return; }

    // Continue queued click-to-move path
    if (_pendingPath != null && _pendingPath.Count > 0)
    {
        if (!CheckPathInterrupts())
        {
            var (nx, ny) = _pendingPath.Dequeue();
            ExecuteTurn(PlayerAction.MoveTo(nx, ny));
            return;
        }
        _pendingPath = null;
    }

    Phase = GamePhase.WaitingForInput;
    _input.SetAcceptingInput(true);
}
```

### 4.6 Interrupt check — correct snapshot logic

```csharp
private bool CheckPathInterrupts()
{
    if (_state == null) return true;

    // Damage taken since path started
    if (_state.PlayerFighter.CurrentHp < _pathInterruptHp) return true;

    // NEW monster now visible (not in the snapshot taken when path started)
    foreach (var m in _state.AliveMonsters)
        if (_state.Map.IsVisible(m.X, m.Y) && !_pathStartVisibleMonsterIds.Contains(m.Id))
            return true;

    return false;
}
```

The snapshot approach (`_pathStartVisibleMonsterIds`) means click-to-move continues even if a monster was already visible when the path started — only NEW monsters in FOV interrupt. This matches Python prototype behavior and makes click-to-move useful in rooms that already have visible monsters.

### Acceptance
- [ ] Tapping a distant walkable tile auto-walks the entire path
- [ ] One step animated per turn (no skipping)
- [ ] Stops when a NEW monster enters FOV (not for pre-existing visible monsters)
- [ ] Stops when player takes damage
- [ ] Adjacent tap moves one step (unchanged behavior)
- [ ] Tapping a monster still attacks it (unchanged behavior)
- [ ] Tapping while path is active cancels path and starts new one

---

## Phase 5: Auto-Explore

**Goal:** Full auto-explore with Dijkstra targeting, A* pathing, interrupt conditions.

### 5.1 AutoExploreState component
**File:** `src/Logic/ECS/AutoExploreState.cs` (new)

```csharp
public sealed class AutoExploreState : IComponent
{
    public bool IsActive { get; set; }
    public List<(int X, int Y)> CurrentPath { get; set; } = new();

    /// <summary>
    /// Tiles explored at activation time. Auto-explore prioritizes NEW tiles
    /// over backtracking through already-known areas. Two-pass strategy:
    /// pass 1 = tiles not in snapshot, pass 2 = any unexplored tile.
    /// This prevents auto-explore from immediately stopping for items/features
    /// discovered in rooms already visited before activation.
    /// </summary>
    public HashSet<(int X, int Y)> ExploredSnapshot { get; set; } = new();

    public HashSet<int> KnownMonsterIds { get; set; } = new();
    public HashSet<(int X, int Y)> KnownStairs { get; set; } = new();
    public int LastHp { get; set; }
    public string? StopReason { get; set; }
    public int StuckCounter { get; set; }
    public (int X, int Y)? LastExpectedPosition { get; set; }

    // Fixed-size circular buffer for oscillation detection (last 6 positions)
    private readonly (int X, int Y)[] _positionHistory = new (int, int)[6];
    private int _positionCount;

    public void RecordPosition(int x, int y)
    {
        if (_positionCount < 6)
            _positionHistory[_positionCount++] = (x, y);
        else
        {
            // Shift left, append
            Array.Copy(_positionHistory, 1, _positionHistory, 0, 5);
            _positionHistory[5] = (x, y);
        }
    }

    /// <summary>
    /// Detects A-B-A-B-A-B pattern (3 complete reversals) using last 6 positions.
    /// </summary>
    public bool IsOscillating()
    {
        if (_positionCount < 6) return false;
        return _positionHistory[0] == _positionHistory[2]
            && _positionHistory[2] == _positionHistory[4]
            && _positionHistory[1] == _positionHistory[3]
            && _positionHistory[3] == _positionHistory[5]
            && _positionHistory[0] != _positionHistory[1];
    }

    public void ResetPositionHistory()
    {
        _positionCount = 0;
    }
}
```

### 5.2 AutoExploreSystem
**File:** `src/Logic/Core/AutoExploreSystem.cs` (new)

```csharp
public static class AutoExploreSystem
{
    public static void Activate(GameState state)
    {
        var ae = state.Player.GetOrAdd<AutoExploreState>();
        ae.IsActive = true;
        ae.StopReason = null;
        ae.CurrentPath.Clear();
        ae.StuckCounter = 0;
        ae.LastExpectedPosition = null;
        ae.LastHp = state.PlayerFighter.CurrentHp;
        ae.ResetPositionHistory();

        // Snapshot explored tiles — prioritize NEW discoveries over already-known areas
        ae.ExploredSnapshot.Clear();
        for (int x = 0; x < state.Map.Width; x++)
            for (int y = 0; y < state.Map.Height; y++)
                if (state.Map.IsExplored(x, y))
                    ae.ExploredSnapshot.Add((x, y));

        // Snapshot monsters currently in FOV — don't interrupt for these
        ae.KnownMonsterIds.Clear();
        foreach (var m in state.AliveMonsters)
            if (state.Map.IsVisible(m.X, m.Y))
                ae.KnownMonsterIds.Add(m.Id);
    }

    public static PlayerAction? GetNextAction(GameState state)
    {
        var ae = state.Player.Get<AutoExploreState>();
        if (ae == null || !ae.IsActive) return null;

        var stopReason = CheckInterrupts(state, ae);
        if (stopReason != null) { Stop(ae, stopReason); return null; }

        if (ae.CurrentPath.Count == 0 && !FindAndSetPath(state, ae))
        {
            Stop(ae, "Exploration complete — no reachable unexplored tiles");
            return null;
        }

        ae.LastExpectedPosition = ae.CurrentPath[0];
        ae.CurrentPath.RemoveAt(0);
        return PlayerAction.MoveTo(ae.LastExpectedPosition.Value.X, ae.LastExpectedPosition.Value.Y);
    }

    private static string? CheckInterrupts(GameState state, AutoExploreState ae)
    {
        // 1. New monster in visible FOV (not in snapshot at activation)
        foreach (var m in state.AliveMonsters)
            if (state.Map.IsVisible(m.X, m.Y) && !ae.KnownMonsterIds.Contains(m.Id))
                return $"Monster spotted: {m.Name}";

        // 2. New stair visible and not already known to auto-explore
        if (state.StairDown != null
            && state.Map.IsVisible(state.StairDown.X, state.StairDown.Y)
            && !ae.KnownStairs.Contains((state.StairDown.X, state.StairDown.Y)))
            return "Stairs found";

        // 3. Damage taken since last check
        if (state.PlayerFighter.CurrentHp < ae.LastHp)
            return "Took damage";

        // 4. Stuck — didn't reach expected position
        if (ae.LastExpectedPosition.HasValue)
        {
            var (ex, ey) = ae.LastExpectedPosition.Value;
            if (state.Player.X != ex || state.Player.Y != ey)
            {
                ae.StuckCounter++;
                if (ae.StuckCounter >= 3) return "Movement blocked";
            }
            else ae.StuckCounter = 0;
        }

        // 5. Oscillation
        ae.RecordPosition(state.Player.X, state.Player.Y);
        if (ae.IsOscillating()) return "Movement oscillation detected";

        // Update tracking state for next call
        ae.LastHp = state.PlayerFighter.CurrentHp;
        if (state.StairDown != null && state.Map.IsExplored(state.StairDown.X, state.StairDown.Y))
            ae.KnownStairs.Add((state.StairDown.X, state.StairDown.Y));

        return null;
    }

    private static bool FindAndSetPath(GameState state, AutoExploreState ae)
    {
        var dijkstra = Pathfinder.DijkstraMap(state.Map, state.Player.X, state.Player.Y);

        // Pass 1: prioritize tiles NOT in the explored snapshot (new discoveries)
        var target = Pathfinder.NearestWhere(dijkstra, state.Map.Width, state.Map.Height,
            (x, y) => !state.Map.IsExplored(x, y) && !ae.ExploredSnapshot.Contains((x, y)));

        // Pass 2: fall back to any unexplored tile reachable on this floor
        // (allows finishing isolated pockets that were unreachable at activation time
        // but may have been opened up since, or simply completes the map)
        target ??= Pathfinder.NearestWhere(dijkstra, state.Map.Width, state.Map.Height,
            (x, y) => !state.Map.IsExplored(x, y));

        if (target == null) return false;

        var path = Pathfinder.AStar(state.Map,
            state.Player.X, state.Player.Y, target.Value.X, target.Value.Y, state.Player);
        if (path == null || path.Count == 0) return false;

        ae.CurrentPath.Clear();
        ae.CurrentPath.AddRange(path);
        return true;
    }

    private static void Stop(AutoExploreState ae, string reason)
    {
        ae.IsActive = false;
        ae.StopReason = reason;
        ae.CurrentPath.Clear();
    }
}
```

### 5.3 GameController auto-explore integration
**File:** `src/Presentation/GameController.cs` (modify)

```csharp
private bool _autoExploreMode;

public void StartAutoExplore()
{
    if (_state == null || Phase != GamePhase.WaitingForInput) return;
    _pendingPath = null;
    _autoExploreMode = true;
    AutoExploreSystem.Activate(_state);
    AdvanceAutoExplore();
}

private void AdvanceAutoExplore()
{
    if (!_autoExploreMode || _state == null) return;
    var action = AutoExploreSystem.GetNextAction(_state);
    if (action == null)
    {
        _autoExploreMode = false;
        Phase = GamePhase.WaitingForInput;
        _input.SetAcceptingInput(true);
        return;
    }
    ExecuteTurn(action);
}
```

### 5.4 HUD auto-explore button
**File:** `src/Presentation/UI/HUD.cs` (modify)

- Add "Explore" button
- `HUD` emits `event Action? ExploreRequested`
- `GameController.Initialize` subscribes: `_hud.ExploreRequested += StartAutoExplore`
- Button visually dims while `_autoExploreMode` is true
- `HUD.SetAutoExploreActive(bool)` method for the dim state

### 5.5 Auto-explore tests
**File:** `tests/Logic/AutoExploreTests.cs` (new)

Test harness note: auto-explore tests require `IsDungeonMode=true` and real FOV computation. Tests must call `state.RecomputeFov()` after placement.

```
AutoExplore_ActivatesAndWalksToUnexploredTile
AutoExplore_StopsOnNewMonsterInFov
AutoExplore_DoesNotStopForMonsterVisibleAtActivation
AutoExplore_StopsOnDamageTaken
AutoExplore_StopsWhenFullyExplored
AutoExplore_OscillationDetected_Stops
AutoExplore_StuckCounter_Stops
AutoExplore_KnownStairs_DoesNotStopRepeatedly
AutoExplore_ExploredSnapshot_PrioritizesNewAreas
AutoExplore_FindsPathAroundObstacle
AutoExplore_NoReachableTarget_Stops
AutoExplore_ReactsToFovAfterMonsterTurn (monster walks into FOV during monster turn)
```

### Acceptance
- [ ] HUD "Explore" button activates auto-explore; button dims
- [ ] Auto-explore walks to unexplored tiles systematically
- [ ] Stops when NEW monster enters FOV
- [ ] Does NOT stop for monsters already visible at activation
- [ ] Stops when player takes damage
- [ ] Stops when no reachable unexplored tiles remain
- [ ] Stops on oscillation / stuck
- [ ] Does NOT re-trigger on the same stair twice
- [ ] Tapping anything cancels auto-explore
- [ ] All unit tests pass
- [ ] All harness scenario tests pass

---

## Phase 6: Integration and Polish

### 6.1 OnTurnCompleted wiring in Main.cs
Add to `OnTurnCompleted`:
```csharp
private void OnTurnCompleted(TurnResult result)
{
    if (_state == null) return;
    // ... existing stats accumulation ...
    _hud?.Refresh();
    _combatLog?.RecordTurn(result, _state);
    DungeonRenderer.UpdateVisibility(_tileLayer!, _state.Map);   // NEW
    _entitySprites?.UpdateVisibility(_state);                     // NEW
    PlayerCamera.Update(_gameView!, _state.Player);               // NEW
}
```

### 6.2 Floor transition cleanup
`SetupPresentation` creates a fresh `GameMap` each floor — `_visible` and `_explored` start `false`. `DungeonFloorBuilder.Build` calls `RecomputeFov()` after player placement. Starting area is visible immediately. `_tileLayer` is reassigned by the new `Render` call.

### 6.3 Scenario harness regression
Run full scenario harness suite. Verify:
- All metrics unchanged (FOV doesn't affect combat math)
- `RevealAll()` in `GameStateFactory.FromScenario` works correctly
- No new test failures

---

## Key Files Reference

### New files
```
src/Presentation/Map/PlayerCamera.cs       — Player-following camera
src/Logic/Map/FovComputer.cs               — Recursive shadowcasting FOV
src/Logic/Map/Pathfinder.cs                — A* and Dijkstra
src/Logic/ECS/AutoExploreState.cs          — Auto-explore component
src/Logic/Core/AutoExploreSystem.cs        — Auto-explore state machine
tests/Logic/FovComputerTests.cs            — FOV correctness tests
tests/Logic/PathfinderTests.cs             — A* and Dijkstra tests
tests/Logic/AutoExploreTests.cs            — Auto-explore behavior tests
```

### Modified files
```
src/Logic/ECS/GameMap.cs                   — _visible, _explored arrays + visibility API + CanMoveToWith
src/Logic/ECS/Entity.cs                    — GetOrAdd<T>() helper
src/Logic/Core/GameState.cs                — RecomputeFov()
src/Logic/Core/TurnController.cs           — Two FOV recomputes per turn (after player, after monsters)
src/Logic/Core/DungeonFloorBuilder.cs      — Initial FOV compute on build
src/Logic/Content/GameStateFactory.cs      — RevealAll() after CreateArena (scenario fog policy)
src/Presentation/Map/DungeonRenderer.cs    — Return TileLayer; UpdateVisibility static method
src/Presentation/Entities/EntitySpriteManager.cs — UpdateVisibility(state)
src/Presentation/GameController.cs         — ExecuteTurn(); path queue; snapshot; auto-explore; HUD wiring
src/Presentation/UI/HUD.cs                 — Explore button + ExploreRequested event
src/Presentation/Main.cs                   — _tileLayer field; OnTurnCompleted wiring; camera
```

### New directory
```
src/Logic/Map/    — FovComputer.cs, Pathfinder.cs (pure algorithms, not ECS components)
```

---

## Sequencing and Dependencies

```
Phase 1 (Camera)        — no prerequisites, build first
Phase 2 (FOV)           — needs Phase 1 coordination on DungeonRenderer only; otherwise independent
Phase 3 (Pathfinding)   — no prerequisites (pure logic); can build in parallel with Phase 2
Phase 4 (Click-to-move) — needs Phase 3 (A*) + Phase 2 (FOV for interrupt checks)
Phase 5 (Auto-explore)  — needs Phase 2 (FOV interrupts) + Phase 3 (pathfinding) + Phase 4 (Entity.GetOrAdd)
Phase 6 (Integration)   — wires up all of the above
```

Phases 2 and 3 can be built in separate parallel sessions.

---

## Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| Shadowcasting edge cases (corners, pillars) | Medium | Explicit FovComputer unit tests with reference maps |
| A* diagonal corner-cutting | Medium | `CanMoveToWith` checks both cardinal neighbors for diagonal |
| FOV breaks harness scenario metrics | High | `RevealAll()` in `GameStateFactory.FromScenario`; `IsDungeonMode` guard in `RecomputeFov()` |
| Click-to-move interrupts too early | Low | Resolved: `_pathStartVisibleMonsterIds` snapshot in Phase 4 |
| Auto-explore oscillation in corridors | Medium | Oscillation detection ported exactly from Python prototype |
| `MoveToward` deviation from A* path | Low | Accepted limitation; stuck counter catches worst cases |
| Camera jitter on fast multi-step | Low | Snap camera (no lerp for now); smooth lerp deferred |

---

## Out of Scope (Deferred)

- Monster memory (remembering last-seen position of off-screen monsters)
- Auto-loot / auto-interact (auto-explore stops at items but doesn't pick them up)
- Persistent explored state across save/load (no save system yet)
- Harness bot using `AutoExploreSystem` (bot currently uses `BotBrain` direct targeting)
- `PlayerAction.MoveExact` — exact tile move that fails rather than greedy fallback

---

## Camera Mode Evaluation (Deferred — needs playtest to decide)

**Status:** Plan only. Build after click-to-move is in so camera behaviour can be evaluated with real multi-step movement.

The current camera (Phase 1) always keeps the player centred — "hard follow" mode. This works but makes the whole map jerk on every step. Three modes worth implementing and comparing side-by-side:

### Mode A — Hard Follow (current)
Player is always pixel-centred. Map moves every step.
- Implemented: `PlayerCamera.AnimateTo` with 0.12s tween.
- Downside: map motion on every move is distracting; player loses spatial context.

### Mode B — Deadzone / Edge-scroll (Python PoC approach)
Camera stays fixed until the player walks within N tiles of the viewport edge, then scrolls to re-centre. Player can see the full local area without the map moving.
- **Most roguelike-appropriate.** Player retains spatial orientation; map only moves when needed.
- Implementation: in `PlayerCamera`, compare player screen position to viewport bounds minus a deadzone margin (e.g. 20% of viewport). Only tween if player is outside the deadzone.
- Deadzone size is tunable — wider = less scrolling, narrower = closer to hard follow.

### Mode C — Manual Scroll + Follow
Player is loosely followed; user can also drag/pan the map manually. Tap-to-scroll releases follow lock; player move re-engages it.
- More complex, better for large maps. Overkill until map sizes grow.
- Defer until after Mode B is evaluated.

### Pinch-to-zoom
Separate from scroll mode. Pinch gesture changes `PlayerCamera.DefaultZoom` between min (~1.5×) and max (~4×). Store last zoom in a field on `Main` so it persists across floor transitions.
- Pair with whichever scroll mode is chosen.

### Implementation plan for Mode B (when ready)

Modify `PlayerCamera.AnimateTo` to accept a deadzone parameter:

```csharp
public static void AnimateTo(Node2D gameView, Entity player, Node animRoot,
    float duration = 0.12f, float zoom = DefaultZoom, float deadzoneRatio = 0.25f)
{
    var viewport = gameView.GetViewport().GetVisibleRect().Size;
    var playerScreen = IsometricMapper.GridToScreen(player.X, player.Y);

    // Where would the player appear on screen given current gameView transform?
    var playerOnScreen = gameView.ToGlobal(playerScreen * zoom) - gameView.GlobalPosition + gameView.Position;
    // Actually: player screen pos = gameView.Position + playerScreen * zoom
    var currentPlayerOnScreen = gameView.Position + playerScreen * zoom;

    float deadzoneX = viewport.X * deadzoneRatio;
    float deadzoneY = (viewport.Y - UiTopMargin - UiBottomMargin) * deadzoneRatio;
    float minX = deadzoneX, maxX = viewport.X - deadzoneX;
    float minY = UiTopMargin + deadzoneY, maxY = viewport.Y - UiBottomMargin - deadzoneY;

    bool needsScroll = currentPlayerOnScreen.X < minX || currentPlayerOnScreen.X > maxX
                    || currentPlayerOnScreen.Y < minY || currentPlayerOnScreen.Y > maxY;

    if (!needsScroll) return;  // Player still inside deadzone — no camera movement

    // Re-centre player
    float availableH = viewport.Y - UiTopMargin - UiBottomMargin;
    float centerY = UiTopMargin + availableH / 2f;
    var targetPos = new Vector2(
        viewport.X / 2f - playerScreen.X * zoom,
        centerY - playerScreen.Y * zoom
    );

    gameView.Scale = new Vector2(zoom, zoom);
    var tween = animRoot.CreateTween();
    tween.TweenProperty(gameView, "position", targetPos, duration)
         .SetEase(Tween.EaseType.Out).SetTrans(Tween.TransitionType.Quad);
}
```

Add a `CameraMode` enum to `PlayerCamera` (`HardFollow`, `Deadzone`) and a static field `ActiveMode` so the mode can be switched at runtime for testing without recompiling. A debug UI toggle or a config constant is sufficient for the evaluation phase.
