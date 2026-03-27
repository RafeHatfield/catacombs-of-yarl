namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// An axis-aligned rectangular room in a generated dungeon.
/// X, Y are the top-left corner (inclusive). Width and Height are in tiles.
/// Interior tiles are [X, X+Width) x [Y, Y+Height).
/// </summary>
public sealed record Room(int X, int Y, int Width, int Height)
{
    public int CenterX => X + Width / 2;
    public int CenterY => Y + Height / 2;

    /// <summary>
    /// True if this room overlaps the other room, including a 1-tile padding gap.
    /// Matches the Python prototype's Rect.intersect() which uses > not >= so that rooms
    /// touching at an edge (with 1-tile gap) are considered non-intersecting.
    /// </summary>
    public bool Intersects(Room other)
    {
        // Expand each room by 1 tile in all directions for the padding check
        return X - 1 < other.X + other.Width
            && X + Width + 1 > other.X
            && Y - 1 < other.Y + other.Height
            && Y + Height + 1 > other.Y;
    }

    /// <summary>True if the tile (x, y) falls inside this room's interior.</summary>
    public bool Contains(int x, int y)
        => x >= X && x < X + Width && y >= Y && y < Y + Height;
}
