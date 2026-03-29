# Plan: Slime Monsters (slime + large_slime)

**Status:** PENDING
**PoC reference:** `~/development/rlike/config/entities.yaml` lines 483–549, `~/development/rlike/services/slime_split_service.py`, `~/development/rlike/components/fighter.py` lines 631–676, 1594–1629, 2295–2338

---

## What this plan does

Adds `slime` and `large_slime` to the procedural spawn pool. These are the first non-orc faction enemies — they appear at depth 2+ (slime, weight 20–60) making early playtesting immediately more varied.

Two mechanics come with them that are core to their identity:

1. **Split Under Pressure** — large_slime splits into 2–3 minor slimes when HP drops below 40%. NOT split-on-death. One-time-only.
2. **Corrosion** — on each hit against the player, a percentage chance to degrade the player's equipped metal weapon by 1 DamageMax, capped at 50% of base.

Both mechanics are data-driven from YAML config, reusable by future monsters.

---

## PoC design — exact values

### Slime stats
```
slime:      hp:15  dmg:1-3  str:8  dex:6  con:10  acc:default  ev:default
            etp_base:10  corrosion_chance:0.05  no split
            faction:"hostile_all" (deferred — see deferred plan)
            tags:["no_flesh","amorphous","acidic"]
            depth_weights: [[20,2],[40,4],[60,6]]

large_slime: hp:40  dmg:2-5  str:12  dex:6  con:14  def:1  xp:75
             etp_base:35  corrosion_chance:0.10
             split_trigger_hp_pct:0.40  split_child_type:"slime"
             split_min:2  split_max:3  split_weights:[40,60]
             depth_weights: [[5,3],[15,5],[25,7]]
```

### Corrosion mechanic (PoC `_corrode_weapon`)
- Triggers on any successful hit if attacker has `corrosion_chance > 0`
- Roll: `rng.NextDouble() < corrosion_chance`
- Target: player's equipped **metal** main-hand weapon only
- Effect: `weapon.DamageMax -= 1`
- Floor: `Math.Max(1, BaseDamageMax / 2)` — can never corrode below 50% of base
- Message: orange text in combat log

### Split mechanic (PoC `slime_split_service.py`)
- Triggers AFTER HP damage is applied, BEFORE death check
- Condition: `fighter.Hp / fighter.MaxHp < split_trigger_hp_pct`
- Guard: `HasSplit == true` → skip (one-time only)
- On trigger: mark `HasSplit = true`, remove original, spawn children
- Children: `num_children` determined by weighted random from `split_weights`
- Spawn positions: expanding ring search around original position (radius 1–3)
- Depth: children inherit current floor depth (scale correctly)
- Split takes precedence over death — if a hit would both split and kill, split wins

---

## Changes required

### 1. `MonsterDefinition.cs` — split config fields

Add to `MonsterDefinition`:
```csharp
[YamlMember(Alias = "corrosion_chance")]
public double CorrosionChance { get; set; } = 0.0;

[YamlMember(Alias = "split_trigger_hp_pct")]
public double? SplitTriggerHpPct { get; set; }

[YamlMember(Alias = "split_child_type")]
public string? SplitChildType { get; set; }

[YamlMember(Alias = "split_min_children")]
public int SplitMinChildren { get; set; } = 2;

[YamlMember(Alias = "split_max_children")]
public int SplitMaxChildren { get; set; } = 3;

[YamlMember(Alias = "split_weights")]
public List<int>? SplitWeights { get; set; }
```

`ContentLoader.Merge` inheritance rules:
- `CorrosionChance`: child `!= 0` wins, else parent
- `SplitTriggerHpPct`: child non-null wins, else parent
- `SplitChildType`: child non-null wins, else parent
- `SplitMinChildren`, `SplitMaxChildren`: child `!= 2`/`!= 3` wins, else parent
- `SplitWeights`: child non-null wins, else parent

---

### 2. `SplitTracker` component — new file

**File:** `src/Logic/ECS/SplitTracker.cs`

```csharp
namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Tracks split-under-pressure config and one-time-split guard.
/// Set on large_slime (and any future splitting monster) at spawn time.
/// </summary>
public sealed class SplitTracker : IComponent
{
    public Entity? Owner { get; set; }

    public double TriggerHpPct { get; }
    public string ChildType { get; }
    public int MinChildren { get; }
    public int MaxChildren { get; }
    public int[]? Weights { get; }

    /// <summary>True once split has fired. Prevents double-splitting.</summary>
    public bool HasSplit { get; set; }

    public SplitTracker(double triggerHpPct, string childType,
        int minChildren, int maxChildren, int[]? weights)
    {
        TriggerHpPct = triggerHpPct;
        ChildType = childType;
        MinChildren = minChildren;
        MaxChildren = maxChildren;
        Weights = weights;
    }
}
```

**`MonsterFactory.CreateFromDefinition`** — attach `SplitTracker` when `SplitTriggerHpPct` is set:
```csharp
if (def.SplitTriggerHpPct.HasValue && def.SplitChildType != null)
{
    entity.Add(new SplitTracker(
        triggerHpPct: def.SplitTriggerHpPct.Value,
        childType: def.SplitChildType,
        minChildren: def.SplitMinChildren,
        maxChildren: def.SplitMaxChildren,
        weights: def.SplitWeights?.ToArray()));
}
```

---

### 3. `Equippable.cs` — add `Material` and `BaseDamageMax`

**File:** `src/Logic/Combat/Equippable.cs`

Add two fields:
```csharp
/// <summary>
/// Physical material of the weapon. "metal" weapons can be corroded by slimes.
/// "wood" and null are immune. Matches PoC entities.yaml material field.
/// </summary>
public string? Material { get; set; }

/// <summary>
/// Original DamageMax at creation time — never changes.
/// Used as the floor for corrosion (weapon can't be degraded below 50% of base).
/// </summary>
public int BaseDamageMax { get; private set; }
```

Set `BaseDamageMax` in the constructor or via an init method. Since `Equippable` uses a slot-only constructor, set it via property init after `DamageMax` is assigned:

In `ItemFactory.cs` where `Equippable` is created:
```csharp
var equippable = new Equippable(slot)
{
    DamageMin = def.DamageMin,
    DamageMax = def.DamageMax,
    Material = def.Material,      // new
};
equippable.SetBaseDamageMax();    // captures DamageMax at creation
```

Add to `Equippable`:
```csharp
/// <summary>Call once after DamageMax is set at creation.</summary>
public void SetBaseDamageMax() => BaseDamageMax = DamageMax;
```

---

### 4. `ItemDefinition.cs` — add `Material` field

**File:** `src/Logic/Content/ItemDefinition.cs`

```csharp
/// <summary>
/// Physical material. "metal" weapons can be corroded by slimes.
/// "wood" and null are immune.
/// </summary>
[YamlMember(Alias = "material")]
public string? Material { get; set; }
```

---

### 5. `TurnController.cs` — split and corrosion resolution

#### 5a. Split — in `ResolvePlayerAttack`, after damage is applied

After the existing damage/death logic, add:
```csharp
// Check for split-under-pressure BEFORE death check
var split = target.Get<SplitTracker>();
if (split != null && !split.HasSplit)
{
    var tFighter = target.Require<Fighter>();
    double hpPct = tFighter.MaxHp > 0 ? (double)tFighter.Hp / tFighter.MaxHp : 0;
    if (hpPct < split.TriggerHpPct)
    {
        split.HasSplit = true;
        ResolveSplit(state, target, split, events);
        return; // original is gone — skip death event
    }
}
```

New private method `ResolveSplit`:
```csharp
private static void ResolveSplit(GameState state, Entity original, SplitTracker split, List<TurnEvent> events)
{
    int numChildren = RollSplitChildren(split, state.Rng);
    var positions = FindSplitPositions(state.Map, original.X, original.Y, numChildren, state);

    // Kill original (HP = 0, no XP event — split is not a kill)
    var origFighter = original.Require<Fighter>();
    origFighter.Hp = 0;
    state.Map.UnregisterEntity(original);

    var children = new List<Entity>();
    for (int i = 0; i < Math.Min(numChildren, positions.Count); i++)
    {
        var child = state.MonsterFactory.Create(split.ChildType,
            positions[i].X, positions[i].Y, state.Depth, state.Rng);
        if (child == null) continue;
        state.Monsters.Add(child);
        state.Map.RegisterEntity(child);
        children.Add(child);
    }

    events.Add(TurnEvent.Split(original, children));
    // No XP awarded — split is not a kill
}
```

`GameState` needs a `Rng` property (check if already present) and `MonsterFactory` reference. If `MonsterFactory` isn't currently on `GameState`, it needs to be added — see note below.

`RollSplitChildren` — weighted random using `SeededRandom`:
```csharp
private static int RollSplitChildren(SplitTracker split, SeededRandom rng)
{
    if (split.Weights == null || split.Weights.Length == 0)
        return rng.Next(split.MinChildren, split.MaxChildren + 1);

    int total = split.Weights.Sum();
    int roll = rng.Next(total);
    int running = 0;
    for (int i = 0; i < split.Weights.Length; i++)
    {
        running += split.Weights[i];
        if (roll < running)
            return split.MinChildren + i;
    }
    return split.MaxChildren;
}
```

`FindSplitPositions` — expanding ring search (port of PoC `_get_valid_spawn_positions`):
```csharp
private static List<(int X, int Y)> FindSplitPositions(
    GameMap map, int cx, int cy, int count, GameState state)
{
    var found = new List<(int X, int Y)>();
    var occupied = state.Monsters
        .Where(m => m.Require<Fighter>().IsAlive)
        .Select(m => (m.X, m.Y))
        .ToHashSet();
    occupied.Add((state.Player.X, state.Player.Y));

    for (int radius = 1; radius <= 3 && found.Count < count; radius++)
    {
        for (int dx = -radius; dx <= radius && found.Count < count; dx++)
        for (int dy = -radius; dy <= radius && found.Count < count; dy++)
        {
            if (Math.Abs(dx) != radius && Math.Abs(dy) != radius) continue;
            int nx = cx + dx, ny = cy + dy;
            if (map.IsWalkable(nx, ny) && !occupied.Contains((nx, ny)))
            {
                found.Add((nx, ny));
                occupied.Add((nx, ny)); // reserve for next child
            }
        }
    }

    if (found.Count == 0) found.Add((cx, cy)); // fallback: stack on origin
    return found;
}
```

#### 5b. Corrosion — in monster attack resolution

In `ResolveMonsterAttack` (or wherever monster → player damage is applied), after a successful hit:
```csharp
// Corrosion check — slimes degrade metal weapons on hit
var attackerFighter = attacker.Require<Fighter>();
// CorrosionChance is stored on the entity — read from a CorrosionComponent or fighter extension
// Simplest approach: check attacker tags for "acidic" and read CorrosionChance via component
var corrosion = attacker.Get<CorrosionComponent>();
if (corrosion != null && damage > 0)
    ResolveCorrosion(state, corrosion.Chance, state.Rng, events);
```

`CorrosionComponent` — new simple component:
```csharp
public sealed class CorrosionComponent : IComponent
{
    public Entity? Owner { get; set; }
    public double Chance { get; }
    public CorrosionComponent(double chance) => Chance = chance;
}
```

Attached in `MonsterFactory` when `CorrosionChance > 0`.

`ResolveCorrosion`:
```csharp
private static void ResolveCorrosion(GameState state, double chance, SeededRandom rng, List<TurnEvent> events)
{
    if (rng.NextDouble() >= chance) return;

    var equipment = state.Player.Get<Equipment>();
    var mainHand = equipment?.MainHand;
    if (mainHand == null) return;

    var equippable = mainHand.Get<Equippable>();
    if (equippable == null || equippable.Material?.ToLower() != "metal") return;

    int floor = Math.Max(1, equippable.BaseDamageMax / 2);
    if (equippable.DamageMax <= floor) return;

    equippable.DamageMax--;
    events.Add(TurnEvent.Corrosion(mainHand, equippable.DamageMax, equippable.BaseDamageMax));
}
```

---

### 6. `TurnEvent.cs` — new event types

Add:
```csharp
/// <summary>A splitting monster has divided into children.</summary>
public static TurnEvent Split(Entity original, IReadOnlyList<Entity> children) =>
    new(TurnEventKind.Split) { SourceEntity = original, SpawnedEntities = children.ToList() };

/// <summary>A metal weapon was corroded by acid.</summary>
public static TurnEvent Corrosion(Entity weapon, int newDamageMax, int baseDamageMax) =>
    new(TurnEventKind.Corrosion) { SourceEntity = weapon, Value = newDamageMax, MaxValue = baseDamageMax };
```

Add `TurnEventKind.Split` and `TurnEventKind.Corrosion` to the enum.
Add `SpawnedEntities` list field to `TurnEvent` (only populated for Split events).

---

### 7. `GameState` — `MonsterFactory` reference

`ResolveSplit` needs to spawn new monsters. Currently `MonsterFactory` lives in `DungeonFloorBuilder`, not `GameState`.

**Option A:** Pass `MonsterFactory` to `TurnController.ProcessTurn` as a parameter.
**Option B:** Add `MonsterFactory` as a field on `GameState`.
**Option C:** Pre-resolve the factory via a `SpawnRequest` that `DungeonFloorBuilder` processes — overkill.

**Recommended: Option A** — pass `MonsterFactory` as optional parameter to `ProcessTurn`. Null means no splitting possible (test environments that don't need it). This keeps `GameState` as a pure data container.

`ProcessTurn` signature change:
```csharp
public static TurnResult ProcessTurn(
    GameState state,
    PlayerAction action,
    MonsterFactory? monsterFactory = null)
```

---

### 8. `config/entities.yaml` — slime definitions + weapon materials

#### New monsters
```yaml
  slime:
    name: "Slime"
    stats:
      hp: 15
      power: 0
      defense: 0
      xp: 25
      damage_min: 1
      damage_max: 3
      strength: 8
      dexterity: 6
      constitution: 10
      accuracy: 3
      evasion: 0
    char: "s"
    color: [0, 255, 0]
    ai_type: "basic"
    faction: "beast"          # "hostile_all" deferred — see deferred plan
    render_order: "actor"
    blocks: true
    tags: ["no_flesh", "amorphous", "acidic"]
    etp_base: 10
    can_seek_items: false
    inventory_size: 0
    corrosion_chance: 0.05
    spawn_weight: 0           # no flat weight — uses depth_weights
    depth_weights:
      - weight: 20
        min_depth: 2
      - weight: 40
        min_depth: 4
      - weight: 60
        min_depth: 6

  large_slime:
    name: "Large Slime"
    extends: slime
    stats:
      hp: 40
      defense: 1
      xp: 75
      damage_min: 2
      damage_max: 5
      strength: 12
      constitution: 14
    char: "S"
    color: [0, 200, 0]
    etp_base: 35
    corrosion_chance: 0.10
    split_trigger_hp_pct: 0.40
    split_child_type: "slime"
    split_min_children: 2
    split_max_children: 3
    split_weights: [40, 60]
    depth_weights:
      - weight: 5
        min_depth: 3
      - weight: 15
        min_depth: 5
      - weight: 25
        min_depth: 7
```

#### Weapon materials — update existing items
Add `material` field to all weapons in `config/entities.yaml` items section:
- `dagger`: metal
- `shortsword`: metal
- `longsword`: metal
- `club`: wood
- `quarterstaff`: wood
- `mace`: metal
- `battleaxe`: metal
- All other swords/axes: metal

---

### 9. `GameController.cs` (Presentation) — handle Split and Corrosion events

In `OnTurnCompleted` (or wherever events are processed):

**Split:** Remove sprite for original entity, spawn sprites for children. Use existing `SpawnMonsterSprite` pathway for children.

**Corrosion:** Add toast message "The slime corrodes your [weapon name]! [X%]"

---

## Files changed summary

| File | Change |
|------|--------|
| `src/Logic/Content/MonsterDefinition.cs` | Add split config fields + CorrosionChance |
| `src/Logic/Content/ContentLoader.cs` | Merge rules for new fields |
| `src/Logic/Content/MonsterFactory.cs` | Attach SplitTracker + CorrosionComponent at spawn |
| `src/Logic/Content/ItemDefinition.cs` | Add Material field |
| `src/Logic/Content/ItemFactory.cs` | Set Material + call SetBaseDamageMax on Equippable |
| `src/Logic/Combat/Equippable.cs` | Add Material, BaseDamageMax, SetBaseDamageMax() |
| `src/Logic/ECS/SplitTracker.cs` | NEW — split config + HasSplit guard |
| `src/Logic/ECS/CorrosionComponent.cs` | NEW — corrosion chance carrier |
| `src/Logic/Core/TurnController.cs` | Split check in ResolvePlayerAttack; corrosion check in monster attack; ResolveSplit + ResolveCorrosion helpers; MonsterFactory param on ProcessTurn |
| `src/Logic/Core/TurnEvent.cs` | TurnEventKind.Split + Corrosion; SpawnedEntities field; factory methods |
| `src/Presentation/GameController.cs` | Handle Split + Corrosion events |
| `config/entities.yaml` | Add slime + large_slime; add material to weapons |

---

## Out of scope — see `tasks/plans/deferred_slime_abilities.md`

- `greater_slime` (depth 7+, splits into large_slimes)
- `engulf` mechanic (movement penalty while slime is adjacent)
- `hostile_all` faction behavior (slimes attacking other monsters)
- `natural_damage_type: "acid"` and damage type system
- Corrosion armor degradation

---

## Validation

### Automated tests
- `SlimeDoesNotSplitAboveHpThreshold` — deal non-triggering damage, assert no split
- `SlimeSplitsAtHpThreshold` — deal triggering damage, assert original gone + 2–3 children spawned
- `SlimeSplitsOnlyOnce` — hit twice past threshold, assert no double-split
- `CorrosionDoesNotAffectWoodWeapon` — slime hits player with wood weapon equipped, assert no degradation
- `CorrosionDegradesMetal` — force corrosion (roll = 0), assert DamageMax decreases
- `CorrosionFloorAt50Pct` — corrode to floor, assert DamageMax stops at BaseDamageMax/2
- `LargeSlimeDoesNotSpawnBeforeDepth3` — depth 2 generation, assert no large_slime
- `SlimeSpawnsAtDepth2` — depth 2 generation, assert slime present

### Regression
- `dotnet test --filter "Category!=Slow"` — all existing + new tests pass

### Manual smoke
- Depth 2: slimes appear, corrosion toast fires on hit with metal weapon
- Depth 3: large slimes start appearing; split at ~40% HP spawns 2–3 slimes
- Wood club equipped: no corrosion messages
