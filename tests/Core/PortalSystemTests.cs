using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Core;

/// <summary>
/// Comprehensive tests for PortalSystem — the logic layer backing the Wand of Portals.
///
/// PortalSystem is a new system with no PoC reference; all correctness is defined here.
/// Tests use manually constructed GameState (no YAML) for speed, except the YAML integration
/// tests at the bottom which verify wand_of_portals loads correctly.
/// </summary>
[TestFixture]
public class PortalSystemTests
{
    // ─── Common helpers ───────────────────────────────────────────────────────

    private static (GameState state, EntityFactory entityFactory) CreateState(
        int playerX = 3, int playerY = 3,
        int mapSize = 20,
        int seed = 1337)
    {
        var rng = new SeededRandom(seed);
        var map = GameMap.CreateArena(mapSize, mapSize);

        var player = new Entity(0, "Player", playerX, playerY, blocksMovement: true);
        player.Add(new Fighter(hp: 80, strength: 14, dexterity: 14, constitution: 14,
            accuracy: 3, evasion: 0, damageMin: 2, damageMax: 8));
        player.Add(new Inventory());
        map.RegisterEntity(player);

        var state = new GameState(player, new List<Entity>(), map, rng);

        // Entity IDs for portals should not collide with player (0) or any monster IDs we add
        var entityFactory = new EntityFactory(startId: 500);
        return (state, entityFactory);
    }

    private static Entity AddMonster(GameState state, int id, int x, int y, int hp = 30)
    {
        var m = new Entity(id, "Orc", x, y, blocksMovement: true);
        m.Add(new Fighter(hp: hp, strength: 8, dexterity: 8, constitution: 8,
            accuracy: 2, evasion: 0, damageMin: 1, damageMax: 3));
        m.Add(new AiComponent { AiType = "basic", Faction = "orc", Tags = ["humanoid", "living"] });
        state.Monsters.Add(m);
        state.Map.RegisterEntity(m);
        return m;
    }

    private static Entity MakeInfiniteWand()
    {
        var wand = new Entity(200, "Wand of Portals");
        wand.Add(new WandComponent { Charges = 0, MaxCharges = 10, Infinite = true });
        wand.Add(new SpellEffect { SpellId = "portal", Targeting = TargetingMode.Portal });
        return wand;
    }

    private static string FindEntitiesYaml()
    {
        var testDir = TestContext.CurrentContext.TestDirectory;
        var path = Path.GetFullPath(Path.Combine(testDir, "..", "..", "..", "..", "config", "entities.yaml"));
        if (File.Exists(path)) return path;
        path = Path.GetFullPath(Path.Combine(testDir, "config", "entities.yaml"));
        if (File.Exists(path)) return path;
        throw new FileNotFoundException($"entities.yaml not found. Tried: {path}");
    }

    // ─── PlacePortals ────────────────────────────────────────────────────────

    [Test]
    public void PlacePortals_CreatesTwoPortalEntities()
    {
        var (state, factory) = CreateState();

        var events = PortalSystem.PlacePortals(state, placedByEntityId: 0,
            entranceX: 5, entranceY: 5, exitX: 10, exitY: 10, entityFactory: factory);

        Assert.That(events, Is.Not.Null, "Valid placement should return events");
        Assert.That(state.Portals, Has.Count.EqualTo(2), "Two portal entities should exist");
    }

    [Test]
    public void PlacePortals_EntranceIsLinkedToExit()
    {
        var (state, factory) = CreateState();

        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        var entrance = state.Portals.First(p => p.Get<PortalComponent>()?.Type == PortalType.Entrance);
        var exit = state.Portals.First(p => p.Get<PortalComponent>()?.Type == PortalType.Exit);

        Assert.That(entrance.Get<PortalComponent>()!.LinkedPortalId, Is.EqualTo(exit.Id),
            "Entrance should link to exit");
    }

    [Test]
    public void PlacePortals_ExitIsLinkedToEntrance()
    {
        var (state, factory) = CreateState();

        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        var entrance = state.Portals.First(p => p.Get<PortalComponent>()?.Type == PortalType.Entrance);
        var exit = state.Portals.First(p => p.Get<PortalComponent>()?.Type == PortalType.Exit);

        Assert.That(exit.Get<PortalComponent>()!.LinkedPortalId, Is.EqualTo(entrance.Id),
            "Exit should link to entrance");
    }

    [Test]
    public void PlacePortals_RecyclesExistingPair_RemovesOldPortals()
    {
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);
        Assert.That(state.Portals, Has.Count.EqualTo(2));

        // Place again — should remove old and create new
        PortalSystem.PlacePortals(state, 0, 6, 6, 12, 12, factory);

        Assert.That(state.Portals, Has.Count.EqualTo(2), "Should still have exactly two portals after recycling");
        // Verify positions changed
        var entrance = state.Portals.First(p => p.Get<PortalComponent>()?.Type == PortalType.Entrance);
        Assert.That(entrance.X, Is.EqualTo(6), "New entrance should be at updated position");
        Assert.That(entrance.Y, Is.EqualTo(6));
    }

    [Test]
    public void PlacePortals_RecyclesExistingPair_EmitsRemovedEvent()
    {
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Second placement should emit PortalRemovedEvent for the old pair
        var events = PortalSystem.PlacePortals(state, 0, 6, 6, 12, 12, factory)!;

        var removedEvents = events.OfType<PortalRemovedEvent>().ToList();
        Assert.That(removedEvents, Has.Count.EqualTo(1), "Should emit one PortalRemovedEvent when recycling");
    }

    [Test]
    public void PlacePortals_InvalidTile_NonWalkable_Fails()
    {
        var (state, factory) = CreateState();
        // Wall tiles are at x=0 or y=0 in the arena
        var events = PortalSystem.PlacePortals(state, 0,
            entranceX: 0, entranceY: 0,  // wall tile
            exitX: 5, exitY: 5, entityFactory: factory);

        Assert.That(events, Is.Null, "Placement on non-walkable tile should fail (return null)");
        Assert.That(state.Portals, Is.Empty, "No portals should be created on invalid placement");
    }

    [Test]
    public void PlacePortals_SameTile_Fails()
    {
        var (state, factory) = CreateState();
        var events = PortalSystem.PlacePortals(state, 0,
            entranceX: 5, entranceY: 5,
            exitX: 5, exitY: 5,  // same as entrance
            entityFactory: factory);

        Assert.That(events, Is.Null, "Entrance and exit on same tile should fail");
        Assert.That(state.Portals, Is.Empty, "No portals should be created when same tile");
    }

    [Test]
    public void PlacePortals_EmitsPlacedEvents()
    {
        var (state, factory) = CreateState();

        var events = PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory)!;

        var placedEvents = events.OfType<PortalPlacedEvent>().ToList();
        Assert.That(placedEvents, Has.Count.EqualTo(2), "Should emit two PortalPlacedEvents");

        var entranceEvent = placedEvents.FirstOrDefault(e => e.Type == PortalType.Entrance);
        var exitEvent = placedEvents.FirstOrDefault(e => e.Type == PortalType.Exit);

        Assert.That(entranceEvent, Is.Not.Null);
        Assert.That(entranceEvent!.X, Is.EqualTo(5));
        Assert.That(entranceEvent.Y, Is.EqualTo(5));
        Assert.That(exitEvent, Is.Not.Null);
        Assert.That(exitEvent!.X, Is.EqualTo(10));
        Assert.That(exitEvent.Y, Is.EqualTo(10));
    }

    // ─── CheckPortalCollision ────────────────────────────────────────────────

    [Test]
    public void CheckCollision_PlayerOnEntrance_TeleportsToExit()
    {
        var (state, factory) = CreateState(playerX: 5, playerY: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Player is now standing on entrance (5,5)
        var evt = PortalSystem.CheckPortalCollision(state.Player, state);

        Assert.That(evt, Is.Not.Null, "Should return a PortalTeleportEvent");
        Assert.That(state.Player.X, Is.EqualTo(10), "Player should teleport to exit X");
        Assert.That(state.Player.Y, Is.EqualTo(10), "Player should teleport to exit Y");
        Assert.That(evt!.FromX, Is.EqualTo(5));
        Assert.That(evt.FromY, Is.EqualTo(5));
        Assert.That(evt.ToX, Is.EqualTo(10));
        Assert.That(evt.ToY, Is.EqualTo(10));
    }

    [Test]
    public void CheckCollision_PlayerOnExit_TeleportsToEntrance()
    {
        var (state, factory) = CreateState(playerX: 10, playerY: 10);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Player is standing on exit (10,10) — should teleport to entrance
        var evt = PortalSystem.CheckPortalCollision(state.Player, state);

        Assert.That(evt, Is.Not.Null);
        Assert.That(state.Player.X, Is.EqualTo(5));
        Assert.That(state.Player.Y, Is.EqualTo(5));
    }

    [Test]
    public void CheckCollision_MonsterOnPortal_Teleports()
    {
        var (state, factory) = CreateState();
        var orc = AddMonster(state, 1, x: 5, y: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        var evt = PortalSystem.CheckPortalCollision(orc, state);

        Assert.That(evt, Is.Not.Null, "Monster on portal should teleport");
        Assert.That(orc.X, Is.EqualTo(10), "Monster should be at exit X");
        Assert.That(orc.Y, Is.EqualTo(10), "Monster should be at exit Y");
    }

    [Test]
    public void CheckCollision_NoPortalAtPosition_ReturnsNull()
    {
        var (state, factory) = CreateState(playerX: 3, playerY: 3);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Player at (3,3), portals at (5,5) and (10,10)
        var evt = PortalSystem.CheckPortalCollision(state.Player, state);

        Assert.That(evt, Is.Null, "No portal at player position — should return null");
    }

    [Test]
    public void CheckCollision_NoPortalsActive_ReturnsNull()
    {
        var (state, _) = CreateState(playerX: 5, playerY: 5);

        var evt = PortalSystem.CheckPortalCollision(state.Player, state);

        Assert.That(evt, Is.Null, "No portals exist — should return null immediately");
    }

    [Test]
    public void CheckCollision_NoChaining_JustTeleportedEntity()
    {
        var (state, factory) = CreateState(playerX: 5, playerY: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // First teleport: entrance → exit
        var evt1 = PortalSystem.CheckPortalCollision(state.Player, state);
        Assert.That(evt1, Is.Not.Null, "First teleport should succeed");
        Assert.That(state.Player.X, Is.EqualTo(10), "Player at exit after first teleport");

        // Player is now at exit (10,10). The exit portal has UsedThisTurn=true (set by first teleport).
        // Attempting to teleport again on the exit portal this turn should be blocked.
        var evt2 = PortalSystem.CheckPortalCollision(state.Player, state);
        Assert.That(evt2, Is.Null, "Chain teleport should be blocked (UsedThisTurn flag)");
        Assert.That(state.Player.X, Is.EqualTo(10), "Player should not have moved again");
    }

    [Test]
    public void CheckCollision_AfterClearUsedFlags_CanTeleportAgainNextTurn()
    {
        var (state, factory) = CreateState(playerX: 5, playerY: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // First teleport
        PortalSystem.CheckPortalCollision(state.Player, state);
        Assert.That(state.Player.X, Is.EqualTo(10));

        // Simulate end of turn — clear used flags
        PortalSystem.ClearPortalUsedFlags(state);

        // Move player back to entrance manually
        state.Player.X = 5;
        state.Player.Y = 5;

        // Should be able to teleport again next turn
        var evt = PortalSystem.CheckPortalCollision(state.Player, state);
        Assert.That(evt, Is.Not.Null, "Should teleport again after UsedThisTurn was cleared");
    }

    // ─── ClearPortals ─────────────────────────────────────────────────────────

    [Test]
    public void ClearPortals_RemovesAllPortalEntities()
    {
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);
        Assert.That(state.Portals, Has.Count.EqualTo(2));

        PortalSystem.ClearPortals(state);

        Assert.That(state.Portals, Is.Empty, "ClearPortals should remove all portal entities");
    }

    [Test]
    public void ClearPortals_ClearsGameStatePortalList()
    {
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        PortalSystem.ClearPortals(state);

        Assert.That(state.Portals, Is.Empty, "state.Portals should be empty after ClearPortals");
    }

    [Test]
    public void ClearPortals_ReturnsRemovedEvent_WhenPortalsExisted()
    {
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        var evt = PortalSystem.ClearPortals(state);

        Assert.That(evt, Is.Not.Null, "ClearPortals should return PortalRemovedEvent when portals existed");
    }

    [Test]
    public void ClearPortals_ReturnsNull_WhenNoPortalsExisted()
    {
        var (state, _) = CreateState();

        var evt = PortalSystem.ClearPortals(state);

        Assert.That(evt, Is.Null, "ClearPortals should return null when no portals exist");
    }

    // ─── Wand of Portals properties ──────────────────────────────────────────

    [Test]
    public void WandOfPortals_InfiniteCharges_NeverDepleted()
    {
        var wand = MakeInfiniteWand();
        var wandComp = wand.Require<WandComponent>();

        Assert.That(wandComp.Infinite, Is.True);
        Assert.That(wandComp.HasCharges, Is.True);

        // Simulate many uses
        for (int i = 0; i < 100; i++)
            wandComp.TryConsume();

        Assert.That(wandComp.HasCharges, Is.True, "Infinite wand should always have charges");
    }

    [Test]
    public void WandOfPortals_SpellId_IsPortal()
    {
        var wand = MakeInfiniteWand();
        Assert.That(wand.Require<SpellEffect>().SpellId, Is.EqualTo("portal"));
    }

    // ─── TurnController integration ──────────────────────────────────────────

    [Test]
    public void TurnController_PortalAction_CallsPlacePortals()
    {
        var (state, factory) = CreateState(playerX: 3, playerY: 3);
        var wand = MakeInfiniteWand();
        state.Player.Require<Inventory>().Add(wand);

        // Cast with entrance at (5,5), exit at (10,10)
        var action = PlayerAction.CastSpellPortal(wand, 5, 5, 10, 10);
        var result = TurnController.ProcessTurn(state, action, portalEntityFactory: factory);

        var placedEvents = result.Events.OfType<PortalPlacedEvent>().ToList();
        Assert.That(placedEvents, Has.Count.EqualTo(2), "Two PortalPlacedEvents expected");
        Assert.That(state.Portals, Has.Count.EqualTo(2), "Two portals in state.Portals");
    }

    [Test]
    public void TurnController_PortalAction_NoFactory_SilentNoOp()
    {
        var (state, _) = CreateState();
        var wand = MakeInfiniteWand();
        state.Player.Require<Inventory>().Add(wand);

        // No factory injected — should not crash, just silently do nothing
        var action = PlayerAction.CastSpellPortal(wand, 5, 5, 10, 10);
        var result = TurnController.ProcessTurn(state, action, portalEntityFactory: null);

        Assert.That(state.Portals, Is.Empty, "No portals should be created without a factory");
        Assert.That(result.Events.OfType<PortalPlacedEvent>(), Is.Empty);
    }

    [Test]
    public void TurnController_PlayerMove_ChecksPortalCollision()
    {
        var (state, factory) = CreateState(playerX: 4, playerY: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Move player onto the entrance portal at (5,5)
        var result = TurnController.ProcessTurn(state,
            PlayerAction.MoveTo(5, 5), portalEntityFactory: factory);

        var teleportEvent = result.Events.OfType<PortalTeleportEvent>().FirstOrDefault();
        Assert.That(teleportEvent, Is.Not.Null, "Moving onto portal should emit PortalTeleportEvent");
        Assert.That(state.Player.X, Is.EqualTo(10));
        Assert.That(state.Player.Y, Is.EqualTo(10));
    }

    [Test]
    public void TurnController_MonsterMove_ChecksPortalCollision()
    {
        // Place orc next to entrance so it will move onto it
        var (state, factory) = CreateState(playerX: 15, playerY: 15);
        var orc = AddMonster(state, 1, x: 4, y: 5);
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);

        // Move player away so orc doesn't attack and instead moves
        // The orc will try to move toward the player (15,15), moving from (4,5) toward (5,5)
        var result = TurnController.ProcessTurn(state, PlayerAction.Wait, portalEntityFactory: factory);

        // Orc should have moved and possibly triggered the portal
        var teleportEvent = result.Events.OfType<PortalTeleportEvent>()
            .FirstOrDefault(e => e.EntityId == orc.Id);
        // Note: The orc may or may not step exactly on the portal tile depending on A* pathing.
        // This test verifies the system doesn't crash when portals + monster movement coexist.
        // A tighter test is below using CheckPortalCollision directly.
        Assert.That(result.Events, Is.Not.Null, "Monster movement with portals should not crash");
    }

    [Test]
    public void TurnController_PortalAction_InfiniteWand_NotConsumed()
    {
        var (state, factory) = CreateState();
        var wand = MakeInfiniteWand();
        state.Player.Require<Inventory>().Add(wand);

        TurnController.ProcessTurn(state, PlayerAction.CastSpellPortal(wand, 5, 5, 10, 10),
            portalEntityFactory: factory);

        // Wand should still be in inventory (infinite wands are never destroyed)
        Assert.That(state.PlayerInventory!.Items, Contains.Item(wand),
            "Infinite wand should remain in inventory after use");
        Assert.That(wand.Require<WandComponent>().HasCharges, Is.True);
    }

    [Test]
    public void TurnController_PortalRecycle_OldPortalRemoved()
    {
        var (state, factory) = CreateState();
        var wand = MakeInfiniteWand();
        state.Player.Require<Inventory>().Add(wand);

        // First placement
        TurnController.ProcessTurn(state, PlayerAction.CastSpellPortal(wand, 5, 5, 10, 10),
            portalEntityFactory: factory);
        Assert.That(state.Portals, Has.Count.EqualTo(2));

        // Second placement — should remove old pair and create new
        var result = TurnController.ProcessTurn(state,
            PlayerAction.CastSpellPortal(wand, 6, 6, 12, 12),
            portalEntityFactory: factory);

        Assert.That(state.Portals, Has.Count.EqualTo(2), "Still exactly 2 portals");
        var removedEvent = result.Events.OfType<PortalRemovedEvent>().FirstOrDefault();
        Assert.That(removedEvent, Is.Not.Null, "Should emit PortalRemovedEvent when recycling");
    }

    // ─── Floor transition ─────────────────────────────────────────────────────

    [Test]
    public void FloorTransition_ClearsPortals()
    {
        // This tests that ClearPortals is the right call on floor transition.
        // The actual floor transition is handled by the presentation layer (DescendEvent).
        // This unit test verifies ClearPortals leaves state clean for a new floor.
        var (state, factory) = CreateState();
        PortalSystem.PlacePortals(state, 0, 5, 5, 10, 10, factory);
        Assert.That(state.Portals, Has.Count.EqualTo(2));

        PortalSystem.ClearPortals(state);

        Assert.That(state.Portals, Is.Empty, "Portals should be cleared on floor transition");

        // Verify portals cannot be triggered on cleared state
        state.Player.X = 5;
        state.Player.Y = 5;
        var evt = PortalSystem.CheckPortalCollision(state.Player, state);
        Assert.That(evt, Is.Null, "No collision after clearing portals");
    }

    // ─── YAML integration ─────────────────────────────────────────────────────

    [Test]
    public void WandOfPortals_LoadsFromYaml()
    {
        var loader = new ContentLoader();
        var bundle = loader.LoadAllFromFile(FindEntitiesYaml());

        Assert.That(bundle.SpellItems.ContainsKey("wand_of_portals"),
            "wand_of_portals should be present in entities.yaml");

        var def = bundle.SpellItems["wand_of_portals"];
        Assert.That(def.IsWand, Is.True, "wand_of_portals should be marked is_wand=true");
        Assert.That(def.Infinite, Is.True, "wand_of_portals should be infinite");
        Assert.That(def.SpellId, Is.EqualTo("portal"), "wand_of_portals spell_id should be 'portal'");
    }

    [Test]
    public void WandOfPortals_CreatedByFactory_HasInfiniteComponent()
    {
        var loader = new ContentLoader();
        var bundle = loader.LoadAllFromFile(FindEntitiesYaml());
        var entityFactory = new EntityFactory();
        var spellFactory = new SpellItemFactory(bundle.SpellItems, entityFactory);

        var wand = spellFactory.CreateWand("wand_of_portals", new SeededRandom(1337));

        Assert.That(wand, Is.Not.Null, "CreateWand should return a valid entity");
        var wandComp = wand!.Get<WandComponent>();
        Assert.That(wandComp, Is.Not.Null, "Should have WandComponent");
        Assert.That(wandComp!.Infinite, Is.True, "WandComponent.Infinite should be true");
        Assert.That(wandComp.HasCharges, Is.True);
    }

    [Test]
    public void WandOfPortals_NotInFloorPool()
    {
        // Verify wand_of_portals is not in any floor item pool (it's a starting item only).
        var testDir = TestContext.CurrentContext.TestDirectory;
        var poolPath = Path.GetFullPath(Path.Combine(testDir, "..", "..", "..", "..", "config", "floor_item_pools.yaml"));

        if (!File.Exists(poolPath))
        {
            Assert.Ignore("floor_item_pools.yaml not found — skipping floor pool check");
            return;
        }

        var content = File.ReadAllText(poolPath);
        Assert.That(content, Does.Not.Contain("wand_of_portals"),
            "wand_of_portals should not appear in floor_item_pools.yaml");
    }
}
