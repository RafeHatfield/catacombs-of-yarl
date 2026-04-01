using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Displays active status effects as badges in the HUD.
/// Each badge shows the effect short name and remaining turns: [Poison 7], [Shield 4].
///
/// Color coding:
///   Debuffs (poison, burning, slowed, disarmed, blinded, sleep, weakness, entangled,
///            disoriented, silenced, immobilized, fear): red/orange
///   Buffs   (shield, protection, barkskin, regeneration, speed, focused, invisible): green/blue
///   Neutral (sluggish, aggravated): gray
///
/// Updated from the player entity via Refresh(). Clears when no effects are active.
/// </summary>
public sealed partial class StatusEffectBar : Control
{
    private HBoxContainer? _badgeRow;

    // Badge colors by category
    private static readonly Color DebuffColor  = new(1f, 0.4f, 0.4f);   // red/orange
    private static readonly Color BuffColor    = new(0.4f, 1f, 0.6f);   // green
    private static readonly Color NeutralColor = new(0.7f, 0.7f, 0.7f); // gray

    // Short display names for each effect — keyed on EffectName property.
    private static readonly Dictionary<string, string> ShortNames = new(StringComparer.OrdinalIgnoreCase)
    {
        ["poison"]     = "Psn",
        ["burning"]    = "Burn",
        ["plague"]     = "Plg",
        ["slowed"]     = "Slw",
        ["immobilized"] = "Imm",
        ["sleep"]      = "Slp",
        ["disarmed"]   = "Dis",
        ["blinded"]    = "Bld",
        ["weakness"]   = "Wk",
        ["entangled"]  = "Ent",
        ["disoriented"] = "Cnf",
        ["silenced"]   = "Sil",
        ["fear"]       = "Fea",
        ["shield"]     = "Shd",
        ["protection"] = "Pro",
        ["barkskin"]   = "Brk",
        ["regeneration"] = "Reg",
        ["speed"]      = "Spd",
        ["focused"]    = "Foc",
        ["invisibility"] = "Inv",
        ["sluggish"]   = "Slg",
        ["enraged"]    = "Rge",
        ["taunted"]    = "Tnt",
        ["aggravated"] = "Agg",
    };

    // Debuff effect names (used for color assignment).
    private static readonly HashSet<string> DebuffNames = new(StringComparer.OrdinalIgnoreCase)
    {
        "poison", "burning", "plague", "slowed", "immobilized", "sleep",
        "disarmed", "blinded", "weakness", "entangled", "disoriented",
        "silenced", "fear", "enraged",
    };

    // Buff effect names (everything not in debuff or neutral is treated as neutral fallback).
    private static readonly HashSet<string> BuffNames = new(StringComparer.OrdinalIgnoreCase)
    {
        "shield", "protection", "barkskin", "regeneration", "speed", "focused", "invisibility",
    };

    public override void _Ready()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Ignore;

        _badgeRow = new HBoxContainer
        {
            MouseFilter = MouseFilterEnum.Ignore,
            SizeFlagsHorizontal = SizeFlags.ShrinkBegin,
        };
        _badgeRow.AddThemeConstantOverride("separation", 4);
        AddChild(_badgeRow);
    }

    /// <summary>
    /// Refresh the badge row from the player entity's current status effects.
    /// Call this from HUD.Refresh() after every turn.
    /// </summary>
    public void Refresh(Entity? player)
    {
        if (_badgeRow == null) return;

        // Clear existing badges.
        foreach (Node child in _badgeRow.GetChildren())
            child.SafeFree();

        if (player == null) return;

        // Collect all active effects.
        var effects = player.GetAllComponents().OfType<IStatusEffect>().ToList();
        if (effects.Count == 0) return;

        // Sort: debuffs first, then buffs, then neutral. Within each group: alphabetical.
        effects.Sort((a, b) =>
        {
            int catA = Category(a.EffectName);
            int catB = Category(b.EffectName);
            if (catA != catB) return catA.CompareTo(catB);
            return string.Compare(a.EffectName, b.EffectName, StringComparison.OrdinalIgnoreCase);
        });

        foreach (var effect in effects)
        {
            var badge = BuildBadge(effect);
            _badgeRow.AddChild(badge);
        }
    }

    private Control BuildBadge(IStatusEffect effect)
    {
        string shortName = ShortNames.TryGetValue(effect.EffectName, out var sn) ? sn : effect.EffectName[..3].ToUpper();
        string text = effect.IsPermanent ? shortName : $"{shortName} {effect.RemainingTurns}";
        Color color = EffectColor(effect.EffectName);

        var label = new Label
        {
            Text = text,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        label.AddThemeFontSizeOverride("font_size", 18);
        label.AddThemeColorOverride("font_color", color);

        // Minimal background.
        var panel = new PanelContainer { MouseFilter = MouseFilterEnum.Ignore };
        var style = new StyleBoxFlat
        {
            BgColor               = new Color(0.05f, 0.05f, 0.1f, 0.7f),
            CornerRadiusTopLeft   = 3,
            CornerRadiusTopRight  = 3,
            CornerRadiusBottomLeft  = 3,
            CornerRadiusBottomRight = 3,
            ContentMarginLeft   = 5f,
            ContentMarginRight  = 5f,
            ContentMarginTop    = 1f,
            ContentMarginBottom = 1f,
        };
        panel.AddThemeStyleboxOverride("panel", style);
        panel.AddChild(label);

        return panel;
    }

    private static Color EffectColor(string effectName) =>
        DebuffNames.Contains(effectName) ? DebuffColor :
        BuffNames.Contains(effectName)  ? BuffColor :
        NeutralColor;

    /// <summary>0 = debuff (sort first), 1 = buff, 2 = neutral.</summary>
    private static int Category(string effectName) =>
        DebuffNames.Contains(effectName) ? 0 :
        BuffNames.Contains(effectName)  ? 1 : 2;
}
