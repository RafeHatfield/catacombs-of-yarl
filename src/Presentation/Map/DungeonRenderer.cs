using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Renders a GameMap as isometric tiles. Creates Sprite2D nodes for each
/// floor and wall tile under the TileMapLayer node.
///
/// Renders back-to-front (by grid row/column sum) for correct depth sorting.
/// Floor tiles get random variation seeded by position for visual interest.
/// </summary>
public sealed class DungeonRenderer
{
    private const string TilePath = "res://src/Presentation/assets/tiles/iso";

    private static readonly string[] FloorVariants = { "tileA", "tileB", "tileC", "tileD", "tileE", "tileF", "tileG" };
    private static readonly string[] WallVariants = { "greyA", "greyB", "greyC", "greyD", "greyE", "greyF", "greyG" };

    /// <summary>
    /// Render the entire GameMap as iso tile sprites under the given parent node.
    /// </summary>
    public static void Render(GameMap map, Node2D parent)
    {
        // Clear any existing tiles
        foreach (var child in parent.GetChildren())
        {
            child.QueueFree();
        }

        // Render in sorted order for correct depth
        for (int gy = 0; gy < map.Height; gy++)
        {
            for (int gx = 0; gx < map.Width; gx++)
            {
                bool walkable = map.IsWalkable(gx, gy);
                var screenPos = IsometricMapper.GridToScreen(gx, gy);

                string tileName;
                if (!walkable)
                {
                    // Wall tile — vary by position
                    int variantIdx = PositionHash(gx, gy) % WallVariants.Length;
                    tileName = $"iso_dun_wall_{WallVariants[variantIdx]}";
                }
                else
                {
                    // Floor tile — vary by position
                    int variantIdx = PositionHash(gx, gy) % FloorVariants.Length;
                    tileName = $"iso_dun_floor_{FloorVariants[variantIdx]}";
                }

                var texture = GD.Load<Texture2D>($"{TilePath}/{tileName}.png");
                if (texture == null)
                {
                    GD.PrintErr($"Missing tile texture: {tileName}");
                    continue;
                }

                var sprite = new Sprite2D
                {
                    Texture = texture,
                    Position = screenPos,
                    Centered = false, // Position is top-left of tile image
                    ZIndex = IsometricMapper.GetSortOrder(gx, gy),
                };

                parent.AddChild(sprite);
            }
        }
    }

    /// <summary>
    /// Simple deterministic hash for tile variation. Same position always gets same variant.
    /// </summary>
    private static int PositionHash(int x, int y)
    {
        // Simple hash that spreads well for small grids
        return Math.Abs((x * 7919 + y * 6271) ^ (x * 31 + y * 37));
    }
}
