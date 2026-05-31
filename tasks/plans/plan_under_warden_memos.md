# Plan: Under-Warden Memo Delivery System

**Status:** [x] Phase 4 complete. All engineering phases done; content drafting ongoing (see Content Status table).

**Content status:** 13 memos across 8 incident types (sessions 1–3). cause_trap + cause_acid have body[1+] variants. ~12 remaining.

---

## What It Is

A memo delivery system that surfaces Under-Warden correspondence between runs. Memos
appear in an inbox UI after each run, presenting bureaucratic notes keyed to specific
in-run and cross-run incidents. Two registers:

- **direct** — Written TO Sasha. Personal address, tone progression per incident type.
- **internal_cc** — Written ABOUT Sasha to departments; Sasha cc'd as procedural
  courtesy. Third-person, chilling institutional distance. The contrast with direct
  correspondence is the point.

---

## Tone Taxonomy (locked — matches `under_warden` persistence namespace keys)

| Tone | Character |
|------|-----------|
| `polite` | Courteous, institutional. Opening correspondence. Almost warm. |
| `procedural_notice` | Pattern noted, regulations cited. No judgment — yet. |
| `formal_complaint` | Complaint filed. The patience is still present; the mask is not. |
| `final_audit` | Terminal. Brief. Administrative. Like a termination notice. |

---

## Incident Types

Key format: `{tone}.{incident_type}`. Each incident_type has a fixed register.

| Incident Key | Register | Trigger condition |
|---|---|---|
| `death_first` | internal_cc | First run death ever |
| `death_repeat` | direct | 3rd+ cumulative death |
| `cause_trap` | direct | Death caused by a trap |
| `cause_acid` | direct | Death caused by acid damage |
| `cause_possession_neglect` | direct | Home body killed during possession |
| `cause_own_poison` | direct | Death by own poison (throw, splash) |
| `floor_low` | direct | Death on floor 1–3 |
| `floor_milestone` | internal_cc | First time reaching floor 10 / 15 / 20 |
| `audit_warning` | direct | Cumulative death count crosses audit threshold |
| `audit_final` | direct | Terminal audit threshold (final warning) |
| `catalog_referenced` | direct | A catalog entry surfaced in-run (standalone session — uses {catalog_entry} slot) |
| `item_theft` | direct | Item flagged as Under-Warden property taken |
| `run_clean` | direct | Run completed without traps triggered and without possession |
| `hall_warden_possession` | direct | Player has possessed a Hall Warden N times across runs |

### `hall_warden_possession` thresholds

| Fires at | Tone |
|---|---|
| 1st Hall Warden possession ever | `polite` |
| 3rd cumulative possession | `procedural_notice` |
| 6th+ cumulative possession | `formal_complaint` |

Tracked via `hall_warden_possessions_total` counter in `under_warden` namespace.
Incremented on `PossessionExitedEvent` where `HostSpecies == "hall_warden"`.

---

## Slot Vocabulary

| Slot | Source |
|---|---|
| `{run_number}` | `RunCounterData.RunCount` |
| `{floor}` | Run result: floor death/event occurred on |
| `{cause_of_death}` | Run result cause key → resolved via `cause_display_names.yaml` |
| `{killer_species}` | Run result: killer entity species |
| `{run_count}` | `RunCounterData.RunCount` |
| `{memo_count}` | `under_warden.memo_count` |
| `{floor_best}` | `RunCounterData.BestFloorReached` |
| `{offense_summary}` | Computed from `under_warden` grievance log |
| `{catalog_entry}` | `CatalogEntryRenderer.RenderEntry()` for most recent past-self |

---

## Cause Display Names

`config/under_warden/cause_display_names.yaml` — bureaucratic phrases for engine
cause-of-death strings. Loaded at render time. Fallback: underscore→space + title-case.

**File exists.** 20 entries covering environmental hazards, self-inflicted, monster
causes, and special cases (including `under_warden_directly`).

---

## First-Fire Semantics

Different from `VoiceLineRegistry` (session-level):

- `body[0]` fires **once ever** — cross-run persisted in `under_warden.delivered_memos`
  (a `HashSet<string>` of fired `{tone}.{incident_type}` keys).
- Subsequent fires of the same key use `body[1..n]` variants (random selection from pool).
- Single-shot incident types (`death_first`, `floor_milestone`, `audit_final`,
  `catalog_referenced`) author `body[0]` only — no variants needed.
- Multi-fire types (`cause_trap`, `cause_acid`, `death_repeat`, `audit_warning`, etc.)
  author `body[0]` as first-encounter pitch (more explanatory), `body[1..n]` as repeat
  variants (shorter, assume familiarity, different angle on the fifth fire than the first).

---

## YAML Format

```yaml
# config/under_warden/memos.yaml
# Key: {tone}.{incident_type}
# register: direct | internal_cc
# to: department string (internal_cc only; authored content, not rendered)
# subject: string (slots allowed)
# body: list — body[0] canonical first-fire; body[1+] repeat variants
# Emphasis: **text** → bold (parsed by MemoRenderer; do not use BBCode directly)

polite.death_first:
  register: internal_cc
  to: "Occupancy Management, Sublevel Correspondence"
  subject: "Attrition Record: Unit #{run_number}, Floor {floor}"
  body:
    - |
      From: The Under-Warden
      To: Occupancy Management, Sublevel Correspondence
      Cc: Unit #{run_number}, as procedural courtesy
      ...
```

**File exists.** 7 memos across 4 incident types. See `config/under_warden/memos.yaml`.

---

## Content Status

| Memo Key | Status |
|---|---|
| `polite.death_first` | ✅ Drafted (body[0] canonical) |
| `polite.floor_low` | ✅ Drafted (body[0]) |
| `polite.cause_trap` | ✅ Drafted (body[0] + body[1] + body[2]) |
| `polite.cause_acid` | ✅ Drafted (body[0] + body[1] + body[2]) |
| `polite.hall_warden_possession` | ✅ Drafted (body[0]) |
| `procedural_notice.hall_warden_possession` | ✅ Drafted (body[0]) |
| `formal_complaint.hall_warden_possession` | ✅ Drafted (body[0]) |
| `procedural_notice.death_repeat` | ✅ Drafted (body[0]) — 2026-05-30 |
| `procedural_notice.cause_possession_neglect` | ✅ Drafted (body[0]) — 2026-05-30 |
| `procedural_notice.audit_warning` | ✅ Drafted (body[0]) — 2026-05-30 |
| `procedural_notice.run_clean` | ✅ Drafted (body[0]) — 2026-05-30 |
| `catalog_referenced` (any tone) | ⬜ Standalone session (needs {catalog_entry} slot wired) |
| Remaining ~12 memos | ⬜ Future sessions |
| `body[1+]` variants for remaining multi-fire triggers | ⬜ Future session |

---

## Engineering Status

| Component | Status |
|---|---|
| `config/under_warden/memos.yaml` | ✅ Created (7 memos) |
| `config/under_warden/cause_display_names.yaml` | ✅ Created (20 entries) |
| `MemoDefinition` type | ✅ Built |
| `MemoRegistry` (YAML loader + lookup) | ✅ Built |
| `MemoFormatter` (slot interpolation) | ✅ Built |
| Cross-run persistence wiring | ✅ Built (`ProceduralGrievancesLogged`, `TotalMemosSentEver`, `HallWardenPossessionsTotal`, `PendingMemos`) |
| `PostRunContext` DTO | ✅ Built — `src/Logic/Content/PostRunContext.cs` |
| `MemoDeliveryEvaluator` | ✅ Built — `src/Logic/Content/MemoDeliveryEvaluator.cs` (19 tests) |
| Inbox UI (`MemoInboxPanel`) | ✅ Built — `src/Presentation/UI/MemoInboxPanel.cs` (Phase 4) |
| `Main.cs` wiring | ✅ Complete — registry load, `EvaluateRunEnd`, `EvaluateHallWardenPossession`, `OnReplayRequested`, `OnInboxClosed` |

---

## Implementation Phases

**Phase 1 — Registry + formatter (Logic layer)**
- `MemoDefinition` DTO: `Register` (enum), `To` (nullable string), `Subject`, `Body` (list)
- `MemoRegistry`: YAML loader, `{tone}.{incident_type}` lookup, compound-key fallback,
  `MemoDefinition? GetMemo(string key, int fireIndex)` where `fireIndex` 0 = first-fire
- `MemoFormatter`: slot interpolation — takes `MemoDefinition` + `Dictionary<string, string>` slots,
  returns `(subject: string, body: string)`; cause display name lookup from `cause_display_names.yaml`
- AOT factory registration
- Tests: registry lookup, missing key graceful null, slot substitution, cause display name fallback

**Phase 2 — Cross-run persistence fields**
- `under_warden` namespace additions:
  - `delivered_memos: HashSet<string>` — tracks fired `{tone}.{incident_type}` keys (for first-fire semantics)
  - `memo_count: int` — total memos ever delivered (feeds `{memo_count}` slot)
  - `hall_warden_possessions_total: int` — incremented on `PossessionExitedEvent` where host is hall_warden
  - `pending_memos: List<PendingMemo>` — queue of memos waiting to surface in inbox
- `PendingMemo` record: `Key`, `Subject`, `Body`, `DeliveredRun`
- Tests: counter increment, delivered_memos deduplication, pending queue add/consume

**Phase 3 — Delivery trigger (post-run evaluation)** ✅ COMPLETE
- `PostRunContext` DTO: `src/Logic/Content/PostRunContext.cs`
- `MemoDeliveryEvaluator`: `src/Logic/Content/MemoDeliveryEvaluator.cs`
  - `EvaluateRunEnd(PostRunContext, PersistentRunState, MemoRegistry)` — 4 incident checks
  - `EvaluateHallWardenPossession(PersistentRunState, MemoRegistry, int)` — threshold checks at 1/3/6+
- 19 tests in `tests/Content/MemoDeliveryEvaluatorTests.cs`, all passing
- Wiring into post-run flow (`Main.cs`) deferred to Phase 4 (presentation layer work)

**Phase 4 — Inbox UI**
- `MemoInboxPanel.cs` in Presentation layer
- Reads `pending_memos` from persistence; displays subject list + selected body
- Marks memos as read (removes from pending queue, increments `memo_count`)
- Surfaces after run-end screen, before floor transition on new run
- **BBCode rendering**: MemoRenderer parses `**text**` → `[b]text[/b]` before display

---

## Files To Create

| Path | Contents |
|---|---|
| `src/Logic/Content/MemoDefinition.cs` | DTO with Register enum, To, Subject, Body list |
| `src/Logic/Content/MemoRegistry.cs` | YAML loader, lookup, AotObjectFactory registration |
| `src/Logic/Content/MemoFormatter.cs` | Slot interpolation + cause display name resolution |
| `src/Logic/Content/MemoDeliveryEvaluator.cs` | Post-run incident evaluation → pending queue |
| `src/Logic/Persistence/Namespaces/UnderWardenData.cs` | Namespace data class (or extend existing) |
| `src/Presentation/UI/MemoInboxPanel.cs` | Inbox UI |
| `tests/Content/MemoRegistryTests.cs` | Registry tests |
| `tests/Content/MemoFormatterTests.cs` | Slot interpolation tests |
| `tests/Content/MemoDeliveryEvaluatorTests.cs` | Incident detection tests |

---

## Open Questions

- **`catalog_referenced` slot source**: `CatalogEntryRenderer.RenderEntry()` requires a
  live `PastSashasData` record and `VoiceLineRegistry`. The memo delivery evaluator will
  need both wired in. Handle in standalone session once catalog content is drafted.
- **`run_clean` definition**: exact trigger condition TBD (no traps triggered AND no
  possession? or just no deaths from self-inflicted causes?). Calibrate when drafting
  the `procedural_notice.run_clean` memo.
- **`MemoInboxPanel` placement**: surfaces after run-end screen vs. as a main-menu item
  vs. both. Decide during Phase 4.

---

## Cross-References

- `plan_cross_run_persistence.md` — `under_warden` namespace; `UnderWardenData` class
- `plan_possession_system.md` — `cause_possession_neglect` incident + `hall_warden_possessions_total` counter
- `config/under_warden/memos.yaml` — authored memo content
- `config/under_warden/cause_display_names.yaml` — cause display name mapping
- `docs/story/the_under_warden_v3.md` — tone taxonomy source, voice calibration
