# §6.4 PROBE — SURFACE AUDIT

**Status: evidence for a freeze decision that has NOT been taken. Nothing here ratifies a
canvas, creates a palette, or promotes a candidate. No probe arm has run.**

Run 2026-08-25 against commit `330130c` (branch `art/probe-6.4-receive-light`).
Ledger: `audit_evidence/ledger.jsonl`, one flushed row per call. Images: `audit_evidence/*.png`.

**Every verdict below is what the server did.** Schemas are recorded where they disagree with
behaviour, and where a row is schema-only it says so. Tagging follows PIXELLAB-VERIFIED:
**[API]** measured by a real call, **[SCHEMA]** read from a live spec.

Spend: **246 generations** across the whole session (4371 → 4125 remaining). Credits `$8.11`
unchanged throughout — this account bills against a generation allowance, not the usd balance.

---

## COLUMN 1 — style/reference conditioning

| Surface | 24×24 | Conditioning channel | Refs | Measured limits |
|---|---|---|---|---|
| MCP `create_image_pixflux` | **✗ [API]** | `init_image` — img2img, **not** style transfer | 1 init | Refuses any canvas under 1024px |
| MCP `create_image_pixen` | ✓ [API] | **none** [API] | 0 | Rejects `style_image_base64` as an unexpected keyword — cannot run Stage 2 at all |
| MCP `create_image_pro` | ✓ [API] | `style_image` + `reference_images` + `style_copy` | **1 style + up to 4 labelled** [API] | 5 refs → `error: at most 4 reference images, got 5`. 91–168 s/generation |
| v1 REST `/generate-image-bitforge` | ✓ [API] | `style_image` + `style_strength` | **exactly 1** [SCHEMA] | Style image size must **equal** generation size. 21.5 s/generation |
| v2 HTTP `/create-image-bitforge` | ✓ [API] | same as v1 | **exactly 1** [SCHEMA] | same. 20.6 s/generation |

**The size-match rule is a hard server error, not a guideline** [API]:

```
HTTP 500 {"detail":"style_image must be size (24, 24), not torch.Size([32, 32])"}
```

**`style_strength` defaults to `0.0` in `client_compat`** — a reference passed at the default
does nothing. Moving it 0 → 100 changed the output [API].

**Latent defect found in passing.** `client_compat.generate_image_bitforge` encodes
`color_image` but passes `style_image` through raw kwargs, where it dies as
`TypeError: Object of type Image is not JSON serializable`. **The wrapper has never been able to
carry a style image.** `sweep.py` conditioned through the raw SDK instead — the path
`client_compat` exists to route around. Any Stage 2 on a BitForge surface must encode
`Base64Image` by hand or fix the wrapper.

---

## COLUMN 2 — is the treatment lever honoured under conditioning?

The instrument is a controlled pair: same seed, same reference, same prompt, one knob moved.
A pixel-diff is not an aesthetic judgement and does not score art (§13.4) — it answers exactly
one mechanical question: *did the parameter do anything at all.*

### The noise floor had to be measured first (§13.5)

The first pass reported **HONOURED on all four surfaces** at `pixdiff=1.0000`, including a
control. That is an instrument that cannot fail, so its passes did not count. The negative
control — *the identical call, twice* — is what made it readable:

| Surface | Identical call, repeated | Reading |
|---|---|---|
| v1 BitForge | **3 distinct outputs in 8 calls**; pairwise 0.0000 / 0.3542 | seed partly honoured; noise floor ≈ **0.354** |
| v2 BitForge | same pattern, same values as v1 | noise floor ≈ **0.354** |
| MCP `pro` | 1.0000 | seed ignored; **no headroom** |
| MCP `pixflux` | 1.0000 | seed ignored; **no headroom** |
| MCP `pixen` | 1.0000 | seed ignored; **no headroom** |

⚠ **No surface is seed-reproducible.** A two-sample check briefly showed v1 at 0.0000 and was
recorded as "deterministic"; an eight-sample census disproved it. Nothing on this platform lets
you re-derive an image from (prompt, seed) — **the ledger must store the image, not just the
parameters.** The probe's "same seed across arms" premise does not hold on any surface.

### The verdicts that survive the noise floor

| Surface | Lever tested | pixdiff | vs noise | Verdict |
|---|---|---|---|---|
| v1 BitForge | `shading` under `style_image` | 1.0000 | 0.354 | **HONOURED** [API] |
| v2 BitForge | `shading` under `style_image` | 1.0000 | 0.354 | **HONOURED** [API] |
| MCP `pro` | `style_copy` with/without `shading` | 1.0000 | 1.0000 | ⚠ **NO INSTRUMENT** |
| MCP `pixflux` | `shading` under `init_image` | 1.0000 | 1.0000 | ⚠ **NO INSTRUMENT** |
| MCP `pixen` | — no lever, no conditioning | — | — | n/a |

**What HONOURED does and does not mean.** It means the parameter changed the output well above
the platform's own variance. It does **not** mean the parameter changed it in the intended
direction — whether `flat shading` actually reads flatter is an eye question and belongs to the
human gate (§13.2, §13.4). Do not promote this row into an aesthetic claim.

The two MCP rows are the honest `NO INSTRUMENT` output, not a failure to look. Getting a verdict
there needs an aggregate over many samples per condition, which is a proxy under construction
and is not worth building for a decision that other columns already settle.

---

## The pixflux floor: hard, and an AREA floor

[API], four calls:

| Canvas | Area | Result |
|---|---|---|
| 24×24 | 576 px | **REFUSED** — `24x24 is too small (576px, minimum is 32x32 = 1024px)` |
| 16×16 | 256 px | **REFUSED** — same form |
| 32×32 | 1024 px | ACCEPTED |
| **16×64** | **1024 px** | **ACCEPTED** |

**It is a floor on total pixels, not on either dimension** — 16×64 passes with a 16px side. The
schema declares `minimum: 16` per dimension [SCHEMA], which the server contradicts; the server
is the authority.

**It is hard, not a default.** The documented bypass — omit `width`/`height` and let
`init_image` dictate size — was tried with a 24×24 init image and refused with the identical
576px error. There is no parameter that lowers it.

---

## v1 retirement status: OUR policy, not the vendor's

**[API] — both live specs fetched this session:**

- `v1/openapi.json`: 8 paths, `POST /generate-image-bitforge` → `deprecated=False`. **Zero
  endpoints flagged deprecated.**
- `v2/openapi.json`: 83 paths, `POST /create-image-bitforge` → `deprecated=False`. **Zero
  endpoints flagged deprecated.**

There is **no deprecation, no sunset date, and no vendor signal of any kind.** The retirement is
internal policy only, and it is conditional rather than dated —
`PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md` §7: *"Nothing new should be written against it, and
it should be deleted once round 1 of the new look is running on v2."* That is **discouraged,
with a trigger, no date** — not deprecated-with-date.

**The audit's §3 inference holds up behaviourally, which I initially doubted.** It argues from
empty set-difference that v1 and v2 BitForge are one endpoint under two names. They also
*behave* identically: same 3-variant pattern at a fixed seed, same 0.3542 pairwise noise, same
latency to within a second. Migrating BitForge v1 → v2 is a base-URL change, as §3 says.

---

## The tension the columns expose

Stage 2 asks for **≥2 references**. Measured capacity:

- BitForge (v1 **and** v2): **exactly one** `style_image`.
- MCP `pro`: up to **4** — the only surface that can satisfy ≥2. (The brief's "≤8" is
  unreachable anywhere.)

BitForge's second channel is `color_image`, the forced-palette slot — and **this probe forbids
creating a palette**, so that channel is closed by the probe's own terms.

The ≥2 requirement traces to our own art finding, not a platform rule: PIXELLAB-VERIFIED §2.3
records that one reference could not carry both density and value, failing the value floor on
6–7 of 7 blocks until a value plate was added. §2.3 also says, explicitly: *"Never cite it as a
platform constraint — it would wrongly veto `create_image_pro`."*

**Whether it binds here is a judgement for Rafe.** The failure it describes was against a value
floor. This probe has no palette, no value floor, and no lint gate, and Stage 2 asks a narrower
question than round 1 did: *does the arm's treatment hold under conditioning.*

---

## Where each surface stands against the probe's declared terms

| | 24×24 | shading lever | lever measurable | ≥2 refs | s/gen |
|---|---|---|---|---|---|
| v1 BitForge | ✓ | ✓ | ✓ | ✗ (1) | 21.5 |
| **v2 BitForge** | **✓** | **✓** | **✓** | **✗ (1)** | **20.6** |
| MCP `pro` | ✓ | ✗ (`style_copy` only) | ✗ | ✓ (4) | 91–168 |
| MCP `pixflux` | ✗ | ✓ | ✗ | ✗ | ~13 |
| MCP `pixen` | ✓ | ✗ | — | ✗ | ~13 |

**No surface satisfies every declared term.** The freeze is a choice about which term to spend.
