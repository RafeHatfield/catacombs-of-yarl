using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using PityTrackerType = CatacombsOfYarl.Logic.Balance.PityTracker;

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
    ///
    /// spellItems: optional SpellItemFactory for resolving scroll and wand item IDs.
    /// Resolution order for items: SpellItemFactory.CreateScroll → SpellItemFactory.CreateWand
    /// → ConsumableFactory. Matches FillRooms and GameStateFactory.FromScenario patterns.
    /// </summary>
    public static List<Entity> PlaceGuaranteedSpawns(
        GeneratedMap map,
        GuaranteedSpawns spawns,
        MonsterFactory monsters,
        ItemFactory items,
        ConsumableFactory consumables,
        SeededRandom rng,
        int depth,
        EntityIdAllocator ids,
        SpellItemFactory? spellItems = null)
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

        // Place guaranteed consumable items (potions, scrolls, wands)
        // Resolution order mirrors FillRooms: SpellItemFactory scroll → wand → ConsumableFactory.
        // This allows guaranteed_spawns.items to include scroll/wand IDs alongside potion IDs.
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

                Entity? entity = null;

                // Try SpellItemFactory first (scrolls and wands)
                if (spellItems != null)
                {
                    entity = spellItems.CreateScroll(entry.Type)
                        ?? spellItems.CreateWand(entry.Type, rng, depth);
                }

                // Fall back to ConsumableFactory (potions)
                entity ??= consumables.Create(entry.Type);

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
        bool allowSpike = false,
        ItemFactory? items = null,
        IReadOnlyList<FloorItemPoolEntry>? floorItemPool = null,
        SpellItemFactory? spellItems = null,
        Content.IdentificationRegistry? identRegistry = null,
        Content.AppearancePool? appearancePool = null,
        Difficulty difficulty = Difficulty.Medium,
        Content.LootTagRegistry? lootTagRegistry = null,
        Content.LootPolicyConfig? lootPolicy = null,
        PityTrackerType? pityTracker = null)
    {
        var placed = new List<Entity>();
        var occupied = new HashSet<(int, int)>();

        occupied.Add(map.PlayerSpawn);
        if (map.StairDownPos.HasValue) occupied.Add(map.StairDownPos.Value);
        if (map.StairUpPos.HasValue) occupied.Add(map.StairUpPos.Value);

        // Precompute globally reachable tiles via flood fill from player spawn.
        // Props can create enclosed walkable pockets inside rooms that IsWalkable() accepts
        // but pathfinding cannot reach. Filtering candidates against this set ensures nothing
        // is placed in an unreachable corner.
        var reachable = FloodFillReachable(map.Map, map.PlayerSpawn.X, map.PlayerSpawn.Y);

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
            .Select(id =>
            {
                monsters.TryGetDefinition(id, out var d);
                int weight = d!.DepthWeights != null
                    ? SpawnUtils.FromDungeonLevel(d.DepthWeights, depth)
                    : (d.SpawnWeight ?? 0);
                return (id, weight);
            })
            .Where(p => p.weight > 0)
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

        // Depth-filtered equipment pool for floor drops.
        // MinDepth: item must be unlocked at this depth.
        // MaxDepth: item ages out above this depth (defaults to 99 — no cap unless specified).
        var depthFilteredEquipPool = floorItemPool?
            .Where(e => e.MinDepth <= depth && e.MaxDepth >= depth)
            .ToList();

        foreach (var room in map.Rooms)
        {
            // Skip player room — player starts here, no hostile spawns
            if (room == map.PlayerRoom) continue;

            int roomEtp = 0;

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

                var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                if (pos == null) break;

                // Resolve orc variants based on depth — "orc" routes to a depth-appropriate subtype.
                string resolvedId = monsterId == "orc" ? Balance.OrcVariantResolver.Resolve(depth, rng) : monsterId;
                var entity = monsters.Create(resolvedId, pos.Value.X, pos.Value.Y, depth, rng);
                if (entity == null) continue;

                var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                CopyComponents(entity, withId);
                ReIdMonsterEquipment(withId, ids);

                map.Map.RegisterEntity(withId);
                occupied.Add(pos.Value);
                placed.Add(withId);
                roomEtp += etp;
            }

            // ── Per-room pity advance ────────────────────────────────────────
            // Advance pity counters before generating an item. This means the counter
            // reflects "rooms processed without X" at the moment of generation — matches
            // PoC semantics where the counter increments when a room is entered.
            pityTracker?.AdvanceRoom();

            // Roll item count for this room (0 to maxItems).
            // Dead-end rooms guarantee at least 1 item as a loot bias — rewarding exploration
            // of branching passages that lead nowhere else (SROOM-001).
            if (consumablePool.Count > 0)
            {
                int itemCount = room.IsDeadEnd
                    ? rng.Next(1, maxItems + 2)   // 1..(maxItems+1) — always at least 1
                    : rng.Next(0, maxItems + 1);   // 0..maxItems — normal
                for (int i = 0; i < itemCount; i++)
                {
                    string consumableId = consumablePool[rng.Next(consumablePool.Count)];
                    var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                    if (pos == null) break;

                    var entity = consumables.Create(consumableId,
                        registry: identRegistry, pool: appearancePool, rng: rng, difficulty: difficulty);
                    if (entity == null) continue;

                    var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                    CopyComponents(entity, withId);

                    map.Map.RegisterEntity(withId);
                    occupied.Add(pos.Value);
                    placed.Add(withId);
                }
            }

            // ── Floor loot drop ─────────────────────────────────────────────
            // LootController path (when loot registries are available):
            //   - Band-density scaling (B1=35%, B2=45%, B3-B5=100%)
            //   - Category-weighted selection from band EV table
            //   - Pity-tracked categories biased when dry
            //   - Dead-end rooms skip the density roll (always get an item)
            //   - Vault rooms generate 1-2 guaranteed items (density roll also skipped)
            //
            // Fallback path (when registries are null):
            //   - Flat ~40% roll + SelectWeighted from depth-filtered flat pool
            //   - Backward compat for tests that don't load loot_tags.yaml
            if (lootTagRegistry != null && lootPolicy != null)
            {
                // LootController-driven path (new band-aware system)
                bool isDeadEnd = room.IsDeadEnd;
                bool isVault = room.IsVault;

                // Dead-end: always generate at least one item
                if (isDeadEnd || isVault)
                {
                    int lootCount = isVault ? rng.Next(1, 3) : 1; // vault: 1-2, dead-end: always 1
                    for (int li = 0; li < lootCount; li++)
                    {
                        string? itemId = LootController.GenerateRoomItem(
                            depth, rng, lootTagRegistry, lootPolicy, pityTracker,
                            skipDensityRoll: true);  // guaranteed — skip density

                        if (itemId == null) continue;

                        var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                        if (pos == null) break;

                        var lootEntity = ResolveAndCreateItem(itemId, depth, rng, spellItems, items,
                            consumables, identRegistry, appearancePool, difficulty);
                        if (lootEntity == null) continue;

                        var withId = new Entity(ids.Next(), lootEntity.Name, pos.Value.X, pos.Value.Y, lootEntity.BlocksMovement);
                        CopyComponents(lootEntity, withId);
                        map.Map.RegisterEntity(withId);
                        occupied.Add(pos.Value);
                        placed.Add(withId);
                    }
                }
                else
                {
                    // Normal room: density roll decides whether an item appears
                    string? itemId = LootController.GenerateRoomItem(
                        depth, rng, lootTagRegistry, lootPolicy, pityTracker,
                        skipDensityRoll: false);

                    if (itemId != null)
                    {
                        var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                        if (pos != null)
                        {
                            var lootEntity = ResolveAndCreateItem(itemId, depth, rng, spellItems, items,
                                consumables, identRegistry, appearancePool, difficulty);
                            if (lootEntity != null)
                            {
                                var withId = new Entity(ids.Next(), lootEntity.Name, pos.Value.X, pos.Value.Y, lootEntity.BlocksMovement);
                                CopyComponents(lootEntity, withId);
                                map.Map.RegisterEntity(withId);
                                occupied.Add(pos.Value);
                                placed.Add(withId);
                            }
                        }
                    }
                }
            }
            else
            {
                // ── Fallback: flat pool selection ────────────────────────────
                // Used when loot_tags.yaml/loot_policy.yaml not loaded (e.g., unit tests).
                // Preserves existing ~40% roll + SelectWeighted behaviour.

                bool canDropItem = depthFilteredEquipPool != null && depthFilteredEquipPool.Count > 0
                    && rng.Next(0, 100) < 40;
                if (canDropItem)
                {
                    var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                    if (pos != null)
                    {
                        var entry = SelectWeighted(depthFilteredEquipPool!, rng);
                        if (entry != null)
                        {
                            Entity? entity = null;

                            if (spellItems != null)
                            {
                                entity = spellItems.CreateScroll(entry.ItemId,
                                            registry: identRegistry, pool: appearancePool,
                                            identRng: rng, difficulty: difficulty)
                                    ?? spellItems.CreateWand(entry.ItemId, rng, depth,
                                            registry: identRegistry, pool: appearancePool,
                                            identRng: rng, difficulty: difficulty);
                            }

                            entity ??= items?.Create(entry.ItemId);
                            entity ??= consumables.Create(entry.ItemId, registry: identRegistry,
                                pool: appearancePool, rng: rng, difficulty: difficulty);

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

                // Vault room flat-pool fallback
                if (room.IsVault && depthFilteredEquipPool != null && depthFilteredEquipPool.Count > 0)
                {
                    int vaultItemCount = rng.Next(1, 3); // 1-2 guaranteed items
                    for (int vi = 0; vi < vaultItemCount; vi++)
                    {
                        var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                        if (pos == null) break;

                        var entry = SelectWeighted(depthFilteredEquipPool, rng);
                        if (entry == null) break;

                        Entity? entity = null;
                        if (spellItems != null)
                        {
                            entity = spellItems.CreateScroll(entry.ItemId,
                                         registry: identRegistry, pool: appearancePool,
                                         identRng: rng, difficulty: difficulty)
                                  ?? spellItems.CreateWand(entry.ItemId, rng, depth,
                                         registry: identRegistry, pool: appearancePool,
                                         identRng: rng, difficulty: difficulty);
                        }
                        entity ??= items?.Create(entry.ItemId);

                        if (entity == null) continue;

                        var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                        CopyComponents(entity, withId);
                        map.Map.RegisterEntity(withId);
                        occupied.Add(pos.Value);
                        placed.Add(withId);
                    }
                }
            }

            // Vault rooms guarantee 1 guardian monster regardless of normal ETP budget.
            // Vault rooms are meant to be dangerous — the guardian is why the room has good loot.
            if (room.IsVault && (useWeighted ? weightedPool.Count > 0 : allDepthEligible.Count > 0))
            {
                string guardianId = useWeighted
                    ? SelectWeightedMonster(weightedPool, rng)
                    : allDepthEligible[rng.Next(allDepthEligible.Count)];

                string resolvedId = guardianId == "orc"
                    ? Balance.OrcVariantResolver.Resolve(depth, rng)
                    : guardianId;

                var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                if (pos != null)
                {
                    var entity = monsters.Create(resolvedId, pos.Value.X, pos.Value.Y, depth, rng);
                    if (entity != null)
                    {
                        var withId = new Entity(ids.Next(), entity.Name, pos.Value.X, pos.Value.Y, entity.BlocksMovement);
                        CopyComponents(entity, withId);
                        ReIdMonsterEquipment(withId, ids);
                        map.Map.RegisterEntity(withId);
                        occupied.Add(pos.Value);
                        placed.Add(withId);
                    }
                }
            }
        }

        // Grand Shrine altar rewards — place a guaranteed item at each altar position.
        // Altar rewards are more interesting than typical floor loot: prefer upgrade_weapon or
        // upgrade_armor categories (PoC: altar = gear shrine). Pity is not applied to altar loot.
        // Item placement at the altar is a real pickup entity, not a prop.
        foreach (var altarPos in map.GrandShrineAltarPositions)
        {
            if (occupied.Contains(altarPos)) continue;
            if (!map.Map.IsWalkable(altarPos.X, altarPos.Y)) continue;

            Entity? altarItem = null;

            if (lootTagRegistry != null && lootPolicy != null)
            {
                // LootController: bias toward upgrade_weapon or upgrade_armor
                string altarCategory = rng.Next(2) == 0 ? "upgrade_weapon" : "upgrade_armor";
                string? altarItemId = LootController.GenerateRoomItem(
                    depth, rng, lootTagRegistry, lootPolicy, pity: null,
                    skipDensityRoll: true, forcedCategory: altarCategory);
                if (altarItemId != null)
                {
                    altarItem = ResolveAndCreateItem(altarItemId, depth, rng, spellItems, items,
                        consumables, identRegistry, appearancePool, difficulty);
                }
            }
            else if (depthFilteredEquipPool != null && depthFilteredEquipPool.Count > 0)
            {
                // Fallback: flat pool
                var entry = SelectWeighted(depthFilteredEquipPool, rng);
                if (entry != null)
                {
                    if (spellItems != null)
                    {
                        altarItem = spellItems.CreateScroll(entry.ItemId,
                                        registry: identRegistry, pool: appearancePool,
                                        identRng: rng, difficulty: difficulty)
                                 ?? spellItems.CreateWand(entry.ItemId, rng, depth,
                                        registry: identRegistry, pool: appearancePool,
                                        identRng: rng, difficulty: difficulty);
                    }
                    altarItem ??= items?.Create(entry.ItemId);
                }
            }

            // Fall back to consumable if all other paths fail
            if (altarItem == null && consumablePool.Count > 0)
            {
                string consumableId = consumablePool[rng.Next(consumablePool.Count)];
                altarItem = consumables.Create(consumableId,
                    registry: identRegistry, pool: appearancePool, rng: rng, difficulty: difficulty);
            }

            if (altarItem == null) continue;

            var withId = new Entity(ids.Next(), altarItem.Name, altarPos.X, altarPos.Y, altarItem.BlocksMovement);
            CopyComponents(altarItem, withId);
            map.Map.RegisterEntity(withId);
            occupied.Add(altarPos);
            placed.Add(withId);
        }

        return placed;
    }

    /// <summary>
    /// Resolve an item ID from LootController to a concrete Entity using the factory chain.
    /// Resolution order: SpellItemFactory (scrolls → wands) → ItemFactory (equipment) → ConsumableFactory.
    /// Returns null if no factory can resolve the ID.
    /// </summary>
    private static Entity? ResolveAndCreateItem(
        string itemId, int depth, SeededRandom rng,
        SpellItemFactory? spellItems, ItemFactory? items, ConsumableFactory consumables,
        Content.IdentificationRegistry? identRegistry, Content.AppearancePool? appearancePool,
        Difficulty difficulty)
    {
        Entity? entity = null;

        if (spellItems != null)
        {
            entity = spellItems.CreateScroll(itemId,
                         registry: identRegistry, pool: appearancePool,
                         identRng: rng, difficulty: difficulty)
                  ?? spellItems.CreateWand(itemId, rng, depth,
                         registry: identRegistry, pool: appearancePool,
                         identRng: rng, difficulty: difficulty);
        }

        entity ??= items?.Create(itemId);

        entity ??= consumables.Create(itemId,
            registry: identRegistry, pool: appearancePool, rng: rng, difficulty: difficulty);

        return entity;
    }

    /// <summary>
    /// Place interactive features (chests, signposts, murals) on a dungeon floor.
    ///
    /// Floor-level quotas:
    ///   - 1 chest per floor (100% chance), placed in a random non-player room.
    ///   - 0–2 signs per floor (50/35/15 distribution), placed in non-player rooms.
    ///   - 0–1 mural per floor (40% chance), placed wall-adjacent in a non-player room.
    ///
    /// All features are placed at reachable, walkable, unoccupied positions.
    /// Features are registered on the map so pathfinding treats them as blocking.
    ///
    /// Returns a flat list of all created feature entities.
    /// When signRegistry or muralRegistry is null, that feature type is skipped (scenario mode).
    /// </summary>
    public static List<Entity> PlaceFloorFeatures(
        GeneratedMap map,
        EntityIdAllocator ids,
        SeededRandom rng,
        int depth,
        HashSet<(int, int)> occupied,
        SignpostMessageRegistry? signRegistry,
        MuralRegistry? muralRegistry,
        MuralTracker? muralTracker,
        IReadOnlyList<FloorItemPoolEntry>? floorItemPool = null,
        SpellItemFactory? spellItems = null,
        ItemFactory? items = null,
        ConsumableFactory? consumables = null,
        IdentificationRegistry? identRegistry = null,
        AppearancePool? appearancePool = null,
        Difficulty difficulty = Difficulty.Medium,
        Content.LootTagRegistry? lootTagRegistry = null,
        Content.LootPolicyConfig? lootPolicy = null)
    {
        var placed = new List<Entity>();

        // Non-player rooms for feature placement
        var featureRooms = map.Rooms
            .Where(r => r != map.PlayerRoom)
            .ToList();

        if (featureRooms.Count == 0)
            return placed;

        // Precompute reachable tiles for features too (avoids prop-enclosed pockets)
        var reachable = FloodFillReachable(map.Map, map.PlayerSpawn.X, map.PlayerSpawn.Y);

        // ── Chest placement (1 per floor, always) ────────────────────────────
        {
            var room = featureRooms[rng.Next(featureRooms.Count)];
            var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
            if (pos != null)
            {
                // Generate loot now for determinism — same seed produces same chest contents.
                // LootController path: use band-aware chest loot generation.
                // Fallback: legacy ChestLootGenerator from flat floor item pool.
                List<Entity> lootEntities;
                if (lootTagRegistry != null && lootPolicy != null && consumables != null)
                {
                    // LootController generates item IDs; resolve them to entities via factory chain.
                    var chestItemIds = LootController.GenerateChestLoot(depth, rng, lootTagRegistry, lootPolicy, pity: null);
                    lootEntities = new List<Entity>(chestItemIds.Count);
                    foreach (var itemId in chestItemIds)
                    {
                        var lootEntity = ResolveAndCreateItem(itemId, depth, rng, spellItems, items,
                            consumables, identRegistry, appearancePool, difficulty);
                        if (lootEntity == null) continue;
                        var lootWithId = new Entity(ids.Next(), lootEntity.Name, 0, 0, lootEntity.BlocksMovement);
                        CopyComponents(lootEntity, lootWithId);
                        lootEntities.Add(lootWithId);
                    }
                }
                else
                {
                    lootEntities = floorItemPool != null && consumables != null
                        ? ChestLootGenerator.Generate(depth, rng, ids, floorItemPool, spellItems, items, consumables,
                            identRegistry, appearancePool, difficulty)
                        : new List<Entity>();
                }

                var chest = FeatureFactory.CreateChest(pos.Value.X, pos.Value.Y, ids);
                map.Map.RegisterEntity(chest);
                occupied.Add(pos.Value);
                placed.Add(chest);

                // Register loot entities as floor items at the chest position —
                // they are not yet accessible; they'll be dropped to FloorItems on open.
                // Store loot item IDs on the component for TurnController to resolve.
                var chestComp = chest.Get<ChestComponent>();
                if (chestComp != null)
                    foreach (var lootItem in lootEntities)
                        chestComp.LootItemIds.Add(lootItem.Id.ToString());

                // Keep loot entities in the placed list so DungeonFloorBuilder can route them.
                // They start with no position on the map — they appear only when the chest opens.
                // The caller (DungeonFloorBuilder) must NOT register them or add them to FloorItems
                // until the chest is opened. Tag them with ChestLoot so the caller can identify them.
                // For simplicity in this pass: store loot entities as pre-built items at (chestX, chestY)
                // and add them to FloorItems — TurnController will already have them ready.
                // Actually: PoC resolves loot at open-time. C# pass: generate at place-time and
                // pre-position at chest coords, but only add to FloorItems on ChestOpenedEvent.
                // Store loot in ChestLootStash on the entity. See TASK-004 for consumption.

                // Attach a ChestLootStash component so TurnController can drop them on open.
                chest.Add(new ChestLootStash(lootEntities));
            }
        }

        // ── Sign placement (0–2 per floor) ───────────────────────────────────
        if (signRegistry != null)
        {
            // 50/35/15 distribution for 0/1/2 signs
            int signRoll = rng.Next(100);
            int signCount = signRoll < 50 ? 0 : signRoll < 85 ? 1 : 2;

            var signTypes = signRegistry.SignTypes;

            for (int i = 0; i < signCount; i++)
            {
                var room = featureRooms[rng.Next(featureRooms.Count)];
                var pos = FindFreePosition(map.Map, room, occupied, rng, reachable);
                if (pos == null) continue;

                string signType = signTypes[rng.Next(signTypes.Count)];
                var (message, resolvedType) = signRegistry.GetRandomMessage(signType, depth, rng);

                var sign = FeatureFactory.CreateSignpost(pos.Value.X, pos.Value.Y, ids, message, resolvedType);
                map.Map.RegisterEntity(sign);
                occupied.Add(pos.Value);
                placed.Add(sign);
            }
        }

        // ── Mural placement (0–1 per floor, wall-adjacent) ───────────────────
        if (muralRegistry != null && muralTracker != null && rng.Next(100) < 40)
        {
            muralTracker.ResetForFloor();

            // Find a wall-adjacent walkable tile in a non-player room
            (int X, int Y)? muralPos = null;
            foreach (var room in featureRooms.OrderBy(_ => rng.Next(int.MaxValue)))
            {
                muralPos = FindWallAdjacentPosition(map.Map, room, occupied, rng, reachable);
                if (muralPos != null) break;
            }

            if (muralPos != null)
            {
                var muralData = muralTracker.GetUniqueMuralForFloor(depth, muralRegistry, rng);
                if (muralData != null)
                {
                    // Pick a random tile variant (4036, 4037, 4038)
                    int tileId = 4036 + rng.Next(3);

                    var mural = FeatureFactory.CreateMural(
                        muralPos.Value.X, muralPos.Value.Y, ids,
                        muralData.Value.Text, muralData.Value.Id, tileId);
                    map.Map.RegisterEntity(mural);
                    occupied.Add(muralPos.Value);
                    placed.Add(mural);
                }
            }
        }

        return placed;
    }

    /// <summary>
    /// Find a walkable, unoccupied tile adjacent to at least one wall (cardinal neighbor).
    /// Used for mural placement — murals should feel embedded in the stonework.
    /// Returns null if no wall-adjacent free tile exists in the room.
    /// </summary>
    private static (int X, int Y)? FindWallAdjacentPosition(
        GameMap map, Room room, HashSet<(int, int)> occupied,
        SeededRandom rng, HashSet<(int, int)>? reachable = null)
    {
        var candidates = new List<(int X, int Y)>();
        for (int x = room.X; x < room.X + room.Width; x++)
        {
            for (int y = room.Y; y < room.Y + room.Height; y++)
            {
                if (!map.IsWalkable(x, y)) continue;
                if (occupied.Contains((x, y))) continue;
                if (reachable != null && !reachable.Contains((x, y))) continue;

                // Must have at least one cardinal wall neighbor
                bool hasWallNeighbor =
                    (!map.InBounds(x, y - 1) || map.GetTileKind(x, y - 1) == TileKind.Wall) ||
                    (!map.InBounds(x, y + 1) || map.GetTileKind(x, y + 1) == TileKind.Wall) ||
                    (!map.InBounds(x - 1, y) || map.GetTileKind(x - 1, y) == TileKind.Wall) ||
                    (!map.InBounds(x + 1, y) || map.GetTileKind(x + 1, y) == TileKind.Wall);

                if (hasWallNeighbor)
                    candidates.Add((x, y));
            }
        }

        if (candidates.Count == 0) return null;
        return candidates[rng.Next(candidates.Count)];
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
        SeededRandom rng,
        HashSet<(int, int)>? reachable = null)
    {
        // Collect all candidate tiles in this room that are walkable, unoccupied,
        // and reachable from the player spawn (when a reachable set is provided).
        // The reachable filter prevents items/monsters from being placed in walkable
        // pockets that are physically enclosed by blocking props.
        var candidates = new List<(int X, int Y)>();
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                if (map.IsWalkable(x, y) && !occupied.Contains((x, y))
                    && (reachable == null || reachable.Contains((x, y))))
                    candidates.Add((x, y));

        if (candidates.Count == 0) return null;

        return candidates[rng.Next(candidates.Count)];
    }

    /// <summary>
    /// BFS flood fill from (startX, startY) across walkable tiles.
    /// Returns all reachable (X, Y) positions. Used to exclude prop-enclosed
    /// unreachable pockets from entity placement candidates.
    /// </summary>
    private static HashSet<(int, int)> FloodFillReachable(GameMap map, int startX, int startY)
    {
        var visited = new HashSet<(int, int)>();
        if (!map.IsWalkable(startX, startY)) return visited;

        var queue = new Queue<(int, int)>();
        queue.Enqueue((startX, startY));
        visited.Add((startX, startY));

        while (queue.Count > 0)
        {
            var (x, y) = queue.Dequeue();
            foreach (var (nx, ny) in new[] { (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) })
            {
                if (visited.Contains((nx, ny))) continue;
                // Treat Door as passable — opening it grants access to the room beyond.
                var nk = map.GetTileKind(nx, ny);
                if (map.IsWalkable(nx, ny) || nk == TileKind.Door)
                {
                    visited.Add((nx, ny));
                    queue.Enqueue((nx, ny));
                }
            }
        }

        return visited;
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
