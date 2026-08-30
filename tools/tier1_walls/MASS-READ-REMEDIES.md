# Mass-read at distance — three remedies, with numbers

**For the design thread, with the walk evidence beside it.** Nothing here is chosen; item (5) of
the gate ruling says the ruling happens there. What a builder can do is measure each remedy at the
two cases the gate named — **the standing case (≤2 tiles)** and **3–4 tiles** — and say what each
one costs and which laws it touches.

All numbers are Weber contrast on the lit capture at 1×, taken on `tier1_wall_standing`, which is
the gate scene's geometry with the player standing at the chokepoint mouth. Instrument:
`measure_mass_read.py`. The rig is the ratified one unless a row says otherwise.

---

## 0. First — the defect is not the one the ruling named, and the measurement says so

The gate's new requirement is *"wall mass beats void by a readable margin."* **Measured, it
already does, and by a long way:**

| separation | standing ≤2 | 3–4 tiles | beyond 4 |
|---|---:|---:|---:|
| **W(wall, void)** | **0.889** | **0.833** | **0.893** |
| **W(wall, floor)** | **−0.050** | **+0.038** | +0.219 |

*(compensated arm, the build walked at the gate)*

**Wall against void is 0.83–0.89 — six times the floor family's 0.1440 reference. Wall against
FLOOR is 0.04.** The thing a player cannot do is tell the wall from the ground, not tell it from
the dark, and that is exactly the comparison the seats kept making without being asked:

> *"at y=225, the 'solid wall' column at x=300 reads luminance 18. The open passage floor at
> x=405, same row, also reads 18. **Identical.**"*

⚠ **One qualification, because a ratio is not a level.** Wall-versus-void is 0.89 Weber and **8
delivered levels** — 9.4 against 1.1 of 255. Both are near-black in absolute terms, which is why a
seat could separate them by measurement and still say *"the image gives you no way to tell them
apart at 1:1."* If the perceptual-floor law is applied to mass-versus-nothing **as a ratio** the
requirement passes today; **as delivered levels** it is marginal. That distinction is the design
thread's to make and it changes which remedy matters.

---

## 1. The three remedies

### R1 — Move the rig (falloff / radius)

**What it does.** Flattening the falloff lifts everything the lamp reaches. At the ratified radius,
falloff 0.50 raises the four-tile legibility point from 0.156 to 0.338 **without spending the arc**
— the scene's declared dark points get *darker*, not brighter (0.060 → 0.056). Radius is the knob
that spends the arc: 6.5 drowns a declared dark point at 0.151 and the capture is refused.

**What it does for mass-read: nothing at the standing case, and it is measured rather than
argued.** The pipeline is exactly multiplicative in albedo, so the lamp scales wall and floor
together and their ratio is invariant:

| | W(wall, floor) standing | 3–4 tiles |
|---|---:|---:|
| ratified rig (falloff 1.00) | **−0.235** | −0.154 |
| falloff 0.50 | **−0.223** | −0.194 |

*(material arm, same scene, same cells)*

**Five thousandths at the standing case.** What the rig buys is REPRESENTABILITY — absolute levels,
so the material is not quantised away — and that is a real and separate good. It is not a mass-read
lever.

**Cost:** one table of numbers, no asset work, no engine work. **Laws touched:** §6.2 (re-gate of
Ruling 56 — ratified on the device by eye, so moving it is a walk, not an edit); §6.2.1's
re-derivation rule fires on every authored ratio derived against the old numbers.

### R2 — A light-response clamp on wall tiles in the renderer

**What it does.** Give wall cells a floor on delivered luminance independent of the lamp, so a wall
at five tiles does not fall to 9/255. This is the one remedy that changes W(wall, floor) *at
distance*, because it lifts the wall while the floor keeps falling.

**Delivered numbers: NOT MEASURED, and deliberately not estimated.** It does not exist, and a
number produced by arithmetic on a system nobody has built is the kind of evidence this project
has ruled against twice. What can be stated is the shape: the clamp's effect at the standing case
is zero by construction (the wall is already well above any floor you would set), and its effect
past four tiles is whatever the clamp value is.

**Cost:** engine work, and it is the expensive kind — a per-material light response is a renderer
feature, not a parameter. **Laws touched:** **§6.3 head-on.** *Assets are authored to RECEIVE
light, not to depict it* — a clamp is the asset declining to receive it. §6.2 names this option
already and has never costed it. It is the only remedy that puts a ruled clause at risk rather
than merely re-opening a ratified number.

### R3 — Author the wall DARKER than the floor, within the ladder

**What it does.** §6.5 as re-scoped requires the 2:1 separation between the wall's own two planes
at standing distance, and nothing about the wall's relationship to the floor. That frees the whole
stack to move down — and **down is the direction the ladder can actually reach.**

To deliver W(wall, floor) = +0.3 the top plane needs an authored ≈196, which is off the ladder
(top rung 154.38). To deliver **−0.3** it needs ≈105, which is rung 4. The asymmetry is the same
one §1 of `STACK-FINDING.md` measured from the other side: k_top ≈ 0.67 means brightness is
unreachable and darkness is cheap.

**And it is already built. It is the `material` arm.**

| arm | authored top | W(wall,floor) standing | 3–4 tiles | amplitude, standing (Weber / levels) |
|---|---:|---:|---:|---|
| `compensated` (rung 8) | 154.38 | −0.050 | +0.038 | 0.520 / 41.1 |
| **`material` (rung 5)** | **114.70** | **−0.235** | **−0.154** | **0.518 / 35.8** |

**The material arm separates wall from floor nearly five times better at the standing case**, is the only
arm above the 0.1440 reference in that band, and **matches the compensated arm on material
amplitude at every range measured from the standing station** (0.52 / 0.37 / 0.41 / 0.36 against
0.52 / 0.32 / 0.37 / 0.33).

⚠ **This reverses a recommendation this session made two days ago, and the reversal is the
measurement's, not a change of mind.** The earlier finding — *compensated holds 18.2 delivered
levels at three tiles where material holds −1.4* — was taken on the gate scene with the player in
the middle of a room, where every wall is four tiles or further. Measured at the standing case,
which is the case the gate has now ruled §6.5 down to, the ordering reverses. **The old number was
not wrong; it was an answer about the far field, read as an answer about walls.**

**Cost:** zero. Both arms are composed, instrumented and on disk. **Laws touched:** none —
§6.5 as re-scoped is silent about wall-versus-floor, and going darker is squarely inside the ladder
and inside §8.1 (*a wall is dark because it is enclosed*).

---

## 2. What none of the three reaches, named because it is the fourth thing

All three move a VALUE. The floor session, arriving at the same wall from the other side, named the
successor its own levers could not reach:

> *"a floor that must state its route needs a signal the falloff does not multiply — geometry
> breaking the silhouette, an object, a change of plane."*

Mass-read has the same shape. A wall that must say *you may not go here* at four tiles is asking
for a silhouette, not a brightness — and every remedy above is a brightness. **This is named, not
proposed:** it is a change to §3's two-plane construction, which is the clause riding provisional
into this tier, and it is not a builder's suggestion.

---

## 3. The recommendation, stated so it can be disagreed with

**R3, at zero cost, and it is already sitting on disk.** Take the `material` arm to the walk; it is
five times better at the one distance the stack law now lives at, and it costs nothing to try
because it is built.

**R1 second, for a different job.** The falloff lever buys representability past four tiles and
does not spend the arc. It is not a mass-read fix and should not be sold as one.

**R2 last, and only if the walk says R3 is not enough.** It is the only one that touches a ruled
clause head-on, and §6.3 has been ratified once already on a probe that was expensive to run.

**And the requirement as ruled needs one decision before it can be tested:** wall-versus-void is
0.89 as a ratio and 8 levels as an absolute. Which of those the perceptual-floor law means for
mass-versus-nothing decides whether the requirement is already met or barely met.
