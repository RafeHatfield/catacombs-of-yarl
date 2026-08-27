#!/usr/bin/env python3
"""The declared 220-generation ceiling, enforced in code rather than remembered.

Two independent numbers, both reported, neither allowed to stand in for the other:

  * **attributed** — the sum of `usage.generations` over this audit's own completed calls.
    This is what THIS audit spent, by its own measurement.
  * **balance delta** — the settled pool at the first bracket minus the settled pool at the
    last. This includes anything else spending against the shared subscription.

The wall gauntlet ended with these two disagreeing by 320 generations and no way to localise
the difference, because its script never bracketed. Here they are both computed from the
ledgers at any moment, and `check()` refuses to authorise a call that would cross the ceiling.

⚠ `usage` is **null on the 202** for this endpoint and arrives on the completion GET. A call
that is created but never fetched is billed and invisible to `attributed`; PENDING counts them
so an un-fetched job cannot hide under the ceiling.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CEILING = 240   # 220 declared + 20 authorised by ruling for the tile_depth_ratio call
                #   (DECLARATION.md AMENDMENT, PREDICTION.md). Raised by the human gate,
                #   never by this seat.
PER_CALL = 20


def rows():
    for p in sorted(glob.glob(os.path.join(HERE, "**", "*.jsonl"), recursive=True)):
        for line in open(p):
            line = line.strip()
            if line:
                yield p, json.loads(line)


def tally():
    attributed = 0.0
    accepted = set()
    fetched = set()
    brackets = []
    for _, r in rows():
        if r.get("phase") == "create" and r.get("verdict") == "ACCEPTED":
            accepted.add(r["tile_id"])
        if r.get("phase") == "fetch" and r.get("verdict") == "OK":
            fetched.add(r["tile_id"])
            u = r.get("usage") or {}
            attributed += float(u.get("generations") or 0)
        if r.get("verdict") == "BRACKET":
            brackets.append(r)
    pending = accepted - fetched
    # ⚠ Brackets are collected by walking files, and glob order is alphabetical, not
    # chronological. Ordering the phases by filename put arm3's OPEN before yield's CLOSE and
    # reported a NEGATIVE spend of -40 against 220 attributed. Sort by the ledger timestamp,
    # which is what actually orders the phases.
    brackets.sort(key=lambda b: b.get("ts") or "")
    opens = [b for b in brackets if b["claim"].startswith("balance:open")]
    closes = [b for b in brackets if b["claim"].startswith("balance:close")]
    delta = None
    if opens and closes and opens[0].get("pool") and closes[-1].get("pool"):
        delta = opens[0]["pool"] - closes[-1]["pool"]
    phases = [(b.get("ts"), b["claim"], b.get("pool")) for b in brackets]
    return {"phases": phases,
            "attributed": attributed, "pending_calls": sorted(pending),
            "pending_gens": len(pending) * PER_CALL, "balance_delta": delta,
            "first_pool": opens[0]["pool"] if opens else None,
            "last_pool": closes[-1]["pool"] if closes else None,
            "n_brackets": len(brackets)}


def check(planned_calls, label=""):
    """Refuse to authorise a phase that would cross the declared ceiling. Raises."""
    t = tally()
    committed = t["attributed"] + t["pending_gens"]
    projected = committed + planned_calls * PER_CALL
    print("[budget] %s: attributed=%.0f pending=%.0f planned=%d calls (%d gens) "
          "-> projected %.0f of %d" %
          (label, t["attributed"], t["pending_gens"], planned_calls,
           planned_calls * PER_CALL, projected, CEILING))
    if projected > CEILING:
        raise SystemExit(
            "BUDGET REFUSED: %.0f projected exceeds the declared ceiling of %d. The ceiling "
            "was declared before the first call and is not tuned after (LOOP-PROCESS §8). "
            "Stop and report." % (projected, CEILING))
    return t


def main():
    t = tally()
    print(json.dumps(t, indent=2, sort_keys=True))
    print("\nattributed %.0f + pending %.0f of ceiling %d  (%.0f left)"
          % (t["attributed"], t["pending_gens"], CEILING,
             CEILING - t["attributed"] - t["pending_gens"]))
    if t["balance_delta"] is not None:
        print("balance delta across all brackets: %.0f  (pool %s -> %s)"
              % (t["balance_delta"], t["first_pool"], t["last_pool"]))
        gap = t["balance_delta"] - t["attributed"]
        if abs(gap) > 0.5:
            print("⚠ %.0f generations moved that this audit's own calls do not account for. "
                  "The subscription is shared with the sibling project "
                  "(PIXELLAB-UW-AUDIT-2026-08-25); both numbers are stated, neither is "
                  "picked for being flattering." % gap)
        else:
            print("✅ balance delta and attributed spend agree — the bracket closes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
