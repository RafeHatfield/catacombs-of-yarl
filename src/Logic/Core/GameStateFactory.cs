using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Creates GameState instances from scenario definitions. Single source of truth
/// for entity setup — used by both the harness and the presentation layer.
/// </summary>
public static class GameStateFactory
{
    /// <summary>
    /// Create a GameState from a scenario definition with deterministic seed.
    /// </summary>
    public static GameState FromScenario(
        ScenarioDefinition scenario,
        int seed,
        MonsterFactory monsterFactory,
        ItemFactory? itemFactory = null,
        ConsumableFactory? consumableFactory = null)
    {
        var rng = new SeededRandom(seed);
        var map = GameMap.CreateArena(12, 12);

        var player = CreatePlayer(scenario, itemFactory, consumableFactory);
        player.X = 3;
        player.Y = 6;
        map.RegisterEntity(player);

        var monsters = CreateMonsters(scenario, map, rng, monsterFactory);

        return new GameState(player, monsters, map, rng, scenario.TurnLimit);
    }

    private static Entity CreatePlayer(
        ScenarioDefinition scenario,
        ItemFactory? itemFactory,
        ConsumableFactory? consumableFactory)
    {
        var def = scenario.Player;
        var player = new Entity(0, "Player", 0, 0, blocksMovement: true);
        player.Add(new Fighter(
            hp: def.Hp,
            strength: def.Strength,
            dexterity: def.Dexterity,
            constitution: def.Constitution,
            accuracy: def.Accuracy,
            evasion: def.Evasion,
            damageMin: def.DamageMin,
            damageMax: def.DamageMax));

        Equipment? playerEquipment = null;
        if (itemFactory != null && (def.Weapon != null || def.Armor != null))
        {
            playerEquipment = player.Add(new Equipment());
            if (def.Weapon != null)
            {
                var weapon = itemFactory.Create(def.Weapon);
                if (weapon != null) playerEquipment.MainHand = weapon;
            }
            if (def.Armor != null)
            {
                var armor = itemFactory.Create(def.Armor);
                if (armor != null) playerEquipment.Chest = armor;
            }
        }

        // Speed bonus for momentum system — from scenario config and/or weapon
        double weaponSpeed = playerEquipment?.MainHand?.Get<SpeedBonusTracker>()?.EquipmentRatio ?? 0;
        if (def.SpeedBonus > 0 || weaponSpeed > 0)
            player.Add(new SpeedBonusTracker(baseRatio: def.SpeedBonus) { EquipmentRatio = weaponSpeed });

        if (consumableFactory != null && scenario.Items.Count > 0)
        {
            var inventory = player.Add(new Inventory());
            foreach (var itemDef in scenario.Items)
            {
                for (int i = 0; i < itemDef.Count; i++)
                {
                    var item = consumableFactory.Create(itemDef.Type);
                    if (item != null) inventory.Add(item);
                }
            }
        }

        return player;
    }

    private static List<Entity> CreateMonsters(
        ScenarioDefinition scenario,
        GameMap map,
        SeededRandom rng,
        MonsterFactory monsterFactory)
    {
        var monsters = new List<Entity>();
        int idx = 0;
        foreach (var monsterDef in scenario.Monsters)
        {
            for (int i = 0; i < monsterDef.Count; i++)
            {
                var monster = monsterFactory.Create(monsterDef.Type, depth: scenario.Depth, rng: rng);
                if (monster != null)
                {
                    monster.X = 8 + (idx % 3);
                    monster.Y = 4 + (idx / 3) * 2;
                    map.RegisterEntity(monster);
                    monsters.Add(monster);
                    idx++;
                }
            }
        }
        return monsters;
    }
}
