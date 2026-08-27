#!/usr/bin/env python3
"""THE BLIND FLOOR SEAT — the gate on this session's remediation.

LOOP-PROCESS §1.1.1: nothing reaches the human gate that the blind critic would kill.
LOOP-PROCESS §3: the critic is a fresh `claude -p` with cwd OUTSIDE the repo. Not a subagent.
Blindness is structural rather than promised - the process cannot reach the repo, the bible, the
ledger, or any prior round. It sees a directory of PNGs and the seat prompt.
LOOP-PROCESS §2.1: what it sees is the LIT IN-SCENE CAPTURE at the reference device's pixel
size, never a contact sheet. A receive-light asset judged unlit is judged by the wrong
instrument.
LOOP-PROCESS §2.2: every capture declares its own scope. This round's scope is THE FLOOR; the
walls are byte-identical across the set and are declared out of scope in the prompt, because §3's
unresolved wall-thickness problem culled all five arms of the composition spike eight rounds
running and would swamp a floor verdict.

THE TWO ROUNDS, AND WHY BOTH ARE NEEDED - LOOP-PROCESS §4 / bible §13.5
-----------------------------------------------------------------------
No instrument's pass counts until it has demonstrated it can fail, and a check that fails
everything has demonstrated nothing either. The two rounds together are the control:

  ROUND A   the four survivor floors AS THEY SIT IN THE LEDGER, un-remediated.
            The seat must CULL them. This is the demonstration that the check can fail.

  ROUND B   the four remediated floors, PLUS ONE PLANT: the raw un-remediated B-KAB, the
            hardest-ringed tile in the corpus and one the seat has already culled in round A.
            The seat must pass all four and cull the plant.
            If the plant passes, ROUND B IS VOID and its verdicts are not read - not
            discounted, void.

A seat that culls everything satisfies round A and then fails round B's bar. A seat that passes
everything fails round A and is caught by round B's plant. Only a seat that discriminates can
satisfy both, which is what makes the pair a control rather than two opinions.

The rounds run as separate processes, the codes are anonymised and deliberately not in set
order, and nothing tells the seat which round it is in or what is expected.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CAPTURES = os.path.join(HERE, "evidence", "captures")
OUT = os.path.join(HERE, "evidence", "seat")
WORK_ROOT = ("/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
             "ee659c3f-f445-47fc-8679-e38f870d738a/scratchpad/floor_seat")

# code -> capture. Deliberately not in set order, so a seat cannot infer the grouping.
ROUNDS = {
    "A": (dict(F3="orig_A-HEB_lit.png", F1="orig_C-GAB_lit.png",
               F4="orig_A-VAB_lit.png", F2="orig_B-KAB_lit.png"),
          None),
    "B": (dict(F2="remed_C-GAB_lit.png", F5="remed_A-VAB_lit.png",
               F1="remed_B-KAB_lit.png", F4="orig_B-KAB_lit.png",
               F3="remed_A-HEB_lit.png"),
          "F4"),
}

HEDGE = ("fine", "acceptable", "good enough", "improved", "better than", "solid", "promising",
         "close", "nearly there", "has potential", "serviceable", "decent", "workable")


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def build_work(round_id, mapping):
    work = os.path.join(WORK_ROOT, "round%s" % round_id)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    for code, src in mapping.items():
        shutil.copy2(os.path.join(CAPTURES, src), os.path.join(work, code + ".png"))
    return work


def run(work):
    prompt = open(os.path.join(HERE, "seat_prompt.txt")).read()
    proc = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"],
                          cwd=work, capture_output=True, text=True, timeout=2400,
                          stdin=subprocess.DEVNULL)
    return proc.stdout + proc.stderr


def parse(text):
    verdicts = {}
    for block in re.split(r"(?=^CANDIDATE:)", text, flags=re.MULTILINE):
        m = re.match(r"CANDIDATE:\s*(\S+)", block.strip())
        if not m:
            continue
        code = m.group(1).replace(".png", "")

        def field(name):
            mm = re.search(r"^%s:\s*(.*)$" % name, block, flags=re.MULTILINE)
            return mm.group(1).strip() if mm else ""
        v = field("VERDICT").upper()
        why = field("WHY")
        # LOOP-PROCESS §5: a PASS whose reason hedges is converted to FAIL, mechanically.
        hedged = v.startswith("PASS") and any(h in why.lower() for h in HEDGE)
        verdicts[code] = dict(cull=field("CULL"), verdict="FAIL" if hedged else v,
                              raw_verdict=v, hedge_converted=hedged, why=why,
                              q1=field("Q1"), q2=field("Q2"), q3=field("Q3"),
                              q4=field("Q4"), q5=field("Q5"))
    flips = []
    fl = re.search(r"^FLIP LIST\s*$(.*)", text, flags=re.MULTILINE | re.DOTALL)
    if fl:
        for line in fl.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                flips.append(line[2:].strip())
    rank = []
    rk = re.search(r"^RANKING\s*$(.*?)^SEPARATOR:", text, flags=re.MULTILINE | re.DOTALL)
    if rk:
        rank = [l.strip() for l in rk.group(1).splitlines() if l.strip()]
    sep = re.search(r"^SEPARATOR:\s*(.*)$", text, flags=re.MULTILINE)
    return verdicts, flips, rank, (sep.group(1).strip() if sep else "")


def do_round(round_id):
    mapping, plant = ROUNDS[round_id]
    work = build_work(round_id, mapping)
    print("=" * 78)
    print("BLIND FLOOR SEAT - ROUND %s" % round_id)
    print("commit: %s" % git_commit())
    print("cwd:    %s" % work)
    print("        outside the repo; %d captures, codes anonymised, not in set order"
          % len(mapping))
    print("=" * 78)

    text = run(work)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "round%s_transcript.txt" % round_id), "w") as f:
        f.write(text)

    verdicts, flips, rank, sep = parse(text)
    for code in sorted(verdicts):
        v = verdicts[code]
        tag = "%s = %s%s" % (code, mapping.get(code, "?"),
                             "  <- PLANT" if code == plant else "")
        print("  %-40s %-4s cull=%-12s %s"
              % (tag, v["verdict"], v["cull"] or "none", v["why"][:70]))
        if v["hedge_converted"]:
            print("      (PASS converted to FAIL: the reason hedged - LOOP-PROCESS §5)")

    passes = [c for c, v in verdicts.items() if v["verdict"] == "PASS"]
    record = dict(round=round_id, commit=git_commit(), mapping=mapping, plant=plant,
                  verdicts=verdicts, passes=passes, ranking=rank, separator=sep,
                  flip_list=flips)

    if plant:
        pv = verdicts.get(plant, {})
        caught = pv.get("verdict") == "FAIL"
        record["plant_caught"] = caught
        record["round_void"] = not caught
        print("\n  PLANT CONTROL: %s (cull=%s)"
              % ("CAUGHT" if caught else "MISSED - ROUND VOID", pv.get("cull")))
    real = [c for c in verdicts if c != plant]
    n_pass = sum(1 for c in real if verdicts[c]["verdict"] == "PASS")
    print("  %d of %d non-plant captures passed." % (n_pass, len(real)))
    if sep:
        print("  separator: %s" % sep)
    with open(os.path.join(OUT, "round%s_result.json" % round_id), "w") as f:
        json.dump(record, f, indent=1)
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rounds", nargs="*", default=["A", "B"])
    args = ap.parse_args()
    recs = {}
    for r in args.rounds:
        recs[r] = do_round(r)
        print()

    if set(recs) >= {"A", "B"}:
        a, b = recs["A"], recs["B"]
        a_culled = all(v["verdict"] == "FAIL" for v in a["verdicts"].values())
        b_plant = b.get("plant_caught")
        b_real = [c for c in b["verdicts"] if c != b["plant"]]
        b_pass = sum(1 for c in b_real if b["verdicts"][c]["verdict"] == "PASS")
        print("=" * 78)
        print("THE BAR")
        print("  round A - the check can fail:  %s (%d of %d un-remediated culled)"
              % ("YES" if a_culled else "NO",
                 sum(1 for v in a["verdicts"].values() if v["verdict"] == "FAIL"),
                 len(a["verdicts"])))
        print("  round B - plant caught:        %s" % ("YES" if b_plant else "NO - ROUND VOID"))
        print("  round B - all four pass:       %s (%d of %d)"
              % ("YES" if b_pass == len(b_real) else "NO", b_pass, len(b_real)))
        met = a_culled and b_plant and b_pass == len(b_real)
        print("\n  BAR %s" % ("MET" if met else "NOT MET"))
        if not met:
            print("  LOOP-PROCESS §1.1.2: a FAIL is not a stop, it is a reprompt. The flip list")
            print("  is the next round's input.")
            for f in b["flip_list"]:
                print("    - %s" % f)
    print("\n-> %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
