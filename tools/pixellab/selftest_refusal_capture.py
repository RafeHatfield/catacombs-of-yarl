#!/usr/bin/env python3
"""Self-test for the refusal-capture instrument in client_compat.

Makes NO network call and costs nothing. Run:  python3 tools/pixellab/selftest_refusal_capture.py

WHY THIS EXISTS. Two rules meet here:

  - ART-LOOP-PROCESS-v0.md §4 / ART-BIBLE-v0.md §13.5 — *no instrument's pass counts
    until it has demonstrated it can fail.* A refusal-capture path that has only ever
    been exercised on successful calls has proven nothing.
  - PIXELLAB-VERIFIED.md §1.7 — a refusal's reason is unrecoverable after the fact.
    If this instrument is silently broken we do not find out until we have already
    lost the reason we needed.

So this asserts BOTH directions: that a 2xx passes through untouched, and that each
error shape actually raises with the server's verbatim body preserved and correctly
classified. A regression that made _check() swallow errors would turn this red.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import client_compat as cc  # noqa: E402


class FakeResponse:
    """Minimal stand-in for requests.Response — no network, no auth, no cost."""

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class UnreadableResponse(FakeResponse):
    @property
    def text(self):
        raise ValueError("body already consumed")

    @text.setter
    def text(self, v):
        pass


FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} {detail}")
        FAILURES.append(label)


def main():
    print("=== 1. the instrument passes clean responses through ===")
    for status in (200, 201, 204, 399):
        try:
            cc._check(FakeResponse(status, "{}"), "/fake")
            check(f"HTTP {status} does not raise", True)
        except Exception as e:
            check(f"HTTP {status} does not raise", False, f"raised {e!r}")

    print("\n=== 2. the instrument CAN FAIL — every error shape raises ===")
    # The 422 case below is the VERBATIM body the live API returned on 2026-08-25 when
    # /create-1-direction-object was sent a 2001-character description. It is here because
    # the first version of _classify() got it WRONG — it matched "too long" with a space
    # and filed the one over-length shape that actually occurs as invalid_input. Regression
    # guard: this is the real string, not a plausible one.
    REAL_422 = ('{"detail":[{"type":"string_too_long","loc":["body","description"],'
                '"msg":"String should have at most 2000 characters","input":"a wooden barrel ..."}]}')
    cases = [
        (422, REAL_422, "over_length"),
        (400, "Generation blocked by content policy", "content_policy"),
        (400, "description too long, exceeds maxLength 2000", "over_length"),
        (400, "no idea what happened", "invalid_input"),
        (401, "invalid token", "auth"),
        (402, "insufficient balance for this generation", "insufficient_balance"),
        (429, "rate limit exceeded", "rate_limit"),
        (503, "upstream unavailable", "server_error"),
    ]
    for status, body, expected in cases:
        try:
            cc._check(FakeResponse(status, body), "/fake-endpoint")
            check(f"HTTP {status} raises", False, "no exception raised — INSTRUMENT IS BLIND")
        except cc.PixelLabRefusal as e:
            ok = (
                e.status == status
                and e.classification == expected
                and body in e.reason           # verbatim server body preserved
                and e.endpoint == "/fake-endpoint"
            )
            check(
                f"HTTP {status} -> {expected}, reason preserved",
                ok,
                f"got status={e.status} class={e.classification} reason={e.reason!r}",
            )
        except Exception as e:
            check(f"HTTP {status} raises PixelLabRefusal", False, f"raised {type(e).__name__} instead")

    print("\n=== 3. an unreadable body still raises, and says so ===")
    try:
        cc._check(UnreadableResponse(400, ""), "/fake")
        check("unreadable body still raises", False, "no exception — INSTRUMENT IS BLIND")
    except cc.PixelLabRefusal as e:
        check("unreadable body still raises with a marker", "unreadable" in e.reason, f"reason={e.reason!r}")

    print("\n=== 4. the credential lookup accepts either env var name ===")
    saved = {k: os.environ.pop(k, None) for k in cc._TOKEN_VARS}
    try:
        try:
            cc.api_token()
            check("no credential raises", False, "returned a token from an empty environment")
        except RuntimeError:
            check("no credential raises RuntimeError", True)
        for var in cc._TOKEN_VARS:
            os.environ[var] = f"sentinel-{var}"
            got = cc.api_token()
            check(f"{var} alone is accepted", got == f"sentinel-{var}", f"got {got!r}")
            del os.environ[var]
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v

    print()
    if FAILURES:
        print(f"SELFTEST FAILED — {len(FAILURES)} check(s) red: {', '.join(FAILURES)}")
        return 1
    print("SELFTEST GREEN — and it has demonstrated it can go red (see §2/§3 assertions).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
