#!/usr/bin/env python3
"""Collect the three constraint probes that were ACCEPTED instead of refused.

They were expected to 422 for free and did not, so they are billed work that exists. Leaving
them undownloaded would not save the money and would destroy the evidence, so they are fetched,
ledgered, and read as the canvas-column data they turn out to be:

  * `tile_size: 17` and `tile_size: 20` accepted → the "tighter per-shape ranges" note does NOT
    coarsen square_topdown building kits to a set of blessed sizes. The emitted canvas per size
    is the actual answer to the canvas column.
  * `style_images: []` accepted → a zero-reference conditioning call is not refused. Whether it
    is also a silent no-op is answered by the tiles.

⚠ `usage` came back **null** on all three 202s. `PIXELLAB-INTEGRATION-AUDIT` §8.7 recorded the
202 reporting `usage` exactly. Either the field moved to the completion response or the surface
changed; this script records `usage` from the GET as well, and the settled bracket around the
completion is what the cost claim actually rests on.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tiles_pro as tp  # noqa: E402

OUT = os.path.join(HERE, "columns")

JOBS = [
    ("size_17_odd", "30e1af09-3679-4506-b364-e967e26ba0b9"),
    ("size_20_even_nonstandard", "0602d9b4-1797-4aa5-9cdb-c74c5ba04c91"),
    ("style_images_empty_list", "5a431d7f-cb3d-4dce-a87c-7da765ee2f30"),
]


def main():
    led = tp.Ledger(OUT, "constraints_ledger.jsonl")
    summary = []
    with tp.Bracket(led, "collect_surprises"):
        for label, tid in JOBS:
            tiles, meta = tp.fetch(tid, led, "surprise_" + label,
                                   claim="collect:" + label)
            if meta is None:
                print("%-28s FETCH FAILED" % label)
                summary.append({"label": label, "tile_id": tid, "ok": False})
                continue
            sizes = meta["sizes"]
            print("%-28s n=%-3d kind=%-10s sizes=%s usage=%s polls=%d wait=%ss" %
                  (label, meta["n_tiles"], meta["kind"], sizes, meta["usage"],
                   meta["polls"], meta["wait_seconds"]))
            summary.append({"label": label, "tile_id": tid, "ok": True,
                            "n_tiles": meta["n_tiles"], "kind": meta["kind"],
                            "sizes": [list(s) for s in sizes],
                            "usage": meta["usage"], "wait_seconds": meta["wait_seconds"]})
    with open(os.path.join(OUT, "surprises.json"), "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
