# The composition spike

**A mock, not asset production. Nothing here lands, ratifies, or enters the corpus.**

The wall gauntlet (`tools/pixellab/wall_gauntlet/FINDING.md`) spent 100 generations across ten
rounds and passed nothing. Reading its ledger, the pattern is sharp: **everything that failed
was a relationship between parts** — face-to-top, cap-to-course, strap-to-strapped — **and
everything that succeeded was a part**. Coursed masonry material: fine. Flat weathered slab
material: fine. A wall: never.

So this directory tests the road that points at. It treats the generator as a materials
supplier rather than a mason: stone comes off disk out of the gauntlet ledger, the composition
is authored here, and the result goes through the tier-0 rig into the lit corridor on device
for one human question — **does a composed wall read as a wall, and does it read as HELD?**

**This session made zero API calls.** Every stone pixel has a round and a candidate id in
`PARTS_MANIFEST.json`. The binding overlays are programmer-art mocks authored in
`compose_walls.py`, marked `MOCK` in every filename, and are never corpus.

---

**The finding is in `SPIKE.md`. Read that first; this file is how to run the thing.**

## What is in here

| Path | What |
|---|---|
| `compose_walls.py` | Builds the arms from ledger parts. The whole composition lives here. |
| `capture_spike.py` | Ten lit/unlit captures through the tier-0 rig. |
| `control_wall_variants.py` | Positive controls for the wall-variant fix (below). |
| `run_critic.py` | The blind critic seat — fresh `claude -p`, cwd outside the repo. |
| `critic_prompt.txt` | Fiction, tone, questions. Never the bible (LOOP-PROCESS §3.2). |
| `make_sheets.py` | Side-by-side pairs for the human gate. |
| `PARTS_MANIFEST.json` | Every part's ledger provenance, or its MOCK label. |
| `SPIKE.md` | **The session report and the findings.** |
| `verify_palette.py` | Checks that no composed pixel invents a colour. |
| `measure_field.py` | Measures repetition in the RENDERED field, to check the seat's charge. |
| `round_table.py` | The six rounds, read out of the evidence. |
| `segments/` | Straight run, corner, south-facing run, assembled outside the engine. |
| `evidence/` | Captures + rig logs + critic transcripts + control results. |

```bash
python3 tools/composition_spike/compose_walls.py          # build the arms
/Applications/Godot_mono.app/Contents/MacOS/Godot --headless --path . --import
python3 tools/composition_spike/control_wall_variants.py  # the controls must pass first
python3 tools/composition_spike/capture_spike.py          # the captures
python3 tools/composition_spike/run_critic.py 1           # the loop gate
python3 tools/composition_spike/make_sheets.py            # pairs for the eye
python3 tools/composition_spike/verify_palette.py         # no invented colour
python3 tools/composition_spike/measure_field.py          # the repetition charge, measured
python3 tools/composition_spike/round_table.py            # the rounds in one table

TIER0_THEME=res://src/Presentation/assets/composition_spike/tile_themes_boundB.yaml \
  tools/tier0_harness/build_review_app.sh                 # onto the device
```

---

## The composition, in one rule

`DungeonRenderer` computes a 4-bit cardinal mask — bit3(8)=N, bit2(4)=S, bit1(2)=E, bit0(1)=W,
set when that neighbour is **wall** — then collapses 7/11 to 3 and 13/14 to 12. Bible §3's
two-plane rule expressed in that mask is one line:

```
SOUTH BIT CLEAR  ->  floor below  ->  top band + occlusion + FRONT FACE
SOUTH BIT SET    ->  wall below   ->  TOP SURFACE only
```

This is the thing a single generated tile cannot do. The gauntlet's tile had to carry a cap
band whether or not the wall below it wanted one, which is exactly the round-10 objection that
an identical hard-edged cap "stripes the wall every 32 pixels when stacked". Composed per
mask, the band appears only where the wall actually stops.

Geometry is drawn by **occlusion, never by highlight** (§6.3). The top plane is never
brightened; the face under the overhang is darkened, and so is any wall edge that meets floor.
Every pixel is snapped to the union of the parts' own colours, so nothing here proposes a
palette (§5 is PLACEHOLDER and stays that way).

---

## The harness gap, and the smallest fix

`wall_autotile` mapped **one tile id per mask**. A corridor edge therefore stamped a single
tile at every cell that mask occurred — a repeat every 32px, which is the defect the gauntlet's
critic named in every round it reached, and which would have made a strap read as wallpaper
rather than as a repair.

Fixed at the smallest scope that answers it: a mask may now declare a list, and the variant is
chosen by `PositionHash(x, y)` exactly as floor roles already are. A scalar entry still
resolves to itself, so every shipped theme loads unchanged and no existing capture moves.

**And the first version of that fix was incomplete, which is the more useful half of the story.**
It made `wall_autotile` list-valued and left `wall_diagonal.interior_fill` a scalar — and
`interior_fill` is **267 of the ~300 wall cells** in this corridor. The fix varied the visible 6%
of the mass and left the other 94% stamping a single PNG. Two full critic rounds were spent
judging one tile before a blind seat found it. Both roles now take lists.

**Verified the way the tier-0 harness verifies its parameters, not by assertion** (§13.5,
LOOP-PROCESS §4). `control_wall_variants.py` captures the real scene twice and requires the
pixels to differ:

| Control | Plant | Result |
|---|---|---|
| 1 — variants reach the renderer | every mask pinned to one tile id | 11.999% differ — PASS |
| 2 — the mask-3 entry is the one read | mask 3 pointed at the FLOOR tiles | 11.689% differ — PASS |
| 3 — interior_fill's variants reach it | interior_fill pinned to one tile id | 32.641% differ — PASS |

**Control 3 exists because control 1 could not have failed for the bug that actually happened.**
Control 1's regex pins integer-keyed autotile entries; `interior_fill` is a word-keyed role in a
different block, which is exactly how the hole survived a passing control. A control that cannot
fail for the bug in front of it is not a control.

This shape of bug has bitten this harness before: `--tile-size` was echoed into the log while
`TopDownRenderer` drew a hard-coded 24px grid regardless. A parameter that changed only the log
would be decorative and would have to be labelled so or deleted.

---

## The finding the first capture forced

The first lit capture is why `compose_walls.py` emits a tile per mask rather than one face and
one slab. **§3's two planes do not, on their own, separate wall from floor.** A lit wall top at
luminance 96 sat beside a lit floor at 122 with no boundary between them, and in a one-tile-wide
north–south corridor *every* flanking wall cell has wall to its south — so no front face appears
anywhere along its length. The corridor could not be read.

The shipped Oryx placeholder tiles this renderer's mask table was fitted to already answer
that: 184 carries a dark band along its bottom edge, 187 dark columns down both sides. The
engine's grammar expects an **occluded edge wherever wall meets floor**, and §3 does not supply
one.

⚠ **Flagged for the human gate, not decided here.** A dark edge on every wall/floor boundary is
a second linear system, and §12.1 reserves that job for straps, bands and tags. It is occlusion
rather than an outline — it sits on the wall's own edge, only where floor is adjacent, and is
direction-agnostic — but the tension is real and it is Rafe's to rule on.

---

## What this deliberately does not do

- It does not generate. Zero API calls; the bin is the ledger.
- It does not promote any composite or mock to corpus. `MOCK` is in every filename.
- It does not score, lint or census anything, and it instruments no register clause (§13.4).
- It does not conclude. The road ruling is Rafe's, taken with the tiles-pro audit beside it.
