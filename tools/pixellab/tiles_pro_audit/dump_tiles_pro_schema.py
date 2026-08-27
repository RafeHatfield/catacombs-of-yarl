#!/usr/bin/env python3
"""Free: print the /create-tiles-pro request body schema field by field, verbatim."""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def resolve(doc, ref):
    node = doc
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def describe(doc, name, spec, indent="  "):
    bits = []
    t = spec.get("type")
    if "anyOf" in spec:
        alts = []
        for a in spec["anyOf"]:
            if "$ref" in a:
                alts.append(a["$ref"].split("/")[-1])
            else:
                alts.append(a.get("type", "?"))
        t = "anyOf[" + ",".join(alts) + "]"
    if "$ref" in spec:
        t = spec["$ref"].split("/")[-1]
    if "enum" in spec:
        bits.append("enum=" + json.dumps(spec["enum"]))
    for k in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
              "minItems", "maxItems", "maxLength", "default"):
        if k in spec:
            bits.append("%s=%s" % (k, json.dumps(spec[k])))
    for a in spec.get("anyOf", []):
        for k in ("minimum", "maximum", "enum", "minItems", "maxItems", "maxLength"):
            if k in a:
                bits.append("%s=%s" % (k, json.dumps(a[k])))
    desc = (spec.get("description") or "").strip().replace("\n", " ")
    print("%s%-32s %-28s %s" % (indent, name, t, " ".join(bits)))
    if desc:
        print("%s%34s%s" % (indent, "", desc[:300]))


def main():
    doc = json.load(open(os.path.join(OUT, "openapi.json")))
    for endpoint in ("/create-tiles-pro", "/tiles-pro/{tile_id}"):
        node = doc["paths"][endpoint]
        print("\n" + "=" * 78)
        print("POST/GET", endpoint)
        print("=" * 78)
        for method, op in node.items():
            if method not in ("post", "get"):
                continue
            body = op.get("requestBody")
            if body:
                ref = body["content"]["application/json"]["schema"]["$ref"]
                sch = resolve(doc, ref)
                print("-- request:", ref.split("/")[-1],
                      "required:", sch.get("required"))
                for k, v in sch["properties"].items():
                    describe(doc, k, v)
            for code, resp in op.get("responses", {}).items():
                c = resp.get("content", {}).get("application/json", {}).get("schema")
                if c and "$ref" in c:
                    sch = resolve(doc, c["$ref"])
                    print("-- response %s: %s" % (code, c["$ref"].split("/")[-1]))
                    for k, v in sch.get("properties", {}).items():
                        describe(doc, k, v, indent="    ")


if __name__ == "__main__":
    main()
