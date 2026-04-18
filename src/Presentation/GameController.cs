using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Knowledge;
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
    public enum GamePhase { WaitingForInput, Processing, Animating, GameOver, Targeting }

    /// <summary>Animation speed multiplier during auto-explore. 1.0 = normal, lower = faster.</summary>
    public const float AutoExploreSpeedMultiplier = 0.25f;

    /// <summary>Animation speed multiplier during multi-step click-to-move. Between auto-explore and normal.</summary>
    public const float ClickToMoveSpeedMultiplier = 0.55f;

    private GameState? _state;
    private MonsterFactory? _monsterFactory;
    private EntityFactory? _portalEntityFactory;
    private InputHandler _input = new();
    private EntitySpriteManager? _entitySprites;
    private ItemSpriteManager? _itemSprites;
    private QuickSlotBar? _inventoryPanel;
    private EquipmentPanel? _equipmentPanel;
    private ToastLog? _toastLog;
    private TurnAnimator? _animator;
    private LongPressDetector? _longPress;
    private InspectPanel? _inspectPanel;
    private ActionSheet? _actionSheet;
    private IMapRenderer _renderer = new TopDownRenderer(); // safe default
    private Node2D? _gameView; // needed to ToLocal() in OnLongPress

    // Holds the item being thrown — needed to route LocationChosen back to ThrowItem.
    private Entity? _pendingThrowItem;

    // Stored between OnActionChosen and OnAnimationComplete so we can fire the transition
    // after animations finish rather than immediately when the event is emitted.
    private DescendEvent? _pendingDescend;

    // Set when the portal wand enters targeting mode for exit placement (step 2).
    // Used to clean up the pending entrance if the player cancels targeting.
    private Entity? _pendingPortalWand;

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
        ItemSpriteManager? itemSprites = null, QuickSlotBar? inventoryPanel = null,
        EquipmentPanel? equipmentPanel = null, ToastLog? toastLog = null,
        MonsterFactory? monsterFactory = null, IMapRenderer? renderer = null,
        Node2D? gameView = null, EntityFactory? portalEntityFactory = null,
        VfxOverlay? vfxOverlay = null)
    {
#if DEBUG
        System.Diagnostics.Debug.Assert(_animator == null,
            "GameController.Initialize called twice on the same instance — event double-subscribe risk");
#endif
        _state = state;
        _monsterFactory = monsterFactory;
        _portalEntityFactory = portalEntityFactory;
        _entitySprites = entitySprites;
        _itemSprites = itemSprites;
        _inventoryPanel = inventoryPanel;
        _equipmentPanel = equipmentPanel;
        _toastLog = toastLog;
        _renderer = renderer ?? new TopDownRenderer();
        _gameView = gameView;
        _animator = new TurnAnimator(animationRoot, entitySprites, _renderer, vfxOverlay);
        _animator.AnimationComplete += OnAnimationComplete;

        _input.SetState(state);
        _input.SetRenderer(_renderer);
        _input.ActionChosen += OnActionChosen;
        _input.TargetChosen += OnTargetChosen;
        _input.LocationChosen += OnLocationChosen;
        _input.TargetingCancelled += OnTargetingCancelled;
        _input.SetAcceptingInput(true);

        // Set up long-press detection and inspect panel.
        // Both are created as children of this Node so they participate in the scene tree.
        _longPress = new LongPressDetector();
        AddChild(_longPress);
        _longPress.LongPressDetected += OnLongPress;

        // Both InspectPanel and ActionSheet must live in UILayer (CanvasLayer) to render
        // on top of all game tiles and entity sprites. GameController is a plain Node —
        // its children render in world space behind CanvasLayer UI.
        var uiLayer = GetTree()?.CurrentScene?.GetNode<CanvasLayer>("UILayer");

        _inspectPanel = new InspectPanel();
        if (uiLayer != null)
            uiLayer.AddChild(_inspectPanel);
        else
            AddChild(_inspectPanel); // fallback (editor/test context)

        _actionSheet = new ActionSheet();
        if (uiLayer != null)
            uiLayer.AddChild(_actionSheet);
        else
            AddChild(_actionSheet); // fallback (editor/test context)
        _actionSheet.ActionSelected += OnActionSheetSelected;

        // Wire inventory long-press
        if (_inventoryPanel != null)
            _inventoryPanel.ItemLongPressed += HandleInventoryLongPress;

        // Wire equipment panel long-press events
        if (_equipmentPanel != null)
        {
            _equipmentPanel.EquippedItemLongPressed += HandleEquippedSlotLongPress;
            _equipmentPanel.PackItemLongPressed     += HandlePackItemLongPress;
        }

        _pendingPath = null;
        _autoExploreMode = false;
    }

    /// <summary>
    /// Handle a tap on an inventory slot.
    /// - Potions (Consumable with HealAmount > 0): issue UseItem immediately.
    /// - Scrolls / Wands (SpellEffect): dispatch via HandleScrollOrWandUse.
    ///   Self/AutoClosest/AoeSelf → immediate CastSpell action.
    ///   SingleTarget/Location → enter targeting mode, wait for player to pick a target.
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

        // Check if item is a scroll or wand.
        // Throwable potions no longer enter targeting on tap — tap = drink (obvious action).
        // Throw is accessed via long-press → action sheet → Throw.
        var spellEffect = item.Get<SpellEffect>();
        if (spellEffect != null)
        {
            HandleScrollOrWandUse(item, spellEffect);
            return;
        }

        Diag.Log($"  -> UseItem({item.Name})");
        OnActionChosen(PlayerAction.UseItem(item));
    }

    /// <summary>
    /// Dispatch a scroll or wand use.
    ///
    /// Self / AutoClosest / AoeSelf: no targeting UI — fire CastSpell immediately.
    ///   AutoClosest: find closest visible enemy first; if none, toast "No visible targets".
    /// SingleTarget / Location: enter targeting mode.
    /// Portal: wand-of-portals two-step (deferred to Phase 5).
    /// </summary>
    private void HandleScrollOrWandUse(Entity item, SpellEffect spell)
    {
        Diag.Log($"HandleScrollOrWandUse: {item.Name} targeting={spell.Targeting}");

        switch (spell.Targeting)
        {
            case TargetingMode.Self:
            case TargetingMode.AoeSelf:
                // No target required — fire immediately
                OnActionChosen(PlayerAction.CastSpell(item));
                break;

            case TargetingMode.AutoClosest:
                // Resolve target now in the presentation layer (closest visible enemy)
                var closest = FindClosestVisibleEnemy(spell.Range);
                if (closest == null)
                {
                    _toastLog?.AddMessage("No visible targets in range.");
                    Diag.Log("HandleScrollOrWandUse: no visible targets for AutoClosest");
                    return; // Do NOT consume item or turn
                }
                OnActionChosen(PlayerAction.CastSpell(item, targetEntityId: closest.Id));
                break;

            case TargetingMode.SingleTarget:
                EnterTargetingMode(new TargetingState
                {
                    Item  = item,
                    Spell = spell,
                    Mode  = TargetingMode.SingleTarget,
                    Range = spell.Range,
                });
                break;

            case TargetingMode.Location:
                EnterTargetingMode(new TargetingState
                {
                    Item   = item,
                    Spell  = spell,
                    Mode   = TargetingMode.Location,
                    Range  = spell.Range,
                    Radius = spell.Radius,
                });
                break;

            case TargetingMode.Portal:
            {
                if (_state == null) break;
                var step = PortalSystem.GetPortalCastStep(item);
                switch (step)
                {
                    case PortalCastStep.Ready:
                        // Step 1: pick entrance location
                        _pendingPortalWand = item;
                        EnterTargetingMode(new TargetingState
                        {
                            Item  = item,
                            Spell = spell,
                            Mode  = TargetingMode.Location,
                            Range = 0,
                        }, showGenericToast: false);
                        _toastLog?.AddMessage("Tap a tile to place the portal entrance.");
                        break;
                    case PortalCastStep.EntrancePlaced:
                        // Step 2: pick exit location
                        _pendingPortalWand = item;
                        EnterTargetingMode(new TargetingState
                        {
                            Item  = item,
                            Spell = spell,
                            Mode  = TargetingMode.Location,
                            Range = 0,
                        }, showGenericToast: false);
                        _toastLog?.AddMessage("Tap a tile to place the exit portal. Tap yourself to cancel.");
                        break;
                    case PortalCastStep.BothPlaced:
                        // Step 3: reset — removes both portals
                        _toastLog?.AddMessage("Portals removed. Wand recharged.");
                        OnActionChosen(PlayerAction.CastSpell(item));
                        break;
                }
                break;
            }

            default:
                // Unknown targeting mode — treat as Self
                OnActionChosen(PlayerAction.CastSpell(item));
                break;
        }
    }

    // HandleThrowablePotion removed (TASK-006): tap on throwable potions now drinks immediately.
    // Throw is accessed via long-press → action sheet → "Throw" → targeting mode.
    // OnDrinkSelfRequested removed: self-tap during targeting always cancels (no drink path).

    // ─── Action Sheet ─────────────────────────────────────────────────────────

    /// <summary>
    /// Show the action sheet for a long-pressed inventory slot item.
    /// Determines whether the item is currently equipped so the sheet shows the right actions.
    /// </summary>
    public void HandleInventoryLongPress(int itemId)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        var item = FindItemById(itemId);
        if (item == null) return;

        bool isEquipped = IsItemEquipped(item);
        _actionSheet?.Show(item, isEquipped);
    }

    /// <summary>Show the action sheet for a long-pressed equipped slot.</summary>
    public void HandleEquippedSlotLongPress(EquipmentSlot slot, int itemId)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        var item = FindItemById(itemId);
        if (item == null) return;

        _actionSheet?.Show(item, isEquipped: true);
    }

    /// <summary>Show the action sheet for a long-pressed pack item in the equipment panel.</summary>
    public void HandlePackItemLongPress(int itemId)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        var item = FindItemById(itemId);
        if (item == null) return;

        _actionSheet?.Show(item, isEquipped: false);
    }

    /// <summary>
    /// Dispatch the selected action from the action sheet.
    /// </summary>
    private void OnActionSheetSelected(int itemId, ActionSheetAction action)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        var item = FindItemById(itemId);
        if (item == null) return;

        switch (action)
        {
            case ActionSheetAction.Use:
                // Tap-equivalent: drink potion, use scroll, etc.
                HandleInventoryTap(itemId);
                break;

            case ActionSheetAction.Throw:
                // Enter throw targeting mode — any tile is valid (not just monsters)
                EnterThrowTargeting(item);
                break;

            case ActionSheetAction.Drop:
                HandleDropRequest(itemId);
                break;

            case ActionSheetAction.Equip:
                HandleEquipRequest(itemId);
                break;

            case ActionSheetAction.Unequip:
            {
                // Find the slot this item is in and unequip it
                var equippable = item.Get<Equippable>();
                if (equippable != null)
                    HandleUnequipRequest(equippable.Slot);
                break;
            }
        }
    }

    /// <summary>
    /// Enter throw targeting mode for the given item.
    /// Any tile (walkable or with monster) is a valid target — you can throw at empty ground.
    /// On location chosen, fires PlayerAction.ThrowItem.
    /// </summary>
    private void EnterThrowTargeting(Entity item)
    {
        _pendingThrowItem = item;
        // Use Location targeting so any tile (walkable or occupied) is valid.
        // Range 10 = PoC fixed throw range.
        var spell = item.Get<SpellEffect>();
        EnterTargetingMode(new TargetingState
        {
            Item  = item,
            // Spell is required by TargetingState. Use the item's spell if present,
            // or a synthetic Self spell for non-spell items (junk, weapons).
            Spell = spell ?? new SpellEffect { SpellId = "_throw_placeholder", Targeting = TargetingMode.Location },
            Mode  = TargetingMode.Location,
            Range = 10,
        }, showGenericToast: false);
        string throwName = _state != null
            ? ItemDisplay.GetDisplayName(item, _state.IdentificationRegistry, _state.AppearancePool)
            : item.Name;
        _toastLog?.AddMessage($"Tap a tile to throw {throwName}. Tap yourself to cancel.");
    }

    /// <summary>
    /// Look up an item by ID from both inventory and equipment slots.
    /// Returns null if the item can't be found.
    /// </summary>
    private Entity? FindItemById(int itemId)
    {
        if (_state == null) return null;

        var inventory = _state.PlayerInventory;
        if (inventory != null)
        {
            var found = inventory.FindFirst(e => e.Id == itemId);
            if (found != null) return found;
        }

        // Check equipped slots
        var equipment = _state.Player.Get<Equipment>();
        if (equipment != null)
        {
            foreach (EquipmentSlot slot in Enum.GetValues<EquipmentSlot>())
            {
                var item = equipment.GetSlot(slot);
                if (item?.Id == itemId) return item;
            }
        }

        return null;
    }

    /// <summary>Returns true if the item is currently in any equipment slot.</summary>
    private bool IsItemEquipped(Entity item)
    {
        var equipment = _state?.Player.Get<Equipment>();
        if (equipment == null) return false;

        foreach (EquipmentSlot slot in Enum.GetValues<EquipmentSlot>())
        {
            if (equipment.GetSlot(slot)?.Id == item.Id) return true;
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>Enter targeting mode and notify the presentation.</summary>
    private void EnterTargetingMode(TargetingState targeting, bool showGenericToast = true)
    {
        Phase = GamePhase.Targeting;
        _input.EnterTargetingMode(targeting);
        if (showGenericToast)
        {
            string displayName = _state != null
                ? ItemDisplay.GetDisplayName(targeting.Item, _state.IdentificationRegistry, _state.AppearancePool)
                : targeting.Item.Name;
            _toastLog?.AddMessage($"Tap a target for {displayName}. Tap yourself to cancel.");
        }
        Diag.Log($"GameController: entered targeting mode for {targeting.Item.Name}");
    }

    /// <summary>Called when the player picks a single-target monster during targeting mode.</summary>
    private void OnTargetChosen(Entity item, Entity target)
    {
        Diag.Log($"OnTargetChosen: item={item.Name} target={target.Name}(id={target.Id})");
        Phase = GamePhase.WaitingForInput;
        OnActionChosen(PlayerAction.CastSpell(item, targetEntityId: target.Id));
    }

    /// <summary>Called when the player picks a location tile during targeting mode.</summary>
    private void OnLocationChosen(Entity item, int x, int y)
    {
        Diag.Log($"OnLocationChosen: item={item.Name} location=({x},{y})");
        Phase = GamePhase.WaitingForInput;

        // If we entered targeting from the throw action sheet, route to ThrowItem.
        if (_pendingThrowItem != null && _pendingThrowItem.Id == item.Id)
        {
            _pendingThrowItem = null;
            OnActionChosen(PlayerAction.ThrowItem(item, x, y));
            return;
        }

        OnActionChosen(PlayerAction.CastSpell(item, targetX: x, targetY: y));
    }

    /// <summary>Called when targeting is cancelled — no action, no turn consumed.</summary>
    private void OnTargetingCancelled()
    {
        Diag.Log("OnTargetingCancelled: returning to WaitingForInput");
        Phase = GamePhase.WaitingForInput;
        _pendingThrowItem = null; // clear any pending throw session

        // Portal wand: cancel pending entrance placement, remove sprite
        if (_pendingPortalWand != null && _state != null)
        {
            var cancelEvt = PortalSystem.CancelPendingEntrance(_pendingPortalWand, _state);
            if (cancelEvt != null)
            {
                PortalEntranceCancelled?.Invoke(cancelEvt.EntranceEntityId);
                _toastLog?.AddMessage("Portal cancelled.");
            }
            _pendingPortalWand = null;
        }
        else
        {
            _toastLog?.AddMessage("Cancelled.");
        }
    }

    /// <summary>
    /// Fired when a pending portal entrance is cancelled so the presentation can despawn its sprite.
    /// Carries the entrance entity ID.
    /// </summary>
    public event Action<int>? PortalEntranceCancelled;

    /// <summary>
    /// Find the closest alive, visible monster within the given range.
    /// Used for AutoClosest spell targeting.
    /// </summary>
    private Entity? FindClosestVisibleEnemy(int maxRange)
    {
        if (_state == null) return null;

        Entity? closest = null;
        double closestDist = maxRange > 0 ? maxRange + 1.0 : double.MaxValue;

        foreach (var monster in _state.AliveMonsters)
        {
            if (_state.IsDungeonMode && !_state.Map.IsVisible(monster.X, monster.Y))
                continue;

            double dist = _state.Player.DistanceTo(monster.X, monster.Y);
            if (dist < closestDist)
            {
                closest = monster;
                closestDist = dist;
            }
        }

        return closest;
    }

    /// <summary>
    /// Handle a tap on the drop button for an inventory item.
    /// Issues a Drop action, placing the item on the floor at the player's feet.
    /// </summary>
    public void HandleDropRequest(int itemId)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        var inventory = _state.PlayerInventory;
        if (inventory == null) return;
        var item = inventory.FindFirst(e => e.Id == itemId);
        if (item == null) return;
        OnActionChosen(PlayerAction.Drop(item));
    }

    /// <summary>
    /// Handle a tap on an In Pack item in the equipment panel.
    /// Issues an EquipItem action via TurnController.
    /// </summary>
    public void HandleEquipRequest(int itemId)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;

        var inventory = _state.PlayerInventory;
        if (inventory == null) return;

        var item = inventory.FindFirst(e => e.Id == itemId);
        if (item == null) return;

        OnActionChosen(PlayerAction.Equip(item));
    }

    /// <summary>
    /// Handle a tap on an occupied equipment slot in the equipment panel.
    /// Issues an UnequipItem action via TurnController.
    /// </summary>
    public void HandleUnequipRequest(EquipmentSlot slot)
    {
        if (_state == null || Phase != GamePhase.WaitingForInput) return;
        OnActionChosen(PlayerAction.Unequip(slot));
    }

    /// <summary>
    /// Cancel the active targeting operation. Called by the TargetingOverlay cancel button.
    /// Delegates to InputHandler.CancelTargeting which fires TargetingCancelled.
    /// No turn consumed.
    /// </summary>
    public void CancelTargeting()
    {
        if (Phase != GamePhase.Targeting) return;
        Diag.Log("GameController.CancelTargeting called");
        _input.CancelTargeting();
    }

    /// <summary>
    /// Forward raw tap position from the scene's _Input handler.
    /// Dismisses any open inspect panel before routing to normal input handling.
    /// </summary>
    public void HandleTap(Vector2 screenPos)
    {
        // Dismiss inspect panel on any normal tap — the player is acting, not inspecting.
        _inspectPanel?.Hide();
        _longPress?.Cancel();

        // Any tap cancels auto-explore or path-following. The current animation step
        // finishes naturally; OnAnimationComplete then finds nothing pending and returns
        // to WaitingForInput. Don't process the tap further — it was consumed by the cancel.
        if (_autoExploreMode || (_pendingPath != null && _pendingPath.Count > 0))
        {
            _autoExploreMode = false;
            _pendingPath = null;
            _animator!.SpeedMultiplier = 1.0f;
            return;
        }

        _input.HandleTap(screenPos);
    }

    /// <summary>
    /// Handle a long-press or stationary hover at the given screen position.
    /// Checks for a monster or floor item at that tile and shows the inspect panel.
    /// </summary>
    private void OnLongPress(Vector2 screenPos)
    {
        if (_state == null) return;

        // Apply the same ToLocal() transform that Main._UnhandledInput applies before HandleTap.
        // Without this, OnLongPress was passing raw screen coordinates to ScreenToGrid, which
        // expects GameView-local coordinates — causing long-press to resolve the wrong tile.
        var localPos = _gameView != null ? _gameView.ToLocal(screenPos) : screenPos;
        var (gridX, gridY) = _renderer.ScreenToGrid(localPos);

        if (!_state.Map.InBounds(gridX, gridY))
            return;

        // Check for a monster at this tile first (takes priority over floor items)
        var monster = _state.AliveMonsters.FirstOrDefault(m => m.X == gridX && m.Y == gridY);
        if (monster != null)
        {
            var speciesTag = monster.Get<Logic.ECS.SpeciesTag>();
            if (speciesTag != null)
            {
                // Look up the MonsterDefinition from the monster factory for stat label computation.
                // If no factory is available, show a minimal view using just the knowledge entry.
                if (_monsterFactory != null && _monsterFactory.TryGetDefinition(speciesTag.TypeId, out var def) && def != null)
                {
                    var info = _state.Knowledge.GetInfoView(speciesTag.TypeId, def);
                    _inspectPanel?.ShowMonster(info);
                    _inspectPanel?.PositionNear(screenPos, GetViewport()?.GetVisibleRect().Size ?? new Vector2(480, 854));
                    return;
                }
            }
        }

        // Check for a floor item at this tile
        var floorItem = _state.FloorItems.FirstOrDefault(i => i.X == gridX && i.Y == gridY);
        if (floorItem != null)
        {
            var itemInfo = ItemInspectView.From(floorItem);
            _inspectPanel?.ShowItem(itemInfo);
            _inspectPanel?.PositionNear(screenPos, GetViewport()?.GetVisibleRect().Size ?? new Vector2(480, 854));
            return;
        }

        // Nothing of interest at this tile — hide any existing panel
        _inspectPanel?.Hide();
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

            var reason = _state.Player.Get<AutoExploreState>()?.StopReason;
            if (reason != null)
                _toastLog?.AddMessage($"[color=#aaaaaa]Explore: {reason}[/color]");

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
                    _state.Player,
                    canPassDoors: true);

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
    private void ExecuteTurn(PlayerAction action)
    {
        Phase = GamePhase.Processing;
        _input.SetAcceptingInput(false);

        Diag.Log($"ExecuteTurn START action={action.Kind}");
        Diag.Event("ExecuteTurn", new { action = action.Kind.ToString(), turnCount = _state!.TurnCount });
        Diag.Mem("  pre-ProcessTurn");

        var result = TurnController.ProcessTurn(_state!, action, _monsterFactory,
            portalEntityFactory: _portalEntityFactory);
        Diag.Log($"  ProcessTurn done: {result.Events.Count} events, gameOver={result.GameOver}");
        foreach (var evt in result.Events)
            Diag.Log($"    evt: {evt.GetType().Name}");
        Diag.Mem("  post-ProcessTurn");

        Diag.Log("  -> TurnCompleted");
        TurnCompleted?.Invoke(result);
        Diag.Log("  <- TurnCompleted");

        // Single pass over events — avoids 5 separate LINQ allocations per turn.
        bool inventoryChanged = false;
        bool equipmentChanged = false;
        bool identificationChanged = false;
        _pendingDescend = null;
        foreach (var evt in result.Events)
        {
            if (evt is DeathEvent dead)
                _entitySprites?.RemoveEntity(dead.ActorId);
            else if (evt is IdentificationEvent)
                { inventoryChanged = true; identificationChanged = true; }
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
            else if (evt is ThrowEvent throwEvt)
            {
                inventoryChanged = true;
                // Weapons/junk land on the ground — spawn a floor sprite at the landing tile.
                if (throwEvt.ItemLandsOnGround)
                {
                    var landed = _state!.FloorItems.FirstOrDefault(i => i.Id == throwEvt.ItemId);
                    if (landed != null) _itemSprites?.CreateSprite(landed);
                }
            }
            else if (evt is EquipEvent or UnequipEvent)
                { inventoryChanged = true; equipmentChanged = true; }
            else if (evt is DescendEvent desc)
                _pendingDescend = desc;
        }

        // Re-sync floor item visibility: CreateSprite sets Visible=false by default, but
        // TurnCompleted (in Main.cs) ran UpdateVisibility before the event loop above. Any
        // sprites created by DropEvent/ThrowEvent during that loop would never be shown.
        _itemSprites?.UpdateVisibility(_state!);

        // Handle split and corrosion toast messages
        foreach (var evt in result.Events)
        {
            if (evt is SplitEvent splitEvt)
            {
                // Remove the original sprite and spawn sprites for all children
                _entitySprites?.RemoveEntity(splitEvt.OriginalId);
                foreach (var childId in splitEvt.ChildIds)
                {
                    var child = _state!.Monsters.FirstOrDefault(m => m.Id == childId);
                    if (child != null) _entitySprites?.SpawnMonster(child);
                }
            }
            else if (evt is CorrosionEvent corrEvt)
            {
                // Orange corrosion toast: "The Slime corrodes your Dagger! [75%]"
                int pct = corrEvt.BaseDamageMax > 0
                    ? (int)Math.Round((double)corrEvt.NewDamageMax / corrEvt.BaseDamageMax * 100)
                    : 100;
                _toastLog?.AddMessage(
                    $"[color=#ff8800]The {corrEvt.MonsterName} corrodes your {corrEvt.WeaponName}! [{pct}%][/color]");
                equipmentChanged = true; // weapon stats changed — refresh equipment panel
            }
        }

        if (identificationChanged)
            _itemSprites?.RefreshIdentifiedSprites(_state!);
        if (inventoryChanged)
            _inventoryPanel?.Refresh(_state!);
        if (equipmentChanged && _equipmentPanel?.Visible == true)
            _equipmentPanel?.Refresh(_state!);

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

        // Auto-continue portal placement: if the entrance was just placed this turn,
        // immediately enter step-2 targeting so the player picks the exit without
        // having to tap the wand again. _pendingPortalWand persists from step 1.
        if (_pendingPortalWand != null &&
            PortalSystem.GetPortalCastStep(_pendingPortalWand) == PortalCastStep.EntrancePlaced)
        {
            var spell = _pendingPortalWand.Get<SpellEffect>();
            if (spell != null)
            {
                EnterTargetingMode(new TargetingState
                {
                    Item  = _pendingPortalWand,
                    Spell = spell,
                    Mode  = TargetingMode.Location,
                    Range = 0,
                }, showGenericToast: false);
                _toastLog?.AddMessage("Portal entrance placed. Tap a tile for the exit. Tap yourself to cancel.");
                Diag.Log("  OAC: PortalStep2Targeting");
                return;
            }
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
