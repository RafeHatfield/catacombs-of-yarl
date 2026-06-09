namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Target bands for pressure invariants by depth band.
/// From docs/DEPTH_PRESSURE_MODEL.md.
/// </summary>
public readonly record struct TargetBand(double Min, double Max)
{
    public bool Contains(double value) => value >= Min && value <= Max;
    public bool Below(double value) => value < Min;   // observed under the band
    public bool Above(double value) => value > Max;   // observed over the band
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
    // From Python prototype balance/target_bands.py — union of per-depth ranges within each band.
    // Depth 1: [6-8], depth 2: [7-9]   → band 0: [6-9]
    // Depth 3: [8-10], depth 4: [9-11] → band 1: [8-11]
    // Depth 5: [9-12], depth 6: [10-13]→ band 2: [9-13]
    private static readonly TargetBand[] H_PM_Targets =
    [
        new(6.0, 9.0),    // depth 1-2
        new(8.0, 11.0),   // depth 3-4
        new(9.0, 13.0),   // depth 5-6
        new(10.0, 14.0),  // depth 7-8 (extrapolated)
        new(11.0, 15.0),  // depth 9+  (extrapolated)
    ];

    // Depth 1: [20-24], depth 2: [20-24] → band 0: [20-24]
    // Depth 3: [20-23], depth 4: [18-22] → band 1: [18-23]
    // Depth 5: [17-21], depth 6: [16-20] → band 2: [16-21]
    private static readonly TargetBand[] H_MP_Targets =
    [
        new(20.0, 24.0),  // depth 1-2
        new(18.0, 23.0),  // depth 3-4
        new(16.0, 21.0),  // depth 5-6
        new(14.0, 20.0),  // depth 7-8 (extrapolated)
        new(12.0, 18.0),  // depth 9+  (extrapolated)
    ];

    // Death rate targets by depth band — from Python prototype target_bands.py
    // Depth 1: [0-5%], depth 2: [0-8%]   → band 0: [0-8%]
    // Depth 3: [5-15%], depth 4: [15-30%]→ band 1: [5-30%]
    // Depth 5: [25-40%], depth 6: [35-55%]→band 2: [25-55%]
    private static readonly TargetBand[] DeathRate_Targets =
    [
        new(0.00, 0.08),  // depth 1-2: safe learning
        new(0.05, 0.30),  // depth 3-4: pressure begins → serious
        new(0.25, 0.55),  // depth 5-6: dangerous → brutal
        new(0.35, 0.65),  // depth 7-8: brutal (extrapolated)
        new(0.40, 0.70),  // depth 9+: brutal (extrapolated)
    ];

    // Provisional C# bands — empirically calibrated from harness runs on well-tuned scenarios.
    //
    // C# H_PM is LOWER than PoC theory because player DPR is slightly higher per turn
    // (bot always attacks, no turn waste from item-seeking diversion).
    //
    // C# H_MP is HIGHER than PoC theory because PoC monsters have a two-phase hit system
    // (flat pre-check 75% × d20 hit = ~18-19% effective), whereas C# uses pure d20 (~35%).
    // Despite C# monsters hitting more often, DPR_M is diluted by travel/approach turns,
    // so H_MP remains high. Zombie scenarios inflate H_MP further (travel between spread
    // monsters dominates turn count, reducing DPR_M toward zero).
    //
    // Empirical baseline from well-calibrated scenarios (post Phase-0 SHA-256 reseed at seed=1337):
    //   depth1_tuned (0% death):    H_PM=9.1,  H_MP=34.1
    //   depth2_baseline (0%):       H_PM=8.2,  H_MP=37.2
    //   depth3_orc_brutal (18%):    H_PM=8.1,  H_MP=32.7
    //   depth4_tuned (8%):          H_PM=7.3,  H_MP=43.9
    //   depth6_tuned (38%):         H_PM=6.3,  H_MP=38.4
    private static readonly TargetBand[] Provisional_H_PM =
    [
        new(5.0, 10.0),   // depth 1-2: observed 7.7-7.8 baseline; 5.5-5.8 for fine/masterwork probes
        new(6.0, 12.0),   // depth 3-4: observed 6.9-9.5; wider band covers gear variance
        new(6.0, 22.0),   // depth 5-6: wide — orc ~6-9, zombie ~15-20 (HP+resistance)
        new(7.0, 24.0),   // depth 7-8: extrapolated
        new(8.0, 26.0),   // depth 9+: extrapolated
    ];

    private static readonly TargetBand[] Provisional_H_MP =
    [
        new(32.0, 55.0),  // depth 1-2: observed 37-49 across all orc scenarios
        new(28.0, 52.0),  // depth 3-4: observed 35-43 (orc); zombie scenarios will inflate
        new(22.0, 85.0),  // depth 5-6: orc 30-44; zombie spread scenarios inflate to 50-80 (travel time dilution)
        new(20.0, 48.0),  // depth 7-8: extrapolated
        new(16.0, 45.0),  // depth 9+: extrapolated
    ];

    private static readonly TargetBand[] Provisional_DeathRate =
    [
        new(0.00, 0.08),  // depth 1-2: PoC [0-5%/0-8%]; d1 observed 2%
        new(0.05, 0.30),  // depth 3-4: PoC [5-15%/15-30%]
        new(0.25, 0.60),  // depth 5-6: PoC [25-40%/35-55%]; C# sequential eng. → max bumped to 60%
        new(0.35, 0.65),  // depth 7-8: extrapolated
        new(0.40, 0.70),  // depth 9+: extrapolated
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
