using CatacombsOfYarl.Logic.ECS;
using Godot;

using CatacombsOfYarl.Presentation;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Holds references to all tile sprite nodes created by DungeonRenderer.Render.
/// Used by UpdateVisibility to apply fog-of-war modulation each turn without
/// re-creating nodes. Key is grid position (X, Y).
/// </summary>
public sealed class TileLayer
{
    public Dictionary<(int X, int Y), Node2D> TileSprites { get; } = new();

    /// <summary>
    /// Base tile keys where the floor type is Dark (wall-adjacent shadow tiles).
    /// UpdateVisibility applies a slightly dimmed, cool-tinted modulate to these
    /// sprites when visible, giving rooms natural shadow depth near walls without
    /// requiring a separate tile asset.
    /// Only contains base tile keys (x, y) — never offset bones overlay keys.
    /// </summary>
    public HashSet<(int X, int Y)> DarkTileKeys { get; } = new();
}

/// <summary>
/// Renders a GameMap as tile sprites. Creates Sprite2D nodes for each
/// floor and wall tile under the TileMapLayer node.
///
/// Renders back-to-front (by grid row/column sum) for correct depth sorting.
/// Floor tiles get random variation seeded by position for visual interest.
///
/// Second pass: overlays stair sprites on top of floor tiles where TileKind.StairDown
/// is set. This only applies to dungeon-generated maps — scenario maps use CreateArena
/// and never set StairDown tile kinds.
///
/// Tile textures are sourced entirely from TileThemeConfig (loaded from tile_themes.yaml).
/// No tile paths are hardcoded here — the renderer is content-agnostic.
/// </summary>
public sealed class DungeonRenderer
{
    /// <summary>
    /// Render the entire GameMap as tile sprites under the given parent node.
    /// Pass 1: floor/wall tiles for every cell.
    /// Pass 2: stair overlays on top of StairDown/StairUp cells.
    /// Pass 3: bones decorations on ~2.5% of room floor tiles.
    ///
    /// Returns a TileLayer containing references to all base tile sprites so that
    /// UpdateVisibility can apply fog-of-war modulation each turn.
    ///
    /// If themeConfig is null, logs an error and returns an empty TileLayer without crashing.
    /// </summary>
    public static TileLayer Render(GameMap map, Node2D parent, IMapRenderer? renderer = null, TileThemeConfig? themeConfig = null, int seed = 0)
    {
        if (themeConfig == null)
        {
            GD.PrintErr("[DungeonRenderer] No TileThemeConfig provided — dungeon floor will not render.");
            return new TileLayer();
        }

        // Use provided renderer, or fall back to TopDownRenderer as the active default.
        renderer ??= new TopDownRenderer();
        var tileLayer = new TileLayer();

        // Pre-compute floor tile types for the entire map.
        // FloorComposer runs the multi-pass pipeline: edge darkening + noise variation.
        // This is computed once here and referenced in Pass 1 and Pass 3.
        var floorMap = FloorComposer.Compose(map, seed);

        // Clear any existing tiles
        foreach (var child in parent.GetChildren())
        {
            child.SafeFree();
        }

        // Pass 1: floor and wall base tiles
        for (int gy = 0; gy < map.Height; gy++)
        {
            for (int gx = 0; gx < map.Width; gx++)
            {
                bool walkable = map.IsWalkable(gx, gy);
                var screenPos = renderer.GridToScreen(gx, gy);

                var tileTheme = map.GetTileTheme(gx, gy);
                string themeName = ThemeToConfigName(tileTheme);

                string? tilePath;
                bool isDarkFloor = false;
                if (walkable)
                {
                    // Use FloorComposer variant to select the appropriate tile type.
                    // Dark and Accent variants fall back to GetFloorTile when their lists are empty
                    // (both currently point to the same tile 774). DarkTileKeys is populated here
                    // so UpdateVisibility can apply programmatic shadow modulation instead.
                    var tileType = floorMap.TryGetValue((gx, gy), out var ft) ? ft : FloorTileType.Standard;
                    isDarkFloor = tileType == FloorTileType.Dark;
                    tilePath = tileType switch
                    {
                        FloorTileType.Dark   => themeConfig.GetFloorDark(themeName, gx, gy),
                        FloorTileType.Accent => themeConfig.GetFloorAccent(themeName, gx, gy),
                        FloorTileType.Worn   => themeConfig.GetFloorWorn(themeName, gx, gy),
                        _                    => themeConfig.GetFloorTile(themeName, gx, gy),
                    };
                    // Belt-and-suspenders fallback in case a variant returns null
                    tilePath ??= themeConfig.GetFloorTile(themeName, gx, gy);
                }
                else
                {
                    var (cardinal, diagonal) = ComputeWallMasks(map, gx, gy);

                    // Collapse three-wall masks to two-wall edges. Thick walls (2+ tiles
                    // deep) cause room edge tiles to have wall mass behind them, producing
                    // masks 7/11 (horizontal edge + wall behind) and 13/14 (vertical edge
                    // + wall behind). These should render as simple edges (masks 3 and 12),
                    // not T-junctions. The T-junction tiles stay in the YAML for future use
                    // when thin walls or actual corridor junctions need them.
                    cardinal = cardinal switch
                    {
                        7  => 3,  // S+E+W walls, floor N → horizontal edge (E+W walls)
                        11 => 3,  // N+E+W walls, floor S → horizontal edge (E+W walls)
                        13 => 12, // N+S+W walls, floor E → vertical edge (N+S walls)
                        14 => 12, // N+S+E walls, floor W → vertical edge (N+S walls)
                        _  => cardinal,
                    };

                    tilePath = themeConfig.GetWallTile(themeName, cardinal, diagonal);
                }

                if (tilePath == null)
                {
                    GD.PrintErr($"[DungeonRenderer] No tile path for {(walkable ? "floor" : "wall")} at ({gx},{gy}) theme='{themeName}'");
                    continue;
                }

                var texture = GD.Load<Texture2D>(tilePath);
                if (texture == null)
                {
                    GD.PrintErr($"[DungeonRenderer] Missing tile texture: {tilePath}");
                    continue;
                }

                var sprite = new Sprite2D
                {
                    Texture = texture,
                    Position = screenPos,
                    Centered = false, // Position is top-left of tile image
                    ZIndex = renderer.GetTileSortOrder(gx, gy),
                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                };

                parent.AddChild(sprite);
                // Track in TileLayer so UpdateVisibility can modulate this sprite
                tileLayer.TileSprites[(gx, gy)] = sprite;
                if (isDarkFloor) tileLayer.DarkTileKeys.Add((gx, gy));
            }
        }

        // Pass 2: stair overlays — placed on top of the floor tile at the same screen position.
        // Only StairDown and StairUp get overlays; corridors/regular floors need nothing extra.
        // Skip silently if the texture file is missing — never crash.
        // Stair overlays are NOT added to tileLayer — they share visibility with their base tile
        // and are handled separately in UpdateVisibility via the stair overlay list.
        for (int gy = 0; gy < map.Height; gy++)
        {
            for (int gx = 0; gx < map.Width; gx++)
            {
                var kind = map.GetTileKind(gx, gy);
                var tileTheme = map.GetTileTheme(gx, gy);
                string themeName = ThemeToConfigName(tileTheme);

                string? overlayPath = kind switch
                {
                    TileKind.StairDown => themeConfig.GetStairDown(themeName),
                    TileKind.StairUp   => themeConfig.GetStairUp(themeName),
                    _                  => null,
                };

                if (overlayPath == null) continue;

                var overlayTexture = ResourceLoader.Load<Texture2D>(overlayPath);
                if (overlayTexture == null)
                {
                    // Asset missing — skip silently rather than crashing.
                    // The floor tile still renders; the stair is just invisible.
                    GD.PrintErr($"[DungeonRenderer] Missing stair overlay texture: {overlayPath} — skipping.");
                    continue;
                }

                var screenPos = renderer.GridToScreen(gx, gy);

                var overlay = new Sprite2D
                {
                    Texture = overlayTexture,
                    Position = screenPos,
                    Centered = false,
                    // +1 above the floor tile (even) at this grid position — same band as entities, which is fine
                    ZIndex = renderer.GetTileSortOrder(gx, gy) + 1,
                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                };

                parent.AddChild(overlay);
                // Stair overlays share a grid cell with the floor tile below them.
                // We store them under a unique key by offsetting into a parallel entry.
                // This lets UpdateVisibility find and modulate them alongside the base tile.
                // Key: (gx | StairOverlayFlag, gy) won't collide with base tiles.
                // Simpler approach: use the same key suffixed into a separate stair overlay dict.
                // For Phase 2, stair cells are always visible (they're on the path to the exit).
                // We don't track overlays in tileLayer — they are always shown when the base tile
                // at (gx, gy) is shown. Visibility is controlled via the base tile only.
                // The overlay is a child of parent and will be hidden by the scene tree if needed.
                // TODO Phase 3: if fine-grained overlay visibility is needed, add a stair overlay dict.
            }
        }

        // Pass 3: decorative details — bones on room floors (not corridors, not walls).
        // ~2.5% of room tiles get a bones overlay (controlled inside TileThemeConfig.GetBones).
        // Purely atmospheric, never gameplay-affecting.
        // Overlays are tracked in tileLayer with an offset key so UpdateVisibility auto-modulates them.
        for (int gy = 0; gy < map.Height; gy++)
        {
            for (int gx = 0; gx < map.Width; gx++)
            {
                if (!map.IsWalkable(gx, gy)) continue;
                var boneTheme = map.GetTileTheme(gx, gy);
                if (boneTheme == TileTheme.Dirt) continue; // Corridors don't get bones
                // Skip bones on Dark (wall-adjacent) tiles — shadows belong to the walls,
                // not decoration. Bones look odd crammed against wall edges anyway.
                if (floorMap.TryGetValue((gx, gy), out var boneFloorType) && boneFloorType == FloorTileType.Dark) continue;

                string themeName = ThemeToConfigName(boneTheme);
                string? bonesPath = themeConfig.GetBones(themeName, gx, gy);
                if (bonesPath == null) continue; // ~97.5% of tiles — no bones

                var bonesTexture = ResourceLoader.Load<Texture2D>(bonesPath);
                if (bonesTexture == null) continue; // Skip silently if asset missing

                var screenPos = renderer.GridToScreen(gx, gy);
                var overlay = new Sprite2D
                {
                    Texture = bonesTexture,
                    Position = screenPos,
                    Centered = false,
                    // Bones are floor decoration — stay in tile band, above plain floor tile
                    ZIndex = renderer.GetTileSortOrder(gx, gy) + 1,
                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                    Modulate = new Color(1f, 1f, 1f, 0.7f), // slightly transparent — subtle
                };
                parent.AddChild(overlay);
                // Store under offset key (gx, gy + Height) — no collision with base tiles at (gx, gy).
                // UpdateVisibility iterates all TileSprites entries, so these get FOV modulation for free.
                tileLayer.TileSprites[(gx, gy + map.Height)] = overlay;
            }
        }

        return tileLayer;
    }

    /// <summary>
    /// Apply fog-of-war visibility to all tile sprites based on current map state.
    /// Call after each turn completes (both player and monster turns resolve).
    ///
    /// Three states:
    ///   Visible     — full brightness; Dark floor tiles get a shadowed modulate
    ///   Explored    — dimmed blue-grey (previously seen, currently not in FOV)
    ///   Unexplored  — hidden entirely
    ///
    /// Dark floor tiles (wall-adjacent) stay slightly dimmed even when visible —
    /// the shadow modulate is applied via programmatic color rather than a separate asset.
    ///
    /// Bones overlays (offset key y >= map.Height) preserve their 0.7 alpha at all
    /// visible/explored states so they remain subtle rather than fully opaque.
    /// </summary>
    public static void UpdateVisibility(TileLayer layer, GameMap map)
    {
        foreach (var ((x, y), sprite) in layer.TileSprites)
        {
            // Bones overlays are stored under offset key (gx, gy + map.Height) to avoid
            // colliding with base tile keys. Resolve the actual grid position before lookup.
            bool isBoneOverlay = y >= map.Height;
            int realX = x;
            int realY = isBoneOverlay ? y - map.Height : y;

            if (map.IsVisible(realX, realY))
            {
                sprite.Visible = true;
                if (isBoneOverlay)
                    sprite.Modulate = new Color(1f, 1f, 1f, 0.7f);        // bones: restore subtle alpha
                else if (layer.DarkTileKeys.Contains((x, y)))
                    sprite.Modulate = DarkFloorModulate;                   // wall-shadow darkening
                else
                    sprite.Modulate = Colors.White;
            }
            else if (map.IsExplored(realX, realY))
            {
                sprite.Visible = true;
                // Bones overlays keep their 0.7 alpha in explored state too
                sprite.Modulate = isBoneOverlay
                    ? new Color(0.4f, 0.4f, 0.5f, 0.7f)
                    : new Color(0.4f, 0.4f, 0.5f);
            }
            else
            {
                sprite.Visible = false; // never seen — hidden
            }
        }
    }

    // Programmatic shadow modulate for wall-adjacent Dark floor tiles when visible.
    // 70% brightness with a slight blue shift — gives rooms natural depth near walls
    // without requiring a separate tile asset.
    private static readonly Color DarkFloorModulate = new(0.70f, 0.70f, 0.78f);

    /// <summary>
    /// Map the TileTheme enum value to the YAML config theme key.
    ///
    /// All themes currently map to "sandstone" — the TMX-verified tile set from Phase 0.
    /// Additional themes (crypt, moss, dirt) will diverge once their tile IDs are verified
    /// and added to tile_themes.yaml in a later phase.
    /// </summary>
    private static string ThemeToConfigName(TileTheme theme) => theme switch
    {
        TileTheme.Grey  => "sandstone",
        TileTheme.Crypt => "sandstone", // Fallback until crypt tile IDs are verified
        TileTheme.Moss  => "sandstone", // Fallback until moss tile IDs are verified
        TileTheme.Dirt  => "sandstone", // Fallback until dirt theme tile IDs are verified
        _               => "sandstone",
    };

    /// <summary>
    /// Compute the cardinal and diagonal wall masks for autotile selection at (x, y).
    ///
    /// Cardinal mask (0–15): each bit encodes whether the corresponding cardinal
    /// neighbor is a wall (non-walkable or out-of-bounds — border = solid wall):
    ///   bit3 (8) = North (y-1)
    ///   bit2 (4) = South (y+1)
    ///   bit1 (2) = East  (x+1)
    ///   bit0 (1) = West  (x-1)
    ///
    /// Diagonal mask (0–15): only computed when cardinalMask == 15 (all four cardinal
    /// neighbors are walls). Each bit encodes whether a diagonal neighbor IS FLOOR
    /// (walkable). A diagonal floor means this wall tile is an outer corner facing
    /// that diagonal direction:
    ///   bit3 (8) = NE diagonal is floor
    ///   bit2 (4) = NW diagonal is floor
    ///   bit1 (2) = SE diagonal is floor
    ///   bit0 (1) = SW diagonal is floor
    ///
    /// IsWalkable returns false for out-of-bounds, so map borders resolve as wall.
    /// </summary>
    private static (int Cardinal, int Diagonal) ComputeWallMasks(GameMap map, int x, int y)
    {
        int cardinal = 0;
        if (!map.IsWalkable(x,     y - 1)) cardinal |= 8; // North
        if (!map.IsWalkable(x,     y + 1)) cardinal |= 4; // South
        if (!map.IsWalkable(x + 1, y    )) cardinal |= 2; // East
        if (!map.IsWalkable(x - 1, y    )) cardinal |= 1; // West

        // Only check diagonals when all cardinal neighbors are walls.
        // If any cardinal is floor, this can't be an outer corner — skip diagonal work.
        int diagonal = 0;
        if (cardinal == 15)
        {
            if (map.IsWalkable(x + 1, y - 1)) diagonal |= 8; // NE is floor
            if (map.IsWalkable(x - 1, y - 1)) diagonal |= 4; // NW is floor
            if (map.IsWalkable(x + 1, y + 1)) diagonal |= 2; // SE is floor
            if (map.IsWalkable(x - 1, y + 1)) diagonal |= 1; // SW is floor
        }

        return (cardinal, diagonal);
    }
}
