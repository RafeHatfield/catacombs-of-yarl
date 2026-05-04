# Plan: Cross-Run Persistence System

**Status:** [~] Phases 1-4 complete — skeleton, source-gen JSON context, migration framework, RunCounter + PastSashas wired end-to-end. Phase 5 next.
**Spec version:** 1.1 (2026-05-02).

## Current State (2026-05-03)

**Just completed:** Phase 4 — PastSashas + FreedPastSelves. Gear snapshot on player death (OQ-2: equipped slots only). PlayerDeathKillerSpecies/PlayerDeathCause on GameState, set in TurnController at kill site. DungeonFloorBuilder.Build() accepts PersistentRunState and threads it into GameState. PastSashasData.GetEligibleRecords() for possession floor-builder. 14 new tests (1465 total).

**Next step:** Phase 5 — Faction reputation + Unshriven geas (three-state enum, action counter, floor builder reads geas flag).

**Open issues:** iOS NativeAOT smoke test is a manual step requiring iOS export build on a real device. All logic-layer round-trips passing on macOS/arm64. FreedPastSelves write point (OnPossessionDispelled Warden path) will be wired in possession system build.

### Phase checklist

- [x] Phase 0: Spec gate (all OQs resolved, spec v1.1 signed off 2026-04-22)
- [x] Phase 1: Skeleton + JSON context (all 15 namespaces, PersistentRunState, atomic load/save, 12 tests)
- [x] Phase 2: Migration framework (pre-deserialization JSON pass, forward chain, future-namespace fallback, 7 tests)
- [x] Phase 3: Run counter wired end-to-end in Main.cs (StartDungeon depth-1 increment, floor-descent flush, game-over flush, app-background flush via _Notification)
- [x] Phase 4: Past-Sashas + Freed-Past-Selves (gear snapshot on death, killer tracking, DungeonFloorBuilder passthrough, GetEligibleRecords, 14 tests)
- [ ] Phase 5: Faction reputation + Unshriven geas
- [ ] Phase 6: Borrek/Vesh/Hael arcs + catalogs + Hollowmark meta
- [ ] Phase 7: Daily-seed sibling file

- v1.1 (2026-05-02): Tier discipline tightened — run-scoped fields lifted out of cross-run namespaces (§6.2, §6.3). Flush model changed from end-of-turn to narrative-event-boundary (§5). OQ-2 locked as A; OQ-5 closed as B-modified. Hael branch-unlock derived, not stored (§6.6). Hollowmark meta-unlock pool tracked by stable IDs, not index (§6.11). Faction schema explicit about v1 single-faction scope with extension story (§6.3). New consumer: Under-Warden memo escalation state (§6.15). New OQ: heirlooms across runs.
- v1.0 (2026-04-26): Initial spec.
**Drives:** every cross-run consumer in `the_under_warden_v3.md` — past-Sashas (§E-prime), Borrek/Vesh/Hael multi-run arcs (§M-prime), faction reputation (§M-prime), Marya-fragment catalog (§J-K), Things Hael Mentioned (§E), Freed Past-Selves (added in `plan_possession_system.md` §8.5 v1.1), Unshriven geas push-marker (§D-prime), Hollowmark binding span as a future hook (§C-prime), daily-seed challenge mode (§K), achievements/badges (§K).
**Sequencing:** v3 §N principle — **build first.** Every other system in the v3 build downstream of this one. Persistence schema must be in place before cross-run consumers start writing real records.

### v1.0 status

Open. All design decisions in §13 unresolved. Spec is the framing for the design discussion, not the conclusion.

---

## Goals

1. Define a **single canonical contract** for cross-run state — one record format, one load/save lifecycle, one migration pathway. No consumer invents its own persistence layer.
2. Make scope tiers **explicit**: what's run-scoped (resets every run), what's cross-run (persists between runs), what's cross-version (must survive game updates).
3. Make migration **load-bearing**: shipping a v1.1 patch that adds a field cannot break v1.0 saves. Specify the schema_version mechanism on day 1, not when we hit a migration emergency.
4. Make daily-seed records a **sibling concern** — separate file, similar shape, distinct lifecycle. Don't conflate per-character cross-run state with per-date global challenge state.
5. Document **NativeAOT constraints** — System.Text.Json reflection-based serialization is unsafe; source-generated `JsonSerializerContext` required. Catch this on paper before Phase 1.

## Non-goals

- Implementation. No code in this pass.
- Settings persistence (Verbose/Tactical/Silent default, hardmode toggle, difficulty). Those live in a separate settings file. Spec'd elsewhere; this doc only flags the boundary.
- Multi-character / multi-save-slot support. v3 does not ask for it. Schema is designed to extend cleanly to per-character namespacing in v2, but v1 has one implicit character.
- Cloud sync / iCloud. Local-only for v1. Migration story has to be solid first.
- Save scumming protections / anti-cheat. Out of scope for a single-player roguelike.

---

## §1. The contract — `PersistentRunState`

**One canonical record. Namespaced by consumer. JSON on disk. Source-generated serialization.**

### Top-level shape

```jsonc
{
  "schema_version": 1,                 // top-level integer; bump on breaking shape changes
  "saved_at": "2026-04-26T14:32:00Z",  // last-write timestamp, debug aid
  "namespaces": {
    "run_counter":      { "schema_version": 1, "data": { ... } },
    "past_sashas":      { "schema_version": 1, "data": { ... } },
    "factions":         { "schema_version": 1, "data": { ... } },
    "borrek":           { "schema_version": 1, "data": { ... } },
    "vesh":             { "schema_version": 1, "data": { ... } },
    "hael":             { "schema_version": 1, "data": { ... } },
    "marya_fragments":  { "schema_version": 1, "data": { ... } },
    "hael_hints":       { "schema_version": 1, "data": { ... } },
    "freed_past_selves":{ "schema_version": 1, "data": { ... } },
    "unshriven_geas":   { "schema_version": 1, "data": { ... } },
    "hollowmark_meta":  { "schema_version": 1, "data": { ... } },
    "achievements":     { "schema_version": 1, "data": { ... } },
    "encounters":       { "schema_version": 1, "data": { ... } },
    "hollowmark_span":  { "schema_version": 1, "data": { ... } },  // deferred, reserved
    "under_warden":     { "schema_version": 1, "data": { ... } }
  }
}
```

### Why namespaced, not flat

A flat record forces top-level schema bumps for every field add. With per-namespace `schema_version`, we can ship "v1.1 adds a Vesh-specific field" by bumping only `namespaces.vesh.schema_version` from 1 to 2 and writing one migration function. Other namespaces stay at v1.

The top-level `schema_version` is reserved for **structural** changes — splitting a namespace, renaming the file, changing the on-disk encoding. Field-level evolution lives in per-namespace versions.

### Why JSON, not YAML or binary

- YAML is the project's content format (config/*.yaml) — readable, hand-editable, but YamlDotNet is incompatible with iOS NativeAOT InvariantGlobalization (per `feedback_ios_nativeaot.md`). Save data needs to load on iOS.
- Binary (BSON, MessagePack, custom) is fastest but opaque. For a single-player game, debuggability of save state is worth more than load speed.
- JSON via System.Text.Json source-generated `JsonSerializerContext` is NativeAOT-safe, debuggable, and reasonably fast. **Mandatory** approach — see §8.

### Access pattern

Consumers do **not** read or write JSON directly. They read and write through typed accessors on `PersistentState`:

```csharp
// Example consumer access
state.PersistentState.PastSashas.AddRecord(new PastSashaRecord { ... });
var arc = state.PersistentState.Borrek.GetArcState(); // returns enum: Wary | Curious | Allied
state.PersistentState.HaelHints.Unlock(hintId: "wend_buried_under_paths");
bool freed = state.PersistentState.FreedPastSelves.Contains(record);
int total = state.PersistentState.RunCounter.TotalRuns;
```

Each namespace has a typed wrapper class with a clear API. JSON is the on-disk format; consumer code never sees it.

### Single-source rule

`state.PersistentState` is the **single in-memory mirror** of the persistence file. There is no second cache, no per-consumer copy, no sync layer. All reads and writes go through it. The mirror is loaded once at app start; writes flush to disk per the rules in §5.

---

## §2. Scope tiers (explicit)

Three tiers. Every piece of state in the game lives in exactly one.

### Tier 1: Run-scoped — *not in this file*

Cleared at run end (or floor descent for some). Lives in `GameState` and is reconstructed each run.

- Current floor, position, turn count
- Inventory contents, equipment, identification state (per `IdentificationRegistry` — already correctly run-scoped)
- Active status effects on player and monsters
- Hollowmark per-run line pool (which lines have fired this run — "every line is authored once per run" per v3 §C)
- Hollowmark per-run mute toggle (resets every run per v3 §C — "muted for the rest of the run")
- Per-run depth boons (per `BoonTracker` — already correctly run-scoped)
- Per-run pity counters (per `PityTracker`)
- **Past-Sasha "encountered this run" tracking.** `GameState.PastSashasEncounteredThisRun: HashSet<int>` — record IDs consumed in the current run. Resets at run start. The records themselves are cross-run (§6.2); the consumed-set is run-scoped.
- **Per-run unprovoked-kill counters for faction transitions.** `GameState.UnprovokedOrcKillsThisRun: int` — counter that drives the "3 unprovoked → Hostile" v3 §M-prime transition. Resets at run start. The reputation enum it transitions to is cross-run (§6.3); the counter is run-scoped.

These are listed for the *not-list* — anything in this tier is explicitly **out of scope** for the persistence file.

**Tier discipline rule:** every piece of state lives in exactly one tier. Run-scoped fields do not live in cross-run namespaces "for proximity." The boundary is what the tier system is for; smearing it weakens every other guarantee in this spec.

### Tier 2: Cross-run — *the entire surface of this spec*

Persists between runs of the same character. Cleared only on explicit save-wipe.

- Run counter, past-Sashas, faction reputation, Borrek/Vesh/Hael arc states, Marya-fragment unlocks, Hael-hint catalog, Freed Past-Selves catalog, Unshriven geas flag, Hollowmark meta-unlock state, achievements, cross-run NPC-encounter flags.
- Reserved-but-deferred: Hollowmark binding span integer (per v3 §C-prime "don't build this in v1") — field is reserved in the schema so future-us can fill it without a v1.x migration burden.

Full enumeration with field details in §6.

### Tier 3: Cross-version — *the migration story*

State that needs to survive a game update. For v1, **everything in Tier 2 is also Tier 3** — every cross-run field must round-trip through any future patch. The migration story (§3) is the mechanism.

The distinction matters for *future* additions: if we ever introduce state that's cross-run but explicitly version-locked (e.g., a leaderboard score whose calculation changes between versions and is invalidated on patch), it would be Tier 2 but not Tier 3. None today. Reserved category.

### Tier 4 (out-of-band): Settings — *separate file*

Player preferences that are not per-run choices and not persistent narrative state.

- Hollowmark verbosity default (Verbose / Tactical / Silent)
- Hollowmark always-mute toggle (overrides the per-run mute)
- Hardmode toggle (per `plan_possession_system.md` OQ-6 — disables drain safety rail)
- Difficulty setting (Easy / Medium / Hard — per `game_settings.yaml`)
- Daily-seed default opt-in
- Audio settings (when audio lands)
- UI theme / font-size / accessibility toggles

Settings live in a separate file — `user-dir/yarl_settings.json` — with its own schema and lifecycle. **Not in this spec.** Boundary mentioned only to make the not-list crisp.

---

## §3. Schema versioning and migration

### Per-namespace `schema_version` integers

Every namespace carries its own `schema_version` integer. Top-level `schema_version` is reserved for structural changes to the file shape itself (splitting/renaming namespaces, changing on-disk encoding, changing the location).

### Migration triggers

- **On load:** for each namespace, compare `file.namespaces.<ns>.schema_version` to the binary's current `LatestVersion[ns]`.
  - If equal: deserialize directly.
  - If file version < latest: run migrations forward, in sequence (`v1 → v2 → v3 → ...`), then deserialize.
  - If file version > latest: this is an **older binary loading a newer save**. Three options (open question §13, OQ-1):
    - **A. Tolerate** unknown fields, deserialize what's known, write back at the older version (lossy).
    - **B. Refuse** to load the namespace — fall back to defaults, warn the user.
    - **C. Refuse** to load the entire file — error to the user, don't risk corruption.
  - *Recommendation:* B for individual namespaces. Refuse-and-default a single namespace, keep the rest of the file working. Don't lose Borrek progress because we shipped a Hael migration the user hasn't installed yet.

### Migration code shape

```csharp
// src/Logic/Persistence/Migrations.cs
public static class Migrations
{
    public static readonly Dictionary<string, Dictionary<int, Func<JsonElement, JsonElement>>> Forward = new()
    {
        ["borrek"] = new()
        {
            // [fromVersion] → migrate to fromVersion+1
            // Migration v1 → v2: split "trust" into "arc_state" + "action_counter"
            [1] = (oldData) => { /* return new JsonElement with v2 shape */ },
        },
        ["past_sashas"] = new()
        {
            // none yet — v1 only
        },
        // ...
    };
}
```

Migrations are forward-only. We never migrate backward. Older binaries that encounter newer saves use the option-B fallback above.

### When to bump a namespace's version

| Change | Bump version? |
|---|---|
| Add a new field with a default value | **No** — System.Text.Json fills missing fields with the default. Stay at current version. |
| Remove a field | **Yes** — old saves still have the field; migration drops it. |
| Rename a field | **Yes** — migration copies old→new name. |
| Change a field's type or semantics | **Yes** — migration converts. |
| Add a new namespace | **No** — top-level schema_version stays. New namespace appears at v1; old saves don't have it; loader treats absent namespaces as defaults. |
| Remove or rename a namespace | **Yes** at the top level — structural change. |

### The default-value escape hatch

Most field additions don't need migrations. System.Text.Json deserializing `{"a": 1}` into a class with fields `{a, b}` simply leaves `b` at its default value. This means **most patches will not require migration code**, only a sensible default on the new field. Bump the namespace version only when shape changes invalidate that approach.

This is the single most important property of the design. Without it, every patch becomes a migration project. With it, most patches are field-additions with sensible defaults and no per-namespace version bump.

---

## §4. On-disk format and file location

### File path

The logic layer is Godot-free. It receives a `PersistencePathProvider` interface from the presentation layer at startup:

```csharp
public interface IPersistencePathProvider
{
    string GetMainSaveFilePath();    // e.g. "$HOME/Library/Application Support/Godot/yarl/yarl_persistence.json" on macOS
    string GetDailySeedsFilePath();  // sibling: yarl_daily_seeds.json in the same directory
    string GetSettingsFilePath();    // sibling: yarl_settings.json — settings file from §2 Tier 4
    string GetBackupDirectory();     // e.g. "$HOME/Library/Application Support/Godot/yarl/backups/"
}
```

Presentation provides the implementation, which resolves Godot's `user://` to the platform-appropriate path:
- macOS: `~/Library/Application Support/Godot/yarl/`
- iOS: app sandbox `Documents/`
- Windows: `%APPDATA%/Godot/yarl/`
- Linux: `~/.local/share/godot/yarl/`

Logic-layer code uses the abstract paths. Tests inject a temp-dir provider.

### File contents

Single JSON file, UTF-8, with newline at EOF. Pretty-printed with 2-space indent in debug builds for readability; minified in release builds for size. Both are valid JSON; both round-trip through the loader without semantic change.

### Atomic writes

Save writes are atomic to prevent corruption on crash mid-write:

1. Serialize new state to a string in memory.
2. Write to `yarl_persistence.json.tmp` in the same directory.
3. `File.Move` (atomic on every platform) `.tmp` → `yarl_persistence.json`, replacing the existing file.
4. `.tmp` is cleaned up by the move.

If the process dies between steps 1–3, the original file is intact. If it dies during step 3 — most filesystems guarantee `rename`-class atomicity, but iOS app-sandbox quirks should be tested.

### Backup snapshots

On every successful write, **before** the atomic replace, copy the existing main file to `backups/yarl_persistence.YYYYMMDD-HHMMSS.json`. Keep the most recent N (default 5) backup files; rotate older ones out. Surface "Restore Backup" in a settings menu for users who hit a corruption case the migration code didn't anticipate.

This is cheap insurance. The whole save file is small (kilobytes for the entire game's surface — not megabytes); five backup snapshots cost nothing.

### Encoding considerations under InvariantGlobalization

Per `feedback_ios_nativeaot.md`, iOS export runs with `InvariantGlobalization=true`. JSON is ASCII-safe by default, but free-form text fields (Marya-fragment notes, Hael-hint metadata, achievement names) may contain Unicode. Verify:
- Serialization writes Unicode escapes (`\uXXXX`) for non-ASCII characters when using the source-generated context — System.Text.Json defaults are correct here.
- Deserialization round-trips Unicode escapes correctly.
- Test specifically with non-ASCII in Marya fragments (place names from "Wend" lore — Revenese characters etc.) before declaring iOS-safe.

---

## §5. Lifecycle — load and write

### Load (once per app start)

1. App start in `Main.cs` — presentation layer constructs `IPersistencePathProvider`.
2. `PersistentState.LoadFromDisk(provider)` reads the main save file.
3. If file missing: create a fresh `PersistentState` with all namespaces at default values. Do NOT write to disk yet — wait for the first real change.
4. If file present: deserialize via source-generated `JsonSerializerContext`. Run migrations per §3. Surface load errors as a degraded-but-functional state (warn user, continue with defaults for the failed namespace).
5. Loaded state is held by `GameState` for the entire app session.

### Write (narrative-event-boundary)

Persistence flushes at **narrative-event boundaries**, not on per-turn dirty-flag scans. The earlier v1.0 end-of-turn model was rejected (OQ-5 closed B-modified) because it sets up a pattern where any future consumer accidentally calling `MarkDirty()` per-turn would write the file every turn for the rest of a run before anyone noticed.

Boundary events that flush (every one is an explicit, named call site):

| Boundary | Where it fires | What might be dirty |
|---|---|---|
| **Floor descent** | `DungeonFloorBuilder.BuildNextFloor` | Hollowmark meta-unlock progression, geas-flag side effects |
| **Dialogue close** | NPC dialogue system (separate plan) on modal dismiss | Borrek/Vesh/Hael arc state, hint unlocks, encounter flags |
| **Achievement unlock** | Achievement-trigger code paths | `achievements` namespace |
| **Faction-state enum transition** | `FactionRegistry` (or wherever the enum is set) — only the enum *change*, not the per-turn counter increments | `factions` namespace |
| **Marya/Hael/Freed-Past-Selves catalog entry unlock** | Hollowmark voice scheduler, Hael dialogue, possession Variant 3 dispel | Catalog namespaces |
| **Under-Warden memo state change** | Memo escalation logic | `under_warden` namespace (§6.15) |
| **Run end** | Game-over flow before screen renders | All dirty namespaces — forced |
| **App backgrounding** | Platform "going to background" hook (presentation) | All dirty namespaces — forced |
| **Manual Save and Quit** | Settings menu action | All dirty namespaces — forced |

**No per-turn flush.** No end-of-turn scan. The dirty system is event-driven on both ends — events `MarkDirty()`, the same events (or higher-level boundary events) `Flush()`. There is no cron-style sweep.

Per-turn run-scoped counters (`UnprovokedOrcKillsThisRun`, etc., per §2) are not persisted at all — they live in `GameState`, die at run end, and are re-derived from in-game actions on the next run. Loss-on-crash is acceptable for them. The **enum transition** is what flushes, not the counter increment.

### Coalescing

Multiple `MarkDirty()` calls between two boundary events naturally coalesce — only one flush runs at the next boundary, covering whichever namespaces were touched. No additional debounce timer is needed; the boundary itself is the debounce.

### Forced flush

Run end, app backgrounding, and manual Save-and-Quit are listed above as forced — they flush regardless of dirty state, just to guarantee the latest committed state hits disk. Trivial overhead (single small file write); explicit safety.

### Read

Reads are in-memory from `state.PersistentState`. No disk reads after the initial load. Consumers read the typed accessors directly.

---

## §6. Consumer integration

Each consumer namespace gets its own subsection. For each: data shape, write triggers, read sites, scope (run vs cross-run), and migration considerations.

### §6.1. `run_counter` — total runs ever started

```jsonc
{ "total_runs": 12, "first_run_started_at": "2026-04-26T..." }
```

- **Write:** at run start, increment `total_runs`. Set `first_run_started_at` once on first run.
- **Read:** Borrek dialogue gating reads it for "this is at least your second run" thresholds. Past-Sashas system reads it to refuse encounters on first run (per `plan_possession_system.md` and v3 §E-prime — "no first-run encounters with your own corpse").
- **Scope:** cross-run, cross-version. Never resets except by save-wipe.

### §6.2. `past_sashas` — record list of qualifying deaths

```jsonc
{
  "records": [
    {
      "id": 7,
      "died_run": 4,
      "died_floor": 9,
      "died_at": "2026-04-22T...",
      "cause_of_death": "monster",          // "monster" | "self_inflicted" | "under_warden"
      "killer_species": "orc_brute",         // null for self-inflicted
      "gear_carried": [                      // equipped slots only — see Gear serialization below
        { "type_id": "shortsword", "enchantment": 1, "condition": "normal" },
        { "type_id": "leather_armor", "enchantment": 0, "condition": "corroded" }
      ]
    }
  ],
  "next_id": 13                               // monotonic ID generator for new records
}
```

- **Write:** at player death (in `OnDeath` for the home body, `OnHomeBodyKilled` if death-during-possession), serialize current run's death info into a new record. Flushes on run end (boundary event).
- **Read:** at floor generation, `DungeonFloorBuilder` queries past-Sashas for an eligible record (see Eligibility below).
- **Scope:** records are cross-run. **The "consumed this run" tracking lives on `GameState` per §2 tier discipline, not in this namespace.** `GameState.PastSashasEncounteredThisRun: HashSet<int>` holds the record IDs already used in the current run; resets at run start.
- **Eligibility for encounter:** record exists, `total_runs >= 2`, record's `died_run` != current run, record ID not in `PastSashasEncounteredThisRun`, current floor matches (or exceeds — design knob) `died_floor`. The most-recent-qualifying record is selected.
- **Gear serialization (OQ-2 resolved as A):** **equipped slots only.** Items as `{ type_id, enchantment, condition }`. Inventory contents are not serialized — diegetically, the dungeon picked the body clean of everything not strapped to it. Tighter image, simpler image, deterministic recovery (no RNG retry loop where a player rolls past-Sasha encounters hoping to recover a specific potion).

### §6.3. `factions` — reputation enums per faction

```jsonc
{
  "factions": {
    "orc": { "state": "neutral", "runs_since_negative_action": 0 }
  }
}
```

- **Schema shape:** `Dictionary<string, FactionState>`. Keyed by faction-id. **v1 populates only `"orc"`.** Adding additional factions (`"hall_wardens"`, `"undead"`, etc.) in v1.x is a default-add — new keys appear; missing keys default to a fresh-Neutral `FactionState`. No migration needed.
- **State enum:** `Hostile | Neutral | Allied` (per v3 §M-prime resolution).
- **What's NOT in this namespace:** the per-turn unprovoked-kill counter. Per §2 tier discipline, `GameState.UnprovokedOrcKillsThisRun: int` holds the run-scoped counter; transitions to the cross-run enum happen when it crosses the threshold. The counter dies at run end without serializing.
- **Why other factions are absent in v1:** v3 §M-prime explicitly scopes the rep system to the Unshriven (orcs). Hall Wardens are possessable and feature in the Under-Warden's bureaucratic-grievance arc, but their relationship to Sasha is tracked via the `under_warden` namespace (§6.15) not a generic rep enum. Other monster factions (deeper undead, chthonic, beast) are territorial-by-default and don't carry per-run state. If a future feature needs rep tracking for a new faction, add the key — it's a default-add.
- **`runs_since_negative_action`:** the cross-run decay counter for OQ-3's soft-decay model. Increments at run end if no orc-negative action fired during the run; resets to 0 on any orc-negative action. Drives the Hostile → Neutral decay after the threshold (default proposal: 5 runs).
- **Write:** on enum change (Hostile↔Neutral↔Allied transition); at run end if `runs_since_negative_action` increments. Both are boundary-event flushes.
- **Read:** Borrek/Vesh/Hael dialogue gating; orc-faction patrol AI on the Boundary floors; floor generation for war-tunnel shortcut at Allied / orc-hunt at Hostile.
- **Scope:** cross-run with soft decay (per OQ-3 recommendation; finalized at Phase 0 close).

### §6.4. `borrek` — three-state arc + counter

```jsonc
{
  "arc_state": "wary",                 // "wary" | "curious" | "allied"
  "orc_positive_actions": 0,            // counter that drives transitions
  "knife_received": false,              // sentinel for the daughter's-bloodline gift
  "daughter_bloodline_news_delivered": false  // sentinel for the moment
}
```

- **Transitions:** 1 orc-positive action → Curious. 3 → Allied (per v3 §M-prime resolution). Persists across runs.
- **Write:** on action increment; on state transition; on sentinel flags.
- **Read:** Borrek dialogue tree (per the dialogue system, separate plan).
- **Scope:** cross-run. The arc state is sticky — once Allied, always Allied (until explicit save-wipe).

### §6.5. `vesh` — captain arc + Revenese-spirit transaction state

```jsonc
{
  "met": false,                         // first-met flag
  "jobs_completed": 0,                  // Vesh-job counter
  "spirit_received": false,             // has Sasha brought Vesh his Revenese spirit yet?
  "spirit_story_heard": false           // has the +1-stat moment fired?
}
```

- **Write:** on meet, on job completion, on spirit transaction.
- **Read:** Vesh dialogue; Hael-sells-spirit gating (per v3 §M-prime — Hael sells the spirit *once Vesh has been met and Hael is Allied-or-better*).
- **Scope:** cross-run.

### §6.6. `hael` — smuggler arc + hint chain

```jsonc
{
  "met": false,
  "relationship": "neutral",            // "neutral" | "trusted" | "allied"
  "hints_unlocked": ["wend_buried_under_paths", "branch_of_passage_clue"]
}
```

- **`branch_of_passage_unlocked` is NOT a stored field.** It is a computed property on the typed wrapper:

  ```csharp
  public bool BranchOfPassageUnlocked =>
      Relationship == HaelRelationship.Allied
      && HintsUnlocked.Count >= REQUIRED_HINT_COUNT;
  ```

  `REQUIRED_HINT_COUNT` is a tunable constant (default proposal: 4). One source of truth for the gate; no drift between the predicate and the underlying state.

- **Write:** on meet, on relationship transition, on hint unlock.
- **Read:** Hael dialogue; Things Hael Mentioned catalog page (§6.8); Crypt of Wend hidden-floor gating (per v3 §L Swap ending) reads the computed `BranchOfPassageUnlocked`.
- **Scope:** cross-run.

### §6.7. `marya_fragments` — Hollowmark's memory catalog

```jsonc
{
  "unlocked": [
    {
      "id": "marya_taught_by_artificer_with_cat",
      "unlocked_run": 3,
      "unlocked_at": "2026-04-23T...",
      "place": "Wend",                  // metadata for the catalog UI
      "fragment_text_ref": "marya_001"  // reference to content YAML
    }
  ]
}
```

- **Write:** on Hollowmark Marya-memory voice trigger fire (per `plan_possession_system.md` §13 trigger taxonomy — Marya memories are one-shot per run, but they're authored against the cross-run pool, so a fragment fires once and never re-fires across the player's entire history).
- **Read:** Marya Memory Fragments catalog page (UI, separate plan); Hollowmark voice scheduler (to skip already-fired fragments on subsequent runs).
- **Scope:** cross-run. Fragments fire once per player ever, not once per run.

### §6.8. `hael_hints` — Things Hael Mentioned catalog

```jsonc
{
  "unlocked_hints": [
    {
      "id": "wend_buried_under_paths",
      "unlocked_run": 5,
      "hint_text_ref": "hael_hint_001"
    }
  ],
  "branch_of_passage_unlock_marker": false  // surfaces in catalog when enough hints collected
}
```

- **Write:** on Hael dialogue branch that unlocks a hint.
- **Read:** Things Hael Mentioned catalog page; Crypt of Wend gating (the unlock marker fires the next-encounter Branch-of-Passage instructions per v3 §E).
- **Scope:** cross-run.

### §6.9. `freed_past_selves` — Variant 3 dispel records

```jsonc
{
  "records": [
    {
      "freed_past_sasha_id": "uuid-7",     // ref into past_sashas namespace
      "freed_run": 9,
      "freed_at": "2026-04-25T...",
      "freed_floor": 14
    }
  ]
}
```

- **Write:** on `PossessionSystem.OnPossessionInducedHostDeath` with `reason: "warden_dispelled"` (per `plan_possession_system.md` §8.5 v1.2).
- **Read:** Freed Past-Selves catalog page; Hollowmark voice scheduler (variant lines per dispel).
- **Scope:** cross-run.

### §6.10. `unshriven_geas` — push-the-marker flag

```jsonc
{
  "marker_pushed": false,
  "marker_pushed_run": null,
  "marker_pushed_at": null
}
```

- **Write:** on push-the-marker job completion (per v3 §D-prime).
- **Read:** `DungeonFloorBuilder` for floors 4–8 — when set, encounter composition tweaks slightly (more orc, less undead per v3 §D-prime).
- **Scope:** cross-run. One-time flag; once set, never unset.

### §6.11. `hollowmark_meta` — per-floor chattiness unlock state

```jsonc
{
  "floor_unlock_levels": {
    "1": 2,    // floor 1 has unlocked tier 2 of Hollowmark's voice variants (out of N tiers)
    "2": 1,
    "3": 1
  },
  "between_runs_lines_fired": [
    "br_intro_line_001",
    "br_intro_line_017",
    "br_consolation_004"
  ]
}
```

- **`between_runs_lines_fired` is a `HashSet<string>` of stable line IDs**, not an integer index. Patch-safe: when content is added to the between-runs pool in a future patch, prior records still point at the right lines. The scheduler picks an unfired line by id-not-in-set.
- **Write:** at floor descent (advance the floor's unlock level toward max); on between-runs result-screen line fired (add ID to `between_runs_lines_fired`).
- **Read:** Hollowmark voice scheduler (which voice-line variant to fire based on floor unlock level; which between-runs lines are still unfired); between-runs results screen.
- **Scope:** cross-run. Per v3 §J-K — "Hollowmark's voice-line meta-unlock that grows chattier per-floor across runs."

### §6.12. `achievements` — unlock list

```jsonc
{
  "unlocked": [
    { "id": "first_run_complete", "unlocked_at": "2026-04-22T..." },
    { "id": "wore_hall_warden", "unlocked_at": "2026-04-25T..." }
  ]
}
```

- **Write:** on achievement unlock event.
- **Read:** achievements UI page; certain dialogue gates.
- **Scope:** cross-run, cross-version. Achievement IDs are forever-stable strings.

### §6.13. `encounters` — first-met-NPC flags

```jsonc
{
  "met_borrek": false,
  "met_vesh": false,
  "met_hael": false,
  "met_under_warden": false,
  "met_lady_of_long_hour": false  // never met in-game in v1, but reserved
}
```

- **Write:** on first dialogue with each NPC, ever.
- **Read:** dialogue gating (e.g., Vesh-arc starts only after Borrek-met); narrative consistency checks.
- **Scope:** cross-run. Once met, always met.

### §6.14. `hollowmark_span` — *deferred, reserved*

```jsonc
{
  "remaining_span": null,
  "_note": "Reserved for future Hollowmark binding span mechanic per v3 §C-prime. Do not implement in v1."
}
```

- **Write:** none in v1. Field is reserved as a forward-compatible hook so v1.x can add the system without a migration.
- **Read:** none in v1.
- **Scope:** cross-run when activated. Reserved field. **Open question (§13, OQ-4):** ship the namespace empty, or omit the namespace entirely until needed? Recommendation: ship empty — costs nothing now, saves a migration later.

### §6.15. `under_warden` — memo escalation across runs

```jsonc
{
  "total_memos_sent_ever": 12,             // monotonic. INTENTIONALLY not derivable — see note below.
  "last_memo_tone": "formal_complaint",    // "polite" | "procedural_notice" | "formal_complaint" | "final_audit"
  "procedural_grievances_logged": [        // each grievance is a one-time fire, tracked forever
    "unauthorized_descent",
    "soul_transfer_volume_threshold",
    "hall_warden_possession_count_threshold"
  ],
  "audit_attempted_runs": 2,                // how many runs reached floor 25 with a Ledger interaction
  "audit_completed": false                   // sticky once true (Clean Audit ending fired)
}
```

**Note on `total_memos_sent_ever`.** This counter is intentionally stored separately from `procedural_grievances_logged`, even though a naive read suggests it could be derived (one memo fires per grievance, plus per-tone memo counts). It cannot be safely derived: tone-progression rules in the content YAML reference the raw count directly ("after 8 memos ever, escalate to formal_complaint regardless of grievance state"), and content authors will introduce variants that fire memos without logging a new grievance (acknowledgement memos, follow-up memos, reminder memos). Treat the counter as load-bearing primary state, not a derived view. **Do not remove during refactor passes** — content depends on it.

- **Why this consumer exists:** v3 §D has the Under-Warden's memos escalating across runs ("He knows Sasha keeps coming back" — v3 §C-prime). The escalation tone, formal-complaint history, and audit-attempt count are all cross-run state that drive the next run's memo content. Without this namespace, every run sees the same first memo regardless of the player's history.
- **Write:** on memo fire (advance tone if appropriate, record any newly-triggered grievance); at run end if a floor-25 Ledger interaction happened (increment `audit_attempted_runs`); on Clean Audit ending (set `audit_completed` true).
- **Read:** memo content selection at floor entry (the memo system queries `last_memo_tone` and `procedural_grievances_logged` to pick the next memo from the authored pool); Under-Warden floor-25 dialogue branches on `audit_attempted_runs` and `audit_completed`.
- **Scope:** cross-run. `audit_completed` is sticky-once-true (a player who completed Clean Audit on run 4 still has the flag on run 50 — drives different memo content forever after, "the previous attempt remains on file").
- **Tone progression:** monotonic forward — `polite → procedural_notice → formal_complaint → final_audit`. Once advanced, the tone does not regress (the Under-Warden's institutional memory does not soften). Specific advancement rules are content-driven (e.g., "after the third unauthorized soul-transfer ever, advance to formal_complaint") and live in the memo content YAML, not in this schema.
- **Grievance one-time-fire rule:** each grievance ID fires once ever and is logged forever after. Subsequent runs that would fire the same grievance read the log and skip — the Under-Warden does not log the same complaint twice.

---

## §7. Daily-seed sibling file

### Why a separate file

Daily seeds are conceptually different from per-character cross-run state:

- **Cross-run state** belongs to a character's history. If we ever support multiple characters, each character has its own cross-run record.
- **Daily-seed state** is global. The daily seed itself is the same for every player on a given date; the player's score on that seed is per-player. Daily-seed records don't fit into a character namespace cleanly.

Keeping them in separate files means:
- The main file is per-character (now, and trivially extensible to per-character-namespaced when multi-character lands).
- The daily-seed file is global — one file per device, regardless of how many characters exist.
- Resetting one doesn't risk the other.
- Daily-seed corruption doesn't break the main game.

### Schema

```jsonc
{
  "schema_version": 1,
  "saved_at": "2026-04-26T...",
  "records": {
    "2026-04-26": {
      "seed": "abc123-pinned",
      "best_score": 4250,
      "best_floor": 17,
      "runs_completed": 2,
      "first_run_completed_at": "2026-04-26T08:14:00Z",
      "leaderboard_synced": false        // future: cloud leaderboard hook, off in v1
    },
    "2026-04-27": { ... }
  }
}
```

- Per-date keyed by `YYYY-MM-DD`.
- Multiple runs per date supported — `best_score`, `best_floor`, `runs_completed` track aggregates.
- `leaderboard_synced` reserved for future cloud feature; default false.

### Lifecycle

- **Load:** at app start, alongside main file.
- **Write:** at end of any daily-seed run. Atomic write per §4.
- **Read:** main menu (today's seed status); leaderboard UI; achievement triggers ("complete the daily seed for 7 consecutive days").

### Scope

Cross-version. Daily seeds are forever — a player who completed 2026-04-26's daily seed should still see that record after every patch.

### Migration

Same per-file `schema_version` mechanism as the main file. Migrations live in `Migrations.DailySeeds.Forward[fromVersion]`.

---

## §8. NativeAOT / serialization constraints

### Source-generated `JsonSerializerContext` is mandatory

Per `feedback_ios_nativeaot.md`, iOS export uses NativeAOT with `InvariantGlobalization=true`. Reflection-based JSON serialization is not safe under NativeAOT — types may be trimmed or have their constructors stripped.

**Required:** every persistence type is registered in a source-generated `JsonSerializerContext`:

```csharp
[JsonSerializable(typeof(PersistentRunState))]
[JsonSerializable(typeof(PastSashaRecord))]
[JsonSerializable(typeof(BorrekState))]
// ... one [JsonSerializable] per persistence type
[JsonSerializable(typeof(DailySeedsFile))]
public partial class PersistenceJsonContext : JsonSerializerContext { }
```

The source generator emits compile-time-checked serializers. No reflection, no IL emit, NativeAOT-safe.

### What this constrains

- Every persistence type must be a concrete class (no `dynamic`, no `object` fields).
- Polymorphic types (e.g., a `PastSashaCause` discriminated union) are awkward — System.Text.Json supports them with `[JsonDerivedType]` attributes, but verify the source generator handles them under NativeAOT before committing.
- Adding a new persistence type means adding a new `[JsonSerializable]` attribute to `PersistenceJsonContext`. Easy to forget. Phase 1 should add a build-time test that fails if a type implementing `IPersistedRecord` (marker interface) is not registered.

### Trimming

`Logic.csproj` is currently `IsTrimmable=true` (the harness expects it). Persistence types must survive trimming. Source-generated context fixes this — explicitly registered types are root-marked. Verify on iOS export.

### Backup format

Backup files (per §4) use the same JSON format as the main file. They're loadable by the same loader. The backup directory rotation logic uses simple file-system operations (`Directory.GetFiles`, sorted by mtime, delete oldest beyond N).

---

## §9. New components, types, and files

### New files

| Path | Contents |
|---|---|
| `src/Logic/Persistence/PersistentRunState.cs` | Top-level record type; loads/saves; `MarkDirty`/`Flush` API. |
| `src/Logic/Persistence/PersistenceJsonContext.cs` | Source-generated `JsonSerializerContext` with all `[JsonSerializable]` attributes. |
| `src/Logic/Persistence/IPersistencePathProvider.cs` | Interface (per §4). |
| `src/Logic/Persistence/Migrations.cs` | Per-namespace forward migrations (per §3). |
| `src/Logic/Persistence/Namespaces/RunCounterState.cs` | Typed wrapper for §6.1. |
| `src/Logic/Persistence/Namespaces/PastSashasState.cs` | Typed wrapper for §6.2. |
| `src/Logic/Persistence/Namespaces/FactionsState.cs` | Typed wrapper for §6.3. |
| `src/Logic/Persistence/Namespaces/BorrekState.cs` | §6.4. |
| `src/Logic/Persistence/Namespaces/VeshState.cs` | §6.5. |
| `src/Logic/Persistence/Namespaces/HaelState.cs` | §6.6. |
| `src/Logic/Persistence/Namespaces/MaryaFragmentsState.cs` | §6.7. |
| `src/Logic/Persistence/Namespaces/HaelHintsState.cs` | §6.8. |
| `src/Logic/Persistence/Namespaces/FreedPastSelvesState.cs` | §6.9. |
| `src/Logic/Persistence/Namespaces/UnshrivenGeasState.cs` | §6.10. |
| `src/Logic/Persistence/Namespaces/HollowmarkMetaState.cs` | §6.11. |
| `src/Logic/Persistence/Namespaces/AchievementsState.cs` | §6.12. |
| `src/Logic/Persistence/Namespaces/EncountersState.cs` | §6.13. |
| `src/Logic/Persistence/Namespaces/HollowmarkSpanState.cs` | §6.14, deferred-but-reserved. |
| `src/Logic/Persistence/Namespaces/UnderWardenState.cs` | §6.15. |
| `src/Logic/Persistence/DailySeedsFile.cs` | §7 sibling file (separate top-level type). |
| `src/Presentation/Persistence/GodotPersistencePathProvider.cs` | Concrete `IPersistencePathProvider` resolving Godot's `user://`. |

### Modified files

| Path | What changes |
|---|---|
| `src/Logic/Core/GameState.cs` | Add `PersistentState` property of type `PersistentRunState`. |
| `src/Logic/Core/TurnController.cs` | At end-of-turn (after status decrements), check `state.PersistentState.IsDirty`; if true, flush. Forced flush on run end (in the existing game-over code path). |
| `src/Presentation/Main.cs` | At app start: construct `GodotPersistencePathProvider`, call `PersistentRunState.LoadFromDisk(provider)`, attach to GameState. At app backgrounding: forced flush. |
| `Logic.csproj` | Source-generated JSON context requires `<EnableSourceGenerators>true</EnableSourceGenerators>` and a reference to `System.Text.Json` (already present). Verify NativeAOT compatibility. |

### Marker interface

```csharp
public interface IPersistedNamespace
{
    string NamespaceKey { get; }      // "borrek", "past_sashas", etc.
    int CurrentSchemaVersion { get; } // bumped per §3 rules
    bool IsDirty { get; }
    void MarkClean();
}
```

Every namespace state class implements this. Reflection-free dirty-flag enumeration (Phase 1 pattern: hold them in a `List<IPersistedNamespace>` on `PersistentRunState`).

---

## §10. Implementation phases

| Phase | Sessions | Description |
|---|---|---|
| **Phase 0: Spec gate** | 1 | Resolve open questions (§13). Lock the on-disk format. |
| **Phase 1: Skeleton + JSON context** | 1 | `PersistentRunState`, `IPersistencePathProvider`, `PersistenceJsonContext` with stubs for all 15 namespaces, atomic load/save. Empty namespaces, no consumer wiring. **Mandatory deliverable:** generate a synthetic v1 save file with all namespaces populated with non-trivial test data, round-trip it through the iOS NativeAOT export build *before* any consumer code is written. This is the cheapest possible way to surface source-generator surprises; finding one now is hours, finding one in Phase 6 is days. |
| **Phase 2: Migration framework + backup rotation** | 1 | `Migrations.cs` skeleton, version comparison logic, fallback behavior per OQ-1. Backup directory rotation. Test: load a synthetic v1 file with a v2 binary; load a v2 file with a v1 binary. |
| **Phase 3: Run counter, encounters, achievements** | 1 | The simplest namespaces — small structs, clear write triggers. End-to-end: a run starts, counter increments, file persists, next run reads it back. |
| **Phase 4: Past-Sashas + freed-past-selves** | 1 | Schema for past-Sasha records (gear serialization is the load-bearing piece). Wire into `OnHomeBodyKilled`. Wire into Variant 3 dispel (per `plan_possession_system.md` §12). Floor builder reads records. |
| **Phase 5: Faction reputation + Unshriven geas** | 1 | Three-state enum, action counter, soft decay (per OQ-3 resolution). Push-the-marker flag. Floor builder reads geas flag for encounter composition. |
| **Phase 6: Borrek/Vesh/Hael arcs + Marya/Hael catalogs + Hollowmark meta-unlock** | 1–2 | The dialogue-system-dependent namespaces. Wires into the (separately-specced) NPC dialogue system. The catalogs surface in UI (separate plan). |
| **Phase 7: Daily-seed sibling file** | 1 | Separate file, separate loader, main-menu integration. |

**Total: ~7–9 sessions** to feature-complete the persistence backbone. Plus integration work in each consuming feature (already counted in those features' own plans).

Phases 1–3 are the foundation. Phase 4 is the integration with possession. Phases 5–7 are the consumer-by-consumer wiring. **Phases 1–3 should land before any consumer feature starts using persistence in production code** — consumers that touched stub persistence in earlier phases get retrofitted.

---

## §11. Test plan

### Unit tests (logic layer)

| Test | Verifies |
|---|---|
| Save → reload round-trips every namespace at v1 | Basic correctness. |
| Atomic write doesn't lose original on simulated mid-write crash | §4 atomic-write contract. |
| Load with missing file creates fresh state, doesn't write until first MarkDirty | §5 load semantics. |
| Load with partial-corrupt namespace falls back to defaults for that namespace, keeps others intact | §3 OQ-1 resolution. |
| Migration v1 → v2 transforms a synthetic v1 record into the expected v2 shape | §3. |
| Older binary loading newer save handles unknown namespace gracefully | §3 OQ-1 fallback. |
| Multiple MarkDirty calls in one turn coalesce to one flush at end-of-turn | §5 debouncing. |
| Forced flush on run end fires even if no MarkDirty was set this turn | §5. |
| Forced flush on app-background hook fires synchronously | §5 mobile lifecycle. |
| Past-Sasha eligibility: record from current run is excluded; first run has no records | §6.2. |
| Past-Sasha eligibility: encountered_this_run flag prevents same-run reuse | §6.2. |
| Backup rotation keeps 5 most recent | §4 backup. |
| Daily-seeds file load/save independent of main file | §7. |

### Integration tests

| Scenario | Validates |
|---|---|
| Multi-run: complete 5 runs of varying outcomes; verify run_counter, past_sashas, encounters all correct after | End-to-end persistence. |
| Variant 3 round-trip: die to Under-Warden on floor 14, descend on next run, find possessed corpse, dispel, verify gear matches and freed-past-selves grows by 1 | §6.2 + §6.9 + possession §8.5 integration. |
| Borrek arc: simulate 4 runs of orc-positive actions, verify Wary → Curious → Allied transitions persist | §6.4. |
| iOS NativeAOT export round-trip with a non-trivial save file | §8 — the load-bearing constraint. |
| Save corruption recovery: corrupt the file mid-byte; loader falls back to defaults; backup restore works | §4 + §3 robustness. |

### Harness validation

Persistence has no balance dimension; no harness sweeps required. Smoke tests above are sufficient.

---

## §12. What's deliberately not in this spec

Listed for the not-list:

- **Multi-character / save slots.** v3 doesn't ask. Schema extends cleanly when needed (add a `characters` map at top level, namespace records by character_id).
- **Cloud sync / iCloud.** Local-only v1.
- **Settings persistence.** Separate file (§2 Tier 4).
- **Save scumming protections.** Out of scope.
- **Replays / run history.** Distinct from "how many runs total" — actually replaying a prior run's input log is a feature we're not building.
- **Cross-device sync.** Out of scope.
- **Per-run Hollowmark line pool tracking** (which lines fired this run). Run-scoped, lives in `GameState`, not here.
- **Per-run mute toggle.** Run-scoped, lives in `GameState`.
- **Identification state, depth boons, pity counters.** Already correctly run-scoped via existing systems.

---

## §13. Open questions

These need design judgment before Phase 1.

**OQ-1: Older binary loading newer save — fallback policy.**
- A: Tolerate unknown fields, deserialize what's known, write back at the older version (lossy).
- B: Refuse to load the affected namespace, fall back to defaults, warn user. Other namespaces unaffected.
- C: Refuse the entire file, fall back to defaults globally.
- *Recommendation:* B. Single-namespace failure shouldn't lose all of the player's history. Surfaces a "Your save was created in a newer version of the game; some features may be unavailable" warning on the main menu.

**OQ-2: Past-Sasha gear-carried scope.** **Resolved 2026-05-02 as A.**
- A: Equipped slots only.
- B: Equipped + inventory.
- C: Equipped + 50% random inventory subset.
- **Resolution: A.** Simpler, more predictable, deterministic. "The dungeon picked the body clean of everything not strapped to it" is a tighter image than "kept some, flipped a coin on the rest." Avoids the mobile-hostile RNG retry loop of C (where a player rerolls past-Sasha encounters hoping to recover a specific potion). Sidesteps the balance question (is 50% right? does it scale?) entirely. §6.2 updated accordingly.

**OQ-3: Faction reputation persistence.**
- A: Per-run only — reputation resets every run.
- B: Cross-run, sticky — once Hostile, always Hostile until a positive action.
- C: Cross-run, soft decay — Hostile → Neutral after N runs of no orc-negative actions (default proposal: 5 runs).
- *Recommendation:* C. Cross-run with decay. Forces accountability for the current run's actions but doesn't permanently lock the player out of the orc faction. The decay rate is a balance knob.

**OQ-4: Reserve `hollowmark_span` namespace in v1?**
- A: Ship the namespace empty (reserved field, no consumer code).
- B: Omit entirely; add when the system is built.
- *Recommendation:* A. Costs nothing to ship empty; saves a top-level schema bump later. The namespace is a forward-compatible hook for the v3 §C-prime feature.

**OQ-5: Debounce window granularity.** **Resolved 2026-05-02 as B-modified.**
- A (rejected): Flush at end-of-turn. Sets up a pattern where a future consumer accidentally calling `MarkDirty()` per-turn writes the file every turn for the rest of a run before anyone notices the bug.
- B (rejected): Flush at end-of-floor. Loses too much on mid-floor crash for narrative state.
- C (rejected): No debouncing, every event flushes. Too I/O-heavy.
- **Resolution: B-modified — flush at narrative-event boundaries.** Concrete trigger list in §5: floor descent, dialogue close, achievement unlock, faction-state enum transition, NPC arc state transition, catalog entry unlock, Under-Warden memo state change, run end, app background, manual save-and-quit. Per-turn run-scoped counters live on `GameState` (per §2 tier discipline) and are not persisted at all — loss-on-crash is acceptable for them. The boundary itself is the debounce; no separate timer needed. §5 updated accordingly.

**OQ-6: Save-wipe UI.**
- Should the settings menu surface a "Wipe Save Data" option? If yes: with confirmation? With a "delete daily seeds too" sub-option?
- *Recommendation:* Yes; double-confirm; daily-seeds is a separate sub-option. Necessary for QA, useful for players who want a fresh-start, simple to implement.

**OQ-7: Schema-validation failure mode at load.**
- If a namespace's schema is at v3 in the binary, but the file's namespace is v3 yet contains malformed data (wrong type for a field, missing required field), what happens?
- A: Treat as schema mismatch, fall back to defaults for that namespace (per OQ-1B).
- B: Hard error; refuse to load the file; force user to restore from backup.
- *Recommendation:* A. Same fallback as OQ-1B. The malformation may be a one-off bug or save-file edit; degrading gracefully beats hard-failing on a roguelike that's about to start a fresh run anyway. Log the error to `user-dir/persistence_errors.log` for diagnosis.

**OQ-8: Past-Sasha record retention cap.**
- After 100 runs of dying, the past_sashas list has 100 records. Most are stale. Do we cap?
- A: No cap — store every qualifying death forever. Storage is cheap.
- B: Cap at N most-recent qualifying records (N = 25 proposal). Older records age out.
- C: Cap at N, but never age out a record that's the *most recent* per cause-of-death (so the player always has a chance at each Variant).
- *Recommendation:* A. Even at 1000 runs the storage is trivial (kilobytes). The eligibility logic already picks the most-recent record, so older records don't slow anything down. Reconsider only if a real performance issue surfaces.

**OQ-9: Atomic-write semantics on iOS.**
- iOS app sandbox has quirks around `File.Move` atomicity. Some posts in the .NET-on-iOS community report `Move` not being atomic in all cases.
- *Action:* Verify on a real device during Phase 1. If non-atomic, add `fsync` after the temp-file write before the move. If still problematic, fall back to write-direct-then-fsync (lose the atomic-rename property; rely on backup snapshots for recovery).

**OQ-10: When the user changes system clock between runs.**
- Daily-seeds use date keys. A user who time-travels their device clock can replay a daily seed under a different key. Not a security concern (single-player), but the leaderboard hook (when added) cares.
- *Recommendation:* Tag each daily-seed completion with both the device-time-at-completion and a UTC anchor from a network call (when online). Mismatch flags the record as "unverified" for future leaderboard purposes. Out-of-scope for v1; reserved as a metadata field.

**OQ-11: Heirlooms across runs.** *(New 2026-05-02.)*
- v3 §M-prime has Borrek gifting Sasha a knife as the daughter's-bloodline-news payoff. Vesh may share his Revenese-spirit story with a +1 stat moment. Some of these are run-permanent items (carried for that run only); some could be cross-run heirlooms (next-run start with Borrek's knife in inventory).
- v3 doesn't explicitly designate any item as a cross-run heirloom. v2 had heirlooms as a vague concept; v3 dropped the explicit framing.
- A: No cross-run heirlooms in v1. Knife etc. are run-scoped. Cleaner, less to spec.
- B: Designate specific items (Borrek's knife, ?) as heirlooms. Add `heirlooms` namespace tracking which heirloom items the player has earned ever; auto-add to run-start inventory.
- C: Heirlooms exist but are *commemorative*, not mechanical — Borrek's knife appears in a between-runs catalog page as a memento, not in starting inventory.
- *Recommendation:* C. Heirlooms as long-tail commemoration is the same shape as Marya fragments / Things Hael Mentioned / Freed Past-Selves — content for engaged players, no balance impact, no migration when added later. The schema would be a new namespace `heirlooms: { earned: [{ id, earned_run, earned_from }] }`. **Defer the namespace addition until v1.x or until any heirloom is actually authored** — costs nothing to add later as a default-add per §3.

---

## Files for reference

| File | What it tells us |
|---|---|
| `docs/story/the_under_warden_v3.md` §C-prime, §D-prime, §E, §E-prime, §J-K, §L, §M-prime | Source design for every cross-run consumer. |
| `tasks/plans/plan_possession_system.md` §6.2, §6.9, §12 | Past-Sashas + Freed-Past-Selves consumer integration; the load-bearing reason persistence schema must land before possession Phase 5. |
| `~/.claude/projects/-Users-rafehatfield-development-c-yarl/memory/feedback_ios_nativeaot.md` | NativeAOT + InvariantGlobalization constraints driving §8. |
| `src/Logic/Content/IdentificationRegistry.cs` | Reference shape for a per-run-only state container — shows the *not* pattern (this is what cross-run consumers don't do). |
| `src/Logic/Core/GameState.cs` | Where `PersistentState` attaches. |
| `src/Logic/Core/TurnController.cs` | Where the end-of-turn flush hook lands. |
| `src/Presentation/Main.cs` | Where the path provider is constructed and the load-on-startup happens. |
