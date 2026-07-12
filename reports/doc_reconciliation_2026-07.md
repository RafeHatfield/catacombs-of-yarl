# Documentation Reconciliation — 2026-07-12

_Verified against commit **86b6f10** (main after Phase 1 merges of branches A + B)._

Phase 2 of the discovery/audit task: make every doc under `docs/` and `tasks/plans/INDEX.md`
factually correct against the code as of the current commit. Source of truth = code, config
YAML, tests. **Docs only — no code/config/test edits** (final guard below confirms this).

## Summary

- **Corrections made:** 11 substantive factual fixes (traps, resistance, item stacking,
  two-handed weapons, ring counts/reasons, rarity, tileset switching, plus index rebuilds).
- **Docs stamped `Last verified`:** 41 files.
- **Docs archived:** 17 files (2 top-level + 15 story) → `docs/archive/` with manifest.
- **Could-not-verify:** 6 items, listed explicitly at the end (not guessed).
- **Root cause of the misleading review:** confirmed. Main already contained traps, resistance,
  stacking, and the Weighing endgame; the docs said otherwise. The `plan_world_class_review`
  doc itself flagged "doc rot is actively misleading" — corroborated.

---

## Factual corrections (old claim → verified truth → evidence)

### 1. Traps — "not built / planned" → **fully implemented**
- **Old:** `systems/INDEX.md` ("Not Yet Built: Traps"; "note: no traps yet"), `systems/GROUND_HAZARDS.md` ("no traditional placed traps… planned for a future milestone"), `systems/MAP_GENERATION_AND_PROPS.md` ("Traps — not yet implemented").
- **Truth:** 9 trap types placed by the generator and resolved in play.
- **Evidence:** `config/floor_traps.yaml` (spike/web/gas/fire/alarm_plate/teleport/root/hole/acid), `src/Logic/Core/DungeonFloorBuilder.cs` (`FloorTrapRegistry`, "place floor features … traps"), `src/Logic/Combat/TrapActionResolver.cs` (called from `TurnController`; `src/Logic/ECS/TrapPayloadComponent.cs`).
- **Nuance kept:** the scenario-level `trap_rules` override field on `LevelOverride` is parsed-but-not-consumed (no reader in `src/Logic`); placement uses `FloorTrapRegistry`, not `trap_rules`.

### 2. Damage-type resistance/vulnerability — "not built" → **implemented**
- **Old:** `systems/INDEX.md` ("Not Yet Built: Resistance system"); `GROUND_HAZARDS.md` ("when the resistance system is built"); `RINGS.md` ("Resistance system not yet built").
- **Truth:** resistance halves / vulnerability doubles damage, wired to monsters, applied in combat.
- **Evidence:** `src/Logic/Combat/DamageModifiers.cs`, `src/Logic/Combat/CombatResolver.cs:119`, `config/entities.yaml` `damage_resistance` / `damage_vulnerability` (lines ~572/642/776).
- **Nuance kept:** ground-hazard tick damage (`GroundHazard.CurrentDamage`) is raw and does **not** route through `DamageModifiers`; and `ring_of_resistance` is still a no-op (see #4).

### 3. Item stacking — "not implemented" → **implemented (consumables + ammo)**
- **Old:** `systems/INDEX.md` ("Item stacking — not implemented (each item is a separate entity)"); `LOOT_AND_IDENTIFICATION.md` ("Item stacking — unimplemented").
- **Truth:** implemented for consumables and ammo; equipment is non-stackable by nature.
- **Evidence:** `src/Logic/Combat/Consumable.cs` (`StackSize`, decrements on use), `src/Logic/Content/ItemDefinition.cs` (`stack_size`, e.g. fire_arrow=10). Makes `PLAYER_PAIN_POINTS.md` ("Item stacking (5x healing potion)" under Solutions Implemented) correct and consistent.

### 4. Rings — "10 of 15 / 5 stubs" → **16 total, 10 functional, 6 stubs**
- **Old:** `systems/INDEX.md` ("10 of 15 rings", "5 Phase 2 rings"); `RINGS.md` ("Phase 1 (10) … Phase 2 (5)").
- **Truth:** 16 rings defined; `TurnController` handles 9 effect kinds → 10 functional rings; 6 are no-op stubs (resistance, clarity, invisibility, searching, wizardry, luck).
- **Evidence:** `config/entities.yaml` (16 `ring_*`), `src/Logic/Content/ItemFactory.cs` (`ParseRingEffectKind`), `src/Logic/Core/TurnController.cs` ring-effect switch (~2774–2845).
- **Also fixed:** RINGS.md "Blocking System" reasons for `ring_of_resistance` ("Resistance system not yet built" — false; the combat mechanic exists, the ring just isn't wired) and `ring_of_searching` ("Trap system not yet built" — false; traps/secret doors exist, ring not wired).

### 5. Two-handed weapons — "not implemented" → **implemented**
- **Old:** `systems/WEAPONS.md` ("Two-hand weapons are not implemented (no slot restriction)").
- **Truth:** two-handed weapons clear the off-hand slot (bow + shield disallowed).
- **Evidence:** `src/Logic/Combat/Equippable.cs` (`TwoHanded`), `config/entities.yaml` `two_handed: true` (shortbow/longbow, ~1184/1197).

### 6. Rarity tiers — "stubs in code" → **not built (no code/stub)**
- **Old:** `LOOT_AND_IDENTIFICATION.md` ("Rarity tiers … stubs in code, not yet active").
- **Truth:** no rarity enum, field, or stub exists anywhere.
- **Evidence:** absence across `src/Logic/` and `config/` (grep for `rarity|legendary|RarityTier` → none in item definitions; only flavor text "cursed ground" in signposts).

### 7. Tileset switching — plan marked `[ ]` "not started" → `[~]`, core **live**
- **Old:** `tasks/plans/INDEX.md` row `plan_tileset_switching [ ]`.
- **Truth:** data-driven tileset YAML (UF + 16bf), boot-time + `--tileset` CLI selection, depth-based tile themes.
- **Evidence:** `config/tilesets/{16bit_fantasy,ultimate_fantasy}.yaml`, `config/game_settings.yaml` (`tileset:` + `--tileset` override), `src/Logic/ECS/TileTheme.cs`, `DungeonFloorBuilder.AssignTileThemes`. (Marked `[~]` not `[x]` — see could-not-verify #4.)

### 8. `TRADITIONAL_ROGUELIKE_FEATURES.md` — stale wishlist framing
- Added a status-reconciliation banner: item stacking, resistance, and traps are now built (do not treat their "future/N-weeks" entries as current); defer to `systems/INDEX.md`. Kept the doc (it's a useful aspirational roadmap), did not archive.

### 9. `docs/README.md` — index rebuilt against the actual tree
- Removed stale "no traps" note; added the missing `llm-testing/` section and the full `balance/` list; repointed PHASES.md and superseded story drafts to `archive/`; fixed the Story section to the current `THE_UNDER_WARDEN_story.md` + style bible.

### 10. `systems/INDEX.md` — status summary regenerated from code
- Three buckets (fully-implemented / partial-with-named-gaps / not-built), each line citing evidence files. Correctly relocates traps, resistance, stacking, two-handed weapons to "implemented"; keeps blessed/cursed, hunger, shop, amulets, rarity, return-to-previous-floor in "not built" (all verified absent).

### 11. `PLAYER_PAIN_POINTS.md` — QoL "Solutions Implemented" verified
- Confirmed in logic layer: item stacking, autopickup (`TurnController`/`FeatureFactory`), no weight limit (no encumbrance code). Flagged auto-sort and quick-keys as presentation/input-layer, unverified here (see could-not-verify #1/#2).

---

## Docs stamped `Last verified: 2026-07-12 against commit 86b6f10` (41)

All 13 `docs/systems/*.md`; `docs/README.md`; `docs/PLAYER_PAIN_POINTS.md`,
`TRADITIONAL_ROGUELIKE_FEATURES.md`, `DESIGN_PRINCIPLES.md`, `DEPTH_PRESSURE_MODEL.md`,
`PLAYER_PROGRESSION_DOCTRINE.md`, `floor-and-room-design.md`, `YARL_MOBILE_LAYOUT_SPEC.md`,
`2d-vs-iso.md`, `reference_rogue_wizards.md`, `reference_tileset_research.md`,
`under_warden_style_bible.md`; all 10 stamped `docs/balance/*.md` (excl. `balance_findings.md`);
all 5 `docs/llm-testing/*.md`; `docs/archive/MANIFEST.md`; `tasks/plans/INDEX.md`.

**Verified but intentionally left intact (not stamped, per Rule 3):**
`docs/balance/balance_findings.md` — running decision log (current-state records, not history).
`docs/story/THE_UNDER_WARDEN_story.md` — current narrative fiction (no code claims to stamp against).

Design/reference/balance/llm-testing docs were checked for **system-status drift** (targeted greps
for traps/resistance/stacking/"not built") and found clean before stamping; their internal design
math / methodology was not independently re-derived.

---

## Docs archived → `docs/archive/` (17, approved; content moved, nothing deleted)

See `docs/archive/MANIFEST.md` for the per-file reason table. Set:
`PHASES.md`, `memo_handoff_session_3.md`, and 15 story files
(`the_under_warden_v2/v3.md`, `the_under_warden_design_notes.md`,
`the_tax_collector_proposal.md` + `_design_notes.md`, and the 11-file
`other-stories-not-implemented/` dir).

**Deletion is deferred to you** — everything is preserved under `archive/`. Inbound provenance
citations from out-of-scope plan files (`plan_cross_run_persistence.md`, `plan_possession_system.md`,
`plan_under_warden_memos.md`) to the archived Under-Warden drafts still resolve (files moved, not
deleted) but now live under `docs/archive/story/`. Noted in the manifest.

---

## Could not verify either way (listed, not guessed)

1. **Auto-sort inventory** (`PLAYER_PAIN_POINTS.md` "Solutions Implemented") — no logic-layer code (`auto.?sort|SortInventory` → 0 hits). Presentation-layer or unbuilt; not confirmable from the logic layer here.
2. **Quick keys for common actions** (same list) — input/presentation-layer concern; not verifiable in the logic layer.
3. **`plan_map_renderer` `[~]` and `PLAN_topdown_switch` `[~]`** (tasks/plans/INDEX.md) — renderer code exists (`src/Presentation/Map/DungeonRenderer.cs`), but exact iso-vs-top-down phase completion is presentation-layer and was not driven/rendered to confirm. Left `[~]` (unchanged).
4. **`plan_tileset_switching` full completion** — core switching verified live (correction #7), but not every sub-deliverable (e.g. a dedicated "CLI mapping tool") was individually confirmed; hence `[~]`, not `[x]`.
5. **`plan_end_game` / `plan_end_game_impl` `[~]` remaining copy** — Weighing framework code is present (`src/Logic/Endgame/*`), but the specific "remaining" items (2 combat-death ending texts, ally-fallback lines, Refuse/Swap UI copy, balance pass) were not individually verified. Left `[~]` (unchanged).
6. **Fast test suite (workflow Rule 6) — not run.** No local .NET toolchain in this environment, and GitHub Actions cannot dispatch on this private repo (minutes/spending-limit; see Phase 1 findings). Substitute guard used instead: `git diff --name-only 86b6f10..HEAD` touches **only** `docs/`, `tasks/plans/INDEX.md`, and `reports/` — zero `src/`/`config/`/`tests/` changes. Confirmed clean.

---

## Verification

```
$ git diff --name-only 86b6f10..HEAD | grep -vE '^(docs/|tasks/plans/INDEX\.md$|reports/)'
  (none — docs-only, clean)
```
Rule 5 final grep over live docs: no surviving "not built / planned" claim contradicts code
(remaining hits are accurate — a validation-harness note, a precise necro-mechanic divergence,
and the Analyst tool's own v1 evaluator stubs).
