#!/usr/bin/env python3
"""Free: pull the live OpenAPI document and print the tiles-pro surface verbatim.

A schema read costs nothing and is [SCHEMA], not [API]. Nothing in this file is a verdict —
it exists so the paid probes below are aimed at parameters that actually exist.
"""
import json
import os
import sys

import requests

OUT = os.path.dirname(os.path.abspath(__file__))


def main():
    tok = os.environ.get("PIXELLAB_API_TOKEN") or os.environ.get("PIXELLAB_API_KEY")
    if not tok:
        sys.exit("No PixelLab credential")
    h = {"Authorization": "Bearer " + tok}
    doc = None
    for path in ("/openapi.json", "/v2/openapi.json"):
        r = requests.get("https://api.pixellab.ai" + path, headers=h, timeout=60)
        print(path, r.status_code, len(r.text))
        if r.status_code == 200:
            try:
                doc = r.json()
                break
            except Exception:
                pass
    if doc is None:
        sys.exit("no openapi document")
    with open(os.path.join(OUT, "openapi.json"), "w") as f:
        json.dump(doc, f)
    paths = doc.get("paths", {})
    print("paths:", len(paths))
    for p in sorted(paths):
        if "tile" in p:
            print("  ", p, sorted(paths[p].keys()))


if __name__ == "__main__":
    main()
