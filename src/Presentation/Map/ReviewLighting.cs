using Godot;

namespace CatacombsOfYarl.Presentation.Map;

/// <summary>
/// The Tier 0 light rig: ambient darkness plus one carried warm point light.
///
/// ART-BIBLE-v0 §6.1 rules that lighting is engine-rendered, not painted in, and §6.3 rules
/// that assets are authored to RECEIVE light rather than depict it. §6.3 also states the
/// consequence that makes this class a prerequisite rather than a nicety: a receive-light asset
/// looks flat and slightly disappointing when captured unlit, so a capture without a light rig
/// judges the candidate with the wrong instrument.
///
/// §6.2 gives the Boundary region its character — "carried fire; warm, moving, unreliable" —
/// and then says in terms: "Only the Boundary's values are derived at the pilot. The rest are
/// PLACEHOLDER." No numeric value in this file is therefore law. Every one of them is a
/// constructor parameter supplied by the harness config and echoed into the capture log, so
/// that a reader of any capture can see exactly which unratified values produced it. This class
/// deliberately declares no default: a caller must state its numbers, because a default here
/// would become a de facto derived value by the back door.
///
/// The light texture is a procedurally-generated radial falloff, not an art asset. It is a
/// lighting primitive with no palette, no register, and nothing to judge; generating it here
/// keeps the harness free of any authored art, per this session's scope.
/// </summary>
public sealed class ReviewLighting
{
    /// <summary>
    /// All values UNDERIVED per §6.2/§4.3. Carried as a record so the exact rig that produced a
    /// capture can be logged verbatim and reproduced.
    /// </summary>
    public readonly record struct Params(
        Color Ambient,       // CanvasModulate colour — the darkness the light is read against
        Color LightColor,    // carried-fire tint (§6.2 Boundary: warm)
        float Energy,        // PointLight2D energy; 0.0 is the "lighting is live" control
        float RadiusTiles);  // reach of the carried light, in tiles — NOT in pixels, because
                             // §4.3 marks tile size PLACEHOLDER and a pixel radius would silently
                             // hard-code one

    private readonly Params _p;
    private CanvasModulate? _ambient;
    private PointLight2D? _light;

    public ReviewLighting(Params p) => _p = p;

    /// <summary>
    /// Attach the rig under the world node. UI lives on separate CanvasLayers, each of which is
    /// its own canvas, so a CanvasModulate here darkens the dungeon and leaves the HUD alone.
    /// </summary>
    public void Attach(Node2D gameView, int tileWidth, int tileHeight, int playerTileX, int playerTileY)
    {
        _ambient = new CanvasModulate { Name = "ReviewAmbient", Color = _p.Ambient };
        gameView.AddChild(_ambient);

        int texSize = ResolveTextureSize(tileWidth, tileHeight);

        _light = new PointLight2D
        {
            Name         = "ReviewCarriedLight",
            Texture      = BuildRadialFalloff(texSize),
            Color        = _p.LightColor,
            Energy       = _p.Energy,
            TextureScale = 1.0f,
            BlendMode    = Light2D.BlendModeEnum.Add,
            // Centre on the player's tile, not its corner: the carried light is held by the
            // figure, and a half-tile offset is visible at true display size.
            Position     = new Vector2(playerTileX * tileWidth  + tileWidth  / 2f,
                                       playerTileY * tileHeight + tileHeight / 2f),
            ZIndex       = 0,
        };
        gameView.AddChild(_light);
    }

    /// <summary>
    /// Texture diameter in pixels for the configured radius. Derived from the tile size the
    /// renderer is actually using rather than from any constant in this file — tile size is a
    /// parameter here, per §4.3.
    /// </summary>
    private int ResolveTextureSize(int tileWidth, int tileHeight)
    {
        float tile = Mathf.Max(tileWidth, tileHeight);
        int size = Mathf.RoundToInt(_p.RadiusTiles * tile * 2f);
        return Mathf.Max(size, 2);
    }

    /// <summary>
    /// Radial falloff, generated per-pixel. Smoothstep rather than linear so the edge of the
    /// carried light does not read as a hard disc at true display size.
    /// </summary>
    private static Texture2D BuildRadialFalloff(int size)
    {
        var img = Image.CreateEmpty(size, size, false, Image.Format.Rgba8);
        float r = size / 2f;
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                float dx = (x + 0.5f) - r;
                float dy = (y + 0.5f) - r;
                float d  = Mathf.Sqrt(dx * dx + dy * dy) / r;   // 0 at centre, 1 at edge
                float a  = d >= 1f ? 0f : 1f - Mathf.SmoothStep(0f, 1f, d);
                img.SetPixel(x, y, new Color(1f, 1f, 1f, a));
            }
        }
        return ImageTexture.CreateFromImage(img);
    }

    /// <summary>One line, written into the capture log so a capture carries its own rig.</summary>
    public string Describe(int tileWidth, int tileHeight)
        => $"ambient={_p.Ambient.ToHtml(false)} light={_p.LightColor.ToHtml(false)} " +
           $"energy={_p.Energy:0.###} radius_tiles={_p.RadiusTiles:0.###} " +
           $"tile={tileWidth}x{tileHeight} tex={ResolveTextureSize(tileWidth, tileHeight)}px " +
           $"(ALL VALUES UNDERIVED — ART-BIBLE-v0 §6.2/§4.3 PLACEHOLDER)";
}
