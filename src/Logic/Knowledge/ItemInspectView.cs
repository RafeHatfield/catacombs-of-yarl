using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Knowledge;

/// <summary>
/// Pure data record for the item inspect UI.
/// Built from an Entity's components — all Godot-free so it can be populated and tested in logic layer.
/// </summary>
public sealed record ItemInspectView(
    string Name,
    string Category,
    IReadOnlyList<string> StatLines
)
{
    /// <summary>
    /// Build an ItemInspectView from an item entity by reading its components.
    /// Returns a view with generic "Unknown Item" if no recognized components are found.
    /// </summary>
    public static ItemInspectView From(Entity item)
    {
        var lines = new List<string>();
        string category = "Item";

        var equippable = item.Get<Equippable>();
        var consumable = item.Get<Consumable>();
        var spellEffect = item.Get<SpellEffect>();
        var wand = item.Get<WandComponent>();

        if (equippable != null)
        {
            bool isWeapon = equippable.Slot == EquipmentSlot.MainHand || equippable.Slot == EquipmentSlot.OffHand;

            if (isWeapon)
            {
                category = "Weapon";
                if (equippable.DamageMin > 0 || equippable.DamageMax > 0)
                    lines.Add($"Damage: {equippable.DamageMin}-{equippable.DamageMax}");
                if (equippable.ToHitBonus != 0)
                    lines.Add($"Accuracy: +{equippable.ToHitBonus}");
                if (!string.IsNullOrEmpty(equippable.DamageType))
                    lines.Add($"Type: {equippable.DamageType}");
            }
            else
            {
                // Armor slot
                category = equippable.Slot switch
                {
                    EquipmentSlot.Head  => "Helmet",
                    EquipmentSlot.Chest => "Armor",
                    EquipmentSlot.Feet  => "Boots",
                    EquipmentSlot.LeftRing or EquipmentSlot.RightRing => "Ring",
                    EquipmentSlot.Neck  => "Amulet",
                    _                   => "Armor",
                };

                if (equippable.ArmorClassBonus != 0)
                    lines.Add($"AC Bonus: +{equippable.ArmorClassBonus}");
            }
        }
        else if (wand != null && spellEffect != null)
        {
            category = "Wand";
            if (!string.IsNullOrEmpty(spellEffect.SpellId))
                lines.Add($"Spell: {FormatSpellId(spellEffect.SpellId)}");

            string chargesText = wand.Infinite ? "\u221e" : $"{wand.Charges}/{wand.MaxCharges}";
            lines.Add($"Charges: {chargesText}");
        }
        else if (spellEffect != null && consumable != null)
        {
            category = "Scroll";
            if (!string.IsNullOrEmpty(spellEffect.SpellId))
                lines.Add($"Spell: {FormatSpellId(spellEffect.SpellId)}");
        }
        else if (consumable != null)
        {
            category = "Potion";
            if (consumable.HealAmount > 0)
                lines.Add($"Heals: {consumable.HealAmount} HP");
            else
                lines.Add("Effect: Unknown");
        }

        return new ItemInspectView(item.Name, category, lines);
    }

    /// <summary>
    /// Format a spell ID for human-readable display.
    /// "magic_mapping" → "Magic Mapping", "lightning" → "Lightning".
    /// </summary>
    private static string FormatSpellId(string spellId)
    {
        if (string.IsNullOrEmpty(spellId)) return spellId;

        // Replace underscores with spaces and title-case each word
        var parts = spellId.Split('_');
        for (int i = 0; i < parts.Length; i++)
        {
            if (parts[i].Length > 0)
                parts[i] = char.ToUpper(parts[i][0]) + parts[i][1..];
        }
        return string.Join(" ", parts);
    }
}
