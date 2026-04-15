using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Data class representing the tile theme configuration loaded from config/tile_themes.yaml.
///
/// Maps theme names to Oryx 16bf world tile IDs (24x24px). Provides deterministic
/// tile selection methods that DungeonRenderer calls instead of its old hardcoded
/// switch statements.
///
/// Tile variation is always deterministic by position — same (x, y) always resolves
/// to the same tile. This keeps the dungeon visually stable across re-renders.
///
/// Note: This covers dungeon tiles only (floors, walls, stairs, decorations).
/// Entity and item sprites belong to TilesetConfig, not here.
/// </summary>
public sealed class TileThemeConfig
{
    /// <summary>
    /// res:// root path for world tile images.
    /// e.g. "res://src/Presentation/assets/sprites_16bf/world_24x24"
    /// </summary>
    public string TileRoot { get; set; } = "";

    /// <summary>
    /// Filename template with {id} placeholder.
    /// e.g. "oryx_16bit_fantasy_world_{id}.png"
    /// </summary>
    public string TilePattern { get; set; } = "";

    /// <summary>
    /// Name of the fallback theme to use when a requested theme is not defined.
    /// </summary>
    public string DefaultTheme { get; set; } = "sandstone";

    /// <summary>
    /// Map of theme name → per-role tile ID lists.
    /// Roles: floor_primary, floor_accent, wall_autotile (bitmask dict),
    ///        stair_down, stair_up, bones.
    /// </summary>
    public Dictionary<string, TileThemeData> Themes { get; set; } = new();

    // -------------------------------------------------------------------------
    // Path resolution
    // -------------------------------------------------------------------------

    /// <summary>
    /// Convert a tile ID integer to a full res:// texture path.
    /// e.g. 1091 → "res://.../oryx_16bit_fantasy_world_1091.png"
    /// </summary>
    public string GetTexturePath(int tileId)
        => $"{TileRoot}/{TilePattern.Replace("{id}", tileId.ToString())}";

    // -------------------------------------------------------------------------
    // Theme-aware tile selection — deterministic by position
    // -------------------------------------------------------------------------

    /// <summary>
    /// Return a floor texture path for the given theme and position.
    /// 85% primary, 15% accent (random accent chosen deterministically).
    /// Falls back to default_theme if the requested theme is missing.
    /// Returns null if no floor tiles are configured (logs a warning).
    /// </summary>
    public string? GetFloorTile(string theme, int x, int y)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;

        if (data.FloorPrimary.Count == 0)
        {
            GD.PrintErr($"[TileThemeConfig] Theme '{theme}' has no floor_primary tiles.");
            return null;
        }

        int hash = PositionHash(x, y);
        bool useAccent = data.FloorAccent.Count > 0 && (hash % 20) < 3; // 15%

        int tileId = useAccent
            ? data.FloorAccent[hash % data.FloorAccent.Count]
            : data.FloorPrimary[hash % data.FloorPrimary.Count];

        return GetTexturePath(tileId);
    }

    /// <summary>
    /// Return a dark floor tile path for wall-adjacent edge shadowing.
    /// Falls back to GetFloorTile if FloorDark is empty.
    /// </summary>
    public string? GetFloorDark(string theme, int x, int y)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;
        if (data.FloorDark.Count == 0) return GetFloorTile(theme, x, y);
        int hash = PositionHash(x, y);
        int tileId = data.FloorDark[hash % data.FloorDark.Count];
        return GetTexturePath(tileId);
    }

    /// <summary>
    /// Return an accent floor tile path for noise-driven variation clusters.
    /// Falls back to GetFloorTile if FloorAccent is empty.
    /// </summary>
    public string? GetFloorAccent(string theme, int x, int y)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;
        if (data.FloorAccent.Count == 0) return GetFloorTile(theme, x, y);
        int hash = PositionHash(x, y);
        int tileId = data.FloorAccent[hash % data.FloorAccent.Count];
        return GetTexturePath(tileId);
    }

    /// <summary>
    /// Return a worn floor tile path for high-traffic path appearance.
    /// Falls back to GetFloorTile if FloorWorn is empty.
    /// </summary>
    public string? GetFloorWorn(string theme, int x, int y)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;
        if (data.FloorWorn.Count == 0) return GetFloorTile(theme, x, y);
        int hash = PositionHash(x, y);
        int tileId = data.FloorWorn[hash % data.FloorWorn.Count];
        return GetTexturePath(tileId);
    }

    /// <summary>
    /// Return a wall texture path for the given theme using the hybrid cardinal+diagonal
    /// autotile algorithm.
    ///
    /// Algorithm:
    ///   1. cardinalMask 0–14: look up WallAutotile[cardinalMask] directly.
    ///   2. cardinalMask == 15 AND diagonalFloorMask > 0: check diagonal bits for outer corners.
    ///      The diagonal mask encodes which diagonal neighbors are floor (walkable):
    ///        bit3(8) = NE diagonal is floor → this wall is SW outer corner
    ///        bit2(4) = NW diagonal is floor → this wall is SE outer corner
    ///        bit1(2) = SE diagonal is floor → this wall is NW outer corner
    ///        bit0(1) = SW diagonal is floor → this wall is NE outer corner
    ///      Priority when multiple bits set: NW > NE > SW > SE.
    ///   3. cardinalMask == 15 AND diagonalFloorMask == 0: interior fill.
    ///
    /// Falls back gracefully if WallDiagonal is empty or a key is missing.
    /// Falls back to default_theme if the theme itself is missing.
    /// Returns null only if the theme AND default are both unconfigured.
    /// </summary>
    public string? GetWallTile(string theme, int cardinalMask, int diagonalFloorMask)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;

        if (data.WallAutotile.Count == 0)
        {
            GD.PrintErr($"[TileThemeConfig] Theme '{theme}' has no wall_autotile entries.");
            return null;
        }

        // For cardinal mask < 15, the autotile table is authoritative.
        if (cardinalMask < 15)
        {
            if (!data.WallAutotile.TryGetValue(cardinalMask, out int tileId))
            {
                // Missing entry — fall back to interior fill (mask 15).
                if (!data.WallAutotile.TryGetValue(15, out tileId))
                {
                    GD.PrintErr($"[TileThemeConfig] Theme '{theme}' missing bitmask {cardinalMask} and fallback 15.");
                    return null;
                }
            }
            return GetTexturePath(tileId);
        }

        // cardinalMask == 15: all four cardinal neighbors are walls.
        // Check diagonal floor bits to determine if this is an outer corner or true interior.
        if (diagonalFloorMask > 0 && data.WallDiagonal.Count > 0)
        {
            // Priority: NW outer corner > NE outer corner > SW outer corner > SE outer corner.
            // A diagonal floor in direction D means THIS tile is the outer corner facing D.
            // bit1(2) = SE diagonal is floor → this wall is NW outer corner
            if ((diagonalFloorMask & 2) != 0 && data.WallDiagonal.TryGetValue("corner_outer_nw", out int nwId))
                return GetTexturePath(nwId);
            // bit0(1) = SW diagonal is floor → this wall is NE outer corner
            if ((diagonalFloorMask & 1) != 0 && data.WallDiagonal.TryGetValue("corner_outer_ne", out int neId))
                return GetTexturePath(neId);
            // bit3(8) = NE diagonal is floor → this wall is SW outer corner
            if ((diagonalFloorMask & 8) != 0 && data.WallDiagonal.TryGetValue("corner_outer_sw", out int swId))
                return GetTexturePath(swId);
            // bit2(4) = NW diagonal is floor → this wall is SE outer corner
            if ((diagonalFloorMask & 4) != 0 && data.WallDiagonal.TryGetValue("corner_outer_se", out int seId))
                return GetTexturePath(seId);
        }

        // No diagonal floor, or WallDiagonal not configured: interior fill.
        if (data.WallDiagonal.TryGetValue("interior_fill", out int fillId))
            return GetTexturePath(fillId);

        // Final fallback: autotile mask 15 entry.
        if (data.WallAutotile.TryGetValue(15, out int autofillId))
            return GetTexturePath(autofillId);

        GD.PrintErr($"[TileThemeConfig] Theme '{theme}' has no interior_fill or mask-15 fallback.");
        return null;
    }

    /// <summary>
    /// Backwards-compatible wall tile lookup using only the 4-bit cardinal bitmask.
    /// Delegates to GetWallTile with diagonalFloorMask=0 (no diagonal discrimination).
    /// Use GetWallTile directly when the renderer has diagonal information available.
    /// </summary>
    public string? GetAutoWallTile(string theme, int bitmask)
        => GetWallTile(theme, bitmask, 0);

    /// <summary>
    /// Return the stair-down texture path for the given theme.
    /// Falls back to default_theme if missing. Returns null if unconfigured.
    /// </summary>
    public string? GetStairDown(string theme)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;

        if (data.StairDown.Count == 0)
        {
            GD.PrintErr($"[TileThemeConfig] Theme '{theme}' has no stair_down tiles.");
            return null;
        }

        return GetTexturePath(data.StairDown[0]);
    }

    /// <summary>
    /// Return the stair-up texture path for the given theme.
    /// Falls back to default_theme if missing. Returns null if unconfigured.
    /// </summary>
    public string? GetStairUp(string theme)
    {
        var data = ResolveTheme(theme);
        if (data == null) return null;

        if (data.StairUp.Count == 0)
        {
            GD.PrintErr($"[TileThemeConfig] Theme '{theme}' has no stair_up tiles.");
            return null;
        }

        return GetTexturePath(data.StairUp[0]);
    }

    /// <summary>
    /// Return a bones decoration texture path for the given theme and position,
    /// or null if the position doesn't receive a bones overlay (~2.5% chance).
    ///
    /// Deterministic by position — the same tile always either has bones or doesn't,
    /// and always uses the same bones variant. Purely atmospheric.
    /// </summary>
    public string? GetBones(string theme, int x, int y)
    {
        var data = ResolveTheme(theme);
        if (data == null || data.Bones.Count == 0) return null;

        int hash = PositionHash(x, y);
        // ~2.5%: 1 in 40
        if (hash % 40 != 0) return null;

        int tileId = data.Bones[hash % data.Bones.Count];
        return GetTexturePath(tileId);
    }

    // -------------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------------

    /// <summary>
    /// Resolve a theme name to its data, falling back to DefaultTheme if missing.
    /// Returns null and logs an error if even the default theme is missing.
    /// </summary>
    private TileThemeData? ResolveTheme(string theme)
    {
        if (Themes.TryGetValue(theme, out var data))
            return data;

        // Theme not found — fall back to the configured default
        if (theme != DefaultTheme)
        {
            GD.PrintErr($"[TileThemeConfig] Theme '{theme}' not found — falling back to '{DefaultTheme}'.");
            if (Themes.TryGetValue(DefaultTheme, out var fallback))
                return fallback;
        }

        GD.PrintErr($"[TileThemeConfig] Default theme '{DefaultTheme}' not found. Check tile_themes.yaml.");
        return null;
    }

    /// <summary>
    /// Deterministic position hash for tile variation.
    /// Same (x, y) always produces the same hash — dungeon looks stable across re-renders.
    /// </summary>
    private static int PositionHash(int x, int y)
        => Math.Abs((x * 7919 + y * 104729) & 0x7FFFFFFF);
}

/// <summary>
/// Per-theme tile ID lists for each dungeon surface role.
/// All lists may be empty if a role is not configured for this theme.
///
/// WallAutotile maps 4-bit cardinal bitmask (0–15) → tile ID.
/// WallDiagonal maps named corner roles → tile ID for outer corner detection
/// when all four cardinal neighbors are walls (mask 15).
/// </summary>
public sealed class TileThemeData
{
    public List<int> FloorPrimary  { get; set; } = new();
    public List<int> FloorAccent   { get; set; } = new();

    /// <summary>
    /// Wall-adjacent dark floor tiles (distance 1 from a wall).
    /// Provides the edge-darkening effect in the floor composition pipeline.
    /// Optional — floor decoration pipeline uses these when present.
    /// </summary>
    public List<int> FloorDark     { get; set; } = new();

    /// <summary>
    /// Deep interior floor tiles (distance 2+ from any wall).
    /// Provides subtle variation for large open room centers.
    /// Optional — floor decoration pipeline uses these when present.
    /// </summary>
    public List<int> FloorInterior { get; set; } = new();

    /// <summary>
    /// Worn floor tiles for high-traffic paths (noise-driven variation cluster).
    /// Provides a subtle "walked over" look to central corridors and room paths.
    /// Optional — floor decoration pipeline uses these when present.
    /// </summary>
    public List<int> FloorWorn     { get; set; } = new();

    /// <summary>
    /// 4-bit cardinal bitmask → tile ID for connected wall autotiling.
    /// Keys 0–15, where the bitmask encodes cardinal wall neighbors:
    /// bit3(8)=North, bit2(4)=South, bit1(2)=East, bit0(1)=West.
    /// </summary>
    public Dictionary<int, int> WallAutotile { get; set; } = new();

    /// <summary>
    /// Named outer corner and interior fill tile IDs.
    /// Used when cardinalMask==15 to distinguish outer corners from true interior.
    /// Keys: corner_outer_nw, corner_outer_ne, corner_outer_sw, corner_outer_se, interior_fill.
    /// </summary>
    public Dictionary<string, int> WallDiagonal { get; set; } = new();

    public List<int> StairDown     { get; set; } = new();
    public List<int> StairUp       { get; set; } = new();
    public List<int> Bones         { get; set; } = new();
}
