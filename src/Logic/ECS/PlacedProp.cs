namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// A prop that has been placed in a generated dungeon room.
/// Immutable snapshot: position and display info resolved at generation time.
/// </summary>
public sealed record PlacedProp(
    string PropId,        // References props.yaml definition (e.g. "barrel", "bookshelf")
    int X,                // Grid position (top-left of footprint)
    int Y,
    int FootprintW,       // Tile footprint width (1 for 1x1, 3 for 3x1, etc.)
    int FootprintH,       // Tile footprint height (1 for 1x1, 3 for 1x3, etc.)
    bool BlocksMovement,  // True for furniture; false for floor overlays (puddles, grates)
    int TileId,           // Anchor tile ID — used for 1x1 props and as the [0] tile for multi-tile
    int? OverlayTileId = null,              // Second tile rendered on top at same cell (e.g. brazier flame)
    IReadOnlyList<int>? TileLayout = null,  // For multi-tile props: flat row-major list of tile IDs
                                            // (FootprintW * FootprintH entries). Null = use TileId only.
    bool FlipH = false    // Mirror the sprite horizontally. Applied to 1x1 props only (flippable tag).
);
