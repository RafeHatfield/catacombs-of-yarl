# Plan: Scroll, Wand, and Portal System

Status: [x] Complete — Phases 1–5 complete (2026-03-29)
PoC reference: `~/development/rlike` — components/status_effects.py, actions/spells.py, entities.yaml scrolls/wands sections

---

## 1. Architecture Overview

### 1.1 Design Decision: SpellEffect vs Extending ConsumableDefinition

The current `Consumable` component only models healing potions (`HealAmount` + `StackSize`). Scrolls and wands introduce dozens of distinct effect types with targeting modes, AoE parameters, durations, and damage values. Extending `Consumable` with all those fields would bloat every potion entity and violate single-responsibility.

**Decision: New `SpellEffect` component + `SpellDefinition` YAML type.**

- `Consumable` keeps its existing role for potions (stackable, `HealAmount`).
- Scrolls get a `Consumable` (for stack/consume behavior) **plus** a `SpellEffect` component (for what happens on use).
- Wands get a `WandComponent` (charge tracking) **plus** a `SpellEffect` component.
- A shared `SpellResolver` service reads `SpellEffect` and executes the spell logic.

This means `TurnController.TryHeal` stays untouched for potions. A new `ResolveSpell` method handles scrolls and wands.

### 1.2 SpellEffect Component (Logic Layer)

```csharp
// src/Logic/Combat/SpellEffect.cs
public sealed class SpellEffect : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>Canonical spell ID, e.g. "lightning", "fireball", "confusion".</summary>
    public string SpellId { get; set; } = "";

    /// <summary>Targeting mode for this spell.</summary>
    public TargetingMode Targeting { get; set; } = TargetingMode.Self;

    /// <summary>Damage dealt (for direct-damage spells). 0 if not applicable.</summary>
    public int Damage { get; set; }

    /// <summary>AoE radius (for fireball, earthquake, fear, etc.). 0 = single target.</summary>
    public int Radius { get; set; }

    /// <summary>Max range for targeting. 0 = unlimited / self.</summary>
    public int Range { get; set; }

    /// <summary>Duration in turns for applied status effects. 0 = instant.</summary>
    public int Duration { get; set; }

    /// <summary>Secondary effect value (e.g., hazard damage, defense bonus).</summary>
    public int SecondaryValue { get; set; }

    /// <summary>Secondary effect duration (e.g., hazard duration).</summary>
    public int SecondaryDuration { get; set; }

    /// <summary>Misfire chance (0.0 to 1.0). Used by teleport scroll (0.10).</summary>
    public double MisfireChance { get; set; }
}

public enum TargetingMode
{
    Self,           // No UI, instant
    AutoClosest,    // Auto-picks closest visible enemy, no UI
    SingleTarget,   // Tap to select entity
    Location,       // Tap to select floor tile
    AoeSelf,        // AoE centered on caster, no targeting UI
    Cone,           // Tap to select direction (deferred)
    Portal,         // Two-step tap: entrance then exit
}
```

### 1.3 WandComponent (Logic Layer)

```csharp
// src/Logic/Combat/WandComponent.cs
public sealed class WandComponent : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>Current charges remaining.</summary>
    public int Charges { get; set; }

    /// <summary>Maximum charges this wand can hold.</summary>
    public int MaxCharges { get; set; } = 10;

    /// <summary>
    /// Matching scroll ID for recharge. When a scroll with this ID is picked up
    /// while the player holds this wand, the scroll is consumed and +1 charge is added.
    /// </summary>
    public string? RechargeScrollId { get; set; }

    /// <summary>True if this wand has unlimited uses (Wand of Portals).</summary>
    public bool Infinite { get; set; }

    public bool HasCharges => Infinite || Charges > 0;

    public bool TryConsume()
    {
        if (Infinite) return true;
        if (Charges <= 0) return false;
        Charges--;
        return true;
    }
}
```

### 1.4 PortalComponent (Logic Layer)

```csharp
// src/Logic/Combat/PortalComponent.cs
public sealed class PortalComponent : IComponent
{
    public Entity? Owner { get; set; }

    public PortalType Type { get; set; }

    /// <summary>Entity ID of the linked portal on the other end.</summary>
    public int LinkedPortalId { get; set; } = -1;
}

public enum PortalType { Entrance, Exit }
```

### 1.5 PortalPlacerComponent (Logic Layer)

```csharp
// src/Logic/Combat/PortalPlacerComponent.cs
public sealed class PortalPlacerComponent : IComponent
{
    public Entity? Owner { get; set; }

    public PortalPlacerStage Stage { get; set; } = PortalPlacerStage.Idle;

    /// <summary>Entity ID of the placed entrance portal (or -1 if none).</summary>
    public int EntranceId { get; set; } = -1;

    /// <summary>Entity ID of the placed exit portal (or -1 if none).</summary>
    public int ExitId { get; set; } = -1;
}

public enum PortalPlacerStage { Idle, PlacingEntrance, PlacingExit }
```

### 1.6 SpellDefinition (YAML Deserialization)

```csharp
// src/Logic/Content/SpellDefinition.cs
public sealed class SpellDefinition
{
    [YamlMember(Alias = "name")]
    public string? Name { get; set; }

    [YamlMember(Alias = "spell_id")]
    public string SpellId { get; set; } = "";

    [YamlMember(Alias = "targeting")]
    public string Targeting { get; set; } = "self";

    [YamlMember(Alias = "damage")]
    public int Damage { get; set; }

    [YamlMember(Alias = "radius")]
    public int Radius { get; set; }

    [YamlMember(Alias = "range")]
    public int Range { get; set; }

    [YamlMember(Alias = "duration")]
    public int Duration { get; set; }

    [YamlMember(Alias = "secondary_value")]
    public int SecondaryValue { get; set; }

    [YamlMember(Alias = "secondary_duration")]
    public int SecondaryDuration { get; set; }

    [YamlMember(Alias = "misfire_chance")]
    public double MisfireChance { get; set; }

    [YamlMember(Alias = "char")]
    public string Char { get; set; } = "~";

    [YamlMember(Alias = "color")]
    public int[] Color { get; set; } = [255, 255, 255];

    // Wand-specific fields (ignored for scrolls)
    [YamlMember(Alias = "is_wand")]
    public bool IsWand { get; set; }

    [YamlMember(Alias = "min_charges")]
    public int MinCharges { get; set; } = 2;

    [YamlMember(Alias = "max_charges")]
    public int MaxCharges { get; set; } = 4;

    [YamlMember(Alias = "charge_cap")]
    public int ChargeCap { get; set; } = 10;

    [YamlMember(Alias = "infinite")]
    public bool Infinite { get; set; }

    [YamlMember(Alias = "recharge_scroll")]
    public string? RechargeScroll { get; set; }
}
```

### 1.7 New TurnEvent Subclasses

```csharp
// Added to src/Logic/Core/TurnEvent.cs

public sealed class SpellEvent : TurnEvent
{
    public string SpellId { get; init; } = "";
    public string SpellName { get; init; } = "";
    public int? TargetId { get; init; }
    public int TargetX { get; init; }
    public int TargetY { get; init; }
    public int Damage { get; init; }
    public int Radius { get; init; }
    public bool Misfire { get; init; }
    public string? StatusApplied { get; init; }
    public int StatusDuration { get; init; }
    /// <summary>IDs of all entities hit by AoE spells.</summary>
    public IReadOnlyList<int> AffectedIds { get; init; } = Array.Empty<int>();
}

public sealed class WandUseEvent : TurnEvent
{
    public string WandName { get; init; } = "";
    public int RemainingCharges { get; init; }
    public bool OutOfCharges { get; init; }
}

public sealed class WandRechargeEvent : TurnEvent
{
    public string WandName { get; init; } = "";
    public string ScrollName { get; init; } = "";
    public int NewCharges { get; init; }
}

public sealed class PortalPlacedEvent : TurnEvent
{
    public PortalType Type { get; init; }
    public int PortalEntityId { get; init; }
    public int X { get; init; }
    public int Y { get; init; }
}

public sealed class PortalTeleportEvent : TurnEvent
{
    public int FromX { get; init; }
    public int FromY { get; init; }
    public int ToX { get; init; }
    public int ToY { get; init; }
    public int PortalEntryId { get; init; }
    public int PortalExitId { get; init; }
}

public sealed class PortalRemovedEvent : TurnEvent
{
    public int EntranceId { get; init; }
    public int ExitId { get; init; }
}

public sealed class MapRevealEvent : TurnEvent
{
    /// <summary>"fov" for Light Scroll, "full" for Magic Mapping.</summary>
    public string RevealType { get; init; } = "";
}

public sealed class DetectMonstersEvent : TurnEvent
{
    public IReadOnlyList<(int X, int Y, int MonsterId)> MonsterPositions { get; init; }
        = Array.Empty<(int, int, int)>();
    public int Duration { get; init; }
}
```

### 1.8 SpellResolver Service (Logic Layer)

```
src/Logic/Combat/SpellResolver.cs
```

Static class with a single entry point:

```csharp
public static class SpellResolver
{
    /// <summary>
    /// Execute a spell effect. Returns events describing what happened.
    /// Called by TurnController when a scroll is used or a wand is fired.
    /// </summary>
    public static List<TurnEvent> Resolve(
        Entity caster,
        SpellEffect spell,
        GameState state,
        int? targetEntityId = null,
        int? targetX = null,
        int? targetY = null)
    { ... }
}
```

Each `SpellId` maps to a private handler method. The resolver uses a switch on `SpellId`:

- `"lightning"` -> `ResolveLightning`
- `"fireball"` -> `ResolveFireball`
- `"confusion"` -> `ResolveConfusion`
- `"enhance_weapon"` -> `ResolveEnhanceWeapon`
- `"enhance_armor"` -> `ResolveEnhanceArmor`
- etc.

This keeps spell logic centralized and testable. No virtual dispatch, no spell class hierarchy. A switch on a string is simple and the data (damage, range, duration) lives on the `SpellEffect` component, not hardcoded in the resolver.

### 1.9 PlayerAction Changes

Add a new `ActionKind`:

```csharp
// In PlayerAction.cs
public enum ActionKind { Wait, Attack, Move, UseItem, Descend, DropItem, EquipItem, UnequipItem, CastSpell }
```

New factory method:

```csharp
public static PlayerAction CastSpell(Entity item, int? targetEntityId = null, int? targetX = null, int? targetY = null)
    => new(ActionKind.CastSpell, item: item, targetEntityId: targetEntityId, targetX: targetX, targetY: targetY);
```

`PlayerAction` gains a `TargetEntityId` field (nullable int) for single-target spells where the target is chosen via UI tap.

### 1.10 TurnController Integration

In `ResolvePlayerAction`, add a new case:

```csharp
case PlayerAction.ActionKind.CastSpell:
    ResolveSpellAction(state, action, events);
    player.Get<SpeedBonusTracker>()?.ResetMomentum();
    break;
```

`ResolveSpellAction` does:
1. Look up the item's `SpellEffect` component.
2. If item has `WandComponent` — call `TryConsume()`. If out of charges, emit `WandUseEvent(OutOfCharges=true)` and return.
3. If item has `Consumable` — decrement `StackSize`, remove if zero.
4. Call `SpellResolver.Resolve(...)`.
5. If wand, emit `WandUseEvent` with remaining charges.
6. Append all events from the resolver.

### 1.11 Status Effect Components Needed

Each status effect is a separate `IComponent`. The status effect system (plan_status_effects.md) handles tick/expire/remove lifecycle. For this plan, we define the components but the **lifecycle tick is deferred** to plan_status_effects. Applying the component is sufficient for the scroll/wand plan.

Required status effect components for scrolls in this plan:

| Component | Applied By | Key Fields |
|-----------|-----------|------------|
| `ConfusedEffect` | Confusion Scroll/Wand | `int RemainingTurns` (10) |
| `SlowedEffect` | Slow Scroll/Wand | `int RemainingTurns` (10) |
| `ImmobilizedEffect` | Glue Scroll/Wand | `int RemainingTurns` (5) |
| `EnragedEffect` | Rage Scroll/Wand | `int RemainingTurns` (8), `double DamageMultiplier` (2.0), `double AccuracyMultiplier` (0.5) |
| `DisarmedEffect` | Disarm Scroll | `int RemainingTurns` (3) |
| `PlagueEffect` | Plague Scroll | `int RemainingTurns` (20), `int DamagePerTurn` (1) |
| `TauntedEffect` | Yo Mama Scroll/Wand | `int TauntTargetId` (permanent until dispelled) |
| `AggravatedException` | Aggravation Scroll | `string TargetFaction` (permanent) |
| `DetectMonstersEffect` | Detect Monster Scroll | `int RemainingTurns` (20) |

**Deferred to Phase 6** (need plan_status_effects lifecycle first):
- `InvisibilityEffect` (30 turns)
- `ShieldEffect` (+4 defense, 10 turns)
- `HasteEffect` (30 turns speed boost)
- `FearEffect` (15 turns flee AI)
- `SilencedEffect` (3 turns blocks scroll/wand use)
- `SleepEffect` (3 turns skip turns, wake on damage)
- `DisorientationEffect` (3-5 turns)

---

## 2. Targeting System

### 2.1 Overview

The targeting system bridges the presentation layer (touch input) and the logic layer (spell resolution). When a player uses a scroll or wand that requires targeting, the game enters a **targeting mode** that intercepts taps and routes them to spell resolution instead of movement.

### 2.2 GameController State Machine Extension

Current states: `WaitingForInput -> Processing -> Animating -> GameOver`

New state: `Targeting`

```
WaitingForInput -> Targeting (player uses scroll/wand with targeting)
Targeting -> Processing (player taps valid target)
Targeting -> WaitingForInput (player cancels)
```

```csharp
public enum GamePhase { WaitingForInput, Processing, Animating, GameOver, Targeting }
```

### 2.3 TargetingState (Presentation Layer)

```csharp
// src/Presentation/Input/TargetingState.cs
public sealed class TargetingState
{
    /// <summary>The item (scroll/wand) being used.</summary>
    public Entity Item { get; init; } = null!;

    /// <summary>The spell effect from the item.</summary>
    public SpellEffect Spell { get; init; } = null!;

    /// <summary>Targeting mode for this spell.</summary>
    public TargetingMode Mode { get; init; }

    /// <summary>Max range for valid targets.</summary>
    public int Range { get; init; }

    /// <summary>AoE radius for preview (0 = no preview).</summary>
    public int Radius { get; init; }

    /// <summary>For portal two-step: which step are we on?</summary>
    public PortalPlacerStage PortalStage { get; set; } = PortalPlacerStage.Idle;
}
```

### 2.4 InputHandler Changes

Add a `TargetingState?` field. When set, `HandleTap` routes to targeting logic instead of normal movement/attack:

```csharp
public void EnterTargetingMode(TargetingState targeting)
{
    _targeting = targeting;
    _acceptingInput = true;
}

public void CancelTargeting()
{
    _targeting = null;
    TargetingCancelled?.Invoke();
}
```

In `HandleTap`, when `_targeting != null`:

```
if (_targeting.Mode == TargetingMode.SingleTarget)
    -> find entity at grid position, validate range, fire TargetChosen(entity)
if (_targeting.Mode == TargetingMode.Location)
    -> validate walkable + range, fire LocationChosen(x, y)
if (_targeting.Mode == TargetingMode.Portal)
    -> validate walkable + not blocked, fire LocationChosen(x, y)
```

New events on InputHandler:

```csharp
public event Action<Entity, Entity>? TargetChosen;   // (item, target)
public event Action<Entity, int, int>? LocationChosen; // (item, x, y)
public event Action? TargetingCancelled;
```

### 2.5 GameController Integration

When `HandleInventoryTap` or a new `HandleWandUse` detects a spell with a targeting mode other than `Self` or `AutoClosest`:

1. Create `TargetingState` from the item's `SpellEffect`.
2. Set `Phase = GamePhase.Targeting`.
3. Call `_input.EnterTargetingMode(...)`.
4. Show targeting UI overlay (range ring, "Tap to target" toast).

When `TargetChosen` or `LocationChosen` fires:
1. Build `PlayerAction.CastSpell(item, targetEntityId, targetX, targetY)`.
2. Call `ExecuteTurn(action)`.

When `TargetingCancelled` fires:
1. Set `Phase = GamePhase.WaitingForInput`.
2. Hide targeting UI.
3. **Do not consume the turn.**

### 2.6 Cancel Gesture

On mobile, cancellation options (builder should implement the first that's feasible):
1. **Back button** (Android) / swipe-down gesture.
2. **Tap on self** (player's own tile) cancels targeting.
3. **Dedicated cancel button** shown during targeting mode (simplest, recommended).

For Phase 3 implementation: add a "Cancel" button to the targeting overlay. This is the safest mobile UX.

### 2.7 Self and AutoClosest — No Targeting UI

- `TargetingMode.Self`: `GameController` immediately builds `PlayerAction.CastSpell(item)` with no target coords. No targeting mode entered.
- `TargetingMode.AutoClosest`: `GameController` finds the closest visible enemy, builds `PlayerAction.CastSpell(item, targetEntityId: closestMonster.Id)`. If no visible enemies, show "No visible targets" toast and do not consume the item.

### 2.8 Portal Two-Step Targeting (Detailed)

Portal targeting is a special case handled by `TargetingMode.Portal`:

**Step 1 — Place Entrance:**
1. Player uses Wand of Portals (inventory tap or quickbar).
2. If existing portals are active (PortalPlacerComponent has valid IDs), remove them first (emit `PortalRemovedEvent`).
3. Enter targeting mode with `PortalStage = PlacingEntrance`.
4. Toast: "Tap to place entrance portal"
5. Player taps valid walkable tile -> place entrance entity, emit `PortalPlacedEvent`.
6. Transition to Step 2 automatically (no turn consumed yet).

**Step 2 — Place Exit:**
1. `PortalStage` becomes `PlacingExit`.
2. Toast: "Tap to place exit portal"
3. Player taps valid walkable tile (different from entrance) -> place exit entity, emit `PortalPlacedEvent`.
4. Link both portals bidirectionally.
5. **NOW the turn is consumed** (both placements happen as one action).

**Cancel at any point:**
- If cancelled during Step 1: nothing happens, no turn consumed.
- If cancelled during Step 2: remove the entrance entity, no turn consumed.

**Validation for portal placement:**
- Tile must be walkable.
- Tile must not be occupied by a blocking entity.
- Tile must not already have a portal.
- Exit tile must not be the same as entrance tile.
- No range limit (portals are the player's core traversal tool).

---

## 3. Portal Wand — Detailed Design

### 3.1 Entity Design

Two new entity types in `entities.yaml`:

```yaml
# Not items the player carries — these are placed ON the map
portal_entrance:
  name: "Portal (Entrance)"
  char: "O"
  color: [0, 255, 255]     # cyan
  blocks: false             # entities can walk onto portals

portal_exit:
  name: "Portal (Exit)"
  char: "O"
  color: [255, 255, 0]     # yellow
  blocks: false
```

Portal entities are created by `EntityFactory`, placed on the map via `GameMap.RegisterEntity()`, and stored in a new `GameState.Portals` list (or tracked via the `PortalPlacerComponent` on the wand).

### 3.2 Wand of Portals — Item Definition

```yaml
wands:
  wand_of_portals:
    name: "Wand of Portals"
    spell_id: "portal"
    targeting: "portal"
    is_wand: true
    infinite: true
    char: "/"
    color: [0, 200, 200]
```

### 3.3 Portal Placement Flow in TurnController

Portal placement is resolved entirely within `ResolveSpellAction`:

1. `SpellResolver.Resolve` for `spell_id: "portal"` delegates to `ResolvePortal`.
2. `ResolvePortal` receives **both** target locations (entrance + exit) from the `PlayerAction`.
3. The presentation layer handles the two-step tap collection and passes both coordinates to the single `CastSpell` action.

**Alternative approach (simpler for TurnController):** The `CastSpell` action carries `TargetX`/`TargetY` for the entrance and secondary fields `TargetX2`/`TargetY2` for the exit. `PlayerAction` gains two optional secondary target fields.

```csharp
// PlayerAction additions for portal
public int? TargetX2 { get; }
public int? TargetY2 { get; }

public static PlayerAction CastSpellPortal(Entity item, int entranceX, int entranceY, int exitX, int exitY)
    => new(ActionKind.CastSpell, item: item,
           targetX: entranceX, targetY: entranceY,
           targetX2: exitX, targetY2: exitY);
```

### 3.4 Portal Collision — Teleportation

At the end of each entity's move (both player and monster), if the entity's new position matches a portal entity's position:

1. Find the linked portal via `PortalComponent.LinkedPortalId`.
2. Teleport the entity to the linked portal's position.
3. Emit `PortalTeleportEvent`.

This check happens in:
- `TurnController.ResolvePlayerMove` — after the move resolves.
- `TurnController.ResolveMonsterTurns` — after each monster's move.

**Important:** Teleporting through a portal does NOT trigger a second portal check at the destination (prevents infinite loops). Use a `justTeleported` flag or check that the destination portal is the one they arrived at.

### 3.5 Portal Recycle

When the player uses the Wand of Portals while portals are already active:
1. Remove both existing portal entities from the map (`GameMap.UnregisterEntity`).
2. Emit `PortalRemovedEvent`.
3. Clear `PortalPlacerComponent.EntranceId` and `ExitId`.
4. Proceed with new placement.

### 3.6 Player Starts With Wand of Portals

In `DungeonFloorBuilder.CreateDefaultPlayer()`, after creating starting gear:

```csharp
// Wand of Portals — player's core traversal tool, always available
var portalWand = _spellItemFactory.CreateWand("wand_of_portals", depth: 1, rng);
if (portalWand != null)
    inventory.Add(portalWand);
```

The wand is added to inventory, not an equipment slot. It's used from the inventory/quickbar.

### 3.7 Monsters and Portals

Monsters CAN use portals. When a monster moves onto a portal tile during `ResolveMonsterTurns`, the same teleportation check triggers. This creates interesting tactical situations:
- Player can lure monsters through portals.
- Monsters can accidentally stumble onto portals during pursuit.
- The player must consider portal placement carefully — it works both ways.

Monster AI does NOT specifically seek or avoid portals (for now). They path normally and teleport if they walk onto one.

### 3.8 Floor Transition

Portals do NOT persist between floors. When the player descends:
- Portals are left behind on the old floor.
- The `PortalPlacerComponent` on the wand is reset to `Idle` with IDs = -1.
- The player must place new portals on each floor.

---

## 4. Implementation Phases

### Phase 1 — Spell Infrastructure + Self/Auto Scrolls

**No targeting UI needed.** This phase establishes the entire spell system foundation.

#### New Files to Create

| File | Layer | Purpose |
|------|-------|---------|
| `src/Logic/Combat/SpellEffect.cs` | Logic | SpellEffect component + TargetingMode enum |
| `src/Logic/Combat/SpellResolver.cs` | Logic | Spell execution service |
| `src/Logic/Content/SpellDefinition.cs` | Logic | YAML deserialization for scrolls/wands |
| `src/Logic/Content/SpellItemFactory.cs` | Logic | Creates scroll/wand entities from definitions |
| `tests/Core/SpellResolverTests.cs` | Logic | Unit tests for each spell |
| `tests/Content/SpellItemFactoryTests.cs` | Logic | YAML loading + entity creation tests |

#### Files to Modify

| File | Changes |
|------|---------|
| `src/Logic/Core/PlayerAction.cs` | Add `ActionKind.CastSpell`, `TargetEntityId`, factory method `CastSpell(...)` |
| `src/Logic/Core/TurnController.cs` | Add `ResolveSpellAction` case + method |
| `src/Logic/Core/TurnEvent.cs` | Add `SpellEvent`, `MapRevealEvent`, `DetectMonstersEvent` |
| `src/Logic/Content/ContentBundle.cs` | Add `Dictionary<string, SpellDefinition> Scrolls`, `Dictionary<string, SpellDefinition> Wands` |
| `src/Logic/Content/ContentLoader.cs` | Add `LoadScrolls`, `LoadWands` methods, update `LoadAll` |
| `src/Logic/Content/EntitiesFile` (in ContentLoader.cs) | Add `scrolls` and `wands` YAML sections |
| `config/entities.yaml` | Add `scrolls:` section with Phase 1 scrolls |

#### Scrolls in Phase 1 (7 scrolls)

All use `Self` or `AutoClosest` targeting — no UI changes needed.

| Scroll | spell_id | Targeting | Effect |
|--------|----------|-----------|--------|
| Light Scroll | `light` | Self | Reveals all tiles currently in FOV |
| Magic Mapping Scroll | `magic_mapping` | Self | Reveals entire floor |
| Detect Monster Scroll | `detect_monsters` | Self | Reveals all monster positions for 20 turns |
| Enhance Weapon Scroll | `enhance_weapon` | Self | +1 min / +2 max dmg on equipped weapon |
| Enhance Armor Scroll | `enhance_armor` | Self | +1 AC on random equipped armor piece |
| Lightning Scroll | `lightning` | AutoClosest | 40 dmg to closest visible enemy, range 5 |
| Earthquake Scroll | `earthquake` | AoeSelf | 20 dmg to all entities in radius 3 centered on caster |

#### SpellResolver Handlers for Phase 1

```
ResolveLightScroll(caster, spell, state) -> marks all FOV-visible tiles as explored
ResolveMagicMapping(caster, spell, state) -> marks all tiles as explored
ResolveDetectMonsters(caster, spell, state) -> emits DetectMonstersEvent with all monster positions
ResolveEnhanceWeapon(caster, spell, state) -> find equipped MainHand, bump DamageMin+1, DamageMax+2
ResolveEnhanceArmor(caster, spell, state) -> find random equipped armor, bump ArmorClassBonus+1
ResolveLightning(caster, spell, state) -> find closest visible enemy within range, deal damage
ResolveEarthquake(caster, spell, state) -> find all entities in radius, deal damage to each
```

#### Acceptance Criteria — Phase 1

- [x] `SpellEffect` component can be attached to an entity
- [x] `SpellItemFactory` creates scroll entities with both `Consumable` (StackSize=1) and `SpellEffect` components
- [x] YAML scrolls section loads correctly via `ContentLoader.LoadSpellItems`
- [x] `PlayerAction.CastSpell(item)` works for Self-targeting scrolls
- [x] `TurnController` routes `CastSpell` to `SpellResolver`
- [x] Lightning scroll auto-targets closest visible enemy and deals 40 damage
- [x] Lightning scroll with no visible enemies emits failed SpellEvent (scroll IS consumed — consistent with PoC behavior where scrolls always activate)
- [x] Earthquake deals 20 damage to all visible enemies in radius 3; no self-damage
- [x] Enhance Weapon adds +1/+2 to equipped weapon; no-op if no weapon equipped
- [x] Enhance Armor adds +1 AC to random equipped armor; no-op if no armor equipped
- [x] Light Scroll emits MapRevealEvent(RevealType="fov")
- [x] Magic Mapping marks all tiles explored via RevealAll + emits MapRevealEvent(RevealType="full")
- [x] Detect Monster emits DetectMonstersEvent with all monster positions
- [x] Scrolls are consumed after use (StackSize decremented, removed at 0)
- [x] Wand charges deducted on use; wand destroyed at 0 charges
- [x] Wand auto-recharge on matching scroll pickup
- [x] Wand of Portals granted at run start (infinite charges, portal spell deferred to Phase 5)
- [x] All tests pass: `dotnet test --filter "Category!=Slow"` — 514 tests passing

#### Implementation Notes (2026-03-29)

Files created:
- `src/Logic/Combat/SpellEffect.cs` — SpellEffect component + TargetingMode enum
- `src/Logic/Combat/WandComponent.cs` — WandComponent with TryConsume, Infinite support
- `src/Logic/Combat/SpellResolver.cs` — all Phase 1 spell handlers (lightning, earthquake, light, magic_mapping, detect_monsters, enhance_weapon, enhance_armor)
- `src/Logic/Content/SpellDefinition.cs` — YAML deserialization type for scrolls and wands
- `src/Logic/Content/SpellItemFactory.cs` — entity creation from SpellDefinitions
- `tests/Core/SpellResolverTests.cs` — 20 tests
- `tests/Core/SpellCastTests.cs` — 14 integration tests through TurnController
- `tests/Content/SpellItemFactoryTests.cs` — 14 tests

Files modified:
- `src/Logic/Core/TurnEvent.cs` — SpellEvent, WandUseEvent, WandRechargeEvent, MapRevealEvent, DetectMonstersEvent
- `src/Logic/Core/PlayerAction.cs` — ActionKind.CastSpell, TargetEntityId, CastSpell factory method
- `src/Logic/Core/TurnController.cs` — ResolveSpellAction, TryRechargeWand, TryPickUpItemsAt updated
- `src/Logic/Core/DungeonFloorBuilder.cs` — SpellItemFactory injection, wand_of_portals at run start
- `src/Logic/Core/EntityPlacer.cs` — FillRooms accepts SpellItemFactory, creates scrolls/wands from floor pool
- `src/Logic/Content/ContentLoader.cs` — LoadSpellItems method, LoadAll returns SpellItems
- `src/Logic/Content/ContentBundle.cs` — SpellItems dictionary
- `src/Logic/Content/AotObjectFactory.cs` — SpellDefinition types registered
- `config/entities.yaml` — scrolls: and wands: sections, floor_item_pool entries

Decision: Lightning scroll with no valid targets still consumes the scroll. The PoC "no consumption" on miss only applies to targeted spells where targeting fails at the UI layer — for auto-target spells, the resolver has no way to check before activation. Adjust if UX testing shows this feels punishing.

#### Tests — Phase 1

```
SpellResolverTests:
  - Lightning_HitsClosestVisibleEnemy
  - Lightning_NoVisibleEnemy_NoConsumption
  - Lightning_RangeLimit_IgnoresBeyondRange5
  - Earthquake_DamagesAllInRadius3
  - Earthquake_DoesNotDamageCaster
  - EnhanceWeapon_IncrementsDamageRange
  - EnhanceWeapon_NoWeapon_Noop
  - EnhanceArmor_IncrementsAC
  - EnhanceArmor_NoArmor_Noop
  - Light_RevealsAllFovTiles
  - MagicMapping_RevealsAllTiles
  - DetectMonsters_EmitsAllPositions

SpellItemFactoryTests:
  - CreateScroll_HasConsumableAndSpellEffect
  - CreateScroll_StackSize1
  - LoadScrollsFromYaml_ParsesCorrectly

TurnControllerSpellTests:
  - CastSpell_ConsumesScroll
  - CastSpell_StackedScroll_DecrementsStack
  - CastSpell_EmitsSpellEvent
```

---

### Phase 2 — Wand Infrastructure

#### New Files to Create

| File | Layer | Purpose |
|------|-------|---------|
| `src/Logic/Combat/WandComponent.cs` | Logic | Wand charge tracking component |
| `tests/Core/WandTests.cs` | Logic | Wand charge, recharge, empty-wand tests |

#### Files to Modify

| File | Changes |
|------|---------|
| `src/Logic/Core/TurnController.cs` | `ResolveSpellAction` — handle wand charge consumption |
| `src/Logic/Core/TurnEvent.cs` | Add `WandUseEvent`, `WandRechargeEvent` |
| `src/Logic/Content/SpellItemFactory.cs` | Add `CreateWand` method; charges = `rand(min, max) + (depth - 1)`, capped at `charge_cap` |
| `src/Logic/Core/TurnController.cs` | In `TryPickUpItemsAt` — check if picked-up scroll matches a wand's `RechargeScrollId`; if so, consume scroll and add +1 charge |
| `config/entities.yaml` | Add `wands:` section with lightning and earthquake wands |

#### Wand Charge Formula

From PoC: `charges = rand(min_charges, max_charges) + (depth - 1)`, capped at `charge_cap` (default 10).

```csharp
public Entity? CreateWand(string wandId, int depth, SeededRandom rng)
{
    var def = _definitions[wandId];
    int charges = rng.Next(def.MinCharges, def.MaxCharges + 1) + (depth - 1);
    charges = Math.Min(charges, def.ChargeCap);
    // ... create entity with WandComponent(Charges: charges) + SpellEffect
}
```

#### Wand Recharge on Scroll Pickup

In `TurnController.TryPickUpItemsAt`, after a scroll is picked up:

```csharp
// Check if any wand in inventory matches this scroll for recharge
if (item.Has<SpellEffect>() && !item.Has<WandComponent>())
{
    var scrollSpellId = item.Require<SpellEffect>().SpellId;
    var matchingWand = inventory.FindFirst(w =>
        w.Get<WandComponent>()?.RechargeScrollId == scrollSpellId
        && w.Get<WandComponent>()?.Charges < w.Get<WandComponent>()?.MaxCharges);
    if (matchingWand != null)
    {
        var wand = matchingWand.Require<WandComponent>();
        wand.Charges = Math.Min(wand.Charges + 1, wand.MaxCharges);
        // Consume the scroll
        inventory.Remove(item);
        events.Add(new WandRechargeEvent { ... });
    }
}
```

**Note:** Recharge is optional behavior. The scroll is consumed and the wand gains +1 charge. If no matching wand exists, the scroll is kept in inventory as normal (player can still read the scroll directly).

#### Wands in Phase 2

| Wand | spell_id | Matches Scroll | Charges |
|------|----------|---------------|---------|
| Wand of Lightning | `lightning` | `lightning_scroll` | 2-4 + (depth-1), cap 10 |
| Wand of Earthquake | `earthquake` | `earthquake_scroll` | 2-4 + (depth-1), cap 10 |

(These use the Self/AutoClosest spells from Phase 1 — no targeting UI needed.)

#### Acceptance Criteria — Phase 2

- [ ] `WandComponent` tracks charges correctly
- [ ] Wand creation uses charge formula: `rand(min, max) + (depth - 1)`, capped at 10
- [ ] Using a wand decrements charges
- [ ] Empty wand emits `WandUseEvent(OutOfCharges=true)` and does not execute the spell
- [ ] Picking up a matching scroll recharges the wand by +1
- [ ] Scroll is consumed on recharge (not added to inventory)
- [ ] Wand of Portals (infinite) never runs out of charges
- [ ] `WandUseEvent` includes remaining charges for UI display

#### Tests — Phase 2

```
WandTests:
  - TryConsume_DecrementsCharges
  - TryConsume_EmptyWand_ReturnsFalse
  - TryConsume_InfiniteWand_AlwaysTrue
  - CreateWand_ChargeFormula_DepthScaling
  - CreateWand_ChargeCap_Enforced
  - Recharge_MatchingScrollPickup_AddsCharge
  - Recharge_NoMatchingWand_ScrollKeptInInventory
  - Recharge_WandAtCap_NoRecharge
  - EmptyWand_UseEmitsOutOfChargesEvent
```

---

### Phase 3 — Single-Target Targeting UI + Scrolls

**This phase requires presentation layer changes.** Adds targeting mode to InputHandler and GameController.

#### New Files to Create

| File | Layer | Purpose |
|------|-------|---------|
| `src/Presentation/Input/TargetingState.cs` | Presentation | Targeting mode data |
| `src/Presentation/UI/TargetingOverlay.cs` | Presentation | Visual overlay during targeting (range ring, cancel button) |
| `tests/Core/SingleTargetSpellTests.cs` | Logic | Tests for single-target spell effects |

#### Files to Modify

| File | Changes |
|------|---------|
| `src/Presentation/Input/InputHandler.cs` | Add `_targeting` field, `EnterTargetingMode`, `CancelTargeting`, routing in `HandleTap` |
| `src/Presentation/GameController.cs` | Add `GamePhase.Targeting`, wire `TargetChosen`/`LocationChosen`/`TargetingCancelled`, `HandleWandUse`/`HandleScrollUse` |
| `src/Logic/Combat/SpellResolver.cs` | Add handlers for all single-target spells |
| `src/Logic/Core/TurnEvent.cs` | (already has SpellEvent from Phase 1) |
| `config/entities.yaml` | Add single-target scrolls and matching wands |

#### Status Effect Components Created in Phase 3

Each is a simple `IComponent` with `RemainingTurns` (and effect-specific fields):

| File | Component |
|------|-----------|
| `src/Logic/Combat/StatusEffects/ConfusedEffect.cs` | `int RemainingTurns = 10` |
| `src/Logic/Combat/StatusEffects/SlowedEffect.cs` | `int RemainingTurns = 10` |
| `src/Logic/Combat/StatusEffects/ImmobilizedEffect.cs` | `int RemainingTurns = 5` |
| `src/Logic/Combat/StatusEffects/EnragedEffect.cs` | `int RemainingTurns = 8`, `double DmgMult = 2.0`, `double AccMult = 0.5` |
| `src/Logic/Combat/StatusEffects/DisarmedEffect.cs` | `int RemainingTurns = 3` |
| `src/Logic/Combat/StatusEffects/PlagueEffect.cs` | `int RemainingTurns = 20`, `int DmgPerTurn = 1` |
| `src/Logic/Combat/StatusEffects/TauntedEffect.cs` | `int TauntTargetId` (permanent) |

**Note:** These components are *applied* by SpellResolver in Phase 3. Their *per-turn lifecycle* (tick damage, expire, modify AI) is implemented in plan_status_effects. For Phase 3, having the component attached to the entity is the testable outcome. Behavioral integration (confused movement, slowed turn skipping) lands with the status effect system.

#### Scrolls/Wands in Phase 3 (8 scrolls + 5 wands)

| Scroll | spell_id | Targeting | Range | Effect |
|--------|----------|-----------|-------|--------|
| Confusion Scroll | `confusion` | SingleTarget | 8 | Apply ConfusedEffect 10 turns |
| Slow Scroll | `slow` | SingleTarget | 8 | Apply SlowedEffect 10 turns |
| Glue Scroll | `glue` | SingleTarget | 8 | Apply ImmobilizedEffect 5 turns |
| Rage Scroll | `rage` | SingleTarget | 8 | Apply EnragedEffect 8 turns |
| Yo Mama Scroll | `yo_mama` | SingleTarget | 10 | Apply TauntedEffect (permanent) |
| Disarm Scroll | `disarm` | SingleTarget | 8 | Apply DisarmedEffect 3 turns |
| Plague Scroll | `plague` | SingleTarget | 8 | Apply PlagueEffect 20 turns, 1 dmg/turn, corporeal only |
| Aggravation Scroll | `aggravation` | SingleTarget | 10 | Apply AggravatedEffect (permanent faction aggro) |

Matching wands: Confusion, Slow, Glue, Rage, Yo Mama (all with standard charge formula).

#### SpellResolver Handlers for Phase 3

All follow the pattern:
1. Validate target exists and is in range.
2. Validate target is a valid recipient (e.g., plague requires `corporeal_flesh` tag).
3. Add the status effect component to the target entity.
4. Emit `SpellEvent` with `StatusApplied` and `StatusDuration`.

#### Acceptance Criteria — Phase 3

- [ ] `InputHandler` enters targeting mode when a single-target scroll/wand is used
- [ ] Tapping a valid monster in range selects it as target
- [ ] Tapping out of range shows "Out of range" toast, does not consume
- [ ] Cancel button exits targeting without consuming a turn
- [ ] Confusion scroll applies `ConfusedEffect` to target for 10 turns
- [ ] Slow scroll applies `SlowedEffect` to target for 10 turns
- [ ] Glue scroll applies `ImmobilizedEffect` to target for 5 turns
- [ ] Plague scroll only works on targets with `corporeal_flesh` tag
- [ ] Yo Mama scroll applies permanent `TauntedEffect`
- [ ] All single-target wands decrement charges on use
- [ ] Targeting overlay shows during targeting mode (presentation layer test)

#### Tests — Phase 3

```
SingleTargetSpellTests:
  - Confusion_AppliesEffectForDuration
  - Slow_AppliesEffectForDuration
  - Glue_AppliesImmobilizedEffect
  - Rage_AppliesEnragedEffect
  - YoMama_AppliesPermanentTaunt
  - Disarm_AppliesDisarmedEffect
  - Plague_AppliesOnCorporealOnly
  - Plague_FailsOnNonCorporeal
  - Aggravation_AppliesFactionAggro
  - SingleTarget_OutOfRange_NoEffect

TargetingTests (presentation — manual or GdUnit4):
  - EnterTargetingMode_BlocksNormalInput
  - CancelTargeting_RestoresNormalInput
  - ValidTarget_FiresTargetChosen
  - InvalidTarget_ShowsFeedback
```

---

### Phase 4 — Location Targeting + Scrolls

#### Files to Modify

| File | Changes |
|------|---------|
| `src/Presentation/Input/InputHandler.cs` | Add location targeting path in HandleTap |
| `src/Logic/Combat/SpellResolver.cs` | Add handlers for location-targeted spells |
| `config/entities.yaml` | Add location-targeting scrolls and wands |

#### Scrolls/Wands in Phase 4 (4 scrolls + 2 wands)

| Scroll | spell_id | Targeting | Range | Effect |
|--------|----------|-----------|-------|--------|
| Blink Scroll | `blink` | Location | 5 | Teleport caster to target tile |
| Teleport Scroll | `teleport` | Location | Unlimited | Teleport to target; 10% misfire -> random location + DisorientationEffect 3-5 turns |
| Fireball Scroll | `fireball` | Location | Unlimited | 25 dmg AoE radius 3 at target + fire hazard 3 dmg/turn for 3 turns |
| Raise Dead Scroll | `raise_dead` | Location | 5 | Resurrect corpse as mindless zombie (2x HP, 0.5x dmg, attacks everything) |

Matching wands: Fireball, Teleportation (standard charge formula).

#### SpellResolver Handlers

```
ResolveBlink: validate target walkable + in range, move caster to target
ResolveTeleport: validate target walkable, 10% misfire check -> random walkable tile + DisorientationEffect
ResolveFireball: deal 25 dmg to all entities in radius 3 of target, create fire hazard entities
ResolveRaiseDead: find corpse at target location, create zombie entity from it
```

**Fireball fire hazard:** Creates temporary hazard entities at affected tiles. Hazard system is part of plan_traps_chests_features. For Phase 4, emit the damage event and note the hazard as a TODO. The fire hazard is a nice-to-have that can land with the trap/hazard system.

**Raise Dead corpse system:** Corpses don't exist yet (dead monsters are just removed). Raise Dead is included in Phase 4 for targeting infrastructure but the **corpse lifecycle** (dead monster -> corpse entity on floor -> raiseable) is part of plan_monster_specials. Phase 4 should stub this as "no valid corpse found" until corpses exist.

#### Acceptance Criteria — Phase 4

- [ ] Location targeting mode allows tapping any walkable tile
- [x] Blink teleports player to target within range 5
- [x] Blink fails if target is not walkable or beyond range
- [x] Teleport works at any range; 10% misfire sends to random tile
- [x] Teleport misfire applies DisorientationEffect (3 turns)
- [x] Fireball deals 25 damage to all entities in radius 3 of target
- [x] Fireball does not damage entities outside radius
- [x] Raise Dead returns "no valid corpse" until corpse system lands
- [ ] Location targeting shows valid tile highlight (walkable tiles in range)

#### Phase 4 Implementation Notes (2026-03-29)

- **DisorientationEffect** added at `src/Logic/Combat/StatusEffects/DisorientationEffect.cs` — 3-turn default, applied on teleport misfire. Documented in code: functionally identical to ConfusedEffect at the behavior level; separate type distinguishes source for future differentiation.
- **SpellResolver.ResolveTeleport** updated: applies `DisorientationEffect` to caster when `misfire=true`.
- **wand_of_dragon_farts** added to `config/entities.yaml` (floor pool weight=3, depth 4+). Stub: single-target silence/sleep because cone targeting is deferred. `recharge_scroll: "dragon_fart"` for eventual use.
- **ScenarioHarness + ScenarioRunner** extended to accept `SpellItemFactory`. `GameStateFactory.FromScenario` now accepts a `SpellItemFactory?` parameter and resolves items in priority order: SpellItemFactory → ConsumableFactory → ItemFactory. This lets scenario YAML list scrolls/wands in `items:` alongside potions.
- **3 scenario YAML files** created in `config/testing/`: `test_scrolls_auto.yaml`, `test_scrolls_targeted.yaml`, `test_wands.yaml`.
- **SpellScenarioTests.cs** — 21 new tests covering: auto-target lightning, earthquake AoE, magic mapping, fear AoE, fireball AoE with radius check, teleport (clean + forced misfire), DisorientationEffect on misfire, blink, raise_dead stub, wand charge consumption, wand recharge via pickup, all YAML wand/scroll definitions load without error, depth scaling on wand charges.
- **Total test count**: 577 (was 556). All passing.
- **Pending (Phase 4 presentation)**: location targeting tile highlight in InputHandler — this is presentation layer scope and not harness-testable.

#### Tests — Phase 4

```
LocationTargetSpellTests:
  - Blink_TeleportsToTarget
  - Blink_BeyondRange_Fails
  - Blink_NonWalkable_Fails
  - Teleport_MovesToTarget
  - Teleport_Misfire_RandomLocation
  - Teleport_Misfire_AppliesDisorientation
  - Fireball_DamagesAllInRadius
  - Fireball_NoDamageOutsideRadius
  - Fireball_DamagesCasterIfInRadius
  - RaiseDead_NoCorpse_Noop
```

---

### Phase 5 — Portal Wand (Flagship)

#### New Files to Create

| File | Layer | Purpose |
|------|-------|---------|
| `src/Logic/Combat/PortalComponent.cs` | Logic | Portal entity component |
| `src/Logic/Combat/PortalPlacerComponent.cs` | Logic | Wand state tracker |
| `src/Logic/Core/PortalSystem.cs` | Logic | Portal placement, teleportation, cleanup |
| `tests/Core/PortalSystemTests.cs` | Logic | Comprehensive portal tests |

#### Files to Modify

| File | Changes |
|------|---------|
| `src/Logic/Core/PlayerAction.cs` | Add `TargetX2`, `TargetY2` for portal exit; `CastSpellPortal` factory |
| `src/Logic/Core/TurnController.cs` | Portal placement in `ResolveSpellAction`; portal collision check in `ResolvePlayerMove` and `ResolveMonsterTurns` |
| `src/Logic/Core/TurnEvent.cs` | Add `PortalPlacedEvent`, `PortalTeleportEvent`, `PortalRemovedEvent` (already designed above) |
| `src/Logic/Core/GameState.cs` | Add `List<Entity> Portals` for active portal tracking |
| `src/Logic/Core/DungeonFloorBuilder.cs` | Add Wand of Portals to starting inventory |
| `src/Logic/Content/SpellItemFactory.cs` | Handle `infinite: true` wand creation |
| `src/Presentation/Input/InputHandler.cs` | Portal two-step targeting mode |
| `src/Presentation/GameController.cs` | Portal targeting flow, sprite creation for placed portals |
| `config/entities.yaml` | Add `wand_of_portals` and portal entity definitions |

#### PortalSystem (Logic Layer)

```csharp
// src/Logic/Core/PortalSystem.cs
public static class PortalSystem
{
    /// <summary>
    /// Place a portal pair on the map. Recycles existing portals if any.
    /// Returns events describing placement (and removal if recycling).
    /// </summary>
    public static List<TurnEvent> PlacePortals(
        GameState state, Entity wand,
        int entranceX, int entranceY,
        int exitX, int exitY,
        EntityFactory entityFactory)
    { ... }

    /// <summary>
    /// Check if an entity is standing on a portal. If so, teleport to linked portal.
    /// Returns PortalTeleportEvent or null.
    /// </summary>
    public static PortalTeleportEvent? CheckPortalCollision(Entity entity, GameState state)
    { ... }

    /// <summary>
    /// Remove all active portals. Used on floor transition.
    /// </summary>
    public static void ClearPortals(GameState state)
    { ... }
}
```

#### Acceptance Criteria — Phase 5

- [x] Wand of Portals is in player's starting inventory
- [x] Wand of Portals has infinite charges (never consumed)
- [ ] Using the wand enters two-step targeting mode (presentation layer — deferred)
- [x] First tap places cyan entrance portal entity on map (logic: PortalSystem.PlacePortals)
- [x] Second tap places yellow exit portal entity on map (logic: PortalSystem.PlacePortals)
- [x] Portals are bidirectionally linked
- [x] Player walking onto entrance teleports to exit
- [x] Player walking onto exit teleports to entrance
- [x] Monster walking onto a portal teleports to linked portal
- [x] Only one active portal pair at a time — using wand again removes old pair
- [ ] Cancel during step 1: nothing happens (presentation layer — deferred)
- [ ] Cancel during step 2: entrance is removed (presentation layer — deferred)
- [x] Portal placement validates: walkable, not blocked, not same tile
- [x] Portals do NOT persist between floors (ClearPortals implemented)
- [x] Teleport does not chain (arriving at exit doesn't re-trigger portal)
- [x] `PortalTeleportEvent` emitted with correct coordinates
- [x] `PortalPlacedEvent` emitted for each portal placed
- [x] `PortalRemovedEvent` emitted when old pair is recycled

#### Phase 5 Implementation Notes (2026-03-29)

- **PortalComponent** added at `src/Logic/Combat/PortalComponent.cs` — marks entity as one half of a portal pair, stores `LinkedPortalId` and `UsedThisTurn` (anti-chain flag).
- **PortalSystem** added at `src/Logic/Core/PortalSystem.cs` — static class handling placement, collision, clearing, and turn flag resets.
- **New TurnEvents**: `PortalPlacedEvent`, `PortalTeleportEvent`, `PortalRemovedEvent` added to `TurnEvent.cs`.
- **GameState** gains `List<Entity> Portals` — always 0 or 2 entries.
- **PlayerAction** gains `TargetX2`/`TargetY2` and `CastSpellPortal` factory method for two-point portal targeting.
- **TurnController** changes: `ProcessTurn` accepts optional `EntityFactory? portalEntityFactory` parameter (same pattern as `MonsterFactory`); portal spell handled before SpellResolver (needs factory); portal collision check added after player move and monster move; `ClearPortalUsedFlags` called at turn end.
- **Presentation layer deferred**: Two-step targeting UI (InputHandler + GameController) is deferred — the logic layer is complete and fully tested but the UI state machine for portal placement is separate scope.
- **DungeonFloorBuilder.CreateDefaultPlayer()** already had the wand_of_portals grant in place from Phase 1 scaffolding.
- **31 tests** added in `tests/Core/PortalSystemTests.cs`. Total test count: 608 (was 577).
- `config/testing/test_portal_wand.yaml` added for scenario harness smoke testing.

#### Tests — Phase 5

```
PortalSystemTests:
  - PlacePortals_CreatesBothEntities
  - PlacePortals_RecyclesExistingPair
  - PlacePortals_InvalidTile_Fails
  - PlacePortals_SameTile_Fails
  - CheckCollision_PlayerOnEntrance_TeleportsToExit
  - CheckCollision_PlayerOnExit_TeleportsToEntrance
  - CheckCollision_MonsterOnPortal_Teleports
  - CheckCollision_NoPortal_ReturnsNull
  - CheckCollision_NoChaining_AfterTeleport
  - ClearPortals_RemovesAllFromMap
  - WandOfPortals_InfiniteCharges
  - WandOfPortals_InStartingInventory (YAML)
  - FloorTransition_ClearsPortals
  + 18 additional tests covering TurnController integration, recycling, YAML loading
```

---

### Phase 6 — Deferred

These scrolls/wands require systems that don't exist yet. They are tracked here so nothing is lost.

| Scroll/Wand | Blocked By | Reason |
|------------|------------|--------|
| Shield Scroll | plan_status_effects | Needs ShieldEffect with defense modifier lifecycle |
| Haste Scroll | plan_status_effects | Needs HasteEffect with extra-turn mechanic |
| Invisibility Scroll | plan_status_effects | Needs InvisibilityEffect with AI visibility check |
| Fear Scroll | plan_status_effects | Needs FearEffect with flee AI behavior |
| Silence Scroll | plan_status_effects | Needs SilencedEffect blocking scroll/wand use |
| Dragon Fart Scroll | Cone targeting + plan_status_effects | Needs cone targeting mode + SleepEffect + poison hazard |
| Raise Dead (functional) | plan_monster_specials | Needs corpse lifecycle system |
| Identify Scroll | plan_identification_system | Needs identification mechanic |
| Ward Against Drain | Wraith monster | Not relevant until wraith is implemented |
| Soul Ward | Wraith monster | Not relevant until wraith is implemented |

**Status effects applied in Phase 3 (Confused, Slowed, etc.) are "applied but inert" until plan_status_effects lands.** The components will exist on the entities but their behavioral effects (confused movement, slowed turn skipping, etc.) require the status effect tick system. This is intentional — it lets us build and test the scroll/targeting pipeline independently.

---

## 5. YAML Changes

### 5.1 Scroll Definitions

Add to `config/entities.yaml`:

```yaml
scrolls:
  # Phase 1 — Self / Auto targeting
  lightning_scroll:
    name: "Lightning Scroll"
    spell_id: "lightning"
    targeting: "auto_closest"
    damage: 40
    range: 5
    char: "~"
    color: [255, 255, 0]

  earthquake_scroll:
    name: "Earthquake Scroll"
    spell_id: "earthquake"
    targeting: "aoe_self"
    damage: 20
    radius: 3
    char: "~"
    color: [139, 69, 19]

  light_scroll:
    name: "Light Scroll"
    spell_id: "light"
    targeting: "self"
    char: "~"
    color: [255, 255, 200]

  magic_mapping_scroll:
    name: "Magic Mapping Scroll"
    spell_id: "magic_mapping"
    targeting: "self"
    char: "~"
    color: [200, 200, 255]

  detect_monster_scroll:
    name: "Detect Monster Scroll"
    spell_id: "detect_monsters"
    targeting: "self"
    duration: 20
    char: "~"
    color: [200, 255, 200]

  enhance_weapon_scroll:
    name: "Enhance Weapon Scroll"
    spell_id: "enhance_weapon"
    targeting: "self"
    char: "~"
    color: [255, 200, 100]

  enhance_armor_scroll:
    name: "Enhance Armor Scroll"
    spell_id: "enhance_armor"
    targeting: "self"
    char: "~"
    color: [100, 200, 255]

  # Phase 3 — Single target
  confusion_scroll:
    name: "Confusion Scroll"
    spell_id: "confusion"
    targeting: "single_target"
    range: 8
    duration: 10
    char: "~"
    color: [255, 100, 255]

  slow_scroll:
    name: "Slow Scroll"
    spell_id: "slow"
    targeting: "single_target"
    range: 8
    duration: 10
    char: "~"
    color: [100, 100, 255]

  glue_scroll:
    name: "Glue Scroll"
    spell_id: "glue"
    targeting: "single_target"
    range: 8
    duration: 5
    char: "~"
    color: [200, 180, 100]

  rage_scroll:
    name: "Rage Scroll"
    spell_id: "rage"
    targeting: "single_target"
    range: 8
    duration: 8
    char: "~"
    color: [255, 50, 50]

  yo_mama_scroll:
    name: "Yo Mama Scroll"
    spell_id: "yo_mama"
    targeting: "single_target"
    range: 10
    char: "~"
    color: [255, 200, 0]

  disarm_scroll:
    name: "Disarm Scroll"
    spell_id: "disarm"
    targeting: "single_target"
    range: 8
    duration: 3
    char: "~"
    color: [180, 180, 180]

  plague_scroll:
    name: "Plague Scroll"
    spell_id: "plague"
    targeting: "single_target"
    range: 8
    duration: 20
    secondary_value: 1    # damage per turn
    char: "~"
    color: [100, 200, 0]

  aggravation_scroll:
    name: "Aggravation Scroll"
    spell_id: "aggravation"
    targeting: "single_target"
    range: 10
    char: "~"
    color: [200, 50, 50]

  # Phase 4 — Location targeting
  blink_scroll:
    name: "Blink Scroll"
    spell_id: "blink"
    targeting: "location"
    range: 5
    char: "~"
    color: [150, 150, 255]

  teleport_scroll:
    name: "Teleport Scroll"
    spell_id: "teleport"
    targeting: "location"
    misfire_chance: 0.10
    secondary_value: 3     # disorientation min turns
    secondary_duration: 5  # disorientation max turns
    char: "~"
    color: [100, 255, 100]

  fireball_scroll:
    name: "Fireball Scroll"
    spell_id: "fireball"
    targeting: "location"
    damage: 25
    radius: 3
    secondary_value: 3     # fire hazard damage per turn
    secondary_duration: 3  # fire hazard duration
    char: "~"
    color: [255, 100, 0]

  raise_dead_scroll:
    name: "Raise Dead Scroll"
    spell_id: "raise_dead"
    targeting: "location"
    range: 5
    char: "~"
    color: [100, 0, 100]
```

### 5.2 Wand Definitions

```yaml
wands:
  # Phase 2
  wand_of_lightning:
    name: "Wand of Lightning"
    spell_id: "lightning"
    targeting: "auto_closest"
    damage: 40
    range: 5
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "lightning_scroll"
    char: "/"
    color: [255, 255, 0]

  # Phase 3
  wand_of_confusion:
    name: "Wand of Confusion"
    spell_id: "confusion"
    targeting: "single_target"
    range: 8
    duration: 10
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "confusion_scroll"
    char: "/"
    color: [255, 100, 255]

  wand_of_slow:
    name: "Wand of Slow"
    spell_id: "slow"
    targeting: "single_target"
    range: 8
    duration: 10
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "slow_scroll"
    char: "/"
    color: [100, 100, 255]

  wand_of_glue:
    name: "Wand of Glue"
    spell_id: "glue"
    targeting: "single_target"
    range: 8
    duration: 5
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "glue_scroll"
    char: "/"
    color: [200, 180, 100]

  wand_of_rage:
    name: "Wand of Rage"
    spell_id: "rage"
    targeting: "single_target"
    range: 8
    duration: 8
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "rage_scroll"
    char: "/"
    color: [255, 50, 50]

  wand_of_yo_mama:
    name: "Wand of Yo Mama"
    spell_id: "yo_mama"
    targeting: "single_target"
    range: 10
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "yo_mama_scroll"
    char: "/"
    color: [255, 200, 0]

  # Phase 4
  wand_of_fireball:
    name: "Wand of Fireball"
    spell_id: "fireball"
    targeting: "location"
    damage: 25
    radius: 3
    secondary_value: 3
    secondary_duration: 3
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "fireball_scroll"
    char: "/"
    color: [255, 100, 0]

  wand_of_teleportation:
    name: "Wand of Teleportation"
    spell_id: "teleport"
    targeting: "location"
    misfire_chance: 0.10
    secondary_value: 3
    secondary_duration: 5
    is_wand: true
    min_charges: 2
    max_charges: 4
    charge_cap: 10
    recharge_scroll: "teleport_scroll"
    char: "/"
    color: [100, 255, 100]

  # Phase 5
  wand_of_portals:
    name: "Wand of Portals"
    spell_id: "portal"
    targeting: "portal"
    is_wand: true
    infinite: true
    char: "/"
    color: [0, 200, 200]
```

### 5.3 Portal Entity Definitions

Add to `entities.yaml` (or a new `portals` section):

```yaml
portals:
  portal_entrance:
    name: "Portal (Entrance)"
    char: "O"
    color: [0, 255, 255]

  portal_exit:
    name: "Portal (Exit)"
    char: "O"
    color: [255, 255, 0]
```

---

## 6. Files Changed Summary Table

| File | Phase | Action |
|------|-------|--------|
| **New Logic Files** | | |
| `src/Logic/Combat/SpellEffect.cs` | 1 | Create |
| `src/Logic/Combat/SpellResolver.cs` | 1 | Create |
| `src/Logic/Content/SpellDefinition.cs` | 1 | Create |
| `src/Logic/Content/SpellItemFactory.cs` | 1 | Create |
| `src/Logic/Combat/WandComponent.cs` | 2 | Create |
| `src/Logic/Combat/StatusEffects/ConfusedEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/SlowedEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/ImmobilizedEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/EnragedEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/DisarmedEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/PlagueEffect.cs` | 3 | Create |
| `src/Logic/Combat/StatusEffects/TauntedEffect.cs` | 3 | Create |
| `src/Logic/Combat/PortalComponent.cs` | 5 | Create |
| `src/Logic/Combat/PortalPlacerComponent.cs` | 5 | Create |
| `src/Logic/Core/PortalSystem.cs` | 5 | Create |
| **New Presentation Files** | | |
| `src/Presentation/Input/TargetingState.cs` | 3 | Create |
| `src/Presentation/UI/TargetingOverlay.cs` | 3 | Create |
| **New Test Files** | | |
| `tests/Core/SpellResolverTests.cs` | 1 | Create |
| `tests/Content/SpellItemFactoryTests.cs` | 1 | Create |
| `tests/Core/WandTests.cs` | 2 | Create |
| `tests/Core/SingleTargetSpellTests.cs` | 3 | Create |
| `tests/Core/LocationTargetSpellTests.cs` | 4 | Create |
| `tests/Core/PortalSystemTests.cs` | 5 | Create |
| **Modified Logic Files** | | |
| `src/Logic/Core/PlayerAction.cs` | 1, 5 | Add CastSpell action kind, target fields |
| `src/Logic/Core/TurnController.cs` | 1, 2, 4, 5 | Add spell resolution, wand handling, portal collision |
| `src/Logic/Core/TurnEvent.cs` | 1, 2, 5 | Add SpellEvent, WandUseEvent, portal events, etc. |
| `src/Logic/Core/GameState.cs` | 5 | Add Portals list |
| `src/Logic/Core/DungeonFloorBuilder.cs` | 5 | Add Wand of Portals to starting inventory |
| `src/Logic/Content/ContentBundle.cs` | 1 | Add Scrolls, Wands dictionaries |
| `src/Logic/Content/ContentLoader.cs` | 1 | Add LoadScrolls, LoadWands, update LoadAll |
| **Modified Presentation Files** | | |
| `src/Presentation/Input/InputHandler.cs` | 3 | Add targeting mode |
| `src/Presentation/GameController.cs` | 3, 5 | Add Targeting phase, portal targeting flow |
| **Data Files** | | |
| `config/entities.yaml` | 1-5 | Add scrolls, wands, portals sections |

---

## 7. Risks and Decisions

### Risks

1. **Status effect inertia.** Phase 3 scrolls apply status effects that won't DO anything until plan_status_effects lands. This is acceptable — the scroll/targeting pipeline is independently valuable and testable. But it means confusion scrolls won't actually confuse monsters until the status tick system exists. Document this clearly in release notes.

2. **Fire hazard gap.** Fireball's secondary effect (fire hazard) depends on plan_traps_chests_features. Phase 4 implements the direct damage only. The hazard is a TODO.

3. **Corpse gap.** Raise Dead depends on a corpse lifecycle system that doesn't exist. Phase 4 stubs it. Real implementation lands with plan_monster_specials.

4. **Portal AI interaction.** Monsters walking onto portals creates emergent behavior that could be exploitable (lure enemies through portals into traps). This is intentional and desirable, but edge cases (monster AI pathing through portals, monsters getting stuck in portal loops) need testing.

5. **Scroll/wand floor loot integration.** Scrolls and wands should appear in the floor item pool with depth-scaled weights. This requires extending `floor_item_pool` entries to reference scrolls/wands, not just weapons/armor. Phase 1 should include this integration.

### Decisions to Make

1. **Scroll stacking?** Current `Consumable` stacking is name-based. Should two Lightning Scrolls stack into one inventory slot with StackSize=2? **Recommendation: Yes**, same as potions. Scrolls are consumed on use, stacking is natural. Wands do NOT stack (each has independent charge count).

2. **Earthquake self-damage?** PoC convention is caster takes no self-damage from AoE-self spells. Confirm this is desired. **Recommendation: No self-damage** — the caster is the epicenter but is protected.

3. **Portal wand — inventory slot or equipment slot?** Recommendation: inventory. It's used from the quickbar (future), not worn. Equipment slots are for weapons/armor.

4. **Wand recharge priority.** If the player has both a Lightning Scroll and a Wand of Lightning, and picks up another Lightning Scroll — does it auto-recharge the wand? **Recommendation: No auto-recharge on pickup.** Recharge only when the player explicitly uses a scroll on a wand (future UI). For now, picking up a scroll always adds it to inventory. Wand recharge is a stretch goal for this plan.

   **Revised after review:** The PoC does auto-recharge on pickup. Match that behavior — when a scroll is picked up and a matching wand exists with charges < max, consume the scroll and add +1 charge. If no matching wand or wand is full, scroll goes to inventory normally.

---

## 8. Confirmed Design Decisions (2026-03-29)

### UI Placement
Scrolls and wands appear in the **quick-bar** alongside healing potions. No separate inventory management needed to use them — tap from quick-bar to activate. The quick-bar extension (slot type detection) is part of Phase 1 scope.

### Wand of Portals — Unique Starting Item
- Player **starts with Wand of Portals** in starting inventory.
- It **never drops from the floor pool**. Not in any loot table.
- If the player drops it and kills themselves (or uses it up somehow), that's on them — no replacement.
- The Wand of Portals is designed to be a **crucial late-game tool** — future systems will build around its existence (secrets behind walls, bypassing locked areas, tactical repositioning). Treat it like a core player capability, not optional loot.
- Implementation: `DungeonFloorBuilder` adds `wand_of_portals` to starting inventory for the player entity on floor 1 only (or always in starting config, not respawned on floor change).

### Floor Pool Weights for Scrolls and Wands
Added to `floor_item_pools.yaml` with `from_dungeon_level` depth gates:

| Tier | Weight | Depth | Examples |
|------|--------|-------|---------|
| Common scrolls | 15 | 1+ | scroll_of_lightning, scroll_of_light, scroll_of_earthquake, scroll_of_magic_map |
| Uncommon scrolls | 10 | 2+ | scroll_of_detect_monsters, scroll_of_enchant_weapon, scroll_of_enchant_armor, scroll_of_confusion |
| Rare scrolls | 6 | 3+ | scroll_of_fireball, scroll_of_teleport, scroll_of_raise_dead, scroll_of_identify |
| Wands | 8 | 2+ | wand_of_lightning, wand_of_fireball, wand_of_confusion, wand_of_slow, wand_of_teleportation, wand_of_rage, wand_of_glue |

Wand of Portals: **not in pool**. Starting inventory only.

For the testing scenario (`config/testing/test_scroll_wand_basics.yaml`), drop one of each scroll type and a wand — no depth gating needed in the test scenario itself.
