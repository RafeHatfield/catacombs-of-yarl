# Plan: Spell / Wand / Scroll System

Status: [ ] Not started
PoC reference: spells/spell_catalog.py, spells/spell_executor.py, item_functions.py

---

## Architecture Overview

Three delivery mechanisms for spells:
- **Scrolls** — single-use, player only, consumable from inventory
- **Wands** — limited charges, reusable until empty, rechargeable
- **Monster casting** — monsters cast via AI; 50% failure rate

Spells themselves are defined separately from delivery mechanism. The same spell definition can be on a scroll, in a wand, or cast by a monster.

---

## Spell Catalog (30+ spells)

### Offensive

| Spell | Effect | Targeting |
|-------|--------|-----------|
| `lightning_bolt` | 3d8 lightning damage | Single enemy, LOS required |
| `fireball` | 3d6 fire damage, radius 3, creates fire hazard | Location |
| `dragon_fart` | Poison cone, applies SleepEffect + PoisonEffect | Cone (direction) |
| `confusion` | Applies ConfusedEffect for 8 turns | Single enemy |
| `disarm` | Applies DisarmedEffect | Single enemy |
| `silence` | Applies SilencedEffect | Single enemy |
| `slow` | Applies SlowedEffect | Single enemy |
| `fear` | Enemy flees for duration | Single enemy |

### Healing

| Spell | Effect | Targeting |
|-------|--------|-----------|
| `healing` | Restore 20 HP | Self |
| `full_heal` | Restore to max HP | Self (rare, late game) |

### Utility / Buff

| Spell | Effect | Targeting |
|-------|--------|-----------|
| `invisibility` | Applies InvisibilityEffect, 30 turns | Self |
| `teleport` | Random relocation in current floor | Self |
| `shield` | +4 defense, applies ShieldEffect | Self (or monster target with 10% backfire) |
| `enhance_weapon` | Increase equipped weapon's damage range permanently | Self/weapon |
| `identify` | Reveal true identity of one item | Item in inventory |
| `entangle` / `glue` | Applies EntangledEffect | Single enemy |
| `rage` | Applies EnragedEffect + damage buff to target | Single enemy (or self variant) |
| `protection` | Applies ProtectionEffect (damage reduction) | Self |

### Area / Hazard-Creating

| Spell | Effect | Targeting |
|-------|--------|-----------|
| `fireball` | Creates fire hazard tiles in radius | Location |
| `dragon_fart` | Creates poison gas cloud in cone | Directional cone |

---

## Spell Properties

Each `SpellDefinition` in YAML has:

```yaml
lightning_bolt:
  targeting: SINGLE_ENEMY      # SINGLE_ENEMY | AOE | CONE | LOCATION | SELF | SINGLE_ANY
  damage: 3d8
  damage_type: LIGHTNING
  requires_los: true
  range: 8
  effects: []                  # status effects to apply
  hazard: null                 # ground hazard created
```

---

## Wand System

Wands are equippable items (quiver slot or held) with:
- `spell_type` — which spell they cast
- `charges` — remaining uses (shown as "Wand of Lightning (3)")
- `max_charges` — maximum when fully charged

**Mechanics:**
- Casting depletes 1 charge
- At 0 charges: "The wand is spent" — can keep for recharging
- **Enhance Weapon scroll** can recharge a wand to max charges (or a specified wand recharge scroll)
- Unknown wands show material name ("Iron Wand", "Crystal Wand") until identified

**Identification via use** — using an unidentified wand identifies it (you learn what it was after the effect fires).

---

## Scroll System

Scrolls are single-use consumables:
- Used from inventory — fires spell immediately
- Most scrolls target self or require a secondary target selection
- Unknown scrolls show scroll description ("Crinkled Scroll", "Glowing Scroll") until ID'd

**Key scrolls:**
- Scroll of Identify — pick any item, reveal it
- Scroll of Enhance Weapon — upgrade weapon damage die OR recharge a wand
- Scrolls of offensive spells (Lightning, Fireball, etc.)

---

## Monster Spell Usage

Monsters with spell abilities cast from their AI turn:
- **50% failure rate** for all monster spellcasting (balance lever)
- Failed cast: "The orc shaman's chant fizzles" — wastes their action
- Monsters do NOT use scrolls or wands from inventory (too powerful); they only cast innate spells
- Exception: monsters CAN pick up scrolls and attempt to use them, but with the 50% failure rate AND an additional "wrong spell" chance

**Monster spell types** (innate AI abilities):
- Orc Shaman: hex curse, war chant
- Lich: shield, evasion, offensive spells
- Necromancer variants: raise skeleton, raise plague zombie
- Plague Necromancer: spread plague

---

## Targeting System

- `SELF` — immediate effect, no targeting UI
- `SINGLE_ENEMY` — player selects target from visible enemies
- `SINGLE_ANY` — player selects any tile
- `LOCATION` — player selects tile (AOE from that point)
- `CONE` — player selects direction (4 directions)
- `AOE` — immediate radius around caster

Targeting requires UI for SINGLE_ENEMY, LOCATION, CONE. SELF fires immediately.

---

## Spell Executor

`SpellExecutor.Execute(caster, spell, target)`:
1. Validate target (LOS check if required, range check)
2. Apply damage if applicable (routes through combat service)
3. Apply status effects to target
4. Create ground hazards at target location if applicable
5. Generate message log entries
6. Return result (hit/miss/effects applied)

---

## C# Port Checklist

- [ ] `SpellDefinition` YAML schema (targeting, damage, effects, hazard)
- [ ] `SpellRegistry` — loads and indexes all spell defs from YAML
- [ ] `SpellExecutor.Execute()` with all targeting types
- [ ] Scroll item type (consumable, fires spell on use)
- [ ] Wand item type (charges, recharge mechanic)
- [ ] Wand charges in UI display ("Wand of Lightning (3)")
- [ ] Targeting UI for SINGLE_ENEMY, LOCATION, CONE modes
- [ ] Monster innate spell casting (AI-driven, 50% failure)
- [ ] Monster scroll pickup + use (50% failure + chance of wrong spell)
- [ ] Ground hazard tile system (fire, poison gas)
- [ ] Enhance Weapon scroll: upgrade damage die OR recharge wand
- [ ] Identify scroll: inventory picker → reveal item
- [ ] Integration with identification system (unidentified aliases for wands/scrolls)
