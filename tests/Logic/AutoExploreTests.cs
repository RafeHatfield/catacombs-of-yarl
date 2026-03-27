using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Logic;

[TestFixture]
public class AutoExploreTests
{
    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    /// <summary>
    /// Build a dungeon-mode GameState with a small carved map (walls on border, floor inside).
    /// IsDungeonMode=true so RecomputeFov is active.
    /// </summary>
    private static GameState MakeDungeonState(int width = 15, int height = 15,
        int playerX = 7, int playerY = 7)
    {
        var map = new GameMap(width, height, allWalls: true);
        // Carve interior as floor
        for (int x = 1; x < width - 1; x++)
            for (int y = 1; y < height - 1; y++)
                map.SetTile(x, y, TileKind.Floor);

        var player = new Entity(0, "Player", playerX, playerY, blocksMovement: true);
        player.Add(new Fighter(hp: 20, strength: 10, dexterity: 10, constitution: 10,
            accuracy: 2, evasion: 1, damageMin: 1, damageMax: 4));
        map.RegisterEntity(player);

        var state = new GameState(player, new List<Entity>(), map, new SeededRandom(42))
        {
            IsDungeonMode = true,
            CurrentDepth = 1
        };
        state.RecomputeFov();
        return state;
    }

    /// <summary>
    /// Add a monster to an existing state's map and monster list.
    /// Note: Monsters list is read-only via property but backed by the list passed to constructor.
    /// We store the list and pass it in to allow mutation in tests.
    /// </summary>
    private static (GameState State, List<Entity> MonsterList) MakeDungeonStateWithMonsterList(
        int width = 25, int height = 25, int playerX = 2, int playerY = 2)
    {
        var map = new GameMap(width, height, allWalls: true);
        for (int x = 1; x < width - 1; x++)
            for (int y = 1; y < height - 1; y++)
                map.SetTile(x, y, TileKind.Floor);

        var player = new Entity(0, "Player", playerX, playerY, blocksMovement: true);
        player.Add(new Fighter(hp: 20, strength: 10, dexterity: 10, constitution: 10,
            accuracy: 2, evasion: 1, damageMin: 1, damageMax: 4));
        map.RegisterEntity(player);

        var monsters = new List<Entity>();
        var state = new GameState(player, monsters, map, new SeededRandom(42))
        {
            IsDungeonMode = true,
            CurrentDepth = 1
        };
        state.RecomputeFov();
        return (state, monsters);
    }

    private static Entity MakeMonster(int id, int x, int y)
    {
        var m = new Entity(id, "TestOrc", x, y, blocksMovement: true);
        m.Add(new Fighter(hp: 10, strength: 10, dexterity: 10, constitution: 10,
            accuracy: 2, evasion: 1, damageMin: 1, damageMax: 2));
        return m;
    }

    // -----------------------------------------------------------------------
    // Activation
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_Activate_SetsIsActive()
    {
        var state = MakeDungeonState();

        AutoExploreSystem.Activate(state);

        var ae = state.Player.Get<AutoExploreState>();
        Assert.That(ae, Is.Not.Null, "AutoExploreState component should be added on Activate");
        Assert.That(ae!.IsActive, Is.True);
    }

    [Test]
    public void AutoExplore_Activate_ClearsStopReason()
    {
        var state = MakeDungeonState();
        // Pre-set a stale stop reason to confirm Activate clears it
        var ae = state.Player.GetOrAdd<AutoExploreState>();
        ae.StopReason = "stale reason";

        AutoExploreSystem.Activate(state);

        Assert.That(ae.StopReason, Is.Null);
    }

    // -----------------------------------------------------------------------
    // Basic movement
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_GetNextAction_ReturnsMove_WhenUnexploredTilesExist()
    {
        // Small 15x15 map — player starts at (7,7) and can only see nearby tiles.
        // There will be many unexplored tiles further away.
        var state = MakeDungeonState();

        AutoExploreSystem.Activate(state);
        var action = AutoExploreSystem.GetNextAction(state);

        Assert.That(action, Is.Not.Null, "Should return a move action when unexplored tiles exist");
        Assert.That(action!.Kind, Is.EqualTo(PlayerAction.ActionKind.Move));
        Assert.That(action.TargetX, Is.Not.Null);
        Assert.That(action.TargetY, Is.Not.Null);
    }

    [Test]
    public void AutoExplore_StopsWhenFullyExplored()
    {
        // Use a very small map so we can fully explore it in a reasonable number of steps
        var state = MakeDungeonState(width: 9, height: 9, playerX: 4, playerY: 4);

        AutoExploreSystem.Activate(state);

        // Simulate exploration: get action, teleport player to destination, recompute FOV
        // Loop until auto-explore stops or we hit a safety limit
        const int maxIterations = 200;
        int iterations = 0;
        PlayerAction? action;

        do
        {
            action = AutoExploreSystem.GetNextAction(state);
            if (action == null) break;

            // Teleport player to target (bypasses TurnController — tests AutoExploreSystem logic)
            state.Player.X = action.TargetX!.Value;
            state.Player.Y = action.TargetY!.Value;
            state.RecomputeFov();

            iterations++;
        }
        while (iterations < maxIterations);

        var ae = state.Player.Get<AutoExploreState>();
        Assert.That(action, Is.Null, "GetNextAction should return null when exploration completes");
        Assert.That(ae?.StopReason, Does.Contain("complete").IgnoreCase,
            "StopReason should indicate exploration complete");
    }

    // -----------------------------------------------------------------------
    // Interrupt: new monster in FOV
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_StopsOnNewMonsterInFov()
    {
        // Use a large map so FOV doesn't immediately cover the monster at spawn
        var (state, monsters) = MakeDungeonStateWithMonsterList(width: 25, height: 25,
            playerX: 2, playerY: 2);

        // Place monster far away (outside initial FOV radius of 8)
        var monster = MakeMonster(1, 20, 20);
        monsters.Add(monster);
        state.Map.RegisterEntity(monster);

        AutoExploreSystem.Activate(state);

        // Verify first action is valid (monster not in FOV yet)
        var firstAction = AutoExploreSystem.GetNextAction(state);
        Assert.That(firstAction, Is.Not.Null, "Auto-explore should start moving");

        // Teleport player next to the monster so it enters FOV
        state.Player.X = 20;
        state.Player.Y = 19;
        state.RecomputeFov();

        // Monster should now be visible — next GetNextAction should stop
        var stopAction = AutoExploreSystem.GetNextAction(state);
        Assert.That(stopAction, Is.Null, "Should stop when new monster enters FOV");

        var ae = state.Player.Get<AutoExploreState>();
        Assert.That(ae?.StopReason, Does.Contain("Monster").IgnoreCase);
    }

    [Test]
    public void AutoExplore_DoesNotStopForMonsterVisibleAtActivation()
    {
        // Monster visible at activation should be in KnownMonsterIds — don't interrupt for it
        var (state, monsters) = MakeDungeonStateWithMonsterList(width: 15, height: 15,
            playerX: 7, playerY: 7);

        // Place monster adjacent to player (definitely in initial FOV)
        var monster = MakeMonster(1, 8, 7);
        monsters.Add(monster);
        state.Map.RegisterEntity(monster);
        state.RecomputeFov();

        Assert.That(state.Map.IsVisible(8, 7), Is.True, "Monster must be visible at activation");

        AutoExploreSystem.Activate(state);

        // First GetNextAction should NOT be null — monster was visible at activation
        var action = AutoExploreSystem.GetNextAction(state);
        Assert.That(action, Is.Not.Null,
            "Should not stop for a monster that was visible at activation");
    }

    // -----------------------------------------------------------------------
    // Interrupt: damage taken
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_StopsOnDamageTaken()
    {
        var state = MakeDungeonState();

        AutoExploreSystem.Activate(state);

        // Simulate taking damage — reduce HP directly
        state.PlayerFighter.Hp -= 5;

        var action = AutoExploreSystem.GetNextAction(state);
        Assert.That(action, Is.Null, "Should stop when player takes damage");

        var ae = state.Player.Get<AutoExploreState>();
        Assert.That(ae?.StopReason, Does.Contain("damage").IgnoreCase);
    }

    // -----------------------------------------------------------------------
    // Interrupt: oscillation detection
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_OscillationDetected_IsOscillating_ReturnsTrue()
    {
        var ae = new AutoExploreState();

        // Record A-B-A-B-A-B pattern
        ae.RecordPosition(1, 1); // A
        ae.RecordPosition(2, 2); // B
        ae.RecordPosition(1, 1); // A
        ae.RecordPosition(2, 2); // B
        ae.RecordPosition(1, 1); // A
        ae.RecordPosition(2, 2); // B

        Assert.That(ae.IsOscillating(), Is.True, "Should detect A-B-A-B-A-B oscillation");
    }

    [Test]
    public void AutoExplore_NoOscillation_IsOscillating_ReturnsFalse()
    {
        var ae = new AutoExploreState();

        // Forward movement — no oscillation
        ae.RecordPosition(1, 1);
        ae.RecordPosition(2, 2);
        ae.RecordPosition(3, 3);
        ae.RecordPosition(4, 4);
        ae.RecordPosition(5, 5);
        ae.RecordPosition(6, 6);

        Assert.That(ae.IsOscillating(), Is.False, "Forward movement should not be detected as oscillation");
    }

    [Test]
    public void AutoExplore_InsufficientHistory_IsOscillating_ReturnsFalse()
    {
        var ae = new AutoExploreState();

        // Only 4 positions — not enough for full pattern detection
        ae.RecordPosition(1, 1);
        ae.RecordPosition(2, 2);
        ae.RecordPosition(1, 1);
        ae.RecordPosition(2, 2);

        Assert.That(ae.IsOscillating(), Is.False, "Need 6 positions to detect oscillation");
    }

    // -----------------------------------------------------------------------
    // Interrupt: stuck detection
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_StuckCounter_Stops_AfterThreeMissedSteps()
    {
        var state = MakeDungeonState();

        AutoExploreSystem.Activate(state);

        // Get first action — this sets LastExpectedPosition
        var action = AutoExploreSystem.GetNextAction(state);
        Assert.That(action, Is.Not.Null, "Precondition: should get initial action");

        var ae = state.Player.Get<AutoExploreState>()!;
        // Do NOT move the player — simulate blocked movement.
        // LastExpectedPosition is now set to somewhere the player isn't.
        // Each call to GetNextAction increments StuckCounter when position doesn't match.

        // Call 1 — StuckCounter goes to 1
        var a1 = AutoExploreSystem.GetNextAction(state);
        // Call 2 — StuckCounter goes to 2
        var a2 = AutoExploreSystem.GetNextAction(state);
        // Call 3 — StuckCounter reaches 3 → should stop
        var a3 = AutoExploreSystem.GetNextAction(state);

        // At least one of these should be null (stop at count >= 3)
        // a3 should definitely be null if stuck 3 times (the 3rd miss triggers the stop)
        Assert.That(ae.IsActive, Is.False, "Auto-explore should deactivate after 3 blocked steps");
        Assert.That(ae.StopReason, Does.Contain("blocked").IgnoreCase);
    }

    // -----------------------------------------------------------------------
    // Known stairs — no repeat stop
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_KnownStairs_DoesNotStopRepeatedly()
    {
        var state = MakeDungeonState();

        // Place stair-down entity adjacent to player (within initial FOV)
        var stair = new Entity(99, "StairDown", 8, 7, blocksMovement: false);
        state.StairDown = stair;
        state.RecomputeFov();

        Assert.That(state.Map.IsVisible(8, 7), Is.True, "Stair must be visible for this test");

        AutoExploreSystem.Activate(state);

        // First activation: stair is visible but NOT in KnownStairs at activation time.
        // GetNextAction should detect the stair and stop.
        var action1 = AutoExploreSystem.GetNextAction(state);
        Assert.That(action1, Is.Null, "Should stop on first visible stair");
        var ae = state.Player.Get<AutoExploreState>()!;
        Assert.That(ae.StopReason, Does.Contain("Stairs").IgnoreCase);

        // Re-activate — simulate user pressing Explore again after seeing stair notification.
        // The stair is now in KnownStairs because CheckInterrupts adds it when explored.
        // Actually we need to add it manually since CheckInterrupts only adds when explored.
        // Mark it explored first (player walked nearby), then add to KnownStairs.
        ae.KnownStairs.Add((8, 7));
        AutoExploreSystem.Activate(state);

        // After re-activation with stair pre-known, stair interrupt should not fire immediately
        // (the stair is in KnownStairs at activation, so it won't be added again via the interrupt check).
        // The first action should not stop for stairs.
        // Note: Activate doesn't populate KnownStairs from the current state — that's by design.
        // The test verifies that manually pre-populating KnownStairs suppresses the stair interrupt.
        // We need to re-add it to the fresh ae after Activate (Activate calls GetOrAdd which may reuse it).
        ae = state.Player.Get<AutoExploreState>()!;
        ae.KnownStairs.Add((8, 7));

        var action2 = AutoExploreSystem.GetNextAction(state);
        // Should NOT stop for stairs this time (stair is known)
        // It may still stop for other reasons (exploration complete, etc.) but not stairs
        if (action2 == null)
        {
            Assert.That(ae.StopReason, Does.Not.Contain("Stairs").IgnoreCase,
                "Should not stop for already-known stairs");
        }
    }

    // -----------------------------------------------------------------------
    // Position history buffer rollover
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_PositionHistory_CircularBuffer_RollsOver()
    {
        var ae = new AutoExploreState();

        // Fill more than 6 positions — the buffer should only keep the last 6
        for (int i = 0; i < 8; i++)
            ae.RecordPosition(i, i);

        // After 8 records, positions 0-5 should map to (2,2),(3,3),(4,4),(5,5),(6,6),(7,7)
        // IsOscillating checks specific pattern — just verify it doesn't throw and returns false
        Assert.That(ae.IsOscillating(), Is.False,
            "Monotonically increasing positions should not be detected as oscillation");
    }

    // -----------------------------------------------------------------------
    // Deactivation state consistency
    // -----------------------------------------------------------------------

    [Test]
    public void AutoExplore_AfterStop_IsActiveIsFalse()
    {
        var state = MakeDungeonState();

        AutoExploreSystem.Activate(state);
        // Force stop by taking damage
        state.PlayerFighter.Hp -= 5;
        AutoExploreSystem.GetNextAction(state);

        var ae = state.Player.Get<AutoExploreState>()!;
        Assert.That(ae.IsActive, Is.False);
        Assert.That(ae.CurrentPath, Is.Empty, "Path should be cleared on stop");
    }

    [Test]
    public void AutoExplore_GetNextAction_WhenNotActive_ReturnsNull()
    {
        var state = MakeDungeonState();

        // Don't call Activate — AutoExploreState has IsActive=false by default
        state.Player.GetOrAdd<AutoExploreState>(); // ensure component exists but inactive

        var action = AutoExploreSystem.GetNextAction(state);
        Assert.That(action, Is.Null);
    }

    [Test]
    public void AutoExplore_GetNextAction_WhenNoComponent_ReturnsNull()
    {
        var state = MakeDungeonState();
        // Don't activate — no component added at all

        var action = AutoExploreSystem.GetNextAction(state);
        Assert.That(action, Is.Null);
    }
}
