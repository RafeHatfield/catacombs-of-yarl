using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Converts between grid coordinates (from GameMap) and isometric screen positions.
/// Oryx iso tiles are 32x48 pixels. The diamond footprint occupies the lower portion.
///
/// Iso coordinate system:
///   screenX = (gridX - gridY) * HalfTileWidth
///   screenY = (gridX + gridY) * HalfTileHeight
///
/// The tile's visual center (diamond midpoint) is offset from its top-left corner.
/// </summary>
public static class IsometricMapper
{
    public const int TileWidth = 32;
    public const int TileHeight = 48;
    public const int HalfTileWidth = TileWidth / 2;   // 16
    public const int HalfTileHeight = TileHeight / 4;  // 12 — iso step height

    /// <summary>
    /// Convert grid position to screen position (top-left of tile image).
    /// </summary>
    public static Vector2 GridToScreen(int gridX, int gridY)
    {
        float screenX = (gridX - gridY) * HalfTileWidth;
        float screenY = (gridX + gridY) * HalfTileHeight;
        return new Vector2(screenX, screenY);
    }

    /// <summary>
    /// Convert grid position to the center of the tile's diamond footprint.
    /// Used for placing characters — they stand at the diamond center.
    /// </summary>
    public static Vector2 GridToScreenCenter(int gridX, int gridY)
    {
        var topLeft = GridToScreen(gridX, gridY);
        return new Vector2(topLeft.X + HalfTileWidth, topLeft.Y + TileHeight * 0.5f);
    }

    /// <summary>
    /// Convert screen position to the nearest grid coordinate.
    /// Inverse of GridToScreen. Used for tap-to-target.
    /// </summary>
    public static (int gridX, int gridY) ScreenToGrid(Vector2 screenPos)
    {
        // Adjust for the visual diamond center within the 32x48 tile.
        // The diamond midpoint sits at (HalfTileWidth, TileHeight * 0.75f) from tile origin,
        // so subtract that offset before inverting.
        float adjustedX = screenPos.X - HalfTileWidth;
        float adjustedY = screenPos.Y - TileHeight * 0.75f;

        float sum = adjustedY / HalfTileHeight;   // gx + gy
        float diff = adjustedX / HalfTileWidth;    // gx - gy
        float gx = (sum + diff) / 2f;
        float gy = (sum - diff) / 2f;
        return ((int)Mathf.Round(gx), (int)Mathf.Round(gy));
    }

    /// <summary>
    /// Get the Z-index for a tile (floor, wall) at the given grid position.
    /// Even values — tiles always sort behind entities at the same depth.
    /// </summary>
    public static int GetTileSortOrder(int gridX, int gridY)
        => (gridX + gridY) * 2;

    /// <summary>
    /// Get the Z-index for an entity (player, monster) at the given grid position.
    /// Odd values — entities always sort in front of tiles at the same depth.
    /// Guarantees that a wall tile at (x,y) never renders on top of an entity standing
    /// on the tile directly in front of it (same gridX+gridY sum).
    /// </summary>
    public static int GetEntitySortOrder(int gridX, int gridY)
        => (gridX + gridY) * 2 + 1;

    /// <summary>
    /// Get the Z-index for depth sorting. Higher gridX + gridY = drawn later (in front).
    /// Kept for backwards compatibility — use GetTileSortOrder / GetEntitySortOrder where possible.
    /// </summary>
    public static int GetSortOrder(int gridX, int gridY)
        => GetTileSortOrder(gridX, gridY);
}
