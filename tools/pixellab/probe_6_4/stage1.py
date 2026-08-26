#!/usr/bin/env python3
"""§6.4 probe — STAGE 1: unconditioned bootstrap batches.

Text-only + arm parameters. No style conditioning (that is Stage 2). Per arm x subject,
`--n` generations (default 20): 3 arms x 2 subjects x 20 = 120 generations.

The request is composed from the committed prompt files and from nothing else — see
`prompts/README.md`. There are no chat strings in this probe.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
It does not curate. Every generation reaches the ledger and the contact sheet, in the order
the server returned it and with no quality opinion attached. Selection at STOP 1 is Rafe's
alone, and this seat promotes nothing he did not pick.

It also does not classify. `rejected-at-birth` and `treatment-miss` are eye judgements, and
the bible is explicit that a script emitting a number is an instrument that enters the
optimisation while a blind critic rendering a prose verdict is not (§13.4, v0.3 amendment).
So this script records only what the server did — refusals, sizes, timings, degenerate output
— and the eye judgements are made in a separate blind pass that carries its own positive
control (LOOP-PROCESS §4).

THE LEDGER STORES IMAGES. Nothing on this platform is seed-reproducible (AUDIT column 2), so
an image is not re-derivable from its parameters. Every generation is on disk.
"""
import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_bitforge as v2  # noqa: E402

PROMPTS = os.path.join(HERE, "prompts")
OUT = os.path.join(HERE, "stage1")
ARMS = ("A", "B", "C")
SUBJECTS = ("floor", "wall")
SEED_BASE = 1337


def load(name):
    with open(os.path.join(PROMPTS, name)) as f:
        return json.load(f)


def compose(subject, arm, seed):
    """The composition rule, and the only place it exists. prompts/README.md documents it."""
    payload = dict(subject["parameters"])
    payload.update(arm["parameters"])          # arm wins on conflict
    payload["description"] = subject["description"] + " " + arm["lighting"]
    payload["negative_description"] = subject["negative_description"]
    payload["seed"] = seed
    return payload


def degenerate(img):
    """Mechanical unusability only — NOT an aesthetic judgement and NOT a register check.

    Catches the two failures a script can honestly see: the server returned an image that is
    blank (one colour everywhere) or the wrong canvas. Everything else is for the eye.
    """
    if img is None:
        return "no image"
    if img.size != (32, 32):
        return "wrong canvas %s" % (img.size,)
    cols = img.convert("RGB").getcolors(maxcolors=32 * 32)
    if cols is not None and len(cols) <= 1:
        return "blank (1 colour)"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="generations per arm x subject")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true",
                    help="compose and print every request; call nothing, spend nothing")
    args = ap.parse_args()

    subjects = {s: load("subject_%s.json" % s) for s in SUBJECTS}
    arms = {a: load("arm_%s.json" % a) for a in ARMS}

    jobs = []
    for arm in ARMS:
        for subj in SUBJECTS:
            for i in range(args.n):
                jobs.append((arm, subj, i, compose(subjects[subj], arms[arm], SEED_BASE + i)))

    if args.dry_run:
        for arm in ARMS:
            for subj in SUBJECTS:
                p = compose(subjects[subj], arms[arm], SEED_BASE)
                print("\n=== ARM %s / %s ===" % (arm, subj))
                print(json.dumps(p, indent=1))
        print("\n%d jobs would run. Nothing was called." % len(jobs))
        return 0

    led = v2.Ledger(OUT)
    print("commit:  %s" % led.commit)
    print("surface: v2 HTTP %s%s  [FROZEN]" % (v2.V2_BASE, v2.ENDPOINT))
    print("batch:   %d arms x %d subjects x %d = %d generations" %
          (len(ARMS), len(SUBJECTS), args.n, len(jobs)))

    before, stable_b = v2.settled_pool()
    print("pool before: %s (settled=%s)\n" % (before, stable_b))
    led.write({"claim": "stage1:pool_before", "verdict": "INFO",
               "pool": before, "settled": stable_b, "planned_generations": len(jobs)})

    lock = threading.Lock()
    done = [0]
    results = []

    def run(job):
        arm, subj, i, payload = job
        name = "%s_%s_%02d" % (arm, subj, i)
        for attempt in range(4):
            img, row = v2.generate(payload, led, name,
                                   image_subdir=os.path.join(arm, subj),
                                   claim="stage1:arm%s:%s:%02d" % (arm, subj, i),
                                   extra={"arm": arm, "subject": subj, "index": i})
            if row["verdict"].startswith("REFUSED:rate_limit"):
                time.sleep(10 * (attempt + 1))
                continue
            break
        bad = degenerate(img) if row["verdict"] == "OK" else row["verdict"]
        row["mechanical"] = bad or "usable"
        with lock:
            done[0] += 1
            results.append(row)
            print("  [%3d/%3d] %-14s %-8s %s" %
                  (done[0], len(jobs), name, row["verdict"], row["mechanical"]))
        return row

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(run, jobs))
    elapsed = time.time() - t0

    # ---- counts: only what a script can honestly see -------------------------
    print("\n" + "=" * 78)
    print("STAGE 1 — MECHANICAL COUNTS (server-side outcomes only)")
    print("Eye judgements (rejected-at-birth, treatment-miss) are a separate blind pass.")
    print("=" * 78)
    print("%-6s %-7s %5s %5s %8s %9s" % ("arm", "subject", "run", "ok", "refused", "degen"))
    summary = {}
    for arm in ARMS:
        for subj in SUBJECTS:
            rs = [r for r in results if r["arm"] == arm and r["subject"] == subj]
            ok = [r for r in rs if r["verdict"] == "OK"]
            ref = [r for r in rs if r["verdict"].startswith("REFUSED")]
            deg = [r for r in ok if r["mechanical"] != "usable"]
            summary["%s/%s" % (arm, subj)] = {
                "run": len(rs), "ok": len(ok), "refused": len(ref), "degenerate": len(deg)}
            print("%-6s %-7s %5d %5d %8d %9d" %
                  (arm, subj, len(rs), len(ok), len(ref), len(deg)))

    secs = [r["seconds"] for r in results if r.get("seconds")]
    print("\nwall clock: %.1f min at %d workers; mean %.1f s/generation" %
          (elapsed / 60.0, args.workers, sum(secs) / len(secs) if secs else 0))

    after, stable_a = v2.settled_pool()
    spent = (before - after) if (before is not None and after is not None) else None
    print("pool after: %s (settled=%s)   spent: %s" % (after, stable_a, spent))
    led.write({"claim": "stage1:pool_after", "verdict": "INFO", "pool": after,
               "settled": stable_a, "spent": spent, "summary": summary,
               "elapsed_seconds": round(elapsed, 1)})

    with open(os.path.join(OUT, "stage1_counts.json"), "w") as f:
        json.dump({"summary": summary, "n_per_cell": args.n,
                   "pool_before": before, "pool_after": after, "spent": spent,
                   "commit": led.commit,
                   "surface": "v2-http" + v2.ENDPOINT}, f, indent=1)
    print("\ncounts -> %s" % os.path.join(OUT, "stage1_counts.json"))
    print("ledger -> %s" % led.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
