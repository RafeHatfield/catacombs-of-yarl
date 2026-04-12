/// <summary>
/// YARL Balance Pipeline CLI
///
/// Usage (run from project root):
///   dotnet run --project tools/Harness -- --scenario depth1_tuned
///   dotnet run --project tools/Harness -- --scenario depth1_tuned --runs 100 --seed 42
///   dotnet run --project tools/Harness -- --all
///   dotnet run --project tools/Harness -- --all --runs 50
///   dotnet run --project tools/Harness -- --scenario depth1_tuned --json
/// </summary>

using System.Text.Json;
using CatacombsOfYarl.Logic.Balance;

const string EntitiesFile = "config/entities.yaml";
const string LevelsDir    = "config/levels";

// ─── Parse args ────────────────────────────────────────────────────────────

string? scenarioId = null;
bool runAll        = false;
bool jsonOutput    = false;
int? runsOverride  = null;
int seed           = 1337;

for (int i = 0; i < args.Length; i++)
{
    switch (args[i])
    {
        case "--scenario": scenarioId   = args[++i]; break;
        case "--all":      runAll       = true;      break;
        case "--runs":     runsOverride = int.Parse(args[++i]); break;
        case "--seed":     seed         = int.Parse(args[++i]); break;
        case "--json":     jsonOutput   = true;      break;
        case "--help": case "-h":
            PrintHelp(); return 0;
    }
}

if (scenarioId == null && !runAll)
{
    Console.Error.WriteLine("Usage: harness --scenario <id> | --all [--runs N] [--seed N] [--json]");
    Console.Error.WriteLine("Run with --help for details.");
    return 1;
}

if (!File.Exists(EntitiesFile))
{
    Console.Error.WriteLine($"ERROR: '{EntitiesFile}' not found.");
    Console.Error.WriteLine("Run from the project root (the directory containing config/).");
    return 1;
}

// ─── Build runner ──────────────────────────────────────────────────────────

ScenarioRunner runner;
try   { runner = ScenarioRunner.FromEntitiesFile(EntitiesFile); }
catch (Exception ex) { Console.Error.WriteLine($"ERROR loading entities: {ex.Message}"); return 1; }

// ─── Gather scenario paths ─────────────────────────────────────────────────

List<string> paths;
if (runAll)
{
    paths = Directory.GetFiles(LevelsDir, "scenario_depth*.yaml").OrderBy(f => f).ToList();
    if (paths.Count == 0) { Console.Error.WriteLine($"No scenario_depth*.yaml found in '{LevelsDir}'."); return 1; }
}
else
{
    var path = FindScenario(scenarioId!);
    if (path == null) { Console.Error.WriteLine($"Scenario not found: '{scenarioId}'"); return 1; }
    paths = [path];
}

// ─── Run scenarios ─────────────────────────────────────────────────────────

var results = new List<AggregatedMetrics>();
foreach (var path in paths)
{
    Console.Error.Write($"  Running {Path.GetFileNameWithoutExtension(path)}...");
    try
    {
        var m = runner.RunFromFile(path, seed, runsOverride);
        results.Add(m);
        Console.Error.WriteLine($" {m.TotalRuns} runs.");
    }
    catch (Exception ex) { Console.Error.WriteLine($" ERROR: {ex.Message}"); }
}

if (results.Count == 0) { Console.Error.WriteLine("No results."); return 1; }

// ─── Output ────────────────────────────────────────────────────────────────

if (jsonOutput)
{
    // Build full pressure evaluations for JSON
    var evals = results.Select(m =>
    {
        var pm   = ToPresssureMetrics(m);
        var eval = PressureModel.EvaluateProvisional(pm);
        return new
        {
            scenario_id       = m.ScenarioId,
            name              = m.Name,
            depth             = m.Depth,
            runs              = m.TotalRuns,
            seed              = m.Seed,
            death_rate        = m.DeathRate,
            h_pm              = pm.H_PM,
            h_mp              = pm.H_MP,
            dpr_p             = pm.DPR_P,
            dpr_m             = pm.DPR_M,
            avg_turns         = m.AvgTurns,
            player_hit_rate   = m.PlayerHitRate,
            monster_hit_rate  = m.MonsterHitRate,
            evaluation        = eval,
        };
    }).ToList();
    Console.WriteLine(JsonSerializer.Serialize(evals, new JsonSerializerOptions { WriteIndented = true }));
    return 0;
}

if (results.Count == 1) PrintSingle(results[0]);
else                     PrintTable(results);
return 0;

// ─── Helpers ───────────────────────────────────────────────────────────────

// Use PressureModel.Compute so H_PM/H_MP match the DPR-based bands in PressureModel.
PressureMetrics ToPresssureMetrics(AggregatedMetrics m) =>
    PressureModel.Compute(m, m.Depth, m.AvgMonsterMaxHp, (int)Math.Round(m.AvgPlayerMaxHp));

string? FindScenario(string id)
{
    var byFilename = Path.Combine(LevelsDir, $"scenario_{id}.yaml");
    if (File.Exists(byFilename)) return byFilename;

    var asGiven = Path.Combine(LevelsDir, $"{id}.yaml");
    if (File.Exists(asGiven)) return asGiven;

    foreach (var f in Directory.GetFiles(LevelsDir, "*.yaml"))
        foreach (var line in File.ReadLines(f))
        {
            var t = line.TrimStart();
            if (t.StartsWith("scenario_id:") && t.Contains(id)) return f;
            if (t.Length > 0 && !t.StartsWith('#') && !t.StartsWith("scenario_id:") && !t.StartsWith("name:"))
                break;
        }

    return null;
}

void PrintSingle(AggregatedMetrics m)
{
    var pm   = ToPresssureMetrics(m);
    var eval = PressureModel.EvaluateProvisional(pm);
    var sep  = new string('─', 60);

    Console.WriteLine();
    Console.WriteLine($"  {m.ScenarioId}  ({m.TotalRuns} runs, seed {m.Seed})  Depth {m.Depth}");
    if (!string.IsNullOrEmpty(m.Name)) Console.WriteLine($"  {m.Name}");
    Console.WriteLine($"  {sep}");

    Console.WriteLine(MetricLine("Death Rate",
        $"{m.DeathRate:P1}", eval.DeathRate_Target, eval.DeathRate_Status));
    Console.WriteLine(MetricLine("H_PM",
        $"{pm.H_PM:F1}",     eval.H_PM_Target, eval.H_PM_Status));
    Console.WriteLine(MetricLine("H_MP",
        $"{pm.H_MP:F1}",     eval.H_MP_Target, eval.H_MP_Status));
    Console.WriteLine($"  {"DPR_P",-12} {pm.DPR_P,8:F2}    {"DPR_M",-12} {pm.DPR_M:F2}");
    Console.WriteLine($"  {"Avg Turns",-12} {m.AvgTurns,8:F1}    Player Hit%: {m.PlayerHitRate:P0}    Monster Hit%: {m.MonsterHitRate:P0}");
    Console.WriteLine($"  {sep}");

    var findings = PressureModel.Diagnose(eval);
    foreach (var f in findings) Console.WriteLine($"  {f}");
    Console.WriteLine();
}

void PrintTable(List<AggregatedMetrics> ms)
{
    Console.WriteLine();
    Console.WriteLine($"=== YARL Balance Report ({seed} seed) ===");
    Console.WriteLine();
    Console.WriteLine($"  {"Scenario",-28}  {"D",2}  {"Death%",7}  {"[Band]",9}  {"H_PM",5}  {"[Band]",7}  {"H_MP",5}  {"[Band]",7}  Status");
    Console.WriteLine($"  {new string('-', 28)}  {"--"}  {"-------"}  {"---------"}  {"-----"}  {"-------"}  {"-----"}  {"-------"}  ------");

    int passes = 0, fails = 0;
    var failedScenarios = new List<AggregatedMetrics>();

    foreach (var m in ms)
    {
        var pm   = ToPresssureMetrics(m);
        var eval = PressureModel.EvaluateProvisional(pm);

        string dr   = $"{m.DeathRate:P1}";
        string drB  = $"[{eval.DeathRate_Target.Min:P0}-{eval.DeathRate_Target.Max:P0}]";
        string hpm  = $"{pm.H_PM:F1}";
        string hpmB = $"[{eval.H_PM_Target.Min:F1}-{eval.H_PM_Target.Max:F1}]";
        string hmp  = $"{pm.H_MP:F1}";
        string hmpB = $"[{eval.H_MP_Target.Min:F1}-{eval.H_MP_Target.Max:F1}]";

        bool pass = eval.AllInBand;
        if (pass) passes++; else { fails++; failedScenarios.Add(m); }
        string status = pass ? "PASS" : $"FAIL({(eval.H_PM_Status != "OK" ? "H_PM " : "")}{(eval.H_MP_Status != "OK" ? "H_MP " : "")}{(eval.DeathRate_Status != "OK" ? "Death%" : "")})";

        Console.WriteLine($"  {m.ScenarioId,-28}  {m.Depth,2}  {dr,7}  {drB,9}  {hpm,5}  {hpmB,7}  {hmp,5}  {hmpB,7}  {status}");
    }

    Console.WriteLine();
    Console.WriteLine($"  Results: {passes} PASS / {fails} FAIL  ({ms.Count} total)");
    Console.WriteLine();

    if (failedScenarios.Count > 0)
    {
        Console.WriteLine("=== Diagnosis ===");
        Console.WriteLine();
        foreach (var m in failedScenarios)
        {
            Console.WriteLine($"  {m.ScenarioId} (depth {m.Depth}):");
            var findings = PressureModel.Diagnose(PressureModel.EvaluateProvisional(ToPresssureMetrics(m)));
            foreach (var f in findings) Console.WriteLine($"    {f}");
        }
        Console.WriteLine();
    }
}

string MetricLine(string label, string value, TargetBand band, string status)
{
    string tag = status switch { "OK" => "[PASS]", "HIGH" => "[HIGH]", "LOW" => "[LOW ]", _ => "[----]" };
    string bandStr = $"[{band.Min:G4}-{band.Max:G4}]";
    return $"  {label,-12} {value,8}    target: {bandStr,-14}  {tag}";
}

void PrintHelp()
{
    Console.WriteLine("YARL Balance Harness");
    Console.WriteLine();
    Console.WriteLine("Usage:");
    Console.WriteLine("  dotnet run --project tools/Harness -- --scenario <id> [options]");
    Console.WriteLine("  dotnet run --project tools/Harness -- --all [options]");
    Console.WriteLine();
    Console.WriteLine("Options:");
    Console.WriteLine("  --scenario <id>   Run a specific scenario by scenario_id");
    Console.WriteLine("  --all             Run all scenario_depth*.yaml files");
    Console.WriteLine("  --runs <n>        Override run count (default: from YAML, usually 50)");
    Console.WriteLine("  --seed <n>        Base seed (default: 1337)");
    Console.WriteLine("  --json            Output results as JSON");
    Console.WriteLine("  --help, -h        Show this help");
    Console.WriteLine();
    Console.WriteLine("Must be run from the project root (directory containing config/).");
    Console.WriteLine();
    Console.WriteLine("Examples:");
    Console.WriteLine("  dotnet run --project tools/Harness -- --scenario depth1_tuned");
    Console.WriteLine("  dotnet run --project tools/Harness -- --all --runs 100");
    Console.WriteLine("  dotnet run --project tools/Harness -- --all --json > reports/latest.json");
}
