# Retro Diffusion Conventions for YARL

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
