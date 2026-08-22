# Hollowmark Voice Delivery: Scheduler + Ribbon Contract (M1.5)
Ruled 2026-07-20, Foundation thread. Supersedes the archived skeleton
(docs/archive/story/the_under_warden_design_notes.md — ribbon row); ToastLog and
MessageLogPanel remain ruled out; the ribbon is its own widget (5b).

## Canon — who Hollowmark is (ruled Foundation, 2026-08-21)
**Hollowmark IS the wand of portals** — the bound artificer. The item is her body; the
ribbon is her voice. They are one character, not a voice feature plus an unrelated wand.
That the `wand_of_portals` entity does not yet carry her name/description is a **design gap
being closed in Phase 3**, not the design. Never write "Hollowmark is only the voice" — the
voice and the artifact are the same being. (The `wand_of_spell_break` → "Sasha's Sunder"
reflavor is a *separate* item and does not touch this canon.)

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

## Ribbon contract (5b; revised 2026-08 — stacked, attributed, dismiss-mode)
- STACK, newest on top, up to 3 cards; the 4th pushes the oldest off the bottom. The scheduler
  no longer supersedes by tier (that was for a single slot) — the ribbon hook passes
  `currentRibbonTier: null`. The scheduler still delivers at most one line per turn and filters by
  cooldown / mode / once-per-run, so the stack fills gradually, not every turn.
- ATTRIBUTION: each card is tagged "✦ HOLLOWMARK" so the player knows who is speaking.
- DISMISS MODE (device setting, default Manual): Manual = each card stays until tapped (nothing
  missed mid-fight); Timed = each card fades after its own Duration (Short 2.5s / Normal 4s / Long 6s).
- History: tap-to-expand anchor, last 20, run-scoped (from the serialized history). Quiet button
  mutes the current floor. Both live in a persistent controls row above the stack.
