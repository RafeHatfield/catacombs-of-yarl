# The wall lane stops — two critic rounds, and the remedy collides with a ruling

**Two rounds under `.claude/skills/frame-critic`. Both FAIL, both plant CAUGHT (so both are
readable), both `SHIP: NONE`. I am stopping the loop rather than taking a third guess.**

| round | verdict | plant | build slot | history |
|---|---|---|---|---|
| r001 | FAIL | CAUGHT | 3 | `history/r001-worktree-session-2026-08-29.json` |
| r002 | FAIL | CAUGHT | 3 | `history/r002-worktree-session-2026-08-29.json` |

---

## 1. The first flip landed, and it landed because a number had become a target

Round 1's wall flip:

> *"The upper wall masses at x≈60–370 and x≈440–700 are dense **sponge speckle** that reads as
> loose gravel, not a surface."*

That was mine, and its cause is exactly the thing the frame-critic skill was created to stop.
Chasing the floor's measured 84.8% fine-power share, I weighted the cap's 2px octave at 1.60 and
took the share from 49.6% to 73.6%. `grain32.py` is a **builder's tool** and I used its number as
a target — and the metric cannot distinguish *stone at masonry scale* from *maximum high
frequency*, because no metric can. §2 of the skill, walked into within a day of reading it.

Backed off, buying the share from **structure** (the 8px and 4px octaves) and holding the
pure-noise 2px term down: share 48.9%, all nine instruments still green. **Round 2's flip list no
longer contains the speckle item.**

## 2. But the underlying finding survived, in different words

| round | the wall-mass flip |
|---|---|
| r001 | *"dense sponge speckle … Replace with **drawn courses** at the frame's own pixel size."* |
| r002 | *"the dark upper region is **fine mottle with no architecture under it. Draw the stone through it.**"* |

The speckle changed. **The complaint did not: the wall mass has no drawn structure in it.** The
runner's two-strikes matcher did not fire — the texts differ — but in substance this is the same
item surviving two consecutive FAIL rounds, which is the condition that guard exists for: *"the
fix is not landing; a third attempt is a guess."* I am treating it as fired by judgement, and
saying so rather than quietly running a third round.

## 3. ⚠ And the remedy the critic asks for collides with a ruling

Both rounds ask for **courses / architecture drawn through the wall mass**. The cap does not have
them **by ruling, and for a measured reason**:

- The old cap *was* coursed masonry. §8.3.3's corner theorem forces a bed joint onto every tile
  boundary of an edge-matched course set, and **that joint at 32px pitch was the lattice the
  device gate rejected** — the whole reason the cap pass exists.
- §7.4 governs the replacement: *the Boundary is mostly found stone*. A wall top is found rock a
  wall was built under, not a course of dressed stone. Rock has no courses, so the theorem has
  nothing to bite on.

So the critic is asking for the construction the gate culled, and the ruling that replaced it is
the reason it is not there. **That is a ruling trigger, not a build task**, and it is not mine to
resolve. The available middle — structure at a scale larger than grain but not a tile-pitch
course grid (strata, breaks, block edges that ignore the tile) — is a new authored construction,
not a tuning of this one.

## 4. THE MOST IMPORTANT LINE, and it is the runner's own words, in both rounds

> **THE PLANT OUTRANKED THE BUILD.** A blind seat put a frame Rafe personally culled — *"Grey
> walls and ceiling; it looked better a few versions ago."* — above this one.

Twice, two different seats, two different shuffles. The skill is explicit that ranking does not
reproduce Rafe's culls and that this is **not** part of the verdict — but it is a statement about
the build. The same-quarry hue fix landed and is measurable (cap hue +1.6° from the floor, sat
ratio 1.078, against +27.6° and 0.553 before), and a blind seat still prefers the culled frame.

## 5. One more finding, un-repeated and cheap, recorded not fixed

> *"nothing rigged, lashed or pinned anywhere in the lit radius."*

The build places **11 bindings**, and there are **11 face-bearing wall cells inside the lamp's
five-tile reach** — so there is somewhere for orc work to be. Bindings are placed by position hash
across every wall cell in the map, and most wall cells are outside the lamp. §7.1 asks *show me
what holds this together*, and it is being answered where nobody can see it. A placement change
(weight bindings toward reveals that are actually lit) is the obvious candidate and has not been
made, because it belongs to a round that is not running.

---

## What is in the tree, ruled and verified

| ruling | verified how |
|---|---|
| same-quarry hue, walls **and** caps | `quarry_tint` in both manifests; delivered hue +1.6°/+4.8°, sat 1.078/1.136 |
| `hue_shift` 0 | cap manifest |
| cap texture toward masonry grain | fine-power 49.6% → 48.9% after backing off the over-correction |
| bisect vs the approved warm-face build | `BISECT-GREY.md` — `bceb7446` owns it, `72c5bd3a` exonerated, `f3f5a207` contributory |
| cap to rung 3 | cap manifest `top_rung: 3` |
| E/W occlusion at ambient-anchored strength | `RelativeIlluminationAtTile`; past-lamp seam 3.85 → 5.23 levels |
| `void_ring` 0 (§12.1 ring outline) | wall manifest; ring 0.06× an ordinary cell boundary |

**Nothing has been installed.** `CRITIC-VERDICT.json` reads FAIL, so `critic_gate.py` refuses and
`build_review_app.sh` will not export for install. That is the gate working as designed.
