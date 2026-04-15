using System.Text;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Generates a multi-section human-readable text report from a DungeonSoakSummary.
///
/// Port of PoC's bot_survivability_report.py and eco_balance_report.py, unified into
/// a single dungeon-focused report. Suitable for CI output or developer review.
///
/// The report is a pure string — no file I/O. The caller writes it where needed.
/// All sections degrade gracefully: 0 deaths, 0 kills, all survived, no telemetry.
/// </summary>
public static class DungeonSoakReport
{
    private const int BarMaxWidth = 40;

    /// <summary>
    /// Generate a full soak report from the given summary.
    ///
    /// The summary must have been produced by DungeonSoakSummary.ComputeFrom().
    /// Sections are skipped or noted when data is unavailable (e.g. no telemetry),
    /// but the method never throws on valid (even empty) summaries.
    /// </summary>
    public static string Generate(DungeonSoakSummary summary)
    {
        var sb = new StringBuilder();

        AppendOverview(sb, summary);
        AppendSurvivalCurve(sb, summary);
        AppendDeathClassification(sb, summary);
        AppendFloorEfficiency(sb, summary);
        AppendBotEfficiency(sb, summary);
        AppendAnomalies(sb, summary);

        return sb.ToString();
    }

    // ── Section 1: Overview ─────────────────────────────────────────────────

    private static void AppendOverview(StringBuilder sb, DungeonSoakSummary summary)
    {
        sb.AppendLine("=== YARL Dungeon Soak Report ===");

        // Use ConfiguredFloors when known (live soak); fall back to max depth reached (JSONL reader).
        int floorCount = summary.ConfiguredFloors > 0
            ? summary.ConfiguredFloors
            : summary.SurvivalCurve.Count;
        // Base seed: the lowest seed seen across runs, or 0 if no runs.
        int baseSeed = summary.Runs.Count > 0
            ? summary.Runs.Min(r => r.Seed)
            : 0;

        sb.AppendLine($"Runs: {summary.RunsAttempted} | Floors: {floorCount} | Base Seed: {baseSeed}");
        sb.AppendLine($"Survival Rate: {summary.SurvivalRate * 100:F1}%");
        sb.AppendLine($"Avg Floors Completed: {summary.AvgFloorsCompleted:F1} / {floorCount}");
        sb.AppendLine($"Avg Total Turns: {summary.AvgTotalTurns:F1}");
        sb.AppendLine();
    }

    // ── Section 2: Survival Curve ───────────────────────────────────────────

    private static void AppendSurvivalCurve(StringBuilder sb, DungeonSoakSummary summary)
    {
        sb.AppendLine("Survival Curve:");

        if (summary.SurvivalCurve.Count == 0)
        {
            sb.AppendLine("  (no floor data)");
            sb.AppendLine();
            return;
        }

        for (int i = 0; i < summary.SurvivalCurve.Count; i++)
        {
            double fraction = summary.SurvivalCurve[i];
            int barWidth    = (int)(fraction * BarMaxWidth);
            string bar      = new string('#', barWidth);
            sb.AppendLine($"  Floor {i + 1,2}: {fraction * 100,6:F1}%  {bar}");
        }

        sb.AppendLine();
    }

    // ── Section 3: Death Classification ────────────────────────────────────

    private static void AppendDeathClassification(StringBuilder sb, DungeonSoakSummary summary)
    {
        int totalDeaths = summary.FailureTypeCounts.TryGetValue(OutcomeClassifier.FailureDeath, out int d) ? d : 0;
        // "Deaths" for the header = all non-survived, non-exception outcomes
        int totalFailures = summary.RunsAttempted - summary.RunsSurvived;

        sb.AppendLine($"Death Classification ({totalFailures} deaths):");

        if (totalFailures == 0)
        {
            sb.AppendLine("  No deaths recorded.");
            sb.AppendLine();
            return;
        }

        // Failure type table
        sb.AppendLine($"  {"Failure Type",-20}  {"Count",5}    {"%" ,6}");
        sb.AppendLine($"  {"--------------------",-20}  {"-----",5}    {"------",6}");

        foreach (var (type, count) in summary.FailureTypeCounts
            .Where(kvp => kvp.Key != OutcomeClassifier.FailureNone)
            .OrderByDescending(kvp => kvp.Value))
        {
            double pct = totalFailures > 0 ? (double)count / totalFailures * 100.0 : 0.0;
            sb.AppendLine($"  {type,-20}  {count,5}    {pct,5:F1}%");
        }

        sb.AppendLine();

        // Top killers (combat deaths only)
        if (summary.KillerCounts.Count > 0)
        {
            sb.AppendLine($"  Top Killers (combat deaths):");
            var sorted = summary.KillerCounts.OrderByDescending(kvp => kvp.Value).ToList();
            int topN   = Math.Min(5, sorted.Count);
            int topSum = sorted.Take(topN).Sum(kvp => kvp.Value);

            for (int i = 0; i < topN; i++)
            {
                var (killer, count) = sorted[i];
                double pct = totalDeaths > 0 ? (double)count / totalDeaths * 100.0 : 0.0;
                sb.AppendLine($"  {killer,-22}  {count,4}   {pct,5:F1}%");
            }

            if (sorted.Count > topN)
            {
                int others    = sorted.Skip(topN).Sum(kvp => kvp.Value);
                double otherPct = totalDeaths > 0 ? (double)others / totalDeaths * 100.0 : 0.0;
                sb.AppendLine($"  {"(others)",-22}  {others,4}   {otherPct,5:F1}%");
            }

            sb.AppendLine();
        }
    }

    // ── Section 4: Floor Efficiency ─────────────────────────────────────────

    private static void AppendFloorEfficiency(StringBuilder sb, DungeonSoakSummary summary)
    {
        sb.AppendLine("Floor Efficiency:");

        if (summary.Runs.Count == 0)
        {
            sb.AppendLine("  (no run data)");
            sb.AppendLine();
            return;
        }

        // Aggregate per-floor stats from the run list.
        // Each run's PerFloor is keyed by Depth (1-based).
        // We collect all depths that were actually attempted.
        var byDepth = new SortedDictionary<int, List<FloorRunMetrics>>();

        foreach (var run in summary.Runs)
        {
            foreach (var floor in run.PerFloor)
            {
                if (!byDepth.TryGetValue(floor.Depth, out var list))
                {
                    list = new List<FloorRunMetrics>();
                    byDepth[floor.Depth] = list;
                }
                list.Add(floor);
            }
        }

        if (byDepth.Count == 0)
        {
            sb.AppendLine("  (no floor data)");
            sb.AppendLine();
            return;
        }

        sb.AppendLine($"  {"Depth",5}   {"Avg Turns",9}   {"Avg Kills",9}   {"Avg HP End",10}   {"Death%",6}");
        sb.AppendLine($"  {"-----",5}   {"---------",9}   {"---------",9}   {"----------",10}   {"------",6}");

        foreach (var (depth, floors) in byDepth)
        {
            double avgTurns  = floors.Average(f => f.TurnsTaken);
            double avgKills  = floors.Average(f => f.MonstersKilled);
            double deathPct  = floors.Count > 0
                ? (double)floors.Count(f => f.PlayerDied) / floors.Count * 100.0
                : 0.0;

            // Avg HP displayed as "current/max" using the average of both fields.
            // Players with MaxHp=0 (exception runs) are excluded from the average.
            var hpFloors = floors.Where(f => f.PlayerMaxHp > 0).ToList();
            string hpStr;
            if (hpFloors.Count > 0)
            {
                // Clamp to 0: fatal hits leave Hp negative; we want "0" not "-5" in the report.
                int avgHp    = (int)Math.Round(hpFloors.Average(f => Math.Max(0, f.PlayerHpAtEnd)));
                int avgMaxHp = (int)Math.Round(hpFloors.Average(f => f.PlayerMaxHp));
                hpStr = $"{avgHp}/{avgMaxHp}";
            }
            else
            {
                hpStr = "n/a";
            }

            sb.AppendLine($"  {depth,5}   {avgTurns,9:F1}   {avgKills,9:F1}   {hpStr,10}   {deathPct,5:F1}%");
        }

        sb.AppendLine();
    }

    // ── Section 5: Bot Efficiency ───────────────────────────────────────────

    private static void AppendBotEfficiency(StringBuilder sb, DungeonSoakSummary summary)
    {
        sb.AppendLine("Bot Efficiency:");

        var botSummaries = summary.Runs
            .Where(r => r.BotSummary != null)
            .Select(r => r.BotSummary!)
            .ToList();

        if (botSummaries.Count == 0)
        {
            sb.AppendLine("  (Bot telemetry not available -- run with --telemetry to enable)");
            sb.AppendLine();
            return;
        }

        // Aggregate action counts across all runs
        var totalActionCounts = new Dictionary<string, long>();
        long totalDecisions   = 0;
        double healHpSum      = 0.0;
        int healDecisionSum   = 0;
        int deathsWithUnused  = 0;

        int combatDeaths = summary.Runs.Count(r => r.FailureType == OutcomeClassifier.FailureDeath);

        foreach (var bot in botSummaries)
        {
            totalDecisions += bot.TotalDecisions;

            foreach (var (key, count) in bot.ActionCounts)
            {
                totalActionCounts.TryGetValue(key, out long existing);
                totalActionCounts[key] = existing + count;
            }

            if (bot.HealDecisions > 0)
            {
                healHpSum       += bot.AvgHpWhenHealing * bot.HealDecisions;
                healDecisionSum += bot.HealDecisions;
            }

            deathsWithUnused += bot.DeathsWithUnusedPotions;
        }

        sb.AppendLine("  Action Distribution:");

        if (totalDecisions > 0)
        {
            foreach (var (action, count) in totalActionCounts.OrderByDescending(kv => kv.Value))
            {
                double pct = (double)count / totalDecisions * 100.0;
                sb.AppendLine($"    {action,-20} {pct,5:F1}%");
            }
        }
        else
        {
            sb.AppendLine("    (no decisions recorded)");
        }

        sb.AppendLine();
        sb.AppendLine("  Heal Behavior:");

        if (healDecisionSum > 0)
        {
            double avgHpPct = healHpSum / healDecisionSum * 100.0;
            string flag = avgHpPct > 35.0
                ? "  [WARN: healing too early — wasting potions]"
                : avgHpPct < 10.0
                    ? "  [WARN: healing too late — dying with potions]"
                    : "";
            sb.AppendLine($"    Avg HP% when healing: {avgHpPct:F1}%  (target: 15-30%){flag}");
        }
        else
        {
            sb.AppendLine("    Avg HP% when healing: n/a (no heal decisions)");
        }

        string deathsNote = combatDeaths > 0
            ? $"{deathsWithUnused} / {combatDeaths} combat deaths ({(double)deathsWithUnused / combatDeaths * 100.0:F1}%)"
            : "0 combat deaths";
        sb.AppendLine($"    Deaths with unused potions: {deathsNote}");

        sb.AppendLine();
    }

    // ── Section 6: Anomalies ────────────────────────────────────────────────

    private static void AppendAnomalies(StringBuilder sb, DungeonSoakSummary summary)
    {
        sb.AppendLine("Anomalies:");

        var lines = new List<string>();

        // Runs that hit the max turn limit
        int maxTurnsCount = summary.Runs.Count(r =>
            r.FailureType == OutcomeClassifier.FailureMaxTurns
            || r.FailureType == OutcomeClassifier.FailureStuck);
        if (maxTurnsCount > 0)
            lines.Add($"- {maxTurnsCount} run(s) hit max turn limit (possible stuck bot)");

        // Runs with 0 kills
        int zeroKillCount = summary.Runs.Count(r => r.TotalKills == 0);
        if (zeroKillCount > 0)
            lines.Add($"- {zeroKillCount} run(s) had 0 kills (bot may not have engaged enemies)");

        // Runs that died with >= 2 potions remaining (significant waste)
        var wastedPotionRuns = summary.Runs
            .Where(r => r.Outcome == OutcomeClassifier.Died && r.PotionsRemaining >= 2)
            .ToList();
        foreach (var run in wastedPotionRuns)
        {
            // Find the floor death occurred on
            var deathFloor = run.PerFloor.LastOrDefault(f => f.PlayerDied);
            string floorNote = deathFloor != null ? $" on floor {deathFloor.Depth}" : "";
            lines.Add($"- Run (seed {run.Seed}): died{floorNote} with {run.PotionsRemaining} healing potions remaining");
        }

        // Runs that survived but barely (HP fraction < 10%)
        var narrowSurvivalRuns = summary.Runs
            .Where(r => r.Outcome == OutcomeClassifier.Survived && r.FinalHpFraction < 0.1)
            .ToList();
        foreach (var run in narrowSurvivalRuns)
        {
            int pct = (int)(run.FinalHpFraction * 100);
            lines.Add($"- Run (seed {run.Seed}): survived with only {pct}% HP remaining");
        }

        if (lines.Count == 0)
        {
            sb.AppendLine("  None detected.");
        }
        else
        {
            foreach (var line in lines)
                sb.AppendLine($"  {line}");
        }

        sb.AppendLine();
    }
}
