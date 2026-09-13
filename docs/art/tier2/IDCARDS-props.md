# Tier two — the Boundary's props: identity cards

Three props, written to `docs/art/tier1/IDCARD-SCHEMA-tier1.md` v0.1, with the tier-two fields
the schema does not yet carry marked as such. **Written before generation, as the schema
requires; nothing has been generated.**

> ⚠ **THIS PASS HAS NOT FIRED. Precondition 2 of `CC-SESSION-tier2-props.md` is not met:**
> *"Walls LANDED, §3 ratified."* Walls are landed; **§3 is not ratified** — the bible's own status
> trail says *"§3 IS NEITHER RATIFIED NOR REJECTED — IT RIDES PROVISIONAL INTO TIER ONE"* and
> *"RATIFICATION WAITS ON THE DEVICE GATE (§13.1)"*, under the ruled condition *"depth arriving
> ratifies §3; depth failing reopens it with evidence."* That judgement is a one-way door and is
> Rafe's alone. These cards are the part of the pass that can be done without it, so that the
> generation budget is spent the day the door opens rather than a session later.
>
> `park_state: prepared-not-generated` on all three.

**PALETTE REGIME, DECLARED AS PRECONDITION 3 REQUIRES.** §5's values are still `PLACEHOLDER`;
§5.1's derivation has **not** landed. So **the ladder regime continues** — assets are authored to
the family's measured value ladder, not to a locked hex list — and this sentence is repeated in
every report this pass produces.

**THE DIRECTION RULING GOVERNS ALL THREE** (Rafe, 2026-08-28): *mass in the silhouette, weight
straight down, gear over-built and oversized.* Refused by name: trophy spikes and ornament (§7.3
— a spike that holds nothing is decoration), fury poses (§7.4 — heraldic, planted), specular
sheen and rim-glow (§6.3 outlaws both).

**THE PASS'S OWN ACCEPTANCE CRITERION, routed here from the wall lane:** orc work must be visible
**as standing objects in the lit radius** of the walked scene. It is also #167's exit — *"the
prop/overlay pass gives wall tops world-placed OBJECTS standing on them ... so §8.3.1 does not
reach them."* If this pass passes, #167 closes with it.

---

## B-PROP-001 — the boundary marker stone

```yaml
id: B-PROP-001
layer: prop
region: boundary
title: "the boundary marker stone — institutional cut stone under four hundred years of orc work"

role: "A dressed stone post or slab set by the institution to mark a boundary, still standing,
       still doing its job, and repaired onto by orcs for four centuries."
role_accept:
  - "an old marker stone somebody keeps mending"
  - "a boundary post"
  - "a survey or claim stone with fixings driven into it"
role_reject:
  - "a gravestone"          # nothing here is commemorative; the place is administered, not mourned
  - "a shrine or altar"     # §7.4 — nothing is arranged for anyone's benefit
  - "a monster"             # silhouette must not read as a figure at 32px
  - "rubble"                # it is standing and in use, not spent
  - "a wall segment"        # the near-miss that matters: it must read as an OBJECT, not masonry
role_instrument: HUMAN GATE + blind critic Q1

traffic: heavy
care: none
wear_reads_as: polished        # the dressed faces, where hands and gear pass
on_path: true
wear_instrument: NONE

is_made: true
binding_authority: BOTH        # ⚠ the point of this prop — schema v0.1 has no BOTH
  # TWO AUTHORITIES ON ONE OBJECT, and §7.3's dialect distinction must read at 1x:
  #   institution -> the stone itself. Dressed faces, square arris, one seal or tag,
  #                  minimal and correct, never touched since.
  #   orc         -> everything added since. Lashings over lashings, driven pins, pins
  #                  driven beside older pins that failed, redundant and over-built.
  # The card records them separately because the gate question is whether a viewer can
  # tell which hand did which — not whether both are present.
held_by: [pin, rope, band, cramp, seal]
tagged: true                   # the institution inventoried its world; the tag is institutional
binding_instrument: NONE       # blind critic Q5, and the human gate

spine_colours: PLACEHOLDER
region_slots: PLACEHOLDER
warm_share_target: PLACEHOLDER
palette_instrument: LADDER REGIME — §5.1 not landed; authored to the family's measured ladder
warm_share_instrument: NONE

authored_for: receive
baked_highlight: false
baked_outline: false
light_instrument: NONE
outline_instrument: edge-darkness census — CANDIDATE, UNPROVEN

native_canvas: 32x32 native, 2x display          # the scene's grid, §4.3 integer only
scale_factor: 2
density_target: "a RATIO to the figure layer — the marker is the figure's own height class"
canvas_instrument: dimension check (BLOCK)
density_instrument: NONE

tiles: false
tile_edges: none
seam_tolerance: n/a
tiling_instrument: n/a — a prop is not a field

declared_dominant_value: PLACEHOLDER
separation_from_figure: "unaided. No outline, no rim, no plate. It stands beside the figure in
                         the lit radius and must not be confusable with him at 32px."
separation_instrument: NONE

distinct_from: [B-PROP-002, the wall family's face tiles]
uniqueness_instrument: HUMAN GATE
  # ⚠ TIER TWO ACTIVATES THIS CLAUSE. The schema says I9 "activates at tier 2, once tier 1
  # assets can serve as positive controls on the eye". Tier one is landed, so it is live:
  # "name them cold" against the barricade and against wall masonry.

prompt_file: NOT WRITTEN — the pass has not fired
style_references: "≥2, ≤8, authored at target canvas; conditioned on the LANDED corpus at the
                   measured screening rates (wall face + cap donors, floor ashlar)"
mean_snap_distance: NOT MEASURED
producing_commit: NONE
park_state: prepared-not-generated
refusals:
  - "does not add ornament to orc work"
  - "does not carry a trophy spike or any fixing that holds nothing"
  - "does not pose; it stands"
  - "does not present against mock walls"
```

**The question this prop carries:** the made-meets-found seam, first hard test. Two binding
authorities on one object, and §7.3's dialect distinction reading at 1×. It is the object a player
recognises from the fiction, so it is worth iteration.

---

## B-PROP-002 — the lashed barricade section

```yaml
id: B-PROP-002
layer: prop
region: boundary
title: "the lashed barricade section — pure orc grammar at prop scale"

role: "A section of barricade the company built and has been repairing ever since: salvaged
       timber, rope, driven pins, patched onto patches."
role_accept:
  - "a barricade somebody built out of what was to hand"
  - "a blocked or narrowed way"
  - "field fortification, repaired repeatedly"
role_reject:
  - "a fence"               # too light, too regular, too agricultural
  - "a pile of debris"      # it is BUILT; §7.1 wants what holds it together visible
  - "a door or gate"        # it does not open
  - "decoration"            # §7.3 — nothing exists for appearance
role_instrument: HUMAN GATE + blind critic Q1

traffic: light
care: none
wear_reads_as: grimed
on_path: false             # it is what you do NOT walk through; stepping off the path is information
wear_instrument: NONE

is_made: true
binding_authority: orc
held_by: [rope, pin, band, clamp]
tagged: false
binding_instrument: NONE

spine_colours: PLACEHOLDER
region_slots: PLACEHOLDER
warm_share_target: PLACEHOLDER
palette_instrument: LADDER REGIME — §5.1 not landed
warm_share_instrument: NONE

authored_for: receive
baked_highlight: false
baked_outline: false
light_instrument: NONE
outline_instrument: edge-darkness census — CANDIDATE, UNPROVEN

native_canvas: 32x32 native per section, 2x display
scale_factor: 2
density_target: "a RATIO to the figure layer"
canvas_instrument: dimension check (BLOCK)
density_instrument: NONE

tiles: false
tile_edges: "none — but IT REPEATS ALONG A LINE, which is the same hazard by another route"
seam_tolerance: n/a
tiling_instrument: "§8.3.1's CONTINUITY TEST on an assembled line — the motif trap's first
                    prop-scale exam"
  # ⚠ A VARIANT FAMILY FROM ROUND ONE, NEVER A SINGLE SPRITE. §8.3 is settled law here: an
  # incident baked into one asset becomes a MOTIF the moment the asset repeats. The barricade
  # repeats along a line by construction, so it is judged AS LAID, exactly as a tile is.

declared_dominant_value: PLACEHOLDER
separation_from_figure: "unaided; it stands against walls — report how it sits in the §6.5 stack"
separation_instrument: NONE

distinct_from: [B-PROP-001, the wall family's face tiles, the cap field]
uniqueness_instrument: HUMAN GATE

prompt_file: NOT WRITTEN — the pass has not fired
style_references: "≥2, ≤8, authored at target canvas; conditioned on the landed corpus"
mean_snap_distance: NOT MEASURED
producing_commit: NONE
park_state: prepared-not-generated
refusals:
  - "does not ship as a single sprite"
  - "does not add ornament"
  - "does not present against mock walls"
```

**The question this prop carries:** §7.1 at prop scale, in pure orc grammar — redundant,
over-built, repaired on repairs — and the motif trap's first prop-scale exam.

---

## B-PROP-003 — the orc fire

```yaml
id: B-PROP-003
layer: prop
region: boundary
title: "the orc fire — the one light in the game that is tended"

role: "A fire the company keeps: fuel, a built ring, a setting. Orc-built, over-built, nothing
       decorative. §5.4's exception made object."
role_accept:
  - "a fire somebody tends"
  - "a watch fire at a held line"
role_reject:
  - "a campfire"            # too cosy, too temporary, wrong register
  - "a brazier as ornament" # §7.3 — it must be built for burning, not for looking at
  - "a magical light"       # the tone is dry and completely straight
  - "an effect"             # it is an object that emits light, not a light with art on it
role_instrument: HUMAN GATE + blind critic Q1

traffic: heavy
care: none                  # the FIRE is tended; the institution still repairs nothing
wear_reads_as: grimed
on_path: true
wear_instrument: NONE

is_made: true
binding_authority: orc
held_by: [pin, band, clamp]
tagged: false
binding_instrument: NONE

spine_colours: PLACEHOLDER
region_slots: PLACEHOLDER
warm_share_target: PLACEHOLDER
palette_instrument: LADDER REGIME — §5.1 not landed
warm_share_instrument: NONE

authored_for: receive
  # ⚠ AND IT ALSO EMITS. The sprite is authored to RECEIVE light like everything else; the
  # emission is the ENGINE's, a stationary warm PointLight2D. The two must not be conflated:
  # a baked glow on the sprite would be §6.3's outlawed rim by another name, and it would not
  # move when the carried lamp does.
baked_highlight: false
baked_outline: false
light_instrument: NONE
outline_instrument: edge-darkness census — CANDIDATE, UNPROVEN

# ---- TIER-TWO FIELDS THE v0.1 SCHEMA DOES NOT CARRY ----
animates: false
  # §9.1/§9.2: THE WORLD STAYS STILL. The flame sprite does not animate. Not negotiable here.
engine_light: "stationary warm PointLight2D — the rig's FIRST TWO-SOURCE SCENE"
engine_light_captures: [both-lit, carried-only, fire-only]
  # Three captures, because a two-source scene cannot be read from one frame: what the fire
  # contributes, what the lamp contributes, and what they do together are three questions.
flicker_flag:
  state: OFF (default)
  decided_by: "RAFE'S EYE ONLY, at the gate, both states demonstrated"
  build: "the toggle IS built; nothing is ruled"
  # §9.2 names idle-flicker as a killer. The counter-argument is that this one fire is the
  # tended exception. THE BUILDER DOES NOT DECIDE THIS and does not argue it either way.

native_canvas: 32x32 native, 2x display          # multi-tile support is #109 if the ring needs it
scale_factor: 2
density_target: "a RATIO to the figure layer"
canvas_instrument: dimension check (BLOCK)
density_instrument: NONE

tiles: false
tile_edges: none
seam_tolerance: n/a
tiling_instrument: n/a

declared_dominant_value: PLACEHOLDER
separation_from_figure: "unaided, and hardest here — the fire is a bright thing near a figure
                         who carries the only other bright thing"
separation_instrument: NONE

distinct_from: [B-PROP-001, B-PROP-002, the player's lamp]
uniqueness_instrument: HUMAN GATE

prompt_file: NOT WRITTEN — the pass has not fired
style_references: "≥2, ≤8, authored at target canvas; conditioned on the landed corpus"
mean_snap_distance: NOT MEASURED
producing_commit: NONE
park_state: prepared-not-generated
refusals:
  - "does not animate any world sprite"
  - "does not decide the fire-flicker flag"
  - "does not bake a glow onto the sprite"
  - "does not add ornament"
```

**The question this prop carries:** §5.4's exception made object, and the rig's first two-source
scene. Technical before aesthetic — the light interaction is the risk, not the sprite.

---

## Instrument audit for this pass

Unchanged from the tier-1 schema's honest count, with one addition and one deletion:

| Clause | Instrument | Status |
|---|---|---|
| I1 role | Human + critic Q1 | Eye-side |
| I2 wear | — | ⚠ NO INSTRUMENT — by design |
| I3 binding | — | ⚠ NO INSTRUMENT — by design (and B-PROP-001 needs the *dialect* read, which is further from any instrument than binding itself) |
| I4 palette | ladder regime | §5.1 not landed |
| I5 highlight/outline | — / candidate | ⚠ unproven |
| I6 canvas | Dimension check | Buildable |
| I7 tiling | **§8.3.1 continuity test on the assembled line** | **live for B-PROP-002** |
| I8 separation | — | ⚠ NO INSTRUMENT |
| I9 uniqueness | Human gate — **now live** | tier 2 activates it |

**Register conformance stays uninstrumented** (bible §13.4). *Nothing is staged*, *nothing is
ruined — things are used up*, *better made or merely better posed* — these are carried at the
human gate, and no proxy is built for them.

---

*Written 2026-09-08, prepared-not-generated. Fires when §3 is ratified.*
