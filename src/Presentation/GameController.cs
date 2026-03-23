using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Animation;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Input;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Orchestrates the full game loop. Owns GameState, drives TurnController,
/// coordinates input → processing → animation → input cycle.
///
/// State machine:
///   WaitingForInput → (player taps) → Processing → (turn resolved) → Animating → (done) → WaitingForInput
///   Any state → GameOver (player dies or all monsters dead)
/// </summary>
public sealed partial class GameController : Node
{
    public enum GamePhase { WaitingForInput, Processing, Animating, GameOver }

    private GameState? _state;
    private InputHandler _input = new();
    private EntitySpriteManager? _entitySprites;
    private TurnAnimator? _animator;

    public GamePhase Phase { get; private set; } = GamePhase.WaitingForInput;

    /// <summary>Fired each time a turn completes. UI can update from this.</summary>
    public event Action<TurnResult>? TurnCompleted;

    /// <summary>Fired when the game ends.</summary>
    public event Action<bool>? GameEnded; // true = player won

    /// <summary>
    /// Initialize the controller with a loaded game state and scene nodes.
    /// Call after creating GameState and setting up the scene.
    /// </summary>
    public void Initialize(GameState state, EntitySpriteManager entitySprites, Node animationRoot)
    {
        _state = state;
        _entitySprites = entitySprites;
        _animator = new TurnAnimator(animationRoot, entitySprites);
        _animator.AnimationComplete += OnAnimationComplete;

        _input.SetState(state);
        _input.ActionChosen += OnActionChosen;
        _input.SetAcceptingInput(true);
    }

    /// <summary>
    /// Forward raw tap position from the scene's _Input handler.
    /// </summary>
    public void HandleTap(Vector2 screenPos)
    {
        _input.HandleTap(screenPos);
    }

    private void OnActionChosen(PlayerAction action)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;

        Phase = GamePhase.Processing;
        _input.SetAcceptingInput(false);

        var result = TurnController.ProcessTurn(_state, action);
        TurnCompleted?.Invoke(result);

        // Remove dead entities from sprite manager
        foreach (var evt in result.Events.OfType<DeathEvent>())
        {
            _entitySprites?.RemoveEntity(evt.ActorId);
        }

        if (result.GameOver)
        {
            Phase = GamePhase.GameOver;
            // Still animate what happened before showing game over
            _animator?.PlayTurn(result);
        }
        else
        {
            Phase = GamePhase.Animating;
            _animator?.PlayTurn(result);
        }
    }

    private void OnAnimationComplete()
    {
        if (_state == null) return;

        // Update sprite positions after animation
        _entitySprites?.UpdatePositions(_state);

        if (Phase == GamePhase.GameOver)
        {
            GameEnded?.Invoke(_state.PlayerWon);
            return;
        }

        Phase = GamePhase.WaitingForInput;
        _input.SetAcceptingInput(true);
    }
}
