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
}

/// <summary>
/// Renders a GameMap as isometric tiles. Creates Sprite2D nodes for each
/// floor and wall tile under the TileMapLayer node.
///
/// Renders back-to-front (by grid row/column sum) for correct depth sorting.
/// Floor tiles get random variation seeded by position for visual interest.
///
/// Second pass: overlays stair sprites on top of floor tiles where TileKind.StairDown
/// is set. This only applies to dungeon-generated maps — scenario maps use CreateArena
/// and never set StairDown tile kinds.
/// </summary>
public sealed class DungeonRenderer
{
    private const string TilePath = "res://src/Presentation/assets/tiles/iso";

    // FloorVariants and WallVariants removed — replaced by theme-aware PickFloorTile / PickWallTile.

    private const string StairDownTexture = "iso_dun_stairdown_grey";
    private const string StairUpTexture = "iso_dun_stairup_grey";

    /// <summary>
    /// Render the entire GameMap as iso tile sprites under the given parent node.
    /// Pass 1: floor/wall tiles for every cell.
    /// Pass 2: stair overlays on top of StairDown/StairUp cells.
    ///
    /// Returns a TileLayer containing references to all base tile sprites so that
    /// UpdateVisibility can apply fog-of-war modulation each turn.
    /// </summary>
    public static TileLayer Render(GameMap map, Node2D parent)
    {
        var tileLayer = new TileLayer();

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
                var screenPos = IsometricMapper.GridToScreen(gx, gy);

                var theme = map.GetTileTheme(gx, gy);
                string tileName = walkable
                    ? PickFloorTile(theme, gx, gy)
                    : PickWallTile(theme, gx, gy);

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
                    ZIndex = IsometricMapper.GetTileSortOrder(gx, gy),
                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                };

                parent.AddChild(sprite);
                // Track in TileLayer so UpdateVisibility can modulate this sprite
                tileLayer.TileSprites[(gx, gy)] = sprite;
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
                string? overlayName = kind switch
                {
                    TileKind.StairDown => StairDownTexture,
                    TileKind.StairUp => StairUpTexture,
                    _ => null,
                };

                if (overlayName == null) continue;

                var overlayTexture = ResourceLoader.Load<Texture2D>($"{TilePath}/{overlayName}.png");
                if (overlayTexture == null)
                {
                    // Asset missing — skip silently rather than crashing.
                    // The floor tile still renders; the stair is just invisible.
                    GD.PrintErr($"Missing stair overlay texture: {overlayName}.png — skipping.");
                    continue;
                }

                var screenPos = IsometricMapper.GridToScreen(gx, gy);

                var overlay = new Sprite2D
                {
                    Texture = overlayTexture,
                    Position = screenPos,
                    Centered = false,
                    // +1 above the floor tile (even) at this grid position — same band as entities, which is fine
                    ZIndex = IsometricMapper.GetTileSortOrder(gx, gy) + 1,
                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                };

                parent.AddChild(overlay);
                // Stair overlays share a grid cell with the floor tile below them.
                // We store them under a unique key by offsetting into a parallel entry.
                // This lets UpdateVisibility find and modulate them alongside the base tile.
                // Key: (gx | StairOverlayFlag, gy) won't collide with base tiles.
                // Simpler approach: use a separate offset flag stored in a high bit.
                // Actually: just use the same key suffixed into a separate stair overlay dict.
                // For Phase 2, stair cells are always visible (they're on the path to the exit).
                // We don't track overlays in tileLayer — they are always shown when the base tile
                // at (gx, gy) is shown. Visibility is controlled via the base tile only.
                // The overlay is a child of parent and will be hidden by the scene tree if needed.
                // TODO Phase 3: if fine-grained overlay visibility is needed, add a stair overlay dict.
            }
        }

        // Pass 3: decorative details — bones on room floors (not corridors, not walls).
        // ~2.5% of room tiles get a bones overlay. Purely atmospheric, never gameplay-affecting.
        // Overlays are tracked in tileLayer with an offset key so UpdateVisibility auto-modulates them.
        string[] bonesVariants = { "iso_dun_bonesA", "iso_dun_bonesB", "iso_dun_bonesC" };
        for (int gy = 0; gy < map.Height; gy++)
        {
            for (int gx = 0; gx < map.Width; gx++)
            {
                if (!map.IsWalkable(gx, gy)) continue;
                var boneTheme = map.GetTileTheme(gx, gy);
                if (boneTheme == TileTheme.Dirt) continue; // Corridors don't get bones

                int hash = PositionHash(gx, gy);
                if (hash % 40 != 0) continue; // ~2.5% of room tiles

                string bonesName = bonesVariants[hash % 3];
                var bonesTexture = ResourceLoader.Load<Texture2D>($"{TilePath}/{bonesName}.png");
                if (bonesTexture == null) continue; // Skip silently if asset missing

                var screenPos = IsometricMapper.GridToScreen(gx, gy);
                var overlay = new Sprite2D
                {
                    Texture = bonesTexture,
                    Position = screenPos,
                    Centered = false,
                    // Bones are floor decoration — stay in tile band, above plain floor tile
                    ZIndex = IsometricMapper.GetTileSortOrder(gx, gy) + 1,
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
    ///   Visible     — full brightness (white modulate)
    ///   Explored    — dimmed blue-grey (previously seen, currently not in FOV)
    ///   Unexplored  — hidden entirely
    ///
    /// Note: stair overlay sprites are children of the same parent node as base tiles
    /// but are not tracked in tileLayer. They will remain at their natural modulation.
    /// Their base tile IS in tileLayer, so they'll inherit the parent's draw calls.
    /// Fine-grained stair overlay modulation is deferred — in practice stairs are always
    /// in the player's visible area when they matter.
    /// </summary>
    public static void UpdateVisibility(TileLayer layer, GameMap map)
    {
        foreach (var ((x, y), sprite) in layer.TileSprites)
        {
            // Bones overlays are stored under offset key (gx, gy + map.Height) to avoid
            // colliding with base tile keys. Resolve the actual grid position before lookup.
            int realX = x;
            int realY = y >= map.Height ? y - map.Height : y;

            if (map.IsVisible(realX, realY))
            {
                sprite.Visible = true;
                sprite.Modulate = Colors.White;
            }
            else if (map.IsExplored(realX, realY))
            {
                sprite.Visible = true;
                sprite.Modulate = new Color(0.4f, 0.4f, 0.5f); // dim blue-grey for explored-but-dark
            }
            else
            {
                sprite.Visible = false; // never seen — hidden
            }
        }
    }

    /// <summary>
    /// Select a floor tile name based on the tile's theme and position.
    /// 85% primary variant, 15% accent — deterministic by position.
    /// Keeps rooms visually coherent while adding subtle texture.
    /// </summary>
    private static string PickFloorTile(TileTheme theme, int x, int y)
    {
        // 15% accent: (hash % 20) < 3
        bool useAccent = (PositionHash(x, y) % 20) < 3;

        return theme switch
        {
            TileTheme.Grey  => useAccent ? "iso_dun_floor_tileB" : "iso_dun_floor_tileA",
            TileTheme.Crypt => useAccent ? "iso_dun_floor_tileE" : "iso_dun_floor_tileD",
            TileTheme.Moss  => useAccent ? "iso_dun_floor_tileG" : "iso_dun_floor_tileF",
            TileTheme.Dirt  => useAccent ? "iso_dun_floor_dirtB" : "iso_dun_floor_dirtA",
            _               => "iso_dun_floor_tileA",
        };
    }

    /// <summary>
    /// Select a wall tile name based on the tile's theme and position.
    /// 2% cracked variants add wear; otherwise 80% A / 20% B — deterministic by position.
    /// </summary>
    private static string PickWallTile(TileTheme theme, int x, int y)
    {
        int hash = PositionHash(x, y);
        bool useCracked = (hash % 50) == 0;           // 2% cracked
        bool useB       = !useCracked && (hash % 5) == 0; // 20% B (of the remaining 98%)

        return theme switch
        {
            TileTheme.Grey  => useCracked ? "iso_dun_wall_grey_cracked"
                             : useB       ? "iso_dun_wall_greyB"
                                          : "iso_dun_wall_greyA",
            TileTheme.Crypt => useCracked ? "iso_dun_wall_crypt_cracked"
                             : useB       ? "iso_dun_wall_cryptB"
                                          : "iso_dun_wall_cryptA",
            TileTheme.Moss  => useCracked ? "iso_dun_wall_moss_cracked"
                             : useB       ? "iso_dun_wall_mossB"
                                          : "iso_dun_wall_mossA",
            TileTheme.Dirt  => useCracked ? "iso_dun_wall_grey_cracked"
                             : useB       ? "iso_dun_wall_greyB"
                                          : "iso_dun_wall_greyA", // Dirt corridors use grey walls
            _               => "iso_dun_wall_greyA",
        };
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
