using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Heads-up display. Shows player HP bar, turn counter, depth,
/// and the nearest enemy's HP bar when in range.
///
/// Driven by GameState directly — reads values on each Update() call.
/// No Godot scene file — built entirely in code for portability.
/// </summary>
public sealed partial class HUD : Control
{
    private Label? _hpLabel;
    private ProgressBar? _hpBar;
    private Label? _turnLabel;
    private Label? _depthLabel;
    private Control? _enemyHpPanel;
    private Label? _enemyHpLabel;
    private ProgressBar? _enemyHpBar;

    private GameState? _state;

    public override void _Ready()
    {
        BuildLayout();
    }

    public void SetState(GameState state)
    {
        _state = state;
        Refresh();
    }

    /// <summary>Refresh all HUD elements from current GameState.</summary>
    public void Refresh()
    {
        if (_state == null) return;

        var fighter = _state.PlayerFighter;

        // HP bar
        if (_hpBar != null)
        {
            _hpBar.MaxValue = fighter.MaxHp;
            _hpBar.Value = fighter.Hp;
            _hpBar.SelfModulate = HpColor(fighter.Hp, fighter.MaxHp);
        }
        if (_hpLabel != null)
            _hpLabel.Text = $"HP  {fighter.Hp} / {fighter.MaxHp}";

        // Turn counter
        if (_turnLabel != null)
            _turnLabel.Text = $"Turn {_state.TurnCount}";

        // Nearest enemy HP
        var nearest = _state.AliveMonsters
            .OrderBy(m => _state.Player.ChebyshevDistanceTo(m.X, m.Y))
            .FirstOrDefault();

        if (_enemyHpPanel != null && nearest != null)
        {
            var ef = nearest.Require<Fighter>();
            _enemyHpPanel.Visible = true;
            if (_enemyHpBar != null)
            {
                _enemyHpBar.MaxValue = ef.MaxHp;
                _enemyHpBar.Value = ef.Hp;
                _enemyHpBar.SelfModulate = Colors.IndianRed;
            }
            if (_enemyHpLabel != null)
                _enemyHpLabel.Text = $"{nearest.Name}  {ef.Hp}/{ef.MaxHp}";
        }
        else if (_enemyHpPanel != null)
        {
            _enemyHpPanel.Visible = false;
        }
    }

    private void BuildLayout()
    {
        // Full-width bar across the top
        SetAnchorsPreset(LayoutPreset.TopWide);
        CustomMinimumSize = new Vector2(0, 120);

        var bg = new ColorRect { Color = new Color(0.05f, 0.05f, 0.1f, 0.85f) };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(bg);

        var vbox = new VBoxContainer();
        vbox.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        vbox.AddThemeConstantOverride("separation", 4);
        AddChild(vbox);

        var margin = new MarginContainer();
        margin.AddThemeConstantOverride("margin_left", 16);
        margin.AddThemeConstantOverride("margin_right", 16);
        margin.AddThemeConstantOverride("margin_top", 12);
        margin.AddThemeConstantOverride("margin_bottom", 8);
        vbox.AddChild(margin);

        var inner = new VBoxContainer();
        inner.AddThemeConstantOverride("separation", 6);
        margin.AddChild(inner);

        // Top row: HP label + turn counter
        var topRow = new HBoxContainer();
        inner.AddChild(topRow);

        _hpLabel = new Label { Text = "HP  54 / 54", SizeFlagsHorizontal = SizeFlags.ExpandFill };
        _hpLabel.AddThemeFontSizeOverride("font_size", 18);
        topRow.AddChild(_hpLabel);

        _turnLabel = new Label { Text = "Turn 0", HorizontalAlignment = HorizontalAlignment.Right };
        _turnLabel.AddThemeFontSizeOverride("font_size", 16);
        topRow.AddChild(_turnLabel);

        // Player HP bar
        _hpBar = new ProgressBar { ShowPercentage = false };
        _hpBar.CustomMinimumSize = new Vector2(0, 14);
        inner.AddChild(_hpBar);

        // Enemy HP panel
        _enemyHpPanel = new VBoxContainer { Visible = false };
        inner.AddChild(_enemyHpPanel);

        _enemyHpLabel = new Label { Text = "" };
        _enemyHpLabel.AddThemeFontSizeOverride("font_size", 14);
        _enemyHpPanel.AddChild(_enemyHpLabel);

        _enemyHpBar = new ProgressBar { ShowPercentage = false };
        _enemyHpBar.CustomMinimumSize = new Vector2(0, 10);
        _enemyHpPanel.AddChild(_enemyHpBar);
    }

    private static Color HpColor(int hp, int maxHp)
    {
        float frac = maxHp > 0 ? (float)hp / maxHp : 0f;
        if (frac > 0.5f) return Colors.LimeGreen;
        if (frac > 0.25f) return Colors.Yellow;
        return Colors.OrangeRed;
    }
}
