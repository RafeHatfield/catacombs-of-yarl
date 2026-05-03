using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

public sealed class PastSashasData
{
    [JsonPropertyName("records")]
    public List<PastSashaRecord> Records { get; set; } = new();

    [JsonPropertyName("next_id")]
    public int NextId { get; set; } = 1;

    public PastSashaRecord AddRecord(
        int diedRun, int diedFloor, string causeOfDeath,
        string? killerSpecies, List<GearItemRecord> gearCarried)
    {
        var record = new PastSashaRecord
        {
            Id = NextId++,
            DiedRun = diedRun,
            DiedFloor = diedFloor,
            DiedAt = DateTimeOffset.UtcNow,
            CauseOfDeath = causeOfDeath,
            KillerSpecies = killerSpecies,
            GearCarried = gearCarried,
        };
        Records.Add(record);
        return record;
    }
}

public sealed class PastSashaRecord
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("died_run")]
    public int DiedRun { get; set; }

    [JsonPropertyName("died_floor")]
    public int DiedFloor { get; set; }

    [JsonPropertyName("died_at")]
    public DateTimeOffset DiedAt { get; set; }

    // "monster" | "self_inflicted" | "under_warden"
    [JsonPropertyName("cause_of_death")]
    public string CauseOfDeath { get; set; } = "monster";

    [JsonPropertyName("killer_species")]
    public string? KillerSpecies { get; set; }

    [JsonPropertyName("gear_carried")]
    public List<GearItemRecord> GearCarried { get; set; } = new();
}

public sealed class GearItemRecord
{
    [JsonPropertyName("type_id")]
    public string TypeId { get; set; } = "";

    [JsonPropertyName("enchantment")]
    public int Enchantment { get; set; }

    // "normal" | "corroded" | etc.
    [JsonPropertyName("condition")]
    public string Condition { get; set; } = "normal";
}
