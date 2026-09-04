#!/usr/bin/env python3
"""THE FRAME CRITIC — an art round is judged by eyes on delivered frames, and by nothing else.

    .claude/skills/frame-critic/run_frame_critic.sh

WHAT THIS IS
------------
A fresh blind `claude -p` seat is shown a small deck of finished frames — this build's capture,
the asset bar, the last frame Rafe approved, and ONE PICTURE-PLANT drawn from the morgue — and
asked to rank them, say which it would ship, and flag anything with an obvious defect. The deck
is shuffled and unlabelled. The seat gets no code, no coordinates, no thresholds, no bible.

    PASS   the seat would ship this frame, flagged no defect in it, AND ranked it at or above
           the last Rafe-approved frame and near the asset bar (§5's visual bar as a rank).
           Reachable at any round; the guards below never gate it.
    FAIL   any of those missing; the flip list is recorded verbatim
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

THE LOOP GUARDS — this must never grind, and it must not stop a lane that is working
------------------------------------------------------------------------------------
THEY MEASURE PROGRESS, NOT ROUNDS. The five-round park counted rounds, which is the wrong
quantity in both directions at once: five rounds that are getting somewhere should keep going,
and two that are not should already have stopped.

The signal is the one every round already produces at no extra cost — WHERE THE BUILD RANKED in
the blind shuffled deck against the bar, the last approved frame and the plant. It is a judgement
about the picture, and the seat cannot see it coming: it is never told the round number, the
history, or that anything is being tracked. Even the working directory it sits in is named by a
hash now, because it used to be named `<lane>-r7`.

    BROKEN JUDGE  the plant missed twice consecutively -> STOP, and never ship past one
    NO CHANGE     two consecutive FAILs whose delivered frames are within NO_CHANGE_MAD /
                  NO_CHANGE_MAX luminance levels of each other -> STOP. The fix did not
                  reach the picture at all.
    THRASH        the same flip item across two consecutive FAILs AND no movement in rank
                  -> STOP
    STALL         STALL_ROUNDS readable rounds with no new best rank -> STOP
    CEILING       ROUND_CEILING rounds, absolute backstop -> STOP

    TWO STRIKES   the same flip item across two consecutive FAILs, rank movement ignored.
                  ADVISORY — reported and recorded, never a stop. It is the builder's
                  judgement overlay: a flip item can survive a round the build won on every
                  other axis, and stopping there sends a ruling about a lane that is working.

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

# ── THE GUARDS' NUMBERS, DECLARED HERE BEFORE ANY ROUND RUNS ──────────────────────────────────
# LOOP-PROCESS §8: a bar is never re-tuned after the answer is seen. These are the bar.
#
# THE GUARDS MEASURE PROGRESS NOW, NOT ROUNDS. The five-round park counted rounds, which is the
# wrong quantity: five rounds that are getting somewhere should keep going, and two that are not
# should already have stopped. A round cap can only be wrong in both directions at once.
#
# The signal is the one the round already produces: WHERE THE BUILD RANKED in a blind shuffled
# deck against the asset bar, the last Rafe-approved frame, and the plant. It costs nothing extra,
# it is a judgement about the picture rather than about the apparatus, and the seat cannot see it
# coming — it is never told the round number, the history, or that anything is being tracked.
STALL_ROUNDS = 3         # readable rounds with no new best rank, before the line stops
ROUND_CEILING = 15       # absolute backstop, all rounds counted including void ones
JUDGE_MISSES = 2         # consecutive plant misses before the judge is called broken
TWO_STRIKES = 2          # consecutive FAILs carrying the same flip item — ADVISORY, see guards()
FLIP_SAME = 0.60         # Jaccard over content words at which two flip items are "the same item"

# The no-change floor lives with the signature it is measured on — see SIG_GRID below. Two
# captures within it are the same picture, and a FAIL round on the same picture as the last FAIL
# round is a round that was never going to say anything new: §4.2's shape exactly, a fix that
# runs, changes nothing, and says so quietly.

# How far below the asset bar still counts as "near the bar" for a PASS. LOOP-PROCESS §5 asks
# *which of these looks like the shipped game* and requires the answer to be *Yarl or a tie*; the
# deck forbids ties, so one place below the bar is the closest representable tie. Declared before
# any round and not widened after (§8).
NEAR_BAR_SLACK = 1

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


# ================================ the progress signal ==========================================
#
# WHY RANK AND NOT A ROUND COUNT. A round count knows nothing about the work. Rank is the seat's
# own answer to the only question that matters — *of these finished pictures, where does ours
# sit* — and it is already produced by every round at no extra cost.
#
# ⚠ AND IT IS A COARSE SIGNAL, WHICH IS WHY IT GUARDS AND DOES NOT JUDGE. This mechanism's own
# evidence (§1.2.1, four rounds) is that a blind seat's ordering does not reproduce Rafe's culls:
# seats put a culled frame above the current build three times, and ranked another culled frame
# best of three. So rank decides when to STOP AND ASK — a question, never a shipping decision —
# while the verdict itself still rests on SHIP.
def rank_score(pos, n):
    """1.0 when the build ranked first, 0.0 when last. Normalised so a 3-frame deck and a
    4-frame deck are comparable — the deck grows by one the day Rafe names an approved capture,
    and a raw position would silently look like a regression that morning."""
    if not pos or n < 2:
        return None
    return (n - pos) / float(n - 1)


def prog(v):
    return v.get("progress") or {}


def readable(lane_hist):
    """The rounds whose findings may be read. A VOID round's rank is not evidence about the
    build — §4 says its findings are not read, and that has to include its rank."""
    return [v for v in lane_hist if v.get("verdict") != "VOID"]


# ── THE CAPTURE SIGNATURE, so "did this build change" is answerable a round later ─────────────
#
# sha256 answers only "byte-identical". The frames themselves are overwritten by the next round,
# so a distance has to be computable from something small enough to live in the verdict file: a
# SIG_GRID x SIG_GRID grid of mean luminance over the DELIVERED, CROPPED frame — the same pixels
# the seat was shown.
#
# ⚠ IT WAS A PERCEPTUAL HASH FIRST, AND THE HASH COULD NOT SEE THE THING IT WAS FOR. A 256-bit
# dHash put `washed-slab-lane.png` and `tile-quantized-wear.png` — two consecutive real builds
# that Rafe culled for two DIFFERENT defects — **2 bits apart, which was the whole declared
# floor.** The guard would have stopped that lane on a round where the art genuinely moved.
# Raising the hash resolution did not help: the gap held at 0.4-0.9% of bits from 256 up to 4096,
# because a gradient-sign hash asks *is this the same scene* and the answer was yes. It is the
# wrong question. Measured before the guard shipped rather than discovered by a false STOP.
#
# A magnitude answers it. Over the same three frames:
#
#     identical                       MAD 0.000   max 0
#     lane -> tile-quantized wear     MAD 1.942   max 36
#     wear -> keyline                 MAD 1.200   max 38
#
# TWO NUMBERS, NOT ONE, AND BOTH MUST BE SMALL TO FIRE. Mean absolute difference alone would miss
# a change confined to a corner of the frame — one tile of ninety moving twenty levels contributes
# about 0.2 to the mean — and a corner is exactly where a seat looks. The max-cell term is what
# stops a small, real, local change being called no change at all.
SIG_GRID = 32            # cells per side; 1024 cells, stable across grid size (measured)
NO_CHANGE_MAD = 0.25     # mean absolute luminance difference, levels. 5x below the smallest
                         # real round-over-round change measured, and determinism produces 0.
NO_CHANGE_MAX = 4        # worst single cell, levels. 9x below the smallest measured.


def signature(path, box, n=SIG_GRID):
    im = Image.open(path).convert("L")
    if box:
        im = im.crop(tuple(box))
    return bytes(im.resize((n, n), Image.BOX).getdata()).hex()


def sig_delta(a, b):
    """(mean absolute difference, worst cell) in luminance levels, or None."""
    if not a or not b or len(a) != len(b):
        return None
    x, y = bytes.fromhex(a), bytes.fromhex(b)
    d = [abs(p - q) for p, q in zip(x, y)]
    return (sum(d) / float(len(d)), max(d))


def unchanged(a, b):
    d = sig_delta(a, b)
    return (d is not None and d[0] <= NO_CHANGE_MAD and d[1] <= NO_CHANGE_MAX), d


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


def shared_flip(a, b):
    """The first flip item these two rounds are both asking for, or None."""
    for x in a.get("flip_list", []):
        for y in b.get("flip_list", []):
            if same_flip(x, y):
                return (x, y)
    return None


def two_strikes_advisory(lane_hist):
    """THE BUILDER'S OVERLAY, and it is deliberately NOT a STOP.

    The same flip item surviving two consecutive FAILs used to stop the line on its own. That was
    too eager in a way worth naming: a flip item can legitimately survive a round in which the
    build got materially better on every other axis, and stopping there sends a ruling to Rafe
    about a lane that is working.

    So it is computed, reported and recorded — the builder reads it and decides — while the
    mechanical STOP is `thrash`, which is this AND no movement in rank. Same substance, one extra
    condition, and the condition is exactly the thing that distinguishes a stuck lane from a busy
    one.
    """
    fails = [v for v in lane_hist if v.get("verdict") == "FAIL"]
    if len(fails) < TWO_STRIKES:
        return None
    a, b = fails[-2], fails[-1]
    if lane_hist.index(b) != lane_hist.index(a) + 1:
        return None                      # an intervening PASS or VOID breaks the streak
    pair = shared_flip(a, b)
    if not pair:
        return None
    return dict(rounds=[a.get("round"), b.get("round")], items=list(pair))


def guards(hist, lane):
    """Which guard, if any, has fired. Returns (name, explanation) or (None, None).

    Checked over the lane's verdicts as they sit on disk, BEFORE the run is reported, so a session
    that restarts mid-stall walks into the same wall it walked into before.

    ORDER MATTERS AND IS NOT ARBITRARY:
      broken-judge  first — nothing past it is readable, so every other guard would be reasoning
                    about rounds whose findings §4 forbids reading.
      no-change     next — it is the cheapest true statement available: the same picture twice.
      thrash        then — the same request twice, and no movement.
      stall         then — no new best for STALL_ROUNDS readable rounds.
      ceiling       last — the backstop, which should never be the one that fires. If it is, the
                    three above did not see something they should have, and that is worth
                    knowing.
    """
    lane_hist = [v for v in hist if lane_of(v) == lane]
    read = readable(lane_hist)

    # ── broken judge ──────────────────────────────────────────────────────────────────────────
    tail = lane_hist[-JUDGE_MISSES:]
    if len(tail) >= JUDGE_MISSES and all(v.get("verdict") == "VOID" for v in tail):
        return ("broken-judge",
                "the picture-plant was missed %d rounds running. The judging layer is broken; "
                "no round past it is readable and nothing ships past it." % JUDGE_MISSES)

    # ── no change ─────────────────────────────────────────────────────────────────────────────
    # Two consecutive FAILs on the same picture. Not "the fix did not work" — the fix did not
    # reach the frame at all, which is a different problem and needs a different answer.
    if len(read) >= 2:
        a, b = read[-2], read[-1]
        if a.get("verdict") == "FAIL" and b.get("verdict") == "FAIL":
            same, d = unchanged(prog(a).get("capture_signature"),
                                prog(b).get("capture_signature"))
            if same:
                same_bytes = (a.get("build_frame", {}).get("sha256")
                              == b.get("build_frame", {}).get("sha256"))
                return ("no-change",
                        "rounds %s and %s are the same picture — mean %.3f and worst cell %d\n"
                        "    luminance levels apart over the delivered frame%s, against floors of\n"
                        "    %.2f and %d, and both FAIL. Whatever was changed between them did not\n"
                        "    reach the capture."
                        % (a.get("round"), b.get("round"), d[0], d[1],
                           ", byte-identical" if same_bytes else "",
                           NO_CHANGE_MAD, NO_CHANGE_MAX))

    # ── thrash ────────────────────────────────────────────────────────────────────────────────
    adv = two_strikes_advisory(lane_hist)
    if adv:
        a = next(v for v in lane_hist if v.get("round") == adv["rounds"][0])
        b = next(v for v in lane_hist if v.get("round") == adv["rounds"][1])
        sa, sb = prog(a).get("rank_score"), prog(b).get("rank_score")
        if sa is not None and sb is not None and sb <= sa:
            return ("thrash",
                    "the same flip item survived two consecutive FAIL rounds AND the build did\n"
                    "    not move in the deck (rank score %.2f -> %.2f):\n"
                    "    round %s: %s\n    round %s: %s"
                    % (sa, sb, adv["rounds"][0], adv["items"][0],
                       adv["rounds"][1], adv["items"][1]))

    # ── stall ─────────────────────────────────────────────────────────────────────────────────
    # A new best is the only thing that counts as progress. Matching the best is not progress; it
    # is a lane holding still, and holding still for three readable rounds is the signal.
    scored = [v for v in read if prog(v).get("rank_score") is not None]
    if len(scored) > STALL_ROUNDS:
        best, since, at = None, 0, None
        for v in scored:
            s = prog(v)["rank_score"]
            if best is None or s > best:
                best, since, at = s, 0, v.get("round")
            else:
                since += 1
        if since >= STALL_ROUNDS:
            return ("stall",
                    "%d readable rounds with no new best rank. The best is %.2f, set at round\n"
                    "    %s, and nothing since has beaten it. The lane is not converging."
                    % (since, best, at))

    # ── ceiling ───────────────────────────────────────────────────────────────────────────────
    if len(lane_hist) >= ROUND_CEILING:
        return ("ceiling",
                "%d rounds on this lane. This is the backstop and it should never be the guard\n"
                "    that fires — if it did, the progress guards did not see something they\n"
                "    should have, and that is itself worth a ruling." % len(lane_hist))
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
    # The explanations are indented for the terminal. Markdown would render the continuation
    # lines as part of the paragraph anyway, but a leading run of spaces is one blank line away
    # from becoming a code block, so it is stripped rather than trusted.
    L.append("\n".join(l.strip() for l in why.splitlines()) + "\n")
    L.append("## What was tried, round by round\n")
    L.append("`rank` is where the build placed in that round's blind shuffled deck, and `score` "
             "normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. "
             "`Δpic` is how far the delivered frame moved from the previous round: mean and worst "
             "cell, in luminance levels. `0.000 / 0` means the picture did not change at all.\n")
    L.append("| round | verdict | rank | score | best? | Δpic | build | the seat's own words |")
    L.append("|---|---|---|---|---|---|---|---|")
    best = None
    prev_sig = None
    for v in lane_hist:
        p = prog(v)
        s = p.get("rank_score")
        isbest = ""
        if s is not None and v.get("verdict") != "VOID":
            if best is None or s > best:
                best, isbest = s, "**new best**"
        d = sig_delta(prev_sig, p.get("capture_signature"))
        if p.get("capture_signature"):
            prev_sig = p["capture_signature"]
        worst = (v.get("seat", {}).get("WORST_WHY") or "").replace("|", "/")
        L.append("| %s | %s | %s | %s | %s | %s | `%s` | %s |"
                 % (v.get("round"), v.get("verdict"),
                    ("%s/%s" % (p.get("rank_position"), p.get("deck_size"))
                     if p.get("rank_position") else "—"),
                    ("%.2f" % s) if s is not None else "—",
                    isbest, "—" if d is None else "%.3f / %d" % d,
                    (v.get("build_id") or "")[:12],
                    " ".join(worst.split())[:140]))
    L.append("")
    L.append("## The flip lists, verbatim\n")
    L.append("Void rounds do not appear here. §4: the plant was missed, so those findings are not "
             "read — they are kept in the verdict under `flip_list_withheld` and are not "
             "evidence.\n")
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
    plant last, and the round voided on the judge rather than on the art. **The right image for
    the wrong question is not a control.**

    An entry with no `axis` answers any question, so the morgue stays usable while it is being
    tagged, and a surface whose entries carry no matching axis falls back to all of them rather
    than refusing — a narrower plant is better than no round, but no plant is not an option.
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
def plant_caught(r, plant_slot, build_slot):
    ranked_last = bool(r["_rank"]) and r["_rank"][-1] == plant_slot
    worst = r["_worst"] == plant_slot
    flagged = plant_slot in r["_flagged"]
    shipped = plant_slot in r["_ship"]
    rank = r["_rank"]
    outranked = (plant_slot in rank and build_slot in rank
                 and rank.index(plant_slot) < rank.index(build_slot))
    return ((ranked_last or worst or flagged) and not shipped,
            dict(ranked_last=ranked_last, named_worst=worst, flagged=flagged, shipped=shipped,
                 outranked_build=outranked,
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

    # ── THE SEAT MUST NOT BE ABLE TO READ THE ROUND NUMBER OFF ITS OWN CWD ────────────────────
    #
    # The directory used to be named `<lane>-r<n>`, which is the seat's working directory and
    # therefore visible to it. A seat that can see it is in round 7 is a seat that can infer a
    # history it was never shown, and the whole progress signal depends on the seat not knowing
    # anything is being tracked: rank has to be an unprompted judgement about the picture, not a
    # judgement about a campaign.
    #
    # Opaque, and reproducible from the verdict — which records the path.
    work = os.path.join(os.path.expanduser(cfg.get("work_dir", "~/.claude/frame-critic")),
                        "deck-" + hashlib.sha256(
                            ("%s|%d|%s" % (lane, rnd, bid)).encode()).hexdigest()[:16])
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

    mapping = {}
    plant_slot = build_slot = bar_slot = approved_slot = None
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
        if what == "bar":
            bar_slot = i
        if what == "approved":
            approved_slot = i

    print("\n== deck (%d frames, shuffled, unlabelled) — cwd %s" % (len(deck), work))
    for i in sorted(mapping, key=int):
        print("   %s.png  %-9s %s" % (i, mapping[i]["what"], mapping[i]["source"]))
    print("   plant: %s — %s" % (plant["file"], plant["verbatim"]))

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

    caught, how = plant_caught(r, plant_slot, build_slot)
    flips = r["_flip_blocks"].get(build_slot, [])

    # ── WHERE THE BUILD PLACED, which is this round's contribution to the progress signal ──────
    n = len(deck)
    rk = r["_rank"]
    pos = (rk.index(build_slot) + 1) if build_slot in rk else None
    score = rank_score(pos, n)
    bar_pos = (rk.index(bar_slot) + 1) if bar_slot and bar_slot in rk else None
    app_pos = (rk.index(approved_slot) + 1) if approved_slot and approved_slot in rk else None

    # ── THE COMPARATIVE HALF OF PASS — LOOP-PROCESS §5's visual bar, as a rank ─────────────────
    #
    # §5: *blind side-by-side against shipped commercial games, asking which of these looks like
    # the shipped game. The answer must be Yarl or a tie.* The deck forbids ties, so the closest
    # representable thing to a tie is one place below the bar, and that is what NEAR_BAR_SLACK
    # buys — declared here, before any round, and not widened afterwards (§8).
    #
    # AND THE BUILD MUST NOT SIT BELOW THE LAST FRAME RAFE APPROVED. A frame that ranks under the
    # baseline is a regression however well the seat speaks of it.
    beats_approved = (app_pos is None) or (pos is not None and pos <= app_pos)
    near_bar = (bar_pos is None) or (pos is not None and pos <= bar_pos + NEAR_BAR_SLACK)

    # ⚠ ASSUMPTION, STATED RATHER THAN BURIED. The amendment specifying these guards described
    # PASS as *"still = ranks at/above the last-approved frame and near the bar"*. On main PASS
    # was SHIP-based and said nothing about rank, so "still" cannot be read as *unchanged*. It is
    # taken here as *not loosened*: PASS is the CONJUNCTION of the rule that shipped and the
    # comparative rule above. That can only ever refuse more builds than either reading alone,
    # which is the safe direction for an install gate to be wrong in.
    #
    # If rank alone was meant, delete the two SHIP terms from the line below — it is one edit,
    # and it loosens the gate, so it is Rafe's to make rather than mine.
    if not caught:
        verdict = "VOID"
    elif (build_slot in r["_ship"] and build_slot not in r["_flagged"]
            and beats_approved and near_bar):
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
    if how["outranked_build"]:
        print("\n   ⚠ THE PLANT OUTRANKED THE BUILD. A blind seat put a frame Rafe personally")
        print("     culled — \"%s\" — above this one." % plant["verbatim"])
        print("     That is a statement about the build, not about the judge, and it is not")
        print("     part of the verdict. It is the most important line in this round.")
    if how["every_frame_flagged"]:
        print("   note: the seat flagged EVERY frame, including the commercial bar. The plant")
        print("         check still holds (it declined to ship a culled frame) but the flag")
        print("         carries no discrimination this round.")

    # ── the progress signal, and the whole series it belongs to ───────────────────────────────
    lane_hist = [v for v in hist if lane_of(v) == lane]
    prior = [prog(v).get("rank_score") for v in readable(lane_hist)]
    prior = [s for s in prior if s is not None]
    best_before = max(prior) if prior else None
    new_best = (score is not None and verdict != "VOID"
                and (best_before is None or score > best_before))
    prev = readable(lane_hist)
    prev_sig = prog(prev[-1]).get("capture_signature") if prev else None
    this_sig = signature(frame, crop)
    moved = sig_delta(prev_sig, this_sig)

    # The series carries the signature of every round, because the frames themselves are
    # overwritten by the next capture and a distance you cannot recompute is a distance you
    # cannot check.
    series = [dict(round=v.get("round"), verdict=v.get("verdict"),
                   rank_position=prog(v).get("rank_position"),
                   deck_size=prog(v).get("deck_size"),
                   rank_score=prog(v).get("rank_score"),
                   capture_signature=prog(v).get("capture_signature"))
              for v in lane_hist]
    series.append(dict(round=rnd, verdict=verdict, rank_position=pos, deck_size=n,
                       rank_score=score, capture_signature=this_sig))

    print("\n== progress")
    print("   rank      %s of %s   score %s%s"
          % (pos or "?", n, ("%.2f" % score) if score is not None else "?",
             "   <- NEW BEST" if new_best else ""))
    print("   best so far %s" % (("%.2f" % best_before) if best_before is not None else "(none)"))
    if bar_pos:
        print("   the bar ranked %s; near-bar %s (slack %d)"
              % (bar_pos, "YES" if near_bar else "NO", NEAR_BAR_SLACK))
    if app_pos:
        print("   the approved frame ranked %s; at-or-above %s"
              % (app_pos, "YES" if beats_approved else "NO"))
    else:
        print("   NO APPROVED FRAME IN THE DECK — that half of the bar is untested this round.")
    print("   picture moved %s from the previous readable round"
          % ("(first round)" if moved is None
             else "mean %.3f / worst %d luminance levels (floors %.2f / %d)"
                  % (moved[0], moved[1], NO_CHANGE_MAD, NO_CHANGE_MAX)))

    adv = two_strikes_advisory(lane_hist + [dict(lane=lane, round=rnd, verdict=verdict,
                                                 flip_list=flips)])
    if adv:
        print("\n   two-strikes (ADVISORY, not a stop): the same request has now survived rounds")
        print("     %s and %s — \"%s\"" % (adv["rounds"][0], adv["rounds"][1],
                                          " ".join(adv["items"][1].split())[:100]))
        print("     The line continues because rank moved. Builder's judgement whether it should.")

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
        # ── A VOID ROUND CARRIES NO READABLE FLIP LIST ────────────────────────────────────────
        #
        # §4: if the critic does not catch the plant the round is void and its findings are NOT
        # READ — not discounted, void. A soft critic's findings are worse than none because they
        # will be acted on.
        #
        # ⚠ AND THEY WERE BEING PUT IN FRONT OF A READER. `critic_gate.py` printed the flip list
        # for every non-PASS verdict, void included, on the most-read surface the mechanism has.
        # Found the first time a round actually voided. So the withholding lives in the DATA
        # rather than in each reader's manners: every consumer — the gate, the stall report, the
        # guards — is now correct by construction. The findings are kept, under a name that says
        # what they are, because deleting evidence is a different sin.
        flip_list=[] if verdict == "VOID" else flips,
        flip_list_withheld=(flips if verdict == "VOID" else None),
        withheld_because=("LOOP-PROCESS §4: the plant was missed, so this round's findings are "
                          "not read. Nothing here may be cited, quoted, or acted on."
                          if verdict == "VOID" else None),
        # ── THE PROGRESS SIGNAL, AND THE WHOLE SERIES, IN EVERY VERDICT ───────────────────────
        # The series is written into each round's own file rather than only being derivable by
        # walking history/. A counter a restart can clear is a suggestion with a number in it —
        # and so is one that lives only in a directory listing. Here it is in the diff, it is in
        # the verdict the PR carries, and it is in the stall report.
        progress=dict(
            rank_position=pos, deck_size=n, rank_score=score,
            bar_position=bar_pos, approved_position=app_pos,
            approved_frame_in_deck=bool(approved_slot),
            beats_approved=beats_approved, near_bar=near_bar,
            near_bar_slack=NEAR_BAR_SLACK,
            new_best=new_best, best_before=best_before,
            capture_signature=this_sig,
            moved=None if moved is None else dict(mad=moved[0], max_cell=moved[1]),
            two_strikes_advisory=adv,
            series=series,
            guards=dict(stall_rounds=STALL_ROUNDS, round_ceiling=ROUND_CEILING,
                        no_change_mad=NO_CHANGE_MAD, no_change_max=NO_CHANGE_MAX,
                        sig_grid=SIG_GRID, judge_misses=JUDGE_MISSES,
                        flip_same=FLIP_SAME),
        ),
        transcript=os.path.relpath(tpath, REPO),
        law=("LOOP-PROCESS: an art round is judged by eyes on delivered frames. The plant must "
             "land worst-or-flagged; a passed plant voids the round and its findings are not "
             "read. The guards measure progress — rank in the deck — never rounds elapsed."),
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
