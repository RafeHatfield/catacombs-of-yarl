using System.Linq;
using System.Text.Json;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Lays the tier-one Boundary WALL family, and the void beyond it.
///
/// It replaces the theme's wall sprite on every wall cell, exactly the way
/// <see cref="Tier1AshlarFloor"/> replaces the floor's, and for three reasons that the theme's
/// mask table cannot serve.
///
/// ── 1. THE MASK TABLE DRAWS A FRONT FACE WHERE THERE IS NO REVEAL ────────────────────────────
/// ART-BIBLE-v0 §3: a tile shows a front face exactly where floor lies to its SOUTH.
/// `DungeonRenderer` collapses cardinal masks 7 and 11 both to 3 — and mask 7 is a wall whose
/// SOUTH NEIGHBOUR IS WALL (floor lies north of it), while mask 3's south neighbour is floor. One
/// tile therefore serves two opposite geometries, and on the face side it draws a reveal into the
/// middle of a solid mass. Measured on the four review specs: **13 in-map cells per scene** plus
/// the whole top border row — the south walls of every room, which is the most-looked-at wall in
/// any of them.
///
/// The collapse is not a bug in the renderer; its comment says plainly that it was fitted to the
/// old sandstone tileset, where masks 194–197 drew directional T-junctions that looked wrong on
/// plain room edges. It is a bug *here*, under §3, and it could not have been seen before now:
/// the walls in every capture so far have been magenta programmer-art mocks with no planes in
/// them at all. **This class computes the cardinal mask itself, without the collapse.**
///
/// ── 2. EDGE MATCHING NEEDS THE NEIGHBOURS, AND `PickVariant` CANNOT SEE THEM ──────────────────
/// §8.3.2 makes edge-matched sets legal — *matching is agreement, not constancy* — and a run of
/// masonry only reads as one wall if the block crossing a tile boundary is drawn the same on both
/// sides of it. `TileThemeConfig.PickVariant` chooses from a position hash, so two neighbours
/// choose independently and a crossing block is a coin flip. Here the tile is chosen by the two
/// BOUNDARY keys it shares with its neighbours, so both tiles read the same key and draw the same
/// block: the seam is zero rather than small.
///
/// ── 3. THE VOID IS NOT A WALL ────────────────────────────────────────────────────────────────
/// A cell with no floor anywhere near it is not masonry anybody can see — it is the dark beyond
/// the room. Drawing it as stone spends the scene's whole value range on rock nobody looks at and
/// leaves the wall that bounds the room reading as a bright ribbon around a floor. So wall cells
/// are laid in RINGS: ring 1 is the wall a room actually has, and everything past `void_ring` is
/// void.
///
/// **`void_ring` STARTED AT 2 AND THE SEATS MOVED IT TO 1.** Two came from `WALL-RECIPE.md` §2.2's
/// measured *"every room boundary in the bar is two tiles or more"* — which is a statement about
/// MAP GEOMETRY, and was read here as one about how many rings are drawn as lit stone. Round 2's
/// seat found the consequence: *"More of the same stuff … it is wall, and it goes on. What it is
/// NOT is dark."* At two rings the void only appears where a mass is five cells deep or more, and
/// an ordinary dungeon's masses are two to four — so the darkness beyond the walls would
/// essentially never be seen. The map still has its two cells of mass; you simply cannot see
/// through the first one, which is also what a lamp at floor level actually shows you.
///
/// ⚠ **THE VOID VALUE IS NOT RULED HERE.** Three candidates ship and the panel switches between
/// them; §13.1 gives the choice to Rafe, in scene, on the device.
///
/// ⚠ **NO CONTACT SEAM IS DRAWN BY THIS CLASS.** §12.1 makes plane-boundary occlusion mandatory
/// and `WALL-RECIPE.md` §3.1 measured where it belongs — on the FLOOR cell, which is the one that
/// knows what adjoins it. `Tier1FloorOverlays` already draws it per edge. Adding a second copy on
/// the wall side would double the darkening and put a dark edge on every side of every wall tile,
/// which is the definition of a ring.
/// </summary>
public static class Tier1BoundaryWall
{
    private const int T = 32;

    private sealed class Config
    {
        public string Family = "";
        public string Root = "";
        public int Families = 3;
        public int SaltV, SaltH;
        public int VoidRing = 2;
        public int Variants = 1;
        public readonly Dictionary<string, int> Face = new();
        public readonly Dictionary<string, int> TopH = new();
        public readonly Dictionary<string, int> TopV = new();
        public readonly List<int> Void = new();
        public readonly List<(int Salt, string Tag, int X, int Y, int Expect)> EdgeCheck = new();
        public double TopValue, FaceValue;
    }

    /// <summary>FNV-1a 64 over "salt:tag:x:y" — the composer's arithmetic, restated.</summary>
    private static ulong Fnv(int salt, string tag, int x, int y)
    {
        ulong h = 0xCBF29CE484222325UL;
        void Feed(string s)
        {
            foreach (char c in s) h = (h ^ (byte)c) * 0x100000001B3UL;
            h = (h ^ 0x3A) * 0x100000001B3UL;
        }
        Feed(salt.ToString(System.Globalization.CultureInfo.InvariantCulture));
        Feed(tag);
        Feed(x.ToString(System.Globalization.CultureInfo.InvariantCulture));
        Feed(y.ToString(System.Globalization.CultureInfo.InvariantCulture));
        return h;
    }

    private static int Key(Config c, int salt, string tag, int x, int y)
        => (int)(Fnv(salt, tag, x, y) % (ulong)c.Families);

    private static Config? Load(string resPath, out string status)
    {
        status = "";
        using var f = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Read);
        if (f == null) { status = $"manifest unreadable: {resPath}"; return null; }
        var doc = JsonDocument.Parse(f.GetAsText());
        var r = doc.RootElement;
        var c = new Config
        {
            Family = r.GetProperty("family").GetString() ?? "",
            Root = resPath.Substring(0, resPath.LastIndexOf('/') + 1),
            Families = r.GetProperty("edge_families").GetInt32(),
            VoidRing = r.TryGetProperty("void_ring", out var vr) ? vr.GetInt32() : 2,
            SaltV = r.GetProperty("salts").GetProperty("v").GetInt32(),
            SaltH = r.GetProperty("salts").GetProperty("h").GetInt32(),
            TopValue = r.GetProperty("planes").GetProperty("top_value").GetDouble(),
            FaceValue = r.GetProperty("planes").GetProperty("face_value").GetDouble(),
        };
        c.Variants = r.GetProperty("variants").GetInt32();
        var table = r.GetProperty("table");
        foreach (var e in table.GetProperty("face").EnumerateObject()) c.Face[e.Name] = e.Value.GetInt32();
        foreach (var e in table.GetProperty("top_h").EnumerateObject()) c.TopH[e.Name] = e.Value.GetInt32();
        foreach (var e in table.GetProperty("top_v").EnumerateObject()) c.TopV[e.Name] = e.Value.GetInt32();
        foreach (var e in table.GetProperty("void").EnumerateObject()) c.Void.Add(e.Value.GetInt32());
        foreach (var e in r.GetProperty("edge_check").EnumerateArray())
        {
            var a = e.EnumerateArray().ToArray();
            c.EdgeCheck.Add((a[0].GetInt32(), a[1].GetString() ?? "", a[2].GetInt32(),
                             a[3].GetInt32(), a[4].GetInt32()));
        }
        // Tile ids are laid out by the composer's own file naming; the manifest carries the file
        // for each id so nothing here has to guess a pattern.
        foreach (var t in r.GetProperty("tiles").EnumerateArray())
            _files[t.GetProperty("id").GetInt32()] = t.GetProperty("file").GetString() ?? "";
        return c;
    }

    private static readonly Dictionary<int, string> _files = new();

    /// <summary>
    /// How many void candidates the last-applied family shipped. Read by the rig panel so the
    /// toggle offers exactly the candidates that exist rather than a hard-coded three — a panel
    /// that offered a fourth would be proposing a value, and the void is Rafe's to rule.
    /// </summary>
    public static int LastVoidCount { get; private set; }

    /// <summary>
    /// Does a ring-1 neighbour on the given axis face floor across that axis?
    ///
    /// Ring 2 stands behind ring 1 and has no floor of its own to be parallel to. It takes the
    /// orientation of the cell it backs, so a wall's two courses agree instead of crossing —
    /// which is what a two-stone-thick wall actually looks like from above.
    /// </summary>
    private static bool HasNeighbourFacing(GameMap map, int x, int y, bool vertical)
    {
        foreach (var (dx, dy) in vertical ? new[] { (-1, 0), (1, 0) } : new[] { (0, -1), (0, 1) })
        {
            int nx = x + dx, ny = y + dy;
            if (!map.InBounds(nx, ny) || !map.IsWallTile(nx, ny)) continue;
            if (vertical)
            {
                if ((map.InBounds(nx - 1, ny) && !map.IsWallTile(nx - 1, ny))
                 || (map.InBounds(nx + 1, ny) && !map.IsWallTile(nx + 1, ny))) return true;
            }
            else
            {
                if ((map.InBounds(nx, ny - 1) && !map.IsWallTile(nx, ny - 1))
                 || (map.InBounds(nx, ny + 1) && !map.IsWallTile(nx, ny + 1))) return true;
            }
        }
        return false;
    }

    /// <summary>Chebyshev distance to the nearest walkable cell, capped — which ring this is.</summary>
    private static int RingOf(GameMap map, int x, int y, int cap)
    {
        for (int r = 1; r <= cap; r++)
            for (int dy = -r; dy <= r; dy++)
                for (int dx = -r; dx <= r; dx++)
                {
                    if (System.Math.Max(System.Math.Abs(dx), System.Math.Abs(dy)) != r) continue;
                    if (!map.IsWallTile(x + dx, y + dy) && map.InBounds(x + dx, y + dy)) return r;
                }
        return cap + 1;
    }

    private const string BindNode = "Tier1Binding";

    private sealed class Bindings
    {
        public string Root = "";
        public double FaceRate, TopRate;
        public readonly List<(int Id, string Kind, string Plane, string File)> Tiles = new();
    }

    private static Bindings? LoadBindings(string resPath, out string status)
    {
        status = "";
        using var f = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Read);
        if (f == null) { status = $"binding manifest unreadable: {resPath}"; return null; }
        var doc = JsonDocument.Parse(f.GetAsText());
        var r = doc.RootElement;
        var b = new Bindings
        {
            Root = resPath.Substring(0, resPath.LastIndexOf('/') + 1),
            FaceRate = r.GetProperty("rates").GetProperty("face").GetDouble(),
            TopRate = r.GetProperty("rates").GetProperty("top").GetDouble(),
        };
        foreach (var t in r.GetProperty("tiles").EnumerateArray())
            b.Tiles.Add((t.GetProperty("id").GetInt32(),
                         t.GetProperty("kind").GetString() ?? "",
                         t.GetProperty("plane").GetString() ?? "",
                         t.GetProperty("file").GetString() ?? ""));
        return b;
    }

    public static string Apply(TileLayer tileLayer, GameMap map, string manifestResPath,
                               int voidChoice, string? bindingManifest = null)
    {
        var cfg = Load(manifestResPath, out string status);
        if (cfg == null) return $"[Tier1] boundary wall: NOT APPLIED — {status}";

        // THE CROSS-CHECK, BEFORE ANYTHING IS LAID. The composer and this class each compute the
        // boundary keys; if they disagree, every crossing block is drawn from two different
        // halves and the run stops being masonry. A duplicate with an enforcement is a different
        // thing from a duplicate with a comment.
        foreach (var (salt, tag, x, y, expect) in cfg.EdgeCheck)
        {
            int got = Key(cfg, salt, tag, x, y);
            if (got != expect)
                return $"[Tier1] boundary wall: REFUSED — edge-family cross-check failed at "
                     + $"({x},{y}) salt={salt} tag={tag}: composer said {expect}, engine says {got}.";
        }

        if (cfg.Void.Count == 0) return "[Tier1] boundary wall: REFUSED — no void candidates.";
        LastVoidCount = cfg.Void.Count;
        int vc = System.Math.Clamp(voidChoice, 0, cfg.Void.Count - 1);

        Bindings? bind = null;
        string bindStatus = "none declared";
        if (bindingManifest is { Length: > 0 })
        {
            bind = LoadBindings(bindingManifest, out bindStatus);
            if (bind == null) return $"[Tier1] boundary wall: REFUSED — {bindStatus}";
        }

        int face = 0, top = 0, voidCells = 0, missing = 0, faceSuppressed = 0;
        int bound = 0;
        var boundKinds = new Dictionary<string, int>();
        for (int y = 0; y < map.Height; y++)
        {
            for (int x = 0; x < map.Width; x++)
            {
                if (!map.IsWallTile(x, y)) continue;
                if (!tileLayer.TileSprites.TryGetValue((x, y), out var node) || node is not Sprite2D s)
                    continue;

                int ring = RingOf(map, x, y, cfg.VoidRing);
                bool southOpenCache = !map.IsWallTile(x, y + 1) && map.InBounds(x, y + 1);
                int id;
                if (ring > cfg.VoidRing)
                {
                    id = cfg.Void[vc];
                    voidCells++;
                }
                else
                {
                    // §3, computed here rather than read off the collapsed mask: a face exists
                    // exactly where the SOUTH neighbour is not wall.
                    bool southOpen = southOpenCache;
                    // Ring 2 never shows a face: its south neighbour is ring-1 wall by
                    // construction, so the test above already refuses it. Counted anyway, because
                    // a number that is always zero is the cheapest possible regression test.
                    if (!southOpen && ring == 1) faceSuppressed++;

                    // WHICH WAY THE COURSES RUN. A mason lays them parallel to the face, so the
                    // orientation follows the direction of the floor this wall bounds: floor to
                    // the north or south means the wall runs east-west, floor to the east or west
                    // means it runs north-south. Decided here rather than baked, because the same
                    // material has to serve both and an edge-matched tile cannot be rotated at
                    // run time without relabelling its own edges (§8.3.3).
                    bool ns = (!map.IsWallTile(x, y - 1) && map.InBounds(x, y - 1))
                              || southOpenCache;
                    bool ew = (!map.IsWallTile(x - 1, y) && map.InBounds(x - 1, y))
                              || (!map.IsWallTile(x + 1, y) && map.InBounds(x + 1, y));
                    if (ring > 1)
                    {
                        // Ring 2 has no floor of its own to face; it takes the orientation of the
                        // ring-1 cell it stands behind, so a wall's two courses agree.
                        ns = HasNeighbourFacing(map, x, y, vertical: false);
                        ew = HasNeighbourFacing(map, x, y, vertical: true);
                    }
                    bool horizontal = ns || !ew;   // ties go to east-west, the commoner run

                    int ka, kb;
                    if (horizontal)
                    {
                        ka = Key(cfg, cfg.SaltV, "v", x, y);
                        kb = Key(cfg, cfg.SaltV, "v", x + 1, y);
                    }
                    else
                    {
                        ka = Key(cfg, cfg.SaltH, "h", x, y);
                        kb = Key(cfg, cfg.SaltH, "h", x, y + 1);
                    }
                    int var = (int)(Fnv(90777, horizontal ? "h" : "v", x, y) % (ulong)cfg.Variants);
                    string k = $"{ka},{kb},{var}";
                    var tbl = southOpen ? cfg.Face : (horizontal ? cfg.TopH : cfg.TopV);
                    if (!tbl.TryGetValue(k, out id)) { missing++; continue; }
                    if (southOpen) face++; else top++;
                }

                if (!_files.TryGetValue(id, out var file)) { missing++; continue; }
                var tex = GD.Load<Texture2D>(cfg.Root + file);
                if (tex == null) { missing++; continue; }
                s.Texture = tex;
                // A wall tile carries no orientation: flipping one relabels its edges and it stops
                // agreeing with its neighbours (§8.3.3's recorded cost of edge matching).
                s.FlipH = false;
                s.FlipV = false;

                // ── THE ORC LAYER ────────────────────────────────────────────────────────────
                // Placed here, per cell, from the cell's WORLD ADDRESS — never baked into the
                // segment. §8.3.1: a binding drawn into a tile is a binding on every cell that
                // tile lands on, which is thirty identical repairs to a wall nobody repaired
                // thirty times.
                var old = s.GetNodeOrNull<Sprite2D>(BindNode);
                if (old != null) { s.RemoveChild(old); old.QueueFree(); }
                if (bind != null && ring == 1)
                {
                    string plane = southOpenCache ? "face" : "top";
                    double rate = southOpenCache ? bind.FaceRate : bind.TopRate;
                    // A separate salt from the tile keys, so a cell's binding is independent of
                    // the tile it landed on. Sharing one would correlate the two and put the same
                    // strap on the same tile every time — §8.3.1 arriving one level up.
                    ulong r = Fnv(90210, plane, x, y);
                    if ((r % 1000) < (ulong)(rate * 1000))
                    {
                        var pool = bind.Tiles.Where(t => t.Plane == plane).ToList();
                        if (pool.Count > 0)
                        {
                            var pick = pool[(int)(Fnv(90211, plane, x, y) % (ulong)pool.Count)];
                            var btex = GD.Load<Texture2D>(bind.Root + pick.File);
                            if (btex != null)
                            {
                                var bs = new Sprite2D
                                {
                                    Name = BindNode, Texture = btex, Centered = true,
                                    TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
                                    ZIndex = 1,
                                };
                                s.AddChild(bs);
                                bound++;
                                boundKinds[pick.Kind] = boundKinds.GetValueOrDefault(pick.Kind) + 1;
                            }
                        }
                    }
                }
            }
        }

        string kinds = boundKinds.Count == 0 ? "-"
            : string.Join(",", boundKinds.OrderBy(k => k.Key).Select(k => $"{k.Key}:{k.Value}"));
        return $"[Tier1] boundary wall: family={cfg.Family} face={face} top={top} "
             + $"void={voidCells}(choice={vc},ring>{cfg.VoidRing}) missing={missing} "
             + $"face_suppressed={faceSuppressed} "
             + $"planes(top={cfg.TopValue:0.##} face={cfg.FaceValue:0.##}) "
             + $"edge_check={cfg.EdgeCheck.Count}/OK bindings={bound}({kinds}) "
             + $"manifest={manifestResPath}";
    }
}
