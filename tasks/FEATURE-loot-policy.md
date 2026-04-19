# Feature: Loot Policy & 25-Floor Dungeon Structure

## Status: planning

## Current State
- Task file created. Nothing implemented yet.
- Next step: TASK-001 (level_templates.yaml 25-floor stubs).

---

## Overview

Two tightly coupled concerns: the dungeon is canonically 25 floors deep, and the loot system must
be band-aware across those 25 floors. Neither works well without the other.

**Current state of the C# codebase:**
- `FloorItemPoolEntry` has `item`, `weight`, `min_depth` — flat pool, no category, no max_depth
- `EntityPlacer.FillRooms` rolls a flat ~40% chance per room of one item from the depth-filtered pool
- `level_templates.yaml` has entries for depths 1–3 only; depths 4+ fall through to defaults
- No pity system, no band density multipliers, no ring gating
- Harness defaults to 6 floors

**Target state:**
- 25-floor dungeon acknowledged in config with B1–B5 band stubs
- Every item in the pool carries loot category tags
- `LootController` drives per-room item generation using band EVs and category weights
- `PityTracker` (room-based) guarantees no category goes dry across a run
- Item density and ring rate scale per band
- Harness emits loot category counts + pity trigger telemetry

---

## PoC Alignment

The PoC (`~/development/rlike`) is the reference for all balance numbers in this feature.
**Every deviation from PoC design is explicitly flagged below and requires approval before implementation.**

### PoC-exact (adopt unchanged)

**25 floors, 5 bands of 5 floors each:**
```
B1: depths  1-5   (early game, scarcity, learning)
B2: depths  6-10  (early-mid, slight easing)
B3: depths 11-15  (mid game, full density)
B4: depths 16-20  (mid-late, tactical depth)
B5: depths 21-25  (endgame, gear optimization)
```

**Item density multipliers per band (from `balance/loot_tags.py`):**
```
B1: 0.35  (~35% of baseline item density — intentional scarcity)
B2: 0.45
B3: 1.00  (baseline)
B4: 1.00
B5: 1.00
```

**Ring (rare item) gating per band:**
```
B1: 0.05  (almost no rings — prevent early power spike)
B2: 0.15
B3: 0.50
B4: 0.80
B5: 1.00
```

**Healing spawn multipliers per band:**
```
B1: 0.25  (low healing — raises early-game tension; pity is the safety net)
B2: 0.35
B3: 1.00  (baseline)
B4: 1.10  (slightly more — harder content)
B5: 1.10
```

**Room-based pity thresholds (from `balance/pity.py`):**

| Category       | B1 trigger | B2 trigger | B3+ trigger |
|----------------|------------|------------|-------------|
| healing        | 6 rooms    | 5 rooms    | 4 rooms     |
| panic          | 7 rooms    | 6 rooms    | 5 rooms     |
| upgrade_weapon | 8 rooms    | 7 rooms    | 6 rooms     |
| upgrade_armor  | 8 rooms    | 7 rooms    | 6 rooms     |

Soft pity: weight multiplied by 2.0× when window is empty.
Hard pity: inject guaranteed item when rooms-since-last reaches hard threshold (soft threshold + 2).

**Real item categories (from `loot_tags.py`):**
```
healing         — HP restoration items
panic           — emergency escape (teleport, haste, blink, invisibility)
offensive       — direct damage (fireball, lightning, earthquake, offensive wands)
defensive       — protection/mitigation (shield scroll, protection potion)
utility         — tactical/situational (confusion, slow, glue, rage, detect, identify)
upgrade_weapon  — weapon improvements (weapons, enchant_weapon scroll)
upgrade_armor   — armor improvements (armor pieces, enchant_armor scroll)
rare            — rings (all ring types, depth-gated)
key             — progression keys (bronze/silver/gold — no locked doors yet, category reserved)
```

### Explicit Deviations (require approval before implementation)

**DEVIATION-001: Rarity tier system deferred**
PoC has Common/Uncommon/Rare/Legendary tiers with color tints and stat bonuses on equipment.
This predated the balance work and will be implemented later against the live balancing system.
*Status: pre-approved by Rafe (2026-04-18).*

**DEVIATION-002: `identification` as a separate YAML EV category**
PoC's `loot_policy.yaml` lists `identification_ev` as a band target, but `loot_tags.py` never
defines a category called "identification." In practice, `scroll_of_identify` falls into `utility`.
The PoC EV target appears to be a legacy concept that wasn't wired to actual item selection.
*Proposed: treat identify scrolls as `utility`. No separate `identification_ev`. Awaiting approval.*

**DEVIATION-003: `defensive` category fate**
PoC has a `defensive` category covering protection potion, scroll_of_shield, defensive rings.
In our current item set: protection potion → `healing`; scroll_of_shield doesn't exist yet;
defensive rings → `rare`. Three options:
  A. Keep `defensive` as a category, move protection potion into it (matches PoC exactly)
  B. Merge `defensive` into `healing` for protections and `rare` for rings (simpler, fewer categories)
  C. Keep `defensive` empty now, populate when scroll_of_shield and more arrive
*Awaiting approval.*

**DEVIATION-004: `key` category placeholder**
Keys and locked doors don't exist yet. The `key` category will be in the registry but the
item pool for it will be empty. No key items will spawn. When locked doors land, this category
gets populated with bronze_key, silver_key, gold_key.
*Status: no-op deviation, informational only.*

---

## Architecture

### New files

| File | Purpose |
|------|---------|
| `config/loot_tags.yaml` | Per-item category tags, weights, band_min, band_max |
| `config/loot_policy.yaml` | Band EVs, density multipliers, ring gating, pity config |
| `src/Logic/Balance/LootController.cs` | Main generation — band lookup, EV rolls, category selection |
| `src/Logic/Balance/PityTracker.cs` | Room-based drought counters per category, per run |
| `src/Logic/Balance/LootBand.cs` | Band enum + depth→band lookup (static, shared) |
| `src/Logic/Content/LootTag.cs` | Deserialized item tag entry |
| `src/Logic/Content/LootTagRegistry.cs` | Loads loot_tags.yaml, provides category→items lookups |
| `src/Logic/Content/LootPolicyConfig.cs` | Deserialized loot_policy.yaml |

### Modified files

| File | Change |
|------|--------|
| `config/entities.yaml` | Add `max_depth` to floor_item_pool entries; add `categories` per item OR keep flat pool and let loot_tags.yaml own category assignment |
| `config/level_templates.yaml` | Add B1–B5 band stubs (depths 6, 11, 16, 21, 25) |
| `src/Logic/Content/FloorItemPoolEntry.cs` | Add `MaxDepth` field (for items that age out) |
| `src/Logic/Core/EntityPlacer.cs` | Replace flat pool selection with LootController-driven generation |
| `src/Logic/Core/DungeonFloorBuilder.cs` | Wire LootController + PityTracker, carry PityTracker across floors |
| `src/Logic/Core/GameState.cs` | Add `PityTracker` property |
| `tools/Harness/Program.cs` | Emit loot category counts + pity trigger telemetry |

### Key design decision: two-file loot config

`loot_tags.yaml` owns item-level data (what category an item belongs to, its weight within that
category, which bands it can appear in). `loot_policy.yaml` owns band-level data (how many of
each category to target per room, pity thresholds).

This matches the PoC's two-layer structure (`loot_tags.py` + `loot_policy.yaml`) and keeps
item balance separate from band-level balance — two different tuning levers.

The existing `floor_item_pool` in `entities.yaml` remains as a compatibility fallback for
`ChestLootGenerator` and any path that doesn't yet use LootController. Once LootController
is wired everywhere, `floor_item_pool` is retired.

---

## Tasks

### Phase 0 — 25-floor config (no new systems)

- [ ] **TASK-001**: Extend `level_templates.yaml` with B1–B5 band stubs
  - Add band marker entries for depths 6, 11, 16, 21, 25
  - Each stub defines: encounter_budget ETP range appropriate for that band
  - No guaranteed_spawns yet (that's later content work)
  - Stubs signal intent; existing fallthrough still handles depths without entries
  - Files: `config/level_templates.yaml`

- [ ] **TASK-002**: Update harness default depth to 10, document 25-floor goal
  - `tools/Harness/Program.cs`: change `int floors = 6` to `int floors = 10`
  - Add comment explaining 25-floor canonical depth and B1–B5 band structure
  - Files: `tools/Harness/Program.cs`

### Phase 1 — Item category tag system

- [ ] **TASK-003**: Create `LootBand.cs` — band enum and depth lookup
  - `enum LootBand { B1, B2, B3, B4, B5 }`
  - `static LootBand FromDepth(int depth)` — maps depth to band (1-5→B1, 6-10→B2, etc.)
  - Band multiplier tables (density, healing, rare) as static readonly dictionaries
  - Zero Godot dependencies
  - Files: NEW `src/Logic/Balance/LootBand.cs`

- [ ] **TASK-004**: Create `config/loot_tags.yaml` and `LootTag.cs` + `LootTagRegistry.cs`
  - `loot_tags.yaml`: one entry per item in our current item set
  - Schema per entry: `item_id`, `categories: [list]`, `weight: float`, `band_min: int`, `band_max: int`
  - Port item weights from PoC `loot_tags.py` for every item we have; items missing from PoC get reasonable defaults
  - `LootTag.cs`: sealed YAML-deserialized record
  - `LootTagRegistry.cs`: loads file, exposes `GetItemsForCategory(string category, int band)` → filtered weighted list
  - Must cover all items currently in `floor_item_pool` section of entities.yaml
  - Zero Godot dependencies
  - Files: NEW `config/loot_tags.yaml`, NEW `src/Logic/Content/LootTag.cs`, NEW `src/Logic/Content/LootTagRegistry.cs`

- [ ] **TASK-005**: Add `MaxDepth` to `FloorItemPoolEntry`
  - Some items age out (e.g., club is irrelevant past depth 5)
  - YAML alias: `max_depth` (default: 99 — no cap unless specified)
  - Update `config/entities.yaml` floor_item_pool entries: add max_depth where items age out
  - Files: `src/Logic/Content/FloorItemPoolEntry.cs`, `config/entities.yaml`

### Phase 2 — Loot policy config and controller

- [ ] **TASK-006**: Create `config/loot_policy.yaml` and `LootPolicyConfig.cs`
  - Band EVs per category (how many items of each category to target per floor)
  - Item density multipliers per band (B1=0.35, B2=0.45, B3-B5=1.0)
  - Healing multipliers per band
  - Rare (ring) gating per band
  - Pity config: soft threshold per category per band, hard threshold, soft bias multiplier (2.0×)
  - `LootPolicyConfig.cs`: YAML deserializer, loaded once at startup
  - Zero Godot dependencies
  - Files: NEW `config/loot_policy.yaml`, NEW `src/Logic/Content/LootPolicyConfig.cs`

- [ ] **TASK-007**: Create `LootController.cs`
  - Static entry point: `GenerateRoomLoot(int depth, SeededRandom rng, LootTagRegistry tags, LootPolicyConfig policy, PityTracker pity)` → `List<string>` item IDs
  - Internal flow:
    1. Look up current band from depth
    2. Apply density multiplier — roll whether this room generates any item
    3. For rooms that get an item: select category using band EV weights (adjusted by pity soft bias)
    4. Apply healing multiplier and ring gating within category selection
    5. Select specific item from category pool (weighted, filtered by band_min/band_max)
    6. Notify PityTracker of generated item
  - Separate method: `GenerateChestLoot(int depth, SeededRandom rng, ...)` — ignores density roll, generates 1-3 items from appropriate categories for the depth
  - Zero Godot dependencies
  - Files: NEW `src/Logic/Balance/LootController.cs`

### Phase 3 — Pity system

- [ ] **TASK-008**: Create `PityTracker.cs`
  - Tracks per-category room counters (rooms since last appearance) across a run
  - Persists across floor transitions (carried on GameState like BoonTracker)
  - `RecordRoomGenerated(string category)` — called when LootController places a category item
  - `AdvanceRoom()` — called for each room processed (increments all counters)
  - `GetSoftBiasMultiplier(string category, LootBand band)` → float — 2.0× when soft threshold exceeded, 1.0× otherwise
  - `IsHardInjectDue(string category, LootBand band)` → bool
  - `ConsumeHardInject(string category)` — marks as used
  - Pity only tracks the 4 PoC categories: `healing`, `panic`, `upgrade_weapon`, `upgrade_armor`
  - Zero Godot dependencies
  - Files: NEW `src/Logic/Balance/PityTracker.cs`

- [ ] **TASK-009**: Add `PityTracker` to `GameState` and `DungeonFloorBuilder`
  - `GameState.PityTracker` property (nullable — null in scenario/test mode)
  - `DungeonFloorBuilder.Build()`: accept `PityTracker?` parameter (like BoonTracker)
  - New run: create fresh PityTracker
  - Floor transition: carry existing tracker forward (it's per-run, not per-floor)
  - `Main.cs OnFloorTransitionRequested`: pass `_state?.PityTracker` (same pattern as BoonTracker)
  - Files: `src/Logic/Core/GameState.cs`, `src/Logic/Core/DungeonFloorBuilder.cs`, `src/Presentation/Main.cs`

### Phase 4 — Wire into EntityPlacer

- [ ] **TASK-010**: Replace flat pool selection in `EntityPlacer.FillRooms` with `LootController`
  - Currently: `~40% per room, SelectWeighted(depthFilteredPool)`
  - New: `LootController.GenerateRoomLoot(depth, rng, tagRegistry, policy, pityTracker)`
  - Dead-end rooms: still guarantee ≥1 item (existing bias preserved), use LootController for selection
  - Vault rooms: use LootController with 1-2 items, no density roll (already guaranteed)
  - Altar rewards: LootController with `upgrade_weapon` or `upgrade_armor` category bias
  - `LootController` and `LootTagRegistry` passed into `FillRooms` (already structured for optional params)
  - Fallback: if LootController not wired (null), fall through to existing flat pool (backward compat for tests)
  - Files: `src/Logic/Core/EntityPlacer.cs`
  - **Also update `ChestLootGenerator.cs`** to use LootController for chest item generation

- [ ] **TASK-011**: Wire `LootTagRegistry` + `LootPolicyConfig` into `DungeonFloorBuilder` + `Main.cs`
  - Load `loot_tags.yaml` and `loot_policy.yaml` in `Main.cs InitFactories()` (same pattern as signpost registry)
  - Pass both into `DungeonFloorBuilder` constructor (new optional params)
  - Thread through to `EntityPlacer.FillRooms` call
  - Files: `src/Logic/Core/DungeonFloorBuilder.cs`, `src/Presentation/Main.cs`

### Phase 5 — Harness metrics + verification

- [ ] **TASK-012**: Emit loot category telemetry from harness
  - `DungeonRunHarness` or `DungeonSoakResult`: count items per category per floor
  - Track pity trigger events (soft + hard, per category)
  - Output in existing JSONL or summary format
  - Files: `src/Logic/Balance/DungeonRunHarness.cs` (or `tools/Harness/Program.cs`)

- [ ] **TASK-013**: NUnit tests for LootController + PityTracker
  - `LootController_B1_HealingDensity`: run 100 rooms at depth 1, verify healing rate ≈ 25% of baseline (within ±10%)
  - `LootController_B1_RingRate`: run 1000 rooms at depth 1, verify ring rate ≈ 5% of baseline
  - `PityTracker_SoftBias`: advance 6 rooms without healing, verify soft bias active
  - `PityTracker_HardInject`: advance past hard threshold, verify `IsHardInjectDue` true; consume, verify resets
  - `PityTracker_PersistedAcrossFloors`: carry tracker across simulated floor transition, counters preserved
  - `LootController_ChestLoot_DepthAppropriate`: chest at depth 1 vs depth 10 produces depth-appropriate items
  - Files: NEW `tests/Logic/Loot/LootControllerTests.cs`, NEW `tests/Logic/Loot/PityTrackerTests.cs`

- [ ] **TASK-014**: Harness soak run
  - Run `dotnet run --project tools/Harness -- --dungeon --floors 10 --runs 200 --seed 1337`
  - Verify: healing items appear on average every 4-6 rooms (B1 band, pity active)
  - Verify: no run has >8 consecutive rooms without healing in B1 (hard pity ceiling)
  - Verify: rings appear rarely in B1 (< 5% of loot slots)
  - Verify: tests pass 1274+ (no regressions)
  - Manual Godot playtest: play 3 floors, confirm item variety feels designed not random
  - This task stays open until verification complete

---

## Open Questions / Risks

- **DEVIATION-002 + DEVIATION-003 approval** — these must be resolved before TASK-004 (loot_tags.yaml) can be written with confidence. Blocking.
- **`floor_item_pool` retirement timing** — the flat pool lives in entities.yaml until LootController is fully wired. TASK-010 should preserve the fallback path so nothing breaks during transition.
- **AotObjectFactory** — iOS NativeAOT requires manual type registration for all YAML-deserialized types. When `LootTag.cs` and `LootPolicyConfig.cs` are added, their types must be registered in `AotObjectFactory.cs`. Flag in TASK-004 and TASK-006.
- **`offensive` and `utility` categories are not pity-tracked** — PoC only pity-tracks 4 categories. Offensive scrolls can go dry. This is intentional PoC design (offensive items are tactically optional, not survival-critical). Worth noting.
