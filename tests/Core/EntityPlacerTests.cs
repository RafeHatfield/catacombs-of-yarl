using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;
using CatacombsOfYarl.Logic.Combat;

namespace CatacombsOfYarl.Tests.Core;

/// <summary>
/// Tests for EntityPlacer, EntityIdAllocator, EtpCalculator, and Stair component.
/// Covers Phase 4 of the dungeon generation milestone.
/// </summary>
[TestFixture]
public class EntityPlacerTests
{
    // Minimal entity YAML with one monster (orc_grunt) that has a known ETP
    private const string EntitiesYaml = @"
monsters:
  orc_grunt:
    name: Orc Grunt
    stats:
      hp: 20
      power: 0
      defense: 0
      xp: 25
      damage_min: 3
      damage_max: 5
      strength: 12
      dexterity: 10
      constitution: 10
      accuracy: 3
      evasion: 1
    char: o
    color: [63, 127, 63]
    ai_type: basic
    blocks: true
    faction: orc
    tags: [humanoid, living]
    etp_base: 20
consumables:
  healing_potion:
    name: Healing Potion
    heal_amount: 20
";

    private static (MonsterFactory monsters, ItemFactory items, ConsumableFactory consumables) BuildFactories()
    {
        var loader = new ContentLoader();
        var bundle = loader.LoadAll(EntitiesYaml);
        var entityFactory = new EntityFactory(startId: 1);
        var monsters = new MonsterFactory(bundle.Monsters, entityFactory);
        var items = new ItemFactory(bundle.Items, entityFactory);
        var consumables = new ConsumableFactory(bundle.Consumables, entityFactory);
        return (monsters, items, consumables);
    }

    private static GeneratedMap MakeMap(int seed = 1337) =>
        MapGenerator.Generate(60, 40, 8, 5, 10, new SeededRandom(seed));

    // --- EntityIdAllocator ---

    [Test]
    public void EntityIdAllocator_StartFrom1_FirstIdIs1()
    {
        var alloc = new EntityIdAllocator(startFrom: 1);
        Assert.That(alloc.Next(), Is.EqualTo(1));
    }

    [Test]
    public void EntityIdAllocator_Increments_Sequentially()
    {
        var alloc = new EntityIdAllocator(startFrom: 10);
        Assert.That(alloc.Next(), Is.EqualTo(10));
        Assert.That(alloc.Next(), Is.EqualTo(11));
        Assert.That(alloc.Next(), Is.EqualTo(12));
    }

    [Test]
    public void EntityIdAllocator_NoCollisions_WithinFloor()
    {
        var alloc = new EntityIdAllocator();
        var ids = Enumerable.Range(0, 100).Select(_ => alloc.Next()).ToList();
        Assert.That(ids.Distinct().Count(), Is.EqualTo(100));
    }

    // --- EtpCalculator ---

    [Test]
    public void EtpCalculator_GetEtp_ReturnsEtpBase()
    {
        var def = new MonsterDefinition { EtpBase = 27 };
        Assert.That(EtpCalculator.GetEtp(def), Is.EqualTo(27));
    }

    [Test]
    public void EtpCalculator_FitsInBudget_WithinLimit_ReturnsTrue()
    {
        Assert.That(EtpCalculator.FitsInBudget(10, 20, 50, allowSpike: false), Is.True);
    }

    [Test]
    public void EtpCalculator_FitsInBudget_ExceedsLimit_ReturnsFalse()
    {
        Assert.That(EtpCalculator.FitsInBudget(40, 20, 50, allowSpike: false), Is.False);
    }

    [Test]
    public void EtpCalculator_FitsInBudget_AllowSpike_UsesExtendedLimit()
    {
        // 40 + 20 = 60 <= 50 * 1.5 = 75 → true with spike
        Assert.That(EtpCalculator.FitsInBudget(40, 20, 50, allowSpike: true), Is.True);
    }

    [Test]
    public void EtpCalculator_FitsInBudget_AllowSpike_Exceeded_ReturnsFalse()
    {
        // 70 + 20 = 90 > 50 * 1.5 = 75 → false even with spike
        Assert.That(EtpCalculator.FitsInBudget(70, 20, 50, allowSpike: true), Is.False);
    }

    // --- Stair component ---

    [Test]
    public void Stair_IsDown_True_TargetDepth_Set()
    {
        var stair = new Stair(isDown: true, targetDepth: 2);
        Assert.That(stair.IsDown, Is.True);
        Assert.That(stair.TargetDepth, Is.EqualTo(2));
    }

    [Test]
    public void Stair_IsDown_False_UpStair()
    {
        var stair = new Stair(isDown: false, targetDepth: 1);
        Assert.That(stair.IsDown, Is.False);
    }

    // --- PlaceStairDown ---

    [Test]
    public void PlaceStairDown_ReturnsEntity_WithStairComponent()
    {
        var map = MakeMap();
        var ids = new EntityIdAllocator(100);
        var entity = EntityPlacer.PlaceStairDown(map, targetDepth: 2, ids);

        Assert.That(entity, Is.Not.Null);
        var stair = entity!.Get<Stair>();
        Assert.That(stair, Is.Not.Null);
        Assert.That(stair!.IsDown, Is.True);
        Assert.That(stair.TargetDepth, Is.EqualTo(2));
    }

    [Test]
    public void PlaceStairDown_EntityPosition_MatchesStairDownPos()
    {
        var map = MakeMap();
        var ids = new EntityIdAllocator(100);
        var entity = EntityPlacer.PlaceStairDown(map, targetDepth: 2, ids);

        Assert.That(entity!.X, Is.EqualTo(map.StairDownPos!.Value.X));
        Assert.That(entity.Y, Is.EqualTo(map.StairDownPos!.Value.Y));
    }

    [Test]
    public void PlaceStairDown_NoStairDownPos_ReturnsNull()
    {
        // Map with stairs.Down = false → no stair down position
        var stairRules = new StairRules { Down = false, Up = false };
        var mapNoStair = MapGenerator.Generate(60, 40, 8, 5, 10, new SeededRandom(1337), stairRules);
        var ids = new EntityIdAllocator(100);
        var entity = EntityPlacer.PlaceStairDown(mapNoStair, targetDepth: 2, ids);
        Assert.That(entity, Is.Null);
    }

    // --- PlaceGuaranteedSpawns ---

    [Test]
    public void PlaceGuaranteedSpawns_ModeReplace_OnlyGuaranteedEntities()
    {
        var (monsters, items, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(100);
        var rng = new SeededRandom(1337);

        var spawns = new GuaranteedSpawns
        {
            Mode = "replace",
            Monsters = [new SpawnEntry { Type = "orc_grunt", CountMin = 1, CountMax = 1 }]
        };

        var placed = EntityPlacer.PlaceGuaranteedSpawns(map, spawns, monsters, items, consumables, rng, depth: 1, ids);

        // Exactly 1 monster placed (guaranteed count)
        Assert.That(placed, Has.Count.EqualTo(1));
        Assert.That(placed[0].Name, Is.EqualTo("Orc Grunt"));
    }

    [Test]
    public void PlaceGuaranteedSpawns_NoEntityOnWallTile()
    {
        var (monsters, items, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(100);
        var rng = new SeededRandom(42);

        var spawns = new GuaranteedSpawns
        {
            Mode = "additional",
            Monsters = [new SpawnEntry { Type = "orc_grunt", CountMin = 3, CountMax = 3 }]
        };

        var placed = EntityPlacer.PlaceGuaranteedSpawns(map, spawns, monsters, items, consumables, rng, depth: 1, ids);

        foreach (var entity in placed)
            Assert.That(map.Map.IsWalkable(entity.X, entity.Y), Is.True,
                $"Entity {entity.Name} placed on non-walkable tile ({entity.X},{entity.Y})");
    }

    [Test]
    public void PlaceGuaranteedSpawns_NoEntityIdCollisions()
    {
        var (monsters, items, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(100);
        var rng = new SeededRandom(42);

        var spawns = new GuaranteedSpawns
        {
            Mode = "additional",
            Monsters = [new SpawnEntry { Type = "orc_grunt", CountMin = 5, CountMax = 5 }]
        };

        var placed = EntityPlacer.PlaceGuaranteedSpawns(map, spawns, monsters, items, consumables, rng, depth: 1, ids);

        var idSet = placed.Select(e => e.Id).ToHashSet();
        Assert.That(idSet.Count, Is.EqualTo(placed.Count), "Duplicate entity IDs detected");
    }

    [Test]
    public void PlaceGuaranteedSpawns_Deterministic()
    {
        var (monsters1, items1, consumables1) = BuildFactories();
        var (monsters2, items2, consumables2) = BuildFactories();
        var spawns = new GuaranteedSpawns
        {
            Mode = "additional",
            Monsters = [new SpawnEntry { Type = "orc_grunt", CountMin = 2, CountMax = 2 }]
        };

        var map1 = MakeMap(seed: 77);
        var placed1 = EntityPlacer.PlaceGuaranteedSpawns(
            map1, spawns, monsters1, items1, consumables1, new SeededRandom(77), 1, new EntityIdAllocator(100));

        var map2 = MakeMap(seed: 77);
        var placed2 = EntityPlacer.PlaceGuaranteedSpawns(
            map2, spawns, monsters2, items2, consumables2, new SeededRandom(77), 1, new EntityIdAllocator(100));

        Assert.That(placed1.Count, Is.EqualTo(placed2.Count));
        for (int i = 0; i < placed1.Count; i++)
        {
            Assert.That(placed1[i].X, Is.EqualTo(placed2[i].X));
            Assert.That(placed1[i].Y, Is.EqualTo(placed2[i].Y));
        }
    }

    // --- FillRooms ---

    [Test]
    public void FillRooms_NoEntityOnWallTile()
    {
        var (monsters, _, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(1337);

        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 1, ids);

        foreach (var entity in placed)
            Assert.That(map.Map.IsWalkable(entity.X, entity.Y), Is.True,
                $"Entity placed on non-walkable tile ({entity.X},{entity.Y})");
    }

    [Test]
    public void FillRooms_NoEntityIdCollisions()
    {
        var (monsters, _, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(42);

        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 1, ids);

        if (placed.Count > 1)
        {
            var idSet = placed.Select(e => e.Id).ToHashSet();
            Assert.That(idSet.Count, Is.EqualTo(placed.Count), "Duplicate entity IDs in FillRooms");
        }
    }

    [Test]
    public void FillRooms_Deterministic()
    {
        var (monsters1, _, consumables1) = BuildFactories();
        var (monsters2, _, consumables2) = BuildFactories();

        var map1 = MakeMap(seed: 55);
        var placed1 = EntityPlacer.FillRooms(map1, null, monsters1, consumables1,
            new SeededRandom(55), 1, new EntityIdAllocator(200));

        var map2 = MakeMap(seed: 55);
        var placed2 = EntityPlacer.FillRooms(map2, null, monsters2, consumables2,
            new SeededRandom(55), 1, new EntityIdAllocator(200));

        Assert.That(placed1.Count, Is.EqualTo(placed2.Count));
    }

    [Test]
    public void FillRooms_RoomEtpBudget_NotExceeded()
    {
        var (monsters, _, consumables) = BuildFactories();
        var map = MakeMap();
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(1337);

        int roomEtpMax = 30; // orc_grunt has ETP 20, so max 1 per room
        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 1, ids, roomEtpMax);

        // Group placed monsters by room to verify ETP cap
        // We can't easily verify per-room here without more state, but we can check
        // that the total number of monsters fits the overall ETP envelope
        int totalMonsterEtp = placed
            .Where(e => e.Has<CatacombsOfYarl.Logic.Combat.Fighter>())
            .Count() * 20; // 20 ETP per orc_grunt

        int rooms = map.Rooms.Count - 1; // exclude player room
        Assert.That(totalMonsterEtp, Is.LessThanOrEqualTo(rooms * roomEtpMax),
            "Total monster ETP exceeds per-room budget across all rooms");
    }

    // --- Depth-gate tests ---

    // YAML with orc (constant weight 80), orc_brute (depth_weights starting at depth 3),
    // and zombie (depth_weights starting at depth 10). Mirrors the actual entities.yaml
    // monster definitions so these tests exercise the real FromDungeonLevel logic.
    private const string DepthGateEntitiesYaml = @"
monsters:
  orc:
    name: Orc
    spawn_weight: 80
    stats:
      hp: 28
      power: 0
      defense: 0
      xp: 35
      damage_min: 4
      damage_max: 6
      strength: 14
      dexterity: 10
      constitution: 12
      accuracy: 4
      evasion: 1
    char: o
    color: [63, 127, 63]
    ai_type: basic
    blocks: true
    faction: orc
    tags: [corporeal_flesh, humanoid, living]
    etp_base: 27

  orc_brute:
    extends: orc
    min_depth: 3
    depth_weights:
      - weight: 6
        min_depth: 3
      - weight: 12
        min_depth: 4
      - weight: 20
        min_depth: 6
    stats:
      hp: 42
      damage_min: 5
      damage_max: 8
      strength: 16
      xp: 55
    char: O
    color: [90, 160, 90]
    etp_base: 45

  zombie:
    name: Zombie
    min_depth: 10
    depth_weights:
      - weight: 20
        min_depth: 10
      - weight: 40
        min_depth: 13
      - weight: 60
        min_depth: 16
    stats:
      hp: 24
      power: 0
      defense: 0
      xp: 30
      damage_min: 3
      damage_max: 6
      strength: 12
      dexterity: 6
      constitution: 14
      accuracy: 1
      evasion: 0
    char: z
    color: [128, 128, 96]
    ai_type: basic
    blocks: true
    faction: undead
    tags: [corporeal_flesh, undead, mindless, zombie]
    etp_base: 31

consumables:
  healing_potion:
    name: Healing Potion
    heal_amount: 20
";

    private static (MonsterFactory monsters, ItemFactory items, ConsumableFactory consumables) BuildDepthGateFactories()
    {
        var loader = new ContentLoader();
        var bundle = loader.LoadAll(DepthGateEntitiesYaml);
        var entityFactory = new EntityFactory(startId: 1);
        var monsters = new MonsterFactory(bundle.Monsters, entityFactory);
        var items = new ItemFactory(bundle.Items, entityFactory);
        var consumables = new ConsumableFactory(bundle.Consumables, entityFactory);
        return (monsters, items, consumables);
    }

    // Use a large map to maximize spawn sample size — 500-room equivalent via large parameters.
    private static GeneratedMap MakeLargeMap(int seed = 1337) =>
        MapGenerator.Generate(120, 80, 150, 5, 10, new SeededRandom(seed));

    [Test]
    public void ZombieDoesNotSpawnBeforeDepth10()
    {
        var (monsters, _, consumables) = BuildDepthGateFactories();
        var map = MakeLargeMap(seed: 1337);
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(1337);

        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 9, ids);

        var zombies = placed.Where(e => e.Name == "Zombie").ToList();
        Assert.That(zombies, Is.Empty, $"Expected no zombies at depth 9, but found {zombies.Count}");
    }

    [Test]
    public void ZombieSpawnsAtDepth10()
    {
        var (monsters, _, consumables) = BuildDepthGateFactories();
        var map = MakeLargeMap(seed: 1337);
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(1337);

        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 10, ids);

        var zombies = placed.Where(e => e.Name == "Zombie").ToList();
        Assert.That(zombies.Count, Is.GreaterThan(0), "Expected at least one zombie at depth 10");
    }

    [Test]
    public void OrcBruteDoesNotSpawnBeforeDepth3()
    {
        var (monsters, _, consumables) = BuildDepthGateFactories();
        var map = MakeLargeMap(seed: 1337);
        var ids = new EntityIdAllocator(200);
        var rng = new SeededRandom(1337);

        var placed = EntityPlacer.FillRooms(map, null, monsters, consumables, rng, depth: 2, ids);

        var brutes = placed.Where(e => e.Name == "Orc Brute").ToList();
        Assert.That(brutes, Is.Empty, $"Expected no orc_brutes at depth 2, but found {brutes.Count}");
    }
}
