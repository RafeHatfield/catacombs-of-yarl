using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates feature entity instances (chests, signposts, murals) for dungeon floor placement.
///
/// Features differ from monsters: no Fighter, no AI, no ETP budget.
/// They block movement (BlocksMovement=true) and respond to bump-interaction in TurnController.
/// IDs come from the per-floor EntityIdAllocator to avoid collision with monsters and items.
/// </summary>
public static class FeatureFactory
{
    /// <summary>
    /// Create a chest entity at the given position.
    /// Chest starts closed. LootItemIds are resolved at floor-gen time for determinism.
    /// </summary>
    public static Entity CreateChest(int x, int y, EntityIdAllocator ids, List<string>? lootItemIds = null)
    {
        var entity = new Entity(ids.Next(), "Chest", x, y, blocksMovement: true);
        entity.Add(new ChestComponent
        {
            IsOpen = false,
            LootItemIds = lootItemIds ?? new List<string>(),
        });
        return entity;
    }

    /// <summary>
    /// Create a signpost entity at the given position.
    /// Message and signType are assigned at placement time from SignpostMessageRegistry.
    /// </summary>
    public static Entity CreateSignpost(int x, int y, EntityIdAllocator ids, string message, string signType)
    {
        var entity = new Entity(ids.Next(), "Signpost", x, y, blocksMovement: true);
        entity.Add(new SignpostComponent
        {
            Message = message,
            SignType = signType,
            HasBeenRead = false,
        });
        return entity;
    }

    /// <summary>
    /// Create a mural entity at the given position.
    /// Text and muralId come from MuralRegistry; tileId is the visual variant (4036-4038).
    /// Wall-adjacent placement is the caller's responsibility (EntityPlacer.PlaceFloorFeatures).
    /// </summary>
    public static Entity CreateMural(int x, int y, EntityIdAllocator ids, string text, string muralId, int tileId = 4036)
    {
        var entity = new Entity(ids.Next(), "Mural", x, y, blocksMovement: true);
        entity.Add(new MuralComponent
        {
            Text = text,
            MuralId = muralId,
            TileId = tileId,
            HasBeenExamined = false,
        });
        return entity;
    }
}
