# B-PROP-001 — the boundary marker stone: generation prompt

**Auditable file with clause provenance, per `CC-SESSION-tier2-props.md`'s METHOD** — *"Generation
prompts live as auditable files with clause provenance and a self-check that asserts load-bearing
clauses survived — never as a string typed into a chat."*

Identity card: `docs/art/tier2/IDCARDS-props.md`, B-PROP-001.

---

## The prompt

> old dressed stone boundary post standing upright, institutional cut stone with square worn
> faces, wrapped and repaired with thick rope lashings and driven iron pins, repairs layered over
> older repairs, heavy and squat, weathered grey-brown stone, no ornament, no decoration, no
> spikes, matte, unlit

## Parameters, and the clause each one answers

| parameter | value | clause |
|---|---|---|
| `view` | `high top-down` | **§3** — orthogonal grid, portrait, a front face and a top surface. Ratified 2026-09-09. |
| `outline` | `lineless` | **§12.1** — no dark ring anywhere. The identity card's `baked_outline: false`. |
| `shading` | `flat shading` | **§6.3** — no baked directional key light, no rim-glow. The card's `authored_for: receive`: the lamp does the modelling, the art carries form. |
| `detail` | `medium detail` | **§4.3** — 32px native. High detail at this size resolves to noise; the wall gauntlet's *"dense SPONGE SPECKLE"* cull is the logged instance. |
| `width`/`height` | 32 × 32 | measured off the substrate probe: a prop is scaled to fill its 64px cell, so the family authors at 32 native like every other. |

## Load-bearing clauses the output must not violate

Asserted by `assert_prompt.py`, and checked on the returned image rather than assumed:

1. **No baked outline** (§12.1). A dark ring around the silhouette is the cull that closed the
   floor's ring investigation; it is not permitted to arrive baked into a prop instead.
2. **No baked highlight** (§6.3). No lit edge, no rim, no specular. The frame's only light is
   carried by the player.
3. **No ornament, no trophy spike** (§7.3, and the direction ruling by name). *A spike that holds
   nothing is decoration.* Every pin and lashing must be holding something.
4. **Two authorities legible** (§7.3's dialect distinction, and this prop's whole question). The
   stone is institutional — dressed, square, minimal, never touched since. Everything wrapped
   around it is orc — redundant, over-built, repaired on repairs.
5. **Weight straight down** (the direction ruling). Mass in the silhouette; it stands, it is not
   posed.

## What is refused, by name

Trophy spikes and ornament (§7.3), fury poses (§7.4), specular sheen and rim-glow (§6.3),
animation (§9.1/§9.2). **Refused in the prompt text itself** — "no ornament, no decoration, no
spikes, matte, unlit" — so a violation is a generator failure rather than an instruction the
prompt never gave.

## Palette regime

**Ladder, not locked.** §5.1's values are `PLACEHOLDER` and its derivation has not landed, so
generated material is snapped to the family's measured value ladder at composition rather than
generated on a locked hex list. Stated here and in every report this pass produces.

---

*Wave 1: 4 generations. Budget for the pass is 90.*
