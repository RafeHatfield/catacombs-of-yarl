using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Animation;

/// <summary>
/// Renders visual effects (area flashes, path trails, projectile travel, status indicators)
/// on top of the game world using a pre-allocated pool of ColorRect nodes.
///
/// Design constraints:
/// - Pool of 64 ColorRects allocated once at construction — never freed, just hidden/shown.
///   Avoids per-cast allocation and the GCHandle leak that Callable.From lambdas create.
/// - Speed multiplier is passed at each call site — VfxOverlay never stores it.
/// - Cleanup uses TweenProperty to set Visible=false, NOT Callable.From lambdas.
/// - Label nodes (projectile travel, status indicators) are single-use and freed via
///   TweenCallback(Callable.From(...)) only for the SafeFree call — acceptable since
///   that is a static method reference, not a closure capturing a non-GodotObject.
///   Update: we use QueueFree via property tweak instead where possible.
///
/// ZIndex per pooled node: renderer.GetTileSortOrder(x,y) + 5 (above tiles, below UI).
/// </summary>
public sealed class VfxOverlay
{
    private const int PoolSize = 64;
    private const int TileHalfSize = 16; // ColorRect is 32×32, offset by -16 to center

    private readonly Node2D _layer;
    private readonly IMapRenderer _renderer;
    private readonly ColorRect[] _pool;
    private int _poolNext; // index of next available node (wraps around)

    public VfxOverlay(Node2D vfxLayerNode, IMapRenderer renderer)
    {
        _layer = vfxLayerNode;
        _renderer = renderer;
        _pool = new ColorRect[PoolSize];

        // Pre-allocate all pool nodes hidden by default.
        for (int i = 0; i < PoolSize; i++)
        {
            var rect = new ColorRect
            {
                Size = new Vector2(32, 32),
                Visible = false,
                // ZAsRelative = false so ZIndex is scene-absolute (not relative to parent).
                ZAsRelative = false,
                MouseFilter = Control.MouseFilterEnum.Ignore,
            };
            _layer.AddChild(rect);
            _pool[i] = rect;
        }
    }

    /// <summary>
    /// Flash all given tiles simultaneously with <paramref name="color"/>,
    /// fading out over <paramref name="durationSecs"/>.
    /// All tiles animate in parallel using tween.Parallel().
    /// </summary>
    public void AppendAreaEffect(Tween tween, IReadOnlyList<(int X, int Y)> tiles,
        Color color, float durationSecs)
    {
        if (tiles.Count == 0) return;

        bool first = true;
        foreach (var (x, y) in tiles)
        {
            var rect = BorrowNode(x, y, color);

            // Use tween.Parallel() so all tiles fade simultaneously.
            var step = first
                ? tween.TweenProperty(rect, "modulate:a", 0.0f, durationSecs)
                : tween.Parallel().TweenProperty(rect, "modulate:a", 0.0f, durationSecs);
            step.SetEase(Tween.EaseType.In).SetTrans(Tween.TransitionType.Quad);

            // Hide via property tween after fade — avoids Callable.From lambda.
            if (first)
                tween.TweenProperty(rect, "visible", false, 0.0f);
            else
                tween.Parallel().TweenProperty(rect, "visible", false, 0.0f);

            first = false;
        }
    }

    /// <summary>
    /// Flash tiles sequentially along a path (e.g. lightning bolt).
    /// Each tile lights up for <paramref name="perTileSecs"/> then fades,
    /// before the next tile in the sequence begins.
    /// </summary>
    public void AppendPathEffect(Tween tween, IReadOnlyList<(int X, int Y)> tiles,
        Color color, float perTileSecs)
    {
        if (tiles.Count == 0) return;

        foreach (var (x, y) in tiles)
        {
            var rect = BorrowNode(x, y, color);

            // Hold at full alpha briefly, then fade.
            float holdTime = perTileSecs * 0.3f;
            float fadeTime = perTileSecs * 0.7f;

            tween.TweenInterval(holdTime);
            tween.TweenProperty(rect, "modulate:a", 0.0f, fadeTime)
                 .SetEase(Tween.EaseType.Out);
            tween.TweenProperty(rect, "visible", false, 0.0f);
        }
    }

    /// <summary>
    /// Animate a single-glyph projectile travelling from <paramref name="from"/> to
    /// <paramref name="to"/> at <paramref name="speedPerTile"/> seconds per tile.
    /// Pattern matches the existing throw projectile animation in TurnAnimator.
    /// The Label is freed after travel completes (single-use, not pooled).
    /// </summary>
    public void AppendTravelEffect(Tween tween, (int X, int Y) from, (int X, int Y) to,
        Color color, string glyph, float speedPerTile)
    {
        var fromScreen = _renderer.GridToScreenCenter(from.X, from.Y);
        var toScreen   = _renderer.GridToScreenCenter(to.X, to.Y);

        int tileDist = Math.Max(1,
            Math.Abs(to.X - from.X) + Math.Abs(to.Y - from.Y));
        float travelDur = speedPerTile * tileDist;

        var label = new Label
        {
            Text = glyph,
            Modulate = color,
            Position = fromScreen,
            ZIndex = 10,
            ZAsRelative = false,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _layer.AddChild(label);

        tween.TweenProperty(label, "position", toScreen, travelDur)
             .SetEase(Tween.EaseType.InOut)
             .SetTrans(Tween.TransitionType.Linear);

        // Free after travel. Callable.From(static) is acceptable here — no closure capturing
        // non-GodotObject. SafeFree is the established pattern in this codebase.
        tween.TweenCallback(Callable.From(() => label.SafeFree()));
    }

    /// <summary>
    /// Display a floating glyph indicator at <paramref name="screenPos"/>,
    /// drifting upward and fading over <paramref name="durationSecs"/>.
    /// Used for per-entity status effect notifications (e.g. "z" for sleep).
    /// </summary>
    public void AppendStatusIndicator(Tween tween, Vector2 screenPos, string glyph,
        Color color, float durationSecs)
    {
        var label = new Label
        {
            Text = glyph,
            Modulate = color,
            Position = screenPos,
            ZIndex = 12,
            ZAsRelative = false,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _layer.AddChild(label);

        var endPos = screenPos + new Vector2(0, -8f);

        tween.TweenProperty(label, "position", endPos, durationSecs)
             .SetEase(Tween.EaseType.Out);
        tween.Parallel().TweenProperty(label, "modulate:a", 0.0f, durationSecs)
             .SetEase(Tween.EaseType.In);

        tween.TweenCallback(Callable.From(() => label.SafeFree()));
    }

    /// <summary>
    /// Hide all pooled nodes immediately. Call on floor transition.
    /// </summary>
    public void ClearAll()
    {
        foreach (var rect in _pool)
        {
            rect.Visible = false;
            // Reset modulate alpha so nodes are ready for next use.
            rect.Modulate = Colors.White;
        }
    }

    // ── Pool management ────────────────────────────────────────────────────────

    private ColorRect BorrowNode(int gridX, int gridY, Color color)
    {
        var rect = _pool[_poolNext];
        _poolNext = (_poolNext + 1) % PoolSize;

        var screenCenter = _renderer.GridToScreenCenter(gridX, gridY);
        rect.Position = screenCenter - new Vector2(TileHalfSize, TileHalfSize);
        rect.Modulate = new Color(color, 0.8f); // slight transparency for area flash
        rect.ZIndex = _renderer.GetTileSortOrder(gridX, gridY) + 5;
        rect.Visible = true;

        return rect;
    }
}
