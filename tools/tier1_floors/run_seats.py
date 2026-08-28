#!/usr/bin/env python3
"""BLIND SEATS on the tier-one floor family. LOOP-PROCESS §3, with §4's plant.

WHY THIS FILE EXISTS AND WHY IT EXISTS LATE — recorded because the lateness is the finding.

LOOP-PROCESS §3.6: *"The critic runs every round, not at the end. A session that batches N
candidates and presents them uncritiqued has not run the loop; it has run a generator with a
delivery step."* And §1.1.1: nothing reaches the human gate that the blind critic would kill.

This session ran TWO generation batches — base n=40, overlay n=32 — screened both MECHANICALLY,
and went straight on to composition and engine work with **zero seats run**. The mechanical culls
were legitimate (§1.1.1 culls disqualifiers without ceremony) but they are not the critic, and
the composed family — the thing that would actually reach Rafe — had been seen by nobody. That is
the §3.6 violation, it was caught by a mid-flight status check rather than by this session, and
it is written here rather than quietly repaired.

THE SEATS
---------
    F1  the family, alone, absolutely       the round's question
    F2  THE PLANT, alone, absolutely        §4's control on the seat's own rigour
    F3  the family, alone, second opinion   one seat is an anecdote

Each seat sees ONE image and judges it absolutely. §4 requires this shape for tier one — *"tier
one has no shipping corpus to mix in, so 'name them cold' cannot run as designed"* — and a
side-by-side would hand the plant seat the answer by comparison, which is a weaker control than
an absolute judgement.

⚠ AND §1.1.6 WARNS ABOUT EXACTLY THIS SHAPE: *"Absolute verdicts in a vacuum are how ten
independent judges ask for the same wrong thing."* The warning is carried, not dismissed: the
comparative frame §13.3 supplies is a SIDE-BY-SIDE AGAINST THE ASSET BAR, and seat F4 runs it,
with the bar crop written into the seat's working directory OUTSIDE the repo and nowhere else
(§13.3: measurements leave, pixels never do — and that clause governs the repo, which is why the
sighted round's seats could be shown a bar crop by the same mechanism).

THE PLANT — §4, and its consequence is absolute
------------------------------------------------
    If the critic does not catch the plant, the round is VOID and its findings are not read.
    Not discounted — void. A soft critic's findings are worse than no findings, because they
    will be acted on.

The plant is a picturesquely RUINED floor — collapse holes, cobwebbing, moss, dramatic baked
cracks — built by the same composer from the same measured material and captured in the same
scene through the same rig. It is caught if seat F2 culls it, or names the ruin in Q3/Q4/Q5, on
its own axis: §8.1 holds that *nothing in the Paths is ruined; everything is used up*, so a seat
that reports collapse and cobwebs as a defect has read the register. A seat that calls it
atmospheric has not, and F1 and F3 are then unreadable.
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
WORK = "/Users/rafehatfield/.claude/jobs/b976c466/tmp/tier1_seats"

BAR_IMG = ("/Users/rafehatfield/development/assets/oryx/oryx_ultimate_fantasy_1.2/"
           "uf_examples/uf_example_1.png")
# Open floor with a little wall, at the bar's own 48px rendering: the same content as the Yarl
# crop and nothing else. Chosen to be FLOOR, because that is what is being compared.
BAR_CROP = (336, 240, 720, 528)
YARL_CROP = (0, 400, 750, 1000)      # the lit ground around the figure, HUD excluded

# Which capture each seat looks at. Overridable with --family/--plant so a later round can seat a
# new build without overwriting the captures an earlier round's verdicts were taken on — a seat
# transcript citing a filename whose bytes have since changed is not evidence (LOOP-PROCESS §2.3).
FAMILY_IMG = "scene_family.png"
PLANT_IMG = "scene_plant.png"


def SEATS():
    return {
        "F1": dict(img=FAMILY_IMG, what="family", solo=True),
        "F2": dict(img=PLANT_IMG,  what="PLANT",  solo=True),
        "F3": dict(img=FAMILY_IMG, what="family", solo=True),
        "F4": dict(img=FAMILY_IMG, what="family", solo=False),   # comparative, vs the bar
    }
PLANT_SEAT = "F2"
# Which slot the Yarl image lands in for the comparative seat, so a seat cannot learn "A is ours".
F4_YARL_SLOT = "B"


# ---- THE CAPTURE MUST NOT MOVE UNDER THE ROUND ------------------------------------------------
#
# LOOP-PROCESS §2.3: evidence carries its producer's hash, and a seat transcript citing a filename
# whose bytes have since changed is not evidence. That was written as a caution and then violated
# in the obvious way: a round was left running, the family was rebuilt, the capture was overwritten
# in place, and the seats still queued went on to judge A DIFFERENT BUILD THAN THE FIRST SEAT SAW.
# Nothing failed. The round would have been written up as four opinions of one floor.
#
# So the bytes are hashed before the first seat and re-hashed before every seat after it, and the
# run REFUSES rather than continuing across a change. Use round-scoped capture names
# (scene_ashlar_r4.png) so a later round cannot need to overwrite an earlier round's evidence at
# all — a rule that removes the hazard beats a check that catches it.
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def freeze_captures():
    seen = {}
    for name in {FAMILY_IMG, PLANT_IMG}:
        seen[name] = sha256_of(os.path.join(EV, name))
    return seen


def check_captures(frozen):
    for name, want in frozen.items():
        got = sha256_of(os.path.join(EV, name))
        if got != want:
            raise SystemExit(
                "REFUSING: %s changed while the round was running.\n"
                "  was %s\n  now %s\n"
                "Seats already run judged different pixels than the ones left to run would. "
                "Re-capture under a round-scoped name and start the round again." % (name, want, got))


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def yarl_crop(name):
    im = Image.open(os.path.join(EV, name)).convert("RGB").crop(YARL_CROP)
    return im


def bar_crop():
    im = Image.open(BAR_IMG).convert("RGB").crop(BAR_CROP)
    return im


def build_work(seat):
    cfg = SEATS()[seat]
    d = os.path.join(WORK, seat)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    if cfg["solo"]:
        yarl_crop(cfg["img"]).save(os.path.join(d, "A.png"))
        return d, {"A": cfg["img"]}
    other = "A" if F4_YARL_SLOT == "B" else "B"
    yarl_crop(cfg["img"]).save(os.path.join(d, F4_YARL_SLOT + ".png"))
    bar_crop().save(os.path.join(d, other + ".png"))
    return d, {F4_YARL_SLOT: cfg["img"], other: "BAR"}


def prompt_for(seat):
    base = open(os.path.join(HERE, "seat_prompt.txt")).read()
    if SEATS()[seat]["solo"]:
        return base.replace("INPUT: the PNG file(s) in this directory, nothing else.",
                            "INPUT: the file A.png in this directory, nothing else.")
    return base.replace(
        "INPUT: the PNG file(s) in this directory, nothing else.",
        "INPUT: the two files A.png and B.png in this directory, nothing else.\n"
        "**They are from two different games.** You are NOT told which is which and must not\n"
        "guess. Answer every question SEPARATELY for A and for B, labelled Q1_A / Q1_B and so on,\n"
        "and finish with a line 'RANK: <the better floor>' naming A or B, or TIE.\n"
        "The two are shown at their own games' native tile sizes, so the pixels are not the same\n"
        "size in both. That is not a defect in either.\n"
        "NOTE FOR B ONLY IF RELEVANT: one of the two images may have finished walls. The scope\n"
        "rule below still holds — judge the FLOOR in each.")


def run(work, prompt):
    p = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"], cwd=work,
                       capture_output=True, text=True, timeout=2400, stdin=subprocess.DEVNULL)
    return p.stdout + p.stderr


# Labels the prompt asks for, longest first so Q1_WHY is matched before Q1.
LABELS = ["Q1_WHY", "Q3_WHY", "Q1_A", "Q1_B", "Q5_A", "Q5_B", "Q6_A", "Q6_B",
          "CULL_A", "CULL_B", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "CULL", "RANK", "FLIP LIST"]
# Leading markdown of ANY kind: heading hashes, bold stars, or nothing. A seat writes its labels
# however it likes and the parser's job is to find them, not to legislate their formatting.
_LABEL_RE = re.compile(r"^\s*#{0,6}\s*\**(" + "|".join(re.escape(l) for l in LABELS)
                       + r")\**\s*:?\**\s*", re.MULTILINE)


def parse(text, strict=True):
    """Split the transcript on its labels and take everything up to the next one.

    ⚠ THE FIRST VERSION OF THIS FUNCTION READ THE QUESTIONS, NOT THE ANSWERS. It matched
    `^LABEL:\\s*(.*)$` on a single line, and the seat writes its labels as markdown headings —
    `**Q1: WHAT IS THIS FLOOR MADE OF?**` with the answer on the line BELOW. So every field came
    back holding the restated question, and the plant check, which greps those fields for ruin
    vocabulary, was reading text that could not possibly contain any.

    It reported the round VOID. The transcript said the round was void too, for a different and
    real reason — but the two agreed by coincidence, and a check that returns the right verdict
    from the wrong input is not a check. Recorded rather than quietly fixed, because "the output
    looked right" is exactly what LOOP-PROCESS §4.2 says cannot answer for a step.
    """
    out = {}
    marks = [(m.start(), m.end(), m.group(1)) for m in _LABEL_RE.finditer(text)]
    for i, (s0, e0, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = text[e0:end].strip()
        # A heading line restating the question ends in '?' or is shouted; drop it.
        lines = body.splitlines()
        if lines and (lines[0].rstrip("* ").endswith("?")
                      or (lines[0].strip("* ").isupper() and len(lines) > 1)):
            body = "\n".join(lines[1:]).strip()
        if name not in out or len(body) > len(out[name]):
            out[name] = body
    for k in LABELS:
        out.setdefault(k, "")
    out["flips"] = [l.strip()[2:].strip() for l in out.get("FLIP LIST", "").splitlines()
                    if l.strip().startswith("- ")]

    # WHAT GOES RED IF THIS SILENTLY DOES NOTHING (LOOP-PROCESS §4.2). A field that comes back
    # empty because the seat did not answer and a field that comes back empty because the parser
    # could not find the answer are indistinguishable downstream — and the second one nearly
    # voided a valid round. Round 5's plant seat culled under a markdown heading (`## CULL`)
    # rather than a bold label, the parser returned "", and the plant control reported MISSED.
    # It was the parser's third defect in this session and the first that would have thrown away
    # a real result.
    #
    # So: if the transcript contains a label as a word and the parser extracted nothing for it,
    # that is an ERROR rather than an absent answer.
    if strict:
        for name in ("CULL", "Q1", "Q6"):
            if not out.get(name) and re.search(r"\b%s\b" % name, text):
                raise ValueError(
                    "PARSE FAILURE: the transcript mentions %s but nothing was extracted for it. "
                    "An empty field and an unparsed field are not the same thing, and treating "
                    "them alike voids valid rounds." % name)
    return out


# The plant is caught if the seat names the RUIN on its own axis. Matched on the vocabulary the
# plant actually carries, declared here before the seats run so the test cannot be relaxed after
# reading a transcript.
# EXCLUSIVE to the plant. The first list included "crack", "cracked" and "damage", and that is
# wrong in a way that would have made the control decorative: §8.3 puts CRACKS IN THE LEGAL
# INCIDENT SET — the real family ships a crack overlay family at rate 0.11 — so a seat naming a
# crack has said nothing that separates plant from candidate. A control that greens on the thing
# it is controlling for is worse than no control (§13.4's whole argument).
#
# What follows is only what the plant has and the family does not: collapse, cobwebbing, moss,
# rubble, and the word "ruined" itself, which is §8.1's own term for the failure.
# THE VOCABULARY IS DERIVED FROM WHAT THE PLANT CONTAINS, NOT FROM WHAT A SEAT ONCE SAID.
#
# That sentence is the correction, and it took three rounds to earn. The list began as session
# two's, whose plant had moss in the joints and a cobweb dither. The ashlar plant draws COLLAPSE
# VOIDS, bright strands and dramatic cracks — and after round 8 the list was widened by reading
# round 8's transcript and adding the words that seat happened to use. Round 9's seat then
# described the same plant in different words again and scored NOTHING:
#
#     "It's been shot through with HOLES and scribbled on, evenly, everywhere, by nothing in
#      particular. There are roughly twenty punched-through black HOLES across a floor of about
#      92 tiles"
#     CULL: "Damage is uniform decorative scatter — the ground records no traffic, no event, and
#      no repair."
#
# It used "hole" fourteen times. **The plainest word for the plant's most prominent feature had
# never been in the list**, through three rounds — while the list carried "lichen", which the
# plant has never contained. Chasing a critic's vocabulary one transcript at a time is the same
# error as relaxing a threshold after seeing a result: the test ends up derived from the outcome.
#
# So the list is now derived from `plant_ashlar.py`'s three draw calls and nothing else, as STEMS,
# and it is a standing obligation: **when the plant's construction changes, this changes with it,
# before the next round runs.**
#
#     collapse voids   -> hole, void, collaps, cave, punct, crater, pit
#     cobweb strands   -> web, cobweb, strand, silk
#     the register     -> ruin, rubble, moss, lichen, overgrown, derelict
#
# ⚠ "CRACK" IS AND REMAINS EXCLUDED, and now emphatically so: the FAMILY draws cracks, at field
# scale, as its primary incident. A seat naming a crack has said nothing that separates plant from
# candidate, and a control that greens on the thing it is controlling for is worse than no control.
PLANT_WORDS = ("hole", "void", "collaps", "cave", "punct", "crater",
               "web", "strand", "silk",
               "ruin", "rubble", "moss", "lichen", "overgrown", "derelict")


# ⚠ NEGATION. Round 8's plant seat scored a hit on the word "collapse" — inside the sentence
# "Not one large collapse." The verdict was right for a reason the matcher had nothing to do with:
# the seat culled on register, in Q3 and in CULL, and the matcher agreed with it by accident.
#
# A check that returns the right verdict from the wrong input is not a check (LOOP-PROCESS §4.2),
# and this one would have said CAUGHT for a seat that had declared the floor CLEAN of every defect
# in the list. Hits inside a negation are discarded.
NEGATIONS = ("no ", "not ", "none", "nothing", "never", "without", "free of", "n't")


def _negated(blob, at):
    """Is this hit inside a clause that DENIES it? Looks back to the start of the sentence."""
    start = max(blob.rfind(".", 0, at), blob.rfind(";", 0, at), blob.rfind("\n", 0, at)) + 1
    return any(n in blob[start:at] for n in NEGATIONS)


def plant_caught(r, text):
    """Caught if the seat CULLS and names the ruin on its own axis (§4.1: on the axis claimed)."""
    blob = " ".join([r.get(k, "") for k in ("Q1", "Q3", "Q3_WHY", "Q4", "Q5", "CULL")]).lower()
    hit = []
    for w in PLANT_WORDS:
        at = blob.find(w)
        while at >= 0:
            if not _negated(blob, at):
                hit.append(w)
                break
            at = blob.find(w, at + 1)
    culled = bool(r.get("CULL")) and r["CULL"].strip().upper().rstrip(".") != "NONE"
    return (culled and bool(hit)), hit, culled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seats", nargs="*", default=["F1", "F2", "F3", "F4"])
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--family", help="capture filename in evidence/ for the candidate seats")
    ap.add_argument("--plant", help="capture filename in evidence/ for the plant control")
    a = ap.parse_args()
    global FAMILY_IMG, PLANT_IMG
    if a.family:
        FAMILY_IMG = a.family
    if a.plant:
        PLANT_IMG = a.plant
    os.makedirs(OUT, exist_ok=True)
    frozen = freeze_captures()
    print("captures frozen for this round:")
    for k, v in sorted(frozen.items()):
        print("  %-28s %s" % (k, v))
    print()

    results, void = {}, False
    for seat in a.seats:
        check_captures(frozen)
        d, mapping = build_work(seat)
        print("=" * 78)
        print("SEAT %s  round %d%s" % (seat, a.round,
                                       "   <- PLANT CONTROL" if seat == PLANT_SEAT else ""))
        print("  cwd: %s  (outside the repo)" % d)
        print("  slots: %s" % ", ".join("%s=%s" % kv for kv in sorted(mapping.items())))
        text = run(d, prompt_for(seat))
        tp = os.path.join(OUT, "r%d_%s_transcript.txt" % (a.round, seat))
        with open(tp, "w") as f:
            f.write(text)
        r = parse(text)
        r["mapping"] = mapping
        r["transcript"] = os.path.relpath(tp, REPO)
        results[seat] = r

        if seat == PLANT_SEAT:
            caught, hit, culled = plant_caught(r, text)
            r["plant_caught"] = caught
            r["plant_words_hit"] = hit
            print("  Q3: %s" % (r["Q3"] or "(unparsed)")[:100])
            print("  CULL: %s" % (r["CULL"] or "(unparsed)")[:100])
            print("  PLANT CONTROL: %s   (culled=%s, ruin vocabulary hit=%s)"
                  % ("CAUGHT" if caught else "MISSED — ROUND VOID", culled, hit))
            if not caught:
                void = True
        else:
            print("  Q1: %s" % (r["Q1"] or r["Q1_A"] or "(unparsed)")[:90])
            print("  Q2: %s" % (r["Q2"] or "(unparsed)")[:90])
            print("  Q4: %s" % (r["Q4"] or "(unparsed)")[:90])
            print("  Q5: %s" % (r["Q5"] or r["Q5_A"] or "(unparsed)")[:90])
            print("  Q6: %s" % (r["Q6"] or r["Q6_A"] or "(unparsed)")[:90])
            print("  CULL: %s" % (r["CULL"] or r["CULL_A"] or "(unparsed)")[:90])
            if r.get("RANK"):
                print("  RANK: %s" % r["RANK"])
            for fx in r["flips"][:5]:
                print("     flip: %s" % fx[:90])

    check_captures(frozen)
    res = dict(round=a.round, commit=git_commit(), seats=results, captures=frozen,
               plant_seat=PLANT_SEAT, round_void=void,
               plant_words_declared=list(PLANT_WORDS),
               law=("LOOP-PROCESS §4: if the critic does not catch the plant, the round is VOID "
                    "and its findings are not read."))
    rp = os.path.join(OUT, "SEATS-r%d.json" % a.round)
    with open(rp, "w") as f:
        json.dump(res, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(rp, REPO))
    if void:
        print("\n*** ROUND VOID — the plant seat did not catch the plant. Findings not read. ***")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
