#!/usr/bin/env python3
"""§6.4 probe — the BLIND TREATMENT CENSUS, and the control that lets its counts mean anything.

WHAT IT IS FOR
--------------
Stage 1 owes two eye-side counts per arm: `rejected-at-birth` (unusable regardless of
treatment) and `treatment-miss` (usable art, wrong lighting). They are kill-criterion
numerators, so they cannot be skipped — and they cannot be produced by a script either.

WHY AN LLM AND NOT A SCRIPT
---------------------------
§15 records `§6.3 receive-light (no baked highlight)` as **NO INSTRUMENT — a directional-
highlight census is owed**, and notes the sibling project's attempt "measured as a blunt proxy
and was refused a verdict". §13.4 forbids closing that gap by inventing a weak instrument,
because a proxy re-enters the optimisation and starts winning trades it has not earned. The
v0.3 amendment to §13.4 draws the line precisely:

    "a script emitting a number is an instrument and enters the optimisation; a blind LLM
     critic rendering a prose verdict is not."

So the census is a blind read, not a metric. No luminance-gradient score is computed anywhere
in this file, deliberately.

THE CONTROL, AND WHY IT IS SYNTHETIC
------------------------------------
LOOP-PROCESS §4 / §13.5: no instrument's pass counts until it has demonstrated it can fail,
and for a blind critic the prescribed form is a **plant**.

The obvious plant — "check the critic can pick arm A out" — is circular. A low score on arm A
would mean either *the critic cannot see key light* or *arm A never baked one*, and those are
exactly the two things the census exists to tell apart. Ground truth taken from the prompt is
not ground truth.

So the plants are **constructed, not prompted**. A real Stage 1 tile is mechanically given a
hard directional key light (banded, re-quantised, so it reads as authored pixel art and not as
a Photoshop gradient), and another is mechanically flattened to one value per material region.
Their treatment is known by construction and owes nothing to the generator's compliance.

**If the critic misreads the planted tiles, the census is VOID** — not discounted, void, and
its findings are not read (LOOP-PROCESS §4). A soft critic's counts are worse than no counts.

USAGE
  blind_census.py build    # sheets + private key. Do NOT read the key before calling.
  blind_census.py score    # plants first; per-arm counts only if the plants hold
"""
import argparse
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE1 = os.path.join(HERE, "stage1")
OUT = os.path.join(HERE, "census")
KEYFILE = os.path.join(OUT, "_census_key.json")      # ground truth; not read before calling
CALLS = os.path.join(OUT, "census_calls.json")       # the critic's blind calls

SCALE, COLS, PAD, GAP = 8, 6, 26, 18
PER_SHEET = 24          # small enough that each cell is actually looked at, not skimmed
BG, CARD, INK, DIM = (34, 34, 38), (58, 58, 64), (222, 222, 228), (150, 150, 158)
N_PLANTS_EACH = 5

# TWO INDEPENDENT AXES, called separately for every cell.
#
# A single label cannot carry both questions, and collapsing them corrupts both counts: a
# key-lit object would land in "not a tile" and vanish from the lighting census, while a
# planted cell whose donor happened to be a prop would void the control for a reason that has
# nothing to do with the critic's eye. They are also genuinely independent properties — a tile
# can be correctly framed and wrongly lit, or vice versa.
#
#   frame : is this a square, orthogonal, full-frame TILE, or is it not?   -> rejected-at-birth
#   light : is a directional key light depicted, or not?                   -> treatment-miss
FRAME_LABELS = ("TILE", "NOT_TILE")
LIGHT_LABELS = ("KEY", "FORM", "FLAT")


def font(sz):
    for p in ("/System/Library/Fonts/Menlo.ttc",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def quantise(img, n=12):
    """Back to a pixel-art-sized palette, so a constructed plant does not announce itself by
    having ten thousand colours when every real candidate has thirty."""
    return img.convert("RGB").quantize(colors=n, method=Image.MEDIANCUT).convert("RGB")


def plant_key(img):
    """Bake an unmistakable upper-left key light: four value bands across the diagonal, plus a
    hard specular on the brightest band. Banded and re-quantised so it reads as authored."""
    im = img.convert("RGB")
    w, h = im.size
    px = im.load()
    out = Image.new("RGB", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            t = (x / (w - 1) + y / (h - 1)) / 2.0          # 0 upper-left -> 1 lower-right
            band = min(3, int(t * 4))
            f = (1.75, 1.20, 0.78, 0.45)[band]
            r, g, b = px[x, y]
            if band == 0 and (r + g + b) / 3 > 96:          # specular on lit, light material
                op[x, y] = (255, 252, 240)
            else:
                op[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)))
    return quantise(out, 12)


def plant_flat(img):
    """Remove shading: quantise to a few material regions, then set every pixel in a region to
    that region's mean. No gradient, no occlusion darkening, no highlight survives."""
    im = img.convert("RGB")
    q = im.quantize(colors=5, method=Image.MEDIANCUT)
    idx = q.load()
    src = im.load()
    w, h = im.size
    acc = {}
    for y in range(h):
        for x in range(w):
            k = idx[x, y]
            r, g, b = src[x, y]
            a = acc.setdefault(k, [0, 0, 0, 0])
            a[0] += r; a[1] += g; a[2] += b; a[3] += 1
    mean = {k: (v[0] // v[3], v[1] // v[3], v[2] // v[3]) for k, v in acc.items()}
    out = Image.new("RGB", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            op[x, y] = mean[idx[x, y]]
    return out


def code_for(i):
    cons, vow = "BCDFGHJKLMNPQRSTVWXZ", "AEIOUY"
    return cons[i % 20] + vow[(i // 20) % 6] + cons[(i // 120) % 20] + str(i % 10)


def build():
    rows = []
    with open(os.path.join(STAGE1, "ledger.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("verdict") == "OK" and r.get("image") and r.get("claim", "").startswith("stage1:"):
                rows.append(r)
    if not rows:
        print("no Stage 1 images found", file=sys.stderr)
        return 1

    rng = random.Random(20260825)
    items = []
    for r in rows:
        items.append({"truth": "arm" + r["arm"] if "arm" in r else "arm?",
                      "arm": r.get("arm"), "subject": r.get("subject"),
                      "image": r["image"], "src": os.path.join(STAGE1, r["image"])})
    # arm/subject are on the row only if stage1.py wrote them; recover from the path otherwise
    for it in items:
        parts = it["image"].replace(os.sep, "/").split("/")
        if it["arm"] is None and len(parts) >= 3:
            it["arm"], it["subject"] = parts[0], parts[1]
            it["truth"] = "arm" + parts[0]

    os.makedirs(os.path.join(OUT, "plants"), exist_ok=True)
    donors = rng.sample(items, min(2 * N_PLANTS_EACH, len(items)))
    for i, d in enumerate(donors):
        src = Image.open(d["src"]).convert("RGB")
        kind = "PLANT_KEY" if i < N_PLANTS_EACH else "PLANT_FLAT"
        img = plant_key(src) if kind == "PLANT_KEY" else plant_flat(src)
        rel = os.path.join("plants", "%s_%02d.png" % (kind.lower(), i))
        img.save(os.path.join(OUT, rel))
        items.append({"truth": kind, "arm": None, "subject": d["subject"],
                      "image": rel, "src": os.path.join(OUT, rel)})

    rng.shuffle(items)
    key = {}
    for i, it in enumerate(items):
        it["code"] = code_for(i)
        key[it["code"]] = {"truth": it["truth"], "arm": it["arm"],
                           "subject": it["subject"], "image": it["image"]}

    f_h, f_s, f_c = font(19), font(12), font(13)
    sheets = []
    for s in range(0, len(items), PER_SHEET):
        chunk = items[s:s + PER_SHEET]
        ncols = min(COLS, len(chunk))
        nrows = (len(chunk) + ncols - 1) // ncols
        cw = 32 * SCALE
        ch = 32 * SCALE + 17
        W = PAD * 2 + ncols * cw + (ncols - 1) * GAP
        H = PAD + 52 + nrows * ch + (nrows - 1) * GAP + PAD
        sheet = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(sheet)
        d.text((PAD, PAD), "BLIND TREATMENT CENSUS — sheet %d" % (s // PER_SHEET + 1),
               font=f_h, fill=INK)
        d.text((PAD, PAD + 26),
               "Call each cell KEY / FORM / FLAT / UNUSABLE. Arms are not shown and the order "
               "carries no information. Planted cells are present.", font=f_s, fill=DIM)
        for i, it in enumerate(chunk):
            cx = PAD + (i % ncols) * (cw + GAP)
            cy = PAD + 52 + (i // ncols) * (ch + GAP)
            d.rectangle([cx - 3, cy - 3, cx + cw + 2, cy + ch + 2], fill=CARD)
            sheet.paste(Image.open(it["src"]).convert("RGB")
                        .resize((cw, cw), Image.NEAREST), (cx, cy))
            d.text((cx + 2, cy + 32 * SCALE + 2), it["code"], font=f_c, fill=INK)
            sheets.append
        p = os.path.join(OUT, "census_sheet_%d.png" % (s // PER_SHEET + 1))
        sheet.save(p)
        sheets.append(p)

    with open(KEYFILE, "w") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    print("cells: %d  (%d candidates + %d plants)" %
          (len(items), len(items) - 2 * N_PLANTS_EACH, 2 * N_PLANTS_EACH))
    for p in sheets:
        print("sheet -> %s" % p)
    print("key   -> %s   [DO NOT READ BEFORE CALLING]" % KEYFILE)
    return 0


def read_calls():
    """Calls are authored as a flat `CODE FRAME LIGHT` text file — one line per cell, so the
    critic writes calls without also writing JSON punctuation around them. Normalised to
    census_calls.json here so the scored artefact is machine-readable."""
    calls = {}
    with open(os.path.join(OUT, "calls_raw.txt")) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 3:
                calls[parts[0]] = {"frame": parts[1], "light": parts[2]}
    with open(CALLS, "w") as f:
        json.dump(calls, f, indent=1, sort_keys=True)
    return calls


def score():
    key = json.load(open(KEYFILE))
    calls = read_calls()
    missing = [c for c in key if c not in calls]
    if missing:
        print("INCOMPLETE — %d cells uncalled: %s" % (len(missing), missing[:12]))
        return 1
    for c, v in calls.items():
        if v.get("frame") not in FRAME_LABELS or v.get("light") not in LIGHT_LABELS:
            print("bad call for %s: %s" % (c, v))
            return 1

    print("=" * 78)
    print("CONTROL FIRST — the plants (LOOP-PROCESS §4). Their lighting is known by")
    print("construction, not by prompt, so it owes nothing to the generator's compliance.")
    print("=" * 78)
    print("Gated axis: LIGHT, and only the KEY / not-KEY distinction. That is the axis §6.3")
    print("legislates ('highlights are not baked in') and arm B's named failure lives on it.")
    print("The FORM-vs-FLAT boundary is NOT gated: a donor tile that was already near-flat")
    print("yields a 'FLAT plant' a truthful eye may correctly read as FORM, and a control that")
    print("punishes a correct call is not a control. Tuning plants until that stopped would be")
    print("manufacturing an instrument that cannot fail — the exact thing §13.5 forbids.\n")

    ok_key = n_key = ok_not = n_not = 0
    for code, meta in sorted(key.items()):
        t = meta["truth"]
        if t not in ("PLANT_KEY", "PLANT_FLAT"):
            continue
        got = calls[code]["light"]
        if t == "PLANT_KEY":
            n_key += 1
            good = got == "KEY"
            ok_key += good
            note = "ok" if good else "MISS — a baked key light called something else"
        else:
            n_not += 1
            good = got != "KEY"
            ok_not += good
            note = "ok (not KEY)" if good else "MISS — key light seen where there is none"
        print("  %-5s truth=%-11s light=%-5s %s" % (code, t, got, note))

    print("\n  planted key lights called KEY:      %d/%d" % (ok_key, n_key))
    print("  planted flat tiles NOT called KEY:  %d/%d" % (ok_not, n_not))
    passed = (ok_key == n_key) and (ok_not == n_not)
    print("\n  CONTROL: %s" % ("PASS — the census can tell depicted light from its absence."
                                if passed else "FAIL — VOID."))
    if not passed:
        print("\n  The census is VOID (LOOP-PROCESS §4: not discounted, void). Its per-arm")
        print("  counts are NOT reported. Reported instead: ⚠ NO INSTRUMENT for treatment-miss")
        print("  — which is §15's existing status for §6.3, and the correct output.")
        return 2

    print("\n" + "=" * 78)
    print("PER-ARM COUNTS  (plants %d/%d correct)" % (ok_key + ok_not, n_key + n_not))
    print("=" * 78)
    intended = {"A": "KEY", "B": "FORM", "C": "FLAT"}
    print("%-4s %-6s %4s %10s %8s %7s %7s %8s" %
          ("arm", "subj", "n", "not-tile", "tiles", "KEY*", "FORM", "FLAT"))
    out = {}
    for arm in ("A", "B", "C"):
        for subj in ("floor", "wall"):
            cells = [c for c, m in key.items() if m["arm"] == arm and m["subject"] == subj]
            if not cells:
                continue
            nt = sum(1 for c in cells if calls[c]["frame"] == "NOT_TILE")
            tiles = [c for c in cells if calls[c]["frame"] == "TILE"]
            cnt = {l: sum(1 for c in tiles if calls[c]["light"] == l) for l in LIGHT_LABELS}
            allk = sum(1 for c in cells if calls[c]["light"] == "KEY")
            hold = cnt[intended[arm]]
            out["%s/%s" % (arm, subj)] = {
                "n": len(cells), "rejected_at_birth_not_tile": nt, "tiles": len(tiles),
                "light_on_tiles": cnt, "KEY_all_cells_licensed": allk,
                "treatment_hold": hold, "treatment_miss": len(tiles) - hold}
            print("%-4s %-6s %4d %10d %8d %7d %7d %8d" %
                  (arm, subj, len(cells), nt, len(tiles),
                   cnt["KEY"], cnt["FORM"], cnt["FLAT"]))

    print("\n* KEY is the controlled column — the one number the plants licensed.")
    print("  A high KEY count on arm B or C is §6.4's named failure: the generator reverting")
    print("  to DEPICTING light. A low KEY count on arm A is a positive-control problem.")
    print("\nThe FORM/FLAT split below KEY is an UNLICENSED secondary read. It has no control")
    print("and must not be promoted into a verdict.")
    with open(os.path.join(OUT, "census_result.json"), "w") as f:
        json.dump({"control": {"plant_key_ok": ok_key, "plant_key_n": n_key,
                               "plant_notkey_ok": ok_not, "plant_notkey_n": n_not,
                               "passed": passed, "gated_axis": "KEY vs not-KEY"},
                   "per_cell": out}, f, indent=1)
    print("\nresult -> %s" % os.path.join(OUT, "census_result.json"))
    print("\n⚠ These are counts from a blind read, not a metric, and they do not rule. The")
    print("  kill criterion's effort ratio uses generations-per-ACCEPTED-reference, and")
    print("  'accepted' means picked by Rafe at STOP 1 — not called by this census.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("build", "score"))
    sys.exit(build() if ap.parse_args().mode == "build" else score())
