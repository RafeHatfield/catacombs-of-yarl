# Ground Hazards

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
- Fire resistance (fire_beetle tag) will reduce hazard damage when the resistance system is built, but currently raw damage applies to all.
- There are no traditional placed traps in the current implementation. Traps are planned for a future milestone (see `tasks/plans/plan_interactive_props_traps.md`). Ground hazards are the current equivalent of environmental danger.
