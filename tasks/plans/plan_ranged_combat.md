# Plan: Ranged Combat System

Status: [ ] Not started
PoC reference: services/ranged_combat_service.py (Phase 22.2)

---

## What It Is

A ranged attack system that makes bow/crossbow builds genuinely viable while punishing reckless close-range shooting. The core insight: ranged should be tactically interesting, not just "attack from far away for free."

---

## Range Band Table

OPTIMAL_MAX = 6 tiles (sweet spot). Distance is **Chebyshev** (king's move: `max(|dx|, |dy|)`).

| Distance | Outcome |
|----------|---------|
| d <= 1 (adjacent or overlapping) | Retaliation FIRST (free melee strike, player armor halved), then 25% damage shot |
| d == 2 | 50% damage |
| d == 3-6 | 100% damage (optimal) |
| d == 7 | 50% damage |
| d == 8 | 25% damage |
| d > 8 | DENIED — attack fails entirely, no roll |

**d <= 0 edge case:** Treat same as d == 1 (adjacent/retaliation). Unlikely in practice but determinism requires it.

**Minimum damage floor:** Range modifier cannot reduce damage below 1. `max(1, modified_damage)` enforced.

**LoS gate (differs from PoC):** A ranged attack requires line-of-sight via the existing `GameMap.HasLineOfSight()`. Closed doors are opaque. The PoC has no LoS check; C# adds it as a correctness gate. All five scenarios are arena-style and unaffected.

**Player-only gate (Phase 22.2):** Ranged code path activates only for the player (or possessed host). Monsters do not use ranged band logic in this pass. See "Deferred" section.

---

## Retaliation-First Mechanic

When the player shoots at an adjacent enemy (d <= 1), the exact resolution order is:

1. **Validity check** — LoS, distance band, deny if d > 8. If denied: increment `ranged_attacks_denied_out_of_range`, do NOT increment `ranged_attacks_made_by_player`, do NOT consume ammo. Return.
2. **Roll d20 + to-hit bonuses** — determines if shot hits. Computed now, resolved later.
3. **Retaliation check** — if d == 1 and the defender can retaliate (see `can_retaliate` below): the defender makes a free melee attack against the player with **player armor halved**. If the player dies, return immediately — shot does not resolve and **ammo is not consumed**.
4. **Apply shot** — if hit: apply range-band damage modifier, deal damage to target, apply special ammo on-hit effect (rider roll if any). If miss: no damage, no rider effect.
5. **Consume ammo** — decrement quiver count by 1 regardless of hit/miss (but NOT on denial and NOT if player died to retaliation in step 3).
6. **Knockback roll** — 10% chance on hit only. If proc: apply 1-tile knockback.

**`can_retaliate` gate:** Defender cannot retaliate if it has any of: `AsleepEffect`, `StunnedEffect`, `StaggeredEffect`, `ParalyzedEffect`. **`EntangledEffect` does NOT block retaliation** — entangled targets can still strike adjacent attackers. This distinction is load-bearing for the skirmisher scenario.

**Why halved armor?** The player is fumbling with a bow at point-blank range — not holding it defensively.

---

## Weapon Detection

Bows and crossbows have `is_ranged_weapon: true` on their `Equippable` component. Spears and thrown weapons are melee with reach — they do NOT use the ranged combat system. Detection is by flag only, never by reach heuristic.

```yaml
shortbow:
  equippable:
    slot: main_hand
    damage: 1d6
    is_ranged_weapon: true
    accuracy: 2
    two_handed: true    # clears off-hand slot on equip

longbow:
  equippable:
    slot: main_hand
    damage: 1d8
    is_ranged_weapon: true
    accuracy: 3
    two_handed: true
```

**Two-handed flag:** `Equippable` gains a `TwoHanded` bool. Equipping a two-handed weapon clears the `OffHand` slot. This prevents bow + shield stacking, which would produce misleading viability data.

**Longbow max range note:** Both shortbow and longbow use the same range band table (max range 8). The longbow's advantage is higher base damage, not extended range. This matches the PoC and is intentional.

---

## Knockback Proc

- 10% chance on successful ranged hit only (not on miss, not on denied shots)
- Exactly 1 tile knockback in the direction of the shot
- Direction: signed tile vector from attacker to target, each axis clamped to ±1
- Routes through `KnockbackService` (prerequisite — see build order)
- Respects walls and entities: stopped at first blocked tile, 0 tiles moved if immediately blocked
- **Metric counts only successful knockbacks** (`tiles_moved > 0`). Silent failures (wall, entity collision) do not increment `ranged_knockback_procs`.
- Chains oath does NOT add +1 to ranged knockback distance (unlike melee). Intentional — ranged knockback is its own mechanic.

---

## Special Ammo / Quiver System

Player has a **quiver slot** in equipment. Quiver holds a stack of one ammo type. Only items with `is_special_ammo: true` can be equipped to the quiver slot — validated at equip-time, not attack-time.

**Ammo Types:**

| Type | Trigger | Effect | Chance | Duration | Stack Size |
|------|---------|--------|--------|----------|------------|
| `fire_arrow` | On hit | Burning: **flat 1 damage/turn** (NOT 1d4 — PoC config artifact; test is authoritative) | 100% on hit | 3 turns | 10 |
| `net_arrow` | On hit | Entangled: prevents movement and leap | **50% on hit** | 1 turn | 8 |

**Mechanics:**
- Normal arrows are infinite — abstracted, no tracking
- Special arrows consumed on **hit OR miss** (but not on: out-of-range denial, player dies to retaliation before shot resolves)
- When quiver reaches 0, it is unequipped. Player must manually reload from inventory — **no auto-reload** (matches PoC)
- Rider effect rolls only when the shot hits. A miss consumes ammo but applies no rider effect.

**Burning stacking:** If target is already burning, a second fire arrow refreshes duration to 3 turns (non-stacking refresh). Matches PoC and existing C# `BurningEffect.Apply` semantics.

**Entangle stacking:** Same — refresh, not stack. Net arrow on already-entangled target resets to 1 turn.

---

## Event Architecture

All ranged state changes emit `TurnEvent`s. Metrics are derived from events in `RunMetrics.RecordTurn`, not from return values. New events to add:

| Event | Fields | When Emitted |
|-------|--------|--------------|
| `RangedAttackEvent` | `Distance`, `BandName`, `Denied`, `Hit`, `Damage`, `RetaliationTriggered`, `KnockbackApplied` | On every ranged attack attempt |
| `SpecialAmmoConsumedEvent` | `AmmoType`, `Remaining` | On ammo consumption |
| `RangedKnockbackEvent` | `Direction`, `TilesMoved` | On knockback proc (only when tiles_moved > 0) |
| `EntangleMoveBlockedEvent` | `EntityId`, `BlockedActionType` ("move" or "leap") | When movement/leap is denied due to entangle |

`EntangleMoveBlockedEvent` is emitted from:
- `TurnController.ResolvePlayerMove` when player is entangled
- Each monster AI when its movement is blocked by entangle
- `SkirmisherAI` when leap is denied by entangle (use `BlockedActionType = "leap"` to drive `skirmisher_leap_denied_entangled` metric)

---

## Metrics

All 9 metrics added to `RunMetrics` and `AggregatedMetrics`:

| Metric | Derived from | Notes |
|--------|-------------|-------|
| `ranged_attacks_made_by_player` | `RangedAttackEvent` where `!Denied` | Mutually exclusive with denial counter |
| `ranged_attacks_denied_out_of_range` | `RangedAttackEvent` where `Denied` | Fires instead of "made" |
| `ranged_damage_dealt_by_player` | `RangedAttackEvent.Damage` | Sum across hits |
| `ranged_damage_penalty_total` | `RangedAttackEvent` where band != optimal | Difference between full and actual damage |
| `ranged_adjacent_retaliations_triggered` | `RangedAttackEvent.RetaliationTriggered` | |
| `ranged_knockback_procs` | `RangedKnockbackEvent` | Only successful knockbacks |
| `special_ammo_shots_fired` | `SpecialAmmoConsumedEvent` | All consumption (hit and miss) |
| `special_ammo_effects_applied` | `RangedAttackEvent` annotated with effect applied | |
| `entangle_moves_blocked` | `EntangleMoveBlockedEvent` | Player + monster + leap all count |

`FloorRunMetrics` additions: same fields, per-floor granularity. Whether dungeon harness needs these in Phase 22.2 is TBD — defer if the bot doesn't pick up bows.

---

## Bot Policy: `ranged_net_arrow`

New bot behavior dispatched when `player_bot: "ranged_net_arrow"` in scenario YAML. Requires adding a dispatch table in bot infrastructure (currently `player_bot` field is loaded from `ScenarioDefinition` but ignored at runtime — wire it through `DungeonRunHarness` to `BotBrain`).

Decision logic:
1. **Shoot if in optimal band (d 3-6):** If any enemy is at d 3-6 with LoS, shoot the nearest one. Do not move.
2. **Back off if too close (d <= 2):** Step away from the nearest threat (move toward farthest open tile from all threats). Then shoot if now in band.
3. **Close if too far (d > 6):** Move toward nearest enemy until d == 6. Then shoot.
4. **Heal thresholds:** Inherit from `BotBrain` defaults.
5. **Fallback:** If no ranged attack is possible, fall back to melee.

The `tactical_fighter` bot is unchanged — it still walks to adjacent and melee-attacks. Bot dispatch is a new infrastructure concern that `ranged_net_arrow` introduces.

---

## Scenario Coverage (4 scenarios now; chains deferred)

| Scenario | Runs | Bot | Purpose |
|----------|------|-----|---------|
| `scenario_ranged_viability_arena` | 10 | `ranged_net_arrow` | Range bands at optimal/far distance; viability check |
| `scenario_ranged_adjacent_punish_arena` | 10 | `tactical_fighter` | Retaliation triggers at d==1; armor-halving |
| `scenario_ranged_max_range_denial_arena` | 10 | `ranged_net_arrow` | d>8 denied; bot approaches rather than shoots out-of-range |
| `scenario_skirmisher_vs_ranged_net_identity` | 25 | `ranged_net_arrow` | Net arrow entangle blocks skirmisher leap; identity proof |

**Deferred — `scenario_ranged_chains_synergy`:** Requires Oath of Chains system which does not exist. Port with Oath system.

---

## Ranged Build Viability Target

A ranged-focused run (shortbow + net arrows) should complete depth 1-5 at roughly equivalent death rates to a melee build. Not easier, not harder — different. The harness proves this via `scenario_ranged_viability_arena` with the kiting bot.

---

## Deferred

- **Monster ranged AI** — not in PoC. Monsters ignore range bands for now (player-only gate). Future work.
- **Auto-reload from inventory** — PoC requires manual reload; plan aspiration deferred.
- **`scenario_ranged_chains_synergy`** — requires Oath of Chains.
- **Possession + ranged interaction** — if a possessed host has `is_ranged_weapon: true` equipped, ranged code resolves against the host body (per possession semantics). Edge case; defer formal handling.

---

## Build Order (Prerequisite → Dependent)

1. **`KnockbackService`** — prerequisite, no ranged dependency. Handles direction, wall collision, entity collision, map edge.
2. **`TwoHanded` flag on `Equippable`** — clears off-hand on equip.
3. **Quiver slot + `is_special_ammo` validation** — equip-time gate, new `EquipmentSlot.Quiver`.
4. **Bow/arrow YAML definitions** — `shortbow`, `longbow`, `crossbow`, `fire_arrow`, `net_arrow`.
5. **`RangedCombatService.AttemptRangedAttack()`** — range validity (LoS + band), retaliation logic, damage modifier, all new events.
6. **Special-ammo on-hit effects** — burning and entangle application, ammo consumption.
7. **`EntangleMoveBlockedEvent`** — emission from player move path, monster AI move paths, SkirmisherAI leap path.
8. **`RunMetrics` extensions** — all 9 metrics, event derivation, aggregation.
9. **`ranged_net_arrow` bot policy + bot dispatch wiring** — kiting behavior, dispatch table.
10. **Scenario YAML files** (4 scenarios).
11. **Scenario harness tests.**

---

## C# Port Checklist

- [ ] `KnockbackService` (direction calc, wall/entity/edge stops, returns `tiles_moved`)
- [ ] `TwoHanded` flag on `Equippable`, clear off-hand on equip
- [ ] `EquipmentSlot.Quiver`, `is_special_ammo` validation at equip-time
- [ ] `is_ranged_weapon` flag on `Equippable`
- [ ] Bow/arrow YAML definitions (`shortbow`, `longbow`, `fire_arrow`, `net_arrow`)
- [ ] `RangedCombatService.AttemptRangedAttack()` — full resolution order per spec above
- [ ] LoS gate via `GameMap.HasLineOfSight()`
- [ ] Retaliation-first + `can_retaliate` gate (entangled does NOT block)
- [ ] Armor halving during retaliation
- [ ] Minimum 1 damage floor on range-modified shots
- [ ] Knockback proc (10%, on hit only, successful-only metric)
- [ ] `fire_arrow` burning: flat 1/turn, 3 turns, 100% on hit, stack 10
- [ ] `net_arrow` entangle: 50% on hit, 1 turn, stack 8
- [ ] Ammo consumed on hit OR miss (not on denial; not if player dies to retaliation)
- [ ] `RangedAttackEvent`, `SpecialAmmoConsumedEvent`, `RangedKnockbackEvent`, `EntangleMoveBlockedEvent`
- [ ] `EntangleMoveBlockedEvent` emitted from player move, monster AI move, SkirmisherAI leap
- [ ] `RunMetrics` + `AggregatedMetrics`: all 9 metrics
- [ ] `ranged_net_arrow` bot policy (kiting decision logic)
- [ ] Bot dispatch table wired from `ScenarioDefinition.PlayerBot` through harness to `BotBrain`
- [ ] Scenario YAML files (4 scenarios, chains deferred)
- [ ] Scenario harness tests
