#!/usr/bin/env python3
"""THE WALL GAUNTLET — build → critic → flip list → build, autonomously.

LOOP-PROCESS §1.1 governs this session. The critic's FAIL is a reprompt, not a stop; rounds
continue until the bar is met, the budget is spent, or a ruling trigger fires. Nothing returns
to a human for any other reason.

  TASK    at least 5 candidates a blind critic passes as usable-as-wall
  BUDGET  100 generations, declared before the first call and not tuned after
  BAR     5 unhedged PASSes. Below it at budget: "text-to-image cannot produce architectural
          surfaces on this platform at acceptable cost" — a finding, not a failure.

THE CRITIC SEAT
---------------
A fresh `claude -p` per round, cwd OUTSIDE the repo, no repo access, no project memory, and
never the bible (§3 items 1-2). It sees a directory of PNGs and the critic prompt. Blindness
here is structural rather than promised: the process genuinely cannot reach anything else.

THE PLANT — the control that lets a round's verdicts count
----------------------------------------------------------
Every second round seeds one candidate from the Stage 1 morgue: a wall-prompt generation that
is unmistakably an object, not a wall. **A critic that passes a plant voids its round's
verdicts** (§4) — not discounts, voids — and a fresh seat runs. Two consecutive plant passes is
ruling trigger (c) and stops the gauntlet.

Plant selection is deliberate, not random: a random morgue draw could pick a borderline tile
and turn the control into a coin toss. The plants are hand-picked from the Stage 1 wall morgue
for being obviously objects, and their filenames are recorded.

THE HEDGE GUARD
---------------
LOOP-PROCESS §5 enumerates the failing verdict words. A PASS whose reason contains one is a
FAIL by that clause, so it is converted mechanically and every conversion is logged verbatim.
This is applying a written rule, not scoring the art: no judgement is made about the image, and
the critic's own words are preserved in the ledger either way.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab/probe_6_4"))
import v2_bitforge as v2  # noqa: E402

PROMPTS = os.path.join(HERE, "prompts")
OUT = os.path.join(HERE, "rounds")
CRITIC_PROMPT = os.path.join(HERE, "critic_prompt.txt")
WORKROOT = os.environ.get(
    "GAUNTLET_WORK",
    "/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
    "b975ae39-b39f-408f-aade-bdbdc50659f7/scratchpad/gauntlet_work")

BUDGET = 100
BAR = 5
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
MORGUE = os.path.join(REPO, "tools/pixellab/probe_6_4/stage1")

# Hand-picked from the Stage 1 wall morgue for being unmistakably objects. Recorded by name so
# the control is auditable and cannot be quietly swapped for something easier.
# Each is an isometric cube or diamond sitting on a flat grey field: cullable on TWO
# independent grounds (object-not-surface AND wrong-projection), so a critic has to miss both
# to pass one. Chosen by eye from the morgue, not sampled.
PLANTS = [
    "A/wall/A_wall_11.png",   # isometric chest-like cube, warm
    "B/wall/B_wall_11.png",   # isometric cube
    "A/wall/A_wall_02.png",   # isometric cube, teal top face
    "C/wall/C_wall_11.png",   # isometric cube
    "A/wall/A_wall_03.png",   # isometric diamond slab
]

# LOOP-PROCESS §5, verbatim.
FAIL_WORDS = ("fine", "acceptable", "good enough", "improved", "better than",
              "solid", "promising", "close", "nearly there", "has potential",
              "serviceable", "decent", "workable", "could work", "almost")


def load_round(n):
    return json.load(open(os.path.join(PROMPTS, "wall_round%02d.json" % n)))


def payload_for(spec, seed):
    p = dict(spec["parameters"])
    p["description"] = spec["description"]
    p["negative_description"] = spec["negative_description"]
    p["seed"] = seed
    ref = spec.get("style_reference")
    if ref:
        from PIL import Image
        img = Image.open(os.path.join(SURVIVORS, ref + ".png")).convert("RGB")
        p["style_image"] = v2.enc(img)
        p["style_strength"] = spec.get("style_strength", 50)
    return p


def with_guide(p, guide_path, strength):
    """Attach a structural under-drawing as `init_image`.

    A parameter on the frozen surface, not a surface switch. The guide carries geometry only —
    see make_guide.py — and if this works the resulting pipeline is GUIDED generation, which is
    a different claim from "text-to-image works" and must be reported as one.
    """
    from PIL import Image
    p = dict(p)
    p["init_image"] = v2.enc(Image.open(guide_path).convert("RGB"))
    p["init_image_strength"] = strength
    return p


def run_critic(work_dir, transcript_path):
    """Fresh seat. cwd is work_dir, which is outside the repo and contains only PNGs."""
    prompt = open(CRITIC_PROMPT).read()
    proc = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", "Read"],
        cwd=work_dir, capture_output=True, text=True, timeout=1800,
        stdin=subprocess.DEVNULL)
    text = proc.stdout + ("\n[stderr]\n" + proc.stderr if proc.stderr.strip() else "")
    with open(transcript_path, "w") as f:
        f.write(text)
    return text


def parse_verdicts(text):
    """Blocks of CANDIDATE/CULL/VERDICT/WHY, plus the flip list."""
    out = {}
    for m in re.finditer(
            r"CANDIDATE:\s*(\S+).*?CULL:\s*([^\n]+).*?VERDICT:\s*(PASS|FAIL).*?WHY:\s*([^\n]+)",
            text, re.S | re.I):
        name, cull, verdict, why = m.group(1).strip(), m.group(2).strip(), \
            m.group(3).strip().upper(), m.group(4).strip()
        out[name.replace(".png", "")] = {"cull": cull, "verdict": verdict, "why": why}
    flip = []
    fm = re.search(r"FLIP LIST\s*\n(.*)", text, re.S | re.I)
    if fm:
        for line in fm.group(1).splitlines():
            line = line.strip()
            if line.startswith(("-", "*")):
                flip.append(line.lstrip("-* ").strip())
            elif flip and not line:
                break
    return out, flip


def apply_hedge_guard(verdicts):
    converted = []
    for name, v in verdicts.items():
        if v["verdict"] == "PASS":
            low = v["why"].lower()
            hit = next((w for w in FAIL_WORDS if w in low), None)
            if hit:
                v["verdict"] = "FAIL"
                v["hedge_converted"] = hit
                converted.append((name, hit, v["why"]))
    return converted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed-base", type=int, default=None)
    args = ap.parse_args()

    spec = load_round(args.round)
    rd = "round%02d" % args.round
    led = v2.Ledger(os.path.join(OUT, rd))
    seed_base = args.seed_base if args.seed_base is not None else 30000 + args.round * 100

    print("=" * 78)
    print("WALL GAUNTLET — ROUND %d" % args.round)
    print("=" * 78)
    print("framing:     %s" % spec["framing"])
    print("conditioned: %s" % (spec.get("style_reference") or "no (bare)"))
    print("budget:      %d total, BAR %d passes — declared, not tuned\n" % (BUDGET, BAR))

    # Balance bracketed at BOTH ENDS of every round. Added after the first gauntlet run made
    # 100 calls that cost 100 generations while the pool moved 420 — a gap that could not be
    # localised afterwards precisely because no round had a bracket. The subscription is shared
    # with the sibling project, so drift from outside this repo is expected and must be
    # separable from our own spend rather than inferred at the end.
    pool_before, settled_before = v2.settled_pool()
    print("pool before round: %s (settled=%s)\n" % (pool_before, settled_before))
    led.write({"claim": "gauntlet:r%d:pool_before" % args.round, "verdict": "INFO",
               "pool": pool_before, "settled": settled_before, "planned_calls": args.n})

    # ---- build -------------------------------------------------------------
    made = []
    guides = sorted(os.listdir(os.path.join(HERE, "guides"))) if spec.get("init_guide") else []
    guides = [g for g in guides if g.startswith("guide_")]
    for i in range(args.n):
        p = payload_for(spec, seed_base + i)
        extra = {"round": args.round, "index": i,
                 "conditioned": bool(spec.get("style_reference"))}
        if spec.get("init_guide"):
            g = os.path.join(HERE, "guides", guides[i % len(guides)])
            # Two strengths in one round, so the lever's shape is measured rather than guessed.
            strength = spec["init_strengths"][i % len(spec["init_strengths"])]
            p = with_guide(p, g, strength)
            extra.update(init_guide=os.path.basename(g), init_strength=strength)
        img, row = v2.generate(p, led, "r%02d_%02d" % (args.round, i), image_subdir="images",
                               claim="gauntlet:r%d:%02d" % (args.round, i), extra=extra)
        print("  gen %02d  %s" % (i, row["verdict"]))
        if row["verdict"] == "OK":
            made.append((os.path.join(OUT, rd, row["image"]), "r%02d_%02d" % (args.round, i)))

    # ---- critic set: candidates + (every second round) one plant -----------
    work = os.path.join(WORKROOT, rd)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    entries = [(src, name, False) for src, name in made]
    plant_name = None
    if args.round % 2 == 0:
        plant_rel = PLANTS[(args.round // 2 - 1) % len(PLANTS)]
        plant_src = os.path.join(MORGUE, plant_rel)
        plant_name = "r%02d_plant" % args.round
        entries.append((plant_src, plant_name, True))
        print("\n  PLANT SEEDED: %s -> %s" % (plant_rel, plant_name))

    for src, name, _ in entries:
        shutil.copy2(src, os.path.join(work, name + ".png"))

    # ---- critic ------------------------------------------------------------
    print("\n  running blind critic seat (fresh claude -p, cwd=%s)..." % work)
    t0 = time.time()
    transcript = os.path.join(OUT, rd, "critic_transcript.txt")
    text = run_critic(work, transcript)
    verdicts, flip = parse_verdicts(text)
    print("  critic returned in %.0fs; %d verdicts parsed, %d flip items"
          % (time.time() - t0, len(verdicts), len(flip)))

    converted = apply_hedge_guard(verdicts)
    for name, word, why in converted:
        print("  HEDGE GUARD: %s PASS->FAIL on \"%s\" — %s" % (name, word, why))

    # ---- plant control FIRST -----------------------------------------------
    plant_ok = None
    if plant_name:
        pv = verdicts.get(plant_name)
        if pv is None:
            plant_ok = False
            print("\n  PLANT CONTROL: NO VERDICT RETURNED — treated as a failed control.")
        else:
            plant_ok = pv["verdict"] == "FAIL"
            print("\n  PLANT CONTROL: critic said %s (%s) — %s"
                  % (pv["verdict"], pv["cull"], "caught" if plant_ok else "PASSED THE PLANT"))
        if not plant_ok:
            print("  ROUND VOID (§4). Verdicts are NOT read. A fresh seat is owed.")

    passes = [n for n, v in verdicts.items()
              if v["verdict"] == "PASS" and not v.get("_plant")]
    if plant_name:
        passes = [n for n in passes if n != plant_name]

    result = {
        "round": args.round, "generated": len(made), "n_requested": args.n,
        "conditioned": spec.get("style_reference"), "seed_base": seed_base,
        "plant": plant_name, "plant_src": (PLANTS[(args.round // 2 - 1) % len(PLANTS)]
                                           if plant_name else None),
        "plant_caught": plant_ok,
        "round_void": (plant_ok is False),
        "verdicts": verdicts, "flip_list": flip,
        "hedge_conversions": [{"candidate": n, "word": w, "why": y} for n, w, y in converted],
        "passes": [] if plant_ok is False else passes,
        "culls": {},
    }
    for n, v in verdicts.items():
        c = v["cull"].lower()
        if c and c != "none":
            result["culls"][c] = result["culls"].get(c, 0) + 1

    pool_after, settled_after = v2.settled_pool()
    delta = (pool_before - pool_after) if (pool_before and pool_after) else None
    reported = sum(((r.get("usage") or {}).get("generations") or 0)
                   for r in [json.loads(l) for l in open(led.path) if l.strip()]
                   if r.get("claim", "").startswith("gauntlet:r%d:" % args.round)
                   and "request" in r)
    print("\n  pool after round: %s (settled=%s)  delta=%s  reported-by-server=%s"
          % (pool_after, settled_after, delta, reported))
    if delta is not None and abs(delta - reported) > 0.5:
        print("  ⚠ BILLED DELTA DISAGREES WITH REPORTED USAGE by %.1f. The `usage` field is not"
              % (delta - reported))
        print("    the billed amount, or something outside this repo is spending the shared")
        print("    subscription. Do not budget from `usage` alone.")
    result["pool_before"], result["pool_after"] = pool_before, pool_after
    result["billed_delta"], result["reported_usage"] = delta, reported

    with open(os.path.join(OUT, rd, "result.json"), "w") as f:
        json.dump(result, f, indent=1)

    print("\n  culls: %s" % (result["culls"] or "none"))
    print("  PASSES THIS ROUND: %d  %s" % (len(result["passes"]), result["passes"]))
    print("\n  FLIP LIST")
    for item in flip:
        print("   - %s" % item)
    print("\n  transcript -> %s" % transcript)
    return 0


if __name__ == "__main__":
    sys.exit(main())
