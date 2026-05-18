using CatacombsOfYarl.Logic.Persistence;
using CatacombsOfYarl.Logic.Persistence.Namespaces;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Evaluates post-run and mid-run events to decide which Under-Warden memos should be
/// queued for the player to read in the inbox.
///
/// Called from two entry points:
///   - EvaluateRunEnd: after each game run ends (death or survival)
///   - EvaluateHallWardenPossession: when a Hall Warden possession ends
///
/// Both methods append formatted PendingMemo entries to state.UnderWarden.PendingMemos
/// and call state.MarkDirty() if any memos were added.
///
/// Fire semantics:
///   - body[0] fires the first time an incident key fires (cross-run, via ProceduralGrievancesLogged)
///   - body[1] fires on subsequent fires (fireIndex=1), if the memo has a variant
///   - Single-shot memos (only body[0]) never re-fire — checked via HasLoggedGrievance
/// </summary>
public sealed class MemoDeliveryEvaluator
{
    // Engine cause strings that map to the "trap" incident type.
    private static readonly HashSet<string> TrapCauses = new(StringComparer.OrdinalIgnoreCase)
    {
        "spike_trap", "dart_trap", "flame_trap", "own_trap",
    };

    // Engine cause strings that map to the "acid" incident type.
    private static readonly HashSet<string> AcidCauses = new(StringComparer.OrdinalIgnoreCase)
    {
        "acid_pool", "acid_spray",
    };

    private readonly MemoFormatter _formatter = new();

    // ── Public API ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Evaluate which memos should fire after a game run ends. Adds formatted memos
    /// to the pending queue and marks state dirty if any were added.
    ///
    /// Fire order is deterministic: death_first → floor_low → cause_trap → cause_acid.
    /// A single run can produce multiple memos (e.g. first death on floor 2 via spike_trap
    /// fires death_first, floor_low, and cause_trap).
    /// </summary>
    public void EvaluateRunEnd(PostRunContext ctx, PersistentRunState state, MemoRegistry registry)
    {
        if (!ctx.Died)
            return;

        var addedAny = false;

        // ── polite.death_first ─────────────────────────────────────────────────
        // Single-shot. Only fires if this key has never been logged before.
        if (!state.UnderWarden.HasLoggedGrievance("polite.death_first"))
        {
            AddMemo("polite.death_first", ctx, state, registry, ctx.RunNumber);
            addedAny = true;
        }

        // ── polite.floor_low ──────────────────────────────────────────────────
        // Multi-fire. Fires whenever a death happens on floor 3 or below.
        if (ctx.FloorReached <= 3)
        {
            AddMemo("polite.floor_low", ctx, state, registry, ctx.RunNumber);
            addedAny = true;
        }

        // ── polite.cause_trap ─────────────────────────────────────────────────
        // Multi-fire. Fires whenever death cause is a trap type.
        if (ctx.CauseOfDeath != null && TrapCauses.Contains(ctx.CauseOfDeath))
        {
            AddMemo("polite.cause_trap", ctx, state, registry, ctx.RunNumber);
            addedAny = true;
        }

        // ── polite.cause_acid ─────────────────────────────────────────────────
        // Multi-fire. Fires whenever death cause is an acid type.
        if (ctx.CauseOfDeath != null && AcidCauses.Contains(ctx.CauseOfDeath))
        {
            AddMemo("polite.cause_acid", ctx, state, registry, ctx.RunNumber);
            addedAny = true;
        }

        if (addedAny)
            state.MarkDirty();
    }

    /// <summary>
    /// Called when a Hall Warden possession ends. Increments the possession counter and
    /// queues the appropriate memo at each threshold (1, 3, 6+).
    ///
    /// The formal_complaint fires once only (guarded by ProceduralGrievancesLogged).
    /// Always marks state dirty since the counter always increments.
    /// </summary>
    public void EvaluateHallWardenPossession(PersistentRunState state, MemoRegistry registry, int runNumber)
    {
        state.UnderWarden.HallWardenPossessionsTotal++;
        var total = state.UnderWarden.HallWardenPossessionsTotal;

        // Use a null context — possession memos don't have per-run death data.
        // Pass a minimal ctx with only the run number relevant field.
        var ctx = new PostRunContext(
            Died: false,
            CauseOfDeath: null,
            KillerSpecies: null,
            FloorReached: 0,
            RunNumber: runNumber
        );

        if (total == 1)
        {
            AddMemo("polite.hall_warden_possession", ctx, state, registry, runNumber);
        }
        else if (total == 3)
        {
            AddMemo("procedural_notice.hall_warden_possession", ctx, state, registry, runNumber);
        }
        else if (total >= 6 && !state.UnderWarden.HasLoggedGrievance("formal_complaint.hall_warden_possession"))
        {
            AddMemo("formal_complaint.hall_warden_possession", ctx, state, registry, runNumber);
        }

        state.MarkDirty();
    }

    // ── Private helpers ────────────────────────────────────────────────────────

    /// <summary>
    /// Look up the memo definition, determine the correct fire index, format the memo,
    /// and append it to the pending queue. Also calls RecordMemoSent to track the
    /// grievance key and increment TotalMemosSentEver.
    ///
    /// If the key is unknown in the registry, the call is a no-op.
    /// </summary>
    private void AddMemo(
        string memoKey,
        PostRunContext ctx,
        PersistentRunState state,
        MemoRegistry registry,
        int runNumber)
    {
        var memo = registry.GetMemo(memoKey);
        if (memo is null)
            return;

        // fireIndex=0 for first-ever fire; 1 for repeat fires.
        // Single-shot memos only have body[0], so repeat fires would fall back to body[0]
        // anyway — but single-shot memos shouldn't re-fire at all (caller guards via
        // HasLoggedGrievance for single-shot keys). Here we just compute the index.
        var fireIndex = state.UnderWarden.HasLoggedGrievance(memoKey) ? 1 : 0;

        var slots = BuildSlots(ctx, state);
        var (subject, body) = _formatter.Format(memo, fireIndex, slots, registry);

        state.UnderWarden.PendingMemos.Add(new PendingMemo(
            Key: memoKey,
            Subject: subject,
            Body: body,
            DeliveredRun: runNumber
        ));

        // RecordMemoSent increments TotalMemosSentEver and dedup-adds to ProceduralGrievancesLogged.
        state.UnderWarden.RecordMemoSent(newGrievanceId: memoKey);
    }

    /// <summary>
    /// Build the slot dictionary from the run context and persistent state.
    /// All slots are strings; unknown slots are left as-is by MemoFormatter.
    /// </summary>
    private static Dictionary<string, string> BuildSlots(PostRunContext ctx, PersistentRunState state)
    {
        return new Dictionary<string, string>
        {
            ["run_number"]    = ctx.RunNumber.ToString(),
            ["floor"]         = ctx.FloorReached.ToString(),
            ["cause_of_death"] = ctx.CauseOfDeath ?? "unknown",
            ["killer_species"] = ctx.KillerSpecies ?? "",
            ["run_count"]     = state.RunCounter.TotalRuns.ToString(),
            ["memo_count"]    = state.UnderWarden.TotalMemosSentEver.ToString(),
            ["floor_best"]    = state.RunCounter.BestFloorReached.ToString(),
            ["offense_summary"] = "", // deferred — empty string for now
        };
    }
}
