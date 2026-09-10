# B-PROP-003 — the orc fire: generation prompt

Auditable file with clause provenance, per `CC-SESSION-tier2-props.md`'s METHOD. Identity card:
`docs/art/tier2/IDCARDS-props.md`, B-PROP-003.

---

## ⚠ THE HARDEST CONSTRAINT IN THE PASS, STATED FIRST

**The sprite is authored to RECEIVE light. The emission is the engine's.** A stationary warm
`PointLight2D` does the lighting; the art is a fire-*place* that the rig then lights, plus the
flame body itself. What must NOT arrive baked in is **the glow around it** — a painted halo is
§6.3's outlawed rim by another name, and worse, it would not move when the carried lamp does.

That is a real tension with a generator that has drawn ten thousand cosy campfires, so it is
refused three ways: in the prompt text, in `flat shading`, and by the screen on the returned image.

## The prompt

> orc-built fire pit, a ring of heavy stones bound with iron bands and driven pins, filled with
> charred timber and grey ash, a small contained flame, crude and over-built, surrounding stone
> matte and dark, no glow, no halo, no light spill, no sparks, functional not decorative, unlit
> surroundings

## Parameters, and the clause each answers

| parameter | value | clause |
|---|---|---|
| `view` | `high top-down` | **§3**, ratified 2026-09-09 |
| `outline` | `lineless` | **§12.1** — no baked ring |
| `shading` | `flat shading` | **§6.3** — and here it does double duty: flat shading is the setting least likely to paint a glow |
| `detail` | `medium detail` | **§4.3** at 32px |
| size | 32 × 32 | the substrate probe's measured authoring size |

## Load-bearing clauses

1. **No baked glow, halo or light spill** (§6.3, and the identity card's refusal by name). Screened
   on the returned image: a radial brightness gradient centred on the flame, falling off into the
   transparent margin, is a fail however pretty.
2. **No baked outline** (§12.1).
3. **It does not animate** (§9.1/§9.2). One frame. The world stays still — not negotiable, and the
   card records it as a refusal rather than a preference.
4. **Over-built, nothing decorative** (§7.3). The ring is orc work: bound, pinned, repaired. Stones
   piled prettily are not it.
5. **It is an object that emits, not an effect** (`role_reject`: "an effect"). The fire-place must
   read as built even with the engine light off — which is exactly what the `fire-only` and
   `carried-only` captures test.

## The three captures this prop owes

The rig's **first two-source scene**, so one frame cannot answer it:

- **both-lit** — what the player sees.
- **carried-only** — the fire's *object* read, with its own light off. If it stops reading as a
  built thing here, the art is leaning on the engine.
- **fire-only** — the fire's light on the room, with the carried lamp off. What the second source
  actually does.

## The flicker flag — BUILT, NOT DECIDED

**Default OFF.** §9.2 names idle-flicker as a killer; the counter-argument is that this one fire is
the tended exception (§5.4). **The builder does not decide this and does not argue it either way.**
The toggle is built and both states are demonstrated at the gate. Rafe's eye rules.

## Palette regime

Ladder, not locked. §5.1 is `PLACEHOLDER`.

---

*Wave 1: 4 generations. Budget for the pass is 90.*
