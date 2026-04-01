# Plan: Status Effects System

Status: [~] Phase 1 complete (2026-03-30). Phase 2 pending.
PoC reference: `~/development/rlike/components/status_effects.py` (~2600 lines), `~/development/rlike/balance/knowledge_config.py`

---

## 1. Overview

Duration-based effects applied to entities (player or monsters). Each effect has a lifecycle: apply → tick per turn (DOT/HOT, duration decrement) → expire. Effects gate combat, movement, and AI behavior. Many scroll/wand effects already exist as inert components — this system activates them.

**Scope boundary:** Entity-attached effects only. Tile-based ground hazards (fire/poison floor tiles from Fireball/Dragon Fart) are deferred to `plan_traps_chests_features`.

**PoC alignment:** All effects in this plan exist in the PoC unless explicitly labeled **[NEW DESIGN]**. Effects that were in early drafts but are not in the PoC have been removed to a deferred section at the bottom.

---

## 2. Architecture

### 2.1 IStatusEffect Marker Interface

All status effect components implement `IStatusEffect`. This is how `StatusEffectProcessor` finds all effects on an entity without a hardcoded list:

```csharp
public interface IStatusEffect : IComponent
{
    string EffectName { get; }
    int RemainingTurns { get; set; }
    bool IsPermanent { get; }  // true = never ticked down (e.g. TauntedEffect)
}
```

`StatusEffectProcessor` iterates `entity.GetAll<IStatusEffect>()` for tick/expire logic.

### 2.2 Lifecycle Engine

```
TurnController.ProcessTurn()
  ├── [turn start] StatusEffectProcessor.ProcessTurnStart(entity, events)
  │     ├── DOT tick (PoisonEffect, BurningEffect, PlagueEffect)
  │     ├── HOT tick (RegenerationEffect)
  │     ├── Skip-turn check (SlowedEffect, ImmobilizedEffect, EntangledEffect, SleepEffect)
  │     └── Returns SkipTurn=true if entity cannot act
  │
  ├── [action resolution — gated by effects]
  │     ├── Move: blocked by ImmobilizedEffect, EntangledEffect; random dir if DisorientationEffect
  │     ├── Attack: weapon blocked by DisarmedEffect; target override if EnragedEffect/TauntedEffect
  │     └── Spell/Wand: blocked by SilencedEffect
  │
  └── [turn end] StatusEffectProcessor.ProcessTurnEnd(entity, events)
        ├── Decrement RemainingTurns on non-permanent effects
        └── Remove expired effects → emit StatusExpiredEvent
```

### 2.3 No-Stack / Refresh Rule

Re-applying an effect that already exists refreshes the duration instead of stacking:

```csharp
public static T ApplyEffect<T>(Entity entity, int duration) where T : IStatusEffect, new()
{
    var existing = entity.Get<T>();
    if (existing != null)
    {
        existing.RemainingTurns = Math.Max(existing.RemainingTurns, duration);
        return existing;
    }
    var effect = new T { RemainingTurns = duration };
    entity.Add(effect);
    return effect;
}
```

### 2.4 Wake on Damage (Attack Only)

`SleepEffect` breaks when the entity takes **attack damage** (not DOT). DOT (poison, burning) ticks normally while an entity sleeps — the entity takes damage but stays asleep. This matches PoC behavior.

Check is in `CombatResolver.ApplyDamage` (attack path only, not DOT path):
```csharp
if (target.Has<SleepEffect>())
{
    target.Remove<SleepEffect>();
    events.Add(new StatusExpiredEvent(target.Id, "sleep", "woke_on_damage"));
}
```

### 2.5 Shield/Protection/Barkskin — Combat-Time Read

**[Deliberate deviation from PoC]:** The PoC mutates `base_defense` directly on apply/remove. The C# implementation reads active effects at combat resolution time instead. This avoids stat contamination if an effect expires during combat resolution and simplifies the mental model.

```csharp
// In CombatResolver.GetEffectiveAC(entity):
int ac = entity.Require<Fighter>().ArmorClass;
if (entity.Has<ShieldEffect>()) ac += entity.Require<ShieldEffect>().AcBonus;      // +4
if (entity.Has<ProtectionEffect>()) ac += entity.Require<ProtectionEffect>().AcBonus; // +3
if (entity.Has<BarkskinEffect>()) ac += entity.Require<BarkskinEffect>().AcBonus;   // +4
return ac;
```

All three stack additively. The existing base `ArmorClass` stat is never mutated by status effects.

### 2.6 ConfusedEffect → DisorientationEffect (Consolidated)

**The PoC has no separate `ConfusedEffect`.** It uses `DisorientationEffect` which internally swaps AI to `ConfusedMonster` (random movement). The C# codebase has both as inert stubs. **Resolution: remove the `ConfusedEffect` stub; `DisorientationEffect` is the canonical confused-movement effect for both players and monsters.** Confused movement is ONLY movement randomization — not attack randomization.

### 2.7 SpeedEffect / SluggishEffect — Speed Bonus Ratio

The PoC implements speed as a bonus ratio that affects additional attack chances (from fast equipment), not extra turns. `SpeedEffect` increases this ratio; `SluggishEffect` decreases it. Neither grants a full extra turn. These are distinct from `SlowedEffect` (which skips turns).

### 2.8 EnragedEffect — HostileToAll Flag

The PoC switches the monster's faction to `HOSTILE_ALL`. The C# codebase doesn't have a full faction system yet (`plan_faction_system.md` is unstarted). Workaround: add a `HostileToAll` boolean field to monster entities (or to `AiComponent`) that EnragedEffect sets on apply and clears on remove. Monster AI checks `HostileToAll` before faction-based targeting rules.

### 2.9 TauntedEffect — Duration 1000

The PoC passes `duration=1000` to TauntedEffect (effectively permanent through any combat encounter). The C# implementation should match: `RemainingTurns = 1000`, `IsPermanent = false`. Tests should verify the effect persists through typical combat without expiring.

### 2.10 Floor Transition Policy

All status effects are cleared when the player descends to a new floor. This is the simplest policy and avoids confusing carry-over. Implementation: call `ClearAllEffects(player)` in `DungeonFloorBuilder` when building a new floor.

---

## 3. Prerequisite: Tags on MonsterDefinition

`PlagueEffect` only applies to `corporeal_flesh` entities. The PoC defines this as a YAML string tag array. Add to `MonsterDefinition`:

```csharp
[YamlMember(Alias = "tags")]
public List<string> Tags { get; set; } = new();
```

Add `typeof(List<string>)` registration to `AotObjectFactory` (likely already registered). Populate relevant monsters in `entities.yaml`:
- Living humanoids (orc, zombie, skeleton, mummy): `["corporeal_flesh", "humanoid"]`
- Slimes: `["corporeal_flesh"]` (no humanoid)
- Undead that are NOT corporeal (lich): no `corporeal_flesh` tag

This is a Phase 1 prerequisite task — no behavior changes, just data plumbing.

---

## 4. Existing Inert Components (Activated by This Plan)

These exist in `src/Logic/Combat/StatusEffects/` but do nothing yet:
`SlowedEffect`, `ImmobilizedEffect`, `EnragedEffect`, `DisarmedEffect`, `PlagueEffect`, `TauntedEffect`, `FearEffect`, `InvisibilityEffect`, `ShieldEffect`, `SilencedEffect`, `DisorientationEffect`

**Remove:** `ConfusedEffect` stub — superseded by `DisorientationEffect`.
**Remove:** `HasteEffect` stub — not in PoC, deferred (see Section 10).

---

## 5. New Components Needed

| Component | Fields | Source | PoC Class |
|-----------|--------|--------|-----------|
| `PoisonEffect` | `RemainingTurns=10`, `DamagePerTurn=2` | Plague zombie hit, Dragon Fart | `PoisonEffect` |
| `BurningEffect` | `RemainingTurns=5`, `DamagePerTurn=3` | Fire hazards (future) | `BurningEffect` |
| `BlindedEffect` | `RemainingTurns=10`, `AccuracyPenalty=4` | Sunburst Potion | `BlindedEffect` |
| `SleepEffect` | `RemainingTurns=3`, wakes on attack damage | Dragon Fart secondary | `SleepEffect` |
| `WeaknessEffect` | `RemainingTurns=8`, `DamagePenalty=2` | Monster abilities | `WeaknessEffect` |
| `ProtectionEffect` | `RemainingTurns=10`, `AcBonus=3` | Potion of Protection | `ProtectionEffect` |
| `RegenerationEffect` | `RemainingTurns=20`, `HealPerTurn=2` | Regeneration ring | `RegenerationEffect` |
| `SpeedEffect` | `RemainingTurns=20`, `SpeedBonusRatio=0.5` | Potion of Speed | `SpeedEffect` |
| `SluggishEffect` | `RemainingTurns=10`, `SpeedPenaltyRatio=0.5` | Monster abilities | `SluggishEffect` |
| `BarkskinEffect` | `RemainingTurns=8`, `AcBonus=4` | Root Potion secondary | `BarkskinEffect` |
| `FocusedEffect` | `RemainingTurns=8`, `AccuracyBonus=3` | Sunburst Potion secondary | `FocusedEffect` |
| `EntangledEffect` | `RemainingTurns=5` | Root Potion, root trap | `EntangledEffect` |

---

## 6. New TurnEvents

Add to `src/Logic/Core/TurnEvent.cs`:

```csharp
public sealed record StatusExpiredEvent(int EntityId, string EffectName, string Reason = "duration") : TurnEvent;
public sealed record DotDamageEvent(int EntityId, string EffectName, int Damage) : TurnEvent;
public sealed record HotHealEvent(int EntityId, string EffectName, int Amount) : TurnEvent;
public sealed record SkipTurnEvent(int EntityId, string EffectName) : TurnEvent;
```

`StatusAppliedEvent` already exists from Phase 3 scroll work.

---

## 7. Phase 1 — Lifecycle Engine

**Goal:** Infrastructure that ticks, expires, and DOT/HOT processes effects. No behavioral gating yet. Activates the lifecycle without changing combat/movement decisions.

### Prerequisites
- [x] Add `IStatusEffect` marker interface
- [x] Add `Tags` field to `MonsterDefinition` + populate `entities.yaml` (already present)
- [x] Remove `ConfusedEffect` and `HasteEffect` stubs (confusion→DisorientationEffect, haste→SpeedEffect)
- [x] Add `typeof(List<string>)` to `AotObjectFactory` if not present (already registered)

### New Files
- `src/Logic/ECS/IStatusEffect.cs` — marker interface
- `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs` — lifecycle engine
- `src/Logic/Combat/StatusEffects/PoisonEffect.cs`
- `src/Logic/Combat/StatusEffects/BurningEffect.cs`
- `src/Logic/Combat/StatusEffects/BlindedEffect.cs`
- `src/Logic/Combat/StatusEffects/SleepEffect.cs`
- `src/Logic/Combat/StatusEffects/WeaknessEffect.cs`
- `src/Logic/Combat/StatusEffects/ProtectionEffect.cs`
- `src/Logic/Combat/StatusEffects/RegenerationEffect.cs`
- `src/Logic/Combat/StatusEffects/SpeedEffect.cs`
- `src/Logic/Combat/StatusEffects/SluggishEffect.cs`
- `src/Logic/Combat/StatusEffects/BarkskinEffect.cs`
- `src/Logic/Combat/StatusEffects/FocusedEffect.cs`
- `src/Logic/Combat/StatusEffects/EntangledEffect.cs`

### Files to Modify
| File | Change |
|------|--------|
| `src/Logic/Core/TurnController.cs` | Call `ProcessTurnStart` before entity acts; `ProcessTurnEnd` after |
| `src/Logic/Core/TurnEvent.cs` | Add 4 new events |
| `src/Logic/Combat/CombatResolver.cs` | Call `StatusEffectProcessor.OnDamageTaken` on attack damage (wakes Sleep) |
| `src/Logic/Core/DungeonFloorBuilder.cs` | Call `ClearAllEffects(player)` on floor descent |

### PoC-Verified Values
- Poison: 2 damage/turn, 10 turns default
- Burning: 3 damage/turn, 5 turns default
- Plague: 1 damage/turn, 20 turns (already on PlagueEffect)
- Regeneration: 2 HP/turn
- Slow: `turn_counter % 2 == 1` → skip odd-numbered turns
- Sleep: 3 turns, wakes on **attack damage only** (DOT does NOT wake sleep)

### Acceptance Criteria
- [x] `IStatusEffect` interface implemented by all status effect components
- [x] `StatusEffectProcessor` finds effects via `entity.GetAllComponents().OfType<IStatusEffect>()`
- [x] `PoisonEffect` ticks 2 dmg/turn, emits `DotDamageEvent`
- [x] `RegenerationEffect` heals 2 HP/turn, emits `HotHealEvent`
- [x] `SlowedEffect` skips odd-numbered turns, emits `SkipTurnEvent`
- [x] `ImmobilizedEffect` skips all turns for duration
- [x] `SleepEffect` skips turns; wakes on attack damage; NOT woken by DOT
- [x] Sleeping entity takes DOT damage but stays asleep
- [x] All effects decrement `RemainingTurns` at turn end
- [x] Effects at RemainingTurns=0 emit `StatusExpiredEvent` and are removed
- [x] Re-applying existing effect refreshes duration (no duplicate components)
- [x] All effects cleared on floor descent
- [x] Scenario harness runs correctly with SlowedEffect active (no deadlock)
- [x] Tags field loads from YAML correctly for `corporeal_flesh` monsters

### Implementation Notes (2026-03-30)
- Timing model: END-based (ProcessTurnStart before action, ProcessTurnEnd after action per entity)
- Effects applied to a monster during the player's turn get one decrement from monster's ProcessTurnEnd in the same round. Two existing spell scenario test assertions updated to reflect this.
- `RemoveEffect` dispatch table in StatusEffectProcessor handles removal since Entity.Remove<T> requires generic type — new effect types must be registered there.
- `GetAllComponents().OfType<IStatusEffect>()` used instead of `GetAll<IStatusEffect>()` (the ECS doesn't have a polymorphic GetAll).
- Tags were already present on monsters in entities.yaml; List<string> was already in AotObjectFactory.
- ConfusedEffect → DisorientationEffect (SpellResolver "confusion" spell); HasteEffect → SpeedEffect ("haste" spell). SingleTargetSpellTests updated accordingly.

### Tests — `tests/Core/StatusEffectLifecycleTests.cs` (24 tests)
```
- Poison_TicksDamageEachTurn
- Poison_ExpiredAfterDuration
- Poison_DotEventEmittedPerTick
- Burning_TicksDamageEachTurn
- Regeneration_HealsEachTurn
- Regeneration_HotEventEmitted
- Slow_SkipsOddTurns
- Slow_ActsOnEvenTurns
- Slow_SkipTurnEventEmitted
- Immobilized_SkipsAllTurns
- Sleep_SkipsTurns
- Sleep_WakesOnAttackDamage
- Sleep_DoesNotWakeOnDotDamage
- Sleep_WakeEmitsExpiredEvent
- EffectExpiry_RemainingTurnsDecrements
- EffectExpiry_RemovesComponentAtZero
- EffectExpiry_ExpiredEventEmitted
- NoStack_ReapplyRefreshesDuration
- NoStack_DoesNotAddDuplicate
- MultipleEffects_AllTickIndependently
- MultipleEffects_OneExpiresOtherContinues
- Plague_TicksDamageEachTurn
- FloorDescent_ClearsAllEffects
- HarnessRun_SlowedPlayer_DoesNotDeadlock
```

---

## 8. Phase 2 — Movement Effects

**Goal:** Effects that change or block movement.

### Files to Modify
| File | Change |
|------|--------|
| `src/Logic/Core/TurnController.cs` | Player move: check ImmobilizedEffect/EntangledEffect (block); DisorientationEffect (random dir) |
| `src/Logic/AI/MonsterAi.cs` | Monster move: check ImmobilizedEffect/EntangledEffect (skip move); FearEffect (move away from player); DisorientationEffect (random move) |

### Behavior Specs
- **DisorientationEffect**: movement direction replaced with a random direction each turn. Bump into wall = no movement this turn. Movement ONLY — attacks not randomized (PoC-verified).
- **EntangledEffect**: cannot move. CAN still attack adjacent targets.
- **ImmobilizedEffect**: cannot move. Combat gating in Phase 3.
- **FearEffect**: monster moves to maximize distance from player. If cornered (no valid move away), stays in place. Does NOT attack while feared.
- **Player DisorientationEffect**: input direction is ignored; a random direction is chosen instead. No UI blocking — the player taps, the move goes elsewhere. A toast message should explain.

### Acceptance Criteria
- [ ] Disorientated player moves in a random direction (ignoring input)
- [ ] Disorientated monster moves randomly
- [ ] Confused movement is ONLY movement — adjacent enemies not auto-attacked
- [ ] Entangled player cannot move
- [ ] Entangled player can attack adjacent monster
- [ ] Entangled monster cannot move but can attack
- [ ] Immobilized player cannot move
- [ ] Fear monster moves away from player
- [ ] Fear monster cornered → stays in place, does not attack
- [ ] Fear monster does not approach player even if path exists

### Tests — `tests/Core/MovementEffectTests.cs` (20 tests)
```
- Disorientation_PlayerMovesRandomDirection
- Disorientation_MonsterMovesRandomDirection
- Disorientation_RandomDirectionChangesEachTurn
- Disorientation_WallBump_NoMovementThisTurn
- Disorientation_MovementOnly_NoAttackRandomization
- Entangled_PlayerCannotMove
- Entangled_PlayerCanAttackAdjacent
- Entangled_MonsterCannotMove
- Entangled_MonsterCanAttackAdjacent
- Immobilized_PlayerCannotMove
- Immobilized_MonsterCannotMove
- Fear_MonsterMovesAwayFromPlayer
- Fear_MonsterCornered_StaysInPlace
- Fear_MonsterDoesNotApproach
- Fear_MonsterDoesNotAttackWhileFeared
- Disorientation_ExpiresAfterDuration_NormalMovement
- Fear_ExpiresAfterDuration_AIRestored
- Entangled_ExpiresAfterDuration_MovementRestored
- Slow_PlayerSkipsMoveTurn
- Slow_MonsterSkipsMoveTurn
```

---

## 9. Phase 3 — Combat Effects

**Goal:** Effects that gate or modify combat resolution.

### Files to Modify
| File | Change |
|------|--------|
| `src/Logic/Combat/CombatResolver.cs` | `GetEffectiveAC`: read Shield/Protection/Barkskin; read Weakness/Blinded for hit/damage; check InvisibilityEffect for targeting |
| `src/Logic/Core/TurnController.cs` | Check SilencedEffect before spell/wand; check DisarmedEffect before attack; check ImmobilizedEffect before any action |
| `src/Logic/Combat/CombatResolver.cs` | InvisibilityEffect breaks on attacker making an attack; wake SleepEffect on attack damage |

### Behavior Specs (PoC-verified)
- **DisarmedEffect**: weapon attack cancelled; emit `AttackEvent(Hit: false, FailReason: "disarmed")`
- **SilencedEffect**: blocks scroll AND wand use; does NOT block potions or melee
- **ShieldEffect**: +4 effective AC (combat-time read)
- **ProtectionEffect**: +3 effective AC (combat-time read)
- **BarkskinEffect**: +4 effective AC (combat-time read)
- **WeaknessEffect**: -2 damage (minimum 1)
- **BlindedEffect**: -4 accuracy penalty
- **InvisibilityEffect**: monsters cannot target the invisible entity as an attack target; breaks when invisible entity makes any attack or casts a spell; does NOT break on item use or taking damage
- **ImmobilizedEffect**: prevents ALL actions (move AND attack AND spell)

### Acceptance Criteria
- [ ] Disarmed player cannot make weapon attack
- [ ] Disarmed monster cannot make weapon attack
- [ ] Silenced entity cannot use scrolls
- [ ] Silenced entity cannot use wands
- [ ] Silenced entity CAN use potions and make melee attacks
- [ ] Shield adds +4 effective AC via `GetEffectiveAC`
- [ ] Protection adds +3 effective AC
- [ ] Barkskin adds +4 effective AC
- [ ] All three stack additively
- [ ] Weakness reduces damage by 2 (minimum 1)
- [ ] Blinded entity has -4 accuracy penalty applied in hit calculation
- [ ] Invisible player not targeted by monster AI
- [ ] InvisibilityEffect removed when player attacks
- [ ] InvisibilityEffect removed when player casts spell
- [ ] InvisibilityEffect persists through item use
- [ ] Immobilized entity cannot attack
- [ ] Sleeping entity wakes on attack damage (covered in Phase 1, verified in combat context here)

### Tests — `tests/Core/CombatEffectTests.cs` (26 tests)
```
- Disarmed_PlayerCannotAttack
- Disarmed_MonsterCannotAttack
- Disarmed_AttackEmitsFailureEvent
- Disarmed_ExpiresNextTurn_CanAttackAgain
- Silenced_BlocksScrollUse
- Silenced_BlocksWandUse
- Silenced_DoesNotBlockPotion
- Silenced_DoesNotBlockMelee
- Shield_IncreasesEffectiveAC
- Protection_IncreasesEffectiveAC
- Barkskin_IncreasesEffectiveAC
- AllThreeDefenseEffects_StackAdditively
- Weakness_ReducesDamage
- Weakness_MinimumOneDamage
- Blinded_ReducesHitChance
- Invisible_MonsterDoesNotTargetPlayer
- Invisible_BreaksOnPlayerAttack
- Invisible_BreaksOnPlayerSpellCast
- Invisible_PersistsThroughItemUse
- Invisible_MonsterAttacksAfterBreak
- Immobilized_CannotAttack
- Immobilized_CannotCastSpell
- Enraged_AttacksNearestEntity
- Enraged_AttacksFriendlyMonster
- TauntedEffect_AlwaysTargetsPlayer
- Plague_DamagesOnlyCorporealFleshMonsters
```

---

## 10. Phase 4 — AI Override Effects

**Goal:** Effects that change AI targeting and behavior. EnragedEffect hostile-all, TauntedEffect forced targeting, DisorientationEffect (AI already handled in Phase 2), FearEffect flee (AI already handled in Phase 2) — this phase polishes and handles edge cases.

### EnragedEffect: HostileToAll Implementation

Since the faction system doesn't exist yet, add `bool HostileToAll` to `AiComponent`. EnragedEffect sets this on apply, clears on remove. Monster AI checks `HostileToAll` before faction targeting rules:

```csharp
// In MonsterAi.ChooseTarget:
if (aiComp.HostileToAll)
    return FindNearestEntity(state, monster);  // any entity, not just player
else
    return state.Player;  // normal targeting
```

When a monster with `HostileToAll` attacks another monster, that monster retaliates. This is automatic — the attacked monster sees an attacker that isn't the player, checks if it should fight back (yes, it was attacked), and targets the aggressor next turn.

### SpeedEffect / SluggishEffect: Speed Bonus Ratio

**[PoC behavior]:** Speed in the PoC affects `speed_bonus_ratio` — the chance of getting an additional attack from fast equipment. The C# codebase doesn't have bonus attacks yet. For now, SpeedEffect and SluggishEffect are applied but effectively inert until the bonus attack system (part of combat depth plan) is implemented. They should still be applied, ticked, and expired correctly — just with no combat outcome yet. Flag this in code with a TODO comment.

### Acceptance Criteria
- [ ] EnragedEffect sets `AiComponent.HostileToAll = true` on apply
- [ ] EnragedEffect clears `HostileToAll` on remove
- [ ] Enraged monster attacks nearest entity (any — player or monster)
- [ ] Attacked monster retaliates against enraged monster next turn
- [ ] TauntedEffect monster always targets player, overrides normal AI
- [ ] TauntedEffect lasts 1000 turns (effectively permanent through any encounter)
- [ ] SpeedEffect and SluggishEffect apply/tick/expire correctly (behavior is a TODO)
- [ ] DisorientationEffect with AI: monster moves randomly, does not pursue

### Tests — `tests/Core/AiEffectTests.cs` (18 tests)
```
- Enraged_SetsHostileToAll
- Enraged_ClearsHostileToAllOnExpiry
- Enraged_AttacksNearestEntity_PlayerOrMonster
- Enraged_AttackedMonster_RetaliatesNextTurn
- Enraged_ExpiresAfterDuration_NormalAI
- Taunted_AlwaysTargetsPlayer
- Taunted_IgnoresCloserMonsterTargets
- Taunted_Duration1000_PersistsThroughCombat
- SpeedEffect_Applies_NoErrors
- SpeedEffect_Expires_AfterDuration
- SluggishEffect_Applies_NoErrors
- SluggishEffect_Expires_AfterDuration
- Disorientation_MonsterMovesRandom_DoesNotPursue
- AggravatedEffect_TargetsSpecifiedFaction (stub — no faction system yet)
- Fear_MonsterFlees_NotAttacking
- Fear_ExpiresAfterDuration_MonsterAttacksAgain
- MultiEffect_ImmobilizedPlusFear_ImmobilizedWins
- MultiEffect_TauntedPlusDisorientation_TauntedWins (targeting, disorientation affects movement)
```

---

## 11. Phase 5 — UI Display

**Goal:** Active effects visible to the player. Effect badges in HUD, toasts on apply/expire, monster color tints.

### New Files
- `src/Presentation/UI/StatusEffectBar.cs` — row of effect badges under player HP bar

### Files to Modify
| File | Change |
|------|--------|
| `src/Presentation/UI/HUD.cs` | Add StatusEffectBar; update each turn |
| `src/Presentation/UI/ToastLog.cs` | Handle `StatusAppliedEvent`, `StatusExpiredEvent`, `DotDamageEvent` |
| `src/Presentation/Entities/EntitySpriteManager.cs` | Color tint on monster with active debuff |

### Badge Format
Short name + turns remaining: `[Poison 7]`, `[Shield 4]`. Color by category:
- Offensive debuffs: red/orange (`PoisonEffect`, `SlowedEffect`, `ConfusedEffect`, `DisarmedEffect`)
- Defensive buffs: green/blue (`ShieldEffect`, `InvisibilityEffect`, `ProtectionEffect`)
- Neutral: gray (`SilencedEffect`, `ImmobilizedEffect`)

### Toast Messages (PoC-verified format)
- Apply: `"You are poisoned!"` / `"The orc is confused!"`
- Expire: `"The poison fades."` / `"You are no longer slowed."`
- DOT: shown as a distinct combat log line in orange

### Monster Tint (visible when in FOV)
- Poisoned: green tint
- Burning: orange tint
- Confused/Disoriented: purple tint
- Sleeping: blue tint
- Others: subtle gray tint

### Acceptance Criteria
- [ ] Active player effects shown as badges with turns remaining
- [ ] Badge disappears when effect expires
- [ ] Toast appears when player gains a debuff
- [ ] Toast appears when player debuff expires
- [ ] DOT damage has distinct toast line (orange color)
- [ ] Monster sprite tints visually when affected by debuff in FOV

### Tests — `tests/Core/StatusEffectEventTests.cs` (8 logic-layer tests)
```
- StatusAppliedEvent_InTurnResult_ForPlayerEffect
- StatusAppliedEvent_InTurnResult_ForMonsterEffect
- StatusExpiredEvent_InTurnResult_WhenDurationHits0
- DotDamageEvent_InTurnResult_WithCorrectDamageAmount
- HotHealEvent_InTurnResult_WithCorrectHealAmount
- MultipleEffectsExpiring_AllEventsEmitted
- EffectRefresh_NoDoubleApplyEvent
- SkipTurnEvent_EmittedWhenSlowSkips
```

---

## 12. Integration Table

| System | Phase | Change |
|--------|-------|--------|
| `TurnController` | 1 | `ProcessTurnStart`/`End` calls on each entity |
| `TurnController` | 3, 4 | SilencedEffect gate (spells), DisarmedEffect gate (attacks), ImmobilizedEffect gate (all actions), EnragedEffect target override |
| `CombatResolver` | 3 | `GetEffectiveAC` reads Shield/Protection/Barkskin; Weakness/Blinded modifiers; InvisibilityEffect break; `OnDamageTaken` wakes Sleep |
| `MonsterAi` | 2, 4 | Disorientation random move; Fear flee; EnragedEffect HostileToAll; TauntedEffect force-target-player |
| `SpellResolver` | 3 | SilencedEffect gate before spell resolution |
| `AiComponent` | 4 | Add `HostileToAll` boolean field |
| `MonsterDefinition` | 1 | Add `Tags: List<string>` |
| `DungeonFloorBuilder` | 1 | `ClearAllEffects` on floor descent |
| `TurnEvent` | 1 | 4 new events |
| `HUD` | 5 | StatusEffectBar |
| `ToastLog` | 5 | New event handlers |
| `EntitySpriteManager` | 5 | Tint on effect |

---

## 13. Risks & Decisions

1. **EnragedEffect without faction system**: Using `HostileToAll` flag on `AiComponent` as a minimal shim. When `plan_faction_system` lands, replace this with the proper faction switching.

2. **SpeedEffect/SluggishEffect are inert**: No bonus attack system yet. Apply/tick/expire correctly but leave a `// TODO: apply speed_bonus_ratio when bonus attack system lands` comment in the handler.

3. **DisorientationEffect on player**: Player input is intercepted and replaced with a random direction. The tap still consumes a turn — player sees a toast "You stumble in confusion!" but their move goes elsewhere. This is the correct UX for a terminal roguelike translated to mobile.

4. **AggravatedEffect depends on faction system**: The aggravation scroll applies `AggravatedEffect` targeting a specific faction. Without the faction system, this is a stub that emits `StatusAppliedEvent` but has no behavioral effect. Flag clearly with a TODO.

5. **CombatResolver AC reads**: With Shield, Protection, and Barkskin all read in `GetEffectiveAC`, and Weakness/Blinded in the hit formula, `CombatResolver` grows. Extract `EffectiveStatsReader` helper if the resolver exceeds ~200 lines.

6. **Bot harness handling of SkipTurnEvent**: After Phase 1, run a harness scenario with a slowed player. If it deadlocks or produces invalid metrics, update `BotBrain` to handle SkipTurn gracefully before proceeding to later phases.

---

## 14. Total Test Count

| Phase | Test File | Count |
|-------|-----------|-------|
| 1 | StatusEffectLifecycleTests.cs | 24 |
| 2 | MovementEffectTests.cs | 20 |
| 3 | CombatEffectTests.cs | 26 |
| 4 | AiEffectTests.cs | 18 |
| 5 | StatusEffectEventTests.cs | 8 |
| **Total** | | **96** |

---

## 15. Deferred Effects (Not in PoC — Documented for Future Plan)

These effects were in early drafts but are not implemented in `~/development/rlike`. Do not implement until a separate plan is written and reviewed.

| Effect | Reason Deferred |
|--------|----------------|
| `HasteEffect` (double-turn action) | PoC has `SpeedEffect` (speed_bonus_ratio modifier) only; double-turn is new design requiring careful architecture for TurnController re-entrancy and animation sequencing |
| `HeroismEffect` | "Future item" in PoC — no scroll/item source exists |
| `LevitationEffect` | "Future item" in PoC — requires hazard tile system to be meaningful |
| `OathEmbersEffect` | Boss-specific (Phase 22.1.1 Oath of Embers build) |
| `OathVenomEffect` | Boss-specific (Phase 22.1.1 Oath of Venom build) |
| `OathChainsEffect` | Boss-specific (Phase 22.1.1 Oath of Chains build) |
| `WardAgainstDrainEffect` | Requires wraith enemy (plan_monster_specials) |
| `SoulWardEffect` | Requires wraith Soul Bolt attack (plan_monster_specials) |
| `IdentifyModeEffect` | Requires identification system (plan_identification_system) |
| `EngulfedEffect` | Deferred slime ability (deferred_slime_abilities.md) |
