#!/usr/bin/env python3
"""COLUMN 1a — canvas and constraint behaviour, measured by REFUSAL.

A 422 is free (measured on this account, §8.9: an out-of-enum value returned 422 at no cost),
and a validation error that names the true range is worth more than the schema line that
merely says "tighter per-shape ranges". Every probe here is CHOSEN TO BE REFUSED. That is the
point: refusals are the free instrument.

⚠ A 202 is BILLED. Each probe declares what it expects; an unexpected acceptance is recorded
loudly with its `usage`, and the phase is bracketed at both ends regardless, so a surprise
charge is attributable to the probe that caused it rather than reconstructed afterwards.

Nothing here is a verdict about art. It is the shape of the box before anything is put in it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tiles_pro as tp  # noqa: E402

OUT = os.path.join(HERE, "columns")

BASE = {
    "description": "dungeon wall and floor construction kit",
    "tile_type": "square_topdown",
    "tile_feature": "building",
    "tile_size": 32,
    "seed": 1337,
}

# (label, overrides, what this asks, expectation)
PROBES = [
    ("size_15_below_schema_min", {"tile_size": 15},
     "is the documented 16 floor enforced?", "REFUSE"),
    ("size_129_above_schema_max", {"tile_size": 129},
     "is the documented 128 ceiling enforced?", "REFUSE"),
    ("size_17_odd", {"tile_size": 17},
     "do building kits accept odd sizes, or is the per-shape range coarser?", "REFUSE"),
    ("size_20_even_nonstandard", {"tile_size": 20},
     "how coarse is the per-shape range for square_topdown building?", "REFUSE"),
    ("wall_tiles_4", {"building_wall_tiles": 4},
     "is the 1-3 wall-height range enforced?", "REFUSE"),
    ("wall_tiles_0", {"building_wall_tiles": 0},
     "is the lower bound enforced?", "REFUSE"),
    ("roads_at_24", {"tile_feature": "roads", "tile_size": 24},
     "does the error name the exactly-32 rule for square_topdown roads?", "REFUSE"),
    ("bad_layout_enum", {"building_layout": "swatches"},
     "does building_layout validate, i.e. is it a live parameter and not decoration?",
     "REFUSE"),
    ("bad_outline_mode", {"outline_mode": "none"},
     "does outline_mode validate?", "REFUSE"),
    ("wall_angle_100", {"building_wall_angle": 100},
     "is building_wall_angle's 5-90 range enforced (a live parameter refuses)?", "REFUSE"),
    ("depth_ratio_2", {"tile_depth_ratio": 2.0},
     "is tile_depth_ratio's 0-1 range enforced?", "REFUSE"),
    ("view_angle_120", {"tile_view_angle": 120},
     "is tile_view_angle's 0-90 range enforced?", "REFUSE"),
    ("style_images_empty_list", {"style_images": []},
     "is a zero-reference conditioning call refused, or silently accepted?", "REFUSE"),
    ("desc_over_length", {"building_wall_description": "x" * 501},
     "is the 500-char building_wall_description cap enforced?", "REFUSE"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    led = tp.Ledger(OUT, "constraints_ledger.jsonl")
    rows = []
    with tp.Bracket(led, "constraints"):
        for label, over, question, expect in PROBES:
            payload = dict(BASE)
            payload.update(over)
            tile_id, row = tp.create(payload, led, claim="constraint:" + label,
                                     extra={"question": question, "expected": expect,
                                            "overrides": over})
            verdict = row.get("verdict", "?")
            billed = verdict == "ACCEPTED"
            detail = ""
            if billed:
                detail = "⚠ ACCEPTED AND BILLED usage=%s tile_id=%s" % (
                    row.get("usage"), tile_id)
            else:
                try:
                    body = json.loads(row.get("reason") or "{}")
                    det = body.get("detail")
                    if isinstance(det, list) and det:
                        detail = "; ".join(
                            "%s @ %s%s" % (d.get("msg"), ".".join(str(x) for x in d.get("loc", [])),
                                           (" ctx=" + json.dumps(d["ctx"])) if d.get("ctx") else "")
                            for d in det)
                    else:
                        detail = json.dumps(det) if det else (row.get("reason") or "")[:300]
                except Exception:
                    detail = (row.get("reason") or "")[:300]
            surprise = "  <<< UNEXPECTED" if (billed and expect == "REFUSE") else ""
            print("%-28s %-22s %s%s" % (label, verdict, detail[:220], surprise))
            rows.append({"label": label, "overrides": over, "question": question,
                         "expected": expect, "verdict": verdict,
                         "http_status": row.get("http_status"), "detail": detail,
                         "usage": row.get("usage")})
    with open(os.path.join(OUT, "constraints.json"), "w") as f:
        json.dump(rows, f, indent=2, sort_keys=True)
    billed_n = sum(1 for r in rows if r["verdict"] == "ACCEPTED")
    print("\n%d probes, %d refused (free), %d ACCEPTED AND BILLED" %
          (len(rows), len(rows) - billed_n, billed_n))


if __name__ == "__main__":
    main()
