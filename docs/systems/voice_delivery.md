# Hollowmark Voice Delivery: Scheduler + Ribbon Contract (M1.5)
Ruled 2026-07-20, Foundation thread. Supersedes the archived skeleton
(docs/archive/story/the_under_warden_design_notes.md — ribbon row); ToastLog and
MessageLogPanel remain ruled out; the ribbon is its own widget (5b).

## Scheduler (Logic; presentation-agnostic)
- Per-trigger-family SHUFFLE BAGS: draw without replacement; reshuffle only on
  exhaustion; a line never repeats until its family's bag empties.
- ONE-SHOTS: lines flagged once-per-run fire at most once per run, tracked in a
  fired-set independent of bags.
- PRIORITY: integer tier per trigger family, defined in the voice YAML (data, not
  code). Initial ranking: hp-critical > possession > boss/named > species-first-sight
  > traps/hazards > items/economy > idle. Multiple triggers in one turn: highest tier
  wins, ties broken by family order in YAML; losers are NOT consumed.
- COOLDOWN: minimum 3 turns between delivered lines; the top tier (hp-critical) is
  exempt. Suppressed triggers are NOT consumed.
- SILENCE RULES: Verbose (all tiers) / Tactical (tiers above the YAML-marked ambient
  cutoff) / Silent (nothing renders). Floor-silence flag (post-Marya) mutes a floor.
  Shut-up action mutes the current floor.
- THE ONE RULE: any reason a line will not render — mode, silence, cooldown, priority
  loss, surface unavailable (5b provides the probe) — means the scheduler NEVER
  consumes: no bag advance, no one-shot burn. Consumption happens only on delivery.

## Determinism
- The scheduler owns a DEDICATED SeededRandom (seeded run-seed XOR constant),
  serialized as (Seed, CallCount) exactly like the gameplay stream. Bag shuffles and
  any tie-breaks draw ONLY from it. The gameplay Rng is never touched by voice code —
  gameplay hash sequences must be identical with voice enabled or disabled.

## Save boundary (extends save_resume_boundary.md; its gates enforce this)
- SERIALIZE-class (run state): bag states (remaining order per family), one-shot
  fired-set, floor-silence flags, cooldown counter, ribbon history (last 20 delivered
  lines: line id + turn number), the voice Rng (Seed, CallCount).
- NOT in the run save (device settings, 5b): Verbose/Tactical/Silent toggle, ribbon
  duration. Settings must survive across runs; run state must not leak into settings.

## Ribbon contract (implemented 5b; scheduler API must support it)
- One line at a time; new delivery SUPERSEDES current only when strictly higher tier,
  else dropped (unconsumed). No queue, ever.
- Duration: Short 2.5s / Normal 4s (default) / Long 6s; tap-to-dismiss.
- History: tap-to-expand anchor, last 20, run-scoped (from the serialized history).
