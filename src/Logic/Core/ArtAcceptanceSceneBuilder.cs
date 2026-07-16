using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Builds the fixed, authored art-acceptance-test scene (docs/art_test_scene_spec_v2.md §3).
///
/// This is authored floor data, not procedural generation. It exists specifically because
/// ScenarioDefinition (config/levels/*.yaml) has no vocabulary for room geometry or static
/// props, and RoomPropPlacer's archetype-recipe placement has no mechanism to pin exact
/// tile IDs or guarantee specific asset co-presence — the two things this scene needs.
///
/// Fidelity constraint: this builder produces ONLY data — a GameState with a populated
/// GameMap, Props, Features, FloorItems, Monsters, and Player. It contains no rendering
/// code. The caller (see Main.LaunchArtAcceptanceScene) feeds the result through the exact
/// same DungeonRenderer.Render(...) call used for procedurally generated floors — same
/// method, same overload, same wall-autotile and FloorComposer logic. See that call site
/// for the seam evidence. This builder deliberately lives in the Logic layer (no Godot
/// dependency) so its content can be asserted and diffed in the fast headless test suite —
/// see tests/Core/ArtAcceptanceSceneBuilderTests.cs.
///
/// Determinism: per docs/art_test_scene_spec_v2.md §4 ("No seeds, no rolls, no variant
/// selection... identical composition every launch, by construction"), this builder uses
/// no RNG anywhere — every position and tile ID is a fixed literal, and monster creation
/// is called with rng=null, which deterministically skips equipment-roll randomness
/// (MonsterFactory.CreateFromDefinition only spawns equipment when rng is non-null).
/// Two calls produce byte-identical GameMap/Props/Features/FloorItems/Monster data
/// (verified by ArtAcceptanceSceneBuilderTests.Build_IsDeterministic_AcrossTwoColdRuns).
/// </summary>
public static class ArtAcceptanceSceneBuilder
{
    // Interior room is 14 wide x 18 tall (x: 1..14, y: 1..18), with a 1-tile wall border
    // and a 1-tile door + corridor stub on the south wall. Total map: 16 x 21.
    private const int MapWidth = 16;
    private const int MapHeight = 21;
    private const int RoomX0 = 1, RoomY0 = 1, RoomX1 = 14, RoomY1 = 18;
    private const int DoorX = 8, DoorY = 19;
    private const int CorridorStubX = 8, CorridorStubY = 20;

    public static GameState Build(
        MonsterFactory monsterFactory,
        ItemFactory itemFactory,
        ConsumableFactory consumableFactory)
    {
        var map = BuildMap();

        var player = CreatePlayer();
        player.X = 7;
        player.Y = 17;
        map.RegisterEntity(player);

        var monsters = new List<Entity>();
        AddMonster(monsters, map, monsterFactory, "orc_grunt", x: 3, y: 3);  // adjacent to anvil (2,3)
        AddMonster(monsters, map, monsterFactory, "troll", x: 7, y: 9);       // adjacent to table (7,8)

        var props = BuildProps();
        foreach (var prop in props)
            if (prop.BlocksMovement)
                map.MarkPropCell(prop.X, prop.Y);

        // Features (chest/sign/mural) and the key item share one EntityIdAllocator, started
        // after the shared EntityFactory's counter — same pattern as DungeonFloorBuilder
        // (see DungeonFloorBuilder.cs: `new EntityIdAllocator(startFrom: _monsterFactory.EntityFactory.NextId)`)
        // so ids never collide with monster/item entities created above.
        var ids = new EntityIdAllocator(startFrom: monsterFactory.EntityFactory.NextId);

        var features = BuildFeatures(ids);
        foreach (var feature in features)
            map.RegisterEntity(feature);

        var floorItems = BuildFloorItems(ids, itemFactory, consumableFactory);
        foreach (var item in floorItems)
            map.RegisterEntity(item);

        map.RevealAll(); // Static scene — everything visible from the first frame, no fog.

        // GameState.Rng is a required constructor parameter but is never drawn from here —
        // this scene runs no turns and rolls nothing (spec §4: "no seeds, no rolls"). The
        // fixed 0 is an inert placeholder, not a seed choice.
        var state = new GameState(player, monsters, map, new SeededRandom(0), turnLimit: 1)
        {
            IsDungeonMode = true,
            CurrentDepth = 1,
            Props = props,
        };
        foreach (var item in floorItems)
            state.FloorItems.Add(item);
        foreach (var feature in features)
            state.Features.Add(feature);

        return state;
    }

    private static GameMap BuildMap()
    {
        var map = new GameMap(MapWidth, MapHeight, allWalls: true);

        for (int x = RoomX0; x <= RoomX1; x++)
            for (int y = RoomY0; y <= RoomY1; y++)
                map.SetTile(x, y, TileKind.Floor);

        map.SetTile(DoorX, DoorY, TileKind.Door);
        map.SetTile(CorridorStubX, CorridorStubY, TileKind.Floor);

        // TileTheme.Grey resolves to the "sandstone" config key (the only theme currently
        // defined — see DungeonRenderer.ThemeToConfigName). Default-initialized to Grey
        // already; set explicitly for readability.
        map.SetTileThemeRect(0, 0, MapWidth - 1, MapHeight - 1, TileTheme.Grey);

        return map;
    }

    private static Entity CreatePlayer()
    {
        // Default scenario-player stats (matches ScenarioPlayer defaults in ScenarioDefinition.cs).
        // Equipment/inventory are intentionally empty — spec §3 does not require specific
        // player gear, only "standard gameplay HUD visible".
        var player = new Entity(0, "Player", 0, 0, blocksMovement: true);
        player.Add(new Fighter(
            hp: 54, strength: 12, dexterity: 14, constitution: 12,
            accuracy: 2, evasion: 1, damageMin: 1, damageMax: 4));
        player.Add(new SpeedBonusTracker(baseRatio: 0.25));
        return player;
    }

    private static void AddMonster(
        List<Entity> monsters, GameMap map, MonsterFactory monsterFactory,
        string monsterId, int x, int y)
    {
        // rng: null deterministically skips equipment-roll randomness (see class docstring) —
        // not an oversight, the mechanism spec §4 relies on for "no rolls".
        var monster = monsterFactory.Create(monsterId, x, y, depth: 1, rng: null);
        if (monster == null)
            throw new InvalidOperationException(
                $"ArtAcceptanceSceneBuilder: monster '{monsterId}' not found in content — " +
                "spec §3 requires it. Check config/entities.yaml.");
        monsters.Add(monster);
        map.RegisterEntity(monster);
    }

    /// <summary>
    /// Room props (furniture placed via PlacedProp — the same record RoomPropPlacer emits).
    /// Tile IDs are pinned explicitly per spec §3; props.yaml's variant lists are irrelevant
    /// here (authored data, not a procedural roll).
    /// </summary>
    private static List<PlacedProp> BuildProps()
    {
        return new List<PlacedProp>
        {
            // Smithy cluster (wall_adjacent forge + tool_rack, free_standing anvil) — §3 "wall_adjacent".
            new("forge",      X: 2, Y: 1, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5011),
            new("tool_rack",  X: 4, Y: 1, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5089),
            new("anvil",      X: 2, Y: 3, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5001),

            // Free-standing candelabra — §3 "free_standing".
            new("candelabra", X: 8, Y: 1, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5080),

            // Center table + chairs — §3 "center".
            new("table",      X: 7, Y: 8, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5052),
            new("chair",      X: 6, Y: 8, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5051),
            new("chair",      X: 8, Y: 8, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5056),
            new("chair",      X: 7, Y: 7, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5057),

            // Floor overlays — §3 "floor_overlay". Non-blocking.
            new("rubble",     X: 3, Y: 10, FootprintW: 1, FootprintH: 1, BlocksMovement: false, TileId: 5078),
            new("rubble",     X: 4, Y: 11, FootprintW: 1, FootprintH: 1, BlocksMovement: false, TileId: 5079),
            new("puddle",     X: 10, Y: 11, FootprintW: 1, FootprintH: 1, BlocksMovement: false, TileId: 5110),

            // Canon barrel (268) beside generated sack (5102) — §3 nearest-equivalent pairing.
            new("barrel",     X: 2, Y: 16, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 268),
            new("sack",       X: 3, Y: 16, FootprintW: 1, FootprintH: 1, BlocksMovement: true,  TileId: 5102),
        };
    }

    /// <summary>
    /// Interactive features (chests, sign, mural) — rendered by DungeonRenderer Pass 5 via
    /// ChestComponent/SignpostComponent/MuralComponent, resolved through TileThemeConfig
    /// (chest/sign) or MuralComponent.TileId (mural) exactly as generated floors are.
    /// </summary>
    private static List<Entity> BuildFeatures(EntityIdAllocator ids)
    {
        var chestClosed = FeatureFactory.CreateChest(11, 13, ids);

        var chestOpen = FeatureFactory.CreateChest(13, 13, ids);
        chestOpen.Get<ChestComponent>()!.IsOpen = true;

        var sign = FeatureFactory.CreateSignpost(
            14, 4, ids,
            message: "The forge has gone cold, but the anvil remembers every strike.",
            signType: "lore");

        // tileId 5075 pinned explicitly — spec §3: "the worst A4 offender" (mural_gold_landscape).
        var mural = FeatureFactory.CreateMural(
            12, 1, ids,
            text: "A gilded landscape, its gold leaf flaking at the edges.",
            muralId: "art_scene_mural_gold_landscape",
            tileId: 5075);

        return new List<Entity> { chestClosed, chestOpen, sign, mural };
    }

    /// <summary>
    /// Floor items: the key (5039, via the same world_24x24 direct-render path
    /// ItemSpriteManager uses for KeyItemComponent) plus 2-3 canon items within two tiles
    /// of it, forcing a direct canon-vs-generated item comparison per spec §3.
    /// </summary>
    private static List<Entity> BuildFloorItems(
        EntityIdAllocator ids, ItemFactory itemFactory, ConsumableFactory consumableFactory)
    {
        var key = FeatureFactory.CreateKeyItem(12, 15, ids, lockColorId: 0);

        var items = new List<Entity> { key };

        var potion = consumableFactory.Create("healing_potion");
        if (potion == null)
            throw new InvalidOperationException(
                "ArtAcceptanceSceneBuilder: consumable 'healing_potion' not found — check config/entities.yaml.");
        potion.X = 11; potion.Y = 15;
        items.Add(potion);

        var dagger = itemFactory.Create("dagger");
        if (dagger == null)
            throw new InvalidOperationException(
                "ArtAcceptanceSceneBuilder: item 'dagger' not found — check config/entities.yaml.");
        dagger.X = 13; dagger.Y = 15;
        items.Add(dagger);

        var club = itemFactory.Create("club");
        if (club == null)
            throw new InvalidOperationException(
                "ArtAcceptanceSceneBuilder: item 'club' not found — check config/entities.yaml.");
        club.X = 12; club.Y = 16;
        items.Add(club);

        return items;
    }
}
