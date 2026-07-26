using System.IO;
using System.Text.RegularExpressions;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace CatacombsOfYarl.Tests.Possession;

/// <summary>
/// Hollowmark voice batches 1a (revised) + 1b + 1c + 1d: hp_threshold, region_first_entry,
/// trap_first, kill_streak_clean, long_idle, species_first_sight, item_identified,
/// overnight_identified, on_death triggers.
/// Content-only — no scheduler wiring; pools are sized for the future once-per-run
/// shuffle-bag scheduler, not enforced by the registry today (GetLine is
/// first-line-first, then random with replacement). overnight_identified is
/// forward-authored: the overnight identification mechanic exists only in design
/// docs, not in code. on_death.* keys are flat by design (not on_death.monster.*)
/// so the registry's one-segment compound-key fallback degrades any unmatched
/// cause to the on_death generic pool in a single hop.
/// </summary>
[TestFixture]
public class HollowmarkVoiceBatchTests
{
    private static string VoiceLinePath() =>
        Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "voice_lines", "hollowmark.yaml");

    private static readonly string[] LegacyKeys =
    {
        "past_sasha_encounter.looted_body",
        "past_sasha_encounter.looted_body.on_loot",
        "past_sasha_encounter.quipping_shade.before",
        "past_sasha_encounter.quipping_shade.after",
        "past_sasha_encounter.possessed_corpse.identify",
        "past_sasha_encounter.possessed_corpse.pre_spell_break",
        "past_sasha_encounter.possessed_corpse.post_spell_break",
    };

    // The 9 PoC-canonical TrapType values documented in FloorTrapComponent.cs.
    // Kept here only as the *expected* set derived from that doc comment for the
    // dedicated FloorTrapComponent-roster test below; the batch key-set test
    // derives its expectation independently (see TrapFirstKeys_MatchFloorTrapComponentRoster).
    private static readonly string[] FloorTrapComponentRoster =
    {
        "spike_trap", "web_trap", "alarm_plate", "root_trap",
        "teleport_trap", "gas_trap", "fire_trap", "hole_trap", "acid_trap",
    };

    private static readonly string[] SpeciesFirstSightKeys =
    {
        "orc", "orc_grunt", "orc_brute", "orc_scout", "orc_veteran", "orc_skirmisher",
        "orc_shaman", "orc_chieftain", "troll", "troll_ancient", "skeleton", "zombie",
        "plague_zombie", "wraith", "lich", "necromancer", "plague_necromancer",
        "cultist_blademaster", "cave_spider", "web_spider", "giant_spider",
        "fire_beetle", "slime", "large_slime", "greater_slime",
    };

    // entities.yaml top-level sections that item_identified.* categories map to.
    private static readonly string[] ItemCategories = { "potion", "scroll", "wand", "ring" };

    private static readonly Dictionary<string, string> ItemCategoryToEntitiesSection = new()
    {
        ["potion"] = "consumables",
        ["scroll"] = "scrolls",
        ["wand"] = "wands",
        ["ring"] = "rings",
    };

    private static readonly string[] NewKeys = BuildNewKeys();

    private static string[] BuildNewKeys()
    {
        var keys = new List<string>
        {
            "hp_threshold.25", "hp_threshold.10", "hp_threshold.1",
            "region_first_entry.boundary", "region_first_entry.dimhalls",
            "region_first_entry.crossing", "region_first_entry.inner_court",
            "region_first_entry.weighing",
            "kill_streak_clean", "long_idle",
            "overnight_identified",
        };
        foreach (var trap in FloorTrapComponentRoster)
            keys.Add($"trap_first.{trap}");
        foreach (var species in SpeciesFirstSightKeys)
            keys.Add($"species_first_sight.{species}");
        foreach (var category in ItemCategories)
            keys.Add($"item_identified.{category}");
        foreach (var species in SpeciesFirstSightKeys)
            keys.Add($"on_death.{species}");
        keys.Add("on_death.hazard");
        keys.Add("on_death");
        keys.Add("spell_break_used");
        return keys.ToArray();
    }

    private static Dictionary<string, List<string>> LoadPools()
    {
        var yaml = File.ReadAllText(VoiceLinePath());
        var deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .WithObjectFactory(new AotObjectFactory())
            .Build();
        return deserializer.Deserialize<Dictionary<string, List<string>>>(yaml)
               ?? new Dictionary<string, List<string>>();
    }

    [Test]
    public void HollowmarkYaml_LoadsWithoutError()
    {
        var yaml = File.ReadAllText(VoiceLinePath());
        Assert.DoesNotThrow(() => VoiceLineRegistry.LoadFromYaml(yaml, new AotObjectFactory(strict: true)));
    }

    [Test]
    public void HasTrigger_ReturnsTrueForAllNewKeys()
    {
        var yaml = File.ReadAllText(VoiceLinePath());
        var registry = VoiceLineRegistry.LoadFromYaml(yaml, new AotObjectFactory());

        // The batch 1d task text claimed 28 new keys / 84 total / 77 taxonomy, but the
        // actual payload (25 on_death.<species> + on_death.hazard + on_death) is 27 new
        // keys — the 32-new-lines figure (25 + 4 + 3) does check out, only the key-count
        // figures don't. Asserting the true count derived from the payload; flagged in
        // the PR description rather than silently matching the stated-but-wrong number.
        // Batch 1e adds 1 more key (spell_break_used): 77 taxonomy keys total, matching
        // the batch 1e task's own stated end-state exactly.
        Assert.That(NewKeys.Length, Is.EqualTo(77), "Sanity check on the expected new-key count.");
        foreach (var key in NewKeys)
            Assert.That(registry.HasTrigger(key), Is.True, $"Missing trigger: {key}");
    }

    [Test]
    public void LegacyKeys_StillPresent()
    {
        var yaml = File.ReadAllText(VoiceLinePath());
        var registry = VoiceLineRegistry.LoadFromYaml(yaml, new AotObjectFactory());

        foreach (var key in LegacyKeys)
            Assert.That(registry.HasTrigger(key), Is.True, $"Legacy trigger missing: {key}");
    }

    [Test]
    public void PoolCounts_MatchSpec()
    {
        var pools = LoadPools();
        var expected = new Dictionary<string, int>
        {
            ["hp_threshold.25"] = 4,
            ["hp_threshold.10"] = 4,
            ["hp_threshold.1"] = 3,
            ["region_first_entry.boundary"] = 2,
            ["region_first_entry.dimhalls"] = 2,
            ["region_first_entry.crossing"] = 2,
            ["region_first_entry.inner_court"] = 2,
            ["region_first_entry.weighing"] = 2,
            ["kill_streak_clean"] = 6,
            ["long_idle"] = 6,
            ["overnight_identified"] = 16,
        };
        foreach (var trap in FloorTrapComponentRoster)
            expected[$"trap_first.{trap}"] = 2;
        foreach (var species in SpeciesFirstSightKeys)
            expected[$"species_first_sight.{species}"] = 1;
        foreach (var category in ItemCategories)
            expected[$"item_identified.{category}"] = 10;
        foreach (var species in SpeciesFirstSightKeys)
            expected[$"on_death.{species}"] = 1;
        expected["on_death.hazard"] = 4;
        expected["on_death"] = 3;
        expected["spell_break_used"] = 25;

        var totalLines = 0;
        foreach (var (key, count) in expected)
        {
            Assert.That(pools.ContainsKey(key), Is.True, $"Missing pool: {key}");
            Assert.That(pools[key].Count, Is.EqualTo(count), $"Pool count mismatch for {key}");
            totalLines += pools[key].Count;
        }

        Assert.That(totalLines, Is.EqualTo(189), "Total new-line count across all new pools should be 189.");
    }

    [Test]
    public void OnDeathSpeciesKeys_MatchSpeciesFirstSightKeys_AndEntitiesYamlMonsterIds()
    {
        // Guards the batch's key design intent: on_death.<species> and
        // species_first_sight.<species> must never drift apart, and both must stay
        // pinned to entities.yaml's actual monster roster (excluding troll_probe_*).
        var pools = LoadPools();

        var onDeathSpecies = pools.Keys
            .Where(k => k.StartsWith("on_death.", StringComparison.Ordinal)
                        && k != "on_death.hazard")
            .Select(k => k["on_death.".Length..])
            .ToHashSet();

        var speciesFirstSight = pools.Keys
            .Where(k => k.StartsWith("species_first_sight.", StringComparison.Ordinal))
            .Select(k => k["species_first_sight.".Length..])
            .ToHashSet();

        Assert.That(onDeathSpecies, Is.EquivalentTo(speciesFirstSight),
            "on_death.<species> keys must exactly match species_first_sight.<species> keys.");

        var entitiesPath = Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "entities.yaml");
        var lines = File.ReadAllLines(entitiesPath);
        var monstersStart = Array.FindIndex(lines, l => l == "monsters:");
        var monstersEnd = lines.Length;
        for (var i = monstersStart + 1; i < lines.Length; i++)
        {
            if (Regex.IsMatch(lines[i], @"^[a-z_][a-z0-9_]*:"))
            {
                monstersEnd = i;
                break;
            }
        }
        var monsterIds = new HashSet<string>();
        for (var i = monstersStart + 1; i < monstersEnd; i++)
        {
            var m = Regex.Match(lines[i], @"^  (?<id>[a-z_][a-z0-9_]*):\s*$");
            if (m.Success)
                monsterIds.Add(m.Groups["id"].Value);
        }
        monsterIds.RemoveWhere(id => id.StartsWith("troll_probe_", StringComparison.Ordinal));

        Assert.That(onDeathSpecies, Is.EquivalentTo(monsterIds),
            "on_death.<species> keys must exactly match entities.yaml monster ids (excl. troll_probe_*).");
    }

    [Test]
    public void ItemIdentifiedCategories_MapToNonEmptyEntitiesYamlSections()
    {
        // Guards the batch's key design intent: item_identified.<category> maps to
        // an entities.yaml top-level section. If a section is ever renamed, this
        // test breaks loudly instead of the mapping silently going stale.
        var entitiesPath = Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "entities.yaml");
        var lines = File.ReadAllLines(entitiesPath);

        foreach (var (category, section) in ItemCategoryToEntitiesSection)
        {
            var sectionStart = Array.FindIndex(lines, l => l == $"{section}:");
            Assert.That(sectionStart, Is.GreaterThanOrEqualTo(0),
                $"entities.yaml has no top-level '{section}:' section for item_identified.{category}.");

            var sectionEnd = lines.Length;
            for (var i = sectionStart + 1; i < lines.Length; i++)
            {
                if (Regex.IsMatch(lines[i], @"^[a-z_][a-z0-9_]*:"))
                {
                    sectionEnd = i;
                    break;
                }
            }

            var hasEntry = false;
            for (var i = sectionStart + 1; i < sectionEnd; i++)
            {
                if (Regex.IsMatch(lines[i], @"^  [a-z_][a-z0-9_]*:\s*$"))
                {
                    hasEntry = true;
                    break;
                }
            }
            Assert.That(hasEntry, Is.True, $"entities.yaml section '{section}:' has no entries.");
        }
    }

    [Test]
    public void TrapFirstKeys_MatchFloorTrapComponentRoster()
    {
        // Derive the expected set from FloorTrapComponent's TrapType doc comment,
        // not a copy-pasted literal, so this test breaks if the component's
        // documented roster ever changes without a corresponding voice update.
        var componentSource = File.ReadAllText(Path.Combine(
            TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "src", "Logic", "ECS", "FloorTrapComponent.cs"));

        var match = Regex.Match(componentSource,
            @"PoC-canonical trap type identifiers:\s*///\s*""(?<types>.+?)""\s*\|.*?\n(?:\s*///\s*""[^""]+""\s*\|?\s*\n?)*",
            RegexOptions.Singleline);

        // Pull every quoted identifier out of the doc-comment block that precedes TrapType.
        var docBlockStart = componentSource.IndexOf("PoC-canonical trap type identifiers", StringComparison.Ordinal);
        Assert.That(docBlockStart, Is.GreaterThan(-1), "Could not locate TrapType doc comment in FloorTrapComponent.cs.");
        var docBlockEnd = componentSource.IndexOf("public string TrapType", docBlockStart, StringComparison.Ordinal);
        var docBlock = componentSource.Substring(docBlockStart, docBlockEnd - docBlockStart);

        var expectedTrapTypes = Regex.Matches(docBlock, "\"(?<id>[a-z_]+)\"")
            .Select(m => m.Groups["id"].Value)
            .ToHashSet();

        Assert.That(expectedTrapTypes, Is.Not.Empty, "Failed to parse any TrapType identifiers from the doc comment.");

        var pools = LoadPools();
        var actualTrapKeys = pools.Keys
            .Where(k => k.StartsWith("trap_first.", StringComparison.Ordinal))
            .Select(k => k["trap_first.".Length..])
            .ToHashSet();

        Assert.That(actualTrapKeys, Is.EquivalentTo(expectedTrapTypes),
            "trap_first.* key set must exactly equal FloorTrapComponent's documented TrapType roster.");
    }

    [Test]
    public void SpeciesFirstSightKeys_AreSubsetOfEntitiesYamlMonsterIds()
    {
        // entities.yaml mixes heterogeneous top-level sections (maps and sequences),
        // which a single strongly-typed deserialize can't handle uniformly. We only
        // need the "monsters:" block's direct child keys, so extract that block by
        // indentation (bounded by the next zero-indent top-level key) and regex the
        // two-space-indented "id:" lines out of it — no schema assumptions beyond
        // the file's existing indentation convention.
        var entitiesPath = Path.Combine(TestContext.CurrentContext.TestDirectory,
            "..", "..", "..", "..", "config", "entities.yaml");
        var lines = File.ReadAllLines(entitiesPath);

        var monstersStart = Array.FindIndex(lines, l => l == "monsters:");
        Assert.That(monstersStart, Is.GreaterThanOrEqualTo(0), "entities.yaml has no top-level 'monsters:' key.");
        var monstersEnd = lines.Length;
        for (var i = monstersStart + 1; i < lines.Length; i++)
        {
            if (Regex.IsMatch(lines[i], @"^[a-z_][a-z0-9_]*:"))
            {
                monstersEnd = i;
                break;
            }
        }

        var monsterIds = new HashSet<string>();
        for (var i = monstersStart + 1; i < monstersEnd; i++)
        {
            var m = Regex.Match(lines[i], @"^  (?<id>[a-z_][a-z0-9_]*):\s*$");
            if (m.Success)
                monsterIds.Add(m.Groups["id"].Value);
        }
        monsterIds.RemoveWhere(id => id.StartsWith("troll_probe_", StringComparison.Ordinal));

        Assert.That(monsterIds, Is.Not.Empty, "Failed to parse any monster ids from entities.yaml's monsters: block.");

        var pools = LoadPools();
        var speciesKeys = pools.Keys
            .Where(k => k.StartsWith("species_first_sight.", StringComparison.Ordinal))
            .Select(k => k["species_first_sight.".Length..])
            .ToList();

        foreach (var species in speciesKeys)
            Assert.That(monsterIds, Does.Contain(species), $"species_first_sight.{species} has no matching entities.yaml monster id.");
    }

    // ─── Anti-tell character tier (config/rubric/voice-anti-tell-lint.md) ──────
    // Hard-block: em-dash, en-dash, ellipsis glyph, markdown emphasis chars.
    // Three-period ellipses and hyphens are authored voice and must NOT be flagged.

    private static readonly Regex CharacterTierViolation =
        new("—|–|…|[*`_#]", RegexOptions.Compiled);

    [Test]
    public void AllLines_ContainNoAntiTellCharacterTierViolations()
    {
        var pools = LoadPools();
        var violations = new List<string>();

        foreach (var (key, lines) in pools)
        {
            foreach (var line in lines)
            {
                if (CharacterTierViolation.IsMatch(line))
                    violations.Add($"{key}: \"{line}\"");
            }
        }

        Assert.That(violations, Is.Empty,
            "Anti-tell character-tier hard-block violated:\n" + string.Join("\n", violations));
    }

    [Test]
    public void AntiTellCheck_CanaryFixture_EmDashFailsTheCheck()
    {
        // Canary: a check that has never fired is indistinguishable from one
        // that cannot fire. This fixture proves the regex actually catches an
        // em-dash rather than silently passing everything.
        const string fixtureLine = "Boss—don't.";
        Assert.That(CharacterTierViolation.IsMatch(fixtureLine), Is.True,
            "Canary fixture with an em-dash must fail the anti-tell check.");
    }
}
