# Plan: Balance Pipeline (ETP, Target Bands, Depth Scaling)

Status: [x] Complete — all 5 phases shipped 2026-05-21. See `tasks/plans/plan_balance_pipeline_impl.md` for full detail.
PoC reference: balance/etp.py (~27,473 lines), balance/target_bands.py, balance/depth_scaling.py

---

## What It Is

The entire scientific infrastructure for balance. Balance is not guessed — it's measured. The pipeline is: define scenarios → run harness → collect metrics → compare vs target bands → auto-diagnose gaps → tune → repeat.

---

## ETP System (Effective Threat Points)

ETP is a single number representing an encounter's total threat. It enables budgeting encounters at the design level.

### Formula

```
ETP = (DPS × 6) × Durability × Behavior × Synergy
```

Where:
- **DPS** = average damage per turn
- **Durability** = (expected player hits to kill monster) / 3
- **Behavior** = AI role modifier (see table below)
- **Synergy** = 1.0 + 0.1 per meaningful combo (e.g., healer + fighter = 1.1)

### Behavior Modifiers

| Role | Multiplier |
|------|-----------|
| Passive | 0.8× |
| Basic melee | 0.9× |
| Basic ranged | 1.0× |
| Gap-closer (leaper) | 1.05× |
| Control (CC) | 1.1× |
| Kiter | 1.1× |
| Area denial | 1.15× |
| Summoner | 1.2× |
| Boss | 1.3× |

### Room and Floor Budgets (Per Band)

| Band | Depths | Room ETP | Floor ETP | Spike Mult |
|------|--------|---------|----------|-----------|
| B1 | 1–2 | 3–5 | 15–30 | 1.5× |
| B2 | 3–4 | 5–8 | 25–45 | 1.5× |
| B3 | 5–6 | 7–12 | 40–65 | 1.5× |
| B4 | 7–8 | 10–16 | 60–90 | 1.5× |
| B5 | 9–10 | 14–20 | 80–120 | 1.5× |

Tolerance: ±10% room ETP, ±10% floor ETP.

**Spike multiplier**: Boss rooms can go up to 1.5× their band's room budget.

### How It's Used

When spawning a room:
1. Determine room's ETP budget from current band
2. Select monsters that sum to budget (trim to fit)
3. Log if budget violated (debug flag)

---

## Target Bands

Per-depth design intent for player survival metrics.

| Depth | Death Rate Target | H_PM Range | H_MP Range |
|-------|------------------|-----------|-----------|
| 1 | 0% | 3–5 hits | 8–12 hits |
| 2 | 0–8% | 4–6 hits | 7–10 hits |
| 3 | 5–15% | 4–7 hits | 6–9 hits |
| 4 | 15–30% | 5–8 hits | 5–8 hits |
| 5 | 25–40% | 5–9 hits | 4–7 hits |
| 6 | 35–55% | 6–10 hits | 4–6 hits |

**H_PM** = player hits to kill monster (measures tankiness)
**H_MP** = monster hits to kill player (measures lethality)

### Auto-Diagnosis Logic

When observed metrics fall outside target bands, the system generates diagnostic text:

- Death% too high + H_MP in band → "Monster damage is fine; likely composition or timing problem"
- Death% too high + H_MP low → "Monsters are too lethal; reduce damage or add HP"
- H_PM too high → "Monsters too tanky; reduce HP or defense"
- H_PM too low → "Monsters too fragile; increase HP"
- Death% fine but H_PM high + H_MP high → "Both sides tanky; fights drag on"

---

## Depth Scaling (Progressive Multipliers)

Monsters scale with depth to maintain challenge as player gets stronger.

```yaml
depth_scaling:
  depth_1: {hp_mult: 1.0, damage_mult: 1.0, accuracy_mult: 1.0}
  depth_2: {hp_mult: 1.05, damage_mult: 1.02, accuracy_mult: 1.01}
  depth_3: {hp_mult: 1.12, damage_mult: 1.05, accuracy_mult: 1.02}
  depth_4: {hp_mult: 1.20, damage_mult: 1.08, accuracy_mult: 1.03}
  depth_5: {hp_mult: 1.30, damage_mult: 1.12, accuracy_mult: 1.05}
```

Applied at monster spawn time. Base stats from entities.yaml × depth multiplier.

---

## Scenario Categories

The 140+ scenarios in the PoC fall into three categories:

### Identity Scenarios

Verify a specific mechanic works correctly:
- Each trap type (spike_trap_identity, web_trap_identity, etc.)
- Each monster type (orc_grunt_identity, skeleton_identity, etc.)
- Each item/scroll type (fireball_identity, net_arrow_identity, etc.)
- Each status effect (silence_identity, disarm_identity, etc.)

Identity scenarios have narrow expected outcome ranges (e.g., "fireball should kill 90%+ of zombies in radius").

### Pressure Probes

Measure difficulty at specific depths:
- `depth1_orc_easy`, `depth2_orc_baseline`, `depth3_orc_brutal`
- `depth4_plague_arena`, `depth5_zombie_horde`
- Variants: with/without gear, cautious/aggressive bot

These generate the Death% and H_PM/H_MP metrics checked against target bands.

### Behavioral Tests

Verify that specific interactions work correctly:
- `ranged_viability_arena` — ranged build viable at depth 1-3?
- `ranged_adjacent_punish_arena` — retaliation mechanic firing correctly?
- `faction_hostility_verification` — orcs and undead fight each other?
- `necromancer_corpse_denial` — fire tiles prevent necromancer raises?

---

## Balance Debug Flags (etp_config.yaml)

```yaml
debug:
  log_room_etp: true          # Log ETP per room on spawn
  log_floor_etp: true         # Log floor total ETP
  log_budget_violations: true # Flag when budget exceeded ±10%
  log_monster_etp: false      # Per-monster ETP breakdown (verbose)
```

---

## C# Port Checklist

- [ ] `EtpCalculator` — compute ETP from monster stats + role
- [ ] `EncounterBudgeter` — room population from ETP budget
- [ ] `DepthBandConfig` YAML (room ETP, floor ETP per band)
- [ ] `DepthScalingConfig` YAML (HP/damage/accuracy multipliers)
- [ ] Scaling applied at monster spawn time
- [ ] `TargetBandConfig` YAML (death%, H_PM, H_MP per depth)
- [ ] Auto-diagnosis: compare metrics to bands, generate diagnostic text
- [ ] ETP debug flags and logging
- [ ] Budget violation logging
- [ ] `AnalystAgent` integration: harness output → diagnostic report
- [ ] 140+ scenario YAML files (port from PoC; can do progressively)
- [ ] Scenario validation (min/max expected outcomes)
