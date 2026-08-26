# §6.4 PROBE — PARK STATE at STOP 1

`ART-LOOP-PROCESS-v0.md` §7. A track that stops writes down which state it stopped in.

**State: PREPARED, NOT GENERATED — for everything past STOP 1.**
Stage 1 is *generated and complete*. Stage 2, Precondition B and Stage 3 are staged and
deliberately not spent on, because STOP 1 is a mandatory halt and the work past it depends on
a human pick that has not happened. Nothing here is *finalised* — the probe has not ruled.

---

## What this seat refused, declared before the run and honoured

Recorded per §7: *refusals are declared before the run, not after.* These came from the
session brief and were fixed before the first generation.

| Refusal | Held? |
|---|---|
| Does not amend the kill criterion, the band, or the canvas after Stage 1 begins | **held** — nothing was amended; the framing problem found mid-batch was reported, not corrected into the arms |
| Does not promote a reference Rafe did not pick | **held** — no survivor exists; this seat picked nothing |
| Does not treat any probe output as a game candidate | **held** — every sheet carries `PROBE REFERENCE — NOT RATIFIED` |
| Does not create a palette, set `color_image`, ratify anything, or begin tier 1 | **held** — `color_image` is never set anywhere in `v2_bitforge.py`'s callers |
| Does not switch surfaces, mix seats across references, or route through `client_compat.generate_image_bitforge` | **held** — one surface, v2 HTTP BitForge, every call; `client_compat` is not imported by any probe file |
| Does not compute any effort ratio before every arm's batch is complete | **held** — no ratio is computed anywhere in this session, and it *cannot* be until STOP 1 supplies the denominator |

**The frozen instrument, recorded:** v2 HTTP `POST https://api.pixellab.ai/v2/create-image-bitforge`.
One surface for the entire probe. Chosen on the surface audit's evidence, not on preference.

---

## Stage 1 — GENERATED

Complete. 120 declared, 120 run, batch ran to completion with no early stopping on any arm.
Counts, ledger and contact sheets are in `STOP1-REPORT.md` and `stage1/`.

## STOP 1 — OPEN, awaiting Rafe

Blocked on one thing only: **Rafe picks 2–4 survivors per arm × subject from the six contact
sheets.** This seat cannot proceed past it and does not.

## Stage 2 — PREPARED, NOT GENERATED

Two seats per arm, each conditioned on a *different* STOP 1 survivor, each running half the
arm's budget. Cannot start: BitForge takes exactly one `style_image`, so a seat *is* a
survivor, and there are no survivors until STOP 1 closes.

Staged and ready: `v2_bitforge.py` hand-encodes `Base64Image` (the wrapper defect that would
have blocked this is ticketed as #140 and routed around, not depended on). The size-match rule
is a hard server 500, so every survivor must be authored/selected at 32×32 — which they are,
natively.

## Precondition B — PREPARED, NOT GENERATED. Owed BEFORE Stage 3.

`TopDownRenderer.TileWidth` is a hard-coded `24` — a known PLACEHOLDER violation, already
reported in `tools/tier0_harness/README.md` as a known limit. Owed as **its own small PR**
between Stage 2 and Stage 3: parameterise tile size, render the harness at 32, and re-run the
tier-0 positive controls green **at 32** — each shown able to fail, not assumed still valid
from the 24px run.

⚠ **Discrepancy to settle in that PR:** the brief and the harness README both say *four*
positive controls. There are **five** (`determinism`, `lighting`, `scene`, `device`,
`junction`). All five ran green at 24 this session; all five are owed green at 32.

## Stage 3 — PREPARED, NOT GENERATED

`capture_probe_arms.py` exists and is wired to the three arm directories in
`harness_config.yaml`. It does not run until Precondition B is merged and green: a harness
proven only at a different tile size is not the instrument this probe declared.

## STOP 2 — NOT REACHED

The ruling is Rafe's, on the device, unlabelled as to arm. This session ends at STOP 1 and
does not forecast it.

---

## Live carry-forward

1. **The framing split is the yield ceiling for all three arms.** Uniform across arms, so it
   does not confound the comparison, but it caps every arm's yield equally and will cap
   Stage 2's. `coverage_percentage` is measured against it in `diag_framing/` — evidence for a
   ruling at STOP 1, deliberately not applied to any arm.
2. **The negative description is weakly honoured.** Isometric slabs, moss, and baked outlines
   all appear in output that named each of them as excluded. Recorded as a surface property,
   not worked around.
3. **#140** — `client_compat.generate_image_bitforge` cannot pass a `style_image`. Ticketed,
   routed around, not fixed here.
