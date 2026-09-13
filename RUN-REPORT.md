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
