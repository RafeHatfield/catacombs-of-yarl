#!/usr/bin/env python3
"""ART-BIBLE-v0 §6.4 — capture the three receive-light probe arms for side-by-side comparison.

§6.4 runs a three-arm probe immediately after the Tier 0 session:

    A — baked directional key light                    POSITIVE CONTROL, the conventional approach
    B — no key light; form shading, occlusion, material value retained
    C — flat, material value only                      the strict reading of §6.3

The bible's requirement is precise and it is what this script exists to guarantee: the arms are
"lit in Godot, on the reference device, in a corridor" — under IDENTICAL lighting. An arm is a
different AUTHORING of the same fragment, so the only thing that may vary between captures is
which tile directory the theme config points at. This script therefore reads ONE light rig from
harness_config.yaml and passes the same values to every arm, and it prints the rig once so that
a reader can confirm there was only one.

It also honours §6.4's positive-control clause (Ruling 47): "If A and B cannot be told apart in
the lit scene, that is a finding about the test conditions — not permission to pick either." So
this script reports the measured pixel difference BETWEEN arms and says plainly when two arms are
indistinguishable, rather than presenting three captures and leaving the reader to assume they
differ.

NO ARM ART EXISTS YET. Pointed at stub tiles, this proves the mechanism end to end before a
single asset is drawn. Generating the arms is the next session's work.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_corridor import REPO, read_config, capture, sha256, git_commit
from run_controls import diff_stats, GODOT

from PIL import Image, ImageDraw, ImageFont

ARMS = ("A", "B", "C")
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"


def theme_for(arm):
    return f"res://src/Presentation/assets/tier0_harness/tile_themes_arm_{arm}.yaml"


def contact_sheet(paths, labels, out_path, rig_line):
    """Side-by-side, with the rig stamped on it.

    Stamping the rig is not decoration. §13.1 forbids approving a candidate from a contact
    sheet, so this sheet exists ONLY to compare arms against each other — and it says so on its
    face, so it cannot be mistaken later for an acceptance artefact.
    """
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = sum(i.width for i in imgs)
    h = max(i.height for i in imgs)
    bar = 96
    sheet = Image.new("RGB", (w, h + bar), (20, 19, 18))
    x = 0
    for i in imgs:
        sheet.paste(i, (x, 0))
        x += i.width

    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(FONT_PATH, 17)
        small = ImageFont.truetype(FONT_PATH, 13)
    except OSError:
        font = small = ImageFont.load_default()

    x = 0
    for i, label in zip(imgs, labels):
        d.text((x + 10, h + 8), label, font=font, fill=(240, 170, 60))
        x += i.width
    d.text((10, h + 34), rig_line, font=small, fill=(150, 150, 150))
    d.text((10, h + 54),
           "COMPARISON ONLY — ART-BIBLE-v0 §13.1: no candidate is ever approved from a contact "
           "sheet. Verdicts come from the lit scene on device.",
           font=small, fill=(200, 120, 120))
    d.text((10, h + 74), f"commit {git_commit()}", font=small, fill=(120, 120, 120))
    sheet.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Capture the §6.4 three-arm receive-light probe")
    ap.add_argument("--out-dir", default="tools/tier0_harness/evidence/probe")
    ap.add_argument("--godot", default=GODOT)
    args = ap.parse_args()

    cfg = read_config()
    out_dir = os.path.join(REPO, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    light = cfg["light"]
    rig = (f"IDENTICAL RIG FOR ALL ARMS — ambient={light['ambient']} color={light['color']} "
           f"energy={light['energy']} radius_tiles={light['radius_tiles']} "
           f"(ALL UNDERIVED — §6.2/§4.3 PLACEHOLDER)")
    print(rig + "\n")

    paths, labels = [], []
    for arm in ARMS:
        out = os.path.join(out_dir, f"arm_{arm}.png")
        rc, log, _ = capture(out, theme_for(arm), cfg, args.godot,
                             log_out=out.replace(".png", ".log"))
        if not os.path.exists(out):
            print(f"ABORT: arm {arm} produced no capture", file=sys.stderr)
            print(log, file=sys.stderr)
            sys.exit(1)
        # Echo the rig the ENGINE reported, per arm — proof the rig really was identical, rather
        # than an assertion by this script that it passed the same flags.
        engine_rig = next((l.split("light rig:")[1].strip()
                           for l in log.splitlines() if "light rig:" in l), "(not reported)")
        print(f"arm {arm}: {out}")
        print(f"  sha256: {sha256(out)}  bytes: {os.path.getsize(out)}")
        print(f"  engine rig: {engine_rig}")
        paths.append(out)
        labels.append(f"ARM {arm}")

    print("\n-- between-arm differences (§6.4 Ruling 47: A and B indistinguishable is a FINDING) --")
    indistinguishable = []
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            pct, mean = diff_stats(paths[i], paths[j])
            flag = ""
            if pct < 0.5:
                flag = "  <-- INDISTINGUISHABLE: a finding about the test conditions, " \
                       "NOT permission to pick either"
                indistinguishable.append((ARMS[i], ARMS[j]))
            print(f"  {ARMS[i]} vs {ARMS[j]}: {pct:7.4f}% pixels differ, "
                  f"mean channel delta {mean:7.4f}{flag}")

    sheet = contact_sheet(paths, labels, os.path.join(out_dir, "probe_arms_side_by_side.png"), rig)
    print(f"\nside-by-side: {sheet}  ({os.path.getsize(sheet)} bytes)")
    print(f"commit: {git_commit()}")

    if indistinguishable:
        print(f"\nFINDING: {indistinguishable} could not be told apart in the lit scene.")


if __name__ == "__main__":
    main()
