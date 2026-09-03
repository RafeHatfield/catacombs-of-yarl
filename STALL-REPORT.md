# STALL — wall lane, two strikes on the orc-work item

**Guard: two strikes. Fired by the runner's judgement; the automated matcher stayed silent.**
LOOP-PROCESS §1.1.4 ruling trigger, this report as its evidence. No round 4 has been run.

Lane: `worktree-session-2026-08-29`. Rounds under the critic: `r001`, `r002`, `r003` — all FAIL,
all plant CAUGHT, all `SHIP: NONE`.

---

## The repeat

| round | the item |
|---|---|
| r002 | *"Same missing-repairs problem as 1: **nothing rigged, lashed or pinned anywhere in the lit radius.**"* |
| r003 | *"**Nothing in the frame is an object.** Four hundred years of rope, driven pins, hide and salvaged timber, and **not one piece of it is visible** — the frame is floor, ceiling, and one wall strip. Put the salvage in."* |

Different sentences, one finding: **§7.1's *show me what holds this together* is not answered in
the picture.** The new law in the skill says the runner matches by substance and fires when the
matcher does not, so it is fired here and named as a judgement call.

## What was done between the two, and it landed

Ruling (3) was built: bindings re-keyed to the traffic field, so density follows route-adjacent
walls rather than a flat position hash. Measured on the delivered frame, by differencing a capture
against one taken with bindings omitted:

| | before | after |
|---|---:|---:|
| binding-carrying cells inside the lamp's reach | **0** | **6** |
| total bindings placed | 11 | 13 |

**The fix landed and the complaint did not move.** That is the guard's exact condition, and it is
why a third attempt would be a guess.

## Why I think it is not a tuning problem — for the ruling, not as a decision

The r003 form of the item is **larger than the wall family**. It does not ask for more bindings on
wall faces; it asks for *objects* — rope, driven pins, hide, salvaged timber, as things standing in
the scene. The review scene has no props of any kind, by construction: it is a bare room, corridor
and chokepoint built to test surfaces. **No wall-family change can put an object in a frame that
contains no object system**, and §8.3.1's own reasoning is why the bindings are overlays on faces
rather than props in the first place.

So the wall lane can make repairs more visible on the reveals it owns, and it cannot answer
*"nothing in the frame is an object"* at all. That is a prop/overlay pass, which does not exist,
and it was already logged once as the *no-orc-work-from-above* cost when bindings came off the
wall tops.

---

## The thing that DID move, and it is ruling (2)'s acceptance condition

> **Acceptance: the build outranks the grey plant in the critic's own shuffle before any install.**

| round | rank | where the build sat | where the plant sat |
|---|---|---|---|
| r001 | `1 > 3 > 2` | slot 3, **below the plant** | slot 1, first |
| r002 | — | slot 3, **below the plant** | slot 1 |
| **r003** | **`1 > 2 > 3`** | **slot 1 — FIRST, named BEST, unflagged** | slot 2, second |

> BEST — *"The joints on the room floor are drawn, not applied. In the lit block at (440–600,
> 470–560) the slab edges var…"*

**The build now outranks the frame Rafe culled**, is named best of the deck, and is the only frame
of the three not flagged. The regression named in ruling (2) — *the found-rock pass removed all
architecture* — is measurably reversed by the slab/fracture construction ruling (1) authorised.

## Ruled work completed this turn

| ruling | built | evidence |
|---|---|---|
| (1) cap architecture — field-scale slab/fracture polylines, no constant position | yes | `field_slabs()` in `compose_cap.py`; toroidal jittered seeds at ~3 tiles; all nine instruments green (`cap_seamless` 0.81×, `cap_field_scale` tile-pitch 1.17) |
| (2) build must outrank the plant | **met at r003** | rank `1 > 2 > 3`, build first and unflagged |
| (3) bindings re-key to traffic | yes | 0 → 6 binding cells inside the lamp; rate scales `0.35 + 1.15·f` on the floor's own `TrafficField` |
| (4) two process laws into the skill | yes | `SKILL.md` §5 (two strikes by substance) and §6 (a second gate is deleted, not reconciled) |

## Two open items from r003 that are ruled territory, not build tasks

1. *"The wall run at y 385–435 has a flat black top surface… Give the top face its own lit value,
   separated from both the floor and from black."* Past the lamp this is the §6.5
   standing-distance law and §13.9's representable floor: the ground there holds ~7 levels in
   total, and no authored value survives the multiply. Already ruled *no ladder chase*.
2. The cap's new architecture reads as **soft**: *"soft blotches 12–20px across… The 1px crack
   lines are hard but sit on mush."* That is a granularity complaint about a construction one
   round old, and it is the first time it has been said — **not** a repeat, and the obvious next
   move if the lane restarts.

**Nothing is installed.** `CRITIC-VERDICT.json` reads FAIL; `critic_gate.py` refuses.
