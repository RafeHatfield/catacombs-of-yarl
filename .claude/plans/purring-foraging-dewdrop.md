# Presentation Layer Milestone

## Context

Logic layer is complete: ECS, combat, balance harness, 165 tests, 6/6 tuned scenarios. Zero presentation code exists. The turn loop lives inside `ScenarioHarness.RunOnce()` — a monolithic method that creates the arena, spawns entities, loops turns, and records metrics. The Presentation layer needs a clean API to drive turns one at a time, receiving structured results it can animate.

This plan extracts that API (Phase 1), then builds the Godot iso presentation on top (Phases 2-5).

### Art Direction: Oryx Design Lab (decided 2026-03-22)
- **Isometric from day one.** No top-down phase — go straight to iso since that's the vision.
- **Two Oryx products:**
  - **Iso Dungeon** (32x48 tiles) — floors, walls, doors, stairs, decorations at `~/development/oryx/oryx_iso_dungeon/sliced/`
  - **Ultimate Fantasy 1.2** (48x48 characters, 4 animation frames) at `~/development/oryx/oryx_ultimate_fantasy_1.2/uf_split/uf_heroes/`
- **Full Oryx library purchased** and available at `~/development/oryx/` — pull additional assets as needed.
- **Size mismatch (32x48 tiles vs 48x48 characters):** Use native sizes. Characters overflow tile bounds — standard for iso games. The tile is the ground footprint; characters rise above it. See `/tmp/oryx_comparison/` for visual comparisons.
- **Sprite mapping:** knight=player, goblin=orc_grunt, goblin_warrior=orc_brute, zombie_a=zombie. No orc sprites in Oryx — goblins stand in for orcs.
- **Assets copied into project** for Godot import pipeline. Source stays as master archive.

---

## Phase 1: Logic Layer Refactoring (Pure C#, no Godot)

### Goal
Extract `TurnController` from `ScenarioHarness` so both the harness and the UI share a single turn-processing engine.

### New Files

**`src/Logic/Core/PlayerAction.cs`** — What the player (or UI) submits
```csharp
public sealed class PlayerAction
{
    public enum ActionKind { Wait, Attack, Move, UseItem }
    public ActionKind Kind { get; }
    public Entity? Target { get; }       // Attack target or move-toward entity
    public int? TargetX { get; }         // For tap-to-move (UI)
    public int? TargetY { get; }
    public Entity? Item { get; }         // Specific item (UI), null = auto-find (bot)

    // Static factories: Wait, Attack(target), MoveTo(x,y), MoveToward(entity), UseItem(item?)
}
```

**`src/Logic/Core/TurnEvent.cs`** — Discrete things that happened, in order
```
TurnEvent (abstract, has ActorId)
├── AttackEvent  — TargetId, Hit, Damage, IsCritical, IsFumble, TargetKilled, IsBonusAttack
├── MoveEvent    — FromX/Y, ToX/Y
├── HealEvent    — AmountHealed, ItemId, ItemName
├── WaitEvent    — (empty)
└── DeathEvent   — KillerId
```
Events use entity IDs (not references) — safe to serialize and hold.

**`src/Logic/Core/TurnResult.cs`** — Container for one turn
```csharp
public sealed class TurnResult
{
    public int TurnNumber { get; init; }
    public List<TurnEvent> Events { get; init; }
    public bool GameOver { get; init; }
    public bool PlayerDied { get; init; }
    public bool AllMonstersDefeated { get; init; }
}
```

**`src/Logic/Core/GameState.cs`** — Mutable game state
```csharp
public sealed class GameState
{
    public Entity Player { get; }
    public List<Entity> Monsters { get; }
    public GameMap Map { get; }
    public SeededRandom Rng { get; }
    public int TurnCount { get; set; }
    public int TurnLimit { get; set; }
    // Computed: PlayerFighter, PlayerInventory, IsGameOver, PlayerWon, AliveMonsters
}
```

**`src/Logic/Core/GameStateFactory.cs`** — Creates GameState from ScenarioDefinition
- Extracts `CreatePlayer` and monster-spawning from `ScenarioHarness`
- Single source of truth for entity setup (harness and UI both use this)

**`src/Logic/Core/TurnController.cs`** — The heart of the extraction
```csharp
public static class TurnController
{
    public static TurnResult ProcessTurn(GameState state, PlayerAction action)
    // 1. Increment turn, resolve player action, resolve all monster turns
    // 2. Emit TurnEvents into list for each discrete thing
    // 3. Return TurnResult with events + game-over flags
}
```

Private methods mirror current harness logic exactly:
- `ResolvePlayerAction` — switches on ActionKind
- `ResolvePlayerAttack` — CombatResolver + bonus attack recursion → AttackEvent(s) + DeathEvent
- `ResolveMonsterTurns` — iterate alive monsters, attack if adjacent else move
- `ResolveMonsterAttack` — same pattern as player
- `TryHeal` — find potion, apply, emit HealEvent

**Critical:** RNG call order must match current `ScenarioHarness.RunOnce()` exactly. Same seed → same calls → same results.

### Modified Files

**`src/Logic/Balance/ScenarioHarness.cs`** — Refactor `RunOnce` to:
1. Use `GameStateFactory.FromScenario()` to create state
2. Loop: `BotBrain.Decide() → ToPlayerAction() → TurnController.ProcessTurn()`
3. Collect metrics from TurnResult events via `RunMetrics.RecordTurn()`
4. Remove `CreatePlayer`, `ResolvePlayerAttack`, `ResolveMonsterAttack`, `TryHeal` (moved to TurnController/GameStateFactory)

**`src/Logic/Balance/BotBrain.cs`** — Add `ToPlayerAction(BotAction, Entity player)` bridge
- Keep `BotAction` as-is (internal bot decision type)
- Bridge maps: AttackTarget→Attack, HealSelf→UseItem(null), MoveToward→MoveToward, DoNothing→Wait
- UseItem(null) tells TurnController to auto-find first healing potion (same as current TryHeal)

**`src/Logic/Balance/RunMetrics.cs`** — Add `RecordTurn(TurnResult, int playerId)` method
- Walks event list, increments counters (PlayerAttacks, PlayerHits, etc.)
- Metrics derived from events, not tracked during resolution

### Test Files

**`tests/Core/TurnControllerTests.cs`** — New test suite:
- Attack kills monster → AttackEvent + DeathEvent, state updated
- Attack miss → AttackEvent with Hit=false
- Bonus attack chain → multiple AttackEvents with IsBonusAttack
- Heal consumes potion → HealEvent, inventory reduced
- Move updates position → MoveEvent with correct from/to
- Monsters act after player → monster events follow player events
- Game over on player death / all monsters dead
- **Deterministic regression:** same seed → identical events

**`tests/Core/GameStateFactoryTests.cs`** — Player/monster creation from scenarios

**Regression gate:** Run all 6 tuned scenarios at seed 1337 before and after refactoring. AggregatedMetrics must be identical. If they differ, the RNG call order changed — find and fix.

### Task Order
```
1.1 PlayerAction           — no deps
1.2 TurnEvent + TurnResult — no deps
1.3 GameState              — no deps
1.4 GameStateFactory       — depends on 1.3 (extracts from ScenarioHarness)
1.5 TurnController         — depends on 1.1-1.3
1.6 BotBrain bridge        — depends on 1.1
1.7 RunMetrics.RecordTurn  — depends on 1.2
1.8 ScenarioHarness refactor — depends on 1.4-1.7
1.9 Tests                  — depends on 1.5-1.8
1.10 Regression check      — final gate (all 165 tests + harness metrics match)
```

### Risk: GameMap.MoveToward doesn't report old position
`MoveToward` returns `bool` but mutates entity position directly. TurnController needs before/after for MoveEvent. Fix: capture `(entity.X, entity.Y)` before calling `MoveToward`, then read new position after.

---

## Phase 2: Godot Project Setup & Asset Import

### Oryx Assets to Copy

**Tiles** → `src/Presentation/assets/tiles/iso/`
Source: `~/development/oryx/oryx_iso_dungeon/sliced/`
- Floors: `iso_dun_floor_tileA.png` through `_tileG.png` (7 variants for visual variety)
- Walls: `iso_dun_wall_greyA.png` through `_greyG.png` + `_cracked` variants
- Doors: `iso_dun_door_ironA.png` through `_ironD.png`, `_woodA` through `_woodD`
- Stairs: `iso_dun_stairup_grey.png`, `iso_dun_stairdown_grey.png`
- Decorative: torches, bones, blood (as needed)

**Characters** → `src/Presentation/assets/sprites/heroes/`
Source: `~/development/oryx/oryx_ultimate_fantasy_1.2/uf_split/uf_heroes/`
- `knight_{1-4}.png` (player)
- `goblin_{1-4}.png` (orc_grunt)
- `goblin_warrior_{1-4}.png` (orc_brute)
- `zombie_a_{1-4}.png` (zombie)

**Items** (future) → `src/Presentation/assets/sprites/items/`
Source: `~/development/oryx/oryx_ultimate_fantasy_1.2/uf_split/uf_items/`

### Tasks
- **2.1** Copy asset subsets into project directories (above)
- **2.2** Configure Godot import: nearest-neighbor filter, no mipmaps, pixel-perfect rendering
- **2.3** Sprite mapping (C# dictionary in Presentation layer):
  ```
  monster_id → sprite_base: orc_grunt→goblin, orc_brute→goblin_warrior, zombie→zombie_a
  player → knight
  ```
  Append `_{1-4}.png` for animation frames.
- **2.4** Scene tree skeleton:
  ```
  Main → GameView (Node2D) → TileMapLayer + EntityLayer
       → UILayer (CanvasLayer) → HUD + CombatLog
       → InputHandler
  ```

---

## Phase 3: Isometric Tilemap & Dungeon Rendering

- **3.1** `IsometricMapper.cs` — grid↔screen coordinate conversion
  - Tile step: half_w=16, half_h=12 (for 32x48 Oryx iso tiles)
  - `GridToScreen(gx, gy)` → `screenX = (gx-gy)*16, screenY = (gx+gy)*12`
  - `ScreenToGrid(screenPos)` → inverse transform for touch input
- **3.2** `DungeonRenderer.cs` — populate TileMapLayer from GameMap (walls/floors)
  - Walls on border cells, floor inside; random floor variant per tile (seeded by position)
- **3.3** `EntitySpriteManager.cs` — create/position/remove Sprite2D nodes per entity
  - Characters at native 48x48, bottom-center aligned to tile position
  - Foot offset tunable per sprite type (dial in during iteration)
  - 4-frame idle animation from Oryx frames
- **3.4** Camera — portrait mode (720x1280), centered on player
  - 12x12 arena at iso scale ≈ 480x288 in screen space — fits with room for UI

---

## Phase 4: Turn-Based Input & Game Loop

- **4.1** `InputHandler.cs` — tap → ScreenToGrid → identify target → PlayerAction
- **4.2** `GameController.cs` — state machine: WaitingForInput → ProcessTurn → Animating → repeat
- **4.3** `TurnAnimator.cs` — sequential event animation (move tweens, attack bumps, damage numbers)
- **4.4** Tap targeting highlights (red=attack, blue=move)

---

## Phase 5: UI Layer

- **5.1** HUD — HP bars, turn counter, depth
- **5.2** Combat log — TurnEvents → readable text
- **5.3** Potion button — tap to UseItem
- **5.4** Game over overlay — win/loss, stats, replay

---

## Verification

### Phase 1
```bash
dotnet test --filter "Category!=Slow"   # All 165+ tests pass
dotnet test                              # Full suite including slow
# Compare AggregatedMetrics for 6 tuned scenarios at seed 1337 — must be identical
```

### Phase 2+
- Godot editor loads project without errors
- Arena renders with floor/wall tiles
- Entity sprites appear at correct positions
- Tap input produces correct PlayerActions
- Full turn loop plays through a scenario visually
