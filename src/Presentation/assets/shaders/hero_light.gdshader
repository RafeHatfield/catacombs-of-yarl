shader_type canvas_item;

// THE HERO'S LIGHT RESPONSE — warmest thing on screen, and NEVER BLOWN.
//
// ⚠ THE TITLE USED TO READ 'never the brightest'. That reading was OVERTURNED at
// the human gate on 2026-09-09 and is corrected here rather than left standing in
// a file whose numbers now contradict it.
//
// ISSUE #183, ruled by Rafe at the 2026-09-06 rig walk: *"the hero should receive LESS of the
// lamp's top end than the ground does."* That is a light-response term on the sprite — the same
// class of thing `tier1_polish.gdshader` is for the floor — and explicitly NOT a rig change and
// NOT an albedo repaint. §6.2.1 exists to stop a character decision being made inside a region's
// lighting law, so the rig does not move for this and neither does the floor.
//
// ── WHAT WAS MEASURED, on the ratified rig (r6.0 / falloff 1.00 / ambient 1.50 / energy 1.6) ──
//
// The issue records the sprite's p95 as sitting within a level of the floor beside him. On the
// combined frame it is worse than that: the hero's cell reads p95 242.7 and max 250.0 against
// the lit floor either side of him at p95 203.5 and 207.4. He is not level with the ground —
// HE IS ABOUT FORTY LEVELS ABOVE IT, and the brightest thing in the picture. The clause he
// breaks is not a near-miss.
//
// ── THE CURVE IS THE FLOOR'S, WITH A LOWER CEILING ────────────────────────────────────────────
//
// §6.2's highlight shoulder is already the ruled shape for "reach the top end asymptotically
// instead of saturating", and it is C1-continuous at the knee so no band appears where the
// compression starts. This is that curve with the ceiling set BELOW the lit ground's peak, which
// is the whole of the ruling: the hero asymptotes to a value the floor is allowed to exceed.
//
//     x <= knee     y = x                                    nothing below the knee moves
//     x >  knee     y = knee + d * (1 - exp(-(x-knee)/d)),   d = ceiling - knee
//
// HUE-PRESERVING, on the channel that clips first. The magnitude is taken from the max channel
// and every channel is scaled by the same factor, so pulling the top end down cannot bleach him
// toward the lamp's colour on the way — which would cost exactly the warmth the ruling wants
// kept. Scaling channels independently would darken him and desaturate him at once.
//
// POST-ATTENUATION, because the engine multiplies LIGHT.rgb by LIGHT.a: the value that actually
// lands is `max(lit) * alpha`. Shouldering the pre-attenuation magnitude would compress the hero
// at every range, including out at the arc's edge where he is already dark and must not move.
//
// ── #174'S TRAP, RESTATED, BECAUSE THIS IS A SECOND SURFACE WITH A CUSTOM light() ─────────────
//
// `tools/tier1_floors/SHADER-SEMANTICS.md`, measured on this engine rather than read off a doc:
//
//     LIGHT_COLOR.rgb   the TINT alone. Constant over the light's quad, zero outside it.
//     LIGHT_COLOR.a     the radial falloff. This is where attenuation lives.
//     LIGHT_ENERGY      the energy, exactly.
//     the blend         contribution = LIGHT.rgb * LIGHT.a, added.
//
// So the energy goes on the RGB ONLY. A `vec4` scaled whole is scaled twice and yields a
// QUADRATIC response — which is what the first attempt at #174 shipped on the floor, and it is
// the reason every cross-plane figure in bible §6.5 was voided rather than adjusted. The diffuse
// line below is byte-for-byte the arithmetic a sprite with no ShaderMaterial already runs, so
// with the shoulder inactive this file is the identity and the hero is lit exactly as before.
//
// NULL CONTROL: `hero_knee` above any reachable value (10.0) makes the function the identity
// everywhere, which is how the round proves what the term contributed.

// CHOSEN BY SWEEP, on the hero's OWN pixels rather than on his cell — the cell block's p95 is
// floor, because the sprite is smaller than the tile it stands on, and it clamped to the floor's
// value at every setting. His pixels are isolated against the null arm: the 950 that move are
// exactly the ones his material lights, and none of them is outside his cell.
//
//   ceiling   sprite p95   sprite max   vs floor max (207.51)   vs floor p95 (203.51)
//   null        249.13       249.98          +42.47                  +46.47
//   0.85        198.92       220.43          +12.92                  +16.92
//   0.78        187.00       212.78           +5.26                   +9.26
//   0.74        179.74       207.00           -0.51                   +3.49   a photo finish
//   0.70        172.18       200.23           -7.28                   -3.28   <- ratified here
//   0.66        164.33       192.28          -15.24                  -11.24   going dim
//
// 0.70 is the first setting where his brightest pixel sits below BOTH the lit ground's peak and
// its p95, which is what "never the brightest" has to mean if it is to be checkable. 0.74 clears
// the peak by half a level and still sits above the p95 — a tie is not an answer to this clause.
//
// ══ ⚠ OVERTURNED AT THE HUMAN GATE — RULED (Rafe, 2026-09-09), §13.4.1 ══════════════════════
//
//     "#183 cap overturned at the human gate: the hero reads LIT — sprite peak above the lit
//      floor beside him, below the shoulder's knee (no clipping, real separation). Nine seats
//      across four panels are the evidence; 'warmest never brightest' meant 'never blown,' not
//      'darker than the ground.'"
//
// EVERYTHING BELOW THIS LINE IS SUPERSEDED AND KEPT. The table, the 0.70, the 0.68 — all of it
// derived a ceiling from the reading that the sprite must sit UNDER the ground's peak. That
// reading is now ruled wrong, and the evidence against it is the strongest this loop has
// produced: four independent panels, nine seats, none of which had seen the clause, all naming
// the same consequence — "darker than the ground he stands on", "within one value step of the
// floor", "loses its silhouette ... the lantern never produces a highlight", "the lamp has no
// core". §13.4.1 says a seat is not a vote against a gate ruling, and it was applied correctly
// each time; but the HUMAN GATE outranks both, and it has now ruled.
//
// ── WHAT THE OLD DERIVATION ACTUALLY MISSED: THE PLATEAU WAS CLIPPING ────────────────────────
//
// `m` is `max(lit) * alpha` and CAN EXCEED 1.0 before the engine clamps it. At the null, 72 of
// the hero's 820 delivered pixels — 8.8% — sit within two levels of his max of 251.82, and his
// p95 is 251.32. That is not a highlight, it is a flat top: the clamp had eaten his top end and
// the sprite had nowhere to go. A shoulder applied BEFORE the clamp is precisely the instrument
// for that, and it works — every capped arm below cuts the plateau from 72 pixels to 16.
//
// So the clause was always about BLOWING, and the old ceiling answered it by moving the whole
// figure down instead of by rolling his top end off. Both bounds now, measured on his own 820
// pixels isolated against the null arm, against the lit floor either side of him (p50 179.91,
// p95 202.50, max 206.50):
//
//   knee  ceil   his p50   his max   UP: vs floor max   DOWN: floor max - his p50   blown px
//   null          193.49    251.82        +45.32                +13.01                 72
//   0.80  0.84    179.99    239.61        +33.11                +26.51                 16
//   0.80  0.88    183.41    246.47        +39.97                +23.09                 16   <-
//   0.80  0.92    185.55    249.89        +43.39                +20.95                 16
//   0.86  0.94    190.55    251.32        +44.82                +15.95                 16
//
// SEPARATION IS MEASURED BOTH WAYS, as the ruling asks. UP is whether he reads as the light:
// his peak against the ground's own peak. DOWN is whether he is still a figure standing in his
// light rather than a lantern-shaped blob: the ground's peak against his median. A pair that
// wins upward by losing downward has not answered the clause, it has inverted it.
//
// 0.80 / 0.88 IS TAKEN, and the knee is the load-bearing half. 0.80 is 204 of 255 and his body's
// median sits at 193 — BELOW THE KNEE, so the shoulder does not touch the figure at all; it
// touches only the top end that was clipping. That is the ruling's "below the shoulder's knee"
// in the only sense the curve permits: what a viewer reads as the figure never enters
// compression. The ceiling then buys separation — his peak clears the ground's peak by 40 levels
// and its own p95 by 44 — while leaving 8.5 levels of headroom under the null, so nothing sits
// near the clamp. 0.84 puts his body level with the ground but spends 7 levels of separation for
// it; 0.92 and 0.94 buy 3 more levels of separation and give back the headroom.
//
// ══ SUPERSEDED BELOW ═══════════════════════════════════════════════════════════════════════
//
// ── RE-DERIVED 2026-09-08: 0.70 → 0.68, BECAUSE THE FLOOR MOVED ─────────────────────────────
//
// The table above is measured against a floor reading p95 203.51 / max 207.51. The polish stack
// lowered it — #184 took the worn lane's shine down and #198 made the specular proportional —
// and the lit floor either side of him now reads **p95 202.50 / max 206.50**. At the same 0.70
// his brightest pixel measures **202.55: +0.05 ABOVE the floor's p95**, so the clause this file
// exists to enforce had quietly stopped holding. Nobody touched the hero; his comparator moved
// under him.
//
// This is §6.2's re-derivation rule, not a retune: a derived number moves when its input moves,
// and the input here is the ground he must not out-shine. Re-swept on the current build, his own
// 950 pixels isolated against the null arm:
//
//   ceiling   his p50   his p95   his max   vs floor p95   vs floor max   ruling held
//   0.70       151.30    175.96    202.55        +0.05          -3.95         NO
//   0.68       148.24    173.25    198.70        -3.80          -7.80         yes   <- here
//   0.66       145.81    169.96    194.56        -7.94         -11.94         yes
//
// 0.68 is again the FIRST value that clears both, which is the same derivation rule that chose
// 0.70, applied to the numbers as they now are.
//
// ── AND WHAT A BLIND SEAT ASKED FOR HERE IS THE INVERSE OF THE RULING (§13.4.1) ───────────────
//
// Round r001-polish-198-halo put four of its seven flips on this term:
//
//     "The figure carrying the only light is darker than the ground he stands on ... the sprite
//      must be the brightest thing in its own pool, above the floor value, not 70 below it."
//
// That is a well-observed percept and an exact contradiction of *"the hero should receive LESS
// of the lamp's top end than the ground does"* — Rafe, 2026-09-06. §13.4.1: a seat is a proxy
// for the gate, not a vote against a gate ruling.
//
// It was also worth checking rather than waving away, and the check is recorded because it
// closes a door: THE KNEE IS NOT A WAY TO GIVE THE SEAT WHAT IT WANTS. Swept at the ruled
// ceiling, his median moves 151.30 → 153.66 across knees 0.55 → 0.69 and stops, because with
// the asymptote at 0.70 everything above the knee lands in [knee, 0.70] however high the knee
// is. His body sits 42 levels below the null BECAUSE OF THE CEILING, and the ceiling is the
// ruling. There is no builder setting that answers the flip; only Rafe can, by moving it.
// ── #183 RE-SCOPED — RULED (Rafe, 2026-09-11). READ THIS BEFORE TOUCHING ANYTHING BELOW. ─────
//
//     "the hero light-response engine term stays (Sasha inherits it); all hero-appearance work
//      stops — the current sprite is the Oryx placeholder and is not worked; close the
//      placeholder-look flags as N/A; no hero rounds until the Sasha session against his card."
//
// THE TERM IN THIS FILE IS THE PART THAT STAYS. It is a LIGHTING law — how a figure receives
// the Boundary's lamp — and it belongs to the region, not to whoever is standing in it. Sasha
// inherits it unchanged when she arrives. Nothing below is placeholder work.
//
// WHAT STOPS IS EVERY QUESTION ABOUT HOW THE FIGURE LOOKS. The sprite this lights is the ORYX
// PLACEHOLDER. It is not Sasha, it is not being designed, and its palette, silhouette, gear and
// readability are not open questions — they are answered by a session that has not happened yet,
// against a card that exists.
//
// ⚠ SO A SEAT FLAGGING THE FIGURE'S APPEARANCE IS DISPOSED N/A, NOT ROUTED. That is a new
// disposition state for exactly this class and it is not a way to duck criticism: a flip about
// the LIGHT on the figure is still live and still routes here. The line is what the flip is
// about — exposure and value response belong to this file; colour, shape and kit belong to a
// character nobody has drawn yet.
//
// The morgue's `lamp-clip-figure.png` plant carries the same distinction in its own entry: it
// is planted for the lamp destroying its subject, and a seat catching it for the placeholder's
// art has caught it for the wrong reason (§4.2).

uniform float hero_knee = 0.80;
uniform float hero_ceiling = 0.88;

void light() {
	// The ordinary diffuse term — what this sprite would do with no shader at all.
	vec4 diffuse = vec4(COLOR.rgb * LIGHT_COLOR.rgb * LIGHT_ENERGY, COLOR.a * LIGHT_COLOR.a);

	float a = diffuse.a;
	float m = max(max(diffuse.r, diffuse.g), diffuse.b) * a;
	float s = m;
	if (m > hero_knee) {
		float d = max(hero_ceiling - hero_knee, 1e-4);
		s = hero_knee + d * (1.0 - exp(-(m - hero_knee) / d));
	}
	vec3 lit = diffuse.rgb * ((m > 1e-6) ? (s / m) : 1.0);

	LIGHT = vec4(lit, a);
}
