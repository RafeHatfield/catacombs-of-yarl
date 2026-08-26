#!/usr/bin/env python3
"""Free: print TilesProStyleOptions and the style_images item schema verbatim."""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def main():
    doc = json.load(open(os.path.join(OUT, "openapi.json")))
    comps = doc["components"]["schemas"]
    for name in ("TilesProStyleOptions", "CreateTilesProRequest", "Usage"):
        if name not in comps:
            print("MISSING", name)
            continue
        print("\n===", name, "===")
        sch = comps[name]
        if name == "CreateTilesProRequest":
            si = sch["properties"]["style_images"]
            print("style_images raw:", json.dumps(si)[:900])
            continue
        for k, v in sch.get("properties", {}).items():
            d = (v.get("description") or "").replace("\n", " ")
            print(" ", k, "|", json.dumps({kk: vv for kk, vv in v.items()
                                           if kk != "description"})[:260])
            if d:
                print("      ", d[:280])


if __name__ == "__main__":
    main()
