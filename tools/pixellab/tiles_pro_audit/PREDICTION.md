# `tile_depth_ratio` — PREDICTION, WRITTEN BEFORE THE CALL

**Committed before the request is sent. Not edited afterwards.** If it is wrong, it stays here
wrong, with the result beside it — that is the only version of this document that is worth
anything.

Authorised by Rafe's ruling, 2026-08-26: *"Approved: the one `tile_depth_ratio` call, your
prediction on file before it runs."*

---

## THE CALL

One call. `prompts/wall_kit.json` unchanged, seed 1337 — byte-identical to yield kit A — with a
single parameter added:

```
tile_depth_ratio: 0.5
```

**Why 0.5.** It is the only camera parameter this audit did not spend, and it is documented as
*"Tile depth/thickness ratio (0.0–1.0). Controls how much vertical depth the tile has. Overrides
the default computed from `tile_view`."* The frozen configuration's implicit depth is **0.25** —
measured, not assumed: a 32-wide floor cell comes back 24 tall, so 8 of 32 pixels are depth. 0.5
is double that and sits mid-range, far enough from the default that a live parameter cannot fail
to show it. **No prior measurement of this parameter exists to aim it better, and that is stated
rather than dressed up.**

## THE PREDICTION

**Headline: the readout moves and the bar does not.**

| # | prediction | falsified by |
|---|---|---|
| 1 | **`tile_depth_ratio` is live.** The structural readout moves — at minimum `floor_cell` and `stack_stride_px`, most likely `canvas` too. | `READOUT UNMOVED` |
| 2 | **The floor cell gets *shorter*, not taller** — roughly 32×16 at ratio 0.5, against the baseline's 32×24. More depth means more foreshortening of the ground. | a cell taller than 24, or unchanged |
| 3 | **Clause 1 still scores 0 of 38.** No candidate reads as having a top surface. | **any** candidate passing clause 1 |
| 4 | **The seat again reports face-on coursing on north–south pieces** — the same horizontal running-bond as east–west pieces, because one front elevation is still being masked into every silhouette. | the seat describing correctly-oriented top-surface stone ends |
| 5 | **Clause 3 (§6.3) degrades below kit A's 38/38**, as arm 3's did (32/38), because asking this canvas for more depth-by-value is the same request that manufactured a key light there. | 38/38 on clause 3 |

**Confidence, stated honestly and separately.** 1 and 2 are near-certain — they are geometry, and
geometry on this endpoint is deterministic and has behaved exactly as documented every time. **3
is the one that matters and I hold it firmly**: the arm-3 seat located the defect in the
compositor, not the camera, and a camera parameter cannot add a plane that was never painted. 4
is the direct corollary of 3 and is the sharper test, because it names a specific observation
rather than a score. **5 is the weakest** — arm 3 moved two parameters at once, so its §6.3 loss
is not cleanly attributed, and this call may leave §6.3 alone.

## WHAT WOULD OVERTURN THE AUDIT'S CONCLUSION

Prediction 3 failing. **If any candidate clears clause 1 here, the finding's central claim —
*"the top surface is not modelled, and no camera parameter adds a plane that was never
painted"* — is wrong**, and it will be corrected in `FINDING.md` in place rather than softened.
One passing candidate is not five and would not clear the yield bar; it would still overturn the
mechanism.

## HOW IT IS JUDGED

The same way everything else was: a fresh blind `claude -p` seat, cwd outside the repo, same
`critic_prompt.txt`, the same two plants, the same strict derivation. **The seat is not told this
is a prediction test.** Plants not caught ⇒ round void (§4).

## BUDGET — an amendment, recorded rather than silently applied

The declared ceiling was **220 generations** and the audit landed exactly on it. `spend.check()`
enforces that ceiling in code and **refuses this call** as written.

This is ruling trigger (b) — *an amendment to anything frozen* — and the amendment has been
granted by the human gate, not taken by this seat. The ceiling is raised to **240**, the
authorisation is quoted at the top of this file, and the original 220 stands unedited in
`DECLARATION.md` with an appended amendment note. **A bar changed by ruling is not a bar tuned to
a result**, and the distinction only survives if the change is written down where the original is.
