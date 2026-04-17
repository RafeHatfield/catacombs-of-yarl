namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Simple tile grid for scenario arenas and generated dungeons.
/// Tracks walkable tiles, tile kinds, and entity positions.
/// No rendering, no Godot — pure logic.
/// </summary>
public sealed class GameMap
{
    public int Width { get; }
    public int Height { get; }

    private readonly bool[,] _walkable;
    private readonly TileKind[,] _tiles;
    private readonly bool[,] _visible;
    private readonly bool[,] _explored;
    private readonly TileTheme[,] _theme;
    private readonly List<Entity> _entities = new();
    private readonly HashSet<(int, int)> _propCells = new();

    /// <summary>Default constructor: all tiles walkable (existing behavior for scenarios).</summary>
    public GameMap(int width, int height)
    {
        Width = width;
        Height = height;
        _walkable = new bool[width, height];
        _tiles = new TileKind[width, height];
        _visible = new bool[width, height];
        _explored = new bool[width, height];
        _theme = new TileTheme[width, height]; // zero-initialises to TileTheme.Grey

        // Default: all tiles walkable (existing scenario behavior preserved)
        for (int x = 0; x < width; x++)
            for (int y = 0; y < height; y++)
            {
                _walkable[x, y] = true;
                _tiles[x, y] = TileKind.Floor;
            }
        // _visible and _explored default to false (not yet seen)
    }

    /// <summary>
    /// Dungeon-generation constructor: all tiles initialised as Wall (non-walkable).
    /// Use SetTile to carve rooms and corridors.
    /// </summary>
    public GameMap(int width, int height, bool allWalls)
    {
        Width = width;
        Height = height;
        _walkable = new bool[width, height];
        _tiles = new TileKind[width, height];
        _visible = new bool[width, height];
        _explored = new bool[width, height];
        _theme = new TileTheme[width, height]; // zero-initialises to TileTheme.Grey

        if (allWalls)
        {
            // All tiles start as Wall / non-walkable — generator carves from here
            for (int x = 0; x < width; x++)
                for (int y = 0; y < height; y++)
                {
                    _walkable[x, y] = false;
                    _tiles[x, y] = TileKind.Wall;
                }
        }
        else
        {
            // Treat same as default constructor
            for (int x = 0; x < width; x++)
                for (int y = 0; y < height; y++)
                {
                    _walkable[x, y] = true;
                    _tiles[x, y] = TileKind.Floor;
                }
        }
        // _visible and _explored default to false (not yet seen)
    }

    /// <summary>
    /// Create an enclosed arena (walls on edges, floor inside).
    /// Used by scenario harness — behavior is identical to before TileKind was added.
    /// Writes _walkable directly (not via SetTile) to preserve the exact prior logic.
    /// _tiles is kept in sync manually.
    /// </summary>
    public static GameMap CreateArena(int width, int height)
    {
        var map = new GameMap(width, height);
        for (int x = 0; x < width; x++)
        {
            map._walkable[x, 0] = false;
            map._tiles[x, 0] = TileKind.Wall;
            map._walkable[x, height - 1] = false;
            map._tiles[x, height - 1] = TileKind.Wall;
        }
        for (int y = 0; y < height; y++)
        {
            map._walkable[0, y] = false;
            map._tiles[0, y] = TileKind.Wall;
            map._walkable[width - 1, y] = false;
            map._tiles[width - 1, y] = TileKind.Wall;
        }
        return map;
    }

    public bool InBounds(int x, int y) => x >= 0 && x < Width && y >= 0 && y < Height;

    // --- Visibility / FOV ---

    public bool IsVisible(int x, int y) => InBounds(x, y) && _visible[x, y];
    public bool IsExplored(int x, int y) => InBounds(x, y) && _explored[x, y];

    /// <summary>
    /// Mark (x, y) as visible this turn and explored permanently.
    /// Called by FovComputer for each tile in line-of-sight.
    /// </summary>
    public void SetVisible(int x, int y)
    {
        if (!InBounds(x, y)) return;
        _visible[x, y] = true;
        _explored[x, y] = true; // seeing a tile = explored, forever
    }

    /// <summary>
    /// Clear per-turn visibility. Called at the start of each FOV recompute.
    /// Explored state is unaffected — explored tiles are never un-explored.
    /// </summary>
    public void ClearAllVisible()
    {
        Array.Clear(_visible, 0, _visible.Length);
    }

    /// <summary>
    /// Mark all tiles visible and explored. Used for scenarios (no fog of war).
    /// Called by GameStateFactory.FromScenario after map creation.
    /// The policy "scenarios have no fog" lives at the factory level, not here.
    /// </summary>
    public void RevealAll()
    {
        for (int x = 0; x < Width; x++)
            for (int y = 0; y < Height; y++)
            {
                _visible[x, y] = true;
                _explored[x, y] = true;
            }
    }

    public bool IsWalkable(int x, int y) => InBounds(x, y) && _walkable[x, y] && !_propCells.Contains((x, y));

    /// <summary>
    /// Mark a grid cell as occupied by a blocking prop.
    /// Called during dungeon generation after prop placement.
    /// </summary>
    public void MarkPropCell(int x, int y)
    {
        if (InBounds(x, y)) _propCells.Add((x, y));
    }

    /// <summary>Returns true if a blocking prop occupies this cell.</summary>
    public bool IsPropCell(int x, int y) => _propCells.Contains((x, y));

    /// <summary>
    /// Remove a prop cell marking. Used during connectivity repair when a
    /// previously placed prop is removed to restore passage.
    /// </summary>
    public void UnmarkPropCell(int x, int y) => _propCells.Remove((x, y));

    /// <summary>
    /// Returns true only for actual wall tiles (tile array = Wall).
    /// Used by the wall autotile renderer — does NOT include prop cells.
    /// This separation prevents prop sprites from generating wall graphics around them.
    /// </summary>
    public bool IsWallTile(int x, int y) => InBounds(x, y) && !_walkable[x, y];

    /// <summary>Returns the tile kind at (x, y). Returns Wall if out of bounds.</summary>
    public TileKind GetTileKind(int x, int y)
    {
        if (!InBounds(x, y)) return TileKind.Wall;
        return _tiles[x, y];
    }

    /// <summary>
    /// Set the tile kind and keep _walkable in sync.
    /// Floor, Corridor, StairDown, StairUp, Door = walkable.
    /// Wall, Trap = not walkable.
    /// NOTE: CreateArena writes _walkable directly and bypasses this — that is intentional.
    /// </summary>
    public void SetTile(int x, int y, TileKind kind)
    {
        if (!InBounds(x, y)) return;
        _tiles[x, y] = kind;
        _walkable[x, y] = kind switch
        {
            TileKind.Floor => true,
            TileKind.Corridor => true,
            TileKind.StairDown => true,
            TileKind.StairUp => true,
            TileKind.Door => true,
            TileKind.Wall => false,
            TileKind.Trap => false,
            _ => false,
        };
    }

    // --- Tile theme ---

    /// <summary>Returns the visual theme for a tile. Defaults to Grey if out of bounds.</summary>
    public TileTheme GetTileTheme(int x, int y) =>
        InBounds(x, y) ? _theme[x, y] : TileTheme.Grey;

    /// <summary>Set the visual theme for a single tile.</summary>
    public void SetTileTheme(int x, int y, TileTheme theme)
    {
        if (InBounds(x, y)) _theme[x, y] = theme;
    }

    /// <summary>Set theme for a rectangular region (inclusive bounds).</summary>
    public void SetTileThemeRect(int x1, int y1, int x2, int y2, TileTheme theme)
    {
        for (int x = x1; x <= x2; x++)
            for (int y = y1; y <= y2; y++)
                SetTileTheme(x, y, theme);
    }

    /// <summary>All entities currently registered on this map (players, monsters, floor items, stairs).</summary>
    public IReadOnlyList<Entity> Entities => _entities;

    public void RegisterEntity(Entity entity) => _entities.Add(entity);
    public void UnregisterEntity(Entity entity) => _entities.Remove(entity);

    /// <summary>Check if a tile is blocked by a living, movement-blocking entity.</summary>
    public bool IsBlocked(int x, int y)
    {
        if (!IsWalkable(x, y)) return true;
        return _entities.Any(e => e.X == x && e.Y == y && e.BlocksMovement && IsEntityAlive(e));
    }

    /// <summary>Check if a tile is free to move into.</summary>
    public bool CanMoveTo(int x, int y) => IsWalkable(x, y) &&
        !_entities.Any(e => e.X == x && e.Y == y && e.BlocksMovement && IsEntityAlive(e));

    /// <summary>
    /// Check if a tile can be moved into, with optional exclusions.
    /// excludeEntity: this entity is not counted as a blocker (an entity can't block itself).
    /// ignoreEntityAtDest: when true, entity blocking at (x,y) is ignored — allows pathing TO an occupied tile.
    /// </summary>
    public bool CanMoveToWith(int x, int y, Entity? excludeEntity, bool ignoreEntityAtDest = false)
    {
        if (!IsWalkable(x, y)) return false;
        return !_entities.Any(e =>
            e.X == x && e.Y == y
            && e.BlocksMovement
            && IsEntityAlive(e)
            && (excludeEntity == null || e.Id != excludeEntity.Id)
            && !ignoreEntityAtDest);
    }

    private static bool IsEntityAlive(Entity e)
    {
        var fighter = e.Get<Combat.Fighter>();
        return fighter == null || fighter.IsAlive; // non-fighters don't block based on alive status
    }

    /// <summary>
    /// Move entity one step toward target using simple greedy pathfinding.
    /// Tries direct path first, then axis-aligned alternatives.
    /// Returns true if the entity moved.
    /// </summary>
    public bool MoveToward(Entity mover, int targetX, int targetY)
    {
        int dx = Math.Sign(targetX - mover.X);
        int dy = Math.Sign(targetY - mover.Y);

        // Try diagonal first
        if (dx != 0 && dy != 0 && CanMoveTo(mover.X + dx, mover.Y + dy))
        {
            mover.X += dx;
            mover.Y += dy;
            return true;
        }

        // Try horizontal
        if (dx != 0 && CanMoveTo(mover.X + dx, mover.Y))
        {
            mover.X += dx;
            return true;
        }

        // Try vertical
        if (dy != 0 && CanMoveTo(mover.X, mover.Y + dy))
        {
            mover.Y += dy;
            return true;
        }

        return false;
    }
}
