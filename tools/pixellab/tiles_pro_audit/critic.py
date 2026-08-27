#!/usr/bin/env python3
"""The blind critic seat, and the mechanical scoring of what it says.

SEAT (LOOP-PROCESS §3.1-3.2). A fresh `claude -p` per set, cwd OUTSIDE the repo. Not a
subagent. Blindness is structural rather than promised: the process cannot reach the repo,
the bible, the declaration, any prior set, or this session's context. It receives the fiction,
the tone and the questions — never the rule list, because handing a critic the rules converts
it into a compliance checker, and what is wanted from an LLM critic is a reaction.

NAMES CARRY NOTHING. Candidates are copied out as `cand_NN.png` in an order derived from a
hash of the source path, so plants do not sit at predictable indices and no filename says
what a file is. The mapping is written to the ledger before the seat runs.

ENLARGEMENT. A 52x87 sprite is copied out at 4x nearest-neighbour, and the prompt says so and
tells the critic to judge it as if it were small. Magnification is a reading aid; nothing is
judged at 4x that would not be judged at 1x.

SCORING — and this is the part that keeps §3.2 honest. The critic is never asked whether a
rule was followed. It answers five questions about the depicted world, and THIS FILE derives
the bar's four structural clauses from its own prose:

  clause 1, two planes     <- THICKNESS: the critic says the wall has a top you could set
                              something on, and names what tells it so
  clause 2, segment identity <- ROLE: the critic can say what piece this is; "cannot tell"
                              fails the clause
  clause 3, §6.3-legal     <- LIGHT: the critic names no direction, and the seat did not cull
                              key-light
  clause 4, no baked outline <- the seat did not cull outline

The derivation is mechanical and auditable: every clause resolves to a string test over the
critic's own words, printed beside the verdict. The critic is the instrument; this is the
readout, and the readout does not get a vote.

HEDGE GUARD (LOOP-PROCESS §5). A PASS whose reason contains a listed failing word is a FAIL
by that clause. This applies a written rule to the critic's words; it makes no judgement about
the image, and every conversion is logged verbatim with both the original and the converted
verdict.

PLANTS (§4). A set whose plants are not all caught is VOID and its findings are not read.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plants as PL  # noqa: E402
import sheet as SH  # noqa: E402

WORKROOT = os.environ.get(
    "TILESPRO_CRITIC_WORK",
    "/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl--claude-worktrees-"
    "probe-6-4/7ad9e514-405b-4304-8ce9-162baf85a6cd/scratchpad/critic_work")

# LOOP-PROCESS §5, verbatim.
FAIL_WORDS = ("fine", "acceptable", "good enough", "improved", "better than",
              "solid", "promising", "close", "nearly there", "has potential",
              "serviceable", "decent", "workable", "could work", "almost")

NO_DIRECTION = ("no direction", "none", "no light direction", "no single direction",
                "not directional", "no discernible direction", "ambient", "even",
                "no clear direction", "nondirectional", "non-directional",
                "no specific direction", "no obvious direction", "no apparent direction")
CANNOT_TELL = ("cannot tell", "can't tell", "cannot say", "unclear", "no idea",
               "impossible to tell", "not clear", "cannot determine", "hard to tell",
               "could be anything", "indeterminate")
NO_THICKNESS = ("no", "flat", "no thickness", "cannot", "would fall", "nothing to set",
                "no top", "paint", "would not stay", "wouldn't stay", "no ledge",
                "no shelf", "not thick")


def order_key(name):
    return hashlib.sha256(name.encode()).hexdigest()


def stage(kit_dir, out_dir, zoom=4, with_plants=True):
    """Copy candidates + plants out to a blind work directory. Returns the mapping."""
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    srcs = []
    for i in SH.WALL_SET:
        p = os.path.join(kit_dir, "tile_%02d.png" % i)
        if os.path.exists(p):
            srcs.append(("candidate", "tile_%02d" % i, p))
    if with_plants:
        pdir = os.path.join(HERE, "plants")
        made = PL.build(kit_dir, pdir)
        for m in made:
            srcs.append(("plant", m["plant"], os.path.join(pdir, m["file"])))

    srcs.sort(key=lambda s: order_key(s[1]))
    mapping = []
    for n, (kind, label, path) in enumerate(srcs):
        im = Image.open(path).convert("RGBA")
        big = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        name = "cand_%02d" % n
        big.save(os.path.join(out_dir, name + ".png"))
        mapping.append({"name": name, "kind": kind, "label": label,
                        "source": os.path.relpath(path, HERE), "native": list(im.size)})
    shutil.copy2(os.path.join(HERE, "critic_prompt.txt"),
                 os.path.join(out_dir, "critic_prompt.txt"))
    return mapping


def run_seat(work_dir, timeout=2400):
    prompt = open(os.path.join(work_dir, "critic_prompt.txt")).read()
    t0 = time.time()
    r = subprocess.run(["claude", "-p", prompt], cwd=work_dir, capture_output=True,
                       text=True, timeout=timeout)
    return r.stdout, r.stderr, round(time.time() - t0, 1)


BLOCK = re.compile(r"CANDIDATE:\s*(\S+)(.*?)(?=CANDIDATE:|FLIP LIST|\Z)", re.S)
FIELD = {k: re.compile(r"^%s:\s*(.*)$" % k, re.M | re.I)
         for k in ("CULL", "ROLE", "THICKNESS", "LIGHT", "HOLDS", "HAPPENED",
                   "VERDICT", "WHY")}


def parse(text):
    out = {}
    for m in BLOCK.finditer(text):
        name = m.group(1).strip().strip("*`")
        body = m.group(2)
        rec = {}
        for k, rx in FIELD.items():
            g = rx.search(body)
            rec[k.lower()] = g.group(1).strip() if g else ""
        out[name] = rec
    fl = re.search(r"FLIP LIST(.*)$", text, re.S)
    flip = [l.strip("- ").strip() for l in (fl.group(1).splitlines() if fl else [])
            if l.strip().startswith("-")]
    return out, flip


def any_of(hay, needles):
    h = hay.lower()
    return any(n in h for n in needles)


def score(rec):
    """Derive the bar's four clauses from the critic's own prose. Returns (clauses, notes)."""
    cull = (rec.get("cull") or "").lower()
    culled = cull not in ("", "none", "n/a", "-")
    thick = rec.get("thickness") or ""
    role = rec.get("role") or ""
    light = rec.get("light") or ""

    # clause 1: a top surface distinguishable from a front face
    t = thick.lower().strip()
    c1 = bool(t) and not any_of(t, CANNOT_TELL) and not (
        t.startswith("no") or any_of(t, NO_THICKNESS))
    # clause 2: segment identity — the critic can name the piece
    c2 = bool(role.strip()) and not any_of(role, CANNOT_TELL)
    # clause 3: §6.3-legal — no named light direction, and no key-light cull
    c3 = bool(light.strip()) and (any_of(light, NO_DIRECTION)) and cull != "key-light"
    # clause 4: no baked outline
    c4 = cull != "outline"
    return {"two_planes": c1, "segment_identity": c2, "no_key_light": c3,
            "no_baked_outline": c4, "culled": culled}, {
        "thickness": thick, "role": role, "light": light}


def hedge(rec):
    """LOOP-PROCESS §5 applied mechanically. Returns (final_verdict, converted, word)."""
    v = (rec.get("verdict") or "").upper()
    v = "PASS" if "PASS" in v else ("FAIL" if "FAIL" in v else v)
    why = (rec.get("why") or "").lower()
    if v == "PASS":
        for w in FAIL_WORDS:
            if w in why:
                return "FAIL", True, w
    return v, False, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kit_dir")
    ap.add_argument("--label", required=True)
    ap.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()

    out = os.path.join(HERE, "critic", a.label)
    os.makedirs(out, exist_ok=True)
    work = os.path.join(WORKROOT, a.label)
    mapping = stage(a.kit_dir, work, a.zoom)
    with open(os.path.join(out, "mapping.json"), "w") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    print("staged %d files (incl %d plants) -> %s" %
          (len(mapping), sum(1 for m in mapping if m["kind"] == "plant"), work))

    stdout, stderr, secs = run_seat(work)
    with open(os.path.join(out, "critic_transcript.txt"), "w") as f:
        f.write(stdout)
    if stderr.strip():
        with open(os.path.join(out, "critic_stderr.txt"), "w") as f:
            f.write(stderr)
    print("seat returned in %ss, %d chars" % (secs, len(stdout)))

    recs, flip = parse(stdout)
    by_name = {m["name"]: m for m in mapping}
    results = []
    for name in sorted(by_name):
        rec = recs.get(name)
        m = by_name[name]
        if rec is None:
            results.append({**m, "verdict": "MISSING", "clauses": None})
            continue
        v, converted, word = hedge(rec)
        clauses, notes = score(rec)
        structural = all(clauses[k] for k in
                         ("two_planes", "segment_identity", "no_key_light",
                          "no_baked_outline")) and not clauses["culled"]
        results.append({**m, "raw": rec, "verdict": v, "hedge_converted": converted,
                        "hedge_word": word, "clauses": clauses, "notes": notes,
                        "structural": structural})

    plants = [r for r in results if r["kind"] == "plant"]
    caught = [r for r in plants if r["verdict"] == "FAIL"]
    cands = [r for r in results if r["kind"] == "candidate"]
    structural = [r for r in cands if r.get("structural")]
    passes = [r for r in cands if r["verdict"] == "PASS"]

    print("\n== PLANTS (the control) ==")
    for r in plants:
        print("  %-9s %-9s verdict=%-8s cull=%-24s %s" %
              (r["label"], r["name"], r["verdict"],
               (r.get("raw") or {}).get("cull", "?"), (r.get("raw") or {}).get("why", "")[:70]))
    void = len(caught) != len(plants)
    print("  caught %d of %d -> %s" %
          (len(caught), len(plants),
           "ROUND VOID — findings not read (§4)" if void else "the seat has demonstrated it "
           "can fail; its verdicts count"))

    print("\n== CANDIDATES ==")
    for r in cands:
        c = r.get("clauses") or {}
        print("  %-9s %-9s %-5s%s  planes=%-5s seg=%-5s nokey=%-5s nooutline=%-5s %s" %
              (r["label"], r["name"], r["verdict"],
               "*" if r.get("hedge_converted") else " ",
               c.get("two_planes"), c.get("segment_identity"), c.get("no_key_light"),
               c.get("no_baked_outline"),
               "STRUCTURAL" if r.get("structural") else ""))

    summary = {"label": a.label, "kit_dir": os.path.relpath(a.kit_dir, HERE),
               "seat_seconds": secs, "n_candidates": len(cands), "n_plants": len(plants),
               "plants_caught": len(caught), "void": void,
               "structural_candidates": len(structural),
               "structural_names": [r["label"] for r in structural],
               "ship_passes": len(passes), "ship_pass_names": [r["label"] for r in passes],
               "hedge_conversions": [{"name": r["label"], "word": r["hedge_word"],
                                      "why": r["raw"]["why"]}
                                     for r in results if r.get("hedge_converted")],
               "flip_list": flip, "results": results}
    with open(os.path.join(out, "result.json"), "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    print("\n%s: %d structural candidates, %d ship-passes, of %d judged. %s"
          % (a.label, len(structural), len(passes), len(cands),
             "VOID" if void else "counts"))
    print("flip list: %d items" % len(flip))


if __name__ == "__main__":
    main()
