# Plan: Ranged Combat System

Status: [ ] Not started
PoC reference: services/ranged_combat_service.py (Phase 22.2)

---

## What It Is

A ranged attack system that makes bow/crossbow builds genuinely viable while punishing reckless close-range shooting. The core insight: ranged should be tactically interesting, not just "attack from far away for free."

---

## Range Band Table

OPTIMAL_MAX = 6 tiles (sweet spot). Distance is Chebyshev (king's move).

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
- **Note:** Chains oath does NOT add +1 to ranged knockback (unlike melee). Intentional — ranged knockback is its own independent mechanic.

---

## Special Ammo / Quiver System (Phase 22.2.2)

Player has a quiver slot in equipment. Quiver holds a stack of one ammo type.

**Ammo Types:**

| Type | Effect | Chance | Duration | Stack Size |
|------|--------|--------|----------|------------|
| `fire_arrow` | Burning: **flat 1 damage/turn** (NOT 1d4 — see PoC test `test_quiver_followon_fixes.py`) | 100% on hit | 3 turns | 10 |
| `net_arrow` | Entangled: prevents movement/leap for 1 turn | **50% on hit** | 1 turn | 8 |

**Mechanics:**
- Normal arrows are infinite (no tracking needed — abstracted)
- Special arrows have count; **consumed on hit OR miss** (not just on hit)
- When quiver reaches 0, it is unequipped. Player must manually reload from inventory (no auto-reload — matches PoC)
- Without special ammo equipped, normal arrows are used
- Quiver slot only accepts items with `is_special_ammo: true`

**Fire arrow note:** The PoC `entities.yaml` has `effect_damage_dice: "1d4"` but this is a config artifact — the resolved value is always 1 per the test suite. Port as flat 1/turn.

---

## Monster Ranged Combat

**Deferred — not in PoC.** The PoC has no monster ranged AI; monsters use generic melee-approach behavior regardless of equipped weapon. The idea of ranged-armed monsters maintaining optimal distance is a future design addition, not a Phase 22.2 port. Do not implement in this pass.

---

## Metrics to Track (for harness)

- `ranged_attacks_made_by_player`
- `ranged_attacks_denied_out_of_range`
- `ranged_damage_dealt_by_player`
- `ranged_damage_penalty_total` (cumulative damage penalty from sub-optimal range)
- `ranged_adjacent_retaliations_triggered`
- `ranged_knockback_procs`
- `special_ammo_shots_fired` (any special ammo used)
- `special_ammo_effects_applied` (rider effect actually applied on hit)
- `entangle_moves_blocked` (movement/leap denied because target is entangled)

These are how you prove the ranged build is viable and the retaliation mechanic is doing its job.

---

## Ranged Build Viability Target

A ranged-focused run (shortbow/longbow + special ammo) should be able to complete depth 1-5 at roughly equivalent death rates to a melee build. Not easier, not harder — just different. The harness proves this with ranged-persona bot runs.

---

## Bot Policy

**`ranged_net_arrow`** — Specialized bot behavior used by the skirmisher identity scenario. Uses ranged attacks and pre-loaded net arrow quiver. Needed for `scenario_skirmisher_vs_ranged_net_identity`.

---

## Scenario Coverage (5 scenarios, all ported from PoC)

| Scenario | Purpose |
|----------|---------|
| `scenario_ranged_viability_arena` | Range bands at optimal/far distance; viability check |
| `scenario_ranged_adjacent_punish_arena` | Retaliation triggers at d==1; armor-halving |
| `scenario_ranged_max_range_denial_arena` | d>8 denied; bot approaches rather than shoots out-of-range |
| `scenario_ranged_chains_synergy` | Chains oath non-interaction with ranged knockback |
| `scenario_skirmisher_vs_ranged_net_identity` | 25 runs, `ranged_net_arrow` bot; net arrow entangle blocks skirmisher leap; identity proof |

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

- [ ] Range band table (Chebyshev distance, constants)
- [ ] `is_ranged_weapon` flag on `Equippable`
- [ ] `RangedCombatService.AttemptRangedAttack()`
- [ ] Retaliation-first logic for d==1
- [ ] Armor halving during retaliation
- [ ] Knockback proc (10%)
- [ ] Quiver equipment slot (`is_special_ammo: true` validation)
- [ ] `fire_arrow`: flat 1 dmg/turn burning, 3 turns, stack 10, consume on hit OR miss
- [ ] `net_arrow`: 50% entangle, 1 turn, stack 8, consume on hit OR miss
- [ ] Metric collection (all 9 metrics above)
- [ ] `ranged_net_arrow` bot policy
- [ ] Scenario YAML files (all 5)
- [ ] Scenario harness tests
