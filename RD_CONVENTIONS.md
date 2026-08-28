# Retro Diffusion Conventions for YARL

## ⬛ STANDING LAW — LIVE, 2026-08-28. Everything below the next banner is RETIRED; this section is not.

Two rules banked from the 2026-08 adoption audit
(`tools/retrodiffusion/audit_2026_08/AUDIT-RD.md`). They are **measured**, they are **not
Oryx-track material**, and they survive the retirement of everything under them. They are
recorded here rather than in the audit alone because the next person to reach for RD will open
this file first.

### LAW 1 — The seamless census can never be read without the ring screen beside it

> **A framed tile always passes a seamless census — a border makes every edge identical.
> Vendor seamless claims are satisfiable by the one construction §12.1 forbids. The census can
> never be read without the ring screen beside it.**

Measured: all four tiles of the column audit passed both census measures, **including the two
the ring instrument called RING**. The census is not broken — a keyline round the canvas makes
the wrap join perfectly value-continuous, so the tile lays without a seam *because* it is
fenced. Any surface can therefore satisfy a "seamless tiling" claim by drawing a baked outline,
which is bible §12.1's prohibited construction.

**Operationally:** a seam result is reported **in the same table row** as that tile's ring
result, never on its own line, never in its own table, never as a headline. A seam pass with no
ring verdict beside it is not evidence and must not be quoted as any.

### LAW 2 — Seed-reproducibility is PROVENANCE, not a storage substitute

RD **is** seed-reproducible (measured: two identical calls, same seed, byte-identical PNG —
which is a real difference from PixelLab, where bible §13.7 records the opposite). It is
tempting to conclude that a ledger may therefore store parameters instead of images. **It may
not.**

> **The manifest stores `(prompt, seed, model, full params)` per generation AND the returned
> bytes. Reproducibility holds only while the vendor serves the same weights; a hosted deploy
> can invalidate parameters-only entries silently.**

The failure mode is the one this project has already been bitten by twice — *a step that runs,
changes nothing, and says so quietly* (LOOP-PROCESS §4.2). A parameters-only ledger keeps
working, keeps validating, and keeps returning *a* tile right up until the vendor ships new
weights, at which point every historical entry silently means a different image and nothing
goes red. The bytes are the evidence; the parameters are how you say where they came from.

`audit_2026_08/run20.py` writes both, and its `MANIFEST.json` is the shape to copy.

---


> **⚠️ Art-direction notice — 2026-08-24.** This document was already secondary (PixelLab superseded RD in Apr 2026); the **Oryx-conformance art track is
> closed**, so every instruction below about matching Oryx style, locking to the Oryx palette,
> or passing the Oryx art lint is **retired** — see
> [`docs/ART-BIBLE-v0.md`](docs/ART-BIBLE-v0.md) §§1.3 and the archived track in
> [`docs/archive/oryx-track/`](docs/archive/oryx-track/). The RD walkthroughs it refers to are archived with the track.

---

> **Status: Secondary / Retired for props.**
> PixelLab is the primary sprite generation tool as of 2026-04-24.
> See `tools/pixellab/PIXELLAB_CONVENTIONS.md` for the current pipeline.
> RD is retained here for reference and may still be useful for specific use cases.

## API setup
- API key is in `$RD_API_KEY` environment variable (set in ~/.bashrc)
- Oryx palette: `tools/retrodiffusion/oryx_palette.png`
- Scripts live in `tools/retrodiffusion/` — run from that directory
- Claude can run scripts directly by sourcing `~/.bashrc` for the key

## Style selection

**Primary style: `rd_plus__low_res`** (~$0.027/image)

This is the validated production style. Tested against `rd_plus__classic` and
`rd_plus__topdown_item` on both weapon (club) and prop (anvil) subjects. Produces
the closest match to Oryx library aesthetics: gritty texture, appropriate depth,
correct Oryx-palette colors. Wins on Oryx style compatibility in every test.

Do NOT use `user__oryx_16_bit_fantasy_style_d970121a` (the custom RD Pro style) for
game sprites. It costs $0.18/image (7× more) and has a minimum native resolution of
96px — any 16×16 or 24×24 output from it is a forced downscale that loses per-pixel
intentionality. Use it only for larger showcase renders if ever needed.

**For wooden furniture: still unsettled — needs more testing**
topdown_item produces lighter, warmer wooden chairs/tables but with too much realistic
wood grain detail — they look out of place next to Oryx's bold flat sprites in-game.
low_res produces chunkier, darker, more Oryx-compatible style but hallucinated on tables
with light color qualifiers. Next approach to try: low_res with simple "wooden" prompt
(no light/dark qualifier) and test in-game. Dark chunky wood may suit dungeons better.

**Fallback style: `rd_plus__topdown_item`**
Also usable for props if `low_res` produces a bad batch. Fails for weapons (renders them
as top-down blobs). Do not use for items.

**Disqualified: `rd_plus__classic`**
Too clean/flat, wrong coloring tendencies, stylistically inconsistent with Oryx library.
Minimum size 32×32 — downscaled to 24×24 produces unusable output.

## Sprite specs
- Items (weapons, potions, keys): generate 32×32, downscale to 16×16
- Props (furniture, dungeon objects): generate 48×48, downscale to 24×24
- Characters: not tested yet — start at 48×48 → 24×24

## Standard prompt template
`"{object description}, small sprite on transparent background, pixel art, clear silhouette"`

Notes:
- Keep prompts short and simple — overspecification causes hallucinations at 24×24
- Avoid "top-down RPG" — biases toward flat overhead perspectives
- Avoid color qualifiers ("light oak", "light brown") — destabilizes output; material/object
  description alone is sufficient
- Avoid technical projection terms ("oblique projection", "cavalier", etc.) — model ignores
  or misinterprets them; just describe the object simply

## Pipeline
1. Call `api.retrodiffusion.ai/v1/inferences` with `rd_plus__low_res`
2. Include `input_palette` (oryx_palette.png as base64) to lock Oryx colours
3. Use `remove_bg: true` in the payload
4. Flood-fill clean near-black background (r+g+b < 30) from edges (belt-and-suspenders)
5. Save native size to `style_test_{name}/`
6. Nearest-neighbor resize and save final game size alongside

## Sprite ID namespace
- Oryx originals: 1–999 (do not touch)
- AI items (items_16x16): **4001–4999**
- AI props (world_24x24): **5001–5999**
- AI creatures (creatures_24x24): **6001+** (reserved, not yet in use)
- Register every sprite in `tools/sprite_browser_ai.html` RD_SPRITES array
- In-game entries go in `config/tilesets/16bit_fantasy.yaml` (items) or `config/props.yaml` (props)
- Replaced placeholders graduate from NEW_SPRITES → RD_SPRITES in the browser

## Budget rules
- Default: 4 variants per sprite, 3 styles for comparison = 12 images ≈ $0.32
- Warn before spending more than $2 in a single batch
- Production runs (single style, known winner): 4 variants, pick best = ~$0.11/sprite

## Evaluation criteria (in order)
1. **Oryx style compatibility** — does it blend with the existing tileset?
2. **Shape readability at final size** — recognizable at 16×16 or 24×24? (evaluate at TARGET size, not gen size)
3. **Colour palette** — warm/muted tones, no oversaturated or wrong-hue outputs
4. **Consistency across variants** — does the style reliably produce the right subject?

## Selection workflow
- Claude reads all variants, ranks them with reasoning against the above criteria
- Rafe makes the final call — final selection is often opinion/aesthetic, not objective
- Claude's recommendation is a starting point, not a decision
- Over time, alignment on taste should reduce back-and-forth
