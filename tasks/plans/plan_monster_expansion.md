# Plan: Monster Roster Expansion

**Status:** [ ] Not started
**PoC reference:** `~/development/rlike/config/entities.yaml`, `~/development/rlike/services/spawn_service.py`, `~/development/rlike/components/ai/`
**Prerequisite for:** plan_player_progression.md (boons need content density to tune against)

---

## Overview

The C# codebase has 6 monsters. The PoC has 34. The immediate gap is depths 3-8: with only orcs, orc_brutes, and large_slimes, there isn't enough variety for meaningful progression tuning or interesting combat. This plan ports PoC monsters in waves ordered by dependency and depth coverage.

**All stats, spawn weights, AI parameters, and special abilities are copied directly from the PoC.** No invented values.

---

## Current State (C#)

| Monster | min_depth | Faction | Special |
|---------|-----------|---------|---------|
| orc | 1 | orc | equips weapons/armor |
| orc_grunt | — | orc | scenario-only (spawn_weight 0) |
| orc_brute | 3 | orc | slow, high damage |
| zombie | 10 | undead | slow, piercing resist, bludgeon vuln |
| slime | 2 | beast | corrosion, child of large_slime |
| large_slime | 3 | beast | splits into 2-3 slimes |

**Content desert:** Depths 4-9 have only 3 active monster types.

---

## Wave 0 — Corpse System (Prerequisite)

**Plan file:** [plan_corpse_necromancer.md](plan_corpse_necromancer.md) (Phase 1 only)

Corpses are a foundational system. Skeletons drop bone_piles on death, necromancers raise corpses, and the entire undead/cultist faction depends on corpse entities existing. Build Phase 1 (corpse entity, death transformation, GameState.Corpses, floor descent cleanup, tests) before any Wave 2+ work.

Phase 2-3 of plan_corpse_necromancer (Raise Dead spell + Necromancer AI) can wait until Wave 2.

---

## Wave 1 — Orc Variants (depths 1-6)

These resolve from the base "orc" spawn roll via a variant resolution system. The PoC resolves "orc" into specific variants based on depth-scaled probability tables.

### Orc Variant Resolution Table (PoC)

| Depth | Plain Orc | Brute | Shaman | Skirmisher |
|-------|-----------|-------|--------|------------|
| 1 | 100% | 0% | 0% | 0% |
| 2 | 92% | 5% | 3% | 0% |
| 3 | 78% | 7.5% | 7% | 7.5% |
| 4-5 | 67.5% | 10% | 10% | 12.5% |
| 6+ | 62.5% | 10% | 10% | 17.5% |

Note: orc_veteran (5-15%) and orc_scout also appear in PoC variant tables but are lower priority — basic AI, less combat impact. Add them after the core variants are working.

### 1A. orc_scout — YAML only, basic AI

```yaml
orc_scout:
  extends: orc
  name: "Orc Scout"
  stats:
    hp: 15
    xp: 25
  inventory_size: 3
  seek_distance: 8
  spawn_weight: 0   # resolved via variant system only
```

Fragile, low XP. Mostly adds variety, not threat.

### 1B. orc_veteran — YAML only, basic AI + speed bonus

```yaml
orc_veteran:
  extends: orc
  name: "Orc Veteran"
  stats:
    hp: 25
    power: 1
    xp: 50
  speed_bonus: 0.15
  inventory_size: 6
  spawn_weight: 0   # resolved via variant system only
```

Tougher orc with 15% bonus attack chance.

### 1C. orc_skirmisher — New AI: Pouncing Leap + Fast Pressure

```yaml
orc_skirmisher:
  name: "Orc Skirmisher"
  stats:
    hp: 24
    power: 0
    defense: 0
    xp: 45
    damage_min: 3
    damage_max: 5
    strength: 12
    dexterity: 15
    constitution: 10
    accuracy: 4
    evasion: 3
  ai_type: "skirmisher"
  faction: "orc"
  blocks: true
  speed_bonus: 0.0
  spawn_weight: 0   # resolved via variant system only
```

**Pouncing Leap:** cooldown 3 turns, leaps 2 tiles toward player, triggers at range 3-6 (Chebyshev). Anti-kiting mechanic.
**Fast Pressure:** 20% chance for extra attack per turn at 70% damage.

Does NOT extend orc (standalone definition, no equipment).

### 1D. orc_shaman — New AI: Hang-back Support Caster

```yaml
orc_shaman:
  extends: orc
  name: "Orc Shaman"
  stats:
    hp: 24
    power: 1
    damage_min: 3
    damage_max: 5
    strength: 10
    dexterity: 12
    constitution: 10
    accuracy: 3
    xp: 60
  ai_type: "orc_shaman"
  spawn_weight: 0   # resolved via variant system only
```

**Crippling Hex:** radius 6, duration 5 turns, cooldown 10, -1 to-hit and -1 AC on player.
**Chant of Dissonance:** radius 5, duration 3 turns, cooldown 15, +1 energy cost per player move, interruptible by damage.
**Hang-back:** preferred distance 4-7, danger radius 2 from player.

### 1E. orc_chieftain — New AI: Rally Cry + Sonic Bellow

```yaml
orc_chieftain:
  extends: orc
  name: "Orc Chieftain"
  stats:
    hp: 35
    power: 2
    xp: 75
  speed_bonus: 0.25
  ai_type: "orc_chieftain"
  inventory_size: 8
  seek_distance: 7
  spawn_weight: 0   # resolved via variant system only
```

**Rally Cry (ONE-TIME):** radius 5, requires 2+ orc allies, grants +1 to-hit and +1 damage to orc allies, cleanses fear/morale_debuff. Ends when chieftain first takes damage.
**Sonic Bellow (ONE-TIME at <50% HP):** -1 to-hit penalty on player for 2 turns.

### 1F. Variant Resolution System

New `OrcVariantResolver` in Logic/Content or Logic/Core:
- Called by `EntityPlacer` or `DungeonFloorBuilder` when spawning "orc"
- Takes depth, returns resolved monster ID based on probability table above
- Uses `SeededRandom` for determinism

### Wave 1 Implementation Tasks

| Task | Description | New AI? |
|------|-------------|---------|
| W1-001 | Add orc_scout and orc_veteran to entities.yaml | No |
| W1-002 | Add orc_skirmisher to entities.yaml | Yes — SkirmisherAI |
| W1-003 | Implement SkirmisherAI (Pouncing Leap + Fast Pressure) | New file |
| W1-004 | Add orc_shaman to entities.yaml | Yes — OrcShamanAI |
| W1-005 | Implement OrcShamanAI (Crippling Hex + Chant of Dissonance + hang-back) | New file |
| W1-006 | Add orc_chieftain to entities.yaml | Yes — OrcChieftainAI |
| W1-007 | Implement OrcChieftainAI (Rally Cry + Sonic Bellow + hang-back) | New file |
| W1-008 | Implement OrcVariantResolver + wire into EntityPlacer | New file |
| W1-009 | Unit tests for all 5 variants + variant resolution | Test file |

---

## Wave 2 — New Factions (depths 3-8)

Adds combat variety beyond orcs. Requires Wave 0 (corpse system) for skeleton bone_pile drops.

### 2A. troll — Basic AI + Regeneration

```yaml
troll:
  name: "Troll"
  stats:
    hp: 30
    power: 0
    defense: 2
    xp: 100
    damage_min: 8
    damage_max: 12
    strength: 16
    dexterity: 8
    constitution: 16
  ai_type: "basic"
  faction: "orc"
  blocks: true
  regeneration: 2         # HP per turn
  regen_suppress_types: ["acid", "fire"]  # suppressed for 1 turn by these damage types
  inventory_size: 8
  seek_distance: 7
  depth_weights:
    - { depth: 3, weight: 5 }
    - { depth: 4, weight: 10 }
    - { depth: 5, weight: 15 }
```

PoC main spawn table: `from_dungeon_level([[15, 3], [30, 5], [60, 7]])`. B1 band uses lower weights shown above.

### 2B. skeleton — Formation AI + Shield Wall

```yaml
skeleton:
  name: "Skeleton"
  stats:
    hp: 20
    power: 0
    defense: 0
    xp: 30
    damage_min: 3
    damage_max: 5
    strength: 10
    dexterity: 12
    constitution: 10
    accuracy: 2
    evasion: 1
  ai_type: "skeleton"
  faction: "undead"
  blocks: true
  tags: ["undead", "no_flesh", "low_undead"]
  damage_resistances:
    piercing: 0.5     # 50% resistance
  damage_vulnerabilities:
    bludgeoning: 1.5   # 50% vulnerability
  drops_bone_pile: true  # creates bone_pile entity on death (requires corpse system)
  depth_weights:
    - { depth: 3, weight: 10 }
    - { depth: 5, weight: 20 }
    - { depth: 7, weight: 30 }
```

**Shield Wall:** +1 AC per adjacent skeleton ally (NO CAP). Formation AI seeks adjacency with other skeletons before engaging.

### 2C. cave_spider — Poison DOT

```yaml
cave_spider:
  name: "Cave Spider"
  stats:
    hp: 16
    power: 0
    defense: 1
    xp: 25
    damage_min: 2
    damage_max: 4
    strength: 8
    dexterity: 14
    constitution: 8
    accuracy: 3
    evasion: 2
  ai_type: "basic"
  faction: "beast"
  blocks: true
  tags: ["corporeal_flesh", "beast", "living", "venomous"]
  on_hit_effect: "poison"     # applies poison DOT on melee hit
  poison_resistance: 0.75     # 75% natural resistance
  depth_weights:
    - { depth: 2, weight: 10 }
    - { depth: 4, weight: 20 }
    - { depth: 6, weight: 30 }
```

### 2D. web_spider — Slow on Hit

```yaml
web_spider:
  extends: cave_spider
  name: "Web Spider"
  stats:
    hp: 20
    xp: 40
  on_hit_effect: "slow"      # applies SlowedEffect on hit
  depth_weights:
    - { depth: 4, weight: 5 }
    - { depth: 6, weight: 15 }
    - { depth: 8, weight: 25 }
```

### 2E. fire_beetle — Burning on Contact

```yaml
fire_beetle:
  name: "Fire Beetle"
  stats:
    hp: 12
    power: 3
    defense: 2
    xp: 45
    damage_min: 2
    damage_max: 5
    strength: 10
    dexterity: 14
    constitution: 10
    accuracy: 1
    evasion: 1
  ai_type: "basic"
  faction: "beast"
  blocks: true
  on_hit_effect: "burning"    # applies BurningEffect on hit
  fire_resistance: 1.0        # immune to fire
  depth_weights:
    - { depth: 3, weight: 5 }
    - { depth: 5, weight: 15 }
    - { depth: 7, weight: 25 }
```

### Wave 2 Implementation Tasks

| Task | Description | New AI? | Depends on |
|------|-------------|---------|------------|
| W2-001 | Add troll to entities.yaml, implement regeneration in TurnController | No new AI | — |
| W2-002 | Add skeleton to entities.yaml, implement SkeletonAI (Shield Wall) | Yes | Wave 0 (bone_pile) |
| W2-003 | Implement on_hit_effect system (status effect application on melee) | System | Status effects exist |
| W2-004 | Add cave_spider, web_spider, fire_beetle to entities.yaml | No new AI | W2-003 |
| W2-005 | Implement damage type resistances/vulnerabilities in CombatResolver | System | — |
| W2-006 | Unit tests for all Wave 2 monsters | Test file | All above |

---

## Wave 3 — Mid-game Depth (depths 8-15)

### 3A. giant_spider — Fast, Web Traps

```yaml
giant_spider:
  name: "Giant Spider"
  stats:
    hp: 18
    power: 0
    defense: 1
    xp: 45
    damage_min: 4
    damage_max: 8
    strength: 12
    dexterity: 16
    constitution: 10
    accuracy: 3
    evasion: 3
  ai_type: "basic"
  faction: "beast"
  speed_bonus: 1.5
  depth_weights:
    - { depth: 8, weight: 15 }
    - { depth: 11, weight: 30 }
    - { depth: 14, weight: 45 }
```

### 3B. Necromancer family

Requires Wave 0 (corpse system) + plan_corpse_necromancer.md Phase 2-3.

- necromancer (depth 5+, raises zombies from corpses)
- plague_necromancer (depth 7+, raises plague_zombies)
- bone_necromancer (depth 8+, raises bone_thralls from bone_piles) — deferred
- exploder_necromancer (depth 10+, corpse explosion AoE) — deferred

### 3C. cultist_blademaster — Fast Melee Fighter

```yaml
cultist_blademaster:
  name: "Cultist Blademaster"
  stats:
    hp: 30
    power: 1
    defense: 2
    xp: 80
    damage_min: 6
    damage_max: 10
    strength: 14
    dexterity: 16
    constitution: 12
    accuracy: 4
    evasion: 3
  ai_type: "basic"
  faction: "cultist"
  speed_bonus: 1.25
  inventory_size: 4
  seek_distance: 5
  depth_weights:
    - { depth: 12, weight: 10 }
    - { depth: 15, weight: 20 }
    - { depth: 18, weight: 35 }
```

---

## Wave 4 — Deep Dungeon + Bosses (depths 15+)

Deferred until depths 1-15 are solid. Includes:
- wraith (life drain, very fast, incorporeal)
- lich (Soul Bolt, Command the Dead aura, raise dead)
- troll_ancient (regen 3/turn, high stats)
- greater_slime (splits into large_slimes)
- plague_zombie (depth 13+, plague spread on hit)
- Dragon Lord, Demon King, Zhyraxion forms (bosses)
- corrupted_ritualist (final boss guardian)

Full stats documented in the PoC monster audit (see session notes 2026-04-01).

---

## Priority Order

1. **Wave 0** — Corpse system (plan_corpse_necromancer.md Phase 1). Foundation for undead faction.
2. **Wave 1** — Orc variants. Highest immediate impact: 5 new monsters from the existing orc spawn, adding combat variety to depths 1-6 without any new spawn table entries.
3. **Wave 2** — New factions. Troll, skeleton, spiders, fire beetle. Fills depths 3-8 with diverse threats.
4. **Wave 3** — Mid-game. Necromancers, giant spider, cultist blademaster. Requires corpse system.
5. **Wave 4** — Deep/bosses. Deferred until progression system exists to test against.

After Waves 0-2 (16 new monsters), the game has enough content density to build and tune the depth boon progression system.

---

## Systems Required by Monsters

Several monsters need systems that don't exist yet:

| System | Needed by | Status |
|--------|-----------|--------|
| Corpse entity lifecycle | skeleton, necromancers | Plan exists (plan_corpse_necromancer.md) |
| Orc variant resolution | all orc variants | New — Wave 1 |
| Damage type resistances | skeleton, zombie | Partially exists (PoC has it; C# needs porting) |
| On-hit status effects | cave_spider, web_spider, fire_beetle | Status effects exist; on-hit trigger needed |
| Regeneration per turn | troll, troll_ancient | New — simple TurnController addition |
| Hang-back AI behavior | orc_shaman, orc_chieftain, necromancers | New — reusable AI pattern |
| Pouncing Leap ability | orc_skirmisher | New — SkirmisherAI |
| Shield Wall adjacency | skeleton | New — SkeletonAI |
| Rally/buff ally system | orc_chieftain | New — OrcChieftainAI |
