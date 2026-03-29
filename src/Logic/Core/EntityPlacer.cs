using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Places entities (monsters, items, stairs) onto a GeneratedMap.
/// Separated from MapGenerator so geometry generation and entity placement are independently testable.
///
/// Procedural fill logic matches Python's place_entities:
/// - Skip player room for monster placement
/// - Roll monster/item counts per room
/// - Check ETP budget per room before spawning a monster
/// - Place at a random walkable, unoccupied tile
/// </summary>
public static class EntityPlacer
{
    /// <summary>Default per-room ETP cap when no encounter_budget is configured in the template.</summary>
    public const int DefaultRoomEtpMax = 50;

    /// <summary>
    /// Place guaranteed spawns from a GuaranteedSpawns block.
    /// Monsters are placed in rooms other than the player room.
    /// Items are placed in any room.
    /// Returns all entities created.
    /// </summary>
    public static List<Entity> PlaceGuaranteedSpawns(
        GeneratedMap map,
        GuaranteedSpawns spawns,
        MonsterFactory monsters,
        ItemFactory items,
        ConsumableFactory consumables,
        SeededRandom rng,
        int depth,
        EntityIdAllocator ids)
    {
        var placed = new List<Entity>();
        var occupied = new HashSet<(int, int)>();

        // Occupied positions start with the player spawn and stair positions
        occupied.Add(map.PlayerSpawn);
        if (map.StairDownPos.HasValue) occupied.Add(map.StairDownPos.Value);
        if (map.StairUpPos.HasValue) occupied.Add(map.StairUpPos.Value);

        // Eligible rooms for monster placement: all rooms except the player room
        var monsterRooms = map.Rooms
            .Where(r => r != map.PlayerRoom)
            .ToList();

        if (monsterRooms.Count == 0)
            monsterRooms = map.Rooms.ToList(); // fallback if only 1 room

        // Place guaranteed monsters
        foreach (var entry in spawns.Monsters)
        {
            int count = entry.CountMin == entry.CountMax
                ? entry.CountMin
                : rng.Next(entry.CountMin, entry.CountMax + 1);

            for (int i = 0; i < count; i++)
            {
                // Pick a random eligible room
                var room = monsterRooms[rng.Next(monsterRooms.Count)];
                var pos = FindFreePosition(map.Map, room, occupied, rng);
                if (pos == null) continue;

                var entity = monsters.Create(entry.Type, pos.Value.X, pos.Value.Y, depth, rng);
                if (entity == null) continue;

                // Override entity ID to use allocator
                var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                CopyComponents(entity, withId);
                ReIdMonsterEquipment(withId, ids);

                map.Map.RegisterEntity(withId);
                occupied.Add(pos.Value);
                placed.Add(withId);
            }
        }

        // Place guaranteed consumable items
        foreach (var entry in spawns.Items)
        {
            int count = entry.CountMin == entry.CountMax
                ? entry.CountMin
                : rng.Next(entry.CountMin, entry.CountMax + 1);

            for (int i = 0; i < count; i++)
            {
                var room = map.Rooms[rng.Next(map.Rooms.Count)];
                var pos = FindFreePosition(map.Map, room, occupied, rng);
                if (pos == null) continue;

                var entity = consumables.Create(entry.Type);
                if (entity == null) continue;

                var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                CopyComponents(entity, withId);

                map.Map.RegisterEntity(withId);
                occupied.Add(pos.Value);
                placed.Add(withId);
            }
        }

        // Place guaranteed equipment items
        foreach (var entry in spawns.Equipment)
        {
            int count = entry.CountMin == entry.CountMax
                ? entry.CountMin
                : rng.Next(entry.CountMin, entry.CountMax + 1);

            for (int i = 0; i < count; i++)
            {
                var room = map.Rooms[rng.Next(map.Rooms.Count)];
                var pos = FindFreePosition(map.Map, room, occupied, rng);
                if (pos == null) continue;

                var entity = items.Create(entry.Type);
                if (entity == null) continue;

                var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                CopyComponents(entity, withId);

                map.Map.RegisterEntity(withId);
                occupied.Add(pos.Value);
                placed.Add(withId);
            }
        }

        return placed;
    }

    /// <summary>
    /// Procedurally fill rooms with monsters, consumables, and floor equipment.
    /// Skips the player room. Checks ETP budget per room.
    /// Matching Python place_entities logic.
    ///
    /// If itemFactory and floorItemPool are provided, each non-player room also has a chance
    /// to receive one piece of floor equipment drawn from the depth-filtered pool.
    /// TODO: replace the separate consumable + equipment passes with a single unified pool
    ///       once the band-density scaling system (PoC B1-B5) is ported.
    /// </summary>
    public static List<Entity> FillRooms(
        GeneratedMap map,
        GenerationParameters? genParams,
        MonsterFactory monsters,
        ConsumableFactory consumables,
        SeededRandom rng,
        int depth,
        EntityIdAllocator ids,
        int roomEtpMax = DefaultRoomEtpMax,
        ItemFactory? items = null,
        IReadOnlyList<FloorItemPoolEntry>? floorItemPool = null)
    {
        var placed = new List<Entity>();
        var occupied = new HashSet<(int, int)>();

        occupied.Add(map.PlayerSpawn);
        if (map.StairDownPos.HasValue) occupied.Add(map.StairDownPos.Value);
        if (map.StairUpPos.HasValue) occupied.Add(map.StairUpPos.Value);

        // Track existing registered entities to avoid overlap
        // (guaranteed spawns may have already been placed)

        int maxMonsters = genParams?.MaxMonstersPerRoom ?? 3;
        int maxItems = genParams?.MaxItemsPerRoom ?? 2;

        // Build a weighted pool of monster IDs available at this depth.
        // Only monsters with SpawnWeight > 0 are eligible for procedural placement.
        // Falls back to uniform selection from all depth-eligible monsters if no weighted
        // candidates exist (defensive — shouldn't happen in a properly configured game).
        var allDepthEligible = monsters.AvailableIds
            .Where(id => monsters.TryGetDefinition(id, out var d) && d!.MinDepth <= depth)
            .ToList();

        var weightedPool = allDepthEligible
            .Where(id => monsters.TryGetDefinition(id, out var d) && d!.SpawnWeight > 0)
            .Select(id => { monsters.TryGetDefinition(id, out var d); return (id, d!.SpawnWeight); })
            .ToList();

        bool useWeighted = weightedPool.Count > 0;
        if (!useWeighted)
        {
            // Warn: no weighted monsters at this depth — falling back to uniform selection.
            // This is a content configuration gap, not a runtime error.
            System.Diagnostics.Debug.WriteLine(
                $"[EntityPlacer] Warning: no monsters with spawn_weight > 0 at depth {depth}. " +
                $"Falling back to uniform selection from {allDepthEligible.Count} depth-eligible monsters.");
        }

        var consumablePool = consumables.AvailableIds.ToList();

        // Depth-filtered equipment pool for floor drops
        var depthFilteredEquipPool = floorItemPool?
            .Where(e => e.MinDepth <= depth)
            .ToList();

        foreach (var room in map.Rooms)
        {
            // Skip player room — player starts here, no hostile spawns
            if (room == map.PlayerRoom) continue;

            int roomEtp = 0;
            bool allowSpike = false;

            // Roll monster count for this room (0 to maxMonsters)
            int monsterCount = rng.Next(0, maxMonsters + 1);

            for (int i = 0; i < monsterCount; i++)
            {
                if (useWeighted ? weightedPool.Count == 0 : allDepthEligible.Count == 0) break;

                string monsterId = useWeighted
                    ? SelectWeightedMonster(weightedPool, rng)
                    : allDepthEligible[rng.Next(allDepthEligible.Count)];
                if (!monsters.TryGetDefinition(monsterId, out var def)) continue;

                int etp = EtpCalculator.GetEtp(def!);
                if (!EtpCalculator.FitsInBudget(roomEtp, etp, roomEtpMax, allowSpike)) continue;

                var pos = FindFreePosition(map.Map, room, occupied, rng);
                if (pos == null) break;

                var entity = monsters.Create(monsterId, pos.Value.X, pos.Value.Y, depth, rng);
                if (entity == null) continue;

                var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                CopyComponents(entity, withId);
                ReIdMonsterEquipment(withId, ids);

                map.Map.RegisterEntity(withId);
                occupied.Add(pos.Value);
                placed.Add(withId);
                roomEtp += etp;
            }

            // Roll item count for this room (0 to maxItems)
            if (consumablePool.Count > 0)
            {
                int itemCount = rng.Next(0, maxItems + 1);
                for (int i = 0; i < itemCount; i++)
                {
                    string consumableId = consumablePool[rng.Next(consumablePool.Count)];
                    var pos = FindFreePosition(map.Map, room, occupied, rng);
                    if (pos == null) break;

                    var entity = consumables.Create(consumableId);
                    if (entity == null) continue;

                    var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                    CopyComponents(entity, withId);

                    map.Map.RegisterEntity(withId);
                    occupied.Add(pos.Value);
                    placed.Add(withId);
                }
            }

            // Floor equipment drop — ~40% chance per room of one equipment item.
            // Pool is depth-filtered at call time so this is just a weighted draw.
            // TODO: replace the flat 40% with PoC band-density scaling (B1=0.35x, B2=0.45x, B3+=1.0x).
            if (items != null && depthFilteredEquipPool != null && depthFilteredEquipPool.Count > 0
                && rng.Next(0, 100) < 40)
            {
                var pos = FindFreePosition(map.Map, room, occupied, rng);
                if (pos != null)
                {
                    var entry = SelectWeighted(depthFilteredEquipPool, rng);
                    if (entry != null)
                    {
                        var entity = items.Create(entry.ItemId);
                        if (entity != null)
                        {
                            var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                            CopyComponents(entity, withId);
                            map.Map.RegisterEntity(withId);
                            occupied.Add(pos.Value);
                            placed.Add(withId);
                        }
                    }
                }
            }
        }

        return placed;
    }

    /// <summary>
    /// Place a stair-down entity at the map's StairDownPos.
    /// Returns null if the map has no stair down position.
    /// </summary>
    public static Entity? PlaceStairDown(GeneratedMap map, int targetDepth, EntityIdAllocator ids)
    {
        if (!map.StairDownPos.HasValue) return null;

        var pos = map.StairDownPos.Value;
        var entity = new Entity(ids.Next(), "Stair Down", pos.X, pos.Y, blocksMovement: false);
        entity.Add(new ECS.Stair(isDown: true, targetDepth: targetDepth));
        map.Map.RegisterEntity(entity);
        return entity;
    }

    /// <summary>
    /// Place a stair-up entity at the map's StairUpPos.
    /// Returns null if the map has no stair up position.
    /// </summary>
    public static Entity? PlaceStairUp(GeneratedMap map, int targetDepth, EntityIdAllocator ids)
    {
        if (!map.StairUpPos.HasValue) return null;

        var pos = map.StairUpPos.Value;
        var entity = new Entity(ids.Next(), "Stair Up", pos.X, pos.Y, blocksMovement: false);
        entity.Add(new ECS.Stair(isDown: false, targetDepth: targetDepth));
        map.Map.RegisterEntity(entity);
        return entity;
    }

    /// <summary>
    /// Find a random walkable, unoccupied tile within a room.
    /// Returns null if no free tile exists after sampling.
    /// </summary>
    private static (int X, int Y)? FindFreePosition(
        GameMap map,
        Room room,
        HashSet<(int, int)> occupied,
        SeededRandom rng)
    {
        // Collect all candidate tiles in this room
        var candidates = new List<(int X, int Y)>();
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                if (map.IsWalkable(x, y) && !occupied.Contains((x, y)))
                    candidates.Add((x, y));

        if (candidates.Count == 0) return null;

        return candidates[rng.Next(candidates.Count)];
    }

    /// <summary>
    /// Weighted random selection from a monster pool of (id, weight) pairs.
    /// Returns the last entry if rounding causes the roll to exceed cumulative total.
    /// </summary>
    private static string SelectWeightedMonster(List<(string Id, int Weight)> pool, SeededRandom rng)
    {
        int total = 0;
        foreach (var (_, w) in pool) total += w;

        int roll = rng.Next(total);
        int cumulative = 0;
        foreach (var (id, w) in pool)
        {
            cumulative += w;
            if (roll < cumulative) return id;
        }
        return pool[^1].Id;
    }

    /// <summary>
    /// Weighted random selection from a floor item pool.
    /// Returns null only if the pool is empty.
    /// </summary>
    private static FloorItemPoolEntry? SelectWeighted(List<FloorItemPoolEntry> pool, SeededRandom rng)
    {
        int total = 0;
        foreach (var e in pool) total += e.Weight;
        if (total <= 0) return null;

        int roll = rng.Next(total);
        int cumulative = 0;
        foreach (var e in pool)
        {
            cumulative += e.Weight;
            if (roll < cumulative) return e;
        }
        return pool[^1];
    }

    /// <summary>
    /// Copy all components from source to destination entity.
    /// Used when we need to re-wrap a factory-created entity under a new ID.
    /// </summary>
    private static void CopyComponents(Entity source, Entity destination)
    {
        foreach (var component in source.GetAllComponents())
        {
            component.Owner = null; // detach from source before adding to destination
            destination.Add(component);
        }
    }

    /// <summary>
    /// Re-ID the equipment items held by a monster so their IDs come from the same
    /// allocator as all other map entities.
    ///
    /// Without this, equipment items keep their EntityFactory IDs (assigned during
    /// MonsterFactory.Create). Those IDs will collide with allocator IDs for later
    /// monsters and consumables, causing duplicate IDs in the map registry when the
    /// monster dies and DropMonsterLoot registers the items as floor entities.
    ///
    /// Call this after CopyComponents has transferred the Equipment component to the
    /// re-wrapped monster entity.
    /// </summary>
    private static void ReIdMonsterEquipment(Entity monster, EntityIdAllocator ids)
    {
        var equipment = monster.Get<Equipment>();
        if (equipment == null) return;

        foreach (EquipmentSlot slot in Enum.GetValues<EquipmentSlot>())
        {
            var item = equipment.GetSlot(slot);
            if (item == null) continue;

            var reId = new Entity(ids.Next(), item.Name, item.X, item.Y, item.BlocksMovement);
            CopyComponents(item, reId);
            equipment.SetSlot(slot, reId);
        }
    }
}
