using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using FloorItemPool = System.Collections.Generic.IReadOnlyList<CatacombsOfYarl.Logic.Content.FloorItemPoolEntry>;
using IdentifiableItemDef = (string id, CatacombsOfYarl.Logic.Content.ItemCategory category);

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Assembles a complete GameState for one dungeon floor.
///
/// This is the dungeon-mode entry point — the equivalent of GameStateFactory.FromScenario
/// but for procedurally generated floors. GameStateFactory.FromScenario is NEVER touched.
///
/// Build() is deterministic for the same depth + rng seed. Callers should seed the rng as:
///   baseSeed + depth * 1_000_003
/// ...to get distinct-but-reproducible floors per depth.
///
/// Dependency graph:
///   LevelTemplateRegistry → per-floor overrides (generation params, guaranteed spawns)
///   MapGenerator → geometry (rooms, corridors)
///   EntityPlacer → monsters, items, stairs
///   PlayerCarryForward → stat persistence when descending
/// </summary>
public sealed class DungeonFloorBuilder
{
    // Defaults used when no level template override is found for a depth.
    // Match PoC game_constants.py: 120×80, 150 attempts, 12–18 room size.
    // PoC gets ~75 actual rooms @ ~200 avg tiles = ~15000 walkable tiles (~31% of map).
    private const int DefaultMapWidth = 120;
    private const int DefaultMapHeight = 80;
    private const int DefaultMaxRooms = 150;
    private const int DefaultMinRoomSize = 12;
    private const int DefaultMaxRoomSize = 18;

    private readonly LevelTemplateRegistry _templates;
    private readonly MonsterFactory _monsterFactory;
    private readonly ItemFactory _itemFactory;
    private readonly ConsumableFactory _consumableFactory;
    private readonly FloorItemPool _floorItemPool;
    private readonly SpellItemFactory? _spellItemFactory;

    /// <summary>
    /// All identifiable item definitions (potions, scrolls, wands, rings) for this run.
    /// Used by AppearancePool construction at the start of each run.
    /// Populated from ConsumableFactory and SpellItemFactory if provided to the constructor.
    /// </summary>
    private readonly List<IdentifiableItemDef> _identifiableItems;

    public DungeonFloorBuilder(
        LevelTemplateRegistry templates,
        MonsterFactory monsterFactory,
        ItemFactory itemFactory,
        ConsumableFactory consumableFactory,
        FloorItemPool? floorItemPool = null,
        SpellItemFactory? spellItemFactory = null)
    {
        _templates = templates;
        _monsterFactory = monsterFactory;
        _itemFactory = itemFactory;
        _consumableFactory = consumableFactory;
        _floorItemPool = floorItemPool ?? [];
        _spellItemFactory = spellItemFactory;

        // Collect identifiable item types for AppearancePool construction.
        // Potions come from ConsumableFactory; scrolls/wands come from SpellItemFactory.
        _identifiableItems = BuildIdentifiableItemList(consumableFactory, spellItemFactory);
    }

    private static List<IdentifiableItemDef> BuildIdentifiableItemList(
        ConsumableFactory consumableFactory, SpellItemFactory? spellItemFactory)
    {
        var list = new List<IdentifiableItemDef>();

        foreach (var id in consumableFactory.AvailableIds)
        {
            var def = consumableFactory.GetDefinition(id);
            if (def != null && def.Category != ItemCategory.Other)
                list.Add((id, def.Category));
        }

        if (spellItemFactory != null)
        {
            foreach (var id in spellItemFactory.AvailableIds)
            {
                var def = spellItemFactory.GetDefinition(id);
                if (def != null && def.Category != ItemCategory.Other)
                    list.Add((id, def.Category));
            }
        }

        return list;
    }

    /// <summary>
    /// Build a complete GameState for the given depth.
    ///
    /// If existingPlayer is non-null, carries HP/equipment/inventory forward via PlayerCarryForward.
    /// If null, this is the start of a new run — no carry-forward needed.
    ///
    /// identificationRegistry and appearancePool:
    ///   - Null = new run: creates fresh instances from run seed.
    ///   - Non-null = floor transition: passes the existing instances through unchanged.
    ///     Registry and pool are NOT reset between floors — only reset on new game.
    ///
    /// The returned state has IsDungeonMode=true and StairDown set (or null if no stair was placed).
    /// </summary>
    public GameState Build(int depth, SeededRandom rng, Entity? existingPlayer = null,
        IdentificationRegistry? identificationRegistry = null,
        AppearancePool? appearancePool = null,
        Difficulty difficulty = Difficulty.Medium)
    {
        // Resolve per-depth override (null = use defaults for everything)
        var levelOverride = _templates.GetLevelOverride(depth);
        var genParams = levelOverride?.Parameters;
        var guaranteedSpawns = levelOverride?.GuaranteedSpawns;
        var stairRules = levelOverride?.Stairs;

        var encounterBudget = levelOverride?.EncounterBudget;
        int roomEtpMax = encounterBudget?.EtpMax ?? EntityPlacer.DefaultRoomEtpMax;
        bool allowSpike = encounterBudget?.AllowSpike ?? false;

        // Generation parameters — override wins, else defaults
        int mapWidth = genParams?.MapWidth ?? DefaultMapWidth;
        int mapHeight = genParams?.MapHeight ?? DefaultMapHeight;
        int maxRooms = genParams?.MaxRooms ?? DefaultMaxRooms;
        int minRoomSize = genParams?.MinRoomSize ?? DefaultMinRoomSize;
        int maxRoomSize = genParams?.MaxRoomSize ?? DefaultMaxRoomSize;

        // Generate the floor geometry
        var generatedMap = MapGenerator.Generate(
            mapWidth, mapHeight, maxRooms, minRoomSize, maxRoomSize, rng, stairRules);

        // Assign visual themes to rooms and corridors.
        // Themes are purely cosmetic — they drive sprite selection in DungeonRenderer.
        // This runs AFTER generation so it does not alter the rng consumption sequence.
        AssignTileThemes(generatedMap, depth, rng);

        // Create or carry forward player — always ID 0.
        // Must happen BEFORE EntityIdAllocator is initialized so that any starting gear
        // created by CreateDefaultPlayer() (dagger, armor, potion) advances the shared
        // EntityFactory counter first.
        Entity player;
        if (existingPlayer != null)
        {
            // Clear all status effects on floor transition — no carry-over between floors.
            // Policy: simplest approach that avoids confusing persistent debuffs across floors.
            StatusEffectProcessor.ClearAllEffects(existingPlayer);
            player = PlayerCarryForward.Apply(existingPlayer);

            // Reset portal wand state — portals don't persist between floors.
            // The portal entities belong to the old GameState (abandoned on transition),
            // so only the wand's step tracker needs resetting here.
            var inventory = existingPlayer.Get<Inventory>();
            if (inventory != null)
            {
                foreach (var invItem in inventory.Items)
                    if (invItem.Get<PortalCastStateComponent>() != null)
                        PortalSystem.ResetPortalWandState(invItem);
            }

            // Restore ring effects that are NOT preserved in the carried Fighter stats.
            // Stat rings (protection/strength/dexterity/constitution/might) survive because
            // PlayerCarryForward copies the live Fighter (which has ring bonuses baked in).
            // But RingMaxHpBonus, SpeedBonusTracker.RingRatio, and FreeActionTag are NOT
            // in Fighter's constructor and are NOT copied — ReapplyRingEffects restores them.
            TurnController.ReapplyRingEffects(player);
        }
        else
        {
            // Fresh player for a new run — caller is responsible for providing a properly
            // configured entity. For now, DungeonFloorBuilder creates a default player.
            // This path is used in tests; production code should pass an existing player.
            player = CreateDefaultPlayer();
        }

        // ID allocator: start AFTER the highest ID already consumed by the shared EntityFactory.
        // CreateDefaultPlayer() above may have consumed IDs 1, 2, 3 for dagger/armor/potion.
        // Starting from NextId guarantees map-placed entities never collide with gear IDs.
        var ids = new EntityIdAllocator(startFrom: _monsterFactory.EntityFactory.NextId);

        // Place player at the map's spawn point and register
        player.X = generatedMap.PlayerSpawn.X;
        player.Y = generatedMap.PlayerSpawn.Y;
        generatedMap.Map.RegisterEntity(player);

        // Create identification registry and pool BEFORE FillRooms so items placed during
        // floor generation receive correct pre-identification decisions.
        // Floor transitions pass existing instances through unchanged (registry persists across floors).
        // New runs create fresh instances from the run seed.
        var finalRegistry = identificationRegistry ?? new IdentificationRegistry();
        var finalPool = appearancePool ?? new AppearancePool(_identifiableItems, rng.Seed);

        // Place entities (monsters + items)
        var allMonsters = new List<Entity>();
        var allFloorItems = new List<Entity>();

        bool hasGuaranteedSpawns = guaranteedSpawns != null &&
            (guaranteedSpawns.Monsters.Count > 0 ||
             guaranteedSpawns.Items.Count > 0 ||
             guaranteedSpawns.Equipment.Count > 0);

        if (hasGuaranteedSpawns)
        {
            var guaranteed = EntityPlacer.PlaceGuaranteedSpawns(
                generatedMap, guaranteedSpawns!, _monsterFactory, _itemFactory, _consumableFactory,
                rng, depth, ids, spellItems: _spellItemFactory);

            // Separate monsters from items.
            // Monsters block movement (BlocksMovement=true from MonsterDefinition.Blocks).
            // Items/consumables do not. We cannot use Has<Fighter>() here because
            // CopyComponents stores components under the IComponent key, not the concrete type key.
            foreach (var entity in guaranteed)
                if (entity.BlocksMovement)
                    allMonsters.Add(entity);
                else
                    allFloorItems.Add(entity);

            // "replace" mode: only guaranteed spawns, no procedural fill
            // "additional" mode: guaranteed spawns + procedural fill
            if (guaranteedSpawns!.Mode != "replace")
            {
                var filled = EntityPlacer.FillRooms(
                    generatedMap, genParams, _monsterFactory, _consumableFactory,
                    rng, depth, ids,
                    roomEtpMax: roomEtpMax,
                    allowSpike: allowSpike,
                    items: _itemFactory, floorItemPool: _floorItemPool,
                    spellItems: _spellItemFactory,
                    identRegistry: finalRegistry, appearancePool: finalPool,
                    difficulty: difficulty);

                foreach (var entity in filled)
                    if (entity.BlocksMovement)
                        allMonsters.Add(entity);
                    else
                        allFloorItems.Add(entity);
            }
        }
        else
        {
            // No guaranteed spawns — full procedural fill
            var filled = EntityPlacer.FillRooms(
                generatedMap, genParams, _monsterFactory, _consumableFactory,
                rng, depth, ids,
                roomEtpMax: roomEtpMax,
                allowSpike: allowSpike,
                items: _itemFactory, floorItemPool: _floorItemPool,
                spellItems: _spellItemFactory,
                identRegistry: finalRegistry, appearancePool: finalPool,
                difficulty: difficulty);

            foreach (var entity in filled)
                if (entity.BlocksMovement)
                    allMonsters.Add(entity);
                else
                    allFloorItems.Add(entity);
        }

        // Place stair down
        var stairDown = EntityPlacer.PlaceStairDown(generatedMap, targetDepth: depth + 1, ids);

        var state = new GameState(player, allMonsters, generatedMap.Map, rng, turnLimit: 10_000)
        {
            IsDungeonMode = true,
            CurrentDepth = depth,
            StairDown = stairDown,
            IdentificationRegistry = finalRegistry,
            AppearancePool = finalPool,
            Difficulty = difficulty,
        };

        // Register floor items into state
        foreach (var item in allFloorItems)
            state.FloorItems.Add(item);

        // Compute initial FOV so the player sees their starting area immediately.
        // This must happen after IsDungeonMode=true is set — RecomputeFov is a no-op
        // when IsDungeonMode=false (scenario mode).
        state.RecomputeFov();

        return state;
    }

    /// <summary>
    /// Assign TileTheme to every room tile and corridor tile in the generated map.
    /// Each room gets one theme (cohesive look within a room). Corridors always get Dirt.
    /// This method consumes rng — call it after MapGenerator.Generate() finishes.
    /// </summary>
    private static void AssignTileThemes(GeneratedMap generatedMap, int depth, SeededRandom rng)
    {
        var map = generatedMap.Map;

        // Corridors: set Dirt theme first (rooms will overwrite tiles that overlap corridors).
        // Iterate the full map — any Corridor tile gets Dirt.
        for (int x = 0; x < map.Width; x++)
            for (int y = 0; y < map.Height; y++)
                if (map.GetTileKind(x, y) == TileKind.Corridor)
                    map.SetTileTheme(x, y, TileTheme.Dirt);

        // Rooms: each room picks one theme. The theme rect overwrites corridors that run
        // through the interior, which is the desired behavior (room wins over corridor).
        foreach (var room in generatedMap.Rooms)
        {
            var theme = PickRoomTheme(depth, rng);
            // Room bounds are [X, X+Width) x [Y, Y+Height) — SetTileThemeRect uses inclusive bounds
            map.SetTileThemeRect(room.X, room.Y, room.X + room.Width - 1, room.Y + room.Height - 1, theme);
        }
    }

    /// <summary>
    /// Pick a room theme based on dungeon depth.
    /// Base theme is determined by depth band; ~15% chance of an "accent" room one step deeper.
    /// </summary>
    private static TileTheme PickRoomTheme(int depth, SeededRandom rng)
    {
        // Base theme by depth band — matches design doc: grey → crypt → moss
        TileTheme baseTheme = depth switch
        {
            <= 3 => TileTheme.Grey,
            <= 6 => TileTheme.Crypt,
            _    => TileTheme.Moss,
        };

        // ~15% chance: accent room one step deeper than the base — adds variety without chaos
        if (rng.Next(0, 100) < 15)
        {
            baseTheme = baseTheme switch
            {
                TileTheme.Grey  => TileTheme.Crypt,
                TileTheme.Crypt => TileTheme.Moss,
                TileTheme.Moss  => TileTheme.Crypt, // cycle back at deepest
                _               => baseTheme,
            };
        }

        return baseTheme;
    }

    /// <summary>
    /// Create a default starting player for new runs (no carry-forward).
    /// Stats and starting gear match the Python prototype (initialize_new_game.py).
    ///
    /// Starting gear: dagger (main hand), leather armor (chest), 1 healing potion (inventory).
    /// Unarmed damage 1-2 is overridden by equipped dagger (1-4) in CombatResolver.
    ///
    /// NOTE: IDs for starting gear items come from EntityFactory's internal counter. Build()
    /// reads _monsterFactory.EntityFactory.NextId after this method returns to initialize the
    /// EntityIdAllocator, so map-placed entities always start AFTER the last gear ID assigned here.
    ///
    /// TODO: Move starting gear config into entities.yaml player section so it's data-driven
    /// rather than hardcoded here. Low priority until the full item system is built out.
    /// </summary>
    private Entity CreateDefaultPlayer()
    {
        var player = new Entity(0, "Player", 0, 0, blocksMovement: true);
        player.Add(new Combat.Fighter(
            hp: 54,
            strength: 14,
            dexterity: 14,
            constitution: 14,
            accuracy: 3,
            evasion: 0,
            damageMin: 1,
            damageMax: 2)); // unarmed; dagger equipped below overrides this in CombatResolver

        // Starting equipment — from PoC initialize_new_game.py
        var equipment = new Combat.Equipment();
        player.Add(equipment);

        var dagger = _itemFactory.Create("dagger");
        if (dagger != null)
            equipment.SetSlot(Combat.EquipmentSlot.MainHand, dagger);

        var armor = _itemFactory.Create("leather_armor");
        if (armor != null)
            equipment.SetSlot(Combat.EquipmentSlot.Chest, armor);

        // Starting inventory: 1 healing potion + Wand of Portals (player's core traversal tool)
        var inventory = new Inventory();
        player.Add(inventory);
        var potion = _consumableFactory.Create("healing_potion");
        if (potion != null)
            inventory.Add(potion);

        // Wand of Portals: always granted at run start. Uses a deterministic dummy rng since
        // the wand is infinite — charge count doesn't matter. The wand is the player's core
        // traversal ability and is never absent from the starting loadout.
        if (_spellItemFactory != null)
        {
            var dummyRng = new SeededRandom(0);
            var portalWand = _spellItemFactory.CreateWand("wand_of_portals", dummyRng);
            if (portalWand != null)
                inventory.Add(portalWand);
        }

        return player;
    }
}
