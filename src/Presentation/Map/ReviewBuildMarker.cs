using Godot;
using System.Text.Json;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// Tier 0 review-build marker (ART-BIBLE-v0 §13.1).
///
/// §13.1 requires the verdict to come from the production renderer, in the lit scene, at true
/// display size, ON DEVICE. That last word is the problem this class solves: the review corridor
/// is otherwise reachable only via --corridor-scene, and an iOS app is launched by the OS with
/// no command line at all. Without this, the app could be verified installed on the reference
/// device and still have no way to display the corridor — the device leg of the harness would be
/// an install check wearing a review check's clothes.
///
/// A REVIEW BUILD is therefore identified by a data file baked into the export. If
/// res://src/Presentation/assets/tier0_harness/REVIEW_BUILD.json exists at boot, the app boots
/// straight into the review corridor with the rig that file names. If it does not exist — which
/// is every normal build, because only the harness writes it — nothing here runs and boot is
/// bit-for-bit unchanged. The file is deliberately NOT committed; only REVIEW_BUILD.json.template
/// is, so a review build cannot be created by accident or leak into a player build.
///
/// The rig is carried in the file rather than defaulted in code for the same reason
/// <see cref="ReviewLighting"/> refuses defaults: §6.2 marks the light values PLACEHOLDER, and a
/// default compiled into the engine would quietly become the derived value.
/// </summary>
public sealed class ReviewBuildMarker
{
    public const string Path = "res://src/Presentation/assets/tier0_harness/REVIEW_BUILD.json";

    public string ScenePath { get; private init; } = "";
    public string ThemeConfigPath { get; private init; } = "";
    public ReviewLighting.Params Light { get; private init; }

    /// <summary>
    /// res:// path to a floor family's MANIFEST.json, or null. Present because ART-BIBLE-v0
    /// §8.3's overlays are NOT a tile role — a cell may carry none, one or two of them, chosen
    /// per instance — so they cannot be selected the way `themeConfig` selects tiles, and a
    /// review build has no command line to pass them on. Absent, the scene draws base tiles
    /// only, which is exactly what every review build before tier one did.
    /// </summary>
    public string? FloorOverlays { get; private init; }

    /// <summary>
    /// res:// path to the EDGE-MATCHED floor family's MANIFEST.json, or null. Separate from
    /// <see cref="FloorOverlays"/> because they are different objects: the overlays are the
    /// incident placed per instance, this is the BASE tile set whose edges must agree with the
    /// edges of their neighbours.
    /// </summary>
    public string? WangFloor { get; private init; }
    public string? AshlarFloor { get; private init; }

    /// <summary>
    /// The commit the build was made from, and when — stamped into the marker by
    /// build_review_app.sh. LOOP-PROCESS §2.3: evidence carries its producer's hash, and a
    /// hash mismatch at a ruling invalidates the evidence. Headless captures have always
    /// stamped their commit; the DEVICE BUILD did not, so the one artefact that decides
    /// anything (§13.1) was the one that could not say what it was made from.
    /// </summary>
    public string? Commit { get; private init; }
    public string? BuiltAt { get; private init; }

    /// <summary>
    /// Tile size and integer scale for the review build, mirroring --tile-size / --tile-scale.
    ///
    /// These exist for the same reason the light values do, and the omission would have been
    /// the same bug: an iOS app receives no command line, so a device build had no way to be
    /// told the grid. It would have rendered at the renderer's default 24 while the desktop
    /// captures it is meant to be compared against were taken at 32 — and nothing would have
    /// said so. The device and the capture must be lit by the same rig AND drawn on the same
    /// grid, or they are not comparable and the §13.1 verdict is taken on the wrong picture.
    ///
    /// Null means "not stated in the marker", and the renderer's own defaults apply.
    /// </summary>
    public int? TileSize { get; private init; }
    public float? TileScale { get; private init; }

    private static ReviewBuildMarker? _cached;
    private static bool _looked;

    /// <summary>
    /// True when this is a review build. Result is cached: boot asks twice (once for the theme
    /// override, once for the scene) and the file must not be read differently between them.
    /// </summary>
    public static bool TryLoad(out ReviewBuildMarker? marker)
    {
        if (_looked)
        {
            marker = _cached;
            return _cached != null;
        }
        _looked = true;
        marker = null;

        if (!Godot.FileAccess.FileExists(Path))
            return false;

        try
        {
            using var f = Godot.FileAccess.Open(Path, Godot.FileAccess.ModeFlags.Read);
            if (f == null) return false;

            using var doc = JsonDocument.Parse(f.GetAsText());
            var root = doc.RootElement;
            var light = root.GetProperty("light");

            _cached = new ReviewBuildMarker
            {
                ScenePath       = root.GetProperty("scene").GetString() ?? "",
                ThemeConfigPath = root.GetProperty("themeConfig").GetString() ?? "",
                // EVERY RIG VALUE IS REQUIRED. No key here has a fallback.
                //
                // The first version of this defaulted falloff and ambientLevel to the identity
                // "so a marker written before Ruling 56 still boots to the rig it was built
                // with". That reasoning is wrong and it is the exact failure the same session
                // spent a commit message warning about: a ratified value that can be silently
                // defaulted is a ratified value that can silently drift. A pre-ruling marker
                // SHOULD fail here — it describes a rig that is no longer law, and booting it
                // quietly under the ratified rig's name is how a walk gets taken through numbers
                // nobody decided.
                //
                // GetProperty throws when the key is absent; TryLoad's catch reports it and the
                // app boots the menu instead of the corridor, which is a loud, visible failure
                // rather than a silent substitution.
                Light = new ReviewLighting.Params(
                    Ambient:      new Color(light.GetProperty("ambient").GetString()),
                    LightColor:   new Color(light.GetProperty("color").GetString()),
                    Energy:       (float)light.GetProperty("energy").GetDouble(),
                    RadiusTiles:  (float)light.GetProperty("radiusTiles").GetDouble(),
                    Falloff:      (float)light.GetProperty("falloff").GetDouble(),
                    AmbientLevel: (float)light.GetProperty("ambientLevel").GetDouble()),
                FloorOverlays = root.TryGetProperty("floorOverlays", out var fo)
                            ? fo.GetString() : null,
                WangFloor = root.TryGetProperty("wangFloor", out var wf) ? wf.GetString() : null,
                AshlarFloor = root.TryGetProperty("ashlarFloor", out var af) ? af.GetString() : null,
                Commit  = root.TryGetProperty("commit",  out var cm) ? cm.GetString() : null,
                BuiltAt = root.TryGetProperty("builtAt", out var ba) ? ba.GetString() : null,
                TileSize  = root.TryGetProperty("tileSize", out var ts)
                            ? ts.GetInt32() : (int?)null,
                TileScale = root.TryGetProperty("tileScale", out var sc)
                            ? (float)sc.GetDouble() : (float?)null,
            };
        }
        catch (System.Exception ex)
        {
            // A malformed marker must not silently boot the normal game: a reviewer would then be
            // looking at the menu and wondering where the corridor went.
            GD.PrintErr($"[Tier0] REVIEW_BUILD.json present but unreadable — {ex.Message}");
            return false;
        }

        marker = _cached;
        return marker != null;
    }
}
