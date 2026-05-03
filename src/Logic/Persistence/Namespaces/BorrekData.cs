using System.Text.Json.Serialization;

namespace CatacombsOfYarl.Logic.Persistence.Namespaces;

public sealed class BorrekData
{
    // "wary" | "curious" | "allied"
    [JsonPropertyName("arc_state")]
    public string ArcState { get; set; } = "wary";

    [JsonPropertyName("orc_positive_actions")]
    public int OrcPositiveActions { get; set; }

    [JsonPropertyName("knife_received")]
    public bool KnifeReceived { get; set; }

    [JsonPropertyName("daughter_bloodline_news_delivered")]
    public bool DaughterBloodlineNewsDelivered { get; set; }
}
