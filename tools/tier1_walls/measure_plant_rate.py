# -*- coding: utf-8 -*-
"""The per-seat catch rate on LIVE plants, and what it implies for a 5-seat panel."""
import glob
import io
import json
from collections import defaultdict

RETIRED = {"crushed-midband.png"}

per = defaultdict(lambda: [0, 0])          # plant -> [caught, drawn]
rounds = []
for f in sorted(glob.glob(".claude/skills/frame-critic/history/r00*-art_autonomy-amendment.json")):
    d = json.load(io.open(f, encoding="utf-8"))
    seats = (d.get("panel") or {}).get("per_seat") or []
    if not seats:
        continue
    live_c = live_n = 0
    for s in seats:
        pl = s.get("plant")
        if not pl or pl in RETIRED:
            continue
        per[pl][1] += 1
        live_n += 1
        if s.get("caught"):
            per[pl][0] += 1
            live_c += 1
    rounds.append((d.get("round"), d.get("verdict"), live_c, live_n))

print("per-plant, LIVE plants only (retired excluded):")
tc = tn = 0
for pl, (c, n) in sorted(per.items()):
    tc += c
    tn += n
    print("   %-24s %d of %d caught" % (pl, c, n))
print("   %-24s %d of %d = %.1f%% per-seat catch rate" % ("TOTAL", tc, tn, 100.0 * tc / tn))

print("\nper round:")
for r, v, c, n in rounds:
    print("   round %s  %-15s live plants caught %d of %d" % (r, v, c, n))

p = tc / float(tn)
print("\nWHAT THAT IMPLIES. The plant rule is UNANIMOUS: any seat missing voids the round.")
print("   P(a seat catches)          = %.3f" % p)
for n in (1, 3, 5, 7):
    print("   P(all %d catch) = %.3f^%d  = %.1f%%   -> %.1f%% of rounds VOID"
          % (n, p, n, 100 * p ** n, 100 * (1 - p ** n)))
print("\n⚠ MORE SEATS MAKE A VOID MORE LIKELY, NOT LESS. The 5-seat panel was ruled to reduce")
print("   RANK noise; the plant gate is unanimous-catch, so the same change multiplies the")
print("   chance of tripping it. The two terms pull in opposite directions.")
