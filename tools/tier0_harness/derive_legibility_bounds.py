#!/usr/bin/env python3
"""Derive a scene's ABSOLUTE legibility bounds from a capture of it on the ratified rig.

RULED (Rafe, 2026-09-07). Legibility used to ask *how dark is this point relative to the
brightest lit floor*. The reference cell clipped at 255, so it asked **how dark relative to the
ceiling** — and a highlight shoulder that left every declared-dark pixel BYTE-IDENTICAL made two
declarations fail, because only the denominator moved.

> **THE LAW: an instrument whose reference can saturate measures the ceiling, not the scene.**

The bound is now the delivered luminance a viewer can or cannot see (§13.8), declared per point.

## The derivation, and why it is this one

    bound_lum = reference_luminance_on_the_NULLED_build_at_the_ratified_rig x retired_ratio

with the retired ratios 0.12 (lit) and 0.10 (dark). That is algebraically the old test with the
denominator frozen at a known-good moment, so **every point's pass state is preserved exactly** on
the day of the swap. It changes what the guard MEANS without changing what it SAYS, which is the
only honest way to replace a live instrument: if the swap had also moved verdicts, nobody could
tell the re-definition from a re-tuning.

⚠ **NULLED, and at the RATIFIED rig, both load-bearing.** Nulled because a shouldered reference is
compressed and would bake the compression into the bound. Ratified because §6.2's re-derivation
rule means a bound taken against any other rig is a bound with a fuse in it.

## Usage

    derive_legibility_bounds.py <scene.json> <capture.log> [--write]

Without --write it prints what it would do. The log must be a capture OF THAT SCENE with the
shoulder nulled; the tool reads the reference luminance the engine printed and refuses if the log
does not carry one.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

RETIRED_LIT = 0.12
RETIRED_DARK = 0.10
REF_RE = re.compile(r"reference lum=([0-9.]+)")
PT_RE = re.compile(r"legibility\((-?\d+),(-?\d+)\) expect=(lit|dark)\s+(?:ratio|lum)=([0-9.]+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("log")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    txt = open(os.path.join(REPO, a.log), "rb").read().decode("utf8", "replace")
    refs = REF_RE.findall(txt)
    if not refs:
        raise SystemExit("no 'reference lum=' in %s — the tool cannot invent one." % a.log)
    if len(set(refs)) > 1:
        raise SystemExit("the log carries disagreeing reference values %s — which capture is it?"
                         % sorted(set(refs)))
    ref = float(refs[0])

    measured = {}
    for x, y, ex, v in PT_RE.findall(txt):
        measured[(int(x), int(y))] = (ex, float(v))

    sp = os.path.join(REPO, a.scene)
    d = json.load(open(sp))
    print("reference luminance on this capture: %.4f" % ref)
    print("%-10s %-5s %10s %10s  %s" % ("point", "want", "bound", "measured", "verdict"))
    for L in d.get("legibility", []):
        r = RETIRED_LIT if L["expect"] == "lit" else RETIRED_DARK
        bound = round(ref * r, 6)
        key = (L["x"], L["y"])
        got = measured.get(key)
        # the log prints a RATIO on a pre-swap capture and a LUM on a post-swap one; both are
        # accepted, and the ratio is converted with the same reference it was taken against.
        abs_meas = None
        if got:
            abs_meas = got[1] * ref if got[1] <= 1.5 and "ratio=" in txt.split("\n")[0] else got[1]
            if re.search(r"legibility\(%d,%d\)[^\n]*ratio=%s" % (key[0], key[1], re.escape(str(got[1]))), txt):
                abs_meas = got[1] * ref
        ok = "?" if abs_meas is None else (
            "ok" if ((abs_meas >= bound) if L["expect"] == "lit" else (abs_meas <= bound)) else "FAIL")
        print("(%2d,%2d)    %-5s %10.6f %10.4f  %s"
              % (L["x"], L["y"], L["expect"], bound, abs_meas if abs_meas is not None else -1, ok))
        L["bound_lum"] = bound
    if a.write:
        json.dump(d, open(sp, "w"), indent=2)
        print("\nwrote %s" % a.scene)
    else:
        print("\n(dry run — pass --write to apply)")


if __name__ == "__main__":
    main()
