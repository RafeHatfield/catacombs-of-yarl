#!/usr/bin/env python3
"""Free: print TilesProStyleImage — what a style reference must carry on this endpoint."""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def main():
    doc = json.load(open(os.path.join(OUT, "openapi.json")))
    comps = doc["components"]["schemas"]
    for name in ("TilesProStyleImage", "Base64Image"):
        if name not in comps:
            print("MISSING", name)
            continue
        print("\n===", name, "===")
        print(json.dumps(comps[name], indent=2)[:2000])


if __name__ == "__main__":
    main()
