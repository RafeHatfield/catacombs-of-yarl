using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Map;
using Godot;

using CatacombsOfYarl.Presentation;

namespace CatacombsOfYarl.Presentation.Entities;

/// <summary>
/// Manages floor sprites for items sitting on dungeon tiles.
///
/// Sprite selection:
///   - Looks up item entity name in SpriteMapping.GetItemSpritePath() first.
///   - Falls back to a tinted selection diamond placeholder if no sprite found.
///
/// Items are FOV-gated — only shown when their tile is currently visible.
/// Call RemoveItem when the player picks up an item to free its sprite node.
/// </summary>
public sealed class ItemSpriteManager
{
    private const string FallbackTilePath = "res://src/Presentation/assets/tiles/iso/iso_dun_selectA.png";

    private readonly Node2D _parent;
    private readonly Dictionary<int, Sprite2D> _sprites = new();

    public ItemSpriteManager(Node2D itemLayerNode)
    {
        _parent = itemLayerNode;
    }

    /// <summary>Number of live item floor sprites. Useful for debug overlay.</summary>
    public int SpriteCount => _sprites.Count;

    /// <summary>
    /// Create sprites for all floor items in the game state.
    /// Call once when a floor is loaded.
    /// </summary>
    public void Initialize(GameState state)
    {
        foreach (var item in state.FloorItems)
            CreateSprite(item);
    }

    /// <summary>
    /// Apply FOV visibility to item sprites. Call after each turn's FOV recompute.
    /// </summary>
    public void UpdateVisibility(GameState state)
    {
        foreach (var (itemId, sprite) in _sprites)
        {
            var item = state.FloorItems.FirstOrDefault(i => i.Id == itemId);
            sprite.Visible = item != null && state.Map.IsVisible(item.X, item.Y);
        }
    }

    /// <summary>Remove the sprite for a picked-up item.</summary>
    public void RemoveItem(int itemId)
    {
        if (_sprites.Remove(itemId, out var sprite))
            sprite.SafeFree();
    }

    public void CreateSprite(Entity item)
    {
        // Try item-specific sprite first, fall back to tinted placeholder
        string? itemPath = SpriteMapping.GetItemSpritePath(item.Name.ToLowerInvariant().Replace(' ', '_'));
        Texture2D? texture = null;
        bool usingFallback = false;

        if (itemPath != null)
            texture = GD.Load<Texture2D>(itemPath);

        if (texture == null)
        {
            texture = GD.Load<Texture2D>(FallbackTilePath);
            usingFallback = true;
            if (texture == null)
            {
                GD.PrintErr($"ItemSpriteManager: no texture found for item '{item.Name}'");
                return;
            }
        }

        // Sprites are 48×48; tile bounding box is 32×48.
        // GridToScreenCenter = tile top-left + (16, 24) = horizontal center, vertical center.
        // Centered=true + no offset → sprite center at tile center → perfect alignment.
        var screenPos = IsometricMapper.GridToScreenCenter(item.X, item.Y);

        var sprite = new Sprite2D
        {
            Texture = texture,
            Position = screenPos,
            Centered = true,
            ZIndex = IsometricMapper.GetSortOrder(item.X, item.Y) + 1,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
            Modulate = usingFallback ? FallbackTint(item) : Colors.White,
            Visible = false, // Hidden until FOV reveals tile
        };

        _parent.AddChild(sprite);
        _sprites[item.Id] = sprite;
    }

    /// <summary>
    /// Fallback tint for the selection diamond placeholder.
    /// Green = consumable, gold = weapon, blue = armor, white = unknown.
    /// </summary>
    private static Color FallbackTint(Entity item)
    {
        if (item.Get<Consumable>() != null)
            return new Color(0.2f, 0.9f, 0.2f);

        var equippable = item.Get<Equippable>();
        if (equippable != null)
            return equippable.IsWeapon
                ? new Color(0.9f, 0.7f, 0.1f)
                : new Color(0.4f, 0.6f, 1.0f);

        return Colors.White;
    }
}
