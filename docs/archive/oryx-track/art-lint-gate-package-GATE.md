> # ⛔ RETIRED — 2026-08-24
>
> **This document is part of the closed Oryx-conformance art track. It is superseded by
> [`docs/ART-BIBLE-v0.md`](../../ART-BIBLE-v0.md).**
>
> **Why the track closed:** this package is the conformance burn-down at its high-water mark — 74 of 80 assets conformant — and the track was closed anyway, concluded rather than failed (ART-BIBLE v0 revision history). The conformance split it reports measures a bar that no longer exists.
>
> Kept for the record, not for reference. **Nothing below is in force.** No rule, threshold, palette, or gate in this file is a live standard, and no asset should be judged against it.

---

# Track A — Gate Package

Prepared for Rafe. Everything mechanical in the Track A art conformance burn-down is done;
what remains are decisions about how the art **looks** — the human gate. This package holds the
evidence and the exact manifest edits each verdict would produce, so a decision is a one-line
apply, not a re-investigation.

## Final conformance split (80 tracked generated assets)

- **74 conformant** — all landed and lint-clean-or-WARN.
- **6 nonconformant**, in two groups:
  - **3 parked by rubric preference** (awaiting sticker verdict): anvil `world_5001`,
    armor_stand `world_5002`, club `items_4001`.
  - **3 unwired banked reserve** (awaiting exempt-or-delete ruling): items `4002` / `4003` /
    `4004`, `game_key: null`, not used by any live key.

Verifier: `tools/art_lint/reports/burndown3_reaudit.csv` — full manifest, 80/80, the only six
FAIL rows are these six files, each carrying a manifest note.

## Scene evidence

`scene_full.png` + `scene_crop1_smithy_cluster.png` / `scene_crop2_chest_key_items.png` /
`scene_crop3_worn_floor.png` are the last verified render of the acceptance scene (2026-08-02),
which already includes all five landed heraldic murals, the rock/mushroom/water_barrel picks,
and the three parked originals in place. **No live-art pixel has changed since that capture**
(this run landed no new sprites — the club outline-repair below is a candidate, not a landing),
so it is the current render.

> ⚠️ **Capture tooling is currently broken on `main` — needs a non-art fix (not mine to make).**
> `project.godot` sets `project/assembly_name="CatacombsOfYarl"` (commit 3994acd,
> "align dotnet assembly_name with committed solution"), but the built assembly is
> `CatacombsOfYarl.Presentation` (`<AssemblyName>` in `CatacombsOfYarl.Presentation.csproj`).
> The names must match for Godot to load the C# assembly; they don't, so the `--art-scene-capture`
> boot path (and the game itself) can't run. With `assembly_name` temporarily corrected the boot
> gets further but still hangs at startup under the rebased Godot/.NET 4.7 SDK bump. Both the
> `project.godot` line and the SDK config are outside the art scope and forbidden for this task,
> so fresh captures + a fresh pixel-identity self-test could not be regenerated this run. The
> committed determinism self-test from the unchanged render passed byte-identical
> (`tools/art_lint/scene_evidence/pixel_identity_comparison.txt`, sha256 8074a7e7…).
> **Recommended fix: set `project/assembly_name="CatacombsOfYarl.Presentation"` (or rename the
> assembly to match), then re-run `tools/art_lint/capture_scene.py`.**

---

## Decision 1 — Sticker verdict on the three parked originals

anvil (5001), armor_stand (5002), club (4001) are the original Retro-Diffusion sprites. They
were parked because no conforming candidate (fresh-generated or bank) beat the live art on the
squint/sticker read, so keeping the original was judged the lesser evil vs. a downgrade. They
remain machine-nonconformant:

| file | A1 off-palette | A4 colors | A5 near-pairs | A6 outline |
|---|---|---|---|---|
| anvil 5001 | 253 | 23 (FAIL) | 8 (FAIL) | 0.45 (WARN) |
| armor_stand 5002 | 172 | 26 (FAIL) | 7 (WARN) | 0.25 (WARN) |
| club 4001 | 48 | 15 (WARN) | 4 (WARN) | 0.29 (FAIL) |

The question is the **sticker test** (arm's length, can they be told from canon?) on the three
originals as they render in `scene_crop1_smithy_cluster.png` (anvil + armor_stand) and in-hand
(club).

- **If ACCEPT-AS-IS** (they pass the sticker test despite the machine flags), manifest edit per
  file: add `"lint_exemptions"` covering the failing checks and set
  `"conformance_status": "accepted"`, e.g. for anvil 5001:
  ```json
  "conformance_status": "accepted",
  "lint_exemptions": ["A1_palette", "A4_color_budget", "A5_near_colors", "A6_outline"],
  "accepted_note": "accepted-as-is at gate review 2026-08; original reads correctly, no candidate improved it"
  ```
  (armor_stand 5002: same minus A6; club 4001: A4/A5/A6 — but see Decision 2, which may supersede.)
- **If REJECT** (they fail the sticker test), they stay nonconformant and go back to the
  generation queue with a note; no manifest change now.

## Decision 2 — Optional club outline-repair adoption

An outline-repair pass (`tools/art_lint/outline_repair.py`) traces the sprite's own darkest ramp
color onto the full silhouette boundary. Applied to the best burndown3 club candidate (seed 5),
it produces a sprite that **passes every machine check** — A6 0.588 → 1.0, A4 6 → 5 colors, A5 0
pairs, A1/A2/A3 green — with no design change beyond the one-pixel edge. See
`club_outline_repair_option.png` (live | raw best candidate | repaired).

This is offered as an **option**, not a landing — club stays parked until you rule.

- **If ADOPT**: land `tools/art_lint/candidates/burndown3/club_outline_repaired/club_s5_outline_repaired.png`
  → `src/Presentation/assets/sprites_16bf/items_16x16/oryx_16bit_fantasy_items_4001.png`, then:
  ```json
  "conformance_status": "conformant",
  "route": "pixellab_regen_locked+outline_repair",
  "pick_source": "burndown3 club seed 5, outline-repair pass (A6 1.0, A4 5c, A5 0)"
  ```
  and drop the `rubric_override_note`. This makes club conformant and would move the split to
  75/5. (If you also accept the original at Decision 1, Decision 2 is moot for club — pick one.)
- **If DECLINE**: club stays parked; repaired candidate remains available in the bank.

---

## Also pending (not a gate decision, just flagged) — banked items 4002–4004

Three Retro-Diffusion item sprites banked at `items_4002/4003/4004`, `game_key: null`, wired to
nothing. They carry `gate_note: "unwired — pending exempt-or-delete ruling"`. They are not part
of the parked-six or mural scope. When you're ready: either exempt-and-keep (as future reserve)
or delete. Left untouched here per the "do not decide" boundary.

---

## Summary of manifest state as shipped

- 74 conformant / 6 nonconformant, reconciled to 80.
- 5 heraldic murals landed (route `pixellab_bank`), pixel-matching their named bank files.
- water_barrel 5084/5085 landed (route `pixellab_regen_locked`).
- 3 parked originals carry `rubric_override_note`.
- 3 banked reserves carry `gate_note`.
