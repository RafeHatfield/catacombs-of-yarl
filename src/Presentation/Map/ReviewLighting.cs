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
/// PLACEHOLDER." No numeric value in this file is therefore law. Every one of them is supplied
/// by the harness config or the review marker and echoed into the capture log, so that a reader
/// of any capture can see exactly which unratified values produced it. This class deliberately
/// declares no default rig: a caller must state its numbers, because a default here would
/// become a de facto derived value by the back door.
///
/// The light texture is a procedurally-generated radial falloff, not an art asset. It is a
/// lighting primitive with no palette, no register, and nothing to judge.
///
/// ---------------------------------------------------------------------------------------
/// §6.2.1 — THE TIER-ONE PRECONDITION. Why this class became live and tunable.
/// ---------------------------------------------------------------------------------------
/// RULED (Rafe, 2026-08-27, at the device gate):
///
///     The §6.2 rig values — radius, falloff, ambient — get a readability-tuning pass before
///     any asset is judged through them. The value stack must be legible at GAMEPLAY DISTANCE,
///     not at two tiles. This is a precondition, not a task: no tier-one asset round starts
///     until it is done.
///
/// A tuning pass needs the numbers to move while someone is looking at the scene, on the device,
/// so <see cref="Radius"/>, <see cref="Falloff"/> and <see cref="AmbientLevel"/> are settable at
/// run time and <see cref="ReviewRigPanel"/> puts them behind on-screen controls.
///
/// EVERY DEFAULT HERE REPRODUCES THE PREVIOUS RIG EXACTLY. Falloff 1.0 is the plain smoothstep
/// this class has always drawn; AmbientLevel 1.0 is the marker's ambient colour unscaled. The
/// session that added the knobs does not get to move them — §6.2.1 gives that pass to Rafe, and
/// a builder who nudged a number "to make it look right" would be ratifying the rig by the back
/// door and re-firing §6.2's re-derivation rule without anybody deciding to.
///
/// ---------------------------------------------------------------------------------------
/// ⚠ AND THE LAMP DID NOT FOLLOW THE PLAYER. Fixed here; recorded because it is a finding.
/// ---------------------------------------------------------------------------------------
/// <c>Attach</c> positioned the light at the player's spawn tile and the instance was then
/// dropped on the floor — no reference kept, no update anywhere. Every headless capture was
/// taken on the spawn frame, so captures were correct and nothing went red. **The device WALK
/// was not.** Walking moved the figure out of a stationary pool of light.
///
/// It matters more than a nicety because §6.5's entire derivation rests on the premise:
/// *"the player IS the lamp, and stands south of a north wall — so the face is always one tile
/// nearer the light than its own top."* A lamp anchored to the spawn tile does not deliver that
/// relationship anywhere except at spawn, and §6.2.1's pass — legibility ACROSS the lit radius,
/// at gameplay distance — cannot be run through it at all. <see cref="Follow"/> closes it.
/// </summary>
public sealed class ReviewLighting
{
    /// <summary>
    /// The rig, carried as a record so the exact values that produced a capture can be logged
    /// verbatim and reproduced. RULED for the Boundary (§6.2.1, Ruling 56, 2026-08-28); still
    /// PLACEHOLDER for every other region, which derives its own at its own gate.
    /// </summary>
    public readonly record struct Params(
        Color Ambient,        // CanvasModulate hue — the darkness the light is read against
        Color LightColor,     // carried-fire tint (§6.2 Boundary: warm)
        float Energy,         // PointLight2D energy; 0.0 is the "lighting is live" control
        float RadiusTiles,    // reach of the carried light, in TILES, not pixels — §4.3 marks
                              // tile size PLACEHOLDER and a pixel radius would hard-code one
        float Falloff,        // shape of the radial ramp. 1.00 is the plain smoothstep — the
                              // identity curve, and RULED as such (§6.2.1, Ruling 56).
        float AmbientLevel);  // scales Ambient's brightness, hue held. RULED at 0.70.

    // ⚠ NO PARAMETER HERE HAS A C# DEFAULT, and that is deliberate rather than an oversight.
    //
    // Falloff and AmbientLevel were declared with `= 1.0f` when they were introduced, so that
    // adding them broke no caller. Once Ruling 56 made them law that convenience became the
    // hazard: a caller omitting them would be silently lit by the identity while claiming the
    // ratified rig. Removing the defaults makes the compiler the enforcement — every construction
    // site must state all six values, which is the same discipline the engine already applies to
    // its command line.

    // Knob ranges. NOT art values and NOT rig values — they are the ends of the travel the
    // review panel offers, wide enough that Rafe's pass is not fenced in by a builder's guess
    // at the answer. §6.2.1 gives the pass to the human; this only decides how far the dial goes.
    public const float MinRadius = 2.0f,  MaxRadius = 14.0f, RadiusStep = 0.5f;
    public const float MinFalloff = 0.30f, MaxFalloff = 4.0f, FalloffStep = 0.1f;
    public const float MinAmbient = 0.0f,  MaxAmbient = 4.0f, AmbientStep = 0.1f;

    private Params _p;
    private CanvasModulate? _ambient;
    private PointLight2D? _light;
    private int _tileW = 1, _tileH = 1;

    public ReviewLighting(Params p) => _p = p;

    public Params Current => _p;

    /// <summary>
    /// Attach the rig under the world node. UI lives on separate CanvasLayers, each of which is
    /// its own canvas, so a CanvasModulate here darkens the dungeon and leaves the HUD alone.
    /// </summary>
    public void Attach(Node2D gameView, int tileWidth, int tileHeight, int playerTileX, int playerTileY)
    {
        _tileW = tileWidth;
        _tileH = tileHeight;

        _ambient = new CanvasModulate { Name = "ReviewAmbient", Color = ScaledAmbient() };
        gameView.AddChild(_ambient);

        _light = new PointLight2D
        {
            Name         = "ReviewCarriedLight",
            Texture      = BuildRadialFalloff(ResolveTextureSize(), _p.Falloff),
            Color        = _p.LightColor,
            Energy       = _p.Energy,
            TextureScale = 1.0f,
            BlendMode    = Light2D.BlendModeEnum.Add,
            ZIndex       = 0,
        };
        gameView.AddChild(_light);
        Follow(playerTileX, playerTileY);
    }

    /// <summary>
    /// Move the carried light onto a tile. The player IS the lamp (§6.2, §6.5), so this is
    /// called every frame from the tile the controlled figure is standing on rather than once
    /// at spawn. Centred on the tile, not its corner: a half-tile offset is visible at true
    /// display size.
    /// </summary>
    public void Follow(int tileX, int tileY)
    {
        if (_light == null) return;
        _light.Position = new Vector2(tileX * _tileW + _tileW / 2f,
                                      tileY * _tileH + _tileH / 2f);
    }

    // --- the three §6.2.1 knobs ---------------------------------------------------------------

    public float Radius
    {
        get => _p.RadiusTiles;
        set
        {
            _p = _p with { RadiusTiles = Mathf.Clamp(value, MinRadius, MaxRadius) };
            RebuildTexture();
        }
    }

    public float Falloff
    {
        get => _p.Falloff;
        set
        {
            _p = _p with { Falloff = Mathf.Clamp(value, MinFalloff, MaxFalloff) };
            RebuildTexture();
        }
    }

    public float AmbientLevel
    {
        get => _p.AmbientLevel;
        set
        {
            _p = _p with { AmbientLevel = Mathf.Clamp(value, MinAmbient, MaxAmbient) };
            if (_ambient != null) _ambient.Color = ScaledAmbient();
        }
    }

    /// <summary>
    /// The ambient the scene is actually darkened by: §6.2's hue at the tuned level.
    ///
    /// The knob scales BRIGHTNESS and holds HUE, deliberately. §6.2 gives the Boundary a
    /// character — warm, carried fire — and a knob that walked the colour as well as the level
    /// would let a readability pass quietly restyle the region. This is a readability tuning,
    /// not a licence to relight the Boundary (§6.2.1's third bullet).
    /// </summary>
    private Color ScaledAmbient()
    {
        float k = _p.AmbientLevel;
        return new Color(Mathf.Clamp(_p.Ambient.R * k, 0f, 1f),
                         Mathf.Clamp(_p.Ambient.G * k, 0f, 1f),
                         Mathf.Clamp(_p.Ambient.B * k, 0f, 1f),
                         _p.Ambient.A);
    }

    private void RebuildTexture()
    {
        if (_light == null) return;
        _light.Texture = BuildRadialFalloff(ResolveTextureSize(), _p.Falloff);
    }

    /// <summary>
    /// Texture diameter in pixels for the configured radius. Derived from the tile size the
    /// renderer is actually using rather than from any constant in this file — tile size is a
    /// parameter here, per §4.3.
    /// </summary>
    private int ResolveTextureSize()
    {
        float tile = Mathf.Max(_tileW, _tileH);
        return Mathf.Max(Mathf.RoundToInt(_p.RadiusTiles * tile * 2f), 2);
    }

    /// <summary>
    /// Radial falloff, generated per-pixel. Smoothstep rather than linear so the edge of the
    /// carried light does not read as a hard disc at true display size.
    ///
    /// `falloff` shapes the ramp without moving its reach: it is an exponent on the smoothstep,
    /// so 1.0 is exactly the curve this class drew before the knob existed, above 1.0 pulls the
    /// pool in tight around the lamp, and below 1.0 carries more light out to the radius. It is
    /// the knob §6.2.1 names second, and the gate's own diagnosis of what is wrong — "the pool
    /// is narrow, the falloff is steep, and §6.5's stack is legible in a band around the player
    /// and gone outside it" — is a statement about this curve rather than about the radius.
    /// </summary>
    private static Texture2D BuildRadialFalloff(int size, float falloff)
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
                if (!Mathf.IsEqualApprox(falloff, 1.0f))
                    a = Mathf.Pow(a, falloff);
                img.SetPixel(x, y, new Color(1f, 1f, 1f, a));
            }
        }
        return ImageTexture.CreateFromImage(img);
    }

    /// <summary>One line, written into the capture log so a capture carries its own rig.</summary>
    public string Describe(int tileWidth, int tileHeight)
        => $"ambient={_p.Ambient.ToHtml(false)}@{_p.AmbientLevel:0.##} " +
           $"(effective {ScaledAmbient().ToHtml(false)}) " +
           $"light={_p.LightColor.ToHtml(false)} energy={_p.Energy:0.###} " +
           $"radius_tiles={_p.RadiusTiles:0.###} falloff={_p.Falloff:0.##} " +
           $"tile={tileWidth}x{tileHeight} tex={ResolveTextureSize()}px " +
           // The light values are RULED FOR THE BOUNDARY (§6.2.1, Ruling 56, 2026-08-28) and this
           // string used to stamp every capture "ALL VALUES UNDERIVED". Left alone it would
           // mislabel the evidence in the opposite direction from before — a capture claiming its
           // rig was a guess when the rig is law. Tile size is separate and unchanged: RULED as to
           // value, PLACEHOLDER as to derivation (§4.3), which is not the same status and is not
           // collapsed into one phrase.
           "(light: RULED for the Boundary — §6.2.1 Ruling 56; other regions PLACEHOLDER. " +
           "tile: RULED value, §4.3 derivation outstanding)";

    /// <summary>
    /// The three §6.2.1 knobs alone, in the form a settings log wants: short, greppable, and
    /// complete enough that a walk can be reproduced from one line.
    /// </summary>
    public string Settings()
        => $"radius={_p.RadiusTiles:0.##} falloff={_p.Falloff:0.##} " +
           $"ambient={_p.AmbientLevel:0.##} ({ScaledAmbient().ToHtml(false)}) " +
           $"energy={_p.Energy:0.###}";
}
