# Deferred findings

Findings that survived a review round and were deliberately not fixed in the commit that
raised them. Each says what it is, what it costs, and what has to happen before it lands.

---

## §12.2 multi-cell prop footprints — `CorridorReviewSceneBuilder`

Two review rounds (build → review → fix → re-review). Round 1 returned 3 blockers, round 2
returned 2. Everything below is what round 2 raised and the fix did **not** take, under the
unattended two-round cap. Every one was demonstrated by execution, not by reading the diff.

### deferred — the junction refusal names the wrong cause

A blocking prop on an *arm* of a junction, one cell away from the junction itself, is refused
with *"the carved geometry has a junction at (8,11) but **a prop stands on it**"*. Nothing
stands on it. `HasJunction` also fails when an arm drops below three open neighbours, and the
message cannot tell the two apart. An author will look at (8,11), find it clear, and stop
trusting the guard.

**Fix:** say "on it or on one of its arms", or report which covered cell changed the answer.
**Before:** any round that lets an author place props near the junction by hand.

### deferred — the junction guard is one-directional, so props can MANUFACTURE a junction

It fires on `junctionBefore && !junctionAfter` only. An open 11×11 room reports `junction=NO`;
add four 1×1 blocking props on the diagonals of (7,7) and it is **accepted** with
`junction=YES @(7,7)`, because `HasJunction` requires solid diagonals and prop cells satisfy
that. `ProbeJunctionLuminance` then measures a junction that exists only because four sprites
are standing around it.

**Fix:** refuse when the answer changes in *either* direction, or assert the junction cell is
unchanged. **Before:** any scene with props near a junction — this is the same class as the
defect the guard was written to catch, pointing the other way.

### deferred — `verify_props.py` reports distance two different ways

The per-row `tiles from station` is now the worst cell's distance; the closing
`nearest / furthest` summary still uses the anchor's. The summary therefore understates the
furthest cell, which is exactly the quantity §13.8's floor is about, on exactly the multi-cell
props §12.2 introduced. Separately, `L[max(0, sy):...]` clamps a negative origin to 0, so a
footprint cell off the top or left of the frame is measured at the **wrong cell** and reported
as a confident number; a zero-size region is skipped in silence. `ProbeFloorLegibility` refuses
off-screen points and says why; this file has no equivalent.

**Fix:** derive both numbers from the same per-cell pass; refuse an off-frame cell rather than
clamping it. **Before:** a prop is ever placed near the frame edge.

### deferred — the seal check enforces less than its comment claims

The comment says *"a prop the walker cannot reach is not a prop the gate can judge"*. The code
only enforces that reachability does not **shrink**: two disjoint carve rects with a prop in the
far one is accepted, unreachable, unmentioned.

**Fix:** assert every prop is reachable from the station, not merely that nothing became
unreachable. **Before:** a scene with more than one carved region.

### deferred — `ReviewSceneBuilder` still hardcodes `1, 1`

The sibling builder the `PropPlacement` doc names as the source of this vocabulary has no
`w`/`h`, so §12.2 props cannot be seated in the open-room review scene. The two builders' prop
vocabularies have now diverged, which is what the original comment existed to prevent.

**Fix:** port the footprint fields. **Before:** the open-room scene needs a prop.

### deferred — duplicate `<summary>` on `PropPlacement`

The "THE FIELDS ARE `ReviewSceneBuilder`'S, DELIBERATELY" paragraph is orphaned above the new
one. House drift (`LegibilityPoint` has the same shape), and the merge point is exactly where
the two builders diverged, so it wants doing with the item above.

### ~~still owed — `verify_props.py` does not check that a prop DREW~~ — **DONE 2026-09-11**

Built as `verify_props.py --drew`, and the control took three tries to get honest. See the
commit `harness(judge)`. Two things worth keeping from it:

- **The obvious control is wrong.** Capturing with the props removed does not isolate the
  sprite, because a blocking prop marks its cells and a marked cell changes what the floor
  composer lays under it. The honest control keeps every prop declared, in place and blocking,
  and swaps only the tile ids for a reserved transparent tile.
- **"Zero change outside the footprint" was the wrong bar.** A prop sprite is drawn CENTRED, so
  it overflows into its neighbours by up to half a cell — 5,368 pixels on the current scene, all
  within 32px, median 10. The test is distance, not count.

**The finding as it was raised**, kept because its reasoning is what made the fix correct:
the file's headline is *"EVERY DECLARED PROP MUST DRAW, AND EVERY ONE MUST BE LIT"* and only the
second half existed. The docstring claimed drawing was "checked against a propless control";
`main` measured luminance and nothing else. The incident behind it is why the naive control was
rejected: an earlier probe measured "pixels changed at the prop's cell", called it the sprite
drawing, and was measuring `MarkPropCell` repainting the floor underneath.

⚠ The fix proposed at the time — *"capture a propless control and diff"* — **would have been
wrong**, for exactly that reason. Recorded so the suggestion is not picked up later as if it had
been the answer.
