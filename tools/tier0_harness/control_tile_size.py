#!/usr/bin/env python3
"""Positive control for the TILE SIZE PARAMETER itself.

ART-BIBLE-v0 §13.5 / ART-LOOP-PROCESS-v0 §4: no instrument's pass counts until it has
demonstrated it can fail.

The five existing controls each plant a defect and prove the harness notices. None of them
proves the thing this change added. `--tile-size` is new, and a parameter that is silently
ignored is the specific failure this whole change exists to close: before it, the config could
declare 32 and `TopDownRenderer` would draw a 24px grid regardless, and every control would
still pass — green, reproducible, and measuring the wrong grid.

The engine echoing `tile=32x32` into the log is necessary but not sufficient: an echo proves
the flag was PARSED, not that it reached the renderer's geometry. The pixels are the evidence.

So: capture the identical scene at 24 and at 32 and require that they DIFFER. If they do not,
the parameter is decorative and must be labelled so or deleted.

This is the same shape as the surface audit's method, arrived at for the same reason —
run it twice, vary one parameter, diff the output — and it is the only instrument that catches
a silent no-op.
"""
import os
import sys

from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_corridor import REPO, read_config, capture  # noqa: E402

EVIDENCE = "tools/tier0_harness/evidence"
THEME = "res://src/Presentation/assets/tier0_harness/tile_themes_stub.yaml"
GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"


def shoot(cfg, size, scale, name):
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in cfg.items()}
    cfg["tile"]["size"] = size
    cfg["tile"]["scale"] = scale
    out = os.path.join(REPO, EVIDENCE, name)
    rc, log, cmd = capture(out, THEME, cfg, GODOT, log_out=out.replace(".png", ".log"))
    echoed = next((l.strip() for l in log.splitlines() if "Map renderer:" in l), "<no echo>")
    print("  %-22s exit=%d  %s" % (name, rc, echoed))
    return out if os.path.exists(out) else None


def main():
    cfg = read_config()
    print("CONTROL — the tile size parameter must change the pixels, not just the log.\n")

    print("-- capture at the previous grid (24) --")
    a = shoot(cfg, 24, 3.0, "tilesize_24.png")
    print("-- capture at the ruled grid (32) --")
    b = shoot(cfg, 32, 2.0, "tilesize_32.png")

    if not a or not b:
        print("\nRESULT: FAIL — a capture did not render; nothing can be concluded.")
        return 1

    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        print("\nRESULT: FAIL — captures differ in resolution (%s vs %s); the comparison is "
              "not like-for-like." % (ia.size, ib.size))
        return 1
    d = ImageChops.difference(ia, ib)
    px = list(d.getdata())
    frac = sum(1 for p in px if p != (0, 0, 0)) / float(len(px))
    print("\n  pixels differing between the 24px and 32px captures: %.4f" % frac)

    if frac == 0.0:
        print("\nRESULT: FAIL — byte-identical. --tile-size reached the log and NOT the "
              "renderer.\n  The parameter is decorative. Label it so or delete it (§13.5).")
        return 1
    print("\nRESULT: PASS — the parameter moves the rendered grid, so its pass counts.")
    print("  Note what this does and does not say: it says 24 and 32 are different pictures.")
    print("  It does NOT say 32 is the right number — §4.3's derivation has not happened and")
    print("  the value is carried as a RULING, not as a derived constant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
