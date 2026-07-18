using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Persistence.MidRun;

/// <summary>
/// GameState ⇄ MidRunSaveDto (M1.4 §GameState field classification). Construct-then-restore: on load
/// a GameState is built through its constructor (it is builder-populated, not deserializer-friendly)
/// and every SERIALIZE-class field is restored onto it.
///
/// Scope (4a.3b): scenario-mode GameState — entity table + Map/FOV + Knowledge + GroundHazards + Rng
/// + id watermark + scalar block. Dungeon-mode subsystems are 4a.3b-2; SaveMidRun throws loudly if it
/// sees them rather than dropping them silently. EXCLUDE-class fields and PersistentState never appear.
/// </summary>
public static class MidRunSerializer
{
    public static MidRunSaveDto SaveMidRun(GameState state)
    {
        GuardScenarioOnly(state);

        // Roots: every entity list + player. 4a.2 container traversal closes over inventory/equipment
        // and stash contents; the audit confirmed no other unlisted-entity reference exists.
        var roots = new List<Entity> { state.Player };
        roots.AddRange(state.Monsters);
        roots.AddRange(state.FloorItems);
        roots.AddRange(state.Corpses);
        roots.AddRange(state.Features);
        roots.AddRange(state.Portals);
        if (state.StairDown != null) roots.Add(state.StairDown);
        // Any entity on the map's occupancy index must also be in the table so its id resolves on
        // load (EntitySerializer de-dups by id, so listing extras is harmless).
        roots.AddRange(state.Map.Entities);

        var grids = state.Map.ExportGrids();
        var propCells = new List<int>();
        foreach (var (x, y) in state.Map.PropCells) { propCells.Add(x); propCells.Add(y); }

        return new MidRunSaveDto
        {
            SchemaVersion = MidRunSchema.Version,
            Entities = EntitySerializer.Serialize(roots),
            PlayerId = state.Player.Id,
            MonsterIds = state.Monsters.Select(e => e.Id).ToArray(),
            FloorItemIds = state.FloorItems.Select(e => e.Id).ToArray(),
            CorpseIds = state.Corpses.Select(e => e.Id).ToArray(),
            FeatureIds = state.Features.Select(e => e.Id).ToArray(),
            PortalIds = state.Portals.Select(e => e.Id).ToArray(),
            StairDownId = state.StairDown?.Id,
            Map = new GameMapDto
            {
                Width = state.Map.Width,
                Height = state.Map.Height,
                Tiles = grids.Tiles,
                Walkable = grids.Walkable,
                Visible = grids.Visible,
                Explored = grids.Explored,
                Theme = grids.Theme,
                RegisteredEntityIds = state.Map.RegisteredEntityIds.ToArray(),
                PropCells = propCells.ToArray(),
            },
            Knowledge = state.Knowledge.Entries
                .OrderBy(kv => kv.Key, StringComparer.Ordinal)
                .Select(kv => new KnowledgeEntryDto(kv.Key, kv.Value.SeenCount, kv.Value.EngagedCount,
                    kv.Value.KilledCount, kv.Value.TraitsDiscovered.OrderBy(s => s, StringComparer.Ordinal).ToArray()))
                .ToArray(),
            GroundHazards = state.GroundHazards.Hazards.Values
                .OrderBy(h => h.X).ThenBy(h => h.Y)
                .Select(h => new GroundHazardDto(h.Type, h.X, h.Y, h.BaseDamage, h.MaxDuration, h.RemainingTurns, h.JustPlaced))
                .ToArray(),
            RngSeed = state.Rng.Seed,
            RngCallCount = state.Rng.CallCount,
            IdAllocatorWatermark = state.IdAllocator?.Peek,
            CurrentDepth = state.CurrentDepth,
            TurnCount = state.TurnCount,
            TurnLimit = state.TurnLimit,
            IsDungeonMode = state.IsDungeonMode,
            Difficulty = state.Difficulty,
            PastSashasEncounteredThisRun = state.PastSashasEncounteredThisRun.OrderBy(i => i).ToArray(),
            PlayerDeathKillerSpecies = state.PlayerDeathKillerSpecies,
            PlayerDeathCause = state.PlayerDeathCause,
            Ending = state.Ending,
        };
    }

    public static GameState LoadMidRun(MidRunSaveDto dto)
    {
        if (dto.SchemaVersion != MidRunSchema.Version)
            throw new InvalidOperationException(
                $"Mid-run save schema version {dto.SchemaVersion} != supported {MidRunSchema.Version}.");
        if (dto.IsDungeonMode)
            throw new NotSupportedException("Dungeon-mode mid-run load is 4a.3b-2 (needs subsystem + BoonTable reconstruction).");

        var byId = EntitySerializer.Deserialize(dto.Entities);
        Entity Get(int id) => byId.TryGetValue(id, out var e)
            ? e
            : throw new InvalidOperationException($"Mid-run load: entity id {id} referenced but absent from the table.");

        var player = Get(dto.PlayerId);
        var monsters = dto.MonsterIds.Select(Get).ToList();

        var map = new GameMap(dto.Map.Width, dto.Map.Height);
        map.RestoreGrids(new GameMap.GridSnapshot(dto.Map.Tiles, dto.Map.Walkable, dto.Map.Visible, dto.Map.Explored, dto.Map.Theme));
        foreach (var id in dto.Map.RegisteredEntityIds) map.RegisterEntity(Get(id));
        for (int i = 0; i + 1 < dto.Map.PropCells.Length; i += 2) map.MarkPropCell(dto.Map.PropCells[i], dto.Map.PropCells[i + 1]);

        var rng = SeededRandom.Restore(dto.RngSeed, dto.RngCallCount);

        var state = new GameState(player, monsters, map, rng, dto.TurnLimit)
        {
            IsDungeonMode = dto.IsDungeonMode,
            CurrentDepth = dto.CurrentDepth,
            Difficulty = dto.Difficulty,
            IdAllocator = dto.IdAllocatorWatermark is { } w ? new EntityIdAllocator(w) : null,
        };

        state.TurnCount = dto.TurnCount;
        foreach (var id in dto.FloorItemIds) state.FloorItems.Add(Get(id));
        foreach (var id in dto.CorpseIds) state.Corpses.Add(Get(id));
        foreach (var id in dto.FeatureIds) state.Features.Add(Get(id));
        foreach (var id in dto.PortalIds) state.Portals.Add(Get(id));
        if (dto.StairDownId is { } sd) state.StairDown = Get(sd);

        foreach (var k in dto.Knowledge)
            state.Knowledge.RestoreEntry(k.SpeciesId, k.SeenCount, k.EngagedCount, k.KilledCount, k.TraitsDiscovered);

        foreach (var h in dto.GroundHazards)
        {
            state.GroundHazards.AddHazard(h.Type, h.X, h.Y, h.BaseDamage, h.MaxDuration, h.JustPlaced);
            state.GroundHazards.Hazards[(h.X, h.Y)].RemainingTurns = h.RemainingTurns;
        }

        foreach (var id in dto.PastSashasEncounteredThisRun) state.PastSashasEncounteredThisRun.Add(id);
        state.PlayerDeathKillerSpecies = dto.PlayerDeathKillerSpecies;
        state.PlayerDeathCause = dto.PlayerDeathCause;
        state.Ending = dto.Ending;

        return state;
    }

    // Fail loud on any dungeon-only subsystem so a scenario-scoped save never silently drops state.
    private static void GuardScenarioOnly(GameState s)
    {
        var populated = new List<string>();
        if (s.IsDungeonMode) populated.Add("IsDungeonMode");
        if (s.IdentificationRegistry != null) populated.Add("IdentificationRegistry");
        if (s.AppearancePool != null) populated.Add("AppearancePool");
        if (s.MuralTracker != null) populated.Add("MuralTracker");
        if (s.PityTracker != null) populated.Add("PityTracker");
        if (s.BoonTracker != null) populated.Add("BoonTracker");
        if (s.Rooms is { Count: > 0 }) populated.Add("Rooms");
        if (s.Props.Count > 0) populated.Add("Props");
        if (s.LockedDoors.Count > 0) populated.Add("LockedDoors");
        if (s.Weighing != null || s.WeighingArena != null) populated.Add("Weighing");
        if (s.WeighingAudit != null) populated.Add("WeighingAudit");
        if (populated.Count > 0)
            throw new NotSupportedException(
                "Dungeon-mode mid-run save is 4a.3b-2; these SERIALIZE-class subsystems are populated and " +
                $"would be dropped by the scenario-scoped saver: {string.Join(", ", populated)}.");
    }
}
