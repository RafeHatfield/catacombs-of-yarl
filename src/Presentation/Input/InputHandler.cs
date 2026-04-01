using CatacombsOfYarl.Logic.Combat;
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
/// Normal mode priority:
/// 1. Tap on adjacent enemy → Attack
/// 2. Tap on walkable tile → Move
/// 3. Tap on player's own tile when on stair + floor clear → Descend
/// 4. Nothing valid → Wait (no action emitted)
///
/// Targeting mode (entered via EnterTargetingMode):
/// - Taps route to TargetChosen (entity) or LocationChosen (tile) events
/// - Tap on player's own tile → CancelTargeting
/// - CancelTargeting can also be called directly (e.g., from a Cancel button)
/// </summary>
public sealed class InputHandler
{
    private GameState? _state;
    private IMapRenderer _renderer = new IsometricRenderer(); // default until SetRenderer called
    private bool _acceptingInput = true;
    private TargetingState? _targeting;

    /// <summary>Fired when the player has chosen an action.</summary>
    public event Action<PlayerAction>? ActionChosen;

    /// <summary>
    /// Fired when the player taps a valid entity target during single-target targeting.
    /// Parameters: (item, targetEntity).
    /// GameController creates and dispatches PlayerAction.CastSpell from this.
    /// </summary>
    public event Action<Entity, Entity>? TargetChosen;

    /// <summary>
    /// Fired when the player taps a valid floor tile during location targeting.
    /// Parameters: (item, x, y).
    /// </summary>
    public event Action<Entity, int, int>? LocationChosen;

    /// <summary>Fired when targeting is cancelled (tap self, cancel button, etc.).</summary>
    public event Action? TargetingCancelled;

    public void SetState(GameState state) => _state = state;

    /// <summary>Set the active map renderer. Call before HandleTap is first used.</summary>
    public void SetRenderer(IMapRenderer renderer) => _renderer = renderer;

    /// <summary>Block input during animations/processing.</summary>
    public void SetAcceptingInput(bool accepting) => _acceptingInput = accepting;

    /// <summary>Current targeting state, or null when not in targeting mode.</summary>
    public TargetingState? CurrentTargeting => _targeting;

    /// <summary>
    /// Enter targeting mode. HandleTap will route taps to TargetChosen/LocationChosen
    /// until targeting is resolved (target picked) or cancelled.
    /// </summary>
    public void EnterTargetingMode(TargetingState targeting)
    {
        _targeting = targeting;
        _acceptingInput = true;
        Diag.Log($"InputHandler.EnterTargetingMode: {targeting.Mode} item={targeting.Item.Name}");
    }

    /// <summary>
    /// Cancel targeting mode and fire TargetingCancelled.
    /// Called by GameController in response to cancel button taps or back gesture.
    /// Does NOT consume a turn.
    /// </summary>
    public void CancelTargeting()
    {
        Diag.Log("InputHandler.CancelTargeting");
        _targeting = null;
        TargetingCancelled?.Invoke();
    }

    /// <summary>
    /// Process a raw screen tap/click at the given position.
    /// Converts to grid coords, resolves intent, fires ActionChosen.
    /// When in targeting mode, routes to TargetChosen/LocationChosen instead.
    /// </summary>
    public void HandleTap(Vector2 screenPos)
    {
        if (!_acceptingInput || _state == null || _state.IsGameOver)
        {
            Diag.Log($"HandleTap BLOCKED: accepting={_acceptingInput}, state={_state != null}, gameOver={_state?.IsGameOver}, turnCount={_state?.TurnCount}, turnLimit={_state?.TurnLimit}");
            return;
        }

        var (gridX, gridY) = _renderer.ScreenToGrid(screenPos);

        if (!_state.Map.InBounds(gridX, gridY))
        {
            Diag.Log($"HandleTap OUT_OF_BOUNDS ({gridX},{gridY})");
            return;
        }

        // ── Targeting mode: route tap to spell targeting ─────────────────────
        if (_targeting != null)
        {
            HandleTapInTargetingMode(gridX, gridY);
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
                && _state.PlayerOnStairDown)
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

    /// <summary>
    /// Handle a tap when in targeting mode. Routes based on TargetingMode:
    /// - SingleTarget: validate alive monster in range → fire TargetChosen, or show "invalid" feedback
    /// - Location: validate walkable tile → fire LocationChosen, or show "invalid" feedback
    /// - Tap on player's own tile → cancel targeting
    /// </summary>
    private void HandleTapInTargetingMode(int gridX, int gridY)
    {
        var targeting = _targeting!;
        var state = _state!;
        var player = state.Player;

        Diag.Log($"HandleTap TARGETING_MODE ({gridX},{gridY}) mode={targeting.Mode}");

        // Tapping the player's own tile cancels targeting
        if (gridX == player.X && gridY == player.Y)
        {
            CancelTargeting();
            return;
        }

        if (targeting.Mode == TargetingMode.SingleTarget)
        {
            var target = FindMonsterAt(gridX, gridY);
            if (target == null)
            {
                Diag.Log("HandleTap TARGETING: no monster at tap position");
                // Not a valid target — provide feedback but stay in targeting mode
                return;
            }

            // Validate range
            double dist = player.DistanceTo(gridX, gridY);
            int maxRange = targeting.Range > 0 ? targeting.Range : int.MaxValue;
            if (dist > maxRange)
            {
                Diag.Log($"HandleTap TARGETING: target out of range (dist={dist:F1} > range={maxRange})");
                // Out of range — provide feedback but stay in targeting mode
                return;
            }

            Diag.Log($"HandleTap TARGETING: target chosen = {target.Name}(id={target.Id})");
            var item = targeting.Item;
            _targeting = null; // clear before firing event
            TargetChosen?.Invoke(item, target);
        }
        else if (targeting.Mode == TargetingMode.Location)
        {
            // Validate tile is walkable and in range
            if (!state.Map.IsWalkable(gridX, gridY))
            {
                Diag.Log("HandleTap TARGETING: location not walkable");
                return;
            }

            double dist = player.DistanceTo(gridX, gridY);
            int maxRange = targeting.Range > 0 ? targeting.Range : int.MaxValue;
            if (dist > maxRange)
            {
                Diag.Log($"HandleTap TARGETING: location out of range (dist={dist:F1} > range={maxRange})");
                return;
            }

            Diag.Log($"HandleTap TARGETING: location chosen = ({gridX},{gridY})");
            var item = targeting.Item;
            _targeting = null;
            LocationChosen?.Invoke(item, gridX, gridY);
        }
        else
        {
            // Other targeting modes (Portal, etc.) handled by GameController separately
            Diag.Log($"HandleTap TARGETING: mode {targeting.Mode} not handled in InputHandler");
        }
    }

    private Entity? FindMonsterAt(int gridX, int gridY)
    {
        if (_state == null) return null;
        // Do NOT use AliveMonsters (cached per TurnCount) — the cache is stale between turns
        // when a monster just died. Query Monsters directly with a live IsAlive check so the
        // player can walk onto the tile in the very next tap after killing its occupant.
        return _state.Monsters.FirstOrDefault(
            m => m.X == gridX && m.Y == gridY && m.Get<Fighter>()?.IsAlive == true);
    }
}
