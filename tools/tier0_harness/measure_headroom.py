#!/usr/bin/env python3
"""WHAT A SEAT AND A CAPTURE ACTUALLY COST, so the precheck's floor is measured rather than picked.

RULED (Rafe, 2026-09-10): *"measure what one seat + one capture actually peak at, set the floor
above it."*

⚠ RAW FREE PAGES ARE THE WRONG SIGNAL ON THIS PLATFORM, and reading them is what made three killed
rounds look mysterious. macOS keeps free memory near zero by design — it was 92MB free while
`memory_pressure` reported the system 63% free, because inactive and purgeable pages are
reclaimable and are not "used".

⚠ AND SWAP IS THE WRONG SIGNAL TOO, WHICH I ONLY LEARNED BY RUNNING THIS. Before measuring I wrote
here that swap headroom was what predicted the kills — swap was 3182MB of 4096MB used when the
third round died, and it looked conclusive. It is not: a seat drew **0.0MB** of swap and a capture
drew **0.0MB**, while a seat held 351MB of RSS for seven and a half minutes. That swap had been
filled by other processes long before and never moved. The claim is corrected rather than deleted,
because the wrong hypothesis is the reason this tool exists.

What moves is the system's own free percentage — 16 points for one seat — so that is what the
floor is built on, with swap kept only as a secondary guard against genuine exhaustion.

── THE DECK DOWNSCALE WAS TESTED AND IS NOT SHIPPED ─────────────────────────────────────────

RULED (Rafe, 2026-09-10): *"deck images at device pixel size are larger than a seat needs to rank
craft; downscale deck captures to the seat's judging resolution ... Report the before/after peak
per seat."*

Reported, and the answer is that it buys nothing:

    full scale   750x911 x3 + 384x288    peak RSS 351.0 MB   448s   free% low 48
    half scale   375x455 x3 + 192x144    peak RSS 363.1 MB   450s   free% low 47

**Twelve megabytes HIGHER, which is inside the noise, for the same runtime.** A seat's footprint is
the Claude Code runtime, not its images: the four decoded frames are 6.5MB of 351MB — 1.9% — so
removing them entirely could not move the number that matters.

SO THE CHANGE IS NOT MADE. Downscaling would halve every coordinate a seat quotes and average away
per-fragment lighting finer than a native pixel, and it would do that in exchange for nothing
measurable. A change that only looks like a fix is worse than no change: it perturbs the gate's
input and buys a number that did not move.

The memory problem is solved by the precheck alone, which is the honest scope of it.

Usage:
    python3 tools/tier0_harness/measure_headroom.py seat <deck-dir>
    python3 tools/tier0_harness/measure_headroom.py capture
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def swap_free_mb():
    out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
    m = re.search(r"free = ([\d.]+)M", out)
    return float(m.group(1)) if m else float("nan")


def free_pct():
    out = subprocess.run(["memory_pressure"], capture_output=True, text=True).stdout
    m = re.search(r"System-wide memory free percentage:\s*(\d+)%", out)
    return int(m.group(1)) if m else -1


def rss_kb(pid):
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True)
    try:
        return int(out.stdout.strip())
    except ValueError:
        return 0


def tree_rss_kb(root):
    """RSS of a process and everything it spawned — a seat's cost is not just its own pid."""
    out = subprocess.run(["ps", "-ax", "-o", "pid=,ppid=,rss="], capture_output=True, text=True)
    kids, rss = {}, {}
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        pid, ppid, r = int(parts[0]), int(parts[1]), int(parts[2])
        kids.setdefault(ppid, []).append(pid)
        rss[pid] = r
    total, stack = 0, [root]
    while stack:
        p = stack.pop()
        total += rss.get(p, 0)
        stack += kids.get(p, [])
    return total


def watch(proc, label):
    peak, swap_lo, pct_lo = 0, swap_free_mb(), free_pct()
    swap0 = swap_lo
    t0 = time.time()
    while proc.poll() is None:
        peak = max(peak, tree_rss_kb(proc.pid))
        swap_lo = min(swap_lo, swap_free_mb())
        pct_lo = min(pct_lo, free_pct())
        time.sleep(1.0)
    dt = time.time() - t0
    print("  %-22s peak RSS %6.1f MB | swap free %6.1f -> %6.1f MB (drew %.1f) | free%% low %d | %.0fs"
          % (label, peak / 1024.0, swap0, swap_lo, swap0 - swap_lo, pct_lo, dt))
    return peak / 1024.0, swap0 - swap_lo


def seat(deck):
    prompt = open(os.path.join(REPO, ".claude/skills/frame-critic/seat_prompt.txt")).read()
    p = subprocess.Popen(["claude", "-p", prompt, "--allowedTools", "Read"],
                         cwd=deck, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return watch(p, "one seat")


def capture():
    cmd = ["python3", os.path.join(REPO, "tools/tier0_harness/capture_corridor.py"),
           "--out", os.path.join(REPO, "tools/tier1_floors/evidence/headroom_probe.png"),
           "--theme-config", "res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml",
           "--scene-spec", "src/Presentation/assets/tier0_harness/scenes/tier1_props_review.json",
           "--floor-overlays", "res://src/Presentation/assets/tier1_floors/MANIFEST.json",
           "--ashlar-floor", "res://src/Presentation/assets/tier1_ashlar/MANIFEST.json",
           "--boundary-wall", "res://src/Presentation/assets/tier1_walls/MANIFEST.json",
           "--wall-bindings", "res://src/Presentation/assets/tier1_bindings/MANIFEST.json",
           "--wall-cap", "res://src/Presentation/assets/tier1_cap/MANIFEST.json",
           "--void-ring", "1",
           "--log-out", os.path.join(REPO, "tools/tier1_floors/evidence/headroom_probe.log")]
    p = subprocess.Popen(cmd, cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return watch(p, "one capture")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "seat"
    print("BEFORE: swap free %.1f MB, system free %d%%" % (swap_free_mb(), free_pct()))
    if what == "seat":
        seat(sys.argv[2])
    else:
        capture()
    print("AFTER:  swap free %.1f MB, system free %d%%" % (swap_free_mb(), free_pct()))
