using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Endgame;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Core;

/// <summary>
/// Tier 0 review-harness geometry tests (ART-BIBLE-v0 §13.1).
///
/// The junction is the load-bearing part of the review corridor: the blind critic is asked which
/// way they would walk, and a straight corridor cannot answer that. So HasJunction is an
/// instrument, and ART-LOOP-PROCESS-v0 §4 / bible §13.5 apply to it — its pass does not count
/// until it has been shown to go red. Both directions are asserted here, and the specific
/// false-positive that actually occurred (a corridor carved three tiles wide) has its own test.
/// </summary>
[TestFixture]
public class CorridorReviewSceneBuilderTests
{
    private const string TrunkAndBranch = @"{
        ""name"": ""t"", ""width"": 17, ""height"": 21,
        ""player"": { ""x"": 8, ""y"": 14 },
        ""carve"": [
            { ""x0"": 8, ""y0"": 3,  ""x1"": 8,  ""y1"": 18 },
            { ""x0"": 2, ""y0"": 11, ""x1"": 14, ""y1"": 11 }
        ] }";

    private const string StraightOnly = @"{
        ""name"": ""t"", ""width"": 17, ""height"": 21,
        ""player"": { ""x"": 8, ""y"": 14 },
        ""carve"": [ { ""x0"": 8, ""y0"": 3, ""x1"": 8, ""y1"": 18 } ] }";

    private const string ThreeWideTrunk = @"{
        ""name"": ""t"", ""width"": 17, ""height"": 21,
        ""player"": { ""x"": 8, ""y"": 14 },
        ""carve"": [ { ""x0"": 7, ""y0"": 3, ""x1"": 9, ""y1"": 18 } ] }";

    [Test]
    public void HasJunction_IsTrue_ForCrossedOneWideCorridors()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        Assert.That(CorridorReviewSceneBuilder.HasJunction(state.Map, out var at), Is.True);
        Assert.That(at, Is.EqualTo((8, 11)), "junction should be where the two carves cross");
    }

    /// <summary>The instrument going red: a corridor with no branch has no junction.</summary>
    [Test]
    public void HasJunction_IsFalse_ForAStraightCorridor()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(StraightOnly));

        Assert.That(CorridorReviewSceneBuilder.HasJunction(state.Map, out _), Is.False,
            "a straight corridor cannot answer 'which way would you walk'");
    }

    /// <summary>
    /// The false positive that actually happened. The first Tier 0 capture carved a 3-wide trunk;
    /// the original check counted open orthogonal neighbours only, so every cell in that wide
    /// span looked like a junction and it reported "junction=YES at (8,4)" — the top of a
    /// straight corridor. Regression-locked: a wide span is not a junction.
    /// </summary>
    [Test]
    public void HasJunction_IsFalse_ForAThreeWideCorridor_TheOriginalFalsePositive()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(ThreeWideTrunk));

        Assert.That(CorridorReviewSceneBuilder.HasJunction(state.Map, out var at), Is.False,
            $"a 3-wide corridor is a room, not a junction (reported {at})");
    }

    [Test]
    public void Build_EnclosesTheCorridorInSolidWall()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));
        var map = state.Map;

        for (int x = 0; x < map.Width; x++)
        {
            Assert.That(map.IsWalkable(x, 0), Is.False, $"top border ({x},0) must be wall");
            Assert.That(map.IsWalkable(x, map.Height - 1), Is.False, "bottom border must be wall");
        }
        for (int y = 0; y < map.Height; y++)
        {
            Assert.That(map.IsWalkable(0, y), Is.False, "left border must be wall");
            Assert.That(map.IsWalkable(map.Width - 1, y), Is.False, "right border must be wall");
        }
    }

    [Test]
    public void ParseSpec_RejectsAnEmptyCarveList()
    {
        const string noCarve = @"{ ""name"": ""t"", ""width"": 9, ""height"": 9,
            ""player"": { ""x"": 4, ""y"": 4 }, ""carve"": [] }";

        Assert.That(() => CorridorReviewSceneBuilder.ParseSpecJson(noCarve),
            Throws.InvalidOperationException, "solid rock is not a corridor");
    }

    // ── The review scene carries no losable game state ──────────────────────────────────────
    //
    // Regression-locking the "player dies on the first step" defect. The player never actually
    // died — IsAlive stayed true. The builder was constructed with turnLimit: 1, so the first
    // step took TurnCount to 1 >= 1 and IsGameOver went true by the turn-limit clause. On device
    // that surfaces as the end-of-run overlay, which reads as a death.
    //
    // These assert the INVARIANT rather than the old number: a review surface that can enter a
    // game-over state can capture a death overlay or a changed HUD, and the determinism control
    // would read that as a difference in the art (LOOP-PROCESS §2.3).

    [Test]
    public void Build_OneStepDoesNotEndTheScene_TheReportedDefect()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        Assert.That(state.IsGameOver, Is.False, "the scene must not start over");
        state.TurnCount = 1;
        Assert.That(state.IsGameOver, Is.False,
            "one step ended the review scene — this is the exact reported defect");
    }

    [Test]
    public void Build_CannotBeWalkedIntoAGameOver()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        // Far more turns than any review would ever take, plus the pathological case.
        foreach (var turn in new[] { 1, 2, 10, 1_000, 100_000, 10_000_000 })
        {
            state.TurnCount = turn;
            Assert.That(state.IsGameOver, Is.False, $"scene ended at turn {turn}");
        }
    }

    [Test]
    public void Build_HasNoLossConditionsAtAll()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        Assert.Multiple(() =>
        {
            Assert.That(state.TurnLimit, Is.EqualTo(int.MaxValue), "a turn limit is a loss condition");
            Assert.That(state.Monsters, Is.Empty, "nothing may exist that can deal damage");
            Assert.That(state.Ending, Is.EqualTo(EndingType.None), "no ending may be pre-set");
            Assert.That(state.PlayerFighter.IsAlive, Is.True);
            Assert.That(state.Props, Is.Empty, "props are not part of a floor/wall review");
        });
    }

    /// <summary>
    /// The carve produces floor and wall only. A stair tile would let a walker trigger a descent
    /// mid-review and leave the scene being judged.
    /// </summary>
    [Test]
    public void Build_ContainsNoStairsOrDoors()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));
        var map = state.Map;

        for (int x = 0; x < map.Width; x++)
        {
            for (int y = 0; y < map.Height; y++)
            {
                var kind = map.GetTileKind(x, y);
                Assert.That(kind, Is.EqualTo(TileKind.Wall).Or.EqualTo(TileKind.Floor),
                    $"({x},{y}) is {kind} — the review corridor is floor and wall only");
            }
        }
    }

    [Test]
    public void Build_PlacesThePlayerWhereTheSpecSaid()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        Assert.That((state.Player.X, state.Player.Y), Is.EqualTo((8, 14)));
    }
}
