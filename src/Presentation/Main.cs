using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Root scene node. Loads content, creates GameState, initialises all
/// presentation systems, and routes input to the GameController.
/// </summary>
public partial class Main : Node
{
    private GameController? _gameController;
    private Node2D? _gameView;

    public override void _Ready()
    {
        GD.Print("Catacombs of YARL — loading...");

        var loader = new ContentLoader();
        var projectRoot = ProjectSettings.GlobalizePath("res://");
        var entitiesPath = System.IO.Path.Combine(projectRoot, "config", "entities.yaml");
        var scenarioPath = System.IO.Path.Combine(projectRoot, "config", "levels", "scenario_depth1_tuned.yaml");

        if (!System.IO.File.Exists(entitiesPath))
        {
            GD.PrintErr($"entities.yaml not found at: {entitiesPath}");
            return;
        }

        var content = loader.LoadAllFromFile(entitiesPath);
        var scenario = loader.LoadScenarioFromFile(scenarioPath);

        var entityFactory = new EntityFactory();
        var itemFactory = new ItemFactory(content.Items, entityFactory);
        var monsterFactory = new MonsterFactory(content.Monsters, entityFactory, itemFactory);
        var consumableFactory = new ConsumableFactory(content.Consumables, entityFactory);

        var state = GameStateFactory.FromScenario(scenario, 1337, monsterFactory, itemFactory, consumableFactory);

        _gameView = GetNode<Node2D>("GameView");
        var tileMapLayer = GetNode<Node2D>("GameView/TileMapLayer");
        var entityLayer = GetNode<Node2D>("GameView/EntityLayer");

        // Render dungeon tiles
        DungeonRenderer.Render(state.Map, tileMapLayer);

        // Set up entity sprites
        var entitySprites = new EntitySpriteManager(entityLayer);
        entitySprites.Initialize(state);

        // Centre and scale the view
        CenterView(_gameView, state.Map);

        // Set up game controller
        _gameController = new GameController();
        AddChild(_gameController);
        _gameController.Initialize(state, entitySprites, this);
        _gameController.GameEnded += OnGameEnded;

        GD.Print($"Ready. {state.Monsters.Count} monsters. Tap to play.");
    }

    public override void _Input(InputEvent @event)
    {
        if (_gameController == null || _gameView == null) return;

        // Handle touch or left mouse click
        Vector2? screenPos = null;

        if (@event is InputEventScreenTouch touch && touch.Pressed)
            screenPos = touch.Position;
        else if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
            screenPos = mb.Position;

        if (screenPos.HasValue)
        {
            // Transform from viewport coords to GameView local coords for IsometricMapper
            var localPos = _gameView.ToLocal(screenPos.Value);
            _gameController.HandleTap(localPos);
        }
    }

    private void OnGameEnded(bool playerWon)
    {
        GD.Print(playerWon ? "Victory!" : "Defeated.");
        // Phase 5 will show a proper game over screen
    }

    private static void CenterView(Node2D gameView, GameMap map)
    {
        var viewport = gameView.GetViewport().GetVisibleRect().Size;

        var topLeft   = IsometricMapper.GridToScreen(0, map.Height - 1);
        var topRight  = IsometricMapper.GridToScreen(map.Width - 1, 0);
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
