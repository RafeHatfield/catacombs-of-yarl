# Rounds 23, 24, 26 re-examined on the engine's own mapping

Ruled 2026-09-02 alongside bible §13.10. The coordinate claims are reinstated; this records what
they actually say once measured against the camera's answer instead of my assumption.

---

## The correction

An instrument computed a tile's screen position as `(H − rows·tile) // 2` — the field, centred.
**The camera follows the player.** Measured origins on three stations of one scene:

| station | engine | the assumption |
|---|---|---|
| `route_onroute` | **(−9, 34)** | (−169, −5) |
| `route_onroute_choke` | **(−137, −158)** | (−169, −5) |
| `approach` | **(−137, 34)** | (−169, −5) |

## Round 24 — the seat was right

It placed the corridor at **x 505–565**. The engine places the mouth at **x 535**. Exact.

My contradiction of it was the wrong number, and the finding built on it — *"the seat described
ground with route strength zero"* — is **withdrawn**.

## Round 23 — the seat found the right corridor and mis-stated its extent

Cited: *"x 375–440, y 250–430, the corridor."* On the engine's mapping for that station (−137, 34):

| tile | screen x | screen y | route strength |
|---|---|---|---|
| (8,4) … (8,6) | **375–439** | 290–482 | *(blank — off route)* |
| (8,8) | 375–439 | 546–610 | *(blank)* |
| **(8,9)** | 375–439 | 610–674 | `===` |
| **(8,10)** | 375–439 | 674–738 | `***` |
| **(8,11)** | 375–439 | 738–802 | `%%%` |

**Its x is exactly the corridor column.** My mapping put that column at x 343–407, and that error —
nothing else — is what made the seat look mistaken. Its *y* covers rows 4–6, which are off-route;
the route on that column begins at row 9.

**So "void-for-station" is withdrawn as reasoned.** It was justified by an x-error that did not
exist. What survives is narrower and weaker: the cited *rows* are off-route, in a report whose
column was exact and whose description ("the corridor") was correct. A y-offset in a self-report is
not the same thing as a seat having looked somewhere else, and it does not support voiding a round.

**Unresolved, and left that way rather than guessed:** why x lands exactly and y does not. A
vertical frame offset — the dungeon view begins at y = 90 — would produce something like it, but I
have not demonstrated that and will not assert it.

## What still stands on its own

The seat-coordinate change of round 27 — **positions relative to the figure, in tiles**. It was
ruled on my evidence, and my evidence was wrong; but the change is right for a reason that does not
depend on it. **Relative positions cannot drift under any mapping error, mine or the seat's**, and
the last three rounds have now produced one of each.

## The reversals, as ruled

- rounds 23, 24, 26 coordinate claims — **reinstated**
- round 23 void-for-station — **withdrawn as reasoned**; the round's findings return to the record
- round 24's *"the seat examined ground the route does not touch"* — **withdrawn**
- bible **§13.10** banked: *a measurement that convicts a witness needs the witness's proof
  standard*
