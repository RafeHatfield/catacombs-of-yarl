#!/usr/bin/env python3
"""THE PRECHECK MUST DEMONSTRATE IT CAN REFUSE.

§13.5 / LOOP-PROCESS §4: no instrument's pass counts until it has been shown to fail. A headroom
check that has only ever run on a machine with headroom is a function that returns True, and it
would have let all three killed rounds start.

This drives `headroom.check` itself — never a copy — with the platform readings injected, so what
is proved is what runs.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import headroom as H  # noqa: E402

FAILURES = []


def case(name, pct, swap, kind, want_ok, want_text=""):
    H.free_pct, H.swap_free_mb = (lambda: pct), (lambda: swap)
    ok, msg = H.check(kind)
    good = (ok == want_ok) and (want_text in msg)
    print("%s %-52s -> %s" % ("PASS " if good else "FAIL ", name, msg[:78]))
    if not good:
        FAILURES.append(name)


def main():
    real_pct, real_swap = H.free_pct, H.swap_free_mb
    print("HEADROOM PRECHECK — driving headroom.check with injected platform readings\n")
    print("measured: a seat peaks at %.0fMB and dips free%% by %d; a capture peaks at %.0fMB\n"
          % (H.SEAT_PEAK_MB, H.SEAT_FREE_PCT_DIP, H.CAPTURE_PEAK_MB))

    case("A  61% free, seat            -> allow", 61, 978, "seat", True, "headroom ok")
    case("B  61% free, write           -> allow", 61, 978, "write", True, "headroom ok")

    # the band between the two floors is the whole reason there are two
    case("C  37% free, seat            -> allow", 37, 978, "seat", True, "headroom ok")
    case("D  37% free, WRITE           -> REFUSE", 37, 978, "write", False, "insufficient")

    # the state the three killed rounds actually started in
    case("E  20% free, seat            -> REFUSE", 20, 913, "seat", False, "insufficient")
    case("F  20% free, write           -> REFUSE", 20, 913, "write", False, "insufficient")
    case("G  exactly at the seat floor -> allow", 35, 978, "seat", True, "headroom ok")
    case("H  one point under it        -> REFUSE", 34, 978, "seat", False, "34% free, 35% required")

    # swap is a secondary guard: it did NOT cause these kills, and it still refuses when exhausted
    case("I  plenty free, swap gone    -> REFUSE", 61, 40, "seat", False, "swap free")

    # a platform that does not answer must not become a silent refusal
    case("J  platform silent           -> proceed", -1, float("nan"), "seat", True, "unknown")

    H.free_pct, H.swap_free_mb = real_pct, real_swap
    print("\n" + "=" * 70)
    if FAILURES:
        print("%d CASE(S) FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("EVERY CASE BEHAVED AS DECLARED. The check refuses below either floor, refuses a WRITE")
    print("in the band where it would still seat a round, refuses on exhausted swap, and does not")
    print("turn an unreadable platform into a silent no. E and F are the state three killed")
    print("rounds started in — under this check none of them would have begun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
