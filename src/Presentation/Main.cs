using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using CatacombsOfYarl.Presentation.UI;
using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Root scene node. Loads content, creates GameState, initialises all
/// presentation systems, and routes input to the GameController.
/// </summary>
public partial class Main : Node
{
    private GameController? _gameController;
    private GameState? _state;
    private Node2D? _gameView;
    private HUD? _hud;
    private CombatLog? _combatLog;
    private GameOverScreen? _gameOverScreen;

    // Stats accumulation for game-over screen
    private int _turnCount;
    private int _monstersKilled;
    private int _damageDealt;
    private int _damageTaken;

    public override void _Ready()
    {
        GD.Print("Catacombs of YARL — loading...");
        LoadAndStart();
    }

    private void LoadAndStart()
    {
        // Reset stats
        _turnCount = 0;
        _monstersKilled = 0;
        _damageDealt = 0;
        _damageTaken = 0;

        var loader = new ContentLoader();
        var projectRoot = ProjectSettings.GlobalizePath("res://");
        var entitiesPath = System.IO.Path.Combine(projectRoot, "config", "entities.yaml");
        var scenarioPath = System.IO.Path.Combine(projectRoot, "config", "levels", "scenario_depth1_tuned.yaml");

        var content = loader.LoadAllFromFile(entitiesPath);
        var scenario = loader.LoadScenarioFromFile(scenarioPath);

        var entityFactory = new EntityFactory();
        var itemFactory = new ItemFactory(content.Items, entityFactory);
        var monsterFactory = new MonsterFactory(content.Monsters, entityFactory, itemFactory);
        var consumableFactory = new ConsumableFactory(content.Consumables, entityFactory);

        _state = GameStateFactory.FromScenario(scenario, 1337, monsterFactory, itemFactory, consumableFactory);

        // Get scene nodes
        _gameView = GetNode<Node2D>("GameView");
        var tileMapLayer = GetNode<Node2D>("GameView/TileMapLayer");
        var entityLayer = GetNode<Node2D>("GameView/EntityLayer");
        var uiLayer = GetNode<CanvasLayer>("UILayer");
        var hudNode = GetNode<Control>("UILayer/HUD");
        var combatLogNode = GetNode<Control>("UILayer/CombatLog");

        // Clear any previous render
        foreach (var child in tileMapLayer.GetChildren()) child.QueueFree();
        foreach (var child in entityLayer.GetChildren()) child.QueueFree();
        foreach (var child in hudNode.GetChildren()) child.QueueFree();
        foreach (var child in combatLogNode.GetChildren()) child.QueueFree();

        // Render dungeon
        DungeonRenderer.Render(_state.Map, tileMapLayer);

        // Entity sprites
        var entitySprites = new EntitySpriteManager(entityLayer);
        entitySprites.Initialize(_state);

        // HUD
        _hud = new HUD();
        hudNode.AddChild(_hud);
        _hud.SetState(_state);

        // Combat log
        _combatLog = new CombatLog();
        combatLogNode.AddChild(_combatLog);
        _combatLog.SetPlayerId(_state.Player.Id);

        // Game over screen (floating above everything)
        if (_gameOverScreen == null)
        {
            _gameOverScreen = new GameOverScreen();
            uiLayer.AddChild(_gameOverScreen);
            _gameOverScreen.ReplayRequested += OnReplayRequested;
        }
        else
        {
            _gameOverScreen.Visible = false;
        }

        CenterView(_gameView, _state.Map);

        // Game controller
        if (_gameController != null)
        {
            _gameController.TurnCompleted -= OnTurnCompleted;
            _gameController.GameEnded -= OnGameEnded;
            _gameController.QueueFree();
        }
        _gameController = new GameController();
        AddChild(_gameController);
        _gameController.Initialize(_state, entitySprites, this);
        _gameController.TurnCompleted += OnTurnCompleted;
        _gameController.GameEnded += OnGameEnded;

        GD.Print($"Ready — {_state.Monsters.Count} monsters. Tap to play.");
    }

    public override void _Input(InputEvent @event)
    {
        if (_gameController == null || _gameView == null) return;

        Vector2? screenPos = null;
        if (@event is InputEventScreenTouch touch && touch.Pressed)
            screenPos = touch.Position;
        else if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
            screenPos = mb.Position;

        if (screenPos.HasValue)
        {
            var localPos = _gameView.ToLocal(screenPos.Value);
            _gameController.HandleTap(localPos);
        }
    }

    private void OnTurnCompleted(TurnResult result)
    {
        if (_state == null) return;

        // Accumulate stats
        _turnCount = _state.TurnCount;
        foreach (var evt in result.Events)
        {
            if (evt is AttackEvent atk)
            {
                if (atk.ActorId == _state.Player.Id && atk.Hit) _damageDealt += atk.Damage;
                else if (atk.TargetId == _state.Player.Id && atk.Hit) _damageTaken += atk.Damage;
                if (atk.TargetKilled && atk.ActorId == _state.Player.Id) _monstersKilled++;
            }
        }

        _hud?.Refresh();
        _combatLog?.RecordTurn(result, _state);
    }

    private void OnGameEnded(bool playerWon)
    {
        var stats = $"Turns: {_turnCount}\nMonsters killed: {_monstersKilled}\n" +
                    $"Damage dealt: {_damageDealt}\nDamage taken: {_damageTaken}";
        _gameOverScreen?.Show(playerWon, stats);
    }

    private void OnReplayRequested()
    {
        LoadAndStart();
    }

    private static void CenterView(Node2D gameView, GameMap map)
    {
        var viewport = gameView.GetViewport().GetVisibleRect().Size;

        var topLeft    = IsometricMapper.GridToScreen(0, map.Height - 1);
        var topRight   = IsometricMapper.GridToScreen(map.Width - 1, 0);
        var bottomRight = IsometricMapper.GridToScreen(map.Width - 1, map.Height - 1);

        float minX = topLeft.X;
        float maxX = topRight.X + IsometricMapper.TileWidth;
        float minY = topRight.Y;
        float maxY = bottomRight.Y + IsometricMapper.TileHeight;

        float mapPixelW = maxX - minX;
        float mapPixelH = maxY - minY;

        float uiTopMargin = 130f;
        float uiBottomMargin = 210f;
        float availableH = viewport.Y - uiTopMargin - uiBottomMargin;

        float scale = Mathf.Min(viewport.X / mapPixelW, availableH / mapPixelH);
        scale = Mathf.Min(scale, 3.0f);

        gameView.Scale = new Vector2(scale, scale);
        gameView.Position = new Vector2(
            (viewport.X - mapPixelW * scale) / 2f - minX * scale,
            uiTopMargin + (availableH - mapPixelH * scale) / 2f - minY * scale
        );
    }
}
