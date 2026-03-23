namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Maps entity type IDs (from YAML content) to Oryx sprite base names.
/// Sprites are at res://src/Presentation/assets/sprites/heroes/{base}_{frame}.png
/// where frame is 1-4 for animation.
/// </summary>
public static class SpriteMapping
{
    private static readonly Dictionary<string, string> MonsterToSprite = new()
    {
        ["orc_grunt"] = "goblin",
        ["orc_brute"] = "goblin_warrior",
        ["zombie"] = "zombie_a",
    };

    public const string PlayerSprite = "knight";
    public const int FrameCount = 4;
    public const string SpritePath = "res://src/Presentation/assets/sprites/heroes";

    /// <summary>
    /// Get the sprite base name for a monster type ID.
    /// Returns null if no mapping exists.
    /// </summary>
    public static string? GetSpriteBase(string monsterTypeId)
    {
        return MonsterToSprite.GetValueOrDefault(monsterTypeId);
    }

    /// <summary>
    /// Get the full resource path for a sprite frame.
    /// Frame is 1-based (1-4).
    /// </summary>
    public static string GetFramePath(string spriteBase, int frame)
    {
        return $"{SpritePath}/{spriteBase}_{frame}.png";
    }
}
