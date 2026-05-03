using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

public sealed class VeshData
{
    [JsonPropertyName("met")]
    public bool Met { get; set; }

    [JsonPropertyName("jobs_completed")]
    public int JobsCompleted { get; set; }

    [JsonPropertyName("spirit_received")]
    public bool SpiritReceived { get; set; }

    [JsonPropertyName("spirit_story_heard")]
    public bool SpiritStoryHeard { get; set; }
}
