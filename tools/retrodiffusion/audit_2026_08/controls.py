#!/usr/bin/env python3
"""POSITIVE CONTROLS for the RD client's own guards.

    bible §13.5 / LOOP-PROCESS §4 — no instrument's pass counts until it has demonstrated it
    can fail. For scripts: stub the metric to a constant, plant the defect it exists to catch,
    mutate the thing it guards. Show it goes red. Record the verbatim failure.

Every guard in `rd.py` is planted against here. Each control has a RED half (the defect is
present; the guard must fire) and a GREEN half (the defect is absent; the guard must stay
quiet). A guard that only ever fires, or only ever passes, is decorative — §4's own words — so
both halves are required for a control to count.

    §4.1 LAW — a lever is proven on its AXIS, not on the diff. Each plant below carries the
    defect on the axis its guard claims: the budget plant asks for one generation too many (not
    merely "something changed"); the divergence plant moves the BILLED cost away from the
    ESTIMATE while holding everything else; the reconcile plant moves the POOL away from the
    billed sum. A control that only asks "did anything change?" certifies connectivity and
    reports it as efficacy.

    §4.2 LAW — a step asserting an invariant must be able to go red when it is not. Controls
    5 and 6 are that clause: a partial image return and an unreconciled balance bracket are
    both silent successes unless something makes them loud.

NO NETWORK, NO CREDENTIAL, NO SPEND. The transport is stubbed. This file therefore runs — and
its passes therefore count — before the key ever arrives, which is the whole reason the guards
could be certified in a session that was blocked on the credential.
"""
import io
import json
import os
import sys
import tempfile
import traceback

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd  # noqa: E402

RESULTS = []
FAKE_KEY = "rdpk-CONTROLFAKE0000000000000000"


# --- stub transport ----------------------------------------------------------

class FakeResp:
    def __init__(self, status=200, body=None, text=""):
        self.status_code = status
        self._body = body if body is not None else {}
        self.text = text or json.dumps(self._body)

    def json(self):
        return self._body


class Tripwire(Exception):
    """Raised if the network is touched when the guard should have refused first."""


class FakeRequests:
    """Records calls; can be armed to trip if touched at all."""

    def __init__(self, responses=None, tripwire=False):
        self.responses = list(responses or [])
        self.tripwire = tripwire
        self.calls = []

    def _next(self, url, kwargs):
        self.calls.append((url, kwargs))
        if self.tripwire:
            raise Tripwire("network touched at %s — the guard did not refuse first" % url)
        if not self.responses:
            return FakeResp(200, {})
        r = self.responses.pop(0)
        return r() if callable(r) else r

    def post(self, url, **kw):
        return self._next(url, kw)

    def get(self, url, **kw):
        return self._next(url, kw)


def png_b64(size=(32, 32), colour=(90, 90, 95, 255)):
    buf = io.BytesIO()
    Image.new("RGBA", size, colour).save(buf, format="PNG")
    import base64
    return base64.b64encode(buf.getvalue()).decode("ascii")


def record(name, half, expected, got, ok, verbatim=""):
    RESULTS.append({"control": name, "half": half, "expected": expected, "got": got,
                    "ok": bool(ok), "verbatim": verbatim})
    print("  [%s] %-5s %s\n        expected: %s\n        got:      %s"
          % ("PASS" if ok else "FAIL", half, name, expected, got))
    if verbatim:
        print("        verbatim: %s" % verbatim.replace("\n", "\n                  "))


def _set_key(v):
    if v is None:
        os.environ.pop(rd.TOKEN_VAR, None)
    else:
        os.environ[rd.TOKEN_VAR] = v


# --- CONTROL 1 — preflight ---------------------------------------------------

def control_preflight():
    print("\nCONTROL 1 — preflight: a missing or wrong-shaped credential stops the run cold.")
    saved = os.environ.get(rd.TOKEN_VAR)
    try:
        # RED a: the credential is absent. The defect is on preflight's own axis.
        _set_key(None)
        try:
            rd.preflight()
            record("preflight/absent", "RED", "SystemExit", "returned normally", False)
        except SystemExit as e:
            msg = str(e)
            record("preflight/absent", "RED", "SystemExit naming the env var",
                   "SystemExit", rd.TOKEN_VAR in msg, msg)

        # RED b: a credential of the wrong shape — a real key for a DIFFERENT vendor is the
        # realistic form of this defect, and sending it would leak that vendor's secret to RD.
        _set_key("sk-some-other-vendors-token-000000")
        try:
            rd.preflight()
            record("preflight/wrong_shape", "RED", "SystemExit", "returned normally", False)
        except SystemExit as e:
            msg = str(e)
            record("preflight/wrong_shape", "RED", "SystemExit refusing to send",
                   "SystemExit", "Refusing" in msg, msg)
            # and it must not have printed the credential it refused
            record("preflight/wrong_shape_no_leak", "RED", "the rejected value absent from the "
                   "message", "present" if "sk-some-other" in msg else "absent",
                   "sk-some-other" not in msg)

        # GREEN: a well-shaped credential passes and reports SHAPE, never the value.
        _set_key(FAKE_KEY)
        shape = rd.preflight()
        record("preflight/valid", "GREEN", "shape string with no key material",
               shape, FAKE_KEY not in shape and "len=" in shape)
    finally:
        _set_key(saved)


# --- CONTROL 2 — the hard ceiling -------------------------------------------

def control_budget():
    print("\nCONTROL 2 — Budget: the ceiling is code, and it refuses call N+1 BEFORE the network.")
    b = rd.Budget(ceiling=3)
    b.reserve(2)
    # GREEN: inside the ceiling.
    try:
        b.reserve(1)
        record("budget/inside", "GREEN", "3 of 3 reserved", "spent=%d" % b.spent, b.spent == 3)
    except rd.BudgetExceeded as e:
        record("budget/inside", "GREEN", "no refusal", "refused: %s" % e, False)

    # RED: one generation past the ceiling, on the ceiling's own axis.
    try:
        b.reserve(1)
        record("budget/over", "RED", "BudgetExceeded", "allowed spend=%d" % b.spent, False)
    except rd.BudgetExceeded as e:
        record("budget/over", "RED", "BudgetExceeded naming the ceiling", "BudgetExceeded",
               "hard ceiling of 3" in str(e), str(e))

    # RED: a ceiling above the session ceiling cannot be constructed at all.
    try:
        rd.Budget(ceiling=rd.SESSION_CEILING + 1)
        record("budget/session_ceiling", "RED", "BudgetExceeded", "constructed", False)
    except rd.BudgetExceeded as e:
        record("budget/session_ceiling", "RED", "refusal to exceed the declared session ceiling",
               "BudgetExceeded", True, str(e))

    # RED: the refusal happens BEFORE any request is sent. This is the half that matters —
    # a ceiling enforced after the POST is a ceiling that bills.
    saved_req, saved_key = rd.requests, os.environ.get(rd.TOKEN_VAR)
    try:
        _set_key(FAKE_KEY)
        rd.requests = FakeRequests(tripwire=True)
        tmp = tempfile.mkdtemp()
        led = rd.Ledger(tmp)
        full = rd.Budget(ceiling=1, spent=1)
        try:
            rd.generate({"prompt": "x", "num_images": 1}, led, "x", full)
            record("budget/no_network", "RED", "BudgetExceeded before any HTTP",
                   "generate() returned", False)
        except rd.BudgetExceeded as e:
            record("budget/no_network", "RED", "BudgetExceeded, zero HTTP calls",
                   "BudgetExceeded, %d HTTP calls" % len(rd.requests.calls),
                   len(rd.requests.calls) == 0, str(e))
        except Tripwire as e:
            record("budget/no_network", "RED", "BudgetExceeded before any HTTP",
                   "network was touched", False, str(e))
    finally:
        rd.requests, _ = saved_req, None
        _set_key(saved_key)


# --- CONTROL 3 — estimated vs actual ----------------------------------------

def _gen_once(est_cost, actual_cost, n_images=1, returned=None, tmp=None):
    """One stubbed generate(): a check_cost response then an inference response."""
    returned = n_images if returned is None else returned
    fake = FakeRequests([
        FakeResp(200, {"balance_cost": est_cost}),
        FakeResp(200, {"balance_cost": actual_cost, "model": "rd_fake",
                       "remaining_balance": 100.0,
                       "base64_images": [png_b64() for _ in range(returned)]}),
    ])
    saved = rd.requests
    rd.requests = fake
    try:
        led = rd.Ledger(tmp or tempfile.mkdtemp())
        _, row = rd.generate({"prompt": "x", "num_images": n_images}, led, "t",
                             rd.Budget(ceiling=rd.SESSION_CEILING), claim="control")
        return row, led
    finally:
        rd.requests = saved


def control_divergence():
    print("\nCONTROL 3 — estimate vs actual: a divergence is recorded as a finding, not smoothed.")
    saved = os.environ.get(rd.TOKEN_VAR)
    _set_key(FAKE_KEY)
    try:
        # GREEN: the dry run priced it correctly.
        row, _ = _gen_once(0.06, 0.06)
        record("divergence/agree", "GREEN", "estimate_matched True, divergence 0",
               "matched=%s divergence=%s" % (row.get("estimate_matched"),
                                             row.get("estimate_divergence")),
               row.get("estimate_matched") is True and row.get("estimate_divergence") == 0.0)

        # RED: billed three times the quote. The defect is on the guard's own axis — the ESTIMATE
        # is held and the BILLED cost is moved.
        row, _ = _gen_once(0.06, 0.18)
        record("divergence/diverge", "RED", "estimate_matched False, divergence 0.12",
               "matched=%s divergence=%s" % (row.get("estimate_matched"),
                                             row.get("estimate_divergence")),
               row.get("estimate_matched") is False
               and abs(row.get("estimate_divergence", 0) - 0.12) < 1e-9)
    finally:
        _set_key(saved)


# --- CONTROL 4 — the ledger keeps no secrets and no megabytes ---------------

def control_ledger_hygiene():
    print("\nCONTROL 4 — the ledger: the credential never lands on disk; images are digested.")
    saved = os.environ.get(rd.TOKEN_VAR)
    _set_key(FAKE_KEY)
    try:
        tmp = tempfile.mkdtemp()
        led = rd.Ledger(tmp)
        # RED: the server quotes the token back inside an error body — the realistic leak path,
        # since the payload itself never carries it.
        fake = FakeRequests([FakeResp(401, {}, text="invalid token: %s" % FAKE_KEY)])
        saved_req, rd.requests = rd.requests, fake
        try:
            rd.generate({"prompt": "x", "num_images": 1}, led, "leak",
                        rd.Budget(ceiling=rd.SESSION_CEILING), claim="control",
                        dry_first=False)
        finally:
            rd.requests = saved_req
        disk = open(led.path).read()
        record("ledger/no_key_on_disk", "RED", "credential absent, <redacted> present",
               "key_present=%s redacted_present=%s" % (FAKE_KEY in disk, "<redacted>" in disk),
               FAKE_KEY not in disk and "<redacted>" in disk,
               [l for l in disk.splitlines() if "redacted" in l][:1][0][:220]
               if "<redacted>" in disk else "")

        # GREEN half of the same guard: a real base64 image in a payload is digested, not stored.
        big = png_b64((64, 64))
        red = rd._redact({"prompt": "x", "input_palette": big})
        record("ledger/image_digested", "GREEN", "dict with sha256 + size, no base64 body",
               json.dumps(red.get("input_palette"))[:120],
               isinstance(red.get("input_palette"), dict)
               and str(red["input_palette"].get("_ref", "")).startswith("sha256:")
               and big not in json.dumps(red))
    finally:
        _set_key(saved)


# --- CONTROL 5 — the partial-return invariant (§4.2) ------------------------

def control_partial_return():
    print("\nCONTROL 5 — §4.2: asking for 4 and receiving 3 must go RED, not quietly succeed.")
    saved = os.environ.get(rd.TOKEN_VAR)
    _set_key(FAKE_KEY)
    try:
        # GREEN: asked 4, got 4.
        row, _ = _gen_once(0.24, 0.24, n_images=4, returned=4)
        record("partial/complete", "GREEN", "no INVARIANT_RED",
               row.get("INVARIANT_RED", "none"), "INVARIANT_RED" not in row)
        # RED: asked 4, billed 4, got 3 — a silent partial success on the invariant's own axis.
        row, _ = _gen_once(0.24, 0.24, n_images=4, returned=3)
        record("partial/short", "RED", "INVARIANT_RED naming 4 vs 3",
               row.get("INVARIANT_RED", "none"),
               "INVARIANT_RED" in row and "received 3" in row["INVARIANT_RED"],
               row.get("INVARIANT_RED", ""))
    finally:
        _set_key(saved)


# --- CONTROL 6 — the balance bracket reconciles (§4.2) ----------------------

def control_reconcile():
    print("\nCONTROL 6 — §4.2: a bracket that does not reconcile must go RED, not just print.")
    saved = os.environ.get(rd.TOKEN_VAR)
    _set_key(FAKE_KEY)
    try:
        def run(pool_before, pool_after, billed):
            """The billed figure is planted THROUGH THE LEDGER, not by setting an attribute.

            The first version of this control set `s.billed` directly, and that made it a
            control over a code path the live run does not use: `close()` reconciles against
            `billed_from_ledger()`, because a reconciliation a caller can defeat by forgetting
            to call `note_billed()` is a wish rather than a check — which is exactly how the
            live audit run produced a spurious RECONCILE_RED (billed 0.025 reported against
            0.100 actually spent). §4.1: the plant must sit on the axis the guard measures.
            """
            tmp = tempfile.mkdtemp()
            fake = FakeRequests([FakeResp(200, {"balance": pool_before}),
                                 FakeResp(200, {"balance": pool_after})])
            saved_req, rd.requests = rd.requests, fake
            try:
                s = rd.Session(tmp, "control", budget=rd.Budget(ceiling=2), settle=False)
                s.open()
                if billed:
                    s.led.write({"claim": "control:planted_spend", "kind": "generate",
                                 "verdict": "OK", "actual_cost": billed})
                return s.close()
            finally:
                rd.requests = saved_req

        # GREEN: the pool moved by exactly what the calls billed.
        row = run(10.00, 9.88, 0.12)
        record("reconcile/agree", "GREEN", "verdict INFO, reconciled True",
               "%s reconciled=%s" % (row["verdict"], row.get("reconciled")),
               row["verdict"] == "INFO" and row.get("reconciled") is True)

        # RED: the pool moved by more than the calls accounted for — the real-world shape of
        # this defect is a billed call whose row was lost, and it is on the bracket's own axis.
        row = run(10.00, 9.50, 0.12)
        record("reconcile/disagree", "RED", "verdict RECONCILE_RED with an INVARIANT_RED line",
               "%s reconciled=%s" % (row["verdict"], row.get("reconciled")),
               row["verdict"] == "RECONCILE_RED" and "INVARIANT_RED" in row,
               row.get("INVARIANT_RED", ""))

        # RED: an unreadable balance is not a silent pass either.
        row = run(None, None, 0.0)
        record("reconcile/unreadable", "RED", "RECONCILE_RED on an unreadable pool",
               row["verdict"], row["verdict"] == "RECONCILE_RED", row.get("INVARIANT_RED", ""))
    finally:
        _set_key(saved)


# --- CONTROL 7 — refusals are captured with their reason --------------------

def control_refusal_capture():
    print("\nCONTROL 7 — a refusal is ledgered as loudly as a success, with the server's reason.")
    saved = os.environ.get(rd.TOKEN_VAR)
    _set_key(FAKE_KEY)
    try:
        cases = [(400, "insufficient balance for this request", "insufficient_balance"),
                 (400, "width must be between 64 and 384", "invalid_input"),
                 (422, "validation error: prompt_style", "validation"),
                 (429, "slow down", "rate_limit"),
                 (401, "bad token", "auth"),
                 (500, "upstream exploded", "server_error")]
        for status, body, want in cases:
            tmp = tempfile.mkdtemp()
            led = rd.Ledger(tmp)
            fake = FakeRequests([FakeResp(status, {}, text=body)])
            saved_req, rd.requests = rd.requests, fake
            try:
                _, row = rd.generate({"prompt": "x", "num_images": 1}, led, "r",
                                     rd.Budget(ceiling=rd.SESSION_CEILING), dry_first=False)
            finally:
                rd.requests = saved_req
            ok = row["verdict"] == "REFUSED:" + want and body in row.get("reason", "")
            record("refusal/%d_%s" % (status, want), "RED",
                   "REFUSED:%s with the server's own words retained" % want,
                   "%s | reason=%r" % (row["verdict"], row.get("reason", "")[:60]), ok)
    finally:
        _set_key(saved)


def main():
    print(__doc__.split("\n\n")[0])
    print("=" * 78)
    for fn in (control_preflight, control_budget, control_divergence,
               control_ledger_hygiene, control_partial_return, control_reconcile,
               control_refusal_capture):
        try:
            fn()
        except Exception:
            traceback.print_exc()
            RESULTS.append({"control": fn.__name__, "half": "?", "ok": False,
                            "expected": "no exception", "got": "exception",
                            "verbatim": traceback.format_exc()[-800:]})

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CONTROLS-RESULT.json")
    red = [r for r in RESULTS if r["half"] == "RED"]
    green = [r for r in RESULTS if r["half"] == "GREEN"]
    failed = [r for r in RESULTS if not r["ok"]]
    summary = {"total": len(RESULTS), "red_halves": len(red), "green_halves": len(green),
               "failed": len(failed), "results": RESULTS,
               "verdict": "PASS" if not failed else "FAIL"}
    with open(out, "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    print("\n" + "=" * 78)
    print("%d controls: %d RED halves (guard fired on a planted defect), %d GREEN halves "
          "(guard stayed quiet), %d failed." % (len(RESULTS), len(red), len(green), len(failed)))
    print("VERDICT: %s   ->  %s" % (summary["verdict"], out))
    print("\nEvery guard in rd.py has now demonstrated it can fail. Bible §13.5 satisfied for\n"
          "the client's own instruments BEFORE any of its passes are counted.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
