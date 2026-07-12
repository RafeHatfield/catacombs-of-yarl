# Ground Hazards

_Last verified: 2026-07-12 against commit 86b6f10_

**Source:** `src/Logic/Core/GroundHazard.cs`, `src/Logic/Combat/SpellResolver.cs`  
**Implementation status:** Fully implemented. Two hazard types: Fire and Poison Gas.

---

## Overview

Ground hazards are persistent tile effects that deal decaying damage over multiple turns. They are created by spells landing and affect any entity that occupies or moves through the hazard tile.

One hazard per tile. Adding a new hazard at an occupied tile replaces the existing one (no stacking). Hazards clear on floor transition.

---

## Decay Formula

Damage on each tick decreases linearly from `BaseDamage` down to 1:

```
CurrentDamage = floor(BaseDamage × RemainingTurns / MaxDuration)
```

The hazard is removed when `RemainingTurns` reaches 0.

### JustPlaced Timing

Hazards set `JustPlaced = true` on creation. On the first `TickEnvironment` call, `JustPlaced` is cleared and the hazard is skipped (no damage that turn). This prevents double-damage on the same turn a spell lands — the spell itself already dealt its direct damage.

---

## Fire Hazard

**Created by:** Fireball (scroll/wand), Fire Potion (throw)

| Parameter | Value |
|---|---|
| Type | Fire |
| BaseDamage | 3 |
| MaxDuration | 3 turns |
| Turn 1 damage | 3 |
| Turn 2 damage | 2 |
| Turn 3 damage | 1 |
| Total lingering | 6 damage over 3 turns |

Fire hazards cause `BurningEffect` on entities that take damage from them (the burning status is separate from the ground hazard damage — entities can be burning while standing in a fire tile).

---

## Poison Gas Hazard

**Created by:** Dragon Fart (scroll/wand of dragon_fart)

| Parameter | Value |
|---|---|
| Type | PoisonGas |
| BaseDamage | 6 |
| MaxDuration | 5 turns |
| Turn 1 damage | 6 |
| Turn 2 damage | 4 |
| Turn 3 damage | 3 |
| Turn 4 damage | 2 |
| Turn 5 damage | 1 |
| Total lingering | 16 damage over 5 turns |

Poison gas also applies `ConfusedEffect` (3 turns) to entities that take damage from it.

---

## Damage Tick Timing

Ground hazards tick in the environment phase at the end of each turn (after all entity actions). Each hazard:
1. Deals `CurrentDamage` to any entity on its tile
2. Decrements `RemainingTurns`
3. Is removed if `RemainingTurns ≤ 0`

---

## Notes

- Hazards affect both monsters and the player. Dropped a fireball at your feet? You take the lingering damage too.
- Hazard tick damage is raw (`GroundHazard.CurrentDamage` — linear decay, no resistance lookup) and applies to all entities. The damage-type resistance/vulnerability system (`src/Logic/Combat/DamageModifiers.cs`) is now live for direct combat damage but is not referenced by ground-hazard ticks.
- Ground hazards are distinct from **placed traps**, which are also implemented (9 types in `config/floor_traps.yaml`, placed by the floor generator via `FloorTrapRegistry`, resolved through `src/Logic/Combat/TrapActionResolver.cs`). Ground hazards are lingering area effects (from spells/abilities); traps are floor features triggered on step. See the systems INDEX and `tasks/plans/plan_interactive_props_traps.md` (completed).
