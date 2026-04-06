using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Presentation.Input;

/// <summary>
/// Describes the active targeting operation when the game is in GamePhase.Targeting.
/// Holds the item being aimed and the spell parameters needed to show targeting UI
/// (range ring, valid target highlights) and route the eventual tap to CastSpell.
///
/// Created by GameController.HandleScrollOrWandUse when the SpellEffect.Targeting
/// mode is SingleTarget or Location. Cleared on CancelTargeting or TargetChosen.
/// </summary>
public sealed class TargetingState
{
    /// <summary>The scroll or wand entity being aimed.</summary>
    public required Entity Item { get; init; }

    /// <summary>The spell effect attached to the item.</summary>
    public required SpellEffect Spell { get; init; }

    /// <summary>Targeting mode driving how taps are interpreted.</summary>
    public TargetingMode Mode { get; init; }

    /// <summary>Maximum targeting range in tiles (0 = unlimited).</summary>
    public int Range { get; init; }

    /// <summary>AoE radius for visual preview (0 = no AoE preview).</summary>
    public int Radius { get; init; }

    /// <summary>
    /// True when this targeting session is for a throwable potion (tap = throw, self-tap = drink).
    /// False for scrolls, wands, and non-throwable potions.
    /// </summary>
    public bool IsThrowPotion { get; init; }

    /// <summary>
    /// Throw spell ID (e.g., "throw_weakness"). Set when IsThrowPotion=true.
    /// Used by GameController to construct the correct CastSpell action.
    /// </summary>
    public string? ThrowSpellId { get; init; }

    /// <summary>
    /// Drink spell ID for self-tap fallback (e.g., "drink_weakness").
    /// Null for throw-only potions (self-tap cancels instead of drinking).
    /// </summary>
    public string? DrinkSpellId { get; init; }
}
