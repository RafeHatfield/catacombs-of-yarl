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
| `style_image` | The Oryx sprite composite doesn't work as a style reference — produces green noise at any `style_strength > 0` |
| `oblique_projection`, `isometric`, `view` | Marked "weakly guiding" in the API — mostly ignored or produces subtle unwanted changes |
| `shading`, `detail`, `outline` | Unpredictably changes the character of what's generated, not just the rendering style |

## `color_image` — verified 2026-07 as a real palette lock

Earlier testing (`sweep.py`, ~2026-04) fed `color_image` the full detailed multi-sprite Oryx style
composite and got green-noise corruption, which was read as "no palette lock, spatial transfer
only." That composite is the wrong input shape for what this parameter does. Re-checked 2026-07-24
against the live OpenAPI spec (`api.pixellab.ai/v1/openapi.json` and `/v2/openapi.json`), which
documents `color_image` as: **"Forced color palette, image containing colors used for palette."**
Confirmed empirically: a small flat swatch of solid color blocks (~8-10 colors, no detail, no
spatial structure to a real object) produces output using *only* those exact colors — see
`tools/pixellab/palette_lock_evidence/` for the swatch, the generated output, and the color
measurement.

**Use it:** pass a flat swatch image (solid blocks, not a detailed composite) as `color_image` to
lock generation to a specific color set — e.g. a themed subset of `config/art/oryx_master_palette.json`
sized to the target asset class's color budget (bible §5: props/decals ≤10, items ≤21, creatures ≤18).

**License guard still applies as documented in `docs/art_bible.md` §8**: a swatch built from
`oryx_master_palette.json` *values* (solid RGB blocks, no Oryx pixel imagery) is approved derived-data
conditioning. Feeding an actual Oryx sprite image as `color_image` (or any conditioning input) remains
prohibited pending the license check called out there — never do that, only synthetic swatches.

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

## Structural derivation only + strengthened two-plane filter (Rafe ruling, Round E 2026-08)

**Palette-only derivation is RETIRED for props** (alongside generation). The *only* derivation route
is **structural**: start from a **canon donor sprite's actual construction** (its pixels / plane
structure) and **re-dress** it — never apply canon colours to an invented form. Round E proved why:
palette-only beds (canon colours, invented form) read **top-down-only** and benches read
**front-only** — two-plane violations by omission, because an invented form has no canon plane
structure to inherit.

**Two-plane discard filter — now BOTH questions, on every route incl. derivation, before review:**
1. **"Is any side face visible?"** → must be **no** (a single side-plane pixel column fails).
2. **"Are the front face AND the top surface both present?"** → must be **yes**.

A top-down sprite (top only) or an elevation sprite (front only) fails #2 by omission. Run this
filter on the candidate *before* it reaches in-scene review; a fail is discarded, not submitted.

## Prop generation RETIRED (Rafe ruling, post-play-session 2026-08)

**There is no regeneration route for props anymore.** The prop rework ladder is:
**canon substitution → canon derivation → stop-and-discuss.** If no canon sprite can be
substituted and no canon construction can be derived from canon pixels, the item *stops and
comes back to Rafe* — it is not regenerated. This supersedes the gauntlet/constrained-regen
route for props below (kept only as a record of why the route was closed): across the sweep,
constrained regeneration reliably metric-won with the **wrong object** (a "chunky anvil"
regenerates as a hammer) or produced **metric-clean-but-formless** props (sacks, beds). Canon
substitution/derivation is the only route that holds the register.

The **candidate bank** (`tools/pixellab/.../bank_*`, the ~1174 speculative gens) is retained as
**reference / mood material only** — it is never a source of landed prop pixels. A bank sprite may
inform a *derivation* (as colour/shape reference, like a canon reference) but its pixels do not ship.

Scope: this governs **props**. Items and creatures are not covered by this ruling. See
`docs/art_bible.md` changelog for the canonical statement.

## Register language + canon-validated-swatch rule (play review 2026-08, PR #108)

**Register ruling.** The target look is the Shattered-Pixel/Oryx school: **chunky, low-detail,
bold-read**. The dominant PixelLab failure mode is **refinement** (too fine, too many small
structures) even when palette/colour budget pass. Every generation prompt for a register-critical
prop MUST carry: `"chunky, minimal detail, bold shapes, thick outline"` + the **two-plane rule**:
`"only the front face and the top surface are visible; no side faces, orthographic"`. The register's
projection is exactly two planes — front face + top surface. **Side planes are NEVER visible: a
single pixel column of side face is a violation**, even on an otherwise front-facing sprite. Then
pass the structural-fineness post-filters (`config/rubric/art-lint-spec.md` §AF;
`tools/art_lint/fineness_metrics.py`) — WARN at canon p90.

**Discard filter (blind pre-filter):** the question is now **"is any side face visible?"** — if yes,
discard, regardless of how clean the sprite is otherwise. *Recorded example:* the Round-D nightstand
candidate `nightstand2 s101` was metric-clean and read as a nightstand, but showed a sliver of side
face and was rejected on perspective; `s107` (pure two-plane) was approved.

**Canon-validated-swatch rule.** Build the `color_image` palette-lock swatch from *the concept's own
canon-or-live sprite's dominant colours* (snapped to the master palette), never a generic swatch and
never hand-picked hues. **Recorded example — the chair drift:** an early fresh chair round used a
generic/eyeballed swatch and produced pinkish-pale chairs that read as a different hand next to the
warm-wood canon table; they were gate-rejected on colour, and the fix was to derive the swatch from
the table's own colours (`build_swatch_from_live`). Lock to the object's real palette, then let the
register prompt + fineness filter do the rest.

**What the gauntlet found (2026-08).** Constrained regeneration wins the fineness critic for
*soft/large* concepts (sacks, beds) but tends to metric-win with the *wrong object* for hard
mechanical concepts (a "chunky anvil" regenerates as a hammer) — so the blind visual pre-filter is
mandatory, and compact detailed props (benches, shelves) often can't get `edge_density` under canon
p90 at all. Prefer **canon substitution / derivation** over regeneration whenever a canon concept
exists; keep-fallback items revert to KEEP rather than force a metric-clean but wrong-reading sprite.

## Blind pre-filter gap (rubric feedback 2026-08)

The gauntlet's blind visual pre-filter (seat a candidate between two canon neighbours, discard the
obvious outsider) is necessary but **not sufficient**: the sack and bed regen candidates passed both
the metric critic AND the blind pre-filter, yet Rafe rejected them at rubric as "formless / colour
off" — i.e. metric-clean and not-obviously-alien, but lacking human form-coherence. This is a known
gap. **Do not invent a new metric for it** — form-coherence is a human-eye judgement the acceptance
rubric owns; the pre-filter only trims the obvious. Practical consequence: for soft/organic concepts
(sacks, bedding, piles) prefer canon substitution/derivation, and treat regen candidates as
low-confidence until the human rubric confirms.
