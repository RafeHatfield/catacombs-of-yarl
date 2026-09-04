#!/usr/bin/env python3
"""THE FRAME CRITIC — an art round is judged by eyes on delivered frames, and by nothing else.

    .claude/skills/frame-critic/run_frame_critic.sh

WHAT THIS IS
------------
A fresh blind `claude -p` seat is shown a small deck of finished frames — this build's capture,
the asset bar, the last frame Rafe approved, and ONE PICTURE-PLANT drawn from the morgue — and
asked to rank them, say which it would ship, and flag anything with an obvious defect. The deck
is shuffled and unlabelled. The seat gets no code, no coordinates, no thresholds, no bible.

    PASS   the build's frame is one the seat would ship, and it flagged no defect in it
    FAIL   it would not ship it; the flip list is recorded verbatim
    VOID   the seat did not catch the plant. Findings are NOT READ (LOOP-PROCESS §4)

WHY IT IS BUILT THIS WAY — two measured collapses, both of the review layer, both the same shape
-----------------------------------------------------------------------------------------------
1. THE INSTRUMENTS BECAME THE JUDGE. The wall gate of 2026-08-27: every instrument green, and the
   phone still said no. A device gate FAIL against a fully green instrument set is not a tuning
   miss — it says the thing being measured and the thing being judged had come apart.

2. THE PLANT STOPPED BEING IN THE PICTURE. Wall rounds 9 and 10 both went VOID because the
   generated plant differed from the family in 0.54% of pixels: since the cap pass, the cell's
   base is a cap window and the wall family's top tiles are never drawn, so ruining the wall tiles
   ruined almost nothing. The control was downstream of the engine, so an engine change silently
   neutralised it. Rounds 3 and 6 died the same way for a different reason.

Both collapses are apparatus failures, and both would have been survived by a mechanism with
nothing in it that can break. So:

    THE JUDGE IS EYES ON PICTURES. There is no threshold in it to drift, no metric to
    outcompete a clause that has no number, and no code path between the build and the verdict
    except the capture itself.

    THE PLANT IS A PICTURE. A known-bad frame Rafe personally culled, kept as bytes in
    `morgue/`. An engine change cannot neutralise a picture. The only way to disarm one is to
    delete the file, and that is a visible diff.

    INSTRUMENTS ARE BUILDER'S TOOLS. They are welcome, they are useful for aiming between
    rounds, and they gate nothing. Every measure_*.py in this repo stays exactly where it is.

THE LOOP GUARDS — this must never grind
---------------------------------------
    TWO STRIKES     the same flip item unresolved across two consecutive FAILs -> STOP
    FIVE-ROUND PARK five rounds on this lane with no PASS -> STOP
    BROKEN JUDGE    the plant missed twice consecutively -> STOP, and never ship past one

Every STOP writes STALL-REPORT.md and is a §1.1.4 ruling trigger with that report as its
evidence. THE COUNTERS ARE DERIVED FROM THE VERDICT FILES ON DISK, not held in memory, so
restarting a session cannot reset them — the only way to clear a counter is to delete committed
files, which shows up in a diff.

EXIT CODES
    0 PASS   1 FAIL   2 VOID   3 STOP (a guard fired)   4 precondition/usage
"""
import argparse
import datetime
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import build_id as BID                                    # noqa: E402

CONFIG = os.path.join(REPO, "docs", "FRAME-CRITIC.json")
MORGUE = os.path.join(HERE, "morgue")
HISTORY = os.path.join(HERE, "history")
VERDICT = os.path.join(REPO, "CRITIC-VERDICT.json")
STALL = os.path.join(REPO, "STALL-REPORT.md")
PARK_CLEARED = os.path.join(REPO, "PARK-CLEARED.json")

# ── THE GUARDS' NUMBERS, DECLARED HERE BEFORE ANY ROUND RUNS ──────────────────────────────────
# LOOP-PROCESS §8: a bar is never re-tuned after the answer is seen. These are the bar.
TWO_STRIKES = 2          # consecutive FAILs carrying the same unresolved flip item
PARK_ROUNDS = 5          # rounds on one lane with no PASS
JUDGE_MISSES = 2         # consecutive plant misses before the judge is called broken
FLIP_SAME = 0.60         # Jaccard over content words at which two flip items are "the same item"

# Words that carry no content for the purpose of asking whether two flip items are the same one.
_STOP_WORDS = set("""a an the and or but if then than that this these those it its is are was
were be been being to of in on at by for with from as into over under across along up down out
off not no nor so such very more most less least much many few some any each every both either
neither only just also too do does did doing done have has had having make makes made making
should would could can may might will shall must there their them they you your we our i me my
""".split())


# ================================ verdict history, and the guards =============================
def history(where=None):
    """Every verdict this lane has recorded, oldest first.

    ON DISK BY DESIGN. A counter held in a variable resets when a session restarts, and a guard
    that a restart clears is not a guard — it is a suggestion with a number in it.
    """
    HISTORY_ = where or HISTORY
    if not os.path.isdir(HISTORY_):
        return []
    out = []
    for name in sorted(os.listdir(HISTORY_)):
        if not name.endswith(".json"):
            continue
        try:
            out.append(json.load(open(os.path.join(HISTORY_, name))))
        except Exception:
            continue
    out.sort(key=lambda v: v.get("timestamp", ""))
    return out


def lane_of(v):
    return v.get("lane")


def _words(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in _STOP_WORDS
            and len(w) > 2}


def same_flip(a, b):
    """Are these two flip-list items the same request, differently worded?

    A seat rephrases. Exact string equality would report two strikes as never happening, which is
    the failure mode a guard cannot have: silently never firing. Content-word overlap is the
    cheapest thing that survives rephrasing, and the threshold is declared above, before any round.
    """
    wa, wb = _words(a), _words(b)
    if not wa or not wb:
        return False
    return len(wa & wb) / float(len(wa | wb)) >= FLIP_SAME


def guards(hist, lane):
    """Which guard, if any, has fired. Returns (name, explanation) or (None, None).

    Checked over the lane's verdicts as they sit on disk, BEFORE the run is reported, so a session
    that restarts mid-stall walks into the same wall it walked into before.
    """
    lane_hist = [v for v in hist if lane_of(v) == lane]

    # ── A PARK CLEARS BY AN ADDED ARTIFACT, NEVER BY REMOVING EVIDENCE ────────────────────────
    #
    # RULED (Rafe, 2026-09-03): *"Park cleared by ruling — author and commit PARK-CLEARED.json at
    # repo root … guard counts judged rounds after the marker, no verdict files deleted (evidence
    # stays; the clear is an added artifact)."*
    #
    # The guard fires from the verdict files on disk, so the only other way to clear it is to
    # delete them — and a mechanism whose reset is *destroy the record* teaches exactly the wrong
    # reflex: the lane that most wants the guard gone is the lane holding the evidence against
    # itself. Every round stays readable; the marker only says where a ruling drew the line.
    #
    # It does NOT clear a broken judge. A soft critic is not a lane problem, and no ruling about
    # the lane makes an unreadable verdict readable — which is why this is consulted below the
    # broken-judge check and not above it.
    cleared_after = None
    if os.path.exists(PARK_CLEARED):
        try:
            mk = json.load(open(PARK_CLEARED))
            if mk.get("lane") in (None, lane):
                cleared_after = int(mk.get("cleared_after_round", 0)) or None
        except Exception:                                            # noqa: BLE001
            cleared_after = None

    # BROKEN JUDGE first, because nothing downstream of it is readable. A void round's findings
    # are not evidence, so a stall computed across them would be a stall computed across nothing.
    tail = [v for v in lane_hist[-JUDGE_MISSES:]]
    if len(tail) >= JUDGE_MISSES and all(v.get("verdict") == "VOID" for v in tail):
        return ("broken-judge",
                "the picture-plant was missed %d rounds running. The judging layer is broken; "
                "no round past it is readable and nothing ships past it." % JUDGE_MISSES)

    fails = [v for v in lane_hist if v.get("verdict") == "FAIL"]
    if len(fails) >= TWO_STRIKES:
        a, b = fails[-2], fails[-1]
        # Consecutive means consecutive: an intervening PASS or VOID breaks the streak.
        ia, ib = lane_hist.index(a), lane_hist.index(b)
        if ib == ia + 1:
            for x in a.get("flip_list", []):
                for y in b.get("flip_list", []):
                    if same_flip(x, y):
                        return ("two-strikes",
                                "the same flip item survived two consecutive FAIL rounds:\n"
                                "    round %s: %s\n    round %s: %s"
                                % (a.get("round"), x, b.get("round"), y))

    # ⚠ A VOID DOES NOT COUNT TOWARD THE PARK (RULED, Rafe, 2026-09-03).
    #
    # *"A VOID round is a broken-judge event, not a no-progress round — it must not count toward
    # stall/park."*
    #
    # The park asks whether the LANE is getting anywhere. A void round says nothing about the
    # lane: its findings are not read, by §4, so it produced no evidence either way — and this
    # file already says as much a few lines up, where the broken-judge guard skips them for
    # exactly that reason. Counting them anyway parked the wall lane on a tally that included
    # one round nobody was allowed to learn from, which is a guard firing on its own blindness.
    #
    # The broken-judge guard above is what VOIDs are for, and it still has them.
    judged = [v for v in lane_hist if v.get("verdict") != "VOID"]
    if cleared_after:
        judged = [v for v in judged if int(v.get("round", 0)) > cleared_after]
    if len(judged) >= PARK_ROUNDS and not any(v.get("verdict") == "PASS"
                                              for v in judged[-PARK_ROUNDS:]):
        return ("five-round-park",
                "%d JUDGED rounds on this lane with no PASS (voids excluded — they are not "
                "evidence%s). The lane is parked; the next move is a ruling, not another round."
                % (PARK_ROUNDS,
                   "; rounds up to r%d cleared by PARK-CLEARED.json" % cleared_after
                   if cleared_after else ""))
    return (None, None)


def write_stall(name, why, hist, lane, cfg, out=None):
    out = out or STALL
    lane_hist = [v for v in hist if lane_of(v) == lane]
    L = []
    L.append("# STALL REPORT — %s\n" % name)
    L.append("**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling "
             "trigger: this report is the evidence.\n")
    L.append("- **lane** `%s`" % lane)
    L.append("- **surface** `%s`" % cfg.get("surface"))
    L.append("- **guard** `%s`" % name)
    L.append("- **written** %s\n" % datetime.datetime.now().isoformat(timespec="seconds"))
    L.append("## Why it stopped\n")
    L.append(why + "\n")
    L.append("## What was tried, round by round\n")
    L.append("| round | verdict | build | capture | the seat's own words |")
    L.append("|---|---|---|---|---|")
    for v in lane_hist:
        worst = (v.get("seat", {}).get("WORST_WHY") or "").replace("|", "/")
        L.append("| %s | %s | `%s` | `%s` | %s |"
                 % (v.get("round"), v.get("verdict"), (v.get("build_id") or "")[:12],
                    os.path.basename(v.get("deck", {}).get("build", "")),
                    " ".join(worst.split())[:160]))
    L.append("")
    L.append("## The flip lists, verbatim\n")
    for v in lane_hist:
        if not v.get("flip_list"):
            continue
        L.append("**round %s (%s)**\n" % (v.get("round"), v.get("verdict")))
        for f in v["flip_list"]:
            L.append("- %s" % f)
        L.append("")
    L.append("## Where to look\n")
    L.append("Captures and transcripts, per round:\n")
    for v in lane_hist:
        L.append("- round %s — deck `%s`, transcript `%s`"
                 % (v.get("round"), v.get("deck", {}).get("work_dir", "?"),
                    v.get("transcript", "?")))
    L.append("")
    L.append("## What is being asked for\n")
    L.append("A ruling. Not another round — the guard fired precisely because another round is "
             "the wrong move. Nothing installs to the phone while this stands.\n")
    with open(out, "w") as f:
        f.write("\n".join(L))
    return out


# ================================ the deck ====================================================
def crop_to(path, box, dest):
    """Crop one deck frame, and REFUSE a box that runs off the source image.

    ⚠ FOUND BY THE FIRST FINISHED ROUND, in the asset bar of all places. PIL pads an out-of-bounds
    crop with black and says nothing. The bar crop inherited from the floors' seat runner is
    `(336, 240, 720, 528)` against a source that is **720x504** — so every comparative seat this
    project has ever run was shown the commercial bar with **24 rows of black padding along the
    bottom**, and the seat that finally said so culled the bar for it:

        WORST 1 — "The frame is padded. Content ends at row 239. Rows 240-263 are pure ..."

    The bar is the quality reference. A padded bar is a reference the seat rejects for a defect
    that belongs to the crop box, and the comparison it was there to make does not happen.

    Exactly LOOP-PROCESS §4.2's shape — a step that quietly does nothing anyone can see, until it
    surfaces later and somewhere else. So the box is checked against the image and the round
    refuses rather than padding.
    """
    im = Image.open(path).convert("RGB")
    if box:
        x0, y0, x1, y1 = box
        w, h = im.size
        if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
            raise SystemExit(
                "REFUSING: the crop %s runs off %s, which is %dx%d.\n"
                "PIL would pad the difference with black and say nothing, and a seat shown a "
                "padded frame\ncorrectly culls it for the padding. Fix the box in the config."
                % (tuple(box), os.path.relpath(path, REPO) if path.startswith(REPO) else path,
                   w, h))
        im = im.crop(tuple(box))
    im.save(dest)
    return im.size


def pick_plant(surface, morgue, exclude=(), axis=None):
    """Candidates for this round's plant, narrowed to the AXIS the deck is asking about.

    RULED (Rafe, 2026-09-03): *"Per-axis morgue plants — tag entries by axis, assemble the plant
    to match the deck's question; this is why round 5 VOIDed."*

    A plant is only a control if it is wrong on the axis under test. The wall lane's round 5 was
    judged on CONSTRUCTION — does the cap read as stone or as cement — and was handed the `grey
    walls` plant, whose defect is CHROMA. The build had already had its chroma fixed, so the two
    frames differed on an axis the plant was not carrying, the seat had no reason to rank the
    plant last, and the round voided on the judge rather than on the art. The right image for the
    wrong question is not a control.

    An entry with no `axis` is treated as answering any question, so the morgue stays usable while
    it is being tagged.
    """
    entries = [e for e in morgue["entries"]
               if e["surface"] == surface and e["file"] not in exclude]
    if axis:
        on_axis = [e for e in entries if axis in (e.get("axis") or [axis])]
        if on_axis:
            entries = on_axis
    if not entries:
        raise SystemExit(
            "REFUSING: the morgue holds no known-bad frame for surface %r.\n"
            "A round with no plant is a round with no control, and LOOP-PROCESS §4 does not "
            "permit reading its findings. Add a Rafe-culled frame for this surface to\n"
            "  %s\nbefore running another round." % (surface, os.path.join(MORGUE, "MORGUE.json")))
    return entries


def verify_morgue(morgue):
    """A morgue entry whose bytes have changed is not the frame Rafe culled.

    §2.3 in its plainest form. This is the one check that protects the picture-plant's whole
    claim: a plant that can be edited is a plant that can be softened.
    """
    bad = []
    for e in morgue["entries"]:
        p = os.path.join(MORGUE, e["file"])
        if not os.path.exists(p):
            bad.append("%s is missing" % e["file"])
            continue
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if got != e["sha256"]:
            bad.append("%s has changed: recorded %s, on disk %s"
                       % (e["file"], e["sha256"][:16], got[:16]))
    if bad:
        raise SystemExit("REFUSING: the morgue does not match its manifest.\n  "
                         + "\n  ".join(bad)
                         + "\nA plant that can be edited is a plant that can be softened.")


# ================================ the seat ====================================================
def run_seat(work, prompt, timeout):
    p = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"],
                       cwd=work, capture_output=True, text=True,
                       timeout=timeout, stdin=subprocess.DEVNULL)
    return p.stdout + p.stderr


LABELS = ["BEST_WHY", "WORST_WHY", "FLAGGED", "RANK", "BEST", "WORST", "SHIP"]
_LABEL_RE = re.compile(r"^\s*#{0,6}\s*\**(" + "|".join(LABELS) + r")\**\s*:\**\s*",
                       re.MULTILINE)
_FLIP_RE = re.compile(r"^\s*#{0,6}\s*\**FLIP\s+(\d+)\**\s*:\**\s*", re.MULTILINE)


def parse(text, n_slots):
    """Split the transcript on its labels. Everything up to the next label is the answer.

    ⚠ AN EMPTY FIELD AND AN UNPARSED FIELD ARE NOT THE SAME THING. The floors' seat runner learned
    this the expensive way — its parser matched the QUESTION line rather than the answer below it,
    every field came back holding the restated question, and it reported a valid round VOID. So a
    label that appears in the transcript but yields nothing is an ERROR here, never an absence.
    """
    out = {}
    marks = [(m.start(), m.end(), m.group(1)) for m in _LABEL_RE.finditer(text)]
    flips = [(m.start(), m.end(), int(m.group(1))) for m in _FLIP_RE.finditer(text)]
    allmarks = sorted([(s, e, ("L", n)) for s, e, n in marks]
                      + [(s, e, ("F", n)) for s, e, n in flips])
    per_flip = {}
    for i, (s0, e0, key) in enumerate(allmarks):
        end = allmarks[i + 1][0] if i + 1 < len(allmarks) else len(text)
        body = text[e0:end].strip()
        lines = body.splitlines()
        if lines and lines[0].rstrip("* ").endswith("?"):
            body = "\n".join(lines[1:]).strip()
        kind, name = key
        if kind == "L":
            if name not in out or len(body) > len(out[name]):
                out[name] = body
        else:
            per_flip.setdefault(name, "")
            if len(body) > len(per_flip[name]):
                per_flip[name] = body
    for k in LABELS:
        out.setdefault(k, "")

    for name in ("RANK", "SHIP", "WORST"):
        if not out[name] and re.search(r"\b%s\b" % name, text):
            raise ValueError(
                "PARSE FAILURE: the transcript mentions %s and nothing was extracted for it. "
                "Treating that as an absent answer is how a valid round gets thrown away." % name)

    out["_flip_blocks"] = {k: [l.strip()[2:].strip() for l in v.splitlines()
                               if l.strip().startswith("- ")]
                           for k, v in per_flip.items()}
    out["_rank"] = [int(x) for x in re.findall(r"\d+", out["RANK"])
                    if 1 <= int(x) <= n_slots]
    out["_ship"] = ([] if re.search(r"\bNONE\b", out["SHIP"], re.I)
                    else [int(x) for x in re.findall(r"\d+", out["SHIP"])
                          if 1 <= int(x) <= n_slots])
    out["_flagged"] = ([] if re.search(r"\bNONE\b", out["FLAGGED"], re.I)
                       else [int(x) for x in re.findall(r"\d+", out["FLAGGED"])
                             if 1 <= int(x) <= n_slots])
    out["_worst"] = next((int(x) for x in re.findall(r"\d+", out["WORST"])
                          if 1 <= int(x) <= n_slots), None)
    return out


# THE PLANT RULE, WRITTEN DOWN BEFORE THE FIRST ROUND AND NOT NEGOTIABLE AFTERWARDS.
#
#     The plant must land WORST or FLAGGED, and must not be in SHIP.
#
# It needs no vocabulary list, and that is the point of moving to a picture. The floors' generated
# plant needed one — a hand-maintained list of ruin words — and it went wrong in every direction a
# list can: it carried "lichen", which no plant ever contained, and it lacked "hole", the plainest
# word for the plant's most prominent feature, for three rounds. A list derived by reading
# transcripts is a test derived from its own outcome. A rank has no vocabulary.
#
# ⚠ WHAT THIS RULE DOES NOT TEST, recorded on the first live round rather than discovered later.
#
# The plant tests for SOFTNESS — a seat that would ship a frame the human gate rejected. It does
# NOT test ordering, and the first real round showed why the distinction has to be written down:
# the seat flagged all three frames, shipped none, and ranked THE PLANT FIRST. The plant was
# caught (it declined to ship a culled frame, which is the claim) and the round stood — but the
# ranking is the more interesting fact in it, and a rule that only emitted CAUGHT would have
# thrown it away.
#
# A plant that outranks the build is a statement ABOUT THE BUILD: it is sitting below a frame
# that was already rejected once. So it is recorded as `outranked_build` and reported, rather
# than folded into the verdict. LOOP-PROCESS §8: a bar found wanting mid-run is held frozen,
# cleared honestly, and impeached in the same report — never re-tuned after the answer is seen.
def plant_caught(r, plant_slot, build_slot, approved_slot=None):
    ranked_last = bool(r["_rank"]) and r["_rank"][-1] == plant_slot
    worst = r["_worst"] == plant_slot
    flagged = plant_slot in r["_flagged"]
    shipped = plant_slot in r["_ship"]
    rank = r["_rank"]
    outranked = (plant_slot in rank and build_slot in rank
                 and rank.index(plant_slot) < rank.index(build_slot))
    # ── THE APPROVED FRAME'S OWN RANK (RULED, Rafe, 2026-09-03) ───────────────────────────────
    #
    # The plant answers ONE question — would this seat ship something already culled — and §4 is
    # explicit that RANK does not reproduce Rafe's culls. The approved frame answers a different
    # and much narrower question, and it is one a rank CAN answer: **is this better than the last
    # thing a person said yes to?** A build the seat puts below that frame has gone backwards
    # against a human verdict, whatever else it does.
    outranked_by_approved = bool(approved_slot and rank and approved_slot in rank
                                 and build_slot in rank
                                 and rank.index(approved_slot) < rank.index(build_slot))
    return ((ranked_last or worst or flagged) and not shipped,
            dict(ranked_last=ranked_last, named_worst=worst, flagged=flagged, shipped=shipped,
                 outranked_build=outranked,
                 outranked_by_approved=outranked_by_approved, approved_slot=approved_slot,
                 every_frame_flagged=(len(r["_flagged"]) == len(rank) and bool(rank))))


# ================================ the round ===================================================
def capture(cfg, echo=True):
    """Run the configured capture and hand back the frame it produced.

    The command lives in docs/FRAME-CRITIC.json rather than here so this skill stays
    content-agnostic — it judges frames, it does not know how a wall is composed. What it DOES
    enforce is that the command actually produced a new frame: a stale PNG left over from a
    previous build is the exact evidence failure §2.3 exists for, and a capture step that silently
    does nothing is §4.2's.
    """
    frame = os.path.join(REPO, cfg["capture"]["frame"])
    before = None
    if os.path.exists(frame):
        before = (os.path.getmtime(frame), hashlib.sha256(open(frame, "rb").read()).hexdigest())
    cmd = cfg["capture"]["cmd"]
    if echo:
        print("== capture: %s" % " ".join(cmd))
        for k, v in (cfg["capture"].get("env") or {}).items():
            print("   env %s=%s" % (k, v))
    env = dict(os.environ)
    env.update(cfg["capture"].get("env") or {})
    r = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
        raise SystemExit("REFUSING: the capture command exited %d. There is no frame to judge."
                         % r.returncode)
    if not os.path.exists(frame):
        raise SystemExit("REFUSING: the capture ran and %s does not exist." % frame)
    after = (os.path.getmtime(frame), hashlib.sha256(open(frame, "rb").read()).hexdigest())
    if before is not None and after[0] <= before[0]:
        raise SystemExit(
            "REFUSING: %s was not rewritten by the capture command.\n"
            "A frame left over from an earlier build judged as this one is exactly the evidence\n"
            "failure LOOP-PROCESS §2.3 forbids." % cfg["capture"]["frame"])
    print("   frame: %s  sha256 %s" % (cfg["capture"]["frame"], after[1][:16]))
    # EVERY FLAG THE FRAME WAS TAKEN WITH, in the round's own output. The wrapper command above
    # names a script; the flags are what decide whether the floor is magenta, whether the walls
    # are the tier-0 mocks, and whether the orc layer is present at all — and a capture missing
    # one of those is a plausible-looking wrong picture. capture_corridor.py writes the resolved
    # invocation as the first line of its log; it is echoed here and the log ships with the round.
    log = cfg["capture"].get("log")
    if log and os.path.exists(os.path.join(REPO, log)):
        with open(os.path.join(REPO, log)) as f:
            print("   flags: %s" % f.readline().strip())
        print("   log:   %s" % log)
    return frame, after[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--lane", help="which line of rounds this is. Defaults to the git branch, "
                                   "so a session restart lands on the same counters.")
    ap.add_argument("--no-capture", action="store_true",
                    help="judge the frame already on disk instead of taking a new one. For "
                         "replaying a round, never for gating a build.")
    ap.add_argument("--build-frame", help="override the build frame. Used by the plant "
                                          "self-test, which puts a morgue capture in the "
                                          "build's slot and requires the seat to flag it.")
    ap.add_argument("--timeout", type=int, default=2400)
    # ── SHOWING THE GUARDS THEY CAN FIRE, WITHOUT REIMPLEMENTING THEM ────────────────────────
    # LOOP-PROCESS §4 / bible §13.5: no check's pass counts until it has demonstrated it can
    # fail. These three flags exist so the guards can be driven against a fixture history and
    # shown to STOP — running THE SAME `guards()` and `write_stall()` the real path runs.
    # `verify_on_device.sh --check-log` is the precedent and states the reason: a test that
    # reimplements the thing it tests proves the reimplementation.
    ap.add_argument("--history", help="read verdicts from this directory instead of history/")
    ap.add_argument("--stall-out", help="write the stall report here instead of the repo root")
    ap.add_argument("--check-guards", action="store_true",
                    help="evaluate the loop guards against --history and exit. No round runs, "
                         "no seat is spent, nothing is captured.")
    a = ap.parse_args()

    if not os.path.exists(a.config):
        raise SystemExit("REFUSING: no %s. The critic does not guess what to capture." % a.config)
    cfg = json.load(open(a.config))
    morgue = json.load(open(os.path.join(MORGUE, "MORGUE.json")))
    verify_morgue(morgue)

    lane = a.lane or (BID._git("rev-parse", "--abbrev-ref", "HEAD").strip() or "detached")
    # A SELF-TEST NEVER LANDS IN A REAL LANE'S HISTORY. Its verdict is about the judge, not about
    # a build, and letting one count toward the loop guards would mean a deliberately-failed
    # round pushing a real lane toward a STOP — or, worse, a deliberately-passed one clearing a
    # streak that was earned.
    if a.build_frame and not lane.endswith("-selftest"):
        lane += "-selftest"
    hist = history(a.history)

    # ── THE GUARDS RUN BEFORE THE ROUND, NOT AFTER IT ─────────────────────────────────────────
    # A guard checked only after a fresh round has run is a guard that always pays for one more
    # round. Worse, "never run additional rounds past a broken judge" cannot be honoured by a
    # check that happens at the end of the additional round.
    name, why = guards(hist, lane)
    if name:
        p = write_stall(name, why, hist, lane, cfg, a.stall_out)
        print("\n*** STOP — %s ***\n%s\n\nwritten: %s\n"
              % (name, why, os.path.relpath(p, REPO)))
        print("This is a LOOP-PROCESS §1.1.4 ruling trigger. The line does not restart itself.")
        return 3
    if a.check_guards:
        print("no guard fired for lane %r over %d verdict(s) in %s"
              % (lane, len([v for v in hist if lane_of(v) == lane]), a.history or HISTORY))
        return 0

    rnd = 1 + len([v for v in hist if lane_of(v) == lane])
    print("=" * 78)
    print("FRAME CRITIC — lane %s, round %d" % (lane, rnd))
    print("  commit   %s" % BID.head())
    print("=" * 78)

    # ── the build's frame ─────────────────────────────────────────────────────────────────────
    if a.build_frame:
        frame = os.path.join(REPO, a.build_frame) if not os.path.isabs(a.build_frame) \
            else a.build_frame
        fsha = hashlib.sha256(open(frame, "rb").read()).hexdigest()
        print("== BUILD FRAME OVERRIDDEN: %s  sha256 %s" % (a.build_frame, fsha[:16]))
        print("   This round is a SELF-TEST of the judge, not a verdict on a build.")
    elif a.no_capture:
        frame = os.path.join(REPO, cfg["capture"]["frame"])
        fsha = hashlib.sha256(open(frame, "rb").read()).hexdigest()
        print("== capture skipped; judging %s as it sits (sha256 %s)"
              % (cfg["capture"]["frame"], fsha[:16]))
    else:
        frame, fsha = capture(cfg)

    # ── THE BUILD ID IS TAKEN AFTER THE CAPTURE, NOT BEFORE ───────────────────────────────────
    # The capture writes a PNG and a log into the tree, so an id taken beforehand is stale by the
    # time the verdict records it — and the gate, which recomputes it, would then refuse a build
    # that had passed. Same class of self-reference as the one `prove_gate.py` found in
    # build_id.py: the act of producing the evidence moved the thing the evidence names.
    bid, bdetail = BID.build_id()
    print("   build id %s%s" % (bid, "  (+dirty)" if bdetail["dirty"] else ""))

    # ── the deck ──────────────────────────────────────────────────────────────────────────────
    # Shuffled, so the seat cannot learn a slot. Seeded from the build id and the round, so the
    # shuffle is reproducible from the verdict file alone — a deck nobody can reconstruct is a
    # verdict nobody can check.
    # A self-test puts a morgue frame in the BUILD slot. It must not also be drawn as the plant —
    # the seat would be shown the same picture twice and the control would be judging itself.
    exclude = (os.path.basename(a.build_frame),) if a.build_frame else ()
    candidates = pick_plant(cfg["surface"], morgue, exclude=exclude, axis=cfg.get("axis"))
    rng = random.Random(hashlib.sha256(("%s|%d" % (bid, rnd)).encode()).hexdigest())
    plant = rng.choice(candidates)

    work = os.path.join(os.path.expanduser(cfg.get("work_dir",
                        "~/.claude/frame-critic")), "%s-r%d" % (lane, rnd))
    if os.path.commonpath([os.path.realpath(work), os.path.realpath(REPO)]) \
            == os.path.realpath(REPO):
        raise SystemExit("REFUSING: work_dir is inside the repo. §3.1 — the seat's cwd is "
                         "outside it, so the seat cannot read its way to the answer.")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    crop = cfg.get("crop")
    deck = [("build", frame, crop),
            ("plant", os.path.join(MORGUE, plant["file"]), crop)]
    if cfg.get("approved_capture"):
        deck.append(("approved", os.path.join(REPO, cfg["approved_capture"]["path"]), crop))
    bar = cfg.get("asset_bar")
    if bar:
        # §13.3: measurements leave, pixels never do. The bar crop is written into the seat's
        # working directory OUTSIDE the repo and nowhere else.
        deck.append(("bar", bar["image"], bar.get("crop")))
    rng.shuffle(deck)

    mapping, plant_slot, build_slot, approved_slot = {}, None, None, None
    for i, (what, path, box) in enumerate(deck, start=1):
        size = crop_to(path, box, os.path.join(work, "%d.png" % i))
        mapping[str(i)] = dict(what=what, source=os.path.relpath(path, REPO)
                               if path.startswith(REPO) else path,
                               sha256=hashlib.sha256(open(path, "rb").read()).hexdigest(),
                               crop=box, delivered=list(size))
        if what == "plant":
            plant_slot = i
        if what == "build":
            build_slot = i
        if what == "approved":
            approved_slot = i

    print("\n== deck (%d frames, shuffled, unlabelled) — cwd %s" % (len(deck), work))
    for i in sorted(mapping, key=int):
        print("   %s.png  %-9s %s" % (i, mapping[i]["what"], mapping[i]["source"]))
    print("   plant: %s — %s" % (plant["file"], plant["verbatim"]))
    if cfg.get("axis"):
        print("   axis:  %s   (the plant is drawn to be wrong on THIS axis)" % cfg["axis"])

    prompt = open(os.path.join(HERE, "seat_prompt.txt")).read().replace(
        "the numbered PNG files in this directory",
        "the files %s in this directory" % ", ".join("%d.png" % i
                                                     for i in range(1, len(deck) + 1)))

    print("\n== seat running (fresh claude -p, no repo access)...")
    text = run_seat(work, prompt, a.timeout)
    tpath = os.path.join(HISTORY, "r%03d-%s-transcript.txt" % (rnd, lane.replace("/", "_")))
    os.makedirs(HISTORY, exist_ok=True)
    with open(tpath, "w") as f:
        f.write(text)

    try:
        r = parse(text, len(deck))
    except ValueError as e:
        print("\n%s" % e)
        print("transcript: %s" % os.path.relpath(tpath, REPO))
        return 4

    caught, how = plant_caught(r, plant_slot, build_slot, approved_slot)
    flips = r["_flip_blocks"].get(build_slot, [])

    if not caught:
        verdict = "VOID"
    elif how.get("outranked_by_approved"):
        # RULED 2026-09-03: a build that ranks below the last Rafe-approved frame cannot PASS.
        # "A build that reads greyer or flatter than it cannot rank BEST; this is why r003 passed
        # the critic while failing Rafe's eye." FAIL, not VOID — nothing is wrong with the judge.
        verdict = "FAIL"
    elif build_slot in r["_ship"] and build_slot not in r["_flagged"]:
        verdict = "PASS"
    else:
        verdict = "FAIL"

    print("\n== the seat said")
    print("   RANK    %s" % (r["RANK"] or "(unparsed)")[:120])
    print("   SHIP    %s" % (r["SHIP"] or "(unparsed)")[:120])
    print("   FLAGGED %s" % (r["FLAGGED"] or "(unparsed)")[:120])
    print("   WORST   %s — %s" % (r["WORST"] or "?", " ".join(r["WORST_WHY"].split())[:110]))
    print("   BEST    %s — %s" % (r["BEST"] or "?", " ".join(r["BEST_WHY"].split())[:110]))
    print("\n   plant was slot %s: ranked_last=%s named_worst=%s flagged=%s shipped=%s -> %s"
          % (plant_slot, how["ranked_last"], how["named_worst"], how["flagged"], how["shipped"],
             "CAUGHT" if caught else "MISSED"))
    print("   build was slot %s" % build_slot)
    if approved_slot:
        print("   approved reference was slot %s (%s) — %s"
              % (approved_slot, cfg["approved_capture"].get("build", "?"),
                 "BUILD IS ABOVE IT" if not how["outranked_by_approved"]
                 else "BUILD IS BELOW IT"))
    if how.get("outranked_by_approved"):
        print("\n   ⚠ THE BUILD RANKS BELOW THE LAST APPROVED FRAME. This is a REGRESSION")
        print("     against a verdict a person already gave, and unlike the plant's ordering it")
        print("     IS part of the verdict (RULED 2026-09-03). The build cannot pass below the")
        print("     last thing Rafe said yes to.")
    if how["outranked_build"]:
        print("\n   ⚠ THE PLANT OUTRANKED THE BUILD. A blind seat put a frame Rafe personally")
        print("     culled — \"%s\" — above this one." % plant["verbatim"])
        print("     That is a statement about the build, not about the judge, and it is not")
        print("     part of the verdict. It is the most important line in this round.")
    if how["every_frame_flagged"]:
        print("   note: the seat flagged EVERY frame, including the commercial bar. The plant")
        print("         check still holds (it declined to ship a culled frame) but the flag")
        print("         carries no discrimination this round.")

    out = dict(
        schema="frame-critic/1",
        verdict=verdict,
        lane=lane,
        round=rnd,
        surface=cfg["surface"],
        commit=bdetail["commit"],
        dirty=bdetail["dirty"],
        build_id=bid,
        timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
        build_frame=dict(path=os.path.relpath(frame, REPO) if frame.startswith(REPO) else frame,
                         sha256=fsha,
                         # The log's first line is the resolved engine invocation — every flag the
                         # frame was taken with. §2.3: evidence carries its producer.
                         log=cfg["capture"].get("log") if not a.build_frame else None,
                         flags=(open(os.path.join(REPO, cfg["capture"]["log"])).readline().strip()
                                if (not a.build_frame and cfg["capture"].get("log")
                                    and os.path.exists(os.path.join(REPO,
                                                                    cfg["capture"]["log"])))
                                else None)),
        deck=dict(work_dir=work, slots=mapping, build=os.path.relpath(frame, REPO)
                  if frame.startswith(REPO) else frame),
        plant=dict(slot=plant_slot, file=plant["file"], sha256=plant["sha256"],
                   culled_by=plant["culled_by"], verbatim=plant["verbatim"],
                   caught=caught, how=how),
        seat={k: r[k] for k in LABELS},
        flip_list=flips,
        transcript=os.path.relpath(tpath, REPO),
        law=("LOOP-PROCESS: an art round is judged by eyes on delivered frames. The plant must "
             "land worst-or-flagged; a passed plant voids the round and its findings are not "
             "read."),
    )
    if a.build_frame:
        out["self_test"] = True
        out["verdict"] = verdict
    hpath = os.path.join(HISTORY, "r%03d-%s.json" % (rnd, lane.replace("/", "_")))
    with open(hpath, "w") as f:
        json.dump(out, f, indent=1)
    # A SELF-TEST DOES NOT WRITE CRITIC-VERDICT.json. It is a verdict about the JUDGE, taken on a
    # deck whose build slot held a morgue frame — so putting it at the repo root would overwrite a
    # real round's verdict with one that describes a different picture. The gate refuses a
    # self_test verdict as well, and both are wanted: the gate's check is what stops a stale one
    # opening it, and this is what stops a real one being destroyed.
    if not a.build_frame:
        with open(VERDICT, "w") as f:
            json.dump(out, f, indent=1)

    print("\n*** %s ***" % verdict)
    if verdict == "VOID":
        print("The seat would ship, or did not flag, a frame Rafe personally culled:")
        print("   %s — \"%s\"" % (plant["file"], plant["verbatim"]))
        print("LOOP-PROCESS §4: the round is void and its findings are NOT READ.")
    elif verdict == "FAIL":
        for fx in flips:
            print("   flip: %s" % fx)
    if not a.build_frame:
        print("\nwritten: %s" % os.path.relpath(VERDICT, REPO))
        print("         %s" % os.path.relpath(hpath, REPO))
    else:
        print("\nwritten: %s" % os.path.relpath(hpath, REPO))
        print("         (a self-test writes no CRITIC-VERDICT.json — it judges the judge)")

    # And check the guards again with this round folded in, so a STOP is written the moment it is
    # earned rather than one round later.
    name, why = guards(history(a.history), lane)
    if name:
        p = write_stall(name, why, history(a.history), lane, cfg, a.stall_out)
        print("\n*** STOP — %s ***\n%s\n\nwritten: %s"
              % (name, why, os.path.relpath(p, REPO)))
        print("LOOP-PROCESS §1.1.4 ruling trigger. Ending the turn for Rafe.")
        return 3

    return {"PASS": 0, "FAIL": 1, "VOID": 2}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
