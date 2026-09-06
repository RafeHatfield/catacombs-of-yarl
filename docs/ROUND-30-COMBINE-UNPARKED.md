# Round 30 — the combine un-parks on the re-ratified lamp

**Branch** `art/one-lamp` · **Predecessor** round 29 (#174, one lamp) and round 28 (PR #177, parked
composed-and-holding) · **Gate** the full frame-critic round on the recomposed build, whose PASS
seeds `approved_capture` — the room walk.

---

## 0. What un-parked, and on what

Round 28's combined build was parked **composed and holding, blocked on #174** — the first
occupant of that state. Both conditions the park named are now met:

1. **#174 landed.** The floor's diffuse honours `LIGHT_ENERGY` and the specular's `delivered`
   scalar is built from `LIGHT_COLOR.a * LIGHT_ENERGY`, so both planes are lit by one arithmetic.
2. **Ruling 56 re-ratified** (Rafe, 2026-09-06) on that corrected lamp, walked on device with an
   energy knob for the first time: **radius 5.0 → 6.0, ambient 0.70 → 1.50**, energy 1.6 and
   falloff 1.00 held.

**The park earned its keep.** Its rule — *the resumer re-does rather than re-reads* — fired twice:
once when the arithmetic was corrected, and again when the rig moved under those corrections four
hours later. The second pass invalidated numbers that had been measured correctly **that same
day**. A park called "finalised" would have shipped them into §6.5.

---

## 1. The rig, and what re-deriving against it cost

| | Ruling 56 (2026-08-28) | re-ratified (2026-09-06) |
|---|---:|---:|
| radius | 5.0 tiles | **6.0** |
| falloff | 1.00 | **1.00** (held) |
| ambient level | 0.70 → `#121218` | **1.50 → `#272733`** |
| energy | 1.6 | **1.6** (held — and reachable for the first time) |

⚠ **Ambient went UP, and §6.2.1's third bullet is engaged rather than breached.** The clause asks
the pass to preserve §6.2's arc — *you begin as the only thing here that burns* — and the previous
pass could cite ambient moving *down* as evidence. This one puts it above even the pre-Ruling-56
value. The arc is a register claim, carried eye-side and never instrumented (§13.4), and the gate
that owns it ruled here. **Measured, so the note is not only rhetoric: 33 of 81 in-view floor
cells still sit under the dark bound.** The room is not flooded.

### The delivered reach moved, and it is the figure everything else hangs off

Ruling 56 recorded that **nominal radius is not delivered reach** and that future ratifications
state the delivered one. On the re-ratified rig, floor luminance as a fraction of the nearest lit
floor cell:

| distance | ratio |
|---:|---:|
| 2.0 tiles | 0.590 |
| 3.2 | 0.336 |
| 4.0 | 0.229 |
| 5.0 | 0.118 |
| **5.4** | **0.091** |
| 5.8 | 0.080 |
| 6.0 — the nominal radius | 0.079 |
| beyond | ~0.075, the ambient plateau |

> **Delivered reach ≈ 5.2–5.5 tiles**, against the old rig's ≈ 4. Nominal 6.0 still overstates it,
> exactly as 5.0 overstated 4 — the gap is a property of the falloff, not of the number chosen.

### §6.5 re-derived, twice in one day

Every figure round 29 re-took on the corrected lamp was correct for radius 5.0 / ambient 0.70 and
is stale. Re-measured on the ratified rig, **not adjusted**:

| band | floor (r29) | **floor NEW** | wall (r29) | **wall NEW** | f/w (r29) | **f/w NEW** |
|---|---:|---:|---:|---:|---:|---:|
| ≤2 tiles | 152.34 | **168.73** | 58.40 | **66.51** | 2.609 | **2.537** |
| 2–4 | 57.33 | **87.58** | 20.15 | **31.41** | 2.846 | **2.788** |
| >4 | 9.00 | **22.61** | 5.05 | **11.28** | 1.781 | **2.004** |

**Worst cell in every band**, because a mean hides the cell that decides whether a band reads:

| band | floor min / max | wall min / max |
|---|---|---|
| ≤2 | 110.40 / 214.38 | 14.14 / 93.13 |
| 2–4 | **44.87** / 156.21 | **6.05** / 76.03 |
| >4 | 13.54 / 47.34 | **2.03** / 39.82 |

### The cap against the floor — and one bar changed state

| band | n | L(cap, floor) r28 | r29 | **NEW** | vs the 8-level bar |
|---|---:|---:|---:|---:|---|
| standing ≤2 | 3 | 50.22 | 72.56 | **89.64** | CLEARS |
| 3–4 tiles | 19 | 16.88 | 17.79 | **34.82** | CLEARS |
| beyond 4 | 35 | 4.26 | 4.27 | **10.33** | **CLEARS — it did not before** |

> **The wider pool made wall mass read at range.** *"Beyond four tiles"* has been under the
> perceptual-floor bar in every measurement this project has taken; on this rig it clears at 10.33
> levels. That is the re-ratification paying for itself on a number nobody tuned for.

Sign is negative throughout: the cap is **darker** than the floor. ⚠ **§6.5 row 1 wants the wall
top LIGHTER than the floor, and it is further from that than ever** — the floor gained more than
the cap did at every range. That remains a value-law question and it is Rafe's, at a gate, not an
instrument's. It is **not** ruled here.

---

## 2. The legibility guard refused the first capture, and was right

`tier1_combined_review.json` declares `(11,13)` at 5.1 tiles **expect=dark**, because the old rig's
delivered reach was about four. On the new rig it reads **0.1160** against a 0.1000 bound — it is
legitimately lit, and the guard refused to write the frame.

> **THE BOUND WAS NOT TOUCHED.** Loosening a threshold to pass one's own capture is the failure
> LOOP-PROCESS §4.3 point 1 names, and it would have been the easy move: one number, and the
> refusal disappears.

The **probe moved instead**, to `(11,14)` at 5.4 tiles — ground that is actually past the new
reach — measuring **0.0718**, 28% clear of the bound. The declaration keeps its meaning (*the arc
is part of the distribution and a scene where everything is lit is not the game*); only the cell it
points at moved, and both values and the reasoning are recorded in the declaration's own `why`.

⚠ **FLAGGED: the scene's other dark declaration, `(8,7)`, now passes at 0.0976 against the same
0.1000 bound — 2.4% of margin.** It is marginal on this rig and is the next thing that will refuse
a capture. Recorded rather than pre-emptively moved: moving a guard that has not fired, to stop it
firing later, is the same error in slower motion.

---

## 3. Routed from the walk

| # | the walk's finding | where it went |
|---|---|---|
| 1 | *Sasha reads washed out at this lamp — the sprite receives less of the lamp's top end; warmest never brightest* | **#183**, a hero pass and explicitly not a rig change |
| 2 | *Msg button overlaps the bottom rig control — unreadable* | **FIXED here.** Both anchor bottom-left of the same overlay; the panel's rect ran to −8 so its last row sat under the button. Bottom now stops at −60, derived from `MsgButton`'s own constants, and `GrowVertical.Begin` grows the panel upward so a future row cannot push it back |
| 3a | *polish slightly hot on worn lanes; wall-base occlusion washed by shine* | **#184** — actionable only now the lamp is one quantity and the rig is set |
| 3b | *hallway-bottom brickwork artefact* | **#185**, its own bug |

---

## 4. What this round does NOT rule

- **§6.5's value law.** Row 1 (*wall top lighter than the floor*) is further out of reach, not
  closer. Measured and reported; not ruled.
- **§6.5's void banner.** Round 29 proposed narrowing it on proof that the range-probe scenes never
  carried the shader. Still **proposed, not applied.**
- **Round 28's flip-1 attribution.** Still unannotated in its own document.
- **The ~45° band (#179).** Untouched; two seats, no location, and not the polish mask.

---

## 5. Reproducing

```bash
dotnet build CatacombsOfYarl.Presentation.csproj
/Applications/Godot_mono.app/Contents/MacOS/Godot --headless --path . --import

tools/tier1_floors/capture_combined.sh rerat_r1 1        # refuses if a declared point is wrong
tools/tier1_floors/capture_energy_probe.sh rerat_reach 1.6   # the reach profile, legibility-free

python3 tools/tier1_walls/measure_mass_read.py \
  --scene src/Presentation/assets/tier0_harness/scenes/tier1_combined_review.json \
  --png tools/tier1_floors/evidence/rerat_r1.png \
  --log tools/tier1_floors/evidence/rerat_r1.log \
  --assets src/Presentation/assets/tier1_walls --tag rerat_r1

.claude/skills/frame-critic/run_frame_critic.sh --lane combined
```
