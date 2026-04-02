using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;

namespace CatacombsOfYarl.Logic.AI;

/// <summary>
/// Orc Shaman AI: Crippling Hex + hang-back positioning.
///
/// Decision priority each turn:
///   1. Dead → Wait
///   2. Awareness update
///   3. Not alerted → Wait
///   4. Status effect overrides (FearEffect, DisorientationEffect, EntangledEffect)
///   5. Decrement hex cooldown
///   6. Player within DangerRadius (≤2) → panic retreat (flee one step)
///   7. Hex ready AND player in HexRange → apply CrippledEffect, reset cooldown
///   8. Too close (dist &lt; PreferredDistanceMin) → retreat one step
///   9. Too far (dist > PreferredDistanceMax) → advance one step via A*
///  10. Adjacent → Attack
///  11. Wait (in preferred range, hex on cooldown)
/// </summary>
public static class OrcShamanAI
{
    public static MonsterAction Decide(Entity monster, GameState state)
    {
        // 1. Dead guard.
        var fighter = monster.Get<Fighter>();
        if (fighter != null && !fighter.IsAlive)
            return MonsterAction.Wait();

        var player = state.Player;

        // 2. Awareness update.
        BasicMonsterAI.UpdateAwareness(monster, player, state);

        // 3. Not alerted → idle.
        var alerted = monster.Get<AlertedState>();
        if (alerted == null) return MonsterAction.Wait();

        // 4. Status effect AI overrides.
        if (monster.Has<FearEffect>())
            return BasicMonsterAI.DecideFlee(monster, player, state);

        var target = BasicMonsterAI.ChooseTarget(monster, player, state);
        bool adjacent = monster.ChebyshevDistanceTo(target.X, target.Y) <= 1;

        if (monster.Has<DisorientationEffect>())
        {
            if (adjacent && !target.Has<InvisibilityEffect>()) return MonsterAction.Attack(target);
            return BasicMonsterAI.DecideRandomMove(monster, state);
        }

        if (monster.Has<EntangledEffect>())
        {
            if (adjacent && !target.Has<InvisibilityEffect>()) return MonsterAction.Attack(target);
            return MonsterAction.Wait();
        }

        // 5. Tick cooldown.
        var shaman = monster.Get<OrcShamanComponent>();
        if (shaman == null) return BasicMonsterAI.Decide(monster, state);

        if (shaman.HexCooldownRemaining > 0)
            shaman.HexCooldownRemaining--;

        int dist = monster.ChebyshevDistanceTo(player.X, player.Y);

        // 6. Panic retreat — player too close, flee immediately (highest priority after status effects).
        if (dist <= shaman.DangerRadius)
            return BasicMonsterAI.DecideFlee(monster, player, state);

        // 7. Crippling Hex — fire when ready and player is in range.
        if (shaman.HexCooldownRemaining == 0 && dist <= shaman.HexRange)
        {
            StatusEffectProcessor.ApplyEffect<CrippledEffect>(player, shaman.HexDuration);
            shaman.HexCooldownRemaining = shaman.HexCooldownTurns;
            // Fall through to positioning — the shaman doesn't waste its turn just standing still.
        }

        // 8. Reposition: too close → retreat one step (maximize distance from player).
        if (dist < shaman.PreferredDistanceMin)
        {
            var retreatAction = BasicMonsterAI.DecideFlee(monster, player, state);
            if (retreatAction.Kind != MonsterAction.ActionKind.Wait) return retreatAction;
        }

        // 9. Reposition: too far → advance one step toward player.
        if (dist > shaman.PreferredDistanceMax)
        {
            var path = Pathfinder.AStar(state.Map, monster.X, monster.Y, player.X, player.Y, movingEntity: monster);
            if (path != null && path.Count > 0)
                return MonsterAction.MoveTo(path[0].X, path[0].Y);
        }

        // 10. Adjacent → attack (melee fallback when player is inside preferred range).
        if (adjacent && !target.Has<InvisibilityEffect>())
            return MonsterAction.Attack(target);

        // 11. Wait (in preferred range, hex on cooldown).
        return MonsterAction.Wait();
    }
}
