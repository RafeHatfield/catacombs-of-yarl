using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Map;
using Godot;

using CatacombsOfYarl.Presentation;

namespace CatacombsOfYarl.Presentation.Entities;

/// <summary>
/// Manages Sprite2D nodes for game entities. Creates sprites on game start,
/// updates positions each turn, removes sprites when entities die.
///
/// Characters use native 48x48 Oryx sprites, bottom-center aligned to the
/// iso tile diamond center (Option A from art direction).
/// </summary>
public sealed class EntitySpriteManager
{
    private readonly Node2D _parent;
    private readonly Dictionary<int, Sprite2D> _sprites = new();
    // Cached grid positions — avoids O(n) monster scan in UpdateVisibility each turn.
    private readonly Dictionary<int, (int X, int Y)> _positions = new();

    public EntitySpriteManager(Node2D entityLayerNode)
    {
        _parent = entityLayerNode;
    }

    /// <summary>Number of live entity sprites (player + monsters). Useful for debug overlay.</summary>
    public int SpriteCount => _sprites.Count;

    /// <summary>
    /// Create sprites for all entities in the game state.
    /// Call once at game start.
    /// </summary>
    public void Initialize(GameState state)
    {
        // Player sprite
        CreateSprite(state.Player, SpriteMapping.PlayerSprite);

        // Monster sprites — need to map entity name back to type ID
        // For now, infer from entity name (the content system sets these)
        foreach (var monster in state.Monsters)
        {
            string spriteBase = InferSpriteBase(monster);
            CreateSprite(monster, spriteBase);
        }
    }

    /// <summary>
    /// Update all sprite positions to match current entity positions.
    /// Call after each turn is processed.
    /// </summary>
    public void UpdatePositions(GameState state)
    {
        UpdateSpritePosition(state.Player);
        foreach (var monster in state.Monsters)
        {
            if (monster.Require<Fighter>().IsAlive)
                UpdateSpritePosition(monster);
        }
    }

    /// <summary>
    /// Apply fog-of-war visibility to entity sprites.
    /// Uses the cached position dictionary — O(sprites) not O(sprites × monsters).
    /// </summary>
    public void UpdateVisibility(GameState state)
    {
        foreach (var (entityId, sprite) in _sprites)
        {
            if (!_positions.TryGetValue(entityId, out var pos))
            {
                sprite.Visible = false;
                continue;
            }
            sprite.Visible = state.Map.IsVisible(pos.X, pos.Y);
        }
    }

    /// <summary>
    /// Remove the sprite for a dead entity (fade or instant).
    /// </summary>
    public void RemoveEntity(int entityId)
    {
        if (_sprites.Remove(entityId, out var sprite))
        {
            sprite.SafeFree();
            _positions.Remove(entityId);
        }
    }

    /// <summary>
    /// Get the sprite for an entity, if it exists.
    /// </summary>
    public Sprite2D? GetSprite(int entityId)
    {
        return _sprites.GetValueOrDefault(entityId);
    }

    private void CreateSprite(Entity entity, string spriteBase)
    {
        string framePath = SpriteMapping.GetFramePath(spriteBase, 1); // Frame 1 = idle
        var texture = GD.Load<Texture2D>(framePath);
        if (texture == null)
        {
            GD.PrintErr($"Missing sprite: {framePath}");
            return;
        }

        var screenPos = IsometricMapper.GridToScreenCenter(entity.X, entity.Y);

        var sprite = new Sprite2D
        {
            Texture = texture,
            Position = screenPos,
            Centered = true,
            Offset = new Vector2(0, -texture.GetHeight() * 0.15f),
            ZIndex = IsometricMapper.GetSortOrder(entity.X, entity.Y) + 1,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
        };

        _parent.AddChild(sprite);
        _sprites[entity.Id] = sprite;
        _positions[entity.Id] = (entity.X, entity.Y);
    }

    private void UpdateSpritePosition(Entity entity)
    {
        if (!_sprites.TryGetValue(entity.Id, out var sprite))
            return;

        sprite.Position = IsometricMapper.GridToScreenCenter(entity.X, entity.Y);
        sprite.ZIndex = IsometricMapper.GetSortOrder(entity.X, entity.Y) + 1;
        _positions[entity.Id] = (entity.X, entity.Y);
    }

    /// <summary>
    /// Infer sprite base name from entity. Tries SpriteMapping first,
    /// falls back to a default.
    /// </summary>
    private static string InferSpriteBase(Entity monster)
    {
        // Try common monster type names
        string nameLower = monster.Name.ToLowerInvariant();

        // Check known mappings
        foreach (var typeId in new[] { "orc_grunt", "orc_brute", "zombie" })
        {
            if (nameLower.Contains(typeId.Replace("_", " ")) ||
                nameLower.Contains(typeId.Replace("_", "")))
            {
                var spriteBase = SpriteMapping.GetSpriteBase(typeId);
                if (spriteBase != null) return spriteBase;
            }
        }

        // Fallback heuristics based on common names
        if (nameLower.Contains("orc") && (nameLower.Contains("brute") || nameLower.Contains("warrior")))
            return SpriteMapping.GetSpriteBase("orc_brute") ?? "goblin_warrior";
        if (nameLower.Contains("orc"))
            return SpriteMapping.GetSpriteBase("orc_grunt") ?? "goblin";
        if (nameLower.Contains("zombie"))
            return SpriteMapping.GetSpriteBase("zombie") ?? "zombie_a";

        // Default to goblin
        return "goblin";
    }
}
