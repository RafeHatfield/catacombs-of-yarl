#!/usr/bin/env python3
"""Retro Diffusion v1 REST client for the 2026-08 adoption audit.

SURFACE, AND WHAT IS DELIBERATELY NOT ON IT
-------------------------------------------
API/website surface ONLY: `https://api.retrodiffusion.ai/v1`, header `X-RD-Token`.

The **Aseprite extension is a different product with different models** and is out of scope
for this audit by the session brief. Nothing here buys, installs, or calls it. The MCP server
at `mcp.retrodiffusion.ai` is also not used: it is a second surface with its own tool shapes,
and an audit that cannot say which surface produced a number has measured nothing.

WHY NOT REUSE `../batch_generate.py`
------------------------------------
`tools/retrodiffusion/` is NOT the empty stub the brief assumed. It is a **complete legacy
integration from the RETIRED Oryx-conformance track** (see `../NOTICE.md`): it hard-codes the
Oryx palette, the Oryx custom style id, and Oryx sprite-id namespaces, has no cost dry-run, no
balance bracket, no ledger, no budget ceiling, and gates spending on `input()`. Its every
threshold answers to a corpus that is no longer the target. It is read as evidence about the
surface and is not extended.

THE LEDGER STORES IMAGES, NOT PARAMETERS
----------------------------------------
Bible §13.7: *"Nothing on this platform is seed-reproducible — measured on every surface
tried."* RD **documents** a `seed` parameter and claims reproducibility; that claim is one of
this audit's columns and is UNPROVEN until column 3 measures it. Until then the same law
applies as on BitForge: every generation — accepted, refused, or control — is written to disk
beside a ledger row carrying its full redacted payload. An image is not re-derivable from
(prompt, seed) unless and until a measurement says it is.

THREE GUARDS, EACH OF WHICH MUST BE ABLE TO GO RED
--------------------------------------------------
LOOP-PROCESS §4 / bible §13.5: no instrument's pass counts until it has demonstrated it can
fail. `controls.py` plants a defect against each of these and records the verbatim failure.

  1. `preflight()`      — no key, or a key of the wrong shape, stops the run cold.
  2. `Budget`           — a hard ceiling in code, not a docstring. It refuses call N+1.
  3. `estimate_vs_actual` — a divergence between the free `check_cost` dry run and the billed
                            `balance_cost` is recorded as a FINDING, not smoothed over.

And per LOOP-PROCESS §4.2 (*any step asserting an invariant must be able to go red when it is
not*): the balance bracket is not decoration. `Session.close()` compares the pool delta against
the sum of billed costs and reds on disagreement — the cheap "compare numbers you already have"
check, not a new instrument.

THE KEY IS NEVER PRINTED
------------------------
It is read from the environment, never committed, never logged, never echoed into the ledger,
and never included in a report. `_scrub()` walks every row before it is written and replaces any
occurrence of the credential with `<redacted>` — belt and braces against a server error message
that quotes the token back.
"""
import argparse
import base64
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import time

import requests
from PIL import Image

BASE = "https://api.retrodiffusion.ai/v1"
INFERENCES = "/inferences"
CREDITS = "/inferences/credits"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

# The credential's environment variable. Documented in README.md. `RD_API_KEY` is the name the
# retired track's own conventions file established and the name the legacy scripts already read;
# keeping it means one name for one secret rather than a second one to leak.
TOKEN_VAR = "RD_API_KEY"
KEY_PREFIX = "rdpk-"          # documented by the vendor; shape-checked, never printed

# --- the hard ceiling --------------------------------------------------------
# Session brief: 40 paid generations. This is the number, in code, once. A script that wants a
# smaller ceiling passes one; nothing may pass a larger one.
SESSION_CEILING = 40


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    """A hard ceiling on PAID generations. Free calls (`check_cost`, credits reads) do not
    count against it and must not — the whole point of a free dry run is that it is free.

    Counts IMAGES, not requests: `num_images: 4` is four generations and is billed as four.
    """

    def __init__(self, ceiling=SESSION_CEILING, spent=0):
        if ceiling > SESSION_CEILING:
            raise BudgetExceeded(
                "REFUSING: ceiling %d exceeds the session ceiling %d declared in the brief."
                % (ceiling, SESSION_CEILING))
        self.ceiling = ceiling
        self.spent = spent

    def remaining(self):
        return self.ceiling - self.spent

    def reserve(self, n):
        if self.spent + n > self.ceiling:
            raise BudgetExceeded(
                "REFUSING: %d generation(s) would take this session to %d of a hard ceiling of "
                "%d. Nothing was called and nothing was billed."
                % (n, self.spent + n, self.ceiling))
        self.spent += n
        return self.spent


# --- credential --------------------------------------------------------------

def token():
    val = os.environ.get(TOKEN_VAR)
    if not val:
        raise SystemExit(
            "STOP — no Retro Diffusion credential.\n"
            "  Set %s in the environment before running anything in this directory.\n"
            "  The key is never committed, never printed, and never written to the ledger.\n"
            "  See tools/retrodiffusion/audit_2026_08/README.md." % TOKEN_VAR)
    return val


def preflight(require_prefix=True):
    """Fails loudly and EARLY. Called before any script does work, so a missing key costs a
    second rather than half a batch. Prints the key's shape, never the key."""
    val = token()
    shape = "len=%d prefix_ok=%s" % (len(val), val.startswith(KEY_PREFIX))
    if require_prefix and not val.startswith(KEY_PREFIX):
        raise SystemExit(
            "STOP — %s is set but is not a Retro Diffusion key (%s).\n"
            "  Vendor keys begin %r. Refusing to send a credential to an endpoint it does not\n"
            "  belong to." % (TOKEN_VAR, shape, KEY_PREFIX))
    return shape


def _headers():
    return {"X-RD-Token": token(), "Content-Type": "application/json"}


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


# --- refusal capture ---------------------------------------------------------
# A refusal's reason is unrecoverable after the fact: raise_for_status() reports the status line
# and drops r.text, where the server's actual reason lives. Same discipline as v2_bitforge._check.

class Refusal(RuntimeError):
    def __init__(self, status, classification, reason, payload):
        self.status = status
        self.classification = classification
        self.reason = reason
        self.payload = payload
        super().__init__("HTTP %s [%s] %s" % (status, classification, reason[:400]))


def _classify(status, body):
    b = (body or "").lower()
    # RD documents 400 as "invalid input OR insufficient balance" — one status, two very
    # different facts. Split them on the body, because "we ran out of money" and "the payload is
    # wrong" must never land in the same ledger bucket.
    if "insufficient" in b or (status == 400 and "balance" in b):
        return "insufficient_balance"
    if status in (401,):
        return "auth"
    if status in (403,):
        return "forbidden"
    if status == 404:
        return "not_found"
    if status == 422:
        return "validation"
    if status == 429:
        return "rate_limit"
    if status == 400:
        return "invalid_input"
    if status >= 500:
        return "server_error"
    return "unknown"


def _check(r, payload):
    if r.status_code == 200:
        return
    try:
        body = r.text
    except Exception:
        body = "<body unreadable>"
    raise Refusal(r.status_code, _classify(r.status_code, body), body, payload)


# --- payload hygiene ---------------------------------------------------------

def enc(img):
    """PIL -> bare base64 PNG. RD takes a bare string with NO `data:` prefix (vendor docs)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def enc_file(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


_IMAGE_FIELDS = ("input_image", "input_palette", "mask_image")


def _digest_b64(s):
    raw = base64.b64decode(s)
    out = {"_ref": "sha256:" + hashlib.sha256(raw).hexdigest(), "_bytes": len(raw)}
    try:
        out["_size"] = list(Image.open(io.BytesIO(raw)).size)
    except Exception:
        pass
    return out


def _redact(payload):
    """Ledger-safe copy: image fields become a digest + size, never megabytes of base64.
    The digest is what makes a reference auditable — LOOP-PROCESS §2.3, evidence carries its
    producer's hash."""
    p = copy.deepcopy(payload)
    for f in _IMAGE_FIELDS:
        v = p.get(f)
        if isinstance(v, str) and v:
            p[f] = _digest_b64(v)
    refs = p.get("reference_images")
    if isinstance(refs, list):
        p["reference_images"] = [_digest_b64(v) if isinstance(v, str) else v for v in refs]
    return p


def _scrub(obj):
    """Replace the credential anywhere it appears in a row before it is written. The payload
    does not carry it — it lives in a header — but a server error body can quote it back, and a
    ledger is a file that gets committed."""
    secret = os.environ.get(TOKEN_VAR)
    if not secret:
        return obj
    if isinstance(obj, str):
        return obj.replace(secret, "<redacted>")
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    return obj


# --- balance -----------------------------------------------------------------

def credits():
    """GET /v1/inferences/credits -> the WHOLE object. Recorded whole rather than as one number:
    the same lesson as PixelLab AUDIT 8.1, where dollar credits and a subscription pool arrived
    together and reading one of them was reading the wrong one."""
    r = requests.get(BASE + CREDITS, headers=_headers(), timeout=60)
    _check(r, {})
    return r.json()


def _pool(obj):
    """The spendable figure. RD documents `{"credits": n, "balance": n}`; which of the two moves
    when a generation is billed is COLUMN 6 of the audit and is not assumed here. Both are
    recorded; this returns the one the audit measured as moving, defaulting to `credits`."""
    for k in ("credits", "balance"):
        try:
            return float(obj[k])
        except (KeyError, TypeError, ValueError):
            continue
    return None


def settled_credits(reads=3, interval=6, tries=8):
    """Require `reads` consecutive identical values before believing one.

    Carried across from PixelLab AUDIT 8.5, where the balance ledger settled LATE and SLOWLY and
    two reads 15s apart agreed on a figure that was 32% low — a cost taken from an unsettled
    bracket is a LOWER BOUND, not a measurement. Whether RD settles immediately is COLUMN 6; the
    discipline is applied until measured otherwise, and `stable=False` in a ledger row is the
    honest record that it never settled.
    """
    seen = []
    for _ in range(tries):
        seen.append(_pool(credits()))
        if len(seen) >= reads and len(set(seen[-reads:])) == 1 and seen[-1] is not None:
            return seen[-1], True
        time.sleep(interval)
    return (seen[-1] if seen else None), False


# --- ledger ------------------------------------------------------------------

class Ledger:
    """One flushed row per call, plus the image on disk. Flushed and fsynced per row because a
    crash mid-batch must not lose the record of calls that were already billed."""

    def __init__(self, out_dir, name="ledger.jsonl"):
        self.dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.path = os.path.join(out_dir, name)
        self.commit = git_commit()

    def write(self, row):
        row = dict(row)
        row.setdefault("commit", self.commit)
        row.setdefault("surface", "rd-v1-rest" + INFERENCES)
        row.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        row = _scrub(row)
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return row


# --- the calls ---------------------------------------------------------------

def check_cost(payload, ledger=None, claim=""):
    """The FREE dry run. `check_cost: true` prices the exact payload and generates nothing.

    Run before EVERY paid call, per the session brief. Returns (estimated_cost, raw_response).
    A dry run that itself fails is a finding and is ledgered as one — it means the payload is
    invalid, which is worth knowing for free rather than for $0.18.
    """
    p = dict(payload)
    p["check_cost"] = True
    t0 = time.time()
    row = {"claim": claim, "kind": "check_cost", "request": _redact(p)}
    try:
        r = requests.post(BASE + INFERENCES, headers=_headers(), json=p, timeout=120)
        _check(r, p)
        j = r.json()
        est = j.get("balance_cost", j.get("credit_cost"))
        row.update(verdict="OK", estimated_cost=est, response=j,
                   seconds=round(time.time() - t0, 2))
        if ledger:
            ledger.write(row)
        return est, j
    except Refusal as e:
        row.update(verdict="REFUSED:" + e.classification, http_status=e.status,
                   reason=e.reason[:2000], seconds=round(time.time() - t0, 2))
        if ledger:
            ledger.write(row)
        raise
    except Exception as e:
        row.update(verdict="ERROR:" + type(e).__name__, reason=str(e)[:2000],
                   seconds=round(time.time() - t0, 2))
        if ledger:
            ledger.write(row)
        raise


def generate(payload, ledger, image_stem, budget, image_subdir="images", claim="", extra=None,
             dry_first=True):
    """One PAID RD generation, bracketed and dry-run first.

    Order of operations, and each step is load-bearing:
      1. budget.reserve(n)   — refuse BEFORE the network, so an over-budget call is never billed
      2. check_cost          — free, prices this exact payload
      3. POST                — the paid call
      4. ledger row          — estimated vs actual, both recorded, divergence flagged

    Returns (list of PIL images, ledger row). A refusal is ledgered exactly as loudly as a
    success: it is a measured fact about the surface, and it is the reason `r.text` is captured
    before anything raises.
    """
    n = int(payload.get("num_images", 1))
    budget.reserve(n)                       # raises BudgetExceeded before a byte goes out

    est = None
    est_err = None
    if dry_first:
        try:
            est, _ = check_cost(payload, ledger, claim=claim + ":dryrun")
        except Exception as e:              # a failed dry run is recorded, not fatal by itself
            est_err = "%s: %s" % (type(e).__name__, str(e)[:400])

    t0 = time.time()
    imgs = []
    row = {"claim": claim, "kind": "generate", "images": [], "request": _redact(payload),
           "estimated_cost": est, "estimate_error": est_err,
           "budget_spent": budget.spent, "budget_ceiling": budget.ceiling}
    if extra:
        row.update(extra)
    try:
        r = requests.post(BASE + INFERENCES, headers=_headers(), json=payload, timeout=600)
        _check(r, payload)
        j = r.json()
        actual = j.get("balance_cost", j.get("credit_cost"))
        d = os.path.join(ledger.dir, image_subdir)
        os.makedirs(d, exist_ok=True)
        rels, shas = [], []
        for i, b64 in enumerate(j.get("base64_images", [])):
            if b64.lstrip().startswith("data:") and "," in b64[:64]:
                b64 = b64.split(",", 1)[1]
            raw = base64.b64decode(b64)
            im = Image.open(io.BytesIO(raw)).convert("RGBA")
            rel = os.path.join(image_subdir, "%s_%d.png" % (image_stem, i))
            im.save(os.path.join(ledger.dir, rel))
            imgs.append(im)
            rels.append(rel)
            shas.append(hashlib.sha256(raw).hexdigest())
        row.update(verdict="OK", images=rels, image_sha256=shas,
                   out_size=[list(im.size) for im in imgs],
                   actual_cost=actual, model=j.get("model"),
                   remaining_balance=j.get("remaining_balance"),
                   returned_images=len(rels), requested_images=n,
                   seconds=round(time.time() - t0, 2))
        # COLUMN 5. A divergence is a finding, recorded per call rather than reconciled later.
        if est is not None and actual is not None:
            row["estimate_divergence"] = round(float(actual) - float(est), 6)
            row["estimate_matched"] = abs(float(actual) - float(est)) < 1e-9
        # §4.2's shape: an invariant that can go red. Asking for 4 and being billed for 4 while
        # 3 come back is a silent partial success, which is the failure this clause exists for.
        if len(rels) != n:
            row["INVARIANT_RED"] = "requested %d images, received %d" % (n, len(rels))
    except Refusal as e:
        row.update(verdict="REFUSED:" + e.classification, http_status=e.status,
                   reason=e.reason[:2000], seconds=round(time.time() - t0, 2))
    except Exception as e:
        row.update(verdict="ERROR:" + type(e).__name__, reason=str(e)[:2000],
                   seconds=round(time.time() - t0, 2))
    return imgs, ledger.write(row)


# --- the session bracket -----------------------------------------------------

class Session:
    """Brackets the balance around a run and RECONCILES it at the end.

    LOOP-PROCESS §4.2: *any step asserting an invariant must be able to go red when it is not.*
    "The balance was bracketed" is such an assertion. The gauntlet's unbracketed-balance defect
    does not get a third life, and a bracket that is only printed is not a bracket — this one
    compares the measured pool delta against the sum of billed costs and writes RECONCILED or
    RECONCILE_RED into the ledger.
    """

    def __init__(self, out_dir, claim, budget=None, declaration=None, settle=True):
        self.led = Ledger(out_dir)
        self.claim = claim
        self.budget = budget or Budget()
        self.settle = settle
        self.before = self.stable_before = None
        self.declaration = declaration or {}
        self.billed = 0.0

    def open(self):
        preflight()
        if self.settle:
            self.before, self.stable_before = settled_credits()
        else:
            self.before, self.stable_before = _pool(credits()), False
        self.led.write(dict({"claim": self.claim + ":declaration", "verdict": "INFO",
                             "kind": "declaration",
                             "credits_before": self.before, "settled": self.stable_before,
                             "budget_ceiling": self.budget.ceiling,
                             "session_ceiling": SESSION_CEILING},
                            **self.declaration))
        print("credits before: %s (settled=%s)  ceiling=%d"
              % (self.before, self.stable_before, self.budget.ceiling))
        return self

    def note_billed(self, row):
        c = row.get("actual_cost")
        if isinstance(c, (int, float)):
            self.billed += float(c)

    def close(self):
        after, stable = (settled_credits() if self.settle
                         else (_pool(credits()), False))
        row = {"claim": self.claim + ":close", "verdict": "INFO", "kind": "close",
               "credits_before": self.before, "credits_after": after, "settled_after": stable,
               "generations_spent": self.budget.spent, "billed_sum": round(self.billed, 6)}
        if self.before is not None and after is not None:
            delta = round(self.before - after, 6)
            row["credits_delta"] = delta
            row["reconciled"] = abs(delta - round(self.billed, 6)) < 1e-6
            if not row["reconciled"]:
                row["verdict"] = "RECONCILE_RED"
                row["INVARIANT_RED"] = (
                    "pool moved %s but calls billed %s — the bracket and the per-call costs "
                    "disagree" % (delta, round(self.billed, 6)))
        else:
            row["verdict"] = "RECONCILE_RED"
            row["INVARIANT_RED"] = "balance unreadable at one or both ends of the bracket"
        self.led.write(row)
        print("credits after:  %s (settled=%s)   spent=%d gen   billed=%s   %s"
              % (after, stable, self.budget.spent, round(self.billed, 6), row["verdict"]))
        return row


def main():
    ap = argparse.ArgumentParser(description="RD client self-check. Spends nothing.")
    ap.add_argument("--preflight", action="store_true", help="key presence and shape only")
    ap.add_argument("--credits", action="store_true", help="one free credits read")
    a = ap.parse_args()
    if a.preflight or not (a.credits):
        print("preflight: %s  (%s)" % (preflight(), TOKEN_VAR))
    if a.credits:
        print(json.dumps(credits(), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
