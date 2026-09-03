# Rounds run while the mechanism was being written

These two rounds are **evidence, not lane history.** They were run against a working tree in which
the frame critic itself was still being built, so their build ids describe trees that were never a
build of anything. They are moved here rather than deleted, and moved rather than left in
`history/`, for one reason each:

- **moved out**, because `history/` is where the loop guards count from. A lane's counters must
  come from rounds run on that lane's art, and counting the mechanism's own construction toward a
  two-strikes or a five-round park would fire a guard on a lane that had never had a round.
- **not deleted**, because both found something the design needed, and one of them found it in the
  mechanism's own control.

## `r001-worktree-frame-critic` — the first live round, on main's wall build

Real capture, real seat, real deck. **FAIL**, plant caught. Its finding about the wall build is in
the flip list; the finding about the *mechanism* is this:

> the seat flagged all three frames, shipped none, and **ranked the plant first** — the frame Rafe
> culled for grey walls, placed above the current build.

The plant rule was declared before the round and was **not touched after it** (LOOP-PROCESS §8).
Instead the fact is recorded as `outranked_build`, printed by the runner, and written into the law
as §1.2.1's limit.

## `r001-worktree-frame-critic-selftest` — the judge's own self-test

The build slot deliberately held `morgue/keyline-floor.png`, a frame Rafe culled outright
(*"outlined chips"*). The declared expectation was that the seat would flag it.

**It did not.** It ranked that frame **best of three** and left it out of `FLAGGED` — while
listing the same frame's magenta placeholder walls in its own flip list, so it had plainly seen
them. The round still came out **FAIL**, `SHIP: NONE`, so no gate would have opened, and the plant
in that deck (`tile-quantized-wear.png`) was caught.

Recorded as it happened, because it is the sharpest statement of what this mechanism does and does
not promise:

> **The gate rests on SHIP, not on RANK.** A build reaching the phone is one a blind seat said it
> would ship. The seat's ordering does not reproduce the human gate's culls, and two rounds on one
> day say so.
