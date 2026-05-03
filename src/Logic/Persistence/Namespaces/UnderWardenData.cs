using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

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
