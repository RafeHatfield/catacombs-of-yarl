# PixelLab v2 API & MCP server — findings (2026-07-24)

Discovered while investigating the palette-lock question (see the `color_image` section of
`PIXELLAB_CONVENTIONS.md`). Documentation only — no tooling migration made here.

## The `pixellab` Python SDK only wraps the old v1 surface

`pixellab==1.0.5` (latest on PyPI) wraps `/generate-image-bitforge`, `/generate-image-pixflux`,
`/inpaint`, `/balance` — the v1 API (`api.pixellab.ai/v1/openapi.json`). Everything this repo's
tooling does (2a, 2b, `bank_generate.py`) goes through that v1 surface, either via the SDK directly
or via `client_compat.py`'s raw HTTP workaround for the SDK's response-parsing bug.

## v2 exists and is much larger (`api.pixellab.ai/v2/openapi.json`)

Notable endpoints beyond what we use today:

- `/generate-image-v2` — takes `reference_images` (up to 4, for subject guidance) and a `style_image`
  with a `style_options.color_palette` **boolean** ("Copy color palette from style image", default
  `true`). This is a more structured, arguably more reliable palette-lock mechanism than v1's
  `color_image` swatch trick — worth testing before assuming `color_image` is the ceiling.
- `/create-image-pixen` — a third model ("Pixen") not mentioned anywhere in our docs, with an
  `enhance_prompt` option that auto-expands short descriptions into richer prompts before generating.
- `/image-to-pixelart`, `/image-to-pixelart-pro` — convert an arbitrary image into pixel art,
  potentially with palette/quantization control. Could be relevant to the snap-to-palette step we
  currently do ourselves in `tools/art_lint/snap_to_palette.py` (nearest-neighbor per-pixel), though
  ours is deterministic and inspectable in a way an API black box isn't — not an obvious swap.
- `/tilesets`, `/create-tileset`, `/tilesets-sidescroller`, `/create-isometric-tile`,
  `/create-tiles-pro` — proper tileset generation (top-down and sidescroller), relevant to any future
  floor/wall texture or region-tileset work beyond individual prop sprites.
- `/map-objects`, `/create-1-direction-object`, `/create-8-direction-object`,
  `/objects/{id}/select-frames`, `/objects/{id}/dismiss-review` — object generation with built-in
  variant/state management and a review workflow, structurally similar to what burn-down 2's
  contact-sheet + pick flow does by hand.
- `CreateCharacterStateRequest.use_color_palette_from_reference` (boolean) — snaps edited character
  rotations to the source character's existing palette. Relevant if we ever do player-class or
  creature variant work through PixelLab rather than by hand.

## MCP server exists, registered for a different project

`~/.claude.json` has a `pixellab` MCP server (`https://api.pixellab.ai/mcp`) registered under
`/Users/rafehatfield/development/deathmatch`'s project config — not under this repo. Its tool surface
(from `api.pixellab.ai/mcp/docs`) covers characters, top-down/sidescroller tilesets, isometric tiles,
map objects, UI assets, tiles-pro, fonts, and a chat/sandbox layer — a much richer surface than the
raw BitForge/PixFlux calls our scripts make. Not wired into this project; would need to be added to
this repo's Claude config (or a project-level `.mcp.json`) to use directly from a session here.

## Not acted on

This is a discovery note, not a recommendation to migrate. The v1 API plus `color_image` palette-lock
(now documented in `PIXELLAB_CONVENTIONS.md`) already covers the immediate need. Worth revisiting if
future tileset/region work would benefit from the v2 tileset endpoints or the MCP server's built-in
review workflow.
