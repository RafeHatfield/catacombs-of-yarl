using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Slim status bar — Phase 1 layout. Shows HP fill bar + depth label only.
///
/// Intentionally stripped of gear/explore/msg buttons, equipment summary, and
/// enemy HP panel — those move to MenuButtonBar (Phase 2), QuickSlotBar (Phase 3),
/// and FloatingHpBarManager (Phase 4) respectively.
///
/// HP bar uses a ColorRect fill inside a container rather than Godot's ProgressBar
/// so we have full visual control without fighting ProgressBar theme overrides.
/// Fill width: (hp / maxHp) * availableWidth. Color thresholds: green >50%, yellow >25%, red otherwise.
///
/// No Godot scene file — built entirely in code.
/// </summary>
public sealed partial class HUD : Control
{
    private Label? _hpLabel;
    private ColorRect? _hpBarBg;
    private ColorRect? _hpBarFill;
    private Label? _depthLabel;

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

    /// <summary>
    /// Update HUD state from a completed turn result, then refresh all elements.
    /// Enemy HP tracking removed — that's handled by FloatingHpBarManager in Phase 4.
    /// </summary>
    public void OnTurnCompleted(TurnResult result, GameState state)
    {
        _state = state;
        Refresh();
    }

    /// <summary>Refresh all HUD elements from current GameState.</summary>
    public void Refresh()
    {
        if (_state == null) return;

        var fighter = _state.PlayerFighter;

        // HP fill bar — compute fill width from HP fraction.
        // Must read Size after layout; falls back to CustomMinimumSize if layout hasn't resolved yet.
        if (_hpBarFill != null && _hpBarBg != null)
        {
            float availableWidth = _hpBarBg.Size.X > 0 ? _hpBarBg.Size.X : _hpBarBg.CustomMinimumSize.X;
            float frac = fighter.MaxHp > 0 ? (float)fighter.Hp / fighter.MaxHp : 0f;
            frac = Math.Clamp(frac, 0f, 1f);
            _hpBarFill.Size = new Vector2(availableWidth * frac, _hpBarFill.Size.Y);
            _hpBarFill.Color = HpColor(fighter.Hp, fighter.MaxHp);
        }

        if (_hpLabel != null)
            _hpLabel.Text = $"{fighter.Hp}/{fighter.MaxHp}";

        if (_depthLabel != null)
            _depthLabel.Text = $"D:{_state.CurrentDepth}";
    }

    // -------------------------------------------------------------------------

    private void BuildLayout()
    {
        // Fill the StatusBar zone container from Main.tscn (90px TopWide).
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var sans = LoadPixelFont("res://src/Presentation/assets/fonts/PixeloidSans.ttf");
        var bold = LoadPixelFont("res://src/Presentation/assets/fonts/PixeloidSans-Bold.ttf");

        // Dark navy background — same color as the original HUD.
        var bg = new ColorRect { Color = new Color(0.05f, 0.05f, 0.1f, 0.85f) };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(bg);

        // Single-column layout with a margin container for edge padding.
        var margin = new MarginContainer();
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        margin.AddThemeConstantOverride("margin_left",   16);
        margin.AddThemeConstantOverride("margin_right",  16);
        margin.AddThemeConstantOverride("margin_top",    10);
        margin.AddThemeConstantOverride("margin_bottom", 6);
        AddChild(margin);

        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 4);
        margin.AddChild(vbox);

        // ── Row 1: HP fill bar + "HP X/Y" label + depth label ────────────────
        var topRow = new HBoxContainer();
        topRow.AddThemeConstantOverride("separation", 8);
        vbox.AddChild(topRow);

        // HP bar container: a dark background rect that acts as the track.
        // Relative width via SizeFlags.ExpandFill so it fills available space.
        var hpBarContainer = new Control();
        hpBarContainer.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        hpBarContainer.CustomMinimumSize = new Vector2(0, 22);
        topRow.AddChild(hpBarContainer);

        _hpBarBg = new ColorRect
        {
            Color = new Color(0.1f, 0.1f, 0.1f, 0.9f),
            // Match container height; width resolved by Godot layout.
            AnchorRight = 1f,
            AnchorBottom = 1f,
        };
        hpBarContainer.AddChild(_hpBarBg);

        // The fill starts at 0 width; Refresh() sets it based on HP fraction.
        _hpBarFill = new ColorRect
        {
            Color = Colors.LimeGreen,
            // Anchored to left/top/bottom; width is set procedurally in Refresh().
            AnchorLeft   = 0f,
            AnchorTop    = 0f,
            AnchorRight  = 0f,
            AnchorBottom = 1f,
            // Start at max width (immediately corrected by first Refresh).
            Size = new Vector2(200f, 0f),
        };
        hpBarContainer.AddChild(_hpBarFill);

        // HP text overlaid on top of the fill bar.
        _hpLabel = new Label
        {
            Text = "HP",
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment   = VerticalAlignment.Center,
            // Covers the full bar area for centered overlay text.
            AnchorRight  = 1f,
            AnchorBottom = 1f,
        };
        _hpLabel.AddThemeFontOverride("font", bold);
        _hpLabel.AddThemeFontSizeOverride("font_size", 16);
        _hpLabel.AddThemeColorOverride("font_color", Colors.White);
        _hpLabel.MouseFilter = MouseFilterEnum.Ignore;
        hpBarContainer.AddChild(_hpLabel);

        // Depth label — right-aligned, compact.
        _depthLabel = new Label
        {
            Text = "D:1",
            HorizontalAlignment = HorizontalAlignment.Right,
        };
        _depthLabel.AddThemeFontOverride("font", sans);
        _depthLabel.AddThemeFontSizeOverride("font_size", 22);
        _depthLabel.AddThemeColorOverride("font_color", Colors.White);
        topRow.AddChild(_depthLabel);
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
}
