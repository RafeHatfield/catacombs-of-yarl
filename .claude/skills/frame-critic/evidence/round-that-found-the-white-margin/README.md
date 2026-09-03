# The round that found the white margin

The round after `round-that-found-the-padded-bar/`, run with the out-of-bounds crop already fixed.
**FAIL**, plant caught, seven concrete flip items on main's wall build. Kept here rather than in
`history/` for the same reason as its predecessor: its deck was still defective, and the defect is
why it is worth keeping.

## What it found

It ranked the **commercial asset bar last again**:

> **WORST 2** — *"The frame is not finished rendering. There is a pure white (255,255,255) margin
> occupying x 360–383 for the fu…"*

The previous fix moved the crop inside the *file*. It was still outside the *picture*: the example
sheet's artwork occupies **x 24–695, y 24–479**, and everything beyond that is white paper. The
box `(336, 216, 720, 504)` reaches the right-hand margin.

`(304, 192, 688, 480)` is the same 384×288 window placed wholly inside the artwork — floor, a wall
run, water and props.

**The standing rule that came out of it, now in `docs/FRAME-CRITIC.json`: after changing that
field, look at the crop.** The out-of-bounds check is mechanical and exact and is enforced in
code. *Inside the image but outside the picture* is not something a script should be trusted to
judge, and a weak detector for it would be worse than reading the verdict — which is how both
halves of this were found.

## It also confirmed the ranking finding, a third time

> **⚠ THE PLANT OUTRANKED THE BUILD.** `grey-walls.png` — *"Grey walls and ceiling; it looked
> better a few versions ago."* — placed above the current build, by a third seat on a third
> shuffle.

And it triggered the other recorded observable: the seat **flagged every frame, including the
commercial bar**, so the flag carried no discrimination that round. The plant check still holds —
it declined to ship a culled frame, which is the claim — and the runner said so in as many words.

## Its flip list is worth reading anyway

Its findings about the wall build are specific and independent of the bar: the wall cap and the
lit floor share one texture at one value; every joint ramps over 2–3px so the surface reads as a
downscaled photo rather than drawn art; the floor's pale blocks are flat fills with no mortar
network; the 45° wear hatch crosses block boundaries at one angle and one width. Those do not
depend on which frame the bar was.
