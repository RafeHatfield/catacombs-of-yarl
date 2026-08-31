#!/usr/bin/env python3
"""BLIND SEATS on the tier-one wall family. LOOP-PROCESS §3, with §4's plant.

    python3 tools/tier1_walls/run_seats.py W1 W2 W3 --round 1
    python3 tools/tier1_walls/run_seats.py W4 --round 1        # the comparative seat

THE SEATS
    W1  the family, alone, absolutely        the round's question
    W2  THE PLANT, alone, absolutely         §4's control on the seat's own rigour
    W3  the family, alone, second opinion    one seat is an anecdote
    W4  the family beside the asset bar      §13.3's comparative frame, blind both ways

§4's CONSEQUENCE IS ABSOLUTE. If W2 does not cull the plant, or does not name the ruin on its own
axis, the round is **VOID** and its findings are not read. Not discounted — void. A soft critic's
findings are worse than no findings, because they will be acted on.

§13.3: MEASUREMENTS LEAVE, PIXELS NEVER DO. The comparative seat is shown a crop of the asset bar
from the licensed local library. It is written into a working directory OUTSIDE the repo and
nowhere else; no bar pixel enters this tree, in any composite, reference or corpus.

LOOP-PROCESS §2.3: the captures are hashed before the first seat and re-hashed before every seat
after it, and the run REFUSES on a change. A round left running while the family was rebuilt would
otherwise produce four opinions of four different builds and nothing would say so.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
OUT = os.path.join(EV, "seats")
WORK = "/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/8ce8033c-4b4a-4de0-8e48-d9cfede08b85/scratchpad/wall_seats"

BAR_IMG = ("/Users/rafehatfield/development/assets/oryx/oryx_ultimate_fantasy_1.2/"
           "uf_examples/uf_example_1.png")
# A crop of the bar that CONTAINS WALLS, because the subject is the wall. Chosen once, recorded
# here, and not re-picked per round: a crop chosen after seeing a verdict is a crop chosen to
# produce one.
BAR_CROP = (96, 96, 672, 672)
# THE DUNGEON VIEW EXACTLY, and round 1 is why it is not a tighter crop. The first crop trimmed
# 60px off the top and 50 off the bottom "to exclude the HUD", and it trimmed away the VOID with
# them — the seat reported *"the image contains no beyond … the wall's outer face and the canvas
# edge are the same line"*, which was true of the crop and not of the scene. A crop that removes
# the subject is the review scene's own §2.2 failure moved into the review harness.
YARL_CROP = (0, 91, 750, 1000)

# ── THE RUIN VOCABULARY — AND IT IS NOT A CONTROL. SEE `audit_plant_control.py`. ──────────────
#
# THIS LIST IS UNCHANGED, DELIBERATELY. It is exactly the list that scored rounds 1-9, because
# re-scoring nine rounds with a vocabulary chosen after reading their transcripts would be the
# laundering §4 exists to prevent — and every round's verdict below stands or falls on the control
# that was in force when it ran.
#
# ⚠ BUT IT DOES NOT DISCRIMINATE, AND `audit_plant_control.py` PROVES IT BOTH WAYS:
#
#   IT GREENS ON THINGS THE FAMILY SHARES. Nine of its terms appear in FAMILY transcripts —
#   `stamped` in six of ten, `nothing has happened` in seven, `no repair` in five. §4.1's own
#   rule, already written into `plant_caught`, is that a reason the family shares has not
#   discriminated between the arm and the plant. Round 8's catch was `['rubble','stamped']`.
#
#   AND IT REDS ON SEATS THAT PLAINLY NAMED THE RUIN. The plant has drawn A FORKED CRACK since it
#   was written and this list has no crack term at all. Round 9's plant seat reported *"Cracked
#   and shedding, never touched … damage without response, which for a place held for four hundred
#   years by people who are extremely good at fixing things is the wrong story"* — the register
#   violation named exactly — and was scored MISSED.
#
# Adding the crack terms makes it green on everything (rounds 3, 6 and 9 all "catch", mostly on
# `crack`, which the FAMILY also authors — `compose_cap.field_cracks`). Removing every
# family-shared term leaves an arbitrary residue in which `fracture` counts and `crack` does not,
# on a ten-transcript sample. There is no vocabulary that works, because the plant's defect is a
# REGISTER judgement — §8.1's *nothing is ruined, things are used up* — and a substring match
# cannot make one.
#
# **STOP (LOOP-PROCESS §1.1, instrument-can't-fail).** The control needs replacing with a
# judgement, not a wider grep, and that is a change to the loop's structure rather than a fix.
# Not this session's to make.
RUIN_WORDS = ("cobweb", "web", "moss", "collapse", "collapsed", "rubble", "ruin", "ruined",
              "crumbl", "derelict", "abandoned", "overgrown", "picturesque", "atmospheric",
              "gothic", "haunted", "spooky",
              # applied-rather-than-accumulated damage: §8.1's distinction in a seat's own words
              "decorativ", "applied to it", "was applied", "staged", "stamped", "ornamental",
              "nothing has happened", "does not read as history", "not as history")


def sha256_of(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def yarl_crop(name):
    return Image.open(os.path.join(EV, name)).convert("RGB").crop(YARL_CROP)


def build_work(seat, cfg):
    d = os.path.join(WORK, seat)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    if cfg["solo"]:
        yarl_crop(cfg["img"]).save(os.path.join(d, "A.png"))
        return d, {"A": cfg["img"]}
    slot = cfg["yarl_slot"]
    other = "A" if slot == "B" else "B"
    yarl_crop(cfg["img"]).save(os.path.join(d, slot + ".png"))
    Image.open(BAR_IMG).convert("RGB").crop(BAR_CROP).save(os.path.join(d, other + ".png"))
    return d, {slot: cfg["img"], other: "BAR (not in the repo)"}


def prompt_for(cfg):
    base = open(os.path.join(HERE, "seat_prompt.txt")).read()
    if cfg["solo"]:
        return base.replace("INPUT: the PNG file(s) in this directory, nothing else.",
                            "INPUT: the file A.png in this directory, nothing else.")
    return base.replace(
        "INPUT: the PNG file(s) in this directory, nothing else.",
        "INPUT: the two files A.png and B.png in this directory, nothing else.\n"
        "**They are from two different games.** You are NOT told which is which and must not\n"
        "guess. Answer every question SEPARATELY for A and for B, labelled Q1_A / Q1_B and so on,\n"
        "and finish with a line 'RANK: <the better standing structure>' naming A or B, or TIE.\n"
        "The two are shown at their own games' native tile sizes and under their own lighting,\n"
        "so the pixels are not the same size in both and one is lit far more evenly than the\n"
        "other. Neither of those is a defect in either. Judge the STRUCTURE.")


def run_claude(work, prompt):
    p = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"], cwd=work,
                       capture_output=True, text=True, timeout=2400, stdin=subprocess.DEVNULL)
    return p.stdout + p.stderr


LABELS = ["Q1_WHY", "Q7_WHY", "Q1_A", "Q1_B", "Q2_A", "Q2_B", "Q4_A", "Q4_B", "Q5_A", "Q5_B",
          # ⚠ THE MULTI-DIGIT LABELS MUST COME BEFORE THE SINGLE-DIGIT ONES. The alternation is
          # ordered, so with "Q1" first, "Q12:" parses as "Q1" and the round's own seat question
          # vanishes into a field nobody reads. It did, once — r8_W1 came back with Q12 = None
          # while the answer was sitting in the transcript.
          "Q6_A", "Q6_B", "CULL_A", "CULL_B", "Q10", "Q11", "Q12", "Q1", "Q2", "Q3", "Q4", "Q5",
          "Q6",
          "Q7", "Q8", "Q9", "CULL", "RANK", "FLIP LIST"]
_LABEL_RE = re.compile(r"^\s*#{0,6}\s*\**(" + "|".join(re.escape(l) for l in LABELS)
                       + r")\**\s*:?\**\s*", re.MULTILINE)


def parse(text):
    """Split on the labels and take everything up to the next one — INCLUDING the next line.

    The floor round's parser read the questions rather than the answers, because a seat writes
    its labels as markdown headings with the answer on the line BELOW, and a single-line regex
    came back holding the restated question. The plant check greps these fields for ruin
    vocabulary, so it was grepping text that could not contain any and reporting VOID.
    """
    hits = list(_LABEL_RE.finditer(text))
    out = {}
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        out.setdefault(m.group(1), text[m.end():end].strip())
    return out


def plant_caught(fields, raw):
    """Did the seat catch the PLANT, or merely cull something?

    §4.1 is the law here: *"the plant must carry the defect ON THE AXIS THE LEVER CLAIMS, and the
    lever must move THAT. A control that only asks 'did anything change?' certifies connectivity
    and reports it as efficacy."* A cull is 'did anything change'. Naming the ruin is the axis.

    So the two are reported SEPARATELY and only the second decides. A cull is recorded because it
    is useful — and because a cull whose reason the family shares is a finding about the FAMILY,
    which is how round 1's most important sentence arrived.
    """
    culled = fields.get("CULL", "").strip().upper() not in ("", "NONE", "NONE.")
    blob = " ".join(fields.get(k, "") for k in ("Q11", "Q8", "Q5", "Q3", "Q1", "CULL")).lower()
    named = [w for w in RUIN_WORDS if w in blob]
    return culled, named


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seats", nargs="+")
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--family", default="r07_family.png")
    ap.add_argument("--plant", default="r07_plant.png")
    ap.add_argument("--reparse", action="store_true",
                    help="re-split the STORED transcripts with the current label set and rewrite "
                         "`fields`. Reads no model and rolls no dice: same words, parsed right.")
    a = ap.parse_args()

    if a.reparse:
        # ⚠ THIS IS NOT A RE-RUN, and the distinction is §4's. Re-running a seat until it says
        # something is the laundering the plant exists to prevent. Re-PARSING asks the same
        # transcript the same question with a parser that can hear the answer — Q12 was added to
        # the prompt and not to LABELS, so `Q12:` matched the `Q1` alternative and the round's own
        # seat question came back None while its answer sat in the file.
        for seat in a.seats:
            p = os.path.join(OUT, "r%d_%s.json" % (a.round, seat))
            rec = json.load(open(p))
            before = set(rec["fields"])
            rec["fields"] = parse(rec["transcript"])
            rec["reparsed"] = "labels %s; transcript untouched" % sorted(set(rec["fields"]) - before)
            json.dump(rec, open(p, "w"), indent=2)
            print("reparsed %s  +%s" % (os.path.relpath(p, REPO),
                                        sorted(set(rec["fields"]) - before)))
        return

    seats = {
        "W1": dict(img=a.family, what="family", solo=True),
        "W2": dict(img=a.plant, what="PLANT", solo=True),
        "W3": dict(img=a.family, what="family", solo=True),
        "W4": dict(img=a.family, what="family", solo=False, yarl_slot="B"),
    }
    frozen = {n: sha256_of(os.path.join(EV, n)) for n in {a.family, a.plant}}
    os.makedirs(OUT, exist_ok=True)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()

    # ── THE PLANT RUNS FIRST, AND A FAMILY SEAT CANNOT RUN WITHOUT ITS VERDICT ────────────────
    #
    # RULED (Rafe, 2026-08-31): *"the round-result file does not exist on disk until the plant
    # verdict lands, so it cannot be read early even deliberately."*
    #
    # The previous rule withheld family answers from the CONSOLE and wrote the record anyway,
    # which stopped an accident and not a decision — and the decision is what happened: I read
    # `r8_W1.json` straight out of the JSON before the plant seat returned, going around my own
    # guard. The round came back VALID, so nothing had to be withdrawn. That is luck, not process.
    #
    # This is the concurrent floor session's design, adopted rather than reinvented (their round
    # 20: *"the PLANT SEAT NOW RUNS FIRST, so a void round costs one seat instead of two and there
    # is nothing to read early"*). Their candidate transcripts still land as `.WITHHELD.txt`;
    # under this ruling nothing lands at all, because the family seat is never RUN before the
    # control clears. A file that does not exist cannot be read deliberately.
    #
    # It is cheaper too: a void round now costs one seat instead of two.
    a.seats = sorted(set(a.seats), key=lambda s: (s != "W2", s))
    if any(s != "W2" for s in a.seats) and "W2" not in a.seats:
        pp = os.path.join(OUT, "r%d_W2.json" % a.round)
        if not os.path.exists(pp):
            raise SystemExit(
                "REFUSING: round %d has no plant verdict on disk, and a family seat is not run "
                "before one exists (§4). Run W2 for this round first:\n"
                "    python3 %s W2 --round %d --family %s --plant %s"
                % (a.round, os.path.relpath(__file__, REPO), a.round, a.family, a.plant))

    for seat in a.seats:
        # THE GATE, RE-READ FROM DISK FOR EVERY FAMILY SEAT rather than carried in a variable —
        # so a plant that ran in this same invocation and MISSED stops the family seats behind it.
        if seat != "W2":
            pp = os.path.join(OUT, "r%d_W2.json" % a.round)
            ctrl = json.load(open(pp)) if os.path.exists(pp) else None
            if ctrl is None or not ctrl.get("caught"):
                why = ("no plant verdict on disk" if ctrl is None
                       else "the plant was MISSED — round %d is VOID" % a.round)
                print("== %s NOT RUN: %s." % (seat, why))
                print("   §4: a void round's findings are not read, so they are not COLLECTED.")
                print("   Nothing for this seat is written, and there is no file to read early.")
                continue
        for n, want in frozen.items():
            if sha256_of(os.path.join(EV, n)) != want:
                raise SystemExit("REFUSING: %s changed while the round was running. Re-capture "
                                 "under a round-scoped name and start again." % n)
        cfg = seats[seat]
        work, slots = build_work(seat, cfg)
        print("== %s (%s) -> %s" % (seat, cfg["what"], work))
        text = run_claude(work, prompt_for(cfg))
        fields = parse(text)
        rec = dict(seat=seat, round=a.round, what=cfg["what"], commit=commit,
                   slots=slots, capture_sha256=frozen.get(cfg["img"]),
                   fields=fields, transcript=text)
        if seat == "W2":
            culled, named = plant_caught(fields, text)
            rec["plant_culled"] = culled
            rec["ruin_named"] = named
            rec["caught"] = bool(named)          # the AXIS decides, not the cull
            print("   plant: culled=%s (not the test) ruin_named=%s -> %s"
                  % (culled, named, "CAUGHT ON AXIS" if rec["caught"]
                     else "MISSED — ROUND IS VOID"))
        # A record only ever reaches disk for a seat that was ALLOWED to run, and the gate above
        # is the only thing that decides that. There is no PENDING state any more: a family
        # seat's record exists exactly when its round is VALID.
        p = os.path.join(OUT, "r%d_%s.json" % (a.round, seat))
        rec["round_verdict"] = ("VALID" if rec["caught"] else "VOID") if seat == "W2" else "VALID"
        json.dump(rec, open(p, "w"), indent=2)
        print("   wrote %s   [round: %s]" % (os.path.relpath(p, REPO), rec["round_verdict"]))
        if seat == "W2" and not rec["caught"]:
            print("   ── ROUND %d IS VOID. No family seat will run, so no family record will"
                  % a.round)
            print("      exist for it. §4: a void round's findings are not evidence.")
            continue
        for k in ("Q1", "Q2", "Q4", "Q6", "Q9", "Q10", "Q12", "CULL", "RANK"):
            if k in fields:
                print("   %-5s %s" % (k, fields[k].splitlines()[0][:150] if fields[k] else ""))


if __name__ == "__main__":
    main()
