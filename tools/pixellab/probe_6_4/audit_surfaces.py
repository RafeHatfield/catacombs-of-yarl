#!/usr/bin/env python3
"""§6.4 probe — SURFACE AUDIT. Which surface can actually run Stage 2, and does the
treatment lever survive conditioning?

Answers two columns the integration freeze depends on:

  1. STYLE-REFERENCE CONDITIONING — which of {MCP pixflux, MCP pixen/pro, v1 REST}
     accepts style/reference images, at what canvas, with what limits.
  2. LEVER UNDER CONDITIONING — where references ARE accepted, is the shading/treatment
     control still honoured alongside them, or does conditioning override it?

Plus: is pixflux's 32x32 refusal a hard floor or a default?

EVERY ROW IS A REAL CALL. Nothing here is read from a doc or inferred from a schema —
schemas are recorded alongside, but the verdict column is always what the server did.
Ledger is JSONL, flushed per row (PIXELLAB-UW-AUDIT §12: one flush-per-row), so a crash
mid-audit loses nothing. Refusal bodies are captured BEFORE any raise (§6).

NOT a probe arm. Generates no candidate and promotes nothing. Outputs are audit evidence.
"""
import base64
import io as _io
import json
import os
import sys
import time

import requests
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import client_compat as cc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audit_evidence")
LEDGER = os.path.join(OUT, "ledger.jsonl")
MCP_URL = "https://api.pixellab.ai/mcp"


# --------------------------------------------------------------------------- ledger
def ledger(row):
    os.makedirs(OUT, exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())
    status = row.get("verdict", "?")
    print("  [%-8s] %-26s %s" % (status, row.get("claim", ""), row.get("detail", "")[:90]))


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".png")
    img.save(p)
    return p


def pixdiff(a, b):
    """Fraction of pixels differing. The lever test: same seed, one knob moved."""
    a, b = a.convert("RGB"), b.convert("RGB")
    if a.size != b.size:
        return 1.0
    n = sum(1 for p, q in zip(a.getdata(), b.getdata()) if p != q)
    return n / float(a.width * a.height)


def b64png(img):
    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------- MCP
class Mcp:
    """Minimal MCP JSON-RPC client. Streamable-HTTP: replies arrive as SSE `data:` lines."""

    def __init__(self, token):
        self.s = requests.Session()
        self.h = {
            "Authorization": "Bearer %s" % token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self._id = 0
        self.call("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "yarl-probe-6.4-audit", "version": "0"}})
        self.s.post(MCP_URL, headers=self.h,
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"}, timeout=30)

    def call(self, method, params=None):
        self._id += 1
        body = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            body["params"] = params
        r = self.s.post(MCP_URL, headers=self.h, json=body, timeout=600)
        sid = r.headers.get("mcp-session-id")
        if sid:
            self.h["mcp-session-id"] = sid
        # capture the raw body before anything can raise on it
        raw = r.text
        for ln in raw.splitlines():
            if ln.startswith("data: "):
                return json.loads(ln[6:])
        return {"_raw": raw[:2000], "_status": r.status_code}

    def tool(self, name, args):
        """Returns (ok, text, image_or_None, raw_result)."""
        res = self.call("tools/call", {"name": name, "arguments": args})
        r = res.get("result", {})
        text, img = "", None
        for c in r.get("content", []):
            if c.get("type") == "text":
                text += c["text"]
            elif c.get("type") == "image":
                img = Image.open(_io.BytesIO(base64.b64decode(c["data"])))
        return (not r.get("isError", False)), text, img, r

    def generate(self, tool, args, poll_timeout=300):
        """Create -> poll get_image. Returns (ok, detail, image_or_None)."""
        ok, text, img, _ = self.tool(tool, args)
        if not ok:
            return False, text.strip().replace("\n", " | "), None
        if img is not None:
            return True, "inline image", img
        job = None
        for ln in text.splitlines():
            if ln.strip().startswith("id:"):
                job = ln.split(":", 1)[1].strip()
                break
        if not job:
            return False, "no job id and no inline image: " + text[:200], None
        t0 = time.time()
        while time.time() - t0 < poll_timeout:
            ok2, t2, img2, _ = self.tool("get_image", {"job_id": job})
            if img2 is not None:
                return True, "job %s in %.0fs" % (job[:8], time.time() - t0), img2
            if not ok2 and "error" in t2.lower() and "pending" not in t2.lower() \
                    and "progress" not in t2.lower():
                return False, t2.strip().replace("\n", " | "), None
            time.sleep(4)
        return False, "poll timeout after %ds (job %s)" % (poll_timeout, job[:8]), None


# --------------------------------------------------------------------------- v1
def v1(desc, w, h, **kw):
    """v1 REST BitForge. Returns (ok, detail, image_or_None). Captures refusal text."""
    try:
        img = cc.generate_image_bitforge(
            description=desc, image_size={"width": w, "height": h},
            seed=kw.pop("seed", 1337), no_background=kw.pop("no_background", False), **kw)
        return True, "%dx%d" % img.size, img
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, str(e)[:300]), None


# --------------------------------------------------------------------------- main
DESC_FLOOR = "a worn grey stone cobble floor tile"


def main():
    os.makedirs(OUT, exist_ok=True)
    open(LEDGER, "w").close()
    token = cc.api_token()
    m = Mcp(token)

    ok, bal_txt, _, _ = m.tool("get_balance", {})
    bal_before = bal_txt.strip().replace("\n", " | ")
    ledger({"claim": "balance:before", "verdict": "INFO", "detail": bal_before})

    # ---- reference images, authored by us. No external corpus pixels, ever. -----
    ok, d, ref24 = v1(DESC_FLOOR, 24, 24, seed=4242, shading="basic shading",
                      outline="lineless", view="high top-down")
    ledger({"claim": "ref:make 24x24", "verdict": "PASS" if ok else "FAIL", "detail": d})
    if not ok:
        sys.exit("cannot author the 24x24 reference; audit aborted")
    save(ref24, "ref_24")
    ok, d, ref32 = v1(DESC_FLOOR, 32, 32, seed=4242, shading="basic shading",
                      outline="lineless", view="high top-down")
    ledger({"claim": "ref:make 32x32", "verdict": "PASS" if ok else "FAIL", "detail": d})
    save(ref32, "ref_32")

    # =========================================================================
    # FLOOR — is pixflux's 32x32 refusal a hard floor or a default?
    # The refusal names an AREA ("576px, minimum is 32x32 = 1024px"), while the
    # schema declares width/height minimum 16. Those disagree; only calls settle it.
    # =========================================================================
    print("\n== FLOOR: pixflux ==")
    for w, h, tag in ((24, 24, "24x24_576px"), (32, 32, "32x32_1024px"),
                      (16, 64, "16x64_1024px"), (16, 16, "16x16_256px")):
        ok, d, img = m.generate("create_image_pixflux",
                                {"description": DESC_FLOOR, "width": w, "height": h,
                                 "seed": 1337, "no_background": False})
        if img:
            save(img, "floor_pixflux_%s" % tag)
        ledger({"claim": "floor:pixflux %s" % tag, "verdict": "ACCEPTED" if ok else "REFUSED",
                "detail": d, "area": w * h})

    # the documented bypass: omit width/height, let init_image dictate size
    ok, d, img = m.generate("create_image_pixflux",
                            {"description": DESC_FLOOR, "seed": 1337, "no_background": False,
                             "init_image_base64": b64png(ref24), "init_image_strength": 150})
    if img:
        save(img, "floor_pixflux_initimage24_nowh")
    ledger({"claim": "floor:pixflux init24 no-wh", "verdict": "ACCEPTED" if ok else "REFUSED",
            "detail": d + (" -> %s" % (img.size,) if img else "")})

    # =========================================================================
    # COLUMN 1 — STYLE/REFERENCE CONDITIONING ACCEPTANCE
    # =========================================================================
    print("\n== COLUMN 1: conditioning acceptance ==")

    # v1 REST: style_image + style_strength, matched size
    ok, d, img = v1(DESC_FLOOR, 24, 24, seed=99, style_image=ref24, style_strength=50.0,
                    shading="basic shading", outline="lineless")
    if img:
        save(img, "c1_v1_style24_gen24")
    ledger({"claim": "cond:v1 style24@24", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    # v1 REST: does the style image have to match generation size exactly?
    ok, d, img = v1(DESC_FLOOR, 24, 24, seed=99, style_image=ref32, style_strength=50.0,
                    shading="basic shading", outline="lineless")
    if img:
        save(img, "c1_v1_style32_gen24")
    ledger({"claim": "cond:v1 style32@24", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    # MCP pro: style_image at the declared canvas
    ok, d, img = m.generate("create_image_pro",
                            {"description": DESC_FLOOR, "width": 24, "height": 24, "seed": 99,
                             "style_image_base64": b64png(ref24)})
    if img:
        save(img, "c1_pro_style24_gen24")
    ledger({"claim": "cond:pro style24@24", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    # MCP pro: labelled reference_images
    ok, d, img = m.generate("create_image_pro",
                            {"description": DESC_FLOOR, "width": 24, "height": 24, "seed": 99,
                             "reference_images": json.dumps(
                                 [{"base64": b64png(ref24), "label": "stone floor reference"}])})
    if img:
        save(img, "c1_pro_refimages_gen24")
    ledger({"claim": "cond:pro refimages@24", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    # MCP pixen: schema exposes NO conditioning field. Confirm by call.
    ok, d, img = m.generate("create_image_pixen",
                            {"description": DESC_FLOOR, "width": 24, "height": 24, "seed": 99,
                             "style_image_base64": b64png(ref24)})
    ledger({"claim": "cond:pixen style24@24", "verdict": "ACCEPTED" if ok else "REFUSED",
            "detail": d, "note": "pixen schema declares no style/reference field"})

    # MCP pixflux: conditioning is init_image (img2img), not style transfer
    ok, d, img = m.generate("create_image_pixflux",
                            {"description": DESC_FLOOR, "width": 32, "height": 32, "seed": 99,
                             "init_image_base64": b64png(ref32), "init_image_strength": 150,
                             "no_background": False})
    if img:
        save(img, "c1_pixflux_init32_gen32")
    ledger({"claim": "cond:pixflux init32@32", "verdict": "ACCEPTED" if ok else "REFUSED", "detail": d})

    print("\n== balance after ==")
    ok, bal_txt, _, _ = m.tool("get_balance", {})
    ledger({"claim": "balance:after-col1", "verdict": "INFO",
            "detail": bal_txt.strip().replace("\n", " | ")})
    print("\nledger: %s" % LEDGER)


if __name__ == "__main__":
    main()
