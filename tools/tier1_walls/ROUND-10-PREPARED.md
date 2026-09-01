# Round 10, prepared — the room's sides

**Prepared, not built.** Rafe: *"Prepare the material-arm mass-read remedy as your next round,
scoped to caps and N–S tops… No build until Rafe's answers land."* Nothing has been composed,
captured or installed for this round. Everything below is measured on captures already on disk, or
projected from them by a law that has been proven exact.

---

## 1. Why the sides have no mass, and it is one fact about §3

A face exists **exactly where the south neighbour is not wall**. A room's north wall has floor to
its south, so it gets a reveal and reads as mass — *"the north face reads"*. A room's **east and
west walls have floor to their east or west, never to their south**, so §3 draws them no face at
all and they present **cap and nothing else**.

So the sides of a room are exactly the cells with no second plane. The moment the cap stops
separating from the floor, the room stops having sides. This is not a defect in the cap; it is
§3's two-plane projection meeting a surface that has no second plane to be separated from.

**The walk's two complaints are one measurement.** On `r22_standing`, cap-only cells against the
floor they actually abut:

| band | n (all N–S) | cap | floor | worst separation | |
|---|---:|---:|---:|---:|---|
| standing ≤2 | 2 | 71.52 | 89.11 | **15.56** | clears |
| **3–4 tiles** | 4 | 31.13 | 33.22 | **0.58** | **UNDER the 8-level bar** |
| beyond 4 | 11 | 9.16 | 7.24 | **0.13** | **UNDER** |

Against the frame's own unlit-floor reference (6.6): the cap past the lamp sits **1.08 levels**
away from it. *"Caps read as unlit ground"* is 1.08 levels, measured.

### ⚠ And my own earlier number said this was fine

I reported `L(cap, floor) = 19.27 levels — CLEARS` at the standing station and relayed it as the
cap's ruled separation being met. **That figure is the ≤2 band, n = 2 cells** — the only band that
passes. Every cell further out fails, and a room's sides are mostly further out. The measurement
was correct; the reporting privileged the band that agreed with me. `measure_room_sides.py` reports
every band always, takes the **worst** cell rather than the mean (one side of a room that
disappears is a side that disappeared), and has no single-verdict summary to hide behind.

---

## 2. What the lever reaches — and where it collides with §3

Godot 2D is exactly multiplicative in albedo (0.5000, worst cell 0.0006), so every candidate rung
is computable from the capture on disk. **These are predictions, to be verified by capture when a
build is authorised.**

| cap rung | authored | 3–4 tiles vs floor | standing vs floor | rungs above the face | §3 `two_planes` |
|---:|---:|---:|---:|---:|---|
| 5 *(as built)* | 114.70 | 0.58 | 24.04 | 4 | ok |
| 4 | 101.47 | 4.28 | 24.04 | 3 | ok |
| **3** | **88.24** | **6.34** | 32.52 | 2 | **ok** |
| **2** | **75.02** | **8.39 ✓** | 41.01 | 1 | **BREAKS (needs ≥1.5)** |
| 1 | 61.79 | 10.45 ✓ | 49.49 | 0 | breaks |

**The bar is reached at rung 2, and §3 forbids rung 2.** The wall face is rung 1 (61.79) and
`two_planes` requires ≥1.5 rungs of separation, so the cap may go no lower than rung 3 — which
delivers **6.34 against a bar of 8.00**. The shortfall is **1.66 levels, one rung wide.**

**Within the scope as ruled — caps and N–S tops, face untouched — the remedy does not reach the
bar.** That is the finding, and it is why this is prepared rather than run.

**Past four tiles is unreachable at any rung**, which confirms the standing ruling rather than
challenging it: going darker moves the cap *through* the unlit floor (9.16 → 5.99 at rung 2),
ending up 1.25 levels below it instead of 1.92 above. Still under the bar, and arguably more
ground-like, not less. No ladder chase — as ruled.

---

## 3. Four ways out. None taken; the first is the cheapest and the third is the real one

**A — accept rung 3.** Sides return at 3–4 tiles to 6.34 levels, 79% of the bar. §3 intact, zero
new law touched, cost is one recompose. *Partial by construction.*

**B — move the face down with the cap.** Face rung 1 → 0 (48.56), cap rung 2 (75.02): 2 rungs
apart, `two_planes` clears, and 3–4 tiles delivers **8.39 ✓**. **This is outside the ruled scope**
— it changes the face the gate approved by eye — and it spends rung 0, which is one of the two
rungs the floor's keyline fix has just been ruled to use for its deep tail. See §4.

**C — give the sides a second plane, not a darker first one.** §12.1 says plane-boundary occlusion
is **form**, and occlusion is already drawn on E/W boundaries (measured: 3.55–4.09 levels of
darkening on the floor cell abutting a cap-only wall, against 31.56 at a face boundary — the same
~40% ratio, scaled by a lamp that is not there). The sides fail because they have no silhouette,
and every option above answers a silhouette problem with a brightness. This is
`MASS-READ-REMEDIES.md` §2's named fourth thing arriving on the sides:

> *"A wall that must say* you may not go here *at four tiles is asking for a silhouette, not a
> brightness — and every remedy above is a brightness."*

**It touches §3's construction, which rides provisional into this tier.** Not a builder's
suggestion.

**D — do nothing at 3–4 tiles and rule the sides dark-by-design**, as the past-lamp case already
is. Honest, free, and it means rooms have no sides beyond three tiles.

---

## 4. One thing to check before B, because two threads are about to crowd the same rungs

The floor's keyline fix is *"a joint-distribution reshape — mode under the perceptual floor,
minority tail to the deep rungs."* **The deep rungs are 0 and 1: 48.56 and 61.79.** The wall face
already sits at rung 1. Option B would put the face on rung 0 and the cap on rung 2.

So after both changes the floor's joint tail, the wall's face and the wall's cap would occupy
rungs 0–2 of a nine-rung ladder, in the same frame, under a lamp that compresses everything at
range. Wall-versus-floor separation is the quantity this whole round is about, and it is measured
between two families that would both be pushing into the same three rungs from opposite
directions. **Worth one measurement across both families before B is chosen**, and it cannot be
taken until #169 lands.

---

## 5. Questions

1. **Which of A–D**, given that the ruled scope reaches 6.34 against a bar of 8.00?
2. **Is B in scope?** It is the only option that clears the bar, and it costs the gate-approved
   face value and a rung the floor thread is about to occupy.
3. **Is the bar 8 levels here?** §13.8 calls 8 the *ambiguous* point. The sides are a
   navigational read — *where does the room end* — not a texture read, and an edge is more visible
   than a texture at equal contrast. If the sides' bar is lower than the material's, A clears it
   today. That is a human verdict on a measured quantity, which is the only way §13.8 permits a
   floor to exist.

## 6. What is ready to run the moment an answer lands

- `measure_room_sides.py`, **proven two-sided** (§13.5): a cap set to the floor's own value fails
  every band; a cap 40 levels off passes every band.
- The projection table above, which becomes the round's prediction to be confirmed or refuted by
  capture — a real test, not a restatement.
- `compose_cap.py --top-rung N` already exists, so A and the cap half of B are one flag.
- **Round 9 stays VOID and is not re-rolled.** Round 10 is a fresh round on a changed build, and
  it inherits the §1.1 STOP on the plant control: its seat verdict cannot be trusted in either
  direction until that control is replaced.
