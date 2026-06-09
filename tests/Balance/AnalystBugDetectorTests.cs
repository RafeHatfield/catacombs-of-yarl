using System.Text.Json.Nodes;
using CatacombsOfYarl.Analyst;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Acceptance-gate tests for the Analyst BugDetector (Phase 2, predicate mechanism).
///
/// THE GATE (non-optional, per-predicate): a predicate that has never fired is
/// indistinguishable from one that structurally CANNOT fire. So for EACH runnable-now
/// predicate in the REAL rubric (config/rubric/v1.yaml), a transcript fixture engineered to
/// VIOLATE it must produce the bug candidate — and a clean turn in the same fixture must NOT.
/// A clean run reporting nothing is not evidence; only a known-broken fixture firing is.
///
/// These fixtures are permanent regression tests. They load the LIVE rubric (not a stub), so
/// they also prove the loader handles the real file and the live predicate strings fire.
/// </summary>
[TestFixture]
[Description("Analyst BugDetector: each rubric v1 predicate fires on an engineered violation")]
public class AnalystBugDetectorTests
{
    private string _rubricPath = null!;

    [OneTimeSetUp]
    public void Setup()
    {
        var testDir = TestContext.CurrentContext.TestDirectory;
        _rubricPath = Path.Combine(testDir, "..", "..", "..", "..", "config", "rubric", "v1.yaml");
        Assert.That(File.Exists(_rubricPath), Is.True, $"v1.yaml not found at {_rubricPath}");
    }

    private Rubric Rubric() => RubricLoader.LoadFromFile(_rubricPath);

    // ── The four violation fixtures ─────────────────────────────────────────────

    [Test]
    [Description("GATE: soft_lock fires when available_action_count==0 and not is_game_over")]
    public void SoftLock_FiresOnViolation()
    {
        // turn 1 = violation (0 actions, game not over); turn 2 = clean (game over masks it);
        // turn 3 = clean (has actions).
        var jsonl = Transcript(
            CleanTurn(1) with { AvailableActionCount = 0, IsGameOver = false },  // VIOLATION
            CleanTurn(2) with { AvailableActionCount = 0, IsGameOver = true },   // not a soft_lock — game is over
            CleanTurn(3));                                                       // clean
        AssertFiresExactlyOn("soft_lock", jsonl, firingTurns: new[] { 1 });
    }

    [Test]
    [Description("GATE: hp_out_of_range fires when player_hp_pct is outside [0,1]")]
    public void HpOutOfRange_FiresOnViolation()
    {
        var jsonl = Transcript(
            CleanTurn(1) with { PlayerHpPct = 1.5 },   // VIOLATION (> 1)
            CleanTurn(2) with { PlayerHpPct = -0.2 },  // VIOLATION (< 0)
            CleanTurn(3));                             // clean (0.8)
        AssertFiresExactlyOn("hp_out_of_range", jsonl, firingTurns: new[] { 1, 2 });
    }

    [Test]
    [Description("GATE: aggression_tally_negative fires when run_aggression_tally < 0")]
    public void AggressionTallyNegative_FiresOnViolation()
    {
        var jsonl = Transcript(
            CleanTurn(1) with { RunAggressionTally = -1 },  // VIOLATION
            CleanTurn(2) with { RunAggressionTally = 0 },   // clean
            CleanTurn(3) with { RunAggressionTally = 5 });  // clean
        AssertFiresExactlyOn("aggression_tally_negative", jsonl, firingTurns: new[] { 1 });
    }

    [Test]
    [Description("GATE: possession_body_inconsistent fires when possession_active but controlled==player")]
    public void PossessionBodyInconsistent_FiresOnViolation()
    {
        var jsonl = Transcript(
            // VIOLATION: possession active but control never transferred (controlled == player).
            CleanTurn(1) with { PossessionActive = true, ControlledEntityId = 0, PlayerEntityId = 0 },
            // clean: possession active AND control transferred (controlled != player).
            CleanTurn(2) with { PossessionActive = true, ControlledEntityId = 7, PlayerEntityId = 0 },
            // clean: no possession.
            CleanTurn(3) with { PossessionActive = false, ControlledEntityId = 0, PlayerEntityId = 0 });
        AssertFiresExactlyOn("possession_body_inconsistent", jsonl, firingTurns: new[] { 1 });
    }

    // ── Coverage / auditability ─────────────────────────────────────────────────

    [Test]
    [Description("A fully clean transcript yields zero candidates but proves every predicate RAN")]
    public void CleanTranscript_ZeroCandidates_AllPredicatesEvaluated()
    {
        var jsonl = Transcript(CleanTurn(1), CleanTurn(2), CleanTurn(3));
        var result = new BugDetector(Rubric()).Detect(TranscriptLoader.LoadFromText(jsonl));

        Assert.That(result.Candidates, Is.Empty);
        Assert.That(result.Skipped, Is.Empty, "No category should be skipped on a complete transcript.");
        Assert.That(result.Coverage.Count, Is.EqualTo(4), "All four predicate categories must have run.");
        foreach (var c in result.Coverage)
            Assert.That(c.TurnsEvaluated, Is.EqualTo(3), $"{c.Category} must have evaluated every turn.");
    }

    [Test]
    [Description("A predicate whose field is ABSENT from the transcript is SKIPPED, never reported clean")]
    public void MissingField_PredicateSkipped_NotSilentlyClean()
    {
        // Drop run_aggression_tally from every turn. aggression_tally_negative must NOT run.
        var turn = CleanTurn(1).ToNode();
        turn.AsObject().Remove("run_aggression_tally");
        var jsonl = string.Join("\n", Header(), turn.ToJsonString(), Summary());

        var result = new BugDetector(Rubric()).Detect(TranscriptLoader.LoadFromText(jsonl));

        var skip = result.Skipped.SingleOrDefault(s => s.Category == "aggression_tally_negative");
        Assert.That(skip, Is.Not.Null, "Missing field must surface as a SKIP, not a clean pass.");
        Assert.That(skip!.Reason, Does.Contain("run_aggression_tally"));
        Assert.That(result.Coverage.Any(c => c.Category == "aggression_tally_negative"), Is.False,
            "A skipped predicate must not appear in coverage as if it ran.");
    }

    // ── Report shape on a real transcript ───────────────────────────────────────

    [Test]
    [Description("EvaluationReport carries run metadata, candidates, coverage, skips, and a deterministic note")]
    public void EvaluationReport_HasExpectedShape()
    {
        var jsonl = Transcript(CleanTurn(1) with { PlayerHpPct = 2.0 });  // one hp violation
        var transcript = TranscriptLoader.LoadFromText(jsonl);
        var result = new BugDetector(Rubric()).Detect(transcript);
        var report = EvaluationReport.Build(transcript, result);

        var node = JsonNode.Parse(report.ToJson())!.AsObject();
        Assert.Multiple(() =>
        {
            Assert.That(node["run_id"]!.GetValue<string>(), Is.EqualTo("fixture-run"));
            Assert.That(node["player_type"]!.GetValue<string>(), Is.EqualTo("bot"));
            Assert.That(node["replay_available"]!.GetValue<bool>(), Is.True);
            Assert.That(node["bug_candidates"]!.AsArray().Count, Is.EqualTo(1));
            Assert.That(node["bug_candidates"]![0]!["category"]!.GetValue<string>(), Is.EqualTo("hp_out_of_range"));
            Assert.That(node["bug_candidates"]![0]!["evidence_snippet"]!.GetValue<string>(), Does.Contain("player_hp_pct=2"));
            Assert.That(node["predicate_coverage"]!.AsArray().Count, Is.EqualTo(4));
            Assert.That(node["coherence"]!.AsObject().Count, Is.EqualTo(0), "No coherence pass in v1.");
            Assert.That(node["system_coverage"], Is.Not.Null);
            Assert.That(node["analyst_note"]!.GetValue<string>(), Does.Contain("1 bug candidate"));
        });
    }

    // ── Fixture builders ────────────────────────────────────────────────────────

    /// <summary>A non-violating turn: all predicate fields present, none tripping a check.</summary>
    private sealed record TurnFixture(int Turn)
    {
        public int AvailableActionCount { get; init; } = 5;
        public bool IsGameOver { get; init; } = false;
        public double PlayerHpPct { get; init; } = 0.8;
        public int RunAggressionTally { get; init; } = 0;
        public bool PossessionActive { get; init; } = false;
        public int ControlledEntityId { get; init; } = 0;
        public int PlayerEntityId { get; init; } = 0;

        public JsonObject ToNode() => new()
        {
            ["record_type"] = "turn",
            ["turn"] = Turn,
            ["floor"] = 1,
            ["player_hp_pct"] = PlayerHpPct,
            ["available_action_count"] = AvailableActionCount,
            ["is_game_over"] = IsGameOver,
            ["run_aggression_tally"] = RunAggressionTally,
            ["possession_active"] = PossessionActive,
            ["controlled_entity_id"] = ControlledEntityId,
            ["player_entity_id"] = PlayerEntityId,
            ["action_taken"] = new JsonObject { ["kind"] = "Wait" },
            ["events"] = new JsonArray(),
        };
    }

    private static TurnFixture CleanTurn(int turn) => new(turn);

    private static string Header() => new JsonObject
    {
        ["record_type"] = "header",
        ["schema_version"] = 1,
        ["run_id"] = "fixture-run",
        ["persona"] = "balanced",
        ["player_type"] = "bot",
        ["llm_model"] = null,
        ["seed"] = 1,
        ["depth_reached"] = 1,
        ["ending"] = "died",
        ["turn_count"] = 1,
        ["floor_count"] = 1,
        ["replay_available"] = true,
    }.ToJsonString();

    private static string Summary() => new JsonObject
    {
        ["record_type"] = "summary",
        ["hp_profile"] = new JsonArray(),
        ["system_triggers"] = new JsonObject { ["possession_used"] = false },
        ["run_aggression_tally"] = 0,
        ["memos_delivered"] = new JsonArray(),
    }.ToJsonString();

    private static string Transcript(params TurnFixture[] turns)
    {
        var lines = new List<string> { Header() };
        lines.AddRange(turns.Select(t => t.ToNode().ToJsonString()));
        lines.Add(Summary());
        return string.Join("\n", lines);
    }

    private void AssertFiresExactlyOn(string category, string jsonl, int[] firingTurns)
    {
        var result = new BugDetector(Rubric()).Detect(TranscriptLoader.LoadFromText(jsonl));

        // The category was not skipped — it actually ran.
        Assert.That(result.Skipped.Any(s => s.Category == category), Is.False,
            $"{category} must run, not be skipped.");

        var fired = result.Candidates.Where(c => c.Category == category).Select(c => c.Turn).OrderBy(t => t).ToArray();
        Assert.That(fired, Is.EqualTo(firingTurns),
            $"{category} must fire on exactly turns [{string.Join(",", firingTurns)}], got [{string.Join(",", fired)}].");

        // Evidence references the predicate's fields (auditability of WHY it fired).
        foreach (var c in result.Candidates.Where(c => c.Category == category))
            Assert.That(c.EvidenceSnippet, Does.Contain("turn"), "Evidence must localize the firing turn.");
    }
}
