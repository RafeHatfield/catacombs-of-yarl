#!/usr/bin/env python3
"""Order a Pro candidate set against its projection template — the pick is by instrument first.

    python3 tools/tier2_props/projection_pick.py <cand> <archetype> <urls.json|url ...>

Pro returns a SET (16 at 64px, 4 at 128px). Choosing one by eye alone from a contact sheet is
the §13.1 failure in miniature, so the set is ORDERED by how far each candidate's silhouette is
from the template's own measured geometry — signed top-edge shear (which side recedes, and how
much) and symmetry — and the ordered sheet is what a human then looks at, to confirm the top
pick is a nameable object and not a well-shaped blob. The template is measured by the same code
as the candidates, so the target is not a hand-typed number.

Ledger: every candidate is saved (gen/projection2/sets/<cand>_<arch>/NN.png) with the job id and
the measurements, because no surface here is seed-reproducible and an unsaved candidate is
unrecoverable evidence.
"""
import io
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import projection_round2 as pr    # noqa: E402

SETS = os.path.join(pr.GEN, "sets")


def fetch(url):
    with urllib.request.urlopen(url) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def measure(im):
    a = np.asarray(im)
    op = a[:, :, 3] > 0
    if op.sum() == 0:
        return dict(symmetry=0.0, shear=0.0, opaque=0.0)
    return dict(symmetry=pr.symmetry(op), shear=pr.signed_shear(op),
                opaque=float(op.mean()))


def main():
    cand, arch = sys.argv[1], sys.argv[2]
    srcs = sys.argv[3:]
    if len(srcs) == 1 and srcs[0].endswith(".json"):
        j = json.load(open(srcs[0]))
        urls = j["urls"] if isinstance(j, dict) else j
        job = j.get("job_id", "") if isinstance(j, dict) else ""
    else:
        urls, job = srcs, ""
    import projection_mesh as pm
    tmpl = measure(pm.render(cand, arch, pr.canvas_for(arch), grey=True))
    out = os.path.join(SETS, "%s_%s" % (cand, arch))
    os.makedirs(out, exist_ok=True)
    rows = []
    for i, u in enumerate(urls):
        im = fetch(u)
        im.save(os.path.join(out, "%02d.png" % i))
        m = measure(im)
        # distance from the template's geometry: shear is the discriminating axis (sign AND
        # magnitude), symmetry second
        d = abs(m["shear"] - tmpl["shear"]) + 0.5 * abs(m["symmetry"] - tmpl["symmetry"])
        rows.append(dict(index=i, url=u, distance=round(d, 4), **{k: round(v, 4) for k, v in m.items()}))
    rows.sort(key=lambda r: r["distance"])
    json.dump(dict(candidate=cand, archetype=arch, job_id=job,
                   template={k: round(v, 4) for k, v in tmpl.items()}, ordered=rows),
              open(os.path.join(out, "ledger.json"), "w"), indent=1)
    print("%s %s — template shear %+.3f symmetry %.3f" % (cand, arch, tmpl["shear"], tmpl["symmetry"]))
    for r in rows:
        print("  #%02d  dist %.3f   shear %+.3f  sym %.3f  opaque %.2f"
              % (r["index"], r["distance"], r["shear"], r["symmetry"], r["opaque"]))
    # the ordered sheet, best first, 2x for the eye
    ims = [Image.open(os.path.join(out, "%02d.png" % r["index"])) for r in rows]
    w, h = ims[0].size
    cols = min(8, len(ims))
    rowsn = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (w * 2 + 8), rowsn * (h * 2 + 8)), (24, 24, 28, 255))
    for k, im in enumerate(ims):
        big = im.resize((w * 2, h * 2), Image.NEAREST)
        sheet.paste(big, ((k % cols) * (w * 2 + 8) + 4, (k // cols) * (h * 2 + 8) + 4), big)
    sheet.save(os.path.join(out, "ordered_sheet.png"))
    print("  sheet: %s" % os.path.relpath(os.path.join(out, "ordered_sheet.png"), pr.REPO))


if __name__ == "__main__":
    main()
