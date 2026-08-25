using CatacombsOfYarl.Logic.Core;
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

    [Test]
    public void Build_PlacesThePlayerWhereTheSpecSaid()
    {
        var state = CorridorReviewSceneBuilder.Build(
            CorridorReviewSceneBuilder.ParseSpecJson(TrunkAndBranch));

        Assert.That((state.Player.X, state.Player.Y), Is.EqualTo((8, 14)));
    }
}
