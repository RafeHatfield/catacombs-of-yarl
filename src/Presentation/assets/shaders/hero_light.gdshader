shader_type canvas_item;

// THE HERO'S LIGHT RESPONSE — warmest thing on screen, never the brightest.
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
// ── ⚠ RE-DERIVED 2026-09-08: 0.70 → 0.68, BECAUSE THE FLOOR MOVED ────────────────────────────
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
uniform float hero_knee = 0.55;
uniform float hero_ceiling = 0.68;

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
