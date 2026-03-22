namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Simple tile grid for scenario arenas. Tracks walkable tiles and entity positions.
/// No rendering, no Godot — pure logic.
/// </summary>
public sealed class GameMap
{
    public int Width { get; }
    public int Height { get; }

    private readonly bool[,] _walkable;
    private readonly List<Entity> _entities = new();

    public GameMap(int width, int height)
    {
        Width = width;
        Height = height;
        _walkable = new bool[width, height];

        // Default: all tiles walkable
        for (int x = 0; x < width; x++)
            for (int y = 0; y < height; y++)
                _walkable[x, y] = true;
    }

    /// <summary>Create an enclosed arena (walls on edges, floor inside).</summary>
    public static GameMap CreateArena(int width, int height)
    {
        var map = new GameMap(width, height);
        for (int x = 0; x < width; x++)
        {
            map._walkable[x, 0] = false;
            map._walkable[x, height - 1] = false;
        }
        for (int y = 0; y < height; y++)
        {
            map._walkable[0, y] = false;
            map._walkable[width - 1, y] = false;
        }
        return map;
    }

    public bool InBounds(int x, int y) => x >= 0 && x < Width && y >= 0 && y < Height;

    public bool IsWalkable(int x, int y) => InBounds(x, y) && _walkable[x, y];

    public void RegisterEntity(Entity entity) => _entities.Add(entity);

    /// <summary>Check if a tile is blocked by a movement-blocking entity.</summary>
    public bool IsBlocked(int x, int y)
    {
        if (!IsWalkable(x, y)) return true;
        return _entities.Any(e => e.X == x && e.Y == y && e.BlocksMovement);
    }

    /// <summary>Check if a tile is free to move into.</summary>
    public bool CanMoveTo(int x, int y) => IsWalkable(x, y) && !_entities.Any(e => e.X == x && e.Y == y && e.BlocksMovement);

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
