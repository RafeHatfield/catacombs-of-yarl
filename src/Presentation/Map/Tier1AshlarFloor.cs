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
        public int CrackSalt = 3006, CrackRate = 7, CrackMinTiles = 3, CrackMaxTiles = 7;
        public int CrackScale = 1024, CrackTurn = 5;
        public double CrackDepth = 0.42;
        public int[][] CrackDirs = System.Array.Empty<int[]>();
        public int MarksSalt = 3007, MarkMinLen = 5, MarkMaxLen = 10;
        public double MarkDepth = 1.0, PitDepth = 1.0;
        public int MarkBands = 5, MarkPits = 3, WearBands = 3, WearPits = 1;
        public int WearSalt = 3008, ChipSalt = 3009, WearLo = 70, WearHi = 200, ChannelWear = 235;
        public double ChipRate = 0.55, DressingKeep = 0.45;
        public int JointBreakSalt = 3010;
        public double[] JointFill = { 0.0, 0.0, 1.0, 2.0 };
        public double[] JointBreak = { 0.0, 0.0, 0.20, 0.45 };
        public int[][] WearOctaves = System.Array.Empty<int[]>();
        public double[] WearAges = { 0.0, 0.34, 0.67, 1.0 };
        public int[][] MarkDirs = System.Array.Empty<int[]>();
        public int[] OffsetSteps = System.Array.Empty<int>();
        public int[] ClusterTable = { -1, 0, 0, 1 };
        public double[] Ladder = System.Array.Empty<double>();
        public double[] Tint = { 1, 1, 1 };
        public double[] ChromaByAge = { 0, 0, 0, 0 };
        public double[] ChromaDir = { 0, 0, 0 };
        public double[] PolishByAge = { 0, 0, 0, 0 };
        public double PolishExp = 2.0, PolishGain = 1.0;
        public int[][] ATable = System.Array.Empty<int[]>();
        public int[][] MvTable = System.Array.Empty<int[]>();
        public readonly Dictionary<int, string> Atlas = new();
        public string GrainPath = "";
        public readonly List<(int X, int Y, int Salt, int Family)> EdgeCheck = new();
        public readonly List<(int X, int K, int Kind, int Drop, int Steps)> StoneCheck = new();
        public readonly List<(int X, int Y, int Px, int Py, int R, int G, int B)> PaintCheck = new();
        public int[] PaintCheckWornColumns = System.Array.Empty<int>();
        // THE CHECK'S OWN TRAFFIC FIELD. The real one is derived from the level graph and
        // the composer has no map, so the finished-pixel check carries a SYNTHETIC field
        // that both sides agree on. What it verifies is the PAINTING given a field; the
        // derivation is verified by the Logic layer's own tests, where a hierarchy can be
        // asserted without a scene, a device or a capture.
        public byte[,]? CheckTraffic;
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

    // ---- THE CRACK NETWORK, AT FIELD SCALE ------------------------------------------------
    //
    // A crack belongs to an ANCHOR TILE and runs for whole tiles beyond it, so every cell it
    // crosses generates the same polyline from the same world address — the construction that
    // makes a stone continuous, applied to a line.
    //
    // ⚠ TWO INTEGER TRAPS, both of which would desync this from the composer silently and only
    // near the map's origin, which is exactly where a review scene sits:
    //
    //   FLOOR DIVISION. Python's `//` floors toward negative infinity; C#'s `/` truncates toward
    //   zero. The anchor scan reaches eight tiles left and up of the cell being painted, so at
    //   x=0 it visits negative tiles and the polyline carries negative pixel coordinates.
    //   -1 / 1024 is 0 here and -1 there.
    //
    //   MODULO OF A NEGATIVE. Python's `%` returns non-negative; C#'s can return negative. The
    //   direction index random-walks by -1, so it reaches -1 and must wrap to 31, not to -1.
    //
    // Neither would throw. Both would draw a different crack on one side of the origin.
    private static int FloorDiv(int a, int b) => (int)System.Math.Floor((double)a / b);

    private static int Mod(int a, int m) => ((a % m) + m) % m;

    private static int Lcg(int state) => (int)(((long)state * 1103515245 + 12345) & 0x7FFFFFFF);

    private static List<(int X, int Y)> CrackPolyline(Config c, int ax, int ay)
    {
        var pts = new List<(int, int)>();
        int h = Mix(ax, ay, c.CrackSalt + c.Seed);
        if (h % 100 >= c.CrackRate) return pts;

        int st = Lcg(h | 1);
        int length = c.CrackMinTiles + (st >> 7) % (c.CrackMaxTiles - c.CrackMinTiles + 1);
        st = Lcg(st);
        int x = ax * T + (st >> 5) % T;
        st = Lcg(st);
        int y = ay * T + (st >> 5) % T;
        st = Lcg(st);
        int d = (st >> 9) % c.CrackDirs.Length;

        int px = x * c.CrackScale, py = y * c.CrackScale;
        for (int i = 0; i < length * T; i++)
        {
            st = Lcg(st);
            if ((st >> 11) % c.CrackTurn == 0)
            {
                st = Lcg(st);
                d = Mod(d + (((st >> 13) % 2) != 0 ? 1 : -1), c.CrackDirs.Length);
            }
            px += c.CrackDirs[d][0];
            py += c.CrackDirs[d][1];
            pts.Add((FloorDiv(px, c.CrackScale), FloorDiv(py, c.CrackScale)));
        }
        return pts;
    }

    private static HashSet<(int, int)> CrackPixels(Config c, int tx, int ty,
                                                   Dictionary<(int, int), List<(int X, int Y)>> cache)
    {
        var outp = new HashSet<(int, int)>();
        int reach = c.CrackMaxTiles + 1;
        int x0 = tx * T, y0 = ty * T;
        for (int ay = ty - reach; ay <= ty + reach; ay++)
        {
            for (int ax = tx - reach; ax <= tx + reach; ax++)
            {
                if (!cache.TryGetValue((ax, ay), out var line))
                {
                    line = CrackPolyline(c, ax, ay);
                    cache[(ax, ay)] = line;
                }
                foreach (var (wx, wy) in line)
                {
                    int lx = wx - x0, ly = wy - y0;
                    if (lx >= 0 && lx < T && ly >= 0 && ly < T) outp.Add((ly, lx));
                }
            }
        }
        return outp;
    }

    /// <summary>
    /// The dressing on one stone, in STONE-LOCAL pixels: (u, v, depth in ladder rungs).
    ///
    /// The device gate: *"material texture is below the perceptual floor — the floor reads as
    /// linoleum."* The grain this replaces was authored at about ±4 luminance against a 13.23
    /// rung, so it never survived quantisation and a stone face was one flat value with a border.
    ///
    /// What replaces it is not louder noise. These are the marks of a stone that was DRESSED —
    /// claw-chisel striations running ONE WAY PER STONE, because one mason worked one stone one
    /// way, and pits where the tooth tore out rather than cut. All of it is occlusion vocabulary
    /// and nothing else: every mark is a recess, so every mark is darker, and none has a lit side
    /// and a shaded side. A dressing mark drawn with a highlight would be depicted lighting.
    ///
    /// Addressed by the stone and sampled in stone-local coordinates measured from the boundary,
    /// so it cannot repeat on the tile grid and both tiles either side of a spanning stone dress
    /// it identically.
    /// </summary>
    /// <summary>
    /// The stone's own extent in stone-local coordinates: (uLo, uHi, vHi).
    ///
    /// Marks were first scattered across the whole 64×32 stone-local box, and a stone occupies a
    /// fraction of it — so roughly three quarters of every stone's dressing landed outside the
    /// class mask and was discarded. The interior amplitude moved 0.068 → 0.073 of a rung, which
    /// is nothing, on the change that was supposed to be the whole point.
    ///
    /// Derivable from the family tables both tiles already share, so it needs no new agreement
    /// between them. Mirrors <see cref="StoneOrigin"/> case for case.
    /// </summary>
    private static (int Lo, int Hi, int VHi) StoneExtent(Config c, int fw, int fe, int kind,
                                                         int course, int drop, int splitI)
    {
        int aW = c.ATable[fw][course], mvW = c.MvTable[fw][course];
        int aE = c.ATable[fe][course], mvE = c.MvTable[fe][course];
        int vHi = (course == 0 ? c.Splits[splitI][0] - 1 : T - 1) - CourseOriginY(c, splitI, course);

        // THE EXTENT MUST BE DERIVED FROM THE BOUNDARY ALONE, never from the merge. A merged
        // stone's real extent depends on this tile's drop and on the family of its far side,
        // neither of which the tile across the boundary can see — so the two dressed the same
        // stone from different extents and the seam landed on the boundary. Caught by the
        // boundary-step instrument at 1.277, on an axis the device gate had already passed.
        if (kind == 0) return (mvW, T + aW, vHi);
        if (kind == 2 || drop == 2) return (mvE, T + aE, vHi);
        return (0, mvE - aW, vHi);
    }

    private static List<(int U, int V, double D)> StoneMarks(Config c, int key, bool worn,
                                                             (int Lo, int Hi, int VHi) ext,
                                                             double wear)
    {
        // TRAFFICKED STONES POLISH SMOOTHER AS THEIR JOINTS OPEN; sheltered stones stay sharp and
        // tight. The dressing is what traffic takes off first, so its count and its depth both
        // fall with wear — continuous now, where it used to be a binary channel flag.
        double keep = 1.0 - c.DressingKeep * wear;
        var outp = new List<(int, int, double)>();
        int st = Lcg((key ^ (c.MarksSalt + c.Seed)) | 1);
        int uSpan = System.Math.Max(1, ext.Hi - ext.Lo - 1);
        int vSpan = System.Math.Max(1, ext.VHi - 1);

        // ONE DIRECTION PER STONE. A mason does not change hands halfway across a flag.
        var d = c.MarkDirs[(st >> 6) % c.MarkDirs.Length];
        int dx = d[0], dy = d[1];

        // STROKES COME IN BANDS, because a claw chisel has several teeth and a mason works in
        // passes. Scattered singly they read as SCRATCHES — a few long slashes at odd angles
        // across a face, which is damage, not dressing. Clustered into parallel runs 2px apart
        // they read as tooling, and each stroke still clears the readable-extent bar on its own.
        int pxp = -dy, pyp = dx;
        // MORE BANDS, NOT MORE TEETH PER BAND. Teeth raise regularity; bands raise
        // coverage while staying ragged. At three bands the delivered contrast sat at
        // 0.148 against a floor of 0.144, and a 3% margin proves nothing.
        int n = System.Math.Max(1, (int)System.Math.Round(
            ((worn ? c.WearBands : c.MarkBands) + ((st >> 9) % 2)) * keep));
        for (int j = 0; j < n; j++)
        {
            st = Lcg(st); int u = ext.Lo + (st >> 5) % uSpan;
            st = Lcg(st); int v = (st >> 5) % vSpan;
            st = Lcg(st);
            int length = c.MarkMinLen + (st >> 7) % (c.MarkMaxLen - c.MarkMinLen + 1);
            st = Lcg(st);
            int teeth = 2 + (st >> 10) % 2;
            st = Lcg(st);
            int gap = 2 + (st >> 12) % 2;      // 2 or 3 px between teeth, not always 2
            for (int t = 0; t < teeth; t++)
            {
                int ou = u + pxp * t * gap, ov = v + pyp * t * gap;
                // EVERY TOOTH A DIFFERENT LENGTH. Equal-length teeth on an equal pitch is a
                // barcode: the first clustered version read as tally marks on some stones. A
                // chisel skips and bites unevenly, and a ragged end is the difference between
                // tooling and hatching.
                st = Lcg(st);
                int ln = System.Math.Max(c.MarkMinLen, length - (st >> 8) % 3);
                for (int i = 0; i < ln; i++)
                    outp.Add((ou + dx * i, ov + dy * i, c.MarkDepth * keep));
            }
        }

        int m = System.Math.Max(0, (int)System.Math.Round(
            ((worn ? c.WearPits : c.MarkPits) + ((st >> 11) % 3)) * keep));
        for (int j = 0; j < m; j++)
        {
            st = Lcg(st); int u = ext.Lo + (st >> 5) % uSpan;
            st = Lcg(st); int v = (st >> 5) % vSpan;
            st = Lcg(st);
            int wdt = 2 + (st >> 13) % 2;      // 2 or 3 across — never the 1px speck
            for (int aa = 0; aa < wdt; aa++)
                for (int bb = 0; bb < 2; bb++)
                    outp.Add((u + aa, v + bb, c.PitDepth * keep));
        }
        return outp;
    }

    /// <summary>
    /// THE TRAFFIC FIELD, sampled at a world pixel — bilinear between TILE CENTRES.
    ///
    /// Per-tile is what the level graph can say; per-pixel is what the floor needs. Consuming the
    /// per-tile scalar directly would paint the traffic model onto the tile grid, which is
    /// §8.3.1's lattice with a better excuse. Interpolating between centres means a route crosses
    /// a tile boundary without knowing there was one.
    /// </summary>
    private static int TrafficAt(byte[,] f, int wx, int wy)
    {
        int w = f.GetLength(0), h = f.GetLength(1);
        int sx = wx - T / 2, sy = wy - T / 2;
        int gx = FloorDiv(sx, T), gy = FloorDiv(sy, T);
        int fx = sx - gx * T, fy = sy - gy * T;
        int Smp(int x, int y) => f[System.Math.Clamp(x, 0, w - 1), System.Math.Clamp(y, 0, h - 1)];
        int top = Smp(gx, gy) * (T - fx) + Smp(gx + 1, gy) * fx;
        int bot = Smp(gx, gy + 1) * (T - fx) + Smp(gx + 1, gy + 1) * fx;
        return (top * (T - fy) + bot * fy) / (T * T);
    }

    /// <summary>
    /// What the wear pass actually consumes: the traffic field, FRAYED by the old noise.
    ///
    /// The register guardrail is that the path is discovered, never staged — and a pure
    /// interpolation of an accumulated route is a smooth ribbon, which is exactly what "reads as
    /// a drawn route" means. A quarter of the old two-octave field is mixed back in so the edges
    /// break up and the width wanders, without moving where the route goes.
    /// </summary>
    private static int WearScalar(Config c, byte[,]? traffic, int wx, int wy)
    {
        int noise = WearAt(c, wx, wy);
        if (traffic == null) return noise;
        return (TrafficAt(traffic, wx, wy) * 3 + noise) / 4;
    }

    /// <summary>
    /// The old wear scalar at a world pixel, 0..255 — two octaves of value noise at FIVE and ELEVEN
    /// tiles, bilinear, integer throughout so the composer is reproduced exactly.
    ///
    /// Coprime periods, coprime with the tile: nothing in the field lands on the grid or on any
    /// harmonic of it. A single octave at any period would draw its own.
    /// </summary>
    private static int WearAt(Config c, int px, int py)
    {
        long total = 0;
        int wsum = 0;
        foreach (var oct in c.WearOctaves)
        {
            int span = oct[0] * T, weight = oct[1];
            int gx = FloorDiv(px, span), gy = FloorDiv(py, span);
            int fx = px - gx * span, fy = py - gy * span;
            long v00 = Mix(gx, gy, c.WearSalt + c.Seed) & 255;
            long v10 = Mix(gx + 1, gy, c.WearSalt + c.Seed) & 255;
            long v01 = Mix(gx, gy + 1, c.WearSalt + c.Seed) & 255;
            long v11 = Mix(gx + 1, gy + 1, c.WearSalt + c.Seed) & 255;
            long top = v00 * (span - fx) + v10 * fx;
            long bot = v01 * (span - fx) + v11 * fx;
            total += ((top * (span - fy) + bot * fy) / ((long)span * span)) * weight;
            wsum += weight;
        }
        return (int)(total / wsum);
    }

    /// <summary>
    /// The wear scalar as one of four AGES. Not taste — a correctness fix: a continuous scalar
    /// against a seven-rung ladder puts pixels on quantisation knife-edges, and at exactly w=0.5
    /// a joint lands HALF A RUNG between two levels where the tie is broken by floating-point
    /// noise. The composer and its mirror disagreed on 65 pixels for no reason either could be
    /// said to be wrong about, and a third implementation would have been a third coin flip.
    /// Mortar is tight, opening, open, or gone.
    /// </summary>
    private static double Wear01(Config c, int raw, bool channel)
    {
        if (channel) raw = System.Math.Max(raw, c.ChannelWear);
        if (raw <= c.WearLo) return 0.0;
        if (raw >= c.WearHi) return 1.0;
        double f = (raw - c.WearLo) / (double)(c.WearHi - c.WearLo);
        double best = c.WearAges[0];
        foreach (var age in c.WearAges)
            if (System.Math.Abs(age - f) < System.Math.Abs(best - f)) best = age;
        return best;
    }

    /// <summary>Which of the four wear ages this scalar snapped to.</summary>
    private static int AgeIndex(Config c, double w)
    {
        int best = 0;
        for (int i = 1; i < c.WearAges.Length; i++)
            if (System.Math.Abs(c.WearAges[i] - w) < System.Math.Abs(c.WearAges[best] - w)) best = i;
        return best;
    }

    /// <summary>
    /// THE CHROMA CHANNEL's tint for one wear age: the material tint rotated toward the ruled
    /// direction at CONSTANT LUMINANCE.
    ///
    /// The luminance component of the direction is projected out here rather than baked into the
    /// manifest, so that the invariant — this lever moves colour and no value — is enforced in
    /// the code that uses it and cannot drift if the direction is ever re-ruled.
    /// </summary>
    private static double[] ChromaTint(Config c, int age)
    {
        double[] w = { 0.299, 0.587, 0.114 };
        double s = c.ChromaByAge[age];
        double num = 0, den = 0;
        for (int i = 0; i < 3; i++) { num += w[i] * c.Tint[i] * c.ChromaDir[i]; den += w[i] * c.Tint[i]; }
        double k = den == 0 ? 0 : num / den;
        var outv = new double[3];
        for (int i = 0; i < 3; i++) outv[i] = c.Tint[i] * (1.0 + s * (c.ChromaDir[i] - k));
        return outv;
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
        var paintFail = SelfCheck(cfg, grainImg, atlasCache);
        if (paintFail != null) return $"[Tier1] ashlar floor: REFUSED — {paintFail}";

        // WHERE PEOPLE ACTUALLY WALK — derived from the level graph, once, before anything is
        // laid. The review scenes carry no Room records, so the map-only derivation is used: the
        // spine is the level's own longest walk and every leaf hanging off it is a branch.
        var tf = TrafficField.ComputeFromMap(map);
        var traffic = tf.Field;

        // THE FIELD, IN THE LOG, so it can be audited rather than trusted. Counts alone cannot
        // say WHERE the traffic went, and a route through the wrong part of a room would look
        // exactly like a route through the right one in any summary statistic. Ten levels, '.'
        // for unwalked through '#' for the busiest.
        var ramp = " .:-=+*#%@";
        var sb = new System.Text.StringBuilder();
        sb.Append("[Tier1] traffic field (space=unwalked .. @=busiest)\n");
        for (int y = 0; y < map.Height; y++)
        {
            sb.Append("[Tier1]   ");
            for (int x = 0; x < map.Width; x++)
                sb.Append(map.IsWalkable(x, y)
                    ? ramp[System.Math.Clamp(traffic[x, y] * (ramp.Length - 1) / 255, 0, ramp.Length - 1)]
                    : '#');
            sb.Append('\n');
        }
        var crackCache = new Dictionary<(int, int), List<(int X, int Y)>>();
        int laid = 0, channel = 0, missing = 0, polished = 0;

        // §4.2: A STEP THAT DOES NOTHING MUST GO RED. If the shader fails to load, the floor
        // still lays and still looks almost right — the chroma and the joints carry on — and the
        // one lever this round exists to test would be silently absent. So its absence is
        // counted and reported on the same line as everything else.
        var polishShader = ResourceLoader.Load<Shader>(PolishShaderPath);

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

            var outImg = PaintCell(cfg, atlas, grainImg, pos.X, pos.Y, fw, fe, traffic,
                                   isChannel, crackCache, out bool anyWorn, out var polishImg);

            // NO FLIP, NO ROTATION. Orientation is meaning on an edge-matched tile, and the
            // coursing has a direction: turning one would stand its bed joints on end.
            sprite.Texture = ImageTexture.CreateFromImage(outImg);
            sprite.FlipH = false;
            sprite.FlipV = false;

            // THE POLISH LEVER, attached per sprite. A ShaderMaterial each, because the mask is
            // per tile — 74 of them on this scene, which is the cost of a floor that answers the
            // lamp rather than being painted as if it had.
            if (polishShader != null)
            {
                var pm = new ShaderMaterial { Shader = polishShader };
                pm.SetShaderParameter("polish_tex", ImageTexture.CreateFromImage(polishImg));
                pm.SetShaderParameter("polish_exp", (float)cfg.PolishExp);
                pm.SetShaderParameter("polish_gain", (float)cfg.PolishGain);
                sprite.Material = pm;
                polished++;
            }
            laid++;
            if (anyWorn) channel++;
        }

        return $"[Tier1] ashlar floor: laid={laid} channel_cells={channel} missing={missing} "
             + $"families={cfg.Families} seed={cfg.Seed} atlases={atlasCache.Count} "
             + $"edge_check={cfg.EdgeCheck.Count}/OK stone_check={cfg.StoneCheck.Count}/OK "
             + $"paint_check={cfg.PaintCheck.Count}/OK "
             + $"polished={polished}{(polishShader == null ? "/SHADER-MISSING" : "")} "
             + $"traffic=spine:{tf.SpineLength:F0}/routes:{tf.Routes} "
             + $"manifest={manifestResPath}\n" + sb.ToString().TrimEnd();
    }


    /// <summary>
    /// Paint one cell. Extracted so that the SELF-CHECK below runs the very code that lays the
    /// floor rather than a second copy of it — a check against a reimplementation only proves the
    /// reimplementation.
    /// </summary>
    private const string PolishShaderPath = "res://src/Presentation/assets/shaders/tier1_polish.gdshader";

    private static Image PaintCell(Config cfg, Image atlas, Image grainImg, int tx, int ty,
                                   int fw, int fe, byte[,]? traffic, System.Func<int, int, bool>? isChannel,
                                   Dictionary<(int, int), List<(int X, int Y)>> crackCache,
                                   out bool anyWorn, out Image polish)
    {
        var drops = new int[Courses];
        for (int c = 0; c < Courses; c++)
            drops[c] = DropChoice(cfg, tx, ty * Courses + c);
        int splitI = RowSplit(cfg, ty);
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
        var markDepth = new double[T, T];
        double rung = cfg.Ladder[1] - cfg.Ladder[0];
        anyWorn = false;

        for (int c = 0; c < Courses; c++)
        {
            int courseK = ty * Courses + c;
            for (int kind = 0; kind < 3; kind++)
            {
                int cls = 1 + c * 3 + kind;
                int addr = Address(kind, drops[c]);
                int bx = addr == 2 ? tx + 1 : tx;
                int key = addr == 1 ? Mix(tx, courseK, cfg.InteriorSalt + cfg.Seed)
                                    : Mix(bx, courseK, cfg.SpanSalt + cfg.Seed);
                int steps = OffsetSteps(cfg, key, ClusterBias(cfg, bx, courseK));

                // Wear is read off the MAP, which both tiles either side of a boundary can
                // read, and never off "which tile am I". So the channel ends at a JOINT rather
                // than at a tile edge - the soft boundary section 8.2.1 asks for, delivered
                // structurally instead of by feathering.
                bool worn = isChannel != null && (addr switch
                {
                    0 => isChannel(tx - 1, ty) && isChannel(tx, ty),
                    2 => isChannel(tx, ty) && isChannel(tx + 1, ty),
                    _ => isChannel(tx, ty),
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

                // THE WORKED SURFACE, masked by the stone's own class so a mark falling past a
                // joint is simply not drawn. Overlapping marks accumulate, exactly as the
                // composer's do.
                int mAx = (cellIndex % AtlasCols) * T, mAy = (cellIndex / AtlasCols) * T;
                var mExt = StoneExtent(cfg, fw, fe, kind, c, drops[c], splitI);
                double sw = Wear01(cfg, WearScalar(cfg, traffic, tx * T + T / 2, ty * T + T / 2), worn);
                foreach (var (mu, mv, md) in StoneMarks(cfg, key, worn, mExt, sw))
                {
                    int mlx = mu + ox[cls], mly = mv + oy[cls];
                    if (mlx < 0 || mlx >= T || mly < 0 || mly >= T) continue;
                    int atCls = (int)System.Math.Round(
                        atlas.GetPixel(mAx + mlx, mAy + mly).G * 255.0);
                    if (atCls == cls) markDepth[mly, mlx] -= md * rung;
                }
            }
        }

        // ONE RAW ACCUMULATION, THEN ONE QUANTISE, and the order is load-bearing rather than
        // tidy. The composer rounds the whole tile once at the end; rounding per pixel and then
        // subtracting wear computes quantise(quantise(x) + w), which is not quantise(x + w). The
        // mirror did exactly that and disagreed on 1368 pixels — every one a chipped arris,
        // because a chip is the only thing that subtracts from a STONE pixel after the class
        // loop has run.
        var raw = new double[T, T];
        var clsArr = new int[T, T];
        int ax = (cellIndex % AtlasCols) * T, ay = (cellIndex / AtlasCols) * T;

        for (int py = 0; py < T; py++)
        {
            for (int px = 0; px < T; px++)
            {
                var src = atlas.GetPixel(ax + px, ay + py);
                int cls = (int)System.Math.Round(src.G * 255.0);
                clsArr[py, px] = cls;
                double L = cfg.Ladder[(int)System.Math.Round(src.R * 255.0)];

                if (cls > 0 && cls < 7)
                {
                    int lx = ((px - ox[cls]) % GrainSide + GrainSide) % GrainSide;
                    int ly = ((py - oy[cls]) % GrainSide + GrainSide) % GrainSide;
                    var gp = grainImg.GetPixel(bankX[cls] + lx, bankY[cls] + ly);
                    double g = (gp.R * 255.0 - 128.0) / 64.0 * cfg.Coarse
                             + (gp.G * 255.0 - 128.0) / 64.0 * cfg.Fine;
                    L += offset[cls] + g * gmul[cls] + markDepth[py, px];
                }
                raw[py, px] = L;
            }
        }

        // THE ARRIS PASS. A joint beside a trodden stone is shallower, because feet round the
        // edges off — geometry, not light, and a subtraction rather than an addition. Each joint
        // pixel takes its wear from the stones it actually TOUCHES, bounds-checked, never wrapped.
        if (anyWorn && cfg.WearArris > 0.0)
        {
            for (int py = 0; py < T; py++)
            {
                for (int px = 0; px < T; px++)
                {
                    if (clsArr[py, px] != 0) continue;
                    bool nearWorn = false;
                    for (int d = 0; d < 4 && !nearWorn; d++)
                    {
                        int ny = py + (d == 0 ? -1 : d == 1 ? 1 : 0);
                        int nx = px + (d == 2 ? -1 : d == 3 ? 1 : 0);
                        if (ny < 0 || ny >= T || nx < 0 || nx >= T) continue;
                        int nc = clsArr[ny, nx];
                        if (nc > 0 && nc < 7 && wornClass[nc]) nearWorn = true;
                    }
                    if (nearWorn)
                        raw[py, px] += (cfg.LumMedian - raw[py, px]) * cfg.WearArris;
                }
            }
        }

        // ================= THE DIFFERENTIAL-WEAR PASS =================
        //
        // THE DEVICE GATE, second walk: "all the gaps look standardized... freshly laid and
        // mortared, like someone scoured new stone to make it look old." Ruled a register
        // violation: uniform joints are STAGED AGE, and wear is earned differentially.
        //
        // (a) a joint OPENS where feet passed — deeper, therefore darker. Keyed on world position
        //     alone, so both tiles either side of a boundary agree by construction.
        // (b) the stones beside an open joint lose their arrises: a pixel of stone goes with the
        //     joint, and sometimes a second — a corner gone.
        bool channelHere = isChannel != null && isChannel(tx, ty);
        var openAmt = new double[T, T];
        for (int py = 0; py < T; py++)
            for (int px = 0; px < T; px++)
                if (clsArr[py, px] == 0)
                {
                    openAmt[py, px] = Wear01(cfg, WearScalar(cfg, traffic, tx * T + px, ty * T + py), channelHere);

                    // THE JOINT CARRIES THE TRAFFIC. Off-route it stays as deep and as dark as
                    // the bond drew it; trodden it is packed with grit, and a packed joint is a
                    // shallower one — lighter as a consequence of geometry, never as paint. Some
                    // of it fills level with the floor entirely, so the line between two stones
                    // stops being a line, which is what "stones wearing into one another" looks
                    // like at 32px.
                    //
                    // The BOND is untouched: the class mask still divides the stones, so every
                    // stone keeps its address and the corner theorem is unaffected. What degrades
                    // along a path is the VISIBLE enclosure, deliberately.
                    int age = AgeIndex(cfg, openAmt[py, px]);
                    int hb = Mix(tx * T + px, ty * T + py, cfg.JointBreakSalt + cfg.Seed);
                    if ((hb % 1000) / 1000.0 < cfg.JointBreak[age])
                        raw[py, px] = cfg.LumMedian;
                    else
                        raw[py, px] += cfg.JointFill[age] * rung;
                }

        for (int py = 0; py < T; py++)
        {
            for (int px = 0; px < T; px++)
            {
                if (clsArr[py, px] == 0) continue;
                double near = 0.0;
                if (py > 0) near = System.Math.Max(near, openAmt[py - 1, px]);
                if (py < T - 1) near = System.Math.Max(near, openAmt[py + 1, px]);
                if (px > 0) near = System.Math.Max(near, openAmt[py, px - 1]);
                if (px < T - 1) near = System.Math.Max(near, openAmt[py, px + 1]);
                if (near <= 0.0) continue;
                int h = Mix(tx * T + px, ty * T + py, cfg.ChipSalt + cfg.Seed);
                if ((h % 1000) / 1000.0 < cfg.ChipRate * near)
                    raw[py, px] -= near * rung * 1.6;
            }
        }

        // ================= THE CHROMA CHANNEL =================
        //
        // Step two of the pre-declared ladder, after the joint lever was discharged BY PROOF: a
        // lever confined to the joints owns 21.85% of the surface and cannot reach §13.8's floor
        // at any setting. This one runs on the 78.14% the joints never touch.
        //
        // A ratio between channels survives the light rig's multiplication, which an authored
        // value difference does not — and more than half this floor sits below luminance 70,
        // where value work is spent where nobody can see it.
        //
        // FACES ONLY, and at constant luminance. A joint is dark because it is ENCLOSED, and
        // enclosure has no hue; a colour that also darkened would be an occlusion claim with no
        // recess behind it.
        //
        // Read from the UNMASKED wear scalar, not from `openAmt` — that array is the same scalar
        // masked to joints, and indexing chroma with it would give every stone face age 0 and
        // ship a floor with no chroma channel while the reference painter drew one.
        var tints = new double[cfg.ChromaByAge.Length][];
        for (int i = 0; i < tints.Length; i++) tints[i] = ChromaTint(cfg, i);

        // ================= POLISH: THE MASK, NOT THE BRIGHTNESS =================
        //
        // A trodden stone reflects more. That is a response to light, and it is written into a
        // separate single-channel mask that only the shader's light() pass ever reads — never
        // into the colour below. Faces only: a joint is dark because it is ENCLOSED and a crack
        // is a hole, and neither takes a shine.
        var outImg = Image.CreateEmpty(T, T, false, Image.Format.Rgb8);
        var polishImg = Image.CreateEmpty(T, T, false, Image.Format.L8);
        for (int py = 0; py < T; py++)
        {
            for (int px = 0; px < T; px++)
            {
                double L = cfg.Ladder[LadderIndex(cfg, System.Math.Clamp(
                    raw[py, px], cfg.Ladder[0], cfg.Ladder[^1]))];
                double[] t = cfg.Tint;
                double refl = 0.0;
                if (clsArr[py, px] != 0)
                {
                    int fa = AgeIndex(cfg, Wear01(cfg,
                        WearScalar(cfg, traffic, tx * T + px, ty * T + py), channelHere));
                    t = tints[fa];
                    refl = cfg.PolishByAge[fa];
                }
                outImg.SetPixel(px, py, new Color(
                    (float)(L * t[0] / 255.0), (float)(L * t[1] / 255.0),
                    (float)(L * t[2] / 255.0)));
                polishImg.SetPixel(px, py, new Color((float)refl, (float)refl, (float)refl));
            }
        }

        // THE CRACK NETWORK, drawn last so it crosses stones and joints alike. Authored pixels
        // on the family's own ladder — not an overlay, no alpha, no feather, no taper. The
        // per-tile overlay this replaces had a median mark of four pixels and blind seats
        // reported "No cracks. Not one." in captures whose log said event=44.
        if (crackCache != null)
        {
            double cv = cfg.Ladder[LadderIndex(cfg, cfg.LumMedian * cfg.CrackDepth)];
            var col = new Color((float)(cv * cfg.Tint[0] / 255.0), (float)(cv * cfg.Tint[1] / 255.0),
                                (float)(cv * cfg.Tint[2] / 255.0));
            foreach (var (ly, lx) in CrackPixels(cfg, tx, ty, crackCache))
            {
                outImg.SetPixel(lx, ly, col);
                polishImg.SetPixel(lx, ly, new Color(0, 0, 0));
            }
        }

        polish = polishImg;
        return outImg;
    }

    /// <summary>
    /// DOES THE ENGINE PRODUCE THE RIGHT PIXELS, not merely the right numbers?
    ///
    /// The edge-family and stone-offset vectors prove this code agrees with the composer about
    /// which family a boundary has and how many ladder steps a stone moves. They prove nothing
    /// about the two largest pieces of arithmetic in the painter: WHERE IN THE GRAIN BANK a stone
    /// samples, and WHICH JOINTS the arris pass rounds. Both could have been wrong in a way that
    /// produced a plausible floor, on the device, with every existing check green.
    ///
    /// So the manifest carries finished RGB for a scatter of pixels — joints, plain stone, trodden
    /// stone, and joints beside trodden stone — and this refuses to lay anything if a single one
    /// of them disagrees.
    /// </summary>
    private static string? SelfCheck(Config cfg, Image grainImg,
                                     Dictionary<int, Image> atlasCache)
    {
        if (cfg.PaintCheck.Count == 0) return null;
        var checkCracks = new Dictionary<(int, int), List<(int X, int Y)>>();
        var cols = new HashSet<int>(cfg.PaintCheckWornColumns);
        System.Func<int, int, bool> worn = (x, y) => cols.Contains(x);
        var cells = new Dictionary<(int, int), Image>();

        foreach (var s in cfg.PaintCheck)
        {
            if (!cells.TryGetValue((s.X, s.Y), out var img))
            {
                int n = EdgeFamily(s.X, s.Y, cfg.HorizSalt, cfg.Seed, cfg.Families);
                int so = EdgeFamily(s.X, s.Y + 1, cfg.HorizSalt, cfg.Seed, cfg.Families);
                int fw = EdgeFamily(s.X, s.Y, cfg.VertSalt, cfg.Seed, cfg.Families);
                int fe = EdgeFamily(s.X + 1, s.Y, cfg.VertSalt, cfg.Seed, cfg.Families);
                int idx = TileIndex(n, fe, so, fw, cfg.Families);
                if (!cfg.Atlas.TryGetValue(idx, out var path)) return
                    $"paint check: no atlas for tile index {idx} at ({s.X},{s.Y})";
                if (!atlasCache.TryGetValue(idx, out var atlas))
                {
                    atlas = LoadImage(path);
                    if (atlas == null) return $"paint check: atlas unreadable: {path}";
                    atlasCache[idx] = atlas;
                }
                img = PaintCell(cfg, atlas, grainImg, s.X, s.Y, fw, fe, cfg.CheckTraffic, worn,
                                checkCracks, out _, out _);
                cells[(s.X, s.Y)] = img;
            }
            var c = img.GetPixel(s.Px, s.Py);
            int r = (int)System.Math.Round(c.R * 255.0);
            int g = (int)System.Math.Round(c.G * 255.0);
            int bl = (int)System.Math.Round(c.B * 255.0);
            if (r != s.R || g != s.G || bl != s.B)
                return $"paint check FAILED at cell ({s.X},{s.Y}) pixel ({s.Px},{s.Py}): "
                     + $"composer says rgb({s.R},{s.G},{s.B}), engine paints rgb({r},{g},{bl}). "
                     + $"The two agree about the numbers and disagree about the picture.";
        }
        return null;
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
            cfg.WearBands = wear.GetProperty("bands").GetInt32();
            cfg.WearPits = wear.GetProperty("pits").GetInt32();
            cfg.MarkBands = wear.GetProperty("bands_ordinary").GetInt32();
            cfg.MarkPits = wear.GetProperty("pits_ordinary").GetInt32();


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
            var cba = new List<double>();
            foreach (var v in mat.GetProperty("chroma_by_age").EnumerateArray()) cba.Add(v.GetDouble());
            cfg.ChromaByAge = cba.ToArray();
            var cdir = new List<double>();
            foreach (var v in mat.GetProperty("chroma_dir").EnumerateArray()) cdir.Add(v.GetDouble());
            cfg.ChromaDir = cdir.ToArray();
            var pba = new List<double>();
            foreach (var v in mat.GetProperty("polish_by_age").EnumerateArray()) pba.Add(v.GetDouble());
            cfg.PolishByAge = pba.ToArray();
            cfg.PolishExp = mat.GetProperty("polish_exp").GetDouble();
            cfg.PolishGain = mat.GetProperty("polish_gain").GetDouble();
            // THE ONE ASSERTION THAT KEEPS THIS LEVER HONEST. At an exponent of 1.0 the specular
            // term is linear in delivered light, which is arithmetically identical to changing the
            // stone's albedo — the baked value-lift §8.2.1 bans, wearing this lever's name. It is
            // checked here rather than trusted to a comment.
            if (cfg.PolishExp <= 1.0)
                throw new System.InvalidOperationException(
                    $"polish_exp is {cfg.PolishExp}: at or below 1.0 the polish lever IS a baked "
                    + "value-lift, which §8.2.1 bans. Response modulation must be superlinear.");

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

            var cr = root.GetProperty("crack");
            cfg.CrackSalt = salts.GetProperty("crack").GetInt32();
            cfg.CrackRate = cr.GetProperty("rate").GetInt32();
            cfg.CrackMinTiles = cr.GetProperty("min_tiles").GetInt32();
            cfg.CrackMaxTiles = cr.GetProperty("max_tiles").GetInt32();
            cfg.CrackScale = cr.GetProperty("scale").GetInt32();
            cfg.CrackTurn = cr.GetProperty("turn").GetInt32();
            cfg.CrackDepth = cr.GetProperty("depth").GetDouble();
            cfg.CrackDirs = Table(cr.GetProperty("dirs"));

            var mk = root.GetProperty("marks");
            cfg.MarksSalt = salts.GetProperty("marks").GetInt32();
            cfg.MarkMinLen = mk.GetProperty("min_len").GetInt32();
            cfg.MarkMaxLen = mk.GetProperty("max_len").GetInt32();
            cfg.MarkDepth = mk.GetProperty("depth").GetDouble();
            cfg.PitDepth = mk.GetProperty("pit_depth").GetDouble();
            cfg.MarkDirs = Table(mk.GetProperty("dirs"));

            var df = root.GetProperty("differential");
            cfg.WearSalt = salts.GetProperty("wear").GetInt32();
            cfg.ChipSalt = salts.GetProperty("chip").GetInt32();
            cfg.WearOctaves = Table(df.GetProperty("octaves"));
            cfg.WearLo = df.GetProperty("lo").GetInt32();
            cfg.WearHi = df.GetProperty("hi").GetInt32();
            cfg.JointBreakSalt = salts.GetProperty("joint_break").GetInt32();
            var jf = new List<double>();
            foreach (var v in df.GetProperty("joint_fill").EnumerateArray()) jf.Add(v.GetDouble());
            cfg.JointFill = jf.ToArray();
            var jb = new List<double>();
            foreach (var v in df.GetProperty("joint_break").EnumerateArray()) jb.Add(v.GetDouble());
            cfg.JointBreak = jb.ToArray();
            cfg.ChipRate = df.GetProperty("chip_rate").GetDouble();
            cfg.DressingKeep = df.GetProperty("dressing_keep").GetDouble();
            cfg.ChannelWear = df.GetProperty("channel_wear").GetInt32();
            var ages = new List<double>();
            foreach (var v in df.GetProperty("ages").EnumerateArray()) ages.Add(v.GetDouble());
            cfg.WearAges = ages.ToArray();
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

            if (root.TryGetProperty("paint_check", out var pc))
            {
                var wc = new List<int>();
                foreach (var v in pc.GetProperty("worn_columns").EnumerateArray())
                    wc.Add(v.GetInt32());
                cfg.PaintCheckWornColumns = wc.ToArray();
                if (pc.TryGetProperty("traffic", out var tr))
                {
                    var rowsList = new List<int[]>();
                    foreach (var row in tr.EnumerateArray())
                    {
                        var vals = new List<int>();
                        foreach (var v in row.EnumerateArray()) vals.Add(v.GetInt32());
                        rowsList.Add(vals.ToArray());
                    }
                    if (rowsList.Count > 0)
                    {
                        var t = new byte[rowsList[0].Length, rowsList.Count];
                        for (int yy = 0; yy < rowsList.Count; yy++)
                            for (int xx = 0; xx < rowsList[yy].Length; xx++)
                                t[xx, yy] = (byte)rowsList[yy][xx];
                        cfg.CheckTraffic = t;
                    }
                }
                foreach (var e in pc.GetProperty("samples").EnumerateArray())
                    cfg.PaintCheck.Add((e.GetProperty("x").GetInt32(), e.GetProperty("y").GetInt32(),
                                        e.GetProperty("px").GetInt32(), e.GetProperty("py").GetInt32(),
                                        e.GetProperty("r").GetInt32(), e.GetProperty("g").GetInt32(),
                                        e.GetProperty("b").GetInt32()));
            }

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
