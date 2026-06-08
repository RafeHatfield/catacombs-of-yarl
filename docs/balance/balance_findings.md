# Balance Findings Log

Running log of design/balance findings surfaced by the harness. Each is a decision to make, not a
bug to silently fix. Newest first.

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
