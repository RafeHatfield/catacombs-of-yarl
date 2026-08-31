#!/usr/bin/env python3
"""ASSEMBLE THE ASHLAR FIELD, APPLY THE RUNTIME REMAP, AND MEASURE THE FIVE THINGS THAT DECIDE IT.

    ENCLOSURE       session one's terminal finding was "joints enclose nothing — 99.1% of the
                    floor is one connected region". That number is the bar.

    BOUNDARY STEP   ruling (1)'s metric. The crossing-joint geometry put a value step through
                    every stone spanning a cell boundary: 8.72 against 1.17 inside a tile, 7.44x.
                    Blending it got to 2.95x and no further, because a blend hides a disagreement
                    rather than removing one. Under a shared stone address it should be exactly
                    1.00x, and "exactly" is the point — if it is 1.03 something is still keyed
                    per-tile and must be found, not tuned.

    CONTINUITY      the governing test for coursing, per ruling: A LINE THAT TRAVELS ACROSS
                    BOUNDARIES IS MATERIAL; A TREATMENT LOCKED TO BOUNDARIES IS A FRAME. Measured
                    as the share of joint pixels arriving at a tile boundary that carry on
                    through it.

    GRID HIDING     the other half of the same ruling — coursing must HIDE the grid, not reveal
                    it. The bed joint on a tile boundary and the bed joint halfway up the tile
                    are both bed joints of one 16px lattice, so they must be indistinguishable.
                    Measured as the ratio of their joint density and of their mean value. A
                    coursing that travels but draws its boundary line heavier has still drawn the
                    grid, and this is the number that would say so.

    CROSSING SPREAD the clarified law's floor, reported where crossings exist. Under an ashlar
                    bond nothing crosses a horizontal boundary — a bed joint RUNS ALONG it — so
                    that orientation reports n=0 by construction rather than by degeneracy, and
                    the continuity and grid-hiding numbers are what carry it. Reported plainly
                    either way; a zero that is explained is still a zero on the record.

EVERY ONE OF THESE HAS A PLANT (§4, bible §13.5: no instrument's pass counts until it has
demonstrated it can fail). `--plants` builds four deliberately broken fields and asserts that the
matching instrument fires on each and that the others stay quiet.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402
import ring_instrument as RI     # noqa: E402

T = CA.T


# =================================================================================================
# ASSEMBLY — the tiles supply material and bond; this supplies the stone values.
# =================================================================================================

def _one_course_split():
    """Index of the degenerate split the constant-pitch plant needs, appended once.

    ⚠ IT MUTATES `CA.SPLITS`, WHICH THE COMPOSER WRITES INTO THE MANIFEST. In separate processes
    that is harmless and in one process it is a bogus split shipped to the engine, so the append
    is idempotent and the composer asserts the table it writes is the one it declared. A landmine
    that only goes off when two tools share an interpreter is still a landmine.
    """
    if [T, 0] not in CA.SPLITS:
        CA.SPLITS.append([T, 0])
    return CA.SPLITS.index([T, 0])


def stone_worn(worn, kind, x, y):
    """Is this stone in the trodden channel?

    Decided from the MAP, which both tiles either side of a boundary can read, and never from
    "which tile am I". A stone spanning a boundary counts as trodden only when the cells on both
    sides are — so the channel ends at a JOINT rather than at a tile edge, and its boundary is
    the last stone the feet actually polished.
    """
    if worn is None:
        return False
    if kind == 0:
        return bool(worn(x - 1, y)) and bool(worn(x, y))
    if kind == 2:
        return bool(worn(x, y)) and bool(worn(x + 1, y))
    return bool(worn(x, y))


def assemble(w, h, seed, mat, worn=None, defect=None, traffic=None, mouth=None):
    """Lay a w x h field, then paint the material onto it one stone at a time.

    The tiles supply the bond. Everything else — a stone's value and a stone's grain — is chosen
    by that stone's WORLD ADDRESS and sampled in STONE-LOCAL coordinates, so both tiles either
    side of a boundary paint the identical material onto the identical stone.

    `defect` names a plant; see `PLANTS`.
    """
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CF.PALETTE_LEVELS - 1)
    amp = max(mat["grain_mad"], 1.0)
    crack_cache, crack_v = {}, mat["lum_median"] * CA.CRACK_DEPTH
    img = np.zeros((h * T, w * T, 3), dtype=np.uint8)
    joints = np.zeros((h * T, w * T), dtype=bool)
    cracks = np.zeros((h * T, w * T), dtype=bool)
    dressing = np.zeros((h * T, w * T), dtype=bool)
    chips = np.zeros((h * T, w * T), dtype=bool)
    polish = np.zeros((h * T, w * T), dtype=float)
    yy, xx = np.mgrid[0:T, 0:T]

    for y in range(h):
        for x in range(w):
            # THE PLANT FOR SKELETON REPETITION: one family everywhere.
            if defect == "one_family":
                n = s_ = wf = e = 0
            else:
                n = CA.edge_family(x, y, CA.HORIZ, seed)
                s_ = CA.edge_family(x, y + 1, CA.HORIZ, seed)
                wf = CA.edge_family(x, y, CA.VERT, seed)
                e = CA.edge_family(x + 1, y, CA.VERT, seed)
            drops = tuple(CA.drop_choice(x, y * CA.COURSES + c, seed)
                          for c in range(CA.COURSES))
            # THE PLANT FOR BANDING: every row on the same split, which is what the geometry did
            # before the seat objected to it.
            split_i = 0 if defect == "uniform_courses" else CA.row_split(y, seed)
            # THE PLANT FOR CONSTANT PITCH: a split of [T, 0] puts the interior bed line exactly
            # on top of the next boundary, so ONE course fills the tile and the only full-width
            # joints in the world are the tile boundaries themselves — the corner theorem's bill
            # paid in full, with nothing else on the floor to hide it behind.
            if defect == "one_course":
                split_i = _one_course_split()
            _tile, jm, cls, L = CA.build_tile(n, e, s_, wf, mat, seed, drops, split_i)
            L = L.astype(float)

            wear_of_class = {}
            for c in range(CA.COURSES):
                course_k = y * CA.COURSES + c
                for kind in (0, 1, 2):
                    m = cls == (1 + c * 3 + kind)
                    if not m.any():
                        continue
                    # THE ADDRESS. A spanning stone is addressed by ITS BOUNDARY — the one piece
                    # of data both tiles either side of it possess — so both compute the same key
                    # and the step is zero rather than small.
                    addr = CA.stone_kind_address(kind, drops[c])
                    if addr == 0:
                        bx, key = x, CA.stone_key_span(x, course_k, seed)
                    elif addr == 2:
                        bx, key = x + 1, CA.stone_key_span(x + 1, course_k, seed)
                    else:
                        bx, key = x, CA.stone_key_interior(x, course_k, seed)
                    if defect == "per_tile_value":
                        # THE PLANT FOR RULING (1): address the stone by the tile it is seen from
                        # instead of by the boundary it straddles — the old geometry's mistake.
                        key = CA.mix(x * 31 + kind, course_k, CA.INTERIOR + seed)

                    is_worn = stone_worn(worn, addr, x, y)
                    wear_of_class[1 + c * 3 + kind] = is_worn
                    w_raw = int(CA.wear_scalar_block(x * T + T // 2, y * T + T // 2,
                                                     1, seed, traffic)[0, 0])
                    w01 = 0.0 if defect == "uniform_wear" else CA.wear01(w_raw, is_worn)
                    ox = CA.stone_origin(wf, e, kind, c, drops[c])
                    oy = CA.course_origin_y(split_i, c)
                    lx, ly = (xx - ox) % (2 * T), (yy - oy) % (2 * T)
                    g = (CA.grain_patch(key, 8, seed)[ly, lx] * 0.34
                         + CA.grain_patch(key, 16, seed)[ly, lx] * 0.14)
                    # Wear is absence: the grain is walked off the stone and its value closes up
                    # on the family median. No brightening anywhere — §8.2.1.
                    bias = CA.cluster_bias(bx, course_k, seed)
                    L = L + m * (CA.stone_offset(key, step, worn=is_worn, bias=bias)
                                 + g * amp * (CA.WEAR_GRAIN if is_worn else 1.0))

                    # THE WORKED SURFACE. Applied in STONE-LOCAL coordinates and masked by the
                    # stone's own class, so a mark that falls past a joint is simply not drawn —
                    # and both tiles either side of a spanning stone dress it identically.
                    if defect != "no_marks":
                        ext = CA.stone_extent(wf, e, kind, c, drops[c], split_i)
                        for (u, v, depth) in CA.stone_marks(key, seed, ext, worn=is_worn,
                                                            wear=w01):
                            lx, ly = u + ox, v + oy
                            if 0 <= lx < T and 0 <= ly < T and m[ly, lx]:
                                L[ly, lx] -= depth * step
                                dressing[y * T + ly, x * T + lx] = True

            if defect == "boundary_frame":
                # THE PLANT FOR GRID HIDING: an extra joint along the tile's own edge.
                L[0, :] = mat["lum_median"] * 0.35
                L[:, 0] = mat["lum_median"] * 0.35
                jm = jm.copy()
                jm[0, :] = True
                jm[:, 0] = True
            if defect == "broken_courses":
                # THE PLANT FOR CONTINUITY: bed joints stop short of the EAST edge. Cut on one
                # side only — cutting both removes the arrival as well as the crossing, and an
                # instrument must be shown to fail on a defect it can still see.
                for col in (T - 2, T - 1):
                    L[:, col] = np.where(jm[:, col], mat["lum_median"], L[:, col])
                jm = jm.copy()
                jm[:, T - 2:] = False

            # THE ARRIS PASS. A joint beside a trodden stone is shallower, because feet round the
            # edges off — geometry, not light (§6.3). Each joint pixel takes the wear of the
            # nearest stone it touches, so the polish ends where a STONE ends and never draws a
            # straight line on the tile grid.
            if worn is not None:
                # NO WRAP. `np.roll` is circular, so a worn stone on the top row was rounding
                # the arris of a joint on the BOTTOM row of the same tile — 32px away, across a
                # course boundary, for no reason a neighbour could reproduce. The engine walks
                # this with bounds checks and would not have wrapped, so the two would have
                # disagreed exactly where the channel meets a tile edge.
                worn_stone = np.zeros((T, T), dtype=bool)
                for cid, w_ in wear_of_class.items():
                    if w_:
                        worn_stone |= (cls == cid)
                jw = np.zeros((T, T), dtype=bool)
                jw[1:, :] |= worn_stone[:-1, :]
                jw[:-1, :] |= worn_stone[1:, :]
                jw[:, 1:] |= worn_stone[:, :-1]
                jw[:, :-1] |= worn_stone[:, 1:]
                jw &= jm
                if jw.any():
                    L = np.where(jw, L + (mat["lum_median"] - L) * CA.WEAR_ARRIS, L)

            # ================= THE DIFFERENTIAL-WEAR PASS =================
            #
            # THE DEVICE GATE: "all the gaps look standardized... freshly laid and mortared, like
            # someone scoured new stone to make it look old." Ruled: uniform joints are STAGED
            # AGE, and staging is a register violation — wear is earned, differentially.
            #
            # (a) a joint OPENS where feet passed: deeper, and therefore darker. Keyed on world
            #     position, so both tiles either side of a boundary agree about it by
            #     construction — the stone address discipline, applied to the joint.
            # (b) the stones beside an open joint lose their arrises: a pixel of stone goes with
            #     the joint, and occasionally a second — a corner gone.
            #
            # Occlusion vocabulary throughout: everything here is a recess getting deeper or
            # wider. Nothing brightens.
            # THE LINE GEOMETRY, hoisted above every branch that reads it. The `uniform_wear`
            # plant skips the erosion block entirely, and with the geometry defined inside it the
            # polish line below referenced an unbound name and took the whole plant run down after
            # eleven of fourteen — which read as "three plants went silent" until the traceback
            # was found. A plant runner that crashes is not a plant runner that failed.
            wxb, wyb = xx + x * T, yy + y * T
            ldist, ltx, lty = CA.line_geometry_block(x * T, y * T, T)
            if defect == "no_additive":
                ldist = np.full((T, T), 1e9)

            # THE CHROMA CHANNEL, on the stone faces only, from the SAME wear scalar the joints
            # read. Sharing the scalar is what makes the two channels one signal instead of two
            # coincidences: a stone whose joints have packed shut is the same stone whose face has
            # been walked to a colder colour.
            chr_blk = np.zeros((T, T), dtype=float)
            if defect not in ("uniform_wear", "flat_chroma"):
                chr_blk = CA.chroma_strength_block(x * T, y * T, T, seed, traffic,
                                                   bool(worn and worn(x, y)))
                if defect == "chroma_lattice":
                    # THE PLANT: chroma keyed to the tile a stone is SEEN FROM rather than to the
                    # world — §8.3.1's lattice, restated in the colour domain.
                    chr_blk = np.full((T, T), CA.CHROMA_BY_AGE[-1] * ((x + y) % 2))
                chr_blk = np.where((cls != 0) & ~((cls == 0) & jm), chr_blk, 0.0)

            if defect != "uniform_wear":
                jm_pix = (cls == 0) & jm
                wblk = CA.wear_scalar_block(x * T, y * T, T, seed, traffic)
                w01b = CA.wear01_block(wblk, bool(worn and worn(x, y)))
                open_amt = np.where(jm_pix, w01b, 0.0)
                # A SHELTERED joint is shallower. An open one keeps the dark it already had —
                # there is no rung below it — and spends its wear on the arrises instead.
                # A WHOLE RUNG OR NOTHING — §13.8 applied to this very change. Scaling the
                # lightening continuously with wear produced sub-rung shifts on a joint sitting
                # exactly on the ladder's bottom rung, and quantisation ate every one of them:
                # measured spread 0.000. The law says a signal below the floor is absent, and it
                # does not stop being true because the signal is mine.
                #
                # So a joint is TIGHT or it is OPEN. Tight sits a full rung shallower; open keeps
                # the dark it had and spends its wear on the arrises beside it.
                # THE JOINT CARRIES THE TRAFFIC NOW. Off-route it stays as deep and as dark as
                # the bond drew it; trodden it is packed with grit, and a packed joint is a
                # shallower one. Some of it fills level with the floor entirely, so the line
                # between two stones stops being a line — which is what "stones wearing into one
                # another" looks like at 32px.
                ages = np.array(CA.WEAR_AGES)
                idx = np.abs(open_amt[..., None] - ages).argmin(-1)
                fill = np.array(CA.JOINT_FILL_RUNGS)[idx]
                brk = np.array(CA.JOINT_BREAK)[idx]

                # ============ THE COMPACTION KNOWS WHICH WAY THE FEET WENT ============
                # A joint lying ACROSS the route is crossed and packed shut; one running WITH it
                # takes far less and stays open and dark. The bed joints close along a north-south
                # corridor and the head joints survive as continuous lines — the directional grain
                # the seat asked for, made of the bond that was already there.
                axis0 = CA.travel_axis(traffic, x, y) if defect != "no_erosion" else CA.DIR_NONE
                if axis0 != CA.DIR_NONE:
                    # a joint pixel is BED if its run continues left-right, HEAD if up-down
                    bedj = np.zeros((T, T), dtype=bool)
                    bedj[:, 1:-1] = jm_pix[:, :-2] & jm_pix[:, 2:]
                    headj = np.zeros((T, T), dtype=bool)
                    headj[1:-1, :] = jm_pix[:-2, :] & jm_pix[2:, :]
                    wv0, wh0 = CA.aniso_weights(axis0)
                    # bed joints have a north-south normal, head joints an east-west one
                    kw = np.where(bedj & ~headj, wv0, np.where(headj & ~bedj, wh0, 1.0))
                    fill = fill * kw
                    brk = brk * kw
                hb = (CA._mix_np(xx + x * T, yy + y * T, CA.JOINT_BREAK_SALT + seed)
                      % 1000) / 1000.0
                broken = jm_pix & (hb < brk)
                L = L + np.where(jm_pix & ~broken, fill, 0.0) * step
                L = np.where(broken, mat["lum_median"], L)

                # ================= FORM AS EROSION =================
                stone_px = (cls != 0) & ~jm_pix
                fage = np.abs(w01b[..., None] - np.array(CA.WEAR_AGES)).argmin(-1)
                axis = CA.travel_axis(traffic, x, y) if defect != "no_erosion" else CA.DIR_NONE

                # (a) GROUND LOWER AND FLATTER. A walked stone loses its crown: its value
                # collapses toward the material's median. A pull to the median is symmetric, so
                # this takes contrast away without darkening anything on average — a stone that
                # merely got darker would be a stone that got painted.
                if defect != "no_erosion":
                    fl = np.array(CA.DEFORM_FLATTEN)[fage]
                    L = np.where(stone_px, L + (mat["lum_median"] - L) * fl, L)

                # ================= THE ADDITIVE LAYER =================
                # Round 22 moved the axis: the signal is on a real coherent line and is still too
                # small to route by, and every lever before this one SUBTRACTS. These put
                # something back, and all three key off the same line geometry.

                # (2) DISHING ALONG THE LINE — deepest on the centre-line, gone by the shoulder.
                # The threshold hollows below are untouched and compose on top of it.
                L = np.where(stone_px, L - CA.lane_dish_block(ldist, wxb, wyb, seed) * step, L)

                # (3) MARGIN GRIT — the swept lane left conspicuously bare BETWEEN gritty edges.
                grit = CA.grit_block(ldist, wxb, wyb, seed) & stone_px
                L = np.where(grit, L - CA.GRIT_DEPTH * step, L)

                # (c) THRESHOLD HOLLOWS. Where routes converge on a mouth the stone dishes:
                # genuinely lower in the middle with a rim that shadows. Never a sill, never a
                # kerb, never an installed piece — nothing is built here (§8.1).
                if mouth is not None and mouth(x, y) and defect != "no_erosion":
                    cy, cx = (T - 1) / 2.0, (T - 1) / 2.0
                    rr = np.sqrt(((yy - cy) / cy) ** 2 + ((xx - cx) / cx) ** 2)
                    jit = (CA._mix_np(xx + x * T, yy + y * T, CA.HOLLOW_SALT + seed) % 100) / 400.0
                    dish = np.clip(1.0 - rr - jit, 0.0, 1.0) * CA.HOLLOW_DEPTH
                    rim = np.where((rr > 0.82) & (rr < 1.02), CA.HOLLOW_RIM, 0.0)
                    L = np.where(stone_px, L - (dish + rim) * step, L)

                # (b) THE ARRIS GOES WITH THE JOINT — AND THE ROUTE CHOOSES WHICH ARRIS. Feet
                # cross the joints that lie ACROSS a route and skate over the ones that run with
                # it, so the crossed edges round away and the parallel ones stay crisp. In a
                # north-south corridor that leaves the bed joints soft and the head joints sharp:
                # long unbroken runs in the direction of travel, out of geometry that was already
                # there. This is the seat's "directional grain" with no new families and no new
                # bond.
                nv = np.zeros((T, T), dtype=float)     # edges whose normal runs north-south
                nh = np.zeros((T, T), dtype=float)     # edges whose normal runs east-west
                nv[1:, :] = np.maximum(nv[1:, :], open_amt[:-1, :])
                nv[:-1, :] = np.maximum(nv[:-1, :], open_amt[1:, :])
                nh[:, 1:] = np.maximum(nh[:, 1:], open_amt[:, :-1])
                nh[:, :-1] = np.maximum(nh[:, :-1], open_amt[:, 1:])
                # THE ARRIS PASS STAYS ISOTROPIC. It was frozen and passing, and the direction
                # now lives in the compaction where it works; weighting both would double-count
                # one story and make neither measurable on its own axis (§4.1).
                near = np.maximum(nv, nh)

                # A WHOLE RUNG OR NOTHING, §13.8 applied to this lever too: an arris rounds by a
                # full step when the erosion asks for more than half of one, and otherwise stays
                # where it is. A continuous rounding at 32px is a sub-rung shift the quantiser
                # eats, which this project has now measured three times.
                if defect != "no_erosion" and any(CA.DEFORM_ROUND):
                    ro = np.array(CA.DEFORM_ROUND)[fage] * near
                    L = np.where(stone_px & (ro > 0.5), L - step, L)
                hsh = (CA._mix_np(xx + x * T, yy + y * T, CA.CHIP + seed) % 1000) / 1000.0
                chip = stone_px & (near > 0) & (hsh < CA.CHIP_RATE * near)
                L = np.where(chip, L - near * step * 1.6, L)
                chips[y * T:(y + 1) * T, x * T:(x + 1) * T] = chip

            # THE CRACK NETWORK, drawn last so it crosses stones and joints alike. Not an
            # overlay and not alpha: authored pixels on the family's own ladder, which is what
            # §5.1 and §4.3 govern.
            # THE PLANT FOR CRACK EXTENT: draw only the crack this tile ANCHORS, clipped to this
            # tile — which is what the overlay system this replaces did, and produced 127 marks
            # with a median size of four pixels.
            #
            # The first version of this plant clipped on `lx` and did nothing at all, because
            # `lx` is already tile-local and the test was tautological. It reported SILENT, which
            # was the right verdict about a plant that was not planting anything.
            if defect == "tile_confined_cracks":
                px_set = set()
                for (wx, wy) in CA.crack_polyline(x, y, seed):
                    lx, ly = wx - x * T, wy - y * T
                    if 0 <= lx < T and 0 <= ly < T:
                        px_set.add((ly, lx))
            elif defect == "no_cracks":
                px_set = set()
            else:
                px_set = CA.crack_pixels(x, y, seed, crack_cache)
            for (ly, lx) in px_set:
                L[ly, lx] = crack_v
                chr_blk[ly, lx] = 0.0        # a crack is enclosure, and enclosure has no hue
                cracks[y * T + ly, x * T + lx] = True

            # CLIP AGAINST THE LADDER'S OWN ENDS, not against the donors' band. They used to be
            # the same pair of numbers; since the ladder gained two rungs below the donors they
            # are not, and clipping at `lum_lo` here would have pinned the reference painter to
            # 75.02 while the engine — which has always clipped at `Ladder[0]` — went to 48.56.
            # The paint check would have caught it as a 96-sample disagreement with no cause.
            L = CF.quantise(np.clip(L, mat["ladder"][0], mat["ladder"][-1]), mat["ladder"])
            # (1) THE SPECULAR LANE, recorded for the instruments. The shader consumes it in the
            # engine; here it is returned so the reference painter can be measured on the same
            # quantity the device shows.
            polish[y * T:(y + 1) * T, x * T:(x + 1) * T] = np.where(
                (cls != 0) & ~((cls == 0) & jm),
                CA.lane_polish_block(ldist, ltx, lty, wxb, wyb, seed), 0.0)

            tmap = np.stack([CA.chroma_tint(mat["tint"], v) for v in CA.CHROMA_BY_AGE])
            _ci = np.abs(chr_blk[..., None] - np.array(CA.CHROMA_BY_AGE)).argmin(-1)
            img[y * T:(y + 1) * T, x * T:(x + 1) * T] = \
                CF.colourise_map(L, tmap[_ci]).astype(np.uint8)
            joints[y * T:(y + 1) * T, x * T:(x + 1) * T] = jm

    if defect == "value_lattice":
        # THE PLANT FOR THE TINT LATTICE ITSELF: a value ramp locked to the tile grid.
        L = RI.lum(img.astype(float))
        _, gx = np.mgrid[0:h * T, 0:w * T]
        L = L + ((gx // T) % 2) * step * 1.2
        L = CF.quantise(np.clip(L, mat["ladder"][0], mat["ladder"][-1]), mat["ladder"])
        img = CF.colourise(L, mat["tint"]).astype(np.uint8)

    # NO TRANSITION LIST. Wear is now decided per stone, so the channel's edge falls on a joint
    # rather than on a tile boundary, and there is no longer an intended material step at any
    # vertical boundary to exclude. The empty list is the finding, not an omission.
    assemble.last_polish = polish
    return img, joints, [], cracks, dressing | chips


# =================================================================================================
# INSTRUMENTS
# =================================================================================================

def enclosure(joints):
    """Connected components of the NON-joint pixels: the stones. Reported as session one did."""
    h, w = joints.shape
    lab = np.full((h, w), -1, dtype=int)
    sizes, nxt = [], 0
    for sy in range(h):
        for sx in range(w):
            if joints[sy, sx] or lab[sy, sx] >= 0:
                continue
            stack, size = [(sy, sx)], 0
            lab[sy, sx] = nxt
            while stack:
                yy, xx = stack.pop()
                size += 1
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < h and 0 <= nx < w and not joints[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = nxt
                        stack.append((ny, nx))
            sizes.append(size)
            nxt += 1
    total = int((~joints).sum())
    sizes.sort(reverse=True)
    return dict(regions=len(sizes), floor_px=total,
                largest_share=round(sizes[0] / total, 4) if total else 1.0,
                median_region=int(np.median(sizes)) if sizes else 0,
                regions_over_64px=sum(1 for s in sizes if s >= 64))


def boundary_step(img, joints, w, h, transitions=(), cracks=None, dressing=None):
    """RULING (1)'s metric: is a value step at a tile boundary bigger than one inside a tile?

    Measured on STONE pixels only. A joint is meant to be a step — measuring across joints would
    report the bond as a defect and would have let the real defect hide behind it.
    """
    L = RI.lum(img.astype(float))
    # A CRACK IS NOT STONE. It is dark because enclosed, exactly as a joint is, and counting it as
    # stone made this instrument read 1.69 on a field whose boundaries had not moved at all — an
    # instrument reporting the new feature as the old defect.
    # A DRESSING MARK IS NOT STONE EITHER, and leaving it in read 1.362 — above 1.00 for the
    # first time in three sessions, on an axis the device gate had already passed. It was the
    # instrument counting the EDGE OF EVERY CHISEL STROKE as a stone-to-stone step. Same defect as
    # counting cracks as stone, one feature later, and it nearly sent a good floor back for a
    # regression it did not have. With the dressing excluded: 0.66.
    not_stone = joints if cracks is None else (joints | cracks)
    if dressing is not None:
        not_stone = not_stone | dressing
    stone = ~not_stone
    dx = np.abs(np.diff(L, axis=1))
    ok = stone[:, :-1] & stone[:, 1:]
    cols = np.arange(dx.shape[1])
    at = np.zeros_like(cols, dtype=bool)
    trans = np.zeros_like(cols, dtype=bool)
    for x in range(1, w):
        (trans if x in set(transitions) else at)[x * T - 1] = True
    interior = ~(at | trans)
    b = dx[:, at][ok[:, at]]
    i = dx[:, interior][ok[:, interior]]
    bm = float(b.mean()) if b.size else 0.0
    im = float(i.mean()) if i.size else 0.0
    t = dx[:, trans][ok[:, trans]]
    return dict(boundary_mean=round(bm, 3), interior_mean=round(im, 3),
                ratio=round(bm / im, 3) if im else None,
                boundary_max=round(float(b.max()), 2) if b.size else 0.0, n=int(b.size),
                channel_edge_mean=round(float(t.mean()), 3) if t.size else None,
                channel_edge_n=int(t.size))


def _travelling(joints, y, x, run=3):
    """Is this joint pixel part of a HORIZONTAL run — a line going somewhere, not a head joint?

    The first version of `continuity` counted every joint pixel next to a boundary, which meant
    head joints (vertical, a few px long, ending at a bed line) were counted as lines that had
    "failed to continue". On the clean field that read 0.4978 and would have condemned a floor
    whose coursing was in fact unbroken. A joint that was never travelling cannot fail to travel.
    """
    W = joints.shape[1]
    n = 0
    for d in (-1, 1):
        xx = x + d
        while 0 <= xx < W and joints[y, xx] and n < run:
            n += 1
            xx += d
    return n >= run


def continuity(joints, w, h):
    """Does a line arriving at a tile boundary carry on through it?

    A line that travels is material; one that stops at the boundary is a frame. Counted from BOTH
    sides — the first version only looked left, so a plant that cut the courses on the east side
    of every tile produced no arrivals at all and the instrument reported None instead of failing.
    An instrument that goes quiet on the defect it exists to find is worse than no instrument.
    """
    arrive = carry = 0
    for x in range(1, w):
        c = x * T
        for y in range(joints.shape[0]):
            l, r = bool(joints[y, c - 1]), bool(joints[y, c])
            if not (l or r):
                continue
            if not ((l and _travelling(joints, y, c - 1)) or (r and _travelling(joints, y, c))):
                continue                      # a head joint, which was never going anywhere
            arrive += 1
            carry += int(l and r)
    return dict(arriving=arrive, continuing=carry,
                continued=round(carry / arrive, 4) if arrive else None)


def grid_hiding(img, joints, w, h, seed=1337):
    """Is the bed joint ON a tile boundary distinguishable from the one halfway up the tile?

    If it is, the coursing has revealed the grid instead of hiding it, whatever its continuity
    says. Two ratios, both of which should sit at 1.00: joint density, and mean value.

    Also reports the VERTICAL boundary's excess, where there is no bed joint to hide behind and
    any excess at all is a frame.
    """
    L = RI.lum(img.astype(float))
    H, W = joints.shape
    # The boundary bed line is at a fixed phase; the INTERIOR one moves with the row's split, so
    # both masks are built row by row rather than by a phase constant. Using a constant here after
    # the split was introduced would have compared the boundary line against ordinary stone and
    # reported a ratio of about 4 — an instrument reading its own stale assumption as a defect.
    ry = np.arange(H) % T
    bnd = (ry == 0) | (ry == T - 1)
    mid = np.zeros(H, dtype=bool)
    for r in range(h):
        a0 = CA.SPLITS[CA.row_split(r, seed)][0]
        mid[r * T + a0 - 1] = True
        mid[r * T + a0] = True
    bd, md = float(joints[bnd].mean()), float(joints[mid].mean())
    bv, mv = float(L[bnd].mean()), float(L[mid].mean())

    cx = np.arange(W) % T
    at_col = (cx == 0)
    other = ~at_col
    cbd, cod = float(joints[:, at_col].mean()), float(joints[:, other].mean())
    return dict(bed_density_boundary=round(bd, 4), bed_density_mid=round(md, 4),
                bed_density_ratio=round(bd / md, 4) if md else None,
                bed_value_boundary=round(bv, 2), bed_value_mid=round(mv, 2),
                bed_value_ratio=round(bv / mv, 4) if mv else None,
                col_density_boundary=round(cbd, 4), col_density_other=round(cod, 4),
                col_density_ratio=round(cbd / cod, 4) if cod else None)


def banding(joints):
    """ARE THE COURSES A BOND OR A STACK OF STRIPES?

    This instrument exists because a blind seat found what four field instruments had passed:

        "The horizontal banding. The ruled seam every 32px is the single loudest thing on screen
         after the figure. Because the courses never break, the floor reads as a stack of
         horizontal stripes before it reads as stone."
        "Real floors under four hundred years of traffic do not hold a ruled line like that."

    Nothing was measuring it. Enclosure counts stones, boundary-step watches value, continuity
    and grid-hiding watch the tile grid — and a perfectly regular course rhythm passes all four,
    because it is not a tile artefact at all. It is a property of the MATERIAL, and it was the
    first thing a human eye reported.

    Measured as the spacing between full-width bed joints. A single spacing repeated is a stripe
    pattern; several, in no fixed order, is a bond.
    """
    full = np.where(joints.mean(axis=1) > 0.8)[0]
    if len(full) < 3:
        return dict(bed_rows=int(len(full)), distinct_spacings=0, modal_share=None, sd=0.0)
    gaps = np.diff(full)
    gaps = gaps[gaps > 1]                     # a 2px joint is two adjacent rows, not a course
    if not len(gaps):
        return dict(bed_rows=int(len(full)), distinct_spacings=0, modal_share=None, sd=0.0)
    vals, counts = np.unique(gaps, return_counts=True)
    return dict(bed_rows=int(len(full)), courses=int(len(gaps)),
                distinct_spacings=int(len(vals)),
                modal_share=round(float(counts.max()) / len(gaps), 3),
                sd=round(float(gaps.std()), 2),
                spacings=[int(v) for v in vals[:8]])


def _band_ratios(img, joints, worn_cells):
    """IS THE TRODDEN CHANNEL VISIBLE AT ALL?

    §8.2.1 binds the channel to signal by ABSENCE — polish takes grain and value variety away, it
    never adds brightness, because under a carried lamp brightness is what the light is saying.
    The obvious risk in that law is that absence has a floor: subtract enough and there is nothing
    left to subtract, and if the eye still cannot see it, the channel does not exist.

    A blind seat could not find it. This measures what it was looking for:

      TEXTURE   local variation on the stone faces, inside the channel against outside. Polish
                takes it away, so a working channel reads well below 1.0.
      VARIETY   the spread of stone values, inside against outside. Same direction.
      ARRIS     joint-to-stone contrast, inside against outside. A rounded arris holds less
                shadow, so again below 1.0.

    Reported as ratios, with no threshold pretending to be a verdict — the seat decides whether it
    reads. The number says whether there is anything there TO read.
    """
    L = RI.lum(img.astype(float))
    H, W = L.shape
    inside = np.zeros((H, W), dtype=bool)
    for (cx, cy) in worn_cells:
        inside[cy * T:(cy + 1) * T, cx * T:(cx + 1) * T] = True
    outside = ~inside
    face = ~joints

    from numpy.lib.stride_tricks import sliding_window_view
    sd = sliding_window_view(L, (3, 3)).std(axis=(2, 3))
    # ONLY WINDOWS WHOLLY INSIDE A STONE. Counting a window that straddles a joint measures the
    # JOINT's contrast and calls it grain, so erasing joints inside the channel made "texture"
    # collapse to 0.536 on a field whose grain had not been touched at all.
    allface = sliding_window_view(face, (3, 3)).all(axis=(2, 3))
    fi = allface & inside[1:-1, 1:-1]
    fo = allface & outside[1:-1, 1:-1]
    tex_i, tex_o = float(sd[fi].mean()), float(sd[fo].mean())
    var_i, var_o = float(L[face & inside].std()), float(L[face & outside].std())
    ai = float(L[face & inside].mean() - L[joints & inside].mean()) if (joints & inside).any() else 0.0
    ao = float(L[face & outside].mean() - L[joints & outside].mean())
    return dict(texture=tex_i / tex_o if tex_o else 1.0,
                variety=var_i / var_o if var_o else 1.0,
                arris=ai / ao if ao else 1.0, inside_px=int(inside.sum()))


def channel_legibility(img, baseline, joints, worn_cells, w, h):
    """The channel's effect, measured AGAINST THE SAME STONES UNPOLISHED.

    The first version reported inside-vs-outside on the channel field alone, and the number was
    mostly the band's own content. Measured on a field with NO channel at all, the inside/outside
    ratio for a 2-cell band ranges from 0.74 to 1.39 across the seven bands of an 8x8 field —
    wider than the effect being looked for. A ratio of 0.738 was read as a failing instrument
    when it was simply what columns 3 and 4 happen to look like.

    So the band is differenced against ITSELF: the identical field painted with the channel off.
    Whatever those stones were going to be, they were going to be it in both, and what is left is
    the polish. 1.000 means the channel delivered nothing.
    """
    a = _band_ratios(img, joints, worn_cells)
    b = _band_ratios(baseline, joints, worn_cells)
    return dict(texture_ratio=round(a["texture"] / b["texture"], 3),
                variety_ratio=round(a["variety"] / b["variety"], 3),
                arris_ratio=round(a["arris"] / b["arris"], 3),
                band_alone=dict(texture=round(a["texture"], 3), variety=round(a["variety"], 3),
                                arris=round(a["arris"], 3)),
                same_band_unpolished=dict(texture=round(b["texture"], 3),
                                          variety=round(b["variety"], 3),
                                          arris=round(b["arris"], 3)),
                inside_px=a["inside_px"])


def joint_variation(img, joints, w, h, rung):
    """ARE THE JOINTS ALL THE SAME AGE?

    The device gate, second walk: *"all the gaps look standardized… freshly laid and mortared,
    like someone scoured new stone to make it look old."* Ruled a register violation — uniform
    joints are STAGED age, and wear is earned differentially.

    So the thing to measure is not how dark the joints are, which was never the complaint, but
    HOW MUCH THEY DIFFER FROM ONE ANOTHER. Reported as the gap between the most-open decile of
    joint pixels and the most-tight decile, in ladder rungs. A floor of uniformly mortared gaps
    reads near zero however dark those gaps are.

    §13.8 applies to the variation itself: a differential authored below the perceptual floor is
    a floor that is still uniform.
    """
    L = RI.lum(img.astype(float))
    v = np.sort(L[joints])
    if len(v) < 20:
        return dict(joint_px=int(len(v)), spread_rungs=0.0)
    k = max(1, len(v) // 10)
    return dict(joint_px=int(len(v)),
                open_decile=round(float(np.median(v[:k])), 2),
                tight_decile=round(float(np.median(v[-k:])), 2),
                spread_rungs=round((float(np.median(v[-k:])) - float(np.median(v[:k]))) / rung, 3))


def crack_field(cracks, w, h):
    """IS A CRACK LONG ENOUGH TO BE A CRACK, AND DOES IT CROSS A TILE?

    The system this replaces was measured before it was replaced: 127 connected marks over the lit
    ground with a MEDIAN SIZE OF FOUR PIXELS, of which only 26 exceeded 20px, while blind seats
    reported "No cracks. Not one. Across ~140 visible blocks."

    So the two things that were wrong are the two things measured. EXTENT, because a mark too
    small to read costs contrast and returns noise. And CROSSING, because a crack that stops at a
    tile edge is not a crack, it is a decal the size of a tile — and it is the tell that would say
    the world-addressed polyline had quietly become per-tile again.
    """
    H, W = cracks.shape
    lab = np.zeros((H, W), int)
    nxt, sizes = 0, []
    for sy in range(H):
        for sx in range(W):
            if not cracks[sy, sx] or lab[sy, sx]:
                continue
            nxt += 1
            st, n = [(sy, sx)], 0
            lab[sy, sx] = nxt
            while st:
                yy, xx = st.pop()
                n += 1
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = yy + dy, xx + dx
                        if 0 <= ny < H and 0 <= nx < W and cracks[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = nxt
                            st.append((ny, nx))
            sizes.append(n)
    if not sizes:
        return dict(marks=0, median_px=0, max_px=0, crossing_a_boundary=0, share_crossing=None)
    crossing = 0
    for i in range(1, nxt + 1):
        ys, xs = np.where(lab == i)
        if len(set(xs // T)) > 1 or len(set(ys // T)) > 1:
            crossing += 1
    return dict(marks=len(sizes), median_px=int(np.median(sizes)), max_px=int(max(sizes)),
                min_px=int(min(sizes)), crossing_a_boundary=crossing,
                share_crossing=round(crossing / len(sizes), 3),
                retired_system_median_px=4)


def joint_contrast(img, joints):
    """HOW DARK IS A JOINT AGAINST THE STONE BESIDE IT? — the ring, in the only form it took.

    The campaign has banned the ring throughout and every instrument built for it looked at the
    TILE GRID: does a treatment sit at a constant grid position. None of them asked the simpler
    question a person asks first — is every STONE outlined — and so a device walk came back
    reading as "outlined chips" while eleven rounds of instruments reported nothing.

    §13.8's floor is 0.144. A joint is meant to be visible, so this cannot go to zero; what it
    must not do is move without anyone noticing. It moved from 0.342 to 0.579 — 2.4x the floor to
    4.0x — when the palette gained two rungs below the donors, because what a sheltered joint does
    with somewhere darker to go is go there, everywhere the route is not. Off-route is most of a
    floor.
    """
    L = np.asarray(img).astype(float)[..., 0]
    jv, sv = float(np.median(L[joints])), float(np.median(L[~joints]))
    w = (sv - jv) / max(sv, 1e-6)
    return dict(joint=round(jv, 2), stone=round(sv, 2), weber=round(w, 4),
                times_perceptual_floor=round(w / 0.144, 2))


def constant_pitch_lines(joints, w, h, img=None):
    """HOW MUCH OF THE COURSING SITS AT THE ONE PITCH THAT CAN NEVER MOVE?

    A blind seat found this and culled for it, in one sentence:

        "Five continuous unbroken full-width joints at exact 64px pitch, which no slab ever
         bridges. That is a tile edge, not a mason's decision. A mason lays a long stone across a
         course line; a tiling engine cannot."

    It is right, and it is not a defect that can be fixed inside the family. No stone may cross a
    horizontal tile boundary — four tiles meet at a grid corner and the diagonal pair share nothing
    to address a stone with — so a full-width joint sits at exactly one tile pitch for ever, in
    every region, in any floor that wants its stone values addressed at runtime. That is the
    corner theorem's bill, and this measures it.

    `grid_hiding` cannot see it: it asks whether the boundary line LOOKS different from the
    mid-tile line, and the answer is no, they are identical. The seat's question is different and
    sharper — how many of the lines are at a pitch a viewer can predict? The interior lines move
    with the row's split; the boundary line never does.

    Reported as the share of full-width lines sitting at the tile phase. Two courses per tile puts
    it at 0.5. It cannot reach 0 without abandoning runtime addressing.

    ⚠ AND THE SHARE ALONE IS BLIND, which cost a device gate. This instrument reported a steady
    55% for eleven rounds and never once asked HOW DARK those lines are — so when the palette
    gained two rungs below the donors and every sheltered joint dropped from 75.02 to 48.56, the
    count did not move and the floor came back from the handset reading as OUTLINED CHIPS.
    Measured: the full-width lines went from a Weber contrast of 0.103 against the stone — BELOW
    §13.8's floor of 0.144, and therefore absent — to 0.247, which is 1.7x the floor and a line
    the eye is obliged to see.

    §13.8 cuts both ways. It rules that a signal below the perceptual floor is absent; the
    corollary, which nothing had measured until now, is that pushing an unwanted artefact ACROSS
    that floor makes it appear. So the amplitude is reported beside the count, and it is the
    amplitude that has a threshold.
    """
    full = np.where(joints.mean(axis=1) > 0.8)[0]
    if not len(full):
        return dict(full_width_lines=0, at_tile_phase=0, share=None)
    # A line is 2px, drawn half either side of its own y; count each line once.
    lines, last = [], -9
    for y in full:
        if y - last > 1:
            lines.append(int(y))
        last = y
    at = [y for y in lines if (y % T) in (0, T - 1)]

    # HOW DARK IS THE LINE, against the stone it crosses? This is the half that was missing, and
    # it is the half with a threshold: the count cannot go to zero and never could, but the
    # CONTRAST can be kept under §13.8's floor, where an unavoidable line is an invisible one.
    contrast = None
    if img is not None and lines:
        L = np.asarray(img).astype(float)[..., 0]
        stone = float(np.median(L[~joints]))
        vals = []
        for y in lines:
            band = L[max(y - 1, 0):min(y + 2, L.shape[0]), :]
            vals.append(float(band.mean()))
        line_v = float(np.mean(vals))
        contrast = round((stone - line_v) / max(stone, 1e-6), 4)

    return dict(full_width_lines=len(lines), at_tile_phase=len(at),
                share=round(len(at) / len(lines), 3),
                contrast=contrast,
                over_perceptual_floor=(None if contrast is None else bool(contrast >= 0.144)),
                floor=("the COUNT cannot reach 0 while stone values are addressed at runtime — no "
                       "stone may cross a horizontal tile boundary. The CONTRAST can and must "
                       "stay under §13.8's 0.144, where an unavoidable line is an invisible one."))


def skeleton_repeats(joints, w, h):
    """DOES THE SAME JOINT SKELETON APPEAR TWICE IN ONE ROOM?

    The fifth instrument this session, and the fifth found by a blind seat rather than by design:

        "The joint layout has a hard 64px period. Searching for duplicate 32x32 patches across the
         whole floor, the top matches are all at displacement exactly (64,0) or (0,64),
         correlating 0.99+."

    Enclosure, boundary step, continuity, grid hiding and banding all pass a field that repeats
    its bond, because none of them compares one CELL to another. A cell's skeleton is fixed by its
    four families, its row's split and its two merges; two cells agreeing on all of those are
    pixel-identical, and at three families per boundary that happened two or three times per room.

    Reported as the exact-duplicate rate among cell pairs, and separately at one-tile displacement,
    which is where a duplicate is most visible because both copies are on screen together.
    """
    seen = {}
    grid = {}
    for y in range(h):
        for x in range(w):
            key = joints[y * T:(y + 1) * T, x * T:(x + 1) * T].tobytes()
            grid[(x, y)] = key
            seen.setdefault(key, []).append((x, y))
    cells = w * h
    dup_cells = sum(len(v) for v in seen.values() if len(v) > 1)
    adjacent = same = 0
    for y in range(h):
        for x in range(w):
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = x + dx, y + dy
                if nx < w and ny < h:
                    adjacent += 1
                    if grid[(x, y)] == grid[(nx, ny)]:
                        same += 1
    return dict(cells=cells, distinct_skeletons=len(seen),
                cells_sharing_a_skeleton=dup_cells,
                duplicate_rate=round(dup_cells / cells, 4),
                neighbour_pairs=adjacent, identical_neighbours=same,
                identical_neighbour_rate=round(same / adjacent, 4) if adjacent else None)


def crossing_spread(joints, w, h):
    """Where joints cross each boundary, and how spread those offsets are. n=0 where a joint runs
    ALONG the boundary instead of across it, which under an ashlar bond is the horizontal case."""
    xs, ys = [], []
    for cy in range(1, h):
        row = joints[cy * T, :]
        if row.mean() > 0.5:            # a bed joint runs along it; there is nothing to cross
            continue
        for cx in range(w):
            seg = np.where(row[cx * T:(cx + 1) * T])[0]
            if len(seg):
                ys.append(int(seg.mean()))
    for cx in range(1, w):
        col = joints[:, cx * T]
        for cy in range(h):
            seg = np.where(col[cy * T:(cy + 1) * T])[0]
            for v in seg:
                xs.append(int(v))
    def stats(v):
        if not v:
            return dict(n=0)
        a = np.array(v)
        vals, counts = np.unique(a, return_counts=True)
        return dict(n=len(a), distinct=int(len(vals)), sd=round(float(a.std()), 2),
                    spread=int(a.max() - a.min()),
                    modal_share=round(float(counts.max()) / len(a), 3))
    return dict(horizontal_boundaries=stats(ys), vertical_boundaries=stats(xs))


def measure(img, joints, w, h, transitions=(), seed=1337, cracks=None, dressing=None,
            rung=13.23):
    return dict(enclosure=enclosure(joints),
                boundary_step=boundary_step(img, joints, w, h, transitions, cracks, dressing),
                continuity=continuity(joints, w, h),
                grid_hiding=grid_hiding(img, joints, w, h, seed), banding=banding(joints),
                skeleton=skeleton_repeats(joints, w, h),
                constant_pitch=constant_pitch_lines(joints, w, h, img),
                joint_contrast=joint_contrast(img, joints),
                cracks=crack_field(cracks, w, h) if cracks is not None else None,
                joint_variation=joint_variation(img, joints, w, h, rung),
                crossings=crossing_spread(joints, w, h))


# =================================================================================================
# THE PLANTS — §4 and bible §13.5. No instrument's pass counts until it has failed.
# =================================================================================================
#
# Each plant names the instrument that MUST fire and the threshold that decides it. A plant that
# fires the wrong instrument is as much a failure as one that fires nothing.

PLANTS = [
    dict(name="per_tile_value", must_fire="boundary_step",
         why="stones addressed by the tile they are seen from instead of by the boundary they "
             "straddle — ruling (1)'s defect, restated exactly",
         test=lambda m: (m["boundary_step"]["ratio"] or 0) > 1.5),
    dict(name="value_lattice", must_fire="boundary_step",
         why="a value ramp locked to the tile grid — session one's tint lattice in its purest form",
         test=lambda m: (m["boundary_step"]["ratio"] or 0) > 1.5),
    dict(name="boundary_frame", must_fire="grid_hiding",
         why="an extra joint drawn along the tile's own edge: a treatment at a constant position",
         test=lambda m: (m["grid_hiding"]["col_density_ratio"] or 0) > 1.5),
    dict(name="uniform_courses", must_fire="banding",
         why="every tile row on the same 16/16 split, so one spacing repeats down the whole "
             "field — the stack of stripes the seat named, restored on purpose",
         test=lambda m: m["banding"]["distinct_spacings"] <= 1
         or (m["banding"]["modal_share"] or 0) > 0.9),
    dict(name="one_course", must_fire="constant_pitch",
         why="one course per tile, so EVERY full-width joint is a tile boundary — the corner "
             "theorem's bill paid in full and nothing else on the floor to hide it behind",
         test=lambda m: (m["constant_pitch"]["share"] or 0) > 0.95),
    dict(name="tile_confined_cracks", must_fire="cracks",
         why="every crack clipped to the tile that anchors it — the retired overlay system's "
             "defect restored, marks that stop at a tile edge",
         test=lambda m: m["cracks"] is not None and m["cracks"]["share_crossing"] is not None
         and m["cracks"]["share_crossing"] < 0.2),
    dict(name="uniform_wear", must_fire="joint_variation",
         why="every joint the same age — the staged-age defect the second device walk culled, "
             "restored by nulling the wear field",
         test=lambda m: m["joint_variation"]["spread_rungs"] < 0.35),
    dict(name="one_family", must_fire="skeleton",
         why="every boundary collapsed to one family, so every cell of a row draws the same bond "
             "— the 0.99+ duplicates at one-tile displacement the seat measured, restored whole",
         test=lambda m: m["skeleton"]["duplicate_rate"] > 0.5),
    dict(name="broken_courses", must_fire="continuity",
         why="bed joints stopping short of the vertical boundaries — coursing that does not travel",
         # `x or 1.0` on a measured 0.0 yields 1.0, because 0.0 is falsy — so the plant that
         # severed EVERY course scored a perfect failure and was reported as a pass. Explicit
         # None, never truthiness, on any value whose legitimate range includes zero.
         test=lambda m: m["continuity"]["continued"] is not None
         and m["continuity"]["continued"] < 0.75),
]


def channel_plant(w, h, seed, mat):
    """THE PLANT FOR CHANNEL LEGIBILITY: wear that takes nothing away.

    The three wear terms are set to 1.0 — a trodden stone keeps all its grain, all its value
    spread and a full-depth arris — so the channel is declared and delivers nothing. The
    instrument must report ratios at 1.0 and therefore NOTHING TO READ. If it reports a visible
    channel here, it is reading the channel's declaration rather than its pixels, which is the
    failure mode that let a real channel go unseen by three rounds of seats.
    """
    # ⚠ THE THREE CONSTANTS DO NOT SHARE A NULL, and this plant is what found that out.
    #
    # WEAR_GRAIN and WEAR_SPREAD are MULTIPLIERS on what a stone keeps, so 1.0 is "no wear".
    # WEAR_ARRIS is a FRACTION of the way the joint rises toward the stone, so its null is 0.0 and
    # 1.0 erases the joint completely. Setting all three to 1.0 therefore delivered the most worn
    # floor the system can make, the instrument correctly reported a very visible channel, and the
    # plant read that as the instrument failing. Two mistakes agreeing on a verdict.
    # FIVE TERMS NOW, AND THE PLANT HAS CAUGHT EVERY ONE OF THEM AS IT WAS ADDED — the arris, then
    # the dressing counts, now the channel's bias on the wear field. Each time, a term was written
    # where it belonged in the art and not where it belonged in the wear block, the plant went
    # SILENT, and the channel stayed visible through the one term the null could not reach. That
    # is what a control is for, and it is the reason this list is checked rather than remembered.
    keep = (CA.WEAR_GRAIN, CA.WEAR_SPREAD, CA.WEAR_ARRIS, CA.WEAR_BANDS, CA.WEAR_PITS,
            CA.CHANNEL_WEAR)
    CA.WEAR_GRAIN, CA.WEAR_SPREAD, CA.WEAR_ARRIS = 1.0, 1.0, 0.0
    CA.WEAR_BANDS, CA.WEAR_PITS = CA.MARK_BANDS, CA.MARK_PITS
    CA.CHANNEL_WEAR = 0
    try:
        band = lambda x, y: w // 2 - 1 <= x <= w // 2
        img, joints, _, _c, _d = assemble(w, h, seed, mat, band)
        base, _j, _t, _c2, _d2 = assemble(w, h, seed, mat, None)
        cells = [(x, y) for y in range(h) for x in range(w) if band(x, y)]
        m = channel_legibility(img, base, joints | _c | _d, cells, w, h)
    finally:
        (CA.WEAR_GRAIN, CA.WEAR_SPREAD, CA.WEAR_ARRIS,
         CA.WEAR_BANDS, CA.WEAR_PITS, CA.CHANNEL_WEAR) = keep
    flat = all(abs((m[k] or 1.0) - 1.0) < 0.02
               for k in ("texture_ratio", "variety_ratio", "arris_ratio"))
    return flat, m


def chroma_read(img, traffic, w, h):
    """THE CHROMA CHANNEL, read off the pixels: is the cast where the traffic is?

    Two numbers, and the second is the one §5.4 cares about. `separation` asks whether trodden
    stone is measurably more coloured than sheltered stone. `cast_share` asks how much of the
    floor is carrying colour at all — because a cast everywhere is not a signal, it is a wash,
    and *general richness is forbidden; saturation spent everywhere identifies nothing.*

    A third number, `parity_ratio`, exists only to be broken: chroma keyed to the tile a stone is
    seen from rather than to the world would divide cleanly along the grid, and §8.3.1 does not
    stop applying because the lattice is made of colour.
    """
    a = np.asarray(img).astype(float)
    rc = (a.max(-1) - a.min(-1)) / np.maximum(a.max(-1), 1e-6)
    hot = np.zeros(rc.shape, bool)
    cold = np.zeros(rc.shape, bool)
    for y in range(h):
        for x in range(w):
            lvl = int(traffic[x, y])
            sl = (slice(y * T, (y + 1) * T), slice(x * T, (x + 1) * T))
            if lvl >= 200:
                hot[sl] = True
            elif lvl <= 30:
                cold[sl] = True
    ev = np.zeros(rc.shape, bool)
    od = np.zeros(rc.shape, bool)
    for y in range(h):
        for x in range(w):
            sl = (slice(y * T, (y + 1) * T), slice(x * T, (x + 1) * T))
            (ev if (x + y) % 2 == 0 else od)[sl] = True
    e, o = float(rc[ev].mean()), float(rc[od].mean())
    return dict(trodden=float(rc[hot].mean()) if hot.any() else None,
                off_route=float(rc[cold].mean()) if cold.any() else None,
                separation=(float(rc[hot].mean() - rc[cold].mean())
                            if hot.any() and cold.any() else None),
                cast_share=float((rc > 0.03).mean()),
                parity_ratio=float(max(e, o) / max(min(e, o), 1e-6)))


def erosion_read(img, joints, traffic, w, h):
    """FORM AS EROSION, read off the pixels: does the grain run WITH the route?

    A joint that survives is a dark line. Along a north-south corridor the crossed BED joints pack
    shut and the HEAD joints running with the route survive, so the ratio of how far each sits
    below its stone IS the directional grain, in one number.

    `flatten` is the other half: a walked stone loses its crown, so its faces lose value spread.
    """
    L = np.asarray(img).astype(float)[..., 0]
    med = float(np.median(L[~joints]))
    bedj = np.zeros(joints.shape, bool)
    bedj[:, 1:-1] = joints[:, :-2] & joints[:, 2:]
    headj = np.zeros(joints.shape, bool)
    headj[1:-1, :] = joints[:-2, :] & joints[2:, :]
    hot = np.zeros(joints.shape, bool)
    cold = np.zeros(joints.shape, bool)
    for y in range(h):
        for x in range(w):
            sl = (slice(y * T, (y + 1) * T), slice(x * T, (x + 1) * T))
            lvl = int(traffic[x, y])
            if lvl >= 200:
                hot[sl] = True
            elif lvl <= 30:
                cold[sl] = True

    def ratio(m):
        b = bedj & ~headj & m
        hh = headj & ~bedj & m
        if b.sum() < 50 or hh.sum() < 50:
            return None
        return float((med - L[hh].mean()) / max(med - L[b].mean(), 1e-6))

    return dict(grain_ratio_trodden=ratio(hot), grain_ratio_off=ratio(cold),
                spread_trodden=float(L[(~joints) & hot].std()) if hot.any() else None,
                spread_off=float(L[(~joints) & cold].std()) if cold.any() else None)


def erosion_plant(w, h, seed, mat):
    """The plants for form-as-erosion: null it entirely, and null only its direction."""
    tr = np.zeros((w, h), dtype=np.uint8)
    tr[w // 2 - 1:w // 2 + 1, :] = 255
    out = {}
    for name in (None, "no_erosion"):
        img, j, _, _, _ = assemble(w, h, seed, mat, defect=name, traffic=tr)
        out[name or "live"] = erosion_read(img, j, tr, w, h)
    keep = CA.DEFORM_ANISO
    CA.DEFORM_ANISO = 0.0
    try:
        img, j, _, _, _ = assemble(w, h, seed, mat, traffic=tr)
        out["isotropic"] = erosion_read(img, j, tr, w, h)
    finally:
        CA.DEFORM_ANISO = keep
    return out


def chroma_plant(w, h, seed, mat):
    """Two plants for the chroma channel, and the live arm they are judged against."""
    tr = np.zeros((w, h), dtype=np.uint8)
    tr[w // 2 - 1:w // 2 + 1, :] = 255
    out = {}
    for name in (None, "flat_chroma", "chroma_lattice"):
        img, _j, _t, _c, _d = assemble(w, h, seed, mat, defect=name, traffic=tr)
        out[name or "live"] = chroma_read(img, tr, w, h)
    return out


def run_plants(w, h, seed, mat):
    print("PLANTS — every instrument must demonstrate it can fail (§4, bible §13.5)\n")
    rows, ok = [], True
    flat, cm = channel_plant(w, h, seed, mat)
    print("  %-16s -> %-14s %s" % ("flat_channel", "channel", "FIRED" if flat else "SILENT"))
    print("       wear that takes nothing away — the channel declared and not delivered")
    print("       texture %s | variety %s | arris %s  (all 1.0 = nothing to read)"
          % (cm["texture_ratio"], cm["variety_ratio"], cm["arris_ratio"]))
    if not flat:
        print("       ^^ the instrument reports a channel where none was delivered. It is "
              "reading the declaration, not the pixels.")
    ok &= flat
    rows.append(dict(plant="flat_channel", must_fire="channel_legibility", fired=flat,
                     why="wear multipliers set to 1.0: the channel is declared and delivers "
                         "nothing", measured=cm))

    ep = erosion_plant(w, h, seed, mat)
    live_e, none_e, iso_e = ep["live"], ep["no_erosion"], ep["isotropic"]
    for nm, m, fired, why, detail in (
        ("no_erosion", none_e,
         abs((none_e["grain_ratio_trodden"] or 1.0) - 1.0) < 0.15
         and (none_e["spread_trodden"] or 0) > (live_e["spread_trodden"] or 0) * 1.2,
         "form-as-erosion nulled entirely — no flattening, no directional compaction, so the "
         "floor must lose both its grain and its ground-down look",
         "grain %.2f (live %.2f) | face spread %.1f (live %.1f)"
         % (none_e["grain_ratio_trodden"] or 0, live_e["grain_ratio_trodden"] or 0,
            none_e["spread_trodden"] or 0, live_e["spread_trodden"] or 0)),
        ("isotropic_erosion", iso_e,
         abs((iso_e["grain_ratio_trodden"] or 1.0) - 1.0) < 0.15,
         "the erosion kept but its DIRECTION removed — the stones still grind down, and the "
         "floor must stop saying which way",
         "grain %.2f (live %.2f)" % (iso_e["grain_ratio_trodden"] or 0,
                                     live_e["grain_ratio_trodden"] or 0)),
    ):
        print("  %-16s -> %-14s %s" % (nm, "erosion_read", "FIRED" if fired else "SILENT"))
        print("       %s" % why)
        print("       %s" % detail)
        ok &= bool(fired)
        rows.append(dict(plant=nm, must_fire="erosion_read", fired=bool(fired), why=why,
                         measured=m))

    cp = chroma_plant(w, h, seed, mat)
    live, flatc, latt = cp["live"], cp["flat_chroma"], cp["chroma_lattice"]
    for nm, m, fired, why, detail in (
        ("flat_chroma", flatc, (flatc["separation"] or 0) < 0.005,
         "the chroma channel nulled while the joints keep working — the combined verdict must "
         "fall back to what the joint lever alone can carry",
         "separation %.4f (live %.4f) | cast %.1f%%"
         % (flatc["separation"] or 0, live["separation"] or 0, flatc["cast_share"] * 100)),
        ("chroma_lattice", latt, latt["parity_ratio"] > 3.0,
         "chroma keyed to the tile a stone is SEEN FROM rather than to the world — §8.3.1's "
         "lattice restated in the colour domain",
         "parity ratio %.2f (live %.2f)" % (latt["parity_ratio"], live["parity_ratio"])),
    ):
        print("  %-16s -> %-14s %s" % (nm, "chroma_read", "FIRED" if fired else "SILENT"))
        print("       %s" % why)
        print("       %s" % detail)
        ok &= fired
        rows.append(dict(plant=nm, must_fire="chroma_read", fired=bool(fired), why=why,
                         measured=m))
    for p in PLANTS:
        img, joints, tr, ck, dr = assemble(w, h, seed, mat, defect=p["name"])
        m = measure(img, joints, w, h, tr, seed, ck, dr)
        fired = bool(p["test"](m))
        rows.append(dict(plant=p["name"], must_fire=p["must_fire"], why=p["why"],
                         fired=fired, measured=m))
        ok &= fired
        print("  %-16s -> %-14s %s" % (p["name"], p["must_fire"], "FIRED" if fired else "SILENT"))
        print("       %s" % p["why"])
        print("       boundary_step %s | continuity %s | course heights %s | duplicate "
              "skeletons %.1f%% | joint spread %s rungs"
              % (m["boundary_step"]["ratio"], m["continuity"]["continued"],
                 m["banding"]["distinct_spacings"], 100 * m["skeleton"]["duplicate_rate"],
                 m["joint_variation"]["spread_rungs"]))
        if not fired:
            print("       ^^ THIS INSTRUMENT HAS NOT SHOWN IT CAN FAIL. Its pass does not count.")
    print()
    # ================= THE PLANT RUN ASSERTS ITS OWN COMPLETION =================
    #
    # RULED (Rafe, 2026-08-30) after a crash read as a silence. An unbound name took the run down
    # after ELEVEN of fourteen plants, and the only visible symptom was a smaller FIRED count —
    # which looks exactly like "three plants went silent", the one thing this file exists to
    # report. A control suite that can end early and quietly is not a control suite.
    #
    # AN EARLY EXIT IS RED, NEVER QUIET. The count is declared, not inferred from what happened to
    # run: the two special plants plus every entry in the PLANTS table.
    # 1 channel + 2 erosion + 2 chroma + the table. Declared as a sum of its parts rather than a
    # literal, and it caught its own author on the first run: written as 2+2+len it reported
    # "14 of 13" and went red, which is the check doing exactly its job on the way in.
    expected = 1 + 2 + 2 + len(PLANTS)
    if len(rows) != expected:
        print("\n  *** PLANT RUN INCOMPLETE: %d of %d plants reported. The suite did not finish, "
              "which is a RED result and never a quiet one. ***" % (len(rows), expected))
        ok = False
    else:
        print("\n  plant run complete: %d of %d." % (len(rows), expected))

    return ok, rows


def main():
    ap = argparse.ArgumentParser()
    # SIXTEEN, NOT EIGHT — the field has to be big enough to contain the thing being measured.
    #
    # The wear field varies over five and eleven tiles, and an 8x8 field at the origin happens to
    # sit entirely inside one high-wear region: every joint there is open, `joint_variation`
    # reported a spread of 0.000, and it looked exactly like the uniform-mortar defect it exists
    # to catch. The floor was varying; the window was too small to see it. A window that cannot
    # contain the variation reports its absence, which is a false negative dressed as a measurement.
    ap.add_argument("--w", type=int, default=16)
    ap.add_argument("--h", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--plants", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    os.makedirs(a.out, exist_ok=True)

    plants = None
    if a.plants:
        ok, plants = run_plants(a.w, a.h, a.seed, mat)
        if not ok:
            print("REFUSING: an instrument could not be made to fail. Fix the instrument first.")
            return 1

    print("ASHLAR FIELD — %dx%d cells, seed %d\n" % (a.w, a.h, a.seed))
    rows = {}
    for label, worn in (("ordinary", None),
                        ("with_channel", lambda x, y: a.w // 2 - 1 <= x <= a.w // 2)):
        img, joints, tr, ck, dr = assemble(a.w, a.h, a.seed, mat, worn)
        p = os.path.join(a.out, "ashlar_%s.png" % label)
        Image.fromarray(img).save(p)
        m = measure(img, joints, a.w, a.h, tr, a.seed, ck, dr)
        try:
            import field_preview as FP
            m["lattice"] = FP.lattice_score(img)
        except Exception:
            m["lattice"] = None
        rows[label] = dict(file=os.path.relpath(p, REPO), **m)
        e, b, c, g = m["enclosure"], m["boundary_step"], m["continuity"], m["grid_hiding"]
        print("  %s" % label)
        print("     enclosure:    %d regions, largest holds %.1f%% (session one: 99.1%%), "
              "median %dpx, %d over 64px"
              % (e["regions"], 100 * e["largest_share"], e["median_region"],
                 e["regions_over_64px"]))
        print("     boundary step: %.3f at boundaries vs %.3f inside — ratio %s  (was 7.44x, "
              "then 2.95x)" % (b["boundary_mean"], b["interior_mean"], b["ratio"]))
        if b["channel_edge_mean"] is not None:
            print("                    channel edge %.3f over %d px — an INTENDED transition, "
                  "reported apart" % (b["channel_edge_mean"], b["channel_edge_n"]))
        print("     continuity:   %s of joints arriving at a vertical boundary carry through "
              "(%d of %d)" % (c["continued"], c["continuing"], c["arriving"]))
        print("     grid hiding:  boundary bed vs mid bed — density %s, value %s; "
              "boundary column vs others %s"
              % (g["bed_density_ratio"], g["bed_value_ratio"], g["col_density_ratio"]))
        bn = m["banding"]
        print("     banding:      %d courses at %d distinct heights %s, modal share %s, sd %s"
              % (bn.get("courses", 0), bn["distinct_spacings"], bn.get("spacings"),
                 bn["modal_share"], bn["sd"]))
        cp = m["constant_pitch"]
        print("     tile-phase:   %d of %d full-width joints sit at the tile pitch (%.0f%%) — "
              "the corner theorem's bill; cannot reach 0 with runtime addressing"
              % (cp["at_tile_phase"], cp["full_width_lines"], 100 * (cp["share"] or 0)))
        ck_ = m.get("cracks")
        if ck_:
            print("     cracks:       %d marks, median %dpx, max %dpx; %d of them cross a tile "
                  "boundary (%.0f%%). The retired overlay's median mark was 4px."
                  % (ck_["marks"], ck_["median_px"], ck_["max_px"], ck_["crossing_a_boundary"],
                     100 * (ck_["share_crossing"] or 0)))
        jv = m["joint_variation"]
        print("     joint age:    open decile %s vs tight decile %s — a spread of %s rungs "
              "(uniform mortar reads ~0)"
              % (jv.get("open_decile"), jv.get("tight_decile"), jv["spread_rungs"]))
        sk = m["skeleton"]
        print("     skeletons:    %d distinct in %d cells; %d cells share one (%.1f%%); "
              "identical neighbours %d of %d"
              % (sk["distinct_skeletons"], sk["cells"], sk["cells_sharing_a_skeleton"],
                 100 * sk["duplicate_rate"], sk["identical_neighbours"], sk["neighbour_pairs"]))
        if worn:
            cells = [(x, y) for y in range(a.h) for x in range(a.w) if worn(x, y)]
            base, _bj, _bt, _bc, _bd = assemble(a.w, a.h, a.seed, mat, None)
            # Cracks are not stone faces, and leaving them in diluted the ratio from 0.37 to 0.74
            # — the channel's own signal halved by a feature that has nothing to do with it.
            cl = channel_legibility(img, base, joints | ck | dr, cells, a.w, a.h)
            rows[label]["channel_legibility"] = cl
            print("     channel:      texture %s, variety %s, arris %s "
                  "(the same stones unpolished = 1.000; below it, polish took something away)"
                  % (cl["texture_ratio"], cl["variety_ratio"], cl["arris_ratio"]))
        if m["lattice"]:
            print("     lattice:      %.4f" % m["lattice"]["lattice"])

    res = dict(commit=FL.git_commit(), grid=[a.w, a.h], seed=a.seed,
               session_one_largest_share=0.991,
               prior_boundary_step_ratio=dict(unblended=7.44, blended=2.95),
               plants=plants, fields=rows)
    p = os.path.join(a.out, "ASHLAR-FIELD.json")
    with open(p, "w") as f:
        json.dump(res, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
