#!/usr/bin/env python3
"""Tier 0 positive controls — prove the harness can FAIL.

ART-LOOP-PROCESS-v0 §4 / ART-BIBLE-v0 §13.5, inherited from the sibling project as Ruling 47:
NO INSTRUMENT'S PASS COUNTS UNTIL IT HAS DEMONSTRATED IT CAN FAIL. An instrument that cannot be
made to fail is decorative, and a green harness that cannot go red is worse than a red one.

Each control below plants a specific defect and asserts the harness NOTICES it. A control that
cannot be made to fail is reported as such and stops the run — it is never quietly downgraded.

  determinism   two unchanged captures are byte-identical; then alter one tile -> capture differs
  lighting      set light energy to zero -> capture visibly changes
  scene         point the floor role at a WALL tile id -> capture reflects it
  device        bundle id from Info.plist + build id + commit, verified INSTALLED not assumed

Every control prints the raw numbers it judged on. Nothing here reports a verdict without the
evidence that produced it.
"""
import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_corridor import REPO, read_config, capture, sha256, git_commit
from make_stub_tiles import (theme_yaml, write_png, solid,
                             FLOOR_PRIMARY, FLOOR_DARK, WALL_MASK_BASE)

from PIL import Image, ImageChops

STUB_DIR   = "src/Presentation/assets/tier0_harness/stub"
STUB_ROOT  = "res://src/Presentation/assets/tier0_harness/stub"
THEME_MAIN = "src/Presentation/assets/tier0_harness/tile_themes_stub.yaml"
EVIDENCE   = "tools/tier0_harness/evidence"
GODOT      = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
# The reference device, ART-BIBLE-v0 §4.1: iPhone SE. Named so the query cannot
# silently answer about some other attached device.
DEVICE_NAME = os.environ.get("TIER0_DEVICE", "Jiminy Cricket")


def hr(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def diff_stats(a_path, b_path):
    """How different are two captures? Returns (pct_pixels_differing, mean_abs_channel_delta)."""
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        return 100.0, 255.0
    d = ImageChops.difference(a, b)
    px = list(d.getdata())
    n = len(px)
    differing = sum(1 for p in px if p != (0, 0, 0))
    total = sum(p[0] + p[1] + p[2] for p in px)
    return 100.0 * differing / n, total / (n * 3.0)


def reimport():
    subprocess.run([GODOT, "--headless", "--path", REPO, "--import"],
                   capture_output=True, text=True, timeout=600)


def shoot(cfg, out_name, theme=THEME_MAIN, light_overrides=None):
    out = os.path.join(REPO, EVIDENCE, out_name)
    theme_res = theme if theme.startswith("res://") else "res://" + theme
    rc, log, _ = capture(out, theme_res, cfg, GODOT, light_overrides=light_overrides,
                         log_out=out.replace(".png", ".log"))
    if not os.path.exists(out):
        print(f"ABORT: capture failed for {out_name}", file=sys.stderr)
        print(log, file=sys.stderr)
        sys.exit(1)
    return out, log


# ---------------------------------------------------------------------------------------------


def control_determinism(cfg):
    hr("CONTROL 1 — DETERMINISM  (must be byte-identical; then must DIFFER when a tile changes)")

    a, _ = shoot(cfg, "det_run1.png")
    b, _ = shoot(cfg, "det_run2.png")
    ha, hb = sha256(a), sha256(b)
    print(f"run1 sha256: {ha}")
    print(f"run2 sha256: {hb}")
    print(f"byte_identical: {ha == hb}")
    same_ok = ha == hb
    if not same_ok:
        pct, mean = diff_stats(a, b)
        print(f"  NOT identical — {pct:.4f}% pixels differ, mean channel delta {mean:.4f}")

    print("\n-- now PLANT a defect: repaint ONE floor tile, expect the capture to CHANGE --")
    # ONE tile, written directly. An earlier version of this control shelled out to
    # make_stub_tiles.py, which regenerates ALL 27 tiles, and then restored only the single file
    # it had backed up — so it silently left the other 26 altered and poisoned every capture that
    # followed. It also meant the control was not testing what it said it was. Write one file,
    # restore one file.
    tile = os.path.join(REPO, STUB_DIR, f"tier0_stub_{FLOOR_DARK}.png")
    # FLOOR_DARK, not FLOOR_PRIMARY: this corridor is one tile wide, so FloorComposer marks every
    # floor cell Dark and floor_primary is never drawn. Altering it would change nothing.
    backup = tile + ".orig"
    shutil.copyfile(tile, backup)
    try:
        size = cfg["tile"]["size"]
        write_png(tile, size, solid(size, (255, 0, 0), (255, 255, 0)))
        print(f"planted: {os.path.relpath(tile, REPO)} repainted flat red")
        reimport()
        c, _ = shoot(cfg, "det_run3_altered_tile.png")
        hc = sha256(c)
        pct, mean = diff_stats(a, c)
        print(f"run3 sha256: {hc}")
        print(f"differs_from_run1: {hc != ha}")
        print(f"  {pct:.4f}% of pixels differ, mean channel delta {mean:.4f}")
        changed_ok = hc != ha
    finally:
        shutil.copyfile(backup, tile)
        os.remove(backup)
        reimport()
        # Prove the restore actually worked, rather than trusting it: recapture and compare to
        # run1. A control that leaves the tree dirty corrupts every later measurement.
        r, _ = shoot(cfg, "det_run4_restored.png")
        hr_ = sha256(r)
        print(f"\nrestore check — run4 sha256: {hr_}")
        print(f"  matches run1: {hr_ == ha}")
        if hr_ != ha:
            print("  WARNING: the tree was NOT restored to its pre-control state.")

    verdict = same_ok and changed_ok
    print(f"\nRESULT: {'PASS' if verdict else 'FAIL'} "
          f"(identical-when-unchanged={same_ok}, differs-when-altered={changed_ok})")
    return verdict


def control_lighting(cfg):
    hr("CONTROL 2 — LIGHTING IS LIVE  (energy 0 must visibly change the capture)")
    lit, _   = shoot(cfg, "light_on.png")
    unlit, _ = shoot(cfg, "light_off.png", light_overrides={"energy": "0.0"})

    h1, h2 = sha256(lit), sha256(unlit)
    pct, mean = diff_stats(lit, unlit)
    print(f"lit   sha256: {h1}")
    print(f"unlit sha256: {h2}")
    print(f"differ: {h1 != h2}")
    print(f"  {pct:.4f}% of pixels differ, mean channel delta {mean:.4f}")

    # A harness that captures the same image lit and unlit is not lighting anything. Require a
    # difference big enough to be a light rig rather than an encoder wobble.
    ok = (h1 != h2) and pct > 1.0
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — lighting is "
          f"{'live' if ok else 'NOT AFFECTING THE CAPTURE'}")
    return ok


def control_scene(cfg):
    hr("CONTROL 3 — SCENE IS REAL  (swap the floor tile for a WALL tile; capture must reflect it)")
    base, _ = shoot(cfg, "scene_normal.png")

    swapped_theme = os.path.join(REPO, "src/Presentation/assets/tier0_harness/tile_themes_swapped.yaml")
    with open(swapped_theme, "w") as f:
        # EVERY floor role now points at a WALL tile id — the floor should render as wall pixels.
        # Not just floor_primary: this corridor is one tile wide, so FloorComposer's edge-darkening
        # pass makes every floor cell Dark and floor_primary is never drawn. Swapping only
        # floor_primary planted the defect in a dead role and the control passed a swap through
        # with 0.0000% of pixels changed — which is exactly the failure this control exists to catch.
        f.write(theme_yaml(STUB_ROOT, "tier0_stub_{id}.png", floor_all_id=WALL_MASK_BASE))
    print(f"planted: ALL floor roles ({FLOOR_PRIMARY} etc) -> {WALL_MASK_BASE} (a wall tile) "
          f"in {os.path.relpath(swapped_theme, REPO)}")

    try:
        sw, _ = shoot(cfg, "scene_floor_is_wall.png",
                      theme="src/Presentation/assets/tier0_harness/tile_themes_swapped.yaml")
        h1, h2 = sha256(base), sha256(sw)
        pct, mean = diff_stats(base, sw)
        print(f"normal  sha256: {h1}")
        print(f"swapped sha256: {h2}")
        print(f"differ: {h1 != h2}")
        print(f"  {pct:.4f}% of pixels differ, mean channel delta {mean:.4f}")
        ok = (h1 != h2) and pct > 1.0
    finally:
        os.remove(swapped_theme)

    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — the scene "
          f"{'renders the tiles it is pointed at' if ok else 'IGNORED THE TILE SWAP'}")
    return ok


def control_device(cfg):
    hr("CONTROL 4 — DEVICE PATH  (bundle id from Info.plist, build id, commit — VERIFIED installed)")
    ok = True

    # WHERE THE BUNDLE ID ACTUALLY LIVES.
    #
    # There is no Info.plist in the repo — the first run of this control looked for one and found
    # zero candidates. Godot generates it at export time into the built .app, which lands OUTSIDE
    # the repo at the export_path in export_presets.cfg. So there are two sources and they must
    # agree: the DECLARED id (export_presets.cfg, in version control) and the BUILT id (the .app's
    # Info.plist, which is what actually got signed and installed). Reading only the first would
    # be assuming the build honoured it — which is the thing this control exists not to assume.
    declared = None
    presets = os.path.join(REPO, "export_presets.cfg")
    if os.path.exists(presets):
        for line in open(presets):
            if "application/bundle_identifier" in line:
                declared = line.split("=", 1)[1].strip().strip('"')
                break
    print(f"declared bundle id (export_presets.cfg): {declared}")
    if not declared:
        print("  NO declared bundle id — cannot proceed.")
        ok = False

    # WHERE THE BUILT .app ACTUALLY LANDS.
    #
    # NOT at export_presets.cfg's export_path: tools/ios_build.sh overrides the output root with
    # OUT="$ROOT/.ios-build" and drives xcodebuild into .ios-build/xcodeproj/dd/... So resolving
    # export_path pointed this control at a directory that never contains a build, and it
    # reported "NO built .app found" for a build that had just succeeded and installed.
    build_root = os.path.join(REPO, ".ios-build")
    print(f"build root: {build_root}  exists={os.path.isdir(build_root)}")
    found = []
    if os.path.isdir(build_root):
        found = subprocess.run(["find", build_root, "-maxdepth", "6", "-name", "*.app"],
                               capture_output=True, text=True).stdout.split()
    for f in found:
        print(f"  built app: {os.path.relpath(f, REPO)}")
    app = found[0] if found else None

    built_id = build_id = None
    if app:
        plist = os.path.join(app, "Info.plist")
        print(f"\nInfo.plist: {plist}  exists={os.path.exists(plist)}")
        if os.path.exists(plist):
            for key, label in (("CFBundleIdentifier", "built bundle id"),
                               ("CFBundleVersion", "build id (CFBundleVersion)"),
                               ("CFBundleShortVersionString", "short version")):
                r = subprocess.run(["/usr/libexec/PlistBuddy", "-c", f"Print :{key}", plist],
                                   capture_output=True, text=True)
                val = r.stdout.strip() if r.returncode == 0 else "(absent)"
                print(f"  {label}: {val}")
                if key == "CFBundleIdentifier":
                    built_id = val
                if key == "CFBundleVersion":
                    build_id = val
    else:
        print("\nNO built .app found — nothing was exported, so nothing can be verified installed.")
        ok = False

    # A REVIEW BUILD LEGITIMATELY OVERRIDES THE BUNDLE ID.
    #
    # build_review_app.sh passes --bundle-id com.<...>.tier0 so the review build installs beside
    # the real game instead of replacing it. An earlier version of this control compared the built
    # id to export_presets.cfg and flagged any difference as tampering, so it reported
    # "MISMATCH ... .tier0" for a build that was correct by design — it had only ever been
    # exercised against a normal build. The check still has to catch a genuinely unrelated id, so
    # what is accepted is the declared id or a dotted variant OF it, and which one was found is
    # reported rather than glossed.
    build_kind = None
    if declared and built_id:
        if built_id == declared:
            build_kind = "normal build"
        elif built_id.startswith(declared + "."):
            build_kind = f"review/variant build (suffix '{built_id[len(declared) + 1:]}')"
        else:
            print(f"\nMISMATCH: built id {built_id} is not {declared} nor a variant of it")
            ok = False
        if build_kind:
            print(f"\nbuild kind: {build_kind}")

    print(f"\ncommit: {git_commit()}")
    print(f"build id: {build_id}")

    print("\n-- devices actually attached --")
    dev = subprocess.run(["xcrun", "devicectl", "list", "devices"], capture_output=True, text=True)
    print(dev.stdout.strip() or "(no output)")

    # VERIFIED INSTALLED, not assumed: ask the device what it is carrying.
    installed = False
    target = built_id or declared
    if target:
        print("\n-- installed-app query on the device --")
        q = subprocess.run(
            ["xcrun", "devicectl", "device", "info", "apps", "--device", DEVICE_NAME,
             "--bundle-id", target],
            capture_output=True, text=True)
        out = (q.stdout + q.stderr).strip()
        print(out[:3000] or "(no output)")
        installed = q.returncode == 0 and target in q.stdout

    verdict = ok and installed
    detail = ("install VERIFIED on the connected device" if installed
              else "install NOT VERIFIED (see above)")
    if installed and not ok:
        # Do not let a verified install paper over a broken chain of evidence, and do not print a
        # verdict that contradicts its own reason — the first run of this control printed
        # "FAIL — install VERIFIED on the connected device", which is not a readable result.
        detail += ", but the build-artefact chain above did not check out"
    print(f"\nRESULT: {'PASS' if verdict else 'FAIL'} — {detail}")
    return verdict


def control_junction_lit(cfg):
    hr("CONTROL 5 — JUNCTION IS LIT  (shrink the light; a dark junction must BLOCK the capture)")

    # The MISFED guard. The junction is what makes the scene ask its question — the critic is asked
    # which way they would walk. Shrink the carried light and the junction falls outside its reach:
    # the capture still renders, still looks clean, and still passes determinism, while measuring
    # nothing. This control proves the harness refuses that capture instead of shipping it.
    working = cfg["light"]["radius_tiles"]

    print(f"-- GREEN: at the configured working radius ({working}) --")
    out = os.path.join(REPO, EVIDENCE, "junction_lit_green.png")
    rc, log, _ = capture(out, THEME_MAIN if THEME_MAIN.startswith("res://") else "res://" + THEME_MAIN,
                         cfg, GODOT, log_out=out.replace(".png", ".log"))
    for line in log.splitlines():
        if "junction-lit probe" in line and "DIAG" not in line:
            print("  " + line.strip())
    green_ok = rc == 0 and os.path.exists(out)
    print(f"  capture written: {os.path.exists(out)}  exit={rc}")

    print(f"\n-- PLANT: shrink light.radius_tiles below the point where the junction stays lit --")
    red_results = []
    for radius in ("3.5", "3.0"):
        dark = os.path.join(REPO, EVIDENCE, f"junction_lit_red_r{radius}.png")
        if os.path.exists(dark):
            os.remove(dark)
        rc2, log2, _ = capture(dark, THEME_MAIN if THEME_MAIN.startswith("res://") else "res://" + THEME_MAIN,
                               cfg, GODOT, light_overrides={"radius_tiles": radius})
        for line in log2.splitlines():
            if "DIAG" in line:
                continue
            if any(k in line for k in ("junction-lit probe", "JUNCTION-LIT CHECK FAILED",
                                       "CAPTURE REFUSED", "MISFED", "Fix:")):
                print("  " + line.strip())
        wrote = os.path.exists(dark)
        refused = (rc2 == 2) and not wrote
        print(f"  radius={radius}: engine exit={rc2}  capture written={wrote}  -> "
              f"{'REFUSED (correct)' if refused else 'NOT REFUSED'}")
        red_results.append(refused)

    ok = green_ok and all(red_results)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — the junction-lit check "
          f"{'blocks a dark junction and passes a lit one' if ok else 'DID NOT BEHAVE AS REQUIRED'}")
    return ok


CONTROLS = {
    "determinism": control_determinism,
    "lighting":    control_lighting,
    "scene":       control_scene,
    "device":      control_device,
    "junction":    control_junction_lit,
}


def main():
    ap = argparse.ArgumentParser(description="Run the Tier 0 positive controls")
    ap.add_argument("--only", choices=sorted(CONTROLS), nargs="*")
    args = ap.parse_args()

    os.makedirs(os.path.join(REPO, EVIDENCE), exist_ok=True)
    cfg = read_config()
    names = args.only or list(CONTROLS)

    results = {}
    for n in names:
        results[n] = CONTROLS[n](cfg)

    hr("SUMMARY")
    for n, v in results.items():
        print(f"  {n:<12} {'PASS' if v else 'FAIL'}")
    print(f"\ncommit: {git_commit()}")
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
