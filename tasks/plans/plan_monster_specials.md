# Plan: Special Monster Mechanics

Status: [~] In progress
PoC reference: components/ai/, services/slime_split_service.py, components/corpse.py
Implementation plan: tasks/plans/plan_monster_specials_impl.md

---

## What It Is

Monster types beyond basic "pursue and attack." Each of these systems creates distinct tactical scenarios that can't be solved with just "walk up and hit it."

---

## 1. Necromancer / Corpse Lifecycle

### Why It Matters

Necromancers transform dead bodies into new threats. If you don't manage corpses (finish necromancer first, burn/poison areas to deny corpses), a single necromancer can undo all your hard-fought kills.

### Corpse States

1. **Fresh Corpse** — newly dead; can be raised OR looted
2. **Spent Corpse** — already raised from; weaker minion quality; can't be raised again
3. **Destroyed Corpse** — fire/acid/plague explosion; gone entirely

### Necromancer AI Behavior

- In combat: attempt to raise nearest fresh corpse first (before attacking)
- Navigation: pathfind to corpse location (not just enemies)
- Safety check: won't pathfind into fire/poison hazards to reach corpse
- After raising: returns to combat AI

### Raise Mechanic

- Fresh corpse → `skeleton` (basic minion)
- Spent corpse → weaker minion (bone fragment or similar)
- Raised minions join necromancer's faction

### Necromancer Variants

| Variant | Specialty |
|---------|-----------|
| `necromancer` | Basic; raises skeletons from fresh corpses |
| `bone_necromancer` | Focuses on bone minions; faster raise |
| `plague_necromancer` | Spreads PlagueEffect to nearby entities; raises plague zombies |
| `exploder_necromancer` | Raises volatile minions; they explode on death (AoE damage) |

### Counters / Counterplay

- Kill necromancer before it can raise
- Create fire/poison hazards near corpses to deny raises
- Use Disarm on necromancer (prevents raise action? TBD)
- Holy/light damage if implemented could destroy corpses

### Metrics

- `fresh_corpses_created`
- `spent_corpses_created`
- `raises_completed`
- `spent_corpses_exploded` (exploder variant)

---

## 2. Slime Split System

### Why It Matters

Slimes punish AoE and brute-force clearing. Hitting a big slime hard enough splits it into multiple smaller threats. A room that was one `greater_slime` becomes three `slime` problems.

### Slime Hierarchy

```
greater_slime (most HP, most dangerous)
    ↓ split
large_slime × 2 (medium)
    ↓ split
slime × 3 (small, weak individually)
```

### Split Trigger

- Splits occur when slime HP drops below 50% from a single hit (or configurable threshold)
- New slimes spawn adjacent to original; original is removed
- Splits don't trigger recursively in same turn (small slimes don't split further)

### Engulf Effect

- When player is **adjacent** to any slime, applies `EngulfedEffect`
- EngulfedEffect: movement speed reduced (or costs extra action points)
- Effect refreshes each turn the player remains adjacent
- Disappears when player breaks contact with all slimes

**Key tactical decision**: Do you run away (escaping engulf but possibly splitting the slime) or fight through it?

### Metrics

- `split_events_total`
- `slimes_spawned_from_splits`

---

## 3. Skirmisher AI (Phase 22.3)

### Why It Matters

Creates a mobile threat type that can't be kited safely. Skirmishers leap over tiles to engage — keeping 4+ tiles away isn't safe anymore.

### Leap Mechanic

- **Leap range**: 2-3 tiles (hops over gaps)
- **Trigger**: Leap when target is in range but not adjacent, AND cooldown expired
- **Cooldown**: Can't leap every turn (prevents spam)
- **Blocked by Entangle**: Entangled skirmisher cannot leap (tactical counter)

### Hit-and-Run

After attacking adjacent target:
- 50% chance to leap away (end turn at 2-3 tile distance)
- Denies player free next-turn attack
- Re-engages next turn

### Monsters Using This AI

- `orc_skirmisher` — fast orc variant
- `cave_spider` variants — natural leapers
- Any "mobile" archetype monster

---

## 4. Orc Shaman AI

### Spells and Actions

- **Hex Curse**: Applies WeaknessEffect or accuracy penalty to target; 3-turn duration
- **War Chant**: Buff to nearby orcs (accuracy or damage bonus); shaman chants for 2 turns
- **Interrupt**: War Chant can be interrupted by hitting the shaman during chant (action wasted)

### Positioning

- Shaman prefers NOT to be adjacent to player (stays at distance 2-3)
- Will retreat if player gets adjacent
- Prioritizes healing/buffing faction over direct combat

---

## 5. Orc Chieftain AI

- **Rally**: Increases morale of nearby orcs (aggression range + hit bonus)
- **Coordinate**: Designates targets — nearby orcs preferentially attack chieftain's target
- **Tactical Retreat**: Will retreat to doorway or chokepoint when low HP, drawing player into ambush

---

## 6. Plague / Infection System (Phase 20A)

### Plague Spread

- `plague_necromancer` and `plague_zombie` can infect on hit
- PoisonEffect + special "plagued" marker
- Plagued entities spread plague on their attacks (limited duration)
- Plague zombie explosion on death creates poison gas cloud in radius

### Metrics

- `plague_applications`
- `plague_damage_dealt`
- `plague_kills`
- `plague_ticks_processed`

---

## 7. Troll Regeneration

- Trolls regenerate HP each turn (`RegenerationEffect` built-in)
- Fire or acid damage suppresses regeneration for N turns
- Dead troll can "reanimate" if not burned (design decision: maybe require fire kill?)
- Creates strong incentive to carry fire arrows

---

## C# Port Checklist

### Corpse/Necromancer
- [ ] `CorpseEntity` with state (Fresh/Spent/Destroyed)
- [ ] `NecromancerAI` — pathfind to corpse, raise action
- [ ] All 4 necromancer variants
- [ ] Corpse denied by hazard tiles (fire/poison blocks pathfinding)
- [ ] Corpse metrics collection

### Slime
- [ ] Slime hierarchy (3 sizes) in entities.yaml
- [ ] Split trigger on HP threshold
- [ ] `SlimeSplitService.TrySplit()`
- [ ] `EngulfedEffect` applied when adjacent
- [ ] Split + engulf metrics

### Skirmisher
- [ ] `SkirmisherAI` with leap capability
- [ ] Leap cooldown tracking
- [ ] Entangle blocks leap
- [ ] Hit-and-run retreat

### Shaman
- [ ] `OrcShamanAI` with Hex and War Chant
- [ ] Chant interruption mechanic
- [ ] Positioning preference (maintain distance)

### Chieftain
- [ ] `OrcChieftainAI` with Rally and Coordinate
- [ ] Retreat-to-chokepoint behavior

### Plague
- [ ] Plague spread on hit
- [ ] Plague zombie explosion on death
- [ ] Plague metrics

### Troll
- [ ] Passive RegenerationEffect
- [ ] Regen suppression by fire/acid
