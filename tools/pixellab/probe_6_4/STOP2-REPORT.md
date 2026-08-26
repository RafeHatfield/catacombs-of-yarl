# §6.4 PROBE — STOP 2 DELIVERY

Everything the STOP 1 ruling asked for, in its order. **The ruling at STOP 2 is Rafe's and this
seat does not pre-empt it.** §6.3 is ratified or retired on the device, against the frozen
criterion, and nothing below re-tunes that criterion.

Run 2026-08-25/26, branch `art/probe-6.4-stage1`.

---

## 1. SURVIVORS PROMOTED

Four, exactly as picked, from the floor sheets treated as one pool. Marked
`PROBE REFERENCE — NOT RATIFIED` in `survivors/MANIFEST.json`. This seat picked none of them and
promoted nothing else.

| code | from | Stage 1 source |
|---|---|---|
| A-VAB | arm A | `A/floor/A_floor_17.png` |
| A-HEB | arm A | `A/floor/A_floor_16.png` |
| B-KAB | arm B | `B/floor/B_floor_18.png` |
| C-GAB | arm C | `C/floor/C_floor_16.png` |

Arm-of-origin is recorded even though the pool was curated blind to it: the arms may yet differ
somewhere this probe has not looked, and discarding the provenance would make that
unrecoverable. **Wall sheets: zero picks**, as ruled.

---

## 2. WALL MICRO-PROBE — the bar passed, and the bar was the wrong instrument

Bar declared in `wall_microprobe.py` **before the run**, per LOOP-PROCESS §8, in three parts:
surface-not-object, full-frame, orthogonal. Threshold ≥5 of 20.

### Against the bar as declared: 20/20. Four times the threshold.

**The framing hypothesis is confirmed outright.** Stage 1's wall subject failed 59 of 60 by
producing objects — chests, doors, sarcophagi. Surface framing took that to **zero**. Not one of
the 20 is an object on a background field, and not one is isometric. Framing is a real,
controllable dial on this surface, and knowing that is worth the 20 generations on its own.

### And every one of the 20 is undifferentiated noise.

No coursing. No mortar lines. No timber, no lashings, no driven pins, no straps. §12's *names
itself at 1×* fails immediately; §7.1's *everything is held* has nothing to hold. These are
speckle fields the colour of stone.

**I am not re-tuning the bar** — it was declared at 5 and it was cleared at 20, and LOOP-PROCESS
§8 says the bar is never re-tuned after the answer is seen. Both facts are reported and the call
is Rafe's. What I will say plainly is that my bar was badly drawn: I wrote three framing clauses
and explicitly excluded "reads as a wall" as too close to register, and framing turned out to be
the easy half.

**Internal control on the cause, and it is clean.** Stage 1's floor subject used *identical*
parameters — `low detail`, `lineless`, `high top-down`, same canvas, same surface — and produced
legible masonry. So the noise is attributable to the surface-framing language, not to the
parameters. The specific suspects are *"seamless tileable texture"* and *"the pattern continues
past all four edges"*, which are strong attractors toward uniform fields.

**Where this leaves the ruling's branch.** The ruling said a FAIL means *"text-to-image is ruled
wrong for architectural surfaces and the wall pipeline re-plans — conditioning, composition, or
hand-authored seeds."* The bar did not fail. But the destination it guarded may still be right,
reached by a different road: text-to-image can be made to produce **surface** reliably and did
not produce **architecture** in 20 attempts. That is a ruling, and it is yours.

⚠ One of the three re-plan options now has evidence behind it — see §3.

Sheet: `wall_microprobe/microprobe_sheet.png`. All 20, nothing filtered.

---

## 3. CONDITIONING SMOKE TEST — the best result in the probe

12 generations, two references × six identical seeds, `style_strength` 50. Informational, no
gate, and **not Stage 2**.

**Material DNA propagates, strongly and reliably.** 12 of 12 outputs sit unmistakably in their
reference's family.

**It is highly sensitive to which reference — which is the finding tier 1 needs.** The two rows
are different families in palette, value structure, and vegetation, from the *same seeds* and
the *same prompt*, with only the reference changed. The two-seat design's whole premise is that
which reference you pick matters. On this evidence it matters a great deal. Nothing on this
project had ever measured that.

⚠ **Composition propagates too, not just material — and this is the half that will bite.** Every
child of A-VAB inherited its recessed-square-frame layout. A reference with a distinctive
composition stamps that composition on everything conditioned by it. For a tile corpus that
means a seed chosen for its material can quietly cost you variety, and references should be
picked for material with *neutral* composition.

⭐ **Unplanned, and it bears directly on the wall ruling: 12 of 12 conditioned outputs are
full-bleed**, against roughly half for unconditioned Stage 1 floors. Conditioning appears to fix
framing as a side effect, because the reference is itself a full-bleed tile. That is direct
evidence for the *conditioning* option in the wall re-plan, and it was free.

Sheet: `conditioning_smoke/smoke_sheet.png` — reference at the left of each row, its six
children to the right.

---

## 4. PRECONDITION B — done, proven, and one gap closed that nobody had listed

`TopDownRenderer.TileWidth` was a hard-coded 24, so `harness_config.yaml` could declare 32 and
the renderer would draw a 24px grid regardless — a capture could disagree with its own manifest
in silence, and **every positive control would still pass**, green and reproducible, while
measuring the wrong grid.

- Tile size and scale are constructor parameters. **Defaults reproduce the previous behaviour
  exactly** — 24px, zoom 3.0/1.5/6.0 — so every existing call site is unchanged by construction.
- `--tile-size` / `--tile-scale` flags; the engine echoes `tile=32x32` at startup, so no capture
  circulates without naming the grid it was drawn on.
- `harness_config.yaml` declares **32 at ×2**, labelled a RULING and explicitly not a derived
  value, because §4.3's derivation has not happened.

**All five controls green at 32** — determinism, lighting, scene, device, junction — re-run, not
assumed still valid from the 24px run. Verified from the capture logs that the engine actually
received `--tile-size 32 --tile-scale 2.0`.

**A sixth control, for the parameter this change adds** (`control_tile_size.py`). An engine
echoing `tile=32x32` proves the flag was *parsed*, not that it reached the renderer's geometry.
The control captures the same scene at 24 and at 32 and requires the pixels differ. They differ
by **0.6224**. A parameter that changed only the log would be decorative and would have to be
labelled so or deleted (§13.5).

⚠ **The gap nobody had listed, found while wiring the device build.** The review-build marker
carried the light rig but no grid, and an iOS app receives no command line — so the device build
would have rendered at the default **24** while the desktop captures it exists to be compared
against were taken at **32**, with nothing reporting the mismatch. §13.1 hands the verdict to
the device; it would have been taken on the wrong picture. The marker now carries `tileSize` and
`tileScale` for the same reason it already carried the rig.

Fast suite green: **2503 passed, 0 failed.**

### ⚠ Correction: issue #141 was my error, and it changed your sequencing

The STOP 1 ruling says Precondition B should land *"with the #141 exit-code fix landed first, or
the re-proof proves nothing."* **There was nothing to land.** `run_controls.py` exits non-zero on
an aborted run — `shoot()` calls `sys.exit(1)`, and forcing the abort path returns 1. The
"exited with code 0" I reported came from my own observing command, which ended in `| tail -70`;
a pipeline reports its *last* command's status. Verified rather than re-reasoned
(`verify_141.py`), issue closed with the correction. The same mistake had already bitten once
that session, when a `dotnet build | tail` reported success for a build that never ran.

The re-proof therefore rests on the controls themselves, which do go red — each plants a real
defect — and on the new sixth control.

---

## 5. STAGE 3 — the lit comparison

Eight captures at 750×1334, the reference device's exact pixel size, tile 32 at ×2.

**What varies: the floor tile, and only the floor tile.** The wall, the corridor geometry, the
light rig, the tile size and the resolution are constant. The engine's own per-capture echo is
recorded in `stage3_manifest.json`, so the identical rig is *proven* rather than asserted by the
script that passed the flags.

⚠ **The walls are a stated weakness.** One micro-probe wall is used for every survivor, so it
cannot explain a difference between them — but it is structureless. These captures test how a
surface **receives light**. They cannot support any judgement about §7.1 or §12, and none should
be drawn from them.

**Why this is not `capture_probe_arms.py`.** That script captures exactly three arms, because
§6.4 declared a three-arm probe. STOP 1 changed the shape — the pool was curated blind to arm,
on the ground that arm labels carry no lighting information after Stage 1's positive-control
failure. Capturing "three arms" would now be capturing a distinction the evidence says is not
there. `capture_probe_arms.py` is left untouched and unused rather than bent; it remains correct
for a three-arm probe, and this stopped being one.

**Unlit companions.** Ambient only — the carried light's energy to zero and every other rig
value untouched, so a pair differs by the carried light and by nothing else. This is §6.3's
central claim made checkable: if a pair shows no difference, that is evidence *against* the
clause, and the sheet says so on its face.

---

## 6. WHAT RAFE IS ASKED TO DO AT STOP 2

**On the device.** The review app is installed under its own bundle id
(`com.rafehatfield.catacombsofyarl.tier0`), booting straight into the lit corridor at 32/×2,
showing one survivor. It answers the questions that only the device can: does it come alive lit,
does the device hold frame rate with occluders present, and does the light deliver the §6.2
region arc or is it merely darkness with a lamp in it.

**On the sheets, unlabelled and shuffled** — `stop2_lit_unlabelled.png` and
`stop2_lit_vs_unlit.png`. Codes ONE–FOUR; the mapping is in a sidecar the sheets do not reveal.
Blinding matters most here: by STOP 2 there are expectations to protect against, mine included.

⚠ **A limit of this arrangement, stated rather than discovered.** The marker carries one theme,
so the device shows **one** survivor and the other three are compared from captures at exact
device resolution. That splits §6.4's questions across two surfaces: the felt ones on the phone,
the comparison on the sheets. If the comparison must also be on-device, that is four review
builds under four bundle ids and is a rebuild, not a re-capture — say the word.

**The prior question from STOP 1 has not gone away.** Stage 1's positive control failed: no arm
depicted a directional key light, so the four survivors are not four lighting treatments. They
are four floors. Stage 3 therefore shows what receive-light *looks like lit* — genuinely, and it
is the evidence §6.4 asked for — but it cannot show A beating B, because Stage 1 never produced
an A that differed from a B. **§6.4's arm comparison remains unanswered, and no capture here
should be read as answering it.**

---

## EVIDENCE AND SPEND

| | |
|---|---|
| survivors | `tools/pixellab/probe_6_4/survivors/` + `MANIFEST.json` |
| wall micro-probe | `wall_microprobe/` — 20 images, ledger, sheet |
| conditioning smoke | `conditioning_smoke/` — 12 images, ledger, sheet |
| Stage 3 | `tools/tier0_harness/evidence/stage3/` — 8 captures, logs, manifest, sheets |
| controls at 32 | 5 green + the new `control_tile_size.py` |

**Spend this segment: 32 generations** (20 micro-probe + 12 smoke). Pool 3982 → 3950.
**Probe total: 174** (142 at STOP 1 + 32). Pool 4124 → 3950, settled at both ends throughout.

Every generation is on disk with its full request payload. Nothing on this platform is
seed-reproducible, so the ledger stores images and not parameters.
