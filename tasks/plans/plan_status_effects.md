# Plan: Status Effects System

Status: [ ] Not started
PoC reference: components/status_effects.py (~2,600 lines)

---

## What It Is

Duration-based effects applied to entities (player or monsters). Each effect has a lifecycle: apply, tick per turn, expire. Effects are visible in the UI (status bar / message log). Many combat interactions depend on this system existing.

## Effect Lifecycle

1. **Apply** — triggered by spell, item, trap, attack
2. **Turn Start / Turn End** — tick duration, process DOT/HOT, check expiry
3. **Remove** — duration hits 0 or dispelled; reverse stat changes; log message

Effects should NOT stack duplicates by default (re-applying refreshes duration instead).

---

## Effect Inventory (30+ types)

### Offensive / Debuffs

| Effect | Source | Mechanic |
|--------|--------|----------|
| `PoisonEffect` | Plague zombie hit, Dragon Fart | DOT damage per turn + status marker |
| `BurningEffect` | Fire traps, fire arrows, fire hazards | Fire DOT per turn |
| `BlindedEffect` | Sunburst Potion, spells | Reduced accuracy (significant penalty) |
| `SleepEffect` | Dragon Fart secondary effect | Skip turns; wake on damage |
| `ConfusedEffect` | Confusion Potion/Scroll | Random movement/attacks for duration |
| `SlowedEffect` | Web trap, net arrow, Slow Potion | Act every 2nd turn |
| `EntangledEffect` | Root Potion, root trap | Cannot move; can still attack |
| `DisarmedEffect` | Disarm Scroll | Cannot make weapon attacks |
| `SilencedEffect` | Silence Scroll | Cannot cast spells / use wands |
| `WeaknessEffect` | Specific monster abilities | Damage penalty |
| `ImmobilizedEffect` | Paralysis traps/spells | No actions at all |
| `EnragedEffect` | Some orc abilities | Forced to attack nearest entity, friend or foe |

### Defensive / Buffs

| Effect | Source | Mechanic |
|--------|--------|----------|
| `InvisibilityEffect` | Potion of Invisibility | Most AI ignores player; 30 turns default |
| `ShieldEffect` | Shield Scroll | +4 defense for duration; 10% backfire when cast by monsters |
| `ProtectionEffect` | Potion of Protection | Flat damage reduction |
| `RegenerationEffect` | Specific items/boons | Heal N HP per turn |
| `SpeedEffect` | Potion of Speed | Extra turn per turn (act twice) |
| `BarkskinEffect` | Root Potion secondary | Defensive buff (armor bonus) |
| `FocusedEffect` | Sunburst Potion secondary | Accuracy buff |
| `HeroismEffect` | Future item | Combat buff (accuracy + damage) |
| `LevitationEffect` | Future item | Ignore ground hazards |

### Special / Contextual

| Effect | Source | Mechanic |
|--------|--------|----------|
| `SluggishEffect` | Slow Potion at lower magnitude | Speed penalty (not full skip) |
| `DisorientationEffect` | Disorientation attacks | AI swap — monster briefly attacks own faction |
| `EngulfedEffect` | Slime contact | Movement penalty while adjacent to slime |

### Boss-Specific (Phase 22.1.1 Oaths)

| Effect | Trigger | Mechanic |
|--------|---------|----------|
| `OathEmbersEffect` | Oath of Embers build | Conditional fire proc on hit |
| `OathVenomEffect` | Oath of Venom build | Stacking poison on hit |
| `OathChainsEffect` | Oath of Chains build | Bonus damage when hitting multiple targets |

---

## Design Rules

- **No duplicate stacking** — re-applying refreshes duration, doesn't double the effect
- **Wake on damage** — Sleep breaks when entity takes damage
- **Entangle vs Immobilize** — Entangled can attack; Immobilized cannot act at all
- **Monster spell failure** — monsters casting Shield have 10% backfire; other spells have 50% failure rate
- **Silence blocks wands too** — not just innate spellcasting

---

## Status Display

- UI: Show active effects with remaining turns in status panel or as small icons
- Message log: "You are poisoned!" / "The poison fades."
- Monsters also show visible effect markers (color tint or icon)

---

## Ground Hazards (related)

These are floor-tile effects, not entity effects, but created by the same spells:
- **Fire hazard** — Fireball creates burning floor tiles for N turns; deal fire DOT to anyone entering
- **Poison gas** — Dragon Fart cone; gas cloud persists for N turns
- **Spike zone** — Spike trap discharge; single-use floor damage

Ground hazards interact with status effects (walking into fire can apply `BurningEffect`).

---

## Implementation Notes

- Base class `StatusEffect` with `Duration`, `Apply()`, `OnTurnStart()`, `OnTurnEnd()`, `Remove()`
- `Entity` has `List<StatusEffect> ActiveEffects`
- Combat system checks effects before resolving actions (is DisarmedEffect active? block attack)
- Movement system checks effects (is EntangledEffect or ImmobilizedEffect active? block move)
- Spell system checks SilencedEffect before allowing spell/wand usage
- Turn controller must call `ProcessEffects()` at start or end of each entity's turn

## C# Port Checklist

- [ ] `StatusEffect` base class with lifecycle hooks
- [ ] All 30+ effect concrete types
- [ ] `Entity.ActiveEffects` collection with add/remove/refresh logic
- [ ] Integration with combat (DisarmedEffect, WeaknessEffect)
- [ ] Integration with movement (EntangledEffect, ImmobilizedEffect, SlowedEffect)
- [ ] Integration with spells (SilencedEffect)
- [ ] DOT/HOT tick processing in TurnController
- [ ] Ground hazard tile type + entry trigger
- [ ] UI status display (HUD panel or icons)
- [ ] YAML-driven durations and magnitudes
