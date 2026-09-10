shader_type canvas_item;

// POLISH AS LIGHT RESPONSE — the trodden floor answers the lamp.
//
// RULED (Rafe, 2026-08-29), and the distinction this file exists to honour:
//
//     BAKED VALUE-LIFT is banned (§8.2.1). Painting a trodden stone brighter makes it brighter
//     everywhere, including in the dark where nobody is, and it reads as wear that was drawn on.
//     An albedo change is that: under a purely multiplicative rig, `(albedo + d) * (ambient +
//     light)` spends its delta uniformly across every illumination in the room.
//
//     ENGINE RESPONSE MODULATION is legal, and it is a different thing arithmetically, not just
//     rhetorically. This shader touches ONLY the light() pass. It contributes nothing to the
//     ambient pass — a polished stone and a rough one are the same stone in the dark — and its
//     contribution rises FASTER THAN LINEARLY with the light actually delivered to that fragment.
//
// So the signal is concentrated exactly where §13.9 says signal survives, and it is absent
// exactly where §13.9 says it would be wasted. That is not a workaround for the perceptual floor;
// it is the physics of a polished surface, which is why it was available all along.
//
// Dark illegibility is accepted by design (same ruling): the floor is not required to state its
// route into a part of the room the player is not standing in.
//
// ══════════════════════════════════════════════════════════════════════════════════════════════
// ISSUE #174 — THE LAMP IS ONE QUANTITY. Fixed here; do not un-fix it.
//
// This file used to compute its light without ever mentioning LIGHT_ENERGY, under a comment
// asserting that "LIGHT_COLOR already carries the light's colour, its energy and the radial
// falloff texture." It carries the colour. It carries the falloff, in a channel the comment did
// not name. IT DOES NOT CARRY THE ENERGY, and a custom light() that never mentions LIGHT_ENERGY
// simply discards it — while the DEFAULT light pass, which every wall, cap, binding and prop in
// the scene runs because none of them carries a ShaderMaterial, applies it.
//
// The consequence was not a brightness offset. **Every floor tile in the game was lit at energy
// 1.0 while the wall standing next to it was lit at Ruling 56's 1.6** — two planes resolved
// through two different expressions. Measured before the fix on the composed room, sweeping the
// lamp 0 / 1.6 / 8.0: 97.1% of floor pixels BYTE-IDENTICAL across the whole sweep against 59.1%
// of wall pixels, and at energy 0 — the "lighting is live" positive control — the floor at the
// lamp still read 70.07 where the wall beside it read 1.00. The control that proves the lighting
// is live was being passed by a surface that could not see it.
//
// AND IT COULD NOT BE DIVIDED OUT, which is why the fix is here and not in a calibration table:
// no cross-plane ratio taken under it survives a rescale. Bible §6.5's every measured figure was
// VOIDED rather than adjusted for exactly this reason; §6.2 carries the asterisk.
//
// ── AND THE FIX IS NOT THE ONE THE ISSUE DESCRIBES, because LIGHT_COLOR is not one quantity ───
//
// MEASURED on this engine (`tools/tier1_floors/SHADER-SEMANTICS.md`), not assumed, because the
// first attempt at this fix wrote `COLOR * LIGHT_COLOR * LIGHT_ENERGY` and measured a QUADRATIC
// energy response on a floor whose walls were linear:
//
//     LIGHT_COLOR.rgb   the light's TINT and nothing else. Constant ffb066 = (1.002, 0.696,
//                       0.423) at 2.2, 3.2 and 4.5 tiles alike, and (0,0,0) outside the light's
//                       own quad. NO falloff in it, NO energy in it.
//     LIGHT_COLOR.a     the radial falloff texture. 0.574 at the cell measured.
//     LIGHT_ENERGY      the energy, exactly: reads 0.400 at energy 0.4, 0.815 at 0.8.
//     the blend         THE ENGINE MULTIPLIES THE SHADER'S LIGHT.rgb BY LIGHT.a. So a vec4
//                       scaled whole is scaled TWICE, which is where the quadratic came from.
//
// So `* LIGHT_ENERGY` goes on the RGB ONLY and the alpha keeps carrying the attenuation. The
// diffuse term is then albedo x tint x energy, attenuated once by the blend — which is exactly
// what a wall with no ShaderMaterial does. That, and only that, is what "one arithmetic" means,
// and it is checked rather than asserted: with the specular nulled, floor and wall must respond
// to a doubling of the lamp by the same factor. `measure_energy_response.py`, section 3.
// ══════════════════════════════════════════════════════════════════════════════════════════════

uniform sampler2D polish_tex : filter_nearest, repeat_disable;

// How much faster than linear. 1.0 would BE an albedo change and would make this file a lie, so
// the value is asserted below rather than trusted.
uniform float polish_exp = 2.0;
uniform float polish_gain = 1.0;

// ══════════════════════════════════════════════════════════════════════════════════════════════
// THE HIGHLIGHT SHOULDER — RULED (Rafe, 2026-09-07). "The ceiling is a curve, not a knob."
//
// Round 30's blind seat: *"The lit floor is blown out ... a flat pale block roughly 110x28 px with
// no interior texture."* Measured in that block: **11.0% of pixels have RED pinned at 255** while
// blue peaks at 176, and 2,044 pixels have red pinned while green is not. The Boundary's lamp is
// `ffb066` — red 1.0 — so the red channel saturates first, and where it does the stone loses its
// texture IN ITS DOMINANT CHANNEL and shifts hue toward the light at the same time.
//
// THE RIG IS NOT THE LEVER. Ruling 56 was re-ratified on 2026-09-06 and energy, radius, falloff
// and ambient STAND (§13.2 — the eye that walked it owns it). The seat asked for the floor's peak
// to be pulled down; that is refused under §13.4.1, a seat is a proxy for the gate and not a vote
// against it. What moves instead is the shape of the TOP END, which no knob expresses: the walk
// itself asked for the ceiling to be reached "asymptotically instead of saturating", and there was
// no such control. This is it.
//
// THE CURVE. Identity below the knee, then an exponential roll-off asymptotic to the ceiling:
//
//     x <= knee            y = x                                    (nothing below the knee moves)
//     x >  knee            y = knee + d * (1 - exp(-(x-knee)/d)),  d = ceiling - knee
//
// C1-continuous at the knee — its derivative there is exactly 1 — so no band appears where the
// compression starts. It never reaches the ceiling, which is the point: values that used to pin
// at 255 land distinct instead of equal, and the joints come back because their contrast is
// compressed rather than deleted.
//
// APPLIED HUE-PRESERVING, ON THE CHANNEL THAT CLIPS FIRST. The magnitude is taken from the max
// channel and every channel is scaled by the same factor, so the warm lamp cannot bleach a stone
// toward its own colour on the way to the ceiling. Scaling channels independently would fix the
// texture and keep the hue shift, which is half the defect.
//
// AND IT IS MEASURED POST-ATTENUATION. The engine multiplies LIGHT.rgb by LIGHT.a, so the value
// that actually lands is `max(lit) * alpha` — shouldering the pre-attenuation magnitude would
// compress the far field, which is nowhere near the ceiling and must not move at all.
//
// ⚠ ONE ARITHMETIC IS PRESERVED, AND THIS IS THE #174 TRAP RESTATED. Only the floor carries a
// ShaderMaterial, so a term that bit ANYWHERE both planes operate would re-open #174 in a new
// disguise. It cannot: below the knee this function is the identity, exactly — `s/m` is 1.0 by
// construction — and the walls' delivered maximum is 93 against the floor's 249, so no wall
// fragment in this scene is within reach of the knee. THE LATENT CASE IS NAMED RATHER THAN
// ASSUMED AWAY: if a future surface did approach the knee without this shader, it would clip
// while the floor rolled off. The honest fix then is to give that surface the same light(), not
// to widen this one.
//
// Null control: set the knee above any reachable value (10.0) and the function is the identity
// everywhere, which is how the round proves what it contributed.
uniform float shoulder_knee = 0.75;
uniform float shoulder_ceiling = 0.92;

// ── #198: AN ADDITIVE SPECULAR DESTROYS CONTRAST; A PROPORTIONAL ONE PRESERVES IT ────────────
//
// The halo is not a blur and there is nothing soft in the source art. It is the floor's own
// texture LOSING RELATIVE CONTRAST exactly where the light is strongest, which reads as a
// smeared pool with no edge and no cause. Measured by null control on the shipped build, as
// mean|grad| / mean luminance over floor cells, core (0.5-1.2 tiles) against mid-field
// (2.0-2.8):
//
//     as shipped      0.677     the light costs the surface a third of its contrast
//     shoulder null   0.819     the shoulder compresses: |grad| 7.72 -> 11.03, mean 156 -> 173
//     specular null   0.858     the specular dilutes: |grad| 7.72 -> 8.63, mean 156 -> 124
//
// The two signatures are different and that is what identifies them. Nulling the SHOULDER lifts
// absolute variation and the mean together — a compression released. Nulling the SPECULAR barely
// moves absolute variation while dropping the mean 20% — a term that was adding LIGHT WITHOUT
// ADDING TEXTURE. That is the larger of the two, and it is the one this fixes.
//
// Weber is the whole argument. A term added to every fragment of a face alike raises the
// denominator and leaves the numerator, so contrast falls by exactly the share the term carries
// — 18.8% of delivered value at the standing case, which is where the frame reads flattest. A
// term PROPORTIONAL to what the fragment already is multiplies both and contrast survives.
//
// ⚠ THE MAGNITUDE IS NOT BEING RETUNED, ONLY ITS DISTRIBUTION. The scale is normalised by the
// family's own median albedo, so a fragment at the median gets exactly what it got before, the
// mean specular contribution over the surface is preserved, and #184's measured specular share
// is not quietly moved by a change that claims to be about texture. Above the median a stone
// takes more shine, below it less — which is also what a worn face does.
//
// Null control: `spec_shade = 0.0` is the identity, byte-for-byte the term this replaces.
uniform float spec_shade = 1.0;
uniform float albedo_median = 0.446;

void light() {
	// THE DELIVERED-LIGHT SCALAR — the fraction of full illumination this fragment actually
	// receives, and the quantity §13.9 rules on.
	//
	// IT USED TO BE `max(LIGHT_COLOR.rgb)` AND THAT WAS A SECOND DEFECT, INDEPENDENT OF #174.
	// LIGHT_COLOR.rgb is the light's TINT and nothing else — measured constant at
	// (1.002, 0.696, 0.423) across the whole lit field — so its max channel is the Boundary's
	// saturated red, 1.002, at EVERY lit fragment. `pow(delivered, polish_exp)` was computing
	// `pow(1.0, 2) = 1.0` from the day it was written, and **Ruling 70's superlinear response
	// never ran**: the specular was a flat `polish * polish_gain`, attenuated exactly once by
	// the blend, which is linear in delivered light — arithmetically an albedo change, the one
	// thing this file's header says would make it a lie. Measured from the other side too: with
	// the polish live the floor's energy exponent was indistinguishable from the nulled arm
	// (1.992 against 1.989), and the polish still contributed 11.0 levels AT ENERGY ZERO.
	//
	// The attenuation lives in LIGHT_COLOR.a and the energy in LIGHT_ENERGY, so that is what the
	// scalar is built from. Clamped to [0,1] because it is a FRACTION of full delivery and the
	// superlinearity is defined on that interval; above the ratified 1.6 the near field is at
	// full delivery and the exponent stops biting, which is the correct behaviour for a
	// reflectivity and not a cap bolted on to tame it.
	//
	// Two properties this restores, both checked as controls rather than claimed:
	//   - at energy 0 a polished stone and a rough one are THE SAME STONE (this file's header);
	//   - the specular's share of delivered value falls off FASTER than the diffuse's (Ruling 70).
	float delivered = clamp(LIGHT_COLOR.a * LIGHT_ENERGY, 0.0, 1.0);

	// The ordinary diffuse term: what this canvas item would do with no shader at all — and the
	// LIGHT_ENERGY factor on the RGB is what finally makes that sentence true (#174). The ALPHA
	// is left alone on purpose: it carries LIGHT_COLOR.a, the radial falloff, and the engine
	// applies it to the rgb during the blend. Scaling the vec4 whole would apply energy twice.
	vec4 diffuse = vec4(COLOR.rgb * LIGHT_COLOR.rgb * LIGHT_ENERGY, COLOR.a * LIGHT_COLOR.a);

	// The specular term. `polish` is the traffic-keyed reflectivity the engine baked into a
	// single-channel mask — faces only, never joints or cracks, which are enclosure and do not
	// take a shine.
	float polish = texture(polish_tex, UV).r;
	float spec = polish * polish_gain * pow(delivered, polish_exp);

	// #198. The stone's own value, relative to the family's median, scales the shine. Clamped at
	// 2.0 so a blown texel cannot double the term, and mixed by `spec_shade` so the null is exact.
	float albedo = dot(COLOR.rgb, vec3(0.2126, 0.7152, 0.0722));
	float shade = clamp(albedo / max(albedo_median, 1e-4), 0.0, 2.0);
	spec *= mix(1.0, shade, spec_shade);

	vec3 lit = diffuse.rgb + LIGHT_COLOR.rgb * spec;

	// THE SHOULDER. `m` is what actually lands: the first channel to clip, after the blend's
	// alpha. Below the knee `s == m` and the scale is exactly 1.0, so those fragments are
	// byte-identical to the un-shouldered build — which the round proves rather than asserts.
	float a = diffuse.a;

	// ── #198: THE SCALE IS COMPUTED FROM THE LIGHT, NOT FROM THE COMPOSITE ───────────────────
	//
	// `m` used to be `max(lit) * a` — the composite, albedo included. That makes the compression
	// a function of HOW BRIGHT THE STONE IS, so a pale stone is squashed harder than the dark one
	// beside it and the difference between them shrinks. That difference is the surface's texture,
	// and losing it exactly where the light is strongest IS the halo this issue is about.
	//
	// Measured, on this build: the shoulder costs 0.137 of the core-to-mid contrast ratio (0.644
	// with it, 0.781 without). The KNEE is not the lever — 0.75 to 0.88 buys 0.014 — because the
	// knee only decides where compression starts; the CEILING decides how hard, and everything
	// above the knee is pulled toward it whatever its albedo.
	//
	// ⚠ AND THE SHOULDER MUST NOT SIMPLY GO. Nulled, the floor's p99 leaps 205.50 -> 247.85 and
	// 1324 pixels pile within two levels of the max — the flat top §6.2 exists to prevent. So the
	// question is not whether to roll the top end off but WHAT TO MEASURE IT ON.
	//
	// Measuring it on the DELIVERED LIGHT makes the scale a function of distance from the lamp
	// rather than of albedo: two neighbouring stones at the same range get the SAME scale, so
	// their ratio survives untouched, while the pool's top end still rolls off because the light
	// itself does. It is the same argument the specular fix runs — multiplying preserves Weber
	// contrast, and anything that varies with albedo destroys it.
	float ml = clamp(delivered, 0.0, 1.0);
	float sl = ml;
	if (ml > shoulder_knee) {
		float d = max(shoulder_ceiling - shoulder_knee, 1e-4);
		sl = shoulder_knee + d * (1.0 - exp(-(ml - shoulder_knee) / d));
	}
	lit *= (ml > 1e-6) ? (sl / ml) : 1.0;

	LIGHT = vec4(lit, a);
}
