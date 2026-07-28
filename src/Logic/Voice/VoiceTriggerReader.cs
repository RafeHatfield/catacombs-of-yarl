using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Voice;

/// <summary>
/// Derives voice trigger FAMILIES from what is observable at a turn commit (M1.5b trigger bus). Pure
/// logic — no Godot — so the family derivation is headlessly testable; the presentation layer owns only
/// the glue (calling this each <c>TurnCompleted</c> and firing <see cref="VoiceScheduler.TryDeliver"/>).
///
/// Edge-triggered where a sustained condition would otherwise spam: hp-critical fires once per descent
/// below the threshold (re-arms when HP recovers), first-sight fires once per species per run, and
/// possession fires once per entry. Trap and idle are per-event. The scheduler's cooldown + bags handle
/// the rest; this reader never draws randomness and never touches the gameplay Rng.
/// </summary>
public sealed class VoiceTriggerReader
{
    /// <summary>Home-body HP fraction at/below which the player's body is "critical".</summary>
    public const float HpCriticalFraction = 0.25f;

    private bool _wasHpCritical;
    private bool _wasPossessing;
    private readonly HashSet<string> _seenSpecies = new(StringComparer.Ordinal);

    /// <summary>Reset all edge state — called at the start of a new run (depth 1).</summary>
    public void Reset()
    {
        _wasHpCritical = false;
        _wasPossessing = false;
        _seenSpecies.Clear();
    }

    /// <summary>
    /// The trigger families raised by this committed turn, in a stable order. May be empty. The
    /// scheduler resolves priority/cooldown/bags across whatever is returned.
    /// </summary>
    public IReadOnlyList<string> Read(TurnResult result, GameState state)
    {
        var families = new List<string>();

        // hp_critical — edge-triggered on the home body dropping to/below the threshold (alive).
        var body = state.PlayerFighter;
        bool critical = body.Hp > 0 && body.MaxHp > 0 && (float)body.Hp / body.MaxHp <= HpCriticalFraction;
        if (critical && !_wasHpCritical) families.Add("hp_critical");
        _wasHpCritical = critical;

        // possession — edge-triggered on entering possession (control left the home body).
        bool possessing = !ReferenceEquals(state.ControlledEntity, state.Player);
        if (possessing && !_wasPossessing) families.Add("possession");
        _wasPossessing = possessing;

        // trap — the player's own body triggered a trap this turn.
        if (result.Events.Any(e => e is TrapTriggeredEvent t && t.TargetId == state.Player.Id))
            families.Add("trap");

        // idle — the player waited/skipped this turn.
        if (result.Events.Any(e => e is WaitEvent or SkipTurnEvent))
            families.Add("idle");

        // species_first_sight — a species entered the FOV for the first time this run.
        bool anyNewSpecies = false;
        foreach (var m in state.Monsters)
        {
            if (!state.Map.IsVisible(m.X, m.Y)) continue;
            var species = m.Get<SpeciesTag>()?.TypeId;
            if (species != null && _seenSpecies.Add(species)) anyNewSpecies = true;
        }
        if (anyNewSpecies) families.Add("species_first_sight");

        return families;
    }
}
