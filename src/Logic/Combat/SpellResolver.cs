using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Executes spell effects. Single source of truth for spell logic.
///
/// Entry point: Resolve() dispatches on SpellId to a private handler.
/// No virtual dispatch, no inheritance — one switch, data-driven.
/// All numeric parameters (damage, radius, range) come from SpellEffect,
/// not hardcoded in the resolver, so YAML can tune them without C# changes.
///
/// PoC reference: ~/development/rlike/spells/spell_executor.py
/// </summary>
public static class SpellResolver
{
    /// <summary>
    /// Resolve a spell. Called by TurnController when a scroll/wand is used.
    /// Returns all TurnEvents produced (SpellEvent, DamageEvents, MapRevealEvent, etc.).
    ///
    /// targetEntityId: for AutoClosest, the caller pre-resolves the closest monster and passes it.
    ///                 For Self/AoeSelf, null — the resolver uses caster position.
    /// </summary>
    public static List<TurnEvent> Resolve(
        Entity caster,
        SpellEffect spell,
        GameState state,
        int? targetEntityId = null,
        int? targetX = null,
        int? targetY = null)
    {
        return spell.SpellId switch
        {
            "lightning"       => ResolveLightning(caster, spell, state, targetEntityId),
            "earthquake"      => ResolveEarthquake(caster, spell, state),
            "light"           => ResolveLight(caster, spell, state),
            "magic_mapping"   => ResolveMagicMapping(caster, spell, state),
            "detect_monsters" => ResolveDetectMonsters(caster, spell, state),
            "enhance_weapon"  => ResolveEnhanceWeapon(caster, spell, state),
            "enhance_armor"   => ResolveEnhanceArmor(caster, spell, state),
            // ── Phase 3: Single-target status effect spells ──────────────────
            // ConfusedEffect removed — DisorientationEffect is canonical for confused movement.
            "confusion"   => ResolveStatusEffect<DisorientationEffect>(caster, spell, state, targetEntityId,
                                statusName: "disoriented", duration: spell.Duration > 0 ? spell.Duration : 10,
                                applyEffect: (e, d) => e.GetOrAdd<DisorientationEffect>().RemainingTurns = d),
            "slow"        => ResolveStatusEffect<SlowedEffect>(caster, spell, state, targetEntityId,
                                statusName: "slowed", duration: spell.Duration > 0 ? spell.Duration : 10,
                                applyEffect: (e, d) => e.GetOrAdd<SlowedEffect>().RemainingTurns = d),
            "glue"        => ResolveStatusEffect<ImmobilizedEffect>(caster, spell, state, targetEntityId,
                                statusName: "immobilized", duration: spell.Duration > 0 ? spell.Duration : 5,
                                applyEffect: (e, d) => e.GetOrAdd<ImmobilizedEffect>().RemainingTurns = d),
            "rage"        => ResolveStatusEffect<EnragedEffect>(caster, spell, state, targetEntityId,
                                statusName: "enraged", duration: spell.Duration > 0 ? spell.Duration : 8,
                                applyEffect: (e, d) => e.GetOrAdd<EnragedEffect>().RemainingTurns = d),
            "yo_mama"     => ResolveYoMama(caster, spell, state, targetEntityId),
            "disarm"      => ResolveStatusEffect<DisarmedEffect>(caster, spell, state, targetEntityId,
                                statusName: "disarmed", duration: spell.Duration > 0 ? spell.Duration : 3,
                                applyEffect: (e, d) => e.GetOrAdd<DisarmedEffect>().RemainingTurns = d),
            "plague"      => ResolvePlague(caster, spell, state, targetEntityId),
            "aggravation" => ResolveAggravation(caster, spell, state, targetEntityId),
            // ── Phase 3: AoE / Self / Location spells ───────────────────────────────
            "fear"        => ResolveFear(caster, spell, state),
            "invisibility"=> ResolveSelfStatusEffect<InvisibilityEffect>(caster, spell, state,
                                statusName: "invisibility", duration: spell.Duration > 0 ? spell.Duration : 30,
                                applyEffect: (e, d) => e.GetOrAdd<InvisibilityEffect>().RemainingTurns = d),
            "shield"      => ResolveSelfStatusEffect<ShieldEffect>(caster, spell, state,
                                statusName: "shield", duration: spell.Duration > 0 ? spell.Duration : 10,
                                applyEffect: (e, d) => e.GetOrAdd<ShieldEffect>().RemainingTurns = d),
            // HasteEffect removed (not in PoC) — map "haste" spell to SpeedEffect for now.
            // SpeedEffect is inert until the bonus attack system lands (see SpeedEffect.cs TODO).
            "haste"       => ResolveSelfStatusEffect<SpeedEffect>(caster, spell, state,
                                statusName: "speed", duration: spell.Duration > 0 ? spell.Duration : 20,
                                applyEffect: (e, d) => e.GetOrAdd<SpeedEffect>().RemainingTurns = d),
            "silence"     => ResolveStatusEffect<SilencedEffect>(caster, spell, state, targetEntityId,
                                statusName: "silenced", duration: spell.Duration > 0 ? spell.Duration : 3,
                                applyEffect: (e, d) => e.GetOrAdd<SilencedEffect>().RemainingTurns = d),
            "teleport"    => ResolveTeleport(caster, spell, state, targetX, targetY),
            "blink"       => ResolveBlink(caster, spell, state, targetX, targetY),
            "fireball"    => ResolveFireball(caster, spell, state, targetX, targetY),
            // Stub: raise_dead requires corpse lifecycle (plan_monster_specials).
            // Location targeting is wired; the handler returns "no corpse found" until
            // corpse entities exist on the map.
            "raise_dead"  => ResolveRaiseDead(caster, spell, state, targetX, targetY),
            // dragon_fart: cone targeting deferred — stub as single-target sleep for now.
            // Flavor: "falls into a stupor" → SleepEffect is the correct effect, not silence.
            "dragon_fart" => ResolveStatusEffect<SleepEffect>(caster, spell, state, targetEntityId,
                                statusName: "sleep", duration: spell.Duration > 0 ? spell.Duration : 3,
                                applyEffect: (e, d) => e.GetOrAdd<SleepEffect>().RemainingTurns = d),
            _ => [new SpellEvent
            {
                ActorId = caster.Id,
                SpellId = spell.SpellId,
                SpellName = spell.SpellId,
                Success = false,
            }],
        };
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Lightning — AutoClosest: 40 dmg to the nearest visible enemy, range 5
    // PoC: TargetingType.SINGLE_ENEMY + _cast_auto_target_spell
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveLightning(
        Entity caster, SpellEffect spell, GameState state, int? targetEntityId)
    {
        var events = new List<TurnEvent>();

        // If the caller already resolved the target, use it; otherwise auto-find.
        Entity? target = null;
        if (targetEntityId.HasValue)
        {
            target = state.Monsters.FirstOrDefault(m => m.Id == targetEntityId.Value && m.Require<Fighter>().IsAlive);
        }
        else
        {
            target = FindClosestVisibleEnemy(caster, state, spell.Range > 0 ? spell.Range : 5);
        }

        if (target == null)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id,
                SpellId = spell.SpellId,
                SpellName = "Lightning",
                Success = false,
            });
            return events;
        }

        int damage = spell.Damage > 0 ? state.Rng.Next(spell.Damage / 2, spell.Damage + 1) : state.Rng.Next(10, 21);
        var targetFighter = target.Require<Fighter>();
        targetFighter.TakeDamage(damage);
        bool killed = !targetFighter.IsAlive;

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Lightning",
            TargetId = target.Id,
            Damage = damage,
            AffectedIds = [target.Id],
            Success = true,
        });

        if (killed)
        {
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = caster.Id });
        }

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Earthquake — AoeSelf: 20 dmg to ALL visible enemies within radius 3
    // PoC: AoE centered on caster, no self-damage
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveEarthquake(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();
        int radius = spell.Radius > 0 ? spell.Radius : 3;
        int baseDamage = spell.Damage > 0 ? spell.Damage : 20;

        var affected = new List<Entity>();
        var affectedIds = new List<int>();

        foreach (var monster in state.AliveMonsters)
        {
            // Check within radius (Chebyshev distance for consistent roguelike feel)
            int dist = caster.ChebyshevDistanceTo(monster.X, monster.Y);
            if (dist > radius) continue;

            // Earthquake affects visible enemies only (player can't hit what they can't see).
            // In scenario mode (IsDungeonMode=false) all tiles are pre-revealed, so skip
            // the visibility check — it always returns false for unlit scenario maps.
            if (state.IsDungeonMode && !state.Map.IsVisible(monster.X, monster.Y)) continue;

            affected.Add(monster);
        }

        // Roll damage once per monster (variable, not the same roll for all)
        foreach (var target in affected)
        {
            int damage = state.Rng.Next(baseDamage / 2, baseDamage + 1);
            var targetFighter = target.Require<Fighter>();
            targetFighter.TakeDamage(damage);
            bool killed = !targetFighter.IsAlive;

            affectedIds.Add(target.Id);

            if (killed)
            {
                events.Add(new DeathEvent { ActorId = target.Id, KillerId = caster.Id });
            }
        }

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Earthquake",
            Damage = baseDamage,
            AffectedIds = affectedIds,
            Success = affectedIds.Count > 0,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Light — Self: marks all currently-visible tiles as explored (permanent)
    // PoC: reveals current room's tiles in FOV
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveLight(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();

        // In dungeon mode, all currently visible tiles are marked explored.
        // In scenario mode (no FOV), RevealAll is already called — this is a no-op.
        // The effect is "you permanently know every tile you can see right now,"
        // which is meaningful in dark areas that would otherwise un-fog.
        if (state.IsDungeonMode)
        {
            // GameMap.SetVisible already marks tiles as explored. The Light scroll's
            // effect is to mark visible tiles explored even if FOV expires this turn.
            // Since SetVisible already does this, the map state is already correct —
            // the event is what signals the UI to show the "light scroll" flash.
        }

        events.Add(new MapRevealEvent
        {
            ActorId = caster.Id,
            RevealType = "fov",
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Magic Mapping — Self: marks ALL tiles on the floor as explored
    // PoC: reveals entire floor immediately
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveMagicMapping(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();

        // Mark every tile on the current floor as explored (but NOT visible this turn).
        // Explored = shown on minimap / remembered. Visible = currently in FOV.
        // RevealAll sets both, but magic mapping only sets explored, not visible.
        // We need a targeted "set explored" loop — GameMap exposes SetExplored per-tile.
        // Use RevealAll as it's the available API — it sets both explored and visible,
        // which is consistent with PoC behavior (magic map shows the whole floor).
        state.Map.RevealAll();

        events.Add(new MapRevealEvent
        {
            ActorId = caster.Id,
            RevealType = "full",
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Detect Monsters — Self: broadcasts all monster positions
    // PoC: all monsters briefly visible through walls for 20 turns
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveDetectMonsters(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();
        int duration = spell.Duration > 0 ? spell.Duration : 20;

        var positions = state.AliveMonsters
            .Select(m => (m.X, m.Y, m.Id))
            .ToList();

        events.Add(new DetectMonstersEvent
        {
            ActorId = caster.Id,
            MonsterPositions = positions,
            Duration = duration,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Enhance Weapon — Self: +1 min / +2 max dmg to equipped main-hand weapon
    // PoC: enhance_weapon scroll adds +1 to weapon damage range
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveEnhanceWeapon(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();
        var equip = caster.Get<Equipment>();
        var weapon = equip?.MainHand?.Get<Equippable>();

        if (weapon == null || !weapon.IsWeapon)
        {
            // Scroll is wasted — no weapon equipped. Still consumed.
            events.Add(new SpellEvent
            {
                ActorId = caster.Id,
                SpellId = spell.SpellId,
                SpellName = "Enhance Weapon",
                Success = false,
            });
            return events;
        }

        // +1 DamageMin, +2 DamageMax (PoC: "enhance" means a meaningful bump, not just +1)
        weapon.DamageMin += 1;
        weapon.DamageMax += 2;

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Enhance Weapon",
            Success = true,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Enhance Armor — Self: +1 AC to a random equipped armor piece
    // PoC: picks a random equipped armor slot and bumps its ArmorClassBonus
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveEnhanceArmor(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();
        var equip = caster.Get<Equipment>();

        // Collect all equipped armor pieces (slots other than MainHand weapon)
        var armorPieces = new List<Equippable>();
        if (equip != null)
        {
            var candidates = new[] { equip.OffHand, equip.Head, equip.Chest, equip.Feet };
            foreach (var slot in candidates)
            {
                var eq = slot?.Get<Equippable>();
                if (eq != null && !eq.IsWeapon)
                    armorPieces.Add(eq);
            }
        }

        if (armorPieces.Count == 0)
        {
            // No armor equipped — scroll wasted
            events.Add(new SpellEvent
            {
                ActorId = caster.Id,
                SpellId = spell.SpellId,
                SpellName = "Enhance Armor",
                Success = false,
            });
            return events;
        }

        // Pick a random armor piece to enhance
        var chosen = armorPieces[state.Rng.Next(armorPieces.Count)];
        chosen.ArmorClassBonus += 1;

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Enhance Armor",
            Success = true,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Helpers
    // ──────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Find the closest alive monster visible to the caster within the given range.
    /// Uses Euclidean distance (matches PoC distance_to behavior).
    /// Returns null if no visible enemies are in range.
    /// </summary>
    private static Entity? FindClosestVisibleEnemy(Entity caster, GameState state, int maxRange)
    {
        Entity? closest = null;
        double closestDist = maxRange + 1.0; // exclusive upper bound

        foreach (var monster in state.AliveMonsters)
        {
            // In dungeon mode, check FOV visibility. In scenario mode (no FOV), all tiles visible.
            if (state.IsDungeonMode && !state.Map.IsVisible(monster.X, monster.Y))
                continue;

            double dist = caster.DistanceTo(monster.X, monster.Y);
            if (dist < closestDist)
            {
                closest = monster;
                closestDist = dist;
            }
        }

        return closest;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Phase 3: Single-target status effect spells
    //
    // All follow the same pattern:
    //   1. Look up target by targetEntityId (provided by UI after player taps a monster).
    //   2. Validate it's alive and in range.
    //   3. Apply the status effect component.
    //   4. Emit SpellEvent with StatusApplied.
    //
    // The targeting UI (Phase 3 presentation work) validates range before creating the
    // CastSpell action, so range validation here is a defense-in-depth check.
    // ──────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Generic single-target status effect resolver.
    /// Shared by confusion, slow, glue, rage, disarm — all follow the same pattern.
    /// applyEffect receives (targetEntity, duration) to apply the status component.
    /// </summary>
    private static List<TurnEvent> ResolveStatusEffect<TEffect>(
        Entity caster, SpellEffect spell, GameState state,
        int? targetEntityId, string statusName, int duration,
        Action<Entity, int> applyEffect)
        where TEffect : class, CatacombsOfYarl.Logic.ECS.IComponent
    {
        var events = new List<TurnEvent>();
        var target = FindTargetById(state, targetEntityId, spell.Range > 0 ? spell.Range : 8, caster);

        if (target == null)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId,
                SpellName = statusName, Success = false,
            });
            return events;
        }

        applyEffect(target, duration);

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = statusName,
            TargetId = target.Id,
            AffectedIds = [target.Id],
            Success = true,
            StatusApplied = statusName,
            StatusDuration = duration,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Yo Mama — SingleTarget: apply permanent TauntedEffect targeting the CASTER
    // PoC: target yells insult, ALL hostiles attack them (yo_mama_scroll)
    // Effect: the targeted monster is taunted into attacking the caster
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveYoMama(
        Entity caster, SpellEffect spell, GameState state, int? targetEntityId)
    {
        var events = new List<TurnEvent>();
        var target = FindTargetById(state, targetEntityId, spell.Range > 0 ? spell.Range : 10, caster);

        if (target == null)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId,
                SpellName = "Yo Mama", Success = false,
            });
            return events;
        }

        // Target becomes permanently fixated on the caster (e.g., the player taunted an orc)
        var effect = target.GetOrAdd<TauntedEffect>();
        effect.TauntTargetId = caster.Id;
        effect.RemainingTurns = -1; // permanent

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Yo Mama",
            TargetId = target.Id,
            AffectedIds = [target.Id],
            Success = true,
            StatusApplied = "taunted",
            StatusDuration = -1, // permanent
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Plague — SingleTarget: infect corporeal target with 1 dmg/turn for 20 turns
    // PoC: plague_scroll — only works on living/corporeal creatures
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolvePlague(
        Entity caster, SpellEffect spell, GameState state, int? targetEntityId)
    {
        var events = new List<TurnEvent>();
        var target = FindTargetById(state, targetEntityId, spell.Range > 0 ? spell.Range : 8, caster);

        if (target == null)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId,
                SpellName = "Plague", Success = false,
            });
            return events;
        }

        // Plague only affects corporeal creatures — check tags.
        // In scenario mode (no MonsterDefinition lookup), we treat all monsters as corporeal
        // unless they have an "undead" tag that implies non-corporeal (skeletons, ghosts).
        // The tag check uses the PoC convention: "corporeal_flesh" tag = valid target.
        // Fallback: check AiComponent tags if present; otherwise assume corporeal.
        bool isCorporeal = IsCorporeal(target, state);
        if (!isCorporeal)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id,
                SpellId = spell.SpellId,
                SpellName = "Plague",
                TargetId = target.Id,
                Success = false,
                StatusApplied = "",
                StatusDuration = 0,
            });
            return events;
        }

        int duration = spell.Duration > 0 ? spell.Duration : 20;
        int dmgPerTurn = 1;

        var effect = target.GetOrAdd<PlagueEffect>();
        effect.RemainingTurns = duration;
        effect.DamagePerTurn = dmgPerTurn;

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Plague",
            TargetId = target.Id,
            AffectedIds = [target.Id],
            Success = true,
            StatusApplied = "plague",
            StatusDuration = duration,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Aggravation — SingleTarget: target permanently aggros against their own faction
    // PoC: aggravation_scroll — incites monster to attack a faction (usually their own)
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveAggravation(
        Entity caster, SpellEffect spell, GameState state, int? targetEntityId)
    {
        var events = new List<TurnEvent>();
        var target = FindTargetById(state, targetEntityId, spell.Range > 0 ? spell.Range : 10, caster);

        if (target == null)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId,
                SpellName = "Aggravation", Success = false,
            });
            return events;
        }

        // Determine the target's faction from AiComponent; default to "" if unknown.
        // The aggravated monster attacks all members of its own faction (e.g., an orc
        // aggravated against "orc" faction will attack other orcs).
        var ai = target.Get<CatacombsOfYarl.Logic.ECS.AiComponent>();
        string targetFaction = ai?.Faction ?? "";

        var effect = target.GetOrAdd<AggravatedEffect>();
        effect.TargetFaction = targetFaction;
        effect.RemainingTurns = -1; // permanent

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Aggravation",
            TargetId = target.Id,
            AffectedIds = [target.Id],
            Success = true,
            StatusApplied = "aggravated",
            StatusDuration = -1, // permanent
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Fear — AoeSelf: apply FearEffect to all visible monsters within radius
    // PoC: fear.targeting = AOE, radius = 10, duration = 15, no target required
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveFear(Entity caster, SpellEffect spell, GameState state)
    {
        var events = new List<TurnEvent>();
        int radius = spell.Radius > 0 ? spell.Radius : 10;
        int duration = spell.Duration > 0 ? spell.Duration : 15;
        var affectedIds = new List<int>();

        foreach (var monster in state.AliveMonsters)
        {
            double dist = caster.DistanceTo(monster.X, monster.Y);
            if (dist > radius) continue;

            // Scenario mode (no FOV): affect all in radius. Dungeon mode: visible only.
            if (state.IsDungeonMode && !state.Map.IsVisible(monster.X, monster.Y)) continue;

            monster.GetOrAdd<FearEffect>().RemainingTurns = duration;
            affectedIds.Add(monster.Id);

            events.Add(new StatusAppliedEvent
            {
                ActorId = caster.Id,
                TargetId = monster.Id,
                EffectName = "fear",
                Duration = duration,
            });
        }

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Fear",
            AffectedIds = affectedIds,
            Success = affectedIds.Count > 0,
            StatusApplied = "fear",
            StatusDuration = duration,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Self status effect — shared by invisibility, shield, haste
    // Applies the effect to the CASTER, not a targeted enemy.
    // Identical to ResolveStatusEffect but operates on the caster instead of a target.
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveSelfStatusEffect<TEffect>(
        Entity caster, SpellEffect spell, GameState state,
        string statusName, int duration,
        Action<Entity, int> applyEffect)
        where TEffect : class, IComponent
    {
        applyEffect(caster, duration);

        return [new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = statusName,
            Success = true,
            StatusApplied = statusName,
            StatusDuration = duration,
        }];
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Teleport — Location: move caster to target tile; 10% misfire → random tile
    // PoC: teleport.targeting = LOCATION, max_range = 20, misfire_chance = 0.10
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveTeleport(
        Entity caster, SpellEffect spell, GameState state, int? targetX, int? targetY)
    {
        var events = new List<TurnEvent>();
        double misfireChance = spell.MisfireChance > 0 ? spell.MisfireChance : 0.10;
        int fromX = caster.X, fromY = caster.Y;

        bool misfire = state.Rng.NextDouble() < misfireChance;

        int destX, destY;
        if (misfire || !targetX.HasValue || !targetY.HasValue
            || !state.Map.IsWalkable(targetX.Value, targetY.Value))
        {
            // Misfire or no valid target: pick a random walkable tile
            var fallback = FindRandomWalkableTile(state, state.Rng);
            destX = fallback.X;
            destY = fallback.Y;
        }
        else
        {
            destX = targetX.Value;
            destY = targetY.Value;
        }

        caster.X = destX;
        caster.Y = destY;

        // On misfire: apply DisorientationEffect for 3 turns.
        // PoC: misfire = disorienting experience of landing somewhere unexpected.
        // Kept short (3 turns) so it's punishing but not crippling.
        if (misfire)
        {
            caster.GetOrAdd<DisorientationEffect>().RemainingTurns = 3;
        }

        events.Add(new TeleportEvent
        {
            ActorId = caster.Id,
            EntityId = caster.Id,
            FromX = fromX,
            FromY = fromY,
            ToX = destX,
            ToY = destY,
            Misfire = misfire,
        });

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Teleport",
            Success = true,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Blink — Location: short-range teleport, no misfire chance
    // PoC: blink.targeting = LOCATION, max_range = 5
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveBlink(
        Entity caster, SpellEffect spell, GameState state, int? targetX, int? targetY)
    {
        var events = new List<TurnEvent>();
        int maxRange = spell.Range > 0 ? spell.Range : 5;
        int fromX = caster.X, fromY = caster.Y;

        if (!targetX.HasValue || !targetY.HasValue || !state.Map.IsWalkable(targetX.Value, targetY.Value))
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId, SpellName = "Blink", Success = false,
            });
            return events;
        }

        double dist = caster.DistanceTo(targetX.Value, targetY.Value);
        if (dist > maxRange)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId, SpellName = "Blink", Success = false,
            });
            return events;
        }

        caster.X = targetX.Value;
        caster.Y = targetY.Value;

        events.Add(new TeleportEvent
        {
            ActorId = caster.Id,
            EntityId = caster.Id,
            FromX = fromX,
            FromY = fromY,
            ToX = targetX.Value,
            ToY = targetY.Value,
            Misfire = false,
        });

        events.Add(new SpellEvent
        {
            ActorId = caster.Id, SpellId = spell.SpellId, SpellName = "Blink", Success = true,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Fireball — Location AoE: 25 damage, radius 3, at target location
    // PoC: fireball.damage = "3d6" (~10.5 avg), radius = 3, max_range = 10
    // Plan spec uses flat 25 damage — YAML can tune via damage field.
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveFireball(
        Entity caster, SpellEffect spell, GameState state, int? targetX, int? targetY)
    {
        var events = new List<TurnEvent>();
        int radius = spell.Radius > 0 ? spell.Radius : 3;
        int baseDamage = spell.Damage > 0 ? spell.Damage : 25;

        if (!targetX.HasValue || !targetY.HasValue)
        {
            events.Add(new SpellEvent
            {
                ActorId = caster.Id, SpellId = spell.SpellId, SpellName = "Fireball", Success = false,
            });
            return events;
        }

        int cx = targetX.Value, cy = targetY.Value;
        var affectedIds = new List<int>();

        foreach (var monster in state.AliveMonsters)
        {
            // Chebyshev distance from explosion center (same as Earthquake for consistency)
            int dist = Math.Max(Math.Abs(monster.X - cx), Math.Abs(monster.Y - cy));
            if (dist > radius) continue;

            int damage = state.Rng.Next(baseDamage / 2, baseDamage + 1);
            var targetFighter = monster.Require<Fighter>();
            targetFighter.TakeDamage(damage);
            bool killed = !targetFighter.IsAlive;
            affectedIds.Add(monster.Id);

            if (killed)
                events.Add(new DeathEvent { ActorId = monster.Id, KillerId = caster.Id });
        }

        events.Add(new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Fireball",
            Damage = baseDamage,
            AffectedIds = affectedIds,
            Success = true,
        });

        return events;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Raise Dead — Location: stub. Resurrect a corpse as a mindless zombie.
    // PoC: raise_dead_scroll — requires corpse entities at target location.
    // Corpse lifecycle is part of plan_monster_specials. Until that system lands,
    // this always returns "no valid corpse found" (scroll is consumed, nothing happens).
    // ──────────────────────────────────────────────────────────────────────────

    private static List<TurnEvent> ResolveRaiseDead(
        Entity caster, SpellEffect spell, GameState state, int? targetX, int? targetY)
    {
        // TODO: When plan_monster_specials adds corpse entities, check state.Corpses
        // for a corpse at (targetX, targetY) within spell.Range, then create a zombie.
        // For now: scroll is consumed (consumed by TurnController before we get here)
        // but no effect is produced. Return a failed SpellEvent to communicate the no-op.
        return [new SpellEvent
        {
            ActorId = caster.Id,
            SpellId = spell.SpellId,
            SpellName = "Raise Dead",
            Success = false, // No corpse system yet — always fails gracefully
        }];
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Phase 3 Helpers
    // ──────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Find a target monster by entity ID, validating it's alive and within range.
    /// If targetEntityId is null, returns null (single-target spells require an explicit target).
    /// Range uses Euclidean distance (matches PoC distance_to).
    /// </summary>
    private static Entity? FindTargetById(GameState state, int? targetEntityId, double maxRange, Entity caster)
    {
        if (!targetEntityId.HasValue) return null;

        var target = state.Monsters.FirstOrDefault(m =>
            m.Id == targetEntityId.Value && m.Require<Fighter>().IsAlive);
        if (target == null) return null;

        // Validate range
        if (maxRange > 0 && caster.DistanceTo(target.X, target.Y) > maxRange)
            return null;

        return target;
    }

    /// <summary>
    /// Check whether a target entity is corporeal (flesh-and-blood, susceptible to plague).
    /// Non-corporeal: skeletons, ghosts, constructs.
    /// Corporeal: orcs, zombies, slimes, most living creatures.
    ///
    /// Checks AiComponent.Tags for "undead_bone" or "construct" which marks non-corporeal.
    /// Zombies and slimes have flesh so they ARE corporeal.
    /// In scenario/test mode (no tags on entity) — assume corporeal (safe default).
    /// </summary>
    private static bool IsCorporeal(Entity target, GameState state)
    {
        var ai = target.Get<CatacombsOfYarl.Logic.ECS.AiComponent>();
        if (ai?.Tags == null) return true; // no tags → assume corporeal

        // Non-corporeal creature types
        bool isNonCorporeal = ai.Tags.Contains("undead_bone")
            || ai.Tags.Contains("construct")
            || ai.Tags.Contains("ghost")
            || ai.Tags.Contains("ethereal");

        return !isNonCorporeal;
    }

    /// <summary>
    /// Find a random walkable tile on the map. Used by teleport misfire.
    /// Collects all walkable tiles and picks one at random.
    /// Falls back to caster position if no walkable tiles found (shouldn't happen).
    /// </summary>
    private static (int X, int Y) FindRandomWalkableTile(GameState state, SeededRandom rng)
    {
        var candidates = new List<(int X, int Y)>();
        for (int x = 0; x < state.Map.Width; x++)
            for (int y = 0; y < state.Map.Height; y++)
                if (state.Map.IsWalkable(x, y))
                    candidates.Add((x, y));

        if (candidates.Count == 0) return (state.Player.X, state.Player.Y);
        return candidates[rng.Next(candidates.Count)];
    }
}
