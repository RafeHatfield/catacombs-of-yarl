using System.Text.Json;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Builds the Tier 0 review corridor — a lit corridor with a junction, assembled from
/// authored data and rendered through the production renderer (SetupPresentation →
/// DungeonRenderer.Render), per ART-BIBLE-v0 §13.1: a candidate is judged in the lit scene
/// at true display size, never from a contact sheet.
///
/// Sibling of <see cref="ReviewSceneBuilder"/>, which seats prop candidates in an open room.
/// This builder exists because Tier 1 is floors and walls, and floors and walls are judged by
/// walking a corridor — specifically by the junction. The critic is asked which way they would
/// walk; a straight corridor cannot answer that, so the junction is load-bearing, not decoration.
///
/// Geometry is authored as a list of axis-aligned rectangles carved out of solid rock. That is
/// deliberately general: a T-junction, a crossroads, and a dogleg are all just different carve
/// lists, so the shape of the junction is a data decision at review time rather than a code
/// change here.
///
/// NOTHING in this class hard-codes a tile dimension, canvas size, or palette value. Which
/// pixels a tile ID resolves to is decided entirely by the tile-theme config the Presentation
/// layer is pointed at (--tile-theme-config), which is how candidate tiles and the §6.4 probe
/// arms enter without any file being overwritten. ART-BIBLE-v0 §4.3 marks canvas and tile sizes
/// PLACEHOLDER; this builder therefore never names one.
///
/// JSON schema:
/// {
///   "name":   string,                                  // recorded in the capture log
///   "width":  int, "height": int,                      // map extent, in tiles
///   "player": { "x": int, "y": int },                  // where the carried light is anchored
///   "carve":  [ { "x0":int,"y0":int,"x1":int,"y1":int } ... ]   // inclusive rects, floor
/// }
/// </summary>
public static class CorridorReviewSceneBuilder
{
    /// <summary>Parsed geometry, exposed so tests can assert the junction without Godot.</summary>
    public readonly record struct Spec(
        string Name, int Width, int Height, int PlayerX, int PlayerY,
        IReadOnlyList<(int X0, int Y0, int X1, int Y1)> Carve);

    public static Spec ParseSpec(string roundJsonPath)
        => ParseSpecJson(System.IO.File.ReadAllText(roundJsonPath));

    public static Spec ParseSpecJson(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        string name = root.TryGetProperty("name", out var n) ? (n.GetString() ?? "") : "";
        int w = root.GetProperty("width").GetInt32();
        int h = root.GetProperty("height").GetInt32();

        var playerEl = root.GetProperty("player");
        int px = playerEl.GetProperty("x").GetInt32();
        int py = playerEl.GetProperty("y").GetInt32();

        var carve = new List<(int, int, int, int)>();
        foreach (var r in root.GetProperty("carve").EnumerateArray())
        {
            carve.Add((r.GetProperty("x0").GetInt32(), r.GetProperty("y0").GetInt32(),
                       r.GetProperty("x1").GetInt32(), r.GetProperty("y1").GetInt32()));
        }

        if (w <= 2 || h <= 2)
            throw new InvalidOperationException($"Corridor spec '{name}': map must be at least 3x3, got {w}x{h}.");
        if (carve.Count == 0)
            throw new InvalidOperationException($"Corridor spec '{name}': carve list is empty — that is solid rock, not a corridor.");

        return new Spec(name, w, h, px, py, carve);
    }

    /// <summary>
    /// True when the carved geometry contains a genuine CORRIDOR junction: a walkable cell with
    /// three or more walkable orthogonal neighbours AND all four diagonals solid.
    ///
    /// The diagonal condition is not fussiness, it is the whole test. Without it, a corridor
    /// carved three tiles wide reports a junction at its very first cell — every cell in an open
    /// area has three or more open neighbours — and the scene silently stops posing the question
    /// it exists to pose. That is not hypothetical: the first Tier 0 capture carved a 3-wide
    /// trunk and this check duly reported "junction=YES at (8,4)", which was the top of a
    /// straight corridor. At a clean T or + junction of one-wide corridors the diagonals are all
    /// wall, and in any widened area at least one is not.
    ///
    /// Checked at build time and reported in the capture log, because a spec that quietly
    /// degrades to a straight corridor cannot answer "which way would you walk" and nothing else
    /// in the pipeline would notice.
    /// </summary>
    public static bool HasJunction(GameMap map, out (int X, int Y) at)
    {
        for (int y = 0; y < map.Height; y++)
        {
            for (int x = 0; x < map.Width; x++)
            {
                if (!map.IsWalkable(x, y)) continue;

                int open = 0;
                if (map.IsWalkable(x + 1, y)) open++;
                if (map.IsWalkable(x - 1, y)) open++;
                if (map.IsWalkable(x, y + 1)) open++;
                if (map.IsWalkable(x, y - 1)) open++;
                if (open < 3) continue;

                bool diagonalsSolid = !map.IsWalkable(x - 1, y - 1) && !map.IsWalkable(x + 1, y - 1)
                                   && !map.IsWalkable(x - 1, y + 1) && !map.IsWalkable(x + 1, y + 1);
                if (!diagonalsSolid) continue;

                at = (x, y);
                return true;
            }
        }
        at = (-1, -1);
        return false;
    }

    public static GameState Build(string roundJsonPath) => Build(ParseSpec(roundJsonPath));

    public static GameState Build(Spec spec)
    {
        var map = new GameMap(spec.Width, spec.Height, allWalls: true);

        foreach (var (x0, y0, x1, y1) in spec.Carve)
        {
            // Clamp to a 1-tile solid border so the corridor is always enclosed by wall —
            // an unenclosed corridor would show the void, not a wall candidate.
            int cx0 = Math.Max(1, Math.Min(x0, x1));
            int cx1 = Math.Min(spec.Width  - 2, Math.Max(x0, x1));
            int cy0 = Math.Max(1, Math.Min(y0, y1));
            int cy1 = Math.Min(spec.Height - 2, Math.Max(y0, y1));
            for (int x = cx0; x <= cx1; x++)
                for (int y = cy0; y <= cy1; y++)
                    map.SetTile(x, y, TileKind.Floor);
        }

        map.SetTileThemeRect(0, 0, spec.Width - 1, spec.Height - 1, TileTheme.Grey);

        var player = new Entity(0, "Player", spec.PlayerX, spec.PlayerY, blocksMovement: true);
        player.Add(new Fighter(hp: 54, strength: 12, dexterity: 14, constitution: 12,
                               accuracy: 2, evasion: 1, damageMin: 1, damageMax: 4));
        player.Add(new SpeedBonusTracker(baseRatio: 0.25));
        map.RegisterEntity(player);

        // RevealAll, deliberately: fog-of-war is a gameplay-information system and this scene is
        // a lighting instrument. Darkness in this capture must come from the engine light rig
        // (§6.1), not from FOV dimming — otherwise the "lighting is live" control could be
        // satisfied by fog and the harness would be measuring the wrong thing.
        map.RevealAll();

        return new GameState(player, new List<Entity>(), map, new SeededRandom(0), turnLimit: 1)
        {
            IsDungeonMode = true,
            CurrentDepth  = 1,
            Props         = new List<PlacedProp>(),
        };
    }
}
