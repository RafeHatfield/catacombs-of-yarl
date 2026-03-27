# Dungeon Generation Milestone Plan (v3 — Opus Review)

## What the Python Prototype Actually Does

Three distinct YAML types drive the entire system:

1. **Scenario files** (`config/levels/scenario_*.yaml`) — controlled test encounters, exact entity placement, used by the harness. ~89 exist. Already partially ported.
2. **Level template file** (`config/level_templates.yaml`) — per-floor procedural overrides: generation parameters, guaranteed spawns, special rooms, door/trap/stair rules, ETP budgets. Missing entirely from C# so far.
3. **Loot policy** (`config/loot_policy.yaml`) — item quality/quantity rules by depth band. Separate milestone.

The prototype is a **hybrid system**: scenarios are fully handcrafted (exact positions), normal campaign floors are procedurally generated but YAML-controlled at the floor level via `level_templates.yaml`.

---

## Architecture

```
level_templates.yaml          scenario_*.yaml
        │                            │
        ▼                            ▼
LevelTemplateRegistry     ScenarioDefinition (existing)
        │                            │
        ▼                            ▼
DungeonFloorBuilder       GameStateFactory (existing, NEVER TOUCHED)
        │
        ├── MapGenerator (random placement + L-corridors, matching Python)
        ├── EntityPlacer (guaranteed spawns + procedural fill + ETP)
        └── PlayerCarryForward (stat persistence across floors)
```

---

## Phase 1: TileKind + GameMap Extension

**What:** `GameMap` gets tile type awareness. Additive — all existing APIs unchanged.

**Files to create:**
- `src/Logic/ECS/TileKind.cs` — enum: `Wall`, `Floor`, `Corridor`, `StairDown`, `StairUp`, `Door`, `Trap`

**Files to modify:**
- `src/Logic/ECS/GameMap.cs`:
  - Add `TileKind[,] _tiles` alongside `_walkable`
  - Add `GetTileKind(x,y)` / `SetTile(x,y,TileKind)` — `SetTile` keeps `_walkable` in sync (Floor/Corridor/StairDown/StairUp = walkable, Wall = not)
  - Add constructor overload `GameMap(int width, int height, bool allWalls)` — initializes all tiles to `Wall` / non-walkable. Used by dungeon generation.
  - `CreateArena` stays unchanged — continues to use `_walkable` directly

**Tests:**
- SetTile(Floor) makes tile walkable
- SetTile(Wall) makes tile non-walkable
- SetTile(Corridor) makes tile walkable
- GetTileKind returns what was set
- Existing default constructor + CreateArena behavior unchanged

---

## Phase 2: Level Template Registry

**What:** C# equivalent of `level_template_registry.py`. Loads `level_templates.yaml`, exposes `GetLevelOverride(int depth)`.

**Files to create:**
- `src/Logic/Balance/LevelOverride.cs` — full schema with active types + deferred stubs:

```csharp
public sealed class LevelOverride
{
    [YamlMember(Alias = "parameters")]
    public GenerationParameters? Parameters { get; set; }

    [YamlMember(Alias = "guaranteed_spawns")]
    public GuaranteedSpawns? GuaranteedSpawns { get; set; }

    [YamlMember(Alias = "special_rooms")]
    public List<SpecialRoomDef> SpecialRooms { get; set; } = new();

    [YamlMember(Alias = "stairs")]
    public StairRules? Stairs { get; set; }

    [YamlMember(Alias = "encounter_budget")]
    public EncounterBudget? EncounterBudget { get; set; }

    // Deferred — parsed but not processed this milestone
    [YamlMember(Alias = "door_rules")]
    public Dictionary<string, object>? DoorRules { get; set; }

    [YamlMember(Alias = "trap_rules")]
    public Dictionary<string, object>? TrapRules { get; set; }

    [YamlMember(Alias = "secret_rooms")]
    public Dictionary<string, object>? SecretRooms { get; set; }

    [YamlMember(Alias = "connectivity")]
    public Dictionary<string, object>? Connectivity { get; set; }
}

public sealed class GenerationParameters
{
    [YamlMember(Alias = "max_rooms")] public int? MaxRooms { get; set; }
    [YamlMember(Alias = "min_room_size")] public int MinRoomSize { get; set; } = 5;
    [YamlMember(Alias = "max_room_size")] public int MaxRoomSize { get; set; } = 12;
    [YamlMember(Alias = "max_monsters_per_room")] public int MaxMonstersPerRoom { get; set; } = 3;
    [YamlMember(Alias = "max_items_per_room")] public int MaxItemsPerRoom { get; set; } = 2;
    [YamlMember(Alias = "map_width")] public int? MapWidth { get; set; }
    [YamlMember(Alias = "map_height")] public int? MapHeight { get; set; }
}

public sealed class GuaranteedSpawns
{
    [YamlMember(Alias = "mode")] public string Mode { get; set; } = "additional";
    [YamlMember(Alias = "monsters")] public List<SpawnEntry> Monsters { get; set; } = new();
    [YamlMember(Alias = "items")] public List<SpawnEntry> Items { get; set; } = new();
    [YamlMember(Alias = "equipment")] public List<SpawnEntry> Equipment { get; set; } = new();
}

// SpawnEntry uses a custom IYamlTypeConverter to parse both:
//   count: 2       → CountMin=2, CountMax=2
//   count: "2-5"   → CountMin=2, CountMax=5
public sealed class SpawnEntry
{
    public string Type { get; set; } = "";
    public int CountMin { get; set; } = 1;
    public int CountMax { get; set; } = 1;
}

public sealed class StairRules
{
    [YamlMember(Alias = "up")] public bool Up { get; set; } = true;
    [YamlMember(Alias = "down")] public bool Down { get; set; } = true;
    [YamlMember(Alias = "restrict_return_levels")] public int RestrictReturnLevels { get; set; }
    [YamlMember(Alias = "spawn_rules")] public SpawnRules? SpawnRules { get; set; }
}

public sealed class SpawnRules
{
    [YamlMember(Alias = "near_start_bias")] public float NearStartBias { get; set; } = 0.5f;
}

public sealed class EncounterBudget
{
    [YamlMember(Alias = "etp_min")] public int EtpMin { get; set; }
    [YamlMember(Alias = "etp_max")] public int EtpMax { get; set; }
    [YamlMember(Alias = "allow_spike")] public bool AllowSpike { get; set; }
}

public sealed class SpecialRoomDef
{
    [YamlMember(Alias = "type")] public string Type { get; set; } = "";
    [YamlMember(Alias = "count")] public int Count { get; set; } = 1;
    [YamlMember(Alias = "placement")] public string Placement { get; set; } = "random";
    [YamlMember(Alias = "guaranteed_spawns")] public GuaranteedSpawns? GuaranteedSpawns { get; set; }
    [YamlMember(Alias = "encounter_budget")] public EncounterBudget? EncounterBudget { get; set; }
    // Deferred
    [YamlMember(Alias = "metadata")] public Dictionary<string, object>? Metadata { get; set; }
    [YamlMember(Alias = "faction")] public Dictionary<string, object>? Faction { get; set; }
}
```

**Files to create:**
- `src/Logic/Content/LevelTemplateRegistry.cs` — uses same YamlDotNet deserializer config as `ContentLoader` (`IgnoreUnmatchedProperties`, `UnderscoredNamingConvention`)
- `config/level_templates.yaml` — port depths 1 and 10 from Python prototype (only active ones for milestone)
- `config/level_templates_testing.yaml` — port templates 91-99 (parsed but not executed)

**Tests:**
- Loads real `level_templates.yaml` without error (round-trip parse)
- Returns null for unconfigured depth
- Returns correct override for configured depth
- Count `"2-5"` → CountMin=2, CountMax=5
- Count `3` (int) → CountMin=3, CountMax=3
- Templates 91-99 parse without error despite deferred fields
- Mode defaults to "additional"

---

## Phase 3: Room + MapGenerator

**What:** Pure C# dungeon generator. **Uses random room placement with intersection rejection, matching the Python prototype — NOT BSP.** BSP produces different room distributions for the same seed; matching the algorithm enables cross-prototype validation.

**Files to create:**

- `src/Logic/ECS/Room.cs`:
```csharp
public sealed record Room(int X, int Y, int Width, int Height)
{
    public int CenterX => X + Width / 2;
    public int CenterY => Y + Height / 2;
    public bool Intersects(Room other) => ...;  // with 1-tile padding
    public bool Contains(int x, int y) => x >= X && x < X+Width && y >= Y && y < Y+Height;
}
```

- `src/Logic/ECS/CorridorSegment.cs`:
```csharp
public sealed record CorridorSegment(int X1, int Y1, int X2, int Y2);
```

- `src/Logic/ECS/GeneratedMap.cs`:
```csharp
public sealed class GeneratedMap
{
    public GameMap Map { get; }
    public IReadOnlyList<Room> Rooms { get; }
    public IReadOnlyList<CorridorSegment> Corridors { get; }  // for future door placement
    public Room PlayerRoom { get; }
    public (int X, int Y) PlayerSpawn { get; }
    public (int X, int Y)? StairDownPos { get; }
    public (int X, int Y)? StairUpPos { get; }
}
```

- `src/Logic/ECS/MapGenerator.cs`:
```csharp
public static class MapGenerator
{
    public static GeneratedMap Generate(
        int width, int height,
        int maxRooms, int minRoomSize, int maxRoomSize,
        SeededRandom rng,
        StairRules? stairs = null);
}
```

**Algorithm (matching Python game_map.py lines 198-302):**
1. Initialize `GameMap(width, height, allWalls: true)` — all tiles Wall
2. For each room attempt (up to maxRooms):
   - Random width/height within min/max
   - Random position within map bounds
   - Check intersection with all existing rooms (with 1-tile padding) — skip if overlapping
   - Carve room interior: `SetTile(x, y, TileKind.Floor)`
   - If not first room: connect center of this room to center of previous room with L-shaped tunnel (random H-then-V or V-then-H, `SetTile(x, y, TileKind.Corridor)`). Record as `CorridorSegment`.
3. Player room = first room placed. Player spawn = room center.
4. StairDown = center of last room placed. (If `stairs.NearStartBias > 0`, bias selection toward midpoint room instead.)

**Tests:**
- Flood-fill from player spawn reaches all walkable tiles (connectivity)
- Player spawn is walkable
- StairDown pos is walkable and not in player room
- No room overlaps (all pairs)
- Same seed → identical result (determinism)
- Different seeds → different result
- MaxRooms respected
- Min/max room sizes respected
- Corridor segments recorded and non-empty
- `allWalls` constructor produces non-walkable map before carving

---

## Phase 4: Entity Placement + ETP

**What:** Place monsters, items, and stairs onto a generated map. Separate from geometry generation. Minimal ETP budget checking using `etp_base` already present in `entities.yaml`.

**Do NOT port:** `etp_config.yaml` band system, `initialize_encounter_budget_engine()`, module-level state. Use simple per-room budget from level template or hardcoded defaults (room max 50 ETP for depth 1). Full band system is a future milestone.

**Files to create:**

- `src/Logic/ECS/Stair.cs`:
```csharp
public sealed class Stair : IComponent
{
    public bool IsDown { get; }
    public int TargetDepth { get; }
    public Stair(bool isDown, int targetDepth) { ... }
}
```

- `src/Logic/Core/EntityIdAllocator.cs`:
```csharp
// Simple auto-incrementing ID source for dungeon generation.
// Scenarios use explicit IDs (0 = player, 1+ = monsters).
// Dungeon generation uses this to avoid collisions.
public sealed class EntityIdAllocator
{
    private int _next;
    public EntityIdAllocator(int startFrom = 1) { _next = startFrom; }
    public int Next() => _next++;
}
```

- `src/Logic/Balance/EtpCalculator.cs` — minimal:
```csharp
public static class EtpCalculator
{
    public static int GetEtp(MonsterDefinition def) => def.EtpBase;
    public static bool FitsInBudget(int currentEtp, int addEtp, int maxEtp, bool allowSpike)
        => (currentEtp + addEtp) <= (allowSpike ? maxEtp * 1.5 : maxEtp);
}
```

- `src/Logic/Core/EntityPlacer.cs`:
```csharp
public static class EntityPlacer
{
    public static List<Entity> PlaceGuaranteedSpawns(
        GeneratedMap map, GuaranteedSpawns spawns,
        MonsterFactory monsters, ItemFactory items, ConsumableFactory consumables,
        SeededRandom rng, int depth, EntityIdAllocator ids);

    public static List<Entity> FillRooms(
        GeneratedMap map, GenerationParameters? genParams,
        MonsterFactory monsters, ConsumableFactory consumables,
        SeededRandom rng, int depth, EntityIdAllocator ids,
        int roomEtpMax = 50);

    public static Entity PlaceStairDown(
        GeneratedMap map, int targetDepth, EntityIdAllocator ids);

    public static Entity? PlaceStairUp(
        GeneratedMap map, int targetDepth, EntityIdAllocator ids);
}
```

**Procedural fill logic (matching Python `place_entities`):**
- For each room except player room: roll monster count (0 to `maxMonstersPerRoom`), pick from depth-appropriate pool, check ETP budget per room, place at random walkable position not occupied by another entity or the stair
- For each room: roll item count (0 to `maxItemsPerRoom`), pick from consumable pool

**Tests:**
- mode="replace": only guaranteed entities, no procedural fill
- mode="additional": guaranteed + procedural fill
- Room ETP budget not exceeded
- Stair entity has `Stair` component with correct TargetDepth
- No entities on wall tiles
- No entities on stair position
- No entity ID collisions
- Deterministic

---

## Phase 5: DungeonFloorBuilder + GameState Changes

**What:** The dungeon-mode entry point. Assembles complete GameState for one floor. Includes the `IsGameOver` modification — the highest regression risk in the whole milestone.

**Files to create:**

- `src/Logic/Core/PlayerCarryForward.cs`:
```csharp
public static class PlayerCarryForward
{
    // Creates a new player entity for the new floor,
    // copying current HP, max HP, equipment, inventory from previous floor.
    public static Entity Apply(Entity existingPlayer, EntityIdAllocator ids);
}
```

- `src/Logic/Core/DungeonFloorBuilder.cs`:
```csharp
public sealed class DungeonFloorBuilder
{
    public DungeonFloorBuilder(
        LevelTemplateRegistry templates,
        MonsterFactory monsterFactory,
        ItemFactory itemFactory,
        ConsumableFactory consumableFactory);

    public GameState Build(int depth, SeededRandom rng, Entity? existingPlayer = null);
    // Seed per floor: caller passes rng seeded as baseSeed + depth * 1_000_003
}
```

**Files to modify:**

- `src/Logic/Core/GameState.cs`:
  - Add `bool IsDungeonMode { get; init; }` — defaults to `false`
  - Add `int CurrentDepth { get; init; }` — defaults to `1`
  - Add `Entity? StairDown { get; set; }`
  - Add `bool IsFloorClear => IsDungeonMode && AliveMonsters.Count == 0`
  - Add `bool PlayerOnStairDown => StairDown != null && Player.X == StairDown.X && Player.Y == StairDown.Y`
  - **Modify `IsGameOver`** (highest regression risk):
    ```csharp
    public bool IsGameOver =>
        IsDungeonMode
            ? !PlayerFighter.IsAlive || TurnCount >= TurnLimit
            : !PlayerFighter.IsAlive || (Monsters.Count > 0 && AliveMonsters.Count == 0) || TurnCount >= TurnLimit;
    ```

**Tests:**
- `tests/Core/DungeonFloorBuilderTests.cs`:
  - Player in first room
  - StairDown entity at stair position
  - Guaranteed spawns present
  - Determinism: same depth + rng seed = same floor
  - Player carry-forward preserves HP, equipment, inventory
- `tests/Core/GameStateTests.cs` — **explicit regression guard**:
  - `IsGameOver` (IsDungeonMode=false, all monsters dead) → true ← existing behavior preserved
  - `IsGameOver` (IsDungeonMode=false, turn limit) → true
  - `IsGameOver` (IsDungeonMode=true, all monsters dead) → **false** ← new behavior
  - `IsGameOver` (IsDungeonMode=true, player dead) → true
  - `IsGameOver` (IsDungeonMode=true, turn limit) → true
  - `IsFloorClear` true when dungeon mode + all monsters dead
- `tests/Core/PlayerCarryForwardTests.cs`:
  - HP preserved (not reset to max)
  - Equipment preserved
  - Inventory preserved
  - Position/ID reset correctly for new floor

---

## Phase 6: Descend Action

**What:** Wire `PlayerAction.Descend` into `TurnController`. Additive — no existing actions affected.

**Files to modify:**

- `src/Logic/Core/PlayerAction.cs` — add `ActionKind.Descend` and `static PlayerAction Descend`
- `src/Logic/Core/TurnEvent.cs` — add `public sealed class DescendEvent : TurnEvent { public int NewDepth { get; init; } }`
- `src/Logic/Core/TurnController.cs` — handle `Descend`:
  - Guard: `if (!state.IsDungeonMode || !state.PlayerOnStairDown || !state.IsFloorClear)` → treat as Wait
  - Emit `DescendEvent { ActorId = state.Player.Id, NewDepth = state.CurrentDepth + 1 }`
  - Return result with `GameOver = false` (floor transition, not game over)

**Tests:**
- Descend on stair, floor clear, dungeon mode → DescendEvent emitted
- Descend not on stair → WaitEvent
- Descend, monsters alive → WaitEvent
- Descend, not dungeon mode → WaitEvent
- Existing scenario action tests unchanged

---

## Phase 7: Scenario Schema Extension

**What:** Port remaining scenario fields from Python for YAML compatibility. Independent of all other phases.

**Files to modify:**
- `src/Logic/Balance/ScenarioDefinition.cs` — add:
  - `description` (string)
  - `ScenarioMonster.Position` (int[]? — for `[x, y]` placement)
  - `ScenarioMonster.State` (string? — "aware"/"unaware")
  - `ScenarioItem.Position` (int[]?)

- `src/Logic/Core/GameStateFactory.cs` — use `monster.Position` if set (exact placement), otherwise existing offset logic. Backward compatible.

**Tests:**
- Scenario with `position` fields parses and places correctly
- Scenario without `position` fields uses existing offset logic
- Both round-trip through YAML without errors

---

## Phase 8: Presentation Wiring (Godot) — COMPLETE

**Status:** complete
**Build:** clean (0 warnings, 0 errors)
**Tests:** 289/289 passing

**Files modified:**
- `src/Presentation/Map/DungeonRenderer.cs` — second pass renders stair overlays using `map.GetTileKind(x,y)`. `iso_dun_stairdown_grey.png` and `iso_dun_stairup_grey.png` used. Silent skip if texture missing.
- `src/Presentation/Input/InputHandler.cs` — tap on player's own tile when `PlayerOnStairDown && IsFloorClear` fires `PlayerAction.Descend`.
- `src/Presentation/GameController.cs` — added `event Action<int>? FloorTransitionRequested` (C# event, matching existing pattern — NOT a Godot signal). Captures `DescendEvent` in `_pendingDescend` field and fires `FloorTransitionRequested` in `OnAnimationComplete` after animations complete.
- `src/Presentation/Main.cs` — factories extracted to `InitFactories()` (called once from `_Ready`), presentation setup extracted to `SetupPresentation(GameState)`, `StartDungeon(int depth, Entity? existingPlayer)` added. `LoadAndStart()` kept as default `_Ready` path.

**Notes:**
- `FloorTransitionRequested` uses C# event to match `TurnCompleted`/`GameEnded` pattern — no Godot signals anywhere in GameController.
- Transition fires AFTER animation completes (not on the turn), so the player sees their descend step before floor rebuilds.
- Old `GameController` is freed in `SetupPresentation` — the comment in `OnAnimationComplete` documents why input is NOT re-enabled after firing the transition.
- `StartDungeon` is wired but not the default — `LoadAndStart` (scenario YAML) remains the `_Ready` path until we're ready to switch.

---

## Implementation Order

```
Phase 1 (TileKind + GameMap)           pure C#, additive, zero risk — start here
Phase 2 (LevelTemplateRegistry)        pure C#, YAML loading — in parallel with 1
Phase 7 (Scenario Schema Extension)    pure C#, independent — in parallel with 1-2
Phase 3 (MapGenerator)                 pure C#, needs Phase 1
Phase 4 (Entity Placement + ETP)       pure C#, needs Phase 3
Phase 5 (DungeonFloorBuilder)          pure C#, needs 2+3+4 — highest risk phase
Phase 6 (Descend Action)               pure C#, needs Phase 5
Phase 8 (Presentation wiring)          Godot, needs 1-6 complete
```

Run `dotnet test --filter "Category!=Slow"` after every phase. All 184 tests must stay green throughout.

---

## Harness Compatibility Guarantee

| Component | Status |
|---|---|
| `ScenarioDefinition` existing fields | Unchanged |
| `GameStateFactory.FromScenario` | Unchanged — never touched |
| `GameMap.CreateArena` | Unchanged |
| All `GameMap` movement APIs | Unchanged |
| `TurnController` existing action kinds | Unchanged |
| `ScenarioHarness` / `BotBrain` | Unchanged |
| `GameState.IsGameOver` (IsDungeonMode=false) | Preserved exactly by flag guard |
| All 184 existing tests | Must stay green throughout |

---

## What's Deferred (Future Milestones)

- Doors, secret rooms (schema stubs accept the YAML, nothing processes it)
- Traps, hazards, portals
- Floor persistence (returning to visited floors)
- Monster states (aware/unaware/patrolling) — AI milestone
- Loot policy integration — loot milestone
- Full `etp_config.yaml` band system with multipliers
- ETP sanity tooling
- Special room type generators (boss, treasure, vault)
- Connectivity options (MST + loops, corridor styles)
- Faction room configs

---

## Key Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `IsGameOver` regression | `IsDungeonMode` flag defaults false; explicit regression test suite in Phase 5 |
| `TileKind` / `_walkable` sync drift | All tile writes go through `SetTile`; `CreateArena` is the only allowed exception |
| BSP vs random placement mismatch | Plan now explicitly uses random placement matching Python |
| YAML count range ("2-5") parsing | Custom `IYamlTypeConverter` on `SpawnEntry` |
| `var override` keyword collision | Use `levelOverride` or `templateOverride` as variable name |
| Entity ID collisions in dungeon mode | `EntityIdAllocator` starting above scenario player ID range |
| Deferred YAML keys throwing on parse | Deferred fields use `Dictionary<string, object>?` stubs with `IgnoreUnmatchedProperties` |
| `StairRules.SpawnRules` nesting | Matched exactly in schema — `spawn_rules` is a nested object, not a flat field |
