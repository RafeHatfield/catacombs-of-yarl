namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Attached to a monster entity when it dies and leaves a corpse.
/// The entity is transformed in-place: Fighter/AiComponent are stripped,
/// this component is added, BlocksMovement is set to false.
/// The entity remains in state.Monsters AND is added to state.Corpses.
/// </summary>
public sealed class CorpseComponent : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>YAML type key the monster was spawned from (e.g. "orc", "zombie").</summary>
    public string OriginalMonsterId { get; set; } = "";

    /// <summary>Display name of the monster at the time of death.</summary>
    public string OriginalName { get; set; } = "";

    /// <summary>Turn number when this entity died.</summary>
    public int DeathTurn { get; set; }

    /// <summary>Number of times this corpse has been raised. Starts at 0.</summary>
    public int RaiseCount { get; set; }

    /// <summary>Maximum number of times this corpse can be raised. Default 1.</summary>
    public int MaxRaises { get; set; } = 1;

    /// <summary>Prevents re-targeting. Set true after final consumption.</summary>
    public bool Consumed { get; set; }

    /// <summary>Display name of the last entity that raised this corpse. Null if never raised.</summary>
    public string? RaisedByName { get; set; }

    /// <summary>Current lifecycle state: Fresh, Spent, or Consumed.</summary>
    public CorpseState State { get; set; } = CorpseState.Fresh;

    /// <summary>
    /// Unique lineage identifier: "corpse_{x}_{y}_{turn}".
    /// Carried into RaisedFromCorpseTag to track raise chains.
    /// </summary>
    public string CorpseId { get; set; } = "";

    /// <summary>
    /// True when this corpse is eligible to be raised.
    /// Single predicate used by necromancer AI and spell resolver.
    /// </summary>
    public bool CanBeRaised => State == CorpseState.Fresh && RaiseCount < MaxRaises;
}
