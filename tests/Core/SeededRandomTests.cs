using CatacombsOfYarl.Logic.Core;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Core;

[TestFixture]
public class SeededRandomTests
{
    [Test]
    public void SameSeed_ProducesSameSequence()
    {
        var rng1 = new SeededRandom(1337);
        var rng2 = new SeededRandom(1337);

        for (int i = 0; i < 100; i++)
        {
            Assert.That(rng1.Next(1000), Is.EqualTo(rng2.Next(1000)));
        }
    }

    [Test]
    public void DifferentSeeds_ProduceDifferentSequences()
    {
        var rng1 = new SeededRandom(1337);
        var rng2 = new SeededRandom(42);

        bool anyDifferent = false;
        for (int i = 0; i < 100; i++)
        {
            if (rng1.Next(1000) != rng2.Next(1000))
            {
                anyDifferent = true;
                break;
            }
        }

        Assert.That(anyDifferent, Is.True);
    }

    [Test]
    public void DefaultSeed_Is1337()
    {
        var rng = new SeededRandom();
        Assert.That(rng.Seed, Is.EqualTo(1337));
    }
}
