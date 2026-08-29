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

uniform sampler2D polish_tex : filter_nearest, repeat_disable;

// How much faster than linear. 1.0 would BE an albedo change and would make this file a lie, so
// the value is asserted below rather than trusted.
uniform float polish_exp = 2.0;
uniform float polish_gain = 1.0;

void light() {
	// The lamp's delivered strength at this fragment, as a scalar. LIGHT_COLOR already carries
	// the light's colour, its energy and the radial falloff texture, which is precisely the
	// "delivered" quantity §13.9 rules on — taken from the renderer rather than recomputed from
	// the rig's parameters, so it cannot drift away from what is actually on screen.
	float delivered = clamp(max(max(LIGHT_COLOR.r, LIGHT_COLOR.g), LIGHT_COLOR.b), 0.0, 1.0);

	// The ordinary diffuse term: what this canvas item would do with no shader at all.
	vec4 diffuse = COLOR * LIGHT_COLOR;

	// The specular term. `polish` is the traffic-keyed reflectivity the engine baked into a
	// single-channel mask — faces only, never joints or cracks, which are enclosure and do not
	// take a shine.
	float polish = texture(polish_tex, UV).r;
	float spec = polish * polish_gain * pow(delivered, polish_exp);

	LIGHT = vec4(diffuse.rgb + LIGHT_COLOR.rgb * spec, diffuse.a);
}
