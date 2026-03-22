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
/// Runs scenario simulations with tile-based positioning.
/// Bot AI: move toward nearest enemy, attack if adjacent, heal if low HP.
/// Monsters: move toward player, attack if adjacent.
/// Melee range = Chebyshev distance 1 (adjacent, including diagonal).
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

        // Create arena (12x12 enclosed)
        var map = GameMap.CreateArena(12, 12);

        // Create player at left side of arena
        var player = CreatePlayer(scenario, _itemFactory, _consumableFactory);
        player.X = 3;
        player.Y = 6;
        map.RegisterEntity(player);

        // Create monsters spread on right side
        var monsters = new List<Entity>();
        int monsterIndex = 0;
        foreach (var monsterDef in scenario.Monsters)
        {
            for (int i = 0; i < monsterDef.Count; i++)
            {
                var monster = _monsterFactory.Create(monsterDef.Type, depth: scenario.Depth);
                if (monster != null)
                {
                    // Spread monsters on right side of arena
                    monster.X = 8 + (monsterIndex % 3);
                    monster.Y = 4 + (monsterIndex / 3) * 2;
                    map.RegisterEntity(monster);
                    monsters.Add(monster);
                    monsterIndex++;
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

            // === PLAYER TURN ===
            // Priority: panic heal > attack adjacent > threshold heal > move toward enemy
            var nearestAlive = FindNearest(player, monsters);
            bool isAdjacent = nearestAlive != null && player.ChebyshevDistanceTo(nearestAlive.X, nearestAlive.Y) <= 1;

            // Panic heal: very low HP with enemies alive
            double hpFraction = (double)playerFighter.Hp / playerFighter.MaxHp;
            bool panicHealed = false;
            if (hpFraction <= BotConfig.PanicThreshold)
                panicHealed = TryHeal(playerFighter, inventory, metrics);

            if (!panicHealed)
            {
                if (isAdjacent && nearestAlive != null)
                {
                    // Attack adjacent enemy
                    var result = CombatResolver.ResolveAttack(player, nearestAlive, rng);
                    metrics.PlayerAttacks++;
                    if (result.Hit)
                    {
                        metrics.PlayerHits++;
                        metrics.PlayerDamageDealt += result.Damage;
                    }
                    if (result.TargetKilled)
                        metrics.MonstersKilled++;
                }
                else
                {
                    // Not adjacent — heal if below threshold, otherwise move
                    bool thresholdHealed = false;
                    if (hpFraction <= BotConfig.HealThreshold)
                        thresholdHealed = TryHeal(playerFighter, inventory, metrics);

                    if (!thresholdHealed && nearestAlive != null)
                    {
                        // Move toward nearest enemy
                        map.MoveToward(player, nearestAlive.X, nearestAlive.Y);
                    }
                }
            }

            // === MONSTER TURNS ===
            foreach (var monster in monsters)
            {
                var mf = monster.Require<Fighter>();
                if (!mf.IsAlive || !playerFighter.IsAlive)
                    continue;

                bool monsterAdjacent = monster.ChebyshevDistanceTo(player.X, player.Y) <= 1;

                if (monsterAdjacent)
                {
                    var result = CombatResolver.ResolveAttack(monster, player, rng);
                    metrics.MonsterAttacks++;
                    if (result.Hit)
                    {
                        metrics.MonsterHits++;
                        metrics.MonsterDamageDealt += result.Damage;
                    }
                }
                else
                {
                    // Move toward player
                    map.MoveToward(monster, player.X, player.Y);
                }
            }
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }

    private static Entity? FindNearest(Entity from, List<Entity> candidates)
    {
        Entity? nearest = null;
        double bestDist = double.MaxValue;
        foreach (var c in candidates)
        {
            if (!c.Require<Fighter>().IsAlive) continue;
            double d = from.DistanceTo(c.X, c.Y);
            if (d < bestDist)
            {
                bestDist = d;
                nearest = c;
            }
        }
        return nearest;
    }

    private static bool TryHeal(Fighter fighter, Inventory? inventory, RunMetrics metrics)
    {
        if (inventory == null) return false;

        var potion = inventory.FindFirst(item =>
        {
            var c = item.Get<Consumable>();
            return c != null && c.IsHealing;
        });

        if (potion == null) return false;

        var consumable = potion.Require<Consumable>();
        fighter.Heal(consumable.HealAmount);
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
