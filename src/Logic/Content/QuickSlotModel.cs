using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// What one quick-slot shows: which item, what badge, and whether it can be used right now.
///
/// BadgeCount is the stack size for consumables and the charge count for wands;
/// Infinite wands report Infinite=true and BadgeCount is meaningless for them.
///
/// Available=false means a tap would be refused by the rules — a cooldown-gated potion
/// still on cooldown, or a wand with no charges. CooldownRemaining is the turns left,
/// and is 0 whenever Available is true.
/// </summary>
public readonly record struct QuickSlotEntry(
    int    ItemId,
    string DisplayName,
    int    BadgeCount,
    bool   Infinite,
    bool   Available,
    int    CooldownRemaining);

/// <summary>
/// Builds the quick-slot bar's contents as plain data, independent of how it is drawn.
///
/// This exists so the presentation layer can answer "did anything the bar shows change
/// this turn?" without enumerating which turn events happen to imply an inventory change.
/// That enumeration is what broke: a buff potion consumed via ResolveSpellAction emits
/// SpellEvent/StatusAppliedEvent, neither of which was on the list, so the bar kept
/// rendering an item the player had already drunk.
///
/// Lives in Logic.Content (not Presentation) so it can be tested without Godot —
/// same rationale as ItemDisplay, which it sits next to.
///
/// No game rules live here. Availability MIRRORS the gates in TurnController
/// (CanUsePotion) and WandComponent.HasCharges; it never decides them.
/// </summary>
public static class QuickSlotModel
{
    /// <summary>
    /// Snapshot every item the quick-slot bar would show, in inventory order.
    ///
    /// Membership matches QuickSlotBar.RefreshItemSlots: anything carrying a Consumable
    /// or a SpellEffect. Returns an empty list when the player has no inventory.
    /// </summary>
    public static List<QuickSlotEntry> Build(GameState state)
    {
        var entries = new List<QuickSlotEntry>();

        var inventory = state.PlayerInventory;
        if (inventory == null) return entries;

        var fighter = state.PlayerFighter;

        foreach (var item in inventory.Items)
        {
            var consumable = item.Get<Consumable>();
            var spell      = item.Get<SpellEffect>();
            if (consumable == null && spell == null) continue;

            var wand = item.Get<WandComponent>();

            int  badge    = wand != null ? wand.Charges : consumable?.StackSize ?? 0;
            bool infinite = wand?.Infinite ?? false;

            // Mirror of the rules' own gates — never a new rule.
            //   Wand:   WandComponent.HasCharges
            //   Potion: TurnController.CanUsePotion — no cooldown on the item, or none pending.
            bool available = wand != null
                ? wand.HasCharges
                : consumable == null
                    || consumable.UseCooldownTurns == 0
                    || fighter.PotionCooldownRemaining == 0;

            entries.Add(new QuickSlotEntry(
                ItemId:            item.Id,
                DisplayName:       ItemDisplay.GetDisplayName(item, state.IdentificationRegistry, state.AppearancePool),
                BadgeCount:        badge,
                Infinite:          infinite,
                Available:         available,
                CooldownRemaining: available ? 0 : fighter.PotionCooldownRemaining));
        }

        return entries;
    }

    /// <summary>
    /// The entity ID of the weapon in the main hand, or null for bare fists.
    /// Part of the bar's visible state, so it belongs in the change check.
    /// </summary>
    public static int? MainHandItemId(GameState state)
        => state.Player.Get<Equipment>()?.MainHand?.Id;
}
