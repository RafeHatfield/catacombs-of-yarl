# Catacombs of Yarl / The Under-Warden — ART-BIBLE v0

**Status: v0.8 — DRAFT. One clause has been derived from rendered assets on the device (§6.3);
one more is under active test in the sighted round (§3). Everything else in this document still
has not been derived.**

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

## 3. Projection and grid — PROVISIONAL, under active test by the sighted round

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

**STATUS TRAIL (2026-08-26): THE RULED CONDITION FIRED. §3 WAS REOPENED, WITH EVIDENCE — and
what replaces it, if anything, is Rafe's ruling and not the spike's.**

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

- **Compositionally neutral references are style parents.** C-GAB's crack-through-a-field is the
  shape of one: a material, evenly presented, that is a picture of nothing in particular.
- **Charactered references are prop stock.** One-off assets in waiting — never conditioning
  parents, however good they are as images.

**The seed corpus wants the boring ones.** A reference chosen because it is handsome is a
composition about to be copied twelve times.

**Corpus status (2026-08-26).** The four §6.4 survivors carry a measured §12.1 defect: a uniform
~3px near-black ring, B-KAB at luminance 14 against a median of 130. Remediated,
provenance-linked versions supersede them **upon Rafe's re-curation**; the originals stay in the
ledger untouched, because a ledger that edits its own history is not evidence. **Nothing
conditions on an un-remediated survivor.**

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

Only the Boundary's values are derived at the pilot. The rest are PLACEHOLDER.

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
| §6.3 occlusion, not illumination (no encoded light direction) | Differencing check, light-off      | **BUILT AND PROMOTED, ONE AXIS.** Authored form must survive the engine light being switched off; a per-block top-bright/bottom-dark emboss fails the diff. Demonstrated its fail on the round-8 plant before any pass was counted (§13.5). **Licensed for encoded-light-direction only** — it says nothing about whether the form that survives is any good, which stays eye-side (§13.4). |
| §6.3 no baked drop shadows                             | None                                | ⚠ **NO INSTRUMENT.** Joins the directional-highlight census as owed; same status, same caution — Gemfall's analogue measured as a blunt proxy and was refused a verdict. |
| §7.1 everything is held                                | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Eye-side, at the gate. |
| §7.4 heraldic stance (idle sprites are icons)          | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Blind critic eye + human gate. |
| §8.1 wear explained by traffic and indifference        | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** |
| §10.1 attachment-point tolerance across frames         | Buildable and should be built       | **Owed at the Sasha tier.** The one genuinely instrumentable register-adjacent clause in this document. |
| §12 value separation from surface beneath              | None                                | ⚠ **NO INSTRUMENT.** Gemfall's Ruling 70 found no defensible threshold for their analogue; expect the same and prefer the refusal. |
| §12 names itself at 1×                                 | The human gate (§13.2)              | **Eye-side by design.** |
| §1.1 zero expression budget (world creatures faceless) | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Blind critic eye + human gate. |
| §1 register conformance, all clauses                   | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** |

**Thirteen of sixteen clauses have no working instrument today. None is papered over. Seven of
them will never have one, deliberately, and that is a decision rather than a gap.**

**Two rows are new at v0.8, and they move in opposite directions — which is the audit working.**
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
