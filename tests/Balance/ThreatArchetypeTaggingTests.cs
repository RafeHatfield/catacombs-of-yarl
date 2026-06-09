using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// 0c step 3: every combat monster carries the threat archetype docs/balance/threat_archetypes.md §2
/// assigns, resolved through extends-inheritance, and MonsterFactory attaches it as a ThreatArchetypeTag.
/// This is the attribution backbone for role-aware floor health — a misclassified killer would make the
/// report blame the wrong archetype, so the assignment is pinned here (outcome, not attachment).
/// </summary>
[TestFixture]
public class ThreatArchetypeTaggingTests
{
    private static string FindEntitiesYaml()
    {
        var testDir = TestContext.CurrentContext.TestDirectory;
        var path = Path.GetFullPath(Path.Combine(testDir, "..", "..", "..", "..", "config", "entities.yaml"));
        if (File.Exists(path)) return path;
        path = Path.GetFullPath(Path.Combine(testDir, "config", "entities.yaml"));
        if (File.Exists(path)) return path;
        throw new FileNotFoundException($"entities.yaml not found. Tried: {path}");
    }

    private static MonsterFactory CreateFactory()
    {
        var loader = new ContentLoader();
        var bundle = loader.LoadAllFromFile(FindEntitiesYaml());
        var entityFactory = new EntityFactory();
        var itemFactory = new ItemFactory(bundle.Items, entityFactory);
        return new MonsterFactory(bundle.Monsters, entityFactory, itemFactory);
    }

    private static ThreatArchetype? ArchetypeOf(MonsterFactory factory, string typeId)
    {
        var entity = factory.Create(typeId)
            ?? throw new InvalidOperationException($"factory could not create '{typeId}'");
        return entity.Get<ThreatArchetypeTag>()?.Archetype;
    }

    // ── Direct assignments (§2) ───────────────────────────────────────────────────────────
    [TestCase("orc",                 ThreatArchetype.Baseline)]
    [TestCase("skeleton",            ThreatArchetype.Baseline)]
    [TestCase("zombie",              ThreatArchetype.Baseline)]
    [TestCase("cultist_blademaster", ThreatArchetype.Baseline)]
    [TestCase("slime",               ThreatArchetype.Baseline)]
    [TestCase("troll",               ThreatArchetype.Spike)]
    [TestCase("wraith",              ThreatArchetype.Spike)]
    [TestCase("giant_spider",        ThreatArchetype.Spike)]
    [TestCase("cave_spider",         ThreatArchetype.Spike)]
    [TestCase("orc_shaman",          ThreatArchetype.Escalator)]
    [TestCase("orc_chieftain",       ThreatArchetype.Escalator)]
    [TestCase("necromancer",         ThreatArchetype.Escalator)]
    [TestCase("large_slime",         ThreatArchetype.Escalator)]
    [TestCase("lich",                ThreatArchetype.Fused)]
    public void DirectArchetype_IsTaggedAsSpecified(string typeId, ThreatArchetype expected)
        => Assert.That(ArchetypeOf(CreateFactory(), typeId), Is.EqualTo(expected));

    // ── Inheritance via extends (child inherits unless it overrides) ────────────────────────
    [TestCase("orc_grunt",          ThreatArchetype.Baseline)]   // ← orc
    [TestCase("orc_brute",          ThreatArchetype.Baseline)]   // ← orc
    [TestCase("orc_scout",          ThreatArchetype.Baseline)]   // ← orc
    [TestCase("orc_veteran",        ThreatArchetype.Baseline)]   // ← orc
    [TestCase("plague_zombie",      ThreatArchetype.Baseline)]   // ← zombie
    [TestCase("troll_ancient",      ThreatArchetype.Spike)]      // ← troll
    [TestCase("web_spider",         ThreatArchetype.Spike)]      // ← cave_spider
    [TestCase("plague_necromancer", ThreatArchetype.Escalator)] // ← necromancer
    [TestCase("greater_slime",      ThreatArchetype.Escalator)] // ← large_slime ← slime (override holds)
    public void InheritedArchetype_PropagatesThroughExtends(string typeId, ThreatArchetype expected)
        => Assert.That(ArchetypeOf(CreateFactory(), typeId), Is.EqualTo(expected));

    [Test]
    public void OrcSkirmisher_IsBaseline_DespiteNotExtendingOrc()
        => Assert.That(ArchetypeOf(CreateFactory(), "orc_skirmisher"), Is.EqualTo(ThreatArchetype.Baseline));

    // ── Unclassified: no tag, kills carry no archetype (must not crash, must not default) ───
    [Test]
    public void FireBeetle_IsUnclassified_NoTag()
    {
        // fire_beetle is not in §2 — deliberately left untagged pending Rafe's assignment.
        var entity = CreateFactory().Create("fire_beetle");
        Assert.That(entity, Is.Not.Null);
        Assert.That(entity!.Get<ThreatArchetypeTag>(), Is.Null,
            "fire_beetle has no threat_archetype yet — it must stay untagged, not silently default.");
    }

    // ── Parser unit cases ───────────────────────────────────────────────────────────────────
    [TestCase("baseline",  ThreatArchetype.Baseline)]
    [TestCase("SPIKE",     ThreatArchetype.Spike)]
    [TestCase("Escalator", ThreatArchetype.Escalator)]
    [TestCase("fused",     ThreatArchetype.Fused)]
    public void Parse_AcceptsKnownValues_CaseInsensitive(string raw, ThreatArchetype expected)
        => Assert.That(ThreatArchetypeTag.Parse(raw), Is.EqualTo(expected));

    [TestCase(null)]
    [TestCase("")]
    [TestCase("   ")]
    [TestCase("baseliner")]
    [TestCase("tank")]
    public void Parse_RejectsUnknownOrEmpty_ReturnsNull(string? raw)
        => Assert.That(ThreatArchetypeTag.Parse(raw), Is.Null);
}
