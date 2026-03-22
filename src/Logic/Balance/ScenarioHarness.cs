using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Bot heal thresholds — matches the Python prototype's "balanced" persona.
/// </summary>
public static class BotConfig
{
    public const double HealThreshold = 0.30;
    public const double PanicThreshold = 0.15;
}

/// <summary>
/// Runs scenario simulations with tile-based positioning and BotBrain AI.
/// </summary>
public sealed class ScenarioHarness
{
    private readonly MonsterFactory _monsterFactory;
    private readonly ItemFactory? _itemFactory;
    private readonly ConsumableFactory? _consumableFactory;

    public ScenarioHarness(
        MonsterFactory monsterFactory,
        ItemFactory? itemFactory = null,
        ConsumableFactory? consumableFactory = null)
    {
        _monsterFactory = monsterFactory;
        _itemFactory = itemFactory;
        _consumableFactory = consumableFactory;
    }

    public AggregatedMetrics Run(ScenarioDefinition scenario, int baseSeed = 1337)
    {
        var allRuns = new List<RunMetrics>();
        for (int i = 0; i < scenario.Runs; i++)
            allRuns.Add(RunOnce(scenario, baseSeed + i));
        return AggregatedMetrics.FromRuns(scenario.ScenarioId, baseSeed, allRuns);
    }

    public RunMetrics RunOnce(ScenarioDefinition scenario, int seed)
    {
        var rng = new SeededRandom(seed);
        var metrics = new RunMetrics();

        var map = GameMap.CreateArena(12, 12);

        var player = CreatePlayer(scenario, _itemFactory, _consumableFactory);
        player.X = 3;
        player.Y = 6;
        map.RegisterEntity(player);

        var monsters = new List<Entity>();
        int idx = 0;
        foreach (var monsterDef in scenario.Monsters)
        {
            for (int i = 0; i < monsterDef.Count; i++)
            {
                var monster = _monsterFactory.Create(monsterDef.Type, depth: scenario.Depth);
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

        var playerFighter = player.Require<Fighter>();
        var inventory = player.Get<Inventory>();

        for (int turn = 0; turn < scenario.TurnLimit; turn++)
        {
            if (!playerFighter.IsAlive || monsters.All(m => !m.Require<Fighter>().IsAlive))
                break;

            metrics.TurnsTaken++;

            // === PLAYER TURN (via BotBrain) ===
            var action = BotBrain.Decide(player, playerFighter, inventory, monsters, map);

            switch (action.Type)
            {
                case BotAction.ActionType.AttackTarget:
                    ResolvePlayerAttack(player, action.Target!, rng, metrics);
                    break;

                case BotAction.ActionType.HealSelf:
                    TryHeal(playerFighter, inventory, metrics);
                    player.Get<SpeedBonusTracker>()?.ResetMomentum();
                    break;

                case BotAction.ActionType.MoveToward:
                    map.MoveToward(player, action.Target!.X, action.Target.Y);
                    player.Get<SpeedBonusTracker>()?.ResetMomentum();
                    break;
            }

            // === MONSTER TURNS ===
            foreach (var monster in monsters)
            {
                var mf = monster.Require<Fighter>();
                if (!mf.IsAlive || !playerFighter.IsAlive)
                    continue;

                if (monster.ChebyshevDistanceTo(player.X, player.Y) <= 1)
                {
                    ResolveMonsterAttack(monster, player, rng, metrics);
                }
                else
                {
                    map.MoveToward(monster, player.X, player.Y);
                }
            }
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }

    /// <summary>
    /// Resolve a player attack, including bonus attack chain from momentum.
    /// </summary>
    private static void ResolvePlayerAttack(Entity player, Entity target, SeededRandom rng, RunMetrics metrics)
    {
        var result = CombatResolver.ResolveAttack(player, target, rng);
        metrics.PlayerAttacks++;
        if (result.Hit)
        {
            metrics.PlayerHits++;
            metrics.PlayerDamageDealt += result.Damage;
        }
        if (result.TargetKilled)
            metrics.MonstersKilled++;

        // Bonus attack chain — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && !result.TargetKilled && target.Require<Fighter>().IsAlive)
        {
            metrics.BonusAttacks++;
            ResolvePlayerAttack(player, target, rng, metrics);
        }
    }

    /// <summary>
    /// Resolve a monster attack, including bonus attack chain.
    /// </summary>
    private static void ResolveMonsterAttack(Entity monster, Entity player, SeededRandom rng, RunMetrics metrics)
    {
        var result = CombatResolver.ResolveAttack(monster, player, rng);
        metrics.MonsterAttacks++;
        if (result.Hit)
        {
            metrics.MonsterHits++;
            metrics.MonsterDamageDealt += result.Damage;
        }

        // Monster bonus attacks
        if (result.BonusAttackTriggered && player.Require<Fighter>().IsAlive)
        {
            metrics.BonusAttacks++;
            ResolveMonsterAttack(monster, player, rng, metrics);
        }
    }

    private static bool TryHeal(Fighter fighter, Inventory? inventory, RunMetrics metrics)
    {
        if (inventory == null) return false;

        var potion = inventory.FindFirst(item =>
            item.Get<Consumable>()?.IsHealing == true);

        if (potion == null) return false;

        fighter.Heal(potion.Require<Consumable>().HealAmount);
        inventory.Remove(potion);
        metrics.PotionsUsed++;
        return true;
    }

    private static Entity CreatePlayer(ScenarioDefinition scenario, ItemFactory? itemFactory, ConsumableFactory? consumableFactory)
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

        if (itemFactory != null && (def.Weapon != null || def.Armor != null))
        {
            var equipment = player.Add(new Equipment());
            if (def.Weapon != null)
            {
                var weapon = itemFactory.Create(def.Weapon);
                if (weapon != null) equipment.MainHand = weapon;
            }
            if (def.Armor != null)
            {
                var armor = itemFactory.Create(def.Armor);
                if (armor != null) equipment.Chest = armor;
            }
        }

        // Speed bonus for momentum system
        if (def.SpeedBonus > 0)
            player.Add(new SpeedBonusTracker(baseRatio: def.SpeedBonus));

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
}
