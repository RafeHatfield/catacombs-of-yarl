using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
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
    private Label? _depthLabel;
    private Label? _equipLabel;
    private Control? _enemyHpPanel;
    private Label? _enemyHpLabel;
    private ProgressBar? _enemyHpBar;
    private StatusEffectBar? _statusEffectBar;

    private TouchButton? _exploreButton;
    private TouchButton? _gearButton;
    private TouchButton? _msgButton;
    private GameState? _state;

    // Track the last monster the player attacked. We show this monster's HP bar until
    // it dies — then hide the bar entirely. We never auto-switch to "nearest alive" because
    // that looks like an HP reset when the current target drops.
    private int _combatTargetId = -1;

    /// <summary>Fired when the player taps the Explore button.</summary>
    public event Action? ExploreRequested;

    /// <summary>Fired when the player taps the Gear (equipment) button.</summary>
    public event Action? GearRequested;

    /// <summary>Fired when the player taps the message recall button.</summary>
    public event Action? MessageRecallRequested;

    public override void _Ready()
    {
        BuildLayout();
    }

    public void SetState(GameState state)
    {
        _state = state;
        _combatTargetId = -1;
        Refresh();
    }

    /// <summary>
    /// Update combat target tracking from the turn result, then refresh all HUD elements.
    /// Call this after every turn instead of the bare Refresh() overload.
    ///
    /// Target switch rules:
    ///   - Player attacks a monster → that monster becomes the tracked target
    ///   - Tracked target dies → target cleared (bar hides; no auto-switch to nearest)
    /// </summary>
    public void OnTurnCompleted(TurnResult result, GameState state)
    {
        _state = state;

        // Scan events in order. Player-attack events update the target; death events clear it.
        // Both can happen in the same turn (player one-shots a monster), so process death
        // events after attack events so we don't briefly flash the dead monster's full bar.
        foreach (var evt in result.Events)
        {
            if (evt is AttackEvent atk && atk.ActorId == state.Player.Id)
                _combatTargetId = atk.TargetId;
        }
        foreach (var evt in result.Events)
        {
            if (evt is DeathEvent death && death.ActorId == _combatTargetId)
                _combatTargetId = -1;
        }

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

        // Depth
        if (_depthLabel != null)
            _depthLabel.Text = $"Depth: {_state.CurrentDepth}";

        // Equipment summary — weapon + armor, truncated to 12 chars each.
        // Uses identification-aware display names so unidentified rings show correctly.
        if (_equipLabel != null)
        {
            var eq       = _state.Player.Get<Equipment>();
            var registry = _state.IdentificationRegistry;
            var pool     = _state.AppearancePool;

            string WpnName(Entity? item) => item == null ? "—"
                : ItemDisplay.GetDisplayName(item, registry, pool);

            var wpn = Truncate(WpnName(eq?.MainHand), 12);
            var arm = Truncate(eq?.GetSlot(EquipmentSlot.Chest) is Entity chest
                ? ItemDisplay.GetDisplayName(chest, registry, pool)
                : "—", 12);

            _equipLabel.Text = $"Wpn: {wpn}   Arm: {arm}";
        }

        // Status effect badges — show active effects on the player.
        _statusEffectBar?.Refresh(_state.Player);

        // Enemy HP bar: show the tracked combat target if it is still alive.
        // Never fall back to "nearest alive" — that causes apparent HP resets when targets die.
        Entity? target = _combatTargetId >= 0
            ? _state.AliveMonsters.FirstOrDefault(m => m.Id == _combatTargetId)
            : null;

        if (_enemyHpPanel != null && target != null)
        {
            var ef = target.Require<Fighter>();
            _enemyHpPanel.Visible = true;
            if (_enemyHpBar != null)
            {
                _enemyHpBar.MaxValue = ef.MaxHp;
                _enemyHpBar.Value = ef.Hp;
                _enemyHpBar.SelfModulate = Colors.IndianRed;
            }
            if (_enemyHpLabel != null)
                _enemyHpLabel.Text = $"{target.Name}  {ef.Hp}/{ef.MaxHp}";
        }
        else if (_enemyHpPanel != null)
        {
            _enemyHpPanel.Visible = false;
        }
    }

    /// <summary>Visually indicate whether auto-explore is currently running.</summary>
    public void SetAutoExploreActive(bool active)
    {
        if (_exploreButton == null) return;
        _exploreButton.Text     = active ? "Exploring..." : "Explore";
        // Tint yellow while active so the player can see the mode is on.
        _exploreButton.Modulate = active ? Colors.Yellow : Colors.White;
    }

    private void BuildLayout()
    {
        // Fill the container node defined in Main.tscn (200px TopWide)
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var sans = LoadPixelFont("res://src/Presentation/assets/fonts/PixeloidSans.ttf");
        var bold = LoadPixelFont("res://src/Presentation/assets/fonts/PixeloidSans-Bold.ttf");

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

        // Top row: HP label + depth + Explore button
        var topRow = new HBoxContainer();
        inner.AddChild(topRow);

        _hpLabel = new Label { Text = "HP  54 / 54", SizeFlagsHorizontal = SizeFlags.ExpandFill };
        _hpLabel.AddThemeFontOverride("font", bold);
        _hpLabel.AddThemeFontSizeOverride("font_size", 28);
        _hpLabel.AddThemeColorOverride("font_color", Colors.White);
        topRow.AddChild(_hpLabel);

        _depthLabel = new Label { Text = "Depth: 1", HorizontalAlignment = HorizontalAlignment.Right };
        _depthLabel.AddThemeFontOverride("font", sans);
        _depthLabel.AddThemeFontSizeOverride("font_size", 24);
        _depthLabel.AddThemeColorOverride("font_color", Colors.White);
        topRow.AddChild(_depthLabel);

        // Use TouchButton instead of Godot Button — Godot's Button has offset hit areas
        // under integer stretch scale mode on iOS CanvasLayer.
        _gearButton = new TouchButton
        {
            Text              = "Gear",
            FontSize          = 22,
            BackgroundColor   = new Color(0.25f, 0.20f, 0.10f, 0.9f),
            CustomMinimumSize = new Vector2(72, 0),
        };
        _gearButton.Pressed += () => GearRequested?.Invoke();
        topRow.AddChild(_gearButton);

        _exploreButton = new TouchButton
        {
            Text            = "Explore",
            FontSize        = 22,
            BackgroundColor = new Color(0.15f, 0.35f, 0.15f, 0.9f),
            CustomMinimumSize = new Vector2(96, 0),
        };
        _exploreButton.Pressed += () => ExploreRequested?.Invoke();
        topRow.AddChild(_exploreButton);

        _msgButton = new TouchButton
        {
            Text            = "Msg",
            FontSize        = 22,
            BackgroundColor = new Color(0.15f, 0.20f, 0.35f, 0.9f),
            CustomMinimumSize = new Vector2(60, 0),
        };
        _msgButton.Pressed += () => MessageRecallRequested?.Invoke();
        topRow.AddChild(_msgButton);

        // Player HP bar
        _hpBar = new ProgressBar { ShowPercentage = false };
        _hpBar.CustomMinimumSize = new Vector2(0, 14);
        inner.AddChild(_hpBar);

        // Status effect badges — row of colored short-name + turn-count badges.
        // Hidden when no effects are active (StatusEffectBar renders empty).
        _statusEffectBar = new StatusEffectBar();
        _statusEffectBar.CustomMinimumSize = new Vector2(0, 24);
        inner.AddChild(_statusEffectBar);

        // Equipment summary row (weapon + armor)
        _equipLabel = new Label { Text = "Wpn: —   Arm: —" };
        _equipLabel.AddThemeFontOverride("font", sans);
        _equipLabel.AddThemeFontSizeOverride("font_size", 22);
        _equipLabel.AddThemeColorOverride("font_color", new Color(0.85f, 0.85f, 0.85f, 1f));
        inner.AddChild(_equipLabel);

        // Enemy HP panel
        _enemyHpPanel = new VBoxContainer { Visible = false };
        inner.AddChild(_enemyHpPanel);

        _enemyHpLabel = new Label { Text = "" };
        _enemyHpLabel.AddThemeFontOverride("font", sans);
        _enemyHpLabel.AddThemeFontSizeOverride("font_size", 22);
        _enemyHpLabel.AddThemeColorOverride("font_color", Colors.White);
        _enemyHpPanel.AddChild(_enemyHpLabel);

        _enemyHpBar = new ProgressBar { ShowPercentage = false };
        _enemyHpBar.CustomMinimumSize = new Vector2(0, 10);
        _enemyHpPanel.AddChild(_enemyHpBar);
    }

    /// <summary>
    /// Load a font and configure it for pixel-perfect rendering:
    /// no antialiasing, no subpixel positioning, no hinting.
    /// </summary>
    private static FontFile LoadPixelFont(string path)
    {
        var font = GD.Load<FontFile>(path);
        font.Antialiasing = TextServer.FontAntialiasing.None;
        font.SubpixelPositioning = TextServer.SubpixelPositioning.Disabled;
        font.Hinting = TextServer.Hinting.None;
        return font;
    }

    private static Color HpColor(int hp, int maxHp)
    {
        float frac = maxHp > 0 ? (float)hp / maxHp : 0f;
        if (frac > 0.5f) return Colors.LimeGreen;
        if (frac > 0.25f) return Colors.Yellow;
        return Colors.OrangeRed;
    }

    /// <summary>
    /// Truncate a string to maxLen characters, appending "…" if it was cut.
    /// Keeps equipment names readable at small font sizes.
    /// </summary>
    private static string Truncate(string s, int maxLen) =>
        s.Length <= maxLen ? s : s[..maxLen] + "…";
}
