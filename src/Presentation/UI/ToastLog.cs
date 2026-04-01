using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

using CatacombsOfYarl.Presentation;
using System.Globalization;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Floating toast messages overlaid on the dungeon. Each combat event
/// appears as a line of text that fades out after a few seconds.
///
/// Messages stack vertically (newest at bottom), slide upward as new
/// messages push them, and are removed once fully transparent.
///
/// No persistent background — the dungeon shows through.
/// </summary>
public sealed partial class ToastLog : Control
{
    private const float DisplayDuration = 2.5f;  // seconds before fade begins
    private const float FadeDuration    = 0.8f;  // seconds to fade to zero
    private const int   MaxToasts       = 5;
    private const int   FontSize        = 24;

    private int _playerId;
    private VBoxContainer? _stack;
    // Shared style — created once, reused across all toasts to avoid RefCounted GC churn.
    private StyleBoxFlat? _toastStyle;
    private FontFile? _monoFont;

    // Timer-based cleanup: avoids Callable.From() leak in Godot 4 C#.
    // Each toast records its creation time; _Process culls expired toasts.
    private readonly List<(RichTextLabel Label, double ExpireTime, double FadeEndTime)> _activeToasts = new();

    public override void _Ready()
    {
        BuildLayout();
        SetProcess(true);
    }

    public override void _Process(double delta)
    {
        double now = Time.GetTicksMsec() / 1000.0;
        for (int i = _activeToasts.Count - 1; i >= 0; i--)
        {
            var (label, expireTime, fadeEndTime) = _activeToasts[i];

            if (now >= fadeEndTime)
            {
                // Fade complete — remove immediately (no Callable.From needed).
                label.SafeFree();
                _activeToasts.RemoveAt(i);
            }
            else if (now >= expireTime)
            {
                // In fade phase — lerp alpha from 1 to 0.
                float t = (float)((now - expireTime) / FadeDuration);
                var m = label.Modulate;
                label.Modulate = new Color(m.R, m.G, m.B, 1f - t);
            }
        }
    }

    public void SetPlayerId(int playerId) => _playerId = playerId;

    /// <summary>Number of currently-visible toasts. Useful for debug overlay.</summary>
    public int ToastCount => _activeToasts.Count;

    /// <summary>Show an arbitrary message as a toast (e.g. auto-explore stop reason).</summary>
    public void AddMessage(string text) => SpawnToast(text);

    /// <summary>Add messages from a completed turn's events.</summary>
    public void RecordTurn(TurnResult result, GameState state)
    {
        foreach (var evt in result.Events)
        {
            var msg = FormatEvent(evt, state);
            if (msg != null)
                SpawnToast(msg);
        }
    }

    // -------------------------------------------------------------------------

    private void BuildLayout()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Ignore;

        var font = GD.Load<FontFile>("res://src/Presentation/assets/fonts/PixeloidMono.ttf");
        font.Antialiasing = TextServer.FontAntialiasing.None;
        font.SubpixelPositioning = TextServer.SubpixelPositioning.Disabled;
        font.Hinting = TextServer.Hinting.None;
        _monoFont = font;

        _stack = new VBoxContainer
        {
            // Align stacked messages toward the bottom of our area.
            Alignment           = BoxContainer.AlignmentMode.End,
            SizeFlagsHorizontal = SizeFlags.ShrinkBegin,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        _stack.AddThemeConstantOverride("separation", 2);
        _stack.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(_stack);
    }

    private void SpawnToast(string bbcode)
    {
        if (_stack == null) return;

        // Enforce max visible toasts — remove oldest if over limit.
        // Also remove from tracking list so _Process doesn't try to fade a freed node.
        while (_stack.GetChildCount() >= MaxToasts)
        {
            var oldest = _stack.GetChild(0);
            oldest.SafeFree();
            _activeToasts.RemoveAll(t => t.Label == oldest);
        }

        var label = new RichTextLabel
        {
            BbcodeEnabled       = true,
            FitContent          = true,
            AutowrapMode        = TextServer.AutowrapMode.Off,
            ScrollActive        = false,
            MouseFilter         = MouseFilterEnum.Ignore,
            SizeFlagsHorizontal = SizeFlags.ShrinkBegin,
        };
        if (_monoFont != null) label.AddThemeFontOverride("normal_font", _monoFont);
        label.AddThemeFontSizeOverride("normal_font_size", FontSize);
        label.AddThemeColorOverride("default_color", Colors.White);
        label.AppendText(bbcode);

        _toastStyle ??= new StyleBoxFlat
        {
            BgColor                 = new Color(0f, 0f, 0f, 0.55f),
            CornerRadiusTopLeft     = 4,
            CornerRadiusTopRight    = 4,
            CornerRadiusBottomLeft  = 4,
            CornerRadiusBottomRight = 4,
            ContentMarginLeft       = 8f,
            ContentMarginRight      = 8f,
            ContentMarginTop        = 2f,
            ContentMarginBottom     = 2f,
        };
        label.AddThemeStyleboxOverride("normal", _toastStyle);

        _stack.AddChild(label);

        // Track for timer-based fade + removal in _Process.
        // Avoids Callable.From() which leaks delegate GCHandles in Godot 4 C#.
        double now = Time.GetTicksMsec() / 1000.0;
        _activeToasts.Add((label, now + DisplayDuration, now + DisplayDuration + FadeDuration));
    }

    // -------------------------------------------------------------------------

    private string? FormatEvent(TurnEvent evt, GameState state)
    {
        bool isPlayer = evt.ActorId == _playerId;
        string actorName = isPlayer ? "You" : GetEntityName(evt.ActorId, state);
        string targetName(int id) => id == _playerId ? "you" : GetEntityName(id, state).ToLower();

        return evt switch
        {
            AttackEvent { Hit: false } atk =>
                $"[color=gray]{actorName} miss{(isPlayer ? "" : "es")} {targetName(atk.TargetId)}.[/color]",

            AttackEvent { IsCritical: true } atk =>
                $"[color=yellow]CRIT! {actorName} hit{(isPlayer ? "" : "s")} {targetName(atk.TargetId)} for {atk.Damage}![/color]",

            AttackEvent { IsBonusAttack: true } atk =>
                $"[color=cyan]+{atk.Damage} bonus hit on {targetName(atk.TargetId)}[/color]",

            AttackEvent atk =>
                $"{actorName} hit{(isPlayer ? "" : "s")} {targetName(atk.TargetId)} for [color=white]{atk.Damage}[/color].",

            HealEvent heal =>
                $"[color=lime]+{heal.AmountHealed} HP[/color] from {heal.ItemName}.",

            DeathEvent death when death.ActorId == _playerId =>
                "[color=red]You die...[/color]",

            DeathEvent =>
                $"[color=green]{GetEntityName(evt.ActorId, state)} dies![/color]",

            SplitEvent split when split.ChildIds.Count > 0 =>
                $"[color=yellow]The {GetEntityName(split.OriginalId, state)} splits into " +
                $"{split.ChildIds.Count} {GetEntityName(split.ChildIds[0], state).ToLower()}s![/color]",

            SplitEvent split =>
                $"[color=yellow]The {GetEntityName(split.OriginalId, state)} splits![/color]",

            PickUpEvent pickup =>
                $"Picked up {pickup.ItemName}.",

            ItemUseEvent { Success: true } use =>
                $"[color=yellow]{actorName} uses {use.ItemName}![/color]",

            ItemUseEvent { FailureMode: "fizzle" } use =>
                $"[color=gray]{actorName} tries {use.ItemName}... it fizzles.[/color]",

            ItemUseEvent { FailureMode: "wrong_target" } use =>
                $"[color=lime]{actorName} fumbles {use.ItemName} — it backfires![/color]",

            ItemUseEvent { FailureMode: "equipment_damage" } use =>
                $"[color=orange]{actorName} mishandles {use.ItemName} — weapon damaged![/color]",

            // ── Status effect events ─────────────────────────────────────────────────
            // Apply: "You are poisoned!" / "The orc is confused!"
            StatusAppliedEvent statusApplied when statusApplied.TargetId == _playerId =>
                $"[color=orange]You are {statusApplied.EffectName}![/color]",

            StatusAppliedEvent statusApplied =>
                $"[color=orange]The {GetEntityName(statusApplied.TargetId, state).ToLower()} is {statusApplied.EffectName}![/color]",

            // Expire: "The poison fades." / "You are no longer slowed."
            StatusExpiredEvent expired when expired.EntityId == _playerId && expired.Reason == "duration" =>
                $"[color=gray]The {expired.EffectName} fades.[/color]",

            StatusExpiredEvent expired when expired.EntityId == _playerId =>
                $"[color=gray]You are no longer {expired.EffectName}.[/color]",

            StatusExpiredEvent expired when expired.Reason == "duration" =>
                $"[color=gray]The {GetEntityName(expired.EntityId, state).ToLower()} is no longer {expired.EffectName}.[/color]",

            // DOT damage: distinct orange line.
            DotDamageEvent dot when dot.EntityId == _playerId =>
                $"[color=orange]{Capitalize(dot.EffectName)} deals {dot.Damage} damage.[/color]",

            DotDamageEvent dot =>
                $"[color=orange]{Capitalize(dot.EffectName)} damages the {GetEntityName(dot.EntityId, state).ToLower()}.[/color]",

            // HOT healing: green line.
            HotHealEvent hot when hot.EntityId == _playerId =>
                $"[color=lime]+{hot.Amount} HP from {hot.EffectName}.[/color]",

            _ => null,
        };
    }

    private static string Capitalize(string s) =>
        string.IsNullOrEmpty(s) ? s :
        char.ToUpper(s[0], CultureInfo.InvariantCulture) + s[1..];

    private static string GetEntityName(int id, GameState state)
    {
        if (state.Player.Id == id) return "Player";
        return state.Monsters.FirstOrDefault(m => m.Id == id)?.Name ?? "Unknown";
    }
}
