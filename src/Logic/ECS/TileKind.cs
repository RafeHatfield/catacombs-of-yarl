namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Semantic tile type for dungeon generation. Determines walkability and rendering hints.
/// Wall, Floor, and Corridor are the core generation types; others are placed by EntityPlacer.
/// </summary>
public enum TileKind
{
    Wall,
    Floor,
    Corridor,
    StairDown,
    StairUp,
    Door,
    Trap,
}
