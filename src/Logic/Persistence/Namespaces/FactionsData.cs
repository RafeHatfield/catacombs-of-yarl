using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

public sealed class FactionsData
{
    // v1 populates "orc" only. Additional factions are default-adds — missing keys default
    // to a fresh Neutral FactionStateEntry. See spec §6.3 for extension story.
    [JsonPropertyName("factions")]
    public Dictionary<string, FactionStateEntry> Factions { get; set; } = new()
    {
        ["orc"] = new FactionStateEntry()
    };

    public FactionStateEntry GetOrCreate(string factionId)
    {
        if (!Factions.TryGetValue(factionId, out var entry))
        {
            entry = new FactionStateEntry();
            Factions[factionId] = entry;
        }
        return entry;
    }
}

public sealed class FactionStateEntry
{
    // "hostile" | "neutral" | "allied"
    [JsonPropertyName("state")]
    public string State { get; set; } = "neutral";

    // Cross-run decay counter for Hostile → Neutral soft-decay (per spec §6.3, OQ-3).
    [JsonPropertyName("runs_since_negative_action")]
    public int RunsSinceNegativeAction { get; set; }
}
