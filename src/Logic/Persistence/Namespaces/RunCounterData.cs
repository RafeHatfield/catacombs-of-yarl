using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

public sealed class RunCounterData
{
    [JsonPropertyName("total_runs")]
    public int TotalRuns { get; set; }

    [JsonPropertyName("first_run_started_at")]
    public DateTimeOffset? FirstRunStartedAt { get; set; }

    public void IncrementRunCount()
    {
        TotalRuns++;
        FirstRunStartedAt ??= DateTimeOffset.UtcNow;
    }
}
