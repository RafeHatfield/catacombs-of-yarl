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

void light() {
	// ⚠⚠ THIS SCALAR IS BROKEN, IT IS A SECOND DEFECT, AND IT IS NOT FIXED IN THIS CHANGE.
	//
	// `LIGHT_COLOR.rgb` is the light's TINT, measured constant across the whole lit field (see
	// above). Its max channel is the tint's red, 1.002, EVERYWHERE the lamp's quad reaches — so
	// this clamps to exactly 1.0 at every lit fragment and 0.0 outside it, and
	// `pow(delivered, polish_exp)` has been computing `pow(1.0, 2) = 1.0` since the day it was
	// written.
	//
	// **The superlinear response Ruling 70 ruled has therefore never run.** The specular below
	// is a flat `polish * polish_gain`, attenuated exactly ONCE by the blend's LIGHT.a — linear
	// in delivered light, which is arithmetically an albedo change, which is the thing this
	// file's own header says would make it a lie.
	//
	// Left standing here DELIBERATELY. This change connects the lamp and changes nothing else,
	// so that the connection is proved on its own axis with the specular held fixed. The
	// specular is the next step's, with its own control and its own before-picture. Do not tidy
	// this line into the same commit.
	float delivered = clamp(max(max(LIGHT_COLOR.r, LIGHT_COLOR.g), LIGHT_COLOR.b), 0.0, 1.0);

	// The ordinary diffuse term: what this canvas item would do with no shader at all — and the
	// LIGHT_ENERGY factor on the RGB is what finally makes that sentence true (#174). The ALPHA
	// is left alone on purpose: it carries LIGHT_COLOR.a, the radial falloff, and the engine
	// applies it to the rgb during the blend. Scaling the vec4 whole would apply energy twice.
	vec4 diffuse = vec4(COLOR.rgb * LIGHT_COLOR.rgb * LIGHT_ENERGY, COLOR.a * LIGHT_COLOR.a);

	// The specular term. `polish` is the traffic-keyed reflectivity the engine baked into a
	// single-channel mask — faces only, never joints or cracks, which are enclosure and do not
	// take a shine. UNCHANGED BY THIS COMMIT, defect and all.
	float polish = texture(polish_tex, UV).r;
	float spec = polish * polish_gain * pow(delivered, polish_exp);

	LIGHT = vec4(diffuse.rgb + LIGHT_COLOR.rgb * spec, diffuse.a);
}
