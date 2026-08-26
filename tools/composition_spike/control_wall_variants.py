#!/usr/bin/env python3
"""POSITIVE CONTROLS for the wall-variant fix.

ART-BIBLE-v0 §13.5 / LOOP-PROCESS §4: no instrument's pass counts until it has demonstrated it
can fail. This session widened `wall_autotile` from one tile id per mask to a list of variants
picked by PositionHash. That is a new claim about what reaches the renderer's geometry, and the
tier-0 harness has already been bitten once by exactly this shape: `--tile-size` was echoed into
the log while `TopDownRenderer` drew a hard-coded 24px grid regardless, so the config and the
pixels could disagree in silence.

So the claim is tested the same way `control_tile_size.py` tests that one — by capturing the
real scene twice and requiring the PIXELS to differ.

  CONTROL 1 — the variants reach the renderer.
      Capture the corridor with every mask pinned to a single tile id, then with the real
      variant lists. If the list were decorative the two captures would be identical.

  CONTROL 2 — the mask-3 entry is the one being read.
      Plant a defect: point mask 3 (the south-facing run) at the FLOOR tile ids. The corridor's
      wall edges must visibly change. A harness that shrugged this off would not be reading the
      table it claims to read.

Both controls write their captures so a reviewer can look at what the machine compared.
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "tier0_harness"))
from capture_corridor import REPO, read_config, capture, git_commit  # noqa: E402

GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
ASSETS = "src/Presentation/assets/composition_spike"
OUT = os.path.join(REPO, "tools/composition_spike/evidence/controls")

FLOOR_IDS = [9120, 9121, 9122, 9123]   # the four §6.4 probe survivors


def derive_theme(name, transform):
    src = os.path.join(REPO, ASSETS, "tile_themes_boundB.yaml")
    dst = os.path.join(REPO, ASSETS, "tile_themes_%s.yaml" % name)
    with open(dst, "w") as f:
        f.write(transform(open(src).read()))
    return "res://%s/tile_themes_%s.yaml" % (ASSETS, name)


def pin_to_first(text):
    """Every mask resolves to a single tile - the behaviour before variants existed."""
    def sub(m):
        ids = [int(v) for v in re.findall(r"\d+", m.group(2))]
        return "%s[%d]" % (m.group(1), ids[0])
    return re.sub(r"^(      \d+: )(\[[^\]]*\])", sub, text, flags=re.MULTILINE)


def plant_mask3(text):
    """Mask 3 - the south-facing run - pointed at the floor tiles."""
    return re.sub(r"^(      3: )\[[^\]]*\]",
                  r"\1[%s]" % ", ".join(str(i) for i in FLOOR_IDS), text, flags=re.MULTILINE)


def diff_fraction(a, b):
    x = np.array(Image.open(a).convert("RGB")).astype(np.int16)
    y = np.array(Image.open(b).convert("RGB")).astype(np.int16)
    if x.shape != y.shape:
        return 1.0
    return float((np.abs(x - y).sum(2) > 0).mean())


def shoot(theme, name, cfg):
    out = os.path.join(OUT, name + ".png")
    rc, log, _ = capture(out, theme, cfg, GODOT, log_out=out.replace(".png", ".log"))
    if not os.path.exists(out):
        print("ABORT: %s produced no capture (exit %d)" % (name, rc), file=sys.stderr)
        print(log[-3000:], file=sys.stderr)
        sys.exit(1)
    return out


def main():
    cfg = read_config()
    os.makedirs(OUT, exist_ok=True)
    themes = {
        "control_pinned": derive_theme("control_pinned", pin_to_first),
        "control_plant3": derive_theme("control_plant3", plant_mask3),
    }
    if "--build-only" in sys.argv:
        print("derived: %s" % ", ".join(themes))
        print("run Godot --headless --import, then re-run without --build-only")
        return 0

    print("WALL-VARIANT POSITIVE CONTROLS")
    print("commit: %s\n" % git_commit())

    real = shoot("res://%s/tile_themes_boundB.yaml" % ASSETS, "variants", cfg)
    pinned = shoot(themes["control_pinned"], "pinned", cfg)
    planted = shoot(themes["control_plant3"], "plant_mask3", cfg)

    results, ok = [], True
    for label, other, floor in (
            ("CONTROL 1  variants vs one-tile-per-mask", pinned, 0.005),
            ("CONTROL 2  mask 3 planted with floor tiles", planted, 0.005)):
        frac = diff_fraction(real, other)
        passed = frac >= floor
        ok &= passed
        print("  %-44s differing pixels %6.3f%%   %s"
              % (label, frac * 100, "PASS" if passed else "FAIL"))
        results.append(dict(control=label, differing_pixel_fraction=frac,
                            floor=floor, passed=passed))

    with open(os.path.join(OUT, "controls.json"), "w") as f:
        json.dump(dict(commit=git_commit(), results=results, all_passed=bool(ok)), f, indent=1)
    print("\n%s  -> %s" % ("ALL CONTROLS PASSED" if ok else "A CONTROL FAILED",
                           os.path.relpath(OUT, REPO)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
