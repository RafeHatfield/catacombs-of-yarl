#!/usr/bin/env python3
"""Where does `measure_bar.Tiles.get` land for a floor gid, and why is it not the tile?

The sheet probe reads every floor gid at opaque=1.000 by direct indexing; the resolver reads
the same gids at 0.14-0.89. One of the two is wrong about which pixels a gid names, and the
difference is not cosmetic — `bar_measurements.json` and WALL-RECIPE.md's six adopted numbers
were produced through the resolver.

MEASUREMENTS LEAVE; PIXELS NEVER DO (§13.3). Prints numbers. Writes nothing.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/sighted_round"))
import measure_bar as MB      # noqa: E402

maps = sorted(f for f in os.listdir(MB.EXAMPLES) if f.endswith(".tmx"))
print("tileset declarations, per map, in the order load_tmx returns them:\n")
seen = {}
for fn in maps:
    m = MB.load_tmx(os.path.join(MB.EXAMPLES, fn))
    print("  %s" % fn)
    for ts in m["tilesets"]:
        print("     firstgid %-6d count %-6d %-20s %s"
              % (ts["firstgid"], ts["count"], ts["name"], os.path.basename(ts["image"])))
        prev = seen.get(ts["firstgid"])
        if prev and prev != ts["image"]:
            print("     ^^ COLLISION: firstgid %d already seen pointing at %s"
                  % (ts["firstgid"], os.path.basename(prev)))
        seen[ts["firstgid"]] = ts["image"]
        if not os.path.exists(ts["image"]):
            print("     ^^ MISSING FILE: %s" % ts["image"])

print("\nresolver vs direct index, for the floor gids:\n")
tilesets = {}
for fn in maps:
    for ts in MB.load_tmx(os.path.join(MB.EXAMPLES, fn))["tilesets"]:
        tilesets[ts["firstgid"]] = ts
res = MB.Tiles(list(tilesets.values()))
for gid in (62, 63, 64, 66, 67, 102, 112):
    a = res.get(gid)
    chosen = next(s for s in res.sets if gid >= s["firstgid"])
    print("  gid %-5d -> set firstgid %-5d %-22s opaque=%.3f  shape=%s"
          % (gid, chosen["firstgid"], os.path.basename(chosen["image"]),
             float((a[..., 3] > 128).mean()) if a is not None else -1,
             None if a is None else a.shape))
