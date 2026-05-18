using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

/// <summary>
/// A formatted memo queued for display in the inbox UI after a run ends.
/// Produced by MemoDeliveryEvaluator (Phase 3) and consumed by MemoInboxPanel (Phase 4).
/// DeliveredRun is the run number on which this memo was generated.
/// </summary>
public sealed record PendingMemo(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("subject")] string Subject,
    [property: JsonPropertyName("body")] string Body,
    [property: JsonPropertyName("delivered_run")] int DeliveredRun
);

public sealed class UnderWardenData
{
    // Monotonic counter. INTENTIONALLY not derivable from procedural_grievances_logged.
    // Content YAML uses this directly for tone-progression rules ("after 8 memos ever,
    // escalate regardless of grievance state"). Future memo variants fire without logging
    // a new grievance. Treat as load-bearing primary state — do not remove during refactors.
    [JsonPropertyName("total_memos_sent_ever")]
    public int TotalMemosSentEver { get; set; }

    // "polite" | "procedural_notice" | "formal_complaint" | "final_audit"
    // Monotonic forward — never regresses. See spec §6.15 tone-progression rule.
    [JsonPropertyName("last_memo_tone")]
    public string LastMemoTone { get; set; } = "polite";

    // Each grievance ID fires once ever. Subsequent runs skip already-logged grievances.
    [JsonPropertyName("procedural_grievances_logged")]
    public List<string> ProceduralGrievancesLogged { get; set; } = new();

    [JsonPropertyName("audit_attempted_runs")]
    public int AuditAttemptedRuns { get; set; }

    // Sticky once true — Clean Audit ending. Drives different memo content forever after.
    [JsonPropertyName("audit_completed")]
    public bool AuditCompleted { get; set; }

    // Monotonic counter. Incremented on PossessionExitedEvent where host is hall_warden.
    // Thresholds: 1 → polite.hall_warden_possession, 3 → procedural_notice, 6+ → formal_complaint.
    [JsonPropertyName("hall_warden_possessions_total")]
    public int HallWardenPossessionsTotal { get; set; }

    // Queue of formatted memos waiting to surface in the inbox UI.
    // PendingMemos are added after each run by MemoDeliveryEvaluator (Phase 3).
    // Consumed by MemoInboxPanel (Phase 4).
    [JsonPropertyName("pending_memos")]
    public List<PendingMemo> PendingMemos { get; set; } = new();

    public bool HasLoggedGrievance(string grievanceId) =>
        ProceduralGrievancesLogged.Contains(grievanceId);

    public void RecordMemoSent(string? newTone = null, string? newGrievanceId = null)
    {
        TotalMemosSentEver++;
        if (newTone != null) LastMemoTone = newTone;
        if (newGrievanceId != null && !HasLoggedGrievance(newGrievanceId))
            ProceduralGrievancesLogged.Add(newGrievanceId);
    }
}
