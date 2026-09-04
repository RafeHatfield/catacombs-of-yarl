# The first round that actually voided

The wall lane's first round under the progress guards came back **VOID**. The seat put the
picture-plant — `grey-walls.png`, culled by Rafe as *"Grey walls and ceiling; it looked better a
few versions ago"* — **first in the deck, and did not flag it.**

```
RANK      1 > 2 > 3        (1 = the plant, 2 = the build, 3 = the asset bar)
SHIP      NONE
FLAGGED   2, 3             — the build and the commercial bar; not the plant
plant was slot 1: ranked_last=False named_worst=False flagged=False shipped=False -> MISSED
```

`SHIP: NONE`, so nothing would have installed either way. **The round's findings are not read**
(§4) and none of them is quoted here or anywhere else.

## Two things this is evidence of, and one it is not

**It is not evidence about the art.** That is the whole meaning of VOID.

**It is the fifth instance of §1.2.1's recorded limit** — a blind seat's ordering does not
reproduce Rafe's culls — and the first strong enough to void a round rather than merely be noted
beside one. Four seats had put a culled frame above the build; this one put a culled frame at the
top of the deck and found nothing wrong with it.

**And it points at the plant rather than the seat.** `grey-walls.png` was culled for **chroma** —
the wall family was never given the floor's colour, and the delivered cap sat +27.6° of hue off
the floor at 55% of its saturation. The frame critic asks a seat to rank **craft**. A plant whose
defect is orthogonal to the question the seat is asked is a plant that a competent seat can
reasonably rank first: it is well constructed and the wrong colour, and it was only ever the wrong
colour.

`morgue/README.md` already carried this as a stated risk — *"the wall lane holds one entry"* — and
this round converts it from a risk into a measurement. **The wall lane needs a plant culled on
construction, and morgue entries are Rafe's culls, so that is his to supply.** Under §4 the honest
move is to stop and fix the judging layer, not to run the round again until it agrees.

## ⚠ What was lost, and by whom

**The seat transcript for this round no longer exists.** I deleted `history/` for the lane while
clearing state for a re-run, before recognising that a void round's *record* is evidence about the
judge even though its *findings* are not evidence about the art. `runner-output.txt` here is the
runner's console output, which carries the rank, the ship list, the flags and the plant
adjudication — everything cited above — and not the transcript itself.

Recorded rather than quietly worked around. The round below it was re-run because the code changed
under it (`critic_gate.py` was leaking void findings, see `../PROOF.md`), **not** because this
verdict was unwelcome.
