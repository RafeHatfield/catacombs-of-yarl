#!/usr/bin/env python3
"""B-KAB — CONDITIONED REGENERATION, because surgery deletes this tile rather than de-ringing it.

WHY THIS TILE AND NOT THE OTHERS
--------------------------------
`remediate.py` measures, per tile, whether the plate still separates from its ground once the
ring is gone. A-VAB measures +16.0 after surgery: the ring was redundant with a value separation
the tile already had, so stripping it removed a keyline and nothing else. B-KAB measures -1.4:
its plate and its ground are THE SAME VALUE and the near-black ring was the only thing making
the plate read at all. Stripping it does not de-ring B-KAB, it empties it. So B-KAB is
regenerated instead, conditioned on itself, per the session brief.

DECLARED BEFORE THE FIRST CALL — gauntlet clause §1.1.3, sessions are bounded by budget and
width, never by rounds and never by check-ins:

    BUDGET  24 generations, in 3 waves of 8. Spent below the bar -> report what conditioning
            could and could not do, with the ledger as evidence, and B-KAB stays un-remediated
            rather than being replaced by something that failed its own test.
    BAR     at least one child the ring instrument calls CLEAN, whose material is recognisably
            the parent's. The first half is mechanical and is decided here. THE SECOND HALF IS
            NOT DECIDED HERE - the seat gates it and Rafe's eye rules on it (§13.1, §13.2).

THE WAVES ARE A DESIGNED SEQUENCE, NOT A RETRY LOOP
---------------------------------------------------
  wave 1  the parent's own prompt, UNCHANGED, conditioned on the parent. Nothing added.
          This asks the question that is worth an answer whatever happens next: DOES THE RING
          PROPAGATE THROUGH THE CONDITIONING CHANNEL? The parent's prompt already carries
          `outline: lineless` and negatives for `outline, border, frame` - and the parent came
          out of it ringed anyway. Wave 1 measures whether conditioning on a ringed reference
          reproduces the ring on top of that.
  wave 2  + an explicit refusal of the specific construction, in the negative description.
  wave 3  + style_strength raised from 50 to 80.

RESULT, so the next reader does not have to re-run it: 7 of 8 ringed in EVERY wave. The refusal
moved nothing and the style_strength moved nothing. The ring is not a prompt-level defect on
this surface and it cannot be prompted away; screening is what catches it.

RUN ORDER - CHANGED MID-SESSION, AND THE REASON IS RECORDED RATHER THAN TIDIED AWAY
-----------------------------------------------------------------------------------
The first draft ran a wave only if the previous one had failed, so a cheap answer would not be
paid for twice. Wave 1 then cleared the bar with exactly ONE clean child out of eight, and that
exposed the flaw in the rule: the session returns to Rafe under a ruling trigger on character,
and handing him a single take is handing him a dead end rather than a re-curation. The budget
was declared at 24 and the pool holds 2858, so the remaining 16 were spent. Waves 2 and 3 also
answer a question worth more than this tile - whether an explicit refusal of the construction
raises the clean rate - and the ring will recur on every floor generated from here.

`--waves` selects which waves to run; results merge into the existing RESULT.json rather than
replacing it, so wave 1's eight generations are evidence, not something to be paid for twice.

RULING - 2026-08-27, AFTER THIS MODULE RAN
------------------------------------------
**B-KAB retires from conditioning with no remediation. The candidate is NOT promoted.** 22 of 24
children came back ringed, and the blind seat culled the best clean one `keyline`. Promotion is
therefore off by default and requires `--promote`; the 24 children stay here as evidence and
none of them becomes the corpus's B-KAB. Bible §5.5 carries the corpus assignment.

SELECTION - AND WHAT THIS FILE REFUSES TO DO
--------------------------------------------
The instrument CULLS: a child carrying a ring is out, mechanically, no discussion. Among the
children that survive, this file computes a material-proximity ordering to the parent and
nothing else. Bible §13.2, verbatim on the idiom being reused here: the measure "is
uncalibrated, renders no verdict, and only decides ordering. No pass or fail is drawn on the
screen. The eye rules."

So: no child is approved here. The top-ordered clean child enters the remediated set as a
CANDIDATE for the seat, and every clean child goes to the gate, not just the one.

MECHANICS THAT WILL BITE IF FORGOTTEN (from conditioning_smoke.py, banked)
--------------------------------------------------------------------------
  * `style_image` must EQUAL the generation size or the server returns a hard HTTP 500. B-KAB is
    32x32 native and generation is 32x32. Nothing here resizes, and nothing should.
  * `style_strength` defaults to 0, at which a reference does nothing at all. Set explicitly.
  * `client_compat.generate_image_bitforge` cannot carry a style_image (#140). This routes
    through `v2_bitforge`, which hand-encodes `Base64Image`.
  * No surface here is seed-reproducible. Seeds are recorded, never relied on; the ledger
    stores images.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROBE = os.path.join(REPO, "tools/pixellab/probe_6_4")
sys.path.insert(0, HERE)
sys.path.insert(0, PROBE)
import ring_instrument as RI      # noqa: E402
import v2_bitforge as v2          # noqa: E402

SURVIVORS = os.path.join(PROBE, "survivors")
PROMPTS = os.path.join(PROBE, "prompts")
OUT = os.path.join(HERE, "regen_bkab")
REMEDIATED = os.path.join(HERE, "remediated")
CODE = "B-KAB"

WAVE_SIZE = 8
BUDGET = 24

# §12.1's construction, refused in the parent's own vocabulary. Added in wave 2 only, so wave 1
# can answer whether the ring propagates without this confounding it.
RING_REFUSAL = (", keyline, dark ring around the tile, black border around the slab, inset "
                "panel, framed square, square outline inside the tile, plate on a background")


def material_distance(child, parent):
    """Uncalibrated ordering only. Renders no verdict (bible §13.2).

    Two terms, both about material rather than composition: how much of the child's colour mass
    lands on colours the parent used, and how far the child's value histogram sits from the
    parent's. Composition is deliberately not measured - that is the eye's, and a composition
    metric here would be a proxy for a register clause (§13.4).
    """
    ppal = set(map(tuple, parent.reshape(-1, 3).tolist()))
    cpx = list(map(tuple, child.reshape(-1, 3).tolist()))
    shared = sum(1 for c in cpx if c in ppal) / float(len(cpx))
    hp, _ = np.histogram(RI.lum(parent.astype(float)), bins=16, range=(0, 255), density=True)
    hc, _ = np.histogram(RI.lum(child.astype(float)), bins=16, range=(0, 255), density=True)
    hist = float(np.abs(hp - hc).sum()) / 2.0
    return dict(palette_overlap=round(shared, 4), hist_distance=round(hist, 4),
                order_key=round(hist - shared, 4))


def _record_retirement(results, clean, ringed):
    """Write the honest state into the remediated manifest: B-KAB has NO remediation.

    The row must exist and must say so. A code silently absent from the manifest reads as an
    oversight; a row saying "retired, no remediation, and here is what was tried" is the record.
    """
    mp = os.path.join(REMEDIATED, "MANIFEST.json")
    if not os.path.exists(mp):
        return
    man = json.load(open(mp))
    for row in man["floors"]:
        if row["code"] != CODE:
            continue
        for k in ("sha256", "pixels_changed", "strips", "verdict_after", "rings_after",
                  "generation", "surgery_rejected", "pixels_shared_with_parent", "method"):
            row.pop(k, None)
        row["route"] = "retired-no-remediation"
        row["file"] = None
        row["ruling"] = ("RULED (Rafe, 2026-08-27): B-KAB retires from conditioning. No "
                         "remediation. The candidate is not promoted and the un-remediated "
                         "original stays in the ledger. Bible §5.5 corpus status.")
        row["surgery_rejected"] = ("plate and ground are the same value (-1.1); stripping the "
                                   "ring empties the tile rather than de-ringing it")
        row["regeneration_attempted"] = dict(
            budget=BUDGET, generations=len(results), ringed=len(ringed), clean=len(clean),
            clean_children=[r["file"] for r in clean],
            outcome=("the blind seat culled the best clean child `keyline`; no child is "
                     "promoted"),
            evidence="tools/floor_remediation/regen_bkab/")
    man["note_bkab"] = ("B-KAB has NO remediation. Retired from conditioning by ruling "
                        "2026-08-27. Its 24 children stay in regen_bkab/ as evidence; none is "
                        "the corpus's B-KAB. See REPORT.md §4 and §9.")
    with open(mp, "w") as f:
        json.dump(man, f, indent=1)


def wave_payload(base, wave, ref_b64):
    p = dict(base)
    if wave >= 2:
        p["negative_description"] = base["negative_description"] + RING_REFUSAL
    p["style_image"] = ref_b64
    p["style_strength"] = 50 if wave < 3 else 80
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and the payload shape, spend nothing")
    ap.add_argument("--waves", default="1,2,3",
                    help="which waves to run; results merge into the existing RESULT.json")
    ap.add_argument("--promote", action="store_true",
                    help="copy the top-ordered clean child into remediated/. OFF BY DEFAULT "
                         "since the 2026-08-27 ruling: B-KAB is retired from conditioning with "
                         "no remediation and its candidate is not promoted. See the RULING "
                         "block in this module's docstring.")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    parent_path = os.path.join(SURVIVORS, CODE + ".png")
    parent = np.array(Image.open(parent_path).convert("RGB")).astype(int)
    ref = Image.open(parent_path).convert("RGB")

    subj = json.load(open(os.path.join(PROMPTS, "subject_floor.json")))
    arm = json.load(open(os.path.join(PROMPTS, "arm_B.json")))
    base = dict(subj["parameters"])
    base.update(arm["parameters"])
    base["description"] = subj["description"] + " " + arm["lighting"]
    base["negative_description"] = subj["negative_description"]

    if ref.size != (base["image_size"]["width"], base["image_size"]["height"]):
        print("REFUSING: reference is %s, generation is %s. The server rejects a mismatch with a"
              " hard 500 and nothing here resizes a reference." % (ref.size, base["image_size"]))
        return 2

    v_parent, rings_parent = RI.verdict(parent)
    print("B-KAB CONDITIONED REGENERATION")
    print("parent:   %s  instrument says %s (%d loop findings)"
          % (os.path.relpath(parent_path, REPO), v_parent, len(rings_parent)))
    print("arm:      B (the parent's own arm)   reference: the parent itself, 32x32, unresized")
    print("budget:   %d generations, %d waves of %d" % (BUDGET, BUDGET // WAVE_SIZE, WAVE_SIZE))
    print("bar:      at least one child the instrument calls CLEAN")
    print("NOTE:     the parent's prompt ALREADY carries outline:lineless and negatives for")
    print("          'outline, border, frame' - and the parent came out ringed anyway.\n")

    if args.dry_run:
        p = wave_payload(base, 1, "<base64 32x32>")
        print("wave-1 payload keys: %s" % sorted(p))
        print("style_strength=%s  shading=%s  outline=%s"
              % (p["style_strength"], p.get("shading"), p.get("outline")))
        print("\n--dry-run: nothing spent.")
        return 0

    led = v2.Ledger(OUT)
    want_now = [int(w) for w in args.waves.split(",") if w.strip()]
    if want_now:
        before, stable_b = v2.settled_pool()
        led.write({"claim": "regen:pool_before", "verdict": "INFO", "pool": before,
                   "settled": stable_b, "budget": BUDGET, "target": CODE})
        print("pool before: %s (settled=%s)\n" % (before, stable_b))
    else:
        before = None
        print("no waves selected - re-deriving the promotion from the existing ledger, "
              "spending nothing.\n")

    ref_b64 = v2.enc(ref)
    want = [int(w) for w in args.waves.split(",") if w.strip()]
    prior = {}
    rp = os.path.join(OUT, "RESULT.json")
    if os.path.exists(rp):
        prior = json.load(open(rp))
    results = [r for r in prior.get("results", []) if r["wave"] not in want]
    spent = 0
    for wave in (1, 2, 3):
        if wave not in want:
            continue
        if spent >= BUDGET:
            break
        note = {1: "the parent's prompt UNCHANGED - does the ring propagate?",
                2: "+ explicit refusal of the ring construction",
                3: "+ style_strength 80"}[wave]
        print("== WAVE %d ==  %s" % (wave, note))
        for i in range(WAVE_SIZE):
            if spent >= BUDGET:
                break
            seed = 9300 + wave * 100 + i
            p = wave_payload(base, wave, ref_b64)
            p["seed"] = seed
            name = "w%d_seed%d" % (wave, seed)
            img, row = v2.generate(p, led, name, image_subdir="w%d" % wave,
                                   claim="regen:%s:w%d:%d" % (CODE, wave, seed),
                                   extra={"target": CODE, "wave": wave, "seed_used": seed,
                                          "style_strength": p["style_strength"],
                                          "reference": CODE})
            spent += 1
            if img is None:
                print("   seed %d  %s" % (seed, row["verdict"]))
                results.append(dict(wave=wave, seed=seed, verdict=row["verdict"], file=None))
                continue
            child = np.array(img.convert("RGB")).astype(int)
            v, rings = RI.verdict(child)
            prox = material_distance(child, parent)
            rel = row["image"]
            print("   seed %d  %-5s  palette_overlap %.3f  hist_dist %.3f%s"
                  % (seed, v, prox["palette_overlap"], prox["hist_distance"],
                     "" if v == "CLEAN" else "   <- carries a ring, culled"))
            for r in rings[:1]:
                print("        %s %s  wall=%dpx interior=%dpx width=%.2f+-%.2f"
                      % (r["kind"], r["level"], r["contour_px"], r["interior_px"],
                         r["wall_thickness"], r["wall_thickness_spread"]))
            results.append(dict(wave=wave, seed=seed, verdict=v, file=rel,
                                sha256=row.get("image_sha256"), rings=RI.public(rings), **prox))
        n_clean = sum(1 for r in results if r["wave"] == wave and r["verdict"] == "CLEAN")
        print("   wave %d: %d/%d clean\n" % (wave, n_clean, WAVE_SIZE))

    if want_now:
        after, stable_a = v2.settled_pool()
        led.write({"claim": "regen:pool_after", "verdict": "INFO", "pool": after,
                   "settled": stable_a, "generations": spent})
    else:
        after = prior.get("pool_after")

    # Re-screen every child on disk rather than trusting a stored verdict. The instrument was
    # corrected mid-session (side_coverage replaced topological closure, and criterion 4 replaced
    # a border test), and a verdict recorded by a superseded instrument is not evidence.
    for r in results:
        if r.get("file"):
            child = np.array(Image.open(os.path.join(OUT, r["file"])).convert("RGB")).astype(int)
            v, rings = RI.verdict(child)
            r["verdict"], r["rings"] = v, RI.public(rings)
    clean = [r for r in results if r["verdict"] == "CLEAN"]
    ringed = [r for r in results if r["verdict"] == "RING"]
    print("RESULT")
    print("  generations: %d of %d budgeted   pool %s -> %s" % (spent, BUDGET, before, after))
    print("  clean: %d    ringed: %d    refused/error: %d"
          % (len(clean), len(ringed), len(results) - len(clean) - len(ringed)))
    print("\n  DOES THE RING PROPAGATE THROUGH THE CONDITIONING CHANNEL?")
    for w, label in ((1, "parent's prompt UNCHANGED"),
                     (2, "+ explicit ring refusal"),
                     (3, "+ refusal, style_strength 80")):
        ws = [r for r in results if r["wave"] == w and r["verdict"] in ("CLEAN", "RING")]
        if ws:
            print("  wave %d (%-28s): %d of %d ringed, %d clean"
                  % (w, label, sum(1 for r in ws if r["verdict"] == "RING"), len(ws),
                     sum(1 for r in ws if r["verdict"] == "CLEAN")))

    promoted = None
    if clean and not args.promote:
        clean.sort(key=lambda r: r["order_key"])
        print("\n  NOT PROMOTED - RULED (Rafe, 2026-08-27): B-KAB retires from conditioning")
        print("  with no remediation. %d clean children exist and stay here as evidence; none"
              % len(clean))
        print("  becomes the corpus's B-KAB. The un-remediated original stays in the ledger.")
        for r in clean:
            print("    %-16s palette_overlap %.3f  hist_dist %.3f"
                  % (os.path.basename(r["file"]), r["palette_overlap"], r["hist_distance"]))
        stale = os.path.join(REMEDIATED, CODE + ".png")
        if os.path.exists(stale):
            os.remove(stale)
            print("  removed a previously-promoted %s.png from remediated/" % CODE)
        _record_retirement(results, clean, ringed)
    elif clean:
        clean.sort(key=lambda r: r["order_key"])
        promoted = clean[0]
        src = os.path.join(OUT, promoted["file"])
        dst = os.path.join(REMEDIATED, CODE + ".png")
        # The generator returns RGBA; the originals and the tile loader are RGB. A floor tile is
        # opaque by construction (no_background: false) so the alpha must be solid - assert it
        # rather than flatten a hole silently, because a transparent floor tile is a real defect.
        im = Image.open(src)
        if im.mode == "RGBA":
            alpha = np.array(im)[..., 3]
            assert int(alpha.min()) == 255, \
                "clean child has transparent pixels - a floor tile must be opaque"
            im = im.convert("RGB")
        im.save(dst)
        # The remediated MANIFEST was written by remediate.py describing its SURGERY output for
        # this code. The file on disk is now a regenerated child instead, so the row must be
        # rewritten or the manifest misstates provenance - it would claim 62 stripped pixels for
        # a tile that shares none with its parent.
        mp = os.path.join(REMEDIATED, "MANIFEST.json")
        if os.path.exists(mp):
            man = json.load(open(mp))
            child = np.array(Image.open(dst).convert("RGB")).astype(int)
            v_child, rings_child = RI.verdict(child)
            for row in man["floors"]:
                if row["code"] != CODE:
                    continue
                row["route"] = "regenerated"
                row["method"] = ("conditioned on the parent itself; surgery was measured to "
                                 "empty this tile and was rejected")
                row["surgery_rejected"] = dict(
                    reason="plate/ground value separation with the ring gone was below the floor",
                    pixels_that_would_have_been_stripped=row.pop("pixels_changed", None),
                    strips=row.pop("strips", None))
                row["generation"] = dict(
                    source_file=os.path.relpath(src, REPO), wave=promoted["wave"],
                    seed_recorded=promoted["seed"], seed_reproducible=False,
                    style_strength=50 if promoted["wave"] < 3 else 80,
                    budget=BUDGET, generations_screened=len(results),
                    generations_ringed=len(ringed),
                    palette_overlap_with_parent=promoted["palette_overlap"],
                    ordering="uncalibrated, renders no verdict (bible §13.2)")
                row["sha256"] = RI.sha256(dst)
                row["pixels_shared_with_parent"] = int(
                    (child == np.array(Image.open(os.path.join(SURVIVORS, CODE + ".png"))
                                       .convert("RGB")).astype(int)).all(-1).sum())
                row["verdict_after"] = v_child
                row["rings_after"] = RI.public(rings_child)
            man["note_bkab"] = ("B-KAB is a REGENERATED CANDIDATE, not a derivation of its "
                                "parent. It shares no pixels with the survivor and the blind "
                                "seat culled it. See REPORT.md §4 and §7.")
            with open(mp, "w") as f:
                json.dump(man, f, indent=1)
        print("\n  ORDERING (uncalibrated, no verdict drawn - bible §13.2):")
        for r in clean:
            print("    %-16s palette_overlap %.3f  hist_dist %.3f  key %+.4f%s"
                  % (os.path.basename(r["file"]), r["palette_overlap"], r["hist_distance"],
                     r["order_key"], "   <- placed in the remediated set" if r is promoted else ""))
        print("\n  %s -> %s" % (os.path.relpath(src, REPO), os.path.relpath(dst, REPO)))
        print("  This is a CANDIDATE. Nothing here approved it. Every clean child above goes to")
        print("  the gate, not only this one.")
    else:
        print("\n  BAR NOT CLEARED. B-KAB is NOT replaced. The un-remediated original stays in")
        print("  the ledger and the finding goes to the gate intact.")

    with open(rp, "w") as f:
        json.dump(dict(target=CODE, budget=BUDGET,
                       spent=spent + prior.get("spent", 0), commit=v2.git_commit(),
                       pool_before=prior.get("pool_before", before), pool_after=after,
                       parent_sha256=RI.sha256(parent_path),
                       results=sorted(results, key=lambda r: (r["wave"], r["seed"])),
                       promoted=promoted), f, indent=1)
    print("\n-> %s" % os.path.relpath(OUT, REPO))
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
