# PixelLab Conventions for YARL

**Primary sprite generation tool as of 2026-04-24.**
Replaces Retro Diffusion for props and items. See `RD_CONVENTIONS.md` for RD reference.

## API setup
- API key in `$PIXELLAB_API_KEY` environment variable (set in ~/.bashrc)
- Python SDK: `pixellab` package, installed in project venv (`source .venv/bin/activate`)
- Scripts live in `tools/pixellab/` — run from that directory
- Cost model: subscription (~2000 images/month), not pay-per-image

## Model
Use **BitForge** (`client.generate_image_bitforge()`) for all sprite generation.
PixFlux is for large non-sprite content only — do not use for game sprites.

## The single most important rule: use minimal params

Extensive testing showed that adding perspective flags, shading, detail, outline, or
style/color references consistently degrades output quality or causes corruption.
The model's defaults are better than any override we tested.

**Production config:**
```python
client.generate_image_bitforge(
    description="wooden chair, small sprite, pixel art",
    image_size={"width": 32, "height": 32},
    no_background=True,
    seed=42,  # change seed to get different designs
)
```

That's it. Nothing else.

## What NOT to pass

| Parameter | Why not |
|---|---|
| `color_image` | Spatial color transfer, not palette lock — passing the Oryx palette strip corrupts output with green noise |
| `style_image` | The Oryx sprite composite doesn't work as a style reference — produces green noise at any `style_strength > 0` |
| `oblique_projection`, `isometric`, `view` | Marked "weakly guiding" in the API — mostly ignored or produces subtle unwanted changes |
| `shading`, `detail`, `outline` | Unpredictably changes the character of what's generated, not just the rendering style |

## Sprite sizes

- **Props (24×24 final):** generate at 32×32, nearest-neighbor downscale to 24×24
  - 32→24 is not a clean ratio (75%) but is acceptable in-game
  - 48×48 tested: model hallucinates more detail at larger sizes, less consistent
- **Items (16×16 final):** generate at 32×32, nearest-neighbor downscale to 16×16
  - 32→16 is a clean 2:1 ratio

## Prompt template

`"{object}, small sprite, pixel art"`

That's the full template. Keep it short.

- No perspective descriptors — the model defaults to front-dominant view naturally
- No color qualifiers — trust the model's palette choices
- No "top-down RPG", "pixel art dungeon", etc. — adds noise without benefit
- One or two descriptive words about the object are sufficient

## Seed selection

Seeds control which design variant is produced — they are **aesthetic choices, not
quality controls**. There is no "best" seed. Pick seeds whose output you like for each
specific object. Different objects should use whatever seed looks best for that object;
there is no benefit to using the same seed across objects.

Keep a record of which seeds are in use per object (in props.yaml notes or the sprite
browser) so you can regenerate exact matches if needed.

## Pipeline

1. Run `generate_image_bitforge` with minimal params
2. Save native 32×32 to `tools/pixellab/{session_dir}/`
3. Nearest-neighbor downscale to final size (24×24 or 16×16)
4. Save final size to `src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_{id}.png`
5. Register in `tools/sprite_browser_ai.html` RD_SPRITES array
6. Add/update entry in `config/props.yaml` (props) or `config/tilesets/16bit_fantasy.yaml` (items)

## Sprite ID namespace (PixelLab era)

PixelLab sprites continue in the existing AI namespace:
- Props (world_24x24): **5051+** (5001–5050 are Retro Diffusion era)
- Items (items_16x16): **4001+** (no PixelLab items yet as of 2026-04-24)
- Characters (creatures_24x24): **6001+** (untested, not yet in use)

## Evaluation criteria (in order)

1. **Readability at final size** — is the object recognisable at 24×24 or 16×16?
2. **Perspective** — front-dominant with slight top view (not iso, not pure top-down)
3. **Style compatibility** — warm/muted tones, bold pixel shapes, no excessive fine detail
4. **Consistency** — does this seed reliably produce the right object?

Evaluate at the TARGET size (24×24 or 16×16), not at generation size.

## Selection workflow

- Generate 6–8 seeds of a new object to see the range
- Pick 2–4 keepers for variety (game places randomly from tile_ids list)
- Register all keepers in sprite browser and props.yaml
- Test in-game immediately — "stands out" issues only show in context

## Budget rules

- Default: 8 seeds to select from for a new object type (~$0 from subscription)
- No hard spend limit per batch given subscription model, but flag if generating > 50 in one session
- Track total monthly usage to stay within subscription tier

## Known limitations

- **No palette lock** — PixelLab has no equivalent to RD's `input_palette`. Colors are
  consistent within a generation run but don't snap to the Oryx palette exactly. Accepted
  tradeoff: the style difference is smaller than RD was, and replacing enough Oryx props
  makes the PixelLab sub-style look intentional rather than inconsistent.
- **Style gap with Oryx** — PixelLab sprites are slightly more refined than Oryx's chunky
  hand-crafted style. Long-term solution: replace Oryx props progressively so the game
  settles into a consistent PixelLab style rather than a mix.
