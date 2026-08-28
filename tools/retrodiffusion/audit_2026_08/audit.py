#!/usr/bin/env python3
"""THE COLUMNS — one real call per claim, bar declared before any generation.

Same shape as the audits that admitted and refused the surfaces before it: PixelLab's
integration audit (PR #143) and the tiles-pro audit (PR #145, RULED *parts supplier, not
instrument*). A new instrument earns its way in by audit with the bar declared first, and the
bar for THIS audit is in AUDIT-RD.md, written before the first call.

    COLUMN 1  exact-canvas behaviour at 32x32     which styles accept it; what comes back
    COLUMN 2  reference / palette support         mechanism, limits, sizes
    COLUMN 3  seed determinism                    ASSUME NONE, CONFIRM
    COLUMN 4  latency and cost per call           measured on every call in the ledger
    COLUMN 5  estimated vs actual                 free dry run against the billed figure
    COLUMN 6  the balance ledger                  which field moves, and does it settle
    COLUMN 7  the seamless flag                   existence and semantics
    COLUMN 8  bypass_prompt_expansion             live, or a silent billed no-op

DIVISION OF SPEND. Columns 1, 6, 7 and the discovery half of 2 and 8 are answerable with FREE
calls — `check_cost: true` prices and VALIDATES a payload without generating, so every question
of the form "will this surface accept this?" costs nothing. They are in `--free`. Only claims
that need a real image are in `--paid`.

    A free call that answers a column is not a lesser measurement. It is the same measurement
    without the invoice, and refusing to spend where spending buys nothing is the discipline
    the ceiling exists to serve.

REFUSALS. Touches nothing in `tools/tier1_floors/` or `tools/pixellab/probe_6_4/`. Promotes
nothing. Buys nothing. Never exceeds the ceiling in `rd.py`.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audit_out")
PROMPTS = os.path.join(HERE, "prompts")

# The canvas the whole tier-one floor family is authored at (bible §4.3 as to value).
TARGET = 32

# Sizes swept in column 1. 32 is the question; the others bracket it so a refusal message can be
# read as a boundary rather than as a mystery.
SIZE_SWEEP = [16, 24, 32, 48, 64, 96, 128]


def spec():
    return json.load(open(os.path.join(PROMPTS, "floor_material_rd.json")))


def base_payload(s, style, w=TARGET, h=TARGET):
    p = dict(s["parameters"])
    p["prompt"] = s["prompt"]
    p["prompt_style"] = style
    p["width"], p["height"] = w, h
    return p


# --- column 0: what styles exist at all -------------------------------------

def column_styles(led):
    """FREE. The live style list, recorded verbatim.

    RD_CONVENTIONS.md's style ruling is retired Oryx-track material and its IDs may no longer
    exist. The audit resolves the list rather than trusting the retired file.
    """
    t0 = time.time()
    row = {"claim": "rd_audit:col0:styles", "kind": "styles_selector"}
    try:
        r = rd.requests.get(rd.BASE + "/styles/selector", headers=rd._headers(), timeout=60)
        rd._check(r, {})
        j = r.json()
        row.update(verdict="OK", response=j, seconds=round(time.time() - t0, 2))
    except rd.Refusal as e:
        row.update(verdict="REFUSED:" + e.classification, http_status=e.status,
                   reason=e.reason[:2000])
    except Exception as e:
        row.update(verdict="ERROR:" + type(e).__name__, reason=str(e)[:2000])
    led.write(row)
    return row


# --- column 1: exact canvas at 32x32 ----------------------------------------

def column_canvas(led, styles):
    """FREE. For every style, ask `check_cost` for every size in the sweep.

    `check_cost` validates the payload, so a size the style will not accept comes back as a
    refusal with the server's own boundary message — the exact fact column 1 wants — at zero
    cost. What it CANNOT tell us is what actually comes back at an accepted size; that is the
    paid half, `column_canvas_paid`, and it is one call.
    """
    s = spec()
    grid = {}
    for style in styles:
        grid[style] = {}
        for size in SIZE_SWEEP:
            p = base_payload(s, style, size, size)
            claim = "rd_audit:col1:%s:%dx%d" % (style, size, size)
            try:
                est, j = rd.check_cost(p, led, claim=claim)
                grid[style][size] = {"accepted": True, "estimated_cost": est}
            except rd.Refusal as e:
                grid[style][size] = {"accepted": False, "http": e.status,
                                     "classification": e.classification,
                                     "reason": e.reason[:300]}
            except Exception as e:
                grid[style][size] = {"accepted": None, "error": str(e)[:200]}
            print("  %-34s %3d  %s" % (style, size, grid[style][size].get(
                "accepted", "?")))
    led.write({"claim": "rd_audit:col1:grid", "kind": "canvas_grid", "verdict": "INFO",
               "target": TARGET, "grid": grid})
    return grid


def column_canvas_paid(led, budget, style):
    """PAID, 1 generation. Does an accepted 32x32 request actually RETURN 32x32, at native
    pixel scale, with no upscale? A style that accepts the size and returns 128 downscaled is
    not a 32px surface, and only a real image can say."""
    s = spec()
    p = base_payload(s, style, TARGET, TARGET)
    p["seed"] = 133700
    imgs, row = rd.generate(p, led, "col1_native_%s" % style.replace("/", "_"), budget,
                            image_subdir="col1", claim="rd_audit:col1:native",
                            extra={"column": 1, "style": style})
    if imgs:
        print("  returned %s  (requested %dx%d)" % (imgs[0].size, TARGET, TARGET))
    return row


# --- column 2: reference / palette support ----------------------------------

def column_reference(led, budget, style, pro_style=None):
    """Mechanism, limits, sizes.

    FREE half: does this style accept `input_palette`? `reference_images`? At what count and at
    what source size? `check_cost` validates, so every limit is discoverable without spending.
    PAID half: one generation with a palette attached, to confirm the lock is real rather than
    accepted-and-ignored (§4.1 — a parameter that validates is not a parameter that works).
    """
    from PIL import Image
    s = spec()
    findings = {}

    # A neutral 8-colour grey ramp, built here rather than reusing the retired Oryx palette:
    # §5.1's values are PLACEHOLDER, and locking to a closed track's palette would be working
    # to a retired bar. This measures the MECHANISM, which is what §5.1 will need.
    ramp = Image.new("RGB", (8, 1))
    ramp.putdata([(v, v, v + 4) for v in (18, 34, 52, 74, 96, 122, 150, 182)])
    pal_b64 = rd.enc(ramp)

    probes = [
        ("input_palette_8", {"input_palette": pal_b64}),
        ("remove_bg", {"remove_bg": True}),
        ("tile_xy", {"tile_x": True, "tile_y": True}),
        ("tile_x_only", {"tile_x": True}),
        ("seed", {"seed": 4242}),
        ("bypass_prompt_expansion_off", {"bypass_prompt_expansion": False}),
        ("upscale_2", {"upscale_output_factor": 2}),
    ]
    if pro_style:
        probes.append(("reference_images_1", {"reference_images": [pal_b64]}))
        probes.append(("reference_images_10", {"reference_images": [pal_b64] * 10}))

    for name, extra in probes:
        style_here = pro_style if name.startswith("reference_images") else style
        p = base_payload(s, style_here)
        p.update(extra)
        try:
            est, _ = rd.check_cost(p, led, claim="rd_audit:col2:%s" % name)
            findings[name] = {"accepted": True, "estimated_cost": est, "style": style_here}
        except rd.Refusal as e:
            findings[name] = {"accepted": False, "http": e.status,
                              "classification": e.classification, "reason": e.reason[:300],
                              "style": style_here}
        except Exception as e:
            findings[name] = {"accepted": None, "error": str(e)[:200]}
        print("  %-30s %s" % (name, findings[name].get("accepted", "?")))

    led.write({"claim": "rd_audit:col2:probes", "kind": "capability_probes", "verdict": "INFO",
               "findings": findings})

    if budget is not None and findings.get("input_palette_8", {}).get("accepted"):
        p = base_payload(s, style)
        p["input_palette"] = pal_b64
        p["seed"] = 133701
        imgs, row = rd.generate(p, led, "col2_palette", budget, image_subdir="col2",
                                claim="rd_audit:col2:palette_real",
                                extra={"column": 2, "palette_colours": 8})
        if imgs:
            cols = sorted({px[:3] for px in imgs[0].convert("RGB").getdata()})
            row_extra = {"distinct_colours_out": len(cols),
                         "palette_respected": len(cols) <= 8}
            led.write({"claim": "rd_audit:col2:palette_measured", "verdict": "INFO",
                       "kind": "palette_measure", **row_extra})
            print("  palette lock: %d distinct colours out of an 8-colour palette -> %s"
                  % (len(cols), "RESPECTED" if len(cols) <= 8 else "NOT RESPECTED"))
            findings["palette_measured"] = row_extra
    return findings


# --- column 3: seed determinism ---------------------------------------------

def column_seed(led, budget, style, n=2):
    """PAID, `n` generations. ASSUME NONE, CONFIRM.

    Two identical payloads, identical seed. Byte-compare the returned PNGs. This is the column
    where RD could genuinely differ from the neighbouring platform: bible §13.7 records
    'nothing on this platform is seed-reproducible', measured, and RD DOCUMENTS a reproducible
    seed. If it holds, a ledger on this surface could store parameters rather than images.

    Two calls is the minimum that can DISPROVE reproducibility and cannot prove it in general.
    That asymmetry is stated in the report rather than papered over: a match here is evidence,
    not a guarantee, and the ledger keeps storing images either way.
    """
    s = spec()
    shas = []
    for i in range(n):
        p = base_payload(s, style)
        p["seed"] = 999001
        imgs, row = rd.generate(p, led, "col3_seed999001_%d" % i, budget, image_subdir="col3",
                                claim="rd_audit:col3:seed", extra={"column": 3, "repeat": i})
        if row.get("image_sha256"):
            shas.append(row["image_sha256"][0])
        print("  repeat %d  sha %s" % (i, (shas[-1][:16] if shas else "NONE")))
    verdict = ("REPRODUCIBLE" if len(shas) == n and len(set(shas)) == 1
               else "NOT_REPRODUCIBLE" if len(shas) == n else "INCONCLUSIVE")
    led.write({"claim": "rd_audit:col3:verdict", "kind": "seed_determinism", "verdict": verdict,
               "seed": 999001, "shas": shas, "distinct": len(set(shas)), "calls": n})
    print("  COLUMN 3: %s (%d distinct of %d)" % (verdict, len(set(shas)), len(shas)))
    return verdict, shas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--free", action="store_true", help="zero-cost columns only")
    ap.add_argument("--paid", action="store_true", help="the columns that need a real image")
    ap.add_argument("--style", help="prompt_style for the paid columns (resolved live if unset)")
    ap.add_argument("--pro-style", help="an RD Pro style id, for reference_images probes")
    ap.add_argument("--ceiling", type=int, default=8, help="paid generations this run may spend")
    a = ap.parse_args()
    if not (a.free or a.paid):
        a.free = True

    rd.preflight()
    os.makedirs(OUT, exist_ok=True)
    led = rd.Ledger(OUT, "audit_ledger.jsonl")

    if a.free:
        print("\n== COLUMN 0 — the live style list (FREE) ==")
        srow = column_styles(led)
        styles = []
        if srow.get("verdict") == "OK":
            blob = json.dumps(srow["response"])
            styles = sorted(set(json.loads(blob).get("styles", []))) if isinstance(
                srow["response"].get("styles"), list) else []
            print(json.dumps(srow["response"], indent=1)[:3000])
        if a.style:
            styles = [a.style]
        if not styles:
            print("  (no style list parsed — pass --style to sweep a named style)")
        else:
            print("\n== COLUMN 1 — exact canvas sweep (FREE, check_cost validates) ==")
            column_canvas(led, styles[:6])

        if a.style:
            print("\n== COLUMN 2 — capability probes (FREE half) ==")
            column_reference(led, None, a.style, a.pro_style)

    if a.paid:
        if not a.style:
            raise SystemExit("--paid needs --style (resolve it from the --free run first)")
        budget = rd.Budget(ceiling=a.ceiling)
        sess = rd.Session(OUT, "rd_audit", budget=budget,
                          declaration={"columns": [1, 2, 3, 4, 5, 6, 8], "style": a.style,
                                       "target_canvas": TARGET}).open()
        print("\n== COLUMN 1 — one native 32x32 generation (PAID) ==")
        sess.note_billed(column_canvas_paid(led, budget, a.style))
        print("\n== COLUMN 2 — palette lock, measured (PAID) ==")
        column_reference(led, budget, a.style, a.pro_style)
        print("\n== COLUMN 3 — seed determinism (PAID x2) ==")
        column_seed(led, budget, a.style)
        sess.close()

    print("\n-> %s" % os.path.relpath(led.path, rd.REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
