#!/usr/bin/env python3
"""THE INSTRUMENT — six geometric tests on the wall family, and six planted defects.

    python3 tools/tier1_walls/wall_laws.py --controls   # the plants. Run this FIRST.
    python3 tools/tier1_walls/wall_laws.py              # the family

NO TEST HERE SCORES A REGISTER CLAUSE (bible section 13.4). Every one is geometry — value
populations, periodicity, per-pixel variance across a set, edge continuity, joint pitch.
*Nothing is staged*, *the art plays it straight* and *nothing is ruined, things are used up*
have **NO INSTRUMENT** here and are carried at the human gate. There is no dread score.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (section 13.5, LOOP-PROCESS section 4). Each test
below has a plant that carries the defect **on the axis the test claims** — section 4.1's law,
learned twice on this project from levers that moved pixels and proved nothing. `--controls`
requires every plant to fire AND requires the legal family to come back clean, because an
instrument that reds on everything is as decorative as one that greens on everything.
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
import compose_walls as CW      # noqa: E402

T = CW.T
FACE_ROW = CW.FACE_TOP_ROW


def lum(a):
    return a.astype(float) @ np.array([0.299, 0.587, 0.114])


def load_family(assets):
    man = json.load(open(os.path.join(assets, "MANIFEST.json")))
    imgs = {}
    for t in man["tiles"]:
        imgs[t["id"]] = lum(np.asarray(Image.open(os.path.join(assets, t["file"])).convert("RGB")))
    return man, imgs


# ── the six tests ────────────────────────────────────────────────────────────────────────────

def _largest_blob(mask):
    """Size of the biggest 4-connected True region. Flood fill; no scipy dependency."""
    m = mask.copy()
    best = 0
    hgt, w = m.shape
    for sy in range(hgt):
        for sx in range(w):
            if not m[sy, sx]:
                continue
            stack, n = [(sy, sx)], 0
            m[sy, sx] = False
            while stack:
                y, x = stack.pop()
                n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < hgt and 0 <= nx < w and m[ny, nx]:
                        m[ny, nx] = False
                        stack.append((ny, nx))
            best = max(best, n)
    return best


def two_planes(man, imgs):
    """A face tile carries TWO value populations, split at the turn; a top tile carries one.

    Section 3's whole claim in one number. Reported as the separation between the mean of the
    band above the turn and the band below it, in ladder rungs — rungs rather than luminance
    because a separation smaller than the quantiser is a separation that does not exist
    (section 13.8).
    """
    step = man["ladder_step"]
    seps = []
    for t in man["tiles"]:
        if t["cls"] != "face":
            continue
        a = imgs[t["id"]]
        top = a[2:FACE_ROW - 1].mean()
        face = a[FACE_ROW + CW.OCCLUSION_ROWS:].mean()
        seps.append((top - face) / step)
    if not seps:
        return dict(pass_=False, why="no face tiles")
    return dict(pass_=bool(min(seps) >= 1.5), min_rungs=round(float(min(seps)), 3),
                mean_rungs=round(float(np.mean(seps)), 3), n=len(seps),
                bound="min separation >= 1.5 rungs")


def flat_top(man, imgs):
    """The top plane is not the face re-toned (section 3.1).

    ⚠ THE FIRST VERSION OF THIS TEST MEASURED THE WRONG THING AND FAILED THE LEGAL FAMILY, and
    the correction is worth keeping because it is a general one. It compared the peak-to-mean
    power of each band's row profile, reasoning that coursed material is periodic. But a smooth
    fourteen-row profile with grain on it is ALSO dominated by one low frequency, so the statistic
    reported 4.8 on a top plane that has no courses in it at all. Peak-to-mean power says *one
    frequency dominates*, which is not what *coursed* means.

    What section 3.1 actually forbids is visible on the pixels: **the face shows BED JOINTS —
    horizontal dark lines at the course pitch — and the top must not.** So the test counts rows
    whose mean sits a rung or more below the band's own median. The face has them by
    construction; a plane of stone tops has none.

    The forced boundary joint (section 8.3.3) is excluded by row, declared, not thresholded away.
    """
    step = man["ladder_step"]
    worst, who = 0, None
    counts = []
    for t in man["tiles"]:
        if t["cls"] != "face":
            continue
        a = imgs[t["id"]]
        band = a[CW.BED_ROWS:FACE_ROW]
        rows = band.mean(axis=1)
        dark = int((rows <= np.median(rows) - step).sum())
        counts.append(dark)
        if dark > worst:
            worst, who = dark, t["id"]
    return dict(pass_=bool(worst == 0), joint_rows_in_top_band=worst, tile=who,
                mean=round(float(np.mean(counts)), 3), n=len(counts),
                bound="zero rows in the top band a full rung below its own median")


def incident_free_top(man, imgs):
    """No feature sits at a constant position across the top set (section 8.3.1).

    Per-pixel standard deviation across every top tile in the family. A pixel that is the same in
    all of them is a treatment at a constant position, which becomes a lattice when tiled — and
    the test is *where does it sit, and does it sit there every time*, not *what is it*.

    THE BED JOINT IS EXEMPT AND SAYS SO. Section 8.3.3's corner theorem forces one joint onto
    every tile boundary across the run; it is not an incident, it is the only construction in
    which a block never crosses a grid corner. It is excluded by ROW, declared here, rather than
    by a threshold that would quietly forgive anything else in the same place.
    """
    step = man["ladder_step"]
    out = {}
    for cls in ("top_h", "top_v"):
        stack = np.array([imgs[t["id"]] for t in man["tiles"] if t["cls"] == cls])
        sd = stack.std(axis=0)
        m = np.ones_like(sd, dtype=bool)
        if cls == "top_h":
            m[:CW.BED_ROWS, :] = False
        else:
            m[:, :CW.BED_ROWS] = False
        # ⚠ A SHARE IS THE WRONG STATISTIC HERE AND THE PLANT PROVED IT. A four-pixel tick in
        # every tile is 0.4% of a 32x32 field, which no share-based bound can separate from
        # nothing at all — and four pixels at a constant offset is exactly the thing §8.3.1
        # forbids, because thirty copies of it is a lattice. What matters is not how MUCH is
        # frozen but whether anything COHERENT is: the size of the largest connected frozen
        # region. One stray pixel is noise; a 2x2 is a mark.
        frozen = (sd < 0.5) & m
        out[cls] = dict(frozen_px=int(frozen.sum()),
                        largest_frozen_blob=int(_largest_blob(frozen)),
                        sd_rungs=round(float(sd[m].mean() / step), 3))
    worst = max(v["largest_frozen_blob"] for v in out.values())
    return dict(pass_=bool(worst <= 2), largest_frozen_blob=worst, per_class=out,
                bound="no connected region larger than 2px identical across the whole set")


def no_ring(man, imgs):
    """No tile carries a dark or pale edge on all four sides (section 12.1, value-agnostic).

    A ring is a treatment present on every side REGARDLESS of what adjoins it. The test is
    therefore four-sided and signed: it fires whether the border is darker than the interior or
    lighter, because the worked example in section 12.1 was culled for a PALE one.

    ⚠ It reads one tile, and section 12.1's own scale ruling says a ring is judged AS LAID. This
    test can only catch a ring that is inside a single cell; the field census below is what looks
    at the laid version, and neither is a substitute for the gate.
    """
    worst, who = 0.0, None
    for t in man["tiles"]:
        if t["cls"] == "void":
            continue
        a = imgs[t["id"]]
        sides = [a[0, :].mean(), a[-1, :].mean(), a[:, 0].mean(), a[:, -1].mean()]
        interior = a[2:-2, 2:-2].mean()
        # A ring needs ALL FOUR sides to deviate the same way; a joint on one boundary does not.
        d = [s - interior for s in sides]
        if all(x < 0 for x in d) or all(x > 0 for x in d):
            v = min(abs(x) for x in d) / max(interior, 1e-6)
            if v > worst:
                worst, who = v, t["id"]
    return dict(pass_=bool(worst <= 0.12), worst=round(float(worst), 4), tile=who,
                bound="no tile with all four borders deviating >12% the same way")


def edge_agreement(man, imgs):
    """A block that crosses a boundary is drawn the same on both sides of it (section 8.3.2).

    For every edge key, take the tile that has that key on its EAST and the tile that has it on
    its WEST, butt them together, and measure the value step across the seam against the step
    between any two adjacent interior columns. Agreement means the seam is not distinguishable
    from anywhere else in the material — the same statistic the floor family reports.
    """
    tbl = man["table"]["top_h"]
    steps, base = [], []
    # EDGE FAMILY 0 PUTS A JOINT ON THE BOUNDARY, so its "seam" is a joint and is meant to be a
    # large step. Including it measures the joint and calls it a disagreement — which is the
    # instrument marking the corner theorem's forced construction as a defect. The question here
    # is only whether a block that CROSSES a boundary is drawn the same on both sides of it, so
    # the crossing families are the ones tested and the jointed one is named rather than averaged
    # in.
    for k in range(1, man["edge_families"]):
        for var in range(man["variants"]):
            for other in range(man["edge_families"]):
                west = imgs[tbl["%d,%d,%d" % (other, k, var)]]
                east = imgs[tbl["%d,%d,%d" % (k, other, var)]]
                steps.append(float(np.abs(west[:, -1] - east[:, 0]).mean()))
                base.append(float(np.abs(west[:, 1:] - west[:, :-1]).mean()))
    ratio = float(np.mean(steps) / max(np.mean(base), 1e-9))
    return dict(pass_=bool(ratio <= 1.35), seam_over_interior=round(ratio, 4),
                seam=round(float(np.mean(steps)), 3), interior=round(float(np.mean(base)), 3),
                n=len(steps), bound="seam step <= 1.35x an ordinary interior step")


def constant_pitch(man, imgs, cells=12):
    """How much of the laid field's joint network sits at exactly the tile pitch.

    Section 8.3.3 REPORTS this rather than forbidding it: a joint on every tile boundary is what
    the corner theorem forces, and *"it cannot reach 0 while stone values are addressed, and that
    is not a defect to be chased."* What must not happen is the rest of the network collapsing
    onto the same lattice, so the number reported is the share of full-height dark columns that
    land on a tile boundary.
    """
    tbl = man["table"]["top_h"]
    ef, nv = man["edge_families"], man["variants"]
    row = []
    for i in range(cells):
        ka = CW.h(man["salts"]["v"], "v", i, 5) % ef
        kb = CW.h(man["salts"]["v"], "v", i + 1, 5) % ef
        var = CW.h(90777, "h", i, 5) % nv
        row.append(imgs[tbl["%d,%d,%d" % (ka, kb, var)]])
    field = np.hstack(row)
    colmean = field.mean(axis=0)
    # ⚠ A QUARTILE IS THE WRONG THRESHOLD AND THE PLANT PROVED IT. The degenerate case this test
    # exists to catch — every head joint driven onto the tile boundary — leaves the interior FLAT,
    # and a flat interior puts the 25th percentile ON the interior value, so every interior column
    # counts as "dark" and the share of them on a boundary comes back low. The instrument reported
    # its own defect as a pass. A joint is not a quantile of the field, it is a fixed depth below
    # the material, so the threshold is stated in rungs.
    dark = np.where(colmean <= np.median(colmean) - 1.5 * man["ladder_step"])[0]
    on_pitch = sum(1 for c in dark if c % T < CW.BED_ROWS or c % T >= T - CW.BED_ROWS)
    share = on_pitch / max(len(dark), 1)
    return dict(pass_=bool(share <= 0.60), on_pitch_share=round(float(share), 4),
                dark_columns=int(len(dark)), field="%dx1 cells" % cells,
                bound="<= 60% of the darkest columns on a tile boundary")


def cap_seamless(man, imgs, cap=None):
    """The cap runs across a tile boundary as if the boundary were not there.

    RULED (Rafe, 2026-08-30): *"tops become a continuous mass — seams removed across tiles."*

    The old cap could not do this: §8.3.3's corner theorem forced a bed joint onto every tile
    boundary, and that joint at 32px pitch WAS the lattice the gate saw. The cap is one field now,
    cut into windows chosen by world position, so the test is whether two windows the engine will
    place side by side actually join — measured the way the bar was measured, so the two numbers
    are comparable: the step across the shared boundary against an ordinary interior step.
    """
    if cap is None:
        return dict(pass_=False, why="no cap manifest")
    n = cap["field_tiles"]
    W = _capwin(cap)
    steps, inner = [], []
    for gy in range(n):
        for gx in range(n):
            a = W("%d,%d" % (gx, gy))
            b = W("%d,%d" % ((gx + 1) % n, gy))
            c = W("%d,%d" % (gx, (gy + 1) % n))
            steps.append(float(np.abs(a[:, -1] - b[:, 0]).mean()))
            steps.append(float(np.abs(a[-1, :] - c[0, :]).mean()))
            inner.append(float(np.abs(np.diff(a, axis=1)).mean()))
    r = float(np.mean(steps) / max(np.mean(inner), 1e-6))
    return dict(pass_=bool(r <= 1.35), seam_over_interior=round(r, 4),
                seam=round(float(np.mean(steps)), 3), interior=round(float(np.mean(inner)), 3),
                pairs=len(steps), bound="cap seam <= 1.35x an interior step (the bar's is 4.44x)")


def cap_not_featureless(man, imgs, cap=None):
    """§8.3.1's mirror: incident-free is not empty.

    Held to the BAR's own cap, which carries 16.1 distinct values per tile with only 53.8% of it
    on the modal value (`WALL-RECIPE.md` A.1). A cap below that is emptier than the thing we are
    measured against.
    """
    if cap is None:
        return dict(pass_=False, why="no cap manifest")
    W = _capwin(cap)
    levels, modal = [], []
    for k in cap["table"]:
        a = W(k)
        levels.append(int(len(np.unique(np.round(a)))))
        mode = float(np.bincount(np.clip(np.round(a), 0, 255).astype(int).ravel()).argmax())
        modal.append(float((np.abs(a - mode) < 1.5).mean()))
    lv, md = float(np.mean(levels)), float(np.mean(modal))
    return dict(pass_=bool(lv >= 16.1 and md <= 0.538), levels_mean=round(lv, 2),
                modal_share=round(md, 4), n=len(levels),
                bound="at least the bar's 16.1 levels and no flatter than its 53.8% modal share")


def cap_field_scale(man, imgs, cap=None):
    """Variation lives at FIELD scale, not per cell.

    RULED: *"field-scale variation only — cracks spanning several tiles, slow value drift, no
    per-cell anything."* Two numbers: the drift across windows must exist (the bar's caps carry
    sd 7 to 30 within one map), and the field must carry no periodicity AT THE TILE PITCH, which
    is what a per-cell treatment would produce.
    """
    if cap is None:
        return dict(pass_=False, why="no cap manifest")
    n = cap["field_tiles"]
    W = _capwin(cap)
    means = [float(W("%d,%d" % (gx, gy)).mean()) for gy in range(n) for gx in range(n)]
    sd = float(np.std(means))
    # Reassemble the WHOLE field and look for power at the tile pitch on both axes.
    #
    # ⚠ The first version divided the tile-pitch bin by the MEAN of every other bin, and the mean
    # is swamped by the slow drift the cap is supposed to have: a planted per-cell stamp came back
    # at 0.97, silent, because the denominator was the field's own legitimate low-frequency
    # power. A spike is only a spike against its NEIGHBOURS, so the comparison is now the local
    # median either side of the bin — and the plant fires.
    field = np.vstack([np.hstack([W("%d,%d" % (gx, gy)) for gx in range(n)]) for gy in range(n)])
    # ⚠ And it averages the periodogram over every line, not the periodogram of the averaged
    # line. One profile gives one draw per bin from a distribution with as much spread as its own
    # mean, so an ordinary field can put 4.6x in the tile bin by luck alone — which is what the
    # legal cap did on the first run of this version, and it would have been reported as a defect.
    powers = []
    for ax in (0, 1):
        lines = field if ax == 0 else field.T
        spec = (np.abs(np.fft.rfft(lines - lines.mean(axis=1, keepdims=True), axis=1)) ** 2
                ).mean(axis=0)
        k = lines.shape[1] // CW.T
        neigh = np.concatenate([spec[k - 8:k - 1], spec[k + 2:k + 9]])
        powers.append(float(spec[k] / max(np.median(neigh), 1e-9)))
    tile_power = float(max(powers))
    return dict(pass_=bool(sd >= 5.0 and tile_power <= 4.0),
                window_mean_sd=round(sd, 3), tile_pitch_power=round(tile_power, 3),
                bound="drift sd >= 5 (the bar: 7..30) and no spike at the tile pitch")


TESTS = dict(two_planes=two_planes, flat_top=flat_top, incident_free_top=incident_free_top,
             no_ring=no_ring, edge_agreement=edge_agreement, constant_pitch=constant_pitch)
CAP_TESTS = dict(cap_seamless=cap_seamless, cap_not_featureless=cap_not_featureless,
                 cap_field_scale=cap_field_scale)

_CAPCACHE = {}


def _capwin(cap):
    """Window accessor. Returns the planted pixels when this is a planted copy, the shipped ones
    otherwise — so the three cap tests read a plant through exactly the path they read the family
    through, and a plant cannot fire by taking a different code path."""
    if "_imgs" in cap:
        return lambda k: cap["_imgs"][k]
    files = {t["id"]: t["file"] for t in cap["tiles"]}
    return lambda k: _capimg(cap["_root"], files[cap["table"][k]])


def _capimg(root, f):
    if f not in _CAPCACHE:
        _CAPCACHE[f] = lum(np.asarray(Image.open(os.path.join(root, f)).convert("RGB")))
    return _CAPCACHE[f]


def load_cap(assets):
    man = json.load(open(os.path.join(assets, "MANIFEST.json")))
    man["_root"] = assets
    return man


# ── the plants ───────────────────────────────────────────────────────────────────────────────

def cap_plant(cap, kind):
    """A copy of the cap carrying ONE defect, on the axis the matching test claims.

    Each of these is a construction the cap pass was ruled AGAINST, not a generic degradation:
      seam    — every window independently re-levelled. Continuous inside, discontinuous at every
                join: exactly the lattice the gate saw, produced without touching anything else.
      flatten — the featureless cap. §8.3.1's mirror: incident-free is not empty.
      percell — one treatment stamped at a constant offset inside every window: "no per-cell
                anything", violated at the tile pitch and nowhere else.
    """
    W = _capwin(cap)
    imgs = {k: W(k).copy() for k in cap["table"]}
    if kind == "seam":
        for i, k in enumerate(sorted(imgs)):
            imgs[k] += ((i * 37) % 41) - 20
    elif kind == "flatten":
        for k in imgs:
            imgs[k][:] = imgs[k].mean()
    elif kind == "percell":
        for k in imgs:
            imgs[k][6:10, 6:10] -= 40
    else:
        raise SystemExit("no cap plant for %s" % kind)
    out = dict(cap)
    out["_imgs"] = imgs
    return out


def plant(name, man, imgs):
    """Return a mutated copy of the family carrying ONE defect, on the axis its test claims."""
    out = {k: v.copy() for k, v in imgs.items()}
    step = man["ladder_step"]
    if name == "two_planes":
        # The face re-toned FROM the top: section 3.1's "it is more face", value-corrected so
        # nothing else moves. The separation collapses; nothing else does.
        for t in man["tiles"]:
            if t["cls"] == "face":
                a = out[t["id"]]
                a[FACE_ROW:] = a[:FACE_ROW] - 0.4 * step
    elif name == "flat_top":
        # The top band given the FACE's coursing pitch, at the top's own value.
        for t in man["tiles"]:
            if t["cls"] == "face":
                a = out[t["id"]]
                src = a[FACE_ROW:]
                a[:FACE_ROW] = src[:FACE_ROW] + (a[:FACE_ROW].mean() - src[:FACE_ROW].mean())
    elif name == "incident_free_top":
        # One tick at a fixed offset in every top tile. Four pixels; that is the point.
        for t in man["tiles"]:
            if t["cls"].startswith("top"):
                out[t["id"]][6:8, 5:7] = 20.0
    elif name == "no_ring":
        for t in man["tiles"]:
            if t["cls"] == "void":
                continue
            a = out[t["id"]]
            v = a[2:-2, 2:-2].mean() * 1.35
            a[0, :] = v; a[-1, :] = v; a[:, 0] = v; a[:, -1] = v      # a PALE ring
    elif name == "edge_agreement":
        # The crossing block drawn from the tile's own hash instead of the boundary's — which is
        # exactly what PickVariant does, and is the defect this whole family exists to avoid.
        for t in man["tiles"]:
            if t["cls"] == "top_h":
                out[t["id"]][:, -3:] += (t["id"] % 5 - 2) * step
    elif name == "constant_pitch":
        # Every head joint driven onto the tile boundary: agreement collapsed into constancy,
        # which is section 8.3.3's named degenerate case.
        for t in man["tiles"]:
            if t["cls"] == "top_h":
                a = out[t["id"]]
                interior = a[:, 3:-3].mean()
                a[:, 3:-3] = interior
                a[:, :2] = interior - 3 * step
                a[:, -2:] = interior - 3 * step
    else:
        raise SystemExit("no plant for %s" % name)
    return out


def run(man, imgs, only=None, cap=None):
    res = {}
    for name, fn in TESTS.items():
        if only and name != only:
            continue
        res[name] = fn(man, imgs)
    if cap is not None:
        for name, fn in CAP_TESTS.items():
            if only and name != only:
                continue
            res[name] = fn(man, imgs, cap)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=os.path.join(REPO, CW.ASSETS_REL))
    ap.add_argument("--cap", default=os.path.join(REPO, "src/Presentation/assets/tier1_cap"))
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()
    man, imgs = load_family(a.assets)
    cap = load_cap(a.cap) if os.path.exists(os.path.join(a.cap, "MANIFEST.json")) else None

    if not a.controls:
        res = run(man, imgs, cap=cap)
        ok = all(v["pass_"] for v in res.values())
        for k, v in res.items():
            print("  %-20s %s   %s" % (k, "PASS" if v["pass_"] else "FAIL",
                                       {kk: vv for kk, vv in v.items() if kk != "pass_"}))
        json.dump(dict(assets=os.path.relpath(a.assets, REPO), family=man["family"], results=res),
                  open(os.path.join(HERE, "evidence", "WALL-LAWS-%s.json" % man["arm"]), "w"),
                  indent=2)
        return 0 if ok else 1

    print("POSITIVE CONTROLS — every plant must fire on its own axis, and the legal family must")
    print("come back clean. An instrument that reds on everything is as decorative as one that")
    print("greens on everything.\n")
    clean = run(man, imgs, cap=cap)
    fails = [k for k, v in clean.items() if not v["pass_"]]
    print("  legal family : %s%s" % ("CLEAN" if not fails else "DIRTY - ",
                                     "" if not fails else ", ".join(fails)))
    rows, allgood = [], not fails
    for name in TESTS:
        p = run(man, plant(name, man, imgs), only=name)[name]
        fired = not p["pass_"]
        allgood &= fired
        rows.append((name, fired, p))
        print("  %-20s plant -> %s   %s" % (name, "FIRES" if fired else "SILENT",
                                            {k: v for k, v in p.items() if k != "pass_"}))
    if cap is not None:
        for name, kind in (("cap_seamless", "seam"), ("cap_not_featureless", "flatten"),
                           ("cap_field_scale", "percell")):
            p = CAP_TESTS[name](man, imgs, cap_plant(cap, kind))
            fired = not p["pass_"]
            allgood &= fired
            rows.append((name, fired, p))
            print("  %-20s plant -> %s   %s" % (name, "FIRES" if fired else "SILENT",
                                                {k: v for k, v in p.items() if k != "pass_"}))
    else:
        allgood = False
        print("  cap_*                NO CAP MANIFEST - the three cap instruments are unproven")

    json.dump(dict(family=man["family"], legal_clean=not fails,
                   plants={n: dict(fired=f, detail=d) for n, f, d in rows}),
              open(os.path.join(HERE, "evidence", "WALL-LAWS-CONTROLS.json"), "w"), indent=2)
    print("\n  VERDICT: %s" % ("all %d instruments have demonstrated they can fail" % len(rows)
                               if allgood else "NOT ALL INSTRUMENTS ARE PROVEN - see above"))
    return 0 if allgood else 1


if __name__ == "__main__":
    sys.exit(main())
