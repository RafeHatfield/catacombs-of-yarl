# Catacombs of Yarl / The Under-Warden — ART-BIBLE v0

**Status: v0.12 — DRAFT. Two clauses have been derived from rendered assets on the device (§6.3)
or ruled at the gate on them (§8.3); §6.5 and §3.1 are measured against the asset bar and ruled,
awaiting the device gate; §3 remains under test and ratifies at that gate. Everything else in
this document still has not been derived.**

This bible is written *before* pixel work, deliberately. It records decisions taken in
conversation during Phase 1–3 of the art-direction rework (2026-08). It graduates to **v1**
only when the Phase 5 pilot has ratified the clauses marked PROVISIONAL and filled the
clauses marked PLACEHOLDER with derived values.

**Governing principle, inherited from Gemfall: no law is ratified ahead of its derivation.**
Where a rule has a design purpose but no measurement behind it yet, it is marked PLACEHOLDER
and says so. A bible that states numbers it never measured is worse than one with gaps,
because the gaps are honest and the numbers are not.

**Clause status vocabulary:**

| Marker             | Meaning                                                      |
| ------------------ | ------------------------------------------------------------ |
| **LOCKED**         | Decided and ratified. Changes only by explicit revision with a recorded reason. |
| **PROVISIONAL**    | Decided as a direction, pending pilot evidence. Expected to survive; may not. |
| **PLACEHOLDER**    | A rule with a stated design purpose and no derived value. Not law. Not usable as a gate. |
| **RETIRED**        | Formerly law, now struck, kept in place with the evidence that struck it. |
| **NOT LEGISLATED** | Measured or observed, deliberately not turned into a rule.   |

---

## 1. Register — LOCKED (Phase 1 sign-off, 2026-08)

> **The world does not notice you.**
>
> The Paths of the Dead are administered, not haunted. They have been in continuous heavy use
> since before anyone's records begin, and no one has ever cared for them. Nothing here is
> arranged for your benefit — not the light, not the horror, not the way out.
>
> - **The art plays it straight.** The world can be absurd; it is never cute. Every joke in
>   this game comes from Sasha and Hollowmark, and the world's refusal to join in is what
>   makes them a pair.
> - **Nothing is ruined; things are used up.** Surfaces record traffic. Where there is decay,
>   it means no one walks there — and that is information the player can use.
> - **Everything is held.** Nothing in the Paths is monolithic or self-supporting. Bound,
>   strapped, pinned, sealed, tagged. The world is made the way Marya was made.
> - **The light withdraws as you descend.** You arrive as the only thing here that burns. You
>   end somewhere lit for its own purposes.
> - **Sasha and Hollowmark are the warmest thing on screen, always.**
> - **Nothing is staged.** The horror is in the corner, tagged, and the corridor goes past it.
>
> **Anti-references:** Oryx's adventure-cheerfulness. And the off-the-shelf bureaucratic-dread
> kit — beige, rubber stamps, Kafka-by-numbers — which is the same trap in a different corpus.

### 1.1 The division of labour — LOCKED

**The art plays it completely straight. The voice carries all the warmth.**

Sasha and Hollowmark are the only funny thing in the game. The dungeon never winks. Every
joke on screen comes out of the two of them, and the world's total refusal to join in is what
makes them a pair rather than a tone.

This diagnoses the previous track's failure more precisely than "wrong tone." Oryx's art was
doing comedy *too* — a funny voice on top of a funny world, so the voice had nothing to push
against and the whole thing collapsed toward whimsy. It was not a mismatch. It was
**redundancy**: the art was making the writing's job impossible.

**The expression budget for world creatures is zero — RULED from the study pass.** The asset
bar's seriousness is substantially this one refusal: helmets, hoods, shadowed cowls, blank
skulls; nothing smiles, nothing emotes. Yarl adopts it as law: **world creatures do not have
readable faces.** Hidden, shadowed, or structural. The one face in this game belongs to Sasha,
because the warmth is his to carry — and even his is spent sparingly at sprite scale.
(Portraits, if the game ever wants them, are the sanctioned place for faces at dialogue range —
see §16.)

### 1.2 The generative test — LOCKED

**If a rule cannot tell you how to draw a thing nobody has drawn before, it is a bad rule and
it gets cut.**

The register is a function from arbitrary noun to Yarl asset. This is the property the
previous track lacked: there was no rule that could tell you what an Oryx-conformant version
of an unprecedented object looked like, only a corpus you could search and fail to find one in.

Worked example — a gold-encrusted bidet, which is the deliberately absurd test case:

- *Everything is held* — the gold is not inlaid, it is fixed on: pinned, banded, clamped by
  someone who wanted it not to come off. Visible hardware. Plumbing strapped to something
  structural.
- *Used up, not ruined* — gold worn through to base metal wherever a hand or hip has touched
  it. Polished bright on contact surfaces, dull and grimed everywhere else. Basin dished.
- *Nothing is staged* — not on a plinth in a rotunda. In a corridor, against a wall, slightly
  in the way.
- *Tagged* — it has an inventory number. Someone filed this thing.
- *Light* — it does not glow. It catches whatever light the region provides.

The constraints did not restrict the content. They told us how to draw content nobody had
considered. **Unrestricted content is a consequence of the bible being generative, not of the
gates being soft.** Yarl's gates are as strict as Gemfall's.

### 1.3 The named trap — LOCKED

**External-corpus matching is forbidden as a bar.**

The previous track measured conformance to a fixed external corpus (Oryx 16-bit fantasy).
Every drift was a defect, no rule generalised, and every asset was a fight. Nothing in the
instrument stack ever asked *"does this look like Yarl?"* — only *"does this match Oryx?"*

**The lesson is NOT that strictness was the problem.** Gemfall is stricter than the Oryx track
was — a locked palette with zero off-palette pixels tolerated, deterministic conformance, no
hand-edit carve-out — and it produces assets nightly. The variable is **who owns the target.**
Yarl conformed to a corpus someone else shipped, where the answer to "is this right?" lived in
files we did not write. Gemfall conforms to a document its author wrote, which can be amended
when it is wrong and can answer questions about assets nobody has drawn yet.

**This bible is the target. Nothing external is.**

Quality comparison against shipped games (§13.3) is a different operation from style
conformance and is permitted. The distinction is thin and is stated explicitly there.

---

## 2. Scope and derivation population — LOCKED

**This bible is written for five regions and derived from one.**

Build target is a **demo: the first region (the Boundary, floors 1–5), built to a finish
standard.** This aligns with the settled monetisation shape — first region free with
persistence, single unlock — so the demo is not a detour from the game; it is the part that
has to be best anyway, because it sells the other twenty floors.

Consequences, binding:

1. **Region-identity *mechanisms* are in scope now** (§5.2 reserved slots, §6.2 light arc,
   §7.3 binding authority), because they constrain how the Boundary is drawn.
2. **Only the Boundary's *values* are ratified.** Every other region's values are PLACEHOLDER
   and will be derived when that region is built.
3. **The derivation population for every constant in this document is the Boundary corpus.**
   Per Gemfall's Ruling 56: an instrument's verdict is valid only over the population it was
   derived from. Applying a Boundary-derived constant to a Weighing asset is a finding about
   the instrument, not about the asset.

### 2.1 The scope trap — named in advance

**Five floors to a finish standard is not obviously less work than twenty-five to an adequate
one**, and there is no next region forcing a stop, so the bar can drift upward indefinitely.

The park states apply and are law here: **"finalised, not iterated"** (stop improving this, it
is done) and **"prepared, not generated"** (staged, deliberately not spent on). A tier that has
been declared finalised does not reopen because a later tier raised the standard.

---

## 3. Projection and grid — PROVISIONAL, riding into tier one

- **Orthogonal square grid. Portrait orientation. Not isometric.**
- **Volume lives in what stands up, not in the ground plane.** Objects and walls present
  exactly two visible planes: a **front face** and a **top surface**. The floor stays flat.

**Rationale.** Isometry is a way of showing volume, and its cost is paid entirely by the ground
plane — diagonal grids waste screen corners, visible tile count drops, and portrait is the
worst aspect ratio for it because the diamond's long axis runs the wrong way. The benefit
shows up in objects and walls, which gain a second face and start reading as things that
occupy space. **An isometric floor tile buys nothing; it is a diamond instead of a square.**
Orthogonal ground plus two-plane volume keeps the benefit and refuses the cost.

The two-plane rule survives from the retired Oryx track unchanged. It was never an Oryx rule —
it was a way to draw volume without paying isometry's tax, and it is re-adopted on its own
merits.

**STATUS (2026-08-26): PROVISIONAL — UNDER ACTIVE TEST BY THE SIGHTED ROUND.**

The composition spike's condition fired: two-plane construction with invented numbers, judged
absolutely, in an all-top adversarial scene, did not deliver depth — eight rounds, eight noes,
every seat asking for a side face. **Three confounds are named against that evidence, and they
are why the section is under test rather than struck:**

1. **The scene contained zero §3-qualifying face cells.** A §2.2 violation in spirit: the
   shipping game is rooms and reveals, not only chokepoints.
2. **The seats judged in the absolute, with no genre grammar.** §13.3's comparative frame exists
   for exactly this.
3. **The construction numbers were invented**, where the bars' are measurable.

**Declared criterion, before the sighted round runs:** recipe-driven construction — measured
from the bars, pixels never crossing — judged **comparatively**, in a fair mixed scene. **Depth
arriving ratifies §3. Depth failing at budget reopens §3 for real**, side faces become a live
design question, and the licensing fallback becomes a real option to be argued honestly. Last
resort, but named — and named before the round, not after it.

**The reopening evidence stands exactly as recorded below; what it now feeds is that test rather
than an immediate ruling.**

**STATUS TRAIL (2026-08-27, AT THE DEVICE GATE): FAIL. §3 IS NEITHER RATIFIED NOR REJECTED —
IT RIDES PROVISIONAL INTO TIER ONE, per this bible's original sequencing, carrying the recipe,
the flat-top rule (§3.1) and the Q3 control finding intact.**

Rafe's verdict, recorded in his own words because a trail that paraphrases a gate is not a
trail:

> **"Gate verdict: FAIL — the phone overrules the stills."**
> **"two seats ranked this above the bar; the device says otherwise; §13.2 vindicated again."**

**What this does and does not overturn.** It does not touch the Q3 control finding below — the
bar's north–south walls still have no thickness, and that measurement is independent of whether
Yarl's execution is good enough. It does not touch §3.1 or §6.5, which were ruled on the
round's measurements rather than on its verdict. **What it overturns is the inference that
two blind seats ranking the candidate above the bar meant the construction was finished.** It
did not, and the phone said so.

**Two laws come out of the gate and are recorded where they belong:** the motif trap extends to
wall material (§8.3), and the rig gets a readability-tuning pass before any asset is judged
through it (§6.2). **Both are consequences of looking at this on a phone at gameplay distance,
which is the one thing no still and no seat in this round ever did.**

---

**STATUS TRAIL (2026-08-27): THE PREMISE IS VINDICATED BY THE Q3 CONTROL. §3 STAYS
PROVISIONAL; RATIFICATION WAITS ON THE DEVICE GATE (§13.1).**

The sighted round asked its seats a control question every round — *does either image show a
side face?* — and the answer came back **NEITHER, in every round**. That is the finding, because
the second image was **the asset bar**, running at full commercial quality:

> *"B's north–south wall (x=0–13) is flat 90-gray for all 240 rows with a single 71 seam at
> x=14 and no face anywhere — **a vertical wall in B has literally zero thickness**."* — r5
> *"its entire east flank is one native pixel of joint line, while its north-facing sibling gets
> 24 native px of face"* — r3

**The standard we measure against carries the exact limitation §3 imposes.** Two independent
seats measured it, unasked, never having been shown this section and with no idea they were
auditing a bible clause. **The eight rounds of "no thickness" were therefore not evidence that
two-plane construction fails — they were evidence that Yarl was executing it badly**, against a
bar that has the same missing plane and does not suffer for it.

**What was actually wrong was the value stack, and it was inverted** — see §6.5, which this
round produced. In rounds 4 and 5 two independent blind seats ranked the Yarl candidate **above
the bar** on wall depth, unhedged and with no cull, once the stack was corrected. §13.3's bar is
*"the answer must be Yarl, or a tie"*.

⚠ **QUALIFIED, and the qualification is carried at full strength.** The plant control was mixed:
rejected by 4 of the 5 seats that saw it, named on its own axis only once, and waved through by
one seat — which voided round 2 (§4). **The favourable result is evidence, not a validated
pass, and is weighed at 4-of-5-seat strength exactly as the round marked it.** `REPORT.md` §3a.

**RULED (Rafe, 2026-08-27): the premise stands vindicated; the clause is not yet ratified.**
§13.1 governs: in-scene, on device, by eye. A device build of the rounds-4/5 configuration is
owed and is the next step — the round's own captures are headless at device pixel size and are
**round evidence, not gate evidence** (`REPORT.md` §4a). §3 graduates from PROVISIONAL when that
walk happens and not before.

**STATUS TRAIL (2026-08-26): THE RULED CONDITION FIRED. §3 WAS REOPENED, WITH EVIDENCE — and
what replaces it, if anything, is Rafe's ruling and not the spike's.**

*Kept below in full. The reopening was correct on its evidence; what the sighted round changed
is the diagnosis, not the honesty of the record — and the confound named first at the time,
**"the construction numbers were invented, where the bars' are measurable"**, is exactly the one
that turned out to be carrying the failure.*

The ruling was *"depth arriving ratifies §3; depth failing reopens it with evidence"*, against
two rounds spent on plane-boundary occlusion and wall-top value separation with south-facing
front faces present in scene. Both rounds ran. **Depth did not arrive.** Eight blind critic
rounds have now answered the thickness question and every one of them answered no; the last, on
the arm it ranked FIRST of five, said:

> *"the reveal at the boundary reads as a shadow gap rather than a cap, so you still cannot
> distinguish a wall top from a wall face anywhere in the image."*

**The reopening rests on that arm and not on the two constructions the same round showed to be
mistakes.** Round 8 tried a coping course and a joint-deepening pass; the seat ranked both BELOW
the arm that had neither, and both failures are diagnosed in
`tools/composition_spike/SPIKE.md` §5.7. The arm that ranked first carried only the two ruled
variables at their best measured settings, and it still failed. That is the evidence.

What every seat asked for instead, unprompted and without ever being shown this section, was a
**side face** — *"no cap, no cross-section, and no way to tell the top of a wall from the face of
it"* — which is the one plane §3 forbids.

**Previous status, kept because a status trail that overwrites itself is not a trail:**
**STANDS UNAMENDED, PENDING EVIDENCE (Rafe, 2026-08-26).** The composition spike ran
six blind critic rounds against composed two-plane walls and the thickness question came back
**no on every arm in every round** — *"none of them has a wall with a top and a side, so the
whole set is a flat pattern with a path tinted through it."* Six independent seats asked for a
**side face**, unprompted, none having been shown this section.

Two further rounds are ruled to run on plane-boundary occlusion and wall-top value separation,
in a scene where south-facing front faces are actually present — the review corridor could only
ever show a face on 7.3% of its wall cells, which is what every one of those six verdicts rested
on. **Depth arriving ratifies §3. Depth failing reopens it, with evidence.** The evidence trail
is `tools/composition_spike/SPIKE.md`.

**Why PROVISIONAL:** this has not been tested on a Yarl asset at Yarl's density. The Phase 5
pilot builds floors and walls first, which makes it the natural probe. If two-plane walls in a
portrait orthogonal grid do not deliver the volume we want, we find out in the cheapest tier,
before a single prop or creature exists.

**Isometric *objects* are not forbidden** — the ban is on an isometric map.

**Corroboration:** the asset bar's walls are two-plane — front face plus top band, no side
face — running at full commercial quality. The provisional projection has a shipped precedent
in the very library named as the per-asset bar. Still ratified only by the pilot.

**And the corroboration is now measured rather than asserted.** The sighted round's Q3 control
had two independent seats read the bar's own north–south walls and report **zero face** — *"a
vertical wall in B has literally zero thickness"*. The shipped precedent carries §3's limitation
exactly, which is the status trail's 2026-08-27 entry above.

### 3.1 The top plane is FLAT — RULED (Rafe, 2026-08-27). A top surface is not face material re-toned.

**A plane is not made by changing the value of a texture. It is made by changing what the
texture is a picture of.**

The face is coursed because you are looking at *courses*. The top is not, because you are
looking at *the tops of stones*. Re-toning the same coursed masonry and laying it flat produces
a surface that reads as more elevation, whatever value it is given.

**Two blind seats found this independently, neither shown the other's verdict, and both culled
`wrong-projection` for it:**

> *"A top surface does not show five courses of face-brick."*
> *"the brick coursing above it has the same pitch, proportion and orientation as below, so it
> is not a top surface — **it is more face**."*

**And no value change reaches it.** The round that was culled already had §6.5's value stack
broadly right — one of those same seats measured the bar at *"face at 0.49× the top"* and
proposed §6.5's own ratio back as its flip list — and culled the arm anyway. **A plane textured
like elevation reads as elevation at any value.** This clause therefore sits with the projection
rule it protects, not with the values it is independent of.

**Register derivation — §8.1 wear, the same derivation §6.5 runs on.** Decay is traffic-driven
and **nothing walks on a wall top**. A surface nothing has ever touched has accumulated no
incident, so it carries nothing but the joints between the blocks it is made of. A material
derivation: it declares no light direction and survives §6.3.

**As built:** plane flat at its target value, 2 px joints on a 16 px grid at 0.78 of the plane,
phase-offset per variant. Measured on the bar at 91.5% of top-plane pixels holding one exact
value, joints at half-tile pitch. `tools/sighted_round/WALL-RECIPE.md` §2.3.

⚠ **Worth stating why this matters beyond walls: it is §8.3 in different clothes.** Coursing on
a top plane is *material describing the wrong thing*, repeated in every cell. The tile was not
badly drawn — it was a picture of the wrong surface, thirty times over.

---

## 4. Canvas and density — PLACEHOLDER

**No canvas size, tile size, or density ratio in this document is derived. All values below
are the *shape* of the rules, not the rules.**

### 4.1 The density problem is Yarl's alone — LOCKED (as a stated design purpose)

Yarl and Gemfall share a reference device (iPhone SE, 750×1334, portrait) and differ in
**information density**. Gemfall's screen has room to breathe. Yarl's must hold floor, walls,
props, multiple creatures, the player unit, and UI simultaneously.

The transferable consequence is not a number. It is that **the isolation assumption does not
hold.** Gemfall can largely judge an asset on its own merits. Yarl cannot: the real question is
always whether this creature reads against that floor, next to that prop, beside three other
creatures. Every readability rule in this bible must be asked *"does this survive a busy
screen?"* and a rule that only holds in isolation is not a rule.

**Expect Yarl's readability rules to be harsher than Gemfall's** in ways that feel like a
downgrade in isolation: less interior detail, stronger silhouettes, larger value separation,
more environmental restraint so creatures can win the contrast fight. **An asset that would
pass Gemfall's bar can be correctly rejected here for being too good** — too much lovely
detail, competing for attention it is not entitled to.

This agrees with the register rather than fighting it. *Nothing is staged* and *Sasha and
Hollowmark are the warmest thing on screen* are both, read one way, attention-budget rules.

### 4.2 Density is a ratio between layers — PLACEHOLDER

Adopted in shape from Gemfall §2.6: density is legislated as a **relationship between layers**,
never as an absolute per layer. The environment is quieter than the figures. Ratios are
PLACEHOLDER pending the pilot.

**Quiet floors, detail at the edges — corroborated by the bar.** The asset bar's floors are
large flat fields with sparse texture events, and the events sit at walls and corners while
centres stay open. Their reason is readability. Our fiction supplies a better one: **traffic
keeps the centre clear** (§8.2's channel). Bar and register agree about where detail belongs.

### 4.3 Canvas sizes — PLACEHOLDER

Native canvas per layer, and the integer scale factor to logical pixels, are derived at Phase 5
against the reference device. **Integer scaling only; no fractional scaling baked into any
asset; nearest-neighbour filtering; no anti-aliasing.** That much is LOCKED. The numbers are not.

---

## 5. Palette — philosophy LOCKED, values PLACEHOLDER

### 5.1 One global palette, zero-mercy gate — LOCKED

One palette governs the whole game. Every opaque pixel is an exact bible hex or the asset is
rejected outright. Dithering between adjacent ramp steps is permitted. New colours require a
revision of this document.

This is adopted from Gemfall wholesale and for a mechanical reason as much as an aesthetic
one: **style-conditioned generation requires on-palette reference images**, so a locked palette
is what makes the generation recipe work at all.

### 5.2 Shared spine plus reserved region slots — LOCKED (mechanism), PLACEHOLDER (values)

The register requires five distinct regions and a light that withdraws with depth. Five
separate palettes would mean five gates, five reference sets, five chances for the regions to
look like different games, and a player unit that must be legal in all of them regardless.

Instead, keyed on **region** the way Gemfall's gem slots are keyed on **layer**:

- **A shared neutral spine**, common to all twenty-five floors: stone, brass, bone, grime, and
  the dark ramps. This is the cohesion. It is what makes a Yarl asset recognisable as a Yarl
  asset anywhere in the game.
- **A small reserved allocation per region**, legal only on assets belonging to that region.
  The Boundary's fire-warms are illegal in the Weighing; the Weighing's institutional greys are
  illegal in the Boundary. One gate, one flag, five dialects.

**Only the spine and the Boundary's reserved slots are derived at the pilot.** The other four
regions' allocations are PLACEHOLDER.

**Known exposure:** the failure mode of a shared spine is that it flattens the regions into one
another. This is the first thing the pilot should be asked about once a second region exists.

### 5.3 The light arc is an allocation shift, not a palette change — LOCKED (mechanism)

The descent is expressed as **the warm slots' share of canvas shrinking floor by floor** while
cold and neutral share grows. Same spine throughout. This makes the register's central
progression a single measurable number per asset rather than a matter of taste.

Threshold values: PLACEHOLDER. It is not yet known whether a defensible threshold exists; per
Gemfall's Ruling 70, **"no defensible threshold" is a complete calibration result**, and a
refusal is preferred to a number with a story attached.

### 5.4 Warmth is reserved — LOCKED, with one deliberate exception

Warmth belongs to Sasha and Hollowmark. Brass, skin, and firelight against a world that trends
colder and flatter with depth. This serves theme (a living man with the wrong gods in someone
else's filing system), readability (the player unit is never lost on a small screen), and the
difficulty curve (the world visually withdraws its warmth as it gets worse) with one decision.

**The Boundary is the single exception, and it is deliberate.** The Unshriven keep fires. They
are the last people down here who still tend one. The moment the player leaves them behind, the
warmth withdrawal begins in earnest and never reverses. **The Boundary is not a violation of
the rule; it is the rule's opening statement.**

**The warmth reservation is one instance of a general law, confirmed at three scales by the
asset bar: chroma is signal.** Per sprite: two or three material families and **one** saturated
accent doing identity work. Per room: long neutral stretches, then one saturated event that
*is* the room's identity. Per item: hue carries state, not decoration. A saturated pixel should
mean something happened. General richness is forbidden — saturation spent everywhere identifies
nothing.

### 5.5 Reference neutrality is a criterion — RULED (2026-08-26)

§5.1 adopts a locked palette partly because **style-conditioned generation requires on-palette
reference images**. This clause governs *which* images may be that reference, and it is a
measured rule, not a preference.

**Composition propagates with material.** Measured at 12/12 on the wall campaign: every child of
a charactered reference — A-VAB's recessed frame — inherited its *composition*, not only its
material. A reference does not hand down a surface; it hands down whatever it is a picture of.

References therefore divide by job, and the division is load-bearing:

- **Compositionally neutral references are style parents.** ~~C-GAB's crack-through-a-field is
  the shape of one~~ — a material, evenly presented, that is a picture of nothing in particular.
- **Charactered references are prop stock.** One-off assets in waiting — never conditioning
  parents, however good they are as images.

**The seed corpus wants the boring ones.** A reference chosen because it is handsome is a
composition about to be copied twelve times.

> **CRITERION SHARPENED — RULED (Rafe, 2026-08-27, at the gate). Compositionally neutral is not
> enough. The criterion is INCIDENT-FREE: §8.3.**
>
> The example struck through above is why. *Crack-through-a-field* was offered as the very shape
> of a neutral parent — and the gate ruled that same tile a **frame at field scale**. A crack is
> a *composition* of nothing in particular and it is still an **incident**, and §8.3 measures
> what happens to an incident when it is tiled: **repetition converts accident into intent.**
> One crack is an accident; the same crack in every cell is a motif, and the eye reads the
> pattern whatever the crack's quality.
>
> So the division by job survives and its test gets stricter. **A style parent carries material
> and nothing that happened to it.** Incident — cracks, wear, marks, the §8.2.1 channel — is not
> a property of a good parent; it is what the instance system adds later, per §8.3.

**CROSS-CONFIRMED (2026-08-27), by a different instrument on a different campaign.** This
clause's composition finding was measured 12/12 on the *wall* campaign, by tracing children back
to their reference. A blind seat then rediscovered it from the opposite end: shown the *floor*
campaign's lit corridor, never given this bible, never told which tile was which, it culled
A-VAB and named the construction —

> *"Two concentric closed rectangles inset in the middle of every tile, each one width and one
> value the whole way round — **the tile is a framed plaque**, and the moss clumps repeat at the
> same corners to confirm it."*

*A framed plaque* is *a recessed frame* arrived at independently, in a different medium, by an
instrument with no access to the first result. The clause is not resting on one campaign.

**Corpus status — RULED (Rafe, 2026-08-27), superseding the 2026-08-26 paragraph.** The four
§6.4 survivors divide by job, and the division is now assigned rather than pending:

| survivor | role | why |
|---|---|---|
| **C-GAB** | **primary style parent** — retained under screening; see the corpus note below | compositionally neutral ⚠ *"carries no ring, at any value" is **superseded**: RULED a **frame at field scale** (2026-08-27). Retained because references never ship, not because it meets the sharpened §8.3 criterion* |
| **A-HEB** | **secondary style parent** | a joint network, not a keyline; carries no ring |
| **A-VAB** | **prop stock — never a conditioning parent** | charactered. **The ruling holds regardless of surgery:** de-ringing removes a keyline, it does not make a framed plaque neutral, and it is the composition that propagates |
| **B-KAB** | **retired from conditioning. No remediation.** | 24 children conditioned on it came back 22 ringed; the regenerated candidate was culled by the seat and is **not promoted**. Its original stays in the ledger, un-remediated, and nothing conditions on it |

**The 2026-08-26 measurement in this paragraph was wrong and is corrected.** It read *"a uniform
~3px near-black ring, B-KAB at luminance 14 against a median of 130"* — a value framing, from an
instrument that thresholded luminance at 0.30× the tile median. §12.1's own worked example holds
the prohibition is value-agnostic. Measured on geometry instead: **two of the four carry rings,
not one and not four.** A-VAB carries *two* closed 1px loops (76 px and 32 px, each one width
the whole way round) at 0.48× median, which the value threshold could not see; B-KAB carries one
closed 1px loop of 62 px. A-HEB and C-GAB carry mortar joint networks and **never carried a ring
at all**. Instrument, controls and evidence: `tools/floor_remediation/`.

Remediated, provenance-linked versions supersede an original **upon Rafe's re-curation**; the
originals stay in the ledger untouched, because a ledger that edits its own history is not
evidence. **Nothing conditions on an un-remediated survivor**, and after this ruling nothing
conditions on A-VAB or B-KAB in any state.

**CORPUS NOTE — RESOLVED AT THE GATE (Rafe, 2026-08-27): FRAME AT FIELD SCALE.**

> **The dissenting seat was right at the scale that matters.** C-GAB's inset rectangle is a
> **frame**, not a crack through the stone — and what settles it is the field, not the tile.
> Laid nine-up, the rectangle turns its corners and returns inside every cell instead of running
> on into the neighbour. **The instrument could not have decided this and it is not its fault:
> it only ever looks at one 32×32 tile** (`REPORT.md` §6, stated there before this question
> arose), and the property in dispute does not exist at that scale.
>
> **C-GAB retains its conditioning role. References never ship**, and screening holds at the
> measured child rate — 5 of 20 mechanically, 9 of 20 at the seat-adjusted upper bound.
>
> ⚠ **Recorded so tier one does not misread the retention:** the criterion this clause now
> carries is **incident-free** (§8.3), and C-GAB *does not meet it*. It is retained as the best
> available parent under screening, not as one that satisfies the sharpened bar. **When tier one
> authors or selects parents, incident-free is the bar** — and an authored parent can actually
> meet it, which no §6.4 survivor was ever built to do.

The generalisation this ruling produced is law, and it is larger than this tile: **§8.3, the
motif trap.**

*The paragraphs below record what was contested and how it was measured, because a resolved
question should still show its working.*

Three blind seats have now judged the *same bytes* — the identical lit capture, sha256
`6b358533…`, re-derived byte-for-byte at two different commits:

| seat | cull |
|---|---|
| floor-remediation round A | `none` |
| parent-rate round CP | `none` — *"the best surface here by a distance"* |
| **parent-rate round CS** | **`keyline`** |

2–1. The dissenting seat named a four-sided contour *"one value, returning on itself… the dashed
top does not save it"*. **Its geometry was checked and is partly wrong**: the side it calls
closed is dark in 4 of 9 pixels. The instrument measures that same construction at side coverage
**0.791 against its 0.90 requirement** — a nearly-closed rectangle with one broken side, which
is an accurate description of what is there.

**And that is exactly why the instrument cannot settle it.** §12.1's own text holds that gaps do
not excuse a keyline — *"a border with a bite out of one corner, or one drawn as a dashed run of
ticks, is still a keyline"* — while `REPORT.md` §1 records the instrument's KNOWN LIMIT as
precisely this case, and the decision not to lower the threshold *because C-GAB's 0.791 was
taken to be a mortar joint network*. Whether a side present at 4-of-9 reads as a broken keyline
or as an absent one is not a measurement. **Per §13.2 the deadlock routes to the human gate**,
where it sits as one question — *crack through the stone, or frame around the tile?* — and
Rafe's answer settles this note. Building a number to break the tie is the move §13.4 forbids.

**Screening remains the operative guard regardless of how that question lands**, at the measured
child rate rather than at B-KAB's: 5 of 20 mechanically, 9 of 20 at the seat-adjusted upper
bound. Evidence: `tools/floor_remediation/REPORT-PARENT-RATE.md` §4.

**And the ring rate is a property of the reference, not of the surface — MEASURED
(2026-08-27).** Conditioning 20 generations on C-GAB, at levers and prompt held identical to the
B-KAB run's first wave, returned **5 of 20** ringed against B-KAB's **22 of 24** and its **8 of
8** on the matching wave (one-sided exact p = 6.4e-06 and 0.0038). This clause's whole thesis —
that *a reference hands down whatever it is a picture of* — now has a second, quantitative
measurement behind it, from the ring rather than from the composition. `REPORT.md` §4's
*"it will recur on every floor generated from this surface"* is corrected to **"from that
reference"**.

---

## 6. Light — LOCKED

### 6.1 Dynamic lighting is the direction — LOCKED

Lighting is engine-rendered, not painted in. This is a committed direction, not a preserved
option.

### 6.2 The light arc — LOCKED (as region-identity generator)

| Depth          | Source                                        | Tended by                              | Character                 |
| -------------- | --------------------------------------------- | -------------------------------------- | ------------------------- |
| Boundary       | Carried fire; orc fires                       | Someone who cares whether it stays lit | Warm, moving, unreliable  |
| Middle regions | The world's own — fungal, ambient, sourceless | No one                                 | Cold, even, unattended    |
| The core       | The institution's, for its own purposes       | A process                              | Flat, adequate, permanent |

The arc is the theme in luminance: **you begin as the only thing here that burns, and end
somewhere that was lit before you arrived and will be lit after you are filed.** Institutional
light hides nothing and reveals nothing worth seeing — which is how the Weighing gets genuine
menace with almost no gothic vocabulary.

~~Only the Boundary's values are derived at the pilot. The rest are PLACEHOLDER.~~

> **RULED (Rafe, 2026-08-28) — RULING 56. THE BOUNDARY'S RIG IS RATIFIED. PLACEHOLDER CLEARED FOR
> THIS REGION AND FOR NO OTHER.**
>
> Ratified by §6.2.1's readability pass: walked on the reference device (iPhone SE 3rd gen), at
> gameplay distance, across the lit radius, against the tier-one floor family — which is the
> ordering §6.2.1 demands, the rig before the asset.
>
> | knob | value | unit — stated, because a knob position is not a value |
> |---|---:|---|
> | **radius** | **5.0** | **TILES**, not pixels. At the RULED 32px tile: a 320px radius, 640px light texture. Tiles so the number cannot silently hard-code §4.3's still-undecided tile size. |
> | **falloff** | **1.00** | **EXPONENT** on the radial ramp `(1 − smoothstep(0,1,d))^falloff`. 1.00 is the identity — the plain smoothstep. Above 1 tightens the pool, below 1 carries light outward. **Ratified AT the identity, which is a decision and not an absence of one.** |
> | **ambient level** | **0.70** | **SCALAR on the ambient HUE, not a colour.** `#1a1a22 × 0.70 → rgb(18,18,24) = #121218`, which is the CanvasModulate actually applied. Hue held, brightness only — so a readability pass cannot restyle the region. |
> | ambient hue | `1a1a22` | unchanged by the pass |
> | light colour | `ffb066` | unchanged by the pass — §6.2's carried-fire warmth |
> | energy | 1.6 | unchanged by the pass; 0.0 remains the "lighting is live" control |
>
> **BOUNDARY ONLY.** Every other region derives its own at its own gate. Copying these into one
> would be conformance to a neighbouring region's answer, which is the same error §13.3 refuses
> when the neighbour is a commercial bar.
>
> Landed in `tools/tier0_harness/harness_config.yaml` (status `RULED (Boundary only)`) and in the
> device marker template. The two knobs that were previously code defaults — falloff and ambient
> level — are now **passed explicitly and required by the engine**, on the standing discipline
> that no capture is produced by an undeclared rig: *a ratified value that can be silently
> defaulted is a ratified value that can silently drift.*
>
> **Delivered profile, measured once on the ratified rig** (mean luminance by ring, floor-and-wall
> sample, a datum rather than a gate): flat to ~3 tiles, **0.73 at the radius edge**, 0.19 beyond
> it. Legible across the radius and dark outside it, which is what the pass was for.
>
> ⚠ **The scene it was ratified on has NO automated legibility guard.** `ProbeJunctionLuminance`
> refuses to write a capture whose junction is unlit, but it only runs where the geometry has a
> junction — and `tier1_floor_review` reports `junction=NO`, so the guard is skipped entirely. The
> corridor scene is protected and the floor scene is not. **Recorded for floor session two**; not
> built here, because the gate's instruction was to land the values and park.

**⚠ COUPLING FLAG — RULED (Rafe, 2026-08-27): THE ART IS NOW DOWNSTREAM OF THIS PLACEHOLDER.**

The sighted round measured that **the engine compresses the authored value ratio**, and by a
factor it had to solve backwards on Yarl's own rig:

| | authored face ÷ top | delivered, lit | factor |
|---|---:|---:|---:|
| recipe arm, room A north wall | 0.52 | **0.77** | **1.48** |

**The player is the lamp**, and stands south of a north wall — so the face is always one tile
nearer the light than its own top, everywhere, by construction. The engine brightens the face
relative to the top and flattens the separation §6.5 exists to create. A seat measured the
consequence without being told any of it: *"at x=40 that step is 42→28, only 14 points, and at
x=400 it is 56→21 — A's corner therefore exists only where the light happens to land."*

**So authored ratios are derived backwards from delivered targets on the current rig.** To
deliver 0.52 through this rig you author ≈ 0.35. **The bar cannot supply this number and never
could** — its scene is uniformly lit with no run-time light at all. It is the first quantity in
the recipe that had to come from Yarl's own engine.

**The dependency is named, not solved.** Compensating for a measured falloff is a material
decision and declares no light direction, so it survives §6.3. But **a recipe number that
depends on an underived rig value is a number with a fuse in it**: if this table's energy,
radius or ambient move when they are finally derived, the compensation is wrong and the walls
flatten again.

> **RULE: every authored ratio derived against the current rig is RE-DERIVED when §6.2's
> PLACEHOLDER values are ratified.** Whoever ratifies them owns that re-derivation. The honest
> alternatives — derive the rig before freezing the ratio, or give wall tiles a light-response
> clamp in the renderer — are both real and both outside the round that found this.

#### 6.2.1 TIER-ONE PRECONDITION — the rig is tuned for readability BEFORE any asset is judged through it. RULED (Rafe, 2026-08-27, at the device gate).

> **The §6.2 rig values — radius, falloff, ambient — get a readability-tuning pass before any
> asset is judged through them. The value stack must be legible at GAMEPLAY DISTANCE, not at
> two tiles.**

**This is a precondition, not a task: no tier-one asset round starts until it is done.** The
ordering is the whole of it. §6.2's values are PLACEHOLDER; every wall round so far has judged
art through them anyway, and the coupling flag above shows the art bending itself to fit an
undecided rig. **That is backwards, and the device gate is where it became visible.**

**What the gate saw that no still could.** The sighted round's captures were read at 2× on a
desktop, where a plane separation three tiles from the lamp is plainly there. On the phone, at
the distance the game is actually played and across the radius the light actually reaches, the
same separation is not doing the work — the pool is narrow, the falloff is steep, and §6.5's
stack is legible in a band around the player and gone outside it. **A value law that only holds
within two tiles of the lamp is not a value law, it is a vignette.**

**Why the rig is the thing to move rather than the art.** The art has already been solved
backwards once against these numbers (the coupling flag). Solving it backwards a second time,
harder, to survive a falloff nobody has ratified, would bake an unratified rig deeper into every
asset — and §6.5's ratios would then be carrying a lighting decision instead of a material one,
which is the §6.3 line. **The rig is one table of numbers and the corpus is every asset in the
game. Tune the cheap thing.**

**What the pass owes, at minimum:**

- **Legibility at gameplay distance**, stated as a distance and measured there — not at the
  lamp's centre.
- **The §6.5 stack surviving the falloff** across the lit radius, not only at its middle.
- **The §6.2 arc preserved**: this is a readability tuning, not a licence to flood the Boundary
  with light. *You begin as the only thing here that burns* is register and outranks
  convenience.
- **The ratified values written back here**, which fires the re-derivation rule above.

> **DONE — RULING 56 (Rafe, 2026-08-28).** The values are in the §6.2 table above. What the pass
> owed, answered:
>
> - *Legibility at gameplay distance, stated as a distance and measured there* — walked on the SE
>   at the distance the game is played, not read off a 2× desktop crop. That was the specific
>   failure this clause was written to prevent.
> - *The §6.5 stack surviving the falloff across the lit radius* — ⚠ **NOT ANSWERED, and it could
>   not be.** §6.5's stack is a relationship between the wall's two planes and the floor, and the
>   scene's walls are programmer-art mocks. **The rig is ratified on floor legibility alone.**
>   Whether the value stack survives this falloff is owed by the first round that puts real walls
>   in the scene, and that round inherits the re-derivation below rather than a settled answer.
> - *The §6.2 arc preserved* — ambient moved 1.0 → 0.70, i.e. **darker**. The pass took light away
>   rather than adding it, so *you begin as the only thing here that burns* is not weakened by it.
> - *The values written back* — above.
>
> **NOMINAL RADIUS IS NOT DELIVERED REACH — RECORDED (Rafe, 2026-08-28), and it is a note on the
> clause rather than a qualification of the ruling.**
>
> The ratified `radius_tiles` is **5.0**. Measured on the ratified rig, floor luminance as a
> fraction of lit floor one tile from the lamp:
>
> | distance from the lamp | ratio |
> |---:|---:|
> | 2.0 tiles | 0.659 |
> | 3.2 | 0.341 / 0.328 |
> | **4.0** | **0.159** |
> | **5.0** | **0.060** |
> | ground declared dark (5–6 tiles) | 0.057 / 0.059 |
>
> **At the nominal radius the floor reads the same as ground the scene declares dark** — 0.060
> against an ambient floor of ~0.058. The lamp's *delivered* reach is about **four** tiles.
>
> **RATIFICATION STANDS, per §13.2.** The rig was ratified on the device, by eye, at gameplay
> distance — and the eye is the final instrument. A luminance ratio has never been calibrated
> against *legible to a person holding a phone in a dark room*, and a number does not get to
> overturn a look. What the measurement establishes is narrower and still useful: **nominal and
> delivered are different quantities, and scene design must use the delivered one.** A subject
> placed at the nominal radius is placed in the dark.
>
> **CONSEQUENCE FOR EVERY REGION AFTER THIS ONE — RULED: future regions ratify by DELIVERED
> REACH.** The Boundary's 5.0 is now a number with a known meaning; a second region ratifying its
> own 5.0 by eye would be adopting the Boundary's *label* without its measurement. Each region
> states the distance at which its light actually carries, measured, alongside whatever radius
> parameter produces it.
>
> ⚠ **The delivered figure is rig-shaped, not universal.** It follows from radius, falloff, energy
> and ambient together — change any of them and it moves. It is recorded here because §6.2 is
> where someone will be standing when they place something at "the edge of the light".
>
> **AND THE RE-DERIVATION RULE HAS FIRED.** The rig moved: radius 5.5 → 5.0, ambient 1.0 → 0.70.
> Every authored ratio derived against the old numbers is now compensating against a rig that no
> longer exists. Concretely: the sighted round's `WALL-RECIPE.md` authored face ÷ top at ≈0.35 to
> deliver 0.52 through the OLD rig. **That compensation is stale.** Those walls were culled at the
> 2026-08-27 gate and are in nothing shipping, so no live asset is invalidated — but the number is
> not to be picked up and reused. The tier-one FLOOR family derives no ratio against the rig at
> all (its values come from measured donor material), so it needs no re-derivation.

This is the first measured instance of art and rig being coupled on this project. It will not be
the last, and the reason to write it down here rather than in the recipe is that **§6.2 is where
someone will be standing when they break it.**

### 6.3 Assets are authored to RECEIVE light, not to DEPICT it — LOCKED, RATIFIED

**RATIFIED (Rafe, STOP 2, 2026-08-26), on the device, in the lit corridor: the lighting is worth
the effort.** §6.4's probe ran, its kill criterion was declared before any arm and was not
re-tuned after, and the clause survives it. This clause is no longer provisional.

⚠ **What was ratified, stated narrowly because the probe's own positive control failed.**
Stage 1 produced **no arm A** — no candidate in any arm depicted a directional key light, so the
three arms never separated on the lighting axis. **This ratifies the treatment under light. It
is not a victory over a baked arm, because no baked arm existed to beat.** §6.4's Ruling 47
clause governs that outcome and is not overridden here: A and B being indistinguishable is a
finding about test conditions, never permission to pick either. The comparison §6.4 set out to
run remains unrun, and nothing in this ratification should be cited as having run it.

**RULED (Rafe, 2026-08-26): AUTHORED OCCLUSION IS LAW. Receive-light never meant form-free.**

The clause has been read once too often as *draw nothing that could be mistaken for light*, and
that reading is wrong and is now closed. What §6.3 forbids is a DIRECTION: a highlight, a
gradient, a bevel, a bake that says *the light is over there* and that a torch arriving from
somewhere else contradicts. What §6.3 has never forbidden, and now positively requires, is
**form** — the occlusion a shape casts on itself and on the plane it meets, which is identical
under every azimuth and therefore contradicts nothing.

Self-occlusion, contact occlusion under a lip, and **plane-boundary occlusion (§12.1)** are all
form. An asset that omits them is not obeying this clause more strictly; it is under-drawn, and
it will read flat under any light the engine supplies.

**OCCLUSION, NOT ILLUMINATION — the vocabulary is the rule.** Geometry is drawn with
**occlusion** — dark where light cannot reach: crevices, under-edges, recesses, the shadow under
a strap's lip — and never with **illumination** — bright where light would strike: top chamfers,
lit crowns, directional ramps. Same information, opposite vocabulary. **A plane separates from
its neighbour by the dark seam where they meet, not by a highlight along its edge.**

**The vocabulary collision, recorded because it manufactured violations twice.** At 32px,
*"describe geometry with value"* and *"bake a key light"* share a vocabulary. The wall gauntlet's
own critic asked for a 1px chamfer top-and-bottom and received the gauntlet's only key-light
culls; the tiles-pro audit reproduced the same failure through a depth parameter instead of a
prompt. Two surfaces, two mechanisms — **a property of the scale, not of any tool.** Asking any
generator or any author for "depth" without specifying the occlusion vocabulary will manufacture
directional light. **Every future critic kit and prompt file carries this distinction
explicitly.**

**The instrument that enforces it — PROMOTED (§13.5), one axis.** The differencing check
(composition spike, round 8): **authored form must persist identically with the engine light
switched off.** A per-block top-bright/bottom-dark emboss that encodes a light direction fails
the diff. Its demonstrated fail is on the record — it is the method that culled the round-8
plant, quoted verbatim below — so its passes count, on its one axis. **It measures light
direction and nothing else; the eye still rules the rest** (§13.4). Audited in §15.

⚠ **CAVEAT TRAIL — the baked arm exists now, and it outranked every receive-light arm built
against it.** Recorded verbatim from the composition spike's report
(`tools/composition_spike/SPIKE.md` §5.1b, 2026-08-26) because it is adverse evidence on the
axis this clause's ratification could not test, and a caveat trail that summarises adverse
evidence in its own words is not a caveat trail. **§6.3 stands.** This is the record, not a
reopening.

*(Numbering per `tools/composition_spike/SPIKE.md` §5.1b — there is no bible §5.1b.)*

#### 5.1b THE PLANT OUTRANKED THE ARMS — and §6.4 said this comparison had never been run

This was not designed and it is the most consequential thing in the report.

The plant is boundB **plus** a baked per-course key light: identical stones, identical rig,
identical geometry, one forbidden construction added. Six independent blind seats ranked the
five captures best-to-worst:

| round | ranking, best → worst | plant | plant cull |
|---|---|---|---|
| 1 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |
| 2 | boundB > ctrlB > **plant** > boundA > ctrlA | 3 of 5 | none |
| 3 | boundB > boundA > **plant** > ctrlB > ctrlA | 3 of 5 | key-light |
| 4 | ctrlB > boundB > **plant** > boundA > ctrlA | 3 of 5 | key-light |
| 5 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |
| 6 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |

**First in three rounds of six. Never below third of five. Not once last.**

Round 6 named the mechanism: *"a depth cue applied on one axis only is worse than no depth cue
— it asserts a viewing direction the rest of the frame contradicts."* It read as depth. In six
rounds it is **the only thing that produced any depth read at all**, in a set where the
thickness question was otherwise answered no every single time.

**Why this matters more than a ranking usually would.** §6.3 is RATIFIED, and §6.4 states its
own limit in as many words:

> *"Stage 1 produced no arm A — no candidate in any arm depicted a directional key light, so the
> three arms never separated on the lighting axis. This ratifies the treatment under light. It
> is not a victory over a baked arm, because no baked arm existed to beat ... The comparison
> §6.4 set out to run remains unrun, and nothing in this ratification should be cited as having
> run it."*

**A baked arm now exists.** This session built one because LOOP-PROCESS §4 requires a plant, and
it is in one respect a *cleaner* comparison than §6.4's design: the plant and boundB are the
same stones under the same rig, differing by exactly the baked light, so it is a within-arm A/B
rather than three separately-generated arms.

**What this is NOT.** It is not a ruling and not a candidate for one:

- **The plant never passed.** It failed in all six rounds and was culled `key-light` in two,
  with a method — *"still present in the far-left corner at 6× exposure where the engine pool
  never reaches"* — and a measurement, *"+8.7/−6.2 top/bottom split against +2.3/−1.0 for every
  other image in the set."* The clause's own instrument works.
- **A ranking is not the gate.** §13.1 gives the verdict to Rafe on the device, and a seat
  preferring a still image is exactly the "wrong instrument in the wrong context" §6.3 warns
  about — except that these are lit in-scene captures, which is the *right* context, which is
  why it is being reported rather than dismissed.
- **The arms it beat are mocks.** A better-composed wall might beat it. Six rounds did not
  produce one.
- **It was built to be caught**, which biases it toward being conspicuous, not toward being
  liked.

**The honest statement: on the depth axis, in the lit scene, at the ruled canvas, the forbidden
construction outperformed every receive-light arm this session could build, six times out of
six — while remaining correctly detectable as forbidden.** §6.4's unrun comparison has run
incidentally and its first result is adverse. That is a finding for the record and a ruling for
Rafe; it is not this session's to resolve, and §6.3 stands untouched by it.

**What that record does and does not change.** It does not reopen §6.3: the plant never passed,
was culled `key-light` in two rounds by a seat that had demonstrated it could fail, and a
ranking is not §13.1's gate. It does close the sentence above that said the comparison "remains
unrun" — it has now been run once, incidentally, on a within-arm A/B, and its first result is
adverse on the depth axis. Anyone citing this clause should cite that too.

**THE REMATCH RAN, AND IT WENT THE CLAUSE'S WAY.** The two ruled rounds put authored occlusion
against the baked plant on identical stone, with plane-boundary occlusion deepened to the
requirement above and the wall-top albedo separated from the floor's. Across eight rounds the
plant's ranking among five captures went:

| round | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| plant's place | **1st** | 3rd | 3rd | 3rd | **1st** | **1st** | **1st** | **4th** |

**Round 8 is the first round in which legal form beat the baked arm**, and it beat it with
exactly the construction this ruling made law. The plant was also culled `key-light` that round
by a method stronger than any before it — *"differencing against C1 isolates a per-block
top-bright/bottom-dark emboss that would survive the engine light being switched off"* — so it
lost on the ranking and on the cull in the same round.

**Stated at its true strength and no higher.** One round is one round; the plant led the six
that preceded it; the arms are mocks; and a ranking is not §13.1's gate. What the record now
supports is narrower and more useful than a verdict: **the baked arm's advantage was an
advantage over receive-light assets drawn WITHOUT form, and it disappears once they are drawn
with it.** That is the strongest available reading of §5.1b and it is consistent with every
round in the trail.

**This is a one-way door and the most consequential construction rule in this document.**

Sprites are drawn with material and form under relatively even illumination. Highlights are not
baked in. Light arrives from the engine.

Baked highlights fix a single light direction into every asset; add a torch on the right and
everything is still lit from the upper left. The conflict is invisible until the renderer is
switched on, and the only fix is redrawing everything. Gemfall hit the same shape when its
outline rule moved from baked art to the engine (their §4, v1.1).

**Consequence that must be stated or it will cause false rejections:** receive-light assets
look flat and slightly disappointing on a contact sheet. **They come alive only in the lit
scene.** A critic — or a human at a gate — who rejects a receive-light asset for looking
underlit in isolation is applying the wrong instrument in the wrong context. This sharpens
§13.1 from a discipline into a technical necessity.

**Baked drop shadows are depicted lighting and are forbidden with the rest of it.** The asset
bar ships every item sheet twice — with and without painted shadows — because a baked shadow is
wrong in every context except the one it was painted for. That manual workaround is this clause
solved structurally: **the asset never grounds itself; the engine or a composited blob grounds
it per context.** One asset, every context, and nothing fights the probe.

### 6.4 The receive-light probe — RUN AND CLOSED, §6.3 RATIFIED

**Status: closed 2026-08-26.** The probe below is preserved as authored, because §13.6 and
LOOP-PROCESS §8 both turn on the bar having been declared before the answer was visible, and a
criterion rewritten after the fact cannot demonstrate that. What follows is the probe as it was
declared; the outcome is recorded at the end of this section.

§6.3 was a committed direction, **not an unconditional one.** It was the clause in this document
with the largest unmeasured effort cost, and it was to be struck if the probe below said so.

**The named risk, and it is the previous track's shape wearing new clothes.** Generation models
are trained on art that *depicts* light — baked highlights, a key direction, painted
specularity. Asking a generator for evenly-illuminated material-only sprites may be asking it
to do the thing it least wants to do. If so, receive-light becomes the new external-corpus trap
(§1.3): every asset a fight against the tool, for a payoff nobody can see.

**The distinction that probably decides it:** receive-light does **not** necessarily mean flat.
It can mean *no directional key light* while retaining form shading, self-occlusion, and
material value differences — which is far closer to what a generator naturally produces and is
still fully compatible with dynamic light.

**The probe.** One wall-and-floor fragment, three arms:

| Arm   | Authoring                                                    | Role                                             |
| ----- | ------------------------------------------------------------ | ------------------------------------------------ |
| **A** | Baked directional key light                                  | **Positive control.** The conventional approach. |
| **B** | No key light; form shading, occlusion, material value retained | The likely answer.                               |
| **C** | Flat — material value only                                   | The strict reading of §6.3.                      |

Lit in Godot, on the reference device, in a corridor. Four questions:

1. Do B and C look good **lit**?
2. Does the device hold frame rate with occluders present?
3. **How much harder was it to generate B and C than A?** ← the question that decides it.
4. Does the light deliver the §6.2 region arc, or is it merely darkness with a lamp in it?

**Positive control clause (Ruling 47).** Arm A exists so the instrument can be shown to
discriminate. **If A and B cannot be told apart in the lit scene, that is a finding about the
test conditions — not permission to pick either.**

**Kill criterion — declared now, before any result is visible (Ruling: nothing is cut to fit).**
If B and C cost materially more generation effort than A for a payoff not visible on the
device, **§6.3 is RETIRED, §6.1 falls back to baked lighting, and the evidence is recorded in
place.** The bar is not re-tuned after the answer is seen.

**This probe runs before the Phase 5 pilot.** It is the cheapest point at which the answer is
still free: §6.3 is a one-way door, and every asset drawn before it is settled is drawn twice
if it is wrong.

#### The outcome — RULED (Rafe, STOP 2, on the device, 2026-08-26)

**§6.3 RATIFIED.** The lighting is worth the effort. The kill criterion above was not met and
was not re-tuned.

**And the probe's own positive control failed, which narrows what that ratification says.**
Stage 1 ran 120 unconditioned generations across all three arms. **No arm produced a single
candidate depicting a directional key light — arm A included.** The blind census that measured
this passed its own control 10/10 against constructed plants, so the reading counts, with one
limit stated: the plants carry a *hard* key light, so what is licensed is *"no arm produced
directional lighting at plant strength"*, not *"none produced any"*.

Consequences, recorded rather than smoothed over:

- **The three-arm comparison never ran.** There was no arm A to lose to. Ruling 47's clause
  applies exactly as written — a finding about test conditions, not permission to pick an arm —
  and it is not overridden by the ratification.
- **What Stage 3 showed is real and is what was ruled on:** receive-light assets in the lit
  corridor, on the reference device, at 32×32 native at ×2, each against its own unlit
  companion under an otherwise identical rig. §6.3's central claim — that these assets *"look
  flat and slightly disappointing on a contact sheet"* and *"come alive only in the lit scene"*
  — is what the device answered, and it answered it yes.
- **The effort half of the kill criterion never acquired a denominator.** Effort was to be
  measured as generations-per-accepted-reference per arm, against arm A's. With the arms
  undifferentiated, the ratio measures subject difficulty, not lighting treatment. It was not
  computed, and no number should be cited as though it had been.

**Retirement triggers.** This ratification rests on the lit scene, not on a comparison. If a
baked-key-light arm is ever actually produced and beats receive-light on the device, or if the
effort ratio is ever measured with a real arm A and lands clearly beyond the abstention band,
§6.4 reopens. Absent that, §6.3 is settled and the door is shut.

**Evidence.** `tools/pixellab/probe_6_4/` — `AUDIT-FINDINGS.md` (surface freeze),
`STOP1-REPORT.md`, `STOP2-REPORT.md`, `PARK-STATE.md`, and the image ledgers. Every generation
is on disk with its full request payload, because nothing on this platform is seed-reproducible
and a parameter row is therefore not evidence. **Probe total: 174 generations.**

---

### 6.5 The value stack — RULED (Rafe, 2026-08-27). The recipe's load-bearing law.

> **The floor sits BETWEEN the wall's two planes.**
>
> | | target, floor-relative |
> |---|---|
> | **wall top** | **≈ 1.11 × floor** — lighter than the floor |
> | **floor** | 1.00 |
> | **wall face** | **≈ 0.5–0.6 × floor** — darker than the floor |
>
> **Each plane is separated from the floor in a different direction.** That is the law; the
> exact figures are targets carrying §5's PLACEHOLDER status, not constants.

**Register derivation — §6.3, occlusion expressed as a ratio.** The top catches light; the face
is where light cannot easily reach. A horizontal plane under a top-down ambient is open to it; a
vertical plane faces the wall opposite rather than the ceiling, and is the largest recess in the
scene. §6.4 arm B's own words — *"joints, recesses and undercuts sit darker because they are
enclosed"* — applied at the scale of a whole plane. **Enclosure is direction-free by
construction**: dark from every angle, so a torch arriving from anywhere does not contradict it.
This is why the stack is material and not depiction, and why it survives §6.3.

The floor's own position follows from §8.1 and is the half that is easy to miss: *"grime walked
into a surface until it is part of it."* **The floor is dark because it is used. The wall top is
light because nothing has ever touched it.** Two independent derivations — enclosure below,
traffic above — meeting on the same floor value from opposite sides.

**WHY IT IS LOAD-BEARING, and this is the finding of the whole wall campaign.** Yarl's walls had
the relationship **inverted**:

| | top | floor | face | face ÷ top |
|---|---:|---:|---:|---:|
| the bar | **1.11** | 1.00 | **0.59** | **0.53** |
| Yarl, composition spike `before` arm | **0.49** | 1.00 | **0.65** | **1.30** |

Both planes below the floor, 0.16 apart, with **the face brighter than the top**. Not mistuned —
inverted. **Eight blind rounds of "this wall has no thickness" were reading a plane relationship
that the values contradicted, and no side face is required to explain any of it.** Corrected,
two independent seats ranked the Yarl candidate above the bar on depth.

⚠ **The methodological lesson, banked because it will recur.** The spike swept wall-top albedo
at 0.62 and 0.76 of floor, found 0.62 better, and reasoned toward *darker*. Both samples sat on
the **same side** of the floor's value; the answer was on the other side, above 1.0. **A
two-point sweep entirely on one side of the true value points confidently in the wrong direction
and looks like clean evidence while doing it.** Bracket the target or say you have not.

**AND THE ENGINE COMPRESSES IT — COUPLING FLAG, see §6.2.** The authored ratio is not the
delivered ratio. Authored 0.52 arrives as 0.77 under the carried light, a compression factor of
1.48, because the player *is* the lamp and stands south of a north wall — so the face is always
one tile nearer the light than its own top. **Authored ratios are therefore derived backwards
from delivered targets on the current rig.** That dependency is named in §6.2 and is not solved.

**Evidence:** `tools/sighted_round/WALL-RECIPE.md` §0–§1 (measurement and register derivation
per number, under §13.3's origination rule), `bar_measurements.json`, and the seat transcripts.

> **THE FLOOR'S 1.00 IS NOW A MEASURED CONSTANT, NOT A PLACEHOLDER — RECORDED (floor session two,
> 2026-08-28).**
>
> §6.5 states its whole table *floor-relative*, and until now there was no floor to be relative
> to: the wall recipe had to invent one, which is how it came to author ratios against a rig and
> a floor that both moved underneath it. The edge-matched Boundary family fixes the reference.
>
> | | value |
> |---|---:|
> | **median luminance, as authored, unlit** | **114.5** |
> | mean | 113.3 |
> | per-tile mean spread across the 81 tiles | 3.3 |
> | p5 / p95 | 74.9 / 127.8 |
>
> **114.5 is §6.5's 1.00 for the Boundary.** Walls derive against it; it does not drift after
> landing. Measured on the tiles themselves rather than on a capture, deliberately — a lit
> measurement would fold the rig into the constant, and §6.2's re-derivation rule exists precisely
> because a number with a rig baked into it is a number with a fuse in it.
>
> ⚠ **`WALL-RECIPE.md`'s face ÷ top ≈ 0.35 is STALE and is not to be reused.** It was authored to
> deliver 0.52 through the pre-Ruling-56 rig. Those walls were culled at the 2026-08-27 gate, so
> nothing shipping depends on it — but the next wall round derives against the floor above and the
> rig in §6.2, from scratch.
>
> ⚠ **The per-tile spread of 3.3 is itself load-bearing.** Session one measured a 6.4-point spread
> between variants and a blind seat read it as *"the grid draws itself onto the ground"* — the
> cell's own average brightness sitting at a constant position is §8.3.1 with no feature in it at
> all. Every tile in this family is normalised to the family's value for that reason, and the
> spread is reported so the next family can be held to it.

---

## 7. Construction grammar — everything is held — LOCKED

### 7.1 The rule

**Nothing made in the Paths is monolithic or self-supporting.** Every made object visibly
shows what holds it together: strapped, banded, wired, pinned, mortared, tied, clamped, sealed.
Doors have hardware. Stones have cramps and ties. Beams are bracketed. Bundles are corded.

**And everything is tagged.** The institution has inventoried its world. Things wear their
paperwork.

**Failure test, and it is checkable by eye without taste entering into it:** *show me what holds
this together.* An asset that floats, or is carved from one seamless piece, or has no visible
fastening, fails — and the failure has a name and a fix rather than being "feels off."

### 7.2 Why this rule and not another

The fiction's central verb is *bound*. Marya bound into brass. The orcs bound to a line they
cannot advance. Souls bound in a queue awaiting audit. A ward re-anchored to something it
should no longer be attached to. Sasha bound by a debt. The Under-Warden bound by his charter,
which is why he cannot be reasoned with.

Three things this buys at once:

1. **A shared skeleton across five regions** while surface treatment varies. Same grammar, five
   dialects. This is the machinery region identity needs, and it is exactly what the previous
   track lacked.
2. **Readability at 1×.** Bands, straps, and tags are high-contrast linear elements — they are
   what still reads on an iPhone SE after interior detail has dissolved. A rule that serves
   theme and readability simultaneously is rare; take it.
3. **Hollowmark rhymes with the world instead of being an exception.** A woman bound into brass
   is the same operation the world performs on stone, doors, and orcs, applied to a person. The
   player absorbs the logic through hundreds of props before it lands on her.

### 7.3 Binding authority is a region signal — LOCKED (Boundary), PLACEHOLDER (others)

**Who did the binding, and how long ago, differs by region and is legible.**

- **Orc-made (the Boundary): redundant and visible.** Lashed twice. Over-built. Repaired on top
  of prior repairs, because four hundred years of holding a line means everything has been fixed
  a dozen times. Rope, driven pin, hide, timber, salvage. Work done by hand by people who need
  it to hold and do not care how it looks.
- **Institution-made (the core): minimal and correct.** One seal, one tag, done properly, never
  touched again.

The player feels the difference without being told: **the frontier is held together by people
who care whether it holds, and the core is held together by a process that does not care at
all.**

**RULED (Rafe, 2026-08-24): competent but tough. No interest in aesthetics — strength only.**

The Unshriven's work is not desperate and not decorative. It is the work of people who have
been doing this for four hundred years and are extremely good at it, who have never once cared
how it looks. Heavy, over-engineered, correct. Joints that would hold under more load than they
will ever see. Repairs laid over repairs because replacing was never worth it, each one as
sound as the last.

**Nothing on an orc-made object exists for appearance.** No carving that is not structural, no
ornament, no finish. If it is there, it is holding something. This is the sharpest available
contrast with institution-made work, which is also unornamented but for the opposite reason:
the orcs strip it because strength is all they want, and the institution strips it because
nobody cared enough to add any.

### 7.4 Known seams in the rule — flagged, to be tested at Phase 5

1. **Raw geology.** A cave wall is not bound by anything. The rule applies to **made** things;
   the boundary between made and found becomes a region signal in its own right. The Boundary is
   mostly found stone with orc work pinned into it; the deepest regions are made all the way
   down; the transition is a slow inversion of that ratio.
2. **Creature bodies.** An orc is not bound together. **Creatures inherit the grammar through
   their equipment, not their anatomy** — strapped armour, corded bundles, an oath you cannot
   see. This is a real seam and the first creature tier is where it gets tested.

**Creatures stand like they have always been there — RULED from the study pass.** The asset
bar's figures are heraldic: planted, frontal or near-frontal, weight straight down, at most one
deliberate asymmetry. No mid-action idle poses, no dynamic lean. This is where its "epic"
lives — emblem, not drama — and it is exactly right for a world of things bound in place: **the
stillness is the menace.** Idle sprites are icons; motion is spent only where §9 spends it.

---

## 8. Wear — LOCKED

### 8.1 Two independent axes

**Traffic and care are separate dials, and the institution neither repairs nor removes.**

- **Traffic without care → polish.** Treads worn concave. Edges rounded off. Stone smoothed to
  a shine at hand height. Thresholds hollowed. Grime walked into a surface until it is part of
  it.
- **No traffic and no care → decay.** Old things persist in place, half-collapsed, and the
  traffic simply routes around them. A shrine somebody built in a side passage is neither
  maintained nor cleared away, because the Under-Warden's charter covers neither.

**Nothing in the Paths is ruined; everything is used up.** Surfaces record traffic, not time.

**Failure test:** *is the state of this thing explained by traffic and indifference?* A
collapsed shrine off the path passes. A collapsed shrine in the middle of the main flow fails —
the flow would have worn a channel through it.

### 8.2 Wear is legible — LOCKED

**Polish means you are on the path. Decay means you have stepped off it.**

Navigation carried by surface treatment, with no marker, no colour-coding, and no signage —
which matters enormously on a screen with no room for any of those. It also produces exactly
the unease the register wants: **the safe route is the one worn down by the traffic of the
dead.**

### 8.2.1 The trodden channel — RULED (Rafe, 2026-08-25)

The primary expression of legible wear on floors is **a polished channel worn through a wider
hall** — the path of centuries of dead traffic, running down the middle of rooms and corridors
that are wider than it. Ordinary floor flanks it. The channel leads somewhere: stairs down, or
rooms that matter. Route legibility comes from the channel, not from signage.

One-tile-wide corridors remain fully in the game — the chokepoint is a load-bearing roguelike
verb and nothing about the art removes it. A one-wide corridor is either **trodden** (on the
main route: polished wall to wall, because the traffic had no room to spread) or **neglected**
(off-path: §8.1 decay). Both states must be drawable and must read apart at 1×.

**Consequence for review scenes:** a floor candidate is not fully reviewed until it has been
seen in at least: open floor, the channel, a trodden chokepoint, and a neglected passage. A
review scene shaped only as narrow corridor cannot pose the §8.2 question.

**TIER-ONE REQUIREMENTS, banked from the floor-remediation seat — RULED (Rafe, 2026-08-27).**
A blind seat shown the survivor floors in the lit corridor culled every one of them, before and
after remediation, and the reasons that were *not* about keylines are the most useful thing it
produced. They are **requirements landing on tier one, not a verdict on the corpus** — they
measure the absence of systems tier one has not built yet, on a thirty-cell field of one
repeated tile:

> *"Nothing has been done to it. Every arris is sharp, every joint is the same width and depth,
> and the traffic line down the middle is as pristine as the edges."*
> *"the identical bracket-shaped stone sits at the identical position inside every single cell,
> so the eye locks onto a 32-unit lattice within one screen."*
> *"all five are laid to the same flawless repeating module, which is why not one of them reads
> as a floor anything has actually happened to."*

1. **A variant system.** One tile per role is a clone field, and a seat reads a clone field as
   printed paper at any quality of tile. The seat's own figure: author variants whose bond is
   offset between them, so a joint starting at x=8 in one cell lands mid-stone in the next.
   **§8.3 gives this its mechanism and raises its priority: the variant system is not only how
   a field stops looking printed, it is the ONLY place incident is allowed to live.** Until it
   exists there is nowhere to put a crack that does not turn it into a motif.
2. **A wear system, which is this clause.** The channel is what the seat asked for, unprompted
   and having never seen §8.2.1 — *"sand a 12-unit band down the centre, erase the joint detail
   inside it so joints fade where feet cross them, and leave joints at full depth only within
   4 units of the wall."*
3. **A floor-repair vocabulary.** §7.4's orc work exists on walls and nowhere on the ground —
   *"a cracked slab pinned flat with four driven iron pins, or a salvaged timber baulk dropped
   across a hole and worn smooth on its top edge."*
4. **A-HEB IS UNMEASURED AS A PARENT — twenty generations, or an explicit unknown-rate marker,
   before anything conditions on it (RULED, 2026-08-27).** Two of §5.5's four survivors now have
   a measured child ring rate: B-KAB 22 of 24, C-GAB 5 of 20. The secondary style parent has
   none, and the parent-rate run stopped short of taking it by its own declared fork. A
   `may_condition: true` flag is an authorisation, not a measurement, and after this week the
   two are no longer interchangeable — the same flag covers a reference that produced 92% ringed
   children and one that produced 25%. So A-HEB is either measured on the same twenty before it
   parents anything, or it carries an explicit unknown-rate marker wherever it is used, and the
   round using it budgets for screening at a rate nobody has measured.

⚠ **And the review scene owed the seat a fair question, which this clause had already said.**
Those verdicts were rendered on a one-tile-wide corridor, where there is no centre line distinct
from the flanks — so *"the middle of the corridor and the edge of the corridor are byte-identical"*
is partly the scene reporting its own shape. The paragraph above is the standing rule and it was
not met. **A floor round that means to pose the §8.2 question must build the four-scene set
first**; until it does, a wear cull is not fully chargeable to the tile.

---

### 8.3 The motif trap — RULED (Rafe, 2026-08-27, at the gate). LAW.

> **Any incident baked into a tile becomes a motif when tiled.**
>
> **Repetition converts accident into intent, and the eye reads pattern regardless of the
> incident's quality.**

**Therefore:**

- **Style parents carry incident-free material only.** §5.5's parent criterion sharpens from
  *compositionally neutral* to **incident-free**.
- **Incident arrives at the instance level, randomised** — cracks, wear, marks, and §8.2.1's
  channel — via **variants and overlays**: the floor system tier one builds.
- **A tile is the material; the incident is the variant.**

**Why this is a law and not a preference.** A tile is authored once and drawn hundreds of times,
and *drawn hundreds of times* is not a neutral operation — it is the operation that turns a
detail into a statement. Nothing about the incident changes; the **frequency** changes, and
frequency is read as intent. This is why a beautifully drawn crack is not a smaller version of
the problem than a clumsy one: **quality does not enter into it.** A perfect crack in every cell
is a perfect crack announcing itself thirty times, which is a wallpaper motif, which is
§1's *nothing is staged* broken by arithmetic rather than by intent.

**It explains the culls that had no other explanation.** Every blind seat that has looked at a
floor field said a version of this without being given the clause — *"the identical
bracket-shaped stone sits at the identical position inside every single cell"*, *"one bitmap
repeated edge to edge"*, *"the identical U-shaped notch centred on every slab"*, *"a centred,
orientation-locked ornamental motif repeated on every cell is decoration, not paving"*. Five
independent seats, four rounds, one finding. **They were not culling the tiles. They were
culling the tiling.**

**THE SCALE RULE, which is the part that bites hardest.** *The property lives at field scale and
does not exist at tile scale.* A single tile is not enough evidence to judge one, and neither is
a contact sheet of single tiles. **Judge a tile as laid** — this is what §13.1's in-scene rule
has always been protecting, now with a mechanism behind it. It is also why the ring instrument
could not settle C-GAB and was never going to: it looks at one 32×32 tile, and no amount of
tuning reaches a property that is not in its input (`REPORT.md` §6, §12.1's cross-reference).

**Consequence for review scenes, on top of §8.2.1's four:** a floor is reviewed **tiled**, over
enough cells for a repeat to become visible. A one-cell view cannot pose this question any more
than a one-wide corridor can pose the §8.2 one.

**RETROACTIVELY, and it completes a finding that was left open.** `REPORT.md`'s Round B rescore
banked the repetition and absent-wear culls as tier-one requirements rather than as a verdict on
the corpus, and could not fully say *why* the distinction was principled. This clause says it:
**those tiles were BASES, judged as FINISHED FLOORS, before the incident system existed.** The
seats were right and the tiles were not being asked a fair question — not because the review
corridor was one wide (that too, §8.2.1), but because **a base and a floor are different
objects**, and every round so far has shown a seat the first while calling it the second.

**The division this establishes, which tier one inherits:**

| | authored | carries | judged |
|---|---|---|---|
| **base tile** | once, per material | material only — no incident | never alone; only as laid |
| **variant / overlay** | per instance, randomised | the incident — cracks, wear, marks, channel | in the field it produces |

#### 8.3.1 It applies to WALL material identically — RULED (Rafe, 2026-08-27, at the device gate)

**§8.3 was written from floors. It is not a floor clause.** The device gate looked at the
sighted round's walls on the phone and found the same arithmetic running:

> **Wall tops are incident-free material. Boundary rules and edge ticks are pattern, and they
> are out.**

**This culls a construction this bible ruled in four hours earlier, and the sequence is the
point.** §3.1 established that a wall top is flat — *not face material re-toned* — and the
sighted round built that flatness with a **regular 2 px joint grid on a 16 px pitch**,
phase-offset per variant. On a still, at 2×, that reads as the joints between blocks. Tiled
across a room on a phone, it is **a ruled grid** — an incident at fixed offset in every cell,
which is exactly what §8.3 forbids, arriving through the one part of the tile §3.1 had just
made prominent.

**§3.1 is not weakened by this and must not be read as weakened.** *A top surface is not face
material re-toned* stands. What §8.3.1 removes is the thing that was standing in for material
once the coursing came off: **flat does not mean gridded, and a boundary rule is not a
material.** A wall top's material is whatever the stone is; if that reads as empty at 32 px,
the answer is a variant system, not a lattice.

**Where the boundary between the planes goes instead.** The turn between top and face is
geometry and stays — it exists only where floor lies south, so it answers to what adjoins it
(§12.1, §6.5). What may not stay is a rule drawn at a **fixed offset inside every tile**,
because that offset is what the eye adds up.

**The general form, so the next asset class does not have to earn this a third time:**

> **Any treatment applied at a constant position within a tile becomes a lattice when tiled,
> whatever it depicts and however well it is drawn.** Joints, ticks, rules, borders, panels,
> caps. The test is not *what is it* — it is *where does it sit, and does it sit there every
> time.*

**Floors earned this clause; walls confirmed it; it is now written as a property of tiling
rather than of either.**

#### 8.3.2 MATCHING IS AGREEMENT, NOT CONSTANCY — RULED (Rafe, 2026-08-28). Edge-matched sets are legal.

**§8.3.1 forbids a treatment at a CONSTANT POSITION. It does not forbid two neighbouring tiles
from AGREEING about where their shared boundary is crossed** — and the difference between those
two things is the difference between a lattice and a floor.

The clause needed saying because the honest reading of §8.3.1 alone would have banned the only
construction that answers floor session one's terminal finding:

> *"Joints enclose nothing — 99.1% of the floor is one connected region. No stones, only
> scratches. … Every 'stone' leaks into every other stone. For an underworld whose whole premise
> is that it is ADMINISTERED, a floor that cannot show a single completed stone is arguing the
> opposite case."*

A joint network can only close if joints **agree across cell boundaries**, which requires the tile
chosen for a cell to depend on its neighbours. That is an edge-matched (Wang) set, and it is
hereby legal.

**THE DEGENERATE CASE IS NAMED, AND IT IS CHECKABLE.** A set is *lattice-degenerate* when its edge
families are too few to vary the crossing positions — agreement collapses into constancy and
§8.3.1's lattice returns wearing the fix's clothes. Two floors:

1. **At least THREE edge families per boundary orientation.** Two would make every boundary a
   coin-flip between the same two offsets; one is a ruled grid by definition.
2. **Crossing-position variance measured across the ASSEMBLED FIELD, and reported.** A field whose
   joint crossings cluster at constant offsets has re-derived the lattice and **fails**, whatever
   its family count says. §8.3's scale rule again: the property lives at field scale, so a table
   of intended families is not evidence — the pixels are.

**Register derivation**, because §13.3's origination rule requires one and "it makes the floor
close" is a mechanism, not a justification. §1 holds the Paths are **administered** — built,
catalogued, maintained by somebody. A floor of closed, laid stones is that claim in material; a
floor of open scratches is the opposite claim, and a blind seat reached exactly that conclusion
from the pixels without ever being shown the clause. Agreement between neighbours is what
*laid* means: a mason sets a stone against the one already there. Constancy is what *printed*
means. The law distinguishes them because the register does.

**First measured under this clause** (floor session two, `tools/tier1_floors/field_wang.py`):
3 families per orientation, 81 combinations, an 8×8 assembled field —

| | session one | under this clause |
|---|---:|---:|
| largest single region, share of floor | **99.1%** | **3.9%** |
| enclosed regions | 2 of meaningful size | **147**, median 177 px, 77 ≥ 64 px |
| crossing offsets, distinct per orientation | n/a | 3–4, modal share **0.375** (≈ 1/3) |

⚠ **AND THE MECHANISM COSTS SOMETHING, RECORDED SO IT IS NOT DISCOVERED LATER.** An edge-matched
tile **cannot be rotated or flipped** — its orientation *is* its meaning, and turning one relabels
its four edges so it stops agreeing with its neighbours. Session one bought most of its variety
from eight free orientations of every tile (§6.3 paying out: a receive-light asset has no up to
break). That variety must now be bought with combinations instead, which is why the family count
per orientation is a floor rather than a target.

⚠ **The trap has a mirror and it is not licensed here.** *Incident-free* is not *featureless*.
Material has structure — joints, bond, grain, value break — and stripping that to avoid a motif
produces the flat clone field the same seats cull on sight. **The test is whether a feature is a
property of the material (a joint between two stones) or a thing that happened to it (a crack
through one).** The first belongs in the tile; the second does not.

---

## 9. Motion — policy LOCKED, specifications PLACEHOLDER

### 9.1 What moves

**The player unit gets the animation budget. The world stays still.**

Movement is attention. Anything that moves is asking to be looked at, and the register says the
environment declines to compete. A dungeon where the protagonist breathes and everything else
is motionless is unsettling in precisely the right way, and it costs a fraction of animating
the world.

**Scope: idle, walk, basic attack, take-a-hit. That is the set.** Against the §9 frame
arithmetic these four states consume the budget; there is no "and others." **An addition
displaces a frame rather than extending the count** — proposing a fifth state means naming
which of the four gives up a frame, and that trade is a ruling, not a default. A budget that
can be added to is not a budget.

**The bar's arithmetic — read from the asset bar's own sheets (§13.3).** Each Oryx Ultimate
figure carries approximately **five frames**: a two-frame idle, a two-frame walk, one attack.
The entire "baseline of animation" that earns the library its wow is single digits per figure.
**PROVISIONAL count** — read from a packed sheet; to be confirmed against source files and
corrected in place if wrong.

**Sasha's budget accordingly: idle 2, walk 2, attack 1–2, take-a-hit 1 — six to eight frames
total.** Hero-only animation at this count is a small, bounded ask. The four states above are
measured against this bar, not against ambition.

### 9.2 The named failure — LOCKED

**Idle-flicker-everywhere.** Guttering torches, waving banners, ambient sparkle. It reads as
production value, it is what most pixel roguelikes do, and it would quietly dismantle the
register by making the world lively and attentive. Forbidden.

### 9.3 A candidate rule, not adopted — NOT LEGISLATED

Animating *what the fiction says is bound* — a thing straining against what holds it — would
make motion carry information: if it moves, something is holding it. Recorded as an idea with a
real argument behind it. **Not adopted**, because §9.1 already spends the budget and this would
reopen it. Revisit only if hero-only animation ships and there is appetite for more.

### 9.4 Frame counts are recorded, not implicit — LOCKED (process)

Whenever hero animation is built, **frame counts and the frame on which a hit lands are
recorded in the asset's manifest row.** Sound is out of scope for this bible (§14), and this is
the single coupling point: audio timing binds to animation frames, and reconstructing that later
is avoidable waste.

---

## 10. The player unit — Sasha — LOCKED

**Sasha is not an ordinary asset and does not go through the ordinary pipeline.** He is
animated, he is rigged, he carries the reserved warmth channel, and he is the only thing on
screen that moves. He gets his own bible section, his own identity card, and his own pilot tier.

### 10.1 Rigged from frame one — LOCKED. One-way door.

**Sasha is authored as a rig with declared attachment points before the first pixel is drawn.**
A fixed body armature with named attachment points — hand, off-hand, back, shoulders — held
consistent across every frame of every animation.

**This cannot be deferred and it is not visible in the finished sprite.** A beautiful Sasha with
inconsistent hand positions looks identical to a beautiful Sasha with consistent ones, right up
until the first weapon is attached and swims. There is no test that catches it after the fact,
no critic that flags it, and no fix short of redrawing every frame.

**This clause is instrumentable** and should be: declared attachment points must sit within a
derived tolerance across all frames. Tolerance: PLACEHOLDER.

### 10.2 Equipment is layered, never pre-composed — LOCKED

The player is a stack: body, then weapon, shield, cloak drawn over it. Cost scales with items,
additively. Pre-composed variants scale with *combinations*, multiplicatively, and die on
contact with a roguelike item table.

### 10.3 Layer by silhouette class, not by item — LOCKED

At reference-device scale on a busy screen, role reads come from **silhouette and prop**, not
interior detail. The differences that matter are the ones that change the outline: a spear's
long diagonal, a shield's mass on one side, a cloak's fall behind the legs. **Sword versus mace
is a few pixels at the end of an arm and may not read at all.**

So: layer by class — long weapon, short weapon, shield, cloak — with variants inside a class
carried by palette rather than shape. A dozen or so layers, not a table of sixty. **A small
number of silhouette-changing layers delivers nearly all the perceived variety**, because what
the player registers is *"I look different now,"* not *"that is a mace."*

**Corroborated:** the asset bar's hero sheet is this clause running commercially — one base
figure, recoloured into families, variety through palette on shared structure. **Caution that
travels with it:** their recolours roam the whole spectrum; ours run inside the spine plus
region slots (§5.2). Yarl's families will be narrower and quieter than the bar's. That is the
register, not a shortfall, and a critic comparing family-variety against the bar must be told
so.

### 10.4 Layers bind to the rig — LOCKED

Every layer is authored against the same armature, with grip and attachment points landing on
the declared positions in **every** frame. A weapon whose grip drifts two pixels between walk
frames looks broken in a way that is very visible and very tedious to fix.

**Layering and animation multiply each other.** This is affordable only because §9.1 restricts
animation to one asset. Had the answer been "animate everything," §10.2 would be unaffordable.

### 10.5 Pilot sequencing — LOCKED

**Sasha comes last in the pilot**, after floors, walls, props, and one creature. He is the asset
most dependent on everything else being settled: he must read against the floors, win contrast
against the walls, carry the warmth the palette reserved for him, and stand next to the creature
he fights.

---

## 11. Layer and region ownership — PLACEHOLDER

The table below is a **shape**, not an assignment. Sources are not chosen and generation tooling
is a Phase 4 decision.

| Layer    | Content                                  | Source                               | Status      |
| -------- | ---------------------------------------- | ------------------------------------ | ----------- |
| Floor    | Floor tiles, wear states                 | TBD                                  | PLACEHOLDER |
| Wall     | Walls, two-plane volume, thresholds      | TBD                                  | PLACEHOLDER |
| Prop     | Made objects, fixtures, tagged inventory | TBD                                  | PLACEHOLDER |
| Creature | Orcs, undead, Hall Wardens, NPCs         | TBD                                  | PLACEHOLDER |
| Player   | Sasha, Hollowmark, equipment layers      | Bespoke — never a library pull (§10) | LOCKED      |
| UI       | HUD, memos, frames, type                 | TBD                                  | PLACEHOLDER |
| Light/FX | Engine-rendered (§6)                     | In-engine                            | LOCKED      |

**The asset manifest is the only source of truth for what exists.** If it is not in the
manifest, the project does not own it. Row format is adopted from Gemfall: file, layer, source,
verbatim prompt, style reference used, mean snap distance, licence, acceptance date — plus, for
animated assets, frame count and hit frame (§9.4).

---

## 12. Readability — PLACEHOLDER

Every clause in this section is a stated design purpose awaiting a derived value.

- **Names itself at 1×.** Identifiability at true display size, in the scene, is required
  regardless of style conformance. Carried over from the retired track; it was never an
  Oryx-specific rule.
- **Silhouette and prop carry the read.** Colour second. Interior detail not at all. An asset
  that only reads because of an interior detail you had to squint at is a failure.
- **Value separation from the surface beneath.** Yarl has **no allegiance chrome** — no rim, no
  backing plate, no under-figure highlight. Gemfall's value-floor rule is primary with an engine
  rim as backstop; **Yarl's equivalent is primary with nothing behind it**, because a plate under
  every creature is the institution helping you, and the institution does not help you.
  Threshold: PLACEHOLDER.
- **Survives a busy screen** (§4.1). Every rule above is tested with neighbours present.

### 12.1 No baked outline — LOCKED (Rafe, 2026-08-24)

**Nothing in Yarl carries a baked dark ring.** Separation is delivered by the value floor above
and by §7.1's linear elements — bands, straps, pins, tags.

Reasoning, recorded because a weaker version of it was offered first and should not be what the
rule rests on. A baked outline does **not** conflict with dynamic light the way a baked
highlight does: a highlight declares a light *direction* that a torch arriving elsewhere
contradicts, whereas an outline is direction-agnostic and modulates with everything else. That
argument is soft and is not the basis of this ruling. The three that hold:

1. **A fully outlined sprite reads as a sticker.** It separates as a discrete object regardless
   of illumination, flattening the light response §6 exists to buy. Heavy outlining and dynamic
   lighting partly cancel.
2. **It fails where it is most needed.** A dark ring against the near-black ambient of a deep
   floor is invisible. The outline works in bright scenes and abandons the player in dark ones,
   which is the wrong way round for a game whose light withdraws with depth.
3. **It competes with §7.1.** Bands, straps, and tags are the high-contrast linear elements
   carrying the read at 1×. A ring around everything is a second linear system fighting the
   first for the same few pixels.

**Parked fallback — not adopted.** An outline can live in the engine rather than the art
(Gemfall moved theirs there at their v1.1). If the pilot shows figures failing to separate from
floors, an engine-side rim remains available with **no redraw**. Leaning against it: §12 already
holds that the institution does not help you, and a ring under every creature is help. Recorded
so the door stays on its hinges.

**RULED (Rafe, 2026-08-26): PLANE-BOUNDARY OCCLUSION IS FORM. Legal, and required. The ring
stays banned.**

The distinction, because the composition spike flagged this as a live tension and it is now
settled: a **ring** is a dark edge drawn around a thing *because it is a thing*, present on every
side regardless of what adjoins it, and it is what makes a sprite read as a sticker. **Plane-
boundary occlusion** is a dark edge drawn where one plane stops and another begins — on the
wall's own edge, only where floor is adjacent, absent where wall meets wall. The two look alike
listed as pixels and are opposite constructions: one describes the object, the other describes
the *geometry between* objects.

The evidence that forced the ruling: composed two-plane walls rendered without it put a lit wall
top at luminance 96 beside a lit floor at 122 with no boundary of any kind, and a blind critic
could not tell solid from walkable — a `cannot-read` cull, twice. The shipped placeholder tiles
this renderer's mask table was fitted to had always carried it. §3's two planes do not, on their
own, separate wall from floor; this is what does.

**It does not compete with §7.1's linear elements — it is not on the object at all.** Straps,
bands and tags still carry the read across a sprite; occlusion carries the read across a
boundary. Both, not either.

**And it is mandatory, not merely permitted: a wall-top meeting floor without its occluded edge
is not purity, it is a missing plane.** This is construction grammar (§7), not outline — an
occluded seam exists only where two planes actually meet, varies with what adjoins it, and is
therefore form (§6.3). The test that separates it from a ring is stated in the worked example
below.

**A WORKED EXAMPLE, because the spike got this wrong on its first attempt and the error is the
instructive part. THE RING PROHIBITION IS VALUE-AGNOSTIC: A PALE RING IS A RING.**

Round 8 of the composition spike answered a critic's request for a cap band by laying a coping
course of paler, smoother stone along every floor-facing wall edge, and reasoned that a
*material* change declares no light direction and is therefore legal. The material reasoning was
sound and the construction was not. The blind seat:

> *"A flat, featureless ribbon at floor value is applied to every wall edge for its entire
> length, ringing each mass in bright piping so the quadrants read as cut-out cards rather than
> stone."*

Cut-out cards is the sticker read, arrived at from the opposite end of the value scale. The
ruling above already excludes it — *drawn around a thing because it is a thing, present on every
side regardless of what adjoins it* — and nothing in that sentence says dark. **What separates
occlusion from a ring is whether the treatment answers to the geometry it sits on, not whether
it is lighter or darker than its surroundings.** A uniform ribbon of constant width and constant
value applied to every edge answers to nothing.

The same round's ranking is the corroboration: the arm carrying the coping ribbon placed third
of five, below the arm with no cap at all.

**AND THE PROHIBITION IS SCALE-DEPENDENT AS WELL AS VALUE-AGNOSTIC — RULED (Rafe, 2026-08-27,
at the gate).** The worked example above established that a pale ring is a ring. This
establishes where you have to stand to see one.

C-GAB was called ring-clean by an instrument and by two blind seats, and **a frame at field
scale** by the gate. Nothing about the tile changed between those readings; the number of copies
did. A contour that turns its corners and returns *inside its own cell* is invisible as a ring
when you hold one tile and unmistakable as one when you lay nine — because the test that
separates a ring from a joint is **whether it continues into the neighbour**, and a single tile
has no neighbour to continue into.

> **A ring is judged AS LAID. A single tile — and a contact sheet of single tiles — cannot
> answer this clause.**

This is §8.3's scale rule reaching §12.1, and it is why the ring instrument's limit is
structural rather than a tuning failure: it reads one 32×32 tile, so the evidence is not in its
input at any threshold.

**Consequence for the re-aim audit:** `tools/art_lint/outline_repair.py` has no successor under
this ruling and is retired with the Oryx track.

---

## 13. Acceptance — LOCKED

### 13.1 In-scene review is the only approval for anything that lands

No candidate is approved from a standalone contact sheet. Verdicts come from the production
renderer, in the lit scene, seated among approved neighbours. During Phases 1–3, standalone
artifacts are exploration and are judged freely; nothing lands, so nothing needs the scene. The
rule activates at Phase 5, which is sequenced to satisfy it: **the pilot builds floors and walls
first, so the first approved assets ARE the scene**, and every prop and creature after them is
judged in context from day one.

§6.3 makes this a technical necessity as well as a discipline: a receive-light asset **cannot**
be judged unlit.

### 13.2 The human gate is the final instrument

Machine checks are floors, never verdicts. Every metric ever promoted on this project was
eventually humbled by an in-context human look.

> **VINDICATED AGAIN — 2026-08-27, the sighted round's device gate. This is the sharpest
> instance the project has produced, because everything upstream of the phone was green.**
>
> The sighted round did not fail its instruments. It passed them:
>
> - two independent blind seats ranked the candidate **above the asset bar**, unhedged, with no
>   cull — §13.3's own bar, met;
> - the differencing check passed and the arm it was compared against failed it;
> - the ring instrument passed every composed tile, its own control suite green;
> - the recipe's delivered numbers hit the bar's measured construction to two decimal places.
>
> **Rafe's verdict on the phone: FAIL. "The phone overrules the stills."**
>
> Nothing in that list was wrong as far as it went. The seats really did prefer it; the numbers
> really did land. **What they could not see is the thing the clause exists for** — the work at
> the size, the distance and the light it is actually played in. Two of them were looking at a
> 2× crop on a desktop, and one of them was a number.
>
> **The operative lesson, and it is about sequencing rather than about seats:** a stack of
> green instruments is not evidence of quality, it is evidence that the instruments were
> satisfied. **Instrument agreement raises confidence in the instruments, not in the asset.**
> The gate produced two laws in one look — §8.3.1 and §6.2.1 — that six critic-held rounds and
> thirteen seat transcripts did not.

Two gate screens are adopted from Gemfall, and they are the most portable artifacts in that
project's apparatus:

**Name them cold.** Candidates shuffled with already-shipping assets, and **which is which is
not shown.** This blinds the *human*, not just the critic — no grading on novelty, no softening
toward the thing you know is the candidate. The shipped assets act as a positive control on the
eye itself: if one of them stops reading, that is a finding about the test conditions rather
than the candidate. Each slot asks its own card's question, and a card may legitimately ask
*"tell it apart, do not name it"* where naming would be an unfair question.

**The cast on its worst ground.** Each candidate is shown against its own measured *worst*
contexts. The measure is **uncalibrated, renders no verdict, and only decides ordering. No pass
or fail is drawn on the screen. The eye rules.** This is the machine finding the hardest case
and then shutting up, and it is a strict upgrade to §13.1 — which otherwise says "judge in
context" without saying *which* context, and the honest default left alone is a flattering one.

Every gate screen states the contexts it measures and flags any context the shipping game does
not contain.

### 13.3 The quality bar

**PASS means genuinely wowed.** "Fine," "acceptable," "good enough for now," "improved,"
"solid," "promising," and "close" are all **failing** verdicts. Hedging is failing. A critic who
finds no defect should suspect its own rigour before crediting the work.

The visual bar is a **blind side-by-side against shipped commercial games**, asking *"which of
these looks like the shipped game?"* — and the answer must be Yarl, or a tie.

**Reference set — three bars, each assigned to one question. The assignment is what keeps a bar
from becoming a style target.**

- **Shattered Pixel Dungeon — the structure bar.** Grid, readability, portrait layout, how much
  information fits legibly on a phone. It solves Yarl's exact problem. The gameplay bar; the
  look must exceed it.
- **Rogue Wizards — the scene bar.** Light, material, depth, and above all cohesion: everything
  made to the same standard, nothing left provisional. Landscape and isometric, so its
  projection is explicitly **not** a target (§3).
- **Oryx Ultimate Fantasy — the asset bar.** Per-sprite craft: the standard a single Yarl asset
  must meet or beat on a like-for-like look. Recorded in the owner's words, because they are the
  bar speaking: *clean, small, detailed, serious; the threats are threatening; a tasteful
  palette without being overdone; a baseline of animation; wow factor.* This library is also the
  animation-coverage spec for §9 (basic movement and attack, nothing lavish) and approved plant
  stock for critic control rounds — professionally drawn and in the wrong register is precisely
  the failure a soft critic waves through.

**The presentation caveat.** Oryx Ultimate's wow is partly presentational — heroes centred,
posed, composed for the sheet. Yarl's register forbids staging (§1). The bar is their craft,
never their presentation: a Yarl asset must stand beside theirs while unposed, indifferent, and
in a corridor. When a comparison reads "theirs looks better," the first question is **better
made, or merely better posed?** — and that question belongs in the critic's kit.

**This is a quality comparison, not a style target, and the distinction is thin enough to state
plainly: we ask whether Yarl looks as finished, never whether Yarl looks like them.** A finding
that an asset "doesn't match SPD" is not a defect. A finding that it "looks like the free one
next to the paid one" is.

**The guard — LAW.** A bar may never appear in a flip list. "Make it more like [bar]" is an
illegal critique in any round, from any critic, machine or human. Comparisons answer *are we as
good*; only the bible answers *what we should look like*. **DNA and bars never swap roles:
nothing conditions generation that we do not own** (§1.3), and nothing we own is above being
judged against the best.

**WHERE THE BARS LIVE, and the one rule that governs reading them — RECORDED (2026-08-27).**

| bar | location | status |
|---|---|---|
| **Oryx Ultimate Fantasy** — asset bar | **`~/development/assets/oryx`** — the full library, licensed, local | available for measurement |
| **Shattered Pixel Dungeon** — structure bar | not on this machine; **Rafe supplies captures** | outstanding |
| **Rogue Wizards** — scene bar | not on this machine | outstanding |

Recorded so a future round does not re-hunt for a source it already has, and so an absent one is
known to be absent rather than discovered mid-round. The sighted round lost its second source
that way: the brief named SPD, nothing on the machine matched, and the recipe went out
**single-sourced and said so** (`tools/sighted_round/WALL-RECIPE.md` §1).

> **RULED (Rafe, 2026-08-27): naming a source that is not there is the PROMPT's error, not the
> session's.** The correct response to a missing bar is to report the gap, not to substitute a
> nearby source and call the work two-sourced. A recipe that says *single-sourced, and here is
> what that costs* is worth more than one that quietly fills the hole.

**MEASUREMENTS LEAVE; PIXELS NEVER DO.** A tool may read a licensed local library and emit
numbers — `measure_bar.py` is the pattern: it wrote `bar_measurements.json` and nothing else.
**No bar pixel enters this repo, in any composite, reference, or corpus (§1.3), and a known path
does not relax that by one pixel.** The path above is an instruction for measurement tools, not
an invitation to the asset pipeline.

**The origination rule — LAW.** The bar may *occasion* a law; only the register may *justify*
one. Every law in this bible must cite its register derivation, not merely its bar observation
— the v0.5 pass is the worked precedent: faceless creatures follow from §1.1's division of
warmth, heraldic stance follows from a world where everything is bound in place; the bar was
where we noticed, the register is why it's true. **A proposed rule whose only justification is
"the bar does it" is conformance and is refused**, regardless of how good the bar is. This
clause exists because the bible now cites the asset bar in nine sections, and the distance
between "lessons cross" and "style conformance" must be a test, not a paragraph's goodwill.

### 13.4 Register clauses are carried eye-side and are never instrumented — LOCKED

**This is the most important process clause in this document.**

Gemfall's Ruling 77.5: *where a selection process optimises against a mixed set of criteria, the
ones with instruments win and the ones without them are silently traded away* — not because
anyone chose to, but because only one side of the trade is visible to the optimiser. Their
worked case: a figure's declared hi-vis vest ended with 10 torso texels against 68 in its hat,
because a candidate carrying real torso signal was traded away to satisfy a palette clause. The
palette clause won because it was the one with a number.

**Yarl's register is almost entirely uninstrumentable.** *The art plays it straight. Nothing is
ruined; things are used up. Nothing is staged.* No script checks these. And they are exactly
what got traded away last time — the previous track had instruments for everything except the
question that mattered.

Two binding consequences:

1. **Register clauses are carried at the human gate, with explicit weight, and are never
   assumed to survive an automated selection that cannot see them.**
2. **We do not close the gap by inventing an instrument.** A weak proxy is worse than an
   acknowledged absence, because it re-enters the optimisation and starts winning trades it has
   not earned. The precedent is a personhood predicate that passed **67.55% of random noise**
   with a ruling already resting on it. **There will be no "dread score" and no "staging
   detector."** §15's honest `NO INSTRUMENT` row is the correct output instead.

### 13.5 No instrument's pass counts until it has demonstrated it can fail — LOCKED

Adopted verbatim in force from Gemfall's Ruling 47. Positive control **before** verdict, for
every critic, census, measure, and harness. Stub the metric to a constant, plant the defect it
exists to catch, mutate the thing it guards — then show it goes red and record the verbatim
failure. **An instrument that cannot be made to fail is decorative and must be labelled so or
deleted.**

This is the same failure class already named on this project as MISFED. Gemfall supplies the
procedure that catches it.

### 13.6 A candidate never contributes to its own acceptance bar — LOCKED

Where a constant must be calibrated, derive it from the corpus already accepted, never from the
work seeking acceptance. **The eye leads the number: calibrate after the verdict, never before
it.**

### 13.7 Platform facts — measured, recorded once so nobody re-buys them

Not law, and not banked speculation either: each line below was paid for by a run and is cited
to the audit that paid. They are here rather than in the tooling notes because each one closes a
question a future session would otherwise re-open with generations.

- **Architecture and conditioning do not exist on the same surface.** BitForge conditions
  (12/12 propagation, §5.5) and produced architecture **0/100**; tiles-pro produces clean parts
  (0 mechanical culls in 114) and refuses style conditioning on connectable features. **Any
  pipeline needing both composes across surfaces.**
- **tiles-pro is a parts supplier, not an instrument.** Promoted to the stock role on the
  audit's evidence; failed as a standalone wall instrument (**0/114** two-plane).
- **The wall road is composition.** Six-for-six on relationship defects (the composition spike);
  generation supplies materials and parts only.
- **All three camera parameters are spent.** `tile_view` is a silent no-op; `tile_view_angle` and
  `building_wall_angle` are live but reach only the front elevation; `tile_depth_ratio` extrudes
  thickness downward. **No parameter adds a plane that was never painted.**
- **Nothing on this platform is seed-reproducible** — measured on every surface tried. The ledger
  therefore stores **images, not parameters**, and that is process law rather than preference
  (§6.4's evidence note says the same thing from the other end: a parameter row is not evidence).

Sources: PRs #142 (probe 6.4 surface audit), #144 (wall gauntlet), #145 (tiles-pro audit), #146
(composition spike).

---

## 14. Out of scope for this document

**Sound.** Deferred deliberately, not overlooked. Sound has almost no coupling to the decisions
in this bible: it does not constrain how a sprite is drawn and has no one-way doors. Two notes
banked for a future workstream:

- Timing binds to animation frames (§9.4 exists for this reason).
- **The register applies to audio unchanged.** The world does not notice you; nothing is staged.
  The ambience is that of a place that would sound the same if you were not in it. Sasha and
  Hollowmark carry the warmth there too.

**Generation tooling, critic prompts, gate tables, and the screen stack.** Phase 4.

---

## 15. Instrument audit — which clauses can actually be checked

**A law nobody can measure is decorative. This is the honest audit, and at v0 it is mostly
gaps — which is the correct state for a bible whose pilot has not run.**

| Clause                                                 | Instrument                          | Status |
| ------------------------------------------------------ | ----------------------------------- | ---------- |
| §5.1 zero off-palette pixels                           | Palette check, adopted from Gemfall | **Portable, not yet built** |
| §5.2 region slot legality                              | Same check, region-flagged          | **Portable, not yet built** |
| §5.3 warm-share allocation per asset                   | None                                | ⚠ **NO INSTRUMENT.** Purpose stated; threshold may not exist (Ruling 70 applies). |
| §5.4 chroma is signal                                  | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN.** **The countable proxy is named and refused:** saturated-pixel share is measurable, but share is not signal — a census can count saturation and cannot see meaning, so the number would gate the wrong thing and win trades it hasn't earned (§13.4). If a saturation census is ever built, it is ordering-only under the worst-ground pattern (§13.2), renders no verdict, and earns promotion like any instrument (§13.5). |
| §5.5 reference neutrality (style parent vs prop stock) | None                                | ⚠ **NO INSTRUMENT.** Applied when a reference is chosen, by eye. The 12/12 propagation measurement is the *evidence for the rule*, not a gate over candidates — a "composition similarity" score would be exactly the weak proxy §13.4 refuses. |
| §6.3 receive-light (no baked highlight)                | Blind LLM census, plant-controlled   | **BUILT AND PROMOTED, NARROWLY.** `tools/pixellab/probe_6_4/blind_census.py`. A blind read, not a metric (§13.4 v0.3: a script emitting a number is an instrument; a critic rendering a verdict is not). Passed its control **10/10** against *constructed* plants — ground truth taken from the prompt would have been circular. **Licensed for KEY vs not-KEY only, at plant strength.** The FORM-vs-FLAT boundary carries no control and is reported unlicensed, because a donor tile that is already near-flat yields a "flat plant" a truthful eye may correctly read as FORM, and tuning plants until that stopped would manufacture an instrument that cannot fail. |
| §6.3 occlusion, not illumination (no encoded light direction) | Differencing check, light-off      | **BUILT AND PROMOTED, ONE AXIS.** Authored form must survive the engine light being switched off; a per-block top-bright/bottom-dark emboss fails the diff. Demonstrated its fail on the round-8 plant before any pass was counted (§13.5). **Licensed for encoded-light-direction only** — it says nothing about whether the form that survives is any good, which stays eye-side (§13.4). **AND IT HAS NOW CAUGHT A REAL ARM, not only a plant (2026-08-27):** the composition spike's `before` arm measures unlit face÷top **1.22** — face brighter than top, no authored plane separation at all — so the plane structure eight rounds were measured against was the engine's light, not the art. That is the arm its own round-8 seat ranked first of five. An instrument's first real catch is worth more than its control, and this one overturned an inference rather than a candidate. |
| §6.5 the value stack (floor between the planes) | Plane-ratio measurement, `tools/sighted_round/checks.py` | **BUILT, AND HONESTLY NARROW.** Reads top/floor and face/top off a lit capture and off an unlit one. It measures whether the ratios are *present*, which is real and was the finding; it does **not** measure whether they read as planes to an eye — rounds 1 and 2 had the ratios broadly right and were culled `wrong-projection` for §3.1, which no ratio detects. **Licensed for ratio-presence only.** Its delivered numbers are also rig-coupled (§6.2's flag), so a pass is a pass *on this rig*. |
| §6.3 no baked drop shadows                             | None                                | ⚠ **NO INSTRUMENT.** Joins the directional-highlight census as owed; same status, same caution — Gemfall's analogue measured as a blunt proxy and was refused a verdict. |
| §7.1 everything is held                                | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Eye-side, at the gate. |
| §7.4 heraldic stance (idle sprites are icons)          | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Blind critic eye + human gate. |
| §8.1 wear explained by traffic and indifference        | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** |
| §8.3 the motif trap — no incident baked into a base tile | **Split, and the split is the point** | ⚠ **HALF INSTRUMENTABLE, HALF NEVER.** *Verbatim repetition* is trivially checkable and should be — a field laid from one tile is a byte comparison, and the check would have gone red on every floor round to date. **Whether a mark is material or incident is NOT**, and no proxy for it will be built: it is the difference between a joint between two stones and a crack through one, which is a reading, not a measurement (§13.4). Build the cheap half, refuse the other, and never let the cheap half's green stand in for the whole clause. |
| §12.1 ring judged as laid (scale rule)                 | None at tile scale — structurally    | ⚠ **NO INSTRUMENT, AND THE EXISTING ONE IS DISQUALIFIED BY INPUT.** `ring_instrument.py` reads one 32×32 tile; the property lives at field scale, so no threshold reaches it. Recorded because this is the audit's sharpest lesson to date: **an instrument can be correct, controlled, and still be answering at the wrong scale** — and its label now says so (`REPORT.md` §6). |
| §10.1 attachment-point tolerance across frames         | Buildable and should be built       | **Owed at the Sasha tier.** The one genuinely instrumentable register-adjacent clause in this document. |
| §12 value separation from surface beneath              | None                                | ⚠ **NO INSTRUMENT.** Gemfall's Ruling 70 found no defensible threshold for their analogue; expect the same and prefer the refusal. |
| §12 names itself at 1×                                 | The human gate (§13.2)              | **Eye-side by design.** |
| §1.1 zero expression budget (world creatures faceless) | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Blind critic eye + human gate. |
| §1 register conformance, all clauses                   | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** |

**Fifteen of nineteen clauses have no working instrument today. None is papered over. Eight of
them will never have one, deliberately, and that is a decision rather than a gap.**

**One row goes GREEN on evidence at v0.11 and one existing row earns its keep — the first
revision where the audit moved in the project's favour without a new instrument being built.**
§6.5 arrives with a real measurement behind it and a narrow licence. The §6.3 differencing check
made its **first catch on a real arm** rather than a plant, and what it caught was an inference
that eight rounds had rested on. **The caution attached to both: a ratio check cannot see §3.1** —
rounds 1 and 2 had the values broadly right and were culled `wrong-projection` anyway.

**Two rows are new at v0.10, and both are red — which is the audit working in the direction that
costs something.** §8.3 arrives as law with its instrument **split**: build the byte-comparison
half, refuse the material-vs-incident half outright. §12.1's scale row is worse than a gap and is
recorded as such: an instrument that exists, passed its controls, and is **disqualified by its
input** — it reads one tile and the property is in the field. *An instrument can be correct,
controlled, and answering at the wrong scale*, and nothing in §13.5's promotion procedure catches
that, because a positive control built at tile scale confirms tile-scale behaviour perfectly.
**§13.5 gains an implied question a future revision should make explicit: at what scale does this
control prove anything?**

**Two rows were new at v0.8, and they move in opposite directions — which is the audit working.**
§6.3 gained a second instrument, the light-off differencing check, promoted on a demonstrated
fail and licensed to one axis; §5.5 arrived as law with **no** instrument and the countable proxy
named and refused in the row. A revision that only ever adds green rows is not auditing itself.

**One row moved at v0.7, and only one.** §6.3 gained a plant-controlled blind census —
the *first* instrument on this track to demonstrate it can fail before its passes were counted
(§13.5). It is deliberately not a script emitting a number, and its licence is narrow: one axis,
at plant strength. The unlicensed half is reported as unlicensed rather than quietly folded in,
which is the whole of §13.4 working as intended.

---

## 16. Banked observations — NOT LEGISLATED

Recorded so they are not re-derived; deliberately not law.

- **Layered portraits.** The asset bar composes portraits from separate base/hair/hood/feature
  layers — §10.2's additive philosophy applied to faces, and the one place the library permits
  expression. If the dialogue system ever wants NPC portraits (Borrek, Hael, the Under-Warden's
  office), the pattern is solved and composes with §1.1's expression rule: faces live at
  dialogue range, never at sprite range. Owned by the Spine thread if ever scoped.
- **Hue-coded item states.** Monochrome accent variants (the bar's gold/cyan/magenta weapon
  rows) are chroma-as-signal at item scale and would give identification/curse/mention
  mechanics a free visual vocabulary. Game-design surface, not art law. Owned by Combat/Spine
  if ever scoped.
- **Plant stock catalogued.** The bar's cobwebbed crypt corners and staged-horror compositions
  (blood pools, skull altars) are register-illegal in Yarl (§1, §8.1) and therefore ideal
  critic plants: professionally drawn, wrong register — the exact failure a soft critic waves
  through. Already sanctioned in §13.3; noted here so the specific sheets are remembered.

---

*Revision history:*

- *v0.12 — 2026-08-27. **The sighted round's device gate: FAIL, and two laws come out of it.**
  Rafe walked the rounds-4/5 build on the phone and overruled the stills. **§3's status trail
  gains the gate entry** — §3 is neither ratified nor rejected and **rides PROVISIONAL into tier
  one**, carrying the recipe, §3.1 and the Q3 control finding intact; the two entries beneath it
  are kept, because a trail that overwrites itself is not a trail. **New §8.3.1:** the motif trap
  applies to WALL material identically — wall tops are incident-free material, and boundary rules
  and edge ticks are pattern and are out. This culls the 16 px joint grid §3.1's own round built
  four hours earlier, and the clause generalises past both asset classes: *any treatment applied
  at a constant position within a tile becomes a lattice when tiled.* **New §6.2.1, a TIER-ONE
  PRECONDITION:** the rig's radius, falloff and ambient get a readability-tuning pass **before any
  asset is judged through them** — the value stack must be legible at gameplay distance, not at
  two tiles; tune the one table of numbers rather than every asset in the game. **§13.2 gains its
  sharpest instance**: every instrument upstream of the phone was green — two seats above the bar,
  differencing passed, ring clean, delivered numbers on target — and the gate still said FAIL.
  Instrument agreement raises confidence in the instruments, not in the asset.*
- *v0.11 — 2026-08-27. **The sighted round's rulings land — the first round on this project run
  with sight, under §13.3's origination rule.** **NEW §6.5, THE VALUE STACK**, and it is the wall
  campaign's load-bearing finding: **the floor sits BETWEEN the wall's two planes** — top ≈1.11×
  floor, face ≈0.5–0.6× floor. Register derivation is §6.3 occlusion expressed as a ratio: the
  top catches light, the face is where light cannot easily reach, and enclosure is direction-free
  so the stack is material rather than depiction. Yarl had the relationship **inverted** (face
  brighter than top, both below the floor), which is the whole of the eight-round "no thickness"
  finding — no side face required to explain it. Corrected, two blind seats ranked Yarl **above
  the asset bar** on depth. **NEW §3.1, THE FLAT-TOP RULE:** a top surface is not face material
  re-toned; a plane is made by changing what the texture is a picture of, not its value. Two
  seats culled `wrong-projection` for it independently, and no value change reaches it. **§3's
  premise is VINDICATED by the Q3 control** — the bar carries §3's own limitation, measured by
  two seats unasked ("a vertical wall in B has literally zero thickness"), so the clause was
  never on trial; §3 stays PROVISIONAL and ratification waits on the device gate (§13.1).
  **§6.2 gains a COUPLING FLAG:** the engine compresses the authored ratio by a measured 1.48
  because the player is the lamp, so authored ratios are derived backwards from delivered targets
  on the current rig and **must be re-derived when §6.2's PLACEHOLDER values are ratified** — the
  art-to-rig dependency is named, not solved. **§13.3 records where the bars live** and restates
  that measurements leave while pixels never do. All results are qualified at **4-of-5-seat
  strength**: the plant was waved through once, voiding round 2, which stays void. Evidence:
  `tools/sighted_round/`.*

- *v0.10 — 2026-08-27. **The gate answered the C-GAB question and the answer generalised into
  law. NEW §8.3 — THE MOTIF TRAP:** any incident baked into a tile becomes a motif when tiled;
  repetition converts accident into intent, and the eye reads pattern regardless of the
  incident's quality. Therefore **a tile is the material and the incident is the variant** —
  incident (cracks, wear, marks, the §8.2.1 channel) arrives at the instance level, randomised,
  through the variant and overlay system tier one builds. **§5.5's parent criterion sharpens**
  from *compositionally neutral* to **incident-free**, which strikes its own worked example: the
  crack-through-a-field offered as the shape of a neutral parent is the tile the gate then ruled
  a frame. **§5.5's flagged note is RESOLVED — frame at field scale**; C-GAB retains its
  conditioning role because references never ship, and is recorded as retained under screening
  rather than as meeting the sharpened bar. **§12.1 gains the scale rule:** the ring prohibition
  is scale-dependent as well as value-agnostic — **a ring is judged as laid**, and a single tile,
  or a contact sheet of single tiles, cannot answer the clause. The ring instrument's limit is
  therefore structural, not a tuning failure: it reads one 32×32 tile and the evidence is not in
  its input. **§8.2.1's variant system is re-scoped** as the only place incident is permitted to
  live. Retroactively, this completes the floor-remediation round B finding: those tiles were
  bases judged as finished floors before the incident system existed. Evidence:
  `tools/floor_remediation/REPORT-PARENT-RATE.md` and its `exhibit_cgab/` 3×3 plate — the view
  that could run the continue-or-return test no seat had ever been given.*

- *v0.9 — 2026-08-27. The floor campaign's rulings land. **§5.5 gains its corpus assignment**
  (Rafe): C-GAB primary style parent, A-HEB secondary, **A-VAB prop stock regardless of
  surgery** — de-ringing removes a keyline and does not make a framed plaque neutral, and it is
  the composition that propagates — and **B-KAB retired from conditioning with no remediation**,
  its regenerated candidate not promoted. §5.5 also gains a **cross-confirmation**: a blind seat
  on the floor campaign, never given this bible, rediscovered the clause's own composition
  finding by culling A-VAB as "a framed plaque" — the wall campaign's "recessed frame" reached
  independently, in a different medium. And **its 2026-08-26 measurement is corrected**: the
  ring was recorded in luminance ("~3px near-black, B-KAB at 14 against a median of 130") by an
  instrument that thresholded value at 0.30× the median; measured on geometry instead, **two of
  the four carry rings, not one** — A-VAB's two 1px loops sit at 0.48× and were invisible to it,
  while A-HEB and C-GAB never carried a ring at all. **§8.2.1 gains the tier-one requirements**
  the same seat produced — a variant system, the wear system this clause already specifies, and
  a floor-repair vocabulary — banked as requirements rather than as a verdict on the corpus,
  with the standing note that a one-wide corridor cannot pose the §8.2 question and this round's
  scene did not meet §8.2.1's own four-scene rule. Instrument, controls, verbatim seat
  transcripts: `tools/floor_remediation/`.*
- *v0.8 — 2026-08-27. The wall campaign's rulings land. **§6.3 gains the occlusion law** —
  occlusion, not illumination, stated as a vocabulary — with the **vocabulary-collision record**
  (a 1px chamfer request and a depth parameter manufactured the same violation on two different
  surfaces: a property of the scale, not of any tool) and the **light-off differencing check**
  promoted per §13.5 with its demonstrated fail on the record, one axis only. **§12.1** gains the
  mandatory half: a wall-top meeting floor without its occluded edge is a missing plane, not
  purity — construction grammar, not outline (the value-agnostic ruling and the pale-ring worked
  example landed with the spike and are unchanged here). **§3 is PROVISIONAL under active test**
  rather than reopened: three confounds named against the spike's evidence, and the sighted
  round's criterion declared before it runs, with the licensing fallback named as a last resort.
  **New §5.5:** composition propagates with material at 12/12, so reference neutrality is a
  criterion — neutral references are style parents, charactered ones are prop stock — carrying
  the corpus note that nothing conditions on an un-remediated §6.4 survivor. **New §13.7:**
  platform facts recorded once, so no future session re-buys them with generations. §15 gains
  two rows, one instrumented and one deliberately not. Sources: PRs #142–#146 and the
  design-thread rulings of 2026-08-25/26.*

- *v0.7 — 2026-08-26. **§6.3 RATIFIED** (Rafe, STOP 2, on the reference device): receive-light
  survives its probe and the clause is no longer provisional. §6.4 closed and preserved as
  authored, with the outcome appended rather than the criterion rewritten — a bar edited after
  the answer is visible cannot demonstrate it was declared before it. **The ratification is
  recorded narrowly:** Stage 1's positive control failed, no arm produced a baked key light, so
  this ratifies the treatment under light and is not a victory over a baked arm. Retirement
  triggers named. §15's §6.3 row moves from NO INSTRUMENT to a plant-controlled blind census —
  the first instrument on this track to demonstrate it can fail — licensed for one axis at plant
  strength, with the unlicensed half reported as unlicensed. Count 13→12.*

- *v0.6 — 2026-08-25. §15 audit catches up with the v0.5 law: four rows added (three
  BY-DESIGN, shadows census owed), counts corrected; the chroma share-proxy is named and
  refused in the row. §9.1 scope line rewritten — the four states are the set, additions
  displace. §13.3 gains the origination rule: the bar occasions, the register justifies.
  All three from the v0.5 post-merge review.*
- *v0.5 — 2026-08-25. The asset-bar study pass, both halves. §9 gains frame arithmetic
  (PROVISIONAL pending source-file count) and Sasha's 6–8 frame budget; §1.1 the zero
  expression budget; §7.4 the heraldic stance rule; §5.4 generalised to chroma-is-signal at all
  scales; §4.2/§3 corroborations recorded; §6.3 extended to baked shadows; §10.3 corroborated
  with the narrower-families caution; §16 added for banked non-law. Sourced from study of
  licensed sheets in chat; no Oryx pixel enters any pipeline.*
- *v0.4 — 2026-08-25. **§8.2.1 added** (Rafe): the trodden channel as the primary legible-wear
  grammar; one-wide corridors are trodden or neglected, both drawable; review scenes must pose
  the question in four contexts. **§13.3 restructured** (Rafe): three assigned bars — SPD
  structure, Rogue Wizards scene, Oryx Ultimate asset — with the presentation caveat and the
  bar-never-in-a-flip-list guard as LAW. Both from rulings taken in conversation 2026-08-25.*
- *v0.3 — 2026-08-24. **§12.1 RULED** (Rafe): no baked outline anywhere; separation by value
  floor and §7.1 linear elements. Engine-side rim parked as an unadopted fallback.
  `outline_repair.py` retired. **§13.4 amended** (Rafe): a script emitting a number is an
  instrument and enters the optimisation; a blind LLM critic rendering a prose verdict is not.
  Two gates — the critic gates the loop, the human gates the landing. No script ever scores
  register.*
- *v0.2 — 2026-08-24. **§7.3 RULED** (Rafe): Unshriven construction is competent but tough —
  strength only, nothing present for appearance. **New §6.4:** receive-light demoted from
  committed to PROVISIONAL, with a three-arm probe (baked control / no-key-light /
  flat), a positive control, and a kill criterion declared before the probe runs. The named
  risk is that generation models default to depicting light, which would make §6.3 the
  external-corpus trap in new clothes. Probe runs BEFORE the Phase 5 pilot, because §6.3 is a
  one-way door.*
- *v0.1 — 2026-08-24. Initial draft. Written before any pixel work, from Phase 1–3 decisions
  taken in conversation. §1 register locked at Phase 1 sign-off. §2 scope locked to demo-first
  (Boundary, floors 1–5). §3 projection provisional pending pilot. §5–§10 decided in Phase 3
  conversation; all numeric values PLACEHOLDER. §13 acceptance adopted from Gemfall's
  LOOP-PROCESS with §13.4 added — register clauses eye-side, no proxies — as the specific
  correction for the previous track's failure. §15 instrument audit honest at nine of ten
  clauses uninstrumented.*
- *Predecessor: the Oryx-conformance track (closed 2026-08, concluded rather than failed).
  Findings banked in §1.3 and §3. The two-plane perspective rule and "names itself at 1×"
  survive on their own merits and are re-adopted here, not inherited.*
