#!/usr/bin/env python3
"""Load the committed prompt file and assert its load-bearing clauses survived.

LOOP-PROCESS §12: generation prompts live as auditable files with clause provenance and a
self-check that asserts load-bearing clauses survived — never as a string typed into a chat.
The self-check is the half that is usually skipped, so it runs on every load and raises rather
than warns. A prompt that has silently lost §7.3's fastening vocabulary would produce a round
whose failure is unattributable, which is exactly the gauntlet's r9 hazard.

Run directly to print the payload and the check.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.join(HERE, "prompts")

MAXLEN = {"building_wall_description": 500, "building_floor_description": 500,
          "building_floor2_description": 500}


def load(pid):
    with open(os.path.join(PROMPTS, pid + ".json")) as f:
        return json.load(f)


def build_payload(pid, seed, **overrides):
    """Return (payload, spec). Every load-bearing clause is re-asserted here, after overrides,
    so a lever probe cannot quietly drop one and be compared against a kit that kept it."""
    spec = load(pid)
    payload = dict(spec["payload"])
    payload["seed"] = seed
    payload.update(overrides)

    blob = " ".join(str(v) for k, v in sorted(payload.items()) if isinstance(v, str))
    missing = [c for c in spec["load_bearing"] if c not in blob]
    if missing:
        raise AssertionError(
            "PROMPT SELF-CHECK FAILED for %s — load-bearing clauses lost: %s"
            % (pid, "; ".join(missing)))
    for field, cap in MAXLEN.items():
        v = payload.get(field)
        if isinstance(v, str) and len(v) > cap:
            raise AssertionError("%s is %d chars, cap is %d" % (field, len(v), cap))
    return payload, spec


def main():
    for seed_key in ("kit_a", "kit_b"):
        spec = load("wall_kit")
        seed = spec["seeds"][seed_key]
        payload, _ = build_payload("wall_kit", seed)
        print("== %s (seed %d) ==" % (seed_key, seed))
        for k in sorted(payload):
            v = payload[k]
            n = " [%d chars]" % len(v) if isinstance(v, str) else ""
            print("  %-28s %s%s" % (k, json.dumps(v)[:200], n))
    print("\nself-check: %d load-bearing clauses present in both" %
          len(load("wall_kit")["load_bearing"]))

    print("\n== the self-check must be able to fail ==")
    try:
        build_payload("wall_kit", 1,
                      building_wall_description="plain grey stone wall")
        print("  RED — a payload that dropped every §7.3 clause was accepted. INSTRUMENT BLIND.")
        return 1
    except AssertionError as e:
        print("  PASS — caught: %s" % str(e)[:160])
    try:
        build_payload("wall_kit", 1, building_floor_description="x" * 501)
        print("  RED — an over-length field was accepted.")
        return 1
    except AssertionError as e:
        print("  PASS — caught: %s" % str(e)[:160])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
