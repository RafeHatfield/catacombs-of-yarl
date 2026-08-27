#!/usr/bin/env python3
"""THE COMPOSITION SPIKE — the blind critic seat.

LOOP-PROCESS §1.1.1: nothing reaches the human gate that the blind critic would kill. This
session produces visual candidates, so a critic seat runs over them BEFORE anything is put in
front of Rafe.

LOOP-PROCESS §3: the critic is a fresh `claude -p` with cwd OUTSIDE the repo. Not a subagent.
Blindness is structural rather than promised — the process cannot reach the repo, the bible,
the ledger, or any prior round. It sees a directory of PNGs and the critic prompt.

LOOP-PROCESS §2.1: what it sees is the LIT IN-SCENE CAPTURE at the reference device's pixel
size, never a contact sheet. A receive-light asset judged unlit is judged by the wrong
instrument.

LOOP-PROCESS §4 / bible §13.5: the set contains a PLANT — the boundB composition with a baked
per-course key light, the exact defect §6.3 forbids. A critic that passes the plant has not
demonstrated it can fail and VOIDS ITS OWN ROUND; the verdicts on the real arms do not count.

The arm codes are anonymised so the seat cannot infer which capture is the bound arm and which
is its control. The mapping is written to the round record after the verdicts are parsed.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EVIDENCE = os.path.join(HERE, "evidence")
WORK_ROOT = ("/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
             "5c7d3114-dce0-460c-b867-70ca1b348153/scratchpad/critic")

# code -> capture. Deliberately not in arm order.
SET = {
    "C1": "after_lit.png",
    "C2": "after_unbound_lit.png",
    "C3": "before_lit.png",
    "C4": "plant_lit.png",
    "C5": "after_nocap_lit.png",
}
PLANT_CODE = "C4"


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def build_work(round_no):
    work = os.path.join(WORK_ROOT, "round%02d" % round_no)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    for code, src in SET.items():
        shutil.copy2(os.path.join(EVIDENCE, src), os.path.join(work, code + ".png"))
    return work


def run(work):
    prompt = open(os.path.join(HERE, "critic_prompt.txt")).read()
    proc = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"],
                          cwd=work, capture_output=True, text=True, timeout=2400,
                          stdin=subprocess.DEVNULL)
    return proc.stdout + proc.stderr


HEDGE = ("fine", "acceptable", "good enough", "improved", "better than", "solid", "promising",
         "close", "nearly there", "has potential", "serviceable", "decent", "workable")


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


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    work = build_work(round_no)
    print("blind critic seat — round %d" % round_no)
    print("commit: %s" % git_commit())
    print("cwd:    %s   (outside the repo; %d captures, codes anonymised)\n"
          % (work, len(SET)))

    text = run(work)
    out_dir = os.path.join(EVIDENCE, "critic")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "round%02d_transcript.txt" % round_no), "w") as f:
        f.write(text)

    verdicts, flips, rank, sep = parse(text)
    plant = verdicts.get(PLANT_CODE, {})
    plant_caught = plant.get("verdict") == "FAIL"
    passes = [c for c, v in verdicts.items() if v["verdict"] == "PASS"]

    for code in sorted(verdicts):
        v = verdicts[code]
        tagged = "%s = %s%s" % (code, SET[code], "  <- PLANT" if code == PLANT_CODE else "")
        print("  %-34s %-4s cull=%-16s %s"
              % (tagged, v["verdict"], v["cull"] or "none", v["why"][:80]))
    print("\n  PLANT CONTROL: %s (cull=%s)"
          % ("CAUGHT" if plant_caught else "MISSED — ROUND VOID", plant.get("cull")))
    print("  passes: %d   flip items: %d" % (len(passes), len(flips)))

    record = dict(round=round_no, commit=git_commit(), mapping=SET,
                  plant=PLANT_CODE, plant_caught=plant_caught,
                  round_void=not plant_caught, verdicts=verdicts,
                  passes=passes, ranking=rank, separator=sep, flip_list=flips)
    with open(os.path.join(out_dir, "round%02d_result.json" % round_no), "w") as f:
        json.dump(record, f, indent=1)
    print("\n-> %s" % os.path.relpath(out_dir, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
