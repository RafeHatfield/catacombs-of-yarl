# Voice trigger alignment — STOP-FLAG (Phase 2, needs ruling)

**Status:** blocked on a Foundation+Voice design ruling. The E fix (PRs #93/#94) makes the ribbon
render on device, but only the `[DEV]` fixture pools deliver. Wiring the *real* voice is blocked by a
three-way key mismatch documented here. **No fix improvised; the `[DEV]` fixture is NOT deleted** (doing
so now would return the ribbon to silent, because the real pools would not resolve).

## The real taxonomy (enumerated from config/voice_lines/, do not invent)

The authored Hollowmark pools use **compound, specific keys**, e.g.:

| Family (prefix) | Example authored pool keys |
|---|---|
| `hp_threshold` | `hp_threshold.25`, `.10`, `.1` |
| `species_first_sight` | `species_first_sight.orc_grunt`, `.troll`, `.lich`, … (per species) |
| `trap_first` | `trap_first.spike_trap`, `.fire_trap`, `.acid_trap`, … (per type) |
| `region_first_entry` | `region_first_entry.boundary`, `.dimhalls`, … |
| `on_death` | `on_death.orc_grunt`, …, `on_death.hazard`, `on_death` |
| `item_identified` | `item_identified.potion`, `.scroll`, `.wand`, `.ring` |
| `past_sasha_encounter` | `past_sasha_encounter.looted_body`, `.possessed_corpse.pre_spell_break`, … |
| `long_idle`, `kill_streak_clean`, `overnight_identified`, `spell_break_used` | (flat) |
| `possession_enter` (possession.yaml) | `possession_enter.orc`, `.undead`, `.troll`, … |
| `possession_drain_warning_25/50/75`, `possession_exit_*`, `possession_home_body_threatened` | (flat) |
| `between_runs` | `between_runs.milestone.run_1`, `between_runs.died.undead`, … |

## The three-way mismatch

1. **Trigger reader emits BARE placeholder families** — `VoiceTriggerReader` returns `hp_critical`,
   `possession`, `species_first_sight`, `trap`, `idle`. None of these is an authored pool key
   (`hp_threshold.*`, `possession_enter.*`, `species_first_sight.<species>`, `trap_first.<type>`,
   `long_idle`). `VoiceLineRegistry.GetPool` only strips segments downward, so a bare `species_first_sight`
   does **not** resolve to `species_first_sight.orc_grunt`. → no pool → nothing delivers.
2. **The scheduler uses ONE key for tier AND pool.** `_meta.Get(family)` is an exact lookup and
   `_registry.GetPool(family)` needs the specific pool key. A per-family tier ("`species_first_sight`
   → 50") cannot coexist with per-species pools unless the scheduler resolves the tier by compound
   prefix while resolving the pool by the specific key.
3. **Result:** even a perfectly authored `voice_tiers.yaml` would not deliver the real voice until 1+2
   are reconciled.

## Proposed resolution (for the ruling — pick one, then I implement + regression-guard)

**Option A (recommended): specific keys + prefix-tier resolution.**
- Reader emits the *specific* key it can derive: `species_first_sight.<typeId>`, `trap_first.<trapType>`,
  `hp_threshold.25|10|1` (by band), `possession_enter.<hostClass>`, `long_idle`, `on_death.<typeId>`, …
- Scheduler resolves the **tier** by the same compound-prefix fallback `GetPool` already uses (so the
  tier file stays concise — one entry per family *prefix*), and resolves the **pool** by the specific key.
- `voice_tiers.yaml` lists family prefixes with tiers per the ruled priority (below).

**Option B: fully-specific tier file.** Tier file enumerates every specific key. Verbose, brittle as
content grows, and still needs the reader to emit specific keys. Not recommended.

Either way the reader must be taught to emit specific keys (species typeId, trap type, HP band, host
class) — a Presentation trigger-derivation change, headlessly testable against `VoiceTriggerReader`.

## Proposed tier priorities (Voice-thread review pending — ruled ordering, extended)

hp_threshold (exempt) > possession_home_body_threatened / possession_drain_warning > possession_enter >
past_sasha_encounter / spell_break_used (named/artifact) > species_first_sight > trap_first > on_death /
kill_streak_clean > region_first_entry > item_identified / overnight_identified > long_idle. `between_runs`
fires outside a run (own path). Exact integers + the ambient cutoff are a Voice-thread register call.

## Not done here (deliberately)
- `voice_tiers.yaml` not authored as a functional file (the scheme is unruled — a wired file under the
  wrong scheme would mislead).
- `VoiceTriggerReader` / scheduler unchanged.
- The `[DEV]` fixture block in `Main` **kept** — it is what currently delivers; deleting it before the
  real path works would re-silence the ribbon (regression). Delete it in the same change that wires
  real delivery, per §voice_delivery.md.
