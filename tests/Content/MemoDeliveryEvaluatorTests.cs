using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Persistence;
using CatacombsOfYarl.Tests.Persistence;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Content;

/// <summary>
/// Phase 3 tests: MemoDeliveryEvaluator incident detection, memo queuing,
/// slot filling, counter management, and deduplication logic.
///
/// Uses real YAML files from config/under_warden/ loaded once in [OneTimeSetUp].
/// PersistentRunState is created as a fresh in-memory instance per test using
/// a temp directory (same pattern as UnderWardenDataTests).
/// </summary>
[TestFixture]
public class MemoDeliveryEvaluatorTests
{
    private MemoRegistry _registry = null!;
    private MemoDeliveryEvaluator _evaluator = null!;
    private string _tempDir = "";

    [OneTimeSetUp]
    public void LoadRegistry()
    {
        var testDir = TestContext.CurrentContext.TestDirectory;
        var configDir = Path.GetFullPath(
            Path.Combine(testDir, "..", "..", "..", "..", "config", "under_warden"));

        var memosYaml     = File.ReadAllText(Path.Combine(configDir, "memos.yaml"));
        var causeNamesYaml = File.ReadAllText(Path.Combine(configDir, "cause_display_names.yaml"));

        _registry  = MemoRegistry.LoadFromYaml(memosYaml, causeNamesYaml, new AotObjectFactory());
        _evaluator = new MemoDeliveryEvaluator();
    }

    [SetUp]
    public void SetUp()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "yarl_mde_" + Guid.NewGuid());
        Directory.CreateDirectory(_tempDir);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private PersistentRunState FreshState() =>
        PersistentRunState.LoadFromDisk(new FakePersistencePathProvider(_tempDir));

    private static PostRunContext Died(int floor, string? cause = null, string? killer = null, int run = 1) =>
        new(Died: true, CauseOfDeath: cause, KillerSpecies: killer, FloorReached: floor, RunNumber: run);

    private static PostRunContext Survived(int floor = 10, int run = 1) =>
        new(Died: false, CauseOfDeath: null, KillerSpecies: null, FloorReached: floor, RunNumber: run);

    // ── death_first ───────────────────────────────────────────────────────────

    [Test]
    public void Death_QueuesDeath_First_Memo_On_First_Death()
    {
        var state = FreshState();
        var ctx = Died(floor: 5, cause: "orc_brute", run: 1);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        var memos = state.UnderWarden.PendingMemos;
        Assert.That(memos.Any(m => m.Key == "polite.death_first"), Is.True,
            "Expected polite.death_first to be queued on first death");
    }

    [Test]
    public void Death_DoesNotRequeue_Death_First_Memo_On_Second_Death()
    {
        var state = FreshState();
        // Manually log the grievance so it looks like it already fired
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 5, cause: "orc_brute", run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        var deathFirstMemos = state.UnderWarden.PendingMemos
            .Where(m => m.Key == "polite.death_first")
            .ToList();

        Assert.That(deathFirstMemos, Is.Empty,
            "polite.death_first must not re-fire after it has been logged");
    }

    // ── floor_low ─────────────────────────────────────────────────────────────

    [Test]
    public void Death_QueuesFloorLow_When_DiedOnFloor3()
    {
        var state = FreshState();
        // Seed death_first so it doesn't interfere with the count assertion
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 3, run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.floor_low"), Is.True,
            "polite.floor_low should fire for floor <= 3");
    }

    [Test]
    public void Death_DoesNotQueueFloorLow_When_DiedOnFloor4()
    {
        var state = FreshState();
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 4, run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.floor_low"), Is.False,
            "polite.floor_low must not fire for floor > 3");
    }

    // ── cause_trap ────────────────────────────────────────────────────────────

    [Test]
    public void Death_QueuesCauseTrap_For_SpikeTrap()
    {
        var state = FreshState();
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 5, cause: "spike_trap", run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.cause_trap"), Is.True,
            "polite.cause_trap should fire for spike_trap");
    }

    [Test]
    public void Death_QueuesCauseTrap_For_OwnTrap()
    {
        var state = FreshState();
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 5, cause: "own_trap", run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.cause_trap"), Is.True,
            "polite.cause_trap should fire for own_trap");
    }

    [Test]
    public void Death_DoesNotQueueCauseTrap_For_OrcBrute()
    {
        var state = FreshState();
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 5, cause: "orc_brute", run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.cause_trap"), Is.False,
            "polite.cause_trap must not fire for non-trap causes");
    }

    // ── cause_acid ────────────────────────────────────────────────────────────

    [Test]
    public void Death_QueuesCauseAcid_For_AcidPool()
    {
        var state = FreshState();
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");

        var ctx = Died(floor: 5, cause: "acid_pool", run: 2);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.cause_acid"), Is.True,
            "polite.cause_acid should fire for acid_pool");
    }

    // ── multi-memo fire ───────────────────────────────────────────────────────

    [Test]
    public void Death_CanQueueMultipleMemos_For_FirstDeathOnFloor2ByTrap()
    {
        var state = FreshState();
        var ctx = Died(floor: 2, cause: "spike_trap", run: 1);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        var keys = state.UnderWarden.PendingMemos.Select(m => m.Key).ToList();

        Assert.That(keys, Contains.Item("polite.death_first"),  "death_first should fire");
        Assert.That(keys, Contains.Item("polite.floor_low"),    "floor_low should fire (floor 2)");
        Assert.That(keys, Contains.Item("polite.cause_trap"),   "cause_trap should fire (spike_trap)");
        Assert.That(state.UnderWarden.PendingMemos, Has.Count.EqualTo(3),
            "Exactly 3 memos: death_first + floor_low + cause_trap");
    }

    // ── survival ─────────────────────────────────────────────────────────────

    [Test]
    public void Survive_QueuesNoMemos()
    {
        var state = FreshState();
        var ctx = Survived(floor: 10, run: 1);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos, Is.Empty,
            "No memos should fire on survival");
        Assert.That(state.IsDirty, Is.False,
            "State must not be marked dirty if no memos were added");
    }

    // ── Hall Warden possession thresholds ─────────────────────────────────────

    [Test]
    public void HallWarden_First_Queues_PoliteMemo()
    {
        var state = FreshState();

        _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: 1);

        Assert.That(state.UnderWarden.HallWardenPossessionsTotal, Is.EqualTo(1));
        Assert.That(state.UnderWarden.PendingMemos.Any(m => m.Key == "polite.hall_warden_possession"), Is.True,
            "polite.hall_warden_possession should fire at count=1");
    }

    [Test]
    public void HallWarden_Third_Queues_ProceduralNotice()
    {
        var state = FreshState();

        _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: 1);
        _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: 2);
        _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: 3);

        Assert.That(state.UnderWarden.HallWardenPossessionsTotal, Is.EqualTo(3));
        Assert.That(
            state.UnderWarden.PendingMemos.Any(m => m.Key == "procedural_notice.hall_warden_possession"),
            Is.True,
            "procedural_notice.hall_warden_possession should fire at count=3");
    }

    [Test]
    public void HallWarden_Sixth_Queues_FormalComplaint()
    {
        var state = FreshState();

        for (var i = 1; i <= 6; i++)
            _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: i);

        Assert.That(state.UnderWarden.HallWardenPossessionsTotal, Is.EqualTo(6));
        Assert.That(
            state.UnderWarden.PendingMemos.Any(m => m.Key == "formal_complaint.hall_warden_possession"),
            Is.True,
            "formal_complaint.hall_warden_possession should fire at count=6");
    }

    [Test]
    public void HallWarden_Seventh_DoesNotRequeue_FormalComplaint()
    {
        var state = FreshState();

        for (var i = 1; i <= 7; i++)
            _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: i);

        Assert.That(state.UnderWarden.HallWardenPossessionsTotal, Is.EqualTo(7));

        var formalComplaintCount = state.UnderWarden.PendingMemos
            .Count(m => m.Key == "formal_complaint.hall_warden_possession");

        Assert.That(formalComplaintCount, Is.EqualTo(1),
            "formal_complaint.hall_warden_possession must fire at most once (7th call should not re-queue)");
    }

    // ── Slot filling ──────────────────────────────────────────────────────────

    [Test]
    public void FormattedMemo_HasSlotsFilled()
    {
        var state = FreshState();
        // Seed death_first so we only get floor_low
        state.UnderWarden.RecordMemoSent(newGrievanceId: "polite.death_first");
        // Set a known best floor
        state.RunCounter.UpdateBestFloor(12);

        var ctx = Died(floor: 2, cause: "orc_brute", run: 5);

        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        var floorLow = state.UnderWarden.PendingMemos.FirstOrDefault(m => m.Key == "polite.floor_low");
        Assert.That(floorLow, Is.Not.Null, "polite.floor_low should have been queued");

        // The formatted body should contain the floor number, not the raw slot token
        Assert.That(floorLow!.Body, Does.Contain("Floor 2").Or.Contain("floor 2"),
            "Formatted body should contain resolved floor value, not {floor} placeholder");
        Assert.That(floorLow.Body, Does.Not.Contain("{floor}"),
            "{floor} slot must have been substituted");
    }

    // ── Pending memo count ────────────────────────────────────────────────────

    [Test]
    public void PendingMemos_Count_IncreasesCorrectly()
    {
        var state = FreshState();

        // Three incidents fire: death_first, floor_low, cause_trap
        var ctx = Died(floor: 2, cause: "spike_trap", run: 1);
        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.UnderWarden.PendingMemos.Count, Is.EqualTo(3));
    }

    // ── TotalMemosSentEver ────────────────────────────────────────────────────

    [Test]
    public void RecordMemoSent_Called_IncrementsTotalMemosSentEver()
    {
        var state = FreshState();
        Assert.That(state.UnderWarden.TotalMemosSentEver, Is.EqualTo(0),
            "Starts at 0");

        var ctx = Died(floor: 5, cause: "orc_brute", run: 1);
        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        // Only death_first fires (floor > 3, not a trap/acid cause)
        Assert.That(state.UnderWarden.TotalMemosSentEver, Is.EqualTo(1),
            "TotalMemosSentEver should be 1 after one memo queued");
    }

    // ── Dirty flag ───────────────────────────────────────────────────────────

    [Test]
    public void EvaluateRunEnd_MarksStateDirty_WhenMemosAdded()
    {
        var state = FreshState();
        Assert.That(state.IsDirty, Is.False, "Should start clean");

        var ctx = Died(floor: 5, cause: "orc_brute", run: 1);
        _evaluator.EvaluateRunEnd(ctx, state, _registry);

        Assert.That(state.IsDirty, Is.True, "Should be dirty after memo was added");
    }

    [Test]
    public void EvaluateHallWardenPossession_AlwaysMarksStateDirty()
    {
        var state = FreshState();

        _evaluator.EvaluateHallWardenPossession(state, _registry, runNumber: 1);

        Assert.That(state.IsDirty, Is.True,
            "EvaluateHallWardenPossession always increments counter, so always marks dirty");
    }
}
