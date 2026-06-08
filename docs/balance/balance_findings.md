# Balance Findings Log

Running log of design/balance findings surfaced by the harness. Each is a decision to make, not a
bug to silently fix. Newest first.

---

## 2026-06-07 — DECISION: ETP ttk/ttd is the canonical combat-pace target

Two design-intent specs contradicted each other (~2×): the harness `PressureModel` bands (death
35–65%, H_PM 7–24) vs `etp_config.yaml` per-band `target_ttk_hits` / `target_ttd_hits` (B2 = 4/4).

**Ruling (Rafe, 2026-06-07): the ETP `ttk/ttd` targets are canonical for REPRESENTATIVE scenarios.**
The `PressureModel` bands are demoted to **stress-test targets** (they were calibrated for the
over-budget siege scenarios — a coin-flip death rate and a long grind, which is the wrong yardstick
for an intended-difficulty encounter). Going forward:
- Representative scenarios are evaluated against the band's ETP ttk/ttd (H_PM ↔ ttk, H_MP ↔ ttd) and
  a sane per-room death target (a representative room is one of 5–8 per floor — its death rate
  compounds, so it should be low).
- Stress scenarios keep the `PressureModel` bands (the regression net).
- The harness should eventually apply the right band set per scenario kind (representative | stress);
  until then, evaluate representative results against ttk/ttd by hand.

---

## 2026-06-07 — Phase 0 (lock the net)

**FIND-001: `keen_dagger` / the dagger archetype looks strictly-dominated (a trap pick).**
- Evidence: `depth5_zombie_keen` = 94% death rate vs 2–32% for its sibling weapons. The variants line
  up monotonically by average damage: masterwork(5.5)→2%, vicious/fine(4.5)→14–16%, shortsword(3.5)→32%,
  keen_dagger(2.5)→94%. The keen_dagger is the lowest-DPS weapon in the set; crit-on-19 is worthless
  against zombie HP-sponges. **Not a bug** — the honest result of the weakest weapon in an attrition fight.
- Decision needed (itemization pass): does the dagger archetype have a role? A "keen dagger" should be a
  viable crit build, not a death sentence. Daggers need a compensating edge — attack speed, backstab/
  sneak multiplier, or stronger crit math — or they're a strictly-dominated trap. Check what the combat
  model gives daggers today; right now it appears to be "less damage, marginal crit, nothing else."
- Not blocking: 94% is baselined as current honest behavior (regression anchor). When we buff daggers,
  the gate will correctly flag the change.

**FIND-002: the gear-variant matrix conflates weapon *class* with enchant *tier*.**
- The depth{2,3,5} "_keen" columns are `keen_dagger` (a dagger); base/fine/vicious/masterwork are swords.
  So the matrix isn't a clean enchant ladder — the "keen" column secretly tests a different weapon class.
  This muddies the gear-sensitivity read (you can't see "does +tier help?" when one rung swaps the class).
- Improvement (method): when we revisit the matrix, separate the two axes — an enchant ladder on one
  fixed class, and a class-comparison probe at fixed tier. The PoC's matrix carried this conflation
  forward; past the PoC we can fix it.

**Phase 0 result:** baseline refreshed to all 15 scenarios at current (post-bot-persona) behavior;
15/15 PASS; CI (`balance.yml`) gates on the full matrix. The ≤7% deltas from the May-21 baseline are
attributed to the bot-persona instrument change, within tolerance.

**FIND-003: actual time-to-kill is ~2× the canonical ttk target, game-wide.** Now that ETP ttk/ttd
is canonical (decision above), measured H_PM (hits-to-kill a common grunt) is roughly double the
intent at every band tested:
- Depth 2 (B1, target ttk **3**): H_PM **8.0**
- Depth 7 (B2, target ttk **4**): H_PM **7.2**
The player deals the full ETP-baseline damage in both (weapon `RollDamage` + StrengthMod; longsword
1–8 + STR-14 +2 ≈ 6.5/hit, matching the ETP formula's `1d8+2 = 6.5` baseline), so this is **not** an
under-gearing artifact — common monsters simply carry ~2× the HP the ttk target implies (grunt
effective HP ≈ 44–47 vs the ~26 that ttk 4 × 6.5 implies). The `PressureModel` H_PM bands ([5–10],
[7–24]) have ratified this because they were set to the shipped (grindy) numbers, not the intent.
- **Implication:** honoring the canonical ttk/ttd is a *systemic monster-HP / damage-model rebalance*,
  not a per-scenario tweak. It will move the entire baselined suite (expected — re-baseline after).
- **Decision needed (magnitude / appetite):** full honor (→ ttk 3–4, fights ~2× snappier game-wide, a
  major feel change needing playtest validation) vs a measured step (→ ttk ~5 first, playtest, then
  decide) vs revise the targets up to match the shipped pace (cheap, but circular — it abandons the
  intent we just blessed). Recommend committing to the direction but approaching the magnitude in
  measured steps with playtest checks, since ~2× snappier is a dramatic change to the game's feel.
