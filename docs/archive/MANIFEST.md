# Archive Manifest

_Last verified: 2026-07-12 against commit 86b6f10_

Historic and superseded documentation moved here during the 2026-07 documentation
reconciliation. **Nothing here is current-state reference.** Content is preserved (moved,
not deleted) so history is not lost. Kept by maintainer ruling 2026-07-16: retained as
provenance cited by the release roadmap and `tasks/plans/`; not current-state reference.
See `reports/doc_reconciliation_2026-07.md`.

| Archived path | Original path | Reason |
|---|---|---|
| `archive/PHASES.md` | `docs/PHASES.md` | Historic development-phase narrative, self-dated "Last Updated: 2024-12-14". Lists completed work as "planned". Current status now lives in `docs/systems/INDEX.md` and `tasks/plans/INDEX.md`. |
| `archive/memo_handoff_session_3.md` | `docs/memo_handoff_session_3.md` | Stale session handoff memo. Its memo content has been committed to `config/under_warden/memos.yaml` (verified: `procedural_notice.death_repeat` and siblings present), so the handoff is spent. |
| `archive/story/the_under_warden_v2.md` | `docs/story/the_under_warden_v2.md` | Superseded Under-Warden narrative draft. Current narrative: `docs/story/THE_UNDER_WARDEN_story.md`. |
| `archive/story/the_under_warden_v3.md` | `docs/story/the_under_warden_v3.md` | Superseded Under-Warden narrative draft. |
| `archive/story/the_under_warden_design_notes.md` | `docs/story/the_under_warden_design_notes.md` | Design notes for the Under-Warden systems, which are now implemented (possession, memos, cross-run persistence). Retained as provenance. |
| `archive/story/the_tax_collector_proposal.md` | `docs/story/the_tax_collector_proposal.md` | Proposal for an unimplemented story. |
| `archive/story/the_tax_collector_design_notes.md` | `docs/story/the_tax_collector_design_notes.md` | Design notes for the unimplemented Tax Collector story. |
| `archive/story/other-stories-not-implemented/` (11 files) | `docs/story/other-stories-not-implemented/` | Proposals for stories that were never built (vess, long_winter, vale, tax_collector, last_letter, long_rotation, two compass-artifact research dumps, and duplicate under_warden v2/v3 drafts). |

## Note on inbound references

Several **plan** files under `tasks/plans/` cite the archived Under-Warden drafts as design
provenance (by filename + section), e.g. `plan_cross_run_persistence.md`,
`plan_possession_system.md`, `plan_under_warden_memos.md` reference
`the_under_warden_v2.md` / `v3.md` / `the_under_warden_design_notes.md`. Those plan files were
out of scope for this reconciliation (only `tasks/plans/INDEX.md` was edited). The citations
still resolve — the files moved to `archive/story/`, they were not deleted — but the paths are
now under `docs/archive/`. Listed here for transparency.
