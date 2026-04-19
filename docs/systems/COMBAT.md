# Combat System

**Source:** `src/Logic/Combat/CombatResolver.cs`, `src/Logic/ECS/`, `src/Logic/Combat/StatusEffects/`  
**Implementation status:** Fully implemented. Speed/momentum system live. Crits implemented.

---

## Combat Resolution (d20 System)

Each attack rolls d20 + attacker accuracy vs target defense + evasion.

```
AttackRoll = d20 + Accuracy + PowerBonus + StatusBonuses
DefenseTotal = TargetBaseDefense + EquippedArmorAC + RingProtectionBonus + StatusBonuses
```

- If AttackRoll > DefenseTotal → hit
- If AttackRoll ≤ DefenseTotal → miss

**Accuracy** sources: base stat (varies by monster), weapon `to_hit_bonus`, `HeroismEffect`, `FocusedEffect`, depth boon bonuses.  
**Defense** sources: equipped armour AC values, `ring_of_protection` (+2 BaseDefense), `ProtectionEffect` / `ShieldEffect` / `BarkskinEffect` bonuses.  
**Evasion** sources: entity `evasion` stat (from YAML), Dexterity modifier.

---

## Damage Calculation

On a hit:
```
BaseDamage = random(weapon.damage_min, weapon.damage_max) + PowerBonus + StatusBonuses
FinalDamage = max(1, BaseDamage - TargetDamageReduction)
```

**Power bonus** comes from: `strength` stat modifier, `ring_of_might` (+4 flat), `HeroismEffect` (+3), `WeaknessEffect` (negative).

**Damage reduction** is separate from AC — currently only monster special resistances (fire beetle vs fire, skeleton vs bludgeoning).

---

## Critical Hits

Default crit threshold: 20 (natural 20 on d20 = crit). `keen_dagger` sets `crit_threshold: 19`.

On a crit: damage is rolled twice and the higher value is taken (no automatic max damage). Crits always hit regardless of defense roll.

---

## Damage Types

Three types: **Piercing**, **Slashing**, **Bludgeoning**.

Defined per weapon via `damage_type`. Monster resistances (`damage_resistance`) and vulnerabilities (`damage_vulnerability`) apply multiplicatively:
- Resistant: ×0.5 damage  
- Vulnerable: ×1.5 damage  
- Normal: ×1.0

Current active resistances/vulnerabilities: see `MONSTERS.md`.

---

## Speed and Momentum System

The speed system determines how frequently an entity gets an extra action.

### Core Concept

Each entity has a `SpeedBonusRatio` (0.0 = normal, 0.5 = half-speed bonus, etc.). After every attack, an `AttackCounter` increments. When `AttackCounter >= threshold`, a bonus action is granted and the counter resets.

```
threshold = ceil(1.0 / SpeedBonusRatio)
```

Example: Ring of Hummingbird (+25% speed) → threshold = ceil(1/0.25) = 4. Every 4th attack, the entity gets a free extra attack that turn.

### Speed Sources (Stacking)

1. **Weapon speed**: `quickfang_dagger` contributes `EquipmentRatio = 0.18`
2. **Ring speed**: `ring_of_speed` contributes `RingRatio = 0.10`; `ring_of_hummingbird` contributes `RingRatio = 0.25`
3. **Status effects**: `SpeedEffect` (Haste/Potion of Speed) adds `0.50` ratio; `SluggishEffect` subtracts

Combined: `TotalRatio = EquipmentRatio + RingRatio + StatusEffectRatio`

### Momentum Reset

`AttackCounter` resets on target switch by default (the player cannot carry momentum from one target to another). Preserving momentum across target switches is a potential boon — not yet implemented.

### Display

The gear screen shows:  
`SPD +X% (sources) [counter/threshold]`

E.g., `SPD +25% (ring) [2/4]` means: 25% speed from a ring, 2 attacks into a 4-attack cycle.

---

## Monster Speed

Monsters use the same system. Fast monsters:

| Monster | SpeedBonus | Effective Threshold |
|---|---|---|
| `orc_skirmisher` | 20% | 5 |
| `orc_veteran` | 15% | 7 |
| `orc_chieftain` | 25% | 4 |
| `giant_spider` | 35% | 3 |
| `zombie` | 50% | 2 |
| `troll_ancient` | 15% | 7 |
| `wraith` | 200% | 1 (acts every turn with extra) |
| `cultist_blademaster` | 25% | 4 |

Zombie's 50% speed bonus means they get an extra attack every 2 turns — they hit frequently despite low accuracy.

---

## Combat Sequence (Per Turn)

1. Player takes action (move, attack, item use, etc.)
2. If attacking: combat resolves (d20, damage, status effects, momentum)
3. Speed check: if counter ≥ threshold, player gets another action this turn
4. All monsters with remaining turns act (AI decision, combat if applicable)
5. Speed check per monster
6. Status effect ticks (DOT damage, duration decrements)
7. Ground hazard ticks
8. Turn events dispatched to presentation layer

---

## Life Drain (Wraith)

`life_drain_pct: 0.50` — wraith hits drain 50% of damage dealt from the player's **max HP** (not current HP). This permanently reduces `MaxHp` until the player rests or finds a source of max HP restoration. Currently no restoration source is implemented — wraith drain is permanent until death or game reset.

---

## Slime Corrosion

Slimes have a `corrosion_chance` per hit. On proc, a random equipped item degrades (loses +1 to its primary stat). Currently targets `armor_class_bonus` on armour and `to_hit_bonus` on weapons. Equipment cannot degrade below 0.
