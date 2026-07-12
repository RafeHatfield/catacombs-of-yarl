# Status Effects

_Last verified: 2026-07-12 against commit 86b6f10_

**Source:** `src/Logic/Combat/StatusEffects/`  
**Implementation status:** All effects listed below are fully implemented. Duration refresh on re-application: takes the max of existing and new duration (not stacked/additive).

---

## Effect Application Rules

- Re-applying an effect that is already active takes `max(existing_remaining, new_duration)` — no extension exploit from spamming.
- Effects are decremented once per entity turn (not per game turn).
- `SilencedEffect` blocks scroll and wand use but not potions.
- `ImmobilizedEffect` and `EntangledEffect` both prevent movement; the difference is source (paralysis potion vs glue) and whether attacks are also blocked.

---

## Debuff Effects (Negative)

### Damage Over Time

| Effect | Source(s) | Damage/Turn | Duration | Notes |
|---|---|---|---|---|
| `BurningEffect` | Fire Beetle (on-hit), Fire Potion, Fireball ground | 3 | 5 turns | Ground hazard variant: decaying |
| `PoisonEffect` | Cave Spider (on-hit), Potion of Weakness throw | 2 | 10 turns | DOT does NOT wake sleeping entities |
| `PlagueEffect` | Plague Zombie (on-hit), Scroll/Wand of Plague | 1 | 20 turns | Curable only by Antidote Potion |

### Movement Impairment

| Effect | Source(s) | Mechanical Effect | Duration |
|---|---|---|---|
| `SlowedEffect` | Scroll/Wand of Slow, Web Spider (on-hit), Tar Potion throw | Acts every other turn | 10 turns |
| `SluggishEffect` | Potion of Slowness (drink/throw) | Half speed ratio applied (via SpeedBonusTracker) | 20 turns |
| `EntangledEffect` | Scroll/Wand of Glue, Root Potion throw | Cannot move; can still attack | 5 turns |
| `ImmobilizedEffect` | Potion of Paralysis (drink/throw) | Cannot move or attack | 3–5 turns (random) |

### Cognitive / Targeting Impairment

| Effect | Source(s) | Mechanical Effect | Duration |
|---|---|---|---|
| `ConfusedEffect` | Scroll/Wand of Confusion, Dragon Fart cloud | Random movement/attack directions | 10 turns |
| `BlindedEffect` | Potion of Blindness (drink/throw), Sunburst Potion throw | −4 accuracy | 15 turns |
| `FearEffect` | Scroll/Wand of Fear | Flee from player (opposite direction movement) | 15 turns |
| `DisorientationEffect` | Earthquake spell (secondary effect) | Reduced accuracy; stumble movement | 3 turns |
| `SleepEffect` | (internal use, some monster abilities) | Cannot act; wakes on taking damage | 3 turns |

### Stat Reduction

| Effect | Source(s) | Mechanical Effect | Duration |
|---|---|---|---|
| `WeaknessEffect` | Potion of Weakness (drink self = bad, throw at enemy = good) | −power penalty to damage | 30 turns |
| `CrippledEffect` | Earthquake secondary, some monster abilities | −1 to-hit, −1 AC | 5 turns |
| `DisarmedEffect` | Scroll/Wand of Disarm | Fights barehanded (no weapon damage) | 3 turns |
| `SilencedEffect` | Scroll/Wand of Silence | Cannot use scrolls or wands | 3 turns |

### Rage / Aggression

| Effect | Source(s) | Mechanical Effect | Duration |
|---|---|---|---|
| `EnragedEffect` | Scroll/Wand of Rage | 2× damage multiplier; attacks any adjacent entity | 8 turns |
| `AggravatedEffect` | Scroll of Yo Mama, Scroll of Aggravation | Permanently targets player / own faction | Permanent |
| `TauntedEffect` | (internal: orc chieftain taunt ability) | Forces target to attack the chieftain | Variable |

---

## Buff Effects (Positive)

### Healing / Regen

| Effect | Source(s) | Effect | Duration |
|---|---|---|---|
| `RegenerationEffect` | Potion of Regeneration, Ring of Regeneration (passive) | 2 HP/turn | 20 turns |
| `HeroismEffect` | Potion of Heroism | +3 to-hit, +3 damage | 30 turns |

### Defensive

| Effect | Source(s) | Effect | Duration |
|---|---|---|---|
| `ProtectionEffect` | Potion of Protection | +3 AC | 50 turns |
| `ShieldEffect` | Scroll of Shield | +3 AC | 10 turns |
| `BarkskinEffect` | Root Potion (drink) | +3 AC | 10 turns |

### Mobility / Offense

| Effect | Source(s) | Effect | Duration |
|---|---|---|---|
| `SpeedEffect` | Potion of Speed, Scroll/Wand of Haste | +50% speed ratio (extra actions via momentum) | 20 turns |
| `InvisibilityEffect` | Scroll/Wand/Potion of Invisibility | Monsters cannot target you | 30 turns |
| `FocusedEffect` | Sunburst Potion (drink) | +3 accuracy | 8 turns |

### Monster Buffs (AI-Applied)

| Effect | Source | Effect | Notes |
|---|---|---|---|
| `RallyEffect` | Orc Chieftain | +1 to-hit, +1 damage to nearby orcs | Removed when chieftain takes damage |
| `ChargingSoulBoltEffect` | Lich (internal) | Marker: charging Soul Bolt this turn | 1 turn marker only |

---

## Immunities by Monster

See `MONSTERS.md` for per-monster immunity lists. FreeActionTag (from Ring of Free Action) grants player immunity to `SlowedEffect` and `ImmobilizedEffect`.

---

## Ground Hazard Effects

These are technically ground tile effects, not entity status effects, but they deal damage to entities moving through them. See `GROUND_HAZARDS.md` for full details.

| Hazard | Created By | Effect |
|---|---|---|
| Fire | Fireball, Fire Potion | BurningEffect on entities that enter/remain |
| Poison Gas | Dragon Fart | ConfusedEffect + ongoing damage on entities in area |
