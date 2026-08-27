#!/usr/bin/env python3
"""TIER ONE, SESSION ONE — the generation waves for the Boundary floor family.

WHAT THIS BUYS, AND WHAT IT DELIBERATELY DOES NOT
-------------------------------------------------
Bible §13.7, MEASURED, not argued: *"Architecture and conditioning do not exist on the same
surface. BitForge conditions (12/12 propagation, §5.5) and produced architecture 0/100 ...
Any pipeline needing both composes across surfaces."*

This module is the conditioning surface. It buys **material** — colour, value distribution,
grain, joint character — and nothing else. The **architecture** (a seamless irregular bond,
phase-offset between variants, joints that continue into the neighbour) is laid by
`compose_family.py` on the other surface. Spending this budget on architecture is the move the
platform fact says returns 0/100, and it is not attempted.

THE TWO WAVES ARE DIFFERENT OBJECTS, PER §8.3
---------------------------------------------
    base      `prompts/base_material.json`      opaque, full-bleed, INCIDENT-FREE, C-GAB-conditioned
    overlay   `prompts/incident_overlay.json`   transparent decals, INCIDENT IS THE POINT, unconditioned

The vocabulary one refuses is the vocabulary the other requests. That is §8.3's division, not a
contradiction: *a tile is the material, the incident is the variant.*

DECLARED BEFORE THE FIRST CALL — gauntlet clause §1.1.3, bounded by budget and width, never by
rounds and never by check-ins:

    BUDGET    120 generations for the whole session.
                base     40   one wave, C-GAB, style_strength 50
                overlay  32   four families of 8, unconditioned
                reserve  48   held for the gauntlet's own re-runs (§1.1.2: a critic FAIL is a
                              reprompt, not a stop) and for a family that comes back short
    LEVERS    style_strength 50, held — the value the B-KAB(24) and C-GAB(20) parent-rate runs
              held, so this wave's ring rate is comparable to the 5/20 they measured. This is
              material acquisition, not a lever search.
    SCREEN    every child, mechanically: `ring_instrument.py` (constants untouched) plus this
              session's `incident_instrument.py`. Seat spot-check on the borderline band at the
              rate REPORT-PARENT-RATE.md measured (near-ring >= 0.60).
    LEDGER    every call — accepted, rejected, refused — with its full redacted payload, because
              no surface here is seed-reproducible and an image is not re-derivable from
              (prompt, seed). AUDIT-FINDINGS column 2.
    REFUSALS  conditions on C-GAB ONLY. Not A-HEB (UNMEASURED as a parent, §8.2.1 item 4 — this
              session declines to spend 20 generations measuring it and declines to use it under
              an unknown-rate marker). Not B-KAB (retired, no remediation). Not A-VAB (prop
              stock; the ruling holds regardless of surgery). No constant in `ring_instrument.py`
              is altered. No lever is tuned toward a nicer number.
"""
import argparse
import hashlib
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROBE = os.path.join(REPO, "tools/pixellab/probe_6_4")
sys.path.insert(0, PROBE)
import v2_bitforge as v2      # noqa: E402

PROMPTS = os.path.join(HERE, "prompts")
SURVIVORS = os.path.join(PROBE, "survivors")
OUT = os.path.join(HERE, "gen")

# C-GAB — §5.5 RULED primary style parent, 2026-08-27. sha pinned so a swapped reference
# cannot pass silently; LOOP-PROCESS §2.3, evidence carries its producer's hash.
PARENT = "C-GAB"
PARENT_SHA = "1a24a59aa5607c3beebd8d1cf728acc0f43d6fc0bace6015025a7595c3f6db4f"
STYLE_STRENGTH = 50

WAVES = {
    "base": dict(n=40, seed0=13370, prompt="base_material.json", conditioned=True),
    "overlay": dict(n=32, seed0=14370, prompt="incident_overlay.json", conditioned=False),
}


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def base_payload(spec):
    """The prompt file's own fields, assembled. No local edits — a prompt is an auditable file
    with clause provenance (LOOP-PROCESS §12), not a string built here."""
    p = dict(spec["parameters"])
    p["description"] = spec["description"]
    p["negative_description"] = spec["negative_description"]
    return p


def overlay_payload(spec, fam):
    p = dict(spec["parameters"])
    p["description"] = fam["description"]
    p["negative_description"] = spec["negative_description"]
    return p


def run_base(led, n, seed0, dry):
    spec = json.load(open(os.path.join(PROMPTS, "base_material.json")))
    ref_path = os.path.join(SURVIVORS, "C-GAB.png")
    got = sha256_file(ref_path)
    if got != PARENT_SHA:
        raise SystemExit("REFUSING: %s sha256 %s != pinned %s. The conditioning parent is not "
                         "the tile this session declared." % (ref_path, got, PARENT_SHA))
    ref = Image.open(ref_path).convert("RGBA")
    base = base_payload(spec)
    if ref.size != (base["image_size"]["width"], base["image_size"]["height"]):
        raise SystemExit("REFUSING: reference %s vs generation %s; the server 500s on a mismatch "
                         "and nothing here resizes a reference." % (ref.size, base["image_size"]))
    if dry:
        print("base: n=%d  ref=%s(%s)  strength=%d" % (n, PARENT, got[:12], STYLE_STRENGTH))
        print(json.dumps({k: v for k, v in base.items() if k != "description"}, indent=1))
        return 0

    ref_b64 = v2.enc(ref)
    spent = 0
    for i in range(n):
        seed = seed0 + i
        p = dict(base)
        p["style_image"] = ref_b64
        p["style_strength"] = STYLE_STRENGTH
        p["seed"] = seed
        img, row = v2.generate(
            p, led, "base_%04d" % seed, image_subdir="base",
            claim="tier1_floors:base:%d" % seed,
            extra={"wave": "base", "parent": PARENT, "parent_sha256": got,
                   "style_strength": STYLE_STRENGTH, "seed_used": seed})
        spent += 1
        print("  base seed %d  %s" % (seed, row["verdict"]))
    return spent


def run_overlay(led, seed0, dry):
    spec = json.load(open(os.path.join(PROMPTS, "incident_overlay.json")))
    spent = 0
    seed = seed0
    for fam in spec["families"]:
        p0 = overlay_payload(spec, fam)
        if dry:
            print("overlay/%s: n=%d  no_background=%s" % (fam["family"], fam["n"],
                                                          p0.get("no_background")))
            seed += fam["n"]
            continue
        print("== family %s ==" % fam["family"])
        for i in range(fam["n"]):
            p = dict(p0)
            p["seed"] = seed
            img, row = v2.generate(
                p, led, "%s_%04d" % (fam["family"], seed), image_subdir="overlay/" + fam["family"],
                claim="tier1_floors:overlay:%s:%d" % (fam["family"], seed),
                extra={"wave": "overlay", "family": fam["family"], "conditioned": False,
                       "seed_used": seed})
            spent += 1
            print("  %s seed %d  %s" % (fam["family"], seed, row["verdict"]))
            seed += 1
    return spent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", choices=sorted(WAVES), required=True)
    ap.add_argument("--n", type=int, help="override the declared width (recorded in the ledger)")
    ap.add_argument("--seed0", type=int, help="override the declared seed base (for a re-run)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    w = WAVES[a.wave]
    n = a.n or w["n"]
    seed0 = a.seed0 if a.seed0 is not None else w["seed0"]

    os.makedirs(OUT, exist_ok=True)
    led = v2.Ledger(OUT)

    if a.dry_run:
        print("-- DRY RUN: nothing spent --")
        return run_base(led, n, seed0, True) if a.wave == "base" else run_overlay(led, seed0, True)

    before, stable_b = v2.settled_pool()
    led.write({"claim": "tier1_floors:declaration", "verdict": "INFO", "wave": a.wave,
               "n": n, "seed0": seed0, "pool": before, "settled": stable_b,
               "session_budget": 120, "wave_budget": w["n"],
               "conditioned_on": PARENT if w["conditioned"] else None,
               "parent_sha256": PARENT_SHA if w["conditioned"] else None,
               "style_strength": STYLE_STRENGTH if w["conditioned"] else None,
               "refusals": ["A-HEB: UNMEASURED as a parent (§8.2.1 item 4)",
                            "B-KAB: retired from conditioning (§5.5)",
                            "A-VAB: prop stock, never a conditioning parent (§5.5)"]})
    print("pool before: %s (settled=%s)\n" % (before, stable_b))

    spent = run_base(led, n, seed0, False) if a.wave == "base" else run_overlay(led, seed0, False)

    after, stable_a = v2.settled_pool()
    led.write({"claim": "tier1_floors:pool_after", "verdict": "INFO", "wave": a.wave,
               "pool": after, "settled": stable_a, "generations": spent})
    print("\nspent %d   pool %s -> %s (settled=%s)" % (spent, before, after, stable_a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
