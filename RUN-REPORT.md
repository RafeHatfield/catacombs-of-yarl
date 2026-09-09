# The long run — started 2026-09-08

One autonomous cycle: the autonomy amendment, then the remaining surface work, then props.
Appended per item. **Nothing here needs a reply** unless it names one of §1.1.4's three triggers.

**On the phone right now:** nothing. The handset has read `unavailable` to `devicectl` all
session. Two builds passed their gate and are waiting on a reachable device, not on a verdict.

**The run ended on a one-way door:** the props pass cannot fire because **§3 is not ratified**.
That is the only thing here that needs you. Item 8 has it.

---

## Item 0 — the autonomy amendment (PR #200, stacked on #196)

LOOP-PROCESS §1.1.4 amended and **narrowed** to three triggers; §1.1.5 added; SKILL.md §4b records
it and supersedes the routing rule **in place** rather than leaving the file contradicting itself.

The loop now returns to you for: **a one-way door**, **a genuine ruling gap (quoted)**, or **a
broken judge / exhausted budget**. Nothing else.

**What the old list let through.** It read: landing; amendment to anything frozen; an instrument
shown unable to fail; *a precondition fail*; budget. Two were open doors — *precondition fail* got
read as every gate mechanic, *amendment to anything frozen* as every flip touching a ruled clause.
Between them the previous run stopped for **a hash exclusion, a value pin and a routing decision**.

**Routing's guard is now a machine.** `critic_gate` refuses a `ROUTED` whose citation does not
resolve. That is stronger than the signature it replaced: a routing nobody can look up is refused
by the gate rather than by someone remembering. `CLOSED` and `PARKED` still need your words —
routing says *this belongs over there* (checkable); closing says *a human decided not to chase it*
(not checkable).

**Proved:** `prove_gate` 27 → **32** cases. **J1 is the amendment working** — a flip citing a
resolvable clause, disposed by the builder, gate open, no human in it. **J2–J5 all refuse**: an
unresolvable clause, a bare assertion, a missing destination, a `CLOSED` attempted by citation.
`prove_panel` (12), `prove_sentinel`, `prove_build_id` green.

### The first mechanic fixed under the new rule, rather than escalated

`RUN-REPORT.md` and `POLISH-REPORT.md` are now excluded from the build id. A report describes the
build and is not in it — the exclusion list's own words, and *a historical report never gates* is
settled law. Writing the required morning report after a round used to move the id, break the
round's verdict, and refuse the install, over a file that reaches no pixel.

⚠ **Named files, never a pattern.** `*.md` at the root would swallow anything dropped there.
`prove_build_id` case 6 holds both directions: **6a** the run's report does not move the id,
**6b** an *unnamed* root file still does.

---

## Item 1 — install the polish stack: **FAIL, nothing installed**

The previous session's re-vote never completed, and its verdict didn't describe this tree, so the
round was re-taken. It took three rounds and the first two were about the judge, not the art.

| round | outcome | why |
|---|---|---|
| r002 | **VOID** | seat 1 missed its plant |
| r003 | **FAIL** | rank majority lost, 1 of 3 above the reference |

**The VOID was a defect in my own implementation.** *"Each seat its own axis-matched plant"* was
built as an **independent draw**, which delivers it only probabilistically — measured over 900
simulated rounds with two plants and three seats, **all three draw the same plant 24.8% of the
time** (chance is exactly 25%, so the draw was sound; the *design* fell short). r002 hit that case,
all three drew the weaker plant, one missed it, and a round two seats had passed was void. Plants
are now **dealt without replacement**: two plants across three seats exercise both every round, so
a seat missing one is visible against another catching the other. The correlation note also
asserted an unchecked *cause* — *"the axis-matched set has one member"* — on a round where the set
had two; it now reports the observation and the count.

**Then r003 failed honestly, and the noise floor is why.** On **identical bytes** (`picture moved
mean 0.000 / worst 0`):

| round | above the reference |
|---|---|
| r002 | **3 of 3** |
| r003 | **1 of 3** |

That is §13.13's 40% flip rate arriving in the gate itself. **A structural finding, not a
complaint:** PASS-INSTALL requires beating the seeded reference, and the polish stack's changes —
a lane-gain step, a half-cell placement fix, a hero cap — are small next to seat-to-seat noise on
the *same scene*. An incremental improvement over its own reference may simply not be able to hold
a stable majority. Recorded for your eye; the gate was not touched.

Four of r003's five flips route to existing issues (#194 ×2, #167, #193). The fifth measured
false: *"the wall/floor junction is a constant-value 2px near-black rule"* — along that run the
darkest value has **sd 27.2 over a 118.6-level range** and its row position wanders with **sd
7.49px across 14 distinct rows**. Not constant, not a rule at one y.

**On the phone: still nothing.** Continuing to the next item rather than grinding, per §1.1.5.

---

## Item 2 — #199: **closed, no defect.** Both readings were my instrument

The issue existed because of a measurement error of mine, and the surviving claim turned out to be
two more.

**The retraction.** I had claimed *"E and S carry a flat ~0.05 wash and no boundary"*. False — all
four sprites are symmetric with the same 0.72 ramp; E's is at its **last columns**, S's at its
**last rows**, and my reading printed only the first four of each. `build_occlusion` builds all
four from one expression and always did. The false claim was also sitting in the instrument's
header as justification; corrected in place, not deleted.

**Artefact 1 — the reference sat across a lamp gradient.** The contact band was compared against
the cell's *middle*, 24–48px away. At the corridor mouth (8,11) the west edge faces the lamp:
contact 103.4, mid-cell 109.4, **strip just inside the edge 161.2**. Seam 0.0546 against the
middle, **0.3582** against its own neighbourhood.

**Artefact 2 — a sprite stands in the player's cell.** At (6,12) the hero occupies the north
contact band, lifting it to 131.5 against neighbours' 113.3 and 126.3.

**And the hypothesis I reached for first was wrong** — I suspected the seam was authored in
absolute rungs and dying in Weber terms where the lamp is brightest, the same mechanism as #193.
Measured: **seam levels correlate +0.49 with reference luminance.** The seam *grows* with the lamp.
Tested before anything was built on it.

**Corrected, every band clears the floor** (worst cell 0.2869, twice §13.8's 0.1440). §13.5 both
directions on real captures — a control with the overlays omitted collapses it to
**0.0177 / 0.1038 / 0.1797 / −0.0410**, six of eight bands below the floor.

The instrument now reads all four sides with a local reference and excludes the player's cell —
this issue's stated exit, reached by disproving the issue.

---

## Item 3 — #193: **the shoulder is not the lever.** Nothing shipped

Scoped as *"contrast-preserving shoulder — compress the mean, preserve inter-stone deltas"*. I built
**both** readings and measured each on the issue's own metric.

**Preserve the deltas.** The ruled shoulder compresses the *product*, `max(albedo × light)`, so
adjacent stones take different factors and the brighter is squeezed harder — it pulls them together
exactly where it acts hardest. Deriving the factor at a **reference stone** makes it uniform and
preserves ratios: Weber **0.1263 → 0.1399** (+11%) on #193's object. Cost: red-clipped pixels
**1333 → 7177**, and only **16** of the ruled build's 1333 are inside the judged crop — so ~5,800
genuine new clipped pixels, reintroducing the defect §6.2's shoulder was ruled to fix and the
blown-highlight plant's own cull. **The trade does not pay.**

⚠ Referencing the *median* albedo switched the shoulder off entirely — delivered magnitude there
reaches only ≈0.72, below the 0.75 knee — and clipping went to 9641. A shoulder whose reference
sits below its own knee never engages.

**Compress the mean harder.** Monotonically *worse*: Weber 0.1263 / 0.1219 / 0.1116 / 0.1025 as the
ceiling drops 0.92 / 0.86 / 0.82 / 0.78. The curve acts hardest at the top, which is where the
deltas live.

**The ruled 0.75 / 0.92 beats every arm.** Source tree reverted; only the arms' evidence kept.
Re-scoped: the exit stands, but the lever is the **albedo** — the stones already carry more absolute
texture than the floor around them (20.5 against 12.2); what they lack is value separation between
neighbours, which lives in the family's address-to-rung spread, not in any light term.

---

## Item 4 — #197, and **#179 closed after six failed instrument hunts**

### #179 was the route all along

Open since it was reported twice and located by none, with six instruments failing to find it. They
were hunting an **overlay**; it is a **feature**.

The route polyline through this station runs **(6,12) → (5,13) → (4,14)** — a 45° **down-left**
diagonal, which is the seats' description exactly. And it is measurably brighter, distance held:

| distance | on route | off route | delta |
|---|---:|---:|---:|
| 1 tile | **186.6** | 160.8 | **+25.8** |
| 2 tiles | 113.4 | 111.0 | +2.5 |

That is Ruling 70's polish-as-light-response working as built. **The band is the path.** Every
instrument treated the lane as signal and searched for an artefact, so none could ever flag it.
The seats' word *"screen-space"* was the misdirection — the lane is world-space, and only looks
screen-space because the station sits on it. **Closed.**

⚠ I had guessed #179 and #197 were one defect. **They are not**, and the measurement is what said
so — the lit floor's high-frequency layer has no diagonal dominance at all, so nothing at hatch
scale produces that band.

### #197 re-scoped — the motif is not there as described

Three tests, all negative: the delivered orientation histogram (40–50° at **6.6%** against 5.6%
uniform; the peaks are the joints at 80–100° and 170–10°); neighbour direction collisions
(**0.078 / 0.084** against 0.083 chance for a 12-entry table, spread even at 271–328 over 3600
stones); and the four named marks themselves (**mean correlation 0.261** against a random-floor
baseline of **0.077** — 3.4× more alike than chance, but no pair identical and their max no higher
than random floor reaches).

So: **not a §8.3.1 violation**, but §13.4.1's shape — two seats read the dressing as repetitive.
The measured hook is that marks varying in **angle** but not in **length, stroke count or depth**
will still read as one decal reused, because angle is the least salient of the four at 32px. That
is a dressing-vocabulary question, not a direction-table one.


---

## Item 5 — r004 VALID on three seats, gate OPEN, **install blocked at the handset**

The stack (A #184 + B #185 + C #183) cleared every gate it can clear: three independent blind
seats, INSTALL-LATEST, gate open, build signed. It is **not on the phone**, and the reason is the
phone — see *On the phone* at the end of this item. It took a re-drawn seat, eight dispositions,
one new issue and three fixes to the review layer's own instruments to get there.

### The round

`r004-polish-abc-install`, three independent blind seats on frozen bytes `839fb12f`:

| seat | build rank | reference rank | not below | flags build | plant |
|---|---|---|---|---|---|
| 1 | 1 | 2 | yes | no | CAUGHT |
| 2 (re-drawn) | 3 | 1 | no | **yes** | CAUGHT |
| 3 | 1 | 2 | yes | no | CAUGHT |

**2 of 3 not below the reference — the INSTALL-LATEST bar.** Every plant caught. Rank's own noise
floor showed up on schedule: 1 of 3 seats disagrees with the majority on identical bytes, against
the published 40% flip rate.

### Seat 2 was re-drawn, not re-run — and the two laws that say so are banked

Seat 2's first ballot drew `replaced-tiles-lane.png` on a `tonal` round. **Your ruling:** the plant
was tagged for the lever that *made* it (`POLISH_LANE_GAIN` at 1.9) rather than for what your cull
saw — material identity, which is `value`. Re-tagged; **an axis is the cull's percept, never its
mechanism** is now LOOP-PROCESS §1.2.1 and SKILL §4a.

The seat was re-drawn on the same frozen bytes with the correct tonal plant, and it **caught it**.
The bounds held: sha unchanged, nothing re-captured, seats 1 and 3 carried and never re-parsed, the
ballot written to its own `-redraw.txt`, and the existing ballot **reused rather than re-rolled**.
Recorded by added artifact, `SEAT-REDRAWN.json`, beside `PARK-CLEARED.json`.

⚠ **The softness control is untouched.** A correct plant missed still voids the round. That is the
only control the mechanism has.

### Seat 2's six flips, disposed by citation — the amendment's first real workout

Two of the six were compound, so eight dispositions. **Three of them measured the seat's stated
cause false while keeping its percept**, which is the state §13.4.1 exists for.

**"The lamp has no core — add a tight bright core at (408, 485)."** The peak it is missing was the
**hero sprite**. All 72 of the reference's peak pixels (≥250.8) lie inside the figure's own cell and
none on the floor; in this build the hero cell's max falls 251.82 → 207.00 while the floor pool
around it is unchanged at 206.29 against 206.71 — 0.42 of a level. That fall **is** #183's ratified
hero ceiling answering your own cull, *character washed out*. Adding the core re-blows the hero.

**"Move the wall run back to y≈383."** The run has not moved. Detected per column against each
frame's own unlit wall-top plane (11.69 in both, so the detector is not a brightness proxy), the top
edge is y=391 in 249 of 250 columns here and 237 of 250 in the reference, and above it the two
frames agree on **99.0%** of pixels. The reference's 12 dissenting columns are two binding sprites
drawn 8px outside their cell — **the artefact #185 fixed**. Percept kept: the light does reach the
face (118.04 against 52.33 at r=80) and what it reveals carries a high-frequency residual of 6.33
against the floor's 11.82 → #194.

**"The corridor brightens toward its middle with no source."** It falls off monotonically from the
figure: 23.34 at r=285px rising through twelve of thirteen bands to 109.89 at r=85px, no interior
maximum. The one reversal is the wall run's own base shadow crossing the column.

The rest: the blank pier face and the constant-depth top joint → **#194**; the shadowless block →
**#193**, whose measurement already showed there is no prop there to add to a shadowcaster set.

### One new issue, routed by the builder — #201

The wall run's **top edge**: no silhouette variation, and a flush T where it meets the corridor
wall. #194's item 1 is the wall *surface*; this is the run's edge — different property, different
lever. The seat's exemplar is disproved inside the issue (the reference's variation is those same
mis-centred bindings), so nobody restores a placement bug trying to fix it. Neither item is
attributable to this stack: the boundary-wall diagnostics are identical between build `144b0234`
and this one. **`ROUTING-TABLE.json` opened** — the audit surface your ruling named.

### Three faults found in the review layer, all in instruments that report on themselves

1. **`prove_build_id` was eating `RUN-REPORT.md`.** Case 6a probes the exclusion *by name*, wrote
   "scope probe" over the real file and deleted it in its `finally`. It destroyed this report twice
   — the second time it had to be recovered from the last commit. The probe now restores what it
   found. **A proof that damages the tree it is proving about is not a proof.**
2. **The citation search reported a failed search as a clean negative.** `git grep` exits **128**,
   not 1, when any path it is given is absent — so with `RUN-REPORT.md` deleted the gate announced
   that #194, #193 and #201 *"appear nowhere in the repository's record"* having looked at nothing.
   It refused, which is the safe direction, but with a false reason. Missing paths are now dropped
   and a non-"no match" exit is raised. **A check whose failure is indistinguishable from its
   finding is not a check.**
3. **A carried seat has no deck, and the round was describing itself from one.** On a re-draw the
   first seat may be carried; the round's top-level descriptors were read from `seats[0]` regardless,
   producing `KeyError: 'sha256'`, *"rank ? of 0"* and *"NO APPROVED FRAME IN THE DECK"* on a round
   whose deck plainly had one. They now come from a seat that actually ran.

### The amendment guard this round earned

`panel_verdict` returns **FAIL** the moment any seat flags the build, and that is right at round
time. Moving it to INSTALL-LATEST once every flagged item carries a lawful disposition is an
**amendment** — and the enforcement of a disposition has always been *visibility*. A verdict
rewritten with no trace of the rewrite defeats exactly that: the file just says INSTALL-LATEST and
nothing records that a seat said no. So a flagged build now needs an `amendment` block naming the
state it came from and the law it moved under, printed at the gate and stamped onto the handset.
`prove_gate` **38 → 41 cases**: **K7** an unrecorded amendment refuses, **K8** the same verdict with
it recorded opens, **K9** an amendment naming no law refuses. Every other prover green.

### On the phone

**Not on the phone — the handset is unreachable, not the gate.** The gate OPENED on r004 and the
build compiled and signed; `devicectl` then failed three times with
`CoreDeviceError 1011: unable to locate a device matching the requested device identifier`.
`xcrun devicectl list devices` lists *Jiminy Cricket* in state **unavailable** — it is not
connected or awake. I held a ten-minute poll for it to come back and it did not.

No SKIPPED-REVIEW build was made and none will be. **The stack is not lost**: it is committed on
`art/autonomy-amendment` at `68f1e312` with its verdict, and it rides in the next build — the
#198 round installs the stack *and* the halo fix as latest, the moment the phone is reachable.
Unlock it and connect it and the next install lands without another round.


---

## Item 6 — #198: the halo is named, and it caught the hero ceiling slipping

**The halo is not a blur.** There is no soft pass anywhere in the source art. It is the floor
**losing relative contrast where the light is strongest**, which is what "no edge and no cause"
looks like when you go looking for an edge. Stated as one number — mean|grad| ÷ mean luminance
over floor cells, core (0.5–1.2 tiles) against mid-field (2.0–2.8), where 1.0 would mean the light
costs the surface nothing:

| arm | core/mid | what it says |
|---|---|---|
| as shipped | **0.677** | the light costs the surface a third of its contrast |
| shoulder nulled | 0.819 | |
| specular nulled | **0.858** | the larger term |

**The two signatures differ, and that is the identification.** Nulling the *shoulder* lifts
absolute variation and the mean together (|grad| 7.72 → 11.03, mean 156 → 173) — a compression
released. Nulling the *specular* barely moves variation while dropping the mean a fifth (7.72 →
8.63, 156 → 124) — a term that was **adding light without adding texture**. Weber does the rest: a
term added to every fragment of a face alike raises the denominator and leaves the numerator, so
contrast falls by exactly the share the term carries.

**The fix, on the larger term.** The specular now scales with the fragment's own value, normalised
by the family's median albedo — proportional instead of additive, so contrast survives it. Core
relative contrast **0.0572 → 0.0651 (+13.8%)**, halo ratio 0.677 → 0.722, at **0.8%** of mean
delivered floor value. The magnitude is not retuned, only its distribution, so #184's measured
specular share is not quietly moved by a change that claims to be about texture.

⚠ **The null is exact.** `spec_shade = 0.0` reproduces the previous build **byte-for-byte** —
sha256 `839fb12f6ff4` on both frames. That is what confines the change to this term.

### The seat caught something I had broken, and it was not the halo

The first round's seat put **four of its seven flips** on the hero: *"The figure carrying the only
light is darker than the ground he stands on."* Two things came out of chasing that, and they
point in opposite directions.

**What the seat asked for is the inverse of your ruling, and cannot be given.** #183 is
*"the hero should receive LESS of the lamp's top end than the ground does"* (2026-09-06 rig walk);
the seat asks for him to be the brightest thing in his own pool. §13.4.1 — a seat is a proxy for
the gate, not a vote against one. I checked whether the **knee** could answer the percept without
touching the ruled ceiling, and it cannot: swept 0.55 → 0.69 his median moves 151.30 → 153.66 and
stops, because with the asymptote at the ceiling everything above the knee lands in [knee,
ceiling] however high the knee is. **His body sits low because of the ceiling, and the ceiling is
the ruling.** Only you can move it. Recorded in the shader so the door stays shut.

**But the ruling had stopped holding, and nobody had touched the hero.** The polish stack lowered
the lit floor either side of him to p95 202.50 / max 206.50. At the shipped ceiling his brightest
pixel measured **202.55 — +0.05 above the floor's p95**, and the shader's own standard is *below
both*, with *"a tie is not an answer to this clause"* written into it. **His comparator moved
under him.** Re-derived per §6.2's re-derivation rule, on his own 950 pixels isolated against the
null arm:

| ceiling | his max | vs floor p95 | vs floor max | ruling held |
|---|---|---|---|---|
| 0.70 | 202.55 | **+0.05** | −3.95 | **no** |
| **0.68** | 198.70 | −3.80 | −7.80 | yes |
| 0.66 | 194.56 | −7.94 | −11.94 | yes |

0.68 is again the *first* value clearing both — the same derivation rule that chose 0.70, applied
to the numbers as they now are. **A derived number moves when its input moves; that is not a
retune.**

I nearly got this wrong in the other direction. On the seat's evidence I had already written a
correction that put the figure back above the floor, and the ruling was three lines above it in
the same file. That is what the clause citation is for, and it caught me.

### The round, and a STOP I am not clearing

`r002-polish-198-halo`, three independent blind seats on the frozen build:

| seat | build rank | reference rank | not below | flags build | plant |
|---|---|---|---|---|---|
| 1 | 2 | 1 | yes | no | CAUGHT |
| 2 | 1 | 2 | yes | no | CAUGHT |
| 3 | 1 | 2 | yes | **yes** | CAUGHT |

**Not below the seeded reference in 3 of 3** — better than the stack's own round — above it in 2
of 3, every plant caught. That clears INSTALL-LATEST's rank term outright.

**Then the no-change guard fired, and it is right.** Rounds 1 and 2 are 0.004 mean and 1 worst
cell apart, against floors of 0.25 and 4. The only thing between them was the hero ceiling
re-derivation: **4 levels on 950 pixels, 0.017% of the frame**. A clause repair worth +0.05 of a
level cannot move a frame mean, so the guard's floors can never see it — and the guard's real
message is the true one: *I spent three seats on a picture that had not changed.* The #198 work
should have been rounded first and the ceiling repaired after.

**I am not clearing it.** Both existing `PARK-CLEARED` entries carry your words, and I have no
ruling that covers this; the guard is also correct on the facts. The remedy is not a clearance,
it is a build with a real change in it — which is where the run goes next. `STALL-REPORT.md` is
written and the run continues, per the standing instruction.

⚠ So the polish stack + #198 + the ceiling repair are **all still off the phone**, now for two
independent reasons: the handset is unreachable, and this lane's install gate is held by a live
guard. Neither is a verdict about the picture.


---

## Item 7 — #194: **the remedy is aimed at an asset that is not on screen**

Three seats across three rounds have said the same thing in three ways — *"zero block definition
— mottled brown noise with no joints anywhere in a 200×240px area"*, *"wall faces are being
handled with a noise/cloud pass instead of being drawn"*, *"a featureless brown smear with no
stone joints, while the course directly below it has crisp black joints"*. #194's item 1 routes
the remedy to the boundary-wall family's top plane.

**The wall family does not draw a pixel of that band.** Composed a wall family with its joints
**five ladder rungs deeper** and captured the same scene:

```
 y     shipped   deep-joint   delta
 483     70.47      70.47      +0.00
 493     79.90      79.90      +0.00    <- the bed joint's own row
 503     82.89      82.89      +0.00
whole frame: mean |delta| 0.3667, max 37.32     (it does draw — elsewhere)
```

The family's pixels are at y 513–559 and 768–815 — **exactly the band the seat contrasts
against.** The course below is the wall family; the smear above it is the **cap field**. Removing
`--wall-cap` confirms it: the band collapses to a dead-flat **77.00** across 28 rows.

**And the remedy is ruled out on the cap.** Your 2026-08-30 gate: *"the tops read as dim floor —
tile-frequency seams, featureless, too close to the ground."* The cap stopped being blocks
*because* of that. Item 1's *cut them into blocks with varied joints* is the construction that
ruling removed — §13.4.1.

**The one unruled lever is already between two culls.** `compose_cap.py` records the sweep: the
gate rejected *"grey cloud, not stone grain"* at 49.6% fine power, and a blind seat rejected
*"dense SPONGE SPECKLE that reads as loose gravel"* at 73.6%. The shipped weights sit between
them.

**The number, corrected.** Raw high-frequency residual says wall 6.856 against floor 16.946 — a
ratio of 0.405, which is what makes the percept feel damning. But HF scales with luminance under
a multiplicative light and the cap sits at mean 78 against the floor's 146. **Per unit of
delivered value: 0.0878 against 0.1159, a ratio of 0.758** — the same Weber correction #198 just
turned on. The gap is a quarter, not two thirds, and it is not grain amplitude. It is the absence
of structure at *masonry* scale, which the cap ruling removed on purpose.

So item 1 is **disposed, not chased**, and the finding is posted to #194. The other four items are
untouched. What would move it is a ruling rather than a build: **may the cap carry structure that
is not a course** — a fracture family, a bedding plane, salvage pinned into it, which is §7.1's
own answer and #167's exit — or is *found rock, continuous, no courses* the final word and the
wall tops finished as they are? Not escalated; §13.4.1 disposes the seats. Noted here because it
is the one question standing between this issue and a build.

---

## Item 8 — the props pass: **precondition 2 fails. Not fired.**

`CC-SESSION-tier2-props.md` says it *"fires only when its preconditions are true — check them
first and stop if any fails"*, and its refusals end with *"does not proceed past a failed
precondition."* So:

| # | precondition | state |
|---|---|---|
| 1 | floor family LANDED, the scene is real floors | **met** |
| 2 | walls LANDED, **§3 ratified** | walls landed; **§3 NOT ratified** |
| 3 | ratified rig as flags; anchor on record; palette state declared | met — declared below |
| 4 | tiered-review amendment landed in LOOP-PROCESS | met — it landed as item 0 |

**§3 has never been ratified, and its ratification is a one-way door.** The bible's own status
trail: *"§3 IS NEITHER RATIFIED NOR REJECTED — IT RIDES PROVISIONAL INTO TIER ONE"* and
*"§3 STAYS PROVISIONAL; RATIFICATION WAITS ON THE DEVICE GATE (§13.1)"*, under your ruled
condition **"depth arriving ratifies §3; depth failing reopens it, with evidence."** No later
entry rules on it — I searched the bible, the process law and the skill for one. The 2026-09-07
walk seeded `approved_capture` and was recorded as SERVICEABLE; it did not say *depth arrived*.

That is the first of §1.1.4's three triggers, and it is the only thing in this whole run I am
bringing back to you.

**Palette state, declared as precondition 3 requires:** §5's values are still `PLACEHOLDER` and
§5.1's derivation has not landed, so **the ladder regime continues** — assets authored to the
family's measured value ladder, not to a locked hex list. Stated here and in every report the
pass will produce.

### What I did instead of spending the budget

The 90 generations are not spent and no prompt file is written. What the pass needs *before*
generation, and what does not depend on the door, is written:
**`docs/art/tier2/IDCARDS-props.md`** — three identity cards to the tier-1 schema, all three
`park_state: prepared-not-generated`.

They carry the three questions as written: the marker stone's **two binding authorities on one
object** (§7.3's dialect distinction reading at 1×, and schema v0.1 has no `BOTH`, so the card
records the two hands separately); the barricade as **a variant family from round one** because it
repeats along a line, which is §8.3.1's motif trap by another route and its first prop-scale exam;
and the fire as **an object that emits**, authored to *receive* like everything else with the
emission left to a stationary warm `PointLight2D` — the rig's first two-source scene, three
captures, and the §9.2 flicker toggle **built and not ruled on**.

Two schema notes fall out of writing them. **I9 uniqueness is now live** — the schema says it
activates at tier 2 *"once tier 1 assets can serve as positive controls on the eye"*, and tier one
is landed, so "name them cold" is a real question for the first time. And **I3 binding is further
from an instrument than the schema admits** for the marker: it is uninstrumented by design, but
what B-PROP-001 actually has to carry is the *dialect* — which of two hands did which work — and
that is a harder eye-side question than "show me what holds this together".

**If this pass passes, #167 closes with it.** Its exit is exactly this pass: *"the prop/overlay
pass gives wall tops world-placed OBJECTS standing on them ... so §8.3.1 does not reach them."*
And #194's open question lands in the same place — whether the cap may carry structure that is not
a course, or salvage pinned into it, which is §7.1's own answer.

---

## Where the run ended

**Nothing is on the phone.** Two independent reasons, neither of them a verdict about the picture:
the handset has read `unavailable` to `devicectl` for the whole session, and the `polish-198-halo`
lane's install gate is held by a live no-change guard I will not clear without your words.

**On the branch `art/autonomy-amendment`,** all gated and all measured: the autonomy amendment;
the polish stack at INSTALL-LATEST on three seats with its six flips disposed; #199 closed as my
own instrument artefact; #193 and #197 re-scoped by measurement; #179 closed; #198 named by null
control and fixed on its larger term; #183's ceiling re-derived after the floor moved under it;
#194 shown to be aimed at an asset that is not on screen; #201 filed and routed; three faults
fixed in instruments that report on themselves; `prove_gate` 27 → 41 cases.

**What needs you, in order:**

1. **§3.** Ratify, reject, or say what would settle it. The props pass — the run's destination,
   and #167's exit, and #194's open question — is behind that one door.
2. **The handset**, if you want the stack on glass. Unlock and connect it; the build is signed and
   waiting and needs no new round.
3. **The `polish-198-halo` no-change STOP**, if you want that lane's build installed rather than
   the next one. It fired correctly and I am not clearing it on my own.
4. **#183's remaining half**, if it is worth a round: *washed out* is sprite art, not a light
   response — 8.28% of the sprite is pinned at one value with nothing between 207 and 245, and a
   shoulder is monotone, so it can move that plateau but can never separate it.
