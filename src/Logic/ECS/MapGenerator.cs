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

            // Carve room interior as Floor tiles
            CarveRoom(map, newRoom);

            if (rooms.Count > 0)
            {
                // Connect this room's center to the previous room's center with an L-shaped tunnel
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

    /// <summary>Carve all interior tiles of a room as Floor.</summary>
    private static void CarveRoom(GameMap map, Room room)
    {
        for (int x = room.X; x < room.X + room.Width; x++)
            for (int y = room.Y; y < room.Y + room.Height; y++)
                map.SetTile(x, y, TileKind.Floor);
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
