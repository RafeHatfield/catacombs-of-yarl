using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Root node for the game. Loads a scenario, creates GameState, renders the
/// dungeon and entities. Currently a static proof-of-life — no input or turns yet.
/// </summary>
public partial class Main : Node
{
    private GameState? _state;
    private EntitySpriteManager? _entitySprites;

    public override void _Ready()
    {
        GD.Print("Catacombs of YARL — loading...");

        // Load content from YAML
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

        // Create game state
        _state = GameStateFactory.FromScenario(scenario, 1337, monsterFactory, itemFactory, consumableFactory);

        // Get scene tree nodes
        var gameView = GetNode<Node2D>("GameView");
        var tileMapLayer = GetNode<Node2D>("GameView/TileMapLayer");
        var entityLayer = GetNode<Node2D>("GameView/EntityLayer");

        // Render dungeon
        DungeonRenderer.Render(_state.Map, tileMapLayer);

        // Render entities
        _entitySprites = new EntitySpriteManager(entityLayer);
        _entitySprites.Initialize(_state);

        // Center camera on the map
        CenterView(gameView);

        GD.Print($"Rendered {_state.Map.Width}x{_state.Map.Height} arena with {_state.Monsters.Count} monsters.");
    }

    /// <summary>
    /// Center the GameView so the iso map is centered in the viewport.
    /// The iso grid extends both left and right of origin.
    /// </summary>
    private void CenterView(Node2D gameView)
    {
        if (_state == null) return;

        var viewport = GetViewport().GetVisibleRect().Size;
        int mapW = _state.Map.Width;
        int mapH = _state.Map.Height;

        // Calculate bounding box of the iso grid
        var topLeft = IsometricMapper.GridToScreen(0, mapH - 1);
        var topRight = IsometricMapper.GridToScreen(mapW - 1, 0);
        var bottomLeft = IsometricMapper.GridToScreen(0, 0);
        var bottomRight = IsometricMapper.GridToScreen(mapW - 1, mapH - 1);

        float minX = Mathf.Min(topLeft.X, bottomLeft.X);
        float maxX = Mathf.Max(topRight.X, bottomRight.X) + IsometricMapper.TileWidth;
        float minY = Mathf.Min(topRight.Y, topLeft.Y);
        float maxY = Mathf.Max(bottomRight.Y, bottomLeft.Y) + IsometricMapper.TileHeight;

        float mapPixelW = maxX - minX;
        float mapPixelH = maxY - minY;

        // Center in viewport, leaving room for UI (HUD at top, combat log at bottom)
        float uiTopMargin = 130f;
        float uiBottomMargin = 210f;
        float availableH = viewport.Y - uiTopMargin - uiBottomMargin;

        // Scale to fit
        float scale = Mathf.Min(viewport.X / mapPixelW, availableH / mapPixelH);
        scale = Mathf.Min(scale, 3.0f); // Cap at 3x for pixel art

        gameView.Scale = new Vector2(scale, scale);

        float offsetX = (viewport.X - mapPixelW * scale) / 2f - minX * scale;
        float offsetY = uiTopMargin + (availableH - mapPixelH * scale) / 2f - minY * scale;
        gameView.Position = new Vector2(offsetX, offsetY);
    }
}
