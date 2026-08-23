#!/usr/bin/env python3
"""Round E3-final capture: pre-place the two NEW depths props at 5115/5116 (new tile IDs
render by path, per recon), run the round (benches/beds temp-written; reimport picks up the
new tiles), capture, then clean up the two new-ID PNGs so nothing lands."""
import os, shutil, subprocess
import review_capture, rounds_spec

W="src/Presentation/assets/sprites_16bf/world_24x24"
C="tools/art_lint/candidates/round_e3final"
GODOT="/Applications/Godot_mono.app/Contents/MacOS/Godot"
new_tiles={5115:"5115_bone_pile.png", 5116:"5116_flood_marker.png"}

# pre-place new-ID candidates
placed=[]
for tid,src in new_tiles.items():
    dst=f"{W}/oryx_16bit_fantasy_world_{tid}.png"
    shutil.copyfile(f"{C}/{src}", dst); placed.append((tid,dst))
try:
    rounds_spec.main_e3final(review_capture.run_round)
finally:
    # clean up: remove new-ID PNGs + their import sidecars, reimport
    for tid,dst in placed:
        for p in (dst, dst+".import"):
            if os.path.exists(p): os.remove(p)
        gd=f".godot/imported"
        # leftover imported artifacts are harmless; a reimport reconciles
    subprocess.run([GODOT,"--headless","--path",".","--import"],capture_output=True,text=True,timeout=300)
    print("cleaned up new-ID tiles 5115/5116")
