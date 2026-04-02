namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Deterministic random number generator. Same seed always produces the same sequence.
/// Wraps System.Random for now; can be replaced with a more portable PRNG if needed.
/// </summary>
public sealed class SeededRandom
{
    private readonly Random _rng;

    public int Seed { get; }

    public SeededRandom(int seed = 1337)
    {
        Seed = seed;
        _rng = new Random(seed);
    }

    /// <summary>Returns a non-negative random integer less than maxExclusive.</summary>
    public int Next(int maxExclusive) => _rng.Next(maxExclusive);

    /// <summary>Returns a random integer in [minInclusive, maxExclusive).</summary>
    public int Next(int minInclusive, int maxExclusive) => _rng.Next(minInclusive, maxExclusive);

    /// <summary>Returns a random double in [0.0, 1.0).</summary>
    public double NextDouble() => _rng.NextDouble();

    /// <summary>Returns a random float in [0.0, 1.0).</summary>
    public float NextFloat() => (float)_rng.NextDouble();
}
