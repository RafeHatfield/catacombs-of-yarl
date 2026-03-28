# Plan: Ranged Combat System

Status: [ ] Not started
PoC reference: services/ranged_combat_service.py (Phase 22.2)

---

## What It Is

A ranged attack system that makes bow/crossbow builds genuinely viable while punishing reckless close-range shooting. The core insight: ranged should be tactically interesting, not just "attack from far away for free."

---

## Range Band Table

OPTIMAL_MAX = 6 tiles (sweet spot)

| Distance | Outcome |
|----------|---------|
| d == 1 (adjacent) | Retaliation FIRST (free melee strike, player armor halved), then 25% damage shot |
| d == 2 | 50% damage |
| d == 3-6 | 100% damage (optimal) |
| d == 7 | 50% damage |
| d == 8 | 25% damage |
| d > 8 | DENIED — attack fails entirely, no roll |

---

## Retaliation-First Mechanic (Key Design Decision)

When player shoots at an adjacent enemy:
1. Enemy makes a free melee attack against player **first**
2. Player armor is halved for this retaliation strike
3. **If player survives**, shot proceeds at 25% damage
4. **If player dies**, shot doesn't happen

This creates a genuine risk: shooting point-blank is often a terrible idea. Encourages the player to maintain distance or switch to melee when engaged.

**Why halved armor?** The player is fumbling with a bow at point-blank range — not holding it defensively.

---

## Weapon Detection

Bows and crossbows have `is_ranged_weapon: true` on their `Equippable` component. Spears and thrown weapons are melee with reach — they do NOT use the ranged combat system. Distinction matters.

```yaml
shortbow:
  equippable:
    slot: main_hand
    damage: 1d6
    is_ranged_weapon: true
    accuracy: 2
```

---

## Knockback Proc

- 10% chance on any successful ranged hit
- Exactly 1-tile knockback in direction of shot
- Routes through movement service (respects walls/entities)
- This is the ranged build's natural "keep distance" tool

---

## Special Ammo / Quiver System (Phase 22.2.2)

Player has a quiver slot in equipment. Quiver holds a stack of ammo type.

**Ammo Types:**
- `fire_arrow` — deals fire damage on hit, creates small fire hazard at target tile
- `net_arrow` — applies SlowedEffect or EntangledEffect on hit

**Mechanics:**
- Normal arrows are infinite (no tracking needed — abstracted)
- Special arrows have count; auto-loaded from inventory when quiver runs out
- Without special ammo equipped, normal arrows are used

---

## Monster Ranged Combat

Monsters can also use ranged weapons if they spawn with bows. They use the same range band rules. This creates tactical flanking dynamics — a ranged-armed orc scout prefers to stay at distance 3-6.

---

## Metrics to Track (for harness)

- `ranged_attacks_made_by_player`
- `ranged_attacks_denied_out_of_range`
- `ranged_damage_dealt_by_player`
- `ranged_damage_penalty_total` (cumulative damage penalty from sub-optimal range)
- `ranged_adjacent_retaliations_triggered`
- `ranged_knockback_procs`

These are how you prove the ranged build is viable and the retaliation mechanic is doing its job.

---

## Ranged Build Viability Target

A ranged-focused run (longbow + special ammo) should be able to complete depth 1-5 at roughly equivalent death rates to a melee build. Not easier, not harder — just different. The harness proves this with ranged-persona bot runs.

---

## Implementation Notes

- `RangedCombatService.AttemptRangedAttack(attacker, target)` — main entry point
- Checks `is_ranged_weapon` flag on equipped weapon
- Calculates Chebyshev distance
- Routes through `RetaliationService` if d == 1
- Damage multiplier from range band table
- Knockback roll (10%) via `KnockbackService`
- All attacks still go through existing `CombatService` for actual damage resolution

## C# Port Checklist

- [ ] Range band table (constant or YAML-configurable)
- [ ] `is_ranged_weapon` flag on `Equippable`
- [ ] `RangedCombatService.AttemptRangedAttack()`
- [ ] Retaliation-first logic for d==1
- [ ] Armor halving during retaliation
- [ ] Knockback proc (10%)
- [ ] Quiver equipment slot
- [ ] Special ammo types (fire_arrow, net_arrow) with counts
- [ ] Monster ranged AI (maintain optimal range)
- [ ] Metric collection (all 6 metrics above)
- [ ] Scenario coverage: ranged_viability_arena, ranged_adjacent_punish_arena
