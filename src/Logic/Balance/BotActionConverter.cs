using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Converts a BotAction to a PlayerAction suitable for TurnController consumption.
///
/// The simple BotBrain.ToPlayerAction() uses GameMap.MoveToward for MoveToward actions —
/// a greedy directional step that gets stuck at walls. This class provides
/// ToPlayerActionWithPathing() which uses A* for MoveToward so the bot can navigate
/// across dungeon floors with rooms and corridors.
///
/// Used by both DungeonRunHarness (headless) and BotPlayerDriver (graphical).
/// Extracted from DungeonRunHarness.cs (lines 368-401 in the original).
/// </summary>
public static class BotActionConverter
{
    /// <summary>
    /// Convert a BotAction to a PlayerAction, using A* pathing for MoveToward actions.
    ///
    /// For MoveToward actions: computes an A* path from the player to the target,
    /// routing around detected traps (if any). Returns a single-step MoveTo action.
    /// Falls back to Wait if the target is unreachable.
    ///
    /// For all other action types: delegates to BotBrain.ToPlayerAction().
    /// </summary>
    public static PlayerAction ToPlayerActionWithPathing(BotAction botAction, GameState state)
    {
        if (botAction.Type == BotAction.ActionType.MoveToward && botAction.Target != null)
        {
            var target = botAction.Target;

            // Build detected trap set so the bot routes around known hazards.
            // If trap-avoidance produces no path (bot is completely surrounded),
            // fall back to unconstrained A* to keep the bot moving.
            var trapTiles = Pathfinder.DetectedTrapTiles(state.Features);
            var path = Pathfinder.AStar(
                state.Map,
                state.Player.X, state.Player.Y,
                target.X, target.Y,
                state.Player,
                canPassDoors: true,
                avoidTiles: trapTiles.Count > 0 ? trapTiles : null);

            // Fallback: if trap-avoiding path fails, try without avoidance
            path ??= Pathfinder.AStar(
                state.Map,
                state.Player.X, state.Player.Y,
                target.X, target.Y,
                state.Player,
                canPassDoors: true);

            if (path != null && path.Count > 0)
            {
                var (nx, ny) = path[0];
                return PlayerAction.MoveTo(nx, ny);
            }
            else
            {
                return PlayerAction.Wait; // unreachable target
            }
        }

        return BotBrain.ToPlayerAction(botAction);
    }
}
