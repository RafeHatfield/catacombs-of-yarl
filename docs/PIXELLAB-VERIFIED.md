> ## PROVENANCE — this is a COPY. Do not edit it here.
>
> **Source repo:** Gemfall (`~/development/deathmatch`)
> **Source path:** `scratchpad/gauntlet/pixellab-review/PIXELLAB-VERIFIED.md`
> (worktree `.claude/worktrees/pixellab`)
> **Source commit:** `874b5459` — *docs(pixellab): Ruling 104 canon — the silent-step audit*
> **Tracked and clean at that commit.** Copied into YARL 2026-08-25.
>
> Corrections belong upstream in Gemfall, then re-copy. The working record and
> corrections trail it supersedes (`FINDINGS-100.4`, `FINDINGS-101-REAUDIT`,
> `FINDINGS-102-MEASURED`, `PROBE-create_object_state.md`, `MIGRATION-PLAN.md`) stay
> in Gemfall and were **not** copied.
>
> ### ⚠ READ THIS BEFORE APPLYING ANY OF IT TO YARL
>
> **This document describes the PixelLab MCP / object surface. YARL is not on it.**
> Every YARL call site is the **v1 REST surface** — `/generate-image-bitforge`,
> `/inpaint`, `/animate-with-text`, `/balance` — via `pixellab==1.0.5` and
> `tools/pixellab/client_compat.py`. YARL has no MCP registration and no objects,
> characters, packs or review queue.
>
> So §§1.1–1.6, 2.1–2.4, 2.7–2.9 and 4 are **surface-specific and do not describe YARL
> today**. They become live the moment YARL touches v2/MCP — and §2.4's architecture
> decision would be made at that first call. §§1.7, 2.5, 2.6, 3 and 5 transfer as
> written.
>
> What does and does not apply, measured: `docs/PIXELLAB-UW-AUDIT-2026-08-25.md`.
>
> ### ⚠ TWO CLAUSES BELOW ARE CORRECTED BY THE LIVE REST SPEC
>
> Both corrections are **[SCHEMA]**, read from `api.pixellab.ai/v2/openapi.json` on
> 2026-08-25, and both have the same cause: **the MCP tool schemas are a lossy projection
> of the REST spec.** Detail and evidence in
> `docs/PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md` §2 and §4.
>
> - **§2.1 is wrong.** The 2000-char cap **is** declared —
>   `Create1DirectionObjectRequest.description` carries `maxLength=2000` in OpenAPI. It is
>   absent only from the MCP tool description. The three arms bought a fact the spec states.
> - **§2.4 overstates its source.** The *"ALWAYS preserves the SAME individual's face and
>   identity"* sentence is MCP prose with **no counterpart in the REST spec**, which
>   describes `/create-character-state` and `/objects/{id}/states` in near-identical terms.
>   The schema-visible differences are real but narrower: rotation-wide consistency,
>   `use_color_palette_from_reference`, `override_frame_size`. Also: the v3 canvas is padded
>   **~2x** (spec), not ~40%, and reference-mode cost is exactly `ceil(w*h*8/65536)`.
>
> **Law 2 gains a clause for both games:** *the endpoint's own live schema is the OpenAPI
> entry — even when you are calling through MCP.*

---

# PIXELLAB — WHAT WE VERIFIED

**The transfer document. Shared with Under Warden (same subscription, same account).**
**Closed 2026-08-25, Ruling 103. Supersedes FINDINGS-100.4, FINDINGS-101, FINDINGS-102 as the
page to read first** — those remain as the working record and the corrections trail.

## How to read this

**[API]** measured by a real call against our account — the only tag that settles anything.
**[SCHEMA]** read verbatim from the live MCP tool schema.
**[TREE]** our own evidence, cited to file and line.
**[HELP]** what `agent_help` said — *documentation search, not measurement*.
**[INFER]** reasoning measured by nobody.

⚠ **[HELP] has been measured wrong.** On the `edit_image` floor it gave opposite answers four
days apart and the second was false. Treat it as a lead, never a finding.

⚠ **And [SCHEMA] alone has been measured wrong too.** See §1.1 — the failure was reading two
schema clauses separately when they compose. **Tags are necessary, not sufficient.**

---

## 1 — MEASURED FACTS [API]

### 1.1 ⚠ The 32px floor: `edit_image` and `inpaint_image` are CLOSED at 24×24

Called with `width`/`height` **omitted** on a 24×24 RGBA input, `edit_image` returns:

```
error: output size 24x24 is below the 32x32 minimum.
       upscale the input first (nearest-neighbour) or set width/height.
```

⚠ **The schema declares no minimum on the input** — the floor reaches it *transitively*, because
an omitted `width`/`height` **defaults to the input's size** and min-32 applies to the **derived
output**. `inpaint_image` states its floor in prose (*"Image must be 32x32-512x512"*).

**The general lesson, and it cost this project a planned path:** *absence of a declared
constraint on a parameter is not absence of a constraint on its value. A defaulted parameter
inherits every constraint of the thing it defaults from.*

### 1.2 ✅ `create_object_state` is NOT floored — it accepts a 24×24 source

**[API]** Ran end to end against a promoted 24×24 object and returned a **24×24 RGBA** result:
**290 opaque / 286 transparent / 0 semi-alpha**, silhouette moved by one texel, **alpha intact**
(no compositing onto white). **Cost: 20 generations** — the *floor* of the stated 20–40, from the
pool, credits untouched.

**The editing family is not uniformly floored at 32.** `edit_image`/`inpaint_image` are;
`create_object_state` is not. **Do not generalise a floor across a family.**

⚠ **In this one sample, identity survived and the recolour was followed closely** — same figure,
pose and stole geometry, cream→crimson, grey→near-black, skin retained. **`create_object_state`
promises nothing about identity (§2.4). One sample of good behaviour is not a contract.**

⚠ **Two defects that carry to any path:** it **baked an outline ring** (91px of pure `#000000`)
despite *"no outline"* in the instruction — ART-BIBLE §4 forbids baked outlines — and it drifted
the cassock **blue-teal** (`#152D39`, `#0C2831`) with no blue in the instruction, source or
palette. **Generator drift and baked outlines are properties of the generator, not the endpoint.
No endpoint choice shortens the art gate.** Full record: `PROBE-create_object_state.md`.

### 1.3 ✅ `select_object_frames` COSTS NOTHING

**Three promotions, each `get_balance`-bracketed. Ledger unmoved every time:
$8.11 / 320 used / 4680 remaining.**

Corroborated independently: each promoted object serves **byte-identical pixels** to its review
frame — **promotion is a re-pointer, not a re-render.**

| figure | review object | index | promoted | sha256 (both) |
|---|---|---|---|---|
| Chaplain | `44513d58` | 0 | `e463e69f` | `ee7740f5…` |
| Engineer | `0953d7ea` | 9 | `5462d3c3` | `0ce26b61…` |
| Scientist | `2e730fc6` | 35 | `1e063e7b` | `caa457d2…` |

⚠ **Does NOT generalise to `dismiss_review`**, whose cost is still unknown. **[SCHEMA]**
`reduce_colors` is explicitly local (*"Runs locally in about a second"*) and still costs 0.1
generations. **This platform bills non-rendering operations.**

### 1.4 ✅ A REJECTED CALL IS FREE

`get_balance` unmoved across a server-side rejection. Previously [HELP] and [TREE]-by-inference;
now measured. **This is the fact that makes cheap probing possible** — see the standing law.

### 1.5 ✅ Promoting one frame leaves the parent alive

**[SCHEMA]** *"Once no frames remain in the review object it is deleted automatically."*
**[API]** After promoting one index of 64, the parent remained at `review:awaiting-selection`
with 63 frames. **Promote the shipped frame only** — promoting all destroys the parent and every
passed-over candidate, which are evidence.

### 1.6 ✅ Review objects do NOT expire

**[API]** The account holds objects from July, including 16×16 packs, all still in review.
⚠ **[TREE]** `assets/MANIFEST.md:492`'s note that *"Pixellab objects auto-delete"* is **false.**
The conclusion it supports (repo copies are canonical, Ruling 37) is right; the reason is wrong.

### 1.7 ✅ A failure's reason is unrecoverable

**[API]** Object `2dda0fd7` returned *"Generation blocked by content policy"* at queue time and
returns a bare **`Generation failed`** today. The full prompt survives; the classification does
not. **Capture the verbatim error at the moment the call fails, or lose it permanently.**

---

## 2 — SCHEMA FACTS THAT BITE [SCHEMA]

### 2.1 ⚠ The 2000-character prompt cap is undeclared on the endpoint that enforces it

`create_1_direction_object.description` declares **no `maxLength`**. Every neighbour declares
one: `create_image_pro`, `edit_image`, `inpaint_image` at 2000; `create_object_state` and
`create_character_state` `edit_description` at 1000.

**[TREE]** Five consistent data points — rejected at 2606, 2201, 2209; refused client-side at
2011; accepted at exactly 2000. **It has cost this project three arms.** 2000 is consistent with
all five and independently unproven.

**Enforced by `tools/pixellab_pack.py check`, which refuses and never trims.**

### 2.2 ⚠ `size` cannot accompany `style_images`

*"Cannot be set together with style_images — when style_images are provided, the largest style
image determines the output size."* **Still true.** This is why every reference is authored at
the target canvas.

Style-image **count is size-dependent** — ≤85px → 8, ≤170px → 4, above → 1. Not a flat 8.
Candidate counts: ≤42px → 64, ≤85px → 16, ≤170px → 4, above → 1.

⚠ **`create_image_pro` routes around this** — it takes explicit `width`/`height` (**min 16**)
*together with* one style image and up to four **labelled** references, plus `style_copy` to take
only some aspects from the style tile. That last clause is not expressible on
`create_1_direction_object` at all.

### 2.3 ⚠ `style_images` has NO minimum — "single-reference conditioning fails" is OUR art finding

*"When empty, a default style is used based on `view`."* One is legal, zero is legal.

**[TREE]** What our evidence shows (`spike/GENERATIONS.md:41-48`) is that **one reference cannot
carry both density and value** — round 1 conditioned on a dark-mid-neutral tileset alone and
failed the value floor on 6–7 of 7 blocks; the fix was adding a value plate. **True and useful.
Argue it on that merit. Never cite it as a platform constraint** — it would wrongly veto
`create_image_pro`.

### 2.4 ⚠ The identity guarantee belongs to `create_character_state`, NOT `create_object_state`

`create_character_state`, verbatim: *"this ALWAYS preserves the SAME individual's face and
identity, even for edits like 'elderly', 'wounded', or a different class/role. It makes a variant
OF this character… NOT a new character."*

`create_object_state` says **nothing** about identity — only grouping and state naming.

⚠ **`create_character_state` needs a `character_id`. `select_object_frames` produces OBJECTS.**
**[API]** `list_characters()` → **0**. So promotion does *not* unlock the identity contract.

**The bridge:** `create_character` in **v3 mode with `reference_image_url`** *"rotates YOUR sprite
into 8 directions"*, `size` min 16, cost **2–9 generations** — but it forces 8 directions and
*"Canvas will be ~40% larger to make room for animations."*

> ⚠ **THE TRANSFER THAT MATTERS MOST TO UNDER WARDEN:** if you want identity-preserving variants
> later, **enter through `create_character`, not `create_*_object`.** That decision is made at
> your first call and is expensive to reverse. Gemfall walked into this and spent two audits
> discovering it.

### 2.5 ⚠ A pre-call balance check cannot enforce a spend ceiling

`create_character_state`, verbatim: *"the tier is resolved from the canvas at generation time…
**The balance check runs against the 20 floor, which means a call CAN charge more than it
reserved.** Leave 40 generations of headroom."*

**Budget against the per-call CEILING.** A 60-generation authorization is **two** calls, not three.

### 2.6 ⚠ `create_1_direction_object` is the only generation endpoint without `seed`

`create_image_pro`, `edit_image`, `inpaint_image`, `image_to_pixelart`, `create_object_state`,
`create_character_state` all carry `seed`. **The endpoint our recipe is built on does not** — so
our arms are irreproducible by construction.

### 2.7 Retrieval: read the URLs the API returns, never build them

**[API]** `get_object` returns frame URLs directly. Building the string yourself caches a host,
an account UUID and a path layout that are the server's to change — and it is **wrong for
completed objects**, which serve `rotations/<name>.png`, not `frame_N.png`.

There is also a host-independent endpoint: `https://api.pixellab.ai/mcp/objects/{id}/download`.

⚠ **The CDN 403s urllib's default User-Agent.** A browser UA is required and is a **declared
dependency** in `tools/pixellab_pack.py`.

### 2.8 Sub-32px operations that DO work at 24×24

`correct_pixelart` (0.1 gen, no minimum, keeps existing size) · `reduce_colors` (0.1 gen) ·
`image_to_pixelart` (1 gen, output min 16) · `create_character` v3 + reference (2–9 gen, min 16) ·
`create_object_state` (§1.2).

⚠ **`unzoom_image` cannot close the ×2-upscale round trip**: input minimum **256** (24×2 = 48),
and *"The result is OPAQUE: transparency in the input is composited onto white first."*
**Transparent cutouts do not survive it.**

### 2.9 Do not adopt `reduce_colors`

It exists (0.1 gen) and its stated purpose is **joint** quantization — *"quantized TOGETHER, so
an animation or a character's eight directions come back sharing ONE palette instead of drifting
apart."* **Palette drift between frames is not a problem a fixed-palette pipeline has.** A
server-side quantizer would put the palette in two places.

---

## 3 — STANDING LAW (Ruling 102/103, both games)

1. **Confidence tags are MANDATORY** on any claim about an external system. **An untagged claim
   about an API is treated as unverified.**
2. **Cite the endpoint's own live schema** — never a neighbour's, never a prior report.
3. **Budget against the per-call ceiling, never the floor.**
4. ⚠ **Where a question gates real work and the probe is REFUSAL-SHAPED, measure it rather than
   reason about it — a rejected call is measured free (§1.4). Reasoning is for questions that
   cost money to ask.**

⚠ **1–3 are necessary and not sufficient.** All three were obeyed and the `edit_image` floor was
still called wrong, because two schema clauses were read separately when they compose and [HELP]
agreed with the misreading. **Two weak sources agreeing is not corroboration when they fail the
same way.** Rule 4 exists because of that.

---

## 4 — THE PIPELINE STEP THAT WENT UNRUN FOR MONTHS

`docs/art-pipeline.md:30` mandated `select_object_frames` from July. It had **zero call sites**
until 2026-08-25. The account accumulated **90 objects at `review:awaiting-selection`** against 9
completed — all nine map-layer, because the map layer finished its selections and the character
layer did not.

**The cost was not storage.** An object-id-keyed endpoint cannot be called on a review object, so
`create_object_state`, `animate_object` and `update_object_tags` were available to the map layer
and unavailable to the character layer, invisibly, for months.

**Now: 87 review / 12 completed / 3 failed.** The three shipped Pixellab figures are promoted.

⚠ **The reasoning was never missing** — `batch1r/evidence/promote.txt` had it in full. **The API
call and a machine-readable record were.**

> ### ⚠ CANON — THE SILENT-STEP AUDIT (Ruling 104, both games)
>
> **Any step a pipeline doc mandates must have a check that goes red when it doesn't run.**
>
> Nothing failed when this step was skipped. No test went red, no gate complained, the art
> shipped and passed its device gate. The omission was invisible for months while it silently
> cost the character layer an endpoint family. **A documented step with no enforcement is not a
> step. It is a wish.**
>
> The failure mode is specific: the step's *absence* had no observable consequence at the time,
> only later and somewhere else. Such steps cannot be caught by review or by testing the output
> — **the output was fine.** They are caught only by a check that asks *"did this run?"* rather
> than *"is the result good?"*
>
> When you add a mandated step, ask what goes red if someone skips it. If the answer is
> "nothing", either add the check or stop calling it mandatory.

`pixellab_pack.py audit` now reds a lane whose fetched pack has no recorded selection.

---

## 5 — LEDGER DISCIPLINE

- **Record object IDs AT QUEUE TIME, not at fetch time.** Ten objects (~180 generations) exist on
  the account with no repo reference of any kind — packs queued and never fetched, so never
  written down. Recording at fetch time cannot catch that by construction.
- **Bracket every spend with `get_balance`.** It is the only ground truth, and the subscription
  is **shared between two games**.
- ⚠ **Know which regime you are in.** Batch 3 was **dollar-metered in its entirety** — *"THE
  MONTHLY POOL WAS NOT TOUCHED AT ALL"* — at a measured $0.45/100 generations, while the pool
  still held six generations. **Pool arithmetic cannot price dollar-metered history.**
