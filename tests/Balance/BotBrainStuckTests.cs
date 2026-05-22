using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Tests for BotBrain stuck detection (TASK-004).
///
/// Stuck detection fires only on the INSTANCE path (BotBrain instance reused across calls).
/// The static BotBrain.Decide wrapper creates a transient instance per call —
/// stuck detection never fires on the static path. This is intentional.
///
/// Thresholds (from PoC bot_brain.py:33, STUCK_THRESHOLD = 8):
///   - 8 consecutive stuck turns: drop target, wait 1 turn
///   - 15 consecutive stuck turns: return BotAction.AbortRun
/// </summary>
[TestFixture]
[Category("Bot")]
[Description("BotBrain stuck detection: instance state, drop target at 8, abort at 15")]
public class BotBrainStuckTests
{
    // ── State helpers ─────────────────────────────────────────────────────────

    private static (Entity Player, Fighter PlayerFighter, Inventory PlayerInventory, GameMap Map)
        MakeArena(int playerHp = 54)
    {
        const int Width = 20, Height = 20;
        var map = new GameMap(Width, Height, allWalls: true);
        for (int x = 1; x < Width - 1; x++)
            for (int y = 1; y < Height - 1; y++)
                map.SetTile(x, y, TileKind.Floor);

        var player = new Entity(0, "Player", 10, 10, blocksMovement: true);
        var fighter = new Fighter(
            hp: playerHp, strength: 12, dexterity: 14, constitution: 10,
            accuracy: 2, evasion: 1, damageMin: 1, damageMax: 4);
        player.Add(fighter);
        var inventory = new Inventory();
        player.Add(inventory);
        map.RegisterEntity(player);
        return (player, fighter, inventory, map);
    }

    private static Entity MakeMonster(int id, int x, int y, GameMap map, int hp = 100)
    {
        var orc = new Entity(id, "Orc", x, y, blocksMovement: true);
        // High hp so the monster doesn't die from stuck-counter increments
        orc.Add(new Fighter(hp: hp, strength: 14, dexterity: 10, constitution: 12,
            accuracy: 4, evasion: 1, damageMin: 4, damageMax: 6));
        map.RegisterEntity(orc);
        return orc;
    }

    // ── Test 1: Static path never gets stuck ──────────────────────────────────

    [Test]
    [Description("Static BotBrain.Decide never returns AbortRun — each call is a fresh instance")]
    public void Static_Decide_NeverReturnsAbortRun()
    {
        var (player, fighter, inventory, map) = MakeArena();
        // Monster at distance 3 — player will move toward it but can't reach (no actual movement)
        var enemy = MakeMonster(1, 13, 10, map);
        var monsters = new List<Entity> { enemy };

        // Call 20 times — well past both stuck thresholds
        for (int i = 0; i < 20; i++)
        {
            var action = BotBrain.Decide(player, fighter, inventory, monsters, map);
            Assert.That(action.Type, Is.Not.EqualTo(BotAction.ActionType.AbortRun),
                $"Static path call {i+1}: should never return AbortRun (no instance state)");
        }
    }

    // ── Test 2: Instance drops target at stuck threshold ─────────────────────

    [Test]
    [Description("Instance BotBrain: 9 same-position turns returns Wait on turn 9 (drops target at 8)")]
    public void Instance_DropsTarget_After8StuckTurns()
    {
        var (player, fighter, inventory, map) = MakeArena();
        // Enemy at distance 3 — player at (10,10), enemy at (13,10)
        // Player can't actually move in this test (we call Decide without ProcessTurn),
        // so positions don't change, simulating a stuck state.
        var enemy = MakeMonster(1, 13, 10, map);
        var monsters = new List<Entity> { enemy };

        var brain = new BotBrain(BotPersonaRegistry.Get("balanced"));

        // First 8 calls: all should be MoveToward (stuck counter increments each turn)
        for (int i = 0; i < 8; i++)
        {
            var action = brain.Decide(player, fighter, inventory, monsters, map);
            Assert.That(action.Type, Is.EqualTo(BotAction.ActionType.MoveToward),
                $"Turn {i+1}: should be MoveToward before stuck threshold");
        }

        // Turn 9 (stuck counter reaches 8): should drop target and return Wait
        var stuckAction = brain.Decide(player, fighter, inventory, monsters, map);
        Assert.That(stuckAction.Type, Is.EqualTo(BotAction.ActionType.DoNothing),
            "Turn 9: should return Wait after dropping target at stuck threshold 8");
    }

    [Test]
    [Description("Instance BotBrain: with a second enemy available, bot targets it after dropping enemy1")]
    public void Instance_TargetsAlternativeEnemy_WhenAvailable()
    {
        var (player, fighter, inventory, map) = MakeArena();
        var enemy1 = MakeMonster(1, 13, 10, map); // far enemy
        var enemy2 = MakeMonster(2, 12, 10, map); // closer enemy (Manhattan 2) — will be added on turn 9

        var brain = new BotBrain(BotPersonaRegistry.Get("balanced"));

        // Run 8 turns with only enemy1 — bot moves toward it, counter climbs
        var monstersOneEnemy = new List<Entity> { enemy1 };
        for (int i = 0; i < 8; i++)
            brain.Decide(player, fighter, inventory, monstersOneEnemy, map);

        // Turn 9 fires the drop (counter=8)
        var drop = brain.Decide(player, fighter, inventory, monstersOneEnemy, map);
        Assert.That(drop.Type, Is.EqualTo(BotAction.ActionType.DoNothing),
            "Turn 9: drop should fire");

        // Now add enemy2 — the brain should prefer enemy2 over the dropped enemy1
        // But counter is still >= 8, so it will keep dropping until counter reaches 15
        // OR until the bot successfully targets the alternative.
        // When enemy2 is available and enemy1 is dropped, FindNearest finds enemy2 (closer),
        // which is not the dropped target, so the bot should target enemy2.
        var monstersTwo = new List<Entity> { enemy1, enemy2 };
        var action10 = brain.Decide(player, fighter, inventory, monstersTwo, map);

        // enemy2 (at distance 2) is closer than enemy1 (at distance 3), so FindNearest returns enemy2.
        // enemy2 is NOT the dropped target → bot should move toward enemy2
        // HOWEVER: counter is still 9 >= 8, so UpdateStuck will run and then check >= 8.
        // The positions changed (enemy2 is at different position than enemy1 was last turn)
        // so counter resets to 0. Then bot moves toward enemy2.
        Assert.That(action10.Type, Is.EqualTo(BotAction.ActionType.MoveToward),
            "Turn 10 with closer enemy2: should move toward the alternative enemy");
        Assert.That(action10.Target, Is.SameAs(enemy2),
            "Should target the closer enemy2, not the dropped enemy1");
    }

    // ── Test 3: AbortRun at 15 stuck turns ────────────────────────────────────

    [Test]
    [Description("Instance BotBrain: 15 stuck turns returns AbortRun")]
    public void Instance_ReturnsAbortRun_After15StuckTurns()
    {
        var (player, fighter, inventory, map) = MakeArena();
        // Place enemy so player always moves toward it but never reaches it
        var enemy = MakeMonster(1, 13, 10, map);
        var monsters = new List<Entity> { enemy };

        var brain = new BotBrain(BotPersonaRegistry.Get("balanced"));

        BotAction? abortAction = null;

        // Counter does NOT reset when dropping target — it keeps climbing from 8 to 15.
        // Turn-by-turn trace for a single enemy at (13,10) that never moves:
        //   Turns 1-8:  MoveToward (counter 0..7)
        //   Turn 9:     Wait/DoNothing (drop fires at counter=8; counter stays 8)
        //   Turns 10-14: Wait/DoNothing (drop fires again at 9,10,11,12,13,14; counter climbs)
        //   Turn 15: AbortRun (counter reaches 15)
        // Total: should abort by turn ~16. Run 20 turns for safety.
        for (int i = 0; i < 20; i++)
        {
            var action = brain.Decide(player, fighter, inventory, monsters, map);
            if (action.Type == BotAction.ActionType.AbortRun)
            {
                abortAction = action;
                break;
            }
        }

        Assert.That(abortAction, Is.Not.Null,
            "Should have received AbortRun within 20 turns of stuck bot (counter climbs 0→15 without resetting)");
        Assert.That(abortAction!.Type, Is.EqualTo(BotAction.ActionType.AbortRun));
    }

    // ── Test 4: Attack resets stuck counter ───────────────────────────────────

    [Test]
    [Description("Instance BotBrain: actual attack action resets stuck counter (won't abort if making progress)")]
    public void Instance_AttackResetsStuckCounter()
    {
        var (player, fighter, inventory, map) = MakeArena();
        // Enemy adjacent (Chebyshev 1) — player will attack it each turn
        var enemy = MakeMonster(1, 11, 10, map);
        var monsters = new List<Entity> { enemy };

        var brain = new BotBrain(BotPersonaRegistry.Get("balanced"));

        // Run 20 turns with an adjacent enemy — bot attacks every turn, no stuck
        for (int i = 0; i < 20; i++)
        {
            var action = brain.Decide(player, fighter, inventory, monsters, map);
            Assert.That(action.Type, Is.Not.EqualTo(BotAction.ActionType.AbortRun),
                $"Turn {i+1}: should never abort when enemy is adjacent and bot is attacking");
            // Attack is the expected action
            Assert.That(action.Type, Is.EqualTo(BotAction.ActionType.AttackTarget),
                $"Turn {i+1}: should attack adjacent enemy");
        }
    }

    // ── Test 5: AbortRun plumbing ─────────────────────────────────────────────

    [Test]
    [Description("BotAction.AbortRun sentinel: ToPlayerAction returns Wait (safe fallback)")]
    public void AbortRun_ToPlayerAction_ReturnsSafeWait()
    {
        var abortAction = BotAction.AbortRun;
        var playerAction = BotBrain.ToPlayerAction(abortAction);
        Assert.That(playerAction.Kind, Is.EqualTo(PlayerAction.ActionKind.Wait),
            "AbortRun.ToPlayerAction() should return Wait as a safe sentinel");
    }

    [Test]
    [Description("BotAction.ActionType.AbortRun enum value exists")]
    public void AbortRun_ActionTypeEnumExists()
    {
        Assert.That(Enum.IsDefined(typeof(BotAction.ActionType), "AbortRun"),
            "BotAction.ActionType.AbortRun enum value must exist");
    }

    // ── Test 6: Static path isolation ────────────────────────────────────────

    [Test]
    [Description("Static BotBrain.Decide(... persona: ...) accepts persona parameter")]
    public void Static_Decide_AcceptsPersonaParameter()
    {
        var (player, fighter, inventory, map) = MakeArena();
        var enemy = MakeMonster(1, 11, 10, map);
        var monsters = new List<Entity> { enemy };

        // Verify the static method compiles and runs with an explicit persona
        Assert.DoesNotThrow(() =>
        {
            var _ = BotBrain.Decide(player, fighter, inventory, monsters, map,
                persona: BotPersonaRegistry.Get("aggressive"));
        }, "Static BotBrain.Decide with persona parameter should not throw");
    }
}
