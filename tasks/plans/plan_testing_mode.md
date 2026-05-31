# Plan: In-Game Testing Mode

Status: [x] Complete — 2026-05-28
PoC reference: io_layer/bot_brain.py, config/levels/level_templates.yaml (levels 91-99)

---

## What It Is

An in-game "developer menu" accessible at game start (or via secret input) that lets you load specific testing scenarios directly. As the game gets deeper and more complex, you cannot possibly test everything by playing normally. You need to be able to say "load me the trap test, give me a disarm scroll, put me in front of a web trap" in 2 taps.

This is non-negotiable for playtesting anything beyond basic combat. The PoC had this from Phase 12 onward and it was essential.

---

## Testing Menu Flow

```
Main Menu
├── New Game
├── Continue
├── [DEV] Testing Mode        ← only visible in debug builds
│   ├── Combat Tests
│   │   ├── Basic Melee Arena
│   │   ├── Ranged Viability
│   │   ├── Knockback Test
│   │   └── ...
│   ├── Item Tests
│   │   ├── All Potions (identified)
│   │   ├── Wand Battery
│   │   ├── Identify Scroll
│   │   └── ...
│   ├── Trap Tests
│   │   ├── Spike Trap
│   │   ├── Web Trap
│   │   ├── Alarm Plate
│   │   └── ...
│   ├── Map Tests
│   │   ├── Locked Doors
│   │   ├── Secret Rooms
│   │   ├── Portal Network
│   │   └── ...
│   └── Load Custom Scenario (YAML file picker)
└── Settings
```

---

## Testing YAML Format

Each test scenario is a YAML file that completely defines the starting state:

```yaml
scenario_id: spike_trap_identity
name: "Spike Trap — Detection and Disarm"
testing_mode: true
all_items_identified: true     # Override identification system

player:
  position: [10, 10]
  hp: 50
  max_hp: 50
  inventory:
    - healing_potion × 3
  equipment:
    weapon: longsword
    armor: leather_armor

floor:
  width: 20
  height: 20
  theme: stone

features:
  - type: spike_trap
    position: [12, 10]    # 2 tiles in front of player
  - type: spike_trap
    position: [10, 14]    # different approach
  - type: sign
    position: [15, 10]
    message: "Walk into the trap. Try to detect. Try to disarm."

monsters: []              # No monsters for this test
```

---

## Testing-Specific Overrides

When `testing_mode: true`:
- `all_items_identified: true` — skip identification system
- `god_mode: false` — player still takes damage (you need realistic testing)
- `infinite_potions: false` — consumables work normally
- `reveal_map: false` — fog of war still active
- `no_traps: false` — you can turn traps OFF for certain tests too

---

## Load Custom Scenario (File Picker)

On mobile: open a native file picker pointing to the app's Documents directory (or iCloud). Player (developer) can drop YAML files there and load them.

On desktop: file picker dialog for .yaml files.

This is the power feature: you can create a new test scenario in a text editor, drop it in the folder, and it's immediately loadable without recompiling anything. This is how rapid iteration works.

---

## Testing Levels 91–99 (Legacy PoC Approach)

The PoC used special floor numbers for testing:
- Level 91: Door/key testing
- Level 92: Secret room discovery
- Level 93: Trap placement and detection
- Level 94: Stair mechanics
- Level 95: Corridor style testing
- Level 96: Faction hostility verification
- Level 97: Encounter budget compliance
- Level 98: Loot policy soft bias and injection
- Level 99: Comprehensive smoke test

For the C# port, these should be scenario YAML files instead of hardcoded level numbers. The same concept, but data-driven.

---

## Visibility in Builds

- Development builds (Godot `OS.is_debug_build()`): Testing Mode visible
- Release builds: Hidden (but still accessible via secret input if needed)
- CI/harness builds: All test scenarios accessible via command line

---

## Implementation Notes

- `TestingModeManager` handles menu construction from discovered scenario files
- Scenarios loaded from `res://config/testing/` (bundled) OR `user://testing/` (user-added)
- Testing scenario loader bypasses normal dungeon generation entirely
- All testing overrides applied before first frame
- The menu is a Godot scene; the scenarios themselves are pure logic-layer

---

## C# Port Checklist

- [x] Testing menu scene (dev-only visible) — MainMenuPanel debug gate
- [x] `TestScenarioLoader` — embedded in Main.cs LaunchTestScenario (arena + dungeon modes)
- [x] Testing scenario YAML format — ScenarioDefinition with category/all_items_identified/default_bot_persona
- [x] Testing overrides — `all_items_identified` (IdentificationRegistry.AlwaysIdentified), `default_bot_persona` auto-starts BotPlayerDriver
- [x] Bundled test scenarios — Combat, Status Effects, Spells & Wands, Ranged Combat, Traps, Possession, Factions, Bot, Presentation, General
- [x] `user://testing/` directory scanning — ScanTestDirectory scans both res:// and user://
- [ ] Mobile: file picker integration — deferred (user:// scanning covers the main need)
- [x] Debug build gate — OS.IsDebugBuild() gate in MainMenuPanel
- [x] Scenario categories in menu — TestMenuPanel groups by category with headers
- [x] Testing scenarios for each system — 18 scenarios across 10 categories
