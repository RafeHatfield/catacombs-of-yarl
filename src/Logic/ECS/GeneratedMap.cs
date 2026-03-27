namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Result of MapGenerator.Generate(). Contains the carved GameMap, metadata about
/// rooms and corridors (for entity placement and future door/feature placement),
/// and precomputed spawn positions for player and stairs.
/// </summary>
public sealed class GeneratedMap
{
    public GameMap Map { get; }
    public IReadOnlyList<Room> Rooms { get; }

    /// <summary>All corridor segments, in connection order. Used by future door placement.</summary>
    public IReadOnlyList<CorridorSegment> Corridors { get; }

    /// <summary>The first room placed — player starts here.</summary>
    public Room PlayerRoom { get; }

    /// <summary>Exact tile where the player spawns (center of PlayerRoom).</summary>
    public (int X, int Y) PlayerSpawn { get; }

    /// <summary>Position of the down stair, if placed.</summary>
    public (int X, int Y)? StairDownPos { get; }

    /// <summary>Position of the up stair, if placed. Typically null on depth > 1.</summary>
    public (int X, int Y)? StairUpPos { get; }

    public GeneratedMap(
        GameMap map,
        IReadOnlyList<Room> rooms,
        IReadOnlyList<CorridorSegment> corridors,
        Room playerRoom,
        (int X, int Y) playerSpawn,
        (int X, int Y)? stairDownPos,
        (int X, int Y)? stairUpPos)
    {
        Map = map;
        Rooms = rooms;
        Corridors = corridors;
        PlayerRoom = playerRoom;
        PlayerSpawn = playerSpawn;
        StairDownPos = stairDownPos;
        StairUpPos = stairUpPos;
    }
}
