# Art Acceptance Test Scene Spec

Status: v2, adopted 2026-07-16 (diorama ruling). Implements `docs/art_bible.md` §9. Companion: `config/rubric/art-lint-spec.md` Part B.

## 1. Purpose

A single fixed, reproducible scene that every art PR captures before and after. It operationalizes the sticker test: if generated assets can be picked out of this scene, the art fails, regardless of lint results. Lint (Part A) proves palette-level conformance; this scene proves compositional conformance. Both gates are required.

## 2. Mechanism

**Authored data, production renderer.** The scene is a hand-written fixed floor description — tiles, props, creatures, and items at explicit coordinates with explicit tile IDs — injected into the production render path at the generator→renderer seam, and launched via a debug entry point. No parallel scene composition: every pixel is drawn by the same pipeline that draws real floors; only the data is authored instead of generated.

The scene data is versioned repo content. Changing it is a ruling, recorded in the changelog (§9).

Rationale (recorded): the `scenario_*` YAML system is a headless balance-simulation schema with no rendering or prop vocabulary, and the codebase builds scenes programmatically (a single .tscn exists). Neither a scenario file nor an authored .tscn can express or faithfully render this scene. A general authored-floor game feature was considered and deliberately deferred (potential future ruling, motivated by boss encounters, not by test infrastructure).

## 3. Scene content (what must be in frame)

Theme: **sandstone** — it concentrates the burn-down backlog: the `floor_worn` tile (world_3001, the most nonconformant asset in the repo, stamped across floors), all four chest states (5111–5114), the key item (5039), the sign (5077), and all three murals (5070/5071/5075).

One to two connected rooms sized so all of the following are simultaneously inside the portrait viewport at gameplay zoom:

**Floor and structure:** standard sandstone floor with `floor_worn` (3001) present at natural frequency; wall autotile run including at least one corner and one door.

**Generated props — one representative per placement class:**
- `wall_adjacent`: forge (5011) + tool_rack cluster (smithy read)
- `free_standing`: anvil (5001), candelabra (5080/5081)
- `center`: table (505x) with chairs
- `floor_overlay`: rubble (5078/5079), puddle (5110)
- Chests: closed (5111) and open (5112) both visible
- One mural (5075, the worst A4 offender), the sign (5077), the key (5039) on floor

**Canon adjacency (comparison anchors):**
- Orc grunt and troll (canon, balance-locked, stable silhouettes) adjacent to generated props
- 2–3 canon items on the floor within two tiles of the key (5039)
- Canon barrel (268) beside the generated sack (5102)

**UI state:** full gameplay HUD; inventory closed; no modals.

**Deferred content:**
- Hollowmark ribbon: required in frame once the ribbon UI ships (Foundation M1 item 5, not yet built). On landing, add the ribbon with a fixed line (recorded verbatim in §7) via changelog entry. Captures before that date are valid without it.
- Spell/combat fx: excluded from v1 (animation variance). Extend by ruling if fx conformance later needs gating.

## 4. Reproducibility requirements

- The scene is authored and static: identical composition every launch, by construction. No seeds, no rolls, no variant selection.
- No time-of-day, animation-phase, or particle variance in frame. If idle animations exist, capture at a defined tick or pause state.
- Two captures from identical state must be pixel-identical. This is the harness's own acceptance test.

## 5. Capture protocol

- Device: [RULING NEEDED — physical reference device, model + OS; the phone the sticker test is performed on. Emulator captures are supplementary, never the gate.]
- Orientation: portrait, gameplay zoom (no debug zoom).
- Captures per run: (a) full viewport; (b) three fixed 6× nearest-neighbor crops, positions recorded at first capture: the smithy cluster, the chest/key/canon-item area, a floor span containing 3001 tiles.
- Storage: `tools/art_lint/scene_captures/`, named `YYYY-MM-DD_pr<N>_{before|after}_{full|crop1|crop2|crop3}.png`. Committed with the PR.

## 6. Pass criteria (scored per Part B rubric)

1. **Sticker test:** viewing the full capture on the reference device at arm's length, generated assets cannot be sorted from canon. Pass/fail, scored by Rafe.
2. **Squint test:** creatures and threat-relevant objects remain readable and distinguishable from decor. Pass/fail.
3. **Crop comparison:** in each 6× crop, no generated asset reads as a different hand than its canon neighbors. Pass/fail per crop.
4. Optional strengthening (recommended once burn-down nears completion): blinded sort of shuffled single-asset 6× crops; identification above chance fails.

Baseline expectation at adoption: the scene FAILS today. The first capture is the "before" for the entire burn-down; the burn-down is done when this scene passes.

## 7. Adoption parameters

| parameter | value |
|---|---|
| reference device | TBD |
| gameplay zoom / visible tile span | record at first capture |
| Hollowmark ribbon fixed line | deferred to M1 item 5 landing |
| crop positions (3) | record at first capture (tile coordinates) |

## 8. Scope boundary (recorded)

This scene gates art conformance only: pixels in composition. It does not exercise the dungeon generator or `RoomPropPlacer`, and it is explicitly not a regression gate for placement logic or generator behavior. Render-integration regressions (layering, y-sort, theming bugs) that alter this scene's output will be visible in captures but are filed as render bugs, not art failures.

## 9. Changelog

- v2 (2026-07-16): mechanism changed from scenario-YAML to authored-data-into-production-renderer after schema verification showed `ScenarioDefinition` is a headless balance harness with no rendering or prop vocabulary. Seed machinery removed (authored scene is static by construction). Ribbon requirement deferred to M1 item 5. Scope boundary (§8) added.
- v1 (2026-07-16): initial draft (scenario-YAML mechanism; superseded).
