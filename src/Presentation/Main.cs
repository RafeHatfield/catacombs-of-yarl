using System.Linq;
using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Persistence;
using CatacombsOfYarl.Logic.Persistence.Namespaces;
using CatacombsOfYarl.Presentation.Animation;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using CatacombsOfYarl.Presentation.Persistence;
using CatacombsOfYarl.Presentation.UI;
using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Root scene node. Loads content, creates GameState, initialises all
/// presentation systems, and routes input to the GameController.
///
/// Two entry paths:
///   LoadAndStart() — loads a scenario YAML (existing harness/dev path, still the default).
///   StartDungeon(depth) — procedural dungeon via DungeonFloorBuilder (new campaign path).
///
/// Factories are created once in _Ready via InitFactories() and reused across floor
/// transitions. LoadAndStart was previously re-creating them every call — that worked
/// for scenarios (single floor) but is wrong for dungeon mode where Build() is called
/// repeatedly on the same DungeonFloorBuilder.
/// </summary>
public partial class Main : Node
{
    private GameController? _gameController;
    private GameState? _state;
    private Node2D? _gameView;
    private HUD? _hud;
    private ToastLog? _toastLog;
    private GameOverScreen? _gameOverScreen;
    private QuickSlotBar? _inventoryPanel;
    private EquipmentPanel? _equipmentPanel;
    private MenuButtonBar? _menuButtonBar;
    // Stored as field so SetupPresentation can call SetGameState after each floor build.
    private DebugOverlay? _debugOverlay;
    private RectDebugDraw? _rectDebugDraw;

    // Fog-of-war: tile layer tracks sprites for per-turn visibility updates
    private TileLayer? _tileLayer;
    // Tile map parent node — needed to add door overlay sprites on SecretDoorFoundEvent.
    private Node2D? _tileMapLayer;
    // Entity sprite manager is stored here so OnTurnCompleted can call UpdateVisibility
    private EntitySpriteManager? _entitySprites;
    // Item sprite manager tracks floor item overlay sprites
    private ItemSpriteManager? _itemSprites;
    // Ground hazard overlay — persistent tile tints for burning/poison ground.
    private GroundHazardOverlay? _groundHazardOverlay;
    // Floating HP bars — small red bars above damaged enemy sprites (Phase 4).
    private FloatingHpBarManager? _floatingHpBars;

    // Tileset-backed sprite mapping — created once at boot, shared across all floors.
    private SpriteMapping? _spriteMapping;

    // Tile theme config — loaded once at boot, passed to DungeonRenderer.Render on every floor.
    // Covers dungeon tile assets (floors, walls, stairs, decorations). Does not change per floor.
    private TileThemeConfig? _tileThemeConfig;

    // Map renderer — created once at boot, injected into all presentation consumers.
    private IMapRenderer _renderer = new TopDownRenderer(); // safe default until _Ready

    // --- Factories (created once, reused across floor transitions) ---
    private ContentLoader? _contentLoader;
    private MonsterFactory? _monsterFactory;
    private ItemFactory? _itemFactory;
    private ConsumableFactory? _consumableFactory;
    private SpellItemFactory? _spellItemFactory;
    private EntityFactory? _entityFactory;
    private DungeonFloorBuilder? _floorBuilder;
    private LevelTemplateRegistry? _levelTemplates;
    // Set while running a test scenario so floor transitions reuse the same guaranteed spawns.
    private DungeonFloorBuilder? _testScenarioBuilder;

    // Map drag-to-pan state
    private bool _isDragging;
    private bool _dragStartRecorded; // true only when _UnhandledInput saw the matching DOWN event
    private Vector2 _dragStartScreenPos;
    private Vector2 _cameraPositionAtDragStart;

    // Bot mode (debug builds only) — never instantiated in release builds.
    private CatacombsOfYarl.Presentation.Bot.BotPlayerDriver? _botDriver;
    private CatacombsOfYarl.Presentation.Bot.BotModeHud? _botHud;
    private static readonly string[] BotPersonaCycle = ["balanced", "cautious", "aggressive", "greedy", "speedrunner"];
    private static readonly float[] BotSpeedCycle = [1.0f, 0.5f, 0.25f, 0.1f, 0.0f];
    private int _botPersonaIdx;
    private int _botSpeedIdx;
    private const float DragThreshold = 10f; // pixels before drag mode activates

    // VFX overlay — spell and status visual effects. Created once per floor setup.
    private VfxOverlay? _vfxOverlay;

    // Active portal sprites keyed by entity ID. Spawned on PortalPlacedEvent,
    // despawned on PortalRemovedEvent / PortalEntranceCancelledEvent.
    private readonly Dictionary<int, Sprite2D> _portalSprites = new();

    // Tracked tap indicators — alpha lerped in _Process, no Tween involved.
    // SpawnTime is when the indicator appeared; fade starts after FadeDelay seconds.
    // CanvasItem covers both ColorRect (top-down) and any future Sprite2D variant.
    private readonly List<(CanvasItem Node, double SpawnTime)> _tapIndicators = new();
    private const double TapFadeDelay    = 0.15; // seconds at full alpha before fade starts
    private const double TapFadeDuration = 0.35; // seconds to fade to zero

    // Minimap and zoom — zoom limits come from the renderer after boot
    private MiniMap? _miniMap;
    // Msg button — created once, anchored to bottom-left of ViewportOverlay (Phase 5).
    private MsgButton? _msgButton;
    // Message log panel — full-screen overlay opened by Msg button (Phase 6.2).
    private MessageLogPanel? _messageLogPanel;
    // Status effect badge row — created once, anchored to top-left of ViewportOverlay (Phase 5).
    // Hides itself when the player has no active effects, so no viewport clutter during normal play.
    private StatusEffectBar? _statusEffectBar;
    private float _currentZoom;   // initialised in _Ready after renderer is created
    private const float ZoomStep = 0.5f;

    // Dungeon run state
    private int _baseSeed = 1337;
    private int _currentDepth = 1;

    // --art-scene-capture state (tools/art_lint/capture_scene.py driver).
    // Set true in _Ready when the flag is present; consumed in _Process once the
    // post-SetupPresentation camera snap (_pendingCameraSnapFrames) has settled to 0.
    private bool _pendingCapture;
    private string? _captureOutputPath;
    private int _captureSettleBuffer = 2; // extra idle frames after camera-snap settles

    // Cross-run persistence — loaded once at app start, flushed at narrative-event boundaries.
    private GodotPersistencePathProvider? _persistenceProvider;
    private PersistentRunState? _persistentState;

    // Mid-run save/resume (M1.4 4b): off-critical-path autosave every turn + on descent/pause,
    // deleted on run-end (record-then-delete), silently resumed at startup. Dungeon mode only.
    private Logic.Persistence.MidRun.MidRunAutosaveWriter? _midRunWriter;
    private Dictionary<int, Logic.Balance.BoonDefinition>? _boonTable;   // for LoadMidRun (RECONSTRUCT-class)
    // Daily-seed sibling file — loaded once at app start, separate from character state.
    private DailySeedsFile? _dailySeeds;

    // Voice line registry — loaded once, shared across all turns.
    // Null until InitFactories succeeds; VoiceLineEvent handling is a no-op when null.
    private VoiceLineRegistry? _voiceLineRegistry;
    private Logic.Content.WeighingAuditRegistry? _weighingAuditRegistry;
    // Tracks which trigger IDs have already fired their canonical (first) line this run.
    private readonly HashSet<string> _voiceLineFiredSet = new();

    // Under-Warden memo delivery — registry loaded once at boot alongside voice lines.
    // Evaluator is stateless; _memoRegistry is null until InitFactories succeeds.
    private MemoRegistry? _memoRegistry;
    private readonly MemoDeliveryEvaluator _memoEvaluator = new();

    // Inbox panel — created once alongside _gameOverScreen; shown after run ends when
    // PendingMemos is non-empty.
    private MemoInboxPanel? _memoInboxPanel;

    // Stats accumulation for game-over screen
    private int _turnCount;
    private int _monstersKilled;
    private int _damageDealt;
    private int _damageTaken;

    public override void _Ready()
    {
        // --art-scene-capture at a specific logical resolution: project.godot's stretch mode
        // (canvas_items / keep_width / integer) keeps the render canvas pinned to the
        // project's base viewport size (720x1280) regardless of --resolution, which only
        // resizes the OS window around that fixed canvas. ContentScaleSize overrides the
        // base canvas size itself for this run only — no change to project.godot, no effect
        // outside a capture run. Must happen before any viewport-size-dependent setup below
        // (renderer creation, camera math) so everything sees the final size from frame 0.
        if (ReadArtSceneCaptureResolution(out var captureWidth, out var captureHeight))
            GetTree().Root.ContentScaleSize = new Vector2I(captureWidth, captureHeight);

        GD.Print("Catacombs of YARL — loading...");
        Diag.Init();

        // Load cross-run persistence. Missing file → fresh defaults (no write until first dirty flush).
        _persistenceProvider = new GodotPersistencePathProvider();
        _midRunWriter = new Logic.Persistence.MidRun.MidRunAutosaveWriter(
            _persistenceProvider.GetMidRunSaveFilePath(), GD.PrintErr);
        _persistentState = PersistentRunState.LoadFromDisk(_persistenceProvider, GD.PrintErr);
        _dailySeeds = PersistentRunState.LoadDailySeedsFromDisk(_persistenceProvider, GD.PrintErr);
        GD.Print($"[Main] Persistence loaded — {_persistentState.RunCounter.TotalRuns} runs ever.");

        InitSpriteMapping();
        _tileThemeConfig = TileThemeLoader.LoadWithFallback();
        if (_tileThemeConfig.Themes.Count == 0)
            GD.PrintErr("[Main] TileThemeConfig loaded with no themes — dungeon tiles will not render. Check config/tile_themes.yaml.");
        _renderer = CreateRenderer(ReadMapMode());
        _currentZoom = _renderer.DefaultZoom;
        GD.Print($"[Main] Map renderer: {_renderer.GetType().Name} (zoom default={_renderer.DefaultZoom}, min={_renderer.MinZoom}, max={_renderer.MaxZoom})");
        InitFactories();

        // --art-scene: dev/debug launch flag (same convention as --tileset/--map-mode) that
        // boots directly into the fixed art-acceptance test scene instead of the main menu.
        // See ArtAcceptanceSceneBuilder (Logic layer) for the authored floor data.
        //
        // --art-scene-capture --capture-out <path>: same boot path (reuses
        // LaunchArtAcceptanceScene — no parallel boot logic), but additionally captures the
        // settled viewport to a PNG and quits. Driven by tools/art_lint/capture_scene.py.
        if (ReadArtSceneCaptureFlag(out var captureOutputPath))
        {
            _pendingCapture = true;
            _captureOutputPath = captureOutputPath;
            LaunchArtAcceptanceScene();
        }
        else if (ReadArtSceneFlag())
        {
            LaunchArtAcceptanceScene();
        }
        else
        {
            // Silent resume of a valid mid-run save, else the normal menu/new-game flow.
            ResumeOrShowMenu();
        }

        // Debug overlay: only created in editor/debug builds — zero cost in release.
        // Stored as a field so SetupPresentation can wire it to the current floor's objects.
        if (OS.IsDebugBuild())
        {
            _debugOverlay = new DebugOverlay();
            _debugOverlay.Visible = ReadDebugOverlayVisible();
            GetNode<CanvasLayer>("UILayer").AddChild(_debugOverlay);

            _rectDebugDraw = new RectDebugDraw();
            _rectDebugDraw.Visible = false;
            _rectDebugDraw.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
            _rectDebugDraw.MouseFilter = Control.MouseFilterEnum.Ignore;
            GetNode<CanvasLayer>("UILayer").AddChild(_rectDebugDraw);

            // Sprite browser — only for index-based tilesets (16bf etc.). F8 to toggle.
            if (_spriteMapping?.IsIndexBased == true)
            {
                var browser = new UI.SpriteBrowser(_spriteMapping);
                GetNode<CanvasLayer>("UILayer").AddChild(browser);
            }
        }
    }

    public override void _Process(double delta)
    {
        // Re-snap camera for the first N frames after SetupPresentation. Running each frame
        // handles layout settling after the MenuLayer hides — GetVisibleRect() can report a
        // plausible but stale size on the first frame before Godot has processed the change.
        if (_pendingCameraSnapFrames > 0)
        {
            _pendingCameraSnapFrames--;
            _DoInitialCameraSnap();
        }

        // --art-scene-capture: wait for the camera-snap sequence above to fully settle
        // (_pendingCameraSnapFrames reaches 0), then a couple more idle frames as a buffer
        // against any one-frame-late layout settling, then capture and quit.
        if (_pendingCapture && _pendingCameraSnapFrames == 0)
        {
            if (_captureSettleBuffer > 0)
                _captureSettleBuffer--;
            else
                CaptureAndQuit();
        }

        // Animate and clean up tap indicators entirely in _Process — no Tween involved,
        // so no tween holds a reference to the sprite after it's freed.
        double now = Time.GetTicksMsec() / 1000.0;
        for (int i = _tapIndicators.Count - 1; i >= 0; i--)
        {
            var (node, spawnTime) = _tapIndicators[i];

            // Guard: node may have been freed if the floor transitioned while it was alive.
            if (!GodotObject.IsInstanceValid(node))
            {
                _tapIndicators.RemoveAt(i);
                continue;
            }

            double age = now - spawnTime;
            double fadeStart = TapFadeDelay;
            double fadeEnd   = TapFadeDelay + TapFadeDuration;

            if (age >= fadeEnd)
            {
                node.SafeFree();
                _tapIndicators.RemoveAt(i);
            }
            else if (age >= fadeStart)
            {
                float t = (float)((age - fadeStart) / TapFadeDuration);
                var m = node.Modulate;
                node.Modulate = new Color(m.R, m.G, m.B, 1f - t);
            }
        }
    }

    /// <summary>
    /// Load the active tileset config and create the SpriteMapping instance.
    /// Priority: --tileset CLI arg → game_settings.yaml → default "ultimate_fantasy".
    /// Called once from _Ready before InitFactories.
    /// </summary>
    private void InitSpriteMapping()
    {
        var tilesetId = ReadTilesetId();
        GD.Print($"[Main] Loading tileset: {tilesetId}");
        var config = TilesetLoader.LoadWithFallback(tilesetId);
        _spriteMapping = new SpriteMapping(config);
        GD.Print($"[Main] Tileset loaded: {config.Name} ({config.SpriteSize}px, {config.FrameCount} frames)");
    }

    /// <summary>
    /// Determine which tileset ID to load.
    /// Checks CLI args first (--tileset &lt;id&gt;), then game_settings.yaml, then defaults to ultimate_fantasy.
    /// </summary>
    private static string ReadTilesetId()
    {
        // 1. Check --tileset CLI arg (dev override — no file edit needed to switch)
        var args = OS.GetCmdlineArgs();
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == "--tileset")
                return args[i + 1];
        }

        // 2. Check config/game_settings.yaml
        const string settingsPath = "res://config/game_settings.yaml";
        try
        {
            using var file = Godot.FileAccess.Open(settingsPath, Godot.FileAccess.ModeFlags.Read);
            if (file != null)
            {
                var text = file.GetAsText();
                // Simple line-by-line parse — only need the single `tileset:` field.
                // Full YamlDotNet deserialization is overkill for one string value.
                foreach (var line in text.Split('\n'))
                {
                    var trimmed = line.TrimStart();
                    if (!trimmed.StartsWith("tileset:", System.StringComparison.Ordinal)) continue;

                    var value = trimmed["tileset:".Length..].Trim();
                    // Strip surrounding quotes if present
                    if (value.Length >= 2 && value[0] == '"' && value[^1] == '"')
                        value = value[1..^1];
                    if (value.Length > 0) return value;
                }
            }
        }
        catch (System.Exception ex)
        {
            // game_settings.yaml is optional — log and continue to default
            GD.PrintErr($"[Main] Failed to read game_settings.yaml: {ex.Message}");
        }

        // 3. Default
        return "ultimate_fantasy";
    }

    /// <summary>
    /// Determine which map renderer mode to use.
    /// Checks CLI args first (--map-mode &lt;mode&gt;), then game_settings.yaml, then defaults to "iso".
    /// </summary>
    private static string ReadMapMode()
    {
        // 1. Check --map-mode CLI arg (dev override)
        var args = OS.GetCmdlineArgs();
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == "--map-mode")
                return args[i + 1];
        }

        // 2. Check config/game_settings.yaml
        const string settingsPath = "res://config/game_settings.yaml";
        try
        {
            using var file = Godot.FileAccess.Open(settingsPath, Godot.FileAccess.ModeFlags.Read);
            if (file != null)
            {
                var text = file.GetAsText();
                foreach (var line in text.Split('\n'))
                {
                    var trimmed = line.TrimStart();
                    if (!trimmed.StartsWith("map_mode:", System.StringComparison.Ordinal)) continue;

                    var value = trimmed["map_mode:".Length..].Trim();
                    if (value.Length >= 2 && value[0] == '"' && value[^1] == '"')
                        value = value[1..^1];
                    if (value.Length > 0) return value;
                }
            }
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[Main] Failed to read map_mode from game_settings.yaml: {ex.Message}");
        }

        // 3. Default
        return "iso";
    }

    /// <summary>
    /// --art-scene: dev launch flag that boots directly into the fixed art-acceptance test
    /// scene (docs/art_test_scene_spec_v2.md), bypassing the main menu. Same CLI-arg convention
    /// as --tileset/--map-mode. No game_settings.yaml fallback — this is a one-shot debug
    /// launch mode, not a persistent setting.
    /// </summary>
    private static bool ReadArtSceneFlag()
    {
        var args = OS.GetCmdlineArgs();
        foreach (var arg in args)
            if (arg == "--art-scene") return true;
        return false;
    }

    /// <summary>
    /// --art-scene-capture --capture-out &lt;path&gt;: both required together.
    /// </summary>
    private static bool ReadArtSceneCaptureFlag(out string? outputPath)
    {
        outputPath = null;
        var args = OS.GetCmdlineArgs();
        bool present = false;
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "--art-scene-capture") present = true;
            if (args[i] == "--capture-out" && i + 1 < args.Length) outputPath = args[i + 1];
        }
        return present;
    }

    /// <summary>
    /// --capture-width/--capture-height: the resolution.width/height values from
    /// scene_capture_config.yaml, passed through by tools/art_lint/capture_scene.py (the
    /// YAML remains the single source of truth; these flags carry its values into the
    /// engine process, they are not an independent second place to set resolution).
    /// </summary>
    private static bool ReadArtSceneCaptureResolution(out int width, out int height)
    {
        width = height = 0;
        var args = OS.GetCmdlineArgs();
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == "--capture-width") width = int.Parse(args[i + 1]);
            if (args[i] == "--capture-height") height = int.Parse(args[i + 1]);
        }
        return width > 0 && height > 0;
    }

    private static bool ReadDebugOverlayVisible()
    {
        const string settingsPath = "res://config/game_settings.yaml";
        try
        {
            using var file = Godot.FileAccess.Open(settingsPath, Godot.FileAccess.ModeFlags.Read);
            if (file != null)
            {
                foreach (var line in file.GetAsText().Split('\n'))
                {
                    var trimmed = line.TrimStart();
                    if (!trimmed.StartsWith("show_debug_overlay:", System.StringComparison.Ordinal)) continue;
                    var value = trimmed["show_debug_overlay:".Length..].Trim().Trim('"');
                    return value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
                }
            }
        }
        catch { /* silent — default to hidden */ }
        return false;
    }

    /// <summary>
    /// Read the show_prop_inspect setting from game_settings.yaml.
    /// Defaults to true — feature inspection is on unless explicitly disabled.
    /// </summary>
    private static bool ReadShowPropInspect()
    {
        const string settingsPath = "res://config/game_settings.yaml";
        try
        {
            using var file = Godot.FileAccess.Open(settingsPath, Godot.FileAccess.ModeFlags.Read);
            if (file != null)
            {
                foreach (var line in file.GetAsText().Split('\n'))
                {
                    var trimmed = line.TrimStart();
                    if (!trimmed.StartsWith("show_prop_inspect:", System.StringComparison.Ordinal)) continue;
                    var value = trimmed["show_prop_inspect:".Length..].Trim().Trim('"');
                    return value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
                }
            }
        }
        catch { /* silent — default to true */ }
        return true;
    }

    /// <summary>
    /// Create the IMapRenderer for the given mode string.
    /// "topdown" is the default active renderer using 16bf world tiles (24x24).
    /// "iso" preserves the legacy isometric path — can be reactivated via game_settings.yaml.
    /// Unknown values fall back to TopDownRenderer with a warning.
    /// </summary>
    private static IMapRenderer CreateRenderer(string mode)
    {
        return mode.ToLowerInvariant() switch
        {
            "iso" => new IsometricRenderer(),
            "topdown" => new TopDownRenderer(),
            _ => FallbackRenderer(mode),
        };

        static IMapRenderer FallbackRenderer(string value)
        {
            GD.PrintErr($"[Main] map_mode '{value}' is unknown — falling back to topdown.");
            return new TopDownRenderer();
        }
    }

    /// <summary>
    /// Create all content factories and build the level template registry.
    /// Called once from _Ready. Subsequent floor transitions reuse these objects.
    /// </summary>
    private void InitFactories()
    {
        // Read YAML via Godot's FileAccess — on iOS, res:// files are packed inside the
        // .pck bundle and cannot be read via System.IO.File. FileAccess handles this
        // transparently across all platforms.
        var entitiesYaml = ReadGodotResource("res://config/entities.yaml");
        var levelTemplatesYaml = ReadGodotResource("res://config/level_templates.yaml");

        _contentLoader = new ContentLoader();
        ContentBundle content;
        try
        {
            content = _contentLoader.LoadAll(entitiesYaml);
            GD.Print($"Content loaded: {content.Monsters.Count} monsters, {content.Items.Count} items, {content.Consumables.Count} consumables");
            foreach (var (key, mon) in content.Monsters)
                GD.Print($"  Monster: {key} → {mon.Name ?? "(null)"}, hp={mon.Stats?.Hp ?? -1}");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"YAML entities deserialization failed: {ex.GetType().Name}: {ex.Message}");
            if (ex.InnerException != null)
                GD.PrintErr($"  Inner: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}");
            GD.PrintErr($"  Stack: {ex.StackTrace}");
            throw;
        }

        _entityFactory = new EntityFactory();
        _itemFactory = new ItemFactory(content.Items, _entityFactory);
        _monsterFactory = new MonsterFactory(content.Monsters, _entityFactory, _itemFactory);
        _consumableFactory = new ConsumableFactory(content.Consumables, _entityFactory);
        _spellItemFactory = new SpellItemFactory(content.SpellItems, _entityFactory);

        try
        {
            _levelTemplates = LevelTemplateRegistry.FromYaml(levelTemplatesYaml);
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"YAML level_templates deserialization failed: {ex.GetType().Name}: {ex.Message}");
            if (ex.InnerException != null)
                GD.PrintErr($"  Inner: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}");
            GD.PrintErr($"  Stack: {ex.StackTrace}");
            throw;
        }
        // Load depth boons (optional — missing file means no boons, not a crash)
        Dictionary<int, CatacombsOfYarl.Logic.Balance.BoonDefinition>? boonTable = null;
        try
        {
            var boonYaml = ReadGodotResource("res://config/depth_boons.yaml");
            boonTable = _contentLoader.LoadBoons(boonYaml);
            _boonTable = boonTable;   // kept for LoadMidRun on resume (RECONSTRUCT-class, from config)
            GD.Print($"Depth boons loaded: {boonTable.Count} entries");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Depth boons load failed (non-fatal): {ex.Message}");
        }

        PropRegistry? propRegistry = null;
        string? propsYamlForDescriptions = null;
        try
        {
            var propsYaml = ReadGodotResource("res://config/props.yaml");
            propsYamlForDescriptions = propsYaml;
            propRegistry = _contentLoader.LoadProps(propsYaml);
            GD.Print($"Props loaded: {propRegistry.All.Count} prop definitions");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Props load failed (non-fatal — no props will appear): {ex.Message}");
        }

        // Load prop description registry for long-press inspect panel.
        // Both YAMLs are read here; the registry's static ctor already seeded tile-feature entries.
        // Non-fatal: if either file is missing, tile-based feature descriptions still work.
        try
        {
            var interactivePropsYaml = ReadGodotResource("res://config/interactive_props.yaml");
            CatacombsOfYarl.Logic.Content.PropDescriptionRegistry.Load(
                propsYamlForDescriptions ?? "",
                interactivePropsYaml);
            GD.Print("[Main] PropDescriptionRegistry loaded");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"PropDescriptionRegistry load failed (non-fatal): {ex.Message}");
        }

        CatacombsOfYarl.Logic.Content.SignpostMessageRegistry? signpostRegistry = null;
        try
        {
            var signYaml = ReadGodotResource("res://config/signpost_messages.yaml");
            signpostRegistry = CatacombsOfYarl.Logic.Content.SignpostMessageRegistry.FromYaml(signYaml);
            GD.Print($"Signpost registry loaded");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Signpost registry load failed (non-fatal — no signs will appear): {ex.Message}");
        }

        CatacombsOfYarl.Logic.Content.MuralRegistry? muralRegistry = null;
        try
        {
            var muralYaml = ReadGodotResource("res://config/murals_inscriptions.yaml");
            muralRegistry = CatacombsOfYarl.Logic.Content.MuralRegistry.FromYaml(muralYaml);
            GD.Print($"Mural registry loaded: {muralRegistry.Count} entries");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Mural registry load failed (non-fatal — no murals will appear): {ex.Message}");
        }

        CatacombsOfYarl.Logic.Content.LootTagRegistry? lootTagRegistry = null;
        try
        {
            var lootTagsYaml = ReadGodotResource("res://config/loot_tags.yaml");
            lootTagRegistry = CatacombsOfYarl.Logic.Content.LootTagRegistry.FromYaml(lootTagsYaml);
            GD.Print($"Loot tag registry loaded: {lootTagRegistry.Count} entries");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Loot tag registry load failed (non-fatal — falling back to flat pool): {ex.Message}");
        }

        CatacombsOfYarl.Logic.Content.LootPolicyConfig? lootPolicy = null;
        try
        {
            var lootPolicyYaml = ReadGodotResource("res://config/loot_policy.yaml");
            lootPolicy = CatacombsOfYarl.Logic.Content.LootPolicyConfig.FromYaml(lootPolicyYaml);
            GD.Print($"Loot policy loaded");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"Loot policy load failed (non-fatal — falling back to flat pool): {ex.Message}");
        }

        _floorBuilder = new DungeonFloorBuilder(
            _levelTemplates, _monsterFactory, _itemFactory, _consumableFactory,
            content.FloorItemPool, spellItemFactory: _spellItemFactory,
            boonTable: boonTable, propRegistry: propRegistry,
            signpostRegistry: signpostRegistry, muralRegistry: muralRegistry,
            lootTagRegistry: lootTagRegistry, lootPolicy: lootPolicy);

        // Voice line registries — merged into a single registry at boot.
        try
        {
            var hollowmarkYaml = ReadGodotResource("res://config/voice_lines/hollowmark.yaml");
            var quippingShadeYaml = ReadGodotResource("res://config/voice_lines/quipping_shade.yaml");
            var catalogYaml = ReadGodotResource("res://config/voice_lines/catalog_past_selves.yaml");
            var possessionYaml = ReadGodotResource("res://config/voice_lines/possession.yaml");
            _voiceLineRegistry = VoiceLineRegistry.LoadFromYaml(hollowmarkYaml);
            _voiceLineRegistry.Merge(VoiceLineRegistry.LoadFromYaml(quippingShadeYaml));
            _voiceLineRegistry.Merge(VoiceLineRegistry.LoadFromYaml(catalogYaml));
            _voiceLineRegistry.Merge(VoiceLineRegistry.LoadFromYaml(possessionYaml));
            GD.Print("[Main] Voice line registry loaded.");

            var weighingAuditYaml = ReadGodotResource("res://config/voice_lines/weighing_audit.yaml");
            _weighingAuditRegistry = Logic.Content.WeighingAuditRegistry.LoadFromYaml(weighingAuditYaml);
            GD.Print("[Main] Weighing audit registry loaded.");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[Main] Voice line registry load failed (non-fatal): {ex.Message}");
        }

        // Under-Warden memo registry — loaded once at boot alongside voice lines.
        // Non-fatal: inbox UI silently stays disabled if files are missing.
        try
        {
            var memosYaml = ReadGodotResource("res://config/under_warden/memos.yaml");
            var causeNamesYaml = ReadGodotResource("res://config/under_warden/cause_display_names.yaml");
            _memoRegistry = MemoRegistry.LoadFromYaml(memosYaml, causeNamesYaml);
            GD.Print("[Main] Memo registry loaded.");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[Main] Memo registry load failed (non-fatal): {ex.Message}");
        }
    }

    /// <summary>
    /// Load a scenario YAML and start the game. Existing path — used for dev/harness work.
    /// Keeps working as before; factories are now pre-created by InitFactories().
    /// </summary>
    private void LoadAndStart()
    {
        var scenarioYaml = ReadGodotResource("res://config/levels/scenario_depth1_tuned.yaml");
        var scenario = _contentLoader!.LoadScenario(scenarioYaml);
        _state = GameStateFactory.FromScenario(
            scenario, _baseSeed, _monsterFactory!, _itemFactory!, _consumableFactory!);

        SetupPresentation(_state);
        GD.Print($"Ready (scenario) — {_state.Monsters.Count} monsters. Tap to play.");
    }

    /// <summary>
    /// Procedural dungeon entry point. Builds a fresh floor at the given depth.
    /// Pass existingPlayer=null for a new run; pass _state.Player to carry the player forward.
    /// explorationMode=true spawns no monsters — useful for visually inspecting generated floors.
    /// </summary>
    public void StartDungeon(int depth = 1, Entity? existingPlayer = null, bool explorationMode = false)
    {
        _testScenarioBuilder = null; // clear any test scenario override
        _currentDepth = depth;
        var rng = new SeededRandom(_baseSeed + depth * 1_000_003);
        _state = _floorBuilder!.Build(depth, rng, existingPlayer, explorationMode: explorationMode,
            persistentState: _persistentState);

        // Increment run counter at the start of a real run (depth 1, not explore mode).
        // Explore mode is a visual tool, not a campaign run — don't count it.
        if (depth == 1 && !explorationMode && _persistentState != null && _persistenceProvider != null)
        {
            _persistentState.RunCounter.IncrementRunCount();
            _persistentState.MarkDirty();
            _persistentState.Flush(_persistenceProvider, GD.PrintErr);
        }

        // Reset per-run voice line first-fire set on every new run (depth 1).
        if (depth == 1)
            _voiceLineFiredSet.Clear();

        SetupPresentation(_state);
        GD.Print($"Ready (dungeon depth {depth}) — {_state.Monsters.Count} monsters, {_state.FloorItems.Count} floor items. Tap to play.");
    }

    /// <summary>
    /// Shared presentation setup used by both LoadAndStart and StartDungeon.
    /// Tears down any existing presentation nodes, renders the new state, and wires up GameController.
    /// </summary>
    private void SetupPresentation(GameState state)
    {
        // Reset per-run stats
        _turnCount = 0;
        _monstersKilled = 0;
        _damageDealt = 0;
        _damageTaken = 0;

        // Get scene nodes
        _gameView = GetNode<Node2D>("GameView");
        var tileMapLayer = GetNode<Node2D>("GameView/TileMapLayer");
        _tileMapLayer = tileMapLayer;
        var entityLayer = GetNode<Node2D>("GameView/EntityLayer");
        var vfxLayerNode = GetNode<Node2D>("GameView/VfxLayer");
        var uiLayer = GetNode<CanvasLayer>("UILayer");
        var hudNode = GetNode<Control>("UILayer/StatusBar");
        var toastLogNode = GetNode<Control>("UILayer/ToastLog");
        var inventoryPanelNode = GetNode<Control>("UILayer/QuickSlotBar");
        var equipmentPanelNode = GetNode<Control>("UILayer/EquipmentPanel");

        // Phase 1 zone containers — content added in later phases.
        var quickSlotZone   = inventoryPanelNode;  // UILayer/QuickSlotBar
        var menuButtonsZone = GetNode<Control>("UILayer/MenuButtons");
        var bottomSafeArea  = GetNode<Control>("UILayer/BottomSafeArea");

        // These nodes overlay the dungeon — must not block taps on the game view.
        toastLogNode.MouseFilter      = Control.MouseFilterEnum.Ignore;
        equipmentPanelNode.MouseFilter = Control.MouseFilterEnum.Ignore;

        // Clear any previous render — RemoveChild before QueueFree so ghost nodes
        // don't linger in layout containers until end-of-frame.
        foreach (var node in new Node[] { tileMapLayer, entityLayer, hudNode, toastLogNode, inventoryPanelNode, equipmentPanelNode, quickSlotZone, menuButtonsZone, bottomSafeArea })
            foreach (var child in node.GetChildren())
                child.SafeFree();

        // Tap indicators are children of EntityLayer — they were just freed above.
        // Clear the list so _Process doesn't try to fade/free already-disposed nodes.
        _tapIndicators.Clear();

        // Phase 1 placeholder backgrounds — make zones visible during development.
        // QuickSlotBar placeholder replaced by real QuickSlotBar in Phase 3.
        AddZonePlaceholder(quickSlotZone,  new Color(0.08f, 0.08f, 0.12f, 0.92f)); // dark blue-grey
        AddZonePlaceholder(bottomSafeArea, new Color(0.00f, 0.00f, 0.00f, 1.00f)); // solid black
        // MenuButtons zone: populated below by MenuButtonBar (Phase 2 — no placeholder needed).

        // Render dungeon (stair overlays handled inside DungeonRenderer — second pass)
        // Returns TileLayer so we can apply fog-of-war each turn without re-creating nodes.
        // TileThemeConfig is loaded once at boot and reused across all floor transitions.
        // Pass props from GameState so Pass 4 renders placed furniture/overlays.
        // Props is empty in scenario mode (IsDungeonMode=false) — no regression there.
        _tileLayer = DungeonRenderer.Render(state.Map, tileMapLayer, _renderer, _tileThemeConfig,
            props: state.Props, features: state.Features, lockedDoors: state.LockedDoors);

        // Entity sprites — store reference so OnTurnCompleted can call UpdateVisibility
        _entitySprites = new EntitySpriteManager(entityLayer, _spriteMapping!, _renderer);
        _entitySprites.Initialize(state);

        // Item sprites — floor items rendered as tinted overlay sprites on entityLayer.
        // TileThemeConfig is passed so key items can resolve the world_24x24 key sprite
        // (tile 5039) directly, bypassing the items_16x16 tileset lookup.
        _itemSprites = new ItemSpriteManager(entityLayer, _spriteMapping!, _renderer, _tileThemeConfig);
        _itemSprites.Initialize(state);

        // HUD
        _hud = new HUD();
        hudNode.AddChild(_hud);
        _hud.SetState(state);

        // Menu button bar (Phase 2) — Gear and Explore buttons in the MenuButtons zone.
        // Replaces the temporary Phase 1 placeholder for that zone.
        _menuButtonBar = new MenuButtonBar();
        menuButtonsZone.AddChild(_menuButtonBar);
        _menuButtonBar.GearRequested    += OnGearRequested;
        _menuButtonBar.ExploreRequested += () => _gameController?.StartAutoExplore();
        _menuButtonBar.PossessRequested += () => _gameController?.StartPossessionTargeting();
        _menuButtonBar.ExitPossessionRequested += () => _gameController?.ExitPossessionAction();
        _menuButtonBar.CancelPossessionTargetingRequested += () => _gameController?.CancelPossessionTargeting();
        _menuButtonBar.MenuRequested    += () => ShowMainMenu();

        // Quick-slot bar (Phase 3) — scrollable consumable/wand strip + weapon indicator.
        // Replaces InventoryPanel. Drop goes through long-press → action sheet.
        _inventoryPanel = new QuickSlotBar();
        _inventoryPanel.SpriteMappingInstance = _spriteMapping;
        inventoryPanelNode.AddChild(_inventoryPanel);
        _inventoryPanel.Initialize(state);
        _inventoryPanel.ItemTapped     += OnInventoryItemTapped;
        _inventoryPanel.WeaponTapped        += () => _toastLog?.AddMessage("Ranged toggle coming soon");
        _inventoryPanel.WeaponLongPressed   += () =>
        {
            var weapon = _state?.Player.Get<Equipment>()?.MainHand;
            if (weapon != null)
                _gameController?.HandleInventoryLongPress(weapon.Id);
        };
        _rectDebugDraw?.SetQuickSlotBar(_inventoryPanel);

        // Equipment panel — full-screen overlay, starts hidden.
        _equipmentPanel = new EquipmentPanel();
        _equipmentPanel.SpriteMappingInstance = _spriteMapping;
        equipmentPanelNode.AddChild(_equipmentPanel);
        _equipmentPanel.EquipRequested     += itemId => _gameController?.HandleEquipRequest(itemId);
        _equipmentPanel.UnequipRequested   += slot   => _gameController?.HandleUnequipRequest(slot);
        _equipmentPanel.ItemDropRequested  += itemId => _gameController?.HandleDropRequest(itemId);

        // Combat log
        _toastLog = new ToastLog();
        toastLogNode.AddChild(_toastLog);
        _toastLog.SetPlayerId(state.Player.Id);

        // Game over screen (reused across floor transitions — create once, hide/show)
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

        // Memo inbox panel (created once, shown after run ends when memos are pending)
        if (_memoInboxPanel == null)
        {
            _memoInboxPanel = new MemoInboxPanel();
            uiLayer.AddChild(_memoInboxPanel);
            _memoInboxPanel.InboxClosed += OnInboxClosed;
            _memoInboxPanel.Visible = false;
        }

        PlayerCamera.Update(_gameView!, state.ControlledEntity, _currentZoom, _renderer);

        // Minimap: create once, reuse across floors (just call Refresh on each floor).
        if (_miniMap == null)
        {
            _miniMap = new MiniMap();
            _miniMap.MouseFilter = Control.MouseFilterEnum.Ignore;
            // Anchor to top-right of ViewportOverlay — consistent with MsgButton/StatusEffectBar
            // pattern. ViewportOverlay's top edge IS the StatusBar's bottom edge, so an 8px
            // OffsetTop here naturally tracks any future StatusBar height change.
            _miniMap.AnchorLeft   = 1f;
            _miniMap.AnchorTop    = 0f;
            _miniMap.AnchorRight  = 1f;
            _miniMap.AnchorBottom = 0f;
            GetNode<Control>("UILayer/ViewportOverlay").AddChild(_miniMap);

            // Zoom buttons: small +/− panel anchored to the left of the minimap area.
            // Also parented to ViewportOverlay for consistency.
            var zoomPanel = BuildZoomPanel();
            zoomPanel.MouseFilter = Control.MouseFilterEnum.Ignore;
            GetNode<Control>("UILayer/ViewportOverlay").AddChild(zoomPanel);
        }
        _miniMap.OffsetLeft   = -state.Map.Width  * 2 - 8;
        _miniMap.OffsetTop    = 8f;  // 8px gap below ViewportOverlay top (= StatusBar bottom)
        _miniMap.OffsetRight  = -8f;
        _miniMap.OffsetBottom = 8f + state.Map.Height * 2;
        _miniMap.Refresh(state);

        // Apply initial fog-of-war so the floor renders correctly from turn 0.
        // In dungeon mode: DungeonFloorBuilder.Build called RecomputeFov — player sees start area.
        // In scenario mode: map.RevealAll was called — all tiles visible.
        if (_tileLayer != null)
            DungeonRenderer.UpdateVisibility(_tileLayer, state.Map);
        _entitySprites?.UpdateVisibility(state);
        _entitySprites?.UpdateStatusTints(state);
        _itemSprites?.UpdateVisibility(state);
        // Initial HP bar pass — shows bars for any pre-damaged monsters at floor start.
        if (_entitySprites != null)
            _floatingHpBars?.Refresh(state, _entitySprites);

        // Game controller — free old one if it exists
        // Clear portal sprites on floor setup (new floor = no active portals)
        foreach (var sprite in _portalSprites.Values) sprite.QueueFree();
        _portalSprites.Clear();

        // Spawn sprites for any pre-placed static portals (from DungeonFloorBuilder.PlacePortalPairs).
        // Wand-placed portals arrive via PortalPlacedEvent during the turn loop; static portals are
        // placed at floor build time before the first turn, so we seed sprites here instead.
        foreach (var portal in state.Portals)
        {
            var comp = portal.Get<CatacombsOfYarl.Logic.Combat.PortalComponent>();
            if (comp != null)
                SpawnPortalSprite(portal.Id, portal.X, portal.Y, comp.Type);
        }

        // VFX overlay — create once per floor. ClearAll hides any lingering pooled nodes
        // from the previous floor before we create a fresh overlay for the new one.
        _vfxOverlay?.ClearAll();
        _vfxOverlay = new VfxOverlay(vfxLayerNode, _renderer);

        // Ground hazard overlay — persistent tile tints for burning/poison ground.
        // Clear previous floor's nodes, then create fresh for this floor.
        _groundHazardOverlay?.Clear();
        _groundHazardOverlay = new GroundHazardOverlay(vfxLayerNode, _renderer);

        // Floating HP bars — small red bars above damaged enemy sprites.
        // Clear old bars before entityLayer children are freed (child-free loop already ran above),
        // then create a fresh manager pointing at the new entityLayer.
        _floatingHpBars?.Clear();
        _floatingHpBars = new FloatingHpBarManager(entityLayer, _renderer);

        if (_gameController != null)
        {
            Diag.Log($"SetupPresentation: disposing old GameController, phase={_gameController.Phase}");
            _gameController.TurnCompleted -= OnTurnCompleted;
            _gameController.GameEnded -= OnGameEnded;
            _gameController.FloorTransitionRequested -= OnFloorTransitionRequested;
            _gameController.PortalEntranceCancelled -= OnPortalEntranceCancelled;
            _gameController.SafeFree();
        }
        _gameController = new GameController();
        AddChild(_gameController);
        _gameController.Initialize(state, _entitySprites!, this, _itemSprites, _inventoryPanel,
            _equipmentPanel, _toastLog, _monsterFactory, _renderer, _gameView, _entityFactory,
            _vfxOverlay, showPropInspect: ReadShowPropInspect());
        _gameController.TurnCompleted += OnTurnCompleted;
        _gameController.GameEnded += OnGameEnded;
        _gameController.FloorTransitionRequested += OnFloorTransitionRequested;
        _gameController.PortalEntranceCancelled += OnPortalEntranceCancelled;

        // Bot driver — debug builds only. Re-initialize across floor transitions.
        // Release builds: _botDriver is never assigned (BotPlayerDriver is never instantiated).
        if (OS.IsDebugBuild())
        {
            if (_botDriver == null)
            {
                _botDriver = new CatacombsOfYarl.Presentation.Bot.BotPlayerDriver();
                AddChild(_botDriver);

                _botHud = new CatacombsOfYarl.Presentation.Bot.BotModeHud();
                GetNode<CanvasLayer>("UILayer").AddChild(_botHud);
                _botHud.Initialize(_botDriver);
            }
            _botDriver.Initialize(_gameController, state);
        }

        // Message log panel — Phase 6.2. Created once, lives at UILayer root (same level as
        // EquipmentPanel) so it sits above everything else when visible. Starts hidden.
        if (_messageLogPanel == null)
        {
            _messageLogPanel = new MessageLogPanel();
            GetNode<CanvasLayer>("UILayer").AddChild(_messageLogPanel);
        }

        // Msg button — Phase 5. Created once and parented to the ViewportOverlay zone.
        // The Pressed lambda captures `this` (Main), resolving _toastLog/_messageLogPanel at
        // call time so they always refer to the current floor's objects after floor transitions.
        if (_msgButton == null)
        {
            _msgButton = new MsgButton();
            GetNode<Control>("UILayer/ViewportOverlay").AddChild(_msgButton);
            _msgButton.Pressed += () => _messageLogPanel?.Open(_toastLog?.History ?? System.Array.Empty<string>());
        }

        // Status effect bar — Phase 5. Created once, lives in ViewportOverlay just below
        // the StatusBar zone. The ViewportOverlay's top edge IS the StatusBar's bottom edge,
        // so a small offset (8px left, 4px top) positions the badge row flush with the bar.
        // The control hides itself when no effects are active — no viewport clutter.
        if (_statusEffectBar == null)
        {
            _statusEffectBar = new StatusEffectBar();
            _statusEffectBar.CustomMinimumSize = new Vector2(0, 24);
            _statusEffectBar.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            _statusEffectBar.MouseFilter = Control.MouseFilterEnum.Ignore;
            // Anchor to top-left of ViewportOverlay with a small margin from the zone edges.
            _statusEffectBar.AnchorLeft   = 0f;
            _statusEffectBar.AnchorTop    = 0f;
            _statusEffectBar.AnchorRight  = 1f;
            _statusEffectBar.AnchorBottom = 0f;
            _statusEffectBar.OffsetLeft   = 8f;
            _statusEffectBar.OffsetTop    = 4f;
            _statusEffectBar.OffsetRight  = 0f;
            _statusEffectBar.OffsetBottom = 28f; // top offset + height (4 + 24)
            GetNode<Control>("UILayer/ViewportOverlay").AddChild(_statusEffectBar);
        }
        // Refresh immediately so any pre-existing effects show on floor entry.
        _statusEffectBar.Refresh(state.Player);

        // Wire HUD buttons to GameController / EquipmentPanel.
        // Phase 2: Gear/Explore wired via MenuButtonBar (created above).
        // Phase 5: Msg button wired above (MsgButton in ViewportOverlay).

        // Debug overlay — update references each floor so it reflects the new state.
        // No-op in release builds (_debugOverlay is null).
        _debugOverlay?.SetGameState(_gameController, state, _entitySprites, _itemSprites, _toastLog);

        // Queue 4 frames of camera snaps. The first frame handles the immediate stale-viewport
        // case; frames 2–4 handle slower layout settling after MenuLayer hides. Each snap is
        // cheap (one Position/Scale assignment), so running 4 times is safe.
        _pendingCameraSnapFrames = 4;
    }

    // Set > 0 at end of SetupPresentation; decremented each frame until 0.
    // Retrying multiple frames handles the case where GetVisibleRect() reports a plausible
    // but stale size on the first frame after the MenuLayer hides (layout hasn't settled yet).
    private int _pendingCameraSnapFrames;
    private bool _pendingCameraSnap => _pendingCameraSnapFrames > 0;

    private void _DoInitialCameraSnap()
    {
        if (_state == null || _gameView == null) return;
        var viewSize = _gameView.GetViewport().GetVisibleRect().Size;
        if (viewSize.X < 100 || viewSize.Y < 100)
        {
            // Viewport not ready yet — keep retrying.
            _pendingCameraSnapFrames = System.Math.Max(_pendingCameraSnapFrames, 1);
            return;
        }
        PlayerCamera.Update(_gameView, _state.ControlledEntity, _currentZoom, _renderer);
        if (_tileLayer != null)
            DungeonRenderer.UpdateVisibility(_tileLayer, _state.Map);
        _entitySprites?.UpdateVisibility(_state);
        _entitySprites?.UpdateStatusTints(_state);
        _itemSprites?.UpdateVisibility(_state);
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (_gameController == null || _gameView == null) return;

        // --- Touch (mobile) ---
        if (@event is InputEventScreenTouch touch)
        {
            if (touch.Pressed)
            {
                _dragStartScreenPos = touch.Position;
                _cameraPositionAtDragStart = _gameView.Position;
                _isDragging = false;
                _dragStartRecorded = true;
            }
            else
            {
                // Only fire if _UnhandledInput saw the matching DOWN. If a UI button
                // consumed the DOWN via AcceptEvent(), _dragStartRecorded stays false
                // and the orphaned UP is silently ignored.
                bool fingerMoved = (touch.Position - _dragStartScreenPos).Length() > DragThreshold;
                if (_dragStartRecorded && !_isDragging && !fingerMoved)
                {
                    Diag.Log($"_UnhandledInput tap at {_dragStartScreenPos}, phase={_gameController.Phase}");
                    var localPos = _gameView.ToLocal(_dragStartScreenPos);
                    SpawnTapIndicator(localPos);
                    _gameController.HandleTap(localPos);
                }
                _isDragging = false;
                _dragStartRecorded = false;
            }
            return;
        }

        if (@event is InputEventScreenDrag screenDrag)
        {
            var delta = screenDrag.Position - _dragStartScreenPos;
            if (!_isDragging && delta.Length() > DragThreshold)
            {
                _isDragging = true;
                PlayerCamera.CancelTween();
            }
            if (_isDragging)
                _gameView.Position = _cameraPositionAtDragStart + delta;
            return;
        }

        // --- Mouse (desktop) ---
        if (@event is InputEventMouseButton mb && mb.ButtonIndex == MouseButton.Left)
        {
            if (mb.Pressed)
            {
                _dragStartScreenPos = mb.Position;
                _cameraPositionAtDragStart = _gameView.Position;
                _isDragging = false;
                _dragStartRecorded = true;
            }
            else
            {
                bool fingerMoved = (mb.Position - _dragStartScreenPos).Length() > DragThreshold;
                if (_dragStartRecorded && !_isDragging && !fingerMoved)
                {
                    Diag.Log($"_UnhandledInput tap at {_dragStartScreenPos}, phase={_gameController.Phase}");
                    var localPos = _gameView.ToLocal(_dragStartScreenPos);
                    SpawnTapIndicator(localPos);
                    _gameController.HandleTap(localPos);
                }
                _isDragging = false;
                _dragStartRecorded = false;
            }
            return;
        }

        if (@event is InputEventMouseMotion motion && (motion.ButtonMask & MouseButtonMask.Left) != 0)
        {
            var delta = motion.Position - _dragStartScreenPos;
            if (!_isDragging && delta.Length() > DragThreshold)
            {
                _isDragging = true;
                PlayerCamera.CancelTween();
            }
            if (_isDragging)
                _gameView.Position = _cameraPositionAtDragStart + delta;
            return;
        }

        if (OS.IsDebugBuild() && @event is InputEventKey key && key.Pressed && key.Keycode == Key.F3)
        {
            if (_rectDebugDraw != null) _rectDebugDraw.Visible = !_rectDebugDraw.Visible;
        }

        // ── Bot mode hotkeys (debug builds only) ──────────────────────────────
        if (OS.IsDebugBuild() && _botDriver != null && @event is InputEventKey botKey && botKey.Pressed)
        {
            switch (botKey.Keycode)
            {
                case Key.F4:
                    // Toggle bot mode
                    if (_botDriver.Enabled) _botDriver.Disable();
                    else                    _botDriver.Enable();
                    _botHud?.RefreshDisplay();
                    break;

                case Key.F5 when _botDriver.Enabled:
                    // Cycle persona: balanced → cautious → aggressive → greedy → speedrunner → balanced
                    _botPersonaIdx = (_botPersonaIdx + 1) % BotPersonaCycle.Length;
                    _botDriver.SetPersona(BotPersonaCycle[_botPersonaIdx]);
                    _botHud?.RefreshDisplay();
                    Diag.Log($"[Bot] Persona → {BotPersonaCycle[_botPersonaIdx]}");
                    break;

                case Key.F6 when _botDriver.Enabled:
                    // Cycle speed: 1.0 → 0.5 → 0.25 → 0.1 → 0.0 (max) → 1.0
                    _botSpeedIdx = (_botSpeedIdx + 1) % BotSpeedCycle.Length;
                    _botDriver.TurnDelaySeconds = BotSpeedCycle[_botSpeedIdx];
                    _botHud?.RefreshDisplay();
                    Diag.Log($"[Bot] Speed → {BotSpeedCycle[_botSpeedIdx]}s/turn");
                    break;
            }
        }
    }

    private void SpawnTapIndicator(Vector2 localPos)
    {
        if (_gameView == null) return;
        var (gridX, gridY) = _renderer.ScreenToGrid(localPos);

        // Top-left of the tile — ColorRect is not centered, so position at grid origin.
        var tileOrigin = _renderer.GridToScreen(gridX, gridY);

        // Programmatic colored square — no sprite asset needed. Warm yellow-white at low
        // opacity so the highlight is visible without obscuring the tile underneath.
        var rect = new ColorRect
        {
            Size     = new Vector2(_renderer.TileWidth, _renderer.TileHeight),
            Color    = new Color(1f, 1f, 0.7f, 0.3f),
            Position = tileOrigin,
            ZIndex   = _renderer.GetTileSortOrder(gridX, gridY) + 1,
        };
        _gameView.GetNode<Node2D>("EntityLayer").AddChild(rect);

        // No Tween — alpha is lerped in _Process. Avoids a Tween holding a reference
        // to the ColorRect after _Process SafeFree's it (use-after-free on the tween's
        // PropertyTweener when Godot later processes or frees the stopped tween).
        double now = Time.GetTicksMsec() / 1000.0;
        _tapIndicators.Add((rect, now));
    }

    private Texture2D? _portalTexture;

    private void SpawnPortalSprite(int entityId, int gridX, int gridY, PortalType type)
    {
        if (_gameView == null) return;

        // Cyan for entrance, orange for exit — visually distinct at a glance
        var color = type == PortalType.Entrance
            ? new Color(0f, 0.85f, 1f, 0.9f)
            : new Color(1f, 0.5f, 0f, 0.9f);

        _portalTexture ??= GD.Load<Texture2D>(
            "res://src/Presentation/assets/sprites_16bf/fx_32x32/oryx_16bit_fantasy_fx_05.png");

        var sprite = new Sprite2D();
        sprite.Texture = _portalTexture;
        sprite.Position = _renderer.GridToScreenCenter(gridX, gridY);
        sprite.Modulate = color;
        sprite.TextureFilter = CanvasItem.TextureFilterEnum.Nearest;
        // Scale: fx sprites are 32px native. 1.0× matches the 32px iso tile width — large
        // enough to be clearly visible without spilling over adjacent tiles at zoom=4.
        sprite.Scale = new Vector2(1.0f, 1.0f);
        // ZIndex: use the renderer's tile sort order so portals appear above the floor tile at
        // this grid position regardless of renderer mode (iso uses gridX+gridY, top-down uses gridY).
        // +1 places portals above tiles but below entities (entities use GetEntitySortOrder = tile+1).
        sprite.ZIndex = _renderer.GetTileSortOrder(gridX, gridY) + 1;
        _gameView.GetNode<Node2D>("EntityLayer").AddChild(sprite);
        _portalSprites[entityId] = sprite;
    }

    private void DespawnPortalSprite(int entityId)
    {
        if (_portalSprites.TryGetValue(entityId, out var sprite))
        {
            sprite.QueueFree();
            _portalSprites.Remove(entityId);
        }
    }

    private void OnPortalEntranceCancelled(int entranceEntityId)
    {
        DespawnPortalSprite(entranceEntityId);
    }

    private void SwapDoorSprite(int x, int y)
    {
        if (_tileLayer == null || _tileThemeConfig == null || _state == null) return;
        if (!_tileLayer.DoorOverlaySprites.TryGetValue((x, y), out var sprite)) return;

        var theme = _state.Map.GetTileTheme(x, y);
        string themeName = DungeonRenderer.ThemeToConfigName(theme);
        var openPath = _tileThemeConfig.GetDoorOpen(themeName);
        if (openPath == null) return;

        var tex = ResourceLoader.Load<Texture2D>(openPath);
        if (tex != null && sprite is Sprite2D s2d)
            s2d.Texture = tex;
    }

    /// <summary>
    /// Swap the chest sprite at the given cell to the open or empty state texture.
    /// Mirrors the SwapDoorSprite pattern — update existing sprite rather than recreating it.
    /// </summary>
    private void SwapChestSprite(int x, int y, bool looted)
    {
        if (_tileLayer == null || _tileThemeConfig == null || _state == null) return;
        if (!_tileLayer.FeatureOverlaySprites.TryGetValue((x, y), out var sprite)) return;

        var themeName = DungeonRenderer.ThemeToConfigName(_state.Map.GetTileTheme(x, y));
        int tileId = looted ? _tileThemeConfig.GetChestEmpty(themeName) : _tileThemeConfig.GetChestOpen(themeName);
        if (tileId == 0) return;
        var path = _tileThemeConfig.GetTexturePath(tileId);
        var tex = ResourceLoader.Load<Texture2D>(path);
        if (tex != null)
        {
            sprite.Texture = tex;
            sprite.Modulate = Colors.White; // clear any lock tint
        }
    }

    /// <summary>
    /// Handle a locked door being unlocked. The tile has already changed to DoorOpen in the
    /// logic layer (TurnController.TryHandleLockedDoorBump). Here we:
    ///   - Swap the door sprite from locked (tile 203) to open (tile 202).
    ///   - Remove the key icon overlay that was showing the lock color.
    ///
    /// The DoorOverlaySprites entry is reused (same position, new texture).
    /// </summary>
    private void HandleDoorUnlocked(int x, int y)
    {
        if (_tileLayer == null || _tileThemeConfig == null || _state == null) return;

        // Remove key icon overlay for the door.
        if (_tileLayer.LockKeyOverlaySprites.Remove((x, y), out var keyIcon))
            keyIcon.SafeFree();

        // Swap door sprite from locked → open.
        // The tile kind in the map is already DoorOpen — use the same theme-driven path as SwapDoorSprite.
        if (_tileLayer.DoorOverlaySprites.TryGetValue((x, y), out var doorSprite))
        {
            var theme = _state.Map.GetTileTheme(x, y);
            string themeName = DungeonRenderer.ThemeToConfigName(theme);
            var openPath = _tileThemeConfig.GetDoorOpen(themeName);
            if (openPath != null)
            {
                var tex = ResourceLoader.Load<Texture2D>(openPath);
                if (tex != null && doorSprite is Sprite2D s2d)
                {
                    s2d.Texture = tex;
                    s2d.Modulate = Colors.White; // clear lock color tint
                    s2d.Centered = false;
                    s2d.RotationDegrees = 0f; // reset rotation — open door doesn't need it
                }
            }
        }
    }

    /// <summary>
    /// Handle a secret door being revealed. The tile kind has already changed to TileKind.Door
    /// in the logic layer. Here we:
    ///   1. Swap the wall base sprite at (x, y) to the floor tile (the revealed area is now
    ///      passable; the full re-render on the next UpdateVisibility will handle floor color).
    ///      We keep the existing base sprite and let UpdateVisibility re-modulate it naturally —
    ///      the wall sprite sits at (x, y) in TileSprites and will be visible/explored already.
    ///   2. Add a new door overlay sprite at (x, y) tracked in DoorOverlaySprites, exactly
    ///      mirroring how the initial render pass creates door overlays.
    ///
    /// The wall base sprite visually becomes "wrong" (wall texture, but now a door). We fix
    /// this by swapping it to the floor tile texture so the door overlay renders on floor.
    /// </summary>
    private void HandleSecretDoorFound(int x, int y)
    {
        if (_tileLayer == null || _tileThemeConfig == null || _state == null || _tileMapLayer == null)
            return;

        var map = _state.Map;
        var theme = map.GetTileTheme(x, y);
        string themeName = DungeonRenderer.ThemeToConfigName(theme);

        // Step 1: replace the wall base sprite with a floor sprite so the door overlay
        // renders on a floor background rather than a mismatched wall background.
        if (_tileLayer.TileSprites.TryGetValue((x, y), out var baseSprite))
        {
            var floorPath = _tileThemeConfig.GetFloorTile(themeName, x, y);
            if (floorPath != null)
            {
                var floorTex = ResourceLoader.Load<Texture2D>(floorPath);
                if (floorTex != null && baseSprite is Sprite2D s2d)
                    s2d.Texture = floorTex;
            }
        }

        // Step 2: add a door overlay at (x, y) — exactly mirrors DungeonRenderer Pass 2.
        // The door sprite is a closed door (the player still has to open it).
        var doorPath = _tileThemeConfig.GetDoor(themeName);
        if (doorPath == null) return;

        var doorTex = ResourceLoader.Load<Texture2D>(doorPath);
        if (doorTex == null) return;

        // Determine orientation: horizontal if walls above AND below (passage runs E-W).
        // After reveal the tile is now TileKind.Door, so neighbors are still wall/secret-door.
        bool wallN = !map.InBounds(x, y - 1) || map.IsWallTile(x, y - 1);
        bool wallS = !map.InBounds(x, y + 1) || map.IsWallTile(x, y + 1);
        bool isDoorHorizontal = wallN && wallS;

        var screenPos = _renderer.GridToScreen(x, y);
        var doorOverlay = new Sprite2D
        {
            Texture = doorTex,
            Position = isDoorHorizontal ? _renderer.GridToScreenCenter(x, y) : screenPos,
            Centered = isDoorHorizontal,
            RotationDegrees = isDoorHorizontal ? 90f : 0f,
            ZIndex = _renderer.GetTileSortOrder(x, y) + 1,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
        };

        _tileMapLayer.AddChild(doorOverlay);
        _tileLayer.DoorOverlaySprites[(x, y)] = doorOverlay;
    }

    /// <summary>
    /// Remove the key icon overlay from a locked chest when it is unlocked.
    /// Resets the chest sprite tint to White so it looks like a normal closed chest
    /// (it will be swapped to open in the immediately-following ChestOpenedEvent handler).
    /// </summary>
    private void HandleChestUnlocked(int x, int y)
    {
        if (_tileLayer == null) return;

        // Remove the key icon overlay sprite.
        if (_tileLayer.LockKeyOverlaySprites.Remove((x, y), out var keyIcon))
            keyIcon.SafeFree();

        // Reset chest sprite tint to White — the chest is now unlocked and about to open.
        if (_tileLayer.FeatureOverlaySprites.TryGetValue((x, y), out var chestSprite))
            chestSprite.Modulate = Colors.White;
    }

    /// <summary>
    /// Human-readable color name for a lock color ID, used in toast messages.
    /// Must stay in sync with DungeonRenderer.GetLockColor palette.
    /// </summary>
    private static string LockColorName(int colorId) => colorId switch
    {
        0 => "red",
        1 => "blue",
        2 => "green",
        3 => "gold",
        4 => "purple",
        _ => "unknown",
    };

    /// <summary>
    /// After UpdateVisibility sets all visible sprites to White, re-apply lock color tints to:
    ///   - Locked chests still in the player's FOV (FeatureOverlaySprites).
    ///   - Locked doors still in the player's FOV (DoorOverlaySprites via LockedDoors registry).
    ///
    /// Called from OnTurnCompleted after DungeonRenderer.UpdateVisibility. This two-pass approach
    /// (UpdateVisibility sets White baseline → RefreshLockedChestTints overrides where needed)
    /// avoids storing per-sprite original tints in TileLayer.
    /// </summary>
    private void RefreshLockedChestTints()
    {
        if (_tileLayer == null || _state == null) return;

        // Re-tint locked chests (feature overlay sprites).
        foreach (var feature in _state.Features)
        {
            var lockable = feature.Get<LockableComponent>();
            if (lockable == null || !lockable.IsLocked) continue;

            // Only re-tint if this cell is currently visible (explored state keeps the dim tint).
            if (!_state.Map.IsVisible(feature.X, feature.Y)) continue;

            if (_tileLayer.FeatureOverlaySprites.TryGetValue((feature.X, feature.Y), out var sprite))
                sprite.Modulate = DungeonRenderer.GetLockColor(lockable.LockColorId);
        }

        // Re-tint locked doors (door overlay sprites).
        foreach (var ((x, y), colorId) in _state.LockedDoors)
        {
            if (!_state.Map.IsVisible(x, y)) continue;

            if (_tileLayer.DoorOverlaySprites.TryGetValue((x, y), out var doorSprite))
                doorSprite.Modulate = DungeonRenderer.GetLockColor(colorId);
        }
    }

    private void OnTurnCompleted(TurnResult result)
    {
        if (_state == null) return;

        // Mid-run autosave (M1.4 4b). This is the turn-commit seam: GameController fires TurnCompleted
        // immediately after TurnController.ProcessTurn, so _state is fully advanced here. Snapshot on
        // the game thread, write off the critical path. Dungeon mode only (scenario/harness never write
        // device saves). Skip terminal turns — record-then-delete owns those — and descend turns, whose
        // NEW floor is saved synchronously in OnFloorTransitionRequested.
        if (_state.IsDungeonMode && !result.GameOver && _midRunWriter != null
            && !result.Events.Any(e => e is DescendEvent))
            _midRunWriter.RequestWrite(Logic.Persistence.MidRun.MidRunSerializer.SaveMidRun(_state));

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
            else if (evt is PortalPlacedEvent pp)
                SpawnPortalSprite(pp.PortalEntityId, pp.X, pp.Y, pp.Type);
            else if (evt is PortalRemovedEvent pr)
            {
                DespawnPortalSprite(pr.EntranceEntityId);
                DespawnPortalSprite(pr.ExitEntityId);
            }
            else if (evt is DoorOpenedEvent doorEvt)
                SwapDoorSprite(doorEvt.X, doorEvt.Y);
            else if (evt is ChestUnlockedEvent unlockEvt)
            {
                HandleChestUnlocked(unlockEvt.X, unlockEvt.Y);
                string colorName = LockColorName(unlockEvt.LockColorId);
                _toastLog?.AddMessage($"The {colorName} key unlocks the chest!");
            }
            else if (evt is ChestLockedEvent lockedEvt)
            {
                string colorName = LockColorName(lockedEvt.LockColorId);
                _toastLog?.AddMessage($"This chest is locked. You need a {colorName} key.");
            }
            else if (evt is DoorUnlockedEvent doorUnlockEvt)
            {
                HandleDoorUnlocked(doorUnlockEvt.X, doorUnlockEvt.Y);
                string doorColorName = LockColorName(doorUnlockEvt.LockColorId);
                _toastLog?.AddMessage($"The {doorColorName} key unlocks the door!");
            }
            else if (evt is LockedDoorBumpedEvent lockedDoorEvt)
            {
                string doorColorName = LockColorName(lockedDoorEvt.LockColorId);
                _toastLog?.AddMessage($"This door is locked. You need a {doorColorName} key.");
            }
            else if (evt is ChestOpenedEvent chestEvt)
            {
                SwapChestSprite(chestEvt.X, chestEvt.Y, looted: false);
                _toastLog?.AddMessage("You open the chest.");
            }
            else if (evt is ChestLootedEvent lootEvt)
            {
                SwapChestSprite(lootEvt.X, lootEvt.Y, looted: true);
                _toastLog?.AddMessage("You loot the chest!");
            }
            else if (evt is SignpostReadEvent signEvt)
            {
                // Signs are free actions — show the message text as a toast.
                // Sign type could drive color coding in a future pass; neutral for now.
                _toastLog?.AddMessage($"Sign: {signEvt.Message}");
            }
            else if (evt is MuralExaminedEvent muralEvt)
            {
                _gameController?.ShowMuralInspect(muralEvt.Text);
            }
            else if (evt is Logic.Endgame.DebtChoiceGateEvent gateEvt)
            {
                // TODO (presentation tail): show Force / (Self if SwapAvailable) / Refuse buttons.
                // Three gate shapes: Force+Self+Refuse (swap available),
                //                    Force+Refuse (heavy, no swap),
                //                    [never emitted] (clean, no swap → auto-resolved).
                // Button labels and confirmation copy come from the audit registry.
                string forceLabel   = _weighingAuditRegistry?.GetUiText("ui.force_button")  ?? "Take her by force.";
                string selfLabel    = _weighingAuditRegistry?.GetUiText("ui.self_button")   ?? "Give yourself in her place.";
                string refuseLabel  = _weighingAuditRegistry?.GetUiText("ui.refuse_button") ?? "Turn back. Carry the debt.";
                string opts = gateEvt.SwapAvailable
                    ? $"[{forceLabel}] [{selfLabel}] [{refuseLabel}]"
                    : $"[{forceLabel}] [{refuseLabel}]";
                _toastLog?.AddMessage($"[color=#c0c0c0]The Weighing: {opts}[/color]");
            }
            else if (evt is WeighingDialogueEvent dialogueEvt)
            {
                // TODO (presentation tail): replace with WeighingDialoguePanel (blocking, paged,
                // tap-to-advance). Until that panel exists the dialogue is printed to the toast log
                // in sequence so the content is visible during development.
                foreach (var page in dialogueEvt.Pages)
                {
                    string color = page.Speaker switch
                    {
                        "under_warden" => "#c8b880",
                        "guardian"     => "#d0806060",
                        _              => "#aaaaaa",
                    };
                    _toastLog?.AddMessage($"[color={color}]{page.Text}[/color]");
                }
            }
            else if (evt is SecretDoorFoundEvent secretEvt)
            {
                HandleSecretDoorFound(secretEvt.X, secretEvt.Y);
                _toastLog?.AddMessage(secretEvt.Hint);
            }
            else if (evt is PossessionEnteredEvent possEnterEvt)
            {
                _toastLog?.AddMessage($"You possess the {result.Events.OfType<PossessionEnteredEvent>().FirstOrDefault()?.HostSpecies ?? "creature"}.");
                _ = possEnterEvt; // used above via linq
            }
            else if (evt is PossessionExitedEvent possExitEvt)
            {
                string reason = possExitEvt.Reason switch
                {
                    "voluntary"         => "You withdraw your spirit.",
                    "host_died"         => "The host body collapses — your spirit returns.",
                    "visibility_broken" => "The host strays too far. Your spirit snaps back.",
                    "dispelled"         => "The spell is broken. You return to yourself.",
                    "home_body_died"    => "Your home body has fallen.",
                    _                   => "Possession ends.",
                };
                _toastLog?.AddMessage(reason);

                // Track hall warden possessions for Under-Warden memo triggers.
                // Threshold memos (1st, 3rd, 6th+) are queued here so the evaluator
                // can fire mid-run rather than waiting for run end.
                if (possExitEvt.HostSpecies == "hall_warden"
                    && _memoRegistry != null && _persistentState != null)
                {
                    _memoEvaluator.EvaluateHallWardenPossession(
                        _persistentState, _memoRegistry,
                        _persistentState.RunCounter.TotalRuns);
                    // Dirty flag set inside EvaluateHallWardenPossession — flush deferred
                    // to the next natural persistence boundary (floor descent or run end).
                }

                // Variant 3 spell-break: past-self freed. Record in persistence and fire
                // the catalog_referenced memo on first occurrence.
                // NOTE: FreedPastSashaId uses the most recent PastSashaRecord as an
                // approximation until the spawn system stores record IDs on entities.
                if (possExitEvt.Reason == "warden_dispelled"
                    && _persistentState != null && _memoRegistry != null)
                {
                    var mostRecent = _persistentState.PastSashas.Records.Count > 0
                        ? _persistentState.PastSashas.Records[^1]
                        : null;
                    if (mostRecent != null)
                    {
                        _persistentState.FreedPastSelves.AddRecord(
                            freedPastSashaId: mostRecent.Id,
                            freedRun: _persistentState.RunCounter.TotalRuns,
                            freedFloor: _currentDepth);
                        _persistentState.MarkDirty();
                    }

                    string? catalogEntry = null;
                    if (mostRecent != null && _state != null && _voiceLineRegistry != null)
                        catalogEntry = CatalogEntryRenderer.RenderEntry(
                            mostRecent, _persistentState.PastSashas, _voiceLineRegistry, _state.Rng);

                    _memoEvaluator.EvaluateCatalogReferenced(
                        _persistentState, _memoRegistry,
                        _persistentState.RunCounter.TotalRuns,
                        catalogEntry);
                }
            }
            else if (evt is PossessionNearDeathWarningEvent)
            {
                _toastLog?.AddMessage("[color=#ff4444]Your body is failing — drain is critical![/color]");
            }
            else if (evt is VoiceLineEvent voiceEvt && _state != null)
            {
                var line = _voiceLineRegistry?.GetLine(voiceEvt.TriggerId, _state.Rng, _voiceLineFiredSet);
                if (line != null)
                    _toastLog?.AddMessage($"[color=#b090d0]{line}[/color]");
            }
        }

        // Determine possession state for UI updates.
        bool isPossessing = _state != null && !ReferenceEquals(_state.ControlledEntity, _state.Player);
        bool isPossessionTargeting = _gameController?.IsPossessionTargetingActive ?? false;

        if (_hud != null && _state != null)
            _hud.OnTurnCompleted(result, _state);
        _statusEffectBar?.Refresh(_state.Player);
        _menuButtonBar?.SetAutoExploreActive(_gameController?.IsAutoExploreActive ?? false);
        if (isPossessionTargeting)
            _menuButtonBar?.SetPossessionMode(MenuButtonBar.PossessionMode.Targeting);
        else if (isPossessing)
        {
            // Pass species abilities so the button bar can render them when Hall Wardens ship.
            var abilities = _state?.ControlledEntity.Get<HostAbilityComponent>()?.Abilities;
            _menuButtonBar?.SetPossessionMode(MenuButtonBar.PossessionMode.Active, abilities);
        }
        else
            _menuButtonBar?.SetPossessionMode(MenuButtonBar.PossessionMode.Idle);

        if (_equipmentPanel?.Visible == true && _state != null)
            _equipmentPanel.Refresh(_state);

        // Camera follows the controlled entity. Forced possession exits snap; voluntary tweens.
        var forcedExit = result.Events.OfType<PossessionExitedEvent>()
            .FirstOrDefault(e => e.Reason is not "voluntary" and not null);
        if (forcedExit != null && _gameView != null && _state != null)
            PlayerCamera.Update(_gameView, _state.ControlledEntity, _currentZoom, _renderer); // snap
        else if (_gameView != null && _state != null)
            PlayerCamera.AnimateTo(_gameView, _state.ControlledEntity, this, zoom: _currentZoom, renderer: _renderer);
        _miniMap?.Refresh(_state);
        _toastLog?.RecordTurn(result, _state);
        _groundHazardOverlay?.Refresh(_state);

        // Update fog-of-war — TurnController called RecomputeFov twice this turn
        // (after player action, after monster turns). Apply the result to the renderer.
        if (_tileLayer != null)
        {
            DungeonRenderer.UpdateVisibility(_tileLayer, _state.Map);
            // Re-apply lock color tints to visible locked chests.
            // UpdateVisibility sets all visible feature sprites to White as a baseline;
            // this pass overrides with the lock tint where the chest is still locked.
            RefreshLockedChestTints();
        }
        _entitySprites?.UpdateVisibility(_state);
        _entitySprites?.UpdateStatusTints(_state);
        _itemSprites?.UpdateVisibility(_state);
        // Update floating HP bars after visibility is resolved for this turn.
        if (_entitySprites != null)
            _floatingHpBars?.Refresh(_state, _entitySprites);
    }

    private void OnGameEnded(bool playerWon)
    {
        var stats = $"Turns: {_turnCount}\nMonsters killed: {_monstersKilled}\n" +
                    $"Damage dealt: {_damageDealt}\nDamage taken: {_damageTaken}";
        _gameOverScreen?.Show(playerWon, stats);

        if (_state != null && _persistentState != null)
        {
            // A refusal at the Weighing is NOT a death — Sasha assessed the cost and walked out
            // alive, debt open. No corpse to loot/quip/possess; recording a past-Sasha would be a
            // category error (a living man's body in the catalog of the dead). File the refusal
            // instead — the Under-Warden remembers you turned back. [decision 2026-06-01]
            bool refused = _state.PlayerDeathCause == Logic.Endgame.WeighingConstants.LossRefusedCause;
            if (refused)
            {
                _persistentState.RunCounter.UpdateBestFloor(_currentDepth);
                _persistentState.UnderWarden.WeighingRefusals++;
                _persistentState.MarkDirty();
            }
            // Record a past-Sasha on player death (spec §6.2).
            else if (!playerWon)
            {
                var gear = SnapshotEquippedGear(_state.Player);
                var bestFloor = Math.Max(_persistentState.RunCounter.BestFloorReached, _currentDepth);
                _persistentState.RunCounter.UpdateBestFloor(_currentDepth);

                var killerSpecies = _state.PlayerDeathKillerSpecies;
                bool killerWasFirst = killerSpecies != null
                    && _state.Knowledge.GetEntry(killerSpecies).EngagedCount <= 1;

                // "Clean run" heuristic: died to non-self-inflicted cause at floor 10+.
                bool prevClean = _state.PlayerDeathCause is not ("oil_slick_fire" or "own_poison"
                    or "own_trap" or "possessed_wrong_host") && _currentDepth >= 10;

                _persistentState.PastSashas.AddRecord(
                    diedRun: _persistentState.RunCounter.TotalRuns,
                    diedFloor: _currentDepth,
                    causeOfDeath: _state.PlayerDeathCause,
                    killerSpecies: killerSpecies,
                    gearCarried: gear,
                    bestFloorReachedAtDeath: bestFloor,
                    previousRunWasClean: prevClean,
                    killerWasFirstEncounter: killerWasFirst);
                _persistentState.MarkDirty();
            }

            // Weighing outcome (TASK-008): record the ending. Clean Audit sets the sticky
            // audit_completed flag (drives different memo content forever after); reaching floor 25
            // with a Weighing that resolved counts as an audit attempt.
            if (_state.WeighingArena != null && _state.Ending != Logic.Endgame.EndingType.None)
            {
                _persistentState.UnderWarden.AuditAttemptedRuns++;
                if (_state.Ending == Logic.Endgame.EndingType.CleanAudit)
                    _persistentState.UnderWarden.AuditCompleted = true;
                _persistentState.MarkDirty();
            }

            // Faction reputation: apply transitions at run end (spec §6.3).
            // (Reads UnprovokedOrcKillsThisRun, now fed by the run aggression tally — TASK-003.)
            ApplyFactionRunEnd(_state, _persistentState);

            // Excess metric (TASK-003): flush this run's unprovoked cross-faction kills into the
            // cross-run cumulative total that feeds the Weighing's Auditor's Own / Oathkeeper audit.
            var tally = _state.Player.Get<RunAggressionTally>();
            if (tally != null && tally.Total() > 0)
            {
                foreach (var (faction, count) in tally.UnprovokedKillsByFaction)
                    _persistentState.UnderWarden.AddUnprovokedKill(faction, count);
                _persistentState.MarkDirty();
            }

            // Under-Warden memo delivery: evaluate post-run incidents and queue any
            // memos that should surface in the inbox. Must run BEFORE the persistence
            // flush so queued memos are written in the same atomic write.
            if (_memoRegistry != null)
            {
                var ctx = new PostRunContext(
                    Died: !playerWon,
                    CauseOfDeath: _state.PlayerDeathCause,
                    KillerSpecies: _state.PlayerDeathKillerSpecies,
                    FloorReached: _currentDepth,
                    RunNumber: _persistentState.RunCounter.TotalRuns
                );
                _memoEvaluator.EvaluateRunEnd(ctx, _persistentState, _memoRegistry);
                // MarkDirty is called inside EvaluateRunEnd if any memos were queued.
            }
        }

        // Run end is a forced flush — write regardless of dirty state (spec §5).
        if (_persistentState != null && _persistenceProvider != null)
            _persistentState.Flush(_persistenceProvider, GD.PrintErr);

        // RECORD-then-DELETE (M1.4 4b): the run's outcome is now committed to the cross-run save above,
        // so it survives any crash from here. ONLY now delete the mid-run save. Never the reverse — a
        // crash between must lose the mid-run save, never the record. The load-time terminal check is
        // the net for any mid-run save that slipped through (its state IsGameOver → routed back here).
        if (_persistenceProvider != null)
            Logic.Persistence.MidRun.MidRunFile.Delete(_persistenceProvider.GetMidRunSaveFilePath());
    }

    /// <summary>
    /// Snapshot equipped weapon, armor, and rings at death time (OQ-2 resolution A: equipped only).
    /// </summary>
    private static List<GearItemRecord> SnapshotEquippedGear(Entity player)
    {
        var result = new List<GearItemRecord>();
        var equipment = player.Get<Equipment>();
        if (equipment == null) return result;

        foreach (var slot in new[] { EquipmentSlot.MainHand, EquipmentSlot.Chest, EquipmentSlot.LeftRing, EquipmentSlot.RightRing })
        {
            var item = equipment.GetSlot(slot);
            if (item == null) continue;
            var tag = item.Get<ItemTag>();
            if (tag == null) continue;
            var eq = item.Get<Equippable>();
            var enchantment = eq?.ToHitBonus ?? 0;
            result.Add(new GearItemRecord
            {
                TypeId = tag.TypeId,
                Enchantment = enchantment,
                Condition = (eq is { BaseDamageMax: > 0 } && eq.DamageMax < eq.BaseDamageMax)
                    ? "corroded" : "normal",
                // Notable: enchanted (+1 or better) or a specific NPC-gifted item.
                IsNotable = enchantment > 0 || IsNamedItem(tag.TypeId),
            });
        }
        return result;
    }

    // Named / NPC-gifted items that are always "notable" regardless of enchantment.
    // Expand when items like the Borrek knife are added.
    private static readonly HashSet<string> _namedItemIds = new(StringComparer.Ordinal)
    {
        // placeholder — no named items yet; populated as content is added
    };

    private static bool IsNamedItem(string typeId) => _namedItemIds.Contains(typeId);

    /// <summary>
    /// Apply faction reputation transitions at run end (spec §6.3).
    /// Orc: threshold unprovoked kills → Hostile; otherwise increment/check decay.
    /// </summary>
    private static void ApplyFactionRunEnd(GameState state, PersistentRunState persistent)
    {
        bool hadNegativeAction = state.UnprovokedOrcKillsThisRun >= FactionsData.HostileThreshold;
        if (hadNegativeAction)
            persistent.Factions.ApplyNegativeAction(FactionsData.OrcFactionId);
        else
            persistent.Factions.OnRunEndNoNegativeAction(FactionsData.OrcFactionId);
        persistent.MarkDirty();
    }

    public override void _Notification(int what)
    {
        // App backgrounding: forced flush so in-progress state is not lost on iOS/Android.
        if (what == NotificationApplicationPaused)
        {
            if (_persistentState != null && _persistenceProvider != null)
                _persistentState.Flush(_persistenceProvider, GD.PrintErr);
            // Belt-and-suspenders mid-run flush: write the current floor synchronously and wait for any
            // in-flight background write, so a force-kill after backgrounding still resumes losslessly.
            if (_state != null && _state.IsDungeonMode && !_state.IsGameOver && _midRunWriter != null)
                _midRunWriter.FlushSync(Logic.Persistence.MidRun.MidRunSerializer.SaveMidRun(_state));
            _midRunWriter?.WaitForIdle();
        }
    }

    /// <summary>
    /// Fires after animations complete when the player descends a staircase.
    /// Builds the next floor, carrying the player's current state forward.
    /// </summary>
    private void OnFloorTransitionRequested(int newDepth)
    {
        GD.Print($"Floor transition: depth {_currentDepth} → {newDepth}");
        // Track best floor reached — recorded at stairs-down, so the player gets credit for clearing it.
        if (_persistentState != null)
        {
            _persistentState.RunCounter.UpdateBestFloor(_currentDepth);
            _persistentState.MarkDirty();
        }
        var builder = _testScenarioBuilder ?? _floorBuilder;
        if (builder == null) return;
        var rng = new SeededRandom(_baseSeed + newDepth * 1_000_003);
        _currentDepth = newDepth;
        _state = builder.Build(newDepth, rng, _state?.Player,
            identificationRegistry: _state?.IdentificationRegistry,
            appearancePool: _state?.AppearancePool,
            boonTracker: _state?.BoonTracker,
            muralTracker: _state?.MuralTracker,
            pityTracker: _state?.PityTracker,
            persistentState: _persistentState);

        // Inject the audit dialogue registry on the Weighing floor so the orchestrator
        // can emit voiced beats when Guardians rise.
        if (_state?.WeighingArena != null && _weighingAuditRegistry != null)
            _state.WeighingAudit = _weighingAuditRegistry;

        SetupPresentation(_state);

        // Mid-run save: write the NEW floor synchronously so a kill in the Build-to-first-turn window
        // resumes into this floor, never the previous one (M1.4 4b ruling).
        if (_state != null && _state.IsDungeonMode && _midRunWriter != null)
            _midRunWriter.FlushSync(Logic.Persistence.MidRun.MidRunSerializer.SaveMidRun(_state));

        // Floor descent is a narrative-event-boundary flush (spec §5).
        if (_persistentState != null && _persistenceProvider != null && _persistentState.IsDirty)
            _persistentState.Flush(_persistenceProvider, GD.PrintErr);
    }

    private void OnInventoryItemTapped(int itemId)
    {
        _gameController?.HandleInventoryTap(itemId);
    }

    private void OnGearRequested()
    {
        if (_equipmentPanel == null || _state == null) return;
        if (_equipmentPanel.Visible)
            _equipmentPanel.Hide();
        else
            _equipmentPanel.Show(_state);
    }

    private void OnReplayRequested()
    {
        // Hide the game-over screen first in all paths.
        _gameOverScreen?.Hide();

        // If there are pending Under-Warden memos, show the inbox before returning
        // to the main menu. OnInboxClosed handles the menu navigation.
        if (_persistentState != null && _persistentState.UnderWarden.PendingMemos.Count > 0
            && _memoInboxPanel != null && _memoRegistry != null && _persistenceProvider != null)
        {
            _memoInboxPanel.Show(_persistentState, _persistenceProvider, _memoRegistry);
        }
        else
        {
            _currentDepth = 1;
            ShowMainMenu();
        }
    }

    /// <summary>
    /// Called when the player has dismissed all pending memos and the inbox closes.
    /// Navigates back to the main menu to begin a new run.
    /// </summary>
    private void OnInboxClosed()
    {
        if (_memoInboxPanel != null)
            _memoInboxPanel.Visible = false;
        _currentDepth = 1;
        ShowMainMenu();
    }

    // -------------------------------------------------------------------------
    // Zone layout helpers
    // -------------------------------------------------------------------------

    /// <summary>
    /// Add a full-rect ColorRect placeholder to a zone container so the zone is
    /// visible during development. Replaced with real content in later phases.
    /// The placeholder MouseFilter=Ignore so it doesn't consume taps.
    /// </summary>
    private static void AddZonePlaceholder(Control zone, Color color)
    {
        var bg = new ColorRect { Color = color };
        bg.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        bg.MouseFilter = Control.MouseFilterEnum.Ignore;
        zone.AddChild(bg);
    }

    // -------------------------------------------------------------------------
    // Menu system
    // -------------------------------------------------------------------------

    /// <summary>
    /// Show the main menu. Clears any existing panels in MenuLayer and creates fresh ones.
    /// MenuLayer (layer=20) sits above UILayer (layer=10) so it covers everything.
    /// </summary>
    private void ShowMainMenu(string? notice = null)
    {
        var menuLayer = GetNode<CanvasLayer>("MenuLayer");
        ClearMenuLayer(menuLayer);
        menuLayer.Visible = true;

        var panel = new MainMenuPanel();
        menuLayer.AddChild(panel);

        panel.NewGameRequested      += OnNewGameRequested;
        panel.ExploreModeRequested  += OnExploreModeRequested;
        panel.TestingModeRequested  += ShowTestMenu;
        panel.OptionsRequested      += ShowOptions;

        // Quiet one-line notice (e.g. a corrupt save was set aside). Bottom-anchored, unobtrusive.
        if (!string.IsNullOrEmpty(notice))
        {
            GD.Print($"[Main] menu notice: {notice}");
            var label = new Label
            {
                Text = notice,
                HorizontalAlignment = HorizontalAlignment.Center,
                AnchorTop = 0.92f, AnchorBottom = 1f, AnchorLeft = 0f, AnchorRight = 1f,
            };
            label.AddThemeColorOverride("font_color", new Color(0.8f, 0.8f, 0.8f));
            menuLayer.AddChild(label);
        }
    }

    /// <summary>
    /// Startup entry: silently RESUME a valid non-terminal mid-run save (no menu, no prompt), reusing
    /// the existing floor-entry presentation path; otherwise fall through to the menu. Corrupt/mismatched
    /// saves are ARCHIVED (never deleted) and the menu shows a quiet notice. A terminal save routes to the
    /// death/victory flow (record + delete), never into play. (M1.4 4b — Rafe's rulings.)
    /// </summary>
    private void ResumeOrShowMenu()
    {
        if (_persistenceProvider == null) { ShowMainMenu(); return; }
        var path = _persistenceProvider.GetMidRunSaveFilePath();
        var result = Logic.Persistence.MidRun.MidRunFile.LoadMidRunFromFile(path);

        switch (result.Status)
        {
            case Logic.Persistence.MidRun.MidRunLoadStatus.Ok:
                GameState loaded;
                try { loaded = Logic.Persistence.MidRun.MidRunSerializer.LoadMidRun(result.Save!, _boonTable); }
                catch (System.Exception ex)
                {
                    GD.PrintErr($"[Main] mid-run load failed post-parse: {ex.Message}");
                    Logic.Persistence.MidRun.MidRunFile.ArchiveCorrupt(path);
                    ShowMainMenu("A saved run couldn't be loaded and was set aside.");
                    return;
                }
                _state = loaded;
                _currentDepth = loaded.CurrentDepth;
                if (loaded.IsGameOver)
                {
                    // Load-time terminal net: never resume into play. Route to the death/victory flow,
                    // which records the outcome + deletes the save idempotently.
                    bool won = loaded.IsDungeonVictory
                        || (loaded.Ending == Logic.Endgame.EndingType.None && loaded.PlayerWon);
                    OnGameEnded(won);
                    if (_gameOverScreen == null) ShowMainMenu();   // no game-over UI exists yet at startup
                }
                else
                {
                    GD.Print($"[Main] Resuming mid-run save — depth {loaded.CurrentDepth}, turn {loaded.TurnCount}.");
                    _currentDepth = loaded.CurrentDepth;
                    SetupPresentation(loaded);   // reuse the floor-entry path (sprites/camera/FOV) — silent
                }
                return;

            case Logic.Persistence.MidRun.MidRunLoadStatus.Corrupt:
            case Logic.Persistence.MidRun.MidRunLoadStatus.SchemaMismatch:
                var archived = Logic.Persistence.MidRun.MidRunFile.ArchiveCorrupt(path);
                GD.PrintErr($"[Main] mid-run save unreadable ({result.Status}: {result.Error}); archived to {archived}.");
                ShowMainMenu("A saved run was unreadable and was set aside.");
                return;

            default:  // FileNotFound — the normal fresh-launch path
                ShowMainMenu();
                return;
        }
    }

    private void OnExploreModeRequested()
    {
        GetNode<CanvasLayer>("MenuLayer").Visible = false;
        _currentDepth = 1;
        _baseSeed = Random.Shared.Next();
        GD.Print($"[Main] Explore mode seed: {_baseSeed}");
        StartDungeon(explorationMode: true);
    }

    private void OnNewGameRequested()
    {
        GetNode<CanvasLayer>("MenuLayer").Visible = false;
        _currentDepth = 1;
        // Each new game gets a unique seed so no two runs are identical.
        // The seed is stored in _baseSeed and recoverable from GameState.Rng.Seed
        // for future "show seed" or seed-entry UI.
        _baseSeed = Random.Shared.Next();
        GD.Print($"[Main] New game seed: {_baseSeed}");
        StartDungeon();
    }

    /// <summary>
    /// Discover available test scenarios, then show the test scenario picker panel.
    /// </summary>
    private void ShowTestMenu()
    {
        var menuLayer = GetNode<CanvasLayer>("MenuLayer");
        ClearMenuLayer(menuLayer);

        var scenarios = DiscoverTestScenarios();
        var panel = new TestMenuPanel(scenarios);
        menuLayer.AddChild(panel);

        panel.ScenarioSelected += LaunchTestScenario;
        panel.BackRequested    += () => ShowMainMenu();
    }

    private void ShowOptions()
    {
        var menuLayer = GetNode<CanvasLayer>("MenuLayer");
        ClearMenuLayer(menuLayer);

        // Pass the loaded tileset ID so the panel can detect changes made this session.
        var loadedId = _spriteMapping?.TilesetId ?? "ultimate_fantasy";
        var panel = new OptionsPanel(loadedId, _debugOverlay);
        menuLayer.AddChild(panel);

        panel.BackRequested += () => ShowMainMenu();
    }

    /// <summary>
    /// Boot directly into the fixed art-acceptance test scene (--art-scene launch flag).
    ///
    /// The authored floor data comes entirely from ArtAcceptanceSceneBuilder (Logic layer,
    /// no Godot dependency, unit-tested in tests/Core/ArtAcceptanceSceneBuilderTests.cs).
    /// This method's only job is the seam: hand that GameState to SetupPresentation, the
    /// exact same shared entry point StartDungeon/LaunchTestScenario use, which in turn
    /// calls DungeonRenderer.Render(state.Map, ..., props: state.Props, features: state.Features)
    /// — the same render call a procedurally generated floor goes through. No parallel
    /// rendering path exists for this scene.
    /// </summary>
    private void LaunchArtAcceptanceScene()
    {
        GetNode<CanvasLayer>("MenuLayer").Visible = false;

        _currentDepth = 1;
        _state = ArtAcceptanceSceneBuilder.Build(_monsterFactory!, _itemFactory!, _consumableFactory!);

        SetupPresentation(_state);
        GD.Print("Ready (art acceptance scene) — " +
                 $"{_state.Monsters.Count} monsters, {_state.Props.Count} props, {_state.Features.Count} features, " +
                 $"{_state.FloorItems.Count} floor items.");
    }

    /// <summary>
    /// --art-scene-capture: log the worn-tile (3001) in-frame report, save the settled
    /// viewport to --capture-out, and quit. Called once _pendingCameraSnapFrames has
    /// reached 0 and the extra settle buffer has elapsed (see _Process).
    /// </summary>
    private void CaptureAndQuit()
    {
        _pendingCapture = false;

        if (string.IsNullOrEmpty(_captureOutputPath))
        {
            GD.PrintErr("[Main] --art-scene-capture requires --capture-out <path>. Not capturing.");
            GetTree().Quit(1);
            return;
        }

        LogWornTilePositions();

        var image = GetViewport().GetTexture().GetImage();
        var dir = System.IO.Path.GetDirectoryName(_captureOutputPath);
        if (!string.IsNullOrEmpty(dir))
            System.IO.Directory.CreateDirectory(dir);
        var err = image.SavePng(_captureOutputPath);
        if (err != Error.Ok)
            GD.PrintErr($"[Main] Capture save failed ({err}): {_captureOutputPath}");
        else
            GD.Print($"[Main] Capture written: {_captureOutputPath}");

        GetTree().Quit(err == Error.Ok ? 0 : 1);
    }

    /// <summary>
    /// The tile-coordinate rect actually visible in the playable strip between the HUD
    /// margins — same math PlayerCamera.Update used to position/scale _gameView, inverted.
    /// Read-only consumption of existing camera state; does not modify rendering.
    /// </summary>
    private (int x0, int y0, int x1, int y1) ComputeVisibleTileRect()
    {
        var viewport = _gameView!.GetViewport().GetVisibleRect().Size;
        var topLeftScreen = new Vector2(0, PlayerCamera.UiTopMargin);
        var bottomRightScreen = new Vector2(viewport.X, viewport.Y - PlayerCamera.UiBottomMargin);

        Vector2 ToLocal(Vector2 screen) => (screen - _gameView.Position) / _gameView.Scale;

        var (x0, y0) = _renderer!.ScreenToGrid(ToLocal(topLeftScreen));
        var (x1, y1) = _renderer.ScreenToGrid(ToLocal(bottomRightScreen));
        return (x0, y0, x1, y1);
    }

    /// <summary>
    /// Honest floor_worn (3001) in-frame check (spec §5 merge evidence). Calls
    /// FloorComposer.Compose a second time with the exact inputs DungeonRenderer.Render
    /// already used internally (state.Map, seed: 0 — Render's own default, not reproduced
    /// from a guess) to recover which cells it marked Worn; that dictionary is otherwise
    /// discarded by Render and never returned to the caller. Read-only — does not touch
    /// render code. Reproduces Render's own prop-footprint suppression (worn/accent tiles
    /// under blocking props render as Standard) so a suppressed cell isn't misreported as
    /// "worn and in frame" when it visually isn't.
    /// </summary>
    private void LogWornTilePositions()
    {
        if (_state == null) return;

        var floorMap = FloorComposer.Compose(_state.Map, seed: 0);

        var propFootprint = new HashSet<(int, int)>();
        foreach (var p in _state.Props)
            if (p.BlocksMovement)
                for (int fx = p.X; fx < p.X + p.FootprintW; fx++)
                    for (int fy = p.Y; fy < p.Y + p.FootprintH; fy++)
                        propFootprint.Add((fx, fy));

        var wornPositions = floorMap
            .Where(kv => kv.Value == FloorTileType.Worn && !propFootprint.Contains(kv.Key))
            .Select(kv => kv.Key)
            .OrderBy(p => p.Y).ThenBy(p => p.X)
            .ToList();

        var (x0, y0, x1, y1) = ComputeVisibleTileRect();
        var inFrame = wornPositions.Where(p => p.X >= x0 && p.X <= x1 && p.Y >= y0 && p.Y <= y1).ToList();

        GD.Print($"[Main] Visible tile rect: ({x0},{y0})-({x1},{y1})");
        GD.Print($"[Main] floor_worn (3001) tiles: {wornPositions.Count} rendered in the authored room, " +
                  $"{inFrame.Count} in frame: " +
                  string.Join(", ", inFrame.Select(p => $"({p.X},{p.Y})")));
    }

    /// <summary>
    /// Load a test scenario YAML by res:// path and start the game.
    /// Hides the menu layer so the dungeon is visible.
    ///
    /// Routing: when scenario.DungeonMode=true, builds a procedural floor via DungeonFloorBuilder
    /// with the scenario's GuaranteedSpawns injected. Player uses CreateDefaultPlayer() stats.
    /// When false (default), routes through GameStateFactory.FromScenario (flat arena, unchanged).
    ///
    /// Test scenarios always use the current _baseSeed (default 1337) for deterministic replay.
    /// </summary>
    private void LaunchTestScenario(string resPath)
    {
        GetNode<CanvasLayer>("MenuLayer").Visible = false;

        var yaml     = ReadGodotResource(resPath);
        var scenario = _contentLoader!.LoadScenario(yaml);

        if (scenario.DungeonMode)
        {
            // Build a LevelOverride from the scenario's guaranteed spawns.
            // Use small map dimensions for fast load times in test scenarios.
            var levelOverride = new LevelOverride
            {
                GuaranteedSpawns = scenario.GuaranteedSpawns,
                Parameters = new GenerationParameters
                {
                    MapWidth = 60,
                    MapHeight = 40,
                    MaxRooms = 20,
                },
            };

            var registry = LevelTemplateRegistry.FromSingleDepth(scenario.Depth, levelOverride);
            _testScenarioBuilder = new DungeonFloorBuilder(
                registry, _monsterFactory!, _itemFactory!, _consumableFactory!,
                spellItemFactory: _spellItemFactory);

            // Deterministic seed: test scenarios use _baseSeed (default 1337), not randomized.
            var rng = new SeededRandom(_baseSeed + scenario.Depth * 1_000_003);
            _currentDepth = scenario.Depth;
            _state = _testScenarioBuilder.Build(scenario.Depth, rng);

            if (scenario.AllItemsIdentified && _state.IdentificationRegistry != null)
                _state.IdentificationRegistry.AlwaysIdentified = true;

            SetupPresentation(_state);
            GD.Print($"Ready (dungeon-mode test scenario: {resPath}) — depth {scenario.Depth}, " +
                     $"{_state.Monsters.Count} monsters, {_state.FloorItems.Count} floor items. Tap to play.");
        }
        else
        {
            _state = GameStateFactory.FromScenario(
                scenario, _baseSeed, _monsterFactory!, _itemFactory!, _consumableFactory!);

            if (scenario.AllItemsIdentified && _state.IdentificationRegistry != null)
                _state.IdentificationRegistry.AlwaysIdentified = true;

            SetupPresentation(_state);
            GD.Print($"Ready (test scenario: {resPath}) — {_state.Monsters.Count} monsters. Tap to play.");
        }

        // Auto-start bot mode if the scenario specifies a default persona.
        if (!string.IsNullOrEmpty(scenario.DefaultBotPersona) && _botDriver != null)
        {
            _botDriver.SetPersona(scenario.DefaultBotPersona);
            _botDriver.Enable();
            GD.Print($"[TestMode] Bot auto-started with persona: {scenario.DefaultBotPersona}");
        }
    }

    /// <summary>
    /// Scan res://config/testing/ and user://testing/ for .yaml files.
    /// Returns a sorted list of (name, path, category) tuples.
    /// Never throws — returns empty list on missing directory.
    /// </summary>
    private static List<(string name, string path, string category)> DiscoverTestScenarios()
    {
        var results = new List<(string, string, string)>();
        ScanTestDirectory("res://config/testing/", results);
        ScanTestDirectory("user://testing/", results);
        results.Sort((a, b) =>
        {
            var cat = string.Compare(a.Item3, b.Item3, System.StringComparison.Ordinal);
            return cat != 0 ? cat : string.Compare(a.Item1, b.Item1, System.StringComparison.Ordinal);
        });
        return results;
    }

    private static void ScanTestDirectory(string dir, List<(string, string, string)> results)
    {
        using var access = DirAccess.Open(dir);
        if (access == null) return;

        access.ListDirBegin();
        string fileName;
        while ((fileName = access.GetNext()) != "")
        {
            if (!fileName.EndsWith(".yaml", System.StringComparison.OrdinalIgnoreCase)) continue;
            var resPath = dir + fileName;
            var (name, category) = ExtractScenarioMeta(resPath, fileName);
            results.Add((name, resPath, category));
        }
        access.ListDirEnd();
    }

    /// <summary>
    /// Extract `name:` and `category:` fields from a scenario YAML file without full deserialisation.
    /// Falls back to filename stem / "Uncategorised" if fields are absent.
    /// </summary>
    private static (string name, string category) ExtractScenarioMeta(string resPath, string fileName)
    {
        string name     = System.IO.Path.GetFileNameWithoutExtension(fileName);
        string category = "Uncategorised";
        try
        {
            using var file = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Read);
            if (file == null) return (name, category);

            var text = file.GetAsText();
            foreach (var line in text.Split('\n'))
            {
                var trimmed = line.TrimStart();
                if (trimmed.StartsWith("name:", System.StringComparison.Ordinal))
                {
                    var v = StripYamlInline(trimmed["name:".Length..]);
                    if (v.Length > 0) name = v;
                }
                else if (trimmed.StartsWith("category:", System.StringComparison.Ordinal))
                {
                    var v = StripYamlInline(trimmed["category:".Length..]);
                    if (v.Length > 0) category = v;
                }
            }
        }
        catch (System.Exception) { /* Best-effort */ }
        return (name, category);
    }

    private static string StripYamlInline(string raw)
    {
        var v = raw.Trim();
        if (v.Length >= 2 && v[0] == '"' && v[^1] == '"') v = v[1..^1];
        return v;
    }

    /// <summary>
    /// Remove all children from the menu layer so panels are created fresh each time.
    /// Keeps the implementation simple — no panel caching.
    /// </summary>
    private static void ClearMenuLayer(CanvasLayer layer)
    {
        foreach (var child in layer.GetChildren())
            child.SafeFree();
    }

    /// <summary>
    /// Build the zoom +/− button panel. Positioned to the left of the minimap.
    /// Map is always 120×80, so minimap is 240×160 px at 2px/tile.
    /// Minimap OffsetRight = -8, OffsetLeft = -248. Zoom panel sits at OffsetRight = -252, OffsetLeft = -292.
    /// </summary>
    private Control BuildZoomPanel()
    {
        var panel = new VBoxContainer();
        panel.AnchorLeft   = 1f;
        panel.AnchorTop    = 0f;
        panel.AnchorRight  = 1f;
        panel.AnchorBottom = 0f;
        panel.OffsetTop    = 120f; // 210 - 90 (ViewportOverlay starts at StatusBar bottom)
        panel.OffsetLeft   = -292f;
        panel.OffsetRight  = -252f;

        var btnZoomIn = new Button { Text = "+" };
        btnZoomIn.AddThemeFontSizeOverride("font_size", 18);
        btnZoomIn.CustomMinimumSize = new Vector2(36, 36);
        btnZoomIn.Pressed += () =>
        {
            _currentZoom = System.Math.Min(_renderer.MaxZoom, _currentZoom + ZoomStep);
            if (_gameView != null && _state != null)
                PlayerCamera.Update(_gameView, _state.ControlledEntity, _currentZoom, _renderer);
        };

        var btnZoomOut = new Button { Text = "−" };
        btnZoomOut.AddThemeFontSizeOverride("font_size", 18);
        btnZoomOut.CustomMinimumSize = new Vector2(36, 36);
        btnZoomOut.Pressed += () =>
        {
            _currentZoom = System.Math.Max(_renderer.MinZoom, _currentZoom - ZoomStep);
            if (_gameView != null && _state != null)
                PlayerCamera.Update(_gameView, _state.ControlledEntity, _currentZoom, _renderer);
        };

        panel.AddChild(btnZoomIn);
        panel.AddChild(btnZoomOut);

        return panel;
    }

    /// <summary>
    /// Read a file from Godot's resource system. On desktop, res:// maps to the project
    /// directory. On iOS/Android, res:// files are packed inside the .pck bundle and
    /// cannot be accessed via System.IO.File. Godot's FileAccess handles this transparently.
    /// </summary>
    private static string ReadGodotResource(string resPath)
    {
        using var file = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Read);
        if (file == null)
            throw new System.IO.FileNotFoundException($"Godot resource not found: {resPath}");
        var text = file.GetAsText();
        GD.Print($"[ReadGodotResource] {resPath}: {text.Length} chars, starts with: {text[..System.Math.Min(80, text.Length)]}");
        return text;
    }
}
