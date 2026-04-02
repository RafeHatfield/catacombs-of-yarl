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
/// Sprite selection priority:
///   1. ItemTag.TypeId → SpriteMapping.GetItemSpritePath() (primary path)
///   2. item.Name.ToLower().Replace(' ', '_') → SpriteMapping (legacy fallback, GD.PrintErr fires)
///   3. Tinted selection diamond placeholder if neither lookup finds a sprite.
///
/// Items are FOV-gated — only shown when their tile is currently visible.
/// Call RemoveItem when the player picks up an item to free its sprite node.
/// </summary>
public sealed class ItemSpriteManager
{
    private const string FallbackTilePath = "res://src/Presentation/assets/tiles/iso/iso_dun_selectA.png";

    private readonly Node2D _parent;
    private readonly SpriteMapping _spriteMapping;
    private readonly IMapRenderer _renderer;
    private readonly Dictionary<int, Sprite2D> _sprites = new();

    /// <summary>
    /// Cached reference to the current game state. Used by ResolveItemSpritePath to look up
    /// identification state when creating sprites. Updated on Initialize() and when sprites
    /// are refreshed after identification events.
    /// </summary>
    private GameState? _lastState;

    public ItemSpriteManager(Node2D itemLayerNode, SpriteMapping spriteMapping, IMapRenderer renderer)
    {
        _parent = itemLayerNode;
        _spriteMapping = spriteMapping;
        _renderer = renderer;
    }

    /// <summary>Number of live item floor sprites. Useful for debug overlay.</summary>
    public int SpriteCount => _sprites.Count;

    /// <summary>
    /// Create sprites for all floor items in the game state.
    /// Call once when a floor is loaded.
    /// </summary>
    public void Initialize(GameState state)
    {
        _lastState = state;
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
        string? itemPath = ResolveItemSpritePath(item);
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
        var screenPos = _renderer.GridToScreenCenter(item.X, item.Y);

        var sprite = new Sprite2D
        {
            Texture = texture,
            Position = screenPos,
            Centered = true,
            // Items sit on the floor — above the tile but below standing entities
            ZIndex = _renderer.GetTileSortOrder(item.X, item.Y) + 1,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
            Modulate = usingFallback ? FallbackTint(item) : Colors.White,
            Visible = false, // Hidden until FOV reveals tile
        };

        _parent.AddChild(sprite);
        _sprites[item.Id] = sprite;
    }

    /// <summary>
    /// Resolve the sprite resource path for an item entity.
    ///
    /// Identification-aware: unidentified potions use black bottle sprites, unidentified wands
    /// use the plain wand sprite, unidentified scrolls use the rune scroll sprite, and
    /// unidentified rings use material sprites (cycling 76-80).
    ///
    /// Primary: ItemTag.TypeId → mystery sprite (unidentified) or true sprite (identified).
    /// Fallback: name-based key derivation for items without ItemTag.
    /// </summary>
    private string? ResolveItemSpritePath(Entity item, GameState? state = null)
    {
        var registry = state?.IdentificationRegistry;
        var pool     = state?.AppearancePool;

        // Use ItemDisplay helper which handles identification state
        var spriteKey = ItemDisplay.GetSpriteKey(item, registry, pool);
        var path = _spriteMapping.GetItemSpritePath(spriteKey);

        // If mystery sprite key doesn't resolve (tileset might not have it), fall back to TypeId
        if (path == null)
        {
            var tag = item.Get<ItemTag>();
            if (tag != null)
                path = _spriteMapping.GetItemSpritePath(tag.TypeId);
        }

        if (path == null)
        {
            GD.PrintErr($"[ItemSpriteManager] Item '{item.Name}' (id={item.Id}) has no sprite — check tileset YAML.");
        }

        return path;
    }

    /// <summary>Legacy overload used by CreateSprite (called before state is always available).</summary>
    private string? ResolveItemSpritePath(Entity item)
        => ResolveItemSpritePath(item, _lastState);

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
