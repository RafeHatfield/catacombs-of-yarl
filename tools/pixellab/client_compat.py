"""Thin PixelLab API wrapper that bypasses a response-schema bug in pixellab==1.0.5:
the installed SDK's Usage model hardcodes `type: Literal["usd"]`, but this account's
subscription billing now returns `{"type": "generations", "generations": N}`, which
raises a pydantic ValidationError before the image can be read out of the response.
Reuses the SDK's Client for auth/base_url; does the HTTP call and response parsing
directly instead of going through the SDK's broken response model.

⚠ LEGACY SURFACE. This module talks to the PixelLab **v1** REST API. v1 is 8 endpoints;
v2 is 92, and the two BitForge request schemas are byte-identical (see
docs/PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md §3). New work should target v2 / the
hosted MCP server, not this file. It is kept alive, and instrumented, for the existing
tools/pixellab/ scripts only.
"""
import base64
import os
import time
from io import BytesIO

import pixellab
import requests
from PIL import Image

# --- credentials -------------------------------------------------------------
# Historically split: this module read PIXELLAB_API_TOKEN while seven sibling scripts
# and both setup docs read PIXELLAB_API_KEY, so a shell configured exactly as our own
# docs instruct cleared bank_generate's guard and died here with a KeyError. Accept
# either, name both in the error.
_TOKEN_VARS = ("PIXELLAB_API_TOKEN", "PIXELLAB_API_KEY")


def api_token():
    for var in _TOKEN_VARS:
        val = os.environ.get(var)
        if val:
            return val
    raise RuntimeError(
        "No PixelLab credential in the environment. Set one of: "
        + ", ".join(_TOKEN_VARS)
    )


def _client():
    return pixellab.Client(secret=api_token())


def _decode(resp_json):
    img_b64 = resp_json["image"]["base64"]
    return Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")


# --- refusal capture ---------------------------------------------------------
# requests' raise_for_status() reports only "400 Client Error: Bad Request for url: ..."
# and drops r.text, where the server's actual reason lives. A refusal's reason is
# unrecoverable after the fact (PIXELLAB-VERIFIED.md §1.7) — capture it at the moment
# the call fails or lose it permanently.

class PixelLabRefusal(RuntimeError):
    """A server-side rejection, with its reason preserved and classified."""

    def __init__(self, status, classification, reason, endpoint):
        self.status = status
        self.classification = classification
        self.reason = reason
        self.endpoint = endpoint
        super().__init__(f"[{classification}] HTTP {status} on {endpoint}: {reason}")


def _classify(status, body):
    """Best-effort classification. The bucket names match Gemfall's so the two games'
    ledgers can be read side by side. Unknown is a real answer — do not guess."""
    low = (body or "").lower()
    if "content policy" in low or "content_policy" in low or "blocked" in low:
        return "content_policy"
    # [API 2026-08-25] The real over-length body is a FastAPI/pydantic validation error:
    #   {"detail":[{"type":"string_too_long","loc":["body","description"],
    #               "msg":"String should have at most 2000 characters", ...}]}
    # served as HTTP 422. An earlier version of this classifier matched "too long" with a
    # space and returned invalid_input for the one shape that actually occurs — found by
    # probing, not by reading. Match the measured strings.
    if ("too_long" in low or "too long" in low or "at most" in low
            or "maxlength" in low or "max_length" in low or "exceeds" in low):
        return "over_length"
    if "too_short" in low or "at least" in low:
        return "under_length"
    if status == 429 or "rate limit" in low:
        return "rate_limit"
    if status in (401, 403):
        return "auth"
    if status == 402 or "balance" in low or "insufficient" in low:
        return "insufficient_balance"
    if 400 <= status < 500:
        return "invalid_input"
    if status >= 500:
        return "server_error"
    return "unknown"


def _check(r, endpoint):
    if r.status_code < 400:
        return
    body = ""
    try:
        body = r.text or ""
    except Exception:  # pragma: no cover - body already consumed/undecodable
        body = "<unreadable response body>"
    raise PixelLabRefusal(r.status_code, _classify(r.status_code, body), body.strip()[:2000], endpoint)


# --- balance -----------------------------------------------------------------

def get_balance():
    client = _client()
    r = requests.get(f"{client.base_url}/balance", headers=client.headers())
    _check(r, "/balance")
    return r.json()


class balance_bracket:
    """Context manager that reads /balance before and after a batch and records both.

    The subscription is SHARED with Gemfall, so get_balance is the only ground truth
    for what a run actually cost, and a reading taken only at the end cannot be
    differenced. Billing also runs in two regimes (pool-metered and dollar-metered) —
    which one a batch ran under is not recoverable later, so it is captured here.

        with balance_bracket("bank:prop_variety") as b:
            ...generate...
        print(b.summary())

    A balance read that itself fails must not abort a batch: `before`/`after` are set
    to None and `summary()` says so, rather than pretending the spend was zero.
    """

    def __init__(self, label, log_path=None):
        self.label = label
        self.log_path = log_path
        self.before = None
        self.after = None

    # [API 2026-08-25] MEASURED: the balance ledger SETTLES LATE, and slowly.
    #   - six /inpaint calls: 4660 -> 4655 read immediately, -> 4654 seconds later.
    #   - one /create-character-v3: 4634 -> 4592 read after completion, -> 4572 a minute later.
    # An immediate post-batch read UNDERCOUNTS, and a two-read agreement 15s apart was ALSO
    # wrong (it agreed on 4592, which was not the final figure). So: require STABLE_READS
    # consecutive identical readings, and keep the total window long. A spend figure that is
    # quietly 30% low is worse than an honest "unmeasured".
    #
    # ⚠ Consequence for any prior cost claim on this platform, ours or Gemfall's: a cost
    # derived from a short bracket is a LOWER BOUND, not a measurement.
    SETTLE_TRIES = 20
    SETTLE_DELAY = 10.0
    STABLE_READS = 3

    @staticmethod
    def _safe_read():
        try:
            return get_balance()
        except Exception as e:
            print(f"  WARN: balance read failed ({e}) — spend for this batch is unmeasured")
            return None

    @classmethod
    def _settled_read(cls):
        """Read until STABLE_READS consecutive reads agree, or we run out of tries."""
        prev = cls._safe_read()
        if prev is None:
            return None
        agreed = 1
        for _ in range(cls.SETTLE_TRIES):
            time.sleep(cls.SETTLE_DELAY)
            cur = cls._safe_read()
            if cur is None:
                return prev
            agreed = agreed + 1 if cur == prev else 1
            prev = cur
            if agreed >= cls.STABLE_READS:
                return cur
        print("  WARN: balance never settled — the delta below is a LOWER BOUND, not a measurement")
        return prev

    def __enter__(self):
        self.before = self._safe_read()
        print(f"[balance] {self.label} before: {self.before}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.after = self._settled_read()
        print(f"[balance] {self.label} after:  {self.after}")
        if self.log_path:
            try:
                with open(self.log_path, "a") as f:
                    f.write(self.summary() + "\n")
            except Exception as e:  # pragma: no cover
                print(f"  WARN: could not write balance log: {e}")
        return False  # never suppress

    def summary(self):
        if self.before is None or self.after is None:
            return f"{self.label}\tbefore={self.before}\tafter={self.after}\tdelta=UNMEASURED"
        return f"{self.label}\tbefore={self.before}\tafter={self.after}"


# --- generation --------------------------------------------------------------

def generate_image_bitforge(description, image_size, seed=0, no_background=True, color_image=None, **kwargs):
    """color_image: optional PIL Image. Per the live OpenAPI spec (api.pixellab.ai/v1/openapi.json,
    re-checked 2026-08-25), this is a genuine forced-color-palette parameter — "image containing colors
    used for palette" — not spatial color transfer. Verified empirically: a small (~8-10 color) flat
    swatch of solid blocks produces output using only those exact colors. Feed it a flat swatch, not
    a large detailed/multi-object composite (see tools/pixellab/palette_lock_evidence/).
    """
    client = _client()
    request_data = {
        "description": description,
        "image_size": image_size,
        "negative_description": kwargs.pop("negative_description", ""),
        "text_guidance_scale": kwargs.pop("text_guidance_scale", 3.0),
        "extra_guidance_scale": kwargs.pop("extra_guidance_scale", 3.0),
        "style_strength": kwargs.pop("style_strength", 0.0),
        "no_background": no_background,
        "seed": seed,
        **kwargs,
    }
    if color_image is not None:
        request_data["color_image"] = pixellab.models.Base64Image.from_pil_image(color_image).model_dump()
    r = requests.post(f"{client.base_url}/generate-image-bitforge",
                       headers=client.headers(), json=request_data)
    _check(r, "/generate-image-bitforge")
    return _decode(r.json())


def inpaint(description, image_size, inpainting_image, mask_image, seed=0, no_background=True, **kwargs):
    client = _client()
    request_data = {
        "description": description,
        "image_size": image_size,
        "inpainting_image": pixellab.models.Base64Image.from_pil_image(inpainting_image).model_dump(),
        "mask_image": pixellab.models.Base64Image.from_pil_image(mask_image).model_dump(),
        "negative_description": kwargs.pop("negative_description", ""),
        "text_guidance_scale": kwargs.pop("text_guidance_scale", 3.0),
        "extra_guidance_scale": kwargs.pop("extra_guidance_scale", 3.0),
        "no_background": no_background,
        "seed": seed,
        **kwargs,
    }
    r = requests.post(f"{client.base_url}/inpaint",
                       headers=client.headers(), json=request_data)
    _check(r, "/inpaint")
    return _decode(r.json())
