# Balance Coverage Map — 2026-06-06

**Purpose:** an honest grid of what the harness *measures* vs what the game *ships*, so the balance
push is disciplined ("measured, not guessed" starts with knowing what isn't measured). Drives the
build-out plan at the bottom.

## The reframe: parity, not regression

Checked against the PoC (`~/development/rlike`) before calling anything drift:
- The acceptance suite **still passes** — the 6 baselined scenarios (depth 2/3/5 orc + zombie melee)
  are green against the committed baseline. No regression in 2 weeks of new code.
- **The PoC itself never tuned past depth 6.** Its balance suite is the *exact same 15 scenarios* we
  have. So we're at PoC parity, not below it.
- We didn't drift down — we **built up and out without measuring.** The story is 25 floors deep; the
  balance is 5 floors deep.

**Consequence for method:** the "replicate the PoC first" rule runs out of road past depth 6 — there
is nothing to replicate. **Depths 7–25 are original balance work**: the harness must *define* target
bands empirically (run → observe → set band), not port them. Flagging because it changes how we work.

## Depth bands (from region naming in `CatalogEntryRenderer`)

| Band | Floors | Region |
|------|--------|--------|
| I    | 1–5    | Reven Crypt |
| II   | 6–8    | The Boundary |
| III  | 9–12   | The Dimhalls |
| IV   | 13–17  | The Weighing (region) |
| V    | 18–24  | The Inner Court |
| —    | 25     | The Weighing (floor / endgame) |

## Coverage grid

Legend: ✅ measured + baselined · 🟡 scenario exists, not in baselined matrix · ⬜ unmeasured

| System / content        | I (1–5) | II (6–8) | III (9–12) | IV (13–17) | V (18–24) | Weighing |
|-------------------------|:------:|:------:|:------:|:------:|:------:|:------:|
| Melee — orc family      | ✅ (2,3,5) | 🟡 (d6 only) | ⬜ | ⬜ | ⬜ | — |
| Melee — undead (zombie) | ✅ (d5) | ⬜ | ⬜ | ⬜ | ⬜ | — |
| Ranged combat           | 🟡 (arenas) | ⬜ | ⬜ | ⬜ | ⬜ | — |
| Possession              | 🟡 (1 soak) | ⬜ | ⬜ | ⬜ | ⬜ | n/a |
| Factions (emergent)     | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | — |
| Spells / wands / scrolls| ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Rings                   | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | — |
| Potions / throw         | 🟡 (test only) | ⬜ | ⬜ | ⬜ | ⬜ | — |
| Status effects          | 🟡 (test only) | ⬜ | ⬜ | ⬜ | ⬜ | — |
| The Weighing (endgame)  | — | — | — | — | — | ⬜ |

**Net: we measure ~Band I melee. Bands II–V (floors 6–24) and every system past melee are dark.**

## Monster scenario coverage

Has a dedicated identity/soak scenario:
`cave_spider, web_spider, giant_spider, fire_beetle, necromancer, plague_necromancer, orc_shaman,
orc_chieftain, orc_skirmisher, skeleton (shieldwall), troll, slime (engulf)`.

**No dedicated scenario — and dangerous:** `cultist_blademaster, troll_ancient, greater_slime,
wraith, lich`. The lich is a depth-boss-tier caster (Soul Bolt, Command the Dead) that has **never
been measured**. `large_slime, plague_zombie, orc_scout, orc_veteran` also uncovered (lower risk;
orc_grunt/orc_brute are exercised inside the depth-band scenarios).

## Maintenance gap (cheap)

The committed baseline (`reports/baselines/balance_suite_baseline.json`) holds only 6 of the 15 matrix
scenarios. The 9 gear-variants (keen/vicious/masterwork) run but report NO_BASELINE → the CI gate
protects 6, not 15. Decide if the variants belong, then `--update-baseline`.

## Prioritized build-out plan

**Phase 0 — Lock the net (≈minutes).** Re-baseline the full 15-scenario matrix; confirm CI gates on
all 15. Cheap insurance before expanding.

**Phase 1 — Deep descent, Bands II–III first (6–12) [bulk of the work, highest play-impact].**
Most runs die in the mid-game. Author per-band scenarios for the dominant compositions at each depth
(orc siege → Boundary, undead/Dimhalls casters), run to establish empirical H_PM/H_MP/Death% bands,
tune scaling. Pull in the dangerous uncovered monsters here: `lich, wraith, troll_ancient,
greater_slime, cultist_blademaster` at their spawn depths. Then Bands IV–V (13–24).

**Phase 2 — System viability probes (depth-banded).** Faction emergent combat, possession soak across
depths, ranged at depth (not just arenas), spell/ring viability probes. Each answers "does this system
hold its intended power curve as the player descends?"

**Phase 3 — The Weighing soak (TASK-011).** Now unblocked (headless levers: `WeighingAuditOverride`
+ `WeighingHeadlessGatePolicy`). The 4 record-state scenarios: clean / heavy-no-ally /
heavy-with-ally / all-savage. Tune Guardian + Debt placeholder stats (`StatsFor`,
`SpawnDebtCombatant`) + strawman tier thresholds. Isolated — can run in parallel with Phase 1/2.
Output Rafe wants: per-tier time-to-resolution + win-rate across the 4 states (see
`project_weighing_balance_pass` memory). Heavy-with-ally is a distinct combat shape (enraged former
ally mid-gauntlet) — its own scenario.

**Phase 4 — Re-wire CI** to gate on the expanded matrix so this drift can't silently recur.

## Open method question for Rafe

Bands II–V have no PoC target bands to replicate. Proposed approach: for each band, run the dominant
composition, read the harness output, and *set* the band where the curve lands at intended skill+gear
(the PoC's own method, just applied to new depths) — then defend it against the design intent for that
region. Confirm this is the intended way to chart new territory before we start Phase 1.
