# RUN REPORT — overnight queue, 2026-09-13

Lane `art/queue-2026-09-13`, off main `f8a3f40d`. Autonomy rules: no turn ends until a trigger
or the queue empties. Install-latest on PASS. **Palette lock fenced off** — nothing here touches
§5.1 / #204's ladder snapping.

| # | item | state |
|---|---|---|
| 5 | GPU headroom — one measurement with vsync off, report, no tuning | pending |
| 4 | Fire — expose the remaining PLACEHOLDER values (radius, tint) on the panel; rule nothing | pending |
| 1 | #207 barricade flips — A stands across the line, held, bindings gripping; B breaks the pitch; cold naming says "a barricade" | pending |
| 2 | #212 prop placement / depth order — props sit against walls under the top band | pending |
| 3 | #211 wall ends, corners, pillars gain the east face at ½ depth (§3.2) | pending |
| — | frame critic (5 seats, shadowed regime) → install-latest on PASS | pending |

Order: 5 and 4 are independent and small; 1 changes the props; 2 and 3 change the engine's
picture; the critic runs once, last, on the frozen tree.

## Log

### 5. GPU headroom — DONE (reported, not tuned)
- Vsync cannot be disabled on the SE: `DisplayServer.WindowSetVsyncMode(Disabled)` + `MaxFps 0`
  produced the identical 16.67 ms windows (iOS paces every frame). Process delta proves the frame
  is MET and nothing else.
- So the renderer's own per-viewport measurement was added to `[Perf]`: **CPU render
  1.41–1.65 ms/frame** (≈15 ms of headroom on the CPU side) with 216 wall occluders, 3 prop
  occluders, two shadow-casting lights, softness 12. **GPU: the timestamp query returns 0.00 on
  iOS Forward Mobile / Metal — no instrument.** The line now prints `NO-INSTRUMENT` rather than a
  zero. The next tool is Xcode's GPU frame capture, outside this queue.
- Evidence: `tools/cast_shadows/evidence/headroom_boot.log`, `headroom_install.log`.
  Build `headroom` (SKIPPED-REVIEW, vsync off, own bundle id) stays on the phone for the record.

### 4. Fire knobs — DONE (exposed, not ruled)
- Rig panel gains `fire r` (reach, 1.0–8.0 tiles, step 0.5; rebuilds the fire's falloff texture)
  and `fire tint` (a ladder of seven warm hues from `ff6a1e` to `ffd4a0`, `ff8a3c` at 1/7 as
  today's). Energy stays at Rafe's 1.6 mark. The settings line now carries `fire_radius` and
  `fire_tint` so a MARK WALK records them. Nothing ruled.

### 1. #207 barricade flips — DONE (cold naming PASS ×3, the word is "barricade")
- **The bar first:** `cold_naming.py`'s barricade term now accepts only the object (barricade,
  barrier, blockade, roadblock, cheval de frise, obstacle) and refuses what the walk and the card
  reject by name (bench, bed, bricks, sticks, pile, jumble, fence…). "timber / logs / planks" no
  longer count — Rafe's words: reads as wood but not as a barricade. Stricter, so the pre-§12.2
  calibration frame still MISSes it.
- **Variant A stands across the line, held:** an X-frame — two baulks stood on end and crossed at
  the centre (`tiltbox`, a new x–z rotation in `projection_mesh`), a bar lashed behind the
  crossing, rope wrapped at the crossing and both bar ends (§7.1). Chest-high (44 of 64). And
  it is PLACED across a line: the gap between the west wall (2,15) and the pillar (5,15) — in
  open floor the same frame read as "crossed broken planks"; closing a gap it read as
  "a cross-braced barricade" / "a broken wooden barricade".
- **Variant B:** "break the pitch" was done first (unequal, skewed, offset baulks, one leaning)
  and three of three seats still called it *a bench or table* — parallel beams at any pitch are
  furniture-shaped. So B is the family's other crossing: a Λ-frame, two baulks leaning together
  at the apex, a bar lashed low, rope at apex and bar ends. Read as "a wooden A-frame …
  wooden barricade", "sawhorse-style barricade". Placed against the north wall's east end at
  (9,12) beside the fire (its cast shadow), one cell in from the frame edge.
- Generation as before (projected template → pixflux surface at strength 150, three seeds, pick
  by hold: A 0.978, B 0.961). The scene's pocket at (3,13) sealed with A in place until B moved;
  the 56 scene tests are green. Cold naming PASS on three consecutive runs.
- Residual, for Rafe's eye: seats hedge with "broken" / "sawhorse-style" — a standing frame in a
  front elevation on a top-down floor is §3.2's inherent tension, and the seats read it as
  fallen or as a workshop object. The word is met; whether the register is, is the walk's.
