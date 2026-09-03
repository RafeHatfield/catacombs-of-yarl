# The round that found the padded bar

A complete round on main's wall build — real capture, real seat, real deck. **FAIL**, plant
caught, seven concrete flip items. Kept here rather than in `history/` because its deck was
defective, and the defect is the point of keeping it.

## What it found

It ranked the **commercial asset bar last**, and said why:

> **WORST 1** — *"Several things, any one of which stops it. The frame is padded. Content ends at
> row 239. Rows 240–263 are pure …"*

That is not a judgement about the bar. **The bar crop was out of bounds.** The box inherited from
`tools/tier1_floors/run_seats.py` is `(336, 240, 720, 528)`; the source image is **720×504**. PIL
pads an out-of-bounds crop with black and says nothing, so the comparative frame the whole quality
comparison rests on had a black band along its bottom edge — and the seat, correctly, culled it
for the band instead of comparing craft.

Textbook LOOP-PROCESS §4.2: a step that quietly does nothing anyone can see, surfacing later and
somewhere else. Two changes followed:

- `frame_critic.py`'s `crop_to()` **refuses** an out-of-bounds box rather than padding it.
- the box was moved inside the image.

**And the next round culled the bar again**, for the other half of the same mistake. Shifting the
window up to `(336, 216, 720, 504)` is inside the *file* and still outside the *picture* — the
example sheet's artwork occupies x 24–695, y 24–479 and everything beyond that is white paper:

> **WORST 2** — *"There is a pure white (255,255,255) margin occupying x 360–383 …"*

`(304, 192, 688, 480)` is the same 384×288 window placed wholly inside the artwork. The standing
rule now in `docs/FRAME-CRITIC.json`: after changing that field, **look at the crop.** The
out-of-bounds check is mechanical and exact; *inside the image but outside the picture* is not
something a script should be trusted to judge, and a weak detector for it would be worse than
reading the verdict — which is how both were found.

## What it also confirmed — the third instance in a row

> **⚠ THE PLANT OUTRANKED THE BUILD.** A blind seat put `grey-walls.png` — culled by Rafe as
> *"Grey walls and ceiling; it looked better a few versions ago."* — above the current build.

Different seat, different shuffle, same result as the first live round and as the self-test.
**A blind seat's ranking does not reproduce Rafe's culls.** The verdict rests on SHIP, not on RANK,
and this is three-for-three on why that distinction had to be written into the law.

## ⚠ It reaches backwards

`tools/tier1_floors/run_seats.py` still carries the original box. That file belongs to an open art
session and this PR does not touch its work — but **every comparative seat that session ran was
shown a padded bar**, and that is worth knowing before any of those verdicts is cited.
