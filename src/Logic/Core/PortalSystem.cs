using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Handles portal pair placement, entity teleportation, and portal cleanup.
///
/// Design rules (see plan_spell_wand_scroll_system.md § Phase 5):
///   - Only one portal pair active at a time. Using the wand again recycles the old pair.
///   - Portals are bidirectional: entrance → exit AND exit → entrance.
///   - No teleport chaining: PortalComponent.UsedThisTurn prevents re-triggering on arrival.
///     That flag must be cleared at end-of-turn (ClearPortalUsedFlags).
///   - Portals do not persist between floors — ClearPortals is called in floor transition.
///   - Both player and monsters can use portals.
///   - Placement validates: tile must be walkable and not the same tile for both portals.
///
/// This is a new system — there is no PoC reference implementation.
/// </summary>
public static class PortalSystem
{
    /// <summary>
    /// Place a portal pair at the given entrance and exit positions.
    ///
    /// If portals already exist, removes them first (emits PortalRemovedEvent).
    /// Creates two portal entities, links them to each other, registers on the map,
    /// and adds to state.Portals.
    ///
    /// Returns null (no events) if placement is invalid:
    ///   - Either tile is not walkable
    ///   - Entrance and exit are the same tile
    ///
    /// On success returns events: [PortalRemovedEvent?] + [PortalPlacedEvent × 2].
    /// </summary>
    public static List<TurnEvent>? PlacePortals(
        GameState state,
        int placedByEntityId,
        int entranceX, int entranceY,
        int exitX, int exitY,
        EntityFactory entityFactory)
    {
        // Validate: both tiles must be walkable
        if (!state.Map.IsWalkable(entranceX, entranceY)) return null;
        if (!state.Map.IsWalkable(exitX, exitY)) return null;

        // Validate: entrance and exit cannot be the same tile
        if (entranceX == exitX && entranceY == exitY) return null;

        var events = new List<TurnEvent>();

        // Recycle existing portal pair if one is active
        if (state.Portals.Count > 0)
        {
            var removeEvent = RemoveAllPortals(state);
            if (removeEvent != null)
                events.Add(removeEvent);
        }

        // Create entrance entity (cyan)
        var entrance = entityFactory.Create("Portal Entrance", entranceX, entranceY);
        var entranceComp = entrance.Add(new PortalComponent { Type = PortalType.Entrance });

        // Create exit entity (yellow)
        var exit = entityFactory.Create("Portal Exit", exitX, exitY);
        var exitComp = exit.Add(new PortalComponent { Type = PortalType.Exit });

        // Cross-link — each portal points to the other's entity ID
        entranceComp.LinkedPortalId = exit.Id;
        exitComp.LinkedPortalId = entrance.Id;

        // Register on map and in state
        state.Map.RegisterEntity(entrance);
        state.Map.RegisterEntity(exit);
        state.Portals.Add(entrance);
        state.Portals.Add(exit);

        events.Add(new PortalPlacedEvent
        {
            ActorId = placedByEntityId,
            PlacerId = placedByEntityId,
            Type = PortalType.Entrance,
            PortalEntityId = entrance.Id,
            X = entranceX,
            Y = entranceY,
        });

        events.Add(new PortalPlacedEvent
        {
            ActorId = placedByEntityId,
            PlacerId = placedByEntityId,
            Type = PortalType.Exit,
            PortalEntityId = exit.Id,
            X = exitX,
            Y = exitY,
        });

        return events;
    }

    /// <summary>
    /// Check if the given entity is standing on a portal and teleport it to the linked portal.
    ///
    /// Returns a PortalTeleportEvent if teleportation occurred, null otherwise.
    /// Updates the entity's position in-place. The caller is responsible for emitting the event.
    ///
    /// Anti-chaining: if the arrival portal's UsedThisTurn flag is set, we do NOT teleport again.
    /// After teleportation, marks the destination portal as UsedThisTurn to prevent chain triggers.
    ///
    /// The entity's own portal (the one they just stepped onto) is intentionally NOT flagged —
    /// it resets next turn via ClearPortalUsedFlags. This allows future traversal.
    /// </summary>
    public static PortalTeleportEvent? CheckPortalCollision(Entity entity, GameState state)
    {
        if (state.Portals.Count == 0) return null;

        // Find a portal at the entity's current position
        var portal = state.Portals.FirstOrDefault(p =>
            p.X == entity.X && p.Y == entity.Y);

        if (portal == null) return null;

        var portalComp = portal.Get<PortalComponent>();
        if (portalComp == null) return null;

        // Anti-chaining: if this portal was just used this turn, don't re-trigger
        if (portalComp.UsedThisTurn) return null;

        // Find the linked exit portal
        var linked = state.Portals.FirstOrDefault(p => p.Id == portalComp.LinkedPortalId);
        if (linked == null) return null;

        var linkedComp = linked.Get<PortalComponent>();
        if (linkedComp == null) return null;

        // Record origin before moving
        int fromX = entity.X;
        int fromY = entity.Y;

        // Teleport: update entity position directly (the map uses a flat list —
        // no spatial hash to update, just the entity's X/Y fields, same as SpellResolver.ResolveTeleport).
        entity.X = linked.X;
        entity.Y = linked.Y;

        // Flag the destination portal as used this turn to prevent immediate re-teleport
        linkedComp.UsedThisTurn = true;

        return new PortalTeleportEvent
        {
            ActorId = entity.Id,
            EntityId = entity.Id,
            FromX = fromX,
            FromY = fromY,
            ToX = entity.X,
            ToY = entity.Y,
            PortalEntryId = portal.Id,
            PortalExitId = linked.Id,
        };
    }

    /// <summary>
    /// Remove all active portals from the map and clear state.Portals.
    /// Called on floor transitions so portals do not bleed across floors.
    /// Also clears UsedThisTurn flags (moot, but clean).
    /// Returns a PortalRemovedEvent if portals existed, null otherwise.
    /// </summary>
    public static PortalRemovedEvent? ClearPortals(GameState state)
    {
        return RemoveAllPortals(state);
    }

    /// <summary>
    /// Clear the UsedThisTurn flag on all active portals.
    /// Must be called at end-of-turn to allow portals to fire again next turn.
    /// </summary>
    public static void ClearPortalUsedFlags(GameState state)
    {
        foreach (var portal in state.Portals)
        {
            var comp = portal.Get<PortalComponent>();
            if (comp != null) comp.UsedThisTurn = false;
        }
    }

    // ─── Private helpers ───────────────────────────────────────────────────────

    private static PortalRemovedEvent? RemoveAllPortals(GameState state)
    {
        if (state.Portals.Count == 0) return null;

        // Find entrance and exit for the event payload
        int entranceId = -1;
        int exitId = -1;
        foreach (var p in state.Portals)
        {
            var comp = p.Get<PortalComponent>();
            if (comp?.Type == PortalType.Entrance) entranceId = p.Id;
            else if (comp?.Type == PortalType.Exit) exitId = p.Id;

            // Unregister from map — entity still exists in memory but is no longer on the map
            state.Map.UnregisterEntity(p);
        }

        state.Portals.Clear();

        // Only emit if we had a complete pair; partial pairs (shouldn't happen) still clean up
        if (entranceId != -1 && exitId != -1)
        {
            return new PortalRemovedEvent
            {
                ActorId = 0, // system action — no specific actor
                EntranceEntityId = entranceId,
                ExitEntityId = exitId,
            };
        }

        return null;
    }
}
