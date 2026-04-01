# Plan: Corpse Entity & Necromancer AI

**Status:** [ ] Not started
**PoC reference:** `~/development/rlike/components/corpse.py`, `~/development/rlike/death_functions.py`, `~/development/rlike/components/ai/necromancer_ai.py`, `~/development/rlike/components/ai/plague_necromancer_ai.py`, `~/development/rlike/config/entities.yaml` lines 263–365, 609–655

---

## Overview

When a monster dies, its entity transforms in-place into a corpse. Corpses are non-blocking, walkable floor objects with a state machine (FRESH / SPENT / CONSUMED). Necromancers are a new AI archetype that raises FRESH corpses into undead minions, creating a tactical layer where kill order and corpse denial matter. The player also gets access to a Raise Dead scroll targeting corpses.

This is the first system where dead entities remain relevant to gameplay. It unlocks the entire necromancer family and makes the Raise Dead scroll (currently stubbed in SpellResolver) functional.

---

## Why It Matters

Without corpses, combat is fire-and-forget — once something dies, it's gone. Corpses create a resource the necromancer AI exploits, forcing the player to prioritize kill order (necromancer first) or manage corpse positioning. The Raise Dead scroll gives the player the same power, turning enemy corpses into temporary allies.

---

## PoC Design — Exact Values

### Corpse Entity

The dead monster entity is transformed in-place. No new entity is created.

**Components removed on death:** `Fighter`, `AiComponent`, `AlertedState`, all status effects
**Components added on death:** `CorpseComponent`
**Entity changes:** `BlocksMovement = false`

### CorpseComponent Fields

```csharp
string OriginalMonsterId;    // YAML type key ("orc", "zombie")
string OriginalName;         // Display name at time of death
int DeathTurn;               // Turn number when entity died
int RaiseCount;              // Times raised (starts 0)
int MaxRaises;               // Default 1
bool Consumed;               // Prevents re-targeting
string? RaisedByName;        // Who raised it last (null if never raised)
CorpseState State;           // FRESH | SPENT | CONSUMED
string CorpseId;             // Lineage tracking: "corpse_{x}_{y}_{turn}"
```

### CorpseState Enum

| State | Meaning | Transitions |
|-------|---------|-------------|
| FRESH | Newly dead. Can be raised by necromancer or player scroll. | → CONSUMED (after raise, if max_raises reached) |
| SPENT | Re-killed zombie of a previously raised corpse. Cannot be raised again. Can be exploded (deferred). | → CONSUMED (after explosion, deferred) |
| CONSUMED | Final inert state. No further interactions. Stays on floor as visual. | Terminal |

**Scope note:** SPENT state is created by the lineage chain (raised zombie dies → SPENT corpse) but the exploder necromancer that consumes SPENT corpses is deferred. The state machine transitions for SPENT→CONSUMED are documented but not implemented.

### Raise Dead Stat Formula (player scroll, PoC-verified)

| Stat | Formula | Clamp |
|------|---------|-------|
| HP | base × 2.0 | — |
| DamageMin | base × 0.5 | minimum 1 |
| DamageMax | base × 0.5 | minimum 1 |
| STR | base × 0.75 | minimum 6 |
| DEX | base × 0.5 | minimum 6 |
| CON | base × 1.5 | maximum 18 |
| Defense | unchanged | — |
| Accuracy | unchanged | — |
| Evasion | unchanged | — |

- Player-raised: faction = NEUTRAL (attacks everything — player, monsters)
- Necromancer-raised: faction = raiser's faction (e.g., "cultist")

### Necromancer Stats (PoC entities.yaml)

```yaml
necromancer:
  stats:
    hp: 28
    power: 1
    defense: 0
    xp: 80
    damage_min: 2
    damage_max: 4
    strength: 8
    dexterity: 14
    constitution: 12
    accuracy: 4
    evasion: 2
  char: "N"
  color: [80, 40, 120]
  ai_type: "necromancer"
  faction: "cultist"
  tags: ["caster", "controller"]
  etp_base: 44
```

### Necromancer AI Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Raise range | 5 tiles (Euclidean) | `raise_dead_range: 5` |
| Raise cooldown | 4 turns after successful raise | `raise_dead_cooldown_turns: 4` |
| Danger radius | 2 tiles (never approach player closer) | `danger_radius_from_player: 2` |
| Preferred distance min | 4 tiles | `preferred_distance_min: 4` |
| Preferred distance max | 7 tiles | `preferred_distance_max: 7` |

### Necromancer AI Decision Priority (per turn)

1. If raise off cooldown AND FRESH corpse within 5 tiles → **raise it**
2. Else if FRESH corpse exists but out of range → **pathfind toward it** (respecting danger radius)
3. Else if closer than 2 tiles to player → **retreat** (maximize distance)
4. Else → **basic melee AI** (attack if adjacent, approach if in FOV)

### Plague Necromancer (PoC entities.yaml)

Extends necromancer. Same stats, same AI priority. Differences:

- `ai_type: "plague_necromancer"`
- `color: [100, 180, 80]` (sickly green)
- Raises `plague_zombie` instead of `skeleton`/`zombie`
- `summon_monster_id: "plague_zombie"`

### Plague Zombie (PoC entities.yaml)

Extends zombie:

```yaml
plague_zombie:
  extends: zombie
  stats:
    hp: 30
    damage_min: 4
    damage_max: 7
    xp: 45
  char: "Z"
  color: [100, 180, 80]
  tags: ["corporeal_flesh", "undead", "mindless", "low_undead", "plague_carrier", "zombie"]
  etp_base: 40
```

### Raise Dead Scroll

Already defined in `config/entities.yaml` at `scroll_of_raise_dead` with `weight: 0`. Targeting is `location`, range is 5. Re-enable weight after corpse system works.

---

## Architecture Decisions

### Corpse as transformed entity (not new entity)

The dead monster entity keeps its ID. Components are stripped and replaced. This means:
- `state.Monsters` still contains the entity (fighter is dead)
- A new collection `state.Corpses` tracks corpse entities separately
- The entity is removed from `state.Monsters` on transformation and added to `state.Corpses`
- `AliveMonsters` filter already excludes dead fighters, so no change needed there

### Where corpse creation hooks in

Every `DeathEvent` emission in `TurnController` is followed by `DropMonsterLoot`. Corpse creation happens after loot drop — a new `TransformToCorpse` method that:
1. Strips `Fighter`, `AiComponent`, `AlertedState`, all status effects, `SplitTracker`, `CorrosionComponent`
2. Adds `CorpseComponent` with FRESH state
3. Sets `BlocksMovement = false`
4. Moves entity from `state.Monsters` to `state.Corpses`

### Raised entity creation

When a corpse is raised (by necromancer or player scroll):
1. Look up `OriginalMonsterId` in `MonsterFactory`
2. Create a new entity from that definition (fresh stats)
3. Apply raise-dead stat modifiers
4. Place at corpse tile position
5. Set faction (NEUTRAL for player, raiser's faction for AI)
6. Mark corpse as CONSUMED (or SPENT if lineage applies)
7. Add raised entity to `state.Monsters`
8. Add `RaisedFromCorpse` tag component for lineage tracking

### NecromancerAiComponent

A dedicated component (not AiComponent fields) to keep the necromancer-specific config separate:

```csharp
public sealed class NecromancerAiComponent : IComponent
{
    public int RaiseRange { get; set; } = 5;
    public int RaiseCooldown { get; set; } = 4;
    public int DangerRadius { get; set; } = 2;
    public int PreferredDistanceMin { get; set; } = 4;
    public int PreferredDistanceMax { get; set; } = 7;
    public int CooldownRemaining { get; set; } = 0;
    public string SummonMonsterId { get; set; } = "zombie";
}
```

Attached by `MonsterFactory` when `ai_type` is `"necromancer"` or `"plague_necromancer"`. YAML fields on `MonsterDefinition` drive the values.

### Floor descent cleanup

`state.Corpses.Clear()` on floor transition, same pattern as portal cleanup.

---

## Phase 1 — Corpse Entity (Logic Layer)

### TASK-001: CorpseState enum and CorpseComponent

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** none
- **Files to create:**
  - `src/Logic/ECS/CorpseComponent.cs` — component with all fields listed above
  - `src/Logic/ECS/CorpseState.cs` — enum (FRESH, SPENT, CONSUMED)
- **Files to modify:** none
- **Acceptance criteria:**
  - `CorpseComponent` implements `IComponent`
  - All fields from PoC spec present with correct types and defaults
  - `CorpseState` has exactly three values: Fresh, Spent, Consumed
  - Compiles with `dotnet build src/Logic/`

### TASK-002: GameState.Corpses collection

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-001
- **Files to modify:**
  - `src/Logic/Core/GameState.cs` — add `List<Entity> Corpses { get; } = new()`
- **Acceptance criteria:**
  - `state.Corpses` exists as a mutable list, same pattern as `FloorItems` and `Portals`
  - `IsGameOver` logic unchanged (corpses don't affect game-over conditions)
  - Existing tests pass: `dotnet test --filter "Category!=Slow"`

### TASK-003: RaisedFromCorpseTag component

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-001
- **Files to create:**
  - `src/Logic/ECS/RaisedFromCorpseTag.cs` — tag component with `CorpseId` field for lineage tracking
- **Acceptance criteria:**
  - Implements `IComponent`
  - Has `string CorpseId` property (links back to `CorpseComponent.CorpseId`)
  - When a raised zombie dies, TurnController checks for this tag to create SPENT (not FRESH) corpse

### TASK-004: Death → Corpse transformation in TurnController

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-001, TASK-002, TASK-003
- **Files to modify:**
  - `src/Logic/Core/TurnController.cs` — add `TransformToCorpse` method, call after `DropMonsterLoot` at every `DeathEvent` site for monsters (not player death)
  - `src/Logic/Core/TurnEvent.cs` — add `CorpseCreatedEvent` (for presentation layer toast/sprite)
- **Implementation notes:**
  - Three death sites in TurnController emit `DeathEvent` for monsters: player-kills-monster (line ~419), split-fallback (line ~448), monster-kills-player is NOT a corpse (player doesn't become a corpse)
  - `TransformToCorpse(state, deadEntity, killerEntity, events)`:
    1. Get `SpeciesTag` to read `OriginalMonsterId`
    2. Strip components: `Fighter`, `AiComponent`, `AlertedState`, `SplitTracker`, `CorrosionComponent`, `SpeedBonusTracker`, `DamageModifiers`, all status effects (iterate `GetAllComponents()`, remove anything implementing `IStatusEffect`)
    3. Add `CorpseComponent` with state = `RaisedFromCorpseTag` present ? `Spent` : `Fresh`
    4. Set `BlocksMovement = false`
    5. Remove from `state.Monsters`, add to `state.Corpses`
    6. Emit `CorpseCreatedEvent`
  - The player entity is never transformed (only monsters)
  - Guard: don't transform if entity already has `CorpseComponent` (defensive)
- **Acceptance criteria:**
  - After a monster dies, `state.Corpses` contains the entity
  - After a monster dies, `state.Monsters` still contains the entity (for backward compat with `AliveMonsters` filter), OR `state.Monsters` no longer contains it if we move it out — **decision: move it out**. `AliveMonsters` won't miss it since it was already dead.
  - Dead entity has `CorpseComponent` with state = `Fresh`
  - Dead entity has `BlocksMovement = false`
  - Dead entity does NOT have `Fighter` or `AiComponent`
  - `CorpseCreatedEvent` emitted with correct fields
  - Existing combat tests still pass

### TASK-005: Floor descent clears corpses

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-002, TASK-004
- **Files to modify:**
  - `src/Logic/Core/TurnController.cs` — in descend handling, add `state.Corpses.Clear()`
  - OR in `DungeonFloorBuilder` / wherever floor transition resets state
- **Acceptance criteria:**
  - After a `DescendEvent`, `state.Corpses` is empty
  - Corpses from previous floor do not persist

### TASK-006: Phase 1 unit tests

- **Status:** pending
- **Layer:** logic
- **Type:** test
- **Dependencies:** TASK-004, TASK-005
- **Files to create:**
  - `tests/Core/CorpseTests.cs`
- **Test cases:**
  - `MonsterDeath_CreatesCorpseWithFreshState` — kill a monster, verify `CorpseComponent` exists with `State = Fresh`
  - `MonsterDeath_CorpseIsNonBlocking` — verify `BlocksMovement = false`
  - `MonsterDeath_CorpseStripsComponents` — verify no `Fighter`, no `AiComponent`, no `AlertedState`
  - `MonsterDeath_CorpsePreservesPosition` — corpse at same (x, y) as death location
  - `MonsterDeath_CorpseTracksOriginalMonsterId` — `OriginalMonsterId` matches `SpeciesTag`
  - `MonsterDeath_CorpseTracksDeathTurn` — `DeathTurn` matches `state.TurnCount`
  - `MonsterDeath_CorpseIdFormat` — `CorpseId` matches `"corpse_{x}_{y}_{turn}"`
  - `MonsterDeath_CorpseInStateCorpsesList` — entity is in `state.Corpses`
  - `MonsterDeath_CorpseNotInMonstersList` — entity removed from `state.Monsters`
  - `MonsterDeath_EmitsCorpseCreatedEvent` — event in turn result
  - `RaisedZombieDeath_CreatesSPENTCorpse` — entity with `RaisedFromCorpseTag` dies → SPENT state
  - `FloorDescent_ClearsCorpses` — descend, verify `state.Corpses.Count == 0`
  - `PlayerDeath_NoCorpseCreated` — player dies, no `CorpseComponent` added
- **Acceptance criteria:**
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - Tests use deterministic seed (1337)
  - Tests don't depend on Godot

---

## Phase 2 — Raise Dead Spell (Logic Layer)

### TASK-007: SpellResolver.ResolveRaiseDead implementation

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-004
- **Files to modify:**
  - `src/Logic/Combat/SpellResolver.cs` — replace stub `ResolveRaiseDead` with real implementation
- **Files to create:**
  - `src/Logic/Combat/RaiseDeadResolver.cs` — extracted helper for raise-dead stat calculation (shared by player scroll and necromancer AI)
- **Implementation:**
  - Validate target tile (targetX, targetY) is within `spell.Range` (Euclidean) of caster
  - Find corpse at target tile: `state.Corpses.FirstOrDefault(c => c.X == targetX && c.Y == targetY && c.Get<CorpseComponent>()?.State == CorpseState.Fresh)`
  - If no FRESH corpse → return SpellEvent with `Success = false`
  - Create raised entity via `RaiseDeadResolver.Raise(corpse, casterFaction, state, monsterFactory)`
  - `RaiseDeadResolver.Raise`:
    1. Get `CorpseComponent.OriginalMonsterId`
    2. Create entity from `MonsterFactory.Create(monsterId, corpse.X, corpse.Y)`
    3. Apply stat modifiers (HP ×2, DmgMin ×0.5 min 1, DmgMax ×0.5 min 1, STR ×0.75 min 6, DEX ×0.5 min 6, CON ×1.5 max 18, Defense unchanged)
    4. Set faction on `AiComponent`
    5. Add `RaisedFromCorpseTag` with `CorpseId`
    6. Add to `state.Monsters`
  - Mark corpse: increment `RaiseCount`, set `State = Consumed` if `RaiseCount >= MaxRaises`
  - Emit `RaiseDeadEvent` (new TurnEvent subclass)
- **Signature concern:** `SpellResolver.Resolve` currently doesn't receive `MonsterFactory`. Either:
  - (a) Add `MonsterFactory?` parameter to `Resolve` — cascading signature change
  - (b) Pass it via `GameState` — add `GameState.MonsterFactory` property
  - **Decision: (b)** — add `MonsterFactory?` to `GameState` since it's already passed to `ProcessTurn` and needed in multiple places. Set it at the start of `ProcessTurn`.
- **Acceptance criteria:**
  - Casting raise_dead on a tile with a FRESH corpse creates a new monster entity
  - The raised monster has correct stat modifiers applied
  - The raised monster's faction is NEUTRAL when cast by player
  - The corpse's state transitions to CONSUMED
  - Casting on an empty tile or SPENT/CONSUMED corpse returns `Success = false`
  - Range validation works (>5 tiles fails)

### TASK-008: RaiseDeadEvent TurnEvent

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** none (can be created independently)
- **Files to modify:**
  - `src/Logic/Core/TurnEvent.cs` — add `RaiseDeadEvent` and `CorpseCreatedEvent`
- **Fields for RaiseDeadEvent:**
  - `int RaisedEntityId` — ID of the newly raised monster
  - `string RaisedEntityName` — name for toast
  - `int CorpseEntityId` — ID of the corpse that was consumed
  - `string OriginalMonsterName` — "remains of [name]"
  - `int X, Y` — position
  - `bool RaisedByPlayer` — true if player scroll, false if necromancer
- **Fields for CorpseCreatedEvent:**
  - `int CorpseEntityId`
  - `string OriginalMonsterName`
  - `int X, Y`
  - `CorpseState State` — Fresh or Spent
- **Acceptance criteria:**
  - Both events compile and follow the existing `TurnEvent` pattern (sealed class, init properties)

### TASK-009: Re-enable scroll_of_raise_dead weight

- **Status:** pending
- **Layer:** logic
- **Type:** balance
- **Dependencies:** TASK-007
- **Files to modify:**
  - `config/entities.yaml` — change `scroll_of_raise_dead` weight from 0 to a reasonable value (PoC reference needed — check `~/development/rlike/config/entities.yaml` for scroll weights; likely 3-5 given depth 5+ rarity)
- **Acceptance criteria:**
  - `scroll_of_raise_dead` has `weight: 4` (or whatever PoC value is) and `min_depth: 5`
  - Scroll appears in loot pool at depth 5+

### TASK-010: Phase 2 unit tests

- **Status:** pending
- **Layer:** logic
- **Type:** test
- **Dependencies:** TASK-007, TASK-008
- **Files to create:**
  - `tests/Core/RaiseDeadTests.cs`
- **Test cases:**
  - `RaiseDead_FreshCorpse_CreatesRaisedMonster` — raised entity appears in `state.Monsters`
  - `RaiseDead_StatsApplyCorrectly` — HP×2, Dmg×0.5 min 1, STR×0.75 min 6, DEX×0.5 min 6, CON×1.5 max 18
  - `RaiseDead_PlayerCast_FactionNeutral` — raised entity has faction = "neutral"
  - `RaiseDead_CorpseMarkedConsumed` — corpse state = Consumed after raise
  - `RaiseDead_NoCorpseAtTarget_Fails` — SpellEvent.Success = false
  - `RaiseDead_SpentCorpse_Fails` — SPENT corpse cannot be raised
  - `RaiseDead_ConsumedCorpse_Fails` — CONSUMED corpse cannot be raised
  - `RaiseDead_OutOfRange_Fails` — >5 tiles returns failure
  - `RaiseDead_RaisedEntityAtCorpsePosition` — raised entity at (corpse.X, corpse.Y)
  - `RaiseDead_EmitsRaiseDeadEvent` — event present in turn result
  - `RaiseDead_RaisedZombieDies_CreatesSPENTCorpse` — lineage: raised entity dies → SPENT corpse
  - `RaiseDead_MinimumDamageClamp` — monster with DmgMin=1 stays at 1 after ×0.5
- **Acceptance criteria:**
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - Tests verify exact PoC stat multipliers

---

## Phase 3 — Necromancer AI (Logic Layer)

### TASK-011: NecromancerAiComponent

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-001
- **Files to create:**
  - `src/Logic/ECS/NecromancerAiComponent.cs`
- **Fields:**
  - `int RaiseRange = 5`
  - `int RaiseCooldown = 4`
  - `int DangerRadius = 2`
  - `int PreferredDistanceMin = 4`
  - `int PreferredDistanceMax = 7`
  - `int CooldownRemaining = 0`
  - `string SummonMonsterId = "zombie"` — what to raise (overridden for plague_necromancer)
- **Acceptance criteria:**
  - Component implements `IComponent`
  - Default values match PoC

### TASK-012: MonsterDefinition necromancer YAML fields

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-011
- **Files to modify:**
  - `src/Logic/Content/MonsterDefinition.cs` — add necromancer-specific YAML fields:
    - `raise_dead_range: int` (default 5)
    - `raise_dead_cooldown_turns: int` (default 4)
    - `danger_radius_from_player: int` (default 2)
    - `preferred_distance_min: int` (default 4)
    - `preferred_distance_max: int` (default 7)
    - `summon_monster_id: string?` (default null)
  - `src/Logic/Content/MonsterFactory.cs` — when `AiType` is `"necromancer"` or `"plague_necromancer"`, attach `NecromancerAiComponent` with values from definition
- **Acceptance criteria:**
  - `MonsterFactory.Create("necromancer")` produces entity with `NecromancerAiComponent`
  - Component values match YAML config
  - Non-necromancer monsters unaffected

### TASK-013: NecromancerAI decision logic

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-007 (needs RaiseDeadResolver), TASK-011, TASK-012
- **Files to create:**
  - `src/Logic/AI/NecromancerAI.cs` — static `Decide(Entity monster, GameState state)` returning `MonsterAction`
- **Files to modify:**
  - `src/Logic/AI/MonsterAI.cs` — add `"necromancer" => NecromancerAI.Decide(...)` and `"plague_necromancer" => NecromancerAI.Decide(...)` to the switch
  - `src/Logic/AI/MonsterAction.cs` — add `RaiseDead(Entity corpse)` action type if not already present
- **Decision priority implementation:**
  1. Tick cooldown: if `CooldownRemaining > 0`, decrement by 1
  2. Check raise: if cooldown == 0, find nearest FRESH corpse within `RaiseRange` (Euclidean). If found → return `MonsterAction.RaiseDead(corpse)`
  3. Check corpse-seek: if any FRESH corpse exists on the floor but out of range, pathfind toward it. Respect danger radius: if next step brings within `DangerRadius` of player, skip that path.
  4. Check retreat: if Euclidean distance to player < `DangerRadius`, move to maximize distance (reuse `DecideFlee` pattern from BasicMonsterAI)
  5. Else: fall through to `BasicMonsterAI.Decide` for standard melee
- **Acceptance criteria:**
  - Necromancer with corpse in range raises it instead of attacking
  - Necromancer on cooldown seeks corpse or does melee
  - Necromancer never moves within danger radius of player when corpse-seeking
  - Necromancer retreats when player is too close
  - Both `"necromancer"` and `"plague_necromancer"` ai_types dispatch to this AI

### TASK-014: TurnController resolves RaiseDead monster action

- **Status:** pending
- **Layer:** logic
- **Type:** system
- **Dependencies:** TASK-013, TASK-007
- **Files to modify:**
  - `src/Logic/Core/TurnController.cs` — add case for `MonsterAction.RaiseDead` in monster turn resolution
- **Implementation:**
  - Call `RaiseDeadResolver.Raise(corpse, monster.Get<AiComponent>().Faction, state, monsterFactory)`
  - Set `NecromancerAiComponent.CooldownRemaining = RaiseCooldown`
  - Emit `RaiseDeadEvent` with `RaisedByPlayer = false`
  - The raised entity is added to `state.Monsters` and acts on subsequent turns (not the current turn — unlike split children)
- **Acceptance criteria:**
  - Necromancer raises a corpse, cooldown starts
  - Raised entity appears in `state.Monsters` with correct faction
  - `RaiseDeadEvent` emitted
  - Raised entity does NOT act on the turn it was raised (added after monster iteration)

### TASK-015: Necromancer and plague_necromancer in entities.yaml

- **Status:** pending
- **Layer:** logic
- **Type:** scenario
- **Dependencies:** TASK-012
- **Files to modify:**
  - `config/entities.yaml` — add necromancer and plague_necromancer definitions with exact PoC stats
  - `config/entities.yaml` — add plague_zombie definition (extends zombie)
- **YAML entries:**
  ```yaml
  necromancer:
    name: "Necromancer"
    stats:
      hp: 28
      power: 1
      defense: 0
      xp: 80
      damage_min: 2
      damage_max: 4
      strength: 8
      dexterity: 14
      constitution: 12
      accuracy: 4
      evasion: 2
    char: "N"
    color: [80, 40, 120]
    ai_type: "necromancer"
    faction: "cultist"
    blocks: true
    tags: ["caster", "controller"]
    etp_base: 44
    raise_dead_range: 5
    raise_dead_cooldown_turns: 4
    danger_radius_from_player: 2
    preferred_distance_min: 4
    preferred_distance_max: 7
    summon_monster_id: "zombie"
    min_depth: 5
    spawn_weight: 10

  plague_necromancer:
    extends: necromancer
    name: "Plague Necromancer"
    char: "N"
    color: [100, 180, 80]
    ai_type: "plague_necromancer"
    summon_monster_id: "plague_zombie"
    etp_base: 44
    min_depth: 7

  plague_zombie:
    extends: zombie
    name: "Plague Zombie"
    stats:
      hp: 30
      damage_min: 4
      damage_max: 7
      xp: 45
    char: "Z"
    color: [100, 180, 80]
    tags: ["corporeal_flesh", "undead", "mindless", "low_undead", "plague_carrier", "zombie"]
    etp_base: 40
    spawn_weight: 0
  ```
- **Acceptance criteria:**
  - `ContentLoader` parses all three entries without error
  - `MonsterFactory.Create("necromancer")` produces entity with correct components
  - `MonsterFactory.Create("plague_necromancer")` inherits necromancer stats, overrides ai_type and summon_monster_id
  - `plague_zombie` spawned only by necromancer raise (weight: 0, never procedural)

### TASK-016: Phase 3 unit tests

- **Status:** pending
- **Layer:** logic
- **Type:** test
- **Dependencies:** TASK-013, TASK-014, TASK-015
- **Files to create:**
  - `tests/Core/NecromancerAiTests.cs`
- **Test cases:**
  - `Necromancer_RaisesFreshCorpseInRange` — corpse within 5 tiles → raised
  - `Necromancer_CooldownPreventsRaise` — cooldown > 0 → no raise attempt
  - `Necromancer_CooldownTicksDown` — cooldown decrements each turn
  - `Necromancer_SeeksCorpseOutOfRange` — moves toward corpse when out of raise range
  - `Necromancer_RespectssDangerRadius` — won't move within 2 tiles of player when seeking
  - `Necromancer_RetreatsWhenTooClose` — within 2 tiles → moves away
  - `Necromancer_FallsBackToMelee` — no corpses, not in danger → attacks player if adjacent
  - `Necromancer_RaisedMonsterHasRaiserFaction` — raised entity faction = "cultist"
  - `Necromancer_RaisedMonsterDoesNotActSameTurn` — raised entity skips the turn it was created
  - `PlagueNecromancer_RaisesPlagueZombie` — summon_monster_id = "plague_zombie" used
  - `Necromancer_IgnoresSpentCorpse` — SPENT corpse not targeted
  - `Necromancer_IgnoresConsumedCorpse` — CONSUMED corpse not targeted
  - `Necromancer_PreferredDistance` — when no corpse and no danger, maintains 4-7 tiles from player
- **Acceptance criteria:**
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - Tests use deterministic seed
  - Tests construct scenarios without Godot dependencies

---

## Phase 4 — Presentation Layer

### TASK-017: Corpse sprite and rendering

- **Status:** pending
- **Layer:** presentation
- **Type:** system
- **Dependencies:** TASK-004
- **Files to modify:**
  - `src/Presentation/EntitySpriteManager.cs` (or equivalent) — detect `CorpseComponent` on entity, render with corpse sprite / tint
  - Render order: below actors, same layer as floor items
- **Implementation notes:**
  - Corpse visual: dimmed/grayed version of original monster sprite, or a generic "remains" sprite
  - Inspect panel shows "Remains of [OriginalName]" on long-press
- **Acceptance criteria:**
  - Corpses render on the map at correct position
  - Corpses render below living actors
  - Corpses are visually distinct from living monsters

### TASK-018: Raise dead toast messages

- **Status:** pending
- **Layer:** presentation
- **Type:** system
- **Dependencies:** TASK-008
- **Files to modify:**
  - `src/Presentation/GameController.cs` — handle `RaiseDeadEvent` and `CorpseCreatedEvent`
- **Toast messages:**
  - Player raises: "You raise the remains of [name]!"
  - Necromancer raises (in FOV): "The Necromancer raises the remains of [name]!"
  - Corpse created: no toast (visual only — corpse sprite appears)
- **Acceptance criteria:**
  - Toast appears when player uses Raise Dead scroll
  - Toast appears when necromancer raises in player's FOV
  - No toast for out-of-FOV raises

---

## Phase 5 — Deferred (Document Only)

These are documented for future reference. Do NOT implement in this plan.

### SPENT state consumption
- Exploder necromancer targets SPENT corpses, detonates them for AoE damage
- SPENT → CONSUMED transition on explosion
- `CorpseExplosionEvent` TurnEvent
- Explosion damage: TBD (PoC has `explosion_radius: 2`)

### Bone necromancer + bone piles
- Bone necromancer creates bone piles from CONSUMED corpses
- Bone piles are a new entity type (not a corpse state)
- Raises bone_thrall from bone piles
- `bone_necromancer` ai_type

### Corpse denial mechanics
- Fire/poison hazard tiles prevent necromancer pathfinding to corpses
- Holy/light damage could destroy corpses (prevent raise entirely)
- TBD: does Disarm prevent necromancer raise? (PoC says no — raise is not a weapon attack)

### Corpse-specific loot interaction
- Looting a corpse (player inspects and takes remaining items)
- Currently loot drops on death before corpse creation — no interaction needed yet

---

## Risks and Open Decisions

### Risk: GameState.MonsterFactory reference
Adding `MonsterFactory?` to `GameState` creates a new dependency. Alternative: pass it through `SpellResolver.Resolve` parameter list. The `GameState` approach is cleaner since `MonsterFactory` is already threaded through `ProcessTurn` and needed in split resolution. The risk is that tests constructing `GameState` directly would need to optionally provide it — but it's nullable, so no breaking change.

### Risk: Entity removal from state.Monsters
Moving dead entities out of `state.Monsters` into `state.Corpses` could break code that iterates `state.Monsters` expecting to find dead ones. The knowledge update system explicitly says it includes dead monsters: "Build a lookup of all monsters (including dead ones still in state.Monsters)." This code must be updated to also check `state.Corpses` when resolving entity IDs from events.

**Mitigation:** In TASK-004, audit all `state.Monsters` access points:
- `AliveMonsters` — already filters by `IsAlive`, unaffected
- `UpdateKnowledge` — must also check `state.Corpses` for `DeathEvent` actor lookup
- `IsGameOver` / `PlayerWon` — check `Monsters.Count > 0 && AliveMonsters.Count == 0`; if corpses are moved out, `Monsters.Count` shrinks. Need to also count corpses or adjust the condition.
- `AllMonstersDefeated` in `TurnResult` — same concern

**Decision needed:** Should corpses stay in `state.Monsters` (simpler, less risk) or move to `state.Corpses` (cleaner separation)?

**Recommendation:** Keep dead entities in `state.Monsters` AND add them to `state.Corpses`. Dual membership. The `Monsters` list already handles dead entities via `AliveMonsters` filter. `Corpses` is a convenience query list. This avoids all the cascading changes to `IsGameOver`, `PlayerWon`, `UpdateKnowledge`, etc.

### Risk: Raised entity acting on spawn turn
Split children act on spawn turn (by design — "suddenly surrounded"). Raised undead should NOT act on spawn turn (PoC-verified). The implementation must add the raised entity to `state.Monsters` but ensure it's not picked up by the current monster iteration loop. If `ResolveMonsterTurns` uses a snapshot of the list at loop start, this is automatic. If it iterates the live list, the raised entity might get a turn. Verify the iteration pattern before implementing TASK-014.

### Decision: plague_carrier tag behavior
The `plague_zombie` has a `plague_carrier` tag. In the PoC this enables plague spread on melee hit. The plague system itself is in `plan_monster_specials.md` Phase 20A and is NOT implemented yet. For now, the tag is inert metadata. No plague-specific logic ships in this plan. Document this so the builder doesn't try to implement plague spread.

### Decision: Necromancer spawn weight
The PoC doesn't specify a procedural spawn weight for necromancers in the depth_weights table. Propose `spawn_weight: 10` at `min_depth: 5` as a starting point — rare but present. Needs harness validation after implementation. Plague necromancer at `min_depth: 7`.

---

## Metrics for Harness Verification

Once implemented, the following should be measurable via scenario runs:

- `corpses_created` — total FRESH corpses per run
- `raises_completed` — necromancer + player raises per run
- `necromancer_raise_attempts` — how often the AI tries to raise
- `necromancer_cooldown_turns_wasted` — turns spent on cooldown with corpses available
- Death% for necromancer encounters vs. non-necromancer encounters at same depth

These metrics require scenario YAML files with necromancer compositions. Creating those scenarios is out of scope for this plan but should follow immediately after Phase 3.
