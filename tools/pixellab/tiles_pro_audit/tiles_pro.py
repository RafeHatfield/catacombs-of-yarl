#!/usr/bin/env python3
"""The /create-tiles-pro surface for this audit: create, poll, download, ledger.

Built on the §6.4 probe's `v2_bitforge` discipline rather than on `client_compat` (v1, LEGACY
banner), and kept separate from it because the endpoint differs in three ways that a shared
module would paper over:

  * **Async.** `/create-tiles-pro` returns 202 with a `tile_id`; the tiles arrive later from
    `GET /tiles-pro/{id}`. **HTTP 423 on that GET means "still generating", not "refused"**
    (PIXELLAB-INTEGRATION-AUDIT §8.6). Any classifier that buckets 4xx as error files every
    in-progress poll as a rejection.
  * **Many images per call.** The response carries `storage_urls` — one URL per tile — not a
    single inline base64 image.
  * **A different style wire shape.** `TilesProStyleImage` is `{base64, width, height}` with
    no `type` and no `format`. It is NOT `Base64Image`, which is what every other endpoint on
    this platform takes. Carrying the neighbour's shape here is the enum mistake in a new
    costume (§8.9).

THE LEDGER STORES IMAGES, WITH PAYLOADS. Inherited from the §6.4 probe and not relaxed: every
tile of every call is written to disk beside a row carrying the full request. This endpoint is
documented deterministic under `seed`, but a documented property is not a measured one and the
ledger does not get to depend on the thing the audit is testing.

BALANCE IS BRACKETED. The wall gauntlet's one un-closable defect was a script that never
bracketed its own balance, leaving 320 generations unattributable after the fact. Every paid
entry point here opens and closes a settled bracket.
"""
import base64
import copy
import hashlib
import io
import json
import os
import subprocess
import time

import requests
from PIL import Image

V2_BASE = "https://api.pixellab.ai/v2"
CREATE = "/create-tiles-pro"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

_TOKEN_VARS = ("PIXELLAB_API_TOKEN", "PIXELLAB_API_KEY")


def api_token():
    for var in _TOKEN_VARS:
        val = os.environ.get(var)
        if val:
            return val
    raise RuntimeError("No PixelLab credential. Set one of: " + ", ".join(_TOKEN_VARS))


def _headers():
    return {"Authorization": "Bearer " + api_token(), "Content-Type": "application/json"}


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


# --- refusal capture ---------------------------------------------------------

class Refusal(RuntimeError):
    def __init__(self, status, classification, reason, payload):
        self.status = status
        self.classification = classification
        self.reason = reason
        self.payload = payload
        super().__init__("HTTP %s [%s] %s" % (status, classification, reason[:400]))


def classify(status, body):
    b = (body or "").lower()
    if status == 423:
        return "in_progress"          # §8.6 — a retry signal, never an error
    if status in (401, 403):
        return "auth"
    if status == 402 or "insufficient" in b:
        return "insufficient_balance"
    if status == 429:
        return "rate_limit"
    if "string_too_long" in b or "at most" in b:
        return "over_length"
    if "content" in b and "policy" in b:
        return "content_policy"
    if status in (400, 422):
        return "invalid_input"
    if status >= 500:
        return "server_error"
    return "unknown"


def _check(r, payload):
    if r.status_code in (200, 202):
        return
    body = ""
    try:
        body = r.text
    except Exception:
        body = "<body unreadable>"
    raise Refusal(r.status_code, classify(r.status_code, body), body, payload)


def style_image(img):
    """PIL -> TilesProStyleImage. Note the shape: width/height are REQUIRED and there is no
    `type`/`format` field. This is not Base64Image; see the module docstring."""
    img = img.convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {"base64": base64.b64encode(buf.getvalue()).decode("ascii"),
            "width": img.width, "height": img.height}


def _redact(payload):
    """Ledger-safe copy: style images become a digest + size, never megabytes of base64."""
    p = copy.deepcopy(payload)
    imgs = p.get("style_images")
    if isinstance(imgs, list):
        out = []
        for v in imgs:
            if isinstance(v, dict) and v.get("base64"):
                raw = base64.b64decode(v["base64"])
                out.append({"_ref": "sha256:" + hashlib.sha256(raw).hexdigest(),
                            "_size": [v.get("width"), v.get("height")], "_bytes": len(raw)})
            else:
                out.append(v)
        p["style_images"] = out
    return p


# --- balance -----------------------------------------------------------------

def balance():
    r = requests.get(V2_BASE + "/balance", headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def pool(bal):
    try:
        return float(bal["subscription"]["generations"])
    except (KeyError, TypeError, ValueError):
        return None


def settled_pool(reads=3, interval=10, tries=10):
    """§8.5: the balance ledger settles late and slowly — two reads 15 s apart once agreed on a
    figure that was 32% low. Require `reads` consecutive identical values before believing one.
    Returns (value, settled?) and the caller must print LOWER BOUND when settled is False."""
    seen = []
    for _ in range(tries):
        v = pool(balance())
        seen.append(v)
        if len(seen) >= reads and len(set(seen[-reads:])) == 1 and seen[-1] is not None:
            return seen[-1], True
        time.sleep(interval)
    return (seen[-1] if seen else None), False


class Bracket:
    """Open and close a settled balance bracket around a batch, and write both ends to the
    ledger. The gauntlet's defect was not having this; it is not optional here."""

    def __init__(self, ledger, label):
        self.ledger = ledger
        self.label = label
        self.before = None
        self.before_settled = None

    def __enter__(self):
        self.before, self.before_settled = settled_pool()
        self.ledger.write({"claim": "balance:open:" + self.label, "verdict": "BRACKET",
                           "pool": self.before, "settled": self.before_settled})
        print("[bracket] %s open: pool=%s settled=%s" %
              (self.label, self.before, self.before_settled))
        return self

    def __exit__(self, *exc):
        after, settled = settled_pool()
        delta = None
        if self.before is not None and after is not None:
            delta = self.before - after
        self.ledger.write({"claim": "balance:close:" + self.label, "verdict": "BRACKET",
                           "pool": after, "settled": settled, "pool_before": self.before,
                           "delta": delta,
                           "note": None if (settled and self.before_settled)
                                   else "LOWER BOUND, not a measurement"})
        print("[bracket] %s close: pool=%s settled=%s delta=%s%s" %
              (self.label, after, settled, delta,
               "" if (settled and self.before_settled) else "  <-- LOWER BOUND"))
        return False


# --- ledger ------------------------------------------------------------------

class Ledger:
    def __init__(self, out_dir, name="ledger.jsonl"):
        self.dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.path = os.path.join(out_dir, name)
        self.commit = git_commit()

    def write(self, row):
        row = dict(row)
        row.setdefault("commit", self.commit)
        row.setdefault("surface", "v2-http" + CREATE)
        row.setdefault("ts", time.strftime("%H:%M:%S"))
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return row


# --- the call ----------------------------------------------------------------

def create(payload, ledger, claim="", extra=None):
    """POST /create-tiles-pro. Returns (tile_id, row). Ledgers before anything can go wrong
    with the download, because the call is billed at 202 and a crash afterwards must not lose
    the record of a charge."""
    t0 = time.time()
    row = {"claim": claim, "request": _redact(payload), "phase": "create"}
    if extra:
        row.update(extra)
    tile_id = None
    try:
        r = requests.post(V2_BASE + CREATE, headers=_headers(), json=payload, timeout=600)
        _check(r, payload)
        j = r.json()
        tile_id = j.get("tile_id")
        row.update(verdict="ACCEPTED", http_status=r.status_code, tile_id=tile_id,
                   background_job_id=j.get("background_job_id"), usage=j.get("usage"),
                   seconds=round(time.time() - t0, 1))
    except Refusal as e:
        row.update(verdict="REFUSED:" + e.classification, http_status=e.status,
                   reason=e.reason[:3000], seconds=round(time.time() - t0, 1))
    except Exception as e:
        row.update(verdict="ERROR:" + type(e).__name__, reason=str(e)[:2000],
                   seconds=round(time.time() - t0, 1))
    ledger.write(row)
    return tile_id, row


def fetch(tile_id, ledger, out_subdir, claim="", poll_interval=10, max_wait=900):
    """Poll GET /tiles-pro/{id} until it stops returning 423, then download every tile.

    Returns (dict index->PIL, meta row). Poll latency is recorded: it is the honest per-call
    latency for this endpoint and one of the audit's columns.
    """
    t0 = time.time()
    polls = 0
    url = V2_BASE + "/tiles-pro/" + tile_id
    j = None
    while time.time() - t0 < max_wait:
        r = requests.get(url, headers=_headers(), timeout=120)
        polls += 1
        if r.status_code == 423:
            time.sleep(poll_interval)
            continue
        if r.status_code == 200:
            j = r.json()
            break
        ledger.write({"claim": claim, "phase": "poll", "tile_id": tile_id,
                      "verdict": "REFUSED:" + classify(r.status_code, r.text),
                      "http_status": r.status_code, "reason": r.text[:2000], "polls": polls})
        return {}, None
    if j is None:
        ledger.write({"claim": claim, "phase": "poll", "tile_id": tile_id,
                      "verdict": "ERROR:timeout", "polls": polls,
                      "seconds": round(time.time() - t0, 1)})
        return {}, None

    wait_s = round(time.time() - t0, 1)
    d = os.path.join(ledger.dir, out_subdir)
    os.makedirs(d, exist_ok=True)
    urls = j.get("storage_urls") or {}
    tiles = {}
    shas = {}
    for key in sorted(urls, key=lambda k: int(k.split("_")[-1])):
        idx = int(key.split("_")[-1])
        raw = requests.get(urls[key], timeout=120).content
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        img.save(os.path.join(d, "tile_%02d.png" % idx))
        tiles[idx] = img
        shas[idx] = hashlib.sha256(img.tobytes()).hexdigest()

    meta = {"claim": claim, "phase": "fetch", "tile_id": tile_id, "verdict": "OK",
            "kind": j.get("kind"), "n_tiles": len(tiles), "polls": polls,
            "wait_seconds": wait_s, "usage": j.get("usage"),
            "out_subdir": out_subdir,
            "sizes": sorted({tuple(t.size) for t in tiles.values()}),
            "pixel_sha256": shas}
    with open(os.path.join(d, "tile_rules.json"), "w") as f:
        json.dump(j.get("tile_rules"), f, indent=2, sort_keys=True)
    with open(os.path.join(d, "response_meta.json"), "w") as f:
        json.dump({k: v for k, v in j.items() if k != "storage_urls"}, f,
                  indent=2, sort_keys=True)
    ledger.write(meta)
    return tiles, meta


def run_kit(payload, ledger, subdir, claim="", extra=None):
    """One full paid kit: create + fetch. Returns (tiles, create_row, fetch_meta)."""
    tile_id, crow = create(payload, ledger, claim=claim, extra=extra)
    if not tile_id:
        return {}, crow, None
    tiles, meta = fetch(tile_id, ledger, subdir, claim=claim)
    return tiles, crow, meta


# --- the diff instrument -----------------------------------------------------

def pixdiff(a, b):
    """Fraction of pixels differing. Answers exactly one mechanical question — did the
    parameter do anything at all — and is not an aesthetic judgement (bible §13.4)."""
    a, b = a.convert("RGBA"), b.convert("RGBA")
    if a.size != b.size:
        return 1.0
    n = sum(1 for p, q in zip(a.getdata(), b.getdata()) if p != q)
    return n / float(a.width * a.height)


def kitdiff(k1, k2):
    """Mean per-tile pixdiff across two kits, plus the count of tiles that moved at all."""
    keys = sorted(set(k1) & set(k2))
    if not keys:
        return None, 0, 0
    fr = [pixdiff(k1[i], k2[i]) for i in keys]
    return sum(fr) / len(fr), sum(1 for f in fr if f > 0), len(keys)
