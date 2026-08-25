# Archived — the Oryx-conformance art track (closed 2026-08)

> **Nothing in this folder is in force.** Every document here states rules, thresholds, or
> gates that were struck when the track closed. If you are doing art work, the live document
> is [`docs/ART-BIBLE-v0.md`](../../ART-BIBLE-v0.md) and it is the *only* one.

This folder exists so the track is disposed of explicitly rather than quietly. A session
reading the repo could otherwise pick these up and work to a retired standard in good faith,
which is exactly what these files are shaped to make easy — they are detailed, confident, and
were correct when written.

## Why the track closed

It measured conformance against a fixed external corpus — the Oryx 16-Bit Fantasy library —
that nobody here wrote. Every drift was a defect, no rule generalised, and no instrument in
the stack ever asked *does this look like Yarl?*, only *does this match Oryx?* There was no
rule that could tell you what an Oryx-conformant version of an object Oryx never drew should
look like. **The lesson was not that strictness was wrong; it was that the target belonged to
someone else.** See ART-BIBLE v0 §1.2 (the generative test) and §1.3 (the named trap).

The track was **concluded, not failed.** It reached 74 of 80 tracked assets conformant. Two of
its findings survive on their own merits and are re-adopted in the new bible rather than
inherited: the two-plane perspective rule (§3) and *names itself at 1×* (§12).

## What is retained, and what is struck

The roadmap ruling that closed the track (`docs/ROADMAP_release_2026-07.md`, Track A,
2026-08) draws this line explicitly, and it matters more than the folder boundary does:

**Retained and reusable by the new art thread** — the art lint (Part A machine checks plus
the F1–F3 structural-fineness family), `ReviewSceneBuilder` and the in-scene review
protocol, the generated-assets manifest, and the acceptance/capture harness. That code is
on `main` and is not archived. **Struck** — the Oryx target itself: the thresholds derived
from it, the palette membership test against it, and the sticker-test verdict criterion.

So a document being in this folder does **not** mean the machinery it describes is dead. It
means the *bar* it sets is no longer the bar. Two of the files below are archived specs for
tooling that still runs, and their banners say so.

## What is here

| File | Was | Superseded by |
|---|---|---|
| `art_bible.md` | `docs/art_bible.md` — the Oryx art bible, adopted 2026-07-16 (PR #4) | `docs/ART-BIBLE-v0.md` in full |
| `art-lint-spec.md` | `config/rubric/art-lint-spec.md` — machine conformance gate, thresholds set to observed Oryx values | ART-BIBLE v0 §5.1 palette gate (same zero-tolerance mechanism, in-repo target) — **not yet built**, see §15. **The code is retained infrastructure** (Part A checks + F1–F3 fineness); only the Oryx bar is struck. |
| `art_test_scene_spec_v2.md` | `docs/art_test_scene_spec_v2.md` — the sticker-test acceptance scene | ART-BIBLE v0 §13.1 — in-scene review not merely survives but becomes the **only** approval. **`ReviewSceneBuilder`, the review protocol, and the capture harness are retained infrastructure**; only the sticker-test verdict criterion is struck. |
| `art-lint-gate-package-GATE.md` | `tools/art_lint/gate_package/GATE.md` — Track A burn-down at its high-water mark | Nothing. The bar it reports against no longer exists. |
| `reference_tileset_research.md` | `docs/reference_tileset_research.md` — the research that chose Oryx as the baseline | Nothing. It is the record of the decision the new bible reverses. |
| `RETRO_DIFFUSION_WALKTHROUGH.md` | `tools/retrodiffusion/` — generating Oryx-style sprites via Retro Diffusion | Retired twice: RD superseded by PixelLab (Apr 2026), Oryx target struck (Aug 2026). Tooling is re-decided at ART-BIBLE v0 §14, Phase 4. |
| `ASEPRITE_SETUP_WALKTHROUGH.md` | `tools/retrodiffusion/` — hand-edit layer for closing the gap to Oryx conformance | As above. The gap it closed is no longer the thing measured. |
| `retrodiffusion-review-process.md` | `tools/retrodiffusion/` — RD Pro billing/model-tier finding | Nothing. The generator is out of the pipeline. |

## What deliberately did *not* move

- **`tools/art_lint/` (the code)** — the linter still runs and is still useful for mechanical
  checks, but its spec is archived here and its thresholds are Oryx-derived. It is **not a
  gate** until ART-BIBLE v0 §5.1 is built against an in-repo palette. It was never wired into
  CI, so nothing was unblocked by archiving the spec.
- **`tools/pixellab/`** — PixelLab is a live tool, but its docs are written for Oryx style
  matching. They carry an in-place notice; generation tooling is re-decided at Phase 4.
- **`config/tilesets/16bf_sprite_notes.md`** — factual file-format notes about sheets still
  present in the repo. Not art direction.
- **`docs/2d-vs-iso.md`** — its conclusion (top-down over isometric) is independent of the
  Oryx question and still stands.
- **Source-comment citations** of `art_test_scene_spec_v2.md` and `art_bible.md` in
  `src/Logic/Core/`, `src/Presentation/Main.cs`, `tools/Harness/`, and `tools/art_lint/*.py`
  are left as-is. They are provenance for code that still exists, and they now point at
  documents that announce their own retirement.
