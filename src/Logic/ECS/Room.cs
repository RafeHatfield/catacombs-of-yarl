namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// The carved shape of a room's interior. Rectangle is the default and matches the
/// bounding box exactly. All other shapes carve a non-rectangular footprint within
/// the same bounding box — overlap detection and entity placement still use the box.
/// </summary>
public enum RoomShape
{
    Rectangle,    // Full bounding box carved as floor (original behavior)
    Union,        // Two overlapping rectangles — produces L/T/cross shapes
    Cave,         // Cellular automata blob
    Circle,       // Ellipse fitted to bounding box dimensions
    Alcove,       // Rectangle with niche protrusions on the wall edges
    CorridorRoom, // Long thin strip (width 2-3, full bounding-box length)
}

/// <summary>
/// An axis-aligned rectangular room in a generated dungeon.
/// X, Y are the top-left corner (inclusive). Width and Height are in tiles.
/// Interior tiles are [X, X+Width) x [Y, Y+Height).
///
/// Shape records which carving algorithm was used. The actual walkable footprint
/// lives in GameMap — the bounding box is always used for overlap testing and
/// entity placement filtering.
/// </summary>
public sealed record Room(int X, int Y, int Width, int Height)
{
    public int CenterX => X + Width / 2;
    public int CenterY => Y + Height / 2;

    /// <summary>
    /// The shape that was carved into GameMap for this room.
    /// Defaults to Rectangle so all existing new Room(x,y,w,h) call sites compile unchanged.
    /// Set with: newRoom = newRoom with { Shape = shape };
    /// </summary>
    public RoomShape Shape { get; init; } = RoomShape.Rectangle;

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
