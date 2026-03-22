namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Target bands for pressure invariants by depth band.
/// From docs/DEPTH_PRESSURE_MODEL.md.
/// </summary>
public readonly record struct TargetBand(double Min, double Max)
{
    public bool Contains(double value) => value >= Min && value <= Max;
    public string Status(double value) => Contains(value) ? "OK" : value < Min ? "LOW" : "HIGH";
}

/// <summary>
/// Derived pressure metrics from a scenario run.
/// These are the core invariants that define whether combat feels right.
/// </summary>
public sealed class PressureMetrics
{
    public string ScenarioId { get; init; } = "";
    public int Depth { get; init; }

    /// <summary>Player damage per round.</summary>
    public double DPR_P { get; init; }

    /// <summary>Monster damage per round.</summary>
    public double DPR_M { get; init; }

    /// <summary>Player hits to kill one monster. Higher = monsters are tankier.</summary>
    public double H_PM { get; init; }

    /// <summary>Monster hits to kill the player. Lower = more dangerous.</summary>
    public double H_MP { get; init; }

    /// <summary>Average damage taken per monster killed.</summary>
    public double DmgPerEncounter { get; init; }

    /// <summary>Ratio H_PM / H_MP. Attrition > 0.6, balanced 0.3-0.6, spike < 0.3.</summary>
    public double PressureRatio => H_MP > 0 ? H_PM / H_MP : 0;

    public double DeathRate { get; init; }
}

/// <summary>
/// Computes pressure model invariants from aggregated harness metrics.
/// Pure math — no state, no IO.
///
/// H_PM = avg monster HP / DPR_P  (how many rounds to kill one monster)
/// H_MP = player max HP / DPR_M   (how many rounds for monsters to kill player)
/// DPR_P = avg player damage per turn spent attacking
/// DPR_M = avg monster damage per turn
/// </summary>
public static class PressureModel
{
    // Target bands by depth band index (0 = depth 1-2, 1 = depth 3-4, etc.)
    // From docs/DEPTH_PRESSURE_MODEL.md — these are the equilibrium targets.
    private static readonly TargetBand[] H_PM_Targets =
    [
        new(3.5, 4.5),  // depth 1-2
        new(4.0, 5.0),  // depth 3-4
        new(4.5, 5.5),  // depth 5-6
        new(5.0, 6.0),  // depth 7-8
        new(6.0, 7.0),  // depth 9+
    ];

    private static readonly TargetBand[] H_MP_Targets =
    [
        new(10, 14),  // depth 1-2
        new(9, 12),   // depth 3-4
        new(8, 10),   // depth 5-6
        new(7, 9),    // depth 7-8
        new(6, 8),    // depth 9+
    ];

    /// <summary>Get H_PM target band for a depth.</summary>
    public static TargetBand GetH_PM_Target(int depth) =>
        H_PM_Targets[Math.Clamp(DepthScaling.GetBand(depth), 0, H_PM_Targets.Length - 1)];

    /// <summary>Get H_MP target band for a depth.</summary>
    public static TargetBand GetH_MP_Target(int depth) =>
        H_MP_Targets[Math.Clamp(DepthScaling.GetBand(depth), 0, H_MP_Targets.Length - 1)];

    /// <summary>
    /// Derive pressure metrics from aggregated scenario data.
    /// Requires knowing the average monster HP at the scenario depth
    /// and the player's max HP.
    /// </summary>
    public static PressureMetrics Compute(
        AggregatedMetrics agg,
        int depth,
        double avgMonsterHp,
        int playerMaxHp)
    {
        // DPR_P = total player damage / total turns (across all runs)
        // We use per-run averages: avg damage per run / avg turns per run
        double dprP = agg.AvgTurns > 0 ? agg.AvgPlayerDamageDealt / agg.AvgTurns : 0;
        double dprM = agg.AvgTurns > 0 ? agg.AvgMonsterDamageDealt / agg.AvgTurns : 0;

        // H_PM = monster HP / player DPR (rounds to kill one monster)
        double hPM = dprP > 0 ? avgMonsterHp / dprP : 0;

        // H_MP = player HP / monster DPR (rounds for monsters to kill player)
        double hMP = dprM > 0 ? playerMaxHp / dprM : 0;

        // Damage per encounter = avg monster damage / avg kills
        double dmgPerEnc = agg.AvgMonstersKilled > 0
            ? agg.AvgMonsterDamageDealt / agg.AvgMonstersKilled
            : 0;

        return new PressureMetrics
        {
            ScenarioId = agg.ScenarioId,
            Depth = depth,
            DPR_P = dprP,
            DPR_M = dprM,
            H_PM = hPM,
            H_MP = hMP,
            DmgPerEncounter = dmgPerEnc,
            DeathRate = agg.DeathRate,
        };
    }
}
