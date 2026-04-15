using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Core;

namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Procedural dungeon generator using random room placement + L-corridor connections.
/// Algorithm matches the Python prototype (map_objects/game_map.py lines 198-302) so that
/// cross-prototype validation is possible with the same seed.
///
/// NOT BSP — BSP produces different room distributions for the same seed. Random placement
/// with intersection rejection preserves the probability distribution of the prototype.
/// </summary>
public static class MapGenerator
{
    // Defaults used when no level template parameters are present.
    // Match PoC game_constants.py: 120×80, 150 attempts, 12–18 room size.
    public const int DefaultWidth = 120;
    public const int DefaultHeight = 80;
    public const int DefaultMaxRooms = 150;
    public const int DefaultMinRoomSize = 12;
    public const int DefaultMaxRoomSize = 18;

    /// <summary>
    /// Generate a dungeon floor.
    /// </summary>
    /// <param name="width">Map width in tiles.</param>
    /// <param name="height">Map height in tiles.</param>
    /// <param name="maxRooms">Maximum number of rooms to attempt placing.</param>
    /// <param name="minRoomSize">Minimum room side length (inclusive).</param>
    /// <param name="maxRoomSize">Maximum room side length (inclusive).</param>
    /// <param name="rng">Seeded RNG — deterministic for the same seed.</param>
    /// <param name="stairs">Optional stair placement rules. Null = default (place stair in last room).</param>
    public static GeneratedMap Generate(
        int width, int height,
        int maxRooms, int minRoomSize, int maxRoomSize,
        SeededRandom rng,
        StairRules? stairs = null)
    {
        // Phase 1 of Python algorithm: all walls
        var map = new GameMap(width, height, allWalls: true);

        var rooms = new List<Room>();
        var corridors = new List<CorridorSegment>();

        // Attempt to place up to maxRooms rooms
        for (int attempt = 0; attempt < maxRooms; attempt++)
        {
            // Random width and height (minRoomSize..maxRoomSize inclusive, matching randint)
            int w = rng.Next(minRoomSize, maxRoomSize + 1);
            int h = rng.Next(minRoomSize, maxRoomSize + 1);

            // Random position — keep at least 1 wall tile on every map edge so the
            // isometric renderer always has a wall tile behind every floor tile.
            // PoC equivalent: same constraint is implicit because rooms carve x1+1..x2-1
            // (leaving a wall border). C# carves the full rectangle, so we enforce the
            // border here instead.
            int x = rng.Next(1, Math.Max(2, width - w));    // [1, width-w-1]
            int y = rng.Next(1, Math.Max(2, height - h));   // [1, height-h-1]

            var newRoom = new Room(x, y, w, h);

            // Reject if intersects any existing room (with 1-tile padding)
            bool overlaps = false;
            foreach (var existingRoom in rooms)
            {
                if (newRoom.Intersects(existingRoom))
                {
                    overlaps = true;
                    break;
                }
            }
            if (overlaps) continue;

            // Select shape and carve — shape consumes RNG calls before the overlap check passes,
            // so the dungeon seed sequence differs from the old rectangle-only behavior.
            // That is acceptable: generation is seeded per-floor and doesn't need to match
            // the Python prototype output exactly (rooms were rectangular there too).
            var shape = RoomShapeGenerator.SelectShape(w, h, rng);
            RoomShapeGenerator.CarveRoom(map, newRoom, shape, rng);
            newRoom = newRoom with { Shape = shape };

            if (rooms.Count > 0)
            {
                // Connect this room's center to the previous room's center with an L-shaped tunnel.
                // All shape carvers guarantee the center tile is floor (pinned or reset by CarveRoom).
                var prevRoom = rooms[^1];
                ConnectRooms(map, corridors, prevRoom, newRoom, rng);
            }

            rooms.Add(newRoom);
        }

        // If no rooms were placed (pathological case), create a single minimal room
        if (rooms.Count == 0)
        {
            var fallback = new Room(1, 1, minRoomSize, minRoomSize);
            CarveRoom(map, fallback);
            rooms.Add(fallback);
        }

        var playerRoom = rooms[0];
        var playerSpawn = (playerRoom.CenterX, playerRoom.CenterY);

        // Belt-and-suspenders: ensure every room center is reachable from player spawn.
        // Non-rectangular shapes are designed to include their center, but cave/circle shapes
        // can occasionally produce a corner case where the corridor L-tunnel joins at a wall.
        EnsureConnectivity(map, rooms, playerSpawn);

        // Stair down goes in the last room placed
        (int X, int Y)? stairDownPos = null;
        if (stairs == null || stairs.Down)
        {
            var lastRoom = rooms[^1];
            stairDownPos = (lastRoom.CenterX, lastRoom.CenterY);
            map.SetTile(stairDownPos.Value.X, stairDownPos.Value.Y, TileKind.StairDown);
        }

        // Stair up goes in player room on depth > 1 (controlled by caller via StairRules)
        (int X, int Y)? stairUpPos = null;
        if (stairs != null && stairs.Up)
        {
            // Place stair up near-but-not-at the player spawn to avoid spawn-on-stair overlap
            // Use a tile adjacent to center if available, else center
            stairUpPos = FindStairUpPosition(map, playerRoom, playerSpawn);
            if (stairUpPos.HasValue)
                map.SetTile(stairUpPos.Value.X, stairUpPos.Value.Y, TileKind.StairUp);
        }

        return new GeneratedMap(
            map: map,
            rooms: rooms,
            corridors: corridors,
            playerRoom: playerRoom,
            playerSpawn: playerSpawn,
            stairDownPos: stairDownPos,
            stairUpPos: stairUpPos);
    }

    /// <summary>Carve all interior tiles of a room as Floor (fallback for pathological case).</summary>
    private static void CarveRoom(GameMap map, Room room)
    {
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                map.SetTile(x, y, TileKind.Floor);
    }

    /// <summary>
    /// Post-generation connectivity check. Flood fills from playerSpawn and verifies
    /// every room center is reachable. If a room is unreachable, carves an emergency
    /// L-corridor from the nearest reachable room center to reconnect it.
    /// Runs up to 3 passes to handle cascading disconnections.
    ///
    /// This is belt-and-suspenders: shape carvers are designed to include the room center
    /// as floor, but edge cases in cave/circle shapes with small bounding boxes can
    /// occasionally produce a center that the corridor tunnel lands on a wall tile.
    /// </summary>
    private static void EnsureConnectivity(
        GameMap map,
        List<Room> rooms,
        (int X, int Y) playerSpawn)
    {
        const int MaxPasses = 3;

        for (int pass = 0; pass < MaxPasses; pass++)
        {
            // Flood fill from player spawn across all walkable tiles
            var reachable = FloodFillMap(map, playerSpawn.X, playerSpawn.Y);

            // Find the first unreachable room
            Room? unreachable = null;
            foreach (var room in rooms)
            {
                if (!reachable.Contains((room.CenterX, room.CenterY)))
                {
                    unreachable = room;
                    break;
                }
            }

            if (unreachable == null) return; // all rooms connected

            // Find nearest reachable room to connect from
            Room? nearest = null;
            int bestDist = int.MaxValue;
            foreach (var room in rooms)
            {
                if (!reachable.Contains((room.CenterX, room.CenterY))) continue;
                int dist = Math.Abs(room.CenterX - unreachable.CenterX)
                         + Math.Abs(room.CenterY - unreachable.CenterY);
                if (dist < bestDist) { bestDist = dist; nearest = room; }
            }

            if (nearest == null)
            {
                // No reachable room at all — just ensure the first room's center is floor
                map.SetTile(rooms[0].CenterX, rooms[0].CenterY, TileKind.Floor);
                continue;
            }

            // Carve emergency L-corridor (H then V, no random — just fix the gap)
            int x1 = nearest.CenterX, y1 = nearest.CenterY;
            int x2 = unreachable.CenterX, y2 = unreachable.CenterY;
            CarveHTunnel(map, x1, x2, y1);
            CarveVTunnel(map, y1, y2, x2);
            // Ensure the unreachable room center is floor (CarveVTunnel only sets Corridor on Wall)
            map.SetTile(x2, y2, TileKind.Floor);
        }
    }

    /// <summary>
    /// BFS flood fill from (startX, startY) across all walkable tiles on the full map.
    /// Returns the set of (x,y) positions reachable.
    /// </summary>
    private static HashSet<(int X, int Y)> FloodFillMap(GameMap map, int startX, int startY)
    {
        var visited = new HashSet<(int, int)>();
        if (!map.IsWalkable(startX, startY)) return visited;

        var queue = new Queue<(int, int)>();
        queue.Enqueue((startX, startY));
        visited.Add((startX, startY));

        while (queue.Count > 0)
        {
            var (x, y) = queue.Dequeue();
            foreach (var (nx, ny) in new[] { (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) })
            {
                if (visited.Contains((nx, ny))) continue;
                if (!map.IsWalkable(nx, ny)) continue;
                visited.Add((nx, ny));
                queue.Enqueue((nx, ny));
            }
        }
        return visited;
    }

    /// <summary>
    /// Connect two rooms with an L-shaped corridor.
    /// Randomly chooses horizontal-then-vertical or vertical-then-horizontal,
    /// matching the Python coin-flip. Records both segments in corridors list.
    /// </summary>
    private static void ConnectRooms(
        GameMap map,
        List<CorridorSegment> corridors,
        Room from,
        Room to,
        SeededRandom rng)
    {
        int x1 = from.CenterX, y1 = from.CenterY;
        int x2 = to.CenterX, y2 = to.CenterY;

        // Python: if randint(0, 1) == 1: H then V; else: V then H
        if (rng.Next(2) == 1)
        {
            // Horizontal then vertical
            CarveHTunnel(map, x1, x2, y1);
            CarveVTunnel(map, y1, y2, x2);
            corridors.Add(new CorridorSegment(x1, y1, x2, y1)); // H segment
            corridors.Add(new CorridorSegment(x2, y1, x2, y2)); // V segment
        }
        else
        {
            // Vertical then horizontal
            CarveVTunnel(map, y1, y2, x1);
            CarveHTunnel(map, x1, x2, y2);
            corridors.Add(new CorridorSegment(x1, y1, x1, y2)); // V segment
            corridors.Add(new CorridorSegment(x1, y2, x2, y2)); // H segment
        }
    }

    private static void CarveHTunnel(GameMap map, int x1, int x2, int y)
    {
        int xMin = Math.Min(x1, x2);
        int xMax = Math.Max(x1, x2);
        for (int x = xMin; x <= xMax; x++)
        {
            // Only overwrite Wall tiles — don't downgrade Floor to Corridor
            if (map.GetTileKind(x, y) == TileKind.Wall)
                map.SetTile(x, y, TileKind.Corridor);
        }
    }

    private static void CarveVTunnel(GameMap map, int y1, int y2, int x)
    {
        int yMin = Math.Min(y1, y2);
        int yMax = Math.Max(y1, y2);
        for (int y = yMin; y <= yMax; y++)
        {
            if (map.GetTileKind(x, y) == TileKind.Wall)
                map.SetTile(x, y, TileKind.Corridor);
        }
    }

    /// <summary>
    /// Find a suitable position for the up stair within the player room,
    /// distinct from the player spawn center. Falls back to center if nothing else available.
    /// </summary>
    private static (int X, int Y)? FindStairUpPosition(
        GameMap map,
        Room room,
        (int X, int Y) avoidPos)
    {
        // Try center + small offset first
        int[] offsets = [-1, 1, -2, 2];
        foreach (int dx in offsets)
        {
            int nx = room.CenterX + dx;
            if (room.Contains(nx, room.CenterY) && map.IsWalkable(nx, room.CenterY)
                && (nx != avoidPos.X || room.CenterY != avoidPos.Y))
                return (nx, room.CenterY);
        }
        foreach (int dy in offsets)
        {
            int ny = room.CenterY + dy;
            if (room.Contains(room.CenterX, ny) && map.IsWalkable(room.CenterX, ny)
                && (room.CenterX != avoidPos.X || ny != avoidPos.Y))
                return (room.CenterX, ny);
        }
        // Fallback: use center (stair and player will overlap — acceptable edge case)
        return (room.CenterX, room.CenterY);
    }
}
