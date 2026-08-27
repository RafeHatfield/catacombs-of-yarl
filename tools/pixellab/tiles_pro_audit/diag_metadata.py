#!/usr/bin/env python3
"""The pixdiff is blind on this endpoint. This looks for an instrument that is not.

MEASURED, and it overturns a prior [API] claim in this repo: four byte-identical calls at
seed 1337 produced four entirely different kits. The per-tile diff equals each tile's OPAQUE
fraction — every visible pixel differs — so normalised against the visible area the noise floor
is **1.0000**. There is no headroom. A lever pixdiff on this endpoint measures nothing, and
reading one would be the §6.4 audit's own first mistake repeated: MCP `pro` measured its lever
at 1.0000 against a noise floor of 1.0000 and the honest output was `NO INSTRUMENT`.

So the lever column needs a readout the generative noise cannot reach. The response carries
several, and they are discrete rather than pictorial:

  * `tile_rules.parts.painted` — WHICH tiles were individually painted rather than composed
    from swatches. This is `building_layout` expressed as a list of integers.
  * canvas size and `stack_stride_px` — the projection, in pixels.
  * the floor tile's own bounding box — the ground cell, which is what bible §3 asks about.
  * `wall_tiles`, `arity`, `rule_type`, the part table itself — the grammar.

This file checks, for free, whether those are STABLE across the five noisy kits already on
disk. A readout that wobbles between identical calls is no better than the pixdiff. A readout
that is identical across five kits whose every visible pixel differs has headroom, and a lever
that moves it has moved something real.

That check is also this instrument's positive control, and it is available at zero cost:
the five kits are the hardest negative control there is.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

KITS = ["yield/kit_A0", "yield/kit_A1", "yield/kit_A2", "yield/kit_A3", "yield/kit_B"]


def readout(kit_dir):
    """The noise-free description of a kit: grammar and geometry, never pixels."""
    rules = json.load(open(os.path.join(kit_dir, "tile_rules.json"))) or {}
    parts = rules.get("parts") or {}
    floor = Image.open(os.path.join(kit_dir, "tile_00.png")).convert("RGBA")
    bbox = floor.getbbox()
    canvas = list(floor.size)
    return {
        "canvas": canvas,
        "floor_bbox": list(bbox) if bbox else None,
        "floor_cell": [bbox[2] - bbox[0], bbox[3] - bbox[1]] if bbox else None,
        "stack_stride_px": rules.get("stack_stride_px"),
        "wall_tiles": rules.get("wall_tiles"),
        "arity": rules.get("arity"),
        "rule_type": rules.get("rule_type"),
        "view_angle": rules.get("view_angle"),
        "n_painted": len(parts.get("painted") or []),
        "painted": parts.get("painted"),
        "part_keys": sorted(k for k in parts if k not in ("materials", "painted")),
    }


def main():
    outs = {}
    for k in KITS:
        d = os.path.join(HERE, k)
        if not os.path.isdir(d):
            print("missing", k)
            continue
        outs[k] = readout(d)

    keys = ["canvas", "floor_cell", "stack_stride_px", "wall_tiles", "arity", "rule_type",
            "view_angle", "n_painted"]
    print("%-16s %s" % ("readout", "  ".join("%-14s" % os.path.basename(k) for k in outs)))
    stable = {}
    for f in keys:
        vals = [json.dumps(outs[k][f]) for k in outs]
        stable[f] = len(set(vals)) == 1
        print("%-16s %s %s" % (f, "  ".join("%-14s" % v[:14] for v in vals),
                               "STABLE" if stable[f] else "<-- WOBBLES"))
    pl = [json.dumps(outs[k]["painted"]) for k in outs]
    stable["painted"] = len(set(pl)) == 1
    print("%-16s %s" % ("painted list", "identical across all kits" if stable["painted"]
                        else "DIFFERS between kits"))
    pk = [json.dumps(outs[k]["part_keys"]) for k in outs]
    stable["part_keys"] = len(set(pk)) == 1
    print("%-16s %s" % ("part table", "identical across all kits" if stable["part_keys"]
                        else "DIFFERS between kits"))

    n_stable = sum(1 for v in stable.values() if v)
    print("\n%d of %d readouts are identical across %d kits whose every visible pixel differs."
          % (n_stable, len(stable), len(outs)))
    if n_stable == len(stable):
        print("✅ The structural readout has headroom the pixdiff does not. A lever that moves\n"
              "   it has moved something the generative noise cannot fake.")
    else:
        print("⚠ Some readouts wobble between identical calls; those are not instruments "
              "either.")
    with open(os.path.join(HERE, "columns", "structural_readout.json"), "w") as f:
        json.dump({"kits": outs, "stable": stable}, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
