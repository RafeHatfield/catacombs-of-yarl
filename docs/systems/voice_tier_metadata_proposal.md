# Voice Tier Metadata — PROPOSAL (draft for owner ruling)

Status: **PROPOSAL ONLY.** This document is a justified draft of the voice-scheduler tier
metadata. The YAML fenced below is *illustrative* — it is deliberately **not** a live
`config/*` file the loader reads. Tier rulings are the owner's design decisions; several
choices below are blocked on an unmade contract ruling (see **RULINGS NEEDED**).

Scope: every schedulable trigger family across `config/voice_lines/hollowmark.yaml`,
`quipping_shade.yaml`, and `possession.yaml`. Explicitly out of scope (not turn-triggered
ribbon families): `weighing_audit.yaml` (scripted endgame scene), `catalog_past_selves.yaml`
(render templates), `marya_fragments.yaml` (not loaded by `VoiceLineRegistry`), and
`between_runs.*` (results-screen selector — see Excluded).

---

## 1. Verified scheduler substrate (the mechanics every tier field drives)

Every claim below is cited to source. Justifications in §3 reference these.

- **Highest tier wins; ties broken by declaration order (lower `Order` wins).**
  `VoiceScheduler.cs:127` — `best == null || meta.Tier > best.Tier || (meta.Tier == best.Tier && meta.Order < best.Order)`.
- **`Order` is the YAML list index assigned at load, NOT an authored field.**
  `VoiceTierMetadata.cs:62-67` (loop index `i` passed as `Order`), record `VoiceTierMetadata.cs:92`.
  So the *sequence* of the `families:` list is the tie-break; there is no `order:` key to author.
- **`AmbientCutoffTier` — in Tactical mode, families with `tier <= cutoff` are skipped (hidden).**
  `VoiceScheduler.cs:121` — `if (mode == VoiceMode.Tactical && meta.Tier <= _meta.AmbientCutoffTier) continue;`.
  Survivors are those **strictly above** the cutoff (`VoiceMode.cs:13`). Verbose renders all
  tiers (`VoiceMode.cs:11`); Silent renders nothing (`VoiceScheduler.cs:111`).
- **`once_per_run` — skip if the family key is already in the fired-set; burn on delivery.**
  Skip: `VoiceScheduler.cs:122` — `if (meta.OncePerRun && _fired.Contains(meta.Key)) continue;`.
  Burn: `VoiceScheduler.cs:140` — `if (best.OncePerRun) _fired.Add(best.Key);`.
  **The fired-set is keyed on the metadata key (`best.Key`), not on the resolved line or any
  sub-key.** So `once_per_run` on a *coarse* key fires at most once per run **for the whole
  family**, collapsing every sub-variant into a single lifetime fire.
- **`cooldown_exempt` — bypasses the 3-turn inter-line cooldown.**
  `VoiceScheduler.cs:133` — `if (!best.CooldownExempt && (long)currentTurn - _lastDeliveredTurn < CooldownTurns) return null;`.
  `CooldownTurns = 3` (`VoiceScheduler.cs:36`).
- **THE ONE RULE: non-delivery consumes nothing.** Every gate returns `null` *before* the
  consume block: Silent/floor-silence/surface (`VoiceScheduler.cs:111-113`), nothing eligible
  (`:130`), cooldown (`:133`), ribbon supersede (`:136`). Consumption (bag draw, one-shot burn,
  cooldown stamp, history push) happens only at `VoiceScheduler.cs:138-145`. Invariant doc'd at
  `VoiceScheduler.cs:19`.
- **Ribbon supersede — a new line lands only if strictly higher tier than what is showing.**
  `VoiceScheduler.cs:136` — `if (currentRibbonTier is int shown && best.Tier <= shown) return null;`
  (contract `voice_delivery.md:38`). This makes the *relative ordering* of tiers matter for
  on-screen behavior, not just the numbers.
- **`VoiceTierMetadata.Get` is an EXACT ordinal dictionary lookup — NO compound-key fallback.**
  `VoiceTierMetadata.cs:44` (`_byKey` built with `StringComparer.Ordinal`), `:48-49`
  (`_byKey.TryGetValue(...)`). A family key with no exact metadata entry returns `null` and is
  dropped as "unknown / not schedulable" (`VoiceScheduler.cs:120`).
- **`VoiceLineRegistry.GetPool` DOES compound-fallback** (`a.b.c → a.b → a`).
  `VoiceLineRegistry.cs:80` → `Resolve` `:84-97`.
- **Eligibility resolves the pool from the *emitted* string; the draw resolves from the
  *metadata key*.** `VoiceScheduler.cs:123` — `_registry.GetPool(family)`; `:139/:158` —
  `DrawFromBag(best.Key)` → `GetPool(best.Key)`. Because `Get` is exact-match, `best.Key`
  always equals the emitted `family`, so the two are the same string. **Net constraint: the
  metadata key must equal the string the emitter passes to `TryDeliver`, verbatim, AND
  `GetPool(thatString)` must resolve to a non-empty pool.**
- **What the emitter emits today (M1.5b stub).** `VoiceTriggerReader.Read` raises exactly five
  COARSE strings: `hp_critical` (`:44`), `possession` (`:49`), `trap` (`:55`), `idle` (`:58`),
  `species_first_sight` (`:68`). It edge-triggers / dedupes internally: hp once per descent,
  re-arming on recovery (`:41-45`); possession once per entry (`:47-49`); trap & idle per-event
  (`:53-58`); species once per species per run via `_seenSpecies` (`:23`, `:60-68`).
- **Initial priority ranking** (`voice_delivery.md:12-14`):
  hp-critical > possession > boss/named > species-first-sight > traps/hazards > items/economy > idle.

**The blocking consequence:** the five strings the emitter emits today are all coarse, but the
pools are fine-grained (`hp_threshold.25`, `species_first_sight.orc`, `possession_enter`,
`trap_first.spike_trap`, `long_idle`) with **no coarse base pool** for any of them.
`GetPool("hp_critical")`, `GetPool("possession")`, `GetPool("trap")`, `GetPool("idle")`,
`GetPool("species_first_sight")` all return `null` today (no exact key; and `Resolve` only enters
its fallback loop when the string contains a `.`, `VoiceLineRegistry.cs:90` — none of these do).
So **zero families are actually deliverable right now**, regardless of metadata. This is Ruling 1
and it gates the whole file.

---

## 2. Proposed metadata (illustrative — contingent on Ruling 1)

Keys below are the **coarse family identifiers** — the granularity at which tiering is
meaningful (you tier "HP is critical" as one concept, not each of `.25/.10/.1`). They assume
Ruling 1 resolves so that `GetPool(<coarse key>)` and `Get(<coarse key>)` both hit (either by
adding coarse base pools, or by giving `Get` the same compound fallback `GetPool` has — see
RULINGS). `families:` order is high→low for readability; order only matters as the tie-break.

```yaml
# ILLUSTRATIVE — not loaded by the engine. Contingent on Ruling 1 (emitter/pool-key contract).
ambient_cutoff_tier: 25   # Tactical renders only tier > 25 (see §4)

families:
  # ── danger / threat: survive Tactical ──
  - key: hp_critical           # pools: hp_threshold.25/.10/.1
    tier: 70
    cooldown_exempt: true      # ranking #1; top tier is cooldown-exempt
  - key: possession            # pools: possession_enter(+.orc/.undead/.troll/...)
    tier: 60
  - key: species_first_sight   # pools: species_first_sight.<species>
    tier: 40
  - key: spell_break_used      # pool: spell_break_used  (forward — emitter unbuilt)
    tier: 35
  - key: trap                  # pools: trap_first.<type> (+ own_trap quip)
    tier: 30
  # ── flavor / ambient: cut in Tactical ──
  - key: kill_streak_clean     # pool: kill_streak_clean  (forward — emitter unbuilt)
    tier: 25
  - key: item_identified       # pools: item_identified.<category>  (forward — emitter unbuilt)
    tier: 20
  - key: overnight_identified  # pool: overnight_identified  (mechanic + emitter unbuilt)
    tier: 20
  - key: region_first_entry    # pools: region_first_entry.<region>  (forward — emitter unbuilt)
    tier: 15
  - key: idle                  # pool: long_idle
    tier: 10
```

**Note the total absence of `once_per_run: true`.** That is intentional and justified in §3.

---

## 3. Per-family justification

Each row ties the tier/flags to (a) the `voice_delivery.md` ranking and (b) actual scheduler
behavior with citations.

| key | tier | flags | Justification |
|-----|------|-------|---------------|
| `hp_critical` | 70 | `cooldown_exempt: true` | Ranking #1 (`voice_delivery.md:12-14`). Top tier so it always wins the highest-tier resolution (`VoiceScheduler.cs:127`) and can supersede anything on the ribbon (`:136`). Exempt per the contract "the top tier (hp-critical) is exempt" (`voice_delivery.md:15-16`), realized at `VoiceScheduler.cs:133` — a death-spiral warning must fire even inside the 3-turn window. `once_per_run` **false**: the emitter re-arms per descent below threshold (`VoiceTriggerReader.cs:41-45`); a `true` flag would burn the key on first fire (`:140`) and suppress every later crisis for the rest of the run. |
| `possession` | 60 | — | Ranking #2 (`voice_delivery.md:12-14`). Sits below hp so a possession quip never masks a lethal-HP warning on the ribbon (`VoiceScheduler.cs:127,136`). `cooldown_exempt` **false**: only hp-critical is exempt (`voice_delivery.md:15-16`); a possession line waiting out the 3-turn cooldown (`:133`) is acceptable. `once_per_run` **false**: emitter fires once per *entry* and re-arms on exit (`VoiceTriggerReader.cs:47-49`); a `true` flag collapses all possessions in a run to a single line. |
| `species_first_sight` | 40 | — | Ranking #4 (`voice_delivery.md:12-14`). Above traps, below possession. `once_per_run` **false — deliberately, and contrary to the schema's illustrative example** (`VoiceTierMetadata.cs:26-27` shows it `true`). Per-species dedup already lives in the emitter (`_seenSpecies`, `VoiceTriggerReader.cs:60-68`), so the emitter only raises the family on genuinely-new-species turns. Because the fired-set is keyed on the *coarse* metadata key (`VoiceScheduler.cs:140`), `once_per_run: true` would fire for the **first species ever seen** and silence every subsequent species — the opposite of the intent. Leave it false and let the emitter own dedup. (If the owner instead wants scheduler-side dedup, that requires fine keys + per-species metadata — see RULINGS.) |
| `spell_break_used` | 35 | — | Not in the ranking (forward-authored pool, `hollowmark.yaml:329-356`; emitter unbuilt). Combat-relevant feedback, so placed above ambient flavor and just under species. Kept above the ambient cutoff so it survives Tactical (§4). `once_per_run` **false**: dispels recur; per-event. `cooldown_exempt` **false** (only hp is exempt). |
| `trap` | 30 | — | Ranking "traps/hazards", #5 (`voice_delivery.md:12-14`). `once_per_run` **false**: per-event by design ("Trap and idle are per-event", `VoiceTriggerReader.cs:13`; emitter `:53-55`). Pools are first-of-type (`trap_first.*`) so repetition is already bounded by content, not by the scheduler. Kept just above the cutoff (hazard awareness is tactical) — a judgment call flagged in §4. |
| `kill_streak_clean` | 25 | — | Not in ranking (forward pool `hollowmark.yaml:118-126`, capped ≤3/run in the emitter per the comment; emitter unbuilt). A flourish, not tactical — placed **at** the cutoff so it is cut in Tactical (§4). `once_per_run` **false** (fires up to 3×/run). |
| `item_identified` | 20 | — | Ranking "items/economy", #6 (`voice_delivery.md:12-14`). Forward pools `hollowmark.yaml:191-239`; emitter unbuilt. `once_per_run` **false**: many items are identified per run. Below cutoff → ambient. |
| `overnight_identified` | 20 | — | Same economy bucket; mechanic explicitly unimplemented (`hollowmark.yaml:241`). Same tier/flags rationale as `item_identified`. Included for completeness; gated on the mechanic existing. |
| `region_first_entry` | 15 | — | Not in ranking (forward pools `hollowmark.yaml:58-78`; needs a region system to emit). Exploration flavor. `once_per_run` **false**: like species, dedup is per-*region* and must live in the emitter; a coarse `true` flag would fire for the first region only (`VoiceScheduler.cs:140`). Below cutoff → ambient. |
| `idle` | 10 | — | Ranking #7, the floor (`voice_delivery.md:12-14`). Lowest tier so any other trigger supersedes it (`VoiceScheduler.cs:127,136`). `once_per_run` **false**: per-event, ≤3/run bounded by content (`VoiceTriggerReader.cs:13`, `:57-58`). Below cutoff → ambient. |

**Why no family is `once_per_run: true`.** The genuinely once-ever content (run milestones,
`hollowmark.yaml:362-372`) lives under `between_runs.*`, which is a results-screen family
excluded from the turn ribbon (see Excluded). Every turn-ribbon family either recurs by design
or is deduped *inside the emitter* (per descent / per entry / per species / per region /
count-capped). Since the scheduler's fired-set keys on the coarse metadata key
(`VoiceScheduler.cs:140`), a coarse `once_per_run: true` is not "fire each variant once" — it is
"fire the whole family once per run," which is wrong for all of these. So the flag stays off
across the board. (This is a finding worth the owner's eye: the schema example at
`VoiceTierMetadata.cs:26-27` is misleading on exactly this point.)

---

## 4. `ambient_cutoff_tier` proposal: **25**

Semantics: Tactical mode skips families with `tier <= AmbientCutoffTier`
(`VoiceScheduler.cs:121`); only `tier > 25` survives (`VoiceMode.cs:13`).

With cutoff 25:

- **Survive Tactical (tier > 25):** `hp_critical` (70), `possession` (60),
  `species_first_sight` (40), `spell_break_used` (35), `trap` (30). These are the
  danger / threat-assessment / combat families — the information a player in "tactical, cut the
  chatter" mode still needs.
- **Cut as ambient (tier <= 25):** `kill_streak_clean` (25), `item_identified` (20),
  `overnight_identified` (20), `region_first_entry` (15), `idle` (10). Flourish, economy, and
  exploration flavor — the chatter Tactical is meant to suppress.

This matches the ranking's implicit split: the ranking's top buckets (hp, possession,
boss/named, species, traps/hazards) are combat/threat; "items/economy" and "idle" are the tail
(`voice_delivery.md:12-14`). Cutoff 25 draws the line exactly there.

**Owner call flagged:** whether `trap` (30) should survive Tactical is the one debatable
inclusion — first-of-type trap lines are half warning, half flavor. Moving the cutoff to 30
would cut `trap` too (tier 30 <= 30). Recommend keeping trap in (hazard awareness is tactical),
but it is a one-line change if the owner disagrees.

---

## RULINGS NEEDED

### Ruling 1 (headline, blocking) — the emitter → pool-key granularity contract
`VoiceTierMetadata.Get` is exact-match (`VoiceTierMetadata.cs:48-49`); `VoiceLineRegistry.GetPool`
is compound-fallback (`VoiceLineRegistry.cs:84-97`); the emitter emits **coarse** strings
(`VoiceTriggerReader.cs:44,49,55,58,68`); the pools are **fine-grained with no coarse base**
(`hp_threshold.25`, `species_first_sight.orc`, `possession_enter`, `trap_first.spike_trap`,
`long_idle`). Result **today**: `GetPool("hp_critical")` / `("possession")` / `("trap")` /
`("idle")` / `("species_first_sight")` all return `null`, so every emitted family is dropped at
`VoiceScheduler.cs:124` and **nothing is deliverable**. The correct metadata granularity depends
on which fix the owner picks:

- **Option A — coarse everywhere (add base pools).** Author a coarse base pool per family
  (`hp_threshold:`, `possession:`, `trap:`, `idle:`, `species_first_sight:`) in the YAML. Metadata
  keys stay coarse (as proposed in §2). Cost: the fine sub-pools (`.orc`, `.spike_trap`, …) become
  unreachable from the scheduler path (the emitter emits coarse, `GetPool` hits the base pool
  first), so all that bespoke per-species/per-trap writing goes dark unless the emitter is also
  changed to emit fine.
- **Option B — fine emit + compound metadata (code change).** Change the emitter to emit fine
  keys (e.g. `species_first_sight.orc`, `hp_threshold.25`) and give `VoiceTierMetadata.Get` the
  same compound fallback `GetPool` already has, so `Get("species_first_sight.orc")` resolves to a
  coarse `species_first_sight` metadata entry. Metadata stays coarse (as §2); fine pools stay
  reachable. Cost: an engine change to `VoiceTierMetadata` (out of scope for this proposal) plus
  emitter rework. **This is the cleanest — it makes metadata symmetric with the registry.**
- **Option C — fine emit + fine metadata.** Emitter emits fine keys; author one metadata entry
  per fine key (26 species, 9 traps, …). Cost: enormous, duplicative metadata, and tiering
  becomes per-variant when the design wants per-family. Not recommended.

The §2 YAML is written for **Option A or B** (coarse keys). If the owner picks C, the file must
be re-keyed. **This ruling must land before any of §2 is real.**

### Ruling 2 — the "boss/named" tier has no pool
The ranking names **boss/named** at #3 (`voice_delivery.md:12-14`), but no shipped pool emits a
`boss`/`named` family. The nearest content is folded elsewhere: named hosts under
`possession_enter.hall_warden` / `.bone_orc` (`possession.yaml:31,52`) and elite species under
`species_first_sight.orc_chieftain` / `.lich` (`hollowmark.yaml:154,168`). Options: (a) author a
dedicated `boss_encounter` / `named_sighted` family + emitter hook and slot it at tier 50; (b)
declare boss/named an alias that resolves through possession/species and drop it from the tier
list. No family is proposed for it here pending the ruling.

### Ruling 3 — "items/economy" is only half-covered
The ranking's **items/economy** bucket (#6) maps to `item_identified.*` and `overnight_identified`
(proposed, tier 20), but there is **no economy pool at all** (no shop/gold/theft turn family;
`between_runs.survived.theft/swap` is results-screen, not turn ribbon). Ruling: is a live
economy-event family in scope for M1.5, or is "economy" satisfied by the results-screen lines? If
in scope, it needs pools + an emitter + a tier.

### Ruling 4 — `on_death.*` surface + tier
`on_death.*` and the `on_death` fallback (`hollowmark.yaml:263-327`) are death commentary. Unclear
whether these route through the *turn ribbon* (the scheduler) or the death/results screen. If
ribbon: a death fires on a terminal turn — does it even get a turn-commit to emit on, and should
it be top-tier (above hp)? If results screen: exclude like `between_runs.*`. No tier proposed
pending this.

### Ruling 5 — possession sub-events (drain / exit / threatened / wand-kicked)
`possession.yaml` carries distinct trigger families beyond enter: `possession_drain_warning_25/50/75`
(`:64-77`), `possession_exit_voluntary/host_death/out_of_range` (`:79-92`),
`possession_home_body_threatened` (`:94`), `possession_wand_kicked` (`:99`). The emitter emits only
`possession` (on enter, `VoiceTriggerReader.cs:47-49`) — none of these are raised yet, and each is
its own exact top-level key with **no coarse base**, so none can be tiered as one family without
either per-key metadata or a base pool (same shape as Ruling 1). Design note for the owner:
`possession_drain_warning_75` and `possession_home_body_threatened` read as **danger-tier** (near
hp_critical), not flavor — they should probably sit high (55–65) and survive Tactical. Needs an
emitter contract + tier ruling.

### Ruling 6 — `past_sasha_encounter.*` and the self-hazard quips
- `past_sasha_encounter.*` (`hollowmark.yaml:1-34`) is a scripted multi-beat story encounter
  (looted-body → shade → possessed-corpse → spell-break). Is it scheduler-routed (needs an
  emitter + tier) or a scripted scene like `weighing_audit.yaml` (excluded)? If routed, it is
  named/story content and likely high tier.
- The `quipping_shade.yaml` self-hazard quips (`oil_slick_fire`, `possession_neglect`,
  `own_poison`, `own_trap`, `fall_damage`, `acid`, `possessed_wrong_host`,
  `hollowmark_out_of_range`) are self-inflicted-mishap commentary. `own_trap` overlaps the `trap`
  family; the rest have no emitter and no coarse base. Ruling: fold these into a single
  `self_hazard` family (one base pool + one tier, ~trap level) or leave them as bespoke keys? As
  bespoke keys they are unschedulable for the Ruling 1 reason.

---

## Excluded families (not turn-triggered ribbon content)

| Family / file | Reason |
|---------------|--------|
| `between_runs.*` (`hollowmark.yaml:362-436`) | Results-screen selector (`between_runs_conditioning.md`, "Selector unbuilt", `hollowmark.yaml:358-360`). Milestones/deaths/survival are chosen on the between-runs screen, not the turn ribbon; the `run_N` milestone "key = fired-set line id" note (`:360`) is `VoiceLineRegistry` first-fire semantics, not scheduler `once_per_run`. |
| `weighing_audit.yaml` | Scripted endgame scene (per task brief). |
| `catalog_past_selves.yaml` | Render templates, not turn triggers. |
| `marya_fragments.yaml` | Not loaded by `VoiceLineRegistry`. |

---

## Completeness ledger (every top-level pool group dispositioned)

No schedulable family is silently omitted. `hollowmark.yaml`:
`past_sasha_encounter.*` → Ruling 6; `hp_threshold.*` → `hp_critical` (§2); `region_first_entry.*`
→ `region_first_entry` (§2); `trap_first.*` → `trap` (§2); `kill_streak_clean` → §2; `long_idle`
→ `idle` (§2); `species_first_sight.*` → `species_first_sight` (§2); `item_identified.*` →
`item_identified` (§2); `overnight_identified` → §2; `on_death.*` / `on_death` → Ruling 4;
`spell_break_used` → §2; `between_runs.*` → Excluded.
`quipping_shade.yaml`: all eight self-hazard keys → Ruling 6 (`own_trap` also overlaps `trap`).
`possession.yaml`: `possession_enter(+.*)` → `possession` (§2); `possession_drain_warning_*`,
`possession_exit_*`, `possession_home_body_threatened`, `possession_wand_kicked` → Ruling 5.

All contingent on Ruling 1 for actual deliverability.
