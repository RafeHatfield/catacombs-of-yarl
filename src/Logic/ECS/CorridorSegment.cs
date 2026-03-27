namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// One arm of an L-shaped corridor connecting two rooms.
/// Stored for future door placement — corridors are axis-aligned single-tile-wide passages.
/// </summary>
public sealed record CorridorSegment(int X1, int Y1, int X2, int Y2);
