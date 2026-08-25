# PIXELLAB — INTEGRATION AND VERSION AUDIT

**2026-08-25.** Companion to `docs/PIXELLAB-UW-AUDIT-2026-08-25.md`, which audited *our
usage*. This one audits *the platform* — what PixelLab offers now, what we are actually
pointed at, and what a from-scratch YARL art programme should be built on.

Facts are tagged **[SCHEMA]** (read from a live spec fetched today), **[TREE]** (our own
files), or **[API]** (a real call against our account — §8 only). §§1–7 cost nothing; **§8
is measured and cost 88 generations**, authorised by Rafe. Every probe call is recorded at
queue time in `tools/pixellab/probes_2026-08-25/probe_ledger.jsonl`.

**Five of Gemfall's findings are corrected here** — §2, §4, §8.1, §8.3, §8.5 — plus one
platform cost formula that is simply wrong (§8.4). Sources, all fetched 2026-08-25:

| source | result |
|---|---|
| `https://api.pixellab.ai/v1/openapi.json` | 200, 36,851 bytes |
| `https://api.pixellab.ai/v2/openapi.json` | 200, 409,800 bytes |
| `https://api.pixellab.ai/v2/llms.txt` | 200, 16,587 bytes |
| `pypi.org/pypi/pixellab/json` | latest **1.0.5**, uploaded **2025-05-07** |
| `github.com/pixellab-code/pixellab-python` | last push **2026-05-27** |
| `github.com/pixellab-code/pixellab-mcp` | last push **2025-08-10** |

---

## 1 — ARE WE ON THE LATEST? No. We are three layers behind, and one of them is not ours.

**[SCHEMA]** **v1 exposes 8 endpoints. v2 exposes 92.** YARL uses four of the eight:
`/generate-image-bitforge`, `/inpaint`, `/animate-with-text`, `/balance`.

**[TREE/SCHEMA]** The gap is not our fault so much as inherited:

- `pip install pixellab` gives **1.0.5, published 2025-05-07** — that *is* the latest
  published release, and it wraps **v1 only**.
- The SDK's **GitHub repo was pushed 2026-05-27** — roughly a year of work that has never
  been released to PyPI.
- So *"use the most recent version of the SDK"* and *"use the most recent API"* are in
  direct conflict. **The most recent published SDK cannot reach 84 of the platform's 92
  endpoints.** Pinning a newer SDK is not available to us; the way to the current platform
  is HTTP against v2, or the MCP server.

⚠ **The standalone MCP repo (`pixellab-code/pixellab-mcp`) was last pushed 2025-08-10** —
a year stale. **That is not what Gemfall uses.** Gemfall's registration (read from
`~/.claude.json`) is the **hosted** server:

```json
{ "type": "http", "url": "https://api.pixellab.ai/mcp",
  "headers": { "Authorization": "Bearer <token>" } }
```

Hosted, so it tracks the platform rather than a stale repo. **Do not install the
standalone MCP package.**

---

## 2 — ⚠ CORRECTION TO `PIXELLAB-VERIFIED.md` §2.1 — the 2000-char cap **is** declared

Gemfall: *"`create_1_direction_object.description` declares no `maxLength` … It has cost
this project three arms. 2000 is consistent with all five and independently unproven."*

**[SCHEMA]** The live v2 OpenAPI declares it outright:

```
Create1DirectionObjectRequest.description   type=string  maxLength=2000  minLength=1
```

Also `CreateMapObjectRequest.description` → `maxLength=2000`;
`CreateCharacterStateRequest.edit_description` and `CreateObjectStateRequest.edit_description`
→ `maxLength=1000`; `state_name` → `maxLength=100`.

Gemfall's finding is true of the **MCP tool schema** and false of the **REST spec for the
same operation**. They spent three arms measuring what the OpenAPI states.

> **The generalisation, and it is the most useful thing in this document:**
> **the MCP tool schemas are a lossy projection of the REST spec.** Constraints present in
> OpenAPI are missing from the MCP tool description. So `PIXELLAB-VERIFIED.md` Law 2 —
> *cite the endpoint's own live schema* — needs one more clause for both games:
> **the endpoint's own live schema is the OpenAPI entry, even when you are calling
> through MCP.**

---

## 3 — [SCHEMA] v1 and v2 BitForge are the same endpoint under two names

`v1 /generate-image-bitforge` → `GenerateImageBitforgeRequest`, 24 properties.
`v2 /create-image-bitforge` → `CreateImageBitforgeRequest`, 24 properties.
**Set difference in both directions: empty.** Neither carries a `deprecated` flag.

Consequences:

- Our existing BitForge work is **not stale in capability**. The palette-lock `color_image`
  finding, the minimal-params rule, the register prompt work — all still current.
- **Migrating BitForge to v2 is a base-URL change, not a rewrite.**
- v2's own description confirms the palette mechanism: supported features include
  *"Forced palette"*. And a size ceiling we had not written down: *"Maximum area 200x200"*.

---

## 4 — ⚠ CORRECTION TO `PIXELLAB-VERIFIED.md` §2.4 — and the answer to "what does item 1 buy?"

Gemfall's most-emphasised transfer rests on this MCP prose: *"this ALWAYS preserves the SAME
individual's face and identity … NOT a new character"*, contrasted with
`create_object_state`, which *"says nothing about identity."*

**[SCHEMA]** In the REST spec the two are described **almost identically**:

> `POST /create-character-state` — *"Queues a generation job that applies a text edit to an
> existing character's rotations and saves the result as a new character grouped with the
> source via `group_id`. The same edit is applied consistently across all 4 or 8 directions."*
>
> `POST /objects/{object_id}/states` — *"Queues a generation job that applies a text edit to
> an existing object's image(s) and saves the result as a new object grouped with the source
> via `group_id`."*

**The REST spec draws no identity distinction between them.** The identity guarantee is
MCP-layer marketing prose with no counterpart in the schema. It may well describe real
model behaviour — but it is **not a documented contract**, and a decision the brief calls
"expensive to reverse" should not rest on it.

**What the schema *does* separate — real, checkable differences:**

| | character state | object state |
|---|---|---|
| edit applied across all 4/8 rotations consistently | **yes** | n/a |
| `use_color_palette_from_reference` — snap the new state to the source's palette | **yes** | **absent** |
| `override_frame_size` — bigger canvas for edits that add a weapon/wings | **yes** | **absent** |
| `no_background` | yes | absent |
| `seed`, `state_name`, `edit_description` (max 1000) | yes | yes |

**So, concretely, what item 1 buys YARL:** palette-consistency between a creature and its
states, room to grow the canvas for a state that adds bulk, and one edit applied coherently
across rotations. **Not** a guarantee that the face is the same person.

**The spec publishes a cost formula. ⚠ It is wrong by 31× — see §8.4.** `POST
/create-character-v3` states reference-image mode costs `ceil(w*h*8 / 65536)` and
from-scratch `1 + ceil(s²*8/65536)`, which for 32×32 predicts **2 generations**. Measured:
**62**. Do not plan against the published formula. ⚠ Also correcting Gemfall: the spec says
the final canvas is *"padded ~2x for animation room (capped at 256)"*, not ~40% larger —
though the rotations we got back were exactly `image_size` with no padding (§8.4).

⚠ **The YARL-specific catch nobody has raised.** Every character path on this platform is
built around **8 directional rotations** (`/create-character-v3` — *"8 rotations"*;
reference image *"must be south-facing"*). YARL is a **top-down, single-direction** game.
We would be paying for and managing eight views to use one — and the identity machinery is
welded to the rotation machinery. `/objects/{id}/states` is 1-direction-native.

**My read, for your ruling:** the decision is *less* binding than the brief claims and
should be taken on palette-consistency and canvas-growth, not on the identity prose. The
cheap, correct probe is: generate one creature both ways at the same seed, apply the same
state edit, and compare. It costs a handful of generations and settles it with evidence
instead of prose. I would not commit the creature pipeline to `create_character` on the
strength of a sentence that the REST schema does not corroborate.

---

## 5 — ⭐ THE THING WE HAVE NEVER TOUCHED, AND SHOULD — `POST /create-tiles-pro`

You are about to build an entire look from scratch, for a **top-down dungeon**. This
endpoint exists and YARL has never called it. **[SCHEMA]**, verbatim:

> - **`tile_feature: "roads"`** — an 18-configuration path/road autotile set
> - **`tile_feature: "tileset"`** — a terrain-transition Wang set: 16 corner tiles for
>   square_topdown/isometric/oblique
> - **`tile_feature: "building"`** — a construction kit: **floor, connectable wall segments,
>   doorways, pillar and staircase** (square_topdown, isometric, oblique)

That is a dungeon, generated as a coherent connectable set rather than as 80 individually
prompted props that we then try to make look related. It takes `tile_size` 16–128,
`style_images`, `style_options`, and `seed`.

`POST /create-tileset` is the other half — two terrain levels that connect seamlessly,
16 or 25 tiles, with `color_image` **and** per-level reference images
(`lower_reference_image`, `upper_reference_image`, `transition_reference_image`), plus
`outline` / `shading` / `detail` / `raggedness` / `slope_size` controls and a `seed`.

**This reframes the art programme.** Our entire historical process — one prop at a time,
each independently prompted, coherence chased afterwards through palette-lock swatches and
a fineness lint — exists because the only tool we had was a single-image generator.
The platform now has set-coherent generation with style conditioning. **Round 1 of the new
look should start here, not at `bank_generate.py`.**

`POST /map-objects` is the matching props path: `maxLength=2000` description, `color_image`,
`init_image` + `init_image_strength`, `background_image`, `seed`, async job, and — unlike
`create-1-direction-object` — **no review queue to leak** (*"Returns immediately with job
ID. Processing takes ~15-30 seconds."*).

---

## 6 — WHAT I CHANGED (this branch)

Applied from `PIXELLAB-UW-AUDIT` §17, chosen because they survive a migration:

1. **`.mcp.json`** (new) — registers the **hosted** PixelLab MCP server for this repo, the
   same one Gemfall uses. Token comes from `${PIXELLAB_API_TOKEN}` in the environment; **no
   credential is committed.** Needs a session restart to take effect.
2. **`client_compat.py` — refusal capture.** `raise_for_status()` is gone. `_check()` reads
   `r.text` *before* raising, classifies it (`content_policy` / `over_length` /
   `rate_limit` / `auth` / `insufficient_balance` / `invalid_input` / `server_error` /
   `unknown`) and raises `PixelLabRefusal` carrying status, classification, verbatim body and
   endpoint. This closes the loss that already cost us `shelf_bottles_s3`.
3. **`client_compat.py` — `balance_bracket`.** A context manager that reads `/balance` before
   and after a batch and appends both to `reports/pixellab_balance_log.tsv`. A failed balance
   read degrades to `delta=UNMEASURED` rather than silently implying zero spend.
4. **`bank_generate.py`** — wraps its run in `balance_bracket`, and **writes a ledger row on
   failure** (`verdict=error:<classification>`, verbatim reason in `notes`) instead of
   printing to stderr and moving on.
5. **`client_compat.py` — credentials.** Accepts `PIXELLAB_API_TOKEN` **or**
   `PIXELLAB_API_KEY` and names both if neither is set, ending the split that let
   `bank_generate`'s guard pass and then die. ⚠ **`.mcp.json` requires the `_TOKEN` spelling
   specifically** — make that the canonical one.
6. **`selftest_refusal_capture.py`** (new) — no-network, zero-cost self-test.

> ⚠ **The instrument has demonstrated it can fail** (`ART-LOOP-PROCESS-v0.md` §4, bible
> §13.5). `_check()` was temporarily sabotaged to return unconditionally; the self-test went
> from green to **8 red checks** reading `INSTRUMENT IS BLIND`, and back to green on restore.
> Its passes count.

**Deliberately not done:** the `--max-total`-counts-files issue (§8 of the usage audit) and
the ledger-format unification (§5, §12). Both are properties of the v1 script fleet, which
this audit recommends retiring rather than repairing.

---

## 7 — RECOMMENDATION: one surface, v2, and retire the fleet

Today YARL has **three** client constructions (SDK direct in 7 scripts, `client_compat` raw
HTTP, `sweep.py`'s own) and **five** ledger formats, all pointed at v1.

**Target state — one module, v2, two access modes:**

- **MCP (hosted) for interactive and exploratory work** — the sessions where you and I are
  looking at candidates together. Now registered.
- **HTTP against v2 for batch and anything reproducible** — because the MCP schemas are
  lossy (§2) and batch runs need ledgering the MCP layer does not do.
- **The v1 fleet is legacy.** `client_compat.py` now carries a LEGACY banner. Nothing new
  should be written against it, and it should be deleted once round 1 of the new look is
  running on v2.

**Suggested order of work:**

1. **Probe `create-tiles-pro` with `tile_feature: "building"`** at YARL's tile size, with a
   style image. This is the highest-information call available and it either reframes the
   art programme or it doesn't. Cost is small and bounded.
2. **Settle item 1 by measurement, not prose** — the two-way creature-state probe in §4.
3. **Measure the v1/v2 `/inpaint` floor** — still unmeasured, still refusal-shaped,
   therefore free.
4. **Build the single v2 module** once 1–3 have said what it must carry.
5. **Rewrite `PIXELLAB_CONVENTIONS.md`** against the new surface. It currently documents a
   single-image process and a retired Oryx track, and it is our only prompt-discipline
   record — do not lose the register ruling or the canon-validated-swatch rule in the move.

⚠ Per bible §13.5, every check built in step 4 must demonstrate it can fail before its
passes count — the pattern is in `selftest_refusal_capture.py`.

---

## 8 — [API] MEASURED PROBES, 2026-08-25

Everything in this section is **[API]** — real calls against our account, each recorded at
**queue time** in `tools/pixellab/probes_2026-08-25/probe_ledger.jsonl` (96 entries).
**Total spend for the whole session: 88 generations** (4660 → 4572), about 1.8% of the
monthly pool. Authorised by Rafe.

### 8.1 ✅ Both billing regimes are visible in ONE `/balance` response

```json
{"credits":      {"type":"usd","usd":8.11},
 "subscription": {"type":"generations","status":"active",
                  "plan":"Tier 2: Pixel Artisan","generations":4660.0,"total":5000.0}}
```

⚠ **Corrects `PIXELLAB-VERIFIED.md` §5.** "Know which regime you are in" is not a thing you
have to reconstruct after the fact — the endpoint returns the dollar credits **and** the
pool in the same object. Record the whole response, not a single number.

### 8.2 ✅ The 2000-char cap is enforced, and the error names the limit

A 2001-character `description` to `/create-1-direction-object` returns **HTTP 422**:

```json
{"detail":[{"type":"string_too_long","loc":["body","description"],
            "msg":"String should have at most 2000 characters","input":"a wooden barrel ..."}]}
```

A structured pydantic validation error naming the field, the constraint and the limit.
**The rejection was free** — the pool did not move. Gemfall's three arms bought a fact the
API states in both the spec and the error body.

> ⚠ **This probe found a bug in the instrument built earlier the same day.** `_classify()`
> matched `"too long"` with a space; the real body says `"string_too_long"` and
> `"at most"`. The one over-length shape that actually occurs was being filed as
> `invalid_input`. Fixed, and the **verbatim** body is now a regression case in
> `selftest_refusal_capture.py`. This is the entire argument for Law 4 in one incident:
> the reasoned classifier was wrong and the free probe found it in one call.

### 8.3 ⚠ REFUTED — there is no 32px floor on REST `/inpaint`, on either version

| call | result | cost |
|---|---|---|
| v1 `/inpaint` 16×16 | **200**, out 16×16 RGBA | 1.0 gen |
| v1 `/inpaint` 24×24 | **200**, out 24×24 RGBA | 1.0 gen |
| v2 `/inpaint` 16×16 | **200**, out 16×16 RGBA | 1.0 gen |
| v2 `/inpaint` 24×24 | **200**, out 24×24 RGBA | 1.0 gen |

Two things die here:

1. **`regen_chests_variants.py`'s folklore is refuted.** *"Upscale to 64x64 for inpaint
   (clean ratio, avoids min-area issues)"* — there were no min-area issues. The chest
   variant work paid for a canvas it never needed.
2. **Gemfall's §1.1 floor is MCP-surface-only.** `edit_image`/`inpaint_image` on MCP reject
   24×24; REST `/inpaint` accepts 16×16 on both versions. *Do not generalise a floor across
   a family* now extends to: **do not generalise a floor across surfaces either.**

Cost is **1 generation per inpaint**, not the 20–40 of the Pro object tools.

### 8.4 ⚠ THE PUBLISHED COST FORMULA IS WRONG BY 31×

One `POST /create-character-v3`, from-scratch mode, `image_size` 32×32:

| | generations |
|---|---|
| spec formula `1 + ceil(32*32*8/65536)` | **2** |
| **measured** (4634 → 4572, settled) | **62** |

Everything else about the result was as documented: `status: completed`, **8 rotations**
(`north`, `north-east`, … `north-west`), each **exactly 32×32** — ⚠ no ~2× canvas padding
on the rotations, contra the spec's own note. `group_id` is assigned at creation and the
base character is itself a state (`state_name: "Idle"`).

**Consequence.** Gemfall's §2.5 — *"a call CAN charge more than it reserved; budget against
the ceiling"* — is far stronger than stated. It is not a 20-vs-40 question. **A documented
formula was off by a factor of 31.** For YARL: eight rotations we do not need, at 62
generations each, is not the way to make a top-down creature.

### 8.5 ⚠ The balance ledger settles late, and slowly — every short-bracket cost is a lower bound

| observation | immediate read | settled read |
|---|---|---|
| 6 × `/inpaint`, each reporting `usage: 1.0` | 4660 → **4655** | 4660 → **4654** |
| 1 × `/create-character-v3` | 4634 → **4592** | 4634 → **4572** |

The second case is the alarming one: two reads 15 s apart **agreed on 4592**, and the true
figure was 4572. A naive settle rule confirms a number that is 32% low.

⚠ **This reaches back across both games.** Any cost figure derived from a short
`get_balance` bracket — including `PIXELLAB-VERIFIED.md` §1.2's *"Cost: 20 generations — the
floor of the stated 20–40"* — is a **lower bound, not a measurement**, unless the closing
read was held until stable. `balance_bracket` now requires **3 consecutive identical reads
at 10 s intervals** and prints `LOWER BOUND, not a measurement` if it gives up.

### 8.6 ⚠ HTTP 423 means "still generating", not "refused"

`GET /tiles-pro/{id}` while processing returns **423 Locked**,
`{"detail":"Tiles are still being generated"}`. A refusal classifier that buckets any 4xx as
an error will file every in-progress poll as a rejection. **423 is a retry signal.** Any v2
client must treat it as such — noted here because the v2 module in §7 has to get this right
from the start.

### 8.7 ⭐ THE BUILDING KIT — 20 generations, 80 tiles, and a placement grammar

One call to `/create-tiles-pro`, `tile_feature: "building"`, `tile_type: "square_topdown"`,
`tile_size: 32`, `building_wall_tiles: 2`, `tile_view: "high top-down"`, `seed: 1337`,
wall/floor described separately. **Cost: 20 generations** (4654 → 4634, exactly the reported
`usage`). Evidence: `tools/pixellab/probes_2026-08-25/building_kit_sheet.png`.

It returned **80 tiles** *and* `tile_rules` — a machine-readable placement grammar
(`arity: 8`), saved as `building_kit_tile_rules.json`:

| part | indices |
|---|---|
| `floor` | 0 |
| `sides` N/E/S/W | 1–4 |
| `corners` NE/SE/SW/NW | 5–8 |
| `outer_corners` NE/SE/SW/NW | 9–12 |
| `partition` hub + N/E/S/W | 13–17 |
| `partition_wall`, `partition_multi` (NE, NW, ES, SW, NES, NSW, NEW, ESW, NESW) | 18–30 |
| `pillar` | 31 |
| `doors` Na/Nb/Ea/Eb/Sa/Sb/Wa/Wb | 32–39 |
| `stairs`, `stairs_east` | 40–43 |
| `partition_doors` Va/Vb/Ha/Hb | 45–48 |
| `outer_multi` (NES, NEW, NSW, ESW, NESW, NS, EW) | 49–55 |
| `slopes` | 56–59 |
| `roof` — eaves, hips, valleys, ridges, ends, pyramid, interior | 60–79 |

`materials` echoes the wall and floor descriptions back; `painted` lists which tiles were
individually painted rather than assembled from swatches.

**Honest assessment, because this needs a human gate and not my enthusiasm:**

- ✅ **Coherence is the win.** Every piece is the same stone, same lighting, same brick
  scale, same registration. That is the property our one-prop-at-a-time process has never
  achieved and has spent hundreds of generations chasing.
- ✅ **Pre-registered for compositing.** All 80 tiles share a 52×87 canvas with the floor
  footprint anchored at exactly (10,55)–(42,79). The kit is a drop-in for a composer.
- ✅ **The grammar is the real product.** A 9-case partition set with multi-junctions and a
  separate outer-corner set is an autotiler, not a sprite sheet.
- ⚠ **A quarter of it is roof** — 20 of 80 tiles are gable roof, useless for a top-down
  dungeon interior, and we paid for them. No parameter appears to suppress them.
- ⚠ **The footprint is not `tile_size`.** A 32px square_topdown tile at high top-down emits
  a **32×24** floor footprint on a 52×87 canvas (the extra height carries the 2-tile wall).
  YARL's world grid is **24×24**. This needs a deliberate decision, not a downscale reflex.
- ⚠ **Register risk.** The brick courses are fine-grained — many small structures. That is
  precisely the *refinement* failure mode the register ruling names. Whether it reads chunky
  enough is exactly the kind of judgement §13.4 says stays at the human gate. **This is a
  contact sheet. Per bible §13.1 nothing here is approved.**

**What it changes.** Our whole historical process exists because a single-image generator
was the only tool we had. It is not any more. For a from-scratch look, one 20-generation
call produced more usable, more coherent dungeon geometry than the 1,174-generation
speculative bank did.

### 8.8 ⭐ THE IDENTITY PROBE — identity holds, the *edit* is what doesn't

`/create-character-v3` from-scratch → `"skeleton warrior with rusted iron sword and tattered
cloak"`, 32×32, 8 rotations. Then `/create-character-state` on it with
`edit_description: "badly wounded, cracked ribs, one arm missing"`, `state_name: "wounded"`,
`use_color_palette_from_reference: true`, `seed: 1337`.

**Cost: 20 generations** for the state (4572 → 4552, three stable reads). The state carries
the **same `group_id`** as its source, and the same 32×32 size. Evidence:
`tools/pixellab/probes_2026-08-25/identity_compare.png` — all 8 directions, base over state.

**✅ Identity preservation is real, and better than the schema promises.** Across all eight
rotations the state is unmistakably the same individual: same skull, same blue-grey
pauldron, same brown tattered cloak, same rusted blade with the same orange-and-white edge
pattern, same palette, same silhouette. Whatever the REST spec declines to promise, the
model delivers here.

**⚠ And that is exactly the problem.** *The edit barely happened.* The instruction asked for
cracked ribs and **one arm missing**. In the result the figure still has both arms and is
still holding the sword. The differences are minor torso and shading changes. The state is
"the same skeleton, very slightly different" — not "the same skeleton, wounded."

> **The trade-off is the opposite of what the brief's prose implies.** The identity contract
> is not the scarce thing — **edit compliance is.** `create_character_state` appears to
> preserve identity *by being conservative*, and a state edit that needs a large structural
> change does not get one.
>
> **This matters directly for YARL.** Our headline state use cases — a corpse, a dismembered
> or burnt creature — are exactly the large structural edits this path declined to make. On
> this single sample, `create_character_state` would not produce our corpses.

⚠ **One sample. It is a contact sheet, not an approval** (bible §13.1), and one sample of
good behaviour is not a contract — the same caution Gemfall attached to its own state probe.
The next probe should vary edit magnitude (a small edit: "moss-covered"; a large one:
"skeleton collapsed into a pile of bones") to find where compliance breaks, and run the
same pair through `/objects/{id}/states` for the 1-direction comparison YARL actually needs.

**Session total: 108 generations** (4660 → 4552), 2.2% of the monthly pool.

### 8.9 [API] Enums are per-endpoint too, and the candidate-count rule confirms

`/create-1-direction-object` with `view: "high top-down"` — the value `/create-tiles-pro`
accepts — returns **HTTP 422**, free:

```json
{"detail":[{"type":"literal_error","loc":["body","view"],
            "msg":"Input should be 'top-down' or 'sidescroller'",
            "ctx":{"expected":"'top-down' or 'sidescroller'"}}]}
```

`tile_view` on tiles-pro takes `top-down` / `high top-down` / `low top-down` / `side`;
`view` on the object endpoints takes only `top-down` / `sidescroller`. **Do not carry an
enum value from one endpoint to its neighbour** — the same rule as constraints, now measured
for enums.

Resubmitted with `view: "top-down"`: **200**, and the response declares **`n_frames: 64`**,
confirming as **[API]** what `PIXELLAB-VERIFIED.md` §2.2 had as [SCHEMA] — a 32px object
produces 64 candidates and therefore **enters the review queue**. This is the mechanism
behind Gemfall's 90 stuck objects: one ordinary call creates a review object by default.

---

## 9 — [API] PHASE 2 — the edit-magnitude sweep and the tile-size question

Authorised follow-up. Evidence: `probes_2026-08-25/edit_magnitude.png`,
`kit_size_compare.png`.

### 9.1 ⭐⭐ `create_character_state` IS A RE-TEXTURE, NOT A RE-SCULPT

Four state edits on the same source character, same seed, same
`use_color_palette_from_reference`, **20 generations each**:

| edit | kind | applied? |
|---|---|---|
| `"moss-covered and mildewed"` | surface | ✅ **yes** — clear green mossy growth over the same figure |
| `"badly burnt, blackened and charred"` | surface | ✅ **yes** — whole figure darkened and charred convincingly |
| `"badly wounded, cracked ribs, one arm missing"` | structural | ❌ **no** — both arms, still holding the sword |
| `"collapsed into a loose pile of bones on the ground"` | structural, extreme | ❌ **no** — still a standing skeleton warrior, near-identical to base |

**The rule, and it is sharp:**

> **`create_character_state` changes materials, colour and tone. It does not change
> geometry.** Identity is preserved *because* geometry is held rigid — that is the
> mechanism, not a bonus. Ask it to re-sculpt and it silently returns the source.

⚠ **The failure is silent AND billed.** "Collapsed into a pile of bones" charged **20
generations** to return the standing skeleton. There is no error, no warning, no
`edit_applied: false`. A pipeline that fires state edits without a human or a diff check
looking at the output will pay full price for no-ops and never know.

**What this settles for YARL:**

- ✅ **Status/elemental states are a solved problem** — burning, frozen, poisoned, mossy,
  blood-soaked, corrupted. 20 generations each, identity guaranteed, palette snapped to the
  source. This is a genuinely good deal and we should use it.
- ❌ **Corpses cannot come from this path.** Nor can dismemberment, collapse, or any
  silhouette change. A corpse is a different pose and a different silhouette — it must be
  authored as its own asset. **That is the concrete answer to item 1**, and it is the
  opposite of what the transfer brief implied was at stake.

### 9.2 [API] Footprint is `tile_size` × 0.75·`tile_size` — and `tile_size` is a register control

Same building-kit prompt and seed, re-run at `tile_size: 24`. **Same 20 generations, same 80
tiles, same `tile_rules` grammar.**

| `tile_size` | sprite canvas | floor footprint |
|---|---|---|
| 32 | 52 × 87 | **32 × 24** |
| 24 | 38 × 64 | **24 × 18** |

The footprint is `tile_size` wide by **0.75 × `tile_size`** tall — the depth compression of
`tile_view: "high top-down"`. Not a quirk of one call; it is the projection.

⭐ **The unexpected result: the 24px kit reads markedly CHUNKIER than the 32px one.** Same
prompt, same seed, same wall description — but at 24px the model fits fewer, larger bricks
with bolder mortar contrast, while at 32px it packs in fine brick courses. That is the
*refinement* failure mode the register ruling names, appearing and disappearing purely as a
function of `tile_size`.

> **`tile_size` is a register lever.** The register problem we have chased with prompt
> fragments, fineness metrics and palette locks has a direct parameter on this endpoint.
> Smaller tiles force chunk. That is worth more than any prompt wording we have tried.

**On the grid question** — the grid is being reconsidered as part of the rebuild, so the kit
should drive the grid, not the reverse:

- `high top-down` gives visible wall faces and depth, and a **4:3** floor cell.
- A square cell would need `tile_view: "top-down"` (zero depth), which flattens the walls
  too — that trade is measured in §9.3.
- **Recommendation: choose `tile_size` for register first** (24 currently reads better than
  32), then take the cell aspect that projection gives, rather than picking a grid and
  forcing the art to it. Nothing here is approved — it is a contact sheet (bible §13.1).

### 9.3 ⚠ `tile_view` is SILENTLY IGNORED on building kits — and the endpoint is DETERMINISTIC

Same call as §9.2's 24px kit, changing only `tile_view` from `"high top-down"` to
`"top-down"`. Cost: another **20 generations**. Result:

> **All 80 tiles are PIXEL-identical to the `high top-down` run.**
> (PNG bytes differ — encoder metadata — but `ImageChops.difference(...).getbbox()` is
> `None` for every one of the 80.)

**Two things fall out, one bad and one good.**

⚠ **Bad: `tile_view` does nothing when `tile_feature: "building"` is set, and it still
charges.** No error, no warning, no echo in the response. This is the **second silent
billed no-op** measured today (§9.1 is the first). A pattern is forming on this platform:

> **Parameters that do not apply are silently accepted and fully charged.** There is no
> `ignored_parameters` field and no validation error. The only way to know a parameter did
> anything is to run it twice and diff the pixels.

⚠ **This corrects §9.2's recommendation.** You cannot buy a square floor cell by switching
`tile_view` — the 4:3 footprint is fixed for `square_topdown` building kits. If a square
cell is wanted, the untested levers are `building_wall_angle` (spec: *"square_topdown only:
wall storey height as its own camera angle, decoupled from the ground pitch"*) or a
different `tile_type`. **Do not plan around `tile_view` here.**

✅ **Good, and it matters more: `/create-tiles-pro` is deterministic under `seed`.** Same
seed and same *effective* parameters produced 80/80 pixel-identical tiles. Regeneration is
reproducible, which is a hard requirement in this project rather than a preference
(CLAUDE.md, *"Determinism means the seed"*). A future kit can be re-derived from its ledger
row instead of stored — though we should still store it.

> **Method note for the new pipeline.** Pixel-diffing two runs that vary one parameter is
> the only reliable way to tell whether that parameter is live on a given endpoint. It costs
> one extra call and it is the only instrument that can catch a silent no-op. Build it into
> the v2 module as a `--probe-param` mode.

### 9.4 [API] The object path — review hygiene measured end to end, and it out-registers the character path

`POST /create-1-direction-object`, `size: 32`, `view: "top-down"`. The response declared
**`n_frames: 64`** and the object landed in **`status: review`** — we created, deliberately,
exactly the thing Gemfall accumulated 90 of. Full record and reasoning:
`probes_2026-08-25/SELECTION-df3e1cf8.md`. Contact sheet: `obj_review_frames.png`.

**Three costs, all settled over 40 s:**

| call | cost | note |
|---|---|---|
| `create-1-direction-object` (64 candidates) | 20 | the floor of the stated 20–40 |
| `select-frames` (1 of 64) | **0** | ✅ corroborates Gemfall §1.3 independently |
| `dismiss-review` | **0** | ⭐ **a Gemfall unknown, now measured** |

**Corroborated as [API] on our own account:** promoting one frame left the parent at
`status: review` with **63 frames** (§1.5). Promotion does **not** clear the review state —
`dismiss-review` does, after which `GET` returns 404. The account now lists 37 review / 10
completed / 3 failed, **all Gemfall's; YARL leaves none behind.**

⚠ **Free rejection, useful schema:** the field is **`indices`**, not `frame_indices`.

⭐ **The unplanned finding, and it is the most interesting one in phase 2.** Set the 64
object candidates beside the character-v3 output. **The object path reads markedly chunkier
and bolder** — thick continuous outlines, low interior detail, clean silhouettes at native
32px — while the character path produced a finer, more rendered figure. Same account, same
day, similar prompt.

> **For a top-down game building a look from scratch, the object path looks like the better
> register fit, and it is 1-direction-native** — no eight rotations to pay for and manage.
> Combined with §9.1 (states cannot re-sculpt, so corpses are separate assets anyway) and
> §4 (the identity contract is MCP prose the REST spec does not corroborate), **the case for
> entering through `create_character` is now weak for YARL.** The transfer brief's
> most-emphasised warning does not survive contact with our own measurements.
>
> ⚠ One caveat, stated plainly: 64 candidates from one prompt versus one character from
> another is not a controlled comparison of register. It is suggestive, not settled. The
> controlled version — same prompt, same seed, both paths — is the next probe worth running.
