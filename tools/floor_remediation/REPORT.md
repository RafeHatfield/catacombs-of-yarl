# SURVIVOR-FLOOR RING REMEDIATION — session report

**Returning under ruling trigger (b) — an amendment to a frozen bar — and under the brief's own
character trigger for A-VAB. Nothing has landed. §13.1 governs landing and nothing here
satisfies it.**

Declared before the first measurement, not tuned after:

> **TASK** — de-ringed versions of the four §6.4 survivor floors (A-VAB, A-HEB, B-KAB, C-GAB).
> Real corpus remediation, replacing the instrument-only MOCK. Strip surgically where possible;
> where surgery damages the tile's character, regenerate by conditioning on the survivor itself
> and verify the child is ring-free.
>
> **BAR** — a blind seat armed with the spike's ring measurement passes all four, and the check
> is shown able to fail: run it against the un-remediated originals first, and it must cull them.
>
> **REFUSALS** — does not touch the originals in the ledger; does not promote without the
> seat's pass.

---

## 0. THE ANSWER, STATED FIRST

**The four floors were de-ringed. The bar was not met, and it cannot be met by de-ringing them,
because the ring is not what is wrong with two of them and is not the only thing wrong with the
other two.**

Three findings, in order of how much they cost the project if they stay unknown:

1. **The spike's ring table is wrong in both directions, and the MOCK left the strongest
   survivor fully ringed.** A-VAB carries TWO closed 1px loops. `dering_floors.py` removed
   neither, because its test is a luminance threshold and A-VAB's rings sit at 0.48 of the
   median. The MOCK's A-VAB is byte-identical to the raw survivor and so is its lit in-scene
   capture — **sha256 `9e9890c0fa4db115` either way**. A-VAB is the tile the survivor manifest
   marks `strongest` and the tile the spike's own solo-floor captures used as the single floor.
   Meanwhile A-HEB and C-GAB, which that table also judged, never carried a ring at all.

2. **The ring survives the conditioning channel and cannot be prompted away.** 24 generations
   conditioned on B-KAB itself: **22 came out ringed.** The parent's prompt already carries
   `outline: lineless` and negatives for `outline, border, frame`. Adding an explicit refusal of
   the construction moved the rate from 8-of-8 to 7-of-8; raising `style_strength` from 50 to 80
   moved it to 7-of-8. **Neither lever did anything.** Screening is what catches this, not
   prompting — and it will recur on every floor generated from this surface.

3. **Ring-free is nowhere near enough.** The blind seat culled all four un-remediated floors and
   then culled all four remediated ones. Two of the four were never about rings: A-HEB and
   C-GAB draw honest masonry and fail on *per-cell repetition, zero traffic wear, and value
   cast*. The seat's own summary, having never seen the bible: *"all five are laid to the same
   flawless repeating module, which is why not one of them reads as a floor anything has
   actually happened to."*

---

## 1. WHAT THE INSTRUMENT IS, AND WHY IT REPLACES A THRESHOLD

`tools/floor_remediation/ring_instrument.py`. It carries **no luminance threshold anywhere** and
never compares a value to a constant. §12.1's worked example — written into the bible by the
composition spike itself, one round after `dering_floors.py` — says the prohibition is
value-agnostic and that what separates occlusion from a ring is *whether the treatment answers
to the geometry it sits on, not whether it is lighter or darker than its surroundings*.

Five criteria, each traceable to a sentence of §12.1:

| # | criterion | §12.1 |
|---|---|---|
| 1 | **present on every side** — the contour is found in all four directions from the cells it surrounds, ≥ 0.90 | *"present on every side regardless of what adjoins it"* |
| 2 | **thin, of constant width** — median ≤ 2 px, MAD ≤ 0.5; and **hollow** — its pixels lie on the outline of their own extent, not through it | *"a dark edge drawn around a thing"*; *"a uniform ribbon of constant width"* |
| 3 | **rings a thing** — the surrounded region ≥ 16 px | — |
| 4 | **rings ONE thing** — removing it leaves the tile in ≤ 2 parts, not a network of cells | *"drawn around a thing BECAUSE IT IS A THING"* vs *"where one plane stops and another begins"* |
| 5 | **at every value** — swept over the tile's whole ladder in both polarities, every band between two levels, and every exact colour | the clause is value-agnostic, so the sweep must be too |

**Positive control — LOOP-PROCESS §4 / §13.5.** Ten synthetic cases, **7 red and 3 green**, and
the green half is load-bearing: an instrument that only alarms has discriminated nothing. Four
pairs each differ by exactly ONE property:

```
ctrl_midtone_ring  vs ctrl_joint_net    same colour, same 1px width, same constancy
ctrl_edge_frame    vs ctrl_joint_net    both run to the tile border
ctrl_dark_ring     vs ctrl_nicked_ring  identical but for a 2px gap; BOTH are rings
ctrl_split_ring    vs ctrl_occlusion    both open per piece; one assembles into a ring
```

`ctrl_occlusion` is the one that matters most: plane-boundary occlusion is **RULED legal and
required**, and a false positive there would be the worst failure this instrument could have.

**Three of those controls exist because the instrument failed and was caught.** Recorded
because the corrections are the instructive part:

- The control suite itself caught the first draft: it called a masonry joint network a ring.
- The **blind seat** caught the second and third. A topological-closure test passed a keyline
  with a 2px nick, and a per-contour test passed a keyline drawn as two overlapping L-brackets
  (each scoring 0.57 and 0.65 alone). The seat culled both on sight. `ctrl_nicked_ring`,
  `ctrl_split_ring` and `ctrl_dashed_ring` are those failures, planted.

**KNOWN LIMIT, stated rather than tuned away.** A ring broken more than about one pixel in eight
falls below the coverage threshold and is not seen (measured: 1-in-8 → 0.864, 1-in-9 → 0.929).
The threshold is not lowered to reach it, because the seat ruled A-HEB's and C-GAB's mortar
networks are joints and those measure 0.688 and 0.791 — dropping far enough to catch a dense
dash would start calling masonry a keyline. LOOP-PROCESS §8: nothing is cut to fit.

---

## 2. THE MEASUREMENT — 2 OF 4, NOT 1 AND NOT 4

| survivor | spike's table (value threshold) | this instrument (geometry) | what is actually there |
|---|---|---|---|
| **A-VAB** | 0.48 — *"a mid-tone rebate — kept"* | **RING** | two closed 1px loops: 76 px (sides 0.99) and 32 px (sides 1.00), each width 1.00 ± 0.00 |
| A-HEB | 0.57 — *"a mid-tone rebate — kept"* | CLEAN | 135 candidate enclosures, every one rejected — ragged wall or a network of cells |
| **B-KAB** | 0.11 — *"a near-black closed ring"* | **RING** | one closed 1px loop, 62 px, sides 0.99, width 1.00 ± 0.00 |
| C-GAB | 0.53 — *"a mid-tone rebate — kept"* | CLEAN | 43 candidate enclosures, every one rejected |

**The blind seat reached the same two, blind, unprompted, having never seen §12.1 or this
instrument.** On A-VAB: *"Two concentric closed rectangles inset in the middle of every tile,
each one width and one value the whole way round — the tile is a framed plaque."* On A-HEB and
C-GAB it declined to cull them as keylines and said why: *"The top two at least draw stone with
joints between it."*

That is independent corroboration in both directions, and it is why the disagreement with the
spike's table is reported as a correction rather than an opinion.

---

## 3. THE ROUTE IS CHOSEN PER TILE, BY MEASUREMENT

The question that decides surgery vs regeneration is narrow and it is §12's own clause — *value
separation from the surface beneath*. Strip the ring: does the plate still separate from its
ground by value?

| | separation with the ring gone | route | result |
|---|---:|---|---|
| **A-VAB** | **+11.2** | **surgery** | 108 px stripped, 2 loops, no colour invented, instrument CLEAN |
| **B-KAB** | **−1.1** | **regeneration** | surgery empties the tile — plate and ground are the same value |
| A-HEB | — | carried unchanged | verified clean, 0 px changed |
| C-GAB | — | carried unchanged | verified clean, 0 px changed |

This is **not a character score** and must not be read as one. It measures the one mechanism the
ring was performing, because that is the mechanism surgery removes. §13.4 stands: there is no
character detector here and there must not be one.

The fill rule is `dering_floors.py`'s own — the **modal** non-ring neighbour, never a
per-channel median, so no colour is invented — kept unchanged because it was right. An assertion
enforces it rather than a comment claiming it.

---

## 4. B-KAB — 24 GENERATIONS, 22 RINGED

Declared before the first call: 24 generations, 3 waves of 8. Spent: 24. Pool 2866 → 2842.

| wave | lever | ringed | clean |
|---|---|---:|---:|
| 1 | the parent's prompt **unchanged**, conditioned on the parent | 8 of 8 | 0 |
| 2 | + explicit refusal of the ring construction | 7 of 8 | 1 |
| 3 | + refusal, `style_strength` 50 → 80 | 7 of 8 | 1 |

**Neither lever moved it.** One in eight is not a difference at n=8. The parent's prompt already
refuses `outline, border, frame` and sets `outline: lineless`, and the parent came out ringed
anyway — so this is not a case of forgetting to ask.

The two clean children were ordered by material proximity to the parent — uncalibrated, no
verdict drawn (§13.2) — and the top one placed in the remediated set as a **candidate**. Note
that **palette overlap with the parent was 0.000 for all 24**, and the promoted child shares
**0 of 1024 pixels** with the survivor it was conditioned on. The conditioning channel carried
no exact colour through, so the ordering rests on the value histogram alone. That is a weak
ordering and it is labelled as one — and it is why `remediated/MANIFEST.json` records B-KAB as a
regenerated candidate rather than a derivation, with the surgery it rejected kept beside it.

**Run-order change, recorded rather than tidied away.** The first draft stopped after any wave
that cleared the bar. Wave 1 cleared it with exactly one clean child, which exposed the flaw:
the session returns to Rafe under a character trigger, and one take is a dead end rather than a
re-curation. The remaining 16 were spent, and waves 2 and 3 are what turned "conditioning
reproduces the ring" into "and no lever available on this surface changes that".

---

## 5. THE BLIND SEAT — TWO ROUNDS

Fresh `claude -p`, cwd outside the repo, no bible, no memory, codes anonymised and not in set
order. What it sees is the **lit in-scene capture at the reference device's pixel size**
(§2.1) — never a contact sheet. Scope declared per §2.2: the floor. Walls are byte-identical
across the whole set and out of scope, because §3's unresolved wall-thickness problem culled all
five arms of the composition spike eight rounds running and would swamp a floor verdict.

**ROUND A — the four un-remediated survivors. The demonstration that the check can fail.**

> **4 of 4 culled.**
> F4 = A-VAB — `keyline` — *"Two concentric closed rectangles inset in the middle of every tile,
> each one width and one value the whole way round — the tile is a framed plaque, and the moss
> clumps repeat at the same corners to confirm it."*
> F2 = B-KAB — `keyline` — *"Each tile is a dark rounded-corner border ringing an inset panel,
> complete on all four sides at one width and one value, floating on empty ground — a card laid
> on the floor, not stone."*
> F1 = C-GAB — `cull: none` — *"Every tile is fenced left and right by a hard uniform rule and
> stamped with the same rectangular stone in the same place."*
> F3 = A-HEB — `cull: none` — *"The best-drawn stone in the set is undone by a hard uniform
> border down both edges of every tile and a joint skeleton that repeats in lockstep at 32px."*

**ROUND B — the four remediated, plus a plant (the raw B-KAB, hardest-ringed tile in the
corpus).**

> **PLANT CAUGHT** — `keyline`, *"the planted defect, and the most literal sticker-on-ground in
> the set."* The round is valid.
> **0 of 4 passed.**
> F5 = remediated A-VAB — `keyline` — *"A joint of one width and value rings the inset slab in
> each cell, turning all four corners and returning rather than running into the neighbour, and
> the identical U-shaped notch centred on every slab plus moss sprigs at repeating positions
> confirms the read as one stamped plate per cell."*
> F1 = remediated B-KAB — `keyline` — *"Every cell carries a 2px dark maroon border of one value
> around a rounded-corner panel — it rings the shape, turns all four corners and returns, and
> sits on flat unstructured brown, so the floor reads as playing cards dealt onto dirt."*
> F2 = remediated C-GAB — `cull: none` — *"The joints are honest but the floor is one bitmap
> repeated edge to edge with zero traffic history, so it reads as tiled wallpaper."*
> F3 = remediated A-HEB — `cull: none` — *"Verbatim per-cell repetition plus a high-key pink
> surface with no wear anywhere makes this a new patio, not the Paths of the Dead."*

The two rounds together are the control: a seat that culls everything satisfies A and fails B's
bar; a seat that passes everything fails A and is caught by B's plant. Only a discriminating
seat satisfies both.

---

## 6. WHERE THE INSTRUMENT AND THE SEAT PART COMPANY — AND WHY I STOPPED TUNING

The seat culled the two remediated tiles that the instrument calls clean. The obvious move is to
lower the coverage threshold until they agree. **It does not work, and the measurement is the
finding:**

| tile | seat's ruling | highest side coverage in the tile |
|---|---|---:|
| A-VAB original | keyline | 1.000 |
| B-KAB original | keyline | 0.992 |
| **C-GAB original** | **not a keyline** | **0.791** |
| **remediated B-KAB** | **keyline** | **0.757** |
| **A-HEB original** | **not a keyline** | **0.688** |
| **remediated A-VAB** | **keyline** | **0.654** |

**The classes overlap.** No threshold separates them. A tile the seat calls a keyline scores
*below* two tiles it calls clean.

That is not a threshold that needs adjusting; it is a measure that does not encode what the seat
is reacting to. Read the seat's own words for F5: the objection is that the boundary *"turns all
four corners and returns rather than running into the neighbour"*, and that *"the identical
U-shaped notch centred on every slab"* repeats. **The second half is a property of the floor as
laid across thirty cells, and the ring instrument only ever looks at one 32×32 tile.** It cannot
see repetition by construction.

So the instrument stops here, labelled for what it is: **a floor, not a verdict** (§13.2). It
catches the drawn keyline decisively — it corrected the spike's table, it found A-VAB's two
loops, and the seat independently confirmed both. It does not catch every construction a human
calls a keyline, and building a repetition proxy to close the gap is precisely the move §13.4
forbids.

---

## 7. THE BAR, AND THE RULING

**BAR NOT MET.** Round A: 4 of 4 culled — the check can fail. Round B: plant caught, **0 of 4
passed**.

LOOP-PROCESS §1.1.2 says a FAIL is a reprompt, not a stop. I am returning anyway, and naming the
trigger, because **the flip list is not executable inside this brief.** Its items:

- author six floor variants with the bond offset by half a stone between them, so no two
  adjacent cells share a joint at the same column;
- sand a traffic band down the centre of the corridor run, fade joints inside it, leave them at
  full depth only near the wall;
- pull A-HEB off salmon toward the walls' grey-brown and drop it two values;
- halve floor joint contrast relative to the wall's mortar;
- put the orcs' repairs on the floor — a cracked slab pinned flat, a salvaged baulk worn smooth.

**None of that is de-ringing.** It is authoring a floor set: new generation, new variants, a
value ruling, and a wear system. Executing it under a brief that says "produce de-ringed
versions of the four survivor floors" would be scope I was not given.

**Ruling trigger (b) — the bar.** The bar assumed the ring was what stood between these floors
and a pass. Two of the four never carried a ring and still fail; the other two fail on
constructions no ring test separates. The bar needs restating before another round is worth
running.

**The brief's own character trigger — fired, for A-VAB.** Before/after is in
`evidence/gate_before_after.png`, and the verdict surface is the twelve full captures in
`evidence/captures/`. Your eye picked A-VAB; the keyline is gone and the slab still reads on its
own value, but the seat says what remains still rings the slab. **That is a re-curation call and
it is yours.**

**What I would put to you, in one line each:**

1. **Is the §6.4 survivor set worth remediating at all?** Three separate seats have now said it
   does not read as one floor, and this session's seat culled all four before and after. The
   set exists to condition Stage 2 generations, and it is conditioning them toward a ring —
   22 of 24.
2. **A-VAB after surgery — keep, or re-curate?** It is the only tile that improved.
3. **B-KAB — the regenerated child is worse than the parent.** I would not promote it. The
   honest state is that B-KAB has no remediation and its original stays in the ledger.

---

## 8. WHAT I WOULD NOT CLAIM

- **Not that the floors are fixed.** Nothing passed a seat and nothing landed.
- **Not that the instrument is a verdict.** It is a floor with a measured, written-down limit,
  and the seat caught it twice.
- **Not that conditioning failed.** It did what it was asked and carried the parent's material —
  including the parent's ring. That is a finding about the reference, not the channel.
- **Not that A-HEB and C-GAB are good floors.** They are ring-free. The seat culled both.

---

## FILES

```
tools/floor_remediation/
  ring_instrument.py      the value-agnostic detector + 10-case control suite (--controls)
  remediate.py            per-tile route by measurement; surgery; provenance-linked outputs
  regenerate.py           B-KAB conditioned regeneration, 24 generations, ledgered
  capture_floors.py       lit in-scene captures; the floor is the only variable
  run_seat.py             the blind seat, two rounds, plant-controlled
  seat_prompt.txt         armed with the ring measurement; never given the bible
  make_gate_sheet.py      before/after crops for the gate (navigation, not a verdict surface)
  remediated/             the four remediated floors + MANIFEST.json (parent sha256 each)
  regen_bkab/             24 children, ledger.jsonl, RESULT.json
  controls/               the 10 synthetic control tiles
  evidence/
    before.json after.json mock.json remediation.json
    captures/             12 lit captures + manifest.json
    seat/                 roundA/roundB transcripts and results, verbatim
    gate_before_after.png
```

**The originals in `tools/pixellab/probe_6_4/survivors/` were not touched.** Every remediated
file carries its parent's sha256, and `remediate.py` re-verifies each against the survivor
manifest on every run.
