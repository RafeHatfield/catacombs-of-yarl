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
/// Result of evaluating pressure metrics against target bands.
/// </summary>
public sealed class PressureEvaluation
{
    public string ScenarioId { get; init; } = "";
    public int Depth { get; init; }
    public PressureMetrics Metrics { get; init; } = null!;

    public string H_PM_Status { get; init; } = "";
    public string H_MP_Status { get; init; } = "";
    public string DeathRate_Status { get; init; } = "";

    public TargetBand H_PM_Target { get; init; }
    public TargetBand H_MP_Target { get; init; }
    public TargetBand DeathRate_Target { get; init; }

    /// <summary>True if all three metrics are within target bands.</summary>
    public bool AllInBand => H_PM_Status == "OK" && H_MP_Status == "OK" && DeathRate_Status == "OK";
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

    // Death rate targets by depth band — from Python prototype target_bands.py
    private static readonly TargetBand[] DeathRate_Targets =
    [
        new(0.00, 0.05),  // depth 1-2: safe learning
        new(0.05, 0.15),  // depth 3-4: pressure begins
        new(0.25, 0.40),  // depth 5-6: dangerous
        new(0.35, 0.55),  // depth 7-8: brutal
        new(0.35, 0.55),  // depth 9+: brutal
    ];

    // Provisional C# bands — based on tuned scenario measurements with current combat system.
    // Wider than prototype bands. Converge toward prototype as mechanics are added.
    // Measured from tuned scenarios at seed 1337, ±20% for variance.
    private static readonly TargetBand[] Provisional_H_PM =
    [
        new(6.0, 16.0),   // depth 1-2: wide — dagger=12.9 at d1, shortsword+speed=7.8 at d2
        new(6.0, 10.0),   // depth 3-4: longsword+speed (measured 7.7, 7.1)
        new(5.5, 9.0),    // depth 5-6: fine/MW longsword+speed (measured 7.1, 6.5)
        new(5.5, 9.0),    // depth 7-8: extrapolated
        new(5.5, 9.0),    // depth 9+: extrapolated
    ];

    private static readonly TargetBand[] Provisional_H_MP =
    [
        new(22.0, 35.0),  // depth 1-2: (measured 27.5, 28.5)
        new(13.0, 22.0),  // depth 3-4: (measured 16.5, 16.4)
        new(15.0, 35.0),  // depth 5-6: wide — varies by composition (measured 30.7, 19.6)
        new(15.0, 35.0),  // depth 7-8: extrapolated
        new(15.0, 35.0),  // depth 9+: extrapolated
    ];

    private static readonly TargetBand[] Provisional_DeathRate =
    [
        new(0.00, 0.10),  // depth 1-2: (measured 4%, 0%)
        new(0.15, 0.50),  // depth 3-4: (measured 36%, 36%)
        new(0.00, 0.15),  // depth 5-6: (measured 0%, 6%) — speed+weapon dominates
        new(0.10, 0.50),  // depth 7-8: extrapolated
        new(0.20, 0.60),  // depth 9+: extrapolated
    ];

    /// <summary>Get prototype H_PM target band for a depth.</summary>
    public static TargetBand GetH_PM_Target(int depth) =>
        H_PM_Targets[Math.Clamp(DepthScaling.GetBand(depth), 0, H_PM_Targets.Length - 1)];

    /// <summary>Get prototype H_MP target band for a depth.</summary>
    public static TargetBand GetH_MP_Target(int depth) =>
        H_MP_Targets[Math.Clamp(DepthScaling.GetBand(depth), 0, H_MP_Targets.Length - 1)];

    /// <summary>Get provisional C# H_PM target band for a depth.</summary>
    public static TargetBand GetProvisionalH_PM(int depth) =>
        Provisional_H_PM[Math.Clamp(DepthScaling.GetBand(depth), 0, Provisional_H_PM.Length - 1)];

    /// <summary>Get provisional C# H_MP target band for a depth.</summary>
    public static TargetBand GetProvisionalH_MP(int depth) =>
        Provisional_H_MP[Math.Clamp(DepthScaling.GetBand(depth), 0, Provisional_H_MP.Length - 1)];

    /// <summary>Get provisional C# death rate target band for a depth.</summary>
    public static TargetBand GetProvisionalDeathRate(int depth) =>
        Provisional_DeathRate[Math.Clamp(DepthScaling.GetBand(depth), 0, Provisional_DeathRate.Length - 1)];

    /// <summary>Evaluate against provisional C# bands (current combat system).</summary>
    public static PressureEvaluation EvaluateProvisional(PressureMetrics pm)
    {
        var hpmBand = GetProvisionalH_PM(pm.Depth);
        var hmpBand = GetProvisionalH_MP(pm.Depth);
        var deathBand = GetProvisionalDeathRate(pm.Depth);

        return new PressureEvaluation
        {
            ScenarioId = pm.ScenarioId,
            Depth = pm.Depth,
            Metrics = pm,
            H_PM_Status = hpmBand.Status(pm.H_PM),
            H_MP_Status = hmpBand.Status(pm.H_MP),
            DeathRate_Status = deathBand.Status(pm.DeathRate),
            H_PM_Target = hpmBand,
            H_MP_Target = hmpBand,
            DeathRate_Target = deathBand,
        };
    }

    /// <summary>Get death rate target band for a depth.</summary>
    public static TargetBand GetDeathRateTarget(int depth) =>
        DeathRate_Targets[Math.Clamp(DepthScaling.GetBand(depth), 0, DeathRate_Targets.Length - 1)];

    /// <summary>
    /// Evaluate pressure metrics against target bands. Returns a structured evaluation.
    /// </summary>
    public static PressureEvaluation Evaluate(PressureMetrics pm)
    {
        var hpmBand = GetH_PM_Target(pm.Depth);
        var hmpBand = GetH_MP_Target(pm.Depth);
        var deathBand = GetDeathRateTarget(pm.Depth);

        return new PressureEvaluation
        {
            ScenarioId = pm.ScenarioId,
            Depth = pm.Depth,
            Metrics = pm,
            H_PM_Status = hpmBand.Status(pm.H_PM),
            H_MP_Status = hmpBand.Status(pm.H_MP),
            DeathRate_Status = deathBand.Status(pm.DeathRate),
            H_PM_Target = hpmBand,
            H_MP_Target = hmpBand,
            DeathRate_Target = deathBand,
        };
    }

    /// <summary>
    /// Generate actionable diagnosis text from an evaluation.
    /// </summary>
    public static List<string> Diagnose(PressureEvaluation eval)
    {
        var findings = new List<string>();
        var pm = eval.Metrics;

        if (eval.H_PM_Status == "HIGH")
            findings.Add($"H_PM {pm.H_PM:F1} above target {eval.H_PM_Target.Max} — player kills too slowly. Needs higher DPR_P (currently {pm.DPR_P:F2}). Levers: better weapon, affixes, momentum.");
        else if (eval.H_PM_Status == "LOW")
            findings.Add($"H_PM {pm.H_PM:F1} below target {eval.H_PM_Target.Min} — monsters die too fast. Player DPR_P ({pm.DPR_P:F2}) may be too high, or monster HP too low.");

        if (eval.H_MP_Status == "HIGH")
            findings.Add($"H_MP {pm.H_MP:F1} above target {eval.H_MP_Target.Max} — monsters not threatening enough. Monster DPR_M ({pm.DPR_M:F2}) too low. Levers: monster damage/accuracy scaling, encounter composition.");
        else if (eval.H_MP_Status == "LOW")
            findings.Add($"H_MP {pm.H_MP:F1} below target {eval.H_MP_Target.Min} — monsters too lethal. Reduce monster damage/accuracy at this depth.");

        if (eval.DeathRate_Status == "HIGH")
            findings.Add($"Death rate {pm.DeathRate:P0} above target {eval.DeathRate_Target.Max:P0}. If H_PM/H_MP are in band, this is a composition problem (too many simultaneous enemies), not a scaling problem.");
        else if (eval.DeathRate_Status == "LOW")
            findings.Add($"Death rate {pm.DeathRate:P0} below target {eval.DeathRate_Target.Min:P0}. Encounter may be too easy — consider more enemies or fewer potions.");

        if (pm.PressureRatio > 0.6)
            findings.Add($"Pressure ratio {pm.PressureRatio:F2} indicates attrition — fights are long grinds. Consider increasing monster damage to make fights shorter and deadlier.");
        else if (pm.PressureRatio < 0.3)
            findings.Add($"Pressure ratio {pm.PressureRatio:F2} indicates spike lethality — monsters kill fast but die fast. May need more monster HP.");

        if (findings.Count == 0)
            findings.Add("All metrics within target bands.");

        return findings;
    }

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
