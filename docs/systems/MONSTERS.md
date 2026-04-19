# Monsters

**Source:** `config/entities.yaml` → `monsters:` section  
**Implementation status:** All monsters fully implemented. AI types, faction system, and special abilities all live.

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

## AI Types

| AI Type | Behaviour |
|---|---|
| `basic` | Seeks player, moves toward and attacks. Standard melee AI. |
| `skeleton` | Basic + attempts to maintain distance; prefers ranged positions. |
| `skirmisher` | Mobile: attacks then retreats. Uses speed bonus offensively. |
| `orc_shaman` | Casts rally (buffs nearby allies). Seeks distance from player. Casts when allies in range. |
| `orc_chieftain` | Issues Rally to nearby orcs (+1 to-hit, +1 damage until chieftain takes damage). High seek distance. |
| `necromancer` | Raises nearby corpses (cooldown 4t, range 5). Kites at preferred distance 4–7. Flees if player within 2. |
| `plague_necromancer` | Necromancer variant: raises corpses as plague_zombies instead. |
| `lich` | Full caster: Soul Bolt (18% of target HP, range 7, cooldown 8t), Command the Dead (radius 6), Death Siphon (radius 6), Raise Dead (cooldown 4t). Kites at 4–7. |

---

## Special Abilities

### On-Hit Effects (Automatic on Every Hit)

| Monster | Effect | Duration |
|---|---|---|
| `cave_spider` | Poison (2 dmg/turn) | 10 turns |
| `web_spider` | Slowed (half speed) | 10 turns |
| `fire_beetle` | Burning (3 dmg/turn) | 5 turns |
| `plague_zombie` | Plague (1 dmg/turn) | 20 turns |

### Damage Resistances / Vulnerabilities

| Monster | Resists | Vulnerable |
|---|---|---|
| `skeleton` | Piercing | Bludgeoning |
| `cave_spider` | — | — |
| `fire_beetle` | Fire | — |
| `zombie` | Piercing | Bludgeoning |
| `plague_zombie` | Piercing | Bludgeoning |
| `wraith` | — | — |

### Passive Abilities

| Monster | Ability | Details |
|---|---|---|
| `troll` | Regeneration | Heals 2 HP/turn automatically |
| `troll_ancient` | Regeneration | Heals 3 HP/turn |
| `wraith` | Life Drain | Hits drain 50% of damage dealt from player's max HP |
| `wraith` | Incorporeal | `no_flesh` tag, immune to certain effects |
| `large_slime` | Split | When HP drops to 40%, spawns 2–3 slimes |
| `greater_slime` | Split | When HP drops to 35%, spawns 2 large_slimes |
| `slime`, `large_slime`, `greater_slime` | Corrosion | 5–15% chance per hit to corrode equipment (damage_resistance, material) |

### Lich Soul Bolt

Soul Bolt deals `18% of player's current HP` as damage. Range 7 tiles. Cooldown 8 turns. The lich charges for 1 turn before firing (ChargingSoulBoltEffect marker).

---

## Factions

Factions determine which monsters are hostile to each other (and affected by `AggravatedEffect`):

| Faction | Members |
|---|---|
| `orc` | orc, orc_brute, orc_skirmisher, orc_shaman, orc_chieftain, orc_veteran, troll, troll_ancient |
| `undead` | skeleton, zombie, plague_zombie, wraith, lich |
| `beast` | cave_spider, web_spider, fire_beetle, giant_spider, slime, large_slime, greater_slime |
| `cultist` | necromancer, plague_necromancer, cultist_blademaster |
| `monsters` | fire_beetle (mixed category) |

Monsters do not attack their own faction by default. `AggravatedEffect` and `EnragedEffect` override this.

---

## Monster Equipment

Some monsters spawn with equipment:

| Monster | Main Hand | Chest | Spawn Chance |
|---|---|---|---|
| `orc` | club (40%), dagger (30%), shortsword (30%) | leather_armor (100%) | Hand: 75%, Chest: 50% |
| `orc_brute` | (inherits orc pool) | (inherits orc pool) | Same rates |
| `orc_chieftain` | (inherits orc pool) | (inherits orc pool) | Same rates |

Monsters with equipment drop it on death. Item condition / enchantment is not degraded.

---

## Status Immunities

| Monster | Immune To |
|---|---|
| `wraith` | confusion, slow, fear |
| `lich` | confusion, slow, fear, poison, bleed |

Immunities prevent the status effect from being applied at all (SpellResolver checks before applying).

---

## Corpse System

Most monsters leave a corpse on death (`leaves_corpse: true` by default). Exceptions:
- `slime` — `leaves_corpse: false`
- `wraith` — `leaves_corpse: false`
- `lich` — `leaves_corpse: false`

Corpses are required for `raise_dead` spells (Scroll/Wand of Raise Dead, Necromancer AI). A raised corpse becomes a temporary player-allied monster.
