using CatacombsOfYarl.Logic.Balance;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Runs affix weapon variants at depth 2 and 5 to isolate each affix's
/// impact on pressure invariants. Compares against dagger baseline.
/// </summary>
[TestFixture]
[Category("Slow")]
public class AffixProbeTests
{
    private ScenarioRunner _runner = null!;

    private static string ConfigPath(string f) =>
        Path.Combine(TestContext.CurrentContext.TestDirectory, "..", "..", "..", "..", "config", f);

    private static string ScenarioPath(string f) =>
        Path.Combine(TestContext.CurrentContext.TestDirectory, "..", "..", "..", "..", "config", "levels", f);

    [OneTimeSetUp]
    public void Setup()
    {
        _runner = ScenarioRunner.FromEntitiesFile(ConfigPath("entities.yaml"));
    }

    [Test]
    public void PrintAffixProbeReport()
    {
        TestContext.WriteLine("=== AFFIX PROBE REPORT ===");
        TestContext.WriteLine("");

        foreach (int depth in new[] { 2, 5 })
        {
            double monsterHp = depth == 2 ? 29 : 36;
            var hpmTarget = PressureModel.GetH_PM_Target(depth);

            TestContext.WriteLine($"  --- Depth {depth} (H_PM target: {hpmTarget.Min}-{hpmTarget.Max}) ---");
            TestContext.WriteLine(string.Format("  {0,-24} {1,7} {2,7} {3,7} {4,8} {5,8}",
                "Weapon", "H_PM", "DPR_P", "Death%", "HPM?", "Kills"));

            // Baseline
            var baseFile = depth == 2
                ? "scenario_depth2_orc_baseline.yaml"
                : "scenario_depth5_orc_pressure.yaml";
            var baseAgg = _runner.RunFromFile(ScenarioPath(baseFile));
            var basePm = PressureModel.Compute(baseAgg, depth, monsterHp, 55);
            PrintRow("Dagger (baseline)", basePm, baseAgg, hpmTarget);

            // Affixes
            foreach (var affix in new[] { "keen", "vicious", "fine", "masterwork" })
            {
                var file = $"scenario_depth{depth}_orc_{affix}.yaml";
                var path = ScenarioPath(file);
                if (!File.Exists(path)) continue;

                var agg = _runner.RunFromFile(path);
                var pm = PressureModel.Compute(agg, depth, monsterHp, 55);
                var label = affix switch
                {
                    "keen" => "Keen Dagger (crit 19)",
                    "vicious" => "Vicious Shortsword",
                    "fine" => "Fine Longsword (+1 hit)",
                    "masterwork" => "MW Longsword (+1/+1)",
                    _ => affix,
                };
                PrintRow(label, pm, agg, hpmTarget);
            }

            TestContext.WriteLine("");
        }

        Assert.Pass();
    }

    private static void PrintRow(string label, PressureMetrics pm, AggregatedMetrics agg, TargetBand hpmTarget)
    {
        TestContext.WriteLine(string.Format("  {0,-24} {1,7:F1} {2,7:F2} {3,6:P0} {4,8} {5,8:F1}",
            label, pm.H_PM, pm.DPR_P, pm.DeathRate,
            hpmTarget.Status(pm.H_PM), agg.AvgMonstersKilled));
    }

    [Test]
    public void AllAffixes_LowerH_PM_ThanBaseline()
    {
        var baseAgg = _runner.RunFromFile(ScenarioPath("scenario_depth2_orc_baseline.yaml"));
        var basePm = PressureModel.Compute(baseAgg, 2, 29, 55);

        foreach (var affix in new[] { "keen", "vicious", "fine", "masterwork" })
        {
            var path = ScenarioPath($"scenario_depth2_orc_{affix}.yaml");
            if (!File.Exists(path)) continue;

            var agg = _runner.RunFromFile(path);
            var pm = PressureModel.Compute(agg, 2, 29, 55);

            // Each affix should produce lower H_PM than baseline dagger
            // (more damage output = fewer rounds to kill)
            Assert.That(pm.H_PM, Is.LessThanOrEqualTo(basePm.H_PM),
                $"{affix} H_PM {pm.H_PM:F1} should be <= baseline {basePm.H_PM:F1}");
        }
    }
}
