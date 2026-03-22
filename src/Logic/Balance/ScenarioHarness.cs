using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Runs scenario simulations and collects metrics. No Godot dependencies.
/// The harness creates a controlled encounter, runs a simple bot (attack nearest),
/// and records combat metrics for balance analysis.
/// </summary>
public sealed class ScenarioHarness
{
    private readonly MonsterFactory _monsterFactory;

    public ScenarioHarness(MonsterFactory monsterFactory)
    {
        _monsterFactory = monsterFactory;
    }

    /// <summary>
    /// Run a scenario multiple times with sequential seeds starting from baseSeed.
    /// Returns aggregated metrics across all runs.
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

        // Create player
        var player = CreatePlayer(scenario.Player);

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

        // Turn loop: simple bot AI — player attacks nearest alive monster,
        // then each alive monster attacks player. Repeat until done.
        var playerFighter = player.Require<Fighter>();

        for (int turn = 0; turn < scenario.TurnLimit; turn++)
        {
            if (!playerFighter.IsAlive || monsters.All(m => !m.Require<Fighter>().IsAlive))
                break;

            metrics.TurnsTaken++;

            // Player attacks nearest alive monster
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

    private static Entity CreatePlayer(ScenarioPlayer def)
    {
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
        return player;
    }
}
