using System.Text.Json;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Lays the COURSE-ALIGNED ASHLAR floor and paints its stones.
///
/// This does more than pick a texture, and the reason is a ruling. Assigning a stone's value from
/// anything the TILE knows puts that value on the tile lattice — the same value repeating wherever
/// the family pattern repeats — which is §8.3.1 arriving through value instead of through shape.
/// So the shipped asset is the BOND ONLY, and the material is painted here from each stone's
/// WORLD ADDRESS:
///
///     a stone spanning a vertical boundary is addressed by THAT BOUNDARY, which is the one piece
///     of data both tiles either side of it possess. Both compute the same key, so both paint the
///     same value onto the same stone, and the seam is zero rather than small.
///
/// Measured on the assembled field: 7.44x boundary-to-interior value step under the old geometry,
/// 2.95x after blending it, and 0.59x here — below 1.00, meaning a tile boundary is no longer
/// distinguishable from anywhere else on the floor.
///
/// WHY NO STONE MAY CONTAIN A GRID CORNER, which is what forces the coursing.
/// Four tiles meet at a grid corner. Tile (x,r) shares one boundary family with its eastern
/// neighbour and one with its southern, and shares NOTHING with its diagonal. So a stone covering
/// a corner cannot be addressed at all. A bed joint on every tile boundary puts one through every
/// corner and the problem does not arise. Measured: 0 unaddressable stones, against 27 of 77
/// (19.9% of stone pixels) under the crossing-joint geometry that preceded it.
///
/// The INTERIOR bed joint is not so constrained, and it moves per tile row. When it did not, every
/// course in the world was 16px tall and a blind seat read the floor as "a stack of horizontal
/// stripes before it reads as stone". Four course splits, chosen by row, give 5 distinct course
/// heights across a field where there was 1.
///
/// WHAT SHIPS
///   * 81 atlases, one per family combination, each a 6x6 of the four course splits by the nine
///     head-joint merge cases.
///     R is an INDEX INTO THE LADDER (exact — a byte of luminance would round, and a rounding
///     error lands as a value seam). G is the stone class, 0 for joints.
///   * one 512x512 grain bank, 64 patches, two scales packed into R and G.
///
/// ⚠ THE COMPOSER'S ARITHMETIC EXISTS TWICE, here and in `tools/tier1_floors/compose_ashlar.py`.
/// That is the copy-that-drifts hazard this project has been bitten by, and it is tolerated only
/// because BOTH HALVES ARE CHECKED: the manifest carries an edge-family vector and a stone-offset
/// vector, and <see cref="Apply"/> refuses to lay anything if this code fails to reproduce either.
/// A duplicate with an enforcement is a different thing from a duplicate with a comment
/// (LOOP-PROCESS §4.2).
/// </summary>
public static class Tier1AshlarFloor
{
    private const int T = 32;
    private const int Courses = 2;
    private const int AtlasCols = 6;
    private const int GrainSide = 2 * T;      // one patch
    private const int BankCols = 8;

    private sealed class Config
    {
        public int Families = 3;
        public int Seed;
        public int HorizSalt = 101, VertSalt = 202, SpanSalt = 3001, InteriorSalt = 3002;
        public int DropSalt = 3003, ClusterSalt = 3004, SplitSalt = 3005;
        public int[][] Splits = System.Array.Empty<int[]>();
        public int GrainBank = 64;
        public double GrainAmp = 1.0, Coarse = 0.34, Fine = 0.14, WornMul = 0.38;
        public double WearSpread = 0.20, WearArris = 0.45, LumMedian = 114.0;
        public int[] OffsetSteps = System.Array.Empty<int>();
        public int[] ClusterTable = { -1, 0, 0, 1 };
        public double[] Ladder = System.Array.Empty<double>();
        public double[] Tint = { 1, 1, 1 };
        public int[][] ATable = System.Array.Empty<int[]>();
        public int[][] MvTable = System.Array.Empty<int[]>();
        public readonly Dictionary<int, string> Atlas = new();
        public string GrainPath = "";
        public readonly List<(int X, int Y, int Salt, int Family)> EdgeCheck = new();
        public readonly List<(int X, int K, int Kind, int Drop, int Steps)> StoneCheck = new();
    }

    private static int Mix(int x, int y, int salt)
    {
        unchecked
        {
            int h = x * 7919 + y * 104729 + salt * 15485863;
            h ^= h >> 13;
            h *= 1274126177;
            h ^= h >> 16;
            return h & 0x7FFFFFFF;
        }
    }

    private static int EdgeFamily(int a, int b, int salt, int seed, int families)
        => Mix(a, b, salt + seed) % families;

    private static int TileIndex(int n, int e, int s, int w, int f)
        => ((n * f + e) * f + s) * f + w;

    /// <summary>0 keep both head joints, 1 sand the A joint away, 2 sand the MV joint away.</summary>
    private static int DropChoice(Config c, int tx, int courseK)
    {
        int d = Mix(tx, courseK, c.DropSalt + c.Seed) % 7;
        return d == 0 ? 1 : (d == 1 ? 2 : 0);
    }

    /// <summary>
    /// With the MV joint gone, the stone labelled `interior` is not interior any more: it runs on
    /// into the tile to the east and must be addressed by THAT boundary, or the two tiles paint it
    /// differently. This one line is the difference between a merge and a seam.
    /// </summary>
    private static int Address(int kind, int drop) => (kind == 1 && drop == 2) ? 2 : kind;

    /// <summary>
    /// Which course split this TILE ROW uses.
    ///
    /// The joint ON a tile boundary cannot move — the corner theorem needs one through every grid
    /// corner. The INTERIOR one is free, and it moves, because when it did not a blind seat read
    /// the floor as "a stack of horizontal stripes before it reads as stone": one unbroken ruled
    /// line every 16px across the whole map. Chosen per ROW so every tile in a row agrees and the
    /// joint stays continuous across every vertical boundary, while successive rows give courses
    /// of genuinely different heights.
    /// </summary>
    private static int RowSplit(Config c, int r) => Mix(0, r, c.SplitSalt + c.Seed) % c.Splits.Length;

    /// <summary>Stone-local y = 0 for this course under this split.</summary>
    private static int CourseOriginY(Config c, int splitI, int course)
        => course == 0 ? 1 : c.Splits[splitI][0] + 1;

    private static int ClusterBias(Config c, int bx, int courseK)
        => c.ClusterTable[Mix(bx / 3, courseK / 2, c.ClusterSalt + c.Seed) % c.ClusterTable.Length];

    private static int OffsetSteps(Config c, int key, int bias)
    {
        int k = c.OffsetSteps[key % c.OffsetSteps.Length] + bias;
        return System.Math.Clamp(k, -3, 3);
    }

    /// <summary>
    /// Stone-local x = 0 in this tile's coordinates. A SPANNING stone is measured from ITS
    /// BOUNDARY, never from its own left edge: with a head joint sanded away it can begin back in
    /// the previous tile at an offset chosen by a family the far tile cannot see. Measured from
    /// the boundary, the west tile's columns run 0..31 and the east tile's 32.., contiguous, and
    /// derived from nothing but which side of the boundary this tile is on.
    /// </summary>
    private static int StoneOrigin(Config c, int fw, int kind, int course, int drop)
    {
        if (kind == 0) return -T;
        if (kind == 2 || drop == 2) return 0;
        return c.ATable[fw][course];
    }

    private static int LadderIndex(Config c, double v)
    {
        int best = 0;
        double bd = double.MaxValue;
        for (int i = 0; i < c.Ladder.Length; i++)
        {
            double d = System.Math.Abs(v - c.Ladder[i]);
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    public static string Apply(TileLayer tileLayer, GameMap map, string manifestResPath,
                               System.Func<int, int, bool> isChannel)
    {
        var cfg = Load(manifestResPath, out string status);
        if (cfg == null) return $"[Tier1] ashlar floor: NOT APPLIED — {status}";

        // BOTH CROSS-CHECKS, BEFORE ANYTHING IS LAID. The first says this code agrees with the
        // composer about the bond; the second says it agrees about the material. A silent
        // disagreement in either is a seam at every tile boundary that nothing downstream reports.
        foreach (var (x, y, salt, expect) in cfg.EdgeCheck)
        {
            int got = EdgeFamily(x, y, salt, cfg.Seed, cfg.Families);
            if (got != expect)
                return $"[Tier1] ashlar floor: REFUSED — edge-family cross-check failed at "
                     + $"({x},{y}) salt={salt}: composer said {expect}, engine says {got}.";
        }
        foreach (var (x, k, kind, drop, expect) in cfg.StoneCheck)
        {
            int gotDrop = DropChoice(cfg, x, k);
            int addr = Address(kind, gotDrop);
            int bx = addr == 2 ? x + 1 : x;
            int key = addr == 1 ? Mix(x, k, cfg.InteriorSalt + cfg.Seed)
                                : Mix(bx, k, cfg.SpanSalt + cfg.Seed);
            int got = OffsetSteps(cfg, key, ClusterBias(cfg, bx, k));
            if (gotDrop != drop || got != expect)
                return $"[Tier1] ashlar floor: REFUSED — stone cross-check failed at tile x={x} "
                     + $"course={k} kind={kind}: composer said drop={drop} steps={expect}, engine "
                     + $"says drop={gotDrop} steps={got}. The stones would be painted by different "
                     + $"arithmetic than the one that drew the bond.";
        }

        var grainImg = LoadImage(cfg.GrainPath);
        if (grainImg == null)
            return $"[Tier1] ashlar floor: NOT APPLIED — grain bank unreadable: {cfg.GrainPath}";

        var atlasCache = new Dictionary<int, Image>();
        int laid = 0, channel = 0, missing = 0;

        foreach (var (pos, node) in tileLayer.TileSprites)
        {
            if (!map.IsWalkable(pos.X, pos.Y)) continue;
            if (node is not Sprite2D sprite) continue;

            int n = EdgeFamily(pos.X, pos.Y, cfg.HorizSalt, cfg.Seed, cfg.Families);
            int so = EdgeFamily(pos.X, pos.Y + 1, cfg.HorizSalt, cfg.Seed, cfg.Families);
            int fw = EdgeFamily(pos.X, pos.Y, cfg.VertSalt, cfg.Seed, cfg.Families);
            int fe = EdgeFamily(pos.X + 1, pos.Y, cfg.VertSalt, cfg.Seed, cfg.Families);
            int idx = TileIndex(n, fe, so, fw, cfg.Families);

            if (!atlasCache.TryGetValue(idx, out var atlas))
            {
                if (!cfg.Atlas.TryGetValue(idx, out var path)) { missing++; continue; }
                atlas = LoadImage(path);
                if (atlas == null) { missing++; continue; }
                atlasCache[idx] = atlas;
            }

            var drops = new int[Courses];
            for (int c = 0; c < Courses; c++)
                drops[c] = DropChoice(cfg, pos.X, pos.Y * Courses + c);
            int splitI = RowSplit(cfg, pos.Y);
            int cellIndex = splitI * 9 + drops[0] * 3 + drops[1];

            // Per-class parameters computed ONCE, then a single pass over the pixels. The
            // first version looped the whole tile once per class: seven passes and about 7k
            // GetPixel calls per cell before a single pixel was written.
            var offset = new double[7];
            var gmul = new double[7];
            var bankX = new int[7];
            var bankY = new int[7];
            var ox = new int[7];
            var oy = new int[7];
            var wornClass = new bool[7];
            bool anyWorn = false;

            for (int c = 0; c < Courses; c++)
            {
                int courseK = pos.Y * Courses + c;
                for (int kind = 0; kind < 3; kind++)
                {
                    int cls = 1 + c * 3 + kind;
                    int addr = Address(kind, drops[c]);
                    int bx = addr == 2 ? pos.X + 1 : pos.X;
                    int key = addr == 1 ? Mix(pos.X, courseK, cfg.InteriorSalt + cfg.Seed)
                                        : Mix(bx, courseK, cfg.SpanSalt + cfg.Seed);
                    int steps = OffsetSteps(cfg, key, ClusterBias(cfg, bx, courseK));

                    // Wear is read off the MAP, which both tiles either side of a boundary can
                    // read, and never off "which tile am I". So the channel ends at a JOINT rather
                    // than at a tile edge - the soft boundary section 8.2.1 asks for, delivered
                    // structurally instead of by feathering.
                    bool worn = isChannel != null && (addr switch
                    {
                        0 => isChannel(pos.X - 1, pos.Y) && isChannel(pos.X, pos.Y),
                        2 => isChannel(pos.X, pos.Y) && isChannel(pos.X + 1, pos.Y),
                        _ => isChannel(pos.X, pos.Y),
                    });
                    if (worn) anyWorn = true;
                    wornClass[cls] = worn;

                    offset[cls] = steps * (cfg.Ladder[1] - cfg.Ladder[0])
                                * (worn ? cfg.WearSpread : 1.0);
                    gmul[cls] = cfg.GrainAmp * (worn ? cfg.WornMul : 1.0);
                    int bank = key % cfg.GrainBank;
                    bankX[cls] = (bank % BankCols) * GrainSide;
                    bankY[cls] = (bank / BankCols) * GrainSide;
                    ox[cls] = StoneOrigin(cfg, fw, kind, c, drops[c]);
                    oy[cls] = CourseOriginY(cfg, splitI, c);
                }
            }

            var outImg = Image.CreateEmpty(T, T, false, Image.Format.Rgb8);
            int ax = (cellIndex % AtlasCols) * T, ay = (cellIndex / AtlasCols) * T;
            for (int py = 0; py < T; py++)
            {
                for (int px = 0; px < T; px++)
                {
                    var src = atlas.GetPixel(ax + px, ay + py);
                    int cls = (int)System.Math.Round(src.G * 255.0);
                    double L = cfg.Ladder[(int)System.Math.Round(src.R * 255.0)];

                    // Class 0 is a joint. It is copied straight across and NEVER offset: the
                    // ladder's bottom is where the occlusion lives, an offset applied to every
                    // pixel clips 30.16% of them at the floor of the palette, and section 6.3
                    // holds that authored occlusion is form rather than decoration.
                    if (cls > 0 && cls < 7)
                    {
                        int lx = ((px - ox[cls]) % GrainSide + GrainSide) % GrainSide;
                        int ly = ((py - oy[cls]) % GrainSide + GrainSide) % GrainSide;
                        var gp = grainImg.GetPixel(bankX[cls] + lx, bankY[cls] + ly);
                        double g = (gp.R * 255.0 - 128.0) / 64.0 * cfg.Coarse
                                 + (gp.G * 255.0 - 128.0) / 64.0 * cfg.Fine;
                        L = System.Math.Clamp(L + offset[cls] + g * gmul[cls],
                                              cfg.Ladder[0], cfg.Ladder[^1]);
                        L = cfg.Ladder[LadderIndex(cfg, L)];
                    }

                    outImg.SetPixel(px, py, new Color(
                        (float)(L * cfg.Tint[0] / 255.0), (float)(L * cfg.Tint[1] / 255.0),
                        (float)(L * cfg.Tint[2] / 255.0)));
                }
            }

            // THE ARRIS PASS. A joint beside a trodden stone is shallower, because feet round the
            // edges off — geometry, not light (§6.3), and a subtraction rather than an addition,
            // which is what §8.2.1 requires of polish. Each joint pixel takes its wear from the
            // stones it actually touches, so the channel ends where a STONE ends and never draws
            // a straight line on the tile grid.
            //
            // Bounds-checked, not wrapped. The Python reference used a circular shift here and
            // was rounding the arris of joints a whole tile away; the two would have disagreed
            // precisely where the channel meets a tile edge.
            if (anyWorn && cfg.WearArris > 0.0)
            {
                for (int py = 0; py < T; py++)
                {
                    for (int px = 0; px < T; px++)
                    {
                        if ((int)System.Math.Round(atlas.GetPixel(ax + px, ay + py).G * 255.0) != 0)
                            continue;
                        bool nearWorn = false;
                        for (int d = 0; d < 4 && !nearWorn; d++)
                        {
                            int ny = py + (d == 0 ? -1 : d == 1 ? 1 : 0);
                            int nx = px + (d == 2 ? -1 : d == 3 ? 1 : 0);
                            if (ny < 0 || ny >= T || nx < 0 || nx >= T) continue;
                            int nc = (int)System.Math.Round(
                                atlas.GetPixel(ax + nx, ay + ny).G * 255.0);
                            if (nc > 0 && nc < 7 && wornClass[nc]) nearWorn = true;
                        }
                        if (!nearWorn) continue;
                        double jl = cfg.Ladder[(int)System.Math.Round(
                            atlas.GetPixel(ax + px, ay + py).R * 255.0)];
                        jl += (cfg.LumMedian - jl) * cfg.WearArris;
                        jl = cfg.Ladder[LadderIndex(cfg, System.Math.Clamp(
                            jl, cfg.Ladder[0], cfg.Ladder[^1]))];
                        outImg.SetPixel(px, py, new Color(
                            (float)(jl * cfg.Tint[0] / 255.0), (float)(jl * cfg.Tint[1] / 255.0),
                            (float)(jl * cfg.Tint[2] / 255.0)));
                    }
                }
            }

            // NO FLIP, NO ROTATION. Orientation is meaning on an edge-matched tile, and the
            // coursing has a direction: turning one would stand its bed joints on end.
            sprite.Texture = ImageTexture.CreateFromImage(outImg);
            sprite.FlipH = false;
            sprite.FlipV = false;
            laid++;
            if (anyWorn) channel++;
        }

        return $"[Tier1] ashlar floor: laid={laid} channel_cells={channel} missing={missing} "
             + $"families={cfg.Families} seed={cfg.Seed} atlases={atlasCache.Count} "
             + $"edge_check={cfg.EdgeCheck.Count}/OK stone_check={cfg.StoneCheck.Count}/OK "
             + $"manifest={manifestResPath}";
    }

    private static Image? LoadImage(string resPath)
    {
        var tex = GD.Load<Texture2D>(resPath);
        return tex?.GetImage();
    }

    private static Config? Load(string manifestResPath, out string status)
    {
        status = "";
        try
        {
            using var f = Godot.FileAccess.Open(manifestResPath, Godot.FileAccess.ModeFlags.Read);
            if (f == null) { status = $"manifest not found: {manifestResPath}"; return null; }
            using var doc = JsonDocument.Parse(f.GetAsText());
            var root = doc.RootElement;
            string dir = manifestResPath[..(manifestResPath.LastIndexOf('/') + 1)];

            var cfg = new Config
            {
                Families = root.GetProperty("families").GetInt32(),
                Seed = root.GetProperty("seed").GetInt32(),
                GrainBank = root.GetProperty("grain_bank").GetInt32(),
                GrainAmp = root.GetProperty("grain_amp").GetDouble(),
            };
            var salts = root.GetProperty("salts");
            cfg.HorizSalt = salts.GetProperty("horizontal").GetInt32();
            cfg.SplitSalt = salts.GetProperty("split").GetInt32();
            cfg.VertSalt = salts.GetProperty("vertical").GetInt32();
            cfg.SpanSalt = salts.GetProperty("span").GetInt32();
            cfg.InteriorSalt = salts.GetProperty("interior").GetInt32();
            cfg.DropSalt = salts.GetProperty("drop").GetInt32();
            cfg.ClusterSalt = salts.GetProperty("cluster").GetInt32();

            var gs = root.GetProperty("grain_scales");
            cfg.Coarse = gs.GetProperty("coarse").GetDouble();
            cfg.Fine = gs.GetProperty("fine").GetDouble();
            cfg.WornMul = gs.GetProperty("worn_multiplier").GetDouble();
            var wear = root.GetProperty("wear");
            cfg.WearSpread = wear.GetProperty("spread").GetDouble();
            cfg.WearArris = wear.GetProperty("arris").GetDouble();

            var steps = new List<int>();
            foreach (var v in root.GetProperty("offset_steps").EnumerateArray())
                steps.Add(v.GetInt32());
            cfg.OffsetSteps = steps.ToArray();

            var ct = new List<int>();
            foreach (var v in root.GetProperty("cluster_table").EnumerateArray()) ct.Add(v.GetInt32());
            cfg.ClusterTable = ct.ToArray();

            var mat = root.GetProperty("material");
            var lad = new List<double>();
            foreach (var v in mat.GetProperty("ladder").EnumerateArray()) lad.Add(v.GetDouble());
            cfg.Ladder = lad.ToArray();
            cfg.LumMedian = mat.GetProperty("lum_median").GetDouble();
            var tint = new List<double>();
            foreach (var v in mat.GetProperty("tint").EnumerateArray()) tint.Add(v.GetDouble());
            cfg.Tint = tint.ToArray();

            static int[][] Table(JsonElement e)
            {
                var rows = new List<int[]>();
                foreach (var r in e.EnumerateArray())
                {
                    var row = new List<int>();
                    foreach (var v in r.EnumerateArray()) row.Add(v.GetInt32());
                    rows.Add(row.ToArray());
                }
                return rows.ToArray();
            }
            cfg.ATable = Table(root.GetProperty("a_table"));
            cfg.Splits = Table(root.GetProperty("splits"));
            cfg.MvTable = Table(root.GetProperty("mv_table"));

            foreach (var e in root.GetProperty("base").EnumerateArray())
            {
                int idx = TileIndex(e.GetProperty("n").GetInt32(), e.GetProperty("e").GetInt32(),
                                    e.GetProperty("s").GetInt32(), e.GetProperty("w").GetInt32(),
                                    cfg.Families);
                cfg.Atlas[idx] = dir + e.GetProperty("file").GetString();
            }
            cfg.GrainPath = dir + root.GetProperty("grain_file").GetString();

            foreach (var e in root.GetProperty("edge_family_check").EnumerateArray())
                cfg.EdgeCheck.Add((e.GetProperty("x").GetInt32(), e.GetProperty("y").GetInt32(),
                                   e.GetProperty("salt").GetInt32(),
                                   e.GetProperty("family").GetInt32()));
            foreach (var e in root.GetProperty("stone_check").EnumerateArray())
                cfg.StoneCheck.Add((e.GetProperty("x").GetInt32(), e.GetProperty("k").GetInt32(),
                                    e.GetProperty("kind").GetInt32(), e.GetProperty("drop").GetInt32(),
                                    e.GetProperty("steps").GetInt32()));

            status = "ok";
            return cfg;
        }
        catch (System.Exception ex)
        {
            status = $"manifest unreadable: {ex.Message}";
            return null;
        }
    }
}
