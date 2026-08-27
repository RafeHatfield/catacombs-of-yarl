# THE WALL GAUNTLET — FINDING

**Budget exhausted below bar. Returning under ruling trigger (b), and under no other.**

Declared before the first generation, not tuned after (LOOP-PROCESS §8):

> **BAR:** 5 candidates pass the blind critic, unhedged.
> **BUDGET:** 100 generations. Spent below 5 passes → stop and report *"text-to-image cannot
> produce architectural surfaces on this platform at acceptable cost"*, with the ledger as
> evidence. That outcome is a finding, not a failure.

**Result: 100 generations, 10 rounds, 0 passes.** No survivors sheet is produced, because there
are no survivors and this seat does not present unculled candidates (§1.1.1).

---

## THE HEADLINE, STATED AS THE BAR REQUIRES

**Text-to-image cannot produce architectural surfaces on this platform at acceptable cost.**

And one qualification the bar's sentence does not carry, because it was measured after the bar
was written: **guided generation cannot either, on this endpoint** — see §3. That closes an
option the bar had left open as a re-plan destination, which is worth more than the bar's own
sentence.

---

## 1. THE NUMBERS

| round | gens | framing / lever | mechanically culled | reached wall questions | passes |
|---|---:|---|---:|---:|---:|
| 1 | 10 | architectural section (text) | 6 | 4 | 0 |
| 2 | 10 | r1 flip list, repair as physical effect | 4 | 6 | 0 |
| 3 | 10 | "fragment, no centre" | 6 | 4 | 0 |
| 4 | 10 | r3 flip list **+ conditioned on C-GAB** | 4 | 6 | 0 |
| 5 | 10 | **guided** — init_image v1, strength 300/150 | 2 | 8 | 0 |
| 6 | 10 | guide v2, strength 500/800 | 1 | 9 | 0 |
| 7 | 10 | guide v3, strength 300/400 | 1 | 9 | 0 |
| 8 | 10 | guide v4, strength 350 | 4 | 6 | 0 |
| 9 | 10 | guide v5 (no chamfers, materials tinted) | 1 | 9 | 0 |
| 10 | 10 | guide v6 (per-tile variation) | 2 | 8 | 0 |
| | **100** | | **31** | **69** | **0** |

**69 of 100 candidates cleared every mechanical cull and were judged on the wall questions.
None passed.** The failure is not that the generator drew the wrong kind of thing — by round 6
it reliably drew coursed masonry, straight-on, full-bleed, unoutlined. The failure is that
none of it is a wall anyone would ship.

## 2. THE CRITIC IS NOT SOFT — the control held every time

The plant was seeded in rounds 2, 4, 6, 8 and 10 and **caught 5 times out of 5** — twice on
`object-not-surface`, once on `wrong-projection`, and twice with the critic volunteering that
the tile needed redrawing from scratch. **No round was voided.** Every verdict in this report
comes from a seat that had just demonstrated it could fail.

The seat is a fresh `claude -p` per round with cwd outside the repo. Blindness is structural
rather than promised: the process cannot reach the repo, the bible, or any prior round.

The hedge guard (LOOP-PROCESS §5's fail-word list, applied mechanically to any PASS whose
reason hedges) **never fired**, because no PASS was ever issued.

## 3. WHAT `init_image` ACTUALLY IS — the most useful thing measured here

Four rounds of text framing had failed in three distinct ways — object (r1), landmark (r3), and
noise (the earlier micro-probe) — and the critic's flip lists had become pixel surgery: *"move
the top divisions from 5, 13, 19, 25 to 4, 15, 22"*, *"repaint pixel (5,23)"*. No prompt can
execute that. So the geometry was supplied directly through `init_image`, a documented parameter
of the frozen surface.

Four strengths were measured:

| strength | behaviour |
|---:|---|
| 150 | generator dominates; geometry overridden, a candidate reverted to a doorway |
| 300 | the most balanced point observed |
| 500 | guide dominates |
| 800 | **the output IS the guide** — flat grey rectangles, no stone material at all |

> **`init_image` is a BLEND control, not a composition control.** It interpolates between your
> image and a generated one. At the strength where geometry holds, there is no generation left
> to supply material; at the strength where material appears, the geometry is gone. **There is
> no operating point where you pin the composition and generate the surface.**

A consequence worth stating plainly: **a candidate produced at strength 800 is not a generated
asset, it is programmer-art laundered through an API.** Had one passed the critic, the pass
would have been worthless. None did.

## 4. TWO FAILURES THAT NEVER MOVED IN TEN ROUNDS

**The repair never arrived.** Bible §7.3 is the Boundary's identity — lashed, pinned,
over-built, repaired on top of prior repairs. It was requested as material (r1), as physical
effect on the stone (r2), as pixel geometry (r3), drawn into the guide (r5, r6), given a value
no stone shared (r6), made to interrupt its own mortar course (r8), given its own hue (r9), and
driven through a joint (r10). **The critic reported "nothing in this set is fastened" in every
single round.** By r9–r10 a timber band does appear — the hue separation worked — but it reads
as a decorative frieze at a constant height, which is precisely §7.3 inverted: ornament where
structure was asked for.

**The top surface never read as thickness.** §3's two-plane rule. Every round produced a lighter
band; every round the critic called it paint rather than thickness, and by r10 the objection was
that an identical hard-edged cap at the same row in every tile "reads as a shelf, not a top" and
stripes the wall every 32 pixels when stacked.

## 5. THE MOST IMPORTANT THING I LEARNED, AND IT IS AGAINST MYSELF

Round 7's flip list asked for **a 1px chamfer on each block's top and bottom edge**, so that a
value change would "describe geometry instead of a light source". I encoded it literally into
guide v4.

**Round 8 came back with three `key-light` culls — the first of the gauntlet.** A per-course
light-top/dark-bottom pattern at 32×32 is indistinguishable from a baked directional light. The
critic's own instruction, executed faithfully, manufactured the §6.3 violation the same critic
then culled.

> **At this canvas size, the vocabulary for "describe geometry with value" and the vocabulary
> for "bake a key light" are the same vocabulary.** Removing the chamfers in v5 took key-light
> culls back to zero.

This is a live hazard for tier 1 and it is not a wall-specific one. §6.3 is now RATIFIED, so
anything that reads as directional at 32px is a defect — and the most natural way to draw
volume at that size trips it.

## 6. WHAT WAS AND WAS NOT TRIED

**Conditioned vs bare.** Round 4 ran conditioned on **C-GAB** (Rafe's amendment: GAB is
compositionally neutral, VAB is charactered stock and not a style parent). Rounds 1–3 and 5–10
ran bare. Conditioning did not clear a cull class that bare rounds could not — but note the
cleaner evidence already on disk: the STOP 1 smoke test isolated conditioning on identical
seeds and prompt and measured material DNA propagating in 12 of 12. **Conditioning works; it is
not what the walls were missing.**

**Levers spent:** 4 text framings; conditioning; `init_image` at 6 strengths; 6 guide versions.
**Levers deliberately not spent:** `outline` (§12.1 LOCKED), `color_image` (standing refusal —
no palette), canvas or surface (frozen), `detail`/`shading` (held constant as confound controls
across all ten rounds — a genuine gap, named in §7).

## 7. WHAT I WOULD NOT CLAIM

- **Not that no prompt exists.** Ten rounds is ten rounds. The claim is about cost: 100
  generations, a full critic loop each round, and no candidate ever reached a pass.
- **`detail` and `shading` were never moved.** Held constant deliberately so content changes
  stayed attributable, and the budget ran out before they were reached. If the wall pipeline
  re-plans on this surface, they are the cheapest untried thing.
- **The guide is not a palette and never was.** Neutral values, plus hue offsets in v5–v6 to
  separate timber and iron from stone. `color_image` was never set. No guide was ever shown to
  the critic and none can land.

## 8. WHERE THIS LEAVES THE WALL PIPELINE

The bar names the re-plan options. On this evidence:

- **Conditioning-first once a corpus exists** — the strongest remaining option, and the only one
  with positive measured evidence behind it (12/12 propagation). It needs a wall corpus to
  condition *on*, which this gauntlet did not produce.
- **Composition from parts** — `/create-tiles-pro` with `tile_feature: "building"` returned 80
  coherent connectable tiles *and* a placement grammar for 20 generations
  (`PIXELLAB-INTEGRATION-AUDIT` §8.7). It has never been tried at the ruled canvas, and it is
  the only path measured to produce architecture rather than surface. ⚠ It is a **different
  endpoint**, so trying it is a surface change and needs a ruling.
- **Hand-authored seeds** — the guides in this directory are, uncomfortably, the closest thing
  to a usable wall the gauntlet produced. That is a statement about the gauntlet, not a
  recommendation.

**Nothing here is ratified, promoted, or landed. §13.1 governs landing and no candidate reached
a gate.**

## 9. EVIDENCE

Every generation on disk with its full request payload: `rounds/roundNN/images/` + `ledger.jsonl`.
Verbatim critic output per round: `rounds/roundNN/critic_transcript.txt`. Parsed verdicts, culls,
flip lists, plant outcome: `rounds/roundNN/result.json`. Prompt files with per-round provenance
mapping each flip item to the change it produced: `prompts/wall_roundNN.json`. Guides and their
build scripts: `guides/`, `make_guide*.py`. All 100 candidates in one sheet, unfiltered:
`gauntlet_trajectory.png`.

### Spend — and a discrepancy I could not close

**The gauntlet made 100 calls and they cost 100 generations.** Every response reported
`usage: {generations: 1.0}`, and after the run a fresh 4-call bracket re-measured **both** call
shapes against a settled balance: plain **1.00/call**, `init_image` **1.00/call**
(`cost_probe/`). The declared budget of 100 was not exceeded by this gauntlet.

**And the pool moved 420 over the same window** — 3950 settled at the end of the conditioning
smoke test, 3530 settled at the start of the cost probe. 320 generations are unaccounted for by
anything in this repo's ledgers, which record exactly 100 request-bearing rows across the ten
rounds and zero refusals.

**The leading explanation, which I cannot verify from here: the subscription is shared with the
sibling project.** `PIXELLAB-UW-AUDIT-2026-08-25.md` records "2,300+ generations spent against a
shared subscription" and attributes the review objects on the account to Gemfall. This session
ran for hours; a concurrent spend on the other project would look exactly like this.

**What I will not do is pick whichever number flatters the report.** Both are stated: 100 by
measurement of my own calls, 420 by balance delta, 320 unattributed.

⚠ **My process error, and it is the one that made this un-closable.** `gauntlet.py` never
bracketed its own balance — unlike every script in the §6.4 probe, which bracketed each phase
at both ends. Per-round brackets would have localised the drift to a round, or shown it
accruing while nothing of mine was running. Fixed in the script; too late for this run. The
probe's own rule was *cost is measured settled before the batch is authorised, not
reconstructed after it*, and the gauntlet quietly stopped following it.
