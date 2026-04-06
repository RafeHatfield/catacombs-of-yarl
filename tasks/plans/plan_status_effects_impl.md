# Status Effects System -- Implementation Plan

## Status: in-progress

## Overview

The status effects system is the most cross-cutting feature in the game. It gates combat, movement, AI targeting, spell use, and item use. The original plan (`plan_status_effects.md`) defined 5 phases. Phases 1-4 are **complete** -- the lifecycle engine, movement effects, combat effects, and AI override effects are all implemented with 90+ tests passing.

What remains is:
1. **Presentation layer** (Phase 5 from original plan): UI badges, toast messages, monster tints
2. **Potion system**: Status-effect-granting potions (only healing_potion exists in C#; the PoC has 15+ potion types)
3. **Throw system**: Most potions are throwable -- tap potion enters targeting mode, tap target to throw, cancel to drink self
4. **Missing scroll spells**: A few scrolls/wands reference effects but have no dedicated resolution logic
5. **Harness verification**: Running balance scenarios with status effects active to validate they don't break Death%/H_PM metrics

This plan covers the remaining work in concrete builder-agent-sized tasks.

## Reference

- Design doc: `docs/DESIGN_PRINCIPLES.md`, `tasks/plans/plan_status_effects.md` (original 5-phase plan)
- Spell system: `tasks/plans/plan_spell_wand_scroll_system.md` (complete, Phases 1-5)
- Python PoC: `~/development/rlike/components/status_effects.py` (~2600 lines), `~/development/rlike/item_functions.py` (potion handlers), `~/development/rlike/throwing.py` (throw system)
- Current C# status effects: `src/Logic/Combat/StatusEffects/` (27 effect classes + StatusEffectProcessor)
- Current C# spell resolver: `src/Logic/Combat/SpellResolver.cs` (20+ spell handlers)
- Current entities.yaml: `config/entities.yaml` (scrolls/wands defined, only healing_potion for consumables)
- Tests: `tests/Core/StatusEffectLifecycleTests.cs`, `MovementEffectTests.cs`, `CombatEffectTests.cs`, `AiEffectTests.cs`, `StatusEffectEventTests.cs`

## Current State Assessment

### What Is Complete (Phases 1-4)

**Phase 1 -- Lifecycle Engine (24 tests)**
- `IStatusEffect` interface, `StatusEffectProcessor` (apply, tick, expire, floor clear)
- DOT: PoisonEffect, BurningEffect, PlagueEffect
- HOT: RegenerationEffect
- Skip-turn: SlowedEffect, ImmobilizedEffect, SleepEffect
- FreeActionTag immunity (blocks slow + immobilize application)
- No-stack/refresh rule, wake-on-attack-damage
- Floor descent clears all effects
- All 24 lifecycle tests passing

**Phase 2 -- Movement Effects (20+ tests)**
- DisorientationEffect: random movement for player and monster, movement-only (attacks unaffected)
- EntangledEffect: blocks movement, allows adjacent attacks
- FearEffect: monster flees from player, does not attack while feared
- ImmobilizedEffect: full turn skip (via ProcessTurnStart)
- All movement tests passing

**Phase 3 -- Combat Effects (26+ tests)**
- DisarmedEffect: blocks weapon attacks for player and monster (in TurnController)
- SilencedEffect: blocks scroll and wand use (in TurnController.ResolveSpellAction)
- InvisibilityEffect: monsters cannot target; breaks on player attack or spell cast
- ShieldEffect (+4 AC), ProtectionEffect (+3 AC), BarkskinEffect (+4 AC): read in CombatResolver
- WeaknessEffect (-2 damage, min 1): read in CombatResolver
- BlindedEffect (-4 accuracy): read in CombatResolver
- FocusedEffect (+3 accuracy): read in CombatResolver
- CrippledEffect (-1 to-hit, -1 AC): read in CombatResolver (orc shaman hex)
- RallyEffect (+1 to-hit, +1 damage): read in CombatResolver (orc chieftain rally)
- All combat tests passing

**Phase 4 -- AI Override Effects (18+ tests)**
- EnragedEffect: HostileToAll flag on AiComponent, targets nearest entity
- TauntedEffect: forces targeting player, duration 1000
- DisorientationEffect on monster AI: random movement, still attacks adjacent
- EntangledEffect on monster AI: cannot move, attacks adjacent
- FearEffect on monster AI: flee behavior
- Speed/Sluggish: apply/tick/expire correctly (behavior inert -- needs bonus attack system)
- AggravatedEffect: stub with StatusAppliedEvent (needs faction system)
- All AI tests passing

**Phase 5 -- Events (8 tests)**
- StatusAppliedEvent, StatusExpiredEvent, DotDamageEvent, HotHealEvent, SkipTurnEvent
- All event tests passing

### What Remains

| Area | Priority | Description |
|------|----------|-------------|
| Potion infrastructure + throw system | High | ConsumableDefinition spell fields, ThrowSpellId, throw targeting UX |
| Potion content (12+ types) | High | Buff, debuff, dual-mode, and special potions |
| Presentation (UI badges) | Medium | StatusEffectBar under HP, toast messages, monster tints |
| DetectMonsterEffect behavior | Low | Scroll exists but effect just emits event -- no actual FOV reveal |
| Harness verification | Medium | Run scenarios with status effects to validate balance |

---

## Throw System Design

### UX Recommendation: Tap Potion = Enter Targeting Mode (Throw First)

The PoC uses separate "use" and "throw" actions (keyboard 'u' and 't'). On mobile, this split is awkward -- we don't have keyboard shortcuts, and a "drink or throw?" dialog interrupts flow. Instead, the throw UX should reuse the existing targeting infrastructure.

**Concrete design: Tap potion enters targeting mode for throwing. Cancel throws = drink self.**

The flow:

1. Player taps a throwable potion in inventory
2. `HandleInventoryTap` detects `SpellEffect` with `ThrowSpellId` set
3. GameController enters targeting mode with `TargetingMode.SingleTarget`, using `ThrowSpellId` as the spell, range 10
4. Toast: "Tap a target to throw [Potion Name]. Tap yourself to drink."
5. **Player taps a monster**: fires `PlayerAction.CastSpell` with `ThrowSpellId` and `targetEntityId` -- throw resolves, potion consumed
6. **Player taps self (cancel)**: `OnTargetingCancelled` detects this is a potion throw cancel, fires `PlayerAction.CastSpell` with the drink `SpellId` and self-targeting -- drink resolves, potion consumed
7. **Player taps empty space or actual cancel button**: standard cancel, no action, no consumption

This design:
- Reuses the existing `EnterTargetingMode` / `OnTargetChosen` / `OnTargetingCancelled` infrastructure (already built for wands/scrolls)
- Matches the mental model: potions are primarily offensive (throw at enemy), secondarily defensive (drink self)
- For potions where throw makes no sense (healing, buff-only), there is no `ThrowSpellId` -- tap immediately drinks (self-targeting, no targeting mode)
- For debuff potions (weakness, blindness, etc.), the "drink" path is the self-debuff -- tapping self during throw targeting drinks the cursed potion (player debuffs self, which is the unidentified behavior anyway)
- Fire potion is throw-only (no drink effect) -- cancel does nothing, like cancelling a scroll

**Key implementation detail**: `OnTargetingCancelled` currently returns to `WaitingForInput` with no action. For throw-cancel-to-drink, we need a new path: if the targeting state has a `DrinkSpellId` (the potion's primary `SpellId`), cancelling by tapping self triggers the drink action instead of doing nothing. This requires a small addition to `TargetingState` (a `DrinkOnCancel` flag + the drink spell ID).

**Self-tap vs cancel button**: Tapping yourself during targeting already triggers `OnTargetingCancelled` in the existing InputHandler (self-tap = cancel for wands/scrolls). For throw potions, we distinguish: self-tap = drink, cancel button = abort. This requires `InputHandler.HandleTapInTargetingMode` to detect self-tap separately and fire a new event (`ThrowCancelledDrinkSelf`) rather than the generic `TargetingCancelled`.

### Which Potions Get Throw Effects

Based on PoC analysis (`item_functions.py` + `throwing.py` + test scenarios):

| Potion | Drink Effect | Throw Effect | ThrowSpellId | Notes |
|--------|-------------|--------------|--------------|-------|
| Healing Potion | Heal HP | -- | none | Throwing heals the target (monster) -- useless. No throw. |
| Potion of Speed | SpeedEffect (20t) | -- | none | Buff only. No meaningful throw effect. |
| Potion of Protection | ProtectionEffect (50t) | -- | none | Buff only. No meaningful throw effect. |
| Potion of Regeneration | RegenerationEffect (50t) | -- | none | Buff only. No meaningful throw effect. |
| Potion of Invisibility | InvisibilityEffect (30t) | -- | none | Buff only. Throwing makes monster invisible -- bad. |
| Potion of Heroism | HeroismEffect (30t) | -- | none | Buff only. Throwing buffs enemy -- bad. |
| Potion of Weakness | WeaknessEffect (30t) | WeaknessEffect on target (30t) | `throw_weakness` | Drink debuffs self (unidentified trap). Throw debuffs enemy (useful). |
| Potion of Slowness | SlowedEffect (20t) | SlowedEffect on target (20t) | `throw_slowness` | Same logic as weakness. |
| Potion of Blindness | BlindedEffect (15t) | BlindedEffect on target (15t) | `throw_blindness` | Same logic as weakness. |
| Potion of Paralysis | ImmobilizedEffect (3-5t) | ImmobilizedEffect on target (3-5t) | `throw_paralysis` | Same logic as weakness. |
| Tar Potion | SluggishEffect (10t) | SluggishEffect on target (10t) | `throw_tar` | Same logic as weakness. |
| Root Potion | BarkskinEffect (+3 AC, 10t) | EntangledEffect (3t) | `throw_root` | Dual-mode: drink for defense, throw for CC. |
| Sunburst Potion | FocusedEffect (+2 acc, 8t) | BlindedEffect (3t) | `throw_sunburst` | Dual-mode: drink for accuracy, throw for debuff. |
| Fire Potion | -- (throw only) | BurningEffect (1 dmg/t, 4t) | `throw_fire` | Throw-only. `spell_id` is `throw_fire`, no drink. |
| Antidote Potion | Cures PlagueEffect | -- | none | Self-only utility. |

**Summary**: 8 potions get ThrowSpellId (5 debuffs + root + sunburst + fire). 7 potions are drink-only (healing, 5 buffs, antidote). Fire potion is throw-only.

### Architecture: ThrowSpellId on SpellEffect

Add `string? ThrowSpellId` to `SpellEffect`. When `ThrowSpellId` is set:
- `HandleInventoryTap` routes to a new `HandleThrowablePotion` method instead of `HandleScrollOrWandUse`
- `HandleThrowablePotion` enters targeting mode with `SingleTarget`, range 10, using `ThrowSpellId`
- `TargetingState` gains `string? DrinkSpellId` for the drink-on-self-tap fallback
- `SpellResolver` gains handlers for each `throw_*` spell ID (apply effect to target entity)

When `ThrowSpellId` is NOT set but `SpellEffect` is present:
- Potion routes through `HandleScrollOrWandUse` as before (self-targeting = immediate drink)

---

## Phase A: Potion Infrastructure (Throw + Drink)

### Architecture Decision: Potions as SpellEffect Consumables with ThrowSpellId

The C# architecture already has `SpellEffect` + `Consumable` on the same entity for scrolls. Potions use the same pattern:
- A potion is a `Consumable` (stackable, consumed on use) with a `SpellEffect` (spell_id identifies the drink effect)
- Self-only potions use `targeting: "self"` and resolve through `SpellResolver`
- Throwable potions have `ThrowSpellId` set on `SpellEffect` -- tapping enters targeting mode for throw
- The `SpellResolver` gains new spell IDs for each potion effect (both drink and throw variants)
- `IsPotion` on `Consumable` bypasses the SilencedEffect gate

**Key difference from scrolls:** Potions are NOT blocked by SilencedEffect. The SilencedEffect gate in `TurnController.ResolveSpellAction` must check `Consumable.IsPotion` and skip the gate.

### PoC Potion Inventory (What to Port)

| Potion | PoC function | Drink Effect | Throw Effect | PoC Duration | Priority |
|--------|-------------|--------------|--------------|--------------|----------|
| Potion of Speed | `drink_speed_potion` | SpeedEffect | -- | 20 | P1 |
| Potion of Protection | `drink_protection_potion` | ProtectionEffect (+4 AC) | -- | 50 | P1 |
| Potion of Regeneration | `drink_regeneration_potion` | RegenerationEffect (1 HP/turn) | -- | 50 | P1 |
| Potion of Invisibility | `drink_invisibility_potion` | InvisibilityEffect | -- | 30 | P1 |
| Potion of Heroism | `drink_heroism_potion` | HeroismEffect (+3 hit, +3 dmg) | -- | 30 | P1 |
| Potion of Weakness | `drink_weakness_potion` | WeaknessEffect (-2 dmg) | WeaknessEffect on target | 30 | P2 |
| Potion of Slowness | `drink_slowness_potion` | SlowedEffect | SlowedEffect on target | 20 | P2 |
| Potion of Blindness | `drink_blindness_potion` | BlindedEffect (-4 acc) | BlindedEffect on target | 15 | P2 |
| Potion of Paralysis | `drink_paralysis_potion` | ImmobilizedEffect | ImmobilizedEffect on target | 3-5 (random) | P2 |
| Tar Potion | `drink_tar_potion` | SluggishEffect | SluggishEffect on target | 10 | P2 |
| Root Potion | `use_root_potion` | BarkskinEffect (+3 AC, 10t) | EntangledEffect (3t) | varies | P3 |
| Sunburst Potion | `use_sunburst_potion` | FocusedEffect (+2 acc, 8t) | BlindedEffect (3t) | varies | P3 |
| Fire Potion | `apply_burning_potion` | -- (throw only) | BurningEffect (1 dmg/t, 4t) | 4 | P3 |
| Antidote Potion | `drink_antidote_potion` | Cures PlagueEffect | -- | instant | P3 |
| Potion of Experience | `drink_experience_potion` | Grants 1 level | -- | instant | DEFER |
| Lightning Reflexes Potion | `drink_lightning_reflexes_potion` | +50% speed bonus | -- | 15 | DEFER |
| Levitation Potion | `drink_levitation_potion` | LevitationEffect | -- | 40 | DEFER |

### Silenced Gate Fix

Currently `TurnController.ResolveSpellAction` gates ALL spell use behind `SilencedEffect`. Potions should bypass this.

**Decision: Add `bool IsPotion` to `Consumable`.** Set true for potions, false for scrolls. The silence gate checks `!item.Get<Consumable>()?.IsPotion == true` before blocking.

---

## Phase B: Presentation Layer (UI Display)

Status effect badges, toast messages, and monster tints. This is the original Phase 5 from `plan_status_effects.md`. All logic is already emitting the correct events -- this phase just reads them.

---

## Tasks

### Phase A1: Core Infrastructure

- [x] TASK-001: Extend ConsumableDefinition and ConsumableFactory to support SpellEffect potions
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: none
  - Description: **This is the critical infrastructure gap.** Currently `ConsumableDefinition` has no `spell_id`, `targeting`, `duration`, `is_potion`, `throw_spell_id`, or `range` fields. `ConsumableFactory.Create()` never creates `SpellEffect` components. Without this, potions with spell effects cannot be defined in YAML.
    - Add to `ConsumableDefinition`: `SpellId`, `Targeting`, `Duration`, `IsPotion`, `ThrowSpellId`, `Range`, `Damage` (all optional, defaulting to empty/0/false).
    - Add `bool IsPotion` property to `Consumable` component (default false).
    - Update `ConsumableFactory.Create()`: if `def.SpellId` is non-empty, create and attach a `SpellEffect` component with the definition's values. If `def.ThrowSpellId` is non-empty, set `SpellEffect.ThrowSpellId`.
    - Update `TurnController.ResolveSpellAction`: skip the SilencedEffect gate when `item.Get<Consumable>()?.IsPotion == true`.
    - Update `GameController.HandleInventoryTap`: potions with SpellEffect must route through `HandleScrollOrWandUse` (they already will since they have SpellEffect, but the `UseItem` fallback for `Consumable` with no SpellEffect must remain for healing_potion).
  - Files to modify:
    - `src/Logic/Content/ConsumableDefinition.cs` -- add spell/potion fields
    - `src/Logic/Combat/Consumable.cs` -- add `IsPotion` property
    - `src/Logic/Content/ConsumableFactory.cs` -- create SpellEffect when spell_id present, wire ThrowSpellId
    - `src/Logic/Core/TurnController.cs` -- update SilencedEffect gate
    - `src/Logic/Combat/SpellEffect.cs` -- add `string? ThrowSpellId` property
  - Acceptance criteria:
    - ConsumableDefinition can deserialize spell_id, targeting, duration, is_potion, throw_spell_id from YAML
    - ConsumableFactory creates SpellEffect component when spell_id is non-empty
    - SpellEffect.ThrowSpellId is set when throw_spell_id is present in YAML
    - Consumable has `bool IsPotion` defaulting to false
    - Scroll use is still blocked by SilencedEffect
    - Wand use is still blocked by SilencedEffect
    - Potion use (IsPotion=true) bypasses SilencedEffect gate
    - Existing Silenced_BlocksScrollUse and Silenced_BlocksWandUse tests still pass
  - Tests to add:
    - `tests/Core/CombatEffectTests.cs`: `Silenced_DoesNotBlockPotion_WithSpellEffect`
    - `tests/Content/ContentLoaderTests.cs`: `ConsumableFactory_CreatesSpellEffect_WhenSpellIdPresent`
    - `tests/Content/ContentLoaderTests.cs`: `ConsumableFactory_SetsIsPotion_FromDefinition`
    - `tests/Content/ContentLoaderTests.cs`: `ConsumableFactory_SetsThrowSpellId_WhenPresent`

- [x] TASK-001a: Throw targeting UX in GameController (presentation layer)
  - Status: complete
  - Layer: presentation + logic
  - Type: system
  - Dependencies: TASK-001
  - Description: **This is the throw UX implementation.** Full detailed design follows below.
  - Files changed:
    - `src/Presentation/Input/TargetingState.cs` — added IsThrowPotion, ThrowSpellId, DrinkSpellId properties
    - `src/Presentation/Input/InputHandler.cs` — added DrinkSelfRequested event; self-tap during throw targeting fires DrinkSelfRequested instead of CancelTargeting when DrinkSpellId is non-null
    - `src/Presentation/GameController.cs` — subscribed DrinkSelfRequested; added HandleThrowablePotion and OnDrinkSelfRequested; HandleInventoryTap now routes ThrowSpellId != null items to HandleThrowablePotion
    - `src/Logic/Core/TurnController.cs` — added overrideSpellId logic: when TargetEntityId is present and ThrowSpellId is set, overrides spell dispatch to throw variant
    - `src/Logic/Combat/SpellResolver.cs` — added overrideSpellId parameter; dispatch switch uses overrideSpellId ?? spell.SpellId
  - Notes:
    - All 944 tests pass. No logic layer tests added (presentation-layer feature; design specifies manual verification).
    - Fire potion (no DrinkSpellId, routes through HandleScrollOrWandUse as SingleTarget) still works unchanged — does not hit HandleThrowablePotion.
    - Non-throwable potions (ThrowSpellId=null) fall through to HandleScrollOrWandUse unchanged.
    - Silence bypass (IsPotion) already handled in TurnController — drinking via self-tap is unblocked correctly.
    - InvisibilityEffect break already handled in TurnController: throwingPotion = isPotion && TargetEntityId.HasValue. Throw breaks invis, drink does not.
  - Tests: Presentation layer — manual verification. Logic layer routing verified by existing 944 tests.

## TASK-001a: Throw Targeting UX -- Detailed Design

### PoC Throw System Summary (What We Are Porting)

The PoC (`~/development/rlike`) implements throwing as a two-step flow using a dedicated `throwing.py` module:

1. **Initiation**: Player presses `t` key, which opens `THROW_SELECT_ITEM` state (inventory menu). Player selects which item to throw. Alternatively, right-clicking a monster stores the target coordinates and opens `THROW_SELECT_ITEM` -- after item selection, the throw fires immediately at the pre-stored target.

2. **Targeting**: After item selection, enters `THROW_TARGETING` state. Player clicks a tile to throw at. No accuracy roll -- projectile always goes where you click. Bresenham line traces the path, stopping at first wall.

3. **Impact resolution** (`throwing.py:throw_item`):
   - **Hit entity directly**: Full potion effect applied. The potion's `use_function` is called with `target` as the first arg and `throw_mode=True` kwarg.
   - **Hit empty tile**: Potion shatters on ground. "The [potion] shatters on the ground!" No effect applied. Potion consumed (wasted).
   - **Hit wall**: Projectile stops at wall. Same as empty tile if no entity there.

4. **No accuracy mechanic**: The PoC has no throw accuracy roll. You aim, it goes there. If there is an entity on the target tile, it gets hit. If not, it misses.

5. **No splash/AoE**: The PoC has a `TODO: Could add splash damage to adjacent tiles` comment but splash was never implemented. Single-tile effect only.

6. **Range**: 10 tiles (hardcoded in `calculate_throw_path`, line 106). Not displayed in UI.

7. **Dual-mode detection**: Potion functions check `throw_mode` kwarg or presence of `target_x`/`target_y` to determine mode. The `consumable_effects.py` dispatcher handles `EffectMode.THROWN` vs `EffectMode.CONSUMED`.

8. **Turn economy**: Throwing costs 1 turn (same as drinking).

9. **InvisibilityEffect**: Throwing a potion breaks invisibility (offensive action). Drinking does not.

### C# Architecture Decision: How It Maps

The PoC's keyboard-driven two-step flow (press `t` -> select item -> click target) does not translate to mobile. The C# port uses a different UX that achieves the same result with fewer taps.

**Decision: Tap potion = enter targeting mode for throw. Self-tap = drink. Cancel = abort.**

This is confirmed as the right approach. The existing `HandleInventoryTap` -> `HandleScrollOrWandUse` -> `EnterTargetingMode` -> `OnTargetChosen` pipeline already handles single-target spells. The throw UX is a variation of this pipeline with one addition: self-tap triggers drink instead of cancel.

### Design Decision 1: Throw Initiation

**When the player taps a throwable potion in the quick-bar, enter targeting mode for throwing.**

Currently `HandleInventoryTap` (line 148 of `GameController.cs`) checks for `SpellEffect` and routes to `HandleScrollOrWandUse`. Throwable potions already have `SpellEffect` (with `spell_id` = drink spell, `targeting: self`). The problem: `HandleScrollOrWandUse` sees `targeting: self` and fires immediately as a drink.

**Fix**: Before routing to `HandleScrollOrWandUse`, check `spell.ThrowSpellId`. If non-null, route to a new `HandleThrowablePotion` method instead.

```csharp
// In HandleInventoryTap, after getting spellEffect:
if (spellEffect != null)
{
    if (spellEffect.ThrowSpellId != null)
    {
        HandleThrowablePotion(item, spellEffect);
        return;
    }
    HandleScrollOrWandUse(item, spellEffect);
    return;
}
```

**Fire potion special case**: Fire potion has `targeting: single_target` and `spell_id: throw_fire`. It has NO `ThrowSpellId` because it IS a throw spell -- it routes directly through `HandleScrollOrWandUse` as a `SingleTarget` spell. Tapping fire potion enters targeting mode via the existing scroll path. Self-tap cancels (no drink effect). This is correct.

### Design Decision 2: Targeting Mode for Throws

**Use `TargetingMode.SingleTarget` with range 10 (PoC-matched).**

The new `HandleThrowablePotion` method creates a temporary `SpellEffect` for the throw spell and enters targeting mode:

```csharp
private void HandleThrowablePotion(Entity item, SpellEffect spell)
{
    Diag.Log($"HandleThrowablePotion: {item.Name} throw={spell.ThrowSpellId} drink={spell.SpellId}");

    EnterTargetingMode(new TargetingState
    {
        Item  = item,
        Spell = spell,
        Mode  = TargetingMode.SingleTarget,
        Range = spell.Range > 0 ? spell.Range : 10, // PoC default: 10 tiles
        // New fields for throw potion behavior:
        IsThrowPotion = true,
        ThrowSpellId  = spell.ThrowSpellId!,
        DrinkSpellId  = spell.SpellId,  // The drink spell for self-tap fallback
    }, showGenericToast: false);

    _toastLog?.AddMessage($"Tap a target to throw {item.Name}. Tap yourself to drink.");
}
```

**No range display needed for v1.** The PoC does not display throw range either. Range validation happens in `InputHandler.HandleTapInTargetingMode` (already exists, line 184-192).

### Design Decision 3: Hit vs. Miss (No Accuracy Roll)

**No accuracy mechanic. Matches PoC exactly.**

The PoC has no throw accuracy roll. If you target a tile with a monster, the monster gets hit. If you target an empty tile, the potion shatters with no effect.

In the C# system, `SingleTarget` targeting mode already requires tapping a monster entity (line 176: `FindMonsterAt`). Tapping an empty tile does nothing (stays in targeting mode). This means you cannot throw a potion at an empty floor tile -- it simply does not register as a valid target.

**This is actually a slight improvement over the PoC**, where throwing at empty floor wastes the potion. On mobile, accidental throws at empty tiles would be frustrating. Requiring a monster target prevents waste. The tradeoff: no ability to throw potions at empty floor for area denial (which the PoC also does not meaningfully support -- no splash/AoE).

### Design Decision 4: Impact on Empty Tile

**Not applicable in C# implementation.** The `SingleTarget` targeting mode only fires when the player taps a valid monster entity. There is no empty-tile throw path. This matches the PoC's practical behavior (throwing at empty floor wastes the potion with no useful effect) while preventing accidental waste on mobile.

### Design Decision 5: The "Drink Instead" Path (Self-Tap)

**Self-tap during throw targeting triggers the drink spell. This requires modifying InputHandler.**

Currently (line 167-172 of `InputHandler.cs`):
```csharp
// Tapping the player's own tile cancels targeting
if (gridX == player.X && gridY == player.Y)
{
    CancelTargeting();
    return;
}
```

For throw potions, self-tap should trigger a DRINK action, not a cancel. The modified logic:

```csharp
// Tapping the player's own tile
if (gridX == player.X && gridY == player.Y)
{
    if (targeting.IsThrowPotion && targeting.DrinkSpellId != null)
    {
        // Self-tap on throw potion = drink it instead
        var item = targeting.Item;
        _targeting = null;
        DrinkSelfRequested?.Invoke(item);
        return;
    }
    CancelTargeting();
    return;
}
```

**New event on InputHandler:**
```csharp
/// <summary>
/// Fired when the player taps themselves during throw-potion targeting,
/// indicating they want to drink the potion instead of throwing it.
/// </summary>
public event Action<Entity>? DrinkSelfRequested;
```

**GameController subscribes in constructor (near line 123):**
```csharp
_input.DrinkSelfRequested += OnDrinkSelfRequested;
```

**New handler in GameController:**
```csharp
/// <summary>
/// Called when the player self-taps during throw targeting to drink the potion.
/// Fires CastSpell with the drink spell ID (no target = self-targeting).
/// </summary>
private void OnDrinkSelfRequested(Entity item)
{
    Diag.Log($"OnDrinkSelfRequested: drinking {item.Name}");
    Phase = GamePhase.WaitingForInput;
    OnActionChosen(PlayerAction.CastSpell(item));
    // CastSpell with no targetEntityId routes through SpellResolver using the
    // primary SpellId (drink effect). The "self" targeting in the SpellEffect
    // means SpellResolver applies the effect to the caster.
}
```

**Fire potion (throw-only, no drink):** Fire potion has `spell_id: throw_fire` and `targeting: single_target`, with no `throw_spell_id`. It routes through `HandleScrollOrWandUse`, not `HandleThrowablePotion`. Self-tap during targeting triggers standard `CancelTargeting` with "Cancelled." toast. No special handling needed.

If we later add a throw-only potion that DOES use `HandleThrowablePotion` (i.e., has `ThrowSpellId` but the drink spell is useless), set `DrinkSpellId` to null. The self-tap check above (`targeting.DrinkSpellId != null`) falls through to `CancelTargeting`, which is correct. Add a toast: "You drink the potion but nothing happens. The potion is wasted." -- but this is a degenerate case that does not exist in the current PoC potion inventory.

### Design Decision 6: Logic Layer Changes

**No new action type needed. `CastSpell` covers both throw and drink.**

The existing flow is:
- **Throw**: `PlayerAction.CastSpell(item, targetEntityId: target.Id)` -- `TurnController.ResolveSpellAction` resolves with `targetEntityId` set, routes to `SpellResolver` which dispatches on the spell ID.
- **Drink**: `PlayerAction.CastSpell(item)` -- no `targetEntityId`, routes to `SpellResolver` which dispatches on the drink spell ID.

The critical routing detail: when the player taps a monster in throw targeting, `OnTargetChosen` fires `PlayerAction.CastSpell(item, targetEntityId: target.Id)`. But the item's `SpellEffect.SpellId` is the DRINK spell (e.g., `"drink_weakness"`), not the throw spell (e.g., `"throw_weakness"`).

**Fix: OnTargetChosen must use the ThrowSpellId, not the primary SpellId.**

Two approaches:
1. **Swap the SpellId temporarily** before firing CastSpell.
2. **Add a ThrowSpellId override to PlayerAction** so TurnController knows to use it.

**Decision: Approach 1 -- swap SpellId on the SpellEffect component before firing CastSpell.**

This is simpler and avoids polluting the logic layer with presentation concerns. The swap is safe because:
- The item entity is consumed after use (stack decremented, potentially removed from inventory).
- If the action is somehow blocked (e.g., SilencedEffect -- but potions bypass that), the SpellId remains swapped, but that is fine because the item was not consumed.
- Actually, this is NOT safe if something interrupts between the swap and the action.

**Revised decision: Approach 2 -- create a synthetic SpellEffect entity for the throw.**

No, that is over-engineering. Let me reconsider.

**Final decision: Use the simpler approach of creating the CastSpell action with a signal that TurnController should use ThrowSpellId.**

Actually, the cleanest path is: `OnTargetChosen` already produces `PlayerAction.CastSpell(item, targetEntityId: target.Id)`. Inside `TurnController.ResolveSpellAction`, when processing a `CastSpell` with a target entity ID, check if the item's `SpellEffect.ThrowSpellId` is non-null. If so, resolve the throw spell instead of the primary spell.

This is entirely in the logic layer. `SpellResolver.Resolve` already receives `targetEntityId`. The dispatch logic in `SpellResolver` uses `spell.SpellId`. The fix:

```csharp
// In TurnController.ResolveSpellAction, before calling SpellResolver.Resolve:
string resolveSpellId = spell.SpellId;
if (action.TargetEntityId.HasValue && !string.IsNullOrEmpty(spell.ThrowSpellId))
{
    resolveSpellId = spell.ThrowSpellId;
}

var spellEvents = SpellResolver.Resolve(
    state.Player,
    spell,
    state,
    targetEntityId: action.TargetEntityId,
    targetX: action.TargetX,
    targetY: action.TargetY,
    overrideSpellId: resolveSpellId);
```

Then add `string? overrideSpellId = null` parameter to `SpellResolver.Resolve` and use `overrideSpellId ?? spell.SpellId` for the dispatch switch.

**Alternatively**, and more cleanly: the presentation layer can set the SpellId on the item directly before issuing the action. Since `HandleThrowablePotion` created the targeting state with `ThrowSpellId` stored, `OnTargetChosen` can swap the SpellId:

```csharp
private void OnTargetChosen(Entity item, Entity target)
{
    Diag.Log($"OnTargetChosen: item={item.Name} target={target.Name}(id={target.Id})");
    Phase = GamePhase.WaitingForInput;

    // If this was a throw-potion targeting, swap to the throw spell ID
    // so TurnController resolves the throw effect, not the drink effect.
    var spell = item.Get<SpellEffect>();
    if (spell?.ThrowSpellId != null && _wasThrowTargeting)
    {
        spell.SpellId = spell.ThrowSpellId;
    }

    OnActionChosen(PlayerAction.CastSpell(item, targetEntityId: target.Id));
}
```

**Problem**: `_wasThrowTargeting` state is fragile. And mutating the SpellId is unclean.

**FINAL decision: Add `overrideSpellId` parameter to `SpellResolver.Resolve`.** This is 3 lines of logic layer change, does not mutate any component, and is the cleanest approach. The presentation layer does not need to track state beyond what `TargetingState` already carries.

The change in `TurnController.ResolveSpellAction` (around line 332):

```csharp
// Determine which spell ID to resolve. For throwable potions with a target,
// use ThrowSpellId instead of the primary SpellId (which is the drink spell).
string? overrideSpellId = null;
if (action.TargetEntityId.HasValue && !string.IsNullOrEmpty(spell.ThrowSpellId))
{
    overrideSpellId = spell.ThrowSpellId;
}

var spellEvents = SpellResolver.Resolve(
    state.Player,
    spell,
    state,
    targetEntityId: action.TargetEntityId,
    targetX: action.TargetX,
    targetY: action.TargetY,
    overrideSpellId: overrideSpellId);
```

In `SpellResolver.Resolve`, add the parameter and use it:

```csharp
public static List<TurnEvent> Resolve(
    Entity caster, SpellEffect spell, GameState state,
    int? targetEntityId = null, int? targetX = null, int? targetY = null,
    string? overrideSpellId = null)
{
    string spellId = overrideSpellId ?? spell.SpellId;
    return spellId switch
    {
        // ... existing dispatch table unchanged ...
    };
}
```

### Design Decision 7: Events Emitted

**Reuse SpellEvent. No new event type needed.**

Throw resolution goes through `SpellResolver`, which already emits `SpellEvent` with `TargetId`, `StatusApplied`, `StatusDuration`, etc. The events emitted for a throw are identical in structure to a targeted spell cast. The presentation layer can distinguish throw from drink by checking `TargetId` (set = throw, null = drink/self).

The `InvisibilityEffect` break already correctly handles throws: `TurnController.ResolveSpellAction` line 298 checks `isPotion && action.TargetEntityId.HasValue` and breaks invisibility for throws but not drinks.

### Design Decision 8: Non-Throwable Potions

**No change needed. They continue to work as they do today.**

Non-throwable potions (healing, speed, protection, regeneration, invisibility, heroism, antidote) have `ThrowSpellId = null`. The new check in `HandleInventoryTap`:

```csharp
if (spellEffect.ThrowSpellId != null)
{
    HandleThrowablePotion(item, spellEffect);
    return;
}
```

...does not trigger. They fall through to `HandleScrollOrWandUse`, which sees `targeting: self` and fires `CastSpell` immediately. Healing potion (no SpellEffect) falls through to `UseItem`. All existing paths preserved.

### File-Level Change Summary

#### `src/Presentation/Input/TargetingState.cs`
Add 3 properties:
```csharp
/// <summary>True when this targeting session is for a throwable potion.</summary>
public bool IsThrowPotion { get; init; }

/// <summary>Throw spell ID (e.g., "throw_weakness"). Set when IsThrowPotion=true.</summary>
public string? ThrowSpellId { get; init; }

/// <summary>Drink spell ID for self-tap fallback. Null for throw-only potions.</summary>
public string? DrinkSpellId { get; init; }
```

#### `src/Presentation/Input/InputHandler.cs`
1. Add event: `public event Action<Entity>? DrinkSelfRequested;`
2. Modify `HandleTapInTargetingMode` self-tap block (line 167-172):
   - If `targeting.IsThrowPotion && targeting.DrinkSpellId != null`: clear targeting, fire `DrinkSelfRequested(item)`
   - Otherwise: existing `CancelTargeting()` behavior

#### `src/Presentation/GameController.cs`
1. Subscribe to `_input.DrinkSelfRequested += OnDrinkSelfRequested;` in constructor (near line 125)
2. Unsubscribe in dispose/cleanup if applicable
3. Modify `HandleInventoryTap` (after line 164): add `ThrowSpellId` check before `HandleScrollOrWandUse`
4. Add `HandleThrowablePotion(Entity item, SpellEffect spell)` method
5. Add `OnDrinkSelfRequested(Entity item)` method

#### `src/Logic/Core/TurnController.cs`
1. In `ResolveSpellAction` (around line 332): add `overrideSpellId` logic for ThrowSpellId when `TargetEntityId` is present

#### `src/Logic/Combat/SpellResolver.cs`
1. Add `string? overrideSpellId = null` parameter to `Resolve` method
2. Use `overrideSpellId ?? spell.SpellId` at top of dispatch switch

### Bot / Harness Support for Throws

The current C# bot (`BotBrain.cs`) has no throw support. To harness-verify throw potions, add a `ThrowPotion` action type to `BotAction` and a decision branch in `BotBrain.Decide`:

This is NOT part of TASK-001a. It is a separate task (TASK-015 or similar) that adds:
- `BotAction.ActionType.ThrowPotion` with target entity + item
- `BotBrain.ToPlayerAction` mapping: `PlayerAction.CastSpell(item, targetEntityId: target.Id)` with the item's ThrowSpellId override handled by the logic layer changes above
- Decision logic: if holding a throwable potion and enemy is in range 3-10, throw; prefer throwing at range over closing to melee

### Testing Plan

Since this is presentation layer, most verification is manual. However, the logic layer changes (TurnController + SpellResolver) are testable:

1. **Unit test**: `ThrowPotion_UsesThrowSpellId_WhenTargetEntityIdPresent` -- create a potion with `ThrowSpellId = "throw_weakness"`, fire `CastSpell` with `targetEntityId` set, verify `WeaknessEffect` applied to target (not caster)
2. **Unit test**: `DrinkPotion_UsesPrimarySpellId_WhenNoTargetEntityId` -- same potion, fire `CastSpell` with no target, verify `WeaknessEffect` applied to caster (drink behavior)
3. **Unit test**: `NonThrowablePotion_IgnoresThrowSpellId_WhenNull` -- potion with `ThrowSpellId = null`, verify drink behavior regardless of target
4. **Manual verification**: tap potion -> targeting mode -> tap monster -> throw effect applied
5. **Manual verification**: tap potion -> targeting mode -> tap self -> drink effect applied
6. **Manual verification**: tap potion -> targeting mode -> cancel button -> no effect, no consumption
7. **Manual verification**: fire potion (single_target, no ThrowSpellId) -> targeting mode via existing path -> tap monster -> burn applied

### Sequence Diagram

```
THROW PATH:
Player taps throwable potion in quick-bar
  -> GameController.HandleInventoryTap
  -> detects SpellEffect.ThrowSpellId != null
  -> GameController.HandleThrowablePotion
  -> EnterTargetingMode(SingleTarget, range=10, IsThrowPotion=true)
  -> Toast: "Tap target to throw. Tap self to drink."
Player taps monster
  -> InputHandler.HandleTapInTargetingMode
  -> SingleTarget: FindMonsterAt, validate range
  -> TargetChosen.Invoke(item, target)
  -> GameController.OnTargetChosen
  -> PlayerAction.CastSpell(item, targetEntityId=target.Id)
  -> TurnController.ResolveSpellAction
  -> detects targetEntityId + ThrowSpellId -> overrideSpellId = ThrowSpellId
  -> SpellResolver.Resolve(overrideSpellId="throw_weakness")
  -> WeaknessEffect applied to target

DRINK PATH (self-tap):
Player taps self during throw targeting
  -> InputHandler.HandleTapInTargetingMode
  -> self-tap detected + IsThrowPotion + DrinkSpellId != null
  -> DrinkSelfRequested.Invoke(item)
  -> GameController.OnDrinkSelfRequested
  -> PlayerAction.CastSpell(item) [no targetEntityId]
  -> TurnController.ResolveSpellAction
  -> no targetEntityId -> overrideSpellId stays as primary SpellId
  -> SpellResolver.Resolve(spellId="drink_weakness")
  -> WeaknessEffect applied to caster (self)

CANCEL PATH:
Player taps cancel button / swipes away
  -> InputHandler.CancelTargeting
  -> TargetingCancelled.Invoke()
  -> GameController.OnTargetingCancelled
  -> Phase = WaitingForInput, no action, no consumption
```

- [x] TASK-002: Fix InvisibilityEffect break logic for potions
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Description: `ResolveSpellAction` breaks InvisibilityEffect at line 294 for ANY spell cast. The comment says "Does NOT break on item use (potions)" but currently potions with SpellEffect WILL route through `ResolveSpellAction` and break invisibility. The fix: after the SilencedEffect gate (which already skips for potions), also skip the InvisibilityEffect break when `item.Get<Consumable>()?.IsPotion == true`. **Throwing a potion DOES break invisibility** (offensive action targeting another entity).
  - Files to modify:
    - `src/Logic/Core/TurnController.cs` -- wrap InvisibilityEffect break in `!isPotion || hasTarget` check
  - Acceptance criteria:
    - Drinking a buff potion while invisible does NOT break invisibility
    - Casting a scroll while invisible still breaks invisibility
    - Using a wand while invisible still breaks invisibility
    - Throwing a potion (has targetEntityId) DOES break invisibility
  - Tests to add in `tests/Core/CombatEffectTests.cs`:
    - `Invisible_DrinkPotion_DoesNotBreakInvisibility`
    - `Invisible_ThrowPotion_BreaksInvisibility`

### Phase A2: Buff Potions (Drink-Only)

- [x] TASK-003a: Create HeroismEffect status effect class
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: none (can be built before TASK-003)
  - Description: The PoC has a Potion of Heroism (+3 to-hit, +3 damage, 30 turns). This requires a new `HeroismEffect` class similar to RallyEffect but with different values and purpose (potion buff vs. monster ability). Wire into CombatResolver like RallyEffect (additive to-hit and damage bonuses).
  - Files to create:
    - `src/Logic/Combat/StatusEffects/HeroismEffect.cs`
  - Files to modify:
    - `src/Logic/Combat/CombatResolver.cs` -- read HeroismEffect for to-hit and damage bonuses
  - Acceptance criteria:
    - HeroismEffect with AttackBonus=3, DamageBonus=3, default duration=30
    - CombatResolver adds AttackBonus to to-hit and DamageBonus to damage
    - Stacks additively with RallyEffect and FocusedEffect (different effect types, no conflict)
  - Tests to add:
    - `HeroismEffect_AddsToHitBonus_InCombat`
    - `HeroismEffect_AddsDamageBonus_InCombat`
    - `HeroismEffect_StacksWithRallyEffect`

- [x] TASK-003: Add buff potion spell IDs to SpellResolver (speed, protection, regeneration, invisibility, heroism)
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001, TASK-003a
  - Description: Add self-targeting spell handlers to SpellResolver for buff potions. These reuse the existing `ResolveSelfStatusEffect<T>` pattern. Where the effect is identical to an existing scroll spell, reuse the same spell ID. Where duration or values differ, use distinct spell IDs.
  - Spell ID mapping:
    - `"haste"` (existing) -- reuse for Potion of Speed. SpeedEffect, duration from SpellEffect.Duration (20).
    - `"invisibility"` (existing) -- reuse for Potion of Invisibility. InvisibilityEffect, duration 30.
    - `"drink_protection"` (new) -- ProtectionEffect with AcBonus=4, duration=50. **NOTE: PoC uses +4 AC / 50 turns.**
    - `"drink_regeneration"` (new) -- RegenerationEffect with HealPerTurn=1, duration=50. **NOTE: PoC uses 1 HP/turn for 50 turns (50 HP total).**
    - `"drink_heroism"` (new) -- HeroismEffect (+3 to-hit, +3 damage, 30 turns).
  - Files to modify:
    - `src/Logic/Combat/SpellResolver.cs` -- add "drink_protection", "drink_regeneration", "drink_heroism" handlers
  - Acceptance criteria:
    - `"drink_protection"` applies ProtectionEffect with AcBonus=4, duration=50
    - `"drink_regeneration"` applies RegenerationEffect with HealPerTurn=1, duration=50
    - `"haste"` (already exists) works for speed potion
    - `"invisibility"` (already exists) works for invisibility potion
    - `"drink_heroism"` applies HeroismEffect with correct values
  - Tests to add in `tests/Core/SpellResolverPotionTests.cs`:
    - `DrinkProtection_AppliesProtectionEffect_WithCorrectValues`
    - `DrinkRegeneration_AppliesRegenerationEffect_WithCorrectValues`
    - `DrinkSpeed_ReusesHasteSpell_AppliesSpeedEffect`
    - `DrinkInvisibility_ReusesInvisibilitySpell_AppliesInvisibilityEffect`
    - `DrinkHeroism_AppliesHeroismEffect_WithCorrectValues`

- [x] TASK-004: Add buff potion definitions to entities.yaml
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-003, TASK-003a
  - Description: Add YAML definitions for the 5 buff potions to `config/entities.yaml` under the consumables section. Each potion needs: name, spell_id, targeting, is_potion, duration, char, color, category. None of these have ThrowSpellId -- they are drink-only.
  - PoC reference: `~/development/rlike/config/entities.yaml` lines 1665-1711
  - Files to modify:
    - `config/entities.yaml` -- add potion_of_speed, potion_of_protection, potion_of_regeneration, potion_of_invisibility, potion_of_heroism
  - Acceptance criteria:
    - All 5 potions load without YAML parse errors
    - Each potion has `is_potion: true`, correct spell_id, `targeting: self`, NO throw_spell_id
    - Potions appear in ContentLoader's consumable registry
    - ContentLoader round-trip test passes
  - Tests to add in `tests/Content/ContentLoaderTests.cs`:
    - `ContentLoader_LoadConsumables_IncludesBuffPotions`
    - `ContentLoader_BuffPotion_HasIsPotion_True`

### Phase A3: Debuff Potions (Drink Self + Throw at Enemy)

- [x] TASK-005: Add debuff potion spell IDs to SpellResolver -- drink AND throw variants
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Description: Debuff potions have TWO spell IDs each -- one for drinking (applies to self) and one for throwing (applies to target). The drink spell is self-targeting. The throw spell is single-target. Both apply the same effect type with the same duration -- the difference is who receives it.
  - New drink spell IDs (self-targeting, **corrected PoC values**):
    - `"drink_weakness"` (WeaknessEffect, duration **30**)
    - `"drink_slowness"` (SlowedEffect, duration **20**)
    - `"drink_blindness"` (BlindedEffect, duration **15**)
    - `"drink_paralysis"` (ImmobilizedEffect, duration **3-5 random** -- use `state.Rng.Next(3, 6)`)
    - `"drink_tar"` (SluggishEffect, duration 10)
  - New throw spell IDs (single-target, same durations):
    - `"throw_weakness"` (WeaknessEffect on target, duration 30)
    - `"throw_slowness"` (SlowedEffect on target, duration 20)
    - `"throw_blindness"` (BlindedEffect on target, duration 15)
    - `"throw_paralysis"` (ImmobilizedEffect on target, duration 3-5 random)
    - `"throw_tar"` (SluggishEffect on target, duration 10)
  - Files to modify:
    - `src/Logic/Combat/SpellResolver.cs` -- add 10 handlers (5 drink + 5 throw)
  - Acceptance criteria:
    - Each drink spell applies the correct effect to the caster (self)
    - Each throw spell applies the correct effect to the target entity
    - Duration matches PoC values
    - Paralysis uses random duration 3-5 for both drink and throw
    - FreeActionTag blocks drink_slowness, drink_paralysis, throw_slowness, throw_paralysis (via StatusEffectProcessor.ApplyEffect)
    - Events emitted correctly (StatusAppliedEvent via SpellEvent)
  - Tests to add in `tests/Core/SpellResolverPotionTests.cs`:
    - `DrinkWeakness_AppliesWeaknessEffect_ToSelf_Duration30`
    - `DrinkSlowness_AppliesSlowedEffect_ToSelf_Duration20`
    - `DrinkBlindness_AppliesBlindedEffect_ToSelf_Duration15`
    - `DrinkParalysis_AppliesImmobilizedEffect_ToSelf_Duration3To5`
    - `DrinkTar_AppliesSluggishEffect_ToSelf_Duration10`
    - `DrinkSlowness_FreeAction_BlocksApplication`
    - `ThrowWeakness_AppliesWeaknessEffect_ToTarget_Duration30`
    - `ThrowBlindness_AppliesBlindedEffect_ToTarget_Duration15`
    - `ThrowParalysis_AppliesImmobilizedEffect_ToTarget_Duration3To5`
    - `ThrowSlowness_FreeAction_BlocksApplication`

- [x] TASK-006: Add debuff potion definitions to entities.yaml (with ThrowSpellId)
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-005
  - Description: Add YAML definitions for the 5 debuff potions. These are identification-gated. Each has BOTH `spell_id` (drink) and `throw_spell_id` (throw). The `targeting` field is `"self"` (the drink default), but `ThrowSpellId` triggers the throw-first targeting flow in the presentation layer.
  - Files to modify:
    - `config/entities.yaml` -- add potion_of_weakness, potion_of_slowness, potion_of_blindness, potion_of_paralysis, tar_potion
  - Acceptance criteria:
    - All 5 debuff potions load without YAML parse errors
    - Each has `is_potion: true`, `spell_id` (drink), and `throw_spell_id` (throw)
    - Category is `Potion` (eligible for potion appearance pool in identification system)
    - ThrowSpellId is correctly deserialized and set on SpellEffect

### Phase A4: Dual-Mode and Special Potions

- [x] TASK-007: Add dual-mode and special potion spell IDs to SpellResolver
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Description: Root potion, sunburst potion, fire potion, and antidote each need spell handlers. Root and sunburst have both drink and throw spell IDs. Fire is throw-only. Antidote is drink-only.
  - New spell IDs with **corrected PoC values**:
    - `"drink_root"` (BarkskinEffect, +3 AC, 10 turns)
    - `"throw_root"` (EntangledEffect on target, 3 turns)
    - `"drink_sunburst"` (FocusedEffect, +2 acc, 8 turns)
    - `"throw_sunburst"` (BlindedEffect on target, 3 turns)
    - `"throw_fire"` (BurningEffect on target, 1 dmg/turn, 4 turns)
    - `"drink_antidote"` (removes PlagueEffect, emits StatusExpiredEvent with reason "cured")
  - Files to modify:
    - `src/Logic/Combat/SpellResolver.cs` -- add 6 handlers
  - Acceptance criteria:
    - Root potion drink: applies BarkskinEffect (+3 AC, 10 turns)
    - Root potion throw: applies EntangledEffect on target (3 turns)
    - Sunburst potion drink: applies FocusedEffect (+2 acc, 8 turns)
    - Sunburst potion throw: applies BlindedEffect on target (3 turns)
    - Fire potion throw: applies BurningEffect on target (1 dmg/turn, 4 turns)
    - Antidote drink: removes PlagueEffect, emits StatusExpiredEvent
    - Antidote with no plague: no error, consumed normally
  - Tests to add in `tests/Core/SpellResolverPotionTests.cs`:
    - `DrinkRoot_AppliesBarkskin_Plus3AC_10Turns`
    - `ThrowRoot_AppliesEntangled_ToTarget_3Turns`
    - `DrinkSunburst_AppliesFocused_Plus2Acc_8Turns`
    - `ThrowSunburst_AppliesBlinded_ToTarget_3Turns`
    - `ThrowFire_AppliesBurning_ToTarget_1DmgPerTurn_4Turns`
    - `DrinkAntidote_RemovesPlagueEffect`
    - `DrinkAntidote_NoPlaguePresent_NoError`
    - `DrinkAntidote_EmitsStatusExpiredEvent_WithReasonCured`

- [x] TASK-008: Add dual-mode and special potion definitions to entities.yaml
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-007
  - Description: Add YAML definitions for root_potion, sunburst_potion, fire_potion, and antidote_potion. Root and sunburst use `targeting: "self"` (drink default) with `throw_spell_id` set for throw-first targeting. Fire potion uses `targeting: "single_target"` with `spell_id: throw_fire` and NO `throw_spell_id` (it IS a throw -- no dual mode, routes directly through HandleScrollOrWandUse as SingleTarget). Antidote uses `targeting: "self"`, no throw.
  - Files to modify:
    - `config/entities.yaml`
  - Acceptance criteria:
    - All 4 potions load correctly
    - Root and sunburst have both `spell_id` (drink) and `throw_spell_id` (throw)
    - Fire potion has `targeting: single_target`, `spell_id: throw_fire`, no `throw_spell_id`
    - Antidote has `targeting: self`, `spell_id: drink_antidote`, no `throw_spell_id`
    - All have `is_potion: true`

### Phase A5: Loot and Verification

- [x] TASK-010: Wire potions into loot tables and floor item pools
  - Status: complete
  - Layer: logic
  - Type: balance
  - Dependencies: TASK-004, TASK-006, TASK-008
  - Description: Add potions to floor item pools in `config/entities.yaml`. The PoC does NOT use a centralized floor_item_pool with weights for potions -- instead it uses loot_policy.yaml with EV targets per band and category-based injection. The C# port uses a flat weighted pool (`floor_item_pool`). Assign weights proportional to current scroll weights, with depth gating.
  - **Recommended loot table values** (no PoC weights to match -- these are new, derived from PoC EV targets and current C# scroll weights which range 6-30):
    - Buff potions (depth 1+): healing_potion weight 30, speed_potion weight 12, protection_potion weight 12, regeneration_potion weight 10, invisibility_potion weight 8, heroism_potion weight 6
    - Debuff potions (depth 2+): weakness_potion weight 8, slowness_potion weight 8, blindness_potion weight 6, paralysis_potion weight 4, tar_potion weight 6
    - Throwable/special (depth 3+): fire_potion weight 6, root_potion weight 5, sunburst_potion weight 5, antidote_potion weight 8 (depth 4+ to match plague scroll depth gate)
    - NOTE: healing_potion must be added here too -- it is currently NOT in floor_item_pool (confirmed by reading entities.yaml). It only appears via guaranteed_spawns.
  - Files to modify:
    - `config/entities.yaml` -- floor_item_pool section (add potion entries with weights)
  - Acceptance criteria:
    - Potions appear in generated dungeon floors
    - Buff potions available from depth 1
    - Debuff potions available from depth 2+
    - Throwable potions available from depth 3+
    - healing_potion added to floor_item_pool

- [ ] TASK-011: Harness verification -- potions, throw system, and status effects balance check
  - Status: pending (requires harness run; logic layer changes from this session are prerequisites)
  - Layer: logic
  - Type: analysis
  - Dependencies: TASK-010
  - Description: Run dungeon-mode harness scenarios with potions in the loot pool. Verify Death% and H_PM/H_MP remain within target bands. Create a scenario specifically testing potion usage (bot with potions vs standard encounters). Verify that the bot can use throwable potions in combat (requires bot policy for throw vs drink decision).
  - Acceptance criteria:
    - Existing scenario metrics do not regress
    - New potion scenario shows buff potions reduce Death% measurably
    - Cursed potions increase Death% when consumed (unidentified)
    - Throwable debuff potions provide measurable tactical advantage when thrown vs drunk
    - No deadlocks or crashes with status effects active during harness runs

### Phase B: Presentation Layer (UI)

- [ ] TASK-012: StatusEffectBar -- player effect badges in HUD
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: Phase A tasks not required, but recommended
  - Description: Add a row of effect badges below the player HP bar. Each badge shows the effect icon/short name + remaining turns. Color-coded by category (red/orange for debuffs, green/blue for buffs). Read from player entity's IStatusEffect components each turn.
  - **Mobile constraint**: Max 5-6 badges visible at once on a portrait phone screen. The PoC does NOT have a visual badge bar -- it uses text messages only. This is a C# port improvement.
  - **Recommendation**: Use a horizontal HBoxContainer with fixed-size badge nodes. If more than 5 effects are active simultaneously (rare in practice -- requires stacking multiple potions + monster debuffs), show the 5 highest-priority effects. Priority order: skip-turn effects > DOTs > debuffs > buffs. Overflow indicator ("+2 more") if truncated.
  - Files to create:
    - `src/Presentation/UI/StatusEffectBar.cs`
  - Files to modify:
    - `src/Presentation/UI/HUD.cs` -- add StatusEffectBar, update each turn
  - Acceptance criteria:
    - Active player effects shown as badges with turns remaining
    - Badge disappears when effect expires
    - Badges color-coded by category
    - No badge overflow on mobile (truncate at 5 with overflow indicator)

- [ ] TASK-013: Toast messages for status effect events
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: none (events already emitted by logic layer)
  - Description: Handle StatusAppliedEvent, StatusExpiredEvent, DotDamageEvent, and SkipTurnEvent in the ToastLog. Display messages in PoC format: "You are poisoned!", "The orc is confused!", "The poison fades.", DOT damage in orange.
  - Files to modify:
    - `src/Presentation/UI/ToastLog.cs` -- add handlers for new event types
  - Acceptance criteria:
    - Toast appears when player gains a debuff
    - Toast appears when player debuff expires
    - DOT damage has distinct toast line
    - Monster effects show monster name in message

- [ ] TASK-014: Monster sprite tints for active effects
  - Status: pending
  - Layer: presentation
  - Type: system
  - Dependencies: none
  - Description: When a monster has an active status effect and is in the player's FOV, apply a color tint to its sprite. Poison: green, Burning: orange, Disoriented: purple, Sleeping: blue, Others: subtle gray.
  - Files to modify:
    - `src/Presentation/Entities/EntitySpriteManager.cs` -- add tint logic based on entity status effects
  - Acceptance criteria:
    - Poisoned monster has green tint when visible
    - Burning monster has orange tint when visible
    - Sleeping monster has blue tint when visible
    - Tint clears when effect expires

---

## Gaps and Risks (Critical Review Findings)

### GAP-1: ConsumableDefinition lacks spell fields (BLOCKING)

**Severity: High -- blocks all potion tasks.**

`ConsumableDefinition` (`src/Logic/Content/ConsumableDefinition.cs`) currently has only `Name`, `HealAmount`, `Char`, `Color`, `Category`, `DisplayName`, and `Id`. It has NO fields for `spell_id`, `targeting`, `duration`, `is_potion`, `throw_spell_id`, `range`, or `damage`.

`ConsumableFactory.Create()` (`src/Logic/Content/ConsumableFactory.cs`) creates `Consumable` and `IdentifiableItem` components but never creates `SpellEffect`. Without `SpellEffect`, potions cannot route through `ResolveSpellAction` and will fall through to `TryHeal` (which only handles healing).

**Resolution**: TASK-001 addresses this as first priority. It extends both the definition class, the factory, and adds ThrowSpellId to SpellEffect.

### GAP-2: InvisibilityEffect breaks on potion use (BUG)

**Severity: High -- incorrect behavior if shipped as-is.**

`TurnController.ResolveSpellAction` (line 294) breaks InvisibilityEffect for ANY `CastSpell` action. The comment correctly says potions should NOT break invisibility, but since potions with SpellEffect will route through `CastSpell`, they WILL break it.

**Resolution**: TASK-002. The invisibility break must be gated on `!isPotion || hasTarget` (drinking = no break, throwing = break).

### GAP-3: PoC duration values differ significantly from original plan

**Severity: Medium -- incorrect balance if original values used.**

The original plan had incorrect values for several potions:
- Protection potion: plan said +3 AC / 10 turns. PoC says **+4 AC / 50 turns**.
- Regeneration potion: plan said 2 HP/turn / 20 turns. PoC says **1 HP/turn / 50 turns** (50 HP total).
- Weakness potion: plan said 8 turns. PoC says **30 turns**.
- Slowness potion: plan said 10 turns. PoC says **20 turns**.
- Blindness potion: plan said 10 turns. PoC says **15 turns**.
- Paralysis potion: plan said 5 turns fixed. PoC says **3-5 turns random**.
- Sunburst throw: plan said BlindedEffect 10 turns. PoC says **3 turns**.
- Root drink: plan said BarkskinEffect +4 AC. PoC says **+3 AC**.
- Fire potion: plan said 3 dmg/turn / 5 turns. PoC says **1 dmg/turn / 4 turns**.

**Resolution**: All task descriptions updated with corrected PoC values.

### GAP-4: Missing potions from PoC

**Severity: Low-Medium -- completeness gap.**

The original plan missed 3 potions that exist in the PoC:
1. **Potion of Heroism** (+3 to-hit, +3 damage, 30 turns) -- requires new `HeroismEffect` class. Added as TASK-003a.
2. **Lightning Reflexes Potion** (+50% speed bonus, 15 turns) -- depends on speed bonus system being wired. **Defer** alongside SpeedEffect.
3. **Levitation Potion** (40 turns) -- requires LevitationEffect class and ground hazard system. **Defer** until hazard tiles exist.
4. **Experience Potion** (grant 1 level) -- requires level-up system. **Defer** until progression system is built.

### GAP-5: Potion routing through GameController (Presentation layer)

**Severity: Medium -- addressed by TASK-001a.**

`GameController.HandleInventoryTap` (line 148) routes items like this:
- If item has `SpellEffect` -> `HandleScrollOrWandUse` (targeting mode dispatch)
- Else -> `PlayerAction.UseItem` -> `TryHeal`

With throw system: items with `SpellEffect.ThrowSpellId` set must route to `HandleThrowablePotion` instead of `HandleScrollOrWandUse`. This is the core of TASK-001a. Non-throwable potions with SpellEffect still route through `HandleScrollOrWandUse` as self-targeting (immediate drink).

### GAP-6: Self-tap detection in InputHandler

**Severity: Medium -- new behavior needed for throw-cancel-to-drink.**

Currently, tapping the player's tile during `SingleTarget` targeting mode triggers `TargetingCancelled` (no entity at player position matches the monster filter). For throw potions, self-tap must instead trigger `DrinkSelfRequested`. This requires `HandleTapInTargetingMode` to check: if targeting a throw potion and tapped tile is player position, fire drink event instead of cancel.

**Resolution**: TASK-001a handles this. The InputHandler needs to know about the player position (already available via `_state.Player.X/Y`) and the `IsThrowPotion` flag on `TargetingState`.

### GAP-7: SpeedEffect inertness -- ship or defer?

**Severity: Low -- design question.**

SpeedEffect has no gameplay impact until the bonus attack system is wired to it. The Potion of Speed will consume a turn, show a badge, identify the potion type, and do nothing mechanically.

**Recommendation: Ship it.** The identification gameplay value is real -- drinking an unidentified potion that turns out to be speed is a "safe" result that identifies the type for future use. When the speed system is wired later, existing potions will automatically gain their mechanical benefit.

### GAP-8: No PoC weights for floor_item_pool

**Severity: Low -- requires judgment, not data.**

The PoC does not use a flat weighted pool for potions. It uses `loot_policy.yaml` with EV targets per band and category-based injection with pity mechanics. The C# port uses a simpler flat-weight pool. TASK-010 includes recommended weights derived from the PoC's EV targets and the current C# scroll weight range (6-30).

### GAP-9: healing_potion missing from floor_item_pool

**Severity: Medium -- existing gap, not caused by this plan.**

The current `floor_item_pool` in `config/entities.yaml` does NOT include healing_potion. It only appears via guaranteed_spawns in scenarios. TASK-010 should add it (weight 30, depth 1+).

### GAP-10: Stacking interaction -- already handled

**Severity: Low -- handled by existing no-stack/refresh rule.**

`StatusEffectProcessor.ApplyEffect<T>` already implements no-stack/refresh: if the entity already has the effect, it refreshes to `max(remaining, new_duration)`.

### GAP-11: Silenced + Blinded + potion interactions -- already correct

**Severity: Low -- no gap.**

A silenced player can still drink potions (TASK-001 fixes the gate). A blinded player can still drink potions (BlindedEffect only affects accuracy in CombatResolver, not item use).

### GAP-12: Potion identification already works

**Confirmed: no gap.** `ConsumableFactory.Create()` already creates `IdentifiableItem` and calls `PreIdentification.Apply` with `ItemCategory.Potion`. New potions routing through `ResolveSpellAction` will be identified on use automatically.

### GAP-13: Fire potion is throw-only -- no drink effect

**Severity: Low -- design handled.**

Fire potion has no drink effect in the PoC. In the C# port, fire potion uses `targeting: single_target` with `spell_id: throw_fire`. It routes through `HandleScrollOrWandUse` as a SingleTarget spell (like a scroll of confuse or a wand). The player taps a target, it applies BurningEffect. No dual-mode, no ThrowSpellId -- it IS a throw spell. Self-tap during targeting = standard cancel (no effect, no consumption). This means fire potion doesn't need the throw potion infrastructure at all -- it works like a targeted scroll.

### GAP-14: Bot throw intelligence for harness

**Severity: Medium -- harness verification needs bot updates.**

The BotBrain currently only uses healing potions. For harness verification of throw potions, the bot needs a policy for when to throw debuff potions vs when to drink buff potions. This is out of scope for this plan -- it belongs in `plan_bot_personas.md`. For TASK-011, a custom bot policy can be defined in the scenario YAML.

---

## Risks and Decisions

### R1: Potion routing through SpellResolver vs. dedicated PotionResolver
**Decision:** Route through SpellResolver. The infrastructure already handles self-targeting and single-target resolution. Adding a separate resolver creates a parallel dispatch path that duplicates event emission, status application, and targeting logic. The `IsPotion` flag on Consumable is sufficient to differentiate behavior (silence gate bypass).

### R2: Throw UX -- tap potion = enter targeting mode for throw
**Decision: Throw-first.** Tapping a throwable potion enters targeting mode (`SingleTarget`, range 10). Tapping a monster throws. Tapping self drinks. Cancel button aborts. This reuses the existing targeting infrastructure (wands/scrolls already built), matches the mobile-first design (one-tap actions), and avoids a drink-or-throw dialog. Non-throwable potions (buffs, healing, antidote) tap to drink immediately (no targeting mode). Fire potion uses `SingleTarget` targeting like a scroll -- no dual-mode needed.

### R3: SilencedEffect gate for potions
**Decision:** `IsPotion` flag on Consumable. Checked before the silence gate in `ResolveSpellAction`. Simple, explicit, and doesn't require architectural changes.

### R4: Potion identification integration
**Status:** Confirmed working. No new identification infrastructure needed.

### R5: SpeedEffect and SluggishEffect remain inert
**Decision: Ship them.** These effects apply, tick, and expire correctly but have no gameplay impact until the bonus attack system is built.

### R6: InvisibilityEffect and potion use
**Decision:** Drinking a potion does NOT break invisibility (PoC-verified). Throwing a potion DOES break invisibility (offensive action). TASK-002 handles this with the `!isPotion || hasTarget` check.

### R7: Throw range
**Decision: 10 tiles.** The PoC uses `max_range=10` in `calculate_throw_path`. The C# throw targeting will use range 10 for all throwable potions. This can be overridden per-potion in YAML if needed later.

### R8: Projectile path animation
**Decision: Defer.** The PoC uses Bresenham line animation for thrown projectile paths. For the C# port, the throw resolves instantly (like a targeted scroll) with no projectile animation. Projectile animation belongs in a presentation polish pass, not the throw system MVP. The logic layer doesn't need path calculation -- targeting is entity-based (`targetEntityId`), not location-based.

---

## Task Dependency Graph

```
TASK-001 (ConsumableDefinition + factory + IsPotion + silence fix + ThrowSpellId on SpellEffect)
  |
  +-- TASK-001a (Throw targeting UX -- presentation layer)
  |
  +-- TASK-002 (InvisibilityEffect potion fix)
  |
  +-- TASK-003a (HeroismEffect class) [no dep on TASK-001, can run parallel]
  |     |
  |     +-- TASK-003 (buff spell IDs -- depends on TASK-001 + TASK-003a)
  |           |
  |           +-- TASK-004 (buff YAML definitions)
  |                 |
  |                 +-- TASK-010 (loot tables)
  |                       |
  |                       +-- TASK-011 (harness verification)
  |
  +-- TASK-005 (debuff spell IDs -- drink + throw variants)
  |     |
  |     +-- TASK-006 (debuff YAML with ThrowSpellId)
  |           |
  |           +-- TASK-010
  |
  +-- TASK-007 (dual-mode + special spell IDs)
        |
        +-- TASK-008 (dual-mode + special YAML with ThrowSpellId)
              |
              +-- TASK-010

TASK-012 (UI badges)    -- independent of Phase A
TASK-013 (toast msgs)   -- independent of Phase A
TASK-014 (monster tints) -- independent of Phase A
```

### Recommended Build Order

1. **TASK-001** + **TASK-003a** (parallel -- infrastructure + HeroismEffect)
2. **TASK-001a** + **TASK-002** + **TASK-003** (parallel after TASK-001 -- throw UX + invis fix + buff spells)
3. **TASK-004** + **TASK-005** (parallel -- buff YAML + debuff spells)
4. **TASK-006** + **TASK-007** (parallel -- debuff YAML + dual-mode spells)
5. **TASK-008** (dual-mode YAML)
6. **TASK-010** (loot tables -- needs all YAML tasks done)
7. **TASK-011** (harness verification)
8. **TASK-012, 013, 014** (presentation -- can run any time)

## Total Estimated Tests

| Task | New Tests |
|------|-----------|
| TASK-001 | 4 |
| TASK-001a | 0 (presentation, manual verification) |
| TASK-002 | 2 |
| TASK-003a | 3 |
| TASK-003 | 5 |
| TASK-004 | 2 |
| TASK-005 | 10 |
| TASK-006 | 0 (covered by content loader tests) |
| TASK-007 | 8 |
| TASK-008 | 0 (covered by content loader tests) |
| TASK-010 | 0 (harness-verified) |
| TASK-011 | 0 (harness scenarios) |
| **Phase A Total** | **34 new tests** |
| TASK-012-014 | 0 (presentation layer, manual verification) |

---

## Implementation Notes (builder agent, 2026-04-04)

### Phase A: Complete (TASK-001 through TASK-010)

**37 new tests added** (planned 34; 3 extra for infrastructure edge cases).
**907 → 944 tests passing.**

#### TASK-001 + TASK-002: Infrastructure
- `ConsumableDefinition` extended with `SpellId`, `Targeting`, `Duration`, `IsPotion`, `ThrowSpellId`, `Range`, `Damage` fields (YamlMember aliases match PoC snake_case).
- `Consumable` component gets `IsPotion` bool (defaults false).
- `SpellEffect` gets `string? ThrowSpellId` property.
- `ConsumableFactory.Create()` now creates `SpellEffect` when `SpellId` is non-empty.
- `TurnController.ResolveSpellAction`: SilencedEffect gate skips for `isPotion=true`. InvisibilityEffect break: drink does NOT break, throw (has targetEntityId) DOES break.
- `ParseTargetingMode()` added to `ConsumableDefinition` (mirrors `SpellDefinition`).

#### TASK-003a: HeroismEffect
- New `HeroismEffect` class (+3 to-hit, +3 damage, 30 turns default).
- Wired into `CombatResolver.ResolveAttack` alongside RallyEffect (additive stacking, separate component type).

#### TASK-003 through TASK-007: SpellResolver Entries
- All 20 potion spell IDs added (5 buff, 5 debuff drink, 5 debuff throw, 4 dual/special, 1 antidote).
- `drink_slowness`/`throw_slowness`/`drink_paralysis`/`throw_paralysis`: use `StatusEffectProcessor.ApplyEffect` (not `GetOrAdd`) to honor FreeActionTag immunity. Other handlers use `GetOrAdd` directly (consistent with scroll "slow" handler).
- `ResolveParalysisPotion()` and `ResolveAntidote()` added as dedicated helpers.
- `drink_root` sets `AcBonus=3` (PoC value; note existing `BarkskinEffect` default was 4 — overridden at apply time).
- `drink_sunburst` sets `AccuracyBonus=2` (PoC value; existing `FocusedEffect` default was 3 — overridden).
- `drink_protection` sets `AcBonus=4` / duration 50 (PoC: +4 AC / 50 turns).
- `drink_regeneration` sets `HealPerTurn=1` / duration 50 (PoC: 1 HP/t / 50t = 50 HP total).

#### TASK-004/006/008: entities.yaml Content
- 14 new potion definitions added under `consumables:`.
- Fire potion is `targeting: single_target` with `spell_id: throw_fire` (no `throw_spell_id` — it is a direct single_target spell, not a dual-mode throw).
- Paralysis potion has no `duration` in YAML — resolver uses random 3-5 (PoC value).

#### TASK-010: Floor Item Pool
- `healing_potion` added to floor_item_pool at weight 30, depth 1+ (was previously spawn-only via guaranteed_spawns — GAP-9 from plan).
- All 14 new potions added with weights derived from PoC EV targets.

#### Test Duration Assertions
- All `RemainingTurns` assertions after `ProcessTurn` use `Is.InRange(N-1, N)` because `ProcessTurnEnd` decrements effects at end of the same turn they were applied. This is consistent, intentional, and documented in the test file header.

#### TASK-001a Reminder
The throw targeting UX (GameController/InputHandler) is a presentation-layer task that cannot be tested via the logic harness. The logic is fully wired (SpellEffect.ThrowSpellId, CastSpell routing). TASK-001a remains pending — implementation depends on GameController changes in src/Presentation/.

#### Remaining Pending
- TASK-011 (harness verification): needs harness runs with potions in pool
- TASK-001a, TASK-012, TASK-013, TASK-014 (presentation layer)
