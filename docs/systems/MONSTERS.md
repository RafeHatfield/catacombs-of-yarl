# Monsters

**Source:** `config/entities.yaml` → `monsters:` section  
**Last updated:** 2026-06-08 — added giant_spider on-hit poison + giant_spider/cultist_blademaster ability notes (both `basic` AI, no scripted special). Reflects all 4 waves + special abilities through monster_specials plan.

---

## Monster Stats Reference

All stats are from YAML. `etp_base` = Encounter Threat Points used for encounter budget allocation.

### Wave 1 — Orc Faction (Depth 1+)

| ID | Name | HP | Dmg | To-Hit | Evasion | Def | XP | ETP | Depth |
|---|---|---|---|---|---|---|---|---|---|
| `orc` | Orc | 28 | 4–6 | +4 | 1 | 0 | 35 | 27 | 1+ |
| `orc_brute` | Orc Brute | 42 | 5–8 | +4 | 1 | 0 | 55 | 45 | 3+ |
| `orc_skirmisher` | Orc Skirmisher | 24 | 3–5 | +4 | 3 | 0 | 45 | 28 | — |
| `orc_shaman` | Orc Shaman | 24 | 3–5 | +3 | 1 | 0 | 60 | 34 | — |
| `orc_chieftain` | Orc Chieftain | 35 | 4–6 | +4 | 1 | 0 | 75 | 57 | — |
| `orc_veteran` | Orc Veteran | 25 | 4–6 | +4 | 1 | 0 | 50 | 41 | — |
| `orc_scout` | Orc Scout | 15 | 4–6 | +4 | 1 | 0 | 25 | 21 | — |

Spawn weights: `orc` 80, `orc_brute` varies by depth (6 at d3+, 12 at d4+, 20 at d6+). Other orc variants have `spawn_weight: 0` — scenario/encounter-placed only, not random spawn.

### Wave 1 — Undead / Beast (Depth 2+)

| ID | Name | HP | Dmg | To-Hit | Evasion | Def | XP | ETP | Depth |
|---|---|---|---|---|---|---|---|---|---|
| `skeleton` | Skeleton | 20 | 3–5 | +2 | 1 | 0 | 30 | 27 | 2+ |
| `cave_spider` | Cave Spider | 16 | 2–4 | +3 | 2 | 1 | 25 | 16 | 2+ |
| `web_spider` | Web Spider | 20 | 2–4 | +3 | 2 | 1 | 40 | 22 | 3+ |
| `fire_beetle` | Fire Beetle | 12 | 2–5 | +1 | 1 | 2 | 45 | 18 | 2+ |

### Wave 2 — Mid Dungeon (Depth 2+)

| ID | Name | HP | Dmg | To-Hit | Evasion | Def | XP | ETP | Depth |
|---|---|---|---|---|---|---|---|---|---|
| `troll` | Troll | 30 | 8–12 | std | std | 2 | 100 | 50 | 4+ |
| `slime` | Slime | 15 | 1–3 | +3 | 0 | 0 | 25 | 10 | 2+ |
| `large_slime` | Large Slime | 40 | 2–5 | std | 0 | 1 | 75 | 35 | 3+ |

### Wave 3 — Cultist / Caster (Depth 5+)

| ID | Name | HP | Dmg | To-Hit | Evasion | Def | XP | ETP | Depth |
|---|---|---|---|---|---|---|---|---|---|
| `necromancer` | Necromancer | 28 | 2–4 | +4 | 2 | 0 | 80 | 44 | 5+ |
| `plague_necromancer` | Plague Necromancer | 28 | 2–4 | +4 | 2 | 0 | — | 55 | 7+ |
| `giant_spider` | Giant Spider | 18 | 4–8 | +3 | 3 | 1 | 45 | 42 | 8+ |

### Wave 4 — Deep Dungeon (Depth 10+)

| ID | Name | HP | Dmg | ETP | Depth |
|---|---|---|---|---|---|
| `zombie` | Zombie | 24 | 3–6 | 31 | 10+ |
| `plague_zombie` | Plague Zombie | 30 | 4–7 | 40 | 13+ |
| `troll_ancient` | Ancient Troll | 50 | 8–12 | 95 | 15+ |
| `greater_slime` | Greater Slime | 80 | 3–7 | 75 | 12+ |
| `cultist_blademaster` | Cultist Blademaster | 30 | 6–10 | 70 | 12+ |
| `wraith` | Wraith | 20 | 5–9 | 65 | 15+ |
| `lich` | Lich | 60 | 3–6 | 131 | 18+ |

---

## AI Types & Special Abilities

### Orc Skirmisher

**AI:** `skirmisher`

**Pouncing Leap** — When the skirmisher is 3–6 tiles (Chebyshev) from the player and the leap cooldown is 0, it lunges 2 tiles toward the player. Cooldown: 3 turns after each leap.

- Blocked by `EntangledEffect` — entangled skirmisher cannot leap (counter: net arrows).
- Speed bonus (0.20) triggers bonus attacks independently of the leap.

---

### Orc Shaman

**AI:** `orc_shaman`  
Kites at preferred distance 4–7. Panics and retreats if player within 2 tiles.  
Priority: Chant of Dissonance → Crippling Hex → positioning → melee.

**Crippling Hex** — Ranged debuff applied to the player. Range 6, cooldown 10 turns, duration 5 turns. Applies `CrippledEffect` (−1 to-hit, −1 AC).

**Chant of Dissonance** — Channeled ability. Range 5, cooldown 15 turns, channel duration 3 turns.
- While channeling: shaman cannot move or attack (consumes its action each channel turn).
- Player receives `DissonantChantEffect`: every other movement turn is skipped (alternating-skip, shares the same skip slot as Slowed/Engulfed — these don't stack).
- **Interrupted** by any attack damage > 0 on the shaman — channel ends, cooldown resets to 15, effect removed from player.
- **Silenced shaman cannot start a chant** — `SilencedEffect` blocks the cast.
- Shaman death cleans up the player's `DissonantChantEffect` immediately.

---

### Orc Chieftain

**AI:** `orc_chieftain`  
Kites at preferred distance 3–6. Panics and retreats if player within 2 tiles.  
Priority: Rally → Sonic Bellow → positioning → melee.

**Rally Cry** — Fires once per encounter when ≥2 orc allies are within range 5. Applies `RallyEffect` (+1 to-hit, +1 damage) to the chieftain and all qualifying orc allies. Also cleanses `FearEffect` from rallied allies.
- **Ends immediately** when the chieftain takes any attack damage > 0 (all carrier orcs lose the buff simultaneously).
- DOT damage (burning, poison) does not break rally — only direct attack hits.
- Rally cannot re-fire after it ends.

**Sonic Bellow** — Fires once per encounter when chieftain HP drops below 50%. Applies `CrippledEffect` (−1 to-hit, −1 AC, duration 2 turns) to the player.

---

### Troll / Ancient Troll

**AI:** `basic`

**Regeneration** — Heals automatically each turn (troll: 2 HP/turn; troll_ancient: 3 HP/turn).  
**Suppressed** when `AcidEffect` OR `BurningEffect` is active on the troll — neither effect ticks regen while present. This makes fire arrows and acid traps tactically meaningful against trolls.

---

### Slimes (slime, large_slime, greater_slime)

**AI:** `basic`

**Engulf** — On any successful hit against the player, applies `EngulfedEffect` (duration 3 turns, deterministic — no RNG).
- While engulfed and adjacent to any slime at turn start, duration refreshes to 3.
- If no slime is adjacent, duration decays normally.
- Engulfed player skips every other movement turn (alternating-skip, same slot as Slowed/Chanted).

**Corrosion** — Each hit has a 5–15% chance to corrode the player's metal weapon (reduces DamageMax). Chance and severity vary by slime type.

**Split** (large_slime, greater_slime) — When HP drops below the split threshold mid-hit:
- `large_slime` → spawns 2–3 `slime` entities.
- `greater_slime` → spawns 2 `large_slime` entities.

---

### Necromancer / Plague Necromancer

**AI:** `necromancer`  
Kites at preferred distance 4–7. Flees if player closes to 2.

**Raise Dead** — Pathfinds to the nearest fresh corpse (range 5) and raises it as a skeleton ally. Cooldown 4 turns. Will not pathfind through fire/poison hazards to reach a corpse.

**Plague Necromancer variant** — Raises corpses as `plague_zombie` instead of `skeleton`. Otherwise identical AI.

---

### Wraith

**AI:** `basic`

**Life Drain** — Hits drain HP equal to 50% of damage dealt from the player's max HP pool (not current HP). This heals the wraith.

**Incorporeal** (`no_flesh` tag) — Immune to confusion, slow, and fear. Cannot be possessed.

---

### Lich

**AI:** `lich`  
Kites at preferred distance 4–7.

**Soul Bolt** — Deals 18% of the player's current HP as damage. Range 7, cooldown 8 turns. The lich channels for 1 turn (`ChargingSoulBoltEffect`) before firing — interrupting it by killing the lich cancels the bolt.

**Command the Dead** — Rallies nearby undead allies (radius 6).

**Death Siphon** — When an allied undead dies within radius 6, the lich heals.

**Raise Dead** — Raises nearby corpses (cooldown 4 turns).

Cannot be possessed.

---

### Giant Spider / Cultist Blademaster

**AI:** `basic` (both)

Neither has a scripted special. The **Giant Spider** is a high-damage poison beast (poison on hit — see On-Hit Status Effects). The **Cultist Blademaster** is a pure melee beatstick — high damage (6–10), no status, no ability hook. Its threat is raw DPR, not mechanics.

---

## On-Hit Status Effects

| Monster | Effect | Chance | Duration |
|---|---|---|---|
| `cave_spider` | Poison (2 dmg/turn) | 100% | 10 turns |
| `giant_spider` | Poison (2 dmg/turn) | 100% | 10 turns |
| `web_spider` | Slowed (skip every other move) | 100% | 10 turns |
| `fire_beetle` | Burning (3 dmg/turn) | 100% | 5 turns |
| `plague_zombie` | Plague (1 dmg/turn, spreads) | 100% | 20 turns |
| `slime`, `large_slime`, `greater_slime` | Engulfed (skip every other move while adjacent) | 100% | 3 turns (refreshes) |

---

## Passive Abilities Summary

| Monster | Ability | Details |
|---|---|---|
| `troll` | Regeneration | +2 HP/turn. Suppressed by Burning or Acid. |
| `troll_ancient` | Regeneration | +3 HP/turn. Suppressed by Burning or Acid. |
| `wraith` | Life Drain | Heals 50% of damage dealt from player max HP. |
| `large_slime` | Split | Spawns 2–3 slimes when HP falls below 40%. |
| `greater_slime` | Split | Spawns 2 large_slimes when HP falls below 35%. |
| `slime`, `large_slime`, `greater_slime` | Corrosion | 5–15% chance/hit to degrade metal weapons. |

---

## Damage Resistances / Vulnerabilities

| Monster | Resists | Vulnerable |
|---|---|---|
| `skeleton` | Piercing | Bludgeoning |
| `zombie` | Piercing | Bludgeoning |
| `plague_zombie` | Piercing | Bludgeoning |
| `fire_beetle` | Fire | — |

---

## Status Immunities

| Monster | Immune To |
|---|---|
| `wraith` | confusion, slow, fear, possessed |
| `lich` | confusion, slow, fear, poison, bleed, possessed |

Immunities prevent the status effect from being applied at all. `possessed` immunity means the player's possession ability has no effect.

---

## Factions

Factions determine which monsters are hostile to each other (and affected by `AggravatedEffect`). Monsters do not attack their own faction by default.

| Faction | Members |
|---|---|
| `orc` | orc, orc_grunt, orc_brute, orc_skirmisher, orc_shaman, orc_chieftain, orc_veteran, orc_scout, troll, troll_ancient |
| `undead` | skeleton, zombie, plague_zombie, wraith, lich |
| `beast` | cave_spider, web_spider, fire_beetle, giant_spider, slime, large_slime, greater_slime |
| `cultist` | necromancer, plague_necromancer, cultist_blademaster |

---

## Monster Equipment

Some monsters spawn with equipment (dropped on death):

| Monster | Main Hand | Chest | Hand Chance | Chest Chance |
|---|---|---|---|---|
| `orc` | club (40%), dagger (30%), shortsword (30%) | leather_armor | 75% | 50% |
| `orc_brute` | (inherits orc pool) | (inherits orc pool) | 75% | 50% |
| `orc_chieftain` | (inherits orc pool) | (inherits orc pool) | 75% | 50% |

---

## Corpse System

Most monsters leave a corpse on death (`leaves_corpse: true` by default). Exceptions:

| Monster | Reason |
|---|---|
| `slime` | Dissolves on death |
| `wraith` | Incorporeal — no physical remains |
| `lich` | Dissipates |

Corpses are required for Raise Dead (scroll, wand, necromancer AI). A raised corpse becomes a temporary player-allied or faction-allied monster depending on who raised it.
