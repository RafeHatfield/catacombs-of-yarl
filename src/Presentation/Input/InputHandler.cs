using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Map;
using Godot;
using CatacombsOfYarl.Presentation;

namespace CatacombsOfYarl.Presentation.Input;

/// <summary>
/// Translates touch/mouse input into PlayerActions.
/// Reads current GameState to determine what's at the tapped position.
///
/// Priority:
/// 1. Tap on adjacent enemy → Attack
/// 2. Tap on walkable tile → Move
/// 3. Tap on player's own tile when on stair + floor clear → Descend
/// 4. Nothing valid → Wait (no action emitted)
/// </summary>
public sealed class InputHandler
{
    private GameState? _state;
    private bool _acceptingInput = true;

    /// <summary>Fired when the player has chosen an action.</summary>
    public event Action<PlayerAction>? ActionChosen;

    public void SetState(GameState state) => _state = state;

    /// <summary>Block input during animations/processing.</summary>
    public void SetAcceptingInput(bool accepting) => _acceptingInput = accepting;

    /// <summary>
    /// Process a raw screen tap/click at the given position.
    /// Converts to grid coords, resolves intent, fires ActionChosen.
    /// </summary>
    public void HandleTap(Vector2 screenPos)
    {
        if (!_acceptingInput || _state == null || _state.IsGameOver)
        {
            Diag.Log($"HandleTap BLOCKED: accepting={_acceptingInput}, state={_state != null}, gameOver={_state?.IsGameOver}, turnCount={_state?.TurnCount}, turnLimit={_state?.TurnLimit}");
            return;
        }

        var (gridX, gridY) = IsometricMapper.ScreenToGrid(screenPos);

        if (!_state.Map.InBounds(gridX, gridY))
        {
            Diag.Log($"HandleTap OUT_OF_BOUNDS ({gridX},{gridY})");
            return;
        }

        var player = _state.Player;

        // Check if tapped an adjacent alive monster → Attack
        var target = FindMonsterAt(gridX, gridY);
        if (target != null)
        {
            int dist = player.ChebyshevDistanceTo(gridX, gridY);
            if (dist <= 1)
            {
                Diag.Log($"HandleTap ATTACK target={target.Name}(id={target.Id}) dist={dist}");
                ActionChosen?.Invoke(PlayerAction.Attack(target));
                return;
            }
            // Tapped distant enemy → move toward it
            Diag.Log($"HandleTap MOVE_TOWARD target={target.Name} at ({gridX},{gridY})");
            ActionChosen?.Invoke(PlayerAction.MoveToward(target));
            return;
        }

        // Tapped a walkable tile → move there, or descend if on stair
        if (_state.Map.IsWalkable(gridX, gridY))
        {
            // Special case: player taps their own tile while standing on a stair-down
            // with the floor cleared → intent is to descend.
            if (gridX == player.X && gridY == player.Y
                && _state.PlayerOnStairDown
                && _state.IsFloorClear)
            {
                Diag.Log($"HandleTap DESCEND at ({gridX},{gridY})");
                ActionChosen?.Invoke(PlayerAction.Descend);
                return;
            }

            Diag.Log($"HandleTap MOVE_TO ({gridX},{gridY})");
            ActionChosen?.Invoke(PlayerAction.MoveTo(gridX, gridY));
            return;
        }

        Diag.Log($"HandleTap NO_ACTION at ({gridX},{gridY}) — not walkable, no monster");
    }

    private Entity? FindMonsterAt(int gridX, int gridY)
    {
        if (_state == null) return null;
        return _state.AliveMonsters.FirstOrDefault(m => m.X == gridX && m.Y == gridY);
    }
}
