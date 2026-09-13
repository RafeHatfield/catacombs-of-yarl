#!/usr/bin/env python3
"""THE MEMORY PRECHECK — refuse to start what an OOM kill can leave corrupt.

RULED (Rafe, 2026-09-10):

    "before seating a panel or starting any recompose/capture, check free memory against a floor
     (measure what one seat + one capture actually peak at, set the floor above it); if below,
     STOP cleanly with 'insufficient headroom: X free, Y required' — never start a write that an
     OOM kill can leave corrupt."

⚠ I GUESSED SWAP AND THE MEASUREMENT SAID NO. Before measuring I reasoned that swap headroom was
the mechanism — swap was 3182MB of 4096MB used when the third round died, and that looked like the
answer. It is not. Measured:

    one seat      peak RSS 351.0 MB   swap drew 0.0 MB   system free 64% -> 48%   448s
    one capture   peak RSS 507.2 MB   swap drew 0.0 MB   system free 62% -> 57%     4s

**Neither touches swap at all.** The swap that was full had been filled by other processes long
before, and it stayed exactly where it was while a seat ran for seven and a half minutes. A floor
built on swap would have been a number that never moves gating a thing it does not measure — the
saturating-comparator fault of §13.11 in a new place, and I nearly shipped it.

WHAT DOES MOVE is the system's own free percentage: **16 points for a seat**, and the seat holds
its 351MB for 448 seconds, which is the sustained pressure that matters. The capture is heavier at
peak (507MB) but lasts four seconds.

⚠ AND FREE% IS NOT LINEAR IN THE PROCESS. Sixteen points of 16GB is 2.6GB, and the seat is 351MB;
the system reclaims and reallocates around it. So free% is used as a HEADROOM BUDGET rather than
as an estimate of the process — the floor is set to leave more than the measured dip, not to
predict it.

THE FLOORS, and both are derived from the numbers above:

    seat    require free% >= 35, so a 16-point dip still lands near 19
    write   require free% >= 40, because a capture peaks half a gigabyte higher and, unlike a
            seat, a killed write can leave a tile family half-written

Swap is still read and still refuses below 200MB — not because it predicted these kills, but
because exhausted swap is a real way to die and costs nothing to check.

WHY REFUSING IS THE POINT, not merely retrying: a seat that dies costs a seat. A compose or a
capture that dies mid-write can leave a tile family half-written, and the next round would judge a
corrupt asset without knowing. That asymmetry is why the write floor is higher, and why this is a
precheck rather than a retry loop.
"""
import re
import subprocess

# ── THE FLOORS, MEASURED (tools/tier0_harness/measure_headroom.py, 2026-09-10) ───────────────
SEAT_PEAK_MB = 351.0          # measured, one seat, 448s
CAPTURE_PEAK_MB = 507.2       # measured, one capture, 4s
SEAT_FREE_PCT_DIP = 16        # measured, 64% -> 48%

FREE_PCT_FLOOR_SEAT = 35      # a 16-point dip from here still lands near 19
FREE_PCT_FLOOR_WRITE = 40     # a capture peaks 156MB higher, and a killed write can corrupt
SWAP_FLOOR_MB = 200           # not what killed the rounds; still a real way to die


def swap_free_mb():
    """NaN when swap is UNALLOCATED, not zero. After a restart macOS reports
    `total = 0.00M used = 0.00M free = 0.00M` until it first needs a swapfile; that is the
    machine's healthiest state, and reading its 0MB free as EXHAUSTED refused every capture and
    seat on 2026-09-12 with 76% of memory free. Exhaustion is free -> 0 with total > 0."""
    out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
    t = re.search(r"total = ([\d.]+)M", out)
    m = re.search(r"free = ([\d.]+)M", out)
    if t and float(t.group(1)) == 0.0:
        return float("nan")
    return float(m.group(1)) if m else float("nan")


def free_pct():
    out = subprocess.run(["memory_pressure"], capture_output=True, text=True).stdout
    m = re.search(r"System-wide memory free percentage:\s*(\d+)%", out)
    return int(m.group(1)) if m else -1


def check(kind="seat"):
    """(ok, message). `kind` is 'seat' or 'write' — a write's floor is higher because a killed
    write can corrupt a tile family, and a killed seat only costs a seat."""
    need = FREE_PCT_FLOOR_WRITE if kind == "write" else FREE_PCT_FLOOR_SEAT
    sf, pct = swap_free_mb(), free_pct()
    if pct < 0:
        return True, "headroom unknown on this platform; proceeding"
    if pct < need:
        return False, ("insufficient headroom: %d%% free, %d%% required for a %s "
                       "(measured dip for a seat is %d points; swap free %.0fMB). Refusing to "
                       "start — an OOM kill mid-%s is how a tile family gets left half-written."
                       % (pct, need, kind, SEAT_FREE_PCT_DIP, sf,
                          "write" if kind == "write" else "round"))
    if sf == sf and sf < SWAP_FLOOR_MB:
        return False, ("insufficient headroom: %.0fMB swap free, %dMB required (system free "
                       "%d%%). Refusing to start." % (sf, SWAP_FLOOR_MB, pct))
    return True, ("headroom ok: %d%% free (floor %d), swap free %.0fMB" % (pct, need, sf))


def require(kind="seat"):
    """Refuse loudly and cleanly. Callers that write assets must use this, not `check`."""
    ok, msg = check(kind)
    print("[headroom] " + msg)
    return ok, msg


def no_lingering_seats():
    """RULED: 'free each seat fully before the next starts (confirm no lingering processes).'

    `run_seat` uses subprocess.run, which waits and reaps, so a seat is structurally gone before
    the next begins. This asserts it rather than trusting it — a leak here would compound across
    five seats and is exactly the shape that killed three rounds.
    """
    out = subprocess.run(["pgrep", "-f", "claude -p"], capture_output=True, text=True)
    pids = [p for p in out.stdout.split() if p.strip()]
    return len(pids) == 0, pids


if __name__ == "__main__":
    import sys
    ok, msg = require(sys.argv[1] if len(sys.argv) > 1 else "seat")
    clean, pids = no_lingering_seats()
    print("[headroom] lingering seats: %s" % ("none" if clean else ", ".join(pids)))
    raise SystemExit(0 if ok else 3)
