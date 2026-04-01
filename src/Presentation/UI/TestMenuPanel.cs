using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Full-screen panel listing available test scenarios.
/// Presented in debug builds via the "Testing Mode" main menu button.
///
/// Constructor takes the discovered scenario list so this panel has no
/// file-system knowledge — discovery happens in Main.cs.
/// </summary>
public sealed partial class TestMenuPanel : Control
{
    [Signal] public delegate void ScenarioSelectedEventHandler(string path);
    [Signal] public delegate void BackRequestedEventHandler();

    private readonly List<(string Name, string Path)> _scenarios;

    public TestMenuPanel(List<(string name, string path)> scenarios)
    {
        _scenarios = scenarios;
    }

    public override void _Ready()
    {
        BuildLayout();
    }

    private void BuildLayout()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;

        // Semi-transparent dark backdrop
        var bg = new ColorRect
        {
            Color       = new Color(0f, 0f, 0f, 0.85f),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(bg);

        // Outer layout: title + scroll + back button stacked vertically
        var outer = new VBoxContainer { MouseFilter = MouseFilterEnum.Ignore };
        outer.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        outer.AddThemeConstantOverride("separation", 12);
        // Inset from screen edges
        outer.OffsetLeft   = 40f;
        outer.OffsetTop    = 60f;
        outer.OffsetRight  = -40f;
        outer.OffsetBottom = -40f;
        AddChild(outer);

        // Title
        var title = new Label
        {
            Text                = "Testing Mode",
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        title.AddThemeFontSizeOverride("font_size", 36);
        outer.AddChild(title);

        // Scrollable scenario list — grows to fill available space
        var scroll = new ScrollContainer { MouseFilter = MouseFilterEnum.Stop };
        scroll.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        outer.AddChild(scroll);

        var list = new VBoxContainer { MouseFilter = MouseFilterEnum.Ignore };
        list.AddThemeConstantOverride("separation", 10);
        // Ensure the list fills scroll width so buttons align properly
        list.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        scroll.AddChild(list);

        if (_scenarios.Count == 0)
        {
            var empty = new Label
            {
                Text                = "No test scenarios found in res://config/testing/",
                HorizontalAlignment = HorizontalAlignment.Center,
                AutowrapMode        = TextServer.AutowrapMode.Word,
                MouseFilter         = MouseFilterEnum.Ignore,
            };
            empty.AddThemeFontSizeOverride("font_size", 18);
            empty.AddThemeColorOverride("font_color", new Color(0.6f, 0.6f, 0.6f, 1f));
            list.AddChild(empty);
        }
        else
        {
            foreach (var (name, path) in _scenarios)
            {
                // Capture loop variables explicitly — C# lambda closure rules
                var capturedPath = path;
                var btn = new TouchButton
                {
                    Text              = name,
                    FontSize          = 22,
                    BackgroundColor   = new Color(0.2f, 0.35f, 0.55f, 0.95f),
                    CustomMinimumSize = new Vector2(0, 60),
                };
                btn.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
                btn.Pressed += () => EmitSignal(SignalName.ScenarioSelected, capturedPath);
                list.AddChild(btn);
            }
        }

        // Back button — always at the bottom, fixed height
        var backBtn = new TouchButton
        {
            Text              = "← Back",
            FontSize          = 22,
            BackgroundColor   = new Color(0.35f, 0.2f, 0.2f, 0.95f),
            CustomMinimumSize = new Vector2(0, 56),
        };
        backBtn.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        backBtn.Pressed += () => EmitSignal(SignalName.BackRequested);
        outer.AddChild(backBtn);
    }
}
