# THE COMPOSITION SPIKE — session report

**Returning under ruling trigger (a): a landing-gate-shaped judgment, Rafe's eye, in §13.1's
scene, on the device. Nothing lands. What is being ruled on is a road.**

Declared before the first tile was composed, not tuned after (LOOP-PROCESS §0.3, §8):

> **TASK** — composed two-plane wall segments built from the wall gauntlet's parts bin,
> rendered in the lit tier-0 corridor on the reference device, for one human question:
> **does a composed wall read as a wall, and does it read as HELD?**
>
> **METHOD** — parts off disk out of the gauntlet ledger; composition authored in a committed
> script; binding overlays authored as MOCKs and marked so; four arms differing by one variable
> each; blind critic before Rafe.
>
> **BAR** — the composed bound arm passes the blind critic unhedged on the wall question and
> the held question. **BUDGET** — 8 critic rounds. Spent below the bar → report what the
> composition could and could not do, with the captures as evidence. Zero API calls; the bin is
> the ledger.

---

## 1. WHAT WAS BUILT

Four arms, each a complete autotile family of 74 tiles, plus a plant:

| arm | top plane | bindings | what it isolates |
|---|---|---|---|
| **boundA** | R4 slab at its native value (lum 125) | MOCK | the composition as briefed |
| **boundB** | the same slab, luminance-matched to the face (lum 96) — DERIVED | MOCK | the strict §6.3 reading |
| **ctrlA** | native | **none** | held vs unheld, native top |
| **ctrlB** | matched | **none** | held vs unheld, matched top |
| **plant** | matched | MOCK + a baked per-course key light | the critic's own control |

Every pair differs by exactly one thing. The floors, the geometry, the rig, the tile size and
the resolution are identical across all five.

### The parts, and what was discarded

| role | part | ledger provenance | rows used | rows discarded, and why |
|---|---|---|---|---|
| front face | `r07_00` | wall gauntlet round 7 | 5–30 | 0–4, its failed cap band — the critic's verdict on it was *"rows 0-4 use the identical greys as the face, so there is no top band at all"* |
| top plane | `r04_08` | wall gauntlet round 4 | 0–28 | 29–31, its baked floor shadow |
| floors | A-VAB, A-HEB, B-KAB, C-GAB | §6.4 probe survivors | whole | — |
| bindings | straps, pins, cramps, lashing, one tag | **MOCK — authored in `compose_walls.py` this session** | — | — |

`r07_08`, `r07_09` and `r04_00` are recorded in `PARTS_MANIFEST.json` as alternate stock and
were not used. **This session made zero API calls.**

**Every pixel in every composed tile is a colour that exists in the parts bin.** Verified:
boundA writes 1006 distinct colours across its 74 tiles and boundB writes 991, and **zero** of
them are absent from the union palette of the parts. Occlusion, iron, rope and tag values are
all drawn from that set. §5 stays PLACEHOLDER; nothing here proposes a palette.

### The composition rule

`DungeonRenderer` computes a 4-bit cardinal mask (bit3=N, bit2=S, bit1=E, bit0=W, set when that
neighbour is wall) and collapses 7/11→3 and 13/14→12. Bible §3 expressed in that mask is one
line:

```
SOUTH BIT CLEAR  ->  floor below  ->  top band + occlusion + FRONT FACE
SOUTH BIT SET    ->  wall below   ->  TOP SURFACE only
```

**This is the thing a single generated tile cannot do**, and it is the round-10 objection
answered structurally: the gauntlet's tile had to carry a cap band whether or not the wall
below it wanted one, so an identical hard-edged cap "stripes the wall every 32 pixels when
stacked". Composed per mask, the band appears only where the wall actually stops.

Geometry is drawn by occlusion and never by highlight (§6.3). Nothing in any tile is
brightened. The face under the overhang is darkened; so is any wall edge that meets floor.

---

## 2. THE HARNESS GAP, AND THE SMALLEST FIX

**`wall_autotile` mapped one tile id per mask.** A corridor edge therefore stamped a single
tile at every cell that mask occurred — a repeat every 32px, the defect the gauntlet's critic
named in every round it reached. A strap repeating on a 32px lattice reads as wallpaper, which
is §7.3 inverted: ornament where structure was asked for. With one tile per mask the held
question could not have been asked honestly.

Fixed at the smallest scope that answers it: a mask may declare a list, and the variant is
picked by `PositionHash(x, y)` exactly as floor roles already are. A scalar entry still resolves
to itself, so every shipped theme loads unchanged.

**Verified by capture, not by assertion** (§13.5, LOOP-PROCESS §4):

| control | plant | differing pixels | result |
|---|---|---:|---|
| 1 — the variants reach the renderer | every mask pinned to one tile id | 11.121% | PASS |
| 2 — the mask-3 entry is the one being read | mask 3 pointed at the FLOOR tiles | 11.717% | PASS |

This harness has been bitten by exactly this shape before: `--tile-size` was echoed into the
log while `TopDownRenderer` drew a hard-coded 24px grid regardless. A parameter that changed
only the log would be decorative and would have to be labelled so or deleted.

---

## 3. THE FINDING THE FIRST CAPTURE FORCED

**Bible §3's two planes do not, on their own, separate wall from floor.**

The first lit capture — preserved as `evidence/finding_before_edge_occlusion.png`, produced by
commit `339ec10` — is the composition with §3 and nothing else. It shows two things at once:

1. In a one-tile-wide north–south corridor **every** flanking wall cell has wall to its south,
   so under §3's rule no front face appears anywhere along its length. The player walks between
   two fields of wall-top.
2. Those fields sat at luminance 96 beside a lit floor at 122 with **no boundary of any kind
   between them**. Which cells were solid was not readable.

The shipped Oryx placeholder tiles this renderer's mask table was fitted to already answer
that: tile 184 carries a dark band along its bottom edge, 187 dark columns down both sides. The
engine's tile grammar assumes an **occluded edge wherever wall meets floor**, and §3 does not
supply one. Adding it is what makes the current captures readable.

⚠ **This is flagged for the human gate, not decided here.** A dark edge on every wall/floor
boundary is a second linear system, and §12.1 reserves that job for straps, bands and tags. It
is occlusion rather than an outline — it sits on the wall's own edge, only where floor is
adjacent, and is direction-agnostic under any azimuth — but the tension is real and the ruling
is Rafe's.

**A second, smaller finding on the same axis.** The value-matched arm (B) separates from the
floor *better* than the native arm (A), which is the opposite of what the brief's ordering
suggests. The §6.4 survivor floors sit at luminance 122–132; R4's native slab sits at 125,
i.e. on top of them. Matching the top plane down to the face's 96 buys 26 points of separation
from the floor as a side effect of a change made for §6.3 reasons.

---

## 4. WHAT THE CORRIDOR CAN AND CANNOT ASK

Stated because it bounds every verdict below, mine and the critic's.

The review corridor is one tile wide. Across its whole extent the wall masks that occur are:

| effective mask | cells | what it renders |
|---|---:|---|
| 12 (vertical run) | 28 | top surface only |
| 15 + diagonals (interior) | 273 | top surface only |
| 3 (horizontal run) | 22 | **top band + front face** |
| 5, 6, 9, 10 (junction corners) | 1 each | corner |

**So roughly 6% of the wall cells in the scene can show a front face at all**, and they are
confined to two rows either side of the east–west branch. The corridor is an excellent floor
instrument and a thin wall instrument. A verdict from it about the *face* rests on a narrow
strip; a verdict about the *top plane* rests on nearly everything.

This is not a defect introduced by the composition — it follows from §3's rule meeting a
one-wide north–south corridor — but it means **the scene under-tests exactly the plane the
gauntlet was trying and failing to generate.** If the road is taken, the review scene needs an
east–west emphasis or a chamber before a face verdict is worth much. Named here rather than
discovered later.

---

## 5. THE BLIND CRITIC

A fresh `claude -p` per round, cwd outside the repo, five lit captures under anonymous codes,
never the bible (LOOP-PROCESS §3). Verbatim transcripts and parsed verdicts in
`evidence/critic/`.

**Blindness, stated precisely rather than claimed.** The seat runs with cwd in a scratch
directory containing only the five PNGs; it has no project `CLAUDE.md`, no memory directory, no
ledger, and no bible. It was launched with `--allowedTools Read` but demonstrably wrote files
(its own zooms, brightness passes and difference images), so tool restriction did not hold and
the blindness rests on cwd and on the process having no reason to look elsewhere — not on a
sandbox. Recorded because the gauntlet's report claimed the stronger version.

### Round 1 — 0 passes of 5. Plant CAUGHT.

| code | arm | cull | verdict |
|---|---|---|---|
| C1 | boundB | none | FAIL — *"the walls have no mass and the ironmongery is stickers laid on wallpaper"* |
| C2 | ctrlB | none | FAIL — *"a bare, evenly-pointed brick field with zero fixings"* |
| C3 | boundA | **cannot-read** | FAIL — *"the wall value has been raised to floor value ... 8 grey levels against a texture noise of ~34, and in the unlit zone it inverts"* |
| C4 | **plant** | none | FAIL — *"the most obviously planted defect in the set"* |
| C5 | ctrlA | **cannot-read** | FAIL — *"worst separation in the set ... 5.8 levels above wall when lit and 1.1 levels below it when unlit"* |

**The plant control held, and how it held is itself the finding.** The seat failed the plant and
named it as planted, so the round stands. But **it did not tick the `key-light` cull.** It read
the baked per-course light/dark banding — repeated across eleven tiles of face — as *continuous
horizontal timbers*: "dead-straight, unbroken, uniform-width horizontal lines ... with no ends,
no joints, no scarfs, no sag and no fixings ... a ruled stripe, not a ledger."

That extends the gauntlet's §5 finding by one term. The gauntlet found that at 32px the
vocabulary for *describe geometry with value* and the vocabulary for *bake a key light* are the
same vocabulary. **They are also the same vocabulary as *draw a timber band*.** A baked light
laid across a coursed face does not read as light at all — it reads as hardware. Anything
built to detect key-light by asking a critic will, at this canvas, get an object report back.

### What the round found that this session had not

1. **The two-plane composition delivered no perceived thickness.** Q4, on both composed arms:
   *"No — the wall is coplanar with the floor, with no cap, no side face, no edge shadow and no
   occlusion."* This is §4's corridor problem arriving at the eye: with ~6% of wall cells able
   to show a face, a correct §3 composition still reads as a flat brick field.
2. **The bindings failed the held question, precisely.** *"Each sits on top of the brick inside
   a hard black keyline, none bears on anything, none bridges a joint or a crack, and no pin
   passes into the stone."* Round 1's symmetric contact shadow — drawn on both sides of every
   strap in the name of direction-agnostic occlusion — **is a closed keyline**, which is the
   §12.1 sticker read arriving by the back door. It also swallowed the mortar courses running
   up to the strap, so nothing could be seen to be crossed.
3. **The review corridor renders a mirrored dungeon.** *"The left half is a near-exact mirror of
   the right (MAD 6.1 vs 31.7 unmirrored), so every crack and every batten has a twin."* The
   scene is deliberately symmetric about the player's column; `PositionHash` is
   `7919x + 104729y`, so at four variants the index is `(3x + y) mod 4` and mirrored cells
   collide whenever their offset is even. **Half the art is a reflection of the other half.**
   This is a property of the harness, not of this session's tiles, and every capture taken in
   this corridor — §6.4's included — carries it.
4. **The §6.4 survivor floors were culled by a blind seat, in this session's incidental
   evidence.** *"the square-in-square medallion stamped identically at the centre of every
   corridor tile"* and *"the saturated yellow-green vegetation tufts ... the only high-chroma
   pixels in the dungeon ... overgrowth in a place that has no light and no weather."* Not this
   session's to fix, and reported rather than acted on, but it bears on STOP 1's curation.

### Two flip-list items were REFUSED

- *"drop a 2px hard-edged occlusion shadow from that cap onto the adjoining floor tile"* — a
  baked drop shadow in the asset, which §6.3 forbids outright: *the asset never grounds itself;
  the engine or a composited blob grounds it per context.* `FloorComposer` Pass 2 already
  darkens wall-adjacent floor.
- *"a colour one step lighter and one step desaturated"* for the cap band — a highlight. The cap
  is delivered by material change and occlusion instead.

**This is the second time a critic flip list has asked for a §6.3 violation.** The gauntlet's
round-7 list asked for a 1px chamfer per course and its own round 8 then culled three
candidates for `key-light`. A flip list is a reaction, not a spec, and executing one literally
is how the last loop manufactured the defect it was trying to avoid.

### Round 2 — the flip list applied

Changes, each traceable to a charge above: keyline removed and occlusion moved under the lip
only; elements placed on joints found in the stone, with driven pins chipping the brick;
variants 4 → 7 (mirror collisions from every 2nd tile to every 7th, run repeat 4 → 7); slab
variants no longer rolled in x, so the occluded boundary is the only line that means
wall-meets-floor; edge occlusion deepened to three steps; top part swapped `r04_08` → `r04_00`,
killing the branching crack the seat called "bird tracks" — a parts choice out of the same bin,
not a redraw.

*(Round 2 verdict below.)*

---

## 6. EVIDENCE

| what | where |
|---|---|
| the composite script | `compose_walls.py` |
| parts manifest, every provenance or MOCK label | `PARTS_MANIFEST.json` |
| 12 captures, each with its rig log | `evidence/*.png`, `evidence/*.log` |
| capture manifest with commit + per-capture sha256 | `evidence/manifest.json` |
| the pre-fix capture that forced §3 | `evidence/finding_before_edge_occlusion.png` + `.txt` |
| positive controls for the variant fix | `evidence/controls/` |
| blind critic transcript + parsed verdicts | `evidence/critic/` |
| side-by-side pairs for the eye | `evidence/sheets/` |
| segments assembled outside the engine | `segments/` |

Every capture was produced under one identical rig, echoed by the engine into its own log:
`ambient=1a1a22 light=ffb066 energy=1.6 radius_tiles=5.5 tile=32x32` — **all values UNDERIVED,
§6.2 and §4.3 PLACEHOLDER**, carried in every log so no capture can circulate without them.

---

## 7. REFUSALS HELD

- **Did not generate.** Zero API calls; the bin is the ledger.
- **Did not promote anything to corpus.** `MOCK` is in every composed filename; nothing is
  offered to §13.1.
- **Did not polish the overlays beyond the held question.** They are crude on purpose.
- **Did not instrument a register clause** (§13.4). There is no held-ness score. The critic
  renders prose and Rafe renders the verdict.
- **Did not conclude.** The road ruling is Rafe's, taken with the tiles-pro audit beside this.
