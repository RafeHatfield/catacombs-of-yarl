using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Top-down 2D coordinate renderer using Oryx 16bf world tiles (24x24px).
///
/// Tile size is 24x24 (16bf world tile native size). Grid coordinates map directly
/// to screen pixels: GridToScreen(x, y) = (x*24, y*24). Z-order is row-major.
///
/// At DefaultZoom 3.0 on a 720px-wide viewport, approximately 10 tiles are visible
/// horizontally — matching Shattered Pixel Dungeon's density target.
///
/// Zoom range (1.5–6.0) prevents the 24px tiles from becoming unreadably small
/// at min zoom while allowing close pixel-art inspection at max zoom.
/// </summary>
public sealed class TopDownRenderer : IMapRenderer
{
    public int TileWidth  => 24;
    public int TileHeight => 24;

    // Calibrated for 24x24 (16bf world) tiles on a 720x1280 mobile viewport.
    // DefaultZoom 3.0 gives ~10 tiles wide x ~14 tall — same density as Shattered PD.
    // MinZoom 1.5 keeps individual tiles recognizable when zoomed out.
    // MaxZoom 6.0 lets players inspect pixel art detail.
    public float DefaultZoom => 3.0f;
    public float MinZoom     => 1.5f;
    public float MaxZoom     => 6.0f;

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
