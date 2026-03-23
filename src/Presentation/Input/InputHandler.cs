using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Input;

/// <summary>
/// Translates touch/mouse input into PlayerActions.
/// Reads current GameState to determine what's at the tapped position.
///
/// Priority:
/// 1. Tap on adjacent enemy → Attack
/// 2. Tap on walkable tile → Move
/// 3. Nothing valid → Wait (no action emitted)
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
            return;

        var (gridX, gridY) = IsometricMapper.ScreenToGrid(screenPos);

        if (!_state.Map.InBounds(gridX, gridY))
            return;

        var player = _state.Player;

        // Check if tapped an adjacent alive monster → Attack
        var target = FindMonsterAt(gridX, gridY);
        if (target != null)
        {
            int dist = player.ChebyshevDistanceTo(gridX, gridY);
            if (dist <= 1)
            {
                ActionChosen?.Invoke(PlayerAction.Attack(target));
                return;
            }
            // Tapped distant enemy → move toward it
            ActionChosen?.Invoke(PlayerAction.MoveToward(target));
            return;
        }

        // Tapped a walkable tile → move there
        if (_state.Map.IsWalkable(gridX, gridY))
        {
            ActionChosen?.Invoke(PlayerAction.MoveTo(gridX, gridY));
            return;
        }
    }

    private Entity? FindMonsterAt(int gridX, int gridY)
    {
        if (_state == null) return null;
        return _state.AliveMonsters.FirstOrDefault(m => m.X == gridX && m.Y == gridY);
    }
}
