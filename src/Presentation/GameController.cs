using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;
using CatacombsOfYarl.Presentation.Animation;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Input;
using CatacombsOfYarl.Presentation.Map;
using CatacombsOfYarl.Presentation.UI;
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

    /// <summary>Animation speed multiplier during auto-explore. 1.0 = normal, lower = faster.</summary>
    public const float AutoExploreSpeedMultiplier = 0.25f;

    /// <summary>Animation speed multiplier during multi-step click-to-move. Between auto-explore and normal.</summary>
    public const float ClickToMoveSpeedMultiplier = 0.55f;

    private GameState? _state;
    private InputHandler _input = new();
    private EntitySpriteManager? _entitySprites;
    private ItemSpriteManager? _itemSprites;
    private InventoryPanel? _inventoryPanel;
    private TurnAnimator? _animator;

    // Stored between OnActionChosen and OnAnimationComplete so we can fire the transition
    // after animations finish rather than immediately when the event is emitted.
    private DescendEvent? _pendingDescend;

    // Multi-step click-to-move: A* path queued step-by-step, one step per turn.
    private Queue<(int X, int Y)>? _pendingPath;
    // HP snapshot at path start — interrupt if player takes damage mid-path.
    private int _pathInterruptHp = -1;
    // Monster IDs visible when path started — only interrupt on NEW monsters entering FOV.
    // Empty until Phase 2 (FOV) lands; CheckPathInterrupts is a no-op for monster visibility until then.
    private readonly HashSet<int> _pathStartVisibleMonsterIds = new();
    private bool _autoExploreMode;

    public GamePhase Phase { get; private set; } = GamePhase.WaitingForInput;

    /// <summary>True while auto-explore is actively running.</summary>
    public bool IsAutoExploreActive => _autoExploreMode;

    /// <summary>Fired each time a turn completes. UI can update from this.</summary>
    public event Action<TurnResult>? TurnCompleted;

    /// <summary>Fired when the game ends.</summary>
    public event Action<bool>? GameEnded; // true = player won

    /// <summary>
    /// Fired after animations complete when the player has descended a staircase.
    /// Carries the new depth the player is arriving at.
    /// Main listens to this to tear down the current floor and build the next one.
    /// </summary>
    public event Action<int>? FloorTransitionRequested;

    /// <summary>
    /// Initialize the controller with a loaded game state and scene nodes.
    /// Call after creating GameState and setting up the scene.
    /// </summary>
    public override void _Process(double delta)
    {
        // Poll tween completion instead of using TweenCallback + Callable.From.
        // Callable.From(delegate) on a non-GodotObject creates a GCHandle that
        // Godot 4.6 C# doesn't reliably release, causing memory explosion in combat.
        _animator?.CheckComplete();
    }

    public void Initialize(GameState state, EntitySpriteManager entitySprites, Node animationRoot,
        ItemSpriteManager? itemSprites = null, InventoryPanel? inventoryPanel = null)
    {
#if DEBUG
        System.Diagnostics.Debug.Assert(_animator == null,
            "GameController.Initialize called twice on the same instance — event double-subscribe risk");
#endif
        _state = state;
        _entitySprites = entitySprites;
        _itemSprites = itemSprites;
        _inventoryPanel = inventoryPanel;
        _animator = new TurnAnimator(animationRoot, entitySprites);
        _animator.AnimationComplete += OnAnimationComplete;

        _input.SetState(state);
        _input.ActionChosen += OnActionChosen;
        _input.SetAcceptingInput(true);

        _pendingPath = null;
        _autoExploreMode = false;
    }

    /// <summary>
    /// Handle a tap on an inventory slot. Finds the item in the player's inventory
    /// and issues a UseItem action, which TurnController routes to TryHeal (or similar).
    /// </summary>
    public void HandleInventoryTap(int itemId)
    {
        Diag.Log($"HandleInventoryTap: itemId={itemId}, phase={Phase}");
        if (_state == null || Phase != GamePhase.WaitingForInput)
        {
            Diag.Log($"  BLOCKED: state={_state != null}, phase={Phase}");
            return;
        }

        var inventory = _state.PlayerInventory;
        if (inventory == null) { Diag.Log("  BLOCKED: no inventory"); return; }

        var item = inventory.FindFirst(e => e.Id == itemId);
        if (item == null) { Diag.Log($"  BLOCKED: no item with id={itemId}"); return; }

        Diag.Log($"  -> UseItem({item.Name})");
        OnActionChosen(PlayerAction.UseItem(item));
    }

    /// <summary>
    /// Forward raw tap position from the scene's _Input handler.
    /// </summary>
    public void HandleTap(Vector2 screenPos)
    {
        _input.HandleTap(screenPos);
    }

    /// <summary>
    /// Begin auto-explore. Cancels any queued click-to-move path, activates
    /// AutoExploreSystem, and immediately steps the first move.
    /// No-op if state is not ready or game is not waiting for input.
    /// </summary>
    public void StartAutoExplore()
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        Diag.Log("StartAutoExplore");
        _pendingPath = null;
        _autoExploreMode = true;
        _animator!.SpeedMultiplier = AutoExploreSpeedMultiplier;
        AutoExploreSystem.Activate(_state);
        AdvanceAutoExplore();
    }

    private void AdvanceAutoExplore()
    {
        if (!_autoExploreMode || _state == null) return;
        var action = AutoExploreSystem.GetNextAction(_state);
        if (action == null)
        {
            _autoExploreMode = false;
            _animator!.SpeedMultiplier = 1.0f;
            Phase = GamePhase.WaitingForInput;
            _input.SetAcceptingInput(true);
            return;
        }
        ExecuteTurn(action);
    }

    private void OnActionChosen(PlayerAction action)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;

        // Any manual tap cancels auto-explore.
        if (_autoExploreMode)
            Diag.Log($"OnActionChosen: action={action.Kind}, cancelled auto-explore");
        _autoExploreMode = false;
        if (_animator != null) _animator.SpeedMultiplier = 1.0f;
        if (_state != null)
            if (_state.Player.Get<AutoExploreState>() is { } ae) ae.IsActive = false;

        if (action.Kind == PlayerAction.ActionKind.Move
            && action.TargetX.HasValue && action.TargetY.HasValue)
        {
            int tx = action.TargetX.Value, ty = action.TargetY.Value;
            int dist = _state.Player.ChebyshevDistanceTo(tx, ty);

            if (dist > 1)
            {
                // Distant tap: compute A* path and queue all steps.
                var path = Pathfinder.AStar(
                    _state.Map,
                    _state.Player.X, _state.Player.Y,
                    tx, ty,
                    _state.Player);

                if (path == null || path.Count == 0) return; // Unreachable — silently ignore

                _pendingPath = new Queue<(int, int)>(path);
                _pathInterruptHp = _state.PlayerFighter.Hp;
                _animator!.SpeedMultiplier = ClickToMoveSpeedMultiplier;

                // Snapshot which monsters are currently visible so CheckPathInterrupts can
                // distinguish pre-existing visible monsters (safe to ignore) from newly-spotted
                // ones (should interrupt). Phase 2 FOV is live — populate from map visibility.
                _pathStartVisibleMonsterIds.Clear();
                foreach (var m in _state.AliveMonsters)
                    if (_state.Map.IsVisible(m.X, m.Y))
                        _pathStartVisibleMonsterIds.Add(m.Id);

                // Dequeue and execute the first step immediately.
                var (nx, ny) = _pendingPath.Dequeue();
                action = PlayerAction.MoveTo(nx, ny);
            }
            else
            {
                // Adjacent tap — clear any queued path, just take the step normally.
                _pendingPath = null;
            }
        }
        else
        {
            // Non-Move action (Attack, UseItem, Wait, Descend) — cancel any queued path.
            _pendingPath = null;
        }

        ExecuteTurn(action);
    }

    /// <summary>
    /// Execute one turn: process through TurnController, drive animations.
    /// Extracted from OnActionChosen so path continuation in OnAnimationComplete
    /// can reuse it without duplicating the turn-execution logic.
    /// </summary>
    // Debug: track allocations per turn to isolate the memory spike source.
    private long _lastAllocBytes;

    private void ExecuteTurn(PlayerAction action)
    {
        Phase = GamePhase.Processing;
        _input.SetAcceptingInput(false);

        Diag.Log($"ExecuteTurn START action={action.Kind}");
        Diag.Event("ExecuteTurn", new { action = action.Kind.ToString(), turnCount = _state!.TurnCount });
        Diag.Mem("  pre-ProcessTurn");

        var result = TurnController.ProcessTurn(_state!, action);
        Diag.Log($"  ProcessTurn done: {result.Events.Count} events, gameOver={result.GameOver}");
        foreach (var evt in result.Events)
            Diag.Log($"    evt: {evt.GetType().Name}");
        Diag.Mem("  post-ProcessTurn");

        Diag.Log("  -> TurnCompleted");
        TurnCompleted?.Invoke(result);
        Diag.Log("  <- TurnCompleted");

        // Single pass over events — avoids 5 separate LINQ allocations per turn.
        bool inventoryChanged = false;
        _pendingDescend = null;
        foreach (var evt in result.Events)
        {
            if (evt is DeathEvent dead)
                _entitySprites?.RemoveEntity(dead.ActorId);
            else if (evt is PickUpEvent pick)
                { _itemSprites?.RemoveItem(pick.ItemId); inventoryChanged = true; }
            else if (evt is DropEvent drop)
            {
                var dropped = _state!.FloorItems.FirstOrDefault(i => i.Id == drop.ItemId);
                if (dropped != null) _itemSprites?.CreateSprite(dropped);
                inventoryChanged = true;
            }
            else if (evt is HealEvent)
                inventoryChanged = true;
            else if (evt is DescendEvent desc)
                _pendingDescend = desc;
        }

        if (inventoryChanged)
            _inventoryPanel?.Refresh(_state!);

        Diag.Log($"  -> PlayTurn (gameOver={result.GameOver})");
        if (result.GameOver)
        {
            Phase = GamePhase.GameOver;
            _animator?.PlayTurn(result);
        }
        else
        {
            Phase = GamePhase.Animating;
            _animator?.PlayTurn(result);
        }
        Diag.Log("ExecuteTurn END");
    }

    private void OnAnimationComplete()
    {
        Diag.Log("OnAnimationComplete START");
        Diag.Event("AnimationComplete", new { phase = Phase.ToString() });
        if (_state == null) return;

        Diag.Log("  OAC: UpdatePositions");
        _entitySprites?.UpdatePositions(_state);

        if (Phase == GamePhase.GameOver)
        {
            Diag.Log("  OAC: GameOver -> GameEnded");
            GameEnded?.Invoke(_state.PlayerWon);
            return;
        }

        if (_pendingDescend != null)
        {
            Diag.Log("  OAC: FloorTransition");
            var descend = _pendingDescend;
            _pendingDescend = null;
            FloorTransitionRequested?.Invoke(descend.NewDepth);
            return;
        }

        if (_autoExploreMode)
        {
            Diag.Log("  OAC: AutoExplore");
            AdvanceAutoExplore();
            return;
        }

        if (_pendingPath != null && _pendingPath.Count > 0)
        {
            Diag.Log($"  OAC: PathContinue ({_pendingPath.Count} steps left)");
            if (!CheckPathInterrupts())
            {
                var (nx, ny) = _pendingPath.Dequeue();
                Diag.Log($"  OAC: PathStep ({nx},{ny})");
                ExecuteTurn(PlayerAction.MoveTo(nx, ny));
                return;
            }
            Diag.Log("  OAC: PathInterrupt");
            _pendingPath = null;
            _animator!.SpeedMultiplier = 1.0f;
        }
        else if (_pendingPath != null && _pendingPath.Count == 0)
        {
            Diag.Log("  OAC: PathComplete");
            _pendingPath = null;
            _animator!.SpeedMultiplier = 1.0f;
        }

        Diag.Log("  OAC: WaitingForInput");
        Phase = GamePhase.WaitingForInput;
        _input.SetAcceptingInput(true);
    }

    /// <summary>
    /// Returns true if an in-progress path should be stopped.
    ///
    /// Two interrupt conditions:
    /// 1. Player took damage since the path started (any hit stops pathing).
    /// 2. A monster that was NOT visible when the path started is now visible.
    ///    Pre-existing visible monsters are in the snapshot and don't interrupt —
    ///    this allows click-to-move to work usefully in rooms that already have visible enemies.
    ///
    /// Note: until Phase 2 (FOV) lands, GameMap has no IsVisible API and the monster
    /// snapshot is always empty, so condition 2 is a no-op. The structure is wired now
    /// and will activate automatically when Phase 2 adds IsVisible to GameMap.
    /// </summary>
    private bool CheckPathInterrupts()
    {
        if (_state == null) return true;

        // Damage taken since path started.
        if (_state.PlayerFighter.Hp < _pathInterruptHp) return true;

        // New monster entered FOV that wasn't visible when the path started.
        // Phase 2 FOV is live — interrupt if a monster not in the start snapshot is now visible.
        foreach (var m in _state.AliveMonsters)
            if (_state.Map.IsVisible(m.X, m.Y) && !_pathStartVisibleMonsterIds.Contains(m.Id))
                return true;

        return false;
    }
}
