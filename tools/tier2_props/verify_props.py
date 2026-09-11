#!/usr/bin/env python3
"""EVERY DECLARED PROP MUST DRAW, AND EVERY ONE MUST BE LIT.

The tier-two acceptance criterion routed here from the wall lane has two halves, and only one of
them is about the art:

    "the props session PASSES only if orc work is visible AS STANDING OBJECTS IN THE LIT RADIUS
     of the walked scene."

⚠ THIS EXISTS BECAUSE I MADE THE SAME MISTAKE TWICE IN ONE RUN. The first props scene put a second
marker at 5.4 tiles to test §8.3.1's repetition; it measured 17.97 against §13.8's floor of 36.7
and could not answer the question it was placed for. The next scene put the whole barricade family
at 4.0–4.5 tiles; they measured 22–32 and could not either. Both times the placement looked
obviously fine and both times it was dark.

A prop in the dark answers nothing, and remembering that is not a mechanism. So this refuses the
scene, and it refuses BEFORE a panel is seated rather than after five seats have ranked a frame
whose subject is invisible.

BOTH HALVES ARE BUILT NOW. `--drew` is the second one, and it took three tries to get an
honest control.

⚠ THE OBVIOUS CONTROL IS WRONG, AND IT ALREADY FOOLED THIS PROJECT ONCE. Capturing the scene
with the props REMOVED and diffing does not isolate the sprite: a blocking prop marks its cells,
and a marked cell changes what the floor composer lays under it (#128's pedestal suppression).
An earlier probe measured "pixels changed at the prop's cell", called it the sprite drawing, and
was measuring `MarkPropCell` repainting the floor.

THE CONTROL THAT IS HONEST keeps every prop declared, in place, blocking — so every cell is
marked and the floor underneath is composed identically — and swaps only the TILE IDS for a
reserved fully transparent tile. The scene is the same scene; the cells are the same cells; the
one thing that differs is whether a sprite is painted. Whatever changes between the two frames
is the sprite, and nothing else can be.

WHAT IT DOES MEASURE, in its first half: delivered luminance at every cell of every prop's
footprint, reporting the WORST cell. Anchor-only sampling was right while every prop was 1x1 and
became wrong the moment §12.2 allowed a 1x2 — the far cell of a tall prop is always the darker
one.

Usage: python3 tools/tier2_props/verify_props.py [frame.png]
"""
import io
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes/tier1_props_review.json")
FRAME = os.path.join(REPO, "tools/tier1_floors/evidence/combined.png")

PERCEPTUAL_FLOOR = 36.7          # §13.8's 0.1440 on a 0..255 scale
GRID_X0, GRID_Y0, PITCH = 23, -190.5, 64


def lum(p):
    a = np.asarray(Image.open(p).convert("RGB"), dtype=float)
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def cell(tx, ty):
    return int(round(GRID_X0 + PITCH * tx)), int(round(GRID_Y0 + PITCH * ty))


def main(frame=FRAME):
    L = lum(frame)
    spec = json.load(open(SPEC))
    px, py = spec["player"]["x"], spec["player"]["y"]
    props = spec.get("props", [])
    if not props:
        print("no props declared — nothing to verify")
        return 0

    print("THE ROUTED CRITERION: orc work visible as standing objects IN THE LIT RADIUS")
    print("  station (%d,%d), §13.8's perceptual floor is %.1f\n" % (px, py, PERCEPTUAL_FLOOR))
    # ⚠ EVERY CELL OF THE FOOTPRINT, AND THE WORST ONE IS THE ANSWER — §12.2.
    #
    # This sampled the ANCHOR cell alone, which was right while every prop was 1x1 and became
    # wrong the moment §12.2 let a standing stone be two cells tall. The light falls off radially
    # from the station, so the far cell of a tall prop is always the darker one — and on the
    # exemplar the clause was written for, the marker's dressed face is IN that far cell. A 2x2
    # went three-quarters unchecked.
    #
    # Reporting the mean of the whole footprint would be worse than the anchor: it lets a bright
    # near cell carry a dark far one over the floor. The rule is the floor family's own — report
    # the WORST cell, every band — so the footprint passes only if its darkest cell passes.
    print("  tile    cell      footprint   worst cell   worst mean   lit?    tiles from station")
    dark = []
    for p in props:
        pw, ph = int(p.get("w", 1)), int(p.get("h", 1))
        worst, worst_cell = None, None
        for dy in range(ph):
            for dx in range(pw):
                sx, sy = cell(p["x"] + dx, p["y"] + dy)
                reg = L[max(0, sy):sy + PITCH, max(0, sx):sx + PITCH]
                if reg.size == 0:
                    continue
                m = float(reg.mean())
                if worst is None or m < worst:
                    worst, worst_cell = m, (p["x"] + dx, p["y"] + dy)
        if worst is None:
            worst, worst_cell = 0.0, (p["x"], p["y"])
        d = ((worst_cell[0] - px) ** 2 + (worst_cell[1] - py) ** 2) ** 0.5
        ok = worst > PERCEPTUAL_FLOOR
        if not ok:
            dark.append((p["tileId"], worst_cell[0], worst_cell[1], worst, d))
        print("  %-6d  (%2d,%2d)   %dx%-7d  (%2d,%2d)     %7.2f      %-5s   %.1f"
              % (p["tileId"], p["x"], p["y"], pw, ph,
                 worst_cell[0], worst_cell[1], worst, "LIT" if ok else "DARK", d))

    if dark:
        print("\n*** REFUSED — %d prop(s) are below the perceptual floor:" % len(dark))
        for tid, x, y, m, d in dark:
            print("      tile %d at (%d,%d): %.2f at %.1f tiles, floor is %.1f"
                  % (tid, x, y, m, d, PERCEPTUAL_FLOOR))
        print("    A prop in the dark cannot answer the criterion it was placed for. Move it")
        print("    inside the lit radius, or remove it — do NOT lower the floor.")
        return 1

    print("\nEVERY DECLARED PROP IS LIT. %d props, nearest %.1f tiles, furthest %.1f."
          % (len(props),
             min(((p["x"] - px) ** 2 + (p["y"] - py) ** 2) ** 0.5 for p in props),
             max(((p["x"] - px) ** 2 + (p["y"] - py) ** 2) ** 0.5 for p in props)))
    return 0


BLANK_TILE = 9899        # reserved: a 32x32 fully transparent tile, the "draw nothing" id
MIN_DREW_PX = 60         # device pixels a footprint must change to count as having drawn


def _blank_tile_path():
    return os.path.join(REPO, "src/Presentation/assets/tier1_ashlar",
                        "tier1_ashlar_%d.png" % BLANK_TILE)


def ensure_blank_tile():
    """The reserved transparent tile. Written if absent so the control is self-contained."""
    p = _blank_tile_path()
    if not os.path.exists(p):
        Image.new("RGBA", (32, 32), (0, 0, 0, 0)).save(p)
        return True
    return False


def blank_spec(spec):
    """The same scene with every prop's ids swapped for the blank — cells still marked."""
    out = json.loads(json.dumps(spec))
    for pp in out.get("props", []):
        pp["tileId"] = BLANK_TILE
        if "layout" in pp:
            pp["layout"] = [BLANK_TILE] * len(pp["layout"])
    out["_what"] = ["CONTROL, generated by verify_props.py --drew. Every prop is still declared, "
                    "still in place and still blocking, so every cell is marked and the floor "
                    "under it composes identically. Only the tile ids differ. Do not commit."]
    return out


def check_drew(frame, spec, control_png):
    """Every declared prop must change pixels inside its own footprint. Returns a list of misses."""
    a = np.asarray(Image.open(control_png).convert("RGB"), dtype=int)
    b = np.asarray(Image.open(frame).convert("RGB"), dtype=int)
    if a.shape != b.shape:
        raise SystemExit("control and frame differ in size — recapture both")
    changed = np.abs(a - b).max(axis=2) > 2

    print("\n  DID EACH PROP ACTUALLY DRAW? control = same scene, same marked cells, blank tiles")
    print("  tile    cell      footprint   px drawn   verdict")
    misses = []
    for pp in spec["props"]:
        pw, ph = int(pp.get("w", 1)), int(pp.get("h", 1))
        total = 0
        for dy in range(ph):
            for dx in range(pw):
                sx, sy = cell(pp["x"] + dx, pp["y"] + dy)
                reg = changed[max(0, sy):sy + PITCH, max(0, sx):sx + PITCH]
                total += int(reg.sum())
        ok = total >= MIN_DREW_PX
        if not ok:
            misses.append((pp["tileId"], pp["x"], pp["y"], total))
        print("  %-6d  (%2d,%2d)   %dx%-7d %8d   %s"
              % (pp["tileId"], pp["x"], pp["y"], pw, ph, total, "DREW" if ok else "*** NOTHING"))
    # ── WHAT CHANGES OUTSIDE A FOOTPRINT, AND WHY "ZERO" IS THE WRONG BAR ────────────────────
    #
    # The first version of this demanded that NOTHING change outside the declared cells, and the
    # first honest run reported 5,368 pixels that did. They are not contamination: a prop sprite
    # is drawn CENTRED on its cell, so it overflows into its neighbours by up to half a cell.
    # Measured on the props that pass §12.2 — every stray pixel lay within 32px of a footprint,
    # median 10px, none further.
    #
    # So the test is DISTANCE, not count. Overflow hugs the footprint; a control that moved
    # something it should not have — a light, a floor tile, a wall — puts changed pixels out in
    # the room. The bar is half a cell, which is exactly how far a centred sprite can reach.
    inside = np.zeros((changed.shape[0], changed.shape[1]), dtype=bool)
    for pp in spec["props"]:
        for dy in range(int(pp.get("h", 1))):
            for dx in range(int(pp.get("w", 1))):
                sx, sy = cell(pp["x"] + dx, pp["y"] + dy)
                inside[max(0, sy):sy + PITCH, max(0, sx):sx + PITCH] = True

    reach = PITCH // 2
    near = inside.copy()                       # dilate by `reach`, separably, without scipy
    for _ in range(reach):
        near[1:, :] |= near[:-1, :]
        near[:-1, :] |= near[1:, :]
        near[:, 1:] |= near[:, :-1]
        near[:, :-1] |= near[:, 1:]

    overflow = int((changed & ~inside & near).sum())
    far = int((changed & ~near).sum())
    print("  overflow beside a footprint (a centred sprite reaches %dpx): %d" % (reach, overflow))
    print("  changed FURTHER than %dpx from any footprint: %d %s"
          % (reach, far, "(clean)" if far == 0 else "<- the control moved something else"))
    if far:
        misses.append((-1, -1, -1, -far))
    return misses


def main_drew(frame):
    """Capture the blank-tile control, then require every prop to have drawn.

    §13.5 — this instrument demonstrates it can fail every time it runs, and not as a separate
    exercise: the control frame IS the failing case. It is the same scene with nothing painted,
    so running the check against the control instead of the build must report NOTHING for every
    prop. If it does not, the check is measuring something other than the sprite and its pass
    would mean nothing.
    """
    import subprocess
    import tempfile

    spec = json.load(io.open(SPEC, encoding="utf-8"))
    if not spec.get("props"):
        print("no props declared — nothing to verify")
        return 0

    made = ensure_blank_tile()
    if made:
        print("wrote the reserved blank tile %d; Godot must re-import before the control is "
              "captured" % BLANK_TILE)

    tmpdir = tempfile.mkdtemp(prefix="propsdrew-")
    ctl_spec = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes",
                            "_control_props_blank.json")
    io.open(ctl_spec, "w", encoding="utf-8").write(
        json.dumps(blank_spec(spec), indent=1, ensure_ascii=False) + "\n")
    ctl_png = os.path.join(tmpdir, "control.png")
    try:
        cmd = ["python3", os.path.join(REPO, "tools/tier0_harness/capture_corridor.py"),
               "--out", ctl_png,
               "--theme-config",
               "res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml",
               "--scene-spec",
               "src/Presentation/assets/tier0_harness/scenes/_control_props_blank.json",
               "--floor-overlays", "res://src/Presentation/assets/tier1_floors/MANIFEST.json",
               "--ashlar-floor", "res://src/Presentation/assets/tier1_ashlar/MANIFEST.json",
               "--boundary-wall", "res://src/Presentation/assets/tier1_walls/MANIFEST.json",
               "--wall-bindings", "res://src/Presentation/assets/tier1_bindings/MANIFEST.json",
               "--wall-cap", "res://src/Presentation/assets/tier1_cap/MANIFEST.json",
               "--void-ring", "1",
               "--log-out", os.path.join(tmpdir, "control.log")]
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        if not os.path.exists(ctl_png):
            print("CONTROL CAPTURE FAILED — cannot check drawing:\n" + r.stdout[-1500:],
                  file=sys.stderr)
            return 2

        misses = check_drew(frame, spec, ctl_png)

        # THE SELF-TEST, run every time: the control against itself must report NOTHING drawn.
        print("\n  §13.5 — the same check against the CONTROL, where nothing is painted:")
        selfmiss = check_drew(ctl_png, spec, ctl_png)
        if len(selfmiss) != len(spec["props"]):
            print("\n*** THE CHECK IS BROKEN: it reported %d of %d props drawing in a frame "
                  "with no sprites in it. Its pass does not count (§13.5)."
                  % (len(spec["props"]) - len(selfmiss), len(spec["props"])), file=sys.stderr)
            return 2
        print("    all %d report NOTHING, as they must — the check can fail."
              % len(spec["props"]))
    finally:
        if os.path.exists(ctl_spec):
            os.remove(ctl_spec)

    if misses:
        print("\n*** REFUSED — %d prop(s) DID NOT DRAW:" % len(misses))
        for tid, x, y, n in misses:
            if tid == -1:
                print("      the CONTROL IS NOT CLEAN: %d pixels changed far from any prop. "
                      "The blank swap moved something other than the sprites, so a pass here "
                      "would mean nothing." % (-n))
            else:
                print("      tile %d at (%d,%d): %d pixels changed against a blank control"
                      % (tid, x, y, n))
        print("    A prop that is declared, seated, lit and invisible passes every other check")
        print("    in this pass. That is the hole this exists to close.")
        return 1

    print("\n  EVERY DECLARED PROP DREW.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--drew" in sys.argv:
        raise SystemExit(main_drew(args[0] if args else FRAME))
    raise SystemExit(main(args[0] if args else FRAME))
