#!/usr/bin/env python3
"""A BUILD OFFERED FOR A NAMED WALK ASSERTS THAT WALK'S REQUIREMENTS BEFORE IT MAY INSTALL.

RULED (Rafe, 2026-09-05), after a build reached the handset for the #174 rig-energy walk and
could not perform it. Two defects, neither visible in any frame:

  1. the RIG panel exposed radius, falloff and ambient and NOT ENERGY — the one quantity #174
     moved and the one Ruling 56 re-opens. **The walk could not set what it could not touch.**
  2. the review marker named the tier-0 corridor junction under the STUB THEME, so the floor
     rendered in the magenta mock colour. **The wrong surface, not the corrected lamp on the
     real floor.**

⚠ THE FRAME CRITIC PASSED CORRECTLY AND IS NOT AT FAULT. It judges the DELIVERED FRAME and has
no view of panel wiring or marker contents — it never sees the handset at all. Its verdict was
about a desktop capture taken with the correct families on the command line. **This is a separate
MECHANICAL gate, not a critic change**, and conflating the two would weaken the critic to catch
something it structurally cannot see.

WHAT A WALK REQUIREMENT IS. Not "is the build good" — that is the critic's question and this
never asks it. It is: **does this artefact physically contain what the named walk must touch and
show.** A rig walk needs the knob and the real surface. A surface walk needs both families
composed with no mock. Anything else is a walk that ratifies nothing, which is worse than no walk
because it produces a verdict.

The check is on the ARTEFACT'S OWN INPUTS — the marker that will ship inside the app, and the
source the panel is built from — for the same reason `verify_on_device.sh` reads the commit off
the handset rather than trusting the operator: the thing that ships is the thing that is asked.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MARKER_TEMPLATE = os.path.join(REPO, "src/Presentation/assets/tier0_harness/REVIEW_BUILD.json.template")
PANEL = os.path.join(REPO, "src/Presentation/Map/ReviewRigPanel.cs")
LIGHTING = os.path.join(REPO, "src/Presentation/Map/ReviewLighting.cs")

# The families whose absence does not fail — it draws something plausible and wrong. Each maps to
# what the handset shows when the key is missing, because a refusal that does not say what the
# operator would have seen is a refusal they will override.
FAMILIES = {
    "ashlarFloor":   "the floor renders as the MAGENTA placeholder",
    "floorOverlays": "§12.1's plane-boundary occlusion silently disappears",
    "boundaryWall":  "the walls render as the tier-0 MAGENTA MOCKS",
    "wallBindings":  "the walls are bare — §7.1 answered with nothing, silently",
    "wallCap":       "the walls have no top surface",
}

STUB_THEMES = ("tile_themes_stub.yaml",)


def _has_knob(name, panel_path=None, lighting_path=None):
    """Does the RIG panel actually offer this row, and does the rig expose a setter for it?

    BOTH HALVES, because either alone is the bug that shipped. A panel row calling a property
    that does not exist would not compile; a property with no row compiles and is unreachable
    from the handset, which is exactly what happened to energy.
    """
    panel = open(panel_path or PANEL, errors="ignore").read()
    lighting = open(lighting_path or LIGHTING, errors="ignore").read()
    row = re.search(r'AddRow\(\s*_body\s*,\s*"%s"' % re.escape(name), panel) is not None
    setter = re.search(r"public float %s\s*\n\s*\{" % re.escape(name.capitalize()), lighting) is not None
    return row, setter


def check_rig_energy(m, src=None):
    """The §6.2.1 / Ruling 56 rig pass."""
    fails = []
    src = src or {}
    row, setter = _has_knob("energy", src.get("panel"), src.get("lighting"))
    if not setter:
        fails.append("the rig exposes no `Energy` property — ReviewLighting cannot set the lamp")
    if not row:
        fails.append("the RIG panel has no `energy` row — the walk cannot reach the value "
                     "Ruling 56 re-opens (#174)")
    # A rig walk is a judgement about light falling on a SURFACE. The stub theme's magenta is not
    # a surface, and a rig ratified against it is ratified against nothing.
    theme = m.get("themeConfig") or ""
    if any(t in theme for t in STUB_THEMES):
        fails.append("themeConfig is the tier-0 STUB THEME (%s) — the floor renders magenta, so "
                     "the lamp is being judged against a mock" % os.path.basename(theme))
    for key in ("ashlarFloor", "floorOverlays"):
        if not m.get(key):
            fails.append("marker `%s` is unset — %s" % (key, FAMILIES[key]))
    return fails


def check_surface(m, src=None):
    """The tier-one surface gate: both families composed, nothing mock."""
    fails = []
    theme = m.get("themeConfig") or ""
    if any(t in theme for t in STUB_THEMES):
        fails.append("themeConfig is the tier-0 STUB THEME (%s)" % os.path.basename(theme))
    for key, consequence in FAMILIES.items():
        if not m.get(key):
            fails.append("marker `%s` is unset — %s" % (key, consequence))
    return fails


WALKS = {
    "rig-energy": ("the §6.2.1 / Ruling 56 rig pass", check_rig_energy),
    "surface":    ("the tier-one surface gate", check_surface),
}


def main(argv):
    # --panel / --lighting drive the check against FIXTURE SOURCES rather than the working tree.
    # They exist so this gate can demonstrate it fails (§13.5, LOOP-PROCESS §4) against the exact
    # build that got past it on 2026-09-05 — the same reason frame_critic.py takes --history.
    src = {}
    args = []
    it = iter(argv[1:])
    for a in it:
        if a in ("--panel", "--lighting"):
            src[a[2:]] = next(it)
        else:
            args.append(a)
    path = args[0] if args else MARKER_TEMPLATE
    try:
        m = json.load(open(path))
    except Exception as e:
        print("WALK GATE: cannot read %s (%s) — the gate cannot pass on faith." % (path, e))
        return 1

    walk = m.get("walk")
    print("== WALK PRECONDITIONS — marker %s" % os.path.relpath(path, REPO))
    if not walk or walk == "none":
        print("   walk: none declared — this build is not offered for a walk, nothing asserted.")
        return 0
    if walk not in WALKS:
        print("   walk: %r is not a known walk. Known: %s" % (walk, ", ".join(sorted(WALKS))))
        print("\nREFUSING: a build cannot assert requirements nobody has written down.")
        return 1

    label, fn = WALKS[walk]
    fails = fn(m, src)
    print("   walk: %s — %s" % (walk, label))
    if not fails:
        print("   requirements present. This says the walk CAN BE PERFORMED, and nothing about")
        print("   whether the picture is any good — that is the frame critic's question.")
        return 0

    print("   MISSING %d:" % len(fails))
    for f in fails:
        print("     * %s" % f)
    print()
    print("REFUSING TO INSTALL — this build cannot perform the walk it is offered for.")
    print("A walk that cannot reach its value, or shows the wrong surface, ratifies nothing.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
