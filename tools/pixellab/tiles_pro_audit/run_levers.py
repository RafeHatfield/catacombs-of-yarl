#!/usr/bin/env python3
"""COLUMN 3 — lever presence AND measurability.

⚠ **THE PIXDIFF IS BLIND ON THIS ENDPOINT AND IS NOT USED AS THE VERDICT.** Measured in the
yield phase: four byte-identical calls at seed 1337 produced four entirely different kits, and
each tile's diff equals its own opaque fraction — *every visible pixel differs*. Normalised
against the visible area the noise floor is **1.0000**. There is no headroom, and a lever
pixdiff read against that floor would be the §6.4 audit's own first mistake repeated: MCP `pro`
measured its lever at 1.0000 against a noise floor of 1.0000, and the honest output was
`NO INSTRUMENT`. The pixdiff is still computed and still recorded — as an explicitly blind
column, never as a verdict.

**THE VERDICT COMES FROM THE STRUCTURAL READOUT** (`diag_metadata.py`): canvas size, floor
cell, `stack_stride_px`, `wall_tiles`, `arity`, `rule_type`, and the `painted` list — the
grammar and the geometry, never the pixels. That readout was shown to have headroom before it
was used for anything: **10 of 10 of its fields are identical across five kits whose every
visible pixel differs.** It is the hardest available negative control and it was free.

A readout move is not an aesthetic judgement either (bible §13.4). It answers exactly one
mechanical question: did the parameter do anything at all. HONOURED never means "moved in the
intended direction" — that is an eye question and it belongs to the human gate.

  L1  building_layout: "grid"
      The default for square_topdown is "materials" — flat swatches, from which the pieces are
      rendered. The returned grammar says only 20 of 80 tiles were individually `painted`; the
      other 60 are composed. "grid" paints each shaped piece individually. This is the
      wallpaper-versus-architecture axis expressed as a parameter, and it is the single most
      relevant lever on this endpoint.

  L2  tile_view_angle: 90
      `tile_view` is measured [API] SILENTLY IGNORED on building kits and fully charged
      (PIXELLAB-INTEGRATION-AUDIT §9.3). `tile_view_angle` is a DIFFERENT parameter — continuous
      degrees, documented to override `tile_view` — and it has never been called. Two questions
      in one call: is it live where its enum neighbour is dead, and does 90 (top-down, zero
      depth) buy the SQUARE floor cell bible §3 asks for, which §9.3 proved `tile_view` cannot.

  L3  style_images: two references
      The conditioning column. References are the §6.4 probe's own survivors — A-VAB and
      C-GAB, named by Rafe as the two strongest, already the conditioning set for that probe's
      Stage 2. They are BitForge output, not tiles-pro output, so nothing here conditions this
      endpoint on itself. Two, never one: single-reference conditioning is a banked failure on
      this platform (LOOP-PROCESS §12).
      ⚠ The schema says style tiles override tile_type, tile_size, tile_view, tile_view_angle
      and tile_depth_ratio — "the style tiles define the shape". Whether the KIT GEOMETRY
      survives that is the thing worth knowing, and it is why this call is worth 20 generations.

DELIBERATELY NOT SPENT, and named rather than omitted:
  * `outline_mode: "segmentation"` — it guards §12.1, and the baseline kits already carry no
    dark ring, so the lever protects against a defect that is not present. Recorded as a gap.
  * `building_wall_angle` — the parameter that could keep a square ground cell AND a tall wall
    face at once. It is the most interesting untried thing on this endpoint and the budget
    ceiling reached first. Named for whoever runs next.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import diag_metadata as DM  # noqa: E402
import prompt as P  # noqa: E402
import sheet as SH  # noqa: E402
import spend  # noqa: E402
import tiles_pro as tp  # noqa: E402

OUT = os.path.join(HERE, "levers")
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
REFS = ("A-VAB", "C-GAB")


def style_refs():
    return [tp.style_image(Image.open(os.path.join(SURVIVORS, r + ".png"))) for r in REFS]


def main():
    spec = P.load("wall_kit")
    seed = spec["seeds"]["kit_a"]
    levers = [
        ("L1_layout_grid", {"building_layout": "grid"},
         "does painting each piece individually change the output at all?"),
        ("L2_view_angle_90", {"tile_view_angle": 90},
         "is tile_view_angle live where tile_view is a measured silent no-op, and does it "
         "buy a square floor cell?"),
        ("L3_style_images", {"style_images": style_refs()},
         "are style references honoured, and does the kit geometry survive them?"),
    ]
    spend.check(len(levers), "levers")

    os.makedirs(OUT, exist_ok=True)
    led = tp.Ledger(OUT, "levers_ledger.jsonl")

    base_dir = os.path.join(HERE, "yield", "kit_A0")
    base = SH.load_kit(base_dir)
    if not base:
        raise SystemExit("yield kit A0 is not on disk — run run_yield.py first")

    base_readout = DM.readout(base_dir)
    print("baseline structural readout: canvas=%s floor_cell=%s stride=%s painted=%d" %
          (base_readout["canvas"], base_readout["floor_cell"],
           base_readout["stack_stride_px"], base_readout["n_painted"]))
    print("pixdiff noise floor on this endpoint: 1.0000 of the visible area — NO INSTRUMENT\n")

    rows = []
    with tp.Bracket(led, "levers"):
        for label, over, question in levers:
            payload, _ = P.build_payload("wall_kit", seed, **over)
            tiles, crow, meta = tp.run_kit(payload, led, "kit_" + label,
                                           claim="lever:" + label,
                                           extra={"lever": label, "question": question,
                                                  "overrides": list(over)})
            if not tiles:
                print("%-18s CALL FAILED: %s  %s" %
                      (label, crow.get("verdict"), (crow.get("reason") or "")[:120]))
                rows.append({"lever": label, "question": question,
                             "verdict": crow.get("verdict"),
                             "reason": (crow.get("reason") or "")[:1000]})
                continue

            kit_dir = os.path.join(OUT, "kit_" + label)
            r = DM.readout(kit_dir)
            moved_fields = {k: [base_readout[k], r[k]] for k in base_readout
                            if base_readout[k] != r[k]}
            mean, tmoved, tn = tp.kitdiff(base, tiles)
            verdict = "READOUT MOVED" if moved_fields else "READOUT UNMOVED"
            print("%-18s %-16s %s" %
                  (label, verdict,
                   ", ".join("%s %s->%s" % (k, json.dumps(v[0])[:20], json.dumps(v[1])[:20])
                             for k, v in sorted(moved_fields.items())
                             if k != "painted") or "(nothing in the grammar or geometry)"))
            rows.append({"lever": label, "question": question, "overrides": list(over),
                         "verdict": verdict, "moved_fields": sorted(moved_fields),
                         "readout": r, "baseline_readout": base_readout,
                         "moved_detail": moved_fields,
                         "pixdiff_BLIND": mean, "tiles_moved": tmoved, "tiles_compared": tn,
                         "n_tiles": meta["n_tiles"], "sizes": [list(s) for s in meta["sizes"]],
                         "usage": meta["usage"], "wait_seconds": meta["wait_seconds"]})

    with open(os.path.join(OUT, "levers_result.json"), "w") as f:
        json.dump({"instrument": "structural readout (grammar + geometry); pixdiff is NO "
                                 "INSTRUMENT on this endpoint and is recorded blind",
                   "pixdiff_noise_floor": "1.0000 of visible area",
                   "baseline": "yield/kit_A0", "levers": rows},
                  f, indent=2, sort_keys=True, default=str)
    print("\nwrote", os.path.join(OUT, "levers_result.json"))
    print("\n⚠ READOUT MOVED means the parameter changed the grammar or the geometry.\n"
          "  It does NOT mean it changed the art in the intended direction. That is an eye\n"
          "  question and it belongs to the human gate (bible §13.2, §13.4).\n"
          "⚠ READOUT UNMOVED does not prove a silent no-op: a lever could change every pixel\n"
          "  and no field. On this endpoint that case is UNMEASURABLE, because the pixel\n"
          "  channel has no headroom. Say unmeasurable, not unchanged.")


if __name__ == "__main__":
    main()
