namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Maps entity/item type IDs (from YAML content) to Oryx sprite names.
///
/// Monster sprites: res://src/Presentation/assets/sprites/heroes/{base}_{frame}.png
/// Item sprites:    res://src/Presentation/assets/sprites/items/{name}.png
///
/// Monster frames are 1-4 for animation. Items are single static sprites.
/// All sprites sourced from Oryx Ultimate Fantasy 1.2 and 8-Bit Remaster packs.
/// </summary>
public static class SpriteMapping
{
    public const string PlayerSprite = "knight";
    public const int FrameCount = 4;
    public const string MonsterSpritePath = "res://src/Presentation/assets/sprites/heroes";
    public const string ItemSpritePath = "res://src/Presentation/assets/sprites/items";

    // Monster YAML type ID → Oryx sprite base name (in heroes/ folder)
    private static readonly Dictionary<string, string> MonsterToSprite = new()
    {
        // Orcs (depth 1+)
        ["orc"]       = "goblin",
        ["orc_grunt"] = "goblin",
        ["orc_brute"] = "goblin_warrior",

        // Undead
        ["zombie"]    = "zombie_a",
        ["skeleton"]  = "skeleton",
        ["mummy"]     = "mummy",
        ["lich"]      = "lich",

        // Humanoids
        ["goblin"]    = "goblin",
        ["cultist"]   = "cultist",
        ["thief"]     = "thief",

        // Creatures
        ["rat"]       = "rat",
        ["giant_rat"] = "rat_giant",
        ["bat"]       = "bat",
        ["spider"]    = "spider_brown",

        // Bosses / deep
        ["ogre"]      = "ogre",
        ["troll"]     = "troll",
        ["demon"]     = "demon_red",
        ["minotaur"]  = "minotaur",
        ["golem"]     = "golem_stone",
    };

    // Item YAML type ID → Oryx sprite filename (without .png, in items/ folder)
    private static readonly Dictionary<string, string> ItemToSprite = new()
    {
        // Potions
        ["healing_potion"]         = "potion_red",
        ["mana_potion"]            = "potion_blue",
        ["poison_potion"]          = "potion_green",
        ["confusion_potion"]       = "potion_black",
        ["speed_potion"]           = "potion_white",

        // Weapons
        ["dagger"]                 = "weapon_dagger",
        ["poisoned_dagger"]        = "weapon_mystic_dagger",
        ["quickfang_dagger"]       = "weapon_vorpal_dagger",
        ["keen_dagger"]            = "weapon_gold_dagger",
        ["short_sword"]            = "weapon_sword",
        ["long_sword"]             = "weapon_broadsword",
        ["mace"]                   = "weapon_mace",
        ["spear"]                  = "weapon_spear",
        ["crossbow"]               = "weapon_crossbow",
        ["battle_axe"]             = "weapon_axe",
        ["staff"]                  = "weapon_staff",
        ["quarterstaff"]           = "weapon_quarterstaff",

        // Armor (chests)
        ["leather_armor"]          = "armor_leather_chest",
        ["studded_leather_armor"]  = "armor_studded_chest",
        ["chain_mail"]             = "armor_chain_chest",
        ["plate_mail"]             = "armor_plate_chest",
        ["cloth_robe"]             = "armor_cloth_chest",

        // Wands — mapped to staff sprites by element
        ["wand_of_fireball"]       = "weapon_magic_staff_chaos",
        ["wand_of_lightning"]      = "weapon_magic_staff_winged",
        ["wand_of_confusion"]      = "weapon_magic_staff_venom",
        ["wand_of_slow"]           = "weapon_magic_staff_venom",
        ["wand_of_teleportation"]  = "weapon_staff_ankh",
        ["wand_of_portals"]        = "weapon_staff_ankh",
        ["wand_of_rage"]           = "weapon_magic_staff_chaos",
        ["wand_of_glue"]           = "weapon_staff_jeweled",
        ["wand_of_dragon_farts"]   = "weapon_staff_jeweled",
        ["wand_of_yo_mama"]        = "weapon_staff_jeweled",

        // Rings
        ["ring_of_protection"]     = "ring_gold",
        ["ring_of_regeneration"]   = "ring_emerald",
        ["ring_of_resistance"]     = "ring_silver",
        ["ring_of_strength"]       = "ring_ruby",
        ["ring_of_dexterity"]      = "ring_azure",
        ["ring_of_constitution"]   = "ring_copper",
        ["ring_of_might"]          = "ring_ruby",
        ["ring_of_hummingbird"]    = "ring_diamond",
        ["ring_of_teleportation"]  = "ring_amethyst",
        ["ring_of_invisibility"]   = "ring_pearl",
        ["ring_of_speed"]          = "ring_flame",
        ["ring_of_luck"]           = "ring_ornate",
        ["ring_of_wizardry"]       = "ring_cold",
        ["ring_of_clarity"]        = "ring_diamond",
        ["ring_of_free_action"]    = "ring_silver",
        ["ring_of_searching"]      = "ring_ornate",

        // Scrolls / books
        ["scroll_of_identify"]     = "book_blue",
        ["scroll_of_magic_map"]    = "book_brown",
        ["scroll_of_enchant"]      = "book_latch",
        ["scroll_of_fire"]         = "book_red",
        ["scroll_of_teleport"]     = "book_green",
        ["scroll_of_curse"]        = "book_evil",
    };

    /// <summary>Get the sprite base name for a monster type ID.</summary>
    public static string? GetSpriteBase(string monsterTypeId)
    {
        return MonsterToSprite.GetValueOrDefault(monsterTypeId);
    }

    /// <summary>
    /// Get the full resource path for a monster sprite frame.
    /// Frame is 1-based (1-4).
    /// </summary>
    public static string GetFramePath(string spriteBase, int frame)
    {
        return $"{MonsterSpritePath}/{spriteBase}_{frame}.png";
    }

    /// <summary>
    /// Get the full resource path for an item sprite.
    /// Returns null if no mapping exists (caller should fall back to placeholder).
    /// </summary>
    public static string? GetItemSpritePath(string itemTypeId)
    {
        if (ItemToSprite.TryGetValue(itemTypeId, out var spriteName))
            return $"{ItemSpritePath}/{spriteName}.png";
        return null;
    }
}
