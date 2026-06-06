using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.Endgame;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Loads and resolves the Weighing audit dialogue from weighing_audit.yaml.
///
/// YAML format: each key maps to a list of {speaker, text} objects. This is structured
/// sequential content (not random pools), so each key produces exactly one ordered sequence.
/// </summary>
public sealed class WeighingAuditRegistry
{
    private readonly Dictionary<string, List<WeighingDialoguePage>> _sequences;

    public WeighingAuditRegistry(Dictionary<string, List<WeighingDialoguePage>> sequences)
    {
        _sequences = sequences;
    }

    /// <summary>Load from a YAML string.</summary>
    public static WeighingAuditRegistry LoadFromYaml(string yaml, IObjectFactory? factory = null)
    {
        var deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .WithObjectFactory(factory ?? new AotObjectFactory())
            .Build();

        var raw = deserializer.Deserialize<Dictionary<string, List<RawPage>>>(yaml)
                  ?? new Dictionary<string, List<RawPage>>();

        var sequences = raw.ToDictionary(
            kv => kv.Key,
            kv => kv.Value.Select(p => new WeighingDialoguePage(p.Speaker, p.Text)).ToList());

        return new WeighingAuditRegistry(sequences);
    }

    /// <summary>Resolve the audit opening (fires before the first Guardian rises).</summary>
    public IReadOnlyList<WeighingDialoguePage> GetOpening() =>
        GetSequence("opening");

    /// <summary>
    /// Resolve the beat for a given Guardian at a given tier. Returns an empty list if no
    /// content is registered (e.g. placeholder run before content lands).
    /// </summary>
    public IReadOnlyList<WeighingDialoguePage> GetGuardianBeat(GuardianId guardian, GuardianTier tier)
    {
        string guardianKey = guardian switch
        {
            GuardianId.WardenOfWardens => "warden",
            GuardianId.Oathkeeper => "oathkeeper",
            GuardianId.AuditorsOwn => "auditor",
            GuardianId.AssemblyOfTheLost => "assembly",
            GuardianId.Debt => "debt",
            _ => "unknown",
        };
        string tierKey = tier switch
        {
            GuardianTier.Allied => "allied",
            GuardianTier.Diminished => "diminished",
            GuardianTier.Neutral => "neutral",
            GuardianTier.Savage => "savage",
            _ => "neutral",
        };
        return GetSequence($"{guardianKey}.{tierKey}");
    }

    /// <summary>Resolve the Debt sequence — unscaled, no tiers. Fires before the choice gate.</summary>
    public IReadOnlyList<WeighingDialoguePage> GetDebt() => GetSequence("debt");

    /// <summary>Resolve the resolution text for the given ending (fires on WeighingResolvedEvent).</summary>
    public IReadOnlyList<WeighingDialoguePage> GetResolution(Logic.Endgame.EndingType ending)
    {
        string key = ending switch
        {
            Logic.Endgame.EndingType.CleanAudit => "resolution.clean_audit",
            Logic.Endgame.EndingType.Swap => "resolution.swap",
            Logic.Endgame.EndingType.Theft => "resolution.theft",
            Logic.Endgame.EndingType.LossRefused => "resolution.refused",
            _ => "",
        };
        return GetSequence(key);
    }

    public bool HasSequence(string key) => _sequences.ContainsKey(key);

    private IReadOnlyList<WeighingDialoguePage> GetSequence(string key) =>
        _sequences.TryGetValue(key, out var seq) ? seq : Array.Empty<WeighingDialoguePage>();

    private sealed class RawPage
    {
        public string Speaker { get; set; } = "under_warden";
        public string Text { get; set; } = "";
    }
}
