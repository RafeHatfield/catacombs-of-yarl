#!/usr/bin/env python3
"""THE SIGHTED ROUND — STEP 3. Blind comparative seats, §13.3's side-by-side, first use.

§13.3: *the visual bar is a blind side-by-side against shipped commercial games, asking "which
of these looks like the shipped game?" — and the answer must be Yarl, or a tie.*

LOOP-PROCESS §3: each seat is a fresh `claude -p` with cwd OUTSIDE the repo. Not a subagent. It
sees two PNGs and the prompt, and it is never given the bible.

PAIRINGS — the comparison only means something if it can come out either way
----------------------------------------------------------------------------
  S1  recipe vs bar     the round's question
  S2  before vs bar     the control on the comparison itself. `before` is the composition
                        spike's arm, built blind, and eight rounds said it has no thickness. If
                        a seat cannot tell IT from the bar either, the pairing is not measuring
                        anything and S1's result is worthless.
  S3  recipe vs before  the direct A/B on the one thing this round changed
  S4  plant vs bar      LOOP-PROCESS §4. The plant carries §6.3's baked key light. A seat that
                        does not cull it VOIDS ITS OWN ROUND.

BAR PIXELS NEVER ENTER THE REPO. The bar crop is written into the seat's working directory,
which is outside the repo, and nowhere else. What comes back into the repo is the seat's text.

PRESENTATION IS LIKE-FOR-LIKE, AND STATED
------------------------------------------
Each image is cropped to a comparable slice of dungeon - a room's north wall, its floor, and a
little of the solid beyond - and shown at 2x its own game's native tile size. The tiles are
therefore not the same pixel size in the two images, which the prompt says outright. Forcing
them equal would mean resampling one of them off its own grid, and a resampled pixel-art tile is
a different defect being judged.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CAPS = os.path.join(HERE, "evidence", "captures")
OUT = os.path.join(HERE, "evidence", "seats")
WORK = ("/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
        "ee659c3f-f445-47fc-8679-e38f870d738a/scratchpad/sighted_seats")

BAR_IMG = ("/Users/rafehatfield/development/assets/oryx/oryx_ultimate_fantasy_1.2/"
           "uf_examples/uf_example_1.png")
# a room's north wall, its floor, and some solid beyond - the same content as the Yarl crop.
BAR_CROP = (352, 56, 520, 176)     # 7 x 5 tiles at the mockup's 24 px rendering
BAR_SCALE = 2
YARL_CROP = (176, 300, 640, 620)   # 7.25 x 5 tiles at the capture's 64 px rendering
YARL_SCALE = 1

PAIRS = {
    "S1": ("recipe_lit.png", "BAR"),
    "S2": ("before_lit.png", "BAR"),
    "S3": ("recipe_lit.png", "before_lit.png"),
    "S4": ("plant_lit.png", "BAR"),
}
# which slot each member lands in, so a seat cannot learn "A is always ours".
SLOTS = {"S1": ("A", "B"), "S2": ("B", "A"), "S3": ("B", "A"), "S4": ("A", "B")}
PLANT_SEAT = "S4"


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def make_image(which):
    if which == "BAR":
        im = Image.open(BAR_IMG).convert("RGB").crop(BAR_CROP)
        return im.resize((im.width * BAR_SCALE, im.height * BAR_SCALE), Image.NEAREST)
    im = Image.open(os.path.join(CAPS, which)).convert("RGB").crop(YARL_CROP)
    return im.resize((im.width * YARL_SCALE, im.height * YARL_SCALE), Image.NEAREST)


def build_work(seat):
    d = os.path.join(WORK, seat)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    first, second = PAIRS[seat]
    sa, sb = SLOTS[seat]
    make_image(first).save(os.path.join(d, sa + ".png"))
    make_image(second).save(os.path.join(d, sb + ".png"))
    return d, {sa: first, sb: second}


def run(work):
    prompt = open(os.path.join(HERE, "seat_prompt.txt")).read()
    p = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"], cwd=work,
                       capture_output=True, text=True, timeout=2400, stdin=subprocess.DEVNULL)
    return p.stdout + p.stderr


def field(text, name):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(name), text, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse(text):
    out = {k: field(text, k) for k in
           ("Q1", "Q1_WHY", "Q3", "Q3_WHY", "Q4_A", "Q4_B", "Q5_A", "Q5_B",
            "Q6_A", "Q6_B", "CULL_A", "CULL_B", "RANK")}
    m = re.search(r"^Q2:\s*(.*?)(?=^Q3:)", text, flags=re.MULTILINE | re.DOTALL)
    out["Q2"] = m.group(1).strip() if m else ""
    fl = re.search(r"^FLIP LIST\s*$(.*)", text, flags=re.MULTILINE | re.DOTALL)
    out["flips"] = [l.strip()[2:].strip() for l in (fl.group(1).splitlines() if fl else [])
                    if l.strip().startswith("- ")]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seats", nargs="*", default=["S1", "S2", "S3", "S4"])
    ap.add_argument("--round", type=int, default=1)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    results = {}
    for seat in args.seats:
        d, mapping = build_work(seat)
        print("=" * 74)
        print("SEAT %s  round %d   %s" % (seat, args.round,
                                          "  <- PLANT SEAT" if seat == PLANT_SEAT else ""))
        print("  cwd: %s   (outside the repo)" % d)
        print("  pairing: %s" % ", ".join("%s=%s" % (k, v) for k, v in sorted(mapping.items())))
        text = run(d)
        with open(os.path.join(OUT, "r%d_%s_transcript.txt" % (args.round, seat)), "w") as f:
            f.write(text)
        r = parse(text)
        r["mapping"] = mapping
        results[seat] = r
        inv = {v: k for k, v in mapping.items()}
        ours = [v for k, v in mapping.items() if v != "BAR"]
        print("  Q1 depth:  %-8s (%s)" % (r["Q1"], r["Q1_WHY"][:60]))
        print("  Q3 side face: %-6s (%s)" % (r["Q3"], r["Q3_WHY"][:60]))
        print("  RANK: %s   culls: A=%s B=%s" % (r["RANK"], r["CULL_A"], r["CULL_B"]))
        if seat == PLANT_SEAT:
            slot = inv.get("plant_lit.png")
            caught = "key-light" in (r.get("CULL_" + slot, "") or "").lower() if slot else False
            r["plant_caught"] = caught
            print("  PLANT CONTROL: %s" % ("CAUGHT" if caught else "MISSED - ROUND VOID"))
        print()

    with open(os.path.join(OUT, "r%d_results.json" % args.round), "w") as f:
        json.dump(dict(round=args.round, commit=git_commit(), pairs=PAIRS, slots=SLOTS,
                       results=results), f, indent=1)
    print("-> %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
