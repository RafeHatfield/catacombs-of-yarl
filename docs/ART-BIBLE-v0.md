# Catacombs of Yarl / The Under-Warden — ART-BIBLE v0

**Status: v0.4 — DRAFT. Nothing in this document has been derived from a rendered asset.**

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

## 3. Projection and grid — PROVISIONAL, ratified by the Phase 5 pilot

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

**Why PROVISIONAL:** this has not been tested on a Yarl asset at Yarl's density. The Phase 5
pilot builds floors and walls first, which makes it the natural probe. If two-plane walls in a
portrait orthogonal grid do not deliver the volume we want, we find out in the cheapest tier,
before a single prop or creature exists.

**Isometric *objects* are not forbidden** — the ban is on an isometric map.

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

### 6.3 Assets are authored to RECEIVE light, not to DEPICT it — LOCKED

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

### 6.4 Receive-light is PROVISIONAL pending a probe that runs BEFORE the pilot

§6.3 is a committed direction, **not an unconditional one.** It is the clause in this document
with the largest unmeasured effort cost, and it is struck if the probe below says so.

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

Scope: walk, a basic attack, taking a hit, and a small number of others. Mild, not lavish.

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

| Clause                                          | Instrument                          | Status                                                       |
| ----------------------------------------------- | ----------------------------------- | ------------------------------------------------------------ |
| §5.1 zero off-palette pixels                    | Palette check, adopted from Gemfall | **Portable, not yet built**                                  |
| §5.2 region slot legality                       | Same check, region-flagged          | **Portable, not yet built**                                  |
| §5.3 warm-share allocation per asset            | None                                | ⚠ **NO INSTRUMENT.** Purpose stated; threshold may not exist (Ruling 70 applies). |
| §6.3 receive-light (no baked highlight)         | None                                | ⚠ **NO INSTRUMENT.** A directional-highlight census is owed. Gemfall's equivalent measured as a blunt proxy and was refused a verdict. |
| §7.1 everything is held                         | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Eye-side, at the gate. |
| §8.1 wear explained by traffic and indifference | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).**                     |
| §10.1 attachment-point tolerance across frames  | Buildable and should be built       | **Owed at the Sasha tier.** The one genuinely instrumentable register-adjacent clause in this document. |
| §12 value separation from surface beneath       | None                                | ⚠ **NO INSTRUMENT.** Gemfall's Ruling 70 found no defensible threshold for their analogue; expect the same and prefer the refusal. |
| §12 names itself at 1×                          | The human gate (§13.2)              | **Eye-side by design.**                                      |
| §1 register conformance, all clauses            | None, and none will be built        | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).**                     |

**Nine of ten clauses have no working instrument today. None is papered over. Four of them will
never have one, deliberately, and that is a decision rather than a gap.**

---

*Revision history:*

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
