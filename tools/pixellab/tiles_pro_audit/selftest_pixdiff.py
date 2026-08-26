#!/usr/bin/env python3
"""Zero-cost, no-network positive control for the diff instrument (§4, bible §13.5).

The §6.4 audit's own lesson: the first lever pass reported HONOURED on every surface at
pixdiff=1.0000, *including a control*. An instrument that returns the same answer to a real
lever and to nothing at all has not measured anything. So before this audit's lever column is
allowed to mean anything, the diff has to be shown going both ways on inputs whose answer is
known in advance, and shown going red when it is sabotaged.

No PixelLab call. No credential needed. Nothing here is billed.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tiles_pro as tp  # noqa: E402

CHECKS = []


def check(name, ok, detail):
    CHECKS.append((name, ok, detail))
    print(("  PASS  " if ok else "  RED   ") + "%-42s %s" % (name, detail))


def main():
    a = Image.new("RGBA", (32, 32), (80, 80, 90, 255))
    b = a.copy()
    c = a.copy()
    c.putpixel((0, 0), (255, 0, 0, 255))          # exactly one pixel of 1024
    d = Image.new("RGBA", (32, 32), (10, 200, 10, 255))   # every pixel differs
    e = Image.new("RGBA", (52, 87), (80, 80, 90, 255))    # different canvas

    print("\n== diff instrument, known answers ==")
    check("identical -> 0.0", tp.pixdiff(a, b) == 0.0, "%.6f" % tp.pixdiff(a, b))
    check("one pixel -> 1/1024", abs(tp.pixdiff(a, c) - 1 / 1024.0) < 1e-9,
          "%.6f" % tp.pixdiff(a, c))
    check("all pixels -> 1.0", tp.pixdiff(a, d) == 1.0, "%.6f" % tp.pixdiff(a, d))
    check("size mismatch -> 1.0", tp.pixdiff(a, e) == 1.0, "%.6f" % tp.pixdiff(a, e))

    print("\n== kit-level aggregate ==")
    k1 = {0: a, 1: a, 2: a}
    k2 = {0: b, 1: c, 2: d}
    mean, moved, n = tp.kitdiff(k1, k2)
    check("kitdiff counts movers, not tiles", moved == 2 and n == 3,
          "moved=%d of %d, mean=%.6f" % (moved, n, mean))

    print("\n== sabotage: the instrument must go red ==")
    real = tp.pixdiff
    tp.pixdiff = lambda x, y: 1.0                 # stub the metric to a constant (§4)
    stub_identical = tp.pixdiff(a, b)
    _, moved_s, _ = tp.kitdiff({0: a}, {0: b})
    tp.pixdiff = real
    check("stubbed metric is CAUGHT", stub_identical != 0.0 and moved_s == 1,
          "stub said %.4f for identical inputs and counted %d mover" % (stub_identical, moved_s))
    check("restore returns instrument", tp.pixdiff(a, b) == 0.0, "%.6f" % tp.pixdiff(a, b))

    print("\n== 423 is a retry signal, not a refusal (§8.6) ==")
    check("423 -> in_progress", tp.classify(423, "Tiles are still being generated")
          == "in_progress", tp.classify(423, "Tiles are still being generated"))
    check("422 -> invalid_input", tp.classify(422, "literal_error") == "invalid_input",
          tp.classify(422, "literal_error"))

    bad = [n for n, ok, _ in CHECKS if not ok]
    print("\n%d checks, %d red" % (len(CHECKS), len(bad)))
    if bad:
        print("INSTRUMENT IS BLIND:", ", ".join(bad))
        return 1
    print("The diff instrument has demonstrated it can fail. Its zeroes count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
