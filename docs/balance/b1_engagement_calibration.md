# B1 Orc-Density Engagement Calibration

**Status: LOCKED 2026-06-11**
**Companion to:** `threat_archetypes.md §4` (composition-assertion table, rows A)

This record captures the decisions, methods, and findings from the first Layer-1
engagement-balance pass. Read it before re-tuning any B1 orc composition — not to
prevent re-tuning, but so the reasons behind the current numbers are visible and can be
challenged on their merits rather than re-derived from scratch.

---

## The framing that governs everything below

**The with-potion row is the PRIMARY balance reference.**

Health potions are designed to be plentiful — the player nearly always enters a fight with
at least one (this is what the cooldown mechanic enables: generous quantity, rate-capped
in-fight use). B1 orc compositions are balanced *including* the potion. Its absence is the
punishing edge case that makes potions feel necessary, not the normal state.

This means:
- The `leather + dagger + potion` row is what we tune toward.
- The `leather + dagger, no potion` row is the floor — measured to confirm the potion creates
  a meaningful gradient, not to hit a specific number.
- If the with-potion primary row is in-band and the no-potion floor is "clearly worse," both
  goals are met. The floor doesn't need to reach an arbitrary threshold.

This framing inverts a common assumption and should be stated explicitly whenever a new
composition is being characterized. "Is this too hard?" means "too hard for a player who
has their potion," not "too hard for a naked player."

---

## Locked settings (orc_grunt)

| parameter | before | after | lever |
|---|---|---|---|
| HP | 28 | **40** | fight-duration (how many orc swings land before the player kills them) |
| main_hand spawn chance | 0.75 | **1.00** | always-armed; selection stays randomized (club/dagger/sword) |
| chest spawn chance | 0.50 | 0.50 | unchanged — light/no armor is B1 identity |
| damage_min/max | 4–6 | 4–6 | unchanged |
| accuracy | 4 | 4 | unchanged |

**Potion (healing_potion_cd):** 20 HP flat, 10-turn cooldown. Untouched during the orc
calibration — the steepened HP curve brought the primary row into band without touching the
potion. The 20 HP value may need a small re-check if any future change significantly shifts
the fight-length distribution, but it arrived clean.

---

## Calibrated bands (with-potion primary row)

These are the Layer-1 engagement bands for the `leather + dagger + potion` loadout vs B1
`orc_grunt`. They encode the *intended feel*, decided on merits. Results over gates — the
bands moved when the feel called for it (2-orc widened; 5-orc upper bound is 100%).

| composition | band | intended feel |
|---|---|---|
| 2 × orc_grunt | 0–10% | Comfortable: punishing game, but warmup. Dungeon can still bite. |
| 3 × orc_grunt | 10–25% | Tough: you need the potion; you survive but feel it. |
| 4 × orc_grunt | **35–50%** | **The flip: dangerous-but-winnable with the potion.** Bot is the floor of skill; a skilled human does better. |
| 5 × orc_grunt | 50–100% | Decisively too-much: usually die, luck it out sometimes. |

**Observed at lock (seed 1337, 100 runs, HP 40, always-armed):**

| | no-potion floor | with-potion primary |
|---|---|---|
| 2 orcs | 10% (at ceiling) | 5% ✓ |
| 3 orcs | 30% (runs hot — by design; floor is the punishing case) | 13% ✓ |
| 4 orcs | 62% | **35%** ✓ (at the band floor — clean landing) |
| 5 orcs | 81% | 55% ✓ |

The no-potion floor at 4-orc (62%) vs with-potion (35%) is a **−27pp gradient** — the
"you needed that potion" signal is clear and readable. That gradient is the floor row's
entire job. The number doesn't need to hit 70–80%; it needs to be unambiguously worse than
with-potion, and it is.

---

## Method: the loadout sweep (not "tune a single scenario to a band")

We characterized survivability as a function of loadout — `death% = f(composition, weapon, armor, potions)` — rather than guessing a player baseline and tuning to a fixed scenario. This matters because the loadout is a design output (what the floor must supply), not a given.

The sweep ran the 2/3/4/5 orc ladder against multiple loadout rungs:
`naked+dagger`, `naked+sword`, `leather+dagger`, `leather+sword`, `leather+dagger+potion`, `leather+dagger+cdp`

Key findings:
- Each gear axis buys roughly **one flip-rung** in isolation: weapon alone: +1, armor alone: +1, both: +2.
- A **regular 40 HP potion** wipes out the entire lethality curve (24%→1%, 40%→2%, 66%→9%) — structurally broken, not a tuning value.
- The cooldown-potion (20 HP, 10-turn CD) at the shallow pre-fix curve still flattened it too much.
- Once HP steepened the curve, the 20 HP potion arrived in-band without being re-tuned. The deferral was correct.

---

## HP as the fight-duration lever — and its ceiling

**The diagnosis:** H_PM was ~6.0 (player kills an orc in ~6 hits) while H_MP was ~9–10 (orcs need ~10 hits to down the player). The swarm wasn't lethal because the player killed most orcs before they compounded enough swings. This is a fight-*duration* problem, not a per-hit-damage problem.

**HP is the right lever** because: more HP = more orc swings land before they die = more total damage to the player. Per-hit damage stays constant (clean axis separation). Raising damage would drift orcs toward spiky behavior, which violates their attrition identity.

**HP has a deceleration ceiling.** Three-point measurement:

| orc HP | 4-orc no-potion death% |
|---|---|
| 28 | 30% |
| 36 | 58% (+28pp, +3.5pp/HP) |
| 40 | 62% (+4pp, +1.0pp/HP) |

The slope decelerated from +3.5 to +1.0pp/HP between 36→40. This is a real property of the
attrition model: at HP 36, the player was already killing most orcs before the extra HP
compounded further. Forcing 4-orc no-potion to 70–80% would require HP ~48–58, which would
wreck 3-orc and 2-orc. HP can't compress the ladder; it moves all rungs up together.

**HP 40 is the right stopping point** because the with-potion primary row arrived at its
targets and the no-potion gradient is meaningful. The slope diagnosis is how we avoided
brute-forcing past the natural ceiling.

---

## Orc armor: reserved for deeper regions

B1 orc_grunts intentionally spawn light/unarmored (chest spawn chance 0.50 stays). Armored
orcs are a *regional escalation lever* — the shift from "fragile many" to "armored many"
is a readable difficulty step for B2/B3. Introducing armor at B1 would spend that lever early
and conflate lethality (HP, damage) with durability (armor, fight length from the player's
side). Keep them separate.

---

## What this enables

With B1 orc-density calibrated, the composition-assertion table row A ("4 orcs winnable") is
confirmed and measured. The next compositions in order:

1. **Remaining B1 escalators (rows B, C):** `orc_chieftain + grunts`, `orc_shaman + grunts`.
   These wait on the escalator-fork decision (alive-vs-killed comparison method).
2. **B1 spike (rows D, E):** `troll` — lethal-by-attrition, counter via acid/fire. Row E
   (`troll + accessible counter`) is blocked on the troll counter-access fix (see §5.2).
3. **B2 textured baselines:** skeleton (ShieldWall, bludgeoning counter), cave spider, fire beetle.
4. **Mixed baseline compositions** once individual rungs are calibrated.

The per-death capture infrastructure built for the 0c pass handles all of these — including
mixed compositions — because we built true per-death capture, not derive-from-aggregates.
