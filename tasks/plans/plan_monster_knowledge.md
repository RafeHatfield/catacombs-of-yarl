# Plan: Monster Knowledge + Inspect System

Status: [x] Complete — 2026-03-30
PoC reference: `~/development/rlike/services/monster_knowledge.py`, `~/development/rlike/balance/knowledge_config.py`, `~/development/rlike/ui/tooltip.py`

---

## 1. Overview

The monster knowledge system progressively reveals information about monster species as the player encounters and fights them. On first sight: just the name. After fighting: combat stats. After killing several: warnings and tactical advice. This creates meaningful replayability — veteran players recognize threats, newcomers learn through play.

The inspect UI surfaces this via **long-press** (mobile) and **hover** (desktop). The same mechanism shows item stats on the floor and in inventory.

---

## 2. PoC Reference

**Files:**
- `~/development/rlike/services/monster_knowledge.py` — core system
- `~/development/rlike/balance/knowledge_config.py` — all thresholds
- `~/development/rlike/ui/tooltip.py` — display logic

**Tier thresholds (from knowledge_config.py):**
```python
TIER_1_SEEN_COUNT = 1        # Observed: faction, role, coarse speed
TIER_2_ENGAGED_COUNT = 3     # Battled: durability, damage, accuracy, evasion
TIER_3_KILLED_COUNT = 5      # Understood: warnings, traits, advice
```

**Stat label boundaries:**
```python
DURABILITY_FRAGILE_MAX = 20   # max_hp + defense*5
DURABILITY_STURDY_MAX = 40
DURABILITY_TOUGH_MAX = 70
# above 70 = "monstrous"

DAMAGE_LIGHT_MAX = 4          # average damage per hit
DAMAGE_MODERATE_MAX = 8
DAMAGE_HEAVY_MAX = 14
# above 14 = "brutal"

SPEED_SLUGGISH_MAX = 0.6      # speed_bonus_ratio
SPEED_NORMAL_MAX = 1.2
SPEED_FAST_MAX = 1.8
# above 1.8 = "lightning fast"

ACCURACY_OFTEN_MISSES_MAX = 1   # fighter.accuracy
ACCURACY_USUALLY_HITS_MAX = 3

EVASION_EASY_TO_HIT_MAX = 1    # fighter.evasion
EVASION_AVERAGE_MAX = 2
```

**Major traits that unlock Tier 3 early:**
```python
MAJOR_TRAITS = {"plague_carrier", "swarm_ai"}
TIER_3_TRAIT_EXPERIENCE_UNLOCKS = True
```

---

## 3. Architecture

### 3.1 Logic Layer — MonsterKnowledgeSystem

**New file: `src/Logic/Knowledge/MonsterKnowledgeSystem.cs`**

```csharp
public sealed class MonsterKnowledgeSystem
{
    // Per-species knowledge, keyed by species ID (monster type from YAML, e.g. "orc", "zombie")
    private readonly Dictionary<string, MonsterKnowledgeEntry> _entries = new();

    public MonsterKnowledgeEntry GetOrCreate(string speciesId) { ... }

    public void RecordSeen(string speciesId) { ... }
    public void RecordEngaged(string speciesId) { ... }
    public void RecordKilled(string speciesId) { ... }
    public void RecordTrait(string speciesId, string trait) { ... }

    public MonsterInfoView GetInfoView(string speciesId, MonsterDefinition def) { ... }

    // Called on new game — resets all knowledge
    public void Reset() => _entries.Clear();
}
```

**`MonsterKnowledgeEntry`:**
```csharp
public sealed class MonsterKnowledgeEntry
{
    public int SeenCount { get; set; }
    public int EngagedCount { get; set; }
    public int KilledCount { get; set; }
    public HashSet<string> TraitsDiscovered { get; } = new();

    public KnowledgeTier Tier => SeenCount == 0 ? KnowledgeTier.Unknown
        : EngagedCount >= 3 && KilledCount >= 5 ? KnowledgeTier.Understood
        : EngagedCount >= 3 || TraitsDiscovered.Any(t => MajorTraits.Contains(t)) ? KnowledgeTier.Battled
        : KnowledgeTier.Observed;

    private static readonly HashSet<string> MajorTraits = new() { "plague_carrier", "swarm_ai" };
}

public enum KnowledgeTier { Unknown, Observed, Battled, Understood }
```

**`MonsterInfoView` (pure data, no Godot deps):**
```csharp
public sealed record MonsterInfoView(
    string Name,
    KnowledgeTier Tier,
    string? FactionLabel,     // tier 1+
    string? RoleLabel,        // tier 1+
    string? SpeedLabel,       // tier 1+ coarse, tier 2+ detailed
    string? DurabilityLabel,  // tier 2+
    string? DamageLabel,      // tier 2+
    string? AccuracyLabel,    // tier 2+
    string? EvasionLabel,     // tier 2+
    IReadOnlyList<string> SpecialWarnings, // tier 3+
    string? AdviceLine        // tier 3+
);
```

**Label computation (match PoC exactly):**
- Durability = `maxHp + armorClass * 5` → fragile (<20), sturdy (<40), very tough (<70), monstrous
- Damage = average DPR → light (<4), moderate (<8), heavy (<14), brutal
- Speed = speed stat relative to base → sluggish (<0.6x), normal (<1.2x), fast (<1.8x), lightning fast
- Accuracy → often misses (≤1), sometimes misses (≤3), usually hits, rarely misses
- Evasion → easy to hit (≤1), average evasion (≤2), hard to hit, very evasive

### 3.2 Logic Layer — Species ID on Entities

Entities need a species ID so the knowledge system can key on it. Add to `MonsterDefinition`:
- `string TypeId` — the YAML key (already on `MonsterDefinition` as the dictionary key; expose it or copy it)

Or add a `SpeciesTag` component to monster entities at spawn time (value = YAML type id string).

Check how existing code identifies monster species — read `MonsterFactory` and `MonsterDefinition` before deciding.

### 3.3 Logic Layer — TurnController Integration

In `src/Logic/Core/TurnController.cs`, after processing events, update knowledge:

```csharp
// After ProcessTurn returns TurnResult:
foreach (var evt in result.Events)
{
    switch (evt)
    {
        case AttackEvent atk when atk.ActorId == state.Player.Id:
            var target = state.GetMonster(atk.TargetId);
            if (target != null)
                knowledge.RecordEngaged(target.SpeciesId);
            break;

        case AttackEvent atk when atk.TargetId == state.Player.Id:
            var attacker = state.GetMonster(atk.ActorId);
            if (attacker != null)
                knowledge.RecordEngaged(attacker.SpeciesId);
            break;

        case DeathEvent death when death.ActorId != state.Player.Id:
            var dead = state.GetMonster(death.ActorId); // may be gone from AliveMonsters
            if (dead != null)
                knowledge.RecordKilled(dead.SpeciesId);
            break;
    }
}

// FOV update: record seen for any monster entering FOV
foreach (var m in state.AliveMonsters)
    if (state.Map.IsVisible(m.X, m.Y))
        knowledge.RecordSeen(m.SpeciesId);
```

`MonsterKnowledgeSystem` lives on `GameState` or passed to `ProcessTurn` — decide based on what's cleaner (GameState is the likely home).

### 3.4 Logic Layer — ItemInspectView

**New: `src/Logic/Knowledge/ItemInspectView.cs`**

Simple struct built from an Entity + its components:

```csharp
public sealed record ItemInspectView(
    string Name,
    string Category,    // "weapon", "armor", "scroll", "wand", "potion", "ring"
    string? Description,
    IReadOnlyList<string> StatLines  // e.g. ["Damage: 4-8", "Accuracy: +2"]
);
```

Builder: `ItemInspectView.From(Entity item)` — reads `Fighter`, `SpellEffect`, `WandComponent`, `Consumable`, equipment components and formats them.

---

## 4. Presentation Layer

### 4.1 LongPressDetector (`src/Presentation/Input/LongPressDetector.cs`)

Godot `Node` — detects long-press (mobile) and hover (desktop):

```csharp
public sealed partial class LongPressDetector : Node
{
    private const float LongPressThreshold = 0.5f;  // seconds
    private const float HoverThreshold = 0.3f;       // seconds desktop

    [Signal] public delegate void LongPressDetectedEventHandler(Vector2 position);

    private Vector2 _touchStart;
    private double _holdTime;
    private bool _holding;

    // Touch: _Input(InputEventScreenTouch down) → start timer; up → cancel
    // Mouse: _Input(InputEventMouseMotion) → reset timer on move; fire after threshold
}
```

### 4.2 InspectPanel (`src/Presentation/UI/InspectPanel.cs`)

Godot `Control` — floating panel showing monster or item info:

```csharp
public sealed partial class InspectPanel : Control
{
    public void ShowMonster(MonsterInfoView info) { ... }
    public void ShowItem(ItemInspectView info) { ... }
    public void Hide() { ... }

    // Smart positioning: appears near tapped tile, flips if near edge
    public void PositionNear(Vector2 screenPos) { ... }
}
```

**Monster panel layout (tier-gated):**
- Always: monster name (large), tier indicator (e.g. "★ Observed")
- Tier 1+: faction tag, role label, coarse speed
- Tier 2+: durability, damage, accuracy, evasion labels
- Tier 3+: special warnings in orange, advice line in yellow

**Item panel layout:**
- Name, category
- Stat lines (damage range, AC bonus, spell effect, charges, etc.)

### 4.3 GameController Integration

In `src/Presentation/GameController.cs`:
- Wire `LongPressDetector.LongPressDetected` → `OnLongPress(position)`
- `OnLongPress`: convert screen position to grid tile, check for monster/item at tile, call `InspectPanel.ShowMonster` or `ShowItem`
- Tap elsewhere or next turn → `InspectPanel.Hide()`

---

## 5. Phases

### Phase 1 — Logic Infrastructure (no UI)
- `MonsterKnowledgeEntry`, `KnowledgeTier`, `MonsterInfoView`
- `MonsterKnowledgeSystem` with RecordSeen/Engaged/Killed/Trait
- Species ID on entities (SpeciesTag component or MonsterDefinition.TypeId)
- `TurnController` integration: update knowledge after each turn
- `GameState.Knowledge` property (singleton per run, reset on new game)
- Tests: tier transitions, stat label computation, knowledge accumulation

### Phase 2 — Item Inspect View
- `ItemInspectView` builder
- Tests: correct stat lines for each item category

### Phase 3 — Presentation (long-press + panel)
- `LongPressDetector` (touch + hover)
- `InspectPanel` with monster and item modes
- `GameController` wiring
- Presentation tests: panel shows correct tier content, positions near tapped tile

---

## 6. Acceptance Criteria

### Phase 1
- [ ] First time monster seen: tier = Observed
- [ ] After 3 engagements (attack or attacked): tier = Battled
- [ ] After 5 kills: tier = Understood
- [ ] Major trait (plague_carrier) triggers Battled early
- [ ] RecordKilled increments correctly from DeathEvent
- [ ] Knowledge resets on new game
- [ ] Stat labels match PoC thresholds exactly

### Phase 2
- [ ] Weapon inspect shows damage range and accuracy
- [ ] Wand inspect shows spell name and charges remaining
- [ ] Scroll inspect shows spell name and description
- [ ] Potion inspect shows heal amount (or effect for non-heal potions)

### Phase 3
- [ ] Long-press on monster tile shows InspectPanel with tier-gated content
- [ ] Long-press on item tile shows ItemInspectView
- [ ] Long-press on empty tile: no panel
- [ ] Panel dismisses on tap elsewhere
- [ ] Panel repositions near tile edges to avoid going off-screen
- [ ] Desktop hover (0.3s) shows same panel

---

## 7. Tests

### Phase 1 — `tests/Core/MonsterKnowledgeTests.cs`
```
- RecordSeen_Once_TierIsObserved
- RecordSeen_Zero_TierIsUnknown
- RecordEngaged_ThreeTimes_TierIsBattled
- RecordEngaged_TwoTimes_TierStillObserved
- RecordKilled_FiveTimes_TierIsUnderstood
- RecordKilled_Four_TierStillBattled
- MajorTrait_PlagueCarrier_TriggersBattledEarly
- StatLabels_Durability_FragileRange
- StatLabels_Durability_MonstruosRange
- StatLabels_Damage_LightRange
- StatLabels_Damage_BrutalRange
- StatLabels_Speed_SluggishRange
- StatLabels_Speed_LightningFastRange
- InfoView_UnknownTier_AllLabelsNull
- InfoView_ObservedTier_OnlyFactionAndRole
- InfoView_BattledTier_IncludesCombatStats
- InfoView_UnderstoodTier_IncludesWarnings
- TurnController_AttackEvent_IncrementEngaged
- TurnController_DeathEvent_IncrementKilled
- Knowledge_Reset_ClearsAllEntries
```

### Phase 2 — `tests/Core/ItemInspectTests.cs`
```
- Weapon_ShowsDamageRange
- Weapon_ShowsAccuracyBonus
- Armor_ShowsAcBonus
- Wand_ShowsChargesAndSpell
- Scroll_ShowsSpellName
- Potion_ShowsHealAmount
```

---

## 8. Deferred

- Identification system integration: unidentified scrolls/wands show `???` name until identified (plan_identification_system)
- Trait discovery from special events (e.g., first time a zombie resurrects, "plague_carrier" trait is discovered)
- Monster bestiary screen (persistent across runs — future feature)
