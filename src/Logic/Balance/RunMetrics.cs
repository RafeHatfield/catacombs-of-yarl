using CatacombsOfYarl.Logic.Core;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Metrics collected from a single scenario run.
/// </summary>
public sealed class RunMetrics
{
    public int TurnsTaken { get; set; }
    public bool PlayerDied { get; set; }

    // Attack tracking
    public int PlayerAttacks { get; set; }
    public int PlayerHits { get; set; }
    public int PlayerDamageDealt { get; set; }
    public int MonsterAttacks { get; set; }
    public int MonsterHits { get; set; }
    public int MonsterDamageDealt { get; set; }

    // Kill tracking
    public int MonstersKilled { get; set; }

    // Healing
    public int PotionsUsed { get; set; }

    // Momentum
    public int BonusAttacks { get; set; }

    /// <summary>
    /// Record metrics from a single turn's events. Call once per turn.
    /// Derives all counters from the event stream — no parallel tracking needed.
    /// </summary>
    public void RecordTurn(TurnResult result, int playerId)
    {
        TurnsTaken++;
        foreach (var evt in result.Events)
        {
            switch (evt)
            {
                case AttackEvent atk when atk.ActorId == playerId:
                    PlayerAttacks++;
                    if (atk.Hit)
                    {
                        PlayerHits++;
                        PlayerDamageDealt += atk.Damage;
                    }
                    if (atk.IsBonusAttack) BonusAttacks++;
                    if (atk.TargetKilled) MonstersKilled++;
                    break;

                case AttackEvent atk:
                    MonsterAttacks++;
                    if (atk.Hit)
                    {
                        MonsterHits++;
                        MonsterDamageDealt += atk.Damage;
                    }
                    if (atk.IsBonusAttack) BonusAttacks++;
                    break;

                case HealEvent:
                    PotionsUsed++;
                    break;
            }
        }
    }
}

/// <summary>
/// Aggregated metrics across multiple runs of the same scenario.
/// </summary>
public sealed class AggregatedMetrics
{
    public string ScenarioId { get; init; } = "";
    public int TotalRuns { get; init; }
    public int Seed { get; init; }

    // Averages
    public double AvgTurns { get; init; }
    public double DeathRate { get; init; }
    public double PlayerHitRate { get; init; }
    public double MonsterHitRate { get; init; }

    // Pressure model invariants
    public double AvgPlayerDamageDealt { get; init; }
    public double AvgMonsterDamageDealt { get; init; }
    public double AvgMonstersKilled { get; init; }

    /// <summary>
    /// Aggregate a list of run metrics into summary statistics.
    /// </summary>
    public static AggregatedMetrics FromRuns(string scenarioId, int seed, List<RunMetrics> runs)
    {
        if (runs.Count == 0)
            return new AggregatedMetrics { ScenarioId = scenarioId, Seed = seed };

        int totalPlayerAttacks = runs.Sum(r => r.PlayerAttacks);
        int totalPlayerHits = runs.Sum(r => r.PlayerHits);
        int totalMonsterAttacks = runs.Sum(r => r.MonsterAttacks);
        int totalMonsterHits = runs.Sum(r => r.MonsterHits);

        return new AggregatedMetrics
        {
            ScenarioId = scenarioId,
            Seed = seed,
            TotalRuns = runs.Count,
            AvgTurns = runs.Average(r => r.TurnsTaken),
            DeathRate = (double)runs.Count(r => r.PlayerDied) / runs.Count,
            PlayerHitRate = totalPlayerAttacks > 0 ? (double)totalPlayerHits / totalPlayerAttacks : 0,
            MonsterHitRate = totalMonsterAttacks > 0 ? (double)totalMonsterHits / totalMonsterAttacks : 0,
            AvgPlayerDamageDealt = runs.Average(r => r.PlayerDamageDealt),
            AvgMonsterDamageDealt = runs.Average(r => r.MonsterDamageDealt),
            AvgMonstersKilled = runs.Average(r => r.MonstersKilled),
        };
    }
}
