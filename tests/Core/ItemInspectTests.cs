using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Knowledge;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Core;

/// <summary>
/// Tests for ItemInspectView.From — verifies correct stat lines for each item category.
/// </summary>
[TestFixture]
public class ItemInspectTests
{
    private static Entity MakeEntity(int id, string name) => new(id, name);

    [Test]
    public void Weapon_ShowsDamageRange()
    {
        var item = MakeEntity(1, "Short Sword");
        item.Add(new Equippable(EquipmentSlot.MainHand) { DamageMin = 4, DamageMax = 8 });

        var view = ItemInspectView.From(item);

        Assert.That(view.Category, Is.EqualTo("Weapon"));
        Assert.That(view.StatLines, Has.Some.Contains("4-8"));
    }

    [Test]
    public void Weapon_ShowsAccuracyBonus()
    {
        var item = MakeEntity(2, "Enchanted Sword +2");
        item.Add(new Equippable(EquipmentSlot.MainHand) { DamageMin = 4, DamageMax = 8, ToHitBonus = 2 });

        var view = ItemInspectView.From(item);

        Assert.That(view.StatLines, Has.Some.Contains("Accuracy: +2"));
    }

    [Test]
    public void Armor_ShowsAcBonus()
    {
        var item = MakeEntity(3, "Leather Armor");
        item.Add(new Equippable(EquipmentSlot.Chest) { ArmorClassBonus = 3 });

        var view = ItemInspectView.From(item);

        // Chest slot → Armor category
        Assert.That(view.Category, Is.EqualTo("Armor"));
        Assert.That(view.StatLines, Has.Some.Contains("AC Bonus: +3"));
    }

    [Test]
    public void Wand_ShowsChargesAndSpell()
    {
        var item = MakeEntity(4, "Wand of Lightning");
        item.Add(new SpellEffect { SpellId = "lightning", Targeting = TargetingMode.AutoClosest });
        item.Add(new WandComponent { Charges = 3, MaxCharges = 10 });

        var view = ItemInspectView.From(item);

        Assert.That(view.Category, Is.EqualTo("Wand"));
        Assert.That(view.StatLines, Has.Some.Contains("Spell:").And.Some.Contains("Lightning"));
        Assert.That(view.StatLines, Has.Some.Contains("3/10"));
    }

    [Test]
    public void Wand_InfiniteCharges_ShowsInfinitySymbol()
    {
        var item = MakeEntity(5, "Wand of Portals");
        item.Add(new SpellEffect { SpellId = "portal", Targeting = TargetingMode.Portal });
        item.Add(new WandComponent { Infinite = true, MaxCharges = 10 });

        var view = ItemInspectView.From(item);

        Assert.That(view.StatLines, Has.Some.Contains("\u221e"),
            "Infinite wand should show infinity symbol for charges");
    }

    [Test]
    public void Scroll_ShowsSpellName()
    {
        var item = MakeEntity(6, "Scroll of Magic Mapping");
        item.Add(new SpellEffect { SpellId = "magic_mapping", Targeting = TargetingMode.Self });
        item.Add(new Consumable(healAmount: 0) { StackSize = 1 });

        var view = ItemInspectView.From(item);

        Assert.That(view.Category, Is.EqualTo("Scroll"));
        Assert.That(view.StatLines, Has.Some.Contains("Magic Mapping"));
    }

    [Test]
    public void Potion_ShowsHealAmount()
    {
        var item = MakeEntity(7, "Healing Potion");
        item.Add(new Consumable(healAmount: 25) { StackSize = 1 });

        var view = ItemInspectView.From(item);

        Assert.That(view.Category, Is.EqualTo("Potion"));
        Assert.That(view.StatLines, Has.Some.Contains("25 HP"));
    }
}
