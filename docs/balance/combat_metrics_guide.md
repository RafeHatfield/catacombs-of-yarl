# Combat Metrics Guide

_Last verified: 2026-07-12 against commit 86b6f10_

## Overview

Combat metrics enable data-driven analysis of hit rates, attack pacing, and combat balance via the scenario harness.

## Metrics Reference

### Player Combat Stats
- **`total_player_attacks`**: Total attack attempts by the player across all runs
- **`total_player_hits`**: Total successful hits by the player
- **Player Hit Rate**: `total_player_hits / total_player_attacks * 100%`

### Monster Combat Stats
- **`total_monster_attacks`**: Total attack attempts by all monsters across all runs
- **`total_monster_hits`**: Total successful hits by monsters
- **Monster Hit Rate**: `total_monster_hits / total_monster_attacks * 100%`

### What Counts as an Attack?
All d20-based melee attacks, including:
- Normal attacks (hit or miss)
- Critical hits (natural 20)
- Fumbles (natural 1)
- Surprise attacks (auto-hit)
- Bonus/momentum attacks

### What Counts as a Hit?
- Attack roll >= target AC
- Natural 20 (always hits)
- Surprise attacks (always hit)
- **Does NOT count**: Natural 1 (always misses)

---

## Interpreting Results

### Hit Rate Expectations

**General Guidelines** (depth 5, baseline equipment):
- **Player vs Orc**: 60-70% hit rate (slight player advantage)
- **Player vs Zombie**: 70-80% hit rate (zombie disadvantage)
- **Monster vs Player**: 40-60% hit rate (depends on armor/stats)

### Red Flags
- Player hit rate < 50% -> Player too weak or monster AC too high
- Player hit rate > 90% -> Combat too easy, needs challenge
- Monster hit rate > 80% -> Player defense too low, unfair
- Monster hit rate < 20% -> Combat too one-sided

### Combat Ratio
`combat_ratio = total_player_attacks / total_monster_attacks`

- **Ratio > 1.5**: Player attacks much more (speed advantage or monsters dying quickly)
- **Ratio ~ 1.0**: Balanced turn-taking
- **Ratio < 0.7**: Monsters attack more (player on defensive or outnumbered)

---

## Available Scenario Families

### dueling_pit
**Purpose**: Baseline 1v1 combat measurement
- **Depth**: 5
- **Typical Hit Rates**: ~65-70% player, ~40-50% monster
- **Use For**: Baseline accuracy/evasion tuning

### backstab_training
**Purpose**: Surprise attack mechanics
- **Typical Hit Rates**: ~65-70% player, ~55-65% monster
- **Use For**: Stealth/backstab balance

### plague_arena
**Purpose**: Swarm combat and plague mechanics
- **Depth**: 8
- **Typical Hit Rates**: ~75-80% player, ~25-35% monster
- **Use For**: AOE/swarm balance

### orc_swarm_tight
**Purpose**: Close-quarters 3-orc pressure test (no speed gear)
- **Depth**: 5, **Arena**: 9x9
- **Use For**: Mobility denial, early danger

### zombie_horde
**Purpose**: Validate zombie HP tuning vs slow, multiple foes
- **Depth**: 5, **Arena**: 13x13, five zombies
- **Use For**: Momentum/bonus-attack cadence

---

## Difficulty Curve Visualizer

### What It Does
- Aggregates scenario metrics into normalized fields
- Groups by depth or scenario family
- Emits graphs and dashboard

### Reading the Graphs
- **Player/Monster Hit Rate vs Depth**: accuracy feel per band; look for smooth progression
- **Death Rate vs Depth**: target curves for early/mid pressure
- **Bonus Attacks per Run**: cadence of momentum mechanics
- **Pressure Index** (`monster_attacks_per_run - player_attacks_per_run`): negative = player acts more; positive = monsters pressure harder

---

## Troubleshooting

### Metrics show 0/0 attacks
**Cause**: Combat never happened (player/monsters died too quickly or turn limit too short)
**Fix**: Increase turn limit or check scenario spawn configuration

### Hit rates seem inconsistent
**Cause**: Low sample size (< 20 runs)
**Fix**: Run at least 50 iterations for stable statistics

### Monster hit rate = 0%
**Cause**: Player killed monster before it could attack (surprise attacks, high damage)
**Fix**: Expected in some scenarios (e.g., backstab_training)
