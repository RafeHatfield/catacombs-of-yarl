using System.Collections.Generic;
using CatacombsOfYarl.Logic.Voice;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// The Hollowmark ribbon (docs/systems/voice_delivery.md §Ribbon contract). Its OWN Control — NOT
/// ToastLog / MessageLogPanel. One line at a time, italic purple, portrait-safe near the top and clear
/// of the bottom touch controls. Tap the line to dismiss; a small history anchor expands the last-20
/// (run-scoped, from the scheduler's serialized history); a quiet button mutes the current floor.
///
/// No queue: <see cref="ShowLine"/> simply replaces the current line. The scheduler decides whether a
/// new line supersedes (strictly higher tier) via the <see cref="CurrentTier"/> probe, so the ribbon
/// only ever receives lines that are allowed to land.
/// </summary>
public sealed partial class VoiceRibbon : Control
{
    [Signal] public delegate void HistoryRequestedEventHandler();
    [Signal] public delegate void QuietRequestedEventHandler();

    private const int FontSize = 22;
    private static readonly Color Purple = new("b090d0");

    private RichTextLabel? _line;
    private PanelContainer? _bar;
    private PanelContainer? _historyPanel;
    private RichTextLabel? _historyText;

    private double _expireAt;          // Time.GetTicksMsec()/1000 when the current line auto-dismisses
    private int? _currentTier;         // tier of the line on screen, null when empty — the supersede probe

    /// <summary>Tier of the line currently displayed, or null if the ribbon is empty/expired.</summary>
    public int? CurrentTier => _currentTier;

    public override void _Ready()
    {
        // Portrait-safe: a top band, inset from the edges, clear of the bottom touch controls.
        SetAnchorsPreset(LayoutPreset.TopWide);
        OffsetTop = 96;                // below the status bar
        OffsetLeft = 12;
        OffsetRight = -12;
        OffsetBottom = 150;
        MouseFilter = MouseFilterEnum.Ignore;   // container passes through; children opt back in

        _bar = new PanelContainer { Visible = false, MouseFilter = MouseFilterEnum.Stop };
        var bg = new StyleBoxFlat
        {
            BgColor = new Color(0.06f, 0.05f, 0.09f, 0.82f),
            BorderColor = Purple,
            ContentMarginLeft = 12, ContentMarginRight = 8, ContentMarginTop = 6, ContentMarginBottom = 6,
        };
        bg.SetBorderWidthAll(0);
        bg.BorderWidthLeft = 3;
        bg.SetCornerRadiusAll(6);
        _bar.AddThemeStyleboxOverride("panel", bg);
        AddChild(_bar);
        // Fill the ribbon Control's rect. MUST be SetAnchorsAndOffsetsPreset, not SetAnchorsPreset:
        // the latter defaults to keepOffsets=false, which PRESERVES the control's current (content-
        // minimum) size and only repositions it — so the bar stayed a 117x863 vertical strip on device.
        // Setting anchors AND offsets to FullRect resizes it to the parent's 696x54, so the label lays
        // out on one horizontal line. (Device geometry dump caught the strip; there is no headless
        // Godot seam to unit-test this.)
        _bar.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var row = new HBoxContainer();
        _bar.AddChild(row);

        _line = new RichTextLabel
        {
            // FitContent must stay OFF: it reports a min-height computed by wrapping at the label's
            // MINIMUM width, which balloons the PanelContainer to ~863px tall (device geometry) even
            // though the line renders on one row at the real width. With it off, the bar's height comes
            // from its FullRect anchors (~54) and the label fills its row.
            BbcodeEnabled = true,
            FitContent = false,
            ScrollActive = false,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            MouseFilter = MouseFilterEnum.Stop,   // tap the line to dismiss
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            SizeFlagsVertical = SizeFlags.ExpandFill,
        };
        _line.AddThemeFontSizeOverride("normal_font_size", FontSize);
        _line.GuiInput += OnLineInput;
        row.AddChild(_line);

        row.AddChild(MakeGlyphButton("⋯", () => EmitSignal(SignalName.HistoryRequested)));  // ⋯ history
        row.AddChild(MakeGlyphButton("\U0001F910", () => EmitSignal(SignalName.QuietRequested))); // 🤫 quiet floor

        SetProcess(true);
    }

    private Button MakeGlyphButton(string glyph, System.Action onPressed)
    {
        var b = new Button
        {
            Text = glyph,
            Flat = true,
            CustomMinimumSize = new Vector2(44, 44),   // touch target
            MouseFilter = MouseFilterEnum.Stop,
        };
        b.Pressed += () => onPressed();
        return b;
    }

    public override void _Process(double delta)
    {
        if (_currentTier == null) return;
        if (Time.GetTicksMsec() / 1000.0 >= _expireAt) Dismiss();
    }

    /// <summary>
    /// Display a delivered line. Replaces whatever is showing (no queue). <paramref name="tier"/> becomes
    /// the new supersede probe; <paramref name="seconds"/> is the auto-dismiss duration from settings.
    /// </summary>
    public void ShowLine(string text, int tier, float seconds)
    {
        if (_line == null || _bar == null) return;
        _line.Text = $"[i][color=#b090d0]{text}[/color][/i]";
        _currentTier = tier;
        _expireAt = Time.GetTicksMsec() / 1000.0 + seconds;
        _bar.Visible = true;
    }

    /// <summary>Clear the ribbon (tap-to-dismiss or auto-expire). The tier probe goes null.</summary>
    public void Dismiss()
    {
        _currentTier = null;
        if (_bar != null) _bar.Visible = false;
    }

    /// <summary>Toggle the history popup, rendering the scheduler's run-scoped last-20 (newest first).</summary>
    public void ToggleHistory(IReadOnlyList<VoiceHistoryEntry> history)
    {
        if (_historyPanel != null && _historyPanel.Visible)
        {
            _historyPanel.Visible = false;
            return;
        }
        EnsureHistoryPanel();
        var lines = new List<string>();
        for (int i = history.Count - 1; i >= 0; i--)
            lines.Add($"[color=#8878a0]· {history[i].Line}[/color]");
        _historyText!.Text = history.Count == 0
            ? "[color=#6a6a6a][i]No lines yet this run.[/i][/color]"
            : string.Join("\n", lines);
        _historyPanel!.Visible = true;
    }

    private void EnsureHistoryPanel()
    {
        if (_historyPanel != null) return;
        _historyPanel = new PanelContainer { MouseFilter = MouseFilterEnum.Stop };
        _historyPanel.SetAnchorsPreset(LayoutPreset.TopWide);
        _historyPanel.OffsetTop = 54;
        var box = new StyleBoxFlat { BgColor = new Color(0.05f, 0.04f, 0.08f, 0.94f) };
        box.SetCornerRadiusAll(6);
        box.ContentMarginLeft = box.ContentMarginRight = box.ContentMarginTop = box.ContentMarginBottom = 10;
        _historyPanel.AddThemeStyleboxOverride("panel", box);
        var scroll = new ScrollContainer { CustomMinimumSize = new Vector2(0, 260) };
        _historyPanel.AddChild(scroll);
        _historyText = new RichTextLabel
        {
            BbcodeEnabled = true, FitContent = true,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
        };
        _historyText.AddThemeFontSizeOverride("normal_font_size", 18);
        scroll.AddChild(_historyText);
        AddChild(_historyPanel);
        _historyPanel.Visible = false;
    }

    private void OnLineInput(InputEvent @event)
    {
        if (@event is InputEventScreenTouch { Pressed: true } or InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
            Dismiss();
    }
}
