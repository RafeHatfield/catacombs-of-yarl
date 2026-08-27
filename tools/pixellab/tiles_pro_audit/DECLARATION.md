# `/create-tiles-pro` — INSTRUMENT AUDIT: TASK, METHOD, BAR

**Declared before the first call. Committed before the first call. Not tuned after
(LOOP-PROCESS §0.3, §8; bible §13.6).**

This session measures a candidate instrument. It does **not** adopt one, does not change the
frozen surface, does not promote anything to corpus, and does not condition future work on
anything it generates. The instrument ruling is Rafe's, taken with the composition spike's
report beside this one.

---

## TASK

Audit `POST /create-tiles-pro` (`tile_feature: "building"`) as a candidate **wall** instrument.

The incumbent is measured. v2 BitForge text-to-image produces **surface** reliably and
**architecture** never: 100 generations, 10 rounds, 69 candidates reaching the wall questions,
**0 passes** (`tools/pixellab/wall_gauntlet/FINDING.md`). The two failures that never moved in
ten rounds were §7.3's repair and **§3's top surface, which never read as thickness**.

The question here is narrow and is not "is tiles-pro nicer". It is: **does this endpoint
produce architecture — two-plane wall structure — rather than another kind of surface?**

## BAR — names its destination

The gauntlet's bar scored *usable-as-wall*, and wallpaper clears that. This bar does not.

A generation counts as a **structural candidate** only if all four hold:

1. **Two planes.** A top surface distinguishable from a front face (bible §3). Not a lighter
   band that reads as paint; thickness.
2. **Segment identity.** It is a *piece* — a cap, a base, an end, a corner, a junction — not an
   edge-to-edge swatch that would tile in any direction.
3. **§6.3-legal.** No directional key light. **Occlusion-drawn geometry is legal**: dark where
   light cannot reach is correct; bright where light would strike is not. (The gauntlet's §5
   hazard is live — at 32px the vocabulary for *describe geometry with value* and the
   vocabulary for *bake a key light* overlap, and the distinction that survives is direction:
   an occlusion darkens a recess wherever it sits, a key light lights one side of every block
   the same way.)
4. **No baked outline** (§12.1). No dark ring around the piece.

### The yield bar

> **≥ 5 structural candidates in 20 generations.**

**What "20 generations" means on this endpoint, stated because the unit is not obvious and the
reading must not be chosen after the results.** One `tile_feature: "building"` call bills
exactly **20 generations** — measured [API] twice on this account, at `tile_size` 32 and 24
(`PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md` §8.7, §9.2), and re-measured here. So 20
generations is the price of **one kit**, and the yield run is **one kit**, judged on its wall
pieces. This is the like-for-like comparison against the gauntlet, whose 20 generations bought
20 candidates: *does the same money buy five walls here?*

The rejected alternative reading — 20 separate calls, 400 generations — is recorded so the
choice is auditable, not silent. It was rejected because the bar is denominated in the same
unit the gauntlet used (generations, i.e. spend) and because 400 generations is not a bounded
audit.

**Two kits are run, at two seeds, and the bar is applied to each independently.** Declared now,
before any result, so that a second kit cannot later look like a retry. One sample is not a
yield; if the two kits disagree about the bar, *that disagreement is the finding*.

### What each outcome triggers (§1.1.4)

| Outcome | Ruling |
|---|---|
| Bar met on both kits | Candidate-instrument report + columns table. **No adoption.** |
| Bar failed | Finding report, same columns: tiles-pro is not the wall answer either. |
| Kits disagree | Reported as measured; the disagreement is the result, not an average. |
| Instrument cannot fail (critic passes a plant) | **Stop.** Round void, §4. |

---

## METHOD

### Columns first — one real call per claim, no verdict from docs

| Column | How it is answered |
|---|---|
| Canvas at 32×32 | Free 422 constraint probes for the enforced ranges; a paid kit for the actual emitted canvas and footprint |
| Conditioning support | Free probe for zero references; paid probe for whether references are honoured and what they override |
| Lever presence and **measurability** | **Noise floor first** — ≥4 byte-for-byte identical calls — then each lever's pixdiff against that floor |
| Determinism | Assumed absent; the same 4 identical calls confirm or refute it |
| Latency and cost | Wall-clock from POST to tiles-in-hand, and `usage` against a settled balance bracket |

**The noise floor is not optional and this audit's parent probe is why.** §6.4's first lever
pass reported HONOURED on all four surfaces at `pixdiff=1.0000`, *including a control* — an
instrument that cannot fail, whose passes did not count. The negative control is what made the
column readable. A lever verdict here without a floor beneath it would be that mistake in a new
costume.

**A pixdiff is not an aesthetic judgement** (bible §13.4). It answers exactly one mechanical
question: did the parameter do anything at all. HONOURED never means *moved in the intended
direction* — that is an eye question and it belongs to the human gate.

### Yield run

Two kits. Prompts committed as files with clause provenance, wall subject per bible §3 / §7.3 /
§8. Every tile on disk with its full request payload.

### The critic seat

Fresh `claude -p`, cwd outside the repo, no repo access, no bible, no memory (§3.1–3.2).
Fiction and questions only. Questions ask what the rule exists to make answerable, never
whether the rule was followed (§3.3).

**Two plants per critic set, and the second is the one that matters (§4):**

- **Plant A — mechanical.** An unmistakable object from the wall morgue. Should die as
  object-not-surface or wrong-projection.
- **Plant B — the bar's own destination.** A wall-gauntlet swatch — coursed masonry,
  edge-to-edge, no segment identity, exactly the thing that cleared the *old* bar — composited
  onto the same canvas as the kit tiles so it cannot be spotted by its shape. **This plants the
  precise defect this bar exists to catch.** A critic that passes Plant B has not enforced the
  bar, and the round is **void, not discounted**.

Plants are sourced from the wall gauntlet's morgue and that ledger is otherwise not touched.

---

## BUDGET

> **220 generations, hard ceiling.** Declared before the first call and not tuned after.
> Spend below the bar → the finding is *"tiles-pro does not produce architecture at acceptable
> cost either"*, with the ledger as evidence. That outcome is a finding, not a failure.

Planned allocation, ~20 generations per kit call:

| Phase | Calls | Generations |
|---|---:|---:|
| Constraint probes (designed to refuse) | 14 | **0 expected** |
| Noise floor + determinism (4 identical) | 4 | 80 |
| Levers: `building_layout`, `building_wall_angle`, `outline_mode`, conditioning | 4 | 80 |
| Yield: two kits, two seeds | 2 | 40 |
| | | **200 planned, 220 ceiling** |

**Every phase is bracketed at both ends with a settled balance read.** The wall gauntlet's one
un-closable defect was a script that never bracketed its own balance, leaving 320 generations
unattributable after the fact and forcing the report to state two numbers it could not
reconcile. That defect does not recur here: `tiles_pro.Bracket` is entered by every paid entry
point, and a bracket whose reads never settle prints **LOWER BOUND, not a measurement**.

---

## REFUSALS — written before this seat could be tempted (§7)

- **No adoption, no freeze change, no corpus promotion.** Nothing generated here becomes a
  reference, a style parent, or an input to any later run.
- **No comparison by adjective.** The incumbent is compared on numbers and sheets only.
  "Better", "richer", "more architectural" are not findings.
- **No candidate is approved from a contact sheet** (bible §13.1). The sheet in the report is
  evidence, not a shortlist.
- **No register score.** There is no dread metric and no staging detector, and this audit does
  not build a proxy for one (bible §13.4). `NO INSTRUMENT` is a correct row.
- **The wall gauntlet's ledger is read only to source plants.**
- **No claim of work not on disk.** Every number in the report resolves to a file in this
  directory.
- **The bar is not re-read after the images are seen.** It is above, in this commit, before
  them.

---

## AMENDMENT — 2026-08-26, after the audit closed at its ceiling

**Recorded here rather than applied silently, because the original number is the only thing
that makes it checkable (LOOP-PROCESS §11's precedent: recorded rather than silently edited).**

The 220-generation ceiling above stands as declared and was met exactly. Rafe's ruling on this
audit's finding authorises **one further call** — `tile_depth_ratio`, the only camera parameter
the audit did not spend — with the condition that the prediction be committed before the request
is sent. The ceiling is therefore raised to **240** for that one call, and `spend.CEILING` is
changed to match.

- Authorising ruling, verbatim: *"Approved: the one `tile_depth_ratio` call, your prediction on
  file before it runs."*
- Prediction: `PREDICTION.md`, committed before the call.
- This is ruling trigger (b) — an amendment to something frozen — granted by the human gate.
  **A bar changed by ruling is not a bar tuned to a result.**

The ruling also settles what this audit was for, and that is recorded in `FINDING.md §0`:
tiles-pro is promoted to **parts supplier, not instrument**; the wall road is composition; the
architecture/conditioning surface split is platform fact.
