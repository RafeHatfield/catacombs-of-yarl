using System.Collections.Generic;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Voice;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Voice;

/// <summary>
/// The M1.5b trigger bus derivation (pure logic — the Presentation glue just calls this each
/// TurnCompleted). Edge-triggered families fire once per condition-onset; per-event families fire on
/// their event; first-sight fires once per species.
/// </summary>
[TestFixture]
public class VoiceTriggerReaderTests
{
    private static Fighter Body(int hp) =>
        new(hp: hp, strength: 10, dexterity: 10, constitution: 10, accuracy: 5, evasion: 0, damageMin: 1, damageMax: 2);

    private static GameState State(out Entity player, out Entity monster)
    {
        var map = new GameMap(12, 12);
        for (int x = 0; x < 12; x++)
            for (int y = 0; y < 12; y++) map.SetTile(x, y, TileKind.Floor);

        player = new Entity(1, "Player", 5, 5, blocksMovement: true);
        player.Add(Body(100));
        map.RegisterEntity(player);

        monster = new Entity(2, "Orc", 6, 5, blocksMovement: true);
        monster.Add(new SpeciesTag("orc_grunt"));
        monster.Add(Body(30));

        return new GameState(player, new List<Entity> { monster }, map, new SeededRandom(1), turnLimit: 1000);
    }

    private static TurnResult Turn(params TurnEvent[] events) => new() { Events = new List<TurnEvent>(events) };

    [Test]
    public void HpCritical_EdgeTriggered_OncePerDescentBelowThreshold()
    {
        var reader = new VoiceTriggerReader();
        var state = State(out var player, out _);

        state.PlayerFighter.Hp = 20;   // 20/100 = 20% <= 25%
        Assert.That(reader.Read(Turn(), state), Does.Contain("hp_critical"));
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("hp_critical"), "sustained-critical must not re-fire.");

        state.PlayerFighter.Hp = 90;   // recover — re-arm
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("hp_critical"));
        state.PlayerFighter.Hp = 10;   // drop again
        Assert.That(reader.Read(Turn(), state), Does.Contain("hp_critical"), "a fresh descent re-fires.");
    }

    [Test]
    public void Possession_EdgeTriggered_OnEntry()
    {
        var reader = new VoiceTriggerReader();
        var state = State(out var player, out var monster);

        // Not possessing yet.
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("possession"));

        monster.Add(new PossessionEffect
        {
            RemainingTurns = 50, PossessorEntityId = player.Id, DrainPerTurn = 0,
            Source = PossessionSource.PlayerInitiated, EnteredTurn = 1,
        });
        Assume.That(state.ControlledEntity, Is.SameAs(monster));
        Assert.That(reader.Read(Turn(), state), Does.Contain("possession"));
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("possession"), "still-possessing must not re-fire.");
    }

    [Test]
    public void Trap_FiresOnPlayerTargetedTrapEvent_NotOthers()
    {
        var reader = new VoiceTriggerReader();
        var state = State(out var player, out var monster);

        Assert.That(reader.Read(Turn(new TrapTriggeredEvent { TargetId = monster.Id }), state),
            Does.Not.Contain("trap"), "a trap that hit a monster is not the player's.");
        Assert.That(reader.Read(Turn(new TrapTriggeredEvent { TargetId = player.Id }), state),
            Does.Contain("trap"));
    }

    [Test]
    public void Idle_FiresOnWaitOrSkip()
    {
        var reader = new VoiceTriggerReader();
        var state = State(out _, out _);
        Assert.That(reader.Read(Turn(new WaitEvent()), state), Does.Contain("idle"));
    }

    [Test]
    public void FirstSight_FiresOncePerVisibleSpecies()
    {
        var reader = new VoiceTriggerReader();
        var state = State(out _, out var monster);

        // Out of FOV — no first sight.
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("species_first_sight"));

        state.Map.SetVisible(monster.X, monster.Y);
        Assert.That(reader.Read(Turn(), state), Does.Contain("species_first_sight"));
        Assert.That(reader.Read(Turn(), state), Does.Not.Contain("species_first_sight"),
            "a species already seen this run does not re-fire.");

        reader.Reset();   // new run
        Assert.That(reader.Read(Turn(), state), Does.Contain("species_first_sight"),
            "reset re-arms first-sight for a new run.");
    }
}
