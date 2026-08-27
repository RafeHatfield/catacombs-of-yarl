using System.Text.Json;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Draws the incident and channel overlays <see cref="FloorIncidentPlanner"/> placed.
///
/// ART-BIBLE-v0 §8.3 divides the objects and this class draws the second one:
///
///     base tile   material only, no incident   — a tile role, picked by the theme
///     overlay     THE incident, randomised     — not a tile role at all
///
/// The overlay is not a tile role and cannot be one. A cell may carry none, one, or two
/// overlays at once, chosen per instance; `TileThemeLoader`'s schema has one id list per role
/// and no shape for that. So the family's overlay ids and placement rates live in its own
/// MANIFEST.json, which this class reads.
///
/// EACH OVERLAY IS A CHILD OF THE FLOOR SPRITE IT SITS ON, and that is the whole trick rather
/// than an implementation detail. A Godot child inherits its parent's modulate, so an overlay
/// parented to its floor tile picks up fog-of-war and `FloorComposer`'s wall-shadow darkening
/// automatically and exactly. Held as a separate layer it would need its own copy of the
/// visibility rules — and a copy is a thing that goes out of step, silently, one release later.
/// This is also why nothing here subscribes to visibility updates: there is nothing to update.
///
/// REVIEW BUILDS ONLY. Reached from the corridor review scene, which a player build never
/// enters, and gated on the marker naming a manifest.
/// </summary>
public static class Tier1FloorOverlays
{
    /// <summary>
    /// Attach overlays to an already-rendered tile layer. Returns a one-line summary for the
    /// capture log, because a scene that quietly rendered no overlays at all would look exactly
    /// like a scene whose floor has no incident in it (LOOP-PROCESS §4.2 — ask of any step what
    /// goes red if it silently does nothing).
    /// </summary>
    public static string Attach(TileLayer tileLayer, GameMap map, string manifestResPath, int seed)
    {
        var cfg = LoadConfig(manifestResPath, out string load);
        if (cfg == null) return $"floor overlays: NOT ATTACHED — {load}";

        var plan = FloorIncidentPlanner.Plan(map, cfg, seed);
        int grit = 0, events = 0, chan = 0, occl = 0, missing = 0;

        // THE RENDERER'S WHOLE-CELL WALL SHADOW IS TURNED OFF WHERE THIS FAMILY IS ACTIVE.
        //
        // `DungeonRenderer` darkens every wall-adjacent floor cell by multiplying the WHOLE
        // SPRITE by DarkFloorModulate (0.92). The intent is §12.1's contact occlusion and the
        // intent is right — it is the execution that is cell-quantised: the treatment's edge is
        // the cell's edge, and it does not vary with which side the wall is on. §8.3.1 calls
        // that a lattice and §12.1 calls it a ribbon that answers to nothing, and a blind seat
        // measured it as "hard-edged 64px squares aligned to the tile grid ... the room reads as
        // a spreadsheet of cells".
        //
        // This family draws the same occlusion by adjacency, as a gradient fading in from the
        // edge the wall is actually on. Leaving both on would double the darkening AND keep the
        // square step, so the keys are cleared: `UpdateVisibility` then has nothing to modulate
        // and the geometry-shaped version is the only one in the scene.
        int suppressed = tileLayer.DarkTileKeys.Count;
        tileLayer.DarkTileKeys.Clear();

        foreach (var (pos, inc) in plan)
        {
            if (!tileLayer.TileSprites.TryGetValue(pos, out var host) || host == null) continue;

            // Order matters and follows the material: the channel is a wash the floor was worn
            // INTO, so it goes under the loose stuff lying on top of it. Grit then sits on the
            // polished surface, and an event (a crack, a chip) is in the stone itself.
            void Draw(int id, int z, ref int counter, bool orientable)
            {
                if (id < 0) return;
                if (Add(host, cfg, id, pos, z, orientable)) counter++;
                else missing++;
            }

            Draw(inc.ChannelId, 1, ref chan, orientable: false);   // left/right mean their side
            foreach (var oid in inc.OcclusionIds)
                Draw(oid, 2, ref occl, orientable: false);         // N/E/S/W mean their edge
            Draw(inc.EventId,   3, ref events, orientable: true);
            Draw(inc.GritId,    4, ref grit,   orientable: true);
        }

        int channelCells = 0, neglected = 0;
        foreach (var inc in plan.Values)
        {
            if (inc.Channel != ChannelKind.None) channelCells++;
            if (inc.Neglected) neglected++;
        }

        return $"floor overlays: cells={plan.Count} channel={channelCells} neglected={neglected} "
             + $"drawn(grit={grit} event={events} channel={chan} occlusion={occl}) "
             + $"cell_shadow_suppressed={suppressed} missing_texture={missing} "
             + $"seed={seed} manifest={manifestResPath}\n"
             + AsciiChannelMap(map, plan);
    }

    /// <summary>
    /// The channel and the neglected cells, as an ASCII map, in the capture log.
    ///
    /// Counts alone cannot answer the question that matters about a route — WHERE does it go.
    /// The first capture reported `channel=29 neglected=6`, which is consistent both with the
    /// route running the way the scene was built for and with it running up the side passage
    /// that is supposed to be neglected. §8.2.1's channel "leads somewhere", and a number cannot
    /// say where. Seventeen by twenty-one characters can, and the log is already the place a
    /// capture carries its own evidence (LOOP-PROCESS §2.3).
    ///
    ///   L M R  the channel — its west shoulder, its middle, its east shoulder
    ///   F      a one-wide chokepoint ON the route: trodden wall to wall
    ///   .      ordinary floor, off the channel but within reach of the traffic
    ///   x      NEGLECTED: two or more cells clear of the route. §8.1 decay.
    ///   #      solid
    /// </summary>
    private static string AsciiChannelMap(GameMap map,
                                          Dictionary<(int X, int Y), FloorIncident> plan)
    {
        var sb = new System.Text.StringBuilder("[Tier1] channel map (L/M/R channel, F trodden "
                                               + "chokepoint, x neglected, . floor, # solid)\n");
        for (int y = 0; y < map.Height; y++)
        {
            sb.Append("[Tier1]   ");
            for (int x = 0; x < map.Width; x++)
            {
                if (!plan.TryGetValue((x, y), out var inc)) { sb.Append('#'); continue; }
                sb.Append(inc.Channel switch
                {
                    ChannelKind.Left  => 'L',
                    ChannelKind.Mid   => 'M',
                    ChannelKind.Right => 'R',
                    ChannelKind.Full  => 'F',
                    _ => inc.Neglected ? 'x' : '.',
                });
            }
            sb.Append('\n');
        }
        return sb.ToString().TrimEnd();
    }

    private static bool Add(Node2D host, Config cfg, int id, (int X, int Y) pos, int z,
                            bool orientable = true)
    {
        if (!cfg.Path.TryGetValue(id, out var path)) return false;
        var tex = GD.Load<Texture2D>(path);
        if (tex == null) return false;

        // Orientation per cell, by the same position hash the base variants are picked with.
        // Legal on an INCIDENT for the reason §6.3 buys: a mark authored to receive light carries
        // no direction, so there is nothing in it to break by turning it.
        //
        // ⚠ IT IS NOT LEGAL ON EVERY OVERLAY, and `orientable` is that distinction. The channel's
        // shoulders and the contact occlusion are DIRECTION-BEARING BY CONSTRUCTION — a `left`
        // shoulder flipped horizontally is a `right` shoulder, and a north-edge occlusion flipped
        // vertically lands its darkening on the south edge, against no wall at all. Flipping them
        // does not vary the field, it puts the treatment in the wrong place; and for the occlusion
        // it would also break the one thing §12.1 requires of it — that it answer to the geometry
        // it sits on. The distinction is not "which overlays look better turned", it is which ones
        // MEAN something by their orientation.
        int h = orientable
            ? Mathf.Abs((pos.X * 7919 + pos.Y * 104729 + id * 15485863) & 0x7FFFFFFF)
            : 0;
        var s = new Sprite2D
        {
            Texture       = tex,
            Centered      = false,
            Position      = Vector2.Zero,       // child space: the host tile's own origin
            ZIndex        = z,
            ZAsRelative   = true,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
            FlipH         = (h & 1) != 0,
            FlipV         = (h & 2) != 0,
        };
        host.AddChild(s);
        return true;
    }

    private sealed class Config : FloorIncidentPlanner.Config
    {
        public readonly Dictionary<int, string> Path = new();
    }

    /// <summary>
    /// Read the family's manifest. The rates come from the file the composer wrote — this class
    /// keeps no copy of them, so the engine and the offline field preview cannot disagree about
    /// what the floor looks like.
    /// </summary>
    private static Config? LoadConfig(string manifestResPath, out string status)
    {
        status = "";
        try
        {
            using var f = Godot.FileAccess.Open(manifestResPath, Godot.FileAccess.ModeFlags.Read);
            if (f == null) { status = $"manifest not found: {manifestResPath}"; return null; }

            using var doc = JsonDocument.Parse(f.GetAsText());
            var root = doc.RootElement;
            string dir = manifestResPath[..(manifestResPath.LastIndexOf('/') + 1)];

            var cfg = new Config();
            var rates = root.GetProperty("placement").GetProperty("rates");

            var gritIds = new List<int>();
            var byFamily = new Dictionary<string, List<int>>();
            foreach (var e in root.GetProperty("incident").EnumerateArray())
            {
                int id = e.GetProperty("id").GetInt32();
                string fam = e.GetProperty("family").GetString() ?? "";
                cfg.Path[id] = dir + e.GetProperty("file").GetString();
                if (fam == "grit") gritIds.Add(id);
                else
                {
                    if (!byFamily.TryGetValue(fam, out var l)) byFamily[fam] = l = new List<int>();
                    l.Add(id);
                }
            }
            foreach (var e in root.GetProperty("channel").EnumerateArray())
                cfg.Path[e.GetProperty("id").GetInt32()] = dir + e.GetProperty("file").GetString();

            cfg.GritIds = gritIds.ToArray();
            cfg.GritRate = rates.TryGetProperty("grit", out var gr) ? (float)gr.GetDouble() : 0f;

            // One id per event family, chosen per cell from that family's members. The planner
            // walks families in order and takes the FIRST that fires, which is what caps a cell
            // at one event; the rarest families are put first so a common one cannot crowd them
            // out — otherwise `wear` at 0.34 would eat most of what `crack` at 0.11 would have had.
            var ordered = new List<(string Fam, float Rate)>();
            foreach (var fam in byFamily.Keys)
                ordered.Add((fam, rates.TryGetProperty(fam, out var r) ? (float)r.GetDouble() : 0f));
            ordered.Sort((p, q) => p.Rate.CompareTo(q.Rate));

            var eventIds = new List<int>();
            var eventRates = new List<float>();
            foreach (var (fam, rate) in ordered)
            {
                foreach (var id in byFamily[fam]) { eventIds.Add(id); eventRates.Add(rate / byFamily[fam].Count); }
            }
            cfg.EventIds = eventIds.ToArray();
            cfg.EventRates = eventRates.ToArray();

            var chan = new List<int>();
            foreach (var e in root.GetProperty("channel").EnumerateArray())
                chan.Add(e.GetProperty("id").GetInt32());
            cfg.ChannelIds = chan.ToArray();

            if (root.TryGetProperty("occlusion", out var occArr))
            {
                var occIds = new List<int>();
                foreach (var e in occArr.EnumerateArray())
                {
                    int id = e.GetProperty("id").GetInt32();
                    cfg.Path[id] = dir + e.GetProperty("file").GetString();
                    occIds.Add(id);
                }
                cfg.OcclusionIds = occIds.ToArray();
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
