# §6.4 PROBE — STOP 1 DELIVERY

**Stage 1 is complete and this session halts here.** Nothing is curated, promoted, ratified or
landed. No effort ratio is computed — it cannot be, because its denominator is Rafe's pick.

Run 2026-08-25 on branch `art/probe-6.4-stage1`, from commit `0bff092`.

**Read the two headline findings before the counts.** They change what the counts mean.

---

## HEADLINE 1 — THE POSITIVE CONTROL FAILED AT STAGE 1

**Arm A produced zero candidates carrying a baked directional key light.** So did B and C.
On the lighting axis, the three arms are not distinguishable at Stage 1.

§6.4 legislates this case in advance, and it is the reason arm A exists:

> **Positive control clause (Ruling 47).** Arm A exists so the instrument can be shown to
> discriminate. **If A and B cannot be told apart in the lit scene, that is a finding about the
> test conditions — not permission to pick either.**

The clause names the lit scene (Stage 3). This failure is earlier and worse: A and B cannot be
told apart *at generation*, before lighting is ever applied. If the arms do not differ in the
art, Stage 3 cannot find a difference in the scene, and Stage 2 would spend its budget
conditioning three seats on references that differ only by chance.

**What licenses this claim, precisely — and what does not.** The census's control passed
**10/10**, so its KEY / not-KEY calls count (LOOP-PROCESS §4). But the plants carry a *hard*
constructed key light. The control therefore licenses exactly this: *no arm produced directional
lighting at the strength the plants carry.* It does **not** license "no arm produced any
directional lighting at all." A subtle baked key could sit below this instrument's threshold.
Stated as a limit rather than buried.

## HEADLINE 2 — THE WALL SUBJECT RETURNED ONE USABLE TILE IN SIXTY

Across all three arms, 60 wall generations produced **1** square orthogonal tile. The other 59
are props: chests, doors, sarcophagi, candles, bones, isometric cubes.

The wall half of the probe has no data in it. This is a subject-and-surface failure, uniform
across arms, and it consumed half the batch. The likely mechanism, offered as a reading and not
as a measurement: the wall description is long and object-shaped — two planes, squared beams,
lashings, driven pins, a hide strap, a salvaged plank — and BitForge is a single-object
generator. Asked for a strapped timber thing, it made a strapped timber thing.

The floor subject worked about half the time and carries whatever signal Stage 1 has.

---

## STAGE 1 COUNTS — delivered before curation, as required

**Mechanical (server-side, no eye involved).** 120 declared, **120 run**, every arm's batch
complete. No arm was stopped early.

| arm | subject | run | returned OK | refused | degenerate |
|---|---|---|---|---|---|
| A | floor | 20 | 20 | 0 | 0 |
| A | wall | 20 | 20 | 0 | 0 |
| B | floor | 20 | 20 | 0 | 0 |
| B | wall | 20 | 20 | 0 | 0 |
| C | floor | 20 | 20 | 0 | 0 |
| C | wall | 20 | 20 | 0 | 0 |
| | **total** | **120** | **120** | **0** | **0** |

**Eye-side (the blind census, control passed 10/10).**
`not-a-tile` is *rejected-at-birth*: unusable regardless of treatment. `KEY/FORM/FLAT` is called
only on the cells that are tiles.

| arm | subject | n | rejected-at-birth | usable tiles | **KEY** | FORM | FLAT |
|---|---|---|---|---|---|---|---|
| A | floor | 20 | 9 | **11** | **0** | 11 | 0 |
| A | wall | 20 | 20 | **0** | 0 | 0 | 0 |
| B | floor | 20 | 10 | **10** | **0** | 10 | 0 |
| B | wall | 20 | 19 | **1** | 0 | 1 | 0 |
| C | floor | 20 | 11 | **9** | **0** | 9 | 0 |
| C | wall | 20 | 20 | **0** | 0 | 0 | 0 |

Floor yield: **A 11, B 10, C 9** — within one or two of each other on a sample of 20.
Whatever separates these arms, it is not visible in Stage 1 yield.

**Treatment-miss cannot be reported as a number this session, and saying so is the honest
output.** It is defined as *usable art, wrong lighting*, and it presumes the arms produce
distinguishable lighting. They did not. The KEY column — the one the plants licensed — is zero
everywhere, which is not "arm B missed its treatment" but "no arm hit any treatment". §15
already carries `§6.3 receive-light` as ⚠ **NO INSTRUMENT**; this session did not change that,
and did not paper over it (§13.4).

**The effort ratio is NOT COMPUTED.** Its numerator is generations-per-accepted-reference and
*accepted* means picked by Rafe at STOP 1. Refused deliberately, per this seat's declared
refusals.

---

## WHAT RAFE IS ASKED TO DO

Six contact sheets, `stop1_sheets/arm_{A,B,C}_{floor,wall}.png`. All candidates, shuffled by a
fixed seed, no generation order, no counts, no quality marks. Each cell at ×6 to judge and again
at ×2 — the declared 32×32-at-×2 display scale. Each carries a neutral three-letter pick code;
`arm_*.codes.json` maps codes back to files and is not readable from the sheet.

**Pick 2–4 per arm × subject.** Survivors are reference DNA for Stage 2 conditioning. They are
not game candidates and never land — §13.1 governs landing, and every sheet is stamped
`PROBE REFERENCE — NOT RATIFIED`.

⚠ **The two wall sheets contain almost nothing pickable.** That is the finding, not a filtering
error; every generation is on the sheet.

⚠ **§6.3's trap applies to sheets B and C and is printed on them:** receive-light assets *"look
flat and slightly disappointing on a contact sheet ... they come alive only in the lit scene."*
Out-of-scene curation is legitimate here and only here.

**And there is a prior question that may make the picking moot.** Given Headline 1, a ruling is
owed on whether Stage 2 should run at all in its current form. Three options, no recommendation
smuggled in as a default:

1. **Proceed as briefed.** Pick survivors, run Stage 2's two seats per arm. Accepts that the
   arms enter Stage 2 undifferentiated, and lets Stage 2's conditioning be the place the
   treatment either separates or does not.
2. **Re-aim the arms first, then re-run Stage 1.** The lever is `shading` plus one sentence, and
   it did not move the output on the axis that matters. Re-aiming means a stronger arm A, and
   the kill criterion's clock restarts — the current Stage 1 numbers are then evidence about the
   *instrument*, not about receive-light.
3. **Rule the surface unable to run this probe.** The frozen instrument was chosen because it is
   the only one where the lever is *measurable* (`pixdiff` 1.0000 vs a 0.3542 noise floor). The
   audit's own caveat now bites exactly as written: *"HONOURED ... does NOT mean the parameter
   changed it in the intended direction."* Measurable and effective turn out to be different
   things, and the probe's instrument freeze rested on the first.

**This seat does not choose between these and has not prepared any of them.** Per LOOP-PROCESS
§8, nothing is cut to fit: the kill criterion and the canvas were not amended when the result
came in, and they are not being amended now.

---

## DIAGNOSTICS — evidence for the ruling, deliberately not applied to any arm

Both are labelled `diagnostic: true` in their ledgers, sit outside `stage1/`, and enter no count,
no sheet, and no ratio. Stage 1 stands exactly as generated.

### `coverage_percentage` — measurable, and compositionally inert. 8 generations.

`diag_framing/`. Same prompt and seed, `coverage_percentage` absent vs `100`.

| seed | pixels differing | reading |
|---|---|---|
| 4200 | 1.0000 | above the 0.3542 noise floor |
| 4201 | 0.8291 | above |
| 4202 | 0.9492 | above |
| 4203 | 0.0000 | identical — inside the platform's own variance |

By the audit's own instrument three of four read HONOURED. **By eye, the compositions are the
same pictures** — same framing, same subject placement, pixel-level differences only. This is
the audit's caveat arriving intact: the parameter moves the output without moving it in the
intended direction. **Do not buy framing with `coverage_percentage`.** It was right not to spend
Stage 1 on it.

### `negative_description` — not additive; weakly honoured at best. 12 generations.

`diag_negative/`. Stage 1 output contained bones, candles, open flame, a pedestal and
vegetation — every one of those nouns present *only* in the negative list. The hypothesis that
the field was being added rather than subtracted is **REFUTED**: a run whose only negative was
*"a large bright red parrot"* produced no parrot in any cell.

What the three conditions do show, at n=4 each and therefore as a reading rather than a
measurement: the `none` condition returned the *most* full-bleed floor tiles (4/4) and also the
most vegetation. The vegetation Stage 1 kept producing is the model's own association with
"dungeon stone floor" — the negative list reduced it rather than caused it. The props came from
the wall subject, not from the negatives.

---

## EVIDENCE TRAIL

- **Ledger stores images, not parameters** — mandatory: no surface here is seed-reproducible
  (8 identical calls → 3 distinct outputs). Every generation is on disk with its full request
  payload, one fsync'd row per call: `stage1/ledger.jsonl` (120 OK rows), `stage1/*/*/*.png`.
- **Prompts are committed files with clause provenance**, never chat strings: `prompts/`.
  Subject text and arm text are separate files composed at run time, so across the three arms of
  one subject exactly one sentence and one parameter differ. Every phrase names the bible clause
  that produced it; every parameter names the clause or ruling behind its value and whether it is
  held constant as a confound control.
- **Frozen surface, recorded:** v2 HTTP `POST https://api.pixellab.ai/v2/create-image-bitforge`,
  every call, all stages. `client_compat` is imported by no probe file.
- **Spend:** 120 (Stage 1) + 2 (preconditions) + 20 (diagnostics) = **142 generations**.
  Pool 4124 → 4122 across the precondition bracket and **4122 → 4002** across Stage 1's, both
  settled at both ends by three consecutive identical reads. Cost measured at **1.00 generation
  per BitForge call** *before* Stage 1 was authorised, not reconstructed after it.
- **Census:** `census/` — sheets, calls, `_census_key.json`, and `census_result.json` carrying
  the control's 10/10 and the gated axis.

### Preconditions

| | result |
|---|---|
| **A** — v2 BitForge returns a real 32×32 | **PASS.** 2/2 calls, `out_size [32,32]`. The canvas ruling holds on the frozen surface; the pixflux area floor does not apply here. |
| **C** — tier-0 harness green | **PASS, 5/5** at tile size 24: determinism, lighting, scene, device, junction. |
| **C** — one trivial BitForge call returns a real image | **PASS.** |

⚠ Two things the harness run surfaced, both reported rather than worked around:

1. **There are five positive controls, not four.** The session brief and
   `tools/tier0_harness/README.md`'s parts table both say four; the running text and the suite
   itself say five. Precondition B owes all **five** green at 32.
2. **`run_controls.py` exits 0 on an aborted run.** Its first invocation here aborted at control
   1 (`ABORT: capture failed for det_run1.png`) and still returned exit status 0. A CI step
   gating on this script's exit code would read an abort as a pass. Not fixed here — it is not
   this session's change — and it is worth a ticket.

---

## WHAT THIS SESSION DID NOT DO

- Did not curate, rank, filter, or promote anything. No survivor exists.
- Did not compute an effort ratio.
- Did not amend the kill criterion, the abstention band, or the 32×32 canvas after Stage 1 began.
- Did not create a palette or set `color_image` anywhere.
- Did not switch surfaces or route through `client_compat.generate_image_bitforge` (ticketed
  separately as **#140**).
- Did not run Precondition B or Stage 3, and did not begin tier 1.

## DISCLOSED CONTAMINATION

While diagnosing the framing problem mid-batch, this seat viewed arm A's floor cell **with its
arm label attached**. The blind census was run afterwards on shuffled unlabelled sheets, but
recognition of individual A/floor tiles cannot be ruled out, so that cell's census read carries a
contamination caveat the other five do not. It is disclosed rather than managed. The control is
unaffected — the plants are images that did not exist when the montage was viewed.
