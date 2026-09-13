#!/usr/bin/env python3
"""Generate the 5 x 5 matrix: every archetype at every candidate, from its projected template.

    python3 tools/tier2_props/projection_generate.py [--only W,OL] [--seeds 1337,1338,1339]

METHOD, decided by the probes in gen/projection2/probes and sets (see projection_mesh.py):
  * geometry comes from the template — projection_mesh.render() at NATIVE 32px, upscaled x2
    NEAREST so the init image is already 2x2-quantised
  * generation is v2 /create-image-pixflux img2img at init_image_strength 150 — the value at
    which the probe held the side face and still drew a lock plate (200 held but stayed bland,
    90 lost the side)
  * NO forced palette. The first matrix (ledger rows 1-75) used the landed frame's crop as
    color_image and every material came back the same tan — limestone read as pine. That is the
    floor-mottle law (PR #173) arriving here: a LIT frame's colours are the rig, not the
    material. Materials are held by the description and the seeds instead, and the ΔE table
    measures whether they held.
  * a little grain in the template fill (GRAIN), because the remover ate the featureless W
    stone twice (hold 0.195) — a flat grey slab looks like background to it
  * one description per archetype, verbatim across candidates (projection_round2.MATERIALS)
  * three seeds per cell; the pick is by geometry HOLD against the template (silhouette IoU),
    then confirmed nameable by eye on the ordered sheet (projection_pick2.py)

Ledger: every call — accepted or refused — is a row in gen/projection2/raw/ledger.jsonl with its
redacted payload and the image on disk. Budget declared in the doc: 1,100 generations ceiling.
"""
import argparse
import os
import sys
import time

import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools/pixellab/probe_6_4"))
import projection_round2 as pr    # noqa: E402
import projection_mesh as pm      # noqa: E402
import v2_bitforge as v2          # noqa: E402

ENDPOINT = "/create-image-pixflux"
RAW = os.path.join(pr.GEN, "raw")          # matrix 2 (no palette); matrix 1 kept in raw_palette/
STYLE = os.path.join(pr.GEN, "style_landed_frame.png")
STRENGTH = 150
GRAIN = 6          # +- value noise on the init's fill, deterministic per cell
SUFFIX = (". Keep the exact shape, outline and faces of the input. Dungeon prop sprite, matte, "
          "worn, no glow, no cast shadow, transparent background.")


def call(payload, ledger, image_name, extra):
    """v2_bitforge.generate, but at this endpoint. Same ledger, same refusal capture."""
    t0 = time.time()
    row = {"image": None, "request": v2._redact(payload)}
    row.update(extra)
    img = None
    try:
        r = requests.post(v2.V2_BASE + ENDPOINT, headers=v2._headers(), json=payload, timeout=600)
        v2._check(r, payload)
        j = r.json()
        import base64, io, hashlib
        raw = base64.b64decode(j["image"]["base64"])
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        rel = image_name + ".png"
        img.save(os.path.join(ledger.dir, rel))
        row.update(verdict="OK", image=rel, image_sha256=hashlib.sha256(raw).hexdigest(),
                   out_size=list(img.size), usage=j.get("usage"),
                   seconds=round(time.time() - t0, 1))
    except v2.Refusal as e:
        row.update(verdict="REFUSED:" + e.classification, http_status=e.status,
                   reason=e.reason[:2000], seconds=round(time.time() - t0, 1))
    except Exception as e:
        row.update(verdict="ERROR:" + type(e).__name__, reason=str(e)[:2000],
                   seconds=round(time.time() - t0, 1))
    row["surface"] = "v2-http" + ENDPOINT
    ledger.write(row)
    return img, row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=",".join(pr.CANDIDATES))
    ap.add_argument("--arch", default=",".join(a[0] for a in pr.ARCHETYPES))
    ap.add_argument("--seeds", default="1337,1338,1339")
    a = ap.parse_args()
    cands = a.only.split(",")
    archs = a.arch.split(",")
    seeds = [int(s) for s in a.seeds.split(",")]
    os.makedirs(RAW, exist_ok=True)
    ledger = v2.Ledger(RAW)
    before = v2.pool(v2.balance())
    print("pool before: %s" % before)
    n_ok = n_bad = 0
    for cand in cands:
        for name, w, h, _, _ in pr.ARCHETYPES:
            if name not in archs:
                continue
            canvas = pr.canvas_for(name)
            native = pm.render(cand, name, canvas, zoom=0.5)
            import numpy as np
            arr = np.asarray(native).astype(int)
            rng = np.random.RandomState(abs(hash((cand, name))) % (2 ** 31))
            noise = rng.randint(-GRAIN, GRAIN + 1, size=arr.shape[:2] + (1,))
            op = arr[:, :, 3:4] > 0
            arr[:, :, :3] = np.clip(arr[:, :, :3] + noise * op, 0, 255)
            native = Image.fromarray(arr.astype(np.uint8))
            init = native.resize(canvas, Image.NEAREST)
            init.save(os.path.join(RAW, "init_%s_%s.png" % (cand, name)))
            for seed in seeds:
                out = "%s_%s_s%d" % (cand, name, seed)
                if os.path.exists(os.path.join(RAW, out + ".png")):
                    print("  have %s" % out)
                    continue
                payload = {
                    "description": pr.MATERIALS[name] + SUFFIX,
                    "image_size": {"width": canvas[0], "height": canvas[1]},
                    "init_image": v2.enc(init),
                    "init_image_strength": STRENGTH,
                    "no_background": True,
                    "text_guidance_scale": 8,
                    "seed": seed,
                }
                img, row = call(payload, ledger, out,
                                {"candidate": cand, "archetype": name, "seed": seed})
                if img is not None:
                    n_ok += 1
                    print("  %-18s OK  %s  %.0fs" % (out, row["out_size"], row["seconds"]))
                else:
                    n_bad += 1
                    print("  %-18s %s  %s" % (out, row["verdict"], row.get("reason", "")[:120]))
    after = v2.pool(v2.balance())
    print("pool after: %s   (%d ok, %d refused/error; unsettled bracket = lower bound)"
          % (after, n_ok, n_bad))


if __name__ == "__main__":
    main()
