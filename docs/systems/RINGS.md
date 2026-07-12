# Rings

_Last verified: 2026-07-12 against commit 86b6f10_

**Source:** `config/entities.yaml` → `rings:` section; `src/Logic/ECS/RingEffectComponent.cs`  
**Implementation status:** 16 rings defined. 10 are fully functional; 6 are no-op stubs (equip/unequip is handled, but the passive effect does nothing — their `RingEffectKind` is not handled in the `TurnController` ring-effect switch).

---

## Equipment Slots

Two ring slots: `ring_left` and `ring_right`. Both can be equipped simultaneously. Ring effects stack when wearing two of the same type.

---

## Phase 1 — Fully Implemented

| Item ID | Name | Effect | Strength |
|---|---|---|---|
| `ring_of_protection` | Ring of Protection | +2 to `BaseDefense` (flat AC) | +2 AC |
| `ring_of_strength` | Ring of Strength | +2 to `Strength` stat | +2 STR |
| `ring_of_dexterity` | Ring of Dexterity | +2 to `Dexterity` stat | +2 DEX |
| `ring_of_constitution` | Ring of Constitution | +2 `Constitution`, increases max HP, heals on equip | +2 CON |
| `ring_of_might` | Ring of Might | +4 flat damage bonus to min and max damage | +4 damage |
| `ring_of_regeneration` | Ring of Regeneration | Passively heals 1 HP every 5 turns | Interval: 5t |
| `ring_of_speed` | Ring of Speed | +10% speed bonus (adds to SpeedBonusTracker.RingRatio) | +10% speed |
| `ring_of_hummingbird` | Ring of Hummingbird | +25% speed bonus (stronger speed ring) | +25% speed |
| `ring_of_free_action` | Ring of Free Action | Immune to Slow and Paralysis (adds FreeActionTag) | — |
| `ring_of_teleportation` | Ring of Teleportation | 20% chance per hit received to teleport to a random open tile | 20% proc |

---

## Phase 2 — Stubs (Equip Works, Effect Is a No-Op)

These rings can be picked up, equipped, and identified, but their passive effect does nothing yet. They are not in the floor item pool.

| Item ID | Name | Intended Effect | Blocking System |
|---|---|---|---|
| `ring_of_resistance` | Ring of Resistance | Elemental resistance (fire/poison/cold) | Ring effect not wired — the `Resistance` `RingEffectKind` is not handled in `TurnController`. (The damage-type resistance *combat* mechanic itself is built — `DamageModifiers.cs` — the ring just doesn't grant it yet.) |
| `ring_of_clarity` | Ring of Clarity | Slow magic charge drain or anti-confusion | Unclear scope, deferred |
| `ring_of_invisibility` | Ring of Invisibility | Passive invisible while still | Requires monster targeting integration |
| `ring_of_searching` | Ring of Searching | Auto-detect secret doors / traps nearby | Ring effect not wired — the `Searching` `RingEffectKind` is not handled in `TurnController`. (Traps and secret doors themselves are built; the ring just doesn't reveal them yet.) |
| `ring_of_wizardry` | Ring of Wizardry | Extra wand charges or reduced scroll fail chance | No magic system to plug into |
| `ring_of_luck` | Ring of Luck | Improved crit chance or loot luck | System undefined |

---

## Speed Ring Mechanics

`ring_of_speed` and `ring_of_hummingbird` both map to `RingEffectKind.Speed`. The distinction is `SpeedRatio`:
- Ring of Speed: `SpeedRatio = 0.10` (10%)
- Ring of Hummingbird: `SpeedRatio = 0.25` (25%)

These add to `SpeedBonusTracker.RingRatio` on equip. Combined with weapon speed bonuses (from items like `quickfang_dagger`) they drive the speed/momentum system. See `COMBAT.md`.

---

## Depth Availability (Loot Tags)

Rings appear in both the floor item pool and the `rare` loot category in `loot_tags.yaml`.

| Availability | Rings |
|---|---|
| B2+ (depth 6+) | protection, regeneration, strength, dexterity, searching, clarity |
| B3+ (depth 11+) | constitution, might, speed, free_action, luck |
| B4+ (depth 16+) | hummingbird, teleportation, resistance, invisibility, wizardry |

The `rare` category also has the `RareMultiplier` applied in loot generation:
- B1: 0.05× (rings effectively never appear)
- B2: 0.15×
- B3: 0.50×
- B4: 0.80×
- B5: 1.0×

Floor item pool entries for rings use weights of 3–4 (vs weapons at 10–30), so rings are meaningfully rare.

---

## Notes

- No cursed rings currently.
- Unequipping a ring that granted max HP bonus (Ring of Constitution) reduces max HP but does not kill the player if HP is above the new maximum.
- Ring of Teleportation procs on damage received, not on hits dealt. The proc is separate from the player's action.
