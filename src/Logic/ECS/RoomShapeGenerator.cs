using CatacombsOfYarl.Logic.Core;

namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Selects and carves non-rectangular room shapes into a GameMap.
/// All operations are confined to the Room's bounding box — the bounding box
/// still governs overlap detection and entity placement (EntityPlacer filters
/// by IsWalkable, so non-rectangular shapes work automatically).
///
/// Invariant: after any CarveRoom call, the room's center tile (CenterX, CenterY)
/// is always Floor. This guarantees corridor L-tunnels can always connect to it.
/// </summary>
public static class RoomShapeGenerator
{
    // ---------------------------------------------------------------------------
    // Shape selection
    // ---------------------------------------------------------------------------

    // Weights and minimum sizes for each shape. Only shapes whose minimum is met
    // are eligible; the remainder of the weight goes proportionally to eligible shapes.
    private static readonly (RoomShape Shape, int Weight, int MinW, int MinH)[] ShapeWeights =
    [
        (RoomShape.Rectangle,    30, 3, 3),
        (RoomShape.Union,        30, 5, 5),
        (RoomShape.Cave,         15, 7, 7),
        (RoomShape.Circle,        8, 7, 7),
        (RoomShape.Alcove,       10, 8, 8),
        (RoomShape.CorridorRoom,  7, 3, 3), // one dim >= 8, other >= 3 — checked inside
    ];

    /// <summary>
    /// Pick a room shape based on weighted probability. Only shapes whose minimum
    /// size requirement is met are eligible. Rectangle is always eligible.
    /// </summary>
    public static RoomShape SelectShape(int w, int h, SeededRandom rng)
    {
        // Build the eligible set
        var eligible = new List<(RoomShape Shape, int Weight)>();
        foreach (var (shape, weight, minW, minH) in ShapeWeights)
        {
            bool meetsSize = shape switch
            {
                RoomShape.CorridorRoom => (w >= 8 && h >= 3) || (h >= 8 && w >= 3),
                _                     => w >= minW && h >= minH,
            };
            if (meetsSize)
                eligible.Add((shape, weight));
        }

        // Should never be empty (Rectangle is 3x3 and always eligible), but guard anyway
        if (eligible.Count == 0)
            return RoomShape.Rectangle;

        int total = eligible.Sum(e => e.Weight);
        int roll = rng.Next(total);
        int cumulative = 0;
        foreach (var (shape, weight) in eligible)
        {
            cumulative += weight;
            if (roll < cumulative)
                return shape;
        }
        return RoomShape.Rectangle; // unreachable
    }

    // ---------------------------------------------------------------------------
    // Dispatch
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Carve a room using the specified shape algorithm.
    /// After carving, the center tile is guaranteed to be Floor.
    /// </summary>
    public static void CarveRoom(GameMap map, Room room, RoomShape shape, SeededRandom rng)
    {
        switch (shape)
        {
            case RoomShape.Rectangle:
                CarveRectangle(map, room);
                break;
            case RoomShape.Union:
                CarveUnion(map, room, rng);
                break;
            case RoomShape.Cave:
                CarveCave(map, room, rng);
                break;
            case RoomShape.Circle:
                CarveCircle(map, room, rng);
                break;
            case RoomShape.Alcove:
                CarveAlcove(map, room, rng);
                break;
            case RoomShape.CorridorRoom:
                CarveCorridorRoom(map, room, rng);
                break;
        }

        // Invariant: center tile is always floor so corridor tunnels connect correctly.
        map.SetTile(room.CenterX, room.CenterY, TileKind.Floor);
    }

    // ---------------------------------------------------------------------------
    // Rectangle (baseline — reproduces existing MapGenerator behavior)
    // ---------------------------------------------------------------------------

    /// <summary>Carve every tile in the bounding box as Floor.</summary>
    public static void CarveRectangle(GameMap map, Room room)
    {
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                map.SetTile(x, y, TileKind.Floor);
    }

    // ---------------------------------------------------------------------------
    // Union (two overlapping rectangles → L/T/cross shapes)
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Carve two random sub-rectangles within the bounding box and write their
    /// union as Floor. Biases toward T/cross when random axis alignment fires.
    /// Retries up to 3 times if coverage is below 60% of bounding box area, then
    /// falls back to a simple rectangle.
    /// </summary>
    public static void CarveUnion(GameMap map, Room room, SeededRandom rng)
    {
        const int MaxRetries = 3;
        const double MinCoverage = 0.60;

        int bboxArea = room.Width * room.Height;
        int minCoveredTiles = (int)(bboxArea * MinCoverage);

        for (int attempt = 0; attempt <= MaxRetries; attempt++)
        {
            if (attempt == MaxRetries)
            {
                // Exhausted retries — fall back to full rectangle
                CarveRectangle(map, room);
                return;
            }

            // --- Generate rectA: random within bounding box, touches at least one edge ---
            int aw = rng.Next(3, room.Width + 1);
            int ah = rng.Next(3, room.Height + 1);

            // Touch one of the four edges randomly
            int edgeSide = rng.Next(4);
            int ax = edgeSide switch
            {
                0 => room.X,                       // left edge
                2 => room.X + room.Width - aw,     // right edge
                _ => rng.Next(room.X, room.X + room.Width - aw + 1), // top/bottom: random x
            };
            int ay = edgeSide switch
            {
                1 => room.Y,                       // top edge
                3 => room.Y + room.Height - ah,    // bottom edge
                _ => rng.Next(room.Y, room.Y + room.Height - ah + 1), // left/right: random y
            };
            // Clamp to bounding box
            ax = Math.Clamp(ax, room.X, room.X + room.Width - aw);
            ay = Math.Clamp(ay, room.Y, room.Y + room.Height - ah);

            // --- Generate rectB: random within bounding box ---
            int bw = rng.Next(3, room.Width + 1);
            int bh = rng.Next(3, room.Height + 1);
            int bx = rng.Next(room.X, room.X + room.Width - bw + 1);
            int by = rng.Next(room.Y, room.Y + room.Height - bh + 1);

            // 50% chance: share a center axis (T/cross bias)
            if (rng.Next(2) == 0)
            {
                if (rng.Next(2) == 0)
                    bx = ax + aw / 2 - bw / 2; // align on X center
                else
                    by = ay + ah / 2 - bh / 2; // align on Y center
                bx = Math.Clamp(bx, room.X, room.X + room.Width - bw);
                by = Math.Clamp(by, room.Y, room.Y + room.Height - bh);
            }

            // --- Count how many unique tiles will be carved ---
            // Quick area estimate: |A| + |B| - |A∩B|
            int axEnd = ax + aw, ayEnd = ay + ah;
            int bxEnd = bx + bw, byEnd = by + bh;
            int overlapW = Math.Max(0, Math.Min(axEnd, bxEnd) - Math.Max(ax, bx));
            int overlapH = Math.Max(0, Math.Min(ayEnd, byEnd) - Math.Max(ay, by));
            int estimatedTiles = aw * ah + bw * bh - overlapW * overlapH;

            if (estimatedTiles < minCoveredTiles)
                continue; // try again

            // --- Carve both rectangles ---
            for (int x = ax; x < axEnd; x++)
                for (int y = ay; y < ayEnd; y++)
                    map.SetTile(x, y, TileKind.Floor);

            for (int x = bx; x < bxEnd; x++)
                for (int y = by; y < byEnd; y++)
                    map.SetTile(x, y, TileKind.Floor);

            // --- Verify connectivity via flood fill from any carved tile ---
            if (!AllCarvedTilesConnected(map, room))
            {
                // Reset the tiles we carved (set back to wall so next attempt is clean)
                ResetRoom(map, room);
                continue;
            }

            return; // success
        }
    }

    // ---------------------------------------------------------------------------
    // Cave (cellular automata 4-5 rule)
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Generate an organic cave shape using cellular automata.
    /// Minimum bounding box 7×7. Falls back to Rectangle for smaller rooms.
    ///
    /// Algorithm:
    ///   1. Initialize local bool grid: border = wall, interior 45% wall
    ///   2. Pin: center + 3×3 neighborhood always floor (guarantees connectivity)
    ///   3. Run 4 CA iterations with 4-5 rule
    ///   4. Flood fill from center; discard disconnected pockets
    ///   5. Write surviving floor tiles to GameMap
    /// </summary>
    public static void CarveCave(GameMap map, Room room, SeededRandom rng)
    {
        if (room.Width < 7 || room.Height < 7)
        {
            CarveRectangle(map, room);
            return;
        }

        int w = room.Width;
        int h = room.Height;
        bool[,] wall = new bool[w, h]; // true = wall

        // Step 1: Initialize — border always wall, interior 45% wall
        for (int x = 0; x < w; x++)
            for (int y = 0; y < h; y++)
                wall[x, y] = (x == 0 || x == w - 1 || y == 0 || y == h - 1)
                    || rng.Next(100) < 45;

        // Step 2: Pin center 3×3 as definitively floor
        int cx = w / 2, cy = h / 2;
        for (int dx = -1; dx <= 1; dx++)
            for (int dy = -1; dy <= 1; dy++)
            {
                int px = cx + dx, py = cy + dy;
                if (px >= 0 && px < w && py >= 0 && py < h)
                    wall[px, py] = false;
            }

        // Step 3: Run 4 CA iterations (4-5 rule), keeping pinned region floor
        bool[,] next = new bool[w, h];
        for (int iter = 0; iter < 4; iter++)
        {
            for (int x = 0; x < w; x++)
            {
                for (int y = 0; y < h; y++)
                {
                    // Pinned region never changes
                    if (Math.Abs(x - cx) <= 1 && Math.Abs(y - cy) <= 1)
                    {
                        next[x, y] = false;
                        continue;
                    }
                    // Border is always wall
                    if (x == 0 || x == w - 1 || y == 0 || y == h - 1)
                    {
                        next[x, y] = true;
                        continue;
                    }

                    int wallCount = CountWallNeighbors(wall, x, y, w, h);
                    next[x, y] = wall[x, y]
                        ? wallCount >= 4   // wall stays wall if >= 4 wall neighbors
                        : wallCount >= 5;  // floor becomes wall if >= 5 wall neighbors
                }
            }
            // Swap
            Array.Copy(next, wall, w * h);
        }

        // Step 4: Flood fill from center to find connected floor region
        bool[,] reachable = FloodFillLocal(wall, cx, cy, w, h);

        // Step 5: Write to map — only reachable floor tiles
        for (int x = 0; x < w; x++)
            for (int y = 0; y < h; y++)
                if (reachable[x, y]) // reachable implies floor (not wall)
                    map.SetTile(room.X + x, room.Y + y, TileKind.Floor);
    }

    // ---------------------------------------------------------------------------
    // Circle (ellipse equation)
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Carve an ellipse fitted to the room's bounding box.
    /// Minimum 7×7. Falls back to Rectangle for smaller rooms.
    /// Optional single CA smoothing pass to reduce staircase jaggedness.
    /// </summary>
    public static void CarveCircle(GameMap map, Room room, SeededRandom rng)
    {
        if (room.Width < 7 || room.Height < 7)
        {
            CarveRectangle(map, room);
            return;
        }

        // Semi-axes: a along X, b along Y
        // Use (Width-1)/2 so the ellipse boundary fits inside the bounding box
        double a = (room.Width - 1) / 2.0;
        double b = (room.Height - 1) / 2.0;
        double cx = room.X + a;
        double cy = room.Y + b;

        // First pass: carve ellipse
        for (int x = room.X; x < room.X + room.Width; x++)
        {
            for (int y = room.Y; y < room.Y + room.Height; y++)
            {
                double dx = x - cx;
                double dy = y - cy;
                if (dx * dx / (a * a) + dy * dy / (b * b) <= 1.0)
                    map.SetTile(x, y, TileKind.Floor);
            }
        }

        // One CA smoothing pass: wall tile with <= 2 wall neighbors (of 8) → floor
        // This fills in single-tile staircase notches for a smoother oval appearance
        for (int x = room.X + 1; x < room.X + room.Width - 1; x++)
        {
            for (int y = room.Y + 1; y < room.Y + room.Height - 1; y++)
            {
                if (map.GetTileKind(x, y) == TileKind.Floor) continue;
                int wallNeighbors = 0;
                for (int nx = x - 1; nx <= x + 1; nx++)
                    for (int ny = y - 1; ny <= y + 1; ny++)
                        if ((nx != x || ny != y) && map.GetTileKind(nx, ny) == TileKind.Wall)
                            wallNeighbors++;
                if (wallNeighbors <= 2)
                    map.SetTile(x, y, TileKind.Floor);
            }
        }
    }

    // ---------------------------------------------------------------------------
    // Alcove (rectangle with wall protrusions)
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Carve a base rectangle with 2-tile margin, then add small alcoves
    /// extruded outward from wall segments longer than 3 tiles.
    /// Minimum 8×8. Falls back to Rectangle for smaller rooms.
    /// </summary>
    public static void CarveAlcove(GameMap map, Room room, SeededRandom rng)
    {
        if (room.Width < 8 || room.Height < 8)
        {
            CarveRectangle(map, room);
            return;
        }

        // Base rectangle with 2-tile margin on all sides
        int bx1 = room.X + 2;
        int by1 = room.Y + 2;
        int bx2 = room.X + room.Width - 2;  // exclusive
        int by2 = room.Y + room.Height - 2; // exclusive

        // Carve the base rectangle
        for (int x = bx1; x < bx2; x++)
            for (int y = by1; y < by2; y++)
                map.SetTile(x, y, TileKind.Floor);

        // --- North wall: tiles at y = by1, x in [bx1, bx2) ---
        // Extrude toward room.Y (decreasing Y)
        int northLen = bx2 - bx1;
        if (northLen > 3)
            TryAddAlcove(map, room, rng,
                startX: bx1, startY: by1,
                length: northLen, isHorizontal: true, extrudeDir: -1);

        // --- South wall: tiles at y = by2-1, x in [bx1, bx2) ---
        // Extrude toward room.Y+Height (increasing Y)
        if (northLen > 3)
            TryAddAlcove(map, room, rng,
                startX: bx1, startY: by2 - 1,
                length: northLen, isHorizontal: true, extrudeDir: +1);

        // --- West wall: tiles at x = bx1, y in [by1, by2) ---
        int westLen = by2 - by1;
        if (westLen > 3)
            TryAddAlcove(map, room, rng,
                startX: bx1, startY: by1,
                length: westLen, isHorizontal: false, extrudeDir: -1);

        // --- East wall: tiles at x = bx2-1, y in [by1, by2) ---
        if (westLen > 3)
            TryAddAlcove(map, room, rng,
                startX: bx2 - 1, startY: by1,
                length: westLen, isHorizontal: false, extrudeDir: +1);
    }

    /// <summary>
    /// Attempt to carve a single alcove niche from a wall segment.
    /// 20% chance per wall segment. Size 1-2 deep, 1-3 wide.
    /// </summary>
    private static void TryAddAlcove(
        GameMap map, Room room, SeededRandom rng,
        int startX, int startY,
        int length, bool isHorizontal, int extrudeDir)
    {
        if (rng.Next(100) >= 20) return; // 20% chance

        int alcoveDepth = rng.Next(1, 3);  // 1-2 deep
        int alcoveWidth = rng.Next(1, 4);  // 1-3 wide
        alcoveWidth = Math.Min(alcoveWidth, length - 1); // can't be wider than wall

        // Pick a random position along the wall for the alcove
        int posOffset = rng.Next(0, length - alcoveWidth + 1);

        for (int w = 0; w < alcoveWidth; w++)
        {
            for (int d = 1; d <= alcoveDepth; d++)
            {
                int x, y;
                if (isHorizontal)
                {
                    x = startX + posOffset + w;
                    y = startY + d * extrudeDir;
                }
                else
                {
                    x = startX + d * extrudeDir;
                    y = startY + posOffset + w;
                }

                // Only carve tiles strictly within the room's bounding box
                if (room.Contains(x, y))
                    map.SetTile(x, y, TileKind.Floor);
            }
        }
    }

    // ---------------------------------------------------------------------------
    // CorridorRoom (long thin strip)
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Carve a corridor-room: a long thin strip 2-3 tiles wide, full bounding-box length.
    /// Horizontal when Width > Height, vertical when Height > Width, random when square.
    /// Minimum: one dimension >= 8 AND other >= 3. Falls back to Rectangle otherwise.
    /// </summary>
    public static void CarveCorridorRoom(GameMap map, Room room, SeededRandom rng)
    {
        bool canH = room.Width >= 8 && room.Height >= 3;
        bool canV = room.Height >= 8 && room.Width >= 3;

        if (!canH && !canV)
        {
            CarveRectangle(map, room);
            return;
        }

        bool horizontal;
        if (canH && canV)
            horizontal = room.Width >= room.Height || (room.Width == room.Height && rng.Next(2) == 0);
        else
            horizontal = canH;

        int corridorWidth = rng.Next(2, 4); // 2 or 3 tiles

        if (horizontal)
        {
            // Center on Y axis, full X length
            int midY = room.CenterY;
            int halfW = corridorWidth / 2;
            int y1 = Math.Max(room.Y, midY - halfW);
            int y2 = Math.Min(room.Y + room.Height - 1, midY + corridorWidth - 1 - halfW);
            for (int x = room.X; x < room.X + room.Width; x++)
                for (int y = y1; y <= y2; y++)
                    map.SetTile(x, y, TileKind.Floor);
        }
        else
        {
            // Center on X axis, full Y length
            int midX = room.CenterX;
            int halfW = corridorWidth / 2;
            int x1 = Math.Max(room.X, midX - halfW);
            int x2 = Math.Min(room.X + room.Width - 1, midX + corridorWidth - 1 - halfW);
            for (int y = room.Y; y < room.Y + room.Height; y++)
                for (int x = x1; x <= x2; x++)
                    map.SetTile(x, y, TileKind.Floor);
        }
    }

    // ---------------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Count wall neighbors (8-connectivity) in a local bool grid.
    /// Out-of-bounds cells count as wall.
    /// </summary>
    private static int CountWallNeighbors(bool[,] wall, int x, int y, int w, int h)
    {
        int count = 0;
        for (int nx = x - 1; nx <= x + 1; nx++)
            for (int ny = y - 1; ny <= y + 1; ny++)
            {
                if (nx == x && ny == y) continue;
                if (nx < 0 || nx >= w || ny < 0 || ny >= h)
                    count++; // treat OOB as wall
                else if (wall[nx, ny])
                    count++;
            }
        return count;
    }

    /// <summary>
    /// Flood fill from (startX, startY) in a local bool grid (true=wall, false=floor).
    /// Returns bool[,] where true means "reachable floor tile."
    /// </summary>
    private static bool[,] FloodFillLocal(bool[,] wall, int startX, int startY, int w, int h)
    {
        var reachable = new bool[w, h];
        if (wall[startX, startY]) return reachable; // start is a wall — nothing reachable

        var queue = new Queue<(int x, int y)>();
        queue.Enqueue((startX, startY));
        reachable[startX, startY] = true;

        while (queue.Count > 0)
        {
            var (x, y) = queue.Dequeue();
            // 4-connectivity flood fill (corridors are 1 tile wide — diagonal not needed)
            foreach (var (nx, ny) in new[] { (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) })
            {
                if (nx < 0 || nx >= w || ny < 0 || ny >= h) continue;
                if (reachable[nx, ny] || wall[nx, ny]) continue;
                reachable[nx, ny] = true;
                queue.Enqueue((nx, ny));
            }
        }
        return reachable;
    }

    /// <summary>
    /// Check whether all Floor tiles within a room's bounding box on the GameMap
    /// are connected (reachable from the first found floor tile).
    /// </summary>
    private static bool AllCarvedTilesConnected(GameMap map, Room room)
    {
        // Find first floor tile
        int? startX = null, startY = null;
        int totalFloor = 0;
        for (int x = room.X; x < room.X + room.Width && startX == null; x++)
            for (int y = room.Y; y < room.Y + room.Height && startX == null; y++)
                if (map.GetTileKind(x, y) == TileKind.Floor)
                { startX = x; startY = y; }

        if (startX == null) return true; // no floor tiles — vacuously connected

        // Count all floor tiles
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                if (map.GetTileKind(x, y) == TileKind.Floor)
                    totalFloor++;

        // BFS from first floor tile
        var visited = new HashSet<(int, int)>();
        var queue = new Queue<(int, int)>();
        queue.Enqueue((startX.Value, startY.Value));
        visited.Add((startX.Value, startY.Value));

        while (queue.Count > 0)
        {
            var (x, y) = queue.Dequeue();
            foreach (var (nx, ny) in new[] { (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) })
            {
                if (!room.Contains(nx, ny)) continue;
                if (visited.Contains((nx, ny))) continue;
                if (map.GetTileKind(nx, ny) != TileKind.Floor) continue;
                visited.Add((nx, ny));
                queue.Enqueue((nx, ny));
            }
        }

        return visited.Count == totalFloor;
    }

    /// <summary>
    /// Reset all tiles in a room's bounding box back to Wall.
    /// Used by CarveUnion when a retry is needed.
    /// </summary>
    private static void ResetRoom(GameMap map, Room room)
    {
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                map.SetTile(x, y, TileKind.Wall);
    }
}
