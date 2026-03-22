using CatacombsOfYarl.Logic.Content;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Content;

[TestFixture]
public class ContentLoaderTests
{
    private const string TestYaml = @"
monsters:
  orc:
    stats:
      hp: 28
      power: 0
      defense: 0
      xp: 35
      damage_min: 4
      damage_max: 6
      strength: 14
      dexterity: 10
      constitution: 12
      accuracy: 4
      evasion: 1
    char: ""o""
    color: [63, 127, 63]
    ai_type: ""basic""
    blocks: true
    faction: ""orc""
    tags: [""humanoid"", ""living""]
    etp_base: 27

  orc_grunt:
    name: ""Orc""
    extends: orc

  orc_brute:
    extends: orc
    stats:
      hp: 42
      damage_min: 5
      damage_max: 8
      strength: 16
      xp: 55
    char: ""O""
    color: [90, 160, 90]
    etp_base: 45
    tags: [""humanoid"", ""living"", ""brute""]

  zombie:
    stats:
      hp: 24
      xp: 30
      damage_min: 3
      damage_max: 6
      strength: 12
      dexterity: 6
      constitution: 14
      accuracy: 1
      evasion: 0
    char: ""z""
    color: [128, 128, 96]
    blocks: true
    faction: ""undead""
    tags: [""undead"", ""zombie""]
    damage_resistance: ""piercing""
    etp_base: 31
";

    private Dictionary<string, MonsterDefinition> _monsters = null!;

    [OneTimeSetUp]
    public void LoadMonsters()
    {
        var loader = new ContentLoader();
        _monsters = loader.LoadMonsters(TestYaml);
    }

    [Test]
    public void LoadsAllMonsters()
    {
        Assert.That(_monsters, Has.Count.EqualTo(4));
        Assert.That(_monsters.ContainsKey("orc"), Is.True);
        Assert.That(_monsters.ContainsKey("orc_grunt"), Is.True);
        Assert.That(_monsters.ContainsKey("orc_brute"), Is.True);
        Assert.That(_monsters.ContainsKey("zombie"), Is.True);
    }

    [Test]
    public void BaseOrc_Stats()
    {
        var orc = _monsters["orc"];
        Assert.That(orc.Stats!.Hp, Is.EqualTo(28));
        Assert.That(orc.Stats.Strength, Is.EqualTo(14));
        Assert.That(orc.Stats.DamageMin, Is.EqualTo(4));
        Assert.That(orc.Stats.DamageMax, Is.EqualTo(6));
        Assert.That(orc.Stats.Accuracy, Is.EqualTo(4));
        Assert.That(orc.Stats.Evasion, Is.EqualTo(1));
        Assert.That(orc.Stats.Xp, Is.EqualTo(35));
    }

    [Test]
    public void BaseOrc_Fields()
    {
        var orc = _monsters["orc"];
        Assert.That(orc.Char, Is.EqualTo("o"));
        Assert.That(orc.Color, Is.EqualTo(new[] { 63, 127, 63 }));
        Assert.That(orc.Faction, Is.EqualTo("orc"));
        Assert.That(orc.EtpBase, Is.EqualTo(27));
        Assert.That(orc.Tags, Contains.Item("humanoid"));
    }

    [Test]
    public void OrcGrunt_InheritsFromOrc()
    {
        var grunt = _monsters["orc_grunt"];

        // Explicit name
        Assert.That(grunt.Name, Is.EqualTo("Orc"));

        // Inherited stats
        Assert.That(grunt.Stats!.Hp, Is.EqualTo(28));
        Assert.That(grunt.Stats.Strength, Is.EqualTo(14));
        Assert.That(grunt.Stats.Accuracy, Is.EqualTo(4));

        // Inherited fields
        Assert.That(grunt.Char, Is.EqualTo("o"));
        Assert.That(grunt.Faction, Is.EqualTo("orc"));
        Assert.That(grunt.EtpBase, Is.EqualTo(27));

        // Inheritance resolved
        Assert.That(grunt.Extends, Is.Null);
    }

    [Test]
    public void OrcBrute_OverridesParentStats()
    {
        var brute = _monsters["orc_brute"];

        // Overridden stats
        Assert.That(brute.Stats!.Hp, Is.EqualTo(42));
        Assert.That(brute.Stats.DamageMin, Is.EqualTo(5));
        Assert.That(brute.Stats.DamageMax, Is.EqualTo(8));
        Assert.That(brute.Stats.Strength, Is.EqualTo(16));
        Assert.That(brute.Stats.Xp, Is.EqualTo(55));

        // Inherited from parent (not overridden)
        Assert.That(brute.Stats.Constitution, Is.EqualTo(12));
        Assert.That(brute.Stats.Accuracy, Is.EqualTo(4));
        Assert.That(brute.Stats.Evasion, Is.EqualTo(1));

        // Overridden fields
        Assert.That(brute.Char, Is.EqualTo("O"));
        Assert.That(brute.EtpBase, Is.EqualTo(45));

        // Inherited faction
        Assert.That(brute.Faction, Is.EqualTo("orc"));
    }

    [Test]
    public void Zombie_IndependentDefinition()
    {
        var zombie = _monsters["zombie"];

        Assert.That(zombie.Stats!.Hp, Is.EqualTo(24));
        Assert.That(zombie.Stats.Dexterity, Is.EqualTo(6));
        Assert.That(zombie.Stats.Constitution, Is.EqualTo(14));
        Assert.That(zombie.Stats.Accuracy, Is.EqualTo(1));
        Assert.That(zombie.Stats.Evasion, Is.EqualTo(0));
        Assert.That(zombie.Faction, Is.EqualTo("undead"));
        Assert.That(zombie.DamageResistance, Is.EqualTo("piercing"));
        Assert.That(zombie.Tags, Contains.Item("zombie"));
    }

    [Test]
    public void Name_DefaultsToTitleCasedId()
    {
        var brute = _monsters["orc_brute"];
        Assert.That(brute.Name, Is.EqualTo("Orc Brute"));
    }

    [Test]
    public void CircularInheritance_Throws()
    {
        const string circular = @"
monsters:
  a:
    extends: b
    stats:
      hp: 10
    char: ""a""
  b:
    extends: a
    stats:
      hp: 20
    char: ""b""
";
        var loader = new ContentLoader();
        Assert.Throws<InvalidOperationException>(() => loader.LoadMonsters(circular));
    }

    [Test]
    public void EmptyYaml_ReturnsEmpty()
    {
        var loader = new ContentLoader();
        var result = loader.LoadMonsters("monsters: {}");
        Assert.That(result, Is.Empty);
    }
}
