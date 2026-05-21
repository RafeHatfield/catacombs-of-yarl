# Deferred Plan: Slime Advanced Abilities

**Status:** PARTIALLY COMPLETE
- ✅ greater_slime — done (overnight build)
- ✅ Engulf (EngulfedEffect) — implemented 2026-05-20
- ✅ natural_damage_type: "acid" — implemented 2026-05-20; slime attacks now participate in acid damage type system
- 🔄 hostile_all faction AI (inter-faction targeting) — deferred, acknowledged large scope
- ⬜ Natural damage type for armor corrosion — deferred
**Blocked by:** `slime_monsters.md` must be complete first
**PoC reference:** `~/development/rlike/config/entities.yaml` lines 483–580, `~/development/rlike/components/fighter.py` lines 1636–1755, `~/development/rlike/services/faction_engine.py`

---

## What is deferred here

These are all part of Phase 19 in the PoC and are explicitly out of scope for the initial slime implementation. They are documented here so they don't get lost.

---

## 1. `greater_slime` (elite tier)

**PoC stats:**
- hp: 80, dmg: 3–7, str: 14, dex: 6, con: 16, def: 2, xp: 150
- etp_base: 75
- corrosion_chance: 0.15
- split_trigger_hp_pct: 0.35 → splits into 2 `large_slime` (fixed, weight [100])
- color: [0, 150, 0] (dark forest green)
- depth: appropriate for depth 7+ (PoC: depth_weights [[10,7],[20,10],[35,13]])

**What's needed:** The split mechanic infrastructure from `slime_monsters.md` already handles this. Adding `greater_slime` is purely YAML + confirming depth weights. No new code required once the base slime plan is complete.

---

## 2. `engulf` mechanic

**PoC description:** Minor slimes have `special_abilities: ["corrosion", "engulf"]`. Engulf applies a movement penalty (slow) to the player while a slime is adjacent. Persists until the player moves away or kills the slime.

**What's needed:**
- A `SlowEffect` or `MovementPenalty` status component on the player
- TurnController check: at start of player's move, if any adjacent alive slime has engulf, reduce movement speed or cost extra AP
- Removal: when no engulf-capable slimes are adjacent
- Toast message: "The slime engulfs you! Movement hampered."

**Design note:** The PoC engulf is purely a movement cost increase, not a root/immobilize. Player can still move — it just costs more. For a simple turn-based system, this could mean "moving while engulfed costs 2 turns worth of monster actions." Define clearly before implementing.

---

## 3. `hostile_all` faction behavior

**PoC description:** `faction: "hostile_all"` means the slime attacks ALL entities, including other monsters (orcs, zombies). This creates interesting tactical situations where a slime wandering into an orc group causes chaos.

**What's needed:**
- Faction awareness in the AI `MonsterAiSystem` / `AiComponent`
- Current AI: all monsters target only the player
- New: monsters check if target is in same faction before attacking — if different faction AND hostile, attack that monster instead of (or in addition to) moving toward player
- `GameState.AliveMonsters` targeting logic needs to be faction-aware
- PoC uses `faction_engine.py` for these checks

**Design note:** This is a significant AI system change. The payoff is meaningful — slimes wandering into orc encounters is a memorable gameplay moment. But it requires rethinking the entire monster targeting model. Defer until faction engine plan is scoped separately.

**Faction field** (`faction: "beast"`) is already in YAML and `MonsterDefinition`. The data is there; only the AI behavior is deferred.

---

## 4. `natural_damage_type: "acid"` and damage type system

**PoC description:** Slimes deal acid damage naturally. This interacts with:
- Troll regeneration (acid suppresses it)
- Damage resistances/vulnerabilities (some monsters resist acid)
- Future: damage type display in combat log

**What's needed:**
- `natural_damage_type` field already planned for `MonsterDefinition` — parse it
- `CombatResolver` uses it when monster has no weapon equipped
- Resistance/vulnerability system checks damage type against `DamageResistance` field

**Design note:** `DamageResistance` and `DamageVulnerability` already exist on `MonsterDefinition` and the `DamageModifiers` component. The damage type field and the combat resolver hook are what's missing. Relatively contained — could be done alongside troll implementation (troll regen suppressed by acid is the canonical use case).

---

## 5. Corrosion armor degradation

**PoC description:** `_corrode_armor` in `fighter.py` can also degrade equipped off-hand armor. Slimes in the PoC only use `_corrode_weapon`, but the armor path exists for potential future use (acid elementals, etc.).

**What's needed:**
- `Equippable` ArmorClassBonus degradation (similar to DamageMax degradation)
- `BaseArmorClassBonus` (immutable floor reference)
- Floor: some % of base AC bonus

**Design note:** Low priority — slimes never actually trigger this path in the PoC. Leave it until an enemy explicitly needs armor corrosion.

---

## 6. Full faction engine

**PoC reference:** `~/development/rlike/services/faction_engine.py`

The PoC faction engine handles:
- Inter-faction hostility tables (which factions attack which)
- Faction-based AI targeting priority
- Rally effects (orc_chieftain rallies orc faction members)
- Confusion/charm interactions (charmed monsters fight for player's faction)

**What's needed:** A `FactionEngine` service in C# logic layer. This is a significant standalone system that touches AI, combat resolution, and status effects. Scope it separately when multi-faction encounters become a design priority.

---

## Suggested implementation order (when ready)

1. `greater_slime` — trivial once base slimes are in (YAML only)
2. `natural_damage_type` + damage type system — needed for troll regen
3. `hostile_all` faction AI — highest tactical payoff, biggest scope
4. `engulf` — contained movement system, good for depth variety
5. Corrosion armor — lowest priority, no current use case
6. Full faction engine — major system, needs dedicated planning session
