#!/usr/bin/env python3
"""§6.4 probe — SURFACE AUDIT part 2: v1 conditioning, and COLUMN 2 (the lever).

Column 2's question: on a surface that accepts style/reference images, is the
shading/treatment control STILL HONOURED alongside them, or does conditioning override it?

The test is a controlled pair. Same seed, same reference, same prompt; the ONLY thing
moved is the treatment knob. If the two outputs differ, the lever survives conditioning.
If they are byte-identical, conditioning has taken the wheel.

A pixel-diff is not an aesthetic judgement and is not scoring art (§13.4) — it answers
exactly one mechanical question: did the parameter do anything at all.

v1 note: client_compat.generate_image_bitforge encodes `color_image` but passes
`style_image` through raw kwargs, where it dies as an unserialisable PIL object. The
raw SDK encodes it, but the SDK is the path client_compat exists to route around. So
this file encodes Base64Image by hand and keeps using the wrapper.
"""
import json
import os
import sys

import pixellab
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import client_compat as cc  # noqa: E402
from audit_surfaces import Mcp, b64png, ledger, pixdiff, save, OUT, v1  # noqa: E402

DESC = "a worn grey stone cobble floor tile"


def enc(img):
    """PIL -> the wire shape v1 expects for image-valued fields."""
    return pixellab.models.Base64Image.from_pil_image(img).model_dump()


def v1_styled(w, h, style, strength, **kw):
    return v1(DESC, w, h, style_image=enc(style), style_strength=strength, **kw)


def main():
    ref24 = Image.open(os.path.join(OUT, "ref_24.png"))
    ref32 = Image.open(os.path.join(OUT, "ref_32.png"))
    m = Mcp(cc.api_token())

    # ================= COLUMN 1, v1 rows (re-run with correct encoding) =========
    print("\n== COLUMN 1: v1 REST conditioning ==")

    ok, d, img = v1_styled(24, 24, ref24, 50.0, seed=99,
                           shading="basic shading", outline="lineless")
    if img:
        save(img, "c1_v1_style24_gen24")
    ledger({"claim": "cond:v1 style24@24", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    # does the style image have to match the generation size exactly?
    ok, d, img = v1_styled(24, 24, ref32, 50.0, seed=99,
                           shading="basic shading", outline="lineless")
    if img:
        save(img, "c1_v1_style32_gen24")
    ledger({"claim": "cond:v1 style32@24 (mismatch)", "verdict": "ACCEPTED" if ok else "REFUSED",
            "detail": d})

    # style_strength defaults to 0.0 in the wrapper — does a reference at 0 do anything?
    ok, d, a = v1_styled(24, 24, ref24, 0.0, seed=1234, shading="basic shading", outline="lineless")
    ok2, d2, b = v1_styled(24, 24, ref24, 100.0, seed=1234, shading="basic shading",
                           outline="lineless")
    if a:
        save(a, "c1_v1_strength0")
    if b:
        save(b, "c1_v1_strength100")
    frac = pixdiff(a, b) if (a and b) else None
    ledger({"claim": "cond:v1 strength 0 vs 100", "verdict": "INFO",
            "detail": "pixdiff=%.4f" % frac if frac is not None else "%s / %s" % (d, d2),
            "pixdiff": frac})

    # ================= COLUMN 2 — the lever under conditioning ==================
    print("\n== COLUMN 2: is the treatment lever honoured under conditioning? ==")

    # --- v1: style_image held constant, shading moved -------------------------
    ok, d, flat = v1_styled(24, 24, ref24, 50.0, seed=777,
                            shading="flat shading", outline="lineless")
    ok2, d2, det = v1_styled(24, 24, ref24, 50.0, seed=777,
                             shading="detailed shading", outline="lineless")
    if flat:
        save(flat, "c2_v1_styled_flat")
    if det:
        save(det, "c2_v1_styled_detailed")
    frac = pixdiff(flat, det) if (flat and det) else None
    ledger({"claim": "lever:v1 shading under style",
            "verdict": "HONOURED" if (frac or 0) > 0.02 else ("OVERRIDDEN" if frac is not None else "FAIL"),
            "detail": "pixdiff=%.4f (flat vs detailed, style_strength=50, seed fixed)" % frac
                      if frac is not None else "%s / %s" % (d, d2),
            "pixdiff": frac})

    # control: same knob WITHOUT conditioning, so a null result above is readable
    ok, d, flat0 = v1(DESC, 24, 24, seed=777, shading="flat shading", outline="lineless")
    ok2, d2, det0 = v1(DESC, 24, 24, seed=777, shading="detailed shading", outline="lineless")
    frac0 = pixdiff(flat0, det0) if (flat0 and det0) else None
    ledger({"claim": "lever:v1 shading UNconditioned (control)",
            "verdict": "HONOURED" if (frac0 or 0) > 0.02 else "OVERRIDDEN",
            "detail": "pixdiff=%.4f" % frac0 if frac0 is not None else "%s / %s" % (d, d2),
            "pixdiff": frac0})

    # --- pro: style_copy is the only treatment control it has -----------------
    # "Which aspects to take from style_image: any of color_palette, outline, detail,
    # shading. Defaults to all." So the test is whether EXCLUDING shading changes output.
    args = {"description": DESC, "width": 24, "height": 24, "seed": 777,
            "style_image_base64": b64png(ref24)}
    ok, d, with_sh = m.generate("create_image_pro",
                                dict(args, style_copy=["color_palette", "outline", "detail",
                                                       "shading"]))
    ok2, d2, no_sh = m.generate("create_image_pro",
                                dict(args, style_copy=["color_palette", "outline", "detail"]))
    if with_sh:
        save(with_sh, "c2_pro_stylecopy_with_shading")
    if no_sh:
        save(no_sh, "c2_pro_stylecopy_no_shading")
    frac = pixdiff(with_sh, no_sh) if (with_sh and no_sh) else None
    ledger({"claim": "lever:pro style_copy shading on/off",
            "verdict": "HONOURED" if (frac or 0) > 0.02 else ("OVERRIDDEN" if frac is not None else "FAIL"),
            "detail": "pixdiff=%.4f" % frac if frac is not None else "%s / %s" % (d, d2),
            "pixdiff": frac})

    # --- pixflux: init_image held constant, shading moved (32x32, its floor) ---
    a2 = {"description": DESC, "width": 32, "height": 32, "seed": 777, "no_background": False,
          "init_image_base64": b64png(ref32), "init_image_strength": 150}
    ok, d, pf_flat = m.generate("create_image_pixflux", dict(a2, shading="flat shading"))
    ok2, d2, pf_det = m.generate("create_image_pixflux", dict(a2, shading="detailed shading"))
    if pf_flat:
        save(pf_flat, "c2_pixflux_init_flat")
    if pf_det:
        save(pf_det, "c2_pixflux_init_detailed")
    frac = pixdiff(pf_flat, pf_det) if (pf_flat and pf_det) else None
    ledger({"claim": "lever:pixflux shading under init_image",
            "verdict": "HONOURED" if (frac or 0) > 0.02 else ("OVERRIDDEN" if frac is not None else "FAIL"),
            "detail": "pixdiff=%.4f" % frac if frac is not None else "%s / %s" % (d, d2),
            "pixdiff": frac})

    ok, bal, _, _ = m.tool("get_balance", {})
    ledger({"claim": "balance:after-col2", "verdict": "INFO",
            "detail": bal.strip().replace("\n", " | ")})


if __name__ == "__main__":
    main()
