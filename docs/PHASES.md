# Catacombs of YARL - Development Phases

**Last Updated:** 2024-12-14

## Purpose

This document tracks the development arc of Catacombs of YARL from foundation to current state, and maps the road ahead.

**What this is:**
- Historical record of completed work
- Planning tool for future development
- Orientation guide for new contributors

**What this is not:**
- Detailed technical documentation (see individual docs/)
- Complete feature specifications
- Exhaustive change log

**How to use this:**
- Read sequentially to understand how the game evolved
- Use phase numbers as reference points in discussions
- Update as phases complete or priorities shift

---

## Completed Phases

### Phase 1-3: Foundation (Early 2024)

**Status:** COMPLETE

**What it addressed:**
- Core engine architecture and ECS implementation
- Basic turn-based gameplay loop
- Entity system with monsters, items, and player
- Initial UI rendering and input handling
- MVP playable game loop

**What it unlocked:**
- Stable foundation for iterative development
- Ability to test gameplay mechanics in isolation
- Clear separation between game logic and rendering

---

### Phase 4-5: Core Systems Stabilization

**Status:** COMPLETE

**What it addressed:**
- Turn controller refactoring for clean state management
- Input abstraction layer (keyboard/bot/future inputs)
- Message system and combat feedback
- Death screen and game over handling
- Component access patterns and type safety

**What it unlocked:**
- Reliable turn sequencing for complex interactions
- Bot testing infrastructure
- Consistent player feedback across all actions
- Foundation for automated testing

---

### Phase 6-8: World Generation

**Status:** COMPLETE

**What it addressed:**
- YAML-based level template system
- Room generation with doors, corridors, vaults
- Dungeon depth progression
- Loot distribution and item placement
- Victory condition (Amulet of Yarl)

**What it unlocked:**
- Content authoring without code changes
- Varied dungeon layouts and replayability
- Clear progression structure (descend -> retrieve -> ascend)
- Worldgen sanity testing harness

---

### Phase 9-11: Combat Mechanics Expansion

**Status:** COMPLETE

**What it addressed:**
- Surprise attack system (backstab mechanics)
- Momentum and bonus attack chains
- Critical hit system (natural 20 = 2x damage)
- Awareness states (unaware/aware/alert)
- Speed bonuses and turn economy

**What it unlocked:**
- Tactical depth beyond "hit enemy until dead"
- Positioning and flanking strategies
- Speed items as meaningful progression
- Foundation for future status effects

---

### Phase 12: Scenario Harness (Deterministic Testing)

**Status:** COMPLETE

**What it addressed:**
- Hand-authored scenario system (no worldgen RNG)
- Repeatable combat testing with fixed starting conditions
- Scenario-based metrics collection
- Bot policy integration for automated testing

**What it unlocked:**
- Ability to measure combat balance objectively
- Regression detection for combat changes
- Fast iteration on combat tuning (no full runs needed)
- Foundation for difficulty curve analysis

---

### Phase 13: Combat Metrics & Feel Measurement

**Status:** COMPLETE

**What it addressed:**
- Attack rate tracking (player vs monster)
- Hit percentage measurement
- Bonus attack frequency metrics
- Combat pacing visibility

**What it unlocked:**
- Quantitative answers to "does this feel good?"
- Data-driven combat tuning
- Speed bonus effectiveness measurement
- Foundation for difficulty tuning

**Key metrics:** player_hit_rate, monster_hit_rate, bonus_attacks_per_run

---

### Phase 14-15: Bot Intelligence & Telemetry

**Status:** COMPLETE

**What it addressed:**
- Bot persona system (balanced, cautious, aggressive, greedy, speedrunner)
- Tactical decision-making (attack, heal, flee, explore)
- Bot soak testing (hundreds of runs)
- Telemetry and survivability reporting

**What it unlocked:**
- Automated playtesting at scale
- Survivability measurement across scenarios
- Persona-specific behavior validation
- Foundation for heal logic tuning

---

### Phase 16: Difficulty Curve & First Tuning Pass

**Status:** COMPLETE (16A)

**What it addressed:**
- Difficulty curve visualization across depth
- First combat balance tuning (YAML-only changes)
- Target bands for death rate, hit rates, pressure
- Orc/zombie stat adjustments
- Player accuracy improvements

**What it unlocked:**
- Visual understanding of difficulty progression
- Baseline metrics for future comparison
- Confidence in YAML-based iteration
- Graphs: death rate, hit rates, pressure index vs depth

---

### Phase 17: Bot Survivability & Heal Logic (17A-17C)

**Status:** COMPLETE

**What it addressed:**
- Heal threshold calibration (from 3-7% emergency to 25-30% proactive)
- Panic logic for multi-attacker pressure (15% threshold)
- Potion availability detection bugs
- Adaptive heal thresholds per persona
- Combat healing enablement for balanced persona

**What it unlocked:**
- Bots that survive lethal scenarios intelligently
- Survivability metrics that reflect player experience
- Persona-specific heal strategies
- Foundation for advanced AI decision-making

---

### Phase 18: Gear Identity, Affixes, Damage Types (18.0-18.3)

**Status:** COMPLETE

**What it addressed:**
- Explicit weapon affix system (keen, vicious, fine, masterwork)
- Damage type semantics (slashing, piercing, bludgeoning)
- Armor resistances and vulnerabilities
- Monster faction damage modifiers (undead, armored)
- Weapon variant scenarios for balance testing
- Balance Suite orchestration tool

**What it unlocked:**
- Meaningful gear choices (not just +1/+2)
- Tactical weapon selection vs enemy types
- Comprehensive balance regression detection
- Weapon affix effectiveness measurement
- Balance Acceptance Contract for CI

---

### Phase 19: Monster Identity & Abilities

**Status:** COMPLETE (v4.10.0)

**What it addressed:**
- Monster-specific abilities and tactical patterns
- Orc Chieftain (rally aura), Orc Shaman (channeled chant)
- Necromancer variants (base, bone, plague, exploder)
- Lich (Soul Bolt, Soul Ward, Command the Dead, Death Siphon)
- Wraith (Life Drain), Troll (Regeneration), Skeleton (bone pile)
- Corpse Safety System (CorpseComponent prevents infinite loops)

**What it unlocked:**
- 12 new monster variants with unique abilities
- 26-scenario balance suite (all identity kits validated)
- Deterministic ability mechanics
- Faction-aware AI and aura systems

---

### Phase 20: Status Effects & Combat Depth

**Status:** COMPLETE

**What it addressed:**
- Corpse Explosion Lifecycle (FRESH/SPENT/CONSUMED)
- Status Effects: Poison, Burning, Silenced, Slowed, Entangled, Staggered
- Hazards modernization (fire/poison route through status framework)
- Weapon knockback with wall-impact stagger
- Silence canonicalization

**What it unlocked:**
- Tactical depth through persistent effects
- Environmental hazards as meaningful gameplay
- Foundation for traps (status effect routing)
- Combat variety beyond raw damage numbers

---

## Proposed Future Phases

### Phase 21: Traps & Environmental Control

**Status:** PLANNED

**Intent:**
Make dungeon layouts mechanically meaningful beyond monster placement.

**Trap Types:** Spike, Root, Gas, Fire, Teleport, Hole (rare)

**Design Principles:**
- Traps trigger on tile entry (post-successful movement)
- Effects route through existing canonical systems
- No instant death — all survivable
- Knockback into traps is valid interaction

---

### Phase 22: Progression & Meta Systems

**Status:** PLANNED

**Intent:**
Layer meta-progression on top of single-run gameplay.

**Potential features:**
- Unlock system, persistent upgrades, challenge modifiers
- Scoring system and leaderboards
- Achievement tracking

---

### Phase 23: Content Expansion & Polish

**Status:** PLANNED

**Intent:**
Expand existing systems with more content rather than new mechanics.

**Potential features:**
- More monster families, expanded item pool
- Additional spell schools, unique boss encounters
- Biome variety, sound effects, particle effects

---

## Phase Management Notes

### How Phases Are Chosen

Phases are not strictly linear. The order reflects:
1. **Dependencies** (foundation before features)
2. **Risk** (validate core assumptions early)
3. **Feedback** (prioritize based on playtesting)
4. **Momentum** (capitalize on related work)

### When to Start a New Phase

Start a new phase when:
- Previous phase is stable and tested
- Clear problem statement exists
- Success criteria are definable
- Dependencies are satisfied

### Phase Documentation Standards

Each phase should have:
- Problem statement (why)
- Goals (what)
- Deliverables (concrete outputs)
- Success criteria (how we know it's done)
- Key files changed (what/where)

---

## Related Documentation

- **Design Principles:** `docs/DESIGN_PRINCIPLES.md`
- **Balance System:** `docs/balance/balance_system_overview.md`
- **Pressure Model:** `docs/DEPTH_PRESSURE_MODEL.md`
- **Player Progression:** `docs/PLAYER_PROGRESSION_DOCTRINE.md`
- **Pain Points:** `docs/PLAYER_PAIN_POINTS.md`
- **Traditional Features:** `docs/TRADITIONAL_ROGUELIKE_FEATURES.md`

---

## Changelog

- **2024-12-14:** Document created (backfilled Phases 1-18, proposed 19-23)
