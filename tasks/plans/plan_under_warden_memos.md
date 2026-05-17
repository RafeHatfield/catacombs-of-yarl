# Plan: Under-Warden Memo Delivery System

**Status:** [ ] Not started (2026-05-13). YAML schema defined, content drafting in progress. Engineering not yet built.

---

## What It Is

A memo delivery system that surfaces Under-Warden correspondence between dungeon runs. Memos appear in an inbox UI after each run (or on the main menu), presenting bureaucratic notes from the Under-Warden keyed to specific in-run incidents.

Memos are keyed by `{tone}.{incident_type}` and stored in `config/under_warden/memos.yaml`. Two registers exist:

- **direct** — The Under-Warden writing TO Sasha (formal, escalating tone over repeat incidents)
- **internal_cc** — The Under-Warden writing ABOUT Sasha to departments, with Sasha cc'd (bureaucratic aside, dry humor, escalating dossier)

---

## Tone Taxonomy

Tone names are locked (used as keys in cross-run persistence schema; changing them breaks saved data):

| Tone | Character |
|------|-----------|
| `polite` | Courteous, almost warm — opening correspondence |
| `procedural_notice` | Formal record-keeping tone — incident noted, no judgment yet |
| `formal_complaint` | Elevated concern — pattern flagged, wording careful |
| `final_audit` | Terminal tone — exhausted patience, consequences implied |

---

## Incident Types

| Incident Key | Trigger |
|---|---|
| `death_first` | First run death ever |
| `death_repeat` | Subsequent deaths |
| `cause_trap` | Death caused by a trap |
| `cause_acid` | Death caused by acid damage |
| `cause_possession_neglect` | Home body killed during possession |
| `cause_own_poison` | Death by own poison (e.g. splash, misuse) |
| `floor_low` | Run ended on floor 1 or 2 |
| `floor_milestone` | Reached a new deepest floor |
| `audit_warning` | Cross-run threshold crossed (e.g. 10 deaths) |
| `audit_final` | Terminal audit threshold crossed |
| `catalog_referenced` | A catalog entry was accessed in-run |
| `item_theft` | Item taken that was flagged as Under-Warden property |
| `run_clean` | Completed a run with no traps triggered, no possession |

---

## Slot Vocabulary

Memos support interpolated slots in subject and body text. All slots come from cross-run persistence or run result data — no hardcoded C# strings:

| Slot | Source |
|---|---|
| `{run_number}` | Cross-run persistence: total run count |
| `{floor}` | Run result: deepest floor reached |
| `{cause_of_death}` | Run result: cause key, resolved via `cause_display_names.yaml` |
| `{killer_species}` | Run result: species that landed the killing blow |
| `{run_count}` | Cross-run persistence: total runs |
| `{memo_count}` | Cross-run persistence: total memos sent |
| `{floor_best}` | Cross-run persistence: best floor ever reached |
| `{offense_summary}` | Cross-run persistence: computed summary of flagged incidents |
| `{catalog_entry}` | Catalog entry referenced (for `catalog_referenced` incident) |

---

## Cause Display Names

Readable display phrases for `{cause_of_death}` slot live in `config/under_warden/cause_display_names.yaml` — not hardcoded in C#.

Fallback behavior (when a key is missing from the YAML): convert underscore to space, apply title-case. Example: `orc_brute` → "Orc Brute".

---

## First-Fire Semantics

Different from `VoiceLineRegistry` (session-level deduplication):

- Canonical body[0] of each memo fires **once ever** — cross-run persisted in the `under_warden` namespace.
- Subsequent fires of the same `{tone}.{incident_type}` key use body[1..n] variants in round-robin or random order.
- Each body entry is an object with `subject` and `body` fields (supporting multi-line body text).

This means repeat incidents accumulate a growing correspondence thread, not the same letter again.

---

## YAML Schema

```yaml
# config/under_warden/memos.yaml
memos:
  polite.death_first:
    register: direct
    bodies:
      - subject: "Re: Your Recent Departure from Active Service"
        body: |
          Mr. Valdris,

          It has come to our attention that you have died. We understand this is
          sometimes an adjustment. The Reven Administration wishes you a prompt
          recovery and looks forward to your continued engagement with the
          cataloging initiative.

          Should you have questions about the reintegration process, please
          consult your assigned liaison.

          With regard,
          The Under-Warden
          Office of Depth Compliance
      - subject: "Re: Subsequent Departure from Active Service"
        body: |
          Mr. Valdris,

          Again.

          With diminishing regard,
          The Under-Warden
```

---

## Content Status

| Memo Key | Status |
|---|---|
| `polite.death_first` | Drafted (canonical body[0] complete) |
| All others (~29 memos) | In progress |

---

## Engineering Status

| Component | Status |
|---|---|
| YAML schema | Defined (see above) |
| `config/under_warden/memos.yaml` | Not yet created |
| `config/under_warden/cause_display_names.yaml` | Not yet created |
| `MemoRegistry` | Not yet built — structured lookup returning `MemoDefinition` with subject, body, register |
| `MemoDefinition` type | Not yet built |
| Delivery UI (memo inbox) | Not yet designed or built |
| Cross-run persistence wiring (`under_warden` namespace) | Schema reserved, wiring not yet built |

---

## Implementation Phases

| Phase | Description |
|---|---|
| 1 | YAML files: `memos.yaml` + `cause_display_names.yaml`. `MemoDefinition` type. `MemoRegistry` loader and lookup. Unit tests for registry. |
| 2 | Cross-run persistence wiring: track which memo body indices have fired, which incident keys have been triggered. Integration with `under_warden` namespace. |
| 3 | Slot interpolation: `MemoFormatter` takes `MemoDefinition` + slot values dict, returns formatted subject + body. Tests for all slot types including missing-key fallback. |
| 4 | Delivery trigger: after each run, evaluate which incident keys fire, select correct memo + body index, write to pending-memos queue in persistence. |
| 5 | Inbox UI: presentation layer, displayed between runs or on main menu. Read from pending-memos queue, mark as read. |

---

## Files To Create

| Path | Contents |
|---|---|
| `config/under_warden/memos.yaml` | ~30 memos across 4 tones and 13 incident types |
| `config/under_warden/cause_display_names.yaml` | Display names for cause-of-death keys |
| `src/Logic/Content/MemoRegistry.cs` | YAML loader + structured lookup |
| `src/Logic/Content/MemoDefinition.cs` | DTO: subject, body list, register enum |
| `src/Logic/Content/MemoFormatter.cs` | Slot interpolation logic |
| `src/Presentation/UI/MemoInboxPanel.cs` | Delivery UI |
| `tests/Content/MemoRegistryTests.cs` | Unit tests |
| `tests/Content/MemoFormatterTests.cs` | Slot interpolation tests |

---

## Cross-References

- `tasks/plans/plan_cross_run_persistence.md` — `under_warden` namespace lives here; memo fire state persists here
- `tasks/plans/plan_possession_system.md` — `cause_possession_neglect` incident type depends on possession exit data
- `docs/story/the_under_warden_v3.md` — narrative source for Under-Warden voice and tone taxonomy
