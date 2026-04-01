using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Combat.StatusEffects;
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
/// Sprite lookup priority (entity sprites):
///   1. SpeciesTag.TypeId → SpriteMapping.GetSpriteBase() (primary path, all MonsterFactory entities)
///   2. Name-substring heuristics (fallback for hand-constructed test entities without SpeciesTag)
///
/// Player entity has no SpeciesTag — uses SpriteMapping.PlayerSprite directly.
///
/// Characters use native sprite size scaled to 48px equivalent, bottom-center aligned to the
/// iso tile diamond center (Option A from art direction).
/// </summary>
public sealed class EntitySpriteManager
{
    private const string FallbackSprite = "heroes/goblin";

    private readonly Node2D _parent;
    private readonly SpriteMapping _spriteMapping;
    private readonly Dictionary<int, Sprite2D> _sprites = new();
    // Cached grid positions — avoids O(n) monster scan in UpdateVisibility each turn.
    private readonly Dictionary<int, (int X, int Y)> _positions = new();

    public EntitySpriteManager(Node2D entityLayerNode, SpriteMapping spriteMapping)
    {
        _parent = entityLayerNode;
        _spriteMapping = spriteMapping;
    }

    /// <summary>Number of live entity sprites (player + monsters). Useful for debug overlay.</summary>
    public int SpriteCount => _sprites.Count;

    /// <summary>
    /// Create sprites for all entities in the game state.
    /// Call once at game start.
    /// </summary>
    public void Initialize(GameState state)
    {
        // Player entity has no SpeciesTag — use PlayerSprite from tileset config directly.
        CreateSprite(state.Player, _spriteMapping.PlayerSprite);

        foreach (var monster in state.Monsters)
        {
            CreateSprite(monster, InferSpriteBase(monster));
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
    /// Apply status effect tints to monster sprites for visual debuff feedback.
    /// Call after UpdateVisibility() so visibility state is already set.
    ///
    /// Priority (highest wins if multiple effects active):
    ///   poison → burning → disorientation → sleep → any other debuff → no tint
    ///
    /// Player sprite is intentionally excluded — the HUD StatusEffectBar covers that.
    /// </summary>
    public void UpdateStatusTints(GameState state)
    {
        foreach (var monster in state.Monsters)
        {
            if (!_sprites.TryGetValue(monster.Id, out var sprite)) continue;
            sprite.Modulate = ChooseStatusTint(monster);
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
    /// Create a sprite for a newly spawned monster (e.g. a slime spawned by split).
    /// Call after the child entity has been added to state.Monsters.
    /// </summary>
    public void SpawnMonster(Entity monster)
    {
        CreateSprite(monster, InferSpriteBase(monster));
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
        string framePath = _spriteMapping.GetFramePath(spriteBase, 1); // Frame 1 = idle
        var texture = GD.Load<Texture2D>(framePath);
        if (texture == null)
        {
            GD.PrintErr($"Missing sprite: {framePath}");
            return;
        }

        var screenPos = IsometricMapper.GridToScreenCenter(entity.X, entity.Y);

        // Scale compensation: UF sprites are 48px native; 16bf are 24px native.
        // Integer 2x upscaling on 16bf gives clean pixel art without blurring.
        // Scale = 48 / native_size so UF stays at 1.0, 16bf renders at 2.0.
        float scale = 48f / _spriteMapping.SpriteSize;

        // Y offset grounds entity feet on the tile surface. Positive = down, negative = up.
        // Tileset config may override via entity_y_offset; otherwise uses default formula.
        float offsetY = _spriteMapping.GetEntityYOffset(texture.GetHeight(), scale);

        var sprite = new Sprite2D
        {
            Texture = texture,
            Position = screenPos,
            Centered = true,
            Scale = new Vector2(scale, scale),
            Offset = new Vector2(0, offsetY),
            ZIndex = IsometricMapper.GetEntitySortOrder(entity.X, entity.Y),
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
        sprite.ZIndex = IsometricMapper.GetEntitySortOrder(entity.X, entity.Y);
        _positions[entity.Id] = (entity.X, entity.Y);
    }

    /// <summary>
    /// Resolve the sprite base for a monster entity.
    ///
    /// Primary path: SpeciesTag.TypeId → SpriteMapping lookup.
    /// All entities created by MonsterFactory have a SpeciesTag — this path covers 100%
    /// of normal gameplay cases.
    ///
    /// Fallback: name-substring heuristics from the old static SpriteMapping.
    /// Retained for hand-constructed test entities (e.g. in unit tests or debug scenarios)
    /// that may not have a SpeciesTag. A GD.PrintErr fires so gaps surface immediately.
    /// </summary>
    private string InferSpriteBase(Entity monster)
    {
        // Primary: use SpeciesTag for all factory-created monsters (the normal path)
        var tag = monster.Get<SpeciesTag>();
        if (tag != null)
        {
            var spriteBase = _spriteMapping.GetSpriteBase(tag.TypeId);
            if (spriteBase != null) return spriteBase;

            // TypeId exists but isn't in the tileset YAML — missing mapping, not a code bug.
            GD.PrintErr($"[EntitySpriteManager] No sprite mapping for species '{tag.TypeId}' in tileset '{_spriteMapping.SpriteSize}px' — using fallback.");
            return FallbackSprite;
        }

        // Fallback: name-substring heuristics for entities without SpeciesTag.
        // This path should never fire in production. If it does, something is wrong upstream.
        GD.PrintErr($"[EntitySpriteManager] Entity '{monster.Name}' (id={monster.Id}) has no SpeciesTag — using name heuristic fallback.");
        return InferSpriteBaseFromName(monster.Name);
    }

    /// <summary>
    /// Legacy name-substring sprite inference. Kept as a last resort for entities
    /// without SpeciesTag (hand-constructed test entities, debug scenarios).
    /// Never called for normal gameplay — MonsterFactory always adds SpeciesTag.
    /// </summary>
    private static string InferSpriteBaseFromName(string name)
    {
        string nameLower = name.ToLowerInvariant();

        if (nameLower.Contains("large slime") || nameLower == "large_slime")
            return "monsters/slime_red";
        if (nameLower.Contains("slime"))
            return "monsters/slime_green";

        if (nameLower.Contains("orc") && (nameLower.Contains("brute") || nameLower.Contains("warrior")))
            return "heroes/goblin_warrior";
        if (nameLower.Contains("orc grunt") || nameLower == "orc_grunt")
            return "heroes/goblin";
        if (nameLower.Contains("orc"))
            return "heroes/goblin";

        if (nameLower.Contains("zombie"))
            return "heroes/zombie_a";

        return FallbackSprite;
    }

    /// <summary>
    /// Select the sprite tint color based on active status effects.
    /// Priority: poison > burning > disorientation > sleep > any IStatusEffect debuff > normal.
    /// Returns Colors.White (no tint) when no effects are active.
    /// </summary>
    private static Color ChooseStatusTint(Entity entity)
    {
        if (entity.Has<PoisonEffect>())        return new Color(0.5f, 1f,   0.5f);  // green
        if (entity.Has<BurningEffect>())       return new Color(1f,   0.6f, 0.2f);  // orange
        if (entity.Has<DisorientationEffect>()) return new Color(0.8f, 0.5f, 1f);   // purple
        if (entity.Has<SleepEffect>())         return new Color(0.6f, 0.8f, 1f);    // light blue

        // Any remaining IStatusEffect debuff gets a subtle gray tint.
        bool hasAnyEffect = entity.GetAllComponents().OfType<IStatusEffect>().Any();
        if (hasAnyEffect) return new Color(0.8f, 0.8f, 0.8f);

        return Colors.White;
    }
}
