# Plan: Bot Personas for Automated Playtesting

Status: [x] Complete 2026-05-22 — see [plan_bot_personas_impl.md](plan_bot_personas_impl.md) for full detail.
PoC reference: io_layer/bot_brain.py (Phase 17B)

---

## What It Is

Five named bot personas that control how the automated player makes decisions during harness runs. Each persona simulates a different player archetype. Without distinct personas, all harness runs reflect the same "average" behavior and miss pathological edge cases.

---

## The Five Personas

### `balanced` (default)

Standard cautious-but-engaged player.
- Retreat HP threshold: 25%
- Potion HP threshold: 30%
- Combat engagement range: 8 tiles
- Loot priority: 1 (normal — picks up items)
- Combat healing: enabled

### `cautious`

New player or survival-focused player.
- Retreat HP threshold: 40% (retreats early)
- Potion HP threshold: 50% (heals aggressively)
- Combat engagement range: 5 tiles (won't chase far)
- Loot priority: 1 (normal)
- Panic mode: activates at 30% HP if 2+ enemies adjacent → drinks potion regardless
- Will avoid engaging non-adjacent enemies if already damaged

### `aggressive`

Fighter who fights to the death, ignores loot.
- Retreat HP threshold: 10% (almost never retreats)
- Potion HP threshold: 20%
- Combat engagement range: 12 tiles (chases everything)
- Loot priority: 0 (ignores all items)
- No healing items (or uses them only at death's door)

### `greedy`

Loot-focused player who prioritizes items over efficient combat.
- Retreat HP threshold: 25%
- Potion HP threshold: 40%
- Combat engagement range: 6 tiles
- Loot priority: 2 (heavily prioritizes item collection over movement)
- Will detour significantly to pick up items

### `speedrunner`

Rushes to stairs, avoids combat when possible.
- Retreat HP threshold: 30%
- Potion HP threshold: 40%
- Combat engagement range: 4 tiles (minimal combat)
- Loot priority: 0 (skips all items)
- Movement: strongly prefers stairs over exploration
- Will abandon fight if an escape path opens

---

## Bot Decision State Machine

Three states:

1. **EXPLORING** — no enemies in FOV
   - Auto-explore: pathfind to unrevealed tiles
   - Pick up items if loot_priority > 0
   - Navigate toward stairs if speedrunner
   - Terminal: "All areas explored" → go to stairs

2. **COMBAT** — enemies in FOV
   - Pathfind to nearest hostile target
   - Attack adjacent enemies
   - Retreat if HP < retreat_threshold
   - Drink potion if HP < potion_threshold
   - Panic heal if: HP < panic_threshold AND enemies_adjacent >= panic_multi_enemy_count

3. **STUCK** — no progress for 8+ consecutive turns
   - Attempt random movement
   - Force-drink a potion if available
   - After 15 stuck turns: scenario ends as "stuck" (not death)

---

## Heal Configuration Per Persona

```csharp
// Conceptual structure
public class BotHealConfig {
    public float BaseHealThreshold;        // HP% to normally drink potion
    public float PanicThreshold;           // HP% for panic healing
    public int PanicMultiEnemyCount;       // # adjacent enemies to trigger panic
    public bool AllowCombatHealing;        // can heal mid-combat?
}
```

All current personas have combat healing enabled.

---

## Why Multiple Personas Matter

**Aggressive** bot + depth 4 monsters → measures true combat lethality without healing as a crutch
**Cautious** bot → measures whether the game is survivable with defensive play; reveals if healing items are sufficient
**Speedrunner** → measures stair accessibility; reveals if exploration is required or optional
**Greedy** → measures item impact; if greedy bot does dramatically better, items are too powerful

Without distinct personas, you only know "how hard is it for an average bot." You don't know WHY it's hard.

---

## Scenario Bot Selection

Each scenario YAML specifies which bot persona runs it:

```yaml
scenario_id: depth3_orc_pressure
player_bot: balanced   # or cautious, aggressive, greedy, speedrunner
```

Some scenarios run multiple times with different bots to cover behavioral variance.

---

## Implementation Notes

- `BotBrain` class with persona config injected at construction
- Persona config loaded from `config/bot_personas.yaml`
- Decision methods parameterized by persona thresholds
- State transitions: EXPLORING ↔ COMBAT based on enemy FOV
- All bot decisions must go through the same `PlayerAction` pipeline as human input
- Bot should be testable in isolation (unit tests on decision logic)

---

## C# Port Checklist

- [ ] `BotPersona` YAML definition (5 personas with all thresholds)
- [ ] `BotBrainConfig` loading from YAML
- [ ] `BotBrain` state machine (EXPLORING / COMBAT / STUCK)
- [ ] Combat decision: engage, attack, retreat, heal
- [ ] Exploration decision: auto-explore, item pickup, stair priority
- [ ] Panic heal trigger
- [ ] Stuck detection (N consecutive no-progress turns)
- [ ] Scenario YAML: `player_bot` field selects persona
- [ ] Persona-specific behavioral differences actually affecting decisions
- [ ] Harness: bot persona logged in run metadata
- [ ] Test: each persona produces measurably different survival rates
