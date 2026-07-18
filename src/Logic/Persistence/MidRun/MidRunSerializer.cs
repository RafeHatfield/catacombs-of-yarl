using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
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
        GuardWeighingUnsupported(state);

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

            // Dungeon-only subsystems (null in scenario mode). Every collection canonically ordered.
            Identification = state.IdentificationRegistry is not { } ir ? null : new IdentificationDto(
                ir.IdentifiedTypeIds.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                ir.DecidedUnidentifiedTypeIds.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                ir.AlwaysIdentified),
            Appearance = state.AppearancePool is not { } ap ? null : new AppearancePoolDto(
                ap.Descriptors.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => new StringPairDto(kv.Key, kv.Value)).ToArray(),
                ap.MysterySprites.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => new StringPairDto(kv.Key, kv.Value)).ToArray(),
                ap.PotionTypes.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                ap.ScrollTypes.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                ap.WandTypes.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                ap.RingTypes.OrderBy(s => s, StringComparer.Ordinal).ToArray()),
            Murals = state.MuralTracker is not { } mt ? null : new MuralTrackerDto(
                mt.UsedThisFloor.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                mt.UsedThisRun.OrderBy(s => s, StringComparer.Ordinal).ToArray()),
            Pity = state.PityTracker is not { } pt ? null : new PityTrackerDto(
                pt.Counters.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => new IntEntryDto(kv.Key, kv.Value)).ToArray(),
                pt.PendingHardInjects.OrderBy(s => s, StringComparer.Ordinal).ToArray(),
                pt.LootItemCounts.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => new IntEntryDto(kv.Key, kv.Value)).ToArray(),
                pt.HardPityFireCount),
            Boons = state.BoonTracker is not { } bt ? null : new BoonTrackerDto(
                bt.VisitedDepths.OrderBy(i => i).ToArray(), bt.BoonsApplied.ToArray(), bt.DisableDepthBoons),
            Rooms = state.Rooms is null ? null : state.Rooms.Select(r => new RoomDto(
                r.X, r.Y, r.Width, r.Height, r.Shape, r.Archetype, r.IsDeadEnd, r.IsGrandShrine, r.IsVault, r.MaintenanceState)).ToArray(),
            Props = state.Props.Count == 0 ? null : state.Props.Select(p => new PlacedPropDto(
                p.PropId, p.X, p.Y, p.FootprintW, p.FootprintH, p.BlocksMovement, p.TileId, p.OverlayTileId,
                p.TileLayout?.ToArray(), p.FlipH)).ToArray(),
            LockedDoors = state.LockedDoors.OrderBy(kv => kv.Key.X).ThenBy(kv => kv.Key.Y)
                .Select(kv => new LockedDoorDto(kv.Key.X, kv.Key.Y, kv.Value)).ToArray(),
        };
    }

    /// <summary>
    /// Rebuild a GameState from a mid-run save. <paramref name="boonTable"/> is RECONSTRUCT-class:
    /// the caller loads it from config (via DungeonFloorBuilder/ContentLoader) and passes it in — it
    /// is never stored in the save. Null is fine for scenario mode and for a floor with no descent left.
    /// </summary>
    public static GameState LoadMidRun(MidRunSaveDto dto,
        IReadOnlyDictionary<int, BoonDefinition>? boonTable = null)
    {
        if (dto.SchemaVersion != MidRunSchema.Version)
            throw new InvalidOperationException(
                $"Mid-run save schema version {dto.SchemaVersion} != supported {MidRunSchema.Version}.");

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

        // Reconstruct init-only subsystems BEFORE the GameState (they are set at construction).
        var state = new GameState(player, monsters, map, rng, dto.TurnLimit)
        {
            IsDungeonMode = dto.IsDungeonMode,
            CurrentDepth = dto.CurrentDepth,
            Difficulty = dto.Difficulty,
            IdAllocator = dto.IdAllocatorWatermark is { } w ? new EntityIdAllocator(w) : null,
            IdentificationRegistry = BuildIdentification(dto.Identification),
            AppearancePool = BuildAppearance(dto.Appearance),
            MuralTracker = BuildMurals(dto.Murals),
            PityTracker = BuildPity(dto.Pity),
            BoonTracker = BuildBoons(dto.Boons),
            BoonTable = boonTable,                                   // RECONSTRUCT from config, never the save
            Rooms = dto.Rooms?.Select(BuildRoom).ToList(),
            Props = dto.Props is null ? Array.Empty<PlacedProp>() : dto.Props.Select(BuildProp).ToList(),
            PersistentState = null,                                  // cross-run layer is injected by 4b, not the save
        };

        foreach (var d in dto.LockedDoors) state.LockedDoors[(d.X, d.Y)] = d.LockColorId;

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

    // ── subsystem reconstruction (construct-then-restore; static content is caller-provided) ──
    private static IdentificationRegistry? BuildIdentification(IdentificationDto? d)
    {
        if (d is null) return null;
        var r = new IdentificationRegistry();
        r.RestoreState(d.Identified, d.DecidedUnidentified, d.AlwaysIdentified);
        return r;
    }

    private static AppearancePool? BuildAppearance(AppearancePoolDto? d) =>
        d is null ? null : AppearancePool.Restore(
            d.Descriptors.Select(p => new KeyValuePair<string, string>(p.Key, p.Value)),
            d.MysterySprites.Select(p => new KeyValuePair<string, string>(p.Key, p.Value)),
            d.PotionTypes, d.ScrollTypes, d.WandTypes, d.RingTypes);

    private static MuralTracker? BuildMurals(MuralTrackerDto? d)
    {
        if (d is null) return null;
        var m = new MuralTracker();
        m.RestoreState(d.UsedThisFloor, d.UsedThisRun);
        return m;
    }

    private static PityTracker? BuildPity(PityTrackerDto? d)
    {
        if (d is null) return null;
        var p = new PityTracker();
        p.RestoreState(
            d.Counters.Select(e => new KeyValuePair<string, int>(e.Key, e.Count)),
            d.PendingHardInjects,
            d.LootItemCounts.Select(e => new KeyValuePair<string, int>(e.Key, e.Count)),
            d.HardPityFireCount);
        return p;
    }

    private static BoonTracker? BuildBoons(BoonTrackerDto? d)
    {
        if (d is null) return null;
        var b = new BoonTracker { DisableDepthBoons = d.DisableDepthBoons };
        foreach (var depth in d.VisitedDepths) b.VisitedDepths.Add(depth);
        foreach (var boon in d.BoonsApplied) b.BoonsApplied.Add(boon);
        return b;
    }

    private static Room BuildRoom(RoomDto d) => new(d.X, d.Y, d.Width, d.Height)
    {
        Shape = d.Shape, Archetype = d.Archetype, IsDeadEnd = d.IsDeadEnd,
        IsGrandShrine = d.IsGrandShrine, IsVault = d.IsVault, MaintenanceState = d.MaintenanceState,
    };

    private static PlacedProp BuildProp(PlacedPropDto d) => new(d.PropId, d.X, d.Y, d.FootprintW, d.FootprintH,
        d.BlocksMovement, d.TileId, d.OverlayTileId, d.TileLayout, d.FlipH);

    // Weighing* (floor-25 endgame) is the ONLY remaining unserialized SERIALIZE-class surface; its
    // serializers land in 4a.3b-3. Fail loud so a floor-25 save never silently drops the gauntlet
    // state. Every other subsystem is now serialized below.
    private static void GuardWeighingUnsupported(GameState s)
    {
        var populated = new List<string>();
        if (s.Weighing != null || s.WeighingArena != null) populated.Add("Weighing");
        if (s.WeighingAudit != null) populated.Add("WeighingAudit");
        if (populated.Count > 0)
            throw new NotSupportedException(
                "Weighing-floor mid-run save is 4a.3b-3; these SERIALIZE-class subsystems are populated and " +
                $"would be dropped: {string.Join(", ", populated)}.");
    }
}
