using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat.StatusEffects;

/// <summary>
/// Processes status effects for a single entity each turn.
/// Stateless — all state lives in the entity's components.
///
/// Turn lifecycle:
///   ProcessTurnStart → DOT ticks, HOT ticks, skip-turn checks (returns true if turn skipped)
///   ProcessTurnEnd   → decrement durations, remove expired effects, emit StatusExpiredEvent
///
/// Wire points:
///   TurnController.ResolveMonsterTurns / ResolvePlayerAction — call both methods per entity
///   CombatResolver.ResolveAttack — call OnDamageTaken on attack hits to wake Sleep
///   DungeonFloorBuilder.Build (carry-forward path) — call ClearAllEffects on player
/// </summary>
public static class StatusEffectProcessor
{
    // ─────────────────────────────────────────────────────────────────────────
    // Apply
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Apply an effect to an entity using the no-stack/refresh rule.
    /// If the entity already has this effect, refreshes duration to the maximum of
    /// the current remaining turns and the requested duration (no downgrade).
    /// If the entity does not have this effect, creates and attaches a new instance.
    /// Returns the (possibly existing) effect component.
    /// </summary>
    public static T ApplyEffect<T>(Entity entity, int duration) where T : class, IStatusEffect, new()
    {
        var existing = entity.Get<T>();
        if (existing != null)
        {
            // No-stack: take the longer of the two durations
            existing.RemainingTurns = Math.Max(existing.RemainingTurns, duration);
            return existing;
        }
        var effect = new T { RemainingTurns = duration };
        entity.Add(effect);
        return effect;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Turn Start (DOT, HOT, skip-turn checks)
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Process start-of-turn effects: DOT damage, HOT healing, and skip-turn determination.
    /// Returns true if the entity should skip its action this turn.
    ///
    /// SlowedEffect skip rule: odd-numbered turns are skipped (turnCount % 2 == 1).
    /// This matches PoC behavior where the slow effect gates every other turn.
    /// </summary>
    public static bool ProcessTurnStart(Entity entity, List<TurnEvent> events, int turnCount = 0)
    {
        var fighter = entity.Get<Fighter>();
        bool skipTurn = false;

        // ── DOT ticks ──────────────────────────────────────────────────────

        if (entity.Get<PoisonEffect>() is { } poison && fighter != null)
        {
            fighter.TakeDamage(poison.DamagePerTurn);
            events.Add(new DotDamageEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "poison",
                Damage = poison.DamagePerTurn,
            });
        }

        if (entity.Get<BurningEffect>() is { } burning && fighter != null)
        {
            fighter.TakeDamage(burning.DamagePerTurn);
            events.Add(new DotDamageEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "burning",
                Damage = burning.DamagePerTurn,
            });
        }

        if (entity.Get<PlagueEffect>() is { } plague && fighter != null)
        {
            fighter.TakeDamage(plague.DamagePerTurn);
            events.Add(new DotDamageEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "plague",
                Damage = plague.DamagePerTurn,
            });
        }

        // ── HOT ticks ──────────────────────────────────────────────────────

        if (entity.Get<RegenerationEffect>() is { } regen && fighter != null)
        {
            int actualHeal = fighter.Heal(regen.HealPerTurn);
            if (actualHeal > 0)
            {
                events.Add(new HotHealEvent
                {
                    ActorId = entity.Id,
                    EntityId = entity.Id,
                    EffectName = "regeneration",
                    Amount = actualHeal,
                });
            }
        }

        // ── Skip-turn checks ───────────────────────────────────────────────

        // ImmobilizedEffect: always skip
        if (entity.Has<ImmobilizedEffect>())
        {
            events.Add(new SkipTurnEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "immobilized",
            });
            skipTurn = true;
        }

        // SleepEffect: always skip (woken by attack damage via OnDamageTaken)
        if (entity.Has<SleepEffect>())
        {
            events.Add(new SkipTurnEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "sleep",
            });
            skipTurn = true;
        }

        // SlowedEffect: skip odd-numbered turns (turnCount % 2 == 1)
        // Even turns the entity acts normally; odd turns it loses its action.
        // Using the caller-provided turnCount so this is deterministic and testable.
        if (entity.Has<SlowedEffect>() && turnCount % 2 == 1)
        {
            events.Add(new SkipTurnEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "slowed",
            });
            skipTurn = true;
        }

        return skipTurn;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Turn End (duration decrement + expiry)
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Decrement RemainingTurns on all non-permanent effects.
    /// Effects that reach 0 are removed and emit StatusExpiredEvent.
    ///
    /// Uses GetAllComponents().OfType&lt;IStatusEffect&gt;() to enumerate all effects without
    /// a hardcoded list — new effects are automatically handled when they implement IStatusEffect.
    /// Snapshot the list first because Remove() mutates the component dictionary.
    /// </summary>
    public static void ProcessTurnEnd(Entity entity, List<TurnEvent> events)
    {
        // Snapshot: toList prevents mutation-during-iteration if Remove changes the dictionary.
        var effects = entity.GetAllComponents().OfType<IStatusEffect>().ToList();

        foreach (var effect in effects)
        {
            if (effect.IsPermanent) continue;

            effect.RemainingTurns--;

            if (effect.RemainingTurns <= 0)
            {
                // Remove using the concrete runtime type. GetAllComponents returns the concrete
                // instance so GetType() gives us the exact key used by the entity's dictionary.
                RemoveEffect(entity, effect);
                events.Add(new StatusExpiredEvent
                {
                    ActorId = entity.Id,
                    EntityId = entity.Id,
                    EffectName = effect.EffectName,
                    Reason = "duration",
                });
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Wake on Damage
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Called when an entity takes ATTACK damage (not DOT damage).
    /// Wakes SleepEffect: removes it and emits StatusExpiredEvent with reason "woke_on_damage".
    ///
    /// DOT damage does NOT call this — poisoned sleeping entities stay asleep.
    /// This is PoC-verified behavior.
    /// </summary>
    public static void OnDamageTaken(Entity entity, List<TurnEvent> events)
    {
        if (entity.Has<SleepEffect>())
        {
            entity.Remove<SleepEffect>();
            events.Add(new StatusExpiredEvent
            {
                ActorId = entity.Id,
                EntityId = entity.Id,
                EffectName = "sleep",
                Reason = "woke_on_damage",
            });
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Floor Transition
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Remove all status effects from an entity. Called when the player descends to a new floor.
    /// Policy: all effects clear on floor transition — no carry-over (simplest policy, avoids
    /// confusing persistent debuffs across dungeon floors).
    /// </summary>
    public static void ClearAllEffects(Entity entity)
    {
        var effects = entity.GetAllComponents().OfType<IStatusEffect>().ToList();
        foreach (var effect in effects)
            RemoveEffect(entity, effect);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Remove a status effect from an entity using its concrete runtime type.
    /// Entity.RemoveByType() accepts a Type key directly, so no per-type switch is needed.
    /// New effect types are handled automatically as long as they implement IStatusEffect —
    /// no registration required here.
    /// </summary>
    private static void RemoveEffect(Entity entity, IStatusEffect effect)
    {
        entity.RemoveByType(effect.GetType());
    }
}
