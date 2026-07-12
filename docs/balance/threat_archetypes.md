# Threat Archetypes & Composition Targets (Step 0b)

_Last verified: 2026-07-12 against commit 86b6f10_

**Status:** **LOCKED 2026-06-08** (reviewed and blessed by Rafe). This is the definition of "balanced"
for the game. Verdicts and the assertion list refine as balance walks the regions; the *shape* is fixed.
All §7 decisions resolved. Migration-loss triage referenced in §8 lives in `migration_loss_audit.md`.

**Companion to:** `docs/balance/balance_strategy.md` (this is the Step-0b deliverable referenced
in Part 2's sequence — it replaces the single per-region ttk/ttd target table).

**Provenance rule (decide-on-merits):** each archetype's intended profile is decided on its own
design merits FIRST; reality is then measured as a distance from that profile. We do not rewrite
intent to match what the game currently does. (This is the failure that let the PressureModel bands
"ratify the grind.")

**Bot-as-proxy boundary:** every target here is tuned against bot personas in headless soaks. Bots
don't panic, misread threats, or get greedy. This system tunes against the proxy; human playtest is
the ground truth the bots approximate, validated later — not built now. Named here so it isn't
forgotten.

---

## 1. The feel model (0a)

Combat feel is a **durable baseline with deliberate lethal exceptions** — not a global durable-vs-lethal
point on a line. The durable baseline is the canvas; sharp exceptions only read as meaningful *because*
the baseline is durable. If everything is lethal, nothing is special; if everything is durable, it's grind.

This texture is also the **design engine for the toolkit**:
- The **durable baseline** gives possession, factions, and wand-of-portals a many-body battlefield to
  operate on (their natural habitat).
- The **lethal exceptions** create the *demand* to use those tools cleverly — you can't tank the lich,
  so you turn the orcs against it / possess a soak / portal past it.

Exceptions come in **two kinds**:
- **Intrinsic spikes** — sharp by nature, can't be tanked, demand a tactic change, but are **counterable**.
- **Escalators** — transform the baseline swarm from manageable attrition into a *solve-it-now* problem.
  They create **target-priority puzzles** and live in **composition**, not in individual stat blocks.

---

## 2. Archetype sorting (reconciled against code)

| Archetype | Monsters | Notes from code reconciliation |
|---|---|---|
| **Baseline (durable)** | orc, orc_brute, orc_veteran, orc_scout, orc_skirmisher, skeleton, zombie, *cultist_blademaster*, *cave_spider/web_spider*, *giant_spider*, *fire_beetle* | brute = high-end durable beatstick (tier-defining, never nerf). **skeleton is a *textured* baseline** — `skeleton` AI + ShieldWall + bludgeoning-vuln (bring a club/mace). cultist_blademaster = **hot baseline** (§6 Q1). **Textured baselines (reclassified 2026-06-09): cave_spider/web_spider, fire_beetle, giant_spider** — a status proc on a weak beast (poison/slow/burn) is TEXTURE, not a spike; tank it + account for the status. giant_spider hits hard (4-8) but low HP makes it tankable — high damage alone = hard baseline (brute precedent), not spike. Swarm = density lever; extra-attack speed = frequency lever. |
| **Intrinsic spike** | wraith, troll/troll_ancient, lich (also escalator → Fused) | **Tightened definition (2026-06-09): SPIKE = genuinely can't-tank, must-change-approach.** troll (regen → need acid/fire), wraith (life drain + 2× attack speed → burst or avoid), lich Soul Bolt (cancel by killing mid-channel). Status-on-a-weak-beast does NOT qualify — that's textured baseline (see Baseline row). Keeps "died fast to a spike" meaningful: a genuinely sharp threat, not a poison tick. |
| **Escalator** | orc_chieftain, orc_shaman, necromancer, plague_necromancer, large_slime, greater_slime | All mechanics WIRED to affect other entities (rally buffs allies, necro raises real allies, split spawns real children). Two divergences: plague_necro does NOT raise plague_zombies (raises in-place +25% HP + tag); necro hazard-avoidance not implemented (counter, not the escalator mechanic). |
| **Fused** | lich | Soul Bolt (spike) + Command-the-Dead (+1 to-hit aura) / Death Siphon / Raise (escalator). |

**Spawn-mode correction (doc was wrong):** the only truly weight-0/encounter-only monsters are
`orc_grunt`, `orc_scout`, `orc_veteran`, `orc_chieftain`. **Slimes are live random spawns** from
depth 2/3/12 (their `spawn_weight: 0` is shadowed by `depth_weights`). `orc_skirmisher`/`orc_shaman`
reach play procedurally via `OrcVariantResolver`, not direct weight.

---

## 3. Role-profile target table (role is the PRIMARY axis; region scales each)

| Role | ttd (turns to down player, 1v1) | ttk | Danger model | Tuned by | Verdict shape |
|---|---|---|---|---|---|
| **Baseline** (durable) | High — survive many hits | Moderate | Aggregate / attrition | density + composition | 1v1 = easy; threat = numbers |
| **Intrinsic spike** (lethal, counterable) | Low — downs you fast if ignored | varies | Demands a tactic change | **the counter's accessibility at its depth** | w/o counter = lethal; w/ counter = winnable |
| **Escalator** (multiplier) | **N/A** — not ttd-tuned | varies | Transforms the swarm | **multiplier × response window** | swarm alone = winnable; swarm+escalator = too-much *unless neutralized in the window* |
| **Fused** (lich) | Low (Soul Bolt) | high | Both | both | both assertions must hold |

Numbers in the strategy doc's Part-4 mockup are supposition; they get set per-region during tuning,
decided on merits.

---

## 4. Composition-assertion table (the UNIT of balance)

Verdict is evaluated at **baseline gear**. An escalator is tuned correctly when adding it **flips the
verdict**. `Coverage` = is there a scenario to measure it today. `Status` = is it tunable now or
gated on a fix/decision/content.

| # | Composition | Region | Intended verdict | Lever that flips it | Coverage | Status |
|---|---|---|---|---|---|---|
| A | 4 orc grunts | B1 | Winnable | baseline density | ✅ scenarios | **tunable now** |
| B | 4 grunts + 1 chieftain | B1 | Too-much unless chieftain killed in window | rally multiplier (+1/+1, ends on attack dmg) | ✅ `scenario_orc_chieftain_identity` | **tunable now** |
| C | 3 grunts + 1 shaman | B1 | Too-much unless chant interrupted / silenced | turn-skip lock | ✅ identity scenarios | **tunable now** |
| D | 1 troll, no acid access | B1 | Lethal-by-attrition (intended) | — | ✅ `scenario_troll_identity` | **tunable now** (fairness depends on E) |
| E | 1 troll + accessible acid/fire | B1 | Winnable | the counter, made reachable at depth | ❌ | `blocked-on-fix` — fix chosen: **B1 loot-pool acid/fire source** (§5.2) |
| F | skeleton trio, piercing weapon | B2 | Marginal/slow; bludgeoning weapon → winnable | weapon damage-type (club/mace early) | ✅ `scenario_skeleton_shieldwall_identity` | **tunable now** |
| G | slime + large_slime swarm | B3 | Too-much if single-target-chipped; winnable via AoE / kill-from-range | AoE (kills children as fast as they spawn); split is bounded (children don't re-split) | ❌ no authored composition | design settled (§7 D2); **content gap** (author the composition) |
| H | necro + skeleton swarm | B2/3 | Endless unless necro reached & killed | reach window | ✅ `scenario_necromancer_identity` | **tunable now** |
| I | spike + faction-turn (e.g. wraiths vs lich) | B3–B5 | Winnable via turning monsters on the spike | aggravation / faction-turning | ❌ | `blocked-on-fix` (aggravation rewire, §5.1) — *hours away* |
| J | lich + undead court | B5 | Both spike + escalator hold | Soul-bolt cancel + reach + faction-turn | ❌ no authored composition | `blocked-on-fix` + content gap |

**Report health (0c) reads WHICH failure mode occurred:** died grinding = baseline OK · died fast to a
spike = spike OK · died fast to a baseline orc = baseline BROKEN · spike was a pushover = spike BROKEN ·
ignored escalator with no consequence = escalator BROKEN · couldn't reach escalator in time = escalator
UNFAIR.

---

## 5. Counter-web reconciliation & the fix/drop calls

What's wired (counters that work today): troll regen suppressed by acid OR fire; skirmisher leap blocked
by Entangle (and **`root_potion` is an in-loot Entangle source** — net arrows are NOT in the loot pool);
shaman chant interrupted by any attack damage / blocked by Silence (`scroll_of_silence`, depth 1+);
chieftain rally ends on attack damage to chieftain (DOT-safe); lich Soul Bolt cancelled by killing it
mid-channel; skeleton/zombie resist piercing & take double from bludgeoning; possession + wand-of-portals
both work. Control suite exists: glue/slow/fear/confusion, dragon_fart sleep cone, taunt.

### The five calls (folded in):

**5.1 Aggravation / faction-turning — FIX (RESTORE, not build). Track 2, but cheap.**
PoC investigation confirms: faction system is fully ported; only the `_check_enraged_against_faction`
override wire was lost. ~25–40 lines in `ChooseTarget` (model on existing `EnragedEffect` branch +
PoC `basic_monster.py:844`), plus tests + a scenario that exercises an aggravated monster. PoC parity
extras (player faction-choice + resistance table) optional, a few more hours. **Reclassified from
"biggest gap / real build" → trivial rewire.** Can land alongside B1–B2 rather than racing B4/B5.

**5.2 Troll counter-access — FIX: add an accessible acid/fire source to the B1 loot pool.** Troll spawns
at depth 4 (B1); today the only in-economy acid/fire source is the self-damaging acid_trap weapon-coating
path (fire_trap is depth-6-gated, fire/net arrows aren't in the loot pool, monsters can't be lured onto
traps). **Chosen fix (of the three options): the loot-pool one** — because of the troll's *pedagogical
job*. The troll is the player's first "you cannot tank this, find the counter" lesson, and that lesson
only lands if the counter is findable in the world right where the troll appears. Moving the troll deeper
delays the lesson; another counter-form is more work; a findable acid/fire source at B1 teaches the
interaction layer at the exact moment the player first meets a counterable spike. So: put a reliable,
discoverable acid or fire source in the B1 loot economy (not the acid_trap path, not depth-6-gated, not
out-of-pool). The troll's fairness *is* its counter-availability at depth.

**5.3 Slime burst-overkill — RESOLVED: keep PoC (split always wins).** See §7 D2. Overturning re-introduces
the narrow-band bug the precedence rule was built to prevent. Slime counter is AoE / kill-from-range / material.

**5.4 slime → acid → troll easter egg — RESOLVED: BUILD, downside-with-upside.** See §7 D1. Slime corrosion
also applies the existing acid-coating (suppresses troll regen) on every slime-weapon contact; the DamageMax
degrade stays the metal-only chance roll. No new acid system.

**5.5 Necromancer fire-zoning — DEFER, but reframed.** Necromancer already has a working counter (reach &
kill it). Hazard-zoning is a missing *second* counter. PoC investigation reframes it: hazard-avoidance was
a **general** mature PoC feature (weighted-cost in the shared movement primitive, all monsters), lost in
migration — so restoring it is a general AI-fidelity restoration, not a necro feature. Your defer-condition
("unless cheap and useful for other monsters") is technically met. Still lower priority than 5.1; re-decidable.

---

## 6. The four intent-vs-implementation questions

1. **cultist_blademaster — hot baseline; live-but-orphaned.** spawn_weight 6 @ depth 12, so it *can* spawn
   via the procedural pool, but it's in ZERO authored scenarios. At 6–10 dmg with `basic` AI and no
   mechanic, it's the "feels like a spike, plays like a baseline = broken baseline" case. Recommendation:
   don't cut it — give it a real role (a mechanic, or an authored encounter), don't leave it an untested
   depth-12 filler.
2. **Troll fairness — counter NOT reliably available at depth 4.** See 5.2.
3. **spawn_weight 0 → authored composition — confirmed, sharper:** no procedural floor builds an authored
   swarm+escalator; composition assertions live only in scenarios. Deep-tier (slime escalators, ancient
   troll, wraith, lich) has ZERO authored composition. Composition assertions ARE the encounter-design work.
4. **slime → acid → troll — does not currently exist** (corrosion is pure DamageMax degrade, explicitly
   non-interacting with acid coating). Build path in 5.4.

---

## 7. Slime escalator counter-design (D1/D2 — RESOLVED)

- **D1 — slime-acid tradeoff: RESOLVED → downside-with-upside; coating on EVERY contact (decoupled).**
  The DamageMax degrade stays unchanged (per-hit *chance*, 5/10/15% by tier, metal main-hand only). The
  acid-coating applies on **every** slime-weapon contact — **decoupled** from the chance-based degrade proc.
  Reasoning: if the coating itself were a 5% proc, almost nobody connects "slimed sword → troll-killer", and
  the **discoverability IS the easter egg** — chance-gating it kills the thing worth having. Decoupling is
  also what lets a future non-metal/acid-resistant material (bloodwood, mithral) get the coating as pure
  upside (immune to degrade, still coated). So: metal = coating + chance-to-degrade; non-metal = coating,
  no degrade. Worth a `metal`/`acid_resistant` weapon-material tag when those weapons land. Reuse the
  existing `WeaponAcidCoatingComponent` (4-hit / AcidEffect-6 model).

- **D2 — slime burst-overkill: RESOLVED → KEEP PoC (split always wins).** PoC git history (commit `a7beeba`,
  2025-12-16) shows no trial-and-revert of burst-avoids-split — split-precedence was authored that way from
  day one, *specifically to prevent the narrow-band problem*: if overkill skipped the split, a slime would
  only split when landed in the thin [below-threshold, not-dead] band, so splits would almost never fire and
  the escalator dies. (Rafe's "slimes almost never split" recollection is real but maps to a *different* fix —
  the PoC raised split thresholds to 40%/35%, "tuned for observable splits", `PHASE_19_…md:150` — not a
  burst-skip.) **Do not overturn.**
  **The slime counter (settled):** (1) **AoE** — kills children as fast as they spawn; single-target chipping
  lets them multiply (no new code). (2) **Kill-from-range** — split is *bounded* (children are plain `slime`,
  don't re-split), so trigger the one split from range and skip the melee corrosion/engulf tax (no new code;
  note DoT does NOT skip the split). (3) **Material + positioning** — wood/bone dodges corrosion, break
  contact drops engulf. **Revisit (Track-2 content, optional):** a dedicated *prevent-split* lever — a
  freeze/congeal status (cold damage stops division). Additive; does not touch the precedence rule.

---

## 8. The plan: sequence + two converging tracks

**Sequence (no tuning until step 3 done):**
0. **Migration-loss audit → triage** (done — see `migration_loss_audit.md`). Cheap insurance against
   tuning on a false premise. Run before B1, not in parallel, because tuning is gated behind 0c anyway so
   audit-first costs nothing against the tuning start.
1. **Fold any B1–B2-affecting restores** from the audit. The one candidate gate — inert Speed/Sluggish
   (haste/tar) — was **verified and cleared (2026-06-08): no fold needed.** Those items ARE in B1–B2 loot
   (`scroll_of_haste` B1; `potion_of_speed`/`wand_of_haste`/`tar_potion` B2), but the soak bot only ever
   drinks healing potions (`BotBrain` emits Heal/Attack/Move/Wait — no quaff-speed, no throw), and the
   fixed-scenario assertions don't include those items. So inert haste/tar **cannot** pollute B1–B2 numbers.
   → Speed/Sluggish restore drops to **Track-2** (and is necessary-but-not-sufficient: the bot needs a
   use-policy before it shows up in soak numbers at all). No B1–B2-affecting restores found. Tuning is clear.
2. **0c — the whole-game report** with role-aware health (the Part-4 mockup made real).
3. **Tune B1**, every number legible against a verdict in this locked table; ascend by region.

**Track 1 — Balance (B1–B2).** Durable swarm + orc escalators (chieftain, shaman) + skeletons. All wired,
all have scenarios, all measurable today.

**Track 2 — Restores + deep content, in parallel.** (a) Aggravation rewire (trivial, §5.1) — could land
with B1–B2. (b) Troll B1 loot-pool counter (§5.2). (c) Slime-acid easter egg (§7 D1). (d) From the audit,
when their region/need arrives: hazard-avoidance (general AI fidelity, before B3+), chest quality tiers,
binary→graded resistance (before elemental bosses/rings), the cheap ring restores (Clarity, Invisibility).
(e) **Author the missing deep-region compositions** (slime swarms, lich court, ancient troll, wraith) —
*content authoring first, tuning second*; the deep half is unbuilt content, not just unbalanced.

Tracks converge when balance walks up to B3–B5 and finds counters wired and encounters authored.

**Harness-coverage rule for restores:** none of the lost wires are visible to the harness today — no
scenario exercises haste/tar/aggravation/hazard-fields. Any restore adds its scenario coverage in the
same pass, or it silently rots again.
