# ⚠️ This linter has no live spec — 2026-08-24

**`art_lint.py` still runs, and its results are no longer a gate.**

The spec it implements — `config/rubric/art-lint-spec.md` — was archived when the
Oryx-conformance art track closed. It now lives, with a RETIRED banner, at
[`docs/archive/oryx-track/art-lint-spec.md`](../../docs/archive/oryx-track/art-lint-spec.md).

## What that means in practice

- **Every threshold in this directory is an observed Oryx value.** Palette membership checks
  against `config/art/oryx_master_palette.json`; the outline, colour-count, and speckle
  baselines were all measured against the Oryx library in Jul 2026. They measure conformance
  to a corpus that is no longer the target.
- **A FAIL here does not block anything, and a PASS approves nothing.** Do not cite this
  linter as acceptance evidence and do not "fix" an asset to satisfy it.
- The machine checks that *are* mechanical rather than Oryx-specific — pixel-identity
  determinism (`verify_capture_determinism.py`), scene capture, manifest building — remain
  useful as tools.

This was never wired into CI, so archiving the spec unblocked nothing and broke nothing.

**This directory is explicitly retained infrastructure.** The roadmap ruling that closed
Track A (`docs/ROADMAP_release_2026-07.md`) keeps the Part A machine checks and the F1–F3
structural-fineness family as reusable by the new art thread. Archiving the spec retired the
**bar**, not the code. Do not delete this tooling.

## What replaces it

[`docs/ART-BIBLE-v0.md`](../../docs/ART-BIBLE-v0.md) §5.1 specifies the successor palette
gate: the same zero-off-palette-pixels mechanism, against a palette this repo owns rather
than one it borrowed. **It is not built yet** — §15 audits nine of ten clauses as
uninstrumented, and says so deliberately. Until it exists, art acceptance is the human
in-scene gate (§13.1–§13.2), not a script.

Note also §13.5: *no instrument's pass counts until it has demonstrated it can fail.* If you
build the successor, that applies to it.

## `gate_package/`

The PNGs in `gate_package/` are the captured evidence for the Track A human gate. The document
that read them, `GATE.md`, is archived at
[`docs/archive/oryx-track/art-lint-gate-package-GATE.md`](../../docs/archive/oryx-track/art-lint-gate-package-GATE.md).
The images are kept as a record of what the track actually produced; the verdicts they were
prepared for are moot.
