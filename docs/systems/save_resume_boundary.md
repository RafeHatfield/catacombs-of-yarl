# Mid-Run Save/Resume: Serialization Boundary (M1.4)
Ruled 2026-07-16. Design locked in Foundation thread; this doc is the contract.

## Scope
Single floor + run-scoped state. The game is descent-only (M0 ruling: stair-up is flavor,
no ascent, no floor stack) — GameState is strictly single-floor and stays that way.
Cross-run persistence (PersistentRunState) is a SEPARATE file with its own lifecycle:
the mid-run save stores nothing from it and never writes it.

## RNG continuity (two-step ruling)
M1: SeededRandom gains an internal call counter. Every Next/NextDouble/NextFloat
increments it. Save (Seed, CallCount); load reconstructs Random(seed) and burns
CallCount raw draws to restore sequence position. This preserves all existing
sequences — the balance baseline must not move.
Fragility acknowledged: assumes every wrapper call consumes exactly one internal
sample. True for legacy seeded System.Random at game-scale ranges; the two-sample
path triggers only near int.MaxValue ranges. Guard: Next(min,max) asserts
(long)max - min < int.MaxValue / 2. A dedicated continuity test locks the behavior.
M2 (scheduled with the suite re-baseline, when sequence changes are free): replace
System.Random with an explicit-state PRNG (xoshiro256**), serialize state directly,
delete the counter. Do NOT do this now.

## Entity-table serialization (not tree)
Entities are multiply-referenced (Monsters/FloorItems/Portals/Corpses/Features/
StairDown, portal cross-links, inventory contents). The save format stores one
entity record per Id in a flat table; all lists and references are Id arrays.
Load rebuilds the table first, then resolves references. Identity is preserved:
an entity referenced twice deserializes to ONE object. Cycles (portal A <-> B)
are legal by construction.

Structural rule (measured 2026-07-16, for 4a.2): the entity table is the transitive
closure of all reachable entities, NOT just the top-level GameState lists. Once an item
is picked up or equipped it leaves FloorItems and lives inside a container, so the walk
must descend into containers. Specifically: Inventory's `List<Entity>` serializes as an
Id array, and Equipment's nine `Entity?` slots (MainHand, OffHand, Head, Chest, Feet,
LeftRing, RightRing, Neck, Quiver) serialize as nullable Ids — all resolved against the
entity table on load, same rule as every other reference. Any component field typed
`Entity`/`Entity?`/`List<Entity>` follows this rule (store Id / Id array, never the object).

## Component registry + completeness gate
Components (incl. status effects — one IComponent family) are serialized via an explicit
per-type registry (System.Text.Json source-gen context, extending the PersistenceJsonContext
pattern; discriminator = stable type name).
Family size (measured 2026-07-16): 52 concrete `IComponent` + ~32 `IStatusEffect` (the latter
extends `IComponent`), ~84 total. This hand count is indicative only — the reflection gate's
runtime enumeration is AUTHORITATIVE over any hand count, including this one.
Component `Owner` back-references are RECONSTRUCT-class — NEVER serialized. `Owner` is rebuilt
automatically when a component is attached to its entity on load (Entity.Add sets it), so
serializing it would duplicate graph information already carried by the entity table and invite
inconsistency between the two.
CI COMPLETENESS GATE: a reflection test enumerates every concrete IComponent in the
Logic assembly and asserts (a) registered in the serializer, (b) round-trips a
default-constructed + a property-populated instance losslessly. An unregistered
component is a CI failure, not a silent drop.

## GameState field classification (exhaustive — every field appears in exactly one list)
SERIALIZE: Player, Monsters, FloorItems, Portals, Corpses, Features, StairDown (as Id),
  Map (tiles, explored/FOV), CurrentDepth, TurnCount, TurnLimit, IsDungeonMode,
  Difficulty, Rng (Seed+CallCount), Knowledge, IdentificationRegistry, AppearancePool,
  GroundHazards, LockedDoors, Props, Rooms, MuralTracker, PityTracker, BoonTracker,
  PastSashasEncounteredThisRun, PlayerDeathKillerSpecies, PlayerDeathCause, Ending,
  Weighing, WeighingArena, WeighingAudit, IdAllocator (next-id watermark).
RECONSTRUCT from config on load (never serialized): BoonTable and all ContentLoader
  static content — serializing config invites version skew.
EXCLUDE (transient/debug; must never appear in a save file): IsHarnessMode,
  WeighingAuditOverride, WeighingHeadlessGatePolicy.
If implementation reveals a field not listed here, STOP and flag it in the report
with a proposed classification — do not classify silently.

## File + write discipline
JSON via source-gen context. Atomic write: .tmp then File.Move (PersistentRunState
pattern). Save file carries a schema version int from day one. Logic side exposes
SaveMidRun(GameState) -> bytes/file and LoadMidRun(...) -> GameState; WHEN saves
happen (background/kill) is presentation-side, session 4b.

## Determinism soak (CI-gated, permanent)
S1 Round-trip stability: serialize -> deserialize -> serialize; byte-identical.
S2 Divergence: seeded mid-combat state; run N turns recording a state hash per turn;
   separately save -> load -> run same N turns; hash sequences identical. Multiple
   seeds, N >= 50, includes states with active status effects, possession, portals,
   locked doors, corpses, and mid-cooldown items.
S3 (session 4b, device): kill mid-combat, relaunch, identical state — S2 across a
   process boundary.
