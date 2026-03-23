using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Full-screen overlay shown on win or defeat.
/// Shows outcome, basic stats, and a "Play Again" button.
/// </summary>
public sealed partial class GameOverScreen : Control
{
    private Label? _titleLabel;
    private Label? _statsLabel;
    private Button? _replayButton;

    public event Action? ReplayRequested;

    public override void _Ready()
    {
        BuildLayout();
        Visible = false;
    }

    /// <summary>Show the screen with the given outcome and stat text.</summary>
    public void Show(bool playerWon, string stats)
    {
        if (_titleLabel != null)
        {
            _titleLabel.Text = playerWon ? "Victory!" : "Defeated";
            _titleLabel.SelfModulate = playerWon ? Colors.Gold : Colors.OrangeRed;
        }

        if (_statsLabel != null)
            _statsLabel.Text = stats;

        Visible = true;
    }

    private void BuildLayout()
    {
        SetAnchorsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop; // Block input to game when visible

        // Semi-transparent backdrop
        var bg = new ColorRect { Color = new Color(0, 0, 0, 0.75f) };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(bg);

        var vbox = new VBoxContainer();
        vbox.SetAnchorsAndOffsetsPreset(LayoutPreset.Center);
        vbox.GrowHorizontal = GrowDirection.Both;
        vbox.GrowVertical = GrowDirection.Both;
        vbox.CustomMinimumSize = new Vector2(400, 0);
        vbox.AddThemeConstantOverride("separation", 24);
        AddChild(vbox);

        _titleLabel = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        _titleLabel.AddThemeFontSizeOverride("font_size", 48);
        vbox.AddChild(_titleLabel);

        _statsLabel = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.Word,
        };
        _statsLabel.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(_statsLabel);

        _replayButton = new Button { Text = "Play Again" };
        _replayButton.AddThemeFontSizeOverride("font_size", 24);
        _replayButton.CustomMinimumSize = new Vector2(0, 64);
        _replayButton.Pressed += () => ReplayRequested?.Invoke();
        vbox.AddChild(_replayButton);
    }
}
