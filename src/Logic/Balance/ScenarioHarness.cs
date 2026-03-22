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
    /// <summary>Heal when HP drops to this fraction of max HP (30%).</summary>
    public const double HealThreshold = 0.30;

    /// <summary>Panic heal at this fraction when enemies are present (15%).</summary>
    public const double PanicThreshold = 0.15;
}

/// <summary>
/// Runs scenario simulations and collects metrics. No Godot dependencies.
/// Bot AI: heal if below threshold, then attack nearest alive monster.
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

    /// <summary>
    /// Run a scenario multiple times with sequential seeds starting from baseSeed.
    /// </summary>
    public AggregatedMetrics Run(ScenarioDefinition scenario, int baseSeed = 1337)
    {
        var allRuns = new List<RunMetrics>();

        for (int i = 0; i < scenario.Runs; i++)
        {
            int seed = baseSeed + i;
            var metrics = RunOnce(scenario, seed);
            allRuns.Add(metrics);
        }

        return AggregatedMetrics.FromRuns(scenario.ScenarioId, baseSeed, allRuns);
    }

    /// <summary>
    /// Run a single scenario iteration. Returns metrics for that run.
    /// </summary>
    public RunMetrics RunOnce(ScenarioDefinition scenario, int seed)
    {
        var rng = new SeededRandom(seed);
        var metrics = new RunMetrics();

        // Create player with equipment and inventory
        var player = CreatePlayer(scenario, _itemFactory, _consumableFactory);

        // Create monsters
        var monsters = new List<Entity>();
        foreach (var monsterDef in scenario.Monsters)
        {
            for (int i = 0; i < monsterDef.Count; i++)
            {
                var monster = _monsterFactory.Create(monsterDef.Type);
                if (monster != null)
                    monsters.Add(monster);
            }
        }

        var playerFighter = player.Require<Fighter>();
        var inventory = player.Get<Inventory>();

        for (int turn = 0; turn < scenario.TurnLimit; turn++)
        {
            if (!playerFighter.IsAlive || monsters.All(m => !m.Require<Fighter>().IsAlive))
                break;

            metrics.TurnsTaken++;

            // Bot decision: heal or attack
            bool healed = TryBotHeal(player, playerFighter, inventory, metrics);

            if (!healed)
            {
                // Attack nearest alive monster
                var target = monsters.FirstOrDefault(m => m.Require<Fighter>().IsAlive);
                if (target != null)
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
                }
            }

            // Each alive monster attacks player
            foreach (var monster in monsters)
            {
                var mf = monster.Require<Fighter>();
                if (!mf.IsAlive || !playerFighter.IsAlive)
                    continue;

                var result = CombatResolver.ResolveAttack(monster, player, rng);
                metrics.MonsterAttacks++;
                if (result.Hit)
                {
                    metrics.MonsterHits++;
                    metrics.MonsterDamageDealt += result.Damage;
                }
            }
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }

    /// <summary>
    /// Bot heal logic: use a healing potion if HP is below threshold.
    /// Costs the player's action for this turn (no attack if healing).
    /// Returns true if a potion was used.
    /// </summary>
    private static bool TryBotHeal(Entity player, Fighter fighter, Inventory? inventory, RunMetrics metrics)
    {
        if (inventory == null) return false;

        double hpFraction = (double)fighter.Hp / fighter.MaxHp;
        if (hpFraction > BotConfig.HealThreshold) return false;

        // Find a healing potion
        var potion = inventory.FindFirst(item =>
        {
            var c = item.Get<Consumable>();
            return c != null && c.IsHealing;
        });

        if (potion == null) return false;

        // Use the potion
        var consumable = potion.Require<Consumable>();
        int healed = fighter.Heal(consumable.HealAmount);
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

        // Equip weapon and armor
        if (itemFactory != null && (def.Weapon != null || def.Armor != null))
        {
            var equipment = player.Add(new Equipment());

            if (def.Weapon != null)
            {
                var weapon = itemFactory.Create(def.Weapon);
                if (weapon != null)
                    equipment.MainHand = weapon;
            }

            if (def.Armor != null)
            {
                var armor = itemFactory.Create(def.Armor);
                if (armor != null)
                    equipment.Chest = armor;
            }
        }

        // Add inventory with scenario items
        if (consumableFactory != null && scenario.Items.Count > 0)
        {
            var inventory = player.Add(new Inventory());
            foreach (var itemDef in scenario.Items)
            {
                for (int i = 0; i < itemDef.Count; i++)
                {
                    var item = consumableFactory.Create(itemDef.Type);
                    if (item != null)
                        inventory.Add(item);
                }
            }
        }

        return player;
    }
}
