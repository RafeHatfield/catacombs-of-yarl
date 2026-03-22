using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Tests the impact of the momentum/speed system on combat balance.
/// </summary>
[TestFixture]
public class MomentumTests
{
    private ScenarioRunner _runner = null!;

    [OneTimeSetUp]
    public void Setup()
    {
        var path = Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "entities.yaml");
        _runner = ScenarioRunner.FromEntitiesFile(path);
    }

    private string ScenarioPath(string name) =>
        Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "levels", name);

    [Test]
    public void SpeedBonus_IncreasesPlayerDamage()
    {
        var noSpeed = _runner.RunFromFile(ScenarioPath("scenario_depth2_orc_baseline.yaml"));
        var withSpeed = _runner.RunFromFile(ScenarioPath("scenario_depth2_orc_speed.yaml"));

        // Note: baseline has 1 potion, speed scenario has 2 — both for fair comparison
        // The key metric is player damage output, which should increase with speed bonus
        Assert.That(withSpeed.AvgPlayerDamageDealt, Is.GreaterThan(noSpeed.AvgPlayerDamageDealt),
            $"Speed player DMG {withSpeed.AvgPlayerDamageDealt:F0} should exceed no-speed {noSpeed.AvgPlayerDamageDealt:F0}");
    }

    [Test]
    public void PrintMomentumImpact()
    {
        var baseline = _runner.RunFromFile(ScenarioPath("scenario_depth2_orc_baseline.yaml"));
        var speed = _runner.RunFromFile(ScenarioPath("scenario_depth2_orc_speed.yaml"));

        var pmBase = PressureModel.Compute(baseline, 2, 29, 55);
        var pmSpeed = PressureModel.Compute(speed, 2, 29, 55);

        var hpmTarget = PressureModel.GetH_PM_Target(2);

        TestContext.WriteLine("=== Momentum Impact: Depth 2, 3x Orc ===");
        TestContext.WriteLine($"    H_PM target: {hpmTarget.Min}-{hpmTarget.Max}");
        TestContext.WriteLine("");
        TestContext.WriteLine(string.Format("  {0,-18} {1,10} {2,10}",
            "Metric", "No Speed", "Speed 0.25"));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:P0} {2,10:P0}",
            "Death Rate", baseline.DeathRate, speed.DeathRate));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:F1} {2,10:F1}",
            "Avg Turns", baseline.AvgTurns, speed.AvgTurns));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:F1} {2,10:F1}",
            "Avg Player DMG", baseline.AvgPlayerDamageDealt, speed.AvgPlayerDamageDealt));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:F1} {2,10:F1}",
            "Avg Kills", baseline.AvgMonstersKilled, speed.AvgMonstersKilled));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:F2} {2,10:F2}",
            "DPR_P", pmBase.DPR_P, pmSpeed.DPR_P));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10:F1} {2,10:F1}",
            "H_PM", pmBase.H_PM, pmSpeed.H_PM));
        TestContext.WriteLine(string.Format("  {0,-18} {1,10} {2,10}",
            "H_PM Status", hpmTarget.Status(pmBase.H_PM), hpmTarget.Status(pmSpeed.H_PM)));

        Assert.Pass();
    }
}
