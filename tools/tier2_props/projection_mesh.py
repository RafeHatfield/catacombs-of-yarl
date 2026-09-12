#!/usr/bin/env python3
"""THE CANDIDATES AS A PROJECTION, NOT A DRAWING — every archetype is a small 3D model, and each
candidate is a function from (x, depth, height) to the screen. The template a generation is
handed is that function applied to that model, so a candidate is defined once and applied to a
box, a cylinder and a shelf unit identically. The barrel's lid under oblique is the true skewed
ellipse, because that is what the function does to a circle.

WHY THIS EXISTS. The Pro probe (sets/OL_chest, sets/OL_barrel) showed the generator ignores a
projection reference AND a projection instruction: 16 of 16 chests came back in its own 3/4 view
receding RIGHT against a template and a prompt that both said LEFT; 16 of 16 barrels came back
straight-on. Its view prior wins. The img2img probe (probes/) showed geometry HOLDS at
init_image_strength >= 150 and is lost by 90, and that at 150 the generator adds almost no
object — a box stays a box. So the structure — every band, hoop, plate and shelf — has to be in
the template, and generation is asked only for surface. Bible §13.7 said so about walls;
this is the same law arriving at props.

World axes: x to the right, d INTO the scene (north, away from the viewer), z UP. Units are
art pixels at 2x (the generator's canvas). The front face is the south face, d = 0.

    W        (x, d, z) -> (x,              -(z + kW*d))          kW = 0.31, no horizontal run
    O-L      (x, d, z) -> (x - k*d,        -(z + k*d))           k = 1/3   receding up-LEFT 45°
    O-R      (x, d, z) -> (x + k*d,        -(z + k*d))           k = 1/3   receding up-RIGHT 45°
    O-deep   as O-R with k = 1/2
    A        (x, d, z) -> ((x - d)*c,      -(z*cz + (x + d)*c/2))  2:1 dimetric, turned 45° in plan

"Depth k" is the receding RUN ON EACH SCREEN AXIS as a fraction of true depth — the way a pixel
artist steps a 45° receding edge (k of the depth across, k of the depth up). Stated because the
other reading (projected edge LENGTH = k * depth) gives a run of k/sqrt2 and a visibly shallower
side; the brief's "~1/3" and "~1/2" are taken on the per-axis reading and the doc says so.

Faces are flat-shaded by orientation only — up-facing lightest, viewer-facing middle, sideways
darkest — because the generator needs to tell the planes apart. That is a DIAGRAM convention,
not a light: §6.3 forbids a baked key light in shipped art and none of this ships.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

KW = 0.31            # W's top:face proportion, from the props manifest (top_rows 10 of 32)
DEPTH = {"OL": 1.0 / 3, "OR": 1.0 / 3, "Odeep": 0.5, "RULED": 0.5}
SIDE = {"OL": -1.0, "OR": +1.0, "Odeep": +1.0, "RULED": +1.0}
# RULED (Rafe, on device, 2026-09-12; bible §3.2): cabinet oblique, receding RIGHT, k = 1/2 per
# screen axis — the geometry of the build walked as projOdeep. Every object in the game is
# generated from a template rendered through this function. Round objects are the exception
# (true-circle top, vertical body): see round_exception() below.
A_C, A_CZ = 0.72, 0.85


def project(cand, p):
    x, d, z = p
    if cand == "W":
        return (x, -(z + KW * d))
    if cand in DEPTH:
        k, s = DEPTH[cand], SIDE[cand]
        return (x + s * k * d, -(z + k * d))
    if cand == "A":
        return ((x - d) * A_C, -(z * A_CZ + (x + d) * A_C / 2))
    raise ValueError(cand)


# ── primitives: lists of (polygon-in-world, kind, part) ─────────────────────────────────────
def box(x0, x1, d0, d1, z0, z1, part="body"):
    """Six faces, outward, as (points, kind, part). kind: top/bottom/front/back/left/right."""
    P = lambda x, d, z: (x, d, z)
    return [
        ([P(x0, d0, z1), P(x1, d0, z1), P(x1, d1, z1), P(x0, d1, z1)], "top", part),
        ([P(x0, d0, z0), P(x0, d1, z0), P(x1, d1, z0), P(x1, d0, z0)], "bottom", part),
        ([P(x0, d0, z0), P(x1, d0, z0), P(x1, d0, z1), P(x0, d0, z1)], "front", part),
        ([P(x1, d1, z0), P(x0, d1, z0), P(x0, d1, z1), P(x1, d1, z1)], "back", part),
        ([P(x0, d1, z0), P(x0, d0, z0), P(x0, d0, z1), P(x0, d1, z1)], "left", part),
        ([P(x1, d0, z0), P(x1, d1, z0), P(x1, d1, z1), P(x1, d0, z1)], "right", part),
    ]


def cylinder(cx, cd, r_of_z, z0, z1, n=32, rings=8, part="body"):
    """A vertical solid of revolution; r_of_z(z) gives the radius (a barrel bulges)."""
    faces = []
    zs = [z0 + (z1 - z0) * i / rings for i in range(rings + 1)]
    def ring(z):
        r = r_of_z(z)
        return [(cx + r * math.cos(2 * math.pi * i / n), cd + r * math.sin(2 * math.pi * i / n), z)
                for i in range(n)]
    rs = [ring(z) for z in zs]
    faces.append((rs[-1], "top", part))                    # counter-clockwise in (x, d), like box()
    faces.append((list(reversed(rs[0])), "bottom", part))
    for k in range(rings):
        a, b = rs[k], rs[k + 1]
        for i in range(n):
            j = (i + 1) % n
            ang = 2 * math.pi * (i + 0.5) / n
            # side facet: classify by its outward normal for shading
            nx, nd = math.cos(ang), math.sin(ang)
            faces.append(([a[i], a[j], b[j], b[i]], ("curved", nd), part))
    return faces


def null_vector(fn):
    """The world direction fn collapses to a point — the view direction, pointing AWAY from the
    viewer (larger d is further). Solved numerically so it holds for any projection function."""
    o = np.array(fn((0.0, 0.0, 0.0)))
    ex = np.array(fn((1.0, 0.0, 0.0))) - o
    ed = np.array(fn((0.0, 1.0, 0.0))) - o
    ez = np.array(fn((0.0, 0.0, 1.0))) - o
    # find (a, b) with a*ex + b*ez = -ed  ->  v = (a, 1, b)
    M = np.array([ex, ez]).T
    a, b = np.linalg.lstsq(M, -ed, rcond=None)[0]
    return np.array([a, 1.0, b])


def rotbox(cx, cd, z0, length, width, height, angle_deg, part="body"):
    """A box turned angle_deg in plan about (cx, cd), lying from z0 up. For beams."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for pts, kind, prt in box(-length / 2, length / 2, -width / 2, width / 2, z0, z0 + height, part):
        rp = [(cx + x * ca - d * sa, cd + x * sa + d * ca, z) for x, d, z in pts]
        out.append((rp, kind, prt))
    return out


def round_exception(cand):
    """§3.2's round exception (Rafe, 2026-09-12): a cylinder has no front face to keep true and
    oblique makes its ends oblong, so round objects keep a TRUE-CIRCLE top and a VERTICAL body.
    The top is the plan view — a circle, not an ellipse — and the body is the front elevation
    below it: (x, d, z) -> (x, -(z + d)). Nothing shears. `cand` is accepted for symmetry with
    project() and ignored: the exception is the same under every candidate."""
    def f(p):
        x, d, z = p
        return (x, -(z + d))
    return f


# ── the archetypes as models. Dimensions in art px at 2x; origin at the footprint's centre ───
def model(name):
    if name == "stone":
        w, d, h = 26, 20, 88
        return box(-w / 2, w / 2, -d / 2, d / 2, 0, h, "stone")
    if name == "chest":
        w, d, h = 48, 30, 28
        f = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, "wood")
        # two iron bands that wrap over the lid: DECALS — one thin strip per exposed face, none
        # interpenetrating the body, because a painter's sort cannot resolve interpenetration
        for bx in (-w / 2 + 10, w / 2 - 14):
            f += box(bx, bx + 4, -d / 2 - 1, -d / 2, 0, h, "iron")            # front strip
            f += box(bx, bx + 4, -d / 2, d / 2, h, h + 1, "iron")             # over the lid
        # lock plate on the front, proud
        f += box(-4, 4, -d / 2 - 1.5, -d / 2, h / 2 - 6, h / 2 + 4, "iron")
        # lid seam: a thin darker strip round the body at 60% height
        f += box(-w / 2, w / 2, -d / 2 - 0.5, -d / 2, h * 0.6 - 0.5, h * 0.6 + 0.5, "seam")   # front
        f += box(-w / 2 - 0.5, -w / 2, -d / 2, d / 2, h * 0.6 - 0.5, h * 0.6 + 0.5, "seam")   # left
        f += box(w / 2, w / 2 + 0.5, -d / 2, d / 2, h * 0.6 - 0.5, h * 0.6 + 0.5, "seam")     # right
        return f
    if name == "barrel":
        r0, r1, h = 15, 19, 44
        prof = lambda z: r0 + (r1 - r0) * math.sin(math.pi * (z / h))
        f = cylinder(0, 0, prof, 0, h, n=32, rings=10, part="wood")
        for zc in (7, h / 2, h - 7):
            f += cylinder(0, 0, lambda z, zc=zc: prof(zc) + 1.2, zc - 2, zc + 2, n=32, rings=1,
                          part="iron")
        return f
    if name == "altar":
        w, d, h = 104, 36, 22
        f = box(-w / 2, w / 2, -d / 2, d / 2, 6, h, "stone")          # the slab
        f += box(-w / 2 + 8, w / 2 - 8, -d / 2 + 6, d / 2 - 6, 0, 6, "stone_dark")   # the plinth
        return f
    # ── the Boundary's props, re-authored under §3.2 (B-PROP-001/002/003) ──────────────────
    if name == "marker":
        # old dressed stone post; orc rope lashing and driven pins over it.
        # THREE COLD SEATS TWICE CALLED A BANDED BOX 'a wooden crate or barrel'. The read that
        # passed §12 last round was a bare pale post. So: a FRUSTUM (the post tapers 30 -> 22,
        # which no crate does), ONE rope lashing low on the post rather than bands across its
        # middle, pins kept, stone pale as the frozen colouring had it.
        wb, wt, d, h = 30, 22, 20, 96
        def frustum(part):
            P = lambda x, dd, z: (x, dd, z)
            b0, b1, t0, t1 = -wb / 2, wb / 2, -wt / 2, wt / 2
            db, dt = d / 2, d / 2 * (wt / wb)
            return [
                ([P(t0, -dt, h), P(t1, -dt, h), P(t1, dt, h), P(t0, dt, h)], "top", part),
                ([P(b0, -db, 0), P(b1, -db, 0), P(t1, -dt, h), P(t0, -dt, h)], "front", part),
                ([P(b1, -db, 0), P(b1, db, 0), P(t1, dt, h), P(t1, -dt, h)], "right", part),
                ([P(b0, db, 0), P(b0, -db, 0), P(t0, -dt, h), P(t0, db * (wt / wb), h)], "left", part),
                ([P(b1, db, 0), P(b0, db, 0), P(t0, dt, h), P(t1, dt, h)], "back", part),
            ]
        f = frustum("stone_pale")
        z0, z1 = 14, 17
        wz = wb + (wt - wb) * (z0 / h)          # the post's width at the lashing's height
        f += box(-wz / 2 - 1, wz / 2 + 1, -d / 2 - 1, -d / 2, z0, z1, "rope")       # front
        f += box(wz / 2, wz / 2 + 1, -d / 2, d / 2 + 1, z0, z1, "rope")             # right
        for px_, pz in ((-8, 15), (6, 15)):
            f += box(px_, px_ + 3, -d / 2 - 2.5, -d / 2, pz - 1, pz + 3, "iron")
        return f
    if name == "barricade_a":
        # crossed baulks: one lies ON the other (no interpenetration — #207's crossing), rope at
        # the join. 'A heap of thick timber beams lying crossed over one another.'
        L, W_, T = 104, 14, 12
        f = rotbox(0, 0, 0, L, W_, T, 22, "wood")
        f += rotbox(0, 0, T, L * 0.92, W_, T, -26, "wood_dark")
        f += rotbox(0, 0, 2 * T, 18, W_ + 4, 3, -26, "rope")     # lashing over the top baulk
        return f
    if name == "barricade_b":
        # a bound stack: two baulks side by side, a third across their top, rope at both ends
        L, W_, T = 100, 14, 12
        f = rotbox(0, -9, 0, L, W_, T, 4, "wood")
        f += rotbox(0, 9, 0, L * 0.95, W_, T, -3, "wood_dark")
        f += rotbox(0, 0, T, L * 0.9, W_, T, 1, "wood")
        for x in (-32, 30):                                        # rope over the top baulk
            f += rotbox(x, 0, 2 * T, 8, W_ + 4, 3, 1, "rope")
        return f
    if name == "fire_ring":
        # the round exception: a ring of stones, true circle in plan, short vertical bodies.
        # The interior (fuel and flame) is the LANDED sprite's, composited back — that read
        # passed the gate and has no face to project.
        r_out, r_in, hgt = 26, 19, 8
        f = cylinder(0, 0, lambda z: r_out, 0, hgt, n=24, rings=1, part="stone_dark")
        return f
    if name == "rack":
        w, d, h = 48, 22, 50
        t = 3
        f = box(-w / 2, w / 2, d / 2 - t, d / 2, 0, h, "interior")         # back panel
        for zc in (0, h / 3, 2 * h / 3):                                    # three shelves
            f += box(-w / 2, w / 2, -d / 2, d / 2, zc, zc + t, "wood")
        f += box(-w / 2, -w / 2 + t, -d / 2, d / 2, 0, h, "wood")          # left upright
        f += box(w / 2 - t, w / 2, -d / 2, d / 2, 0, h, "wood")            # right upright
        f += box(-w / 2, w / 2, -d / 2, d / 2, h - t, h, "wood")           # top
        return f
    raise ValueError(name)


# ── shading: a diagram convention ───────────────────────────────────────────────────────────
BASE = {
    "stone": (132, 128, 118), "stone_dark": (96, 92, 84), "stone_pale": (150, 144, 134),
    "wood": (128, 86, 44), "wood_dark": (84, 56, 30),
    "iron": (46, 44, 46), "seam": (40, 28, 16), "interior": (58, 38, 20),
    "rope": (104, 82, 44),
}
KIND_K = {"top": 1.28, "front": 1.0, "left": 0.66, "right": 0.66, "back": 0.5, "bottom": 0.5}
GREY = {"stone": 128, "stone_dark": 96, "stone_pale": 150, "wood": 128, "wood_dark": 84, "iron": 46, "seam": 40,
        "interior": 58, "rope": 118}


def shade(part, kind, grey):
    if isinstance(kind, tuple):          # a curved facet: outward normal's depth component
        f = max(0.0, -kind[1])           # 1 facing the viewer, 0 side-on
        k = 0.62 + 0.38 * f
    else:
        k = KIND_K[kind]
    if grey:
        g = min(255, int(GREY[part] * k))
        return (g, g, g, 255)
    r, g, b = BASE[part]
    return (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)


def render(cand, name, canvas, grey=False, outline=True, zoom=1.0, fn=None):
    """Project the model, cull back faces, paint back-to-front, return an RGBA template.
    zoom 0.5 renders at the family's NATIVE 32px (model units are 2x art px). fn overrides the
    candidate's function (the round exception)."""
    W, H = int(canvas[0] * zoom), int(canvas[1] * zoom)
    faces = model(name)
    proj = []
    fn = fn or (lambda p: project(cand, p))
    view_dir = null_vector(fn)
    for pts, kind, part in faces:
        sp = [tuple(v * zoom for v in fn(p)) for p in pts]
        # winding on screen (y down): keep faces that wind the outward way
        area = 0.0
        for i in range(len(sp)):
            x0, y0 = sp[i]
            x1, y1 = sp[(i + 1) % len(sp)]
            area += x0 * y1 - x1 * y0
        if area >= 0:            # back-facing in this convention
            continue
        # painter's key: distance along the VIEW DIRECTION — the projector's null vector (the
        # world direction that maps to a single screen point). Larger = further. The old key
        # (-d, then z) could not resolve two crossed beams; this one can, because the top beam's
        # faces are nearer along the view no matter where the crossing falls.
        cen = np.mean(np.array(pts), axis=0)
        # decals (bands, pins, rope) sit ON a body by construction, so they always draw last: a
        # centroid depth cannot say so, because a tall face's centroid sits above a low band.
        key = float(np.dot(cen, view_dir)) - (1e3 if part in ("iron", "seam", "rope") else 0.0)
        proj.append((key, sp, kind, part))
    proj.sort(key=lambda t: -t[0])         # far first
    # fit: anchor the footprint's front-bottom-centre near the canvas bottom, centred
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    xs = [p[0] for _, sp, _, _ in proj for p in sp]
    ys = [p[1] for _, sp, _, _ in proj for p in sp]
    ox = W / 2 - (min(xs) + max(xs)) / 2
    oy = H - 4 * zoom - max(ys)
    for _, sp, kind, part in proj:
        poly = [(x + ox, y + oy) for x, y in sp]
        flat = not isinstance(kind, tuple)
        dr.polygon(poly, fill=shade(part, kind, grey),
                   outline=(20, 20, 20, 255) if (outline and flat and part not in ("iron", "seam")) else None)
    if outline:
        # one silhouette outline for the whole object, so a curved body reads as one thing
        a = np.asarray(im).copy()
        op = a[:, :, 3] > 0
        edge = op & ~(np.roll(op, 1, 0) & np.roll(op, -1, 0) & np.roll(op, 1, 1) & np.roll(op, -1, 1))
        a[edge] = (20, 20, 20, 255)
        im = Image.fromarray(a)
    return im


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    import projection_round2 as pr
    out = os.path.join(pr.GEN, "mesh")
    os.makedirs(out, exist_ok=True)
    cols, rows = pr.ARCHETYPES, pr.CANDIDATES
    cw, ch = 144, 144
    sheet = Image.new("RGBA", (len(cols) * cw, len(rows) * ch), (24, 24, 28, 255))
    for r, cand in enumerate(rows):
        for c, (name, _, _, _, _) in enumerate(cols):
            im = render(cand, name, pr.canvas_for(name))
            im.save(os.path.join(out, "painted_%s_%s.png" % (cand, name)))
            render(cand, name, pr.canvas_for(name), grey=True).save(
                os.path.join(out, "template_%s_%s.png" % (cand, name)))
            sheet.paste(im, (c * cw + (cw - im.size[0]) // 2, r * ch + (ch - im.size[1]) // 2), im)
    sheet.save(os.path.join(out, "mesh_sheet.png"))
    print("mesh templates: %s" % os.path.relpath(out, pr.REPO))
