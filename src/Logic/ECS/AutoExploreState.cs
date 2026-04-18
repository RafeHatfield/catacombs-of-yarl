namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Component tracking auto-explore state for the player entity.
/// Owned by AutoExploreSystem — do not mutate directly from outside.
/// </summary>
public sealed class AutoExploreState : IComponent
{
    public Entity? Owner { get; set; }

    public bool IsActive { get; set; }
    public List<(int X, int Y)> CurrentPath { get; set; } = new();

    /// <summary>
    /// Tiles explored at activation time. Two-pass strategy: pass 1 prioritises
    /// tiles NOT in this snapshot (new discoveries), pass 2 falls back to any
    /// unexplored tile. Prevents auto-explore stopping for items in already-known rooms.
    /// </summary>
    public HashSet<(int X, int Y)> ExploredSnapshot { get; set; } = new();

    /// <summary>Monster IDs visible in FOV at activation — don't interrupt for these.</summary>
    public HashSet<int> KnownMonsterIds { get; set; } = new();

    /// <summary>
    /// Item entity IDs that were visible and in range at activation — don't re-interrupt for these.
    /// Using entity IDs (not tile positions) so re-activating near a known potion stays silent.
    /// </summary>
    public HashSet<int> KnownItemIds { get; set; } = new();

    /// <summary>Feature entity IDs (chests, signs, murals) visible at activation — don't re-interrupt.</summary>
    public HashSet<int> KnownFeatureIds { get; set; } = new();

    /// <summary>Stair positions already seen — prevents re-triggering on the same stair.</summary>
    public HashSet<(int X, int Y)> KnownStairs { get; set; } = new();

    public int LastHp { get; set; }
    public string? StopReason { get; set; }
    public int StuckCounter { get; set; }
    public (int X, int Y)? LastExpectedPosition { get; set; }

    // Fixed circular buffer for oscillation detection (last 6 positions)
    private readonly (int X, int Y)[] _positionHistory = new (int, int)[6];
    private int _positionCount;

    public void RecordPosition(int x, int y)
    {
        if (_positionCount < 6)
        {
            _positionHistory[_positionCount++] = (x, y);
        }
        else
        {
            Array.Copy(_positionHistory, 1, _positionHistory, 0, 5);
            _positionHistory[5] = (x, y);
        }
    }

    /// <summary>
    /// Detects A-B-A-B-A-B pattern (3 complete reversals) in the last 6 positions.
    /// </summary>
    public bool IsOscillating()
    {
        if (_positionCount < 6) return false;
        return _positionHistory[0] == _positionHistory[2]
            && _positionHistory[2] == _positionHistory[4]
            && _positionHistory[1] == _positionHistory[3]
            && _positionHistory[3] == _positionHistory[5]
            && _positionHistory[0] != _positionHistory[1];
    }

    public void ResetPositionHistory()
    {
        _positionCount = 0;
    }
}
