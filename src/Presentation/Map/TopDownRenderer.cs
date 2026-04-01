using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Top-down 2D coordinate renderer. Working coordinate math, no tile assets yet.
///
/// Tile size is 48×48 (UF terrain native size). Grid coordinates map directly to
/// screen pixels: GridToScreen(x, y) = (x*48, y*48). Z-order is row-major.
///
/// Phase 1: math stub only. Booting with this renderer will fail at DungeonRenderer
/// because top-down tile assets (td_* prefix) don't exist yet. That is expected.
/// Phase 2 adds the tile assets and wires DungeonRenderer to use them.
///
/// Zoom defaults are initial guesses — calibrated visually in Phase 2 TASK-007.
/// </summary>
public sealed class TopDownRenderer : IMapRenderer
{
    public int TileWidth  => 48;
    public int TileHeight => 48;

    // Initial zoom guesses for 48×48 tiles on a mobile screen.
    // These will be calibrated in Phase 2 once top-down tile assets exist.
    public float DefaultZoom => 2.5f;
    public float MinZoom     => 1.0f;
    public float MaxZoom     => 5.0f;

    /// <summary>Screen position of tile top-left corner. Simple grid multiplication.</summary>
    public Vector2 GridToScreen(int gridX, int gridY)
        => new Vector2(gridX * TileWidth, gridY * TileHeight);

    /// <summary>Screen position of tile center — offset by half tile size in each axis.</summary>
    public Vector2 GridToScreenCenter(int gridX, int gridY)
    {
        var topLeft = GridToScreen(gridX, gridY);
        return new Vector2(topLeft.X + TileWidth / 2f, topLeft.Y + TileHeight / 2f);
    }

    /// <summary>
    /// Convert screen position to nearest grid coordinate.
    /// Inverse of GridToScreen: divide by tile size and round.
    /// ScreenToGrid(GridToScreenCenter(x, y)) == (x, y) for all valid positions.
    /// </summary>
    public (int gridX, int gridY) ScreenToGrid(Vector2 screenPos)
    {
        int gridX = (int)Mathf.Round((screenPos.X - TileWidth  / 2f) / TileWidth);
        int gridY = (int)Mathf.Round((screenPos.Y - TileHeight / 2f) / TileHeight);
        return (gridX, gridY);
    }

    /// <summary>Z-index for tiles. Row-major — higher Y sorts in front. Even values.</summary>
    public int GetTileSortOrder(int gridX, int gridY)
        => gridY * 2;

    /// <summary>Z-index for entities. Odd — always in front of tiles at the same row.</summary>
    public int GetEntitySortOrder(int gridX, int gridY)
        => gridY * 2 + 1;
}
