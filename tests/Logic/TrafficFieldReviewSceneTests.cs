using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.Map;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Logic;

/// <summary>
/// A REVIEW SCENE THAT CANNOT EXERCISE THE SYSTEM IT IS USED TO REVIEW.
///
/// The corridor review scenes — `corridor_junction` and `wall_face_review` — return a traffic
/// field of exactly ZERO, so every traffic-keyed system is switched off in them: the wall's
/// aging, and the floor's wear, which is older and has had verdicts taken through it. Found by
/// accident while measuring something else, then audited across the whole review set
/// (`tools/tier1_walls/audit_scene_traffic.py`).
///
/// These tests pin the property in the LOGIC layer, where it can be asserted without a scene, a
/// device or a capture — and they are written to fail on the shape of the defect rather than on
/// one scene's name, so a future spec that reintroduces it says so.
/// </summary>
[TestFixture]
public class TrafficFieldReviewSceneTests
{
    /// <summary>A one-wide cross of corridors: the shape both dead review scenes have.</summary>
    private static GameMap Cross(int w = 17, int h = 21)
    {
        var map = new GameMap(w, h);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                map.SetTile(x, y, TileKind.Wall);
        for (int y = 3; y <= 18; y++) map.SetTile(8, y, TileKind.Floor);
        for (int x = 2; x <= 14; x++) { map.SetTile(x, 8, TileKind.Floor); map.SetTile(x, 14, TileKind.Floor); }
        return map;
    }

    /// <summary>The same corridors with a destination on the end of each arm.</summary>
    private static GameMap CrossWithRooms(int w = 17, int h = 21)
    {
        var map = Cross(w, h);
        void Room(int x0, int y0, int x1, int y1)
        {
            for (int y = y0; y <= y1; y++)
                for (int x = x0; x <= x1; x++)
                    map.SetTile(x, y, TileKind.Floor);
        }
        Room(6, 1, 10, 3);      // north
        Room(6, 16, 10, 18);    // south
        Room(1, 12, 3, 16);     // west, off the lower branch
        return map;
    }

    private static int Occupancy(byte[,] f, GameMap map)
    {
        int n = 0;
        for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
                if (map.IsWalkable(x, y) && f[x, y] > 0) n++;
        return n;
    }

    [Test]
    public void AOneWideCrossHasSomewhereToWalk()
    {
        // The premise, checked first: if this fails the rest of the fixture is measuring the
        // fixture rather than TrafficField.
        var map = Cross();
        int walkable = 0;
        for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
                if (map.IsWalkable(x, y)) walkable++;
        Assert.That(walkable, Is.GreaterThan(30), "the cross should carve about forty cells");
    }

    [Test]
    public void ARoomedSceneAccumulatesTraffic()
    {
        var map = CrossWithRooms();
        var r = TrafficField.ComputeFromMap(map);
        Assert.That(r.Routes, Is.GreaterThan(0), "a scene with destinations must route between them");
        Assert.That(Occupancy(r.Field, map), Is.GreaterThan(0),
            "and the routes must deposit something the renderer can read");
    }

    /// <summary>
    /// THE DEFECT, LOCATED, AND IT IS NOT THE ONE THE AUDIT GUESSED.
    ///
    /// It is not the corridor SHAPE — an empty one-wide cross accumulates traffic perfectly well
    /// (`ABareCrossAccumulates`). It is the PLAYER, and the mechanism is a disagreement between
    /// two pathfinders:
    ///
    ///   * `FarthestWalkable` picks the spine's endpoints with `Pathfinder.DijkstraMap`, which
    ///     **walks through a blocking entity** — measured here: with the figure in place, all
    ///     forty cells are still "reachable" from the corridor's head.
    ///   * The spine itself is `Pathfinder.AStar`, which **does not**. In a one-wide corridor
    ///     every route between the two halves must pass through the figure, so it returns null.
    ///
    /// An empty spine gives routes 0, and routes 0 gives a field of exactly zero. So the failure
    /// is not a degradation, it is a cliff: **40 → 0 occupancy, 5 → 0 routes, from one figure
    /// standing still.** That is why it survived — it is invisible in the spec file and only
    /// appears once somebody is standing in the scene.
    ///
    /// ⚠ NOT FIXED HERE. `TrafficField` is the floor session's live surface (PRs #162, #163,
    /// #165, #166 all open on it), and a concurrent edit to it from this branch would collide
    /// with work in flight. What this session does instead is pin the behaviour, report it, and
    /// build the replacement review scene with a LOOP so that no single figure can sever it —
    /// which is the right scene design regardless of how the disagreement is settled.
    /// </summary>
    [Test]
    public void APlayerStandingInAOneWideCorridorCollapsesTheFieldToZero()
    {
        var map = Cross();
        var before = TrafficField.ComputeFromMap(map);
        Assert.That(Occupancy(before.Field, map), Is.GreaterThan(0),
            "premise: the empty cross routes fine");

        var blocker = new Entity(1, "Player", 8, 11, blocksMovement: true);
        map.RegisterEntity(blocker);
        var after = TrafficField.ComputeFromMap(map);

        // Replicating the endpoint choice, so the mechanism is named rather than inferred.
        var d0 = Pathfinder.DijkstraMap(map, 8, 3, canPassDoors: true);
        int reach = 0;
        for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
                if (map.IsWalkable(x, y) && d0[x, y] < int.MaxValue) reach++;
        TestContext.WriteLine($"reachable from (8,3) with the figure in place: {reach}");
        TestContext.WriteLine($"occupancy before={Occupancy(before.Field, map)} "
                              + $"after={Occupancy(after.Field, map)} "
                              + $"routes before={before.Routes} after={after.Routes} "
                              + $"spine before={before.SpineLength} after={after.SpineLength}");
        Assert.That(reach, Is.EqualTo(Occupancy(before.Field, map)),
            "DijkstraMap walks through the figure: every cell is still 'reachable', which is how "
            + "the endpoints get chosen in a component AStar cannot cross");
        Assert.That(after.Routes, Is.EqualTo(0), "the spine collapses rather than shortening");
        Assert.That(Occupancy(after.Field, map), Is.EqualTo(0),
            "and the field goes to exactly zero — a cliff, not a degradation. One figure standing "
            + "still switches every traffic-keyed system in the scene off.");
    }

    /// <summary>
    /// KEPT AS A CHARACTERISATION RATHER THAN AS A REQUIREMENT.
    ///
    /// This does not assert that a bare cross SHOULD be dead — whether `ComputeFromMap` ought to
    /// find a spine in one is a design question and not this session's to rule. What it pins is
    /// that it currently does not, so the day that changes, the review scenes built around the
    /// limitation get a failing test instead of a silent change of meaning.
    /// </summary>
    [Test]
    public void ABareCrossAccumulates_Characterisation()
    {
        var map = Cross();
        var r = TrafficField.ComputeFromMap(map);
        Assert.That(Occupancy(r.Field, map), Is.GreaterThan(0),
            "characterisation: an EMPTY one-wide cross routes fine. The review scenes' zero field "
            + "is therefore not a property of the corridor shape, and the first draft of this "
            + "fixture asserted the opposite and was wrong.");
    }
}
