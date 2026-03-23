using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Processes one game turn. Stateless — all state lives in GameState.
/// This is the single source of truth for turn resolution.
/// Both the harness (via BotBrain → PlayerAction) and the UI call this.
/// </summary>
public static class TurnController
{
    /// <summary>
    /// Process one complete turn: player action + all monster responses.
    /// Mutates gameState. Returns events describing what happened.
    /// </summary>
    public static TurnResult ProcessTurn(GameState state, PlayerAction action)
    {
        var events = new List<TurnEvent>();
        state.TurnCount++;

        // === PLAYER TURN ===
        ResolvePlayerAction(state, action, events);

        // === MONSTER TURNS ===
        if (state.PlayerFighter.IsAlive)
            ResolveMonsterTurns(state, events);

        var aliveMonsters = state.AliveMonsters;
        return new TurnResult
        {
            TurnNumber = state.TurnCount,
            Events = events,
            GameOver = state.IsGameOver,
            PlayerDied = !state.PlayerFighter.IsAlive,
            AllMonstersDefeated = aliveMonsters.Count == 0,
        };
    }

    private static void ResolvePlayerAction(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var player = state.Player;

        switch (action.Kind)
        {
            case PlayerAction.ActionKind.Attack:
                ResolvePlayerAttack(state, action.Target!, events, isBonusAttack: false);
                break;

            case PlayerAction.ActionKind.UseItem:
                TryHeal(state, action.Item, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.Move:
                ResolvePlayerMove(state, action, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.Wait:
                events.Add(new WaitEvent { ActorId = player.Id });
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;
        }
    }

    private static void ResolvePlayerAttack(GameState state, Entity target, List<TurnEvent> events, bool isBonusAttack)
    {
        var player = state.Player;
        var result = CombatResolver.ResolveAttack(player, target, state.Rng);

        events.Add(new AttackEvent
        {
            ActorId = player.Id,
            TargetId = target.Id,
            Hit = result.Hit,
            Damage = result.Damage,
            IsCritical = result.IsCritical,
            IsFumble = result.IsFumble,
            TargetKilled = result.TargetKilled,
            IsBonusAttack = isBonusAttack,
        });

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = player.Id });
        }

        // Bonus attack chain — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && !result.TargetKilled && target.Require<Fighter>().IsAlive)
        {
            ResolvePlayerAttack(state, target, events, isBonusAttack: true);
        }
    }

    private static void ResolvePlayerMove(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var player = state.Player;
        int fromX = player.X, fromY = player.Y;

        bool moved;
        if (action.Target != null)
            moved = state.Map.MoveToward(player, action.Target.X, action.Target.Y);
        else if (action.TargetX.HasValue && action.TargetY.HasValue)
            moved = state.Map.MoveToward(player, action.TargetX.Value, action.TargetY.Value);
        else
            moved = false;

        if (moved)
        {
            events.Add(new MoveEvent
            {
                ActorId = player.Id,
                FromX = fromX, FromY = fromY,
                ToX = player.X, ToY = player.Y,
            });
        }
    }

    private static void TryHeal(GameState state, Entity? specificItem, List<TurnEvent> events)
    {
        var fighter = state.PlayerFighter;
        var inventory = state.PlayerInventory;
        if (inventory == null) return;

        // Use specific item if provided (UI), otherwise find first healing potion (bot)
        var potion = specificItem ?? inventory.FindFirst(item =>
            item.Get<Consumable>()?.IsHealing == true);

        if (potion == null) return;

        var consumable = potion.Get<Consumable>();
        if (consumable == null) return;

        int healed = fighter.Heal(consumable.HealAmount);
        inventory.Remove(potion);

        events.Add(new HealEvent
        {
            ActorId = state.Player.Id,
            AmountHealed = healed,
            ItemId = potion.Id,
            ItemName = potion.Name,
        });
    }

    private static void ResolveMonsterTurns(GameState state, List<TurnEvent> events)
    {
        var player = state.Player;
        var playerFighter = state.PlayerFighter;

        foreach (var monster in state.Monsters)
        {
            var mf = monster.Require<Fighter>();
            if (!mf.IsAlive || !playerFighter.IsAlive)
                continue;

            if (monster.ChebyshevDistanceTo(player.X, player.Y) <= 1)
            {
                ResolveMonsterAttack(state, monster, events, isBonusAttack: false);
            }
            else
            {
                int fromX = monster.X, fromY = monster.Y;
                bool moved = state.Map.MoveToward(monster, player.X, player.Y);
                if (moved)
                {
                    events.Add(new MoveEvent
                    {
                        ActorId = monster.Id,
                        FromX = fromX, FromY = fromY,
                        ToX = monster.X, ToY = monster.Y,
                    });
                }
            }
        }
    }

    private static void ResolveMonsterAttack(GameState state, Entity monster, List<TurnEvent> events, bool isBonusAttack)
    {
        var player = state.Player;
        var result = CombatResolver.ResolveAttack(monster, player, state.Rng);

        events.Add(new AttackEvent
        {
            ActorId = monster.Id,
            TargetId = player.Id,
            Hit = result.Hit,
            Damage = result.Damage,
            IsCritical = result.IsCritical,
            IsFumble = result.IsFumble,
            TargetKilled = result.TargetKilled,
            IsBonusAttack = isBonusAttack,
        });

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = player.Id, KillerId = monster.Id });
        }

        // Monster bonus attacks
        if (result.BonusAttackTriggered && player.Require<Fighter>().IsAlive)
        {
            ResolveMonsterAttack(state, monster, events, isBonusAttack: true);
        }
    }
}
