#!/usr/bin/env python3
"""Print one tile's full field_laws verdict. A reading aid for the report, not an instrument."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import field_laws as FL      # noqa: E402

KEYS = ("verdict", "cell", "ring_instrument", "mad", "n_incidents", "incidents",
        "n_frames", "frames", "seam", "n_grid", "grid")

for p in sys.argv[1:]:
    v = FL.verdict(p)
    print("== %s" % p)
    print(json.dumps({k: v[k] for k in KEYS}, indent=1))
