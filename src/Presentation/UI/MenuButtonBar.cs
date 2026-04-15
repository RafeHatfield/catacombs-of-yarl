using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Horizontal bar containing Gear and Explore buttons, placed in the MenuButtons
/// zone below the quick-slot bar. Built entirely in code — no .tscn file.
///
/// Phase 2 of the mobile layout overhaul: restores the Gear and Explore button
/// functionality that was temporarily removed from HUD in Phase 1.
///
/// Layout: 8px horizontal margin on each side, 8px gap between buttons.
/// Each button gets SizeFlags.ExpandFill so they split available width evenly.
/// Minimum height is enforced at 48px per Apple HIG touch target guidelines.
///
/// Gear button:    dark gold background, opens the equipment panel.
/// Explore button: dark green background, triggers auto-explore. Updates to
///                 show "Exploring..." with yellow tint while active.
/// </summary>
public sealed partial class MenuButtonBar : Control
{
    // Colors defined in task spec — kept as constants for easy tuning.
    private static readonly Color GearBgColor    = new(0.25f, 0.20f, 0.10f, 0.9f);
    private static readonly Color ExploreBgColor = new(0.15f, 0.35f, 0.15f, 0.9f);
    private static readonly Color ExploreActiveColor = new(0.40f, 0.40f, 0.05f, 0.9f); // yellow-tinted when exploring

    private const int HorizontalMargin = 8;
    private const int ButtonGap        = 8;
    private const int MinButtonHeight  = 48;
    private const int FontSize         = 22;

    private TouchButton? _gearButton;
    private TouchButton? _exploreButton;

    // C# events — no Godot signal allocation. Null-safe: callers must handle null subscribers.
    public event Action? GearRequested;
    public event Action? ExploreRequested;

    public override void _Ready()
    {
        // Fill the MenuButtons zone container entirely.
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;

        BuildLayout();
    }

    /// <summary>
    /// Reflect current auto-explore state on the Explore button.
    /// Called from Main.OnTurnCompleted after each turn.
    ///
    /// When active: "Exploring..." label, yellow-tinted background.
    /// When inactive: "Explore" label, normal dark-green background.
    /// </summary>
    public void SetAutoExploreActive(bool active)
    {
        if (_exploreButton == null) return;

        if (active)
        {
            _exploreButton.Text = "Exploring...";
            _exploreButton.BackgroundColor = ExploreActiveColor;
        }
        else
        {
            _exploreButton.Text = "Explore";
            _exploreButton.BackgroundColor = ExploreBgColor;
        }
    }

    // -------------------------------------------------------------------------
    // Layout — all built in code, no scene file dependency.
    // -------------------------------------------------------------------------

    private void BuildLayout()
    {
        // Outer margin container so buttons don't touch screen edges.
        var margin = new MarginContainer();
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        margin.AddThemeConstantOverride("margin_left",   HorizontalMargin);
        margin.AddThemeConstantOverride("margin_right",  HorizontalMargin);
        margin.AddThemeConstantOverride("margin_top",    8);
        margin.AddThemeConstantOverride("margin_bottom", 8);
        AddChild(margin);

        // HBoxContainer gives us the side-by-side layout with a controlled gap.
        var hbox = new HBoxContainer();
        hbox.AddThemeConstantOverride("separation", ButtonGap);
        // Fill the margin container vertically so buttons expand to zone height.
        hbox.SizeFlagsVertical = SizeFlags.ExpandFill;
        margin.AddChild(hbox);

        // Gear button — dark gold, opens equipment panel.
        // CornerRadius=6 matches the 6px radii used on QuickSlotBar item slots.
        _gearButton = new TouchButton
        {
            Text            = "Gear",
            FontSize        = FontSize,
            BackgroundColor = GearBgColor,
            CornerRadius    = 6,
        };
        // ExpandFill in both axes: fills half the HBox width and the full height.
        _gearButton.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        _gearButton.SizeFlagsVertical   = SizeFlags.ExpandFill;
        _gearButton.CustomMinimumSize   = new Vector2(0, MinButtonHeight);
        _gearButton.Pressed            += () => GearRequested?.Invoke();
        hbox.AddChild(_gearButton);

        // Explore button — dark green, triggers auto-explore.
        _exploreButton = new TouchButton
        {
            Text            = "Explore",
            FontSize        = FontSize,
            BackgroundColor = ExploreBgColor,
            CornerRadius    = 6,
        };
        _exploreButton.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        _exploreButton.SizeFlagsVertical   = SizeFlags.ExpandFill;
        _exploreButton.CustomMinimumSize   = new Vector2(0, MinButtonHeight);
        _exploreButton.Pressed            += () => ExploreRequested?.Invoke();
        hbox.AddChild(_exploreButton);
    }
}
