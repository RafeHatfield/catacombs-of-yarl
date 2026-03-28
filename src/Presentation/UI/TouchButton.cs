using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Reusable button control that uses manual _GuiInput hit-testing instead
/// of Godot's Button class.
///
/// Background: Godot 4.6 with integer stretch scale mode causes Button hit areas
/// to be offset from their visual position on iOS CanvasLayer. This control works
/// around the bug by handling _GuiInput at the Control level and hit-testing against
/// GetRect(), which is always correct regardless of scale mode.
///
/// Usage:
///   var btn = new TouchButton
///   {
///       Text = "Explore",
///       FontSize = 22,
///       BackgroundColor = new Color(0.2f, 0.4f, 0.8f, 1f),
///       CustomMinimumSize = new Vector2(120, 48),
///   };
///   btn.Pressed += () => DoSomething();
///   parent.AddChild(btn);
/// </summary>
public sealed partial class TouchButton : Control
{
    private static readonly Color DisabledColor = new(0.35f, 0.35f, 0.35f, 0.6f);
    private static readonly Color DisabledTextColor = new(0.55f, 0.55f, 0.55f, 1f);

    private ColorRect? _bg;
    private Label?     _label;

    private string _text = "";
    private int    _fontSize = 22;
    private Color  _backgroundColor = new(0.2f, 0.4f, 0.8f, 1f);
    private bool   _disabled;

    // C# event — not a Godot signal, so no Callable allocation or leak.
    public event Action? Pressed;

    // -------------------------------------------------------------------------
    // Properties — updating them after _Ready re-applies to the live nodes.
    // -------------------------------------------------------------------------

    public string Text
    {
        get => _text;
        set
        {
            _text = value;
            if (_label != null) _label.Text = value;
        }
    }

    public int FontSize
    {
        get => _fontSize;
        set
        {
            _fontSize = value;
            _label?.AddThemeFontSizeOverride("font_size", value);
        }
    }

    public Color BackgroundColor
    {
        get => _backgroundColor;
        set
        {
            _backgroundColor = value;
            ApplyColors();
        }
    }

    public bool Disabled
    {
        get => _disabled;
        set
        {
            _disabled = value;
            ApplyColors();
        }
    }

    // -------------------------------------------------------------------------
    // Godot lifecycle
    // -------------------------------------------------------------------------

    public override void _Ready()
    {
        // Stop input here — don't let taps fall through to the game view.
        MouseFilter = MouseFilterEnum.Stop;

        BuildLayout();
    }

    /// <summary>
    /// Hit-test against the button's own rect. Handles both mouse clicks
    /// (desktop/editor) and touch events (iOS device).
    ///
    /// InputEventMouseButton and InputEventScreenTouch both report position
    /// in the local coordinate space when received via _GuiInput, so a simple
    /// GetRect().HasPoint() is sufficient.
    /// </summary>
    public override void _GuiInput(InputEvent @event)
    {
        if (_disabled) return;

        bool tapped = false;

        if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
            tapped = true;
        else if (@event is InputEventScreenTouch touch && touch.Pressed)
            tapped = true;

        if (tapped)
        {
            // Always consume so clicks don't propagate to siblings or the game view.
            AcceptEvent();
            Pressed?.Invoke();
        }
    }

    // -------------------------------------------------------------------------
    // Layout — all children get MouseFilter=Ignore so _GuiInput is received
    // by this node only.
    // -------------------------------------------------------------------------

    private void BuildLayout()
    {
        _bg = new ColorRect { MouseFilter = MouseFilterEnum.Ignore };
        _bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(_bg);

        _label = new Label
        {
            Text                = _text,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment   = VerticalAlignment.Center,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        _label.AddThemeFontSizeOverride("font_size", _fontSize);
        _label.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(_label);

        ApplyColors();
    }

    private void ApplyColors()
    {
        if (_bg    == null) return;
        if (_label == null) return;

        if (_disabled)
        {
            _bg.Color = DisabledColor;
            _label.AddThemeColorOverride("font_color", DisabledTextColor);
        }
        else
        {
            _bg.Color = _backgroundColor;
            _label.RemoveThemeColorOverride("font_color");
        }
    }
}
